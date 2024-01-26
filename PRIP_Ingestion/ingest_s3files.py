import argparse
import copy
import datetime
import hashlib
import json
import os
import re
import uuid
import sys

DEBUG=True

def parse_filename_s3(the_file_name):
    if DEBUG:
        print(the_file_name)
    p = re.compile('(S3_|S3B|S3A)_([A-Z|0-9|_]{11})_([A-Z|0-9|_]{15})_([A-Z|0-9|_]{15})_([A-Z|0-9|_]{15}).*')
    ama = p.match(the_file_name)
    if not ama:
        return ama
    items = ama.groups()
    result = {}
    result["Mission_ID"] = items[0]
    result["File_Class"] = items[1]
    result["Validity_Start"] = items[2]
    result["Validity_Stop"] = items[3]
    result["Generation_Date"] = items[4]
    return result

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
    template_base = None
    with open(args.template) as f:
        template_base = json.load(f)

    # band_dict = {}
    # for (dirpath, dirnames, filenames) in os.walk(args.bands):
    #     for filename in filenames:
    #         with open(os.path.join(args.bands,filename)) as f:
    #             band = json.load(f)
    #             band_dict[band["Name"]] = band["Id"]
    # TODO: Put to a function : load_filetype_configuration(filetype_dir)
    filetype_dict = []
    for (dirpath, dirnames, filenames) in os.walk(args.filetypes):
        for filename in filenames:
            with open(os.path.join(args.filetypes, filename)) as f:
                filetype = json.load(f)
                levels = []
                if "ProductLevels@odata.bind" in filetype:
                    levels = filetype["ProductLevels@odata.bind"]
                elif "ProductLevels" in filetype:
                    levels = ["ProductLevels('"+f["Level"]+"')" for f in filetype["ProductLevels"]]
                filetype_dict.append((filetype["LongName"], filetype["Mission"], levels))
    if len(filetype_dict) == 0:
        raise Exception("No filetypes found in folder")


    odata_datetime_format = "%Y-%m-%dT%H:%M:%S.%fZ"

    # Using readlines()
    file1 = open(args.input, 'r')
    lines = file1.readlines()
    filetype_str = ""
    start_good = ""
    stop_good = ""
    crea_good = ""
    shortname = ""
    # Strips the newline character
    list_of_files = {}
    idx = 1
    for filenames in lines:
        filename = os.path.basename(filenames)
        if DEBUG:
            print("Treating "+filename+ " : " +str(idx)+ " / " + str(len(lines)))
        template = None
        update = False
        if os.path.exists(os.path.join(args.output, os.path.splitext(filename)[0] + ".json")):
            with open(os.path.join(args.output, os.path.splitext(filename)[0] + ".json")) as f:
                try:
                    template = json.load(f)
                except Exception as e:
                    raise Exception("Could not open : " + os.path.join(args.output, os.path.splitext(filename)[0] + ".json"))
            update = True
        else:
            template = copy.copy(template_base)

        # TODO: Put in function:
        #   auxtype_file_json = extract_s3_parameters(filename, template)
        # TODO: Put in function: get_platform(filename)
        # template["Unit"] = get_platform(filename)
        if "S3A_" in filename:
            template["Unit"] = "A"
        elif "S3B_" in filename:
            template["Unit"] = "B"
        else:
            template["Unit"] = "X"
        dic = parse_filename_s3(os.path.splitext(os.path.splitext(filename)[0])[0])

        shortname = dic["File_Class"]
        filetype_str = dic["File_Class"]
        filetype = None
        mission = None
        product_levels = None
        # Look for type, and get filetype/mission/levels associated
        for type in filetype_dict:
            if filetype_str in type[0]:
                filetype = type[0]
                mission = type[1]
                product_levels = type[2]
                break
        if filetype is None:
            raise Exception("unknown file type")
        # TODO: Put Format in Constant
        # TODO : Define function to convert String from format 1 to fmroat 2,
        #  with anoptional offset (timedelta)
        # offset = datetime.timedelta(hours=6) if "SR_2_RMO_AX" in filetype else None
        # start_good = parse_date(dic["Validity_Start"], "%Y%m%dT%H%M%S", offset)
        # stop_good = parse_date(dic["Validity_Stop"], "%Y%m%dT%H%M%S", offset)
        # crea_good = parse_date(dic["Generation_Date"], "%Y%m%dT%H%M%S", None)
        start_dt = datetime.datetime.strptime(dic["Validity_Start"], "%Y%m%dT%H%M%S")
        stop_dt = datetime.datetime.strptime(dic["Validity_Stop"], "%Y%m%dT%H%M%S")
        if "SR_2_RMO_AX" in filetype:
            start_dt = start_dt - datetime.timedelta(hours=6)
            stop_dt = stop_dt + datetime.timedelta(hours=6)
        start_good = datetime.datetime.strftime(start_dt, odata_datetime_format)
        stop_good = datetime.datetime.strftime(stop_dt, odata_datetime_format)
        crea_dt = datetime.datetime.strptime(dic['Generation_Date'], "%Y%m%dT%H%M%S")
        crea_good = datetime.datetime.strftime(crea_dt, odata_datetime_format)

        if "SR_2_RMO_AX" in filetype and "_ST_" in filename:
            if DEBUG:
                print("Skipped : "+filename)
            continue
        template["AuxType@odata.bind"] = "AuxTypes('" + filetype + "')"
        template["@odata.context"] = "$metadata#AuxFiles"
        if not update:
            template["Id"] = str(uuid.uuid4())
        template["FullName"] = filename.strip()
        template["ShortName"] = shortname
        template["Baseline"] = "06.11"
        if "SRAL" in mission:
            template["Baseline"] = "06.19"
            if "S3A_" in filename:
                template["IpfVersion"] = "S3A-2.69"
            elif "S3B_" in filename:
                template["IpfVersion"] = "S3B-1.45"
            else:
                template["IpfVersion"] = "S3A-2.69 & S3B-1.45"
        if "MWR" in mission:
            template["Baseline"] = "06.11"
            if "S3A_" in filename:
                template["IpfVersion"] = "S3A-2.69"
            elif "S3B_" in filename:
                template["IpfVersion"] = "S3B-1.45"
            else:
                template["IpfVersion"] = "S3A-2.69 & S3B-1.45"
        if "OLCI" in mission:
            if "ProductLevels('L2')" in product_levels:
                template["Baseline"] = "06.13"
            elif "ProductLevels('L1')" in product_levels:
                template["Baseline"] = "06.08"
            else:
                raise Exception("Unknown product level for "+filename+ " "+mission)
            if "S3A_" in filename:
               template["IpfVersion"] = "S3A-2.66"
            elif "S3B_" in filename:
               template["IpfVersion"] = "S3B-1.40"
            else:
               template["IpfVersion"] = "S3A-2.66 & S3B-1.40"
        if "SLSTR" in mission:
            if "ProductLevels('L2')" in product_levels:
                template["Baseline"] = "06.16"
                if "S3A_" in filename:
                    template["IpfVersion"] = "S3A-2.61"
                elif "S3B_" in filename:
                    template["IpfVersion"] = "S3B-1.33"
                else:
                    template["IpfVersion"] = "S3A-2.61 & S3B-1.33"
            elif "ProductLevels('L1')" in product_levels:
                template["Baseline"] = "06.17"
                if "S3A_" in filename:
                    template["IpfVersion"] = "S3A-2.59"
                elif "S3B_" in filename:
                    template["IpfVersion"] = "S3B-1.31"
                else:
                    template["IpfVersion"] = "S3A-2.59 & S3B-1.31"
            else:
                raise Exception("Unknown product level for " + filename)
        if "SYN" in mission:
            if "ProductLevels('L2')" in product_levels:
                template["Baseline"] = "06.20"
            elif "ProductLevels('L1')" in product_levels:
                template["Baseline"] = "03.37"
            else:
                raise Exception("Unknown product level for " + filename)
            if "S3A_" in filename:
                template["IpfVersion"] = "S3A-2.66"
            elif "S3B_" in filename:
                template["IpfVersion"] = "S3B-1.40"
            else:
                template["IpfVersion"] = "S3A-2.66 & S3B-1.40"



        #Date part
        template["ValidityStart"] = start_good
        template["ValidityStop"] = stop_good
        template["SensingTimeApplicationStart"] = start_good
        template["SensingTimeApplicationStop"] = stop_good
        template["CreationDate"] = crea_good
        #band
        template["Band"] = "BXX"
        # Write down
        with open(os.path.join(args.output, os.path.splitext(filename)[0] + ".json"), 'w') as json_file:
            json.dump(template, json_file)
        idx = idx + 1


if __name__ == "__main__":
    main()
    sys.exit(0)
