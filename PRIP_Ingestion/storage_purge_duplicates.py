#!/bin/python
# -*- coding: utf-8 -*-

import argparse
import sys

import time
import os
import csv

import requests
from ingestion.auxip_client import AuxipClient
from ingestion.lib.wasabi import remove_from_wasabi
    
def get_command_arguments():
    print("Called with command line: ", sys.argv)
    parser = argparse.ArgumentParser(description="This script removes  from Storage  the files from a list list (with specific UUID) that are duplicated and have no record in AUXIP",  # main description for help
                                     epilog='Usage samples : \n\tpython www.py -au auxip_username -apw password  -f <input file>\n\n',
                                     formatter_class=argparse.RawTextHelpFormatter)  # displayed after help
    parser.add_argument("-au", "--auxipuser",
                        help="Auxip user",
                        required=True)
    parser.add_argument("-apw", "--auxippassword",
                        help="Auxip password ",
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
                        help="Mode  (dev/prod)",
                        required=True)
    parser.add_argument("-f", "--input_file",
                        help="Input file with Reprobase Aux names list to search",
                        required=True)
    parser.add_argument("-o", "--output_file",
                        help="Output file with Storage/Auxip names list status (missing in Auxip/available, duplicated on Storage) (Storage Id )",
                        required=True)
    args_values = parser.parse_args()

    return args_values

def get_duplicate_ids_from_file(input_file):
    '''
       input_file: the file to be read
             records are in the format: num dduplicates, filename, list of ids
            separated by comma
       returns. a dictionary, with key the filename, and value
            a list of UUId s of objects on the storage for the filenamef
    '''
    name_id_table = {}
    print("Reading file ", input_file)
    with open(input_file) as f:
        aux_reader = csv.reader(f, delimiter=",")
        for aux_record in aux_reader:
            if len(aux_record):
                num_dupls = aux_record[0]
                print("Reading rec for file ", aux_record[1], " with ", num_dupls, " duplicates")
                name_id_table[aux_record[1]] = (aux_record[2:])
    # you may also want to remove whitespace characters like `\n` at the end of each line
    return name_id_table


def remove_from_archive_product_instances(path_to_mc, bucket, filename, id_list, mode):
    for uuid in id_list:
        wasabi_res = remove_from_wasabi(path_to_mc,bucket,filename,uuid,mode) 
        if wasabi_res == OK:
            print("%s ==> removed from wasabi successfully with : %s " % (filename,uuid) )
        else:
            global_status = KO
            print("%s ==> Failed remove from Wasabi with : %s " % (filename,uuid) )


def purge_product_instances(name, avail_config, auxip_connection, mcpath, bucket, mode):
    '''
      deletes from storage the files in the avail_config uncatalogued list
      deletes from auxip and storage duplicated files
      at the end only one item shall be kept: either on storage (if not catalgoued)
        or on storage+auxip (if already catalogued)
      delete all the uncatalogued ids but one
      if available is true, delete the last uncatalgoued id
      if any item in the catalogued list
        deletes all but one: from storage and from auxip

     return report: for each id: removed from storage, removed from storage/auxip, failure, not removed
      and the filename common to all
    '''
    # Print: number of items in uncatalogued, number of items in catalogued, available flag
    print("Num not catalogued products: ", len(avail_config['uncatalogued']))
    print("Num catalogued products: ", len(avail_config['catalogued']))
    print("At least one catalogued product: ", "Yes" if len(avail_config['catalogued']) else "No")
    # Remove from archive uncatalogued products, if at least 1
    if len(avail_config['uncatalogued']) > 1:
        # Print: each Id being deleted from storage
        print("Calling Remove_from archive_product instances: ", avail_config['uncatalogued'][:-1])
        remove_from_archive_product_instances(mcpath, bucket, name, avail_config['uncatalogued'][:-1], mode)

    # Last copy on Archive should be kept always: it should be the same kept on AUXIP
    # Print: if deleteing last id from storage (if any)
    if avail_config['available'] and len(avail_config['uncatalogued']) > 0:
        print("At least one catalogued item for file ", name)
        print("Removing also last id from Wasabi: ", avail_config['uncatalogued'][-1])
        remove_from_archive_product_instances(mcpath, bucket, name, [avail_config['uncatalogued'][-1]], mode)

    # print : if deleting from auxip/storage
    if len(avail_config['catalogued']) > 1:
        print("Filename ", name, ", Removing catalogued items : ", avail_config['catalogued'][:-1])
        result = remove_aux_product_instances(name, avail_config['catalogued'][:-1],
                                              auxip_connection,
                                              mcpath, bucket)

    # print last object remaining after purge
    if avail_config['available']:
        print("Kept Auxip and Wasabi product: ", avail_config['catalogued'][-1])
    else:
        print("Kept Wasabi product: ", avail_config['uncatalogued'][-1])
        print(name, " Product to be catalogued on Auxip: ", avail_config['uncatalogued'][-1])

