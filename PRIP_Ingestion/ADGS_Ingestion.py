#!/bin/python
# -*- coding: utf-8 -*-

import argparse
import sys

import time
import os
import csv
import requests
from datetime import datetime

from mission_aux_types import retrieve_aux_type_names
from FileUtils import save_tuples_to_file, save_list_to_file
import ADGS_Retrieval
from ADGS_Retrieval import ADGS_Authentication

 

def get_command_arguments():
    print("Called with command line: ", sys.argv)
    parser = argparse.ArgumentParser(description="This script poll the ADGS all the files",  # main description for help
                                     epilog='Usage samples : \n\tpython ADGS_Ingestion.py -u username -pw password \n\n',
                                     formatter_class=argparse.RawTextHelpFormatter)  # displayed after help
    parser.add_argument("-lu", "--ltaurl",
                        help="ADGS/Lta Endpoint Url",
                        required=True)
    parser.add_argument("-u", "--user",
                        help="ADGS user",
                        required=True)
    parser.add_argument("-pw", "--password",
                        help="ADGS password ",
                        required=True)
    parser.add_argument("-s", "--secret",
                        help="ADGS secret ",
                        required=False)
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
    parser.add_argument("-tf", "--filetypes_file",
                        help="File containing filetypes names",
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
    parser.add_argument("-o", "--output", 
                        help="Output file to hold list of files found on ADGS",
                        required=True)
    parser.add_argument("-l", "--list_only",
                        help="Only list files without downloading them (FALSE if not specified)",
                        required=False,
                        default=False,
                        action='store_true')
    # TODO: Add optional argument: list of filetypes
    #    Alternative to FD
    args_values = parser.parse_args()
    if args_values.types is None and args_values.filetypes_dir is None and args_values.filetypes_file is None:
        parser.print_usage()
        raise Exception("Expected argument Filetypes Directory, Filetypes names File, or a list of types")

    if args_values.secret is None:
        print("Secret was not provided")

    return args_values

# Check if date has only date part
def only_date(date_str):
    return True


def get_aux_types_from_file(filepath):
    auxtypes = []
    with open(filepath, "r") as at_in:
         aux_lines = at_in.readlines()
    return [name.strip() for name in aux_lines]
    
def main():
    args = get_command_arguments()
    requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
    lta_baseurl = args.ltaurl
    print("Accessing LTA/ADGS ", lta_baseurl)
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

    # TOKEN retrieved by ADGS_Retrieval.prip_list.
    # ALternatively, pass token as argument instead of user/passowrd
    adgs_authenticator = ADGS_Authentication(args.user, args.password, args.secret)
    # TODO: Retrieve list of TYPES
    # If Filetypes Dir was defined and Aux Types was not defined, retrieve list of Axu Types
    #  Otherwise, use Aux Types list specified on Command Line
    if args.types is None:
        if args.filetypes_dir is None and args.filetypes_file is not None:
            aux_types = get_aux_types_from_file(args.filetypes_file)
        else:
            aux_types = retrieve_aux_type_names(satellite_platform, args.filetypes_dir)
    else:
        print("From cmd line: ", args.types)
        aux_types = args.types

    for satellite_platform in mission_list:
        print("Mission ", satellite_platform, " - Retrieving from LTA file types: ", aux_types)
        for t in aux_types:
            print("Processing type ", t)
            if satellite_platform == 'S1':
                if t == "AUX_POEORB_S1":
                    t = "AUX_POEORB"
                if t == "AUX_PREORB_S1":
                    t = "AUX_PREORB"

            try:
                prip_list = ADGS_Retrieval.adgs_list(adgs_authenticator,
                                              args.auxipuser, args.auxippassword,
                                              lta_baseurl, [t],
                                              sat=satellite_platform, mode="prod",
                                              from_date=from_date, to_date=to_date)
            except Exception as e:
                print(e)
                # Try again after 5 secs
                time.sleep(5)
                try:
                    prip_list = ADGS_Retrieval.adgs_list(adgs_authenticator,
                                                  args.auxipuser, args.auxippassword,
                                                  lta_baseurl, [t],
                                                  sat=satellite_platform, mode="prod",
                                                  from_date=from_date, to_date=to_date)
                except Exception as ex:
                    print("Failed getting list of Aux files of type {}".format(t))
                    prip_list = []

            print("Mission ", satellite_platform, ", Type ", t, ": Number of ADGS Files found on ADGS: ", len(prip_list))
            print("Retrieve AUX Files: ", prip_list)
            if not args.list_only:
                working_dir = os.path.join(args.working, satellite_platform)
                if not os.path.exists(working_dir):
                    os.makedirs(working_dir)
                list_dir = os.path.join(f"{args.working}_lists", f"{satellite_platform}")
                if not os.path.exists(list_dir):
                    os.makedirs(list_dir)
                o_file = os.path.join(list_dir, f"{args.output}_{t}")
                print("Saving type ", t, " files list to out file ", o_file)
                # Add filenames list to ADGS Retrieved file
                save_list_to_file(prip_list, o_file)
                dwl_counter = 0
                # Extract list of files to be downloaded, filtering by third field in tuple
                # TODO: convert tuple to dataclass or namedtuple
                # Tuple: file_adgs_id, file_name, auxip_availble_flag, checksum
                adgs_files_to_download = [adgs_file for adgs_file in prip_list if not adgs_file[2] ]
                print("{} files to download from ADGS/LTA".format(len(adgs_files_to_download)))
                print(adgs_files_to_download)
                for file_id, file_name, *_ in adgs_files_to_download:
                    print("File ", file_id, ", name: ", file_name)
                    try:
                        ADGS_Retrieval.prip_download(file_id, file_name,
                                              adgs_authenticator,
                                              lta_baseurl, working_dir)
                        dwl_counter += 1
                        print("Downloaded ", dwl_counter, "/", len(prip_list))
                    except Exception as ex:
                        print("Failed downloading product file {}".format(file_name))
                        # TODO: Save failed to download filename to failed lsit file
            else:
                print("Found ", len(prip_list), " files for Type ", t, ": \n", "\n".join((str(prip_item) for prip_item in prip_list)))
                print("End List")
                today_timestamp = datetime.strftime(datetime.utcnow(), "%Y-%m-%d_%H%M")
                # Save list files to parent folder, to avoid mixing files to ingest and support fiels
                o_file = os.path.join(args.working, f"{args.output}_{t}_{today_timestamp}")
                save_list_to_file(prip_list, o_file)
                avail_files = [(prip_file[1], "Available" if prip_file[2] else "Missing") for prip_file in prip_list]
                save_tuples_to_file(avail_files, o_file)
        print("Acquired files for mission ", satellite_platform)
        sys.exit(0)


if __name__ == "__main__":
    main()
