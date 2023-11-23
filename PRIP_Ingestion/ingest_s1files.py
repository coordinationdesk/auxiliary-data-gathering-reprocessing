import argparse
import copy
import datetime
import json
import os
import re
import uuid

DEBUG=False

def parse_filename_wnd(the_file_name):
    if DEBUG:
        print(the_file_name)
    p = re.compile('(S1A|S1B|S1_)_([A-Z|0-9|_]{7})_V([A-Z|0-9|_]{15})_G([A-Z|0-9|_]{15}).*')
    ama = p.match(the_file_name)
    if not ama:
        return ama
    items = ama.groups()
    result = {}
    result["Mission_ID"]= items[0]
    result["File_Class"]= items[1]
    result["Validity_Start"]= items[2]
    result["Generation_Date"]= items[3]
    result["ShortName"] = items[1]
    return result

def parse_filename_orb(the_file_name):
    if DEBUG:
        print(the_file_name)
    p = re.compile('(S1A|S1B|S1_)_([A-Z|0-9]{4})_([A-Z|0-9|_]{4})([A-Z|0-9|_]{6})_([A-Z|0-9|_]{4})_([A-Z|0-9|_]{15})_V([A-Z|0-9|_]{15})_([A-Z|0-9|_]{15}).*')
    ama = p.match(the_file_name)
    if not ama:
        return ama
    items = ama.groups()
    result = {}
    result["Mission_ID"]= items[0]
    result["File_Class"]= items[1]
    result["File_Category"] = items[2]
    result["File_Type"] = items[3]
    result["File_Content"] = items[4]
    result["Generation_Date"] = items[5]
    result["Validity_Start"]= items[6]
    result["Validity_Stop"] = items[7]
    result["ShortName"] = result["File_Category"]+result["File_Type"]
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
        try:
            template_base = json.load(f)
        except Exception as e:
            raise Exception("Could not open : "+args.template)

    # band_dict = {}
    # for (dirpath, dirnames, filenames) in os.walk(args.bands):
    #     for filename in filenames:
    #         with open(os.path.join(args.bands,filename)) as f:
    #             band = json.load(f)
    #             band_dict[band["Name"]] = band["Id"]
    filetype_dict = []
    for (dirpath, dirnames, filenames) in os.walk(args.filetypes):
        for filename in filenames:
            with open(os.path.join(args.filetypes, filename)) as f:
                filetype = json.load(f)
                filetype_dict.append(filetype["LongName"])


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
        if filenames.startswith("#"):
            continue
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
        if "S1A" in filename:
            template["Unit"] = "A"
        elif "S1B" in filename:
            template["Unit"] = "B"
        else:
            template["Unit"] = "X"
        if "AUX_WND" in filename:
            if DEBUG:
                print("AUX_WND file detected")
            filetype_str = "S1__AUX_WND"
            dic = parse_filename_wnd(os.path.splitext(os.path.splitext(filename)[0])[0])
            start_dt = datetime.datetime.strptime(dic["Validity_Start"], "%Y%m%dT%H%M%S")
            stop_dt = start_dt + datetime.timedelta(days=1)
            start_good = datetime.datetime.strftime(start_dt, odata_datetime_format)
            stop_good = datetime.datetime.strftime(stop_dt, odata_datetime_format)
            crea_dt = datetime.datetime.strptime(dic['Generation_Date'], "%Y%m%dT%H%M%S")
            crea_good = datetime.datetime.strftime(crea_dt, odata_datetime_format)
            shortname = dic["ShortName"]
        elif "AUX_WAV" in filename:
            if DEBUG:
                print("AUX_WAVE file detected")
            filetype_str = "S1__AUX_WAV"
            dic = parse_filename_wnd(os.path.splitext(os.path.splitext(filename)[0])[0])
            start_dt = datetime.datetime.strptime(dic["Validity_Start"], "%Y%m%dT%H%M%S")
            stop_dt = start_dt + datetime.timedelta(days=1)
            start_good = datetime.datetime.strftime(start_dt, odata_datetime_format)
            stop_good = datetime.datetime.strftime(stop_dt, odata_datetime_format)
            crea_dt = datetime.datetime.strptime(dic['Generation_Date'], "%Y%m%dT%H%M%S")
            crea_good = datetime.datetime.strftime(crea_dt, odata_datetime_format)
            shortname = dic["ShortName"]
        elif "AUX_ICE" in filename:
            if DEBUG:
                print("AUX_ICE file detected")
            filetype_str = "S1__AUX_ICE"
            dic = parse_filename_wnd(os.path.splitext(os.path.splitext(filename)[0])[0])
            start_dt = datetime.datetime.strptime(dic["Validity_Start"], "%Y%m%dT%H%M%S")
            stop_dt = start_dt + datetime.timedelta(days=1)
            start_good = datetime.datetime.strftime(start_dt, odata_datetime_format)
            stop_good = datetime.datetime.strftime(stop_dt, odata_datetime_format)
            crea_dt = datetime.datetime.strptime(dic['Generation_Date'], "%Y%m%dT%H%M%S")
            crea_good = datetime.datetime.strftime(crea_dt, odata_datetime_format)
            shortname = dic["ShortName"]
        elif "AUX_PP1" in filename:
            if DEBUG:
                print("AUX_PP1 file detected")
            filetype_str = "AUX_PP1"
            dic = parse_filename_wnd(os.path.splitext(os.path.splitext(filename)[0])[0])
            start_dt = datetime.datetime.strptime(dic["Validity_Start"], "%Y%m%dT%H%M%S")
            stop_dt = datetime.datetime.strptime("21000101T000000", "%Y%m%dT%H%M%S")
            start_good = datetime.datetime.strftime(start_dt, odata_datetime_format)
            stop_good = datetime.datetime.strftime(stop_dt, odata_datetime_format)
            crea_dt = datetime.datetime.strptime(dic['Generation_Date'], "%Y%m%dT%H%M%S")
            crea_good = datetime.datetime.strftime(crea_dt, odata_datetime_format)
            shortname = dic["ShortName"]
        elif "AUX_PP2" in filename:
            if DEBUG:
                print("AUX_PP2 file detected")
            filetype_str = "AUX_PP2"
            dic = parse_filename_wnd(os.path.splitext(os.path.splitext(filename)[0])[0])
            start_dt = datetime.datetime.strptime(dic["Validity_Start"], "%Y%m%dT%H%M%S")
            stop_dt = datetime.datetime.strptime("21000101T000000", "%Y%m%dT%H%M%S")
            start_good = datetime.datetime.strftime(start_dt, odata_datetime_format)
            stop_good = datetime.datetime.strftime(stop_dt, odata_datetime_format)
            crea_dt = datetime.datetime.strptime(dic['Generation_Date'], "%Y%m%dT%H%M%S")
            crea_good = datetime.datetime.strftime(crea_dt, odata_datetime_format)
            shortname = dic["ShortName"]
        elif "AUX_CAL" in filename:
            if DEBUG:
                print("AUX_CAL file detected")
            filetype_str = "AUX_CAL"
            dic = parse_filename_wnd(os.path.splitext(os.path.splitext(filename)[0])[0])
            start_dt = datetime.datetime.strptime(dic["Validity_Start"], "%Y%m%dT%H%M%S")
            stop_dt = datetime.datetime.strptime("21000101T000000", "%Y%m%dT%H%M%S")
            start_good = datetime.datetime.strftime(start_dt, odata_datetime_format)
            stop_good = datetime.datetime.strftime(stop_dt, odata_datetime_format)
            crea_dt = datetime.datetime.strptime(dic['Generation_Date'], "%Y%m%dT%H%M%S")
            crea_good = datetime.datetime.strftime(crea_dt, odata_datetime_format)
            shortname = dic["ShortName"]
        elif "AUX_INS" in filename:
            if DEBUG:
                print("AUX_INS file detected")
            filetype_str = "AUX_INS"
            dic = parse_filename_wnd(os.path.splitext(os.path.splitext(filename)[0])[0])
            start_dt = datetime.datetime.strptime(dic["Validity_Start"], "%Y%m%dT%H%M%S")
            stop_dt = datetime.datetime.strptime("21000101T000000", "%Y%m%dT%H%M%S")
            start_good = datetime.datetime.strftime(start_dt, odata_datetime_format)
            stop_good = datetime.datetime.strftime(stop_dt, odata_datetime_format)
            crea_dt = datetime.datetime.strptime(dic['Generation_Date'], "%Y%m%dT%H%M%S")
            crea_good = datetime.datetime.strftime(crea_dt, odata_datetime_format)
            shortname = dic["ShortName"]
        elif "AUX_SCS" in filename:
            if DEBUG:
                print("AUX_SCS file detected")
            filetype_str = "AUX_SCS"
            dic = parse_filename_wnd(os.path.splitext(os.path.splitext(filename)[0])[0])
            start_dt = datetime.datetime.strptime(dic["Validity_Start"], "%Y%m%dT%H%M%S")
            stop_dt = datetime.datetime.strptime("21000101T000000", "%Y%m%dT%H%M%S")
            start_good = datetime.datetime.strftime(start_dt, odata_datetime_format)
            stop_good = datetime.datetime.strftime(stop_dt, odata_datetime_format)
            crea_dt = datetime.datetime.strptime(dic['Generation_Date'], "%Y%m%dT%H%M%S")
            crea_good = datetime.datetime.strftime(crea_dt, odata_datetime_format)
            shortname = dic["ShortName"]
        elif "AUX_PREORB" in filename:
            if DEBUG:
                print("AUX_PREORB file detected")
            filetype_str = "AUX_PREORB_S1"
            dic = parse_filename_orb(os.path.splitext(os.path.splitext(filename)[0])[0])
            start_dt = datetime.datetime.strptime(dic["Validity_Start"], "%Y%m%dT%H%M%S")
            stop_dt = datetime.datetime.strptime(dic["Validity_Stop"], "%Y%m%dT%H%M%S")
            start_good = datetime.datetime.strftime(start_dt, odata_datetime_format)
            stop_good = datetime.datetime.strftime(stop_dt, odata_datetime_format)
            crea_dt = datetime.datetime.strptime(dic['Generation_Date'], "%Y%m%dT%H%M%S")
            crea_good = datetime.datetime.strftime(crea_dt, odata_datetime_format)
            shortname = dic["ShortName"]
        elif "AUX_RESORB" in filename:
            if DEBUG:
                print("AUX_RESORB file detected")
            if DEBUG:
                print("AUX_RESORB out of scope")
            continue
            filetype_str = "AUX_RESORB_S1"
            dic = parse_filename_orb(os.path.splitext(os.path.splitext(filename)[0])[0])
            start_dt = datetime.datetime.strptime(dic["Validity_Start"], "%Y%m%dT%H%M%S")
            stop_dt = datetime.datetime.strptime(dic["Validity_Stop"], "%Y%m%dT%H%M%S")
            start_good = datetime.datetime.strftime(start_dt, odata_datetime_format)
            stop_good = datetime.datetime.strftime(stop_dt, odata_datetime_format)
            crea_dt = datetime.datetime.strptime(dic['Generation_Date'], "%Y%m%dT%H%M%S")
            crea_good = datetime.datetime.strftime(crea_dt, odata_datetime_format)
            shortname = dic["ShortName"]
        elif "AUX_POEORB" in filename:
            if DEBUG:
                print("AUX_PREORB file detected")
            filetype_str = "AUX_POEORB_S1"
            dic = parse_filename_orb(os.path.splitext(os.path.splitext(filename)[0])[0])
            start_dt = datetime.datetime.strptime(dic["Validity_Start"], "%Y%m%dT%H%M%S")
            stop_dt = datetime.datetime.strptime(dic["Validity_Stop"], "%Y%m%dT%H%M%S")
            start_good = datetime.datetime.strftime(start_dt, odata_datetime_format)
            stop_good = datetime.datetime.strftime(stop_dt, odata_datetime_format)
            crea_dt = datetime.datetime.strptime(dic['Generation_Date'], "%Y%m%dT%H%M%S")
            crea_good = datetime.datetime.strftime(crea_dt, odata_datetime_format)
            shortname = dic["ShortName"]
        elif "AMH_ERRMAT" in filename:
            if DEBUG:
                print("AMH_ERRMAT file detected")
            filetype_str = "AMH_ERRMAT_MPC"
            dic = parse_filename_orb(os.path.splitext(os.path.splitext(filename)[0])[0])
            start_dt = datetime.datetime.strptime(dic["Validity_Start"], "%Y%m%dT%H%M%S")
            stop_dt = datetime.datetime.strptime(dic["Validity_Stop"], "%Y%m%dT%H%M%S")
            start_good = datetime.datetime.strftime(start_dt, odata_datetime_format)
            stop_good = datetime.datetime.strftime(stop_dt, odata_datetime_format)
            crea_dt = datetime.datetime.strptime(dic['Generation_Date'], "%Y%m%dT%H%M%S")
            crea_good = datetime.datetime.strftime(crea_dt, odata_datetime_format)
            shortname = dic["ShortName"]
        elif "AMV_ERRMAT" in filename:
            if DEBUG:
                print("AMV_ERRMAT file detected")
            filetype_str = "AMV_ERRMAT_MPC"
            dic = parse_filename_orb(os.path.splitext(os.path.splitext(filename)[0])[0])
            start_dt = datetime.datetime.strptime(dic["Validity_Start"], "%Y%m%dT%H%M%S")
            stop_dt = datetime.datetime.strptime(dic["Validity_Stop"], "%Y%m%dT%H%M%S")
            start_good = datetime.datetime.strftime(start_dt, odata_datetime_format)
            stop_good = datetime.datetime.strftime(stop_dt, odata_datetime_format)
            crea_dt = datetime.datetime.strptime(dic['Generation_Date'], "%Y%m%dT%H%M%S")
            crea_good = datetime.datetime.strftime(crea_dt, odata_datetime_format)
            shortname = dic["ShortName"]
        elif "AUX_RESATT" in filename:
            if DEBUG:
                print("AUX_RESATT file detected")
            filetype_str = "AUX_RESATT"
            dic = parse_filename_orb(os.path.splitext(os.path.splitext(filename)[0])[0])
            start_dt = datetime.datetime.strptime(dic["Validity_Start"], "%Y%m%dT%H%M%S")
            stop_dt = datetime.datetime.strptime(dic["Validity_Stop"], "%Y%m%dT%H%M%S")
            start_good = datetime.datetime.strftime(start_dt, odata_datetime_format)
            stop_good = datetime.datetime.strftime(stop_dt, odata_datetime_format)
            crea_dt = datetime.datetime.strptime(dic['Generation_Date'], "%Y%m%dT%H%M%S")
            crea_good = datetime.datetime.strftime(crea_dt, odata_datetime_format)
            shortname = dic["ShortName"]
        else:
            raise Exception("Filetype not detected : "+filename)

        filetype = None
        for type in filetype_dict:
            if filetype_str in type:
                filetype = type
                break
        if filetype is None:
            raise Exception("unknown file type")
        template["AuxType@odata.bind"] = "AuxTypes('" + filetype + "')"
        template["@odata.context"] = "$metadata#AuxFiles"
        if not update:
            template["Id"] = str(uuid.uuid4())
        template["FullName"] = filename.strip()
        template["ShortName"] = shortname
        template["Baseline"] = "03.40"
        template["IpfVersion"] = "S1-IPF-03.40"
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
