import argparse
import copy
import csv
import datetime
import hashlib
import json
import os
import re
import uuid
import sys

from S2_FileNaming import parse_all_as_dict

DEBUG=True


def build_filetype_table(type_dir):
    filetype_dict = []
    for (dirpath, dirnames, filenames) in os.walk(type_dir):
        for filename in filenames:
            if os.path.splitext(filename)[1] == ".json":
                with open(os.path.join(type_dir, filename)) as f:
                    filetype = json.load(f)
                    filetype_dict.append((filetype["LongName"], filetype["Mission"], filetype["ProductLevels@odata.bind"]))
    return filetype_dict

def main():
    parser = argparse.ArgumentParser(description="",  # main description for help
            epilog='Beta', formatter_class=argparse.RawTextHelpFormatter)  # displayed after help
    parser.add_argument("-i", "--input",
                        help="input",
                       required=True)
    parser.add_argument("-f", "--filetypes",
                        help="filetypes jsons",
                        required=True)
    parser.add_argument("-t", "--template",
                        help="template",
                        required=True)
    parser.add_argument(
            "-o",
            "--output",
            help="Output data directory (product directory). Default value: '.'",
            required=True)

    args = parser.parse_args()

    #Create output dir
    if not os.path.exists(args.output):
        os.makedirs(args.output)
        if not os.path.exists(args.output):
            raise Exception("Impossible to create output dir "+args.output)


    template_base = None
    with open(args.template) as f:
        template_base = json.load(f)

    # band_dict = {}
    # for (dirpath, dirnames, filenames) in os.walk(args.bands):
    #     for filename in filenames:
    #         with open(os.path.join(args.bands,filename)) as f:
    #             band = json.load(f)
    #             band_dict[band["Name"]] = band["Id"]
    filetype_dict = build_filetype_table(args.filetypes)

    print("FileType dict:")
    print(filetype_dict)
    if len(filetype_dict) == 0:
        raise Exception("No filetypes found in folder")

    odata_datetime_format = "%Y-%m-%dT%H:%M:%S.%fZ"

    list_of_files = {}
    # File containing the list of Aux files to be ingested
    file1 = open(args.input, 'r')
    lines = file1.readlines()
    total_lines = len(lines)

    # FROM HERE put in a separate function!
    idx = 1
    # Use enumerate instead of idx!!
    # for file_idx, auxfile_path in enumerate(lines, start=1):
    for auxfile_path in lines:
        filename = os.path.basename(auxfile_path)
        if DEBUG:
            print("Treating ",filename, " : " ,str(idx), " / " , total_lines)
        template = None
        update = False
        # TBC Build Reprobase Json File filename
        # TBC: If the file occurs again, add to existing out JSON one
        auxfile_out_json_path = os.path.join(args.output, os.path.splitext(filename)[0] + ".json")
        print("Loading/Creating JSON file: ", auxfile_out_json_path)
        if os.path.exists(auxfile_out_json_path):
            with open(auxfile_out_json_path) as f:
                try:
                    template = json.load(f)
                except Exception as e:
                    raise Exception(
                        "Could not open : " + auxtype_path)
            update = True
        else:
            template = copy.copy(template_base)
        # Extract metadta from filename
        s2dict =parse_all_as_dict(filename)
        template["@odata.context"] = "$metadata#AuxFiles"
        if not update:
            template["Id"] = str(uuid.uuid4())
        filetype = None
        mission = None
        product_levels = None
        if 'File_Semantic' in s2dict.keys():
            if s2dict['File_Semantic'] == "AUX_RESORB":
                filetype = "AUX_RESORB_S2"
                mission = "S2MSI"
                product_levels = "ProductLevels('L1')"
            elif s2dict['File_Semantic'] == "AUX_PREORB":
                filetype = "AUX_PREORB_S2"
                mission = "S2MSI"
                product_levels = "ProductLevels('L1')"
            else:
                print(s2dict['File_Semantic'])
                # TOOD: Better: build a dict with key type[0] and lookup
                #  for the type specified by File_Semantic
                for type in filetype_dict:
                    if s2dict['File_Semantic'] in type[0]:
                        print(type[0])
                        filetype = type[0]
                        mission = type[1]
                        product_levels = type[2]
                        break
                if filetype is None:
                    raise Exception("unknown file type")
            template["AuxType@odata.bind"] = "AuxTypes('"+filetype+"')"
        else:
            raise Exception("unknown file type")
        template["FullName"] = filename.strip()
        template["ShortName"] = s2dict['File_Category']+s2dict['File_Semantic']
        if 'processing_baseline' in s2dict.keys():
            template["Baseline"] = s2dict['processing_baseline']
        else:
            if "ProductLevels('L2')" in product_levels:
                template["Baseline"] = "02.14"
                template["IpfVersion"] = "V02.08.00"
            elif "ProductLevels('L1')" in product_levels:
                template["Baseline"] = "02.09"
                template["IpfVersion"] = "V2B-4.2.8"
            else:
                raise Exception("unknown product level")
        #Date part
        start_str = s2dict['applicability_time_period'].split("_")[0]
        stop_str = s2dict['applicability_time_period'].split("_")[1]
        start_dt = datetime.datetime.strptime(start_str, "%Y%m%dT%H%M%S")
        try:
            stop_dt = datetime.datetime.strptime(stop_str, "%Y%m%dT%H%M%S")
        except:
            if stop_str == "99999999T999999":
                stop_dt = datetime.datetime.strptime("99991231T235959", "%Y%m%dT%H%M%S")
        start_good = datetime.datetime.strftime(start_dt, odata_datetime_format)
        stop_good = datetime.datetime.strftime(stop_dt, odata_datetime_format)
        template["ValidityStart"] = start_good
        template["ValidityStop"] = stop_good
        template["SensingTimeApplicationStart"] = start_good
        template["SensingTimeApplicationStop"] = stop_good
        crea_dt = datetime.datetime.strptime(s2dict['Creation_Date'], "%Y%m%dT%H%M%S")
        template["CreationDate"] = datetime.datetime.strftime(crea_dt, odata_datetime_format)
        #band
        if "band_index" in s2dict.keys():
            band_id = "B"+s2dict["band_index"]
            template["Band"] = band_id
        else:
            template["Band"] = "BXX"
        #sensor
        if s2dict['Mission_ID'] == "S2A":
            template["Unit"] = "A"
        elif s2dict['Mission_ID'] == "S2B":
            template["Unit"] = "B"
        elif s2dict['Mission_ID'] == "S2_":
            template["Unit"] = "X"
        else:
            raise Exception("Unknown mission ID "+s2dict['Mission_ID'])
        # Write down
        with open(os.path.join(args.output, os.path.splitext(filename)[0] + ".json"), 'w') as json_file:
            json.dump(template, json_file)
        idx = idx + 1


if __name__ == "__main__":
    main()
    sys.exit(0)
