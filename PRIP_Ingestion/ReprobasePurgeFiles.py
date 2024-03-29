#!/bin/python
# -*- coding: utf-8 -*-

import argparse
import sys

import time
import os
import csv
import requests

from ReproBase_query import remove_reprobase_files

def get_command_arguments():
    print("Called with command line: ", sys.argv)
    parser = argparse.ArgumentParser(description="This script removes  from Reprobase  the records for the files in a list (with specific UUID)",  # main description for help
                                     epilog='Usage samples : \n\tpython www.py -au auxip_username -apw password \n\n',
                                     formatter_class=argparse.RawTextHelpFormatter)  # displayed after help
    parser.add_argument("-au", "--auxipuser",
                        help="Auxip user",
                        required=True)
    parser.add_argument("-apw", "--auxippassword",
                        help="Auxip password ",
                        required=True)
    parser.add_argument("-m", "--mode",
                        help="Mode  (dev/prod)",
                        required=True)
    parser.add_argument("-f", "--input_file",
                        help="Input file with Reprobase Aux names list to search",
                        required=True)
    parser.add_argument("-o", "--output_file",
                        help="Output file with Reprobase Aux names list status (missing/available) (Reprobase Id when available)",
                        required=True)
    args_values = parser.parse_args()

    return args_values

# Check if date has only date part
def only_date(date_str):
    return True



def get_aux_names_ids_from_file(filepath):
    with open(filepath) as f:
        aux_reader = csv.reader(f, delimiter=" ")
        for aux_record in aux_reader:
            names_ids.append(aux_record)
    # you may also want to remove whitespace characters like `\n` at the end of each line
    return names_ids

def main():
    args = get_command_arguments()
    requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
    # Read file with Aux names list
    repro_id_names = get_aux_names_ids_from_file(args.input_file)
    # Check files against Reprobase: generate a list specifiying for each Aux file: if available on Reprobase, ID

    try:
        removed = remove_reprobase_files(args.auxipuser, args.auxippassword,
                                  repro_id_names,
                                  args.mode)
        out_file = f"{args.output_file}.removed"
        with open(out_file, "w") as of:
            report_writer = csv.writer(of)
            for fileid in removed:
                report_writer.writerow(fileid)

    except Exception as e:
        print(e)
    print("Files List Reprobase Files Status report completed")
    sys.exit(0)



if __name__ == "__main__":
    main()
