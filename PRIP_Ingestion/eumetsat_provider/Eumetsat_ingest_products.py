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
    args_values = parser.parse_args()

    return args_values

def get_aux_files_from_file(filepath):
    with open(filepath) as f:
        files = f.readlines()
    # you may also want to remove whitespace characters like `\n` at the end of each line
    files = [x.strip() for x in files if len(x)] 
    return files

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

        repository.download_day_products(day_folder, target)
    except Exception as e:
        print(e)
    print("End List")
    print("Ingested files ")


if __name__ == "__main__":
    main()
