#!/bin/python
# -*- coding: utf-8 -*-

import argparse
import sys

from ingestion.lib.auxip import available_files_status
from AuxFilesListUtils import get_aux_names_from_file

import time
import os
import csv


def get_command_arguments():
    print("Called with command line: ", sys.argv)
    parser = argparse.ArgumentParser(description="This script extract the status of availability on AUXIP for all the files",  # main description for help
                                     epilog='Usage samples : \n\tpython PRIP_Ingestion.py -au auxip_username -apw password \n\n',
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
    parser.add_argument("-o", "--output_file",
                        help="Output file with Auxip status",
                        required=True)
    args_values = parser.parse_args()

    return args_values

# Check if date has only date part
def only_date(date_str):
    return True

def main():
    args = get_command_arguments()
    # Read file with Aux names list
    aux_names = get_aux_names_from_file(args.input_file)
    # Check files against AUXIP: generate a list specifiying for each Aux file: if available on AUXIP, checksum, checksum algo, checksum date

    try:
        auxip_files_status = available_files_status( args.auxipuser, args.auxippassword,
                                                 aux_names, step=10,
                                                 mode="prod")
        auxip_file = f"{args.output_file}.auxip_avail"
        with open(auxip_file, "w") as auxip_of:
            aux_writer = csv.writer(auxip_of)
            for au_rec in auxip_files_status:
                aux_writer.writerow(au_rec)
        auxip_names_status_list = [(os.path.splitext(file[0])[0], *(file[1:])) for file in auxip_files_status]
        auxip_names_list = [file[0].strip() for file in auxip_names_status_list]
        not_auxip_files = [(aux_name, "NotAvailable") for aux_name in aux_names if aux_name.strip() not in auxip_names_list]
        # combine the two lists and generate a single list; assign "NotAvailable" to files in second list
        overall_status = sorted(auxip_names_status_list + not_auxip_files, key=lambda x: x[0])
        with open(args.output_file, "w") as of:
            report_writer = csv.writer(of)

            for record in overall_status:
                report_writer.writerow(record)

    except Exception as e:
        print(e)
    print("Auxip Files Status report completed")
    sys.exit(0)



if __name__ == "__main__":
    main()