OK = 0
KO = 1
code_result = {

OK: "OK",
KO: "KO"
}
def remove_aux_product_instances(filename, id_list,
                                 auxip_connection,
                                 path_to_mc, bucket ):

    print("Removeing from Storage and Auxip  aux file ", filename, " with uuid's ", id_list)
     
    global_status = OK
    for uuid in id_list:
        print("Removing from Auxip file ", filename, ", id: ", uuid)
        auxip_res = auxip_connection.remove_auxip_file(filename, uuid) 
        if auxip_res == OK:
            print("%s ==> Removed from AUXIP uuid %s" % (filename, uuid))
        else:
            global_status = KO
            print("%s ==> Failure deleteing from AUXIP with uuid %s" % (filename, uuid))
        wasabi_res = remove_from_wasabi(path_to_mc,bucket,filename,uuid) 
        if wasabi_res == OK:
            global_status = KO
            print("%s ==> removed from wasabi successfully with : %s " % (filename,uuid) )
        else:
            print("%s ==> Failed remove from Wasabi with : %s " % (filename,uuid) )
        
        print ( "%s : %s\tremove_from_wasabi : %s; remove_from_auxip : %s\n" % (filename,uuid, code_result[wasabi_res], code_result[auxip_res]))
    return global_status

def main():
    args = get_command_arguments()
    requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
    # Read file with Aux names list
    names_dupl_id_list = get_duplicate_ids_from_file(args.input_file)
    print("Init Auxip client")
    # Check files against Auxip: generate a list specifiying for each Aux file: if available on Auxip, ID
    auxip_connection = AuxipClient(args.auxipuser, args.auxippassword, args.mode)

    try:
        # Build a new table
        name_dupl_avail_table = {}
        # for each filename 
        for name, id_list in names_dupl_id_list.items():
             availables, not_availables = auxip_connection.get_file_ids_availability(name, id_list)
             # a flag active if at least an instance was available on AUXIP
             #       a list of IDs on storage, not available on AUXIP
             #       a list of IDs on storage, that are available on AUXIP 
             available_ids = availables
             name_dupl_avail_table[name] = {
                  'available' : len(available_ids) > 0,
                  'catalogued' : available_ids,
                  'uncatalogued': not_availables
             }
             print("File ", name, "Available ids: ", available_ids)
             print("Not catalogued ids: ", name_dupl_avail_table[name]['uncatalogued'])
        # Write table of Availability for filename duplicates on file
        print(name_dupl_avail_table)
        archive_deleted = []
        archive_auxip_deleted = []
        #  Purge files from storage (NOTE: it would be bettere if each ID had associated a publication date, and a Checksum)
        # get list of files/ids deleted from archive, list of files/ids deleted from archive and auxip
        # files not deleted (either from archive or from auxip)
        for name, avail_config in name_dupl_avail_table.items():
             purge_product_instances(name, avail_config, auxip_connection,
                                     args.path_to_mc, args.bucket, args.mode)

        # Write operations performed: files deleted only from archive,
        # files deleted from archive and auxip, files retained
        # any erorr?
        #out_file = f"{args.output_file}.removed"
        #with open(out_file, "w") as of:
        #    report_writer = csv.writer(of)
        ##    for fileid in removed:
        #        report_writer.writerow(fileid)
    except Exception as e:
        print(e)
    # 
    print("Archive duplicates Purge from Archive/Auxip completed")
    sys.exit(0)



if __name__ == "__main__":
    main()
