#!/bin/python
# -*- coding: utf-8 -*-

import argparse
import sys

import PRIP_S2
import time
import os
import requests

from mission_aux_types import retrieve_aux_type_names

lta_baseurl = "https://aip.acri-st.fr/odata/v1/"

def get_command_arguments():
    print("Called with command line: ", sys.argv)
    parser = argparse.ArgumentParser(description="This script poll the PRIP all the files",  # main description for help
                                     epilog='Usage samples : \n\tpython PRIP_Ingestion.py -u username -pw password \n\n',
                                     formatter_class=argparse.RawTextHelpFormatter)  # displayed after help
    parser.add_argument("-u", "--user",
                        help="Prip user",
                        required=True)
    parser.add_argument("-pw", "--password",
                        help="Prip password ",
                        required=True)
    parser.add_argument("-au", "--auxipuser",
                        help="Auxip user",
                        required=True)
    parser.add_argument("-apw", "--auxippassword",
                        help="Auxip password ",
                        required=True)
    parser.add_argument("-w", "--working",
                        help="Working folder",
                        required=True)
    parser.add_argument("-fd", "--filetypes_dir",
                        help="Folder containing filetypes jsons",
                        required=False)
    parser.add_argument("-t", "--types", nargs="*",
                        help="List of types to be ingested",
                        required=False)
    parser.add_argument("-m", "--mission",
                        help="Single Mission to retrieve",
                        required=False)
    parser.add_argument("-from", "--from_date",
                        help="Earliest Publication Date of files to be retrieved ",
                        required=False)
    parser.add_argument("-to", "--to_date",
                        help="Latest publication date of files to be retrieved",
                        required=False)
    parser.add_argument("-l", "--list_only",
                        help="Only list files without downloading them (FALSE if not specified)",
                        required=False,
                        default=False,
                        action='store_true')
    # TODO: Add optional argument: list of filetypes
    #    Alternative to FD
    args_values = parser.parse_args()
    if args_values.types is None and args_values.filetypes_dir is None:
        parser.print_usage()
        raise Exception("Expected argument Filetypes Directory")

    return args_values

# Check if date has only date part
def only_date(date_str):
    return True

def main():
    args = get_command_arguments()
    requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
    mission_list = ['S1', 'S2', 'S3']
    # Define Publication Date interval
    from_date = args.from_date if args.from_date is not None else None
    if from_date and only_date(from_date):
        # Check if date contains Time part
        from_date += "T00:00:00Z"

    to_date = args.to_date if args.to_date is not None else None
    if to_date and only_date(to_date):
        # Check if date contains Time part
        to_date += "T00:00:00Z"

    # TODO: naMage combination of
    #   Types being specified (no need to specify Mission)
    #  Mission being specified/not (if not specified, take all)
    #       Types to be retrieved for each Satellite Platform
    if args.mission is not None:
        mission_list = [args.mission]

    for satellite_platform in mission_list:
        # If Filetypes Dir was defined and Aux Types was not defined, retrieve list of Axu Types
        #  Otherwise, use Aux Types list specified on Command Line
        if args.types is None:
            aux_types = retrieve_aux_type_names(satellite_platform, args.filetypes_dir)
        else:
            aux_types = args.types
        print("Mission ", satellite_platform, " - Retrieving from LTA file types: ", aux_types)
        for t in aux_types:
            if satellite_platform == 'S1':
                if t == "AUX_POEORB_S1":
                    t = "AUX_POEORB"
                if t == "AUX_PREORB_S1":
                    t = "AUX_PREORB"

            try:
                # TOKEN retrieved by PRIP_S2.prip_list.
                # ALternatively, pass token as argument instead of user/passowrd
                prip_list = PRIP_S2.prip_list(args.user, args.password,
                                              args.auxipuser, args.auxippassword,
                                              lta_baseurl, [t],
                                              sat=satellite_platform, mode="prod",
                                              from_date=from_date, to_date=to_date)
            except Exception as e:
                print(e)
                # Try again after 5 secs
                time.sleep(5)
                prip_list = PRIP_S2.prip_list(args.user, args.password,
                                              args.auxipuser, args.auxippassword,
                                              lta_baseurl, [t],
                                              sat=satellite_platform, mode="prod",
                                              from_date=from_date, to_date=to_date)

            print("Mission ", satellite_platform, ", Type ", t, ": Number of PRIP File : ", len(prip_list))
            if not args.list_only:
                working_dir = os.path.join(args.working, satellite_platform)
                if not os.path.exists(working_dir):
                    os.makedirs(working_dir)
                print("{} files to download from LTA".format(len(prip_list)))
                for file_id, file_name, file_size in prip_list:
                    print("File ", file_id, ", name: ", file_name)
                    PRIP_S2.prip_download(file_id, file_name,
                                          args.user, args.password,
                                          lta_baseurl, working_dir)
                    print("Downloaded")
            else:
                print("Found files for Type ", t, ": \n", "\n".join((str(prip_item) for prip_item in prip_list)))
                print("End List")
        print("Ingested files for mission ", satellite_platform)


if __name__ == "__main__":
    main()
