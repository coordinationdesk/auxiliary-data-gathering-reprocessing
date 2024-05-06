#!/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import argparse
import uuid as UUID
#import threading
import time
import csv

from lib.auxip import post_to_auxip,get_token_info,refresh_token_info,available_files_status
from lib.auxip_rm import remove_from_auxip
from lib.wasabi import upload_to_wasabi, remove_from_wasabi

OK = 0
KO = 1

code_result = {
0: "OK",
1: "KO"
}

def upload_and_post_replace(thread_id,
                            path_to_mc, bucket,
                            auxip_user, auxip_password,
                            files_list,
                            files_uuids,
                            replaced_files, failures, mode="dev"):
    print("Uploading and posting to auxip to replace available, mode: ", mode)
    # Files to replace are files in the input folder
    # files_uuids is a table with fileanmes associated to current available aux files UUIDs
    # replaced files is a list of files that have been ingested/replaced
    # failures  is a list of files that could not be ingested/replaced (kept)
                # (g["Name"], file_cksum, cksum_alg, cksum_date, file_size, file_id)
    global_status = OK
    token_info = get_token_info(auxip_user, auxip_password,mode=mode)
     
    with open("report_thread_%d.txt" % thread_id,"w") as report:
        timer_start = time.time()
        access_token = token_info['access_token']
        for path_to_auxfile in files_list:
            filename = os.path.basename(path_to_auxfile)
            # get current UUID from uuid table
            avail_uuid = files_uuids.get(filename)
            # Generate the uuid for this aux data
            new_file_uuid = str(UUID.uuid4())
            # upload it to wasabi
            if upload_to_wasabi(path_to_mc,bucket,path_to_auxfile,new_file_uuid,mode) == OK:
                print("%s ==> uploaded to wasabi successfully with : %s " % (path_to_auxfile,new_file_uuid) )
                # refesh token if necessary 
                timer_stop = time.time()
                elapsed_seconds = timer_stop - timer_start
                if elapsed_seconds > 300:
                    timer_start = time.time()
                    token_info = get_token_info(auxip_user, auxip_password,mode=mode)
                    access_token = token_info['access_token']
                # do a post to auxip.svc if the upload to wasabi is OK
                if post_to_auxip(access_token,path_to_auxfile,new_file_uuid,mode) == OK:
                    message = "%s : %s\tupload_to_wasabi : OK; post_to_auxip : OK\n" % (path_to_auxfile,new_file_uuid)
                    replaced_files.append(filename)
                    # REMOVE currently available file with avail_uuid
                    auxip_res = remove_from_auxip(access_token, filename, avail_uuid, mode) 
                    if auxip_res == OK:
                        print("%s ==> Removed previous version from AUXIP" % filename)
                    else:
                        global_status = KO
                        print("%s ==> Failure deleteing previous version from AUXIP, Id: %s" % (filename, avail_uuid))
                    wasabi_res = remove_from_wasabi(path_to_mc, bucket, filename, avail_uuid, mode) 
                    if wasabi_res == OK:
                        print("%s ==> removed previous version from wasabi successfully with : %s " % (filename, avail_uuid) )
                    else:
                        global_status = KO
                        print("%s ==> Failed remove previous version from Wasabi with : %s " % (filename, avail_uuid) )
        
                    message = "%s : %s\tremove_from_wasabi : %s; remove_from_auxip : %s\n" % (filename,avail_uuid, code_result[wasabi_res], code_result[auxip_res])
                    report.write(message)
                else:
                    global_status = KO
                    print("%s ==> Failure posting to AUXIP" % path_to_auxfile)
                    # REMOVE just uploaded file with new uud
                    remove_from_wasabi(path_to_mc,bucket,filename,new_file_uuid,mode)
                    # Add file to failures
                    failure = "%s : %s\tupload_to_wasabi : OK; post_to_auxip : KO \n" % (path_to_auxfile,new_file_uuid)
                    # write failure to file? 
                    failures.append(path_to_auxfile)

                    
            else:
                global_status = KO
                print("%s ==> Failed upload to Wasabi with : %s " % (path_to_auxfile,uuid) )
                message = "%s : %s\tupload_to_wasabi : KO; post_to_auxip : NO VALID UUID\n" % (path_to_auxfile,uuid)

            report.write(message)
    print("Exiting upload_and_post with status ", global_status)
    return global_status

