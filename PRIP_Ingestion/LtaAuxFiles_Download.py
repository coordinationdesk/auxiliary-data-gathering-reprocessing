#!/bin/python
# -*- coding: utf-8 -*-

import argparse
import sys

import PRIP_S2
import time
import os
import requests
from AuxFilesListUtils import get_aux_names_from_file

#lta_baseurl = "https://aip.acri-st.fr/odata/v1/"

def get_command_arguments():
    print("Called with command line: ", sys.argv)
    parser = argparse.ArgumentParser(description="This script poll the PRIP all the files",  # main description for help
                                     epilog='Usage samples : \n\tpython PRIP_Ingestion.py -u username -pw password \n\n',
                                     formatter_class=argparse.RawTextHelpFormatter)  # displayed after help
    parser.add_argument("-lu", "--ltaurl",
                        help="Prip/Lta Endpoint Url",
                        required=True)
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
                        required=False)
    parser.add_argument("-f", "--input_file",
                        help="Input file with Aux names list",
                        required=True)
    parser.add_argument("-l", "--list_only",
                        help="Only list files without downloading them (FALSE if not specified)",
                        required=False,
                        default=False,
                        action='store_true')
    # TODO: Add optional argument: list of filetypes
    #    Alternative to FD
    args_values = parser.parse_args()

    return args_values

# Check if date has only date part
def only_date(date_str):
    return True

def main():
    args = get_command_arguments()
    requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
    lta_baseurl = args.ltaurl
    # Read file with Aux names list
    aux_names = get_aux_names_from_file(args.input_file)
    # Read From LTA list of Files ID's and Checksum/method
    # Check files against AUXIP: generate two lists: already existing, to be ingested
    # If not only list, download files
    # Ingest on AUXIP, Reprobase

    try:
        # TOKEN retrieved by PRIP_S2.prip_list.
        # ALternatively, pass token as argument instead of user/passowrd
        prip_list = PRIP_S2.prip_list_from_names(args.user, args.password,
                          args.auxipuser, args.auxippassword,
                          lta_baseurl, aux_names,
                          mode="prod")
    except Exception as e:
        print(e)
        # Try again after 5 secs
        time.sleep(5)
        prip_list = PRIP_S2.prip_list_from_names(args.user, args.password,
                          args.auxipuser, args.auxippassword,
                          lta_baseurl, aux_names,
                          mode="prod")

    print("Number of Aux Files to ingest: ", len(prip_list))
    print("Number of Requested aux_files : ", len(aux_names))
    if not args.list_only:
        working_dir = os.path.join(args.working, 'S2')
        if not os.path.exists(working_dir):
            os.makedirs(working_dir)
        print("Files to download from LTA", prip_list)
        for file_id, file_name, *_ in prip_list:
            print()
            print("File ", file_id, ", name: ", file_name)
            PRIP_S2.prip_download(file_id, file_name,
                  args.user, args.password,
                  lta_baseurl, working_dir)
            print("Downloaded")
    else:
       print("Found files to be ingested: \n ", "\n".join((str(prip_item[1]) for prip_item in prip_list)))
    print("End List")
    print("Ingested files for mission ", 'S2')


if __name__ == "__main__":
    main()
