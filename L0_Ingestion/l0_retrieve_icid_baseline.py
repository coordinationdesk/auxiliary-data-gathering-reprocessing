#!/bin/python
# -*- coding: utf-8 -*-

import argparse
import re
import sys
import os
import csv
import requests
import datetime as dt

from l0_icid.L0_Icid_extract import L0IcidExtractor

OK = 0
KO = 1
# Read argumens:
#  Auxip Credentials,
# Archive/Storage Credentials
# Aux Type
#  Attribute name to be updated
# Day of work
# temporary folder

# Check if date has only date part
def only_date(date_str):
    return True
# Selection of files to be updated:
#  list of aux types
#   or
#  mission
#   or
#  list of Aux Files from file
#  publication or sensing date interval (from/to)
# what if date interval is not specified?
def get_command_arguments():
    print("Called with command line: ", sys.argv)
    parser = argparse.ArgumentParser(description="This script Retrieves from L0 Product the ICID attribute value ",
                                 epilog='Usage samples : \n\tpython .py -u username -pw password \n\n',
                                 formatter_class=argparse.RawTextHelpFormatter)  # displayed after help
    parser.add_argument("-lu", "--ltaurl",
                        help="Prip/Lta Endpoint Url",
                        required=False)
    parser.add_argument("-u", "--ltauser",
                        help="Prip user",
                        required=False)
    parser.add_argument("-pw", "--ltapassword",
                        help="Prip password ",
                        required=False)
    parser.add_argument("-mi", "--mission",
                        help="Single Mission to retrieve",
                        required=False)
    parser.add_argument("-n", "--numDays",
                        help="Num Days for L0 files",
                        required=False)
    parser.add_argument("-w", "--working",
                        help="Working folder",
                        required=True)
    parser.add_argument("-from", "--from_date",
                        help="Earliest Publication Date of files to be retrieved ",
                        required=False)
    parser.add_argument("-to", "--to_date",
                        help="Latest publication date of files to be retrieved",
                        required=False)
    parser.add_argument("-i", "--input_file",
                        help="Input file with Aux names list",
                        required=False)
    parser.add_argument("-m", "--mode",
                        help="dev or prod",
                        default="dev",
                        required=False)
    arg_values = parser.parse_args()

    if arg_values.input_file is None and \
          (arg_values.ltaurl is  None or arg_values.ltauser is None or arg_values.ltapassword is None):
        parser.error("LTA arguments shall be all specified, if you are not using input File")
    # time_date_pattern = re.compile("([0-9]{8}T[0-9]{6})")
    # Time date in format: year-month-daymonthThour:minutes:seconds
    time_date_pattern = re.compile(r"([0-9]{4})-([0-1][0-9])-([0-3][0-9])T([0-2][0-9]):([0-5][0-9]):([0-5][0-9])")
     # Date in format: year, month day of month
    date_pattern = re.compile("([0-9]{4})-([0-1][0-9])-([0-3][0-9])")
    print("Retrieving L0 ICID from date: ", arg_values.from_date)
    if arg_values.from_date is not None:
        if time_date_pattern.match(arg_values.from_date):
            print("From a date time: converting from string")
            from_datetime = dt.datetime.strptime(arg_values.from_date, '%Y-%m-%dT%H:%M:%S')
        elif date_pattern.match(arg_values.from_date):
            print("From a date (no time): converting from string")
            from_date_str = arg_values.from_date +  '000000'
            # TODO put under try/except to print error if format wrong
            from_datetime = dt.datetime.strptime(from_date_str, '%Y-%m-%d%H%M%S')
        else:
            print(date_pattern.match(arg_values.from_date))
            parser.error("From Date format:  YYYY-MM-DD or YYYY-MM-DDTHH:mm:SS")

        arg_values.from_datetime = from_datetime
    return arg_values

def main():
    args = get_command_arguments()
    requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
    mission=args.mission

    _default_num_days = 15
    num_days = args.numDays if args.numDays is not None else _default_num_days
    mission_l0_types = {
        'S1': ["RAW__0S"],
        'S2': ["MSI_L0__DS"],
        'S3': ["MW_0_MWR___", "OL_0_EFR___", "SL_0_SLT___", "SR_0_SRA___"]
    }
    mission_units = {
        'S1': ["S1A", "S1B"],
        'S2': ["S2A", "S2B"],
        'S3':  ["S3A", "S3B"]
    }
    # Define Publication Date interval

    to_date = args.to_date if args.to_date is not None else None
    if to_date and only_date(to_date):
        # Check if date contains Time part
        to_date += "T00:00:00Z"

    # TODO: Manage combination of
    #   Types being specified (no need to specify Mission)
    #  Mission being specified/not (if not specified, take all)
    #       Types to be retrieved for each Satellite Platform
    if args.mission:
        working_dir = os.path.join(args.working, args.mission)
    else:
        working_dir = args.working
    if not os.path.exists(working_dir):
        os.makedirs(working_dir)
    #attributes_to_update = ['instrumentConfigurationID']

    l0_list_file = args.input_file

    error_files = []
    global_result = OK

    try:
        # Instantiate LTA Client
        print("Starting retrieval of ICID for mission", args.mission)
        lta_retriever = L0IcidExtractor(args.mission, args.ltaurl, args.ltauser,
                                        args.ltapassword, num_days)
        # if input file is defined,get from input file
        # get validities from input file!!
        # Name, start, stop
        # in csv format
        name_id_list = []
        if l0_list_file is not None:
            with open(l0_list_file, "r") as fid:
                l0_names_reader = csv.reader(fid, delimiter=",")
                for l0_record in l0_names_reader:
                    if len(l0_record):
                        name_id_list.append(l0_record)
        else:
           # Retrieve Files for date interval
           # Extract from results pairs of name/id
           #  Get the first result for each day
            if 'from_datetime' in vars(args):
                from_date = args.from_datetime
            print("Loop")
            for l0_type in mission_l0_types[mission]:
                unit_list = mission_units[mission]
                name_id_list.extend ( lta_retriever.get_l0_names_ids(unit_list, from_date, l0_type))
        # Take N fiels at time
        # For each pair name/id
        for name, id, file_date in name_id_list:
            lta_retriever.download_lta_l0_product(name, id,
                                                  working_dir)
            #   Download files
            icid = lta_retriever.get_l0_icid(name, working_dir)
            print("Date ", file_date, ", File: ", name, ", ICID: ", icid)
        # Extract   ICID from downloaded files

    except Exception as e:
        print(e)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        # if conn:
        #     conn.rollback()
    sys.exit(global_result)

if __name__ == "__main__":
    main()
