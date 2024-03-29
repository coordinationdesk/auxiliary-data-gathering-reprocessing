#!/bin/python
# -*- coding: utf-8 -*-

import argparse
import sys

from PRIP_S2 import get_lta_files_from_names
from AuxFilesListUtils import get_aux_names_from_file
import requests
import time
import os
import csv


def get_command_arguments():
    print("Called with command line: ", sys.argv)
    parser = argparse.ArgumentParser(description="This script extract the status of availability on AUXIP for all the files",  # main description for help
                                     epilog='Usage samples : \n\tpython PRIP_Ingestion.py -au auxip_username -apw password \n\n',
                                     formatter_class=argparse.RawTextHelpFormatter)  # displayed after help
    parser.add_argument("-lu", "--ltaurl",
                        help="Prip/Lta Endpoint Url",
                        required=True)
    parser.add_argument("-u", "--user",
                        help="LTA user",
                        required=True)
    parser.add_argument("-pw", "--password",
                        help="LTA password ",
                        required=True)
    parser.add_argument("-f", "--input_file",
                        help="Input file with Aux names list",
                        required=True)
    parser.add_argument("-o", "--output_file",
                        help="Output file with Auxip status",
                        required=True)
    args_values = parser.parse_args()

    return args_values

# Check if date has only date part
def only_date(date_str):
    return True

def main():
    requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
    args = get_command_arguments()
    # Read file with Aux names list
    aux_names = get_aux_names_from_file(args.input_file)
    # Check files against LTA: generate a list specifiying for each Aux file: if available on LTA, ID; checksum, checksum algo, checksum date

    try:
        lta_files = get_lta_files_from_names(args.user, args.password, args.ltaurl,
                              aux_names, 2)
        lta_names_list = [file[1].removesuffix(".TGZ") for file in lta_files]
        # Reorder fields in lta_files
        lta_status_files = [(rec[1].removesuffix(".TGZ"), *rec[2:4], rec[0]) for rec in lta_files]
        not_lta_files = [(aux_name, "NotAvailable") for aux_name in aux_names if aux_name not in lta_names_list]
        # combine the two lists and generate a single list; assign "NotAvailable" to files in second list
        overall_status = sorted(lta_status_files + not_lta_files, key=lambda x: x[0])
        with open(args.output_file, "w") as of:
            report_writer = csv.writer(of)

            for record in overall_status:
                report_writer.writerow(record)
    except Exception as e:
        print(e)
    print("LTA Files Status report completed")



if __name__ == "__main__":
    main()
