# -*- coding: utf-8 -*-

import argparse
import sys

import time
import os
import EumetsatRepository as Eumet


def get_command_arguments():
    print("Called with command line: ", sys.argv)
    parser = argparse.ArgumentParser(description="This script downloads from FTP the files listed in the input file to the specified folder ",  # main description for help
                                     epilog='Usage samples : \n\tpython LTA_FTP_Repo_AuxFilesDownload.py -fh FtpHost -u ftp_username -pw ftp_password \n\n',
                                     formatter_class=argparse.RawTextHelpFormatter)  # displayed after help
    parser.add_argument("-fh", "--ftphost",
                        help="ftp host",
                        required=True)
    parser.add_argument("-u", "--user",
                        help="FTP user",
                        required=True)
    parser.add_argument("-pw", "--password",
                        help="FTP password ",
                        required=True)
    parser.add_argument("-sf", "--start_folder",
                        help="FTP Start Folder ",
                        required=True)
    parser.add_argument("-d", "--day",
                        help="Day of products to be listed",
                        required=True)
    parser.add_argument("-w", "--out_folder",
                        help="Folder where to download FTP files",
                        required=True)
    parser.add_argument("-l", "--list_only",
                        help="Flag: if set, do not download, bug generate repository listing ",
                        default=False,
                        required=False,
                        action='store_true')
    args_values = parser.parse_args()

    return args_values

def get_aux_files_from_file(filepath):
    with open(filepath) as f:
        files = f.readlines()
    # you may also want to remove whitespace characters like `\n` at the end of each line
    files = [x.strip() for x in files if len(x)] 
    return files

def save_aux_files_list(folderpath, list_date, aux_files_list):
    # Open target file
    out_file= os.path.join(folderpath, f"Repository_files_{list_date}.list")
    with open(out_file, "w") as of:
        # Write files in input list, one per line
        for aux_file in aux_files_list:
            print(aux_file, file=of)

def main():
    args = get_command_arguments()
    hostname=args.ftphost
    ftpuser=args.user
    ftppwd=args.password
    target=args.out_folder
    product_day=args.day
    day_folder = args.day
    # Download files from list from FTP
    try:
        repository = Eumet.FtpRepository(hostname,
                                         ftpuser, ftppwd,
                                         args.start_folder, user_home=True)
        if not args.list_only:
            repository.download_day_products(day_folder, target)
        else:
            day_aux_files = repository.list_day_products(day_folder)
            # Save files to output file
            save_aux_files_list(target, product_day, day_aux_files)
            print("\n".join(day_aux_files))
    except Exception as e:
        print(e)
    print("End List")
    if not args.list_only:
        print("Ingested files ")


if __name__ == "__main__":
    main()
