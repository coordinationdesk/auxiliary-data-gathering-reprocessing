#!/bin/python
# -*- coding: utf-8 -*-

import argparse
import sys

import time
import os
import csv
import requests

from ReproBase_query import get_reprobase_files_from_names
from AuxFilesListUtils import get_aux_names_from_file

def get_command_arguments():
    print("Called with command line: ", sys.argv)
    parser = argparse.ArgumentParser(description="This script extract the status of availability on Reprobase for the files in a list",  # main description for help
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

def reprobase_group_by_filename(reprobase_list):
    repro_dict = {}
    for repro_id, repro_filename, *other in reprobase_list:
        print("Id: ", repro_id, ", fullname: ", repro_filename)
        repro_dict.setdefault(repro_filename.strip(), []).append(repro_id)
    return repro_dict

def reprobase_list_from_names(auxip_user, auxip_password,
                              mode,aux_names,
                              out_file_basename):
    # List of pairs ID, filename for files present in Reprobase
    reprobase_files = get_reprobase_files_from_names(auxip_user, auxip_password,
                                                     aux_names, mode)
    repro_file = f"{out_file_basename}.reprobase_avail"
    with open(repro_file, "w") as repro_of:
        repro_writer = csv.writer(repro_of)
        for rep_rec in sorted(reprobase_files, key=lambda x: x[1]):
            repro_writer.writerow(rep_rec)
    repro_avail_names_list = [file[1].strip() for file in reprobase_files]
    missing_names = [name for name in aux_names if name not in repro_avail_names_list]
    missing_names_status = {("Not Available", name) for name in missing_names}

    # Write file with list of filenames missing from Reprobase
    repro_missing_file = f"{out_file_basename}.reprobase_missing"
    with open(repro_missing_file, "w") as repro_m_of:
        for rep_rec in sorted(missing_names):
            repro_m_of.write(rep_rec)
            repro_m_of.write('\n')

    # Write file with status for each filename in input list (ID or not available)
    overall_status = sorted(reprobase_files + list(missing_names_status), key=lambda x: x[1])
    print("Writing Auxip Files status on Reprocessing Baseline to file: ", out_file_basename)
    with open(out_file_basename, "w") as of:
        report_writer = csv.writer(of)
        for record in overall_status:
            report_writer.writerow(record)
    reprobase_dups = reprobase_group_by_filename(reprobase_files)
    dups_filename = f"{out_file_basename}_duplicates"
    print("Writing Auxip Files Reprocessing Baseline duplicate records to file: ", dups_filename)
    with open(dups_filename, "w") as odf:
        df_report_writer = csv.writer(odf)
        for dup_fullname in reprobase_dups:
            # Write as duplicates only files that have more than one occurrence in Reprobase
            dup_id_list = reprobase_dups[dup_fullname]
            print("FullName: ", dup_fullname, ", list of ids: ", reprobase_dups[dup_fullname])
            if len(dup_id_list) > 1:
                df_report_writer.writerow((dup_fullname, dup_id_list))

def main():
    args = get_command_arguments()
    requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
    # Read file with Aux names list
    aux_names = get_aux_names_from_file(args.input_file)
    # Check files against Reprobase: generate a list specifiying for each Aux file: if available on Reprobase, ID

    try:
        reprobase_list_from_names(args.auxipuser, args.auxippassword,
                                  args.mode,
                                  aux_names,
                                  args.output_file)

    except Exception as e:
        print(e)
    print("Files List Reprobase Files Status report completed")
    sys.exit(0)



if __name__ == "__main__":
    main()
