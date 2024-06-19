#!/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import argparse
import time
import csv

from lib.auxip_rm import remove_from_auxip
from lib.auxip import get_token_info,refresh_token_info
from lib.wasabi import remove_from_wasabi

OK = 0
KO = 1

code_result = {
0: "OK",
1: "KO"
}
def remove_aux_file(thread_id,
                    uuid, filename, auxip_user, auxip_password, path_to_mc, bucket, mode ):

    print("Removeing from Storage and Auxip  aux file ", filename, " with uuid ", uuid)
    global_status = OK
    token_info = get_token_info(auxip_user, auxip_password,mode=mode)
     
    with open("report_thread_%d.txt" % thread_id,"w") as report:
        access_token = token_info['access_token']
        auxip_res = remove_from_auxip( access_token, filename, uuid, mode) 
        if auxip_res == OK:
            print("%s ==> Removed from AUXIP" % filename)
        else:
            global_status = KO
            print("%s ==> Failure deleteing from AUXIP" % filename)
        wasabi_res = remove_from_wasabi(path_to_mc,bucket,filename,uuid,mode) 
        if wasabi_res == OK:
            print("%s ==> removed from wasabi successfully with : %s " % (filename,uuid) )
        else:
            global_status = KO
            print("%s ==> Failed remove from Wasabi with : %s " % (filename,uuid) )
        
        message = "%s : %s\tremove_from_wasabi : %s; remove_from_auxip : %s\n" % (filename,uuid, code_result[wasabi_res], code_result[auxip_res])
        report.write(message)
    print("Exiting upload_and_post with status ", global_status)
    return global_status



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="",  # main description for help
            epilog='Beta', formatter_class=argparse.RawTextHelpFormatter)  # displayed after help
    parser.add_argument("-i", "--uuid",
                        help="Auxip UUID of file to be removed",
                        required=True)
    parser.add_argument("-f", "--name",
                        help="Auxip Filename of file to be removed",
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
    args = parser.parse_args()

    # =======================================================================
    #               CREATE AUXILIARY DATA FILES LISTING WITHOUT DUPLICATION
    # =======================================================================
    remove_aux_file(1, args.uuid, args.name, 
                       args.user, args.password,
                       args.path_to_mc, 
                       args.bucket, args.mode) 
    sys.exit(0)
