#!/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import argparse
import uuid as UUID
#import threading
import time

from lib.auxip import post_to_auxip,get_token_info,refresh_token_info,are_file_availables
from lib.wasabi import upload_to_wasabi

OK = 0
KO = 1


def upload_and_post(thread_id,path_to_mc,bucket,auxip_user,auxip_password,listing,listing_out,mode="dev"):
    global_status = OK
    token_info = get_token_info(auxip_user, auxip_password,mode=mode)
    # access_token = token_info['access_token']
    with open("report_thread_%d.txt" % thread_id,"w") as report:
        timer_start = time.time()
        access_token = token_info['access_token']
        for path_to_auxfile in listing:
            # Generate the uuid for this aux data
            uuid = str(UUID.uuid4())
            # upload it to wasabi
            if upload_to_wasabi(path_to_mc,bucket,path_to_auxfile,uuid,mode) == OK:
                print("%s ==> uploaded to wasabi successfully with : %s " % (path_to_auxfile,uuid) )
                # refesh token if necessary 
                timer_stop = time.time()
                elapsed_seconds = timer_stop - timer_start
                if elapsed_seconds > 300:
                    timer_start = time.time()
                    token_info = get_token_info(auxip_user, auxip_password,mode=mode)
                    access_token = token_info['access_token']
                # do a post to auxip.svc if the upload to wasabi is OK
                if post_to_auxip(access_token,path_to_auxfile,uuid,mode) == OK:
                    message = "%s : %s\tupload_to_wasabi : OK; post_to_auxip : OK\n" % (path_to_auxfile,uuid)
                    listing_out.append(os.path.basename(path_to_auxfile))
                else:
                    global_status = KO
                    print("%s ==> Failure posting to AUXIP" % path_to_auxfile)
                    message = "%s : %s\tupload_to_wasabi : OK; post_to_auxip : KO\n" % (path_to_auxfile,uuid)
            else:
                global_status = KO
                print("%s ==> Failed upload to Wasabi with : %s " % (path_to_auxfile,uuid) )
                message = "%s : %s\tupload_to_wasabi : KO; post_to_auxip : NO VALID UUID\n" % (path_to_auxfile,uuid)

            report.write(message)
    print("Exiting upload_and_post with status ", global_status)
    return global_status


def ingest(auxiliary_data_files, auxip_user, auxip_password, path_to_mc, output_list,mode="dev",
           bucket="auxip_s3/auxip"):

    # =======================================================================
    #               EGNORE ALREADY UPLOADED AUX FILES
    # =======================================================================
    auxiliary_data_filenames = [name for name in auxiliary_data_files.keys()]

    # get token_info
    timer_start = time.time()
    # Get Token either here or in upload_and_post
    # token_info = get_token_info(auxip_user, auxip_password,mode=mode)
    # access_token = token_info['access_token']
    # Create listings
    not_yet_uploaded = []
    print("Testing files in auxip or not ...")
    availables = are_file_availables(auxip_user,auxip_password,auxiliary_data_filenames,5,mode)
    print("Availables: "+str(len(availables)))
    for i in auxiliary_data_filenames:
        if i not in availables:
            not_yet_uploaded.append(auxiliary_data_files[i])
    print(str(len(not_yet_uploaded))+" files not in auxip")
    uploaded = []
    global_status = OK
    if len(not_yet_uploaded) > 0:
        global_status = upload_and_post(1, path_to_mc, bucket, auxip_user, auxip_password, not_yet_uploaded, uploaded, mode)
    else:
        print("No new auxiliary data file found in the input folder")
    with open(output_list, mode="w") as l:
        for i in uploaded:
            l.write(i + "\n")
        l.close()
    if global_status == KO:
        exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="",  # main description for help
            epilog='Beta', formatter_class=argparse.RawTextHelpFormatter)  # displayed after help
    parser.add_argument("-i", "--input",
                        help="input folder were to look for new auxiliary data files",
                       required=True)
    parser.add_argument("-u", "--user",
                        help="Auxip user with reporting role",
                        required=True)
    parser.add_argument("-pw", "--password",
                        help="User password ",
                        required=True)
    parser.add_argument("-mc", "--path_to_mc",
                        help="Path to mc program",
                        default="/data/mc",
                        required=False)
    parser.add_argument("-b", "--bucket",
                        help="Name of mc bucket",
                        default="auxip_s3/auxip",
                        required=False)
    parser.add_argument("-m", "--mode",
                        help="dev or prod",
                        default="dev",
                        required=False)
    parser.add_argument(
            "-o",
            "--output",
            help="Output data directory (product directory). Default value: '.'",
            required=True)
    args = parser.parse_args()

    # =======================================================================
    #               CREATE AUXILIARY DATA FILES LISTING WITHOUT DUPLICATION
    # =======================================================================
    print("Listing files ...")
    auxiliary_data_files = {}
    for root, folders, files in os.walk(args.input):
        for name in files:
            # auxiliary_data_files.append(os.path.join(root,name))
            auxiliary_data_files[name] = os.path.join(root, name)
    print("Done")
    if len(auxiliary_data_files):
        ingest(auxiliary_data_files, args.user, args.password, args.path_to_mc,args.output,args.mode, args.bucket)
    else:
        print("No auxiliary data files downloaded to ingest in folder ", args.input)

