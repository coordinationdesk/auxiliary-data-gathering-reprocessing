#!/bin/python
# -*- coding: utf-8 -*-

import argparse
import sys

import PRIP_S2
import time
import os
import requests
from ingestion.lib.auxip import are_file_availables
from AuxFilesListUtils import get_aux_names_from_file


lta_baseurl = "https://aip.acri-st.fr/odata/v1/"

def get_command_arguments():
    print("Called with command line: ", sys.argv)
    parser = argparse.ArgumentParser(description="This script poll the PRIP all the files",  # main description for help
                                     epilog='Usage samples : \n\tpython PRIP_Ingestion.py -u username -pw password \n\n',
                                     formatter_class=argparse.RawTextHelpFormatter)  # displayed after help
    parser.add_argument("-au", "--auxipuser",
                        help="Auxip user",
                        required=True)
    parser.add_argument("-apw", "--auxippassword",
                        help="Auxip password ",
                        required=True)
    parser.add_argument("-f", "--input_file",
                        help="Input file with Aux names list",
                        required=True)
    args_values = parser.parse_args()

    return args_values

# Check if date has only date part
def only_date(date_str):
    return True

def main():
    args = get_command_arguments()
    requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

    # Extract names list from input file
    # Open file
    # Extract aux names list
    aux_names = get_aux_names_from_file(args.input_file)
    auxip_list = []
    try:
        # TOKEN retrieved by PRIP_S2.prip_list.
        # ALternatively, pass token as argument instead of user/passowrd
        auxip_list = are_file_availables( args.auxipuser, args.auxippassword,
                        aux_names,step=10, mode="prod")
    except Exception as e:
        print(e)

    auxip_list.sort()
    print("Number of already present files: ", len(auxip_list))
    for f in auxip_list:
        print(f)
    auxip_prod_unique = set(auxip_list)
    print("Numerb of unique files already present: ", len(auxip_prod_unique))
    print("Number of requested files: ", len(aux_names))


if __name__ == "__main__":
    main()
