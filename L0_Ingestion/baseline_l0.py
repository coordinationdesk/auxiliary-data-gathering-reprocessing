#!/bin/python
# -*- coding: utf-8 -*-

import argparse
import datetime as dt
import time
import sys
import re
import requests
from requests.auth import HTTPBasicAuth

from L0_lta_retriever import LtaL0Retriever
from baseline_l0_client import L0_NamesLoader

lta_baseurl = "aip.acri-st.fr"


def get_command_arguments():
    print("Called with command line: ", sys.argv)
    parser = argparse.ArgumentParser(description="This script allows you to upload to the Task 3 a listing of L0 files for Mission",  # main description for help
            epilog='\n\n', formatter_class=argparse.RawTextHelpFormatter)  # displayed after help
    parser.add_argument("-m", "--mission",
                        help="Mission for L0 files",
                        required=True)
    parser.add_argument("-i", "--inputFile",
                        help="Input listing file",
                        required=False)
    parser.add_argument("-n", "--numDays",
                        help="Num Days for L0 files",
                        required=False)
    L0_NamesLoader.add_arguments(parser)
    parser.add_argument("-lu", "--ltaurl",
                        help="Prip/Lta Endpoint Url",
                        required=False)
    parser.add_argument("-u", "--ltauser",
                        help="Prip user",
                        required=False)
    parser.add_argument("-pw", "--ltapassword",
                        help="Prip password ",
                        required=False)
    parser.add_argument("-fd", "--fromdate",
                        help="Ingest products from date ",
                        required=False)
    arg_values = parser.parse_args()
    print("Command line arguments: ", arg_values)
    if arg_values.inputFile is None and (arg_values.ltaurl is  None or arg_values.ltauser is None or arg_values.ltapassword is None):
        parser.error("LTA arguments shall be all specified, if you are not using input File")
    #date_pattern = re.compile("([0-9]{8}T[0-9]{6})")
    #date_pattern = re.compile("([0-9]{8}})")
    date_pattern = re.compile("([0-9]{4}})-([0-1][0-2])-([0-3][0-9])")
    print(arg_values.fromdate)
    if arg_values.fromdate is not None:
        from_date_str = arg_values.fromdate +  '000000'
        # TODO put under try/except to print error if format wrong
        from_datetime = dt.datetime.strptime(from_date_str, '%Y-%m-%d%H%M%S')
        arg_values.from_datetime = from_datetime
    # if arg_values.fromdate is not None and not date_pattern.match(arg_values.fromdate):
    #     print(date_pattern.match(arg_values.fromdate))
    #     parser.error("From Date format:  YYYYMMDD")
    # check that date is in correct format
    return arg_values


if __name__ == "__main__":

    args = get_command_arguments()
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
    try:
        l0_loader = L0_NamesLoader(mission, args)

        l0_list_file = args.inputFile

        # if input file is defined,get from input file
        # get validities from input file!!
        # Name, start, stop
        # in csv format
        if l0_list_file is not None:
            with open(l0_list_file, "r") as fid:
                for line in fid.readlines():
                    l0_validities = line.rstrip('\n').split(' ')
                    # S1B_IW_RAW__0SDV_20190822T145111_20190822T145143_017700_0214CF_EBA5.SAFE.zip
                    # start, stop = self._l0_name_parser.get_start_stop(l0_name)
                    l0_name, start, stop = l0_validities
                    l0_loader.add_l0_name(l0_name, start, stop)

        else:
            #if args.fromdate:
            #    # set time to 00:00:00
            #    from_datetime_str = args.fromdate+"000000"
            #    from_date = dt.datetime.strptime(from_datetime_str, '%Y%m%d%H%M%S')
            #    # TODO: set the same from date for all types
            # Get Max validity for all types related to mission
            lta_retriever = LtaL0Retriever(mission, args.ltaurl, args.ltauser, args.ltapassword, num_days)
            if 'from_datetime' in vars(args):
                from_date = args.from_datetime
                last_l0_type_table = {}
                for l0_type in mission_l0_types[mission]:
                    last_l0_type_table[l0_type] = {}
                    for unit in mission_units.get(mission):
                        last_l0_type_table[l0_type].update({unit: from_date})
            else:
                last_l0_type_table = l0_loader.get_l0_latest_validity()
            print("Last L0 validity for each Type for mission ", mission, ": ", last_l0_type_table)
            print("Loop")
            for l0_type in mission_l0_types[mission]:
                # for each satellite, or satellite_sensoor:
                print("L0 type ", l0_type)
                for unit, val_time in last_l0_type_table[l0_type].items():
                    # Get from LTA a list of L0 names, for N days (or up to today),
                    l0_products = lta_retriever.get_lta_l0_products(unit, l0_type, val_time)
                    print("Retrieved L0 names for unit: ", unit, ": ", [prod['Name'] for prod in l0_products])
                    # With N from command line, with default if not specified (or default got from config file)
                    # Add the l0 names to db
                    l0_loader.add_l0_products(l0_products)

    except Exception as e:
        print(e)
        # if conn:
        #     conn.rollback()