def upload_and_post(thread_id,path_to_mc,bucket,auxip_user,auxip_password,listing,listing_out,mode="dev"):
    global_status = OK
    token_info = get_token_info(auxip_user, auxip_password,mode=mode)
    
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


def ingest_replace(auxiliary_data_files, 
                   auxip_user, auxip_password,
                   path_to_mc, output_list, out_error_file,
                   mode="dev",
                   bucket="auxip_s3/auxip"):
    #    Ingest not available auxiliary data files
    #    For available files: take note of current UUID
    # =======================================================================
    #               IGNORE ALREADY UPLOADED AUX FILES
    # =======================================================================
    auxiliary_data_filenames = [name for name in auxiliary_data_files.keys()]

    # Create listings
    not_yet_uploaded = []
    print("Testing files in auxip or not ...")
    availables = available_files_status(auxip_user,auxip_password,auxiliary_data_filenames,5,mode)
    available_files = [rec[0] for rec in availables]
    available_uuids = { rec[0]: rec[5] for rec in availables}
    # -- TODO -- availables specifies for each existing file the current UUID
    print("Availables: "+str(len(availables)))
    # not_yet_uploaded = [f for f in auxiliary_data_filenames if f not in availables]
    # if force: upload and post all, remove availables
    for i in auxiliary_data_filenames:
        if i not in available_files:
            not_yet_uploaded.append(auxiliary_data_files[i])
    # At this point we have two lists: files already in auxip and files not in auxip
    #   There could be some files that are present in storage but not in auxip, but 
    # they shall cleaned up by some other maintenance tool
    print(str(len(not_yet_uploaded))+" files not in auxip")
    uploaded = []
    global_status = OK
    if len(not_yet_uploaded) > 0:
        global_status = upload_and_post(1, path_to_mc, bucket,
                                        auxip_user, auxip_password,
                                        not_yet_uploaded, uploaded, mode)
    else:
        print("No new auxiliary data file found in the input folder")
    print(str(len(availables)) + " auxiliary data files to be replaced in auxip")
    if len(availables) > 0:
       failures = []
       to_be_replaced_data_files = [auxiliary_data_files[i] for i in available_files]
       replace_status = upload_and_post_replace(2, path_to_mc, bucket,
                                                auxip_user, auxip_password,
                                                to_be_replaced_data_files,
                                                available_uuids, uploaded, failures,
                                                mode)
    else:
        print("No auxiliary data file found to be replaced ")
    with open(out_error_file, mode="w") as e:
        for i in failures:
            e.write(i + "\n")
    with open(output_list, mode="w") as l:
        for i in uploaded:
            l.write(i + "\n")
    if global_status == KO or replace_status == KO:
        exit(1)

def build_folder_files_table(folder):
    folder_files = {}
    for root, folders, files in os.walk(folder):
        for name in files:
            # auxiliary_data_files.append(os.path.join(root,name))
            folder_files[name] = os.path.join(root, name)
    return folder_files

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
            "-o", "--output",
            help="Output data directory (product directory). Default value: '.'",
            required=True)
    parser.add_argument(
            "-e", "--errors_output",
            help="File to hold the aux files that failed ingestion (with the reason) ",
            required=True)
    args = parser.parse_args()

    # =======================================================================
    #               CREATE AUXILIARY DATA FILES LISTING WITHOUT DUPLICATION
    # =======================================================================
    print("Listing files ...")
    # Build a list of files in specified folder
    auxiliary_data_files = build_folder_files_table(args.input)
    print("Done")
    if len(auxiliary_data_files):
        ingest_replace(auxiliary_data_files, 
                       args.user, args.password,
                       args.path_to_mc, args.output, args.errors_output,
                       args.mode, args.bucket)
    else:
        print("No auxiliary data files downloaded to ingest in folder ", args.input)
    sys.exit(0)
