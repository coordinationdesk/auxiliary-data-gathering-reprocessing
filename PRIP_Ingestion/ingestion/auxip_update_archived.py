#!/bin/python
# -*- coding: utf-8 -*-

import argparse
import sys
import os
import requests

from auxip_catalogue_client import AuxipCatalogueClient
from lib.auxip import build_metadata
from lib.wasabi import download_from_wasabi
from lib.attributes import get_attributes
from AuxFilesListUtils import get_aux_names_from_file
from auxip_db_add_attribute_client import AuxipProductUpdater

OK = 0
KO = 1
# Read argumens:
#  Auxip Credentials,
# Archive/Storage Credentials
# Aux Type
#  Attribute name to be updated
# Day of work
# temporary folder

# Check if date has only date part
def only_date(date_str):
    return True
# Selection of files to be updated:
#  list of aux types
#   or
#  mission
#   or
#  list of Aux Files from file
#  publication or sensing date interval (from/to)
# what if date interval is not specified?
def get_command_arguments():
    print("Called with command line: ", sys.argv)
    parser = argparse.ArgumentParser(description="This script updates the metadata attributes of the aux files",  # main description for help
                                     epilog='Usage samples : \n\tpython .py -u username -pw password \n\n',
                                     formatter_class=argparse.RawTextHelpFormatter)  # displayed after help
    parser.add_argument("-au", "--auxipuser",
                        help="Auxip user",
                        required=True)
    parser.add_argument("-apw", "--auxippassword",
                        help="Auxip password ",
                        required=True)
    parser.add_argument("-w", "--working",
                        help="Working folder",
                        required=True)
    parser.add_argument("-mi", "--mission",
                        help="Single Mission to retrieve",
                        required=False)
    AuxipProductUpdater.add_arguments(parser)
    parser.add_argument("-t", "--types", nargs="*",
                        help="List of types to be ingested",
                        required=False)
    parser.add_argument("-from", "--from_date",
                        help="Earliest Publication Date of files to be retrieved ",
                        required=False)
    parser.add_argument("-to", "--to_date",
                        help="Latest publication date of files to be retrieved",
                        required=False)
    parser.add_argument("-i", "--input_file",
                        help="Input file with Aux names list",
                        required=False)
    parser.add_argument("-mc", "--path_to_mc",
                        help="Path to mc program",
                        default="/data/mc",
                        required=True)
    parser.add_argument("-b", "--bucket",
                        help="Name of mc bucket",
                        default="auxip_s3/auxip",
                        required=True)
    parser.add_argument("-m", "--mode",
                        help="dev or prod",
                        default="dev",
                        required=False)
    parser.add_argument(
            "-e", "--errors_output",
            help="File to hold the aux files that failed ingestion (with the reason) ",
            required=True)
    args_values = parser.parse_args()
    if args_values.types is None and args_values.input_file is None:
        parser.print_usage()
        raise Exception("Expected one of the two arguments: types or input_file Directory")
    if (args_values.types is None or args_values.mission is None) and args_values.input_file is None:
        parser.print_usage()
        raise Exception("Mission and Types arguments must be both specified, if no input file is specified")

    return args_values

def update_product_attributes(aux_record, archive_file, attributes_list):
    """
      Update in aux_record the value of the attributes 
      specified in attributes_list using the values computed from the product file
    """
    try:
        updated = False
        #   Extract attributes
        file_attributes = get_attributes(archive_file)

        catalogue_attributes = aux_record["Attributes"]
        # Remove from attributes, items specifying Odata type, 
        # with key: @odata.type
        for cat_attr in catalogue_attributes:
            cat_attr.pop('@odata.type', None)


        #   Use attributes to update auxip record:
        #      (if md5: replace all the object)
        # we are looking for attributes with name attribute to update
        # Insert/update Attribute att_to_update in Catalogue Aux Record
        # Look for existing attribute item , if any
        for attr_to_update in attributes_list:
            if attr_to_update in file_attributes:
                record_attribute_item = next(
                               (item for item in catalogue_attributes if item['Name'] == attr_to_update),
                                  None)
                if record_attribute_item is None:
                    # Add Attribute record, to catalogue metadata
                    catalogue_attributes.append(build_metadata(attr_to_update,
                                                          file_attributes[attr_to_update]))
                    updated = True
                else:
                    # UPdate Attribute record, on catalogue metadata
                    if file_attributes[attr_to_update] != record_attribute_item['Value']:
                        record_attribute_item['Value'] = file_attributes[attr_to_update]
                        updated = True
                    else:
                        updated = False
    except Exception as ex:
        print("Error while extracting or updating attribute for file ", aux_record['Name'], " with id ", aux_record['Id'])
        print("Error: ", ex)
        raise ex
    finally:
        # remove downloaded file if no errors occurred while extracting attributes
        os.remove(archive_file)
    # Attributes were updated either if the attribute was not already present
    # or if it was present and it changed its value
    return aux_record, updated

# TODO: collect results: for each aux record, download, auxip update status
#   collect messages to be written on a report
def update_aux_files_records(aux_files_records, 
                             temp_dir, mcpath, bucket,
                             # auxip_client,
                             auxip_db_client,
                             attributes_to_update,
                             listing_out,
                             mode):
    global_update_status = OK
    # For each Aux file record:
    for aux_record in aux_files_records:
        try:
            #   Download file from Archive to temporary folder
            was_status = download_from_wasabi(mcpath, bucket,
                                     aux_record['Name'], aux_record['Id'],
                                     temp_dir, mode)
            # If download failed, do not continue
            if was_status != OK:
                global_update_status = KO
                message = f"Failed download of file {aux_record['Name']} with id {aux_record['Id']}"
                continue
            archive_file = os.path.join(temp_dir, aux_record['Name'])
            update_status = OK
            updated_aux_record, updated = update_product_attributes(aux_record,
                                                               archive_file,
                                                               attributes_to_update)
            #   post the record to AUXIP, if updated
            # Record contains also AUXIP ID and Filename
            if updated:
                print("New Record for ", aux_record['Name'], ": ", updated_aux_record)
                #update_status = auxip_client.update_aux_file(updated_aux_record)
                update_status = auxip_db_client.update_aux_file(updated_aux_record, attributes_to_update)
            if update_status == OK:
                listing_out.append(aux_record['Name'])

        except Exception as ex:
            print(f"Failed extracting attributes from {archive_file}: ", ex)
            global_update_status = KO
        # Update global status
        # global_update_status = was_status == OK and update_status = OK
    return global_update_status

def main():
    args = get_command_arguments()
    requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
    # Define Publication Date interval
    from_date = args.from_date if args.from_date is not None else None
    if from_date and only_date(from_date):
        # Check if date contains Time part
        from_date += "T00:00:00Z"

    to_date = args.to_date if args.to_date is not None else None
    if to_date and only_date(to_date):
        # Check if date contains Time part
        to_date += "T00:00:00Z"

    # TODO: Manage combination of
    #   Types being specified (no need to specify Mission)
    #  Mission being specified/not (if not specified, take all)
    #       Types to be retrieved for each Satellite Platform
    aux_types = args.types
    if args.mission:
        working_dir = os.path.join(args.working, args.mission)
    else:
        working_dir = args.working
    if not os.path.exists(working_dir):
        os.makedirs(working_dir)
    attributes_to_update = ['InstrumentConfigurationID']

    # Create Auxip Client
    auxip_client = AuxipCatalogueClient(args.auxipuser, args.auxippassword, args.mode)
    auxip_db_client = AuxipProductUpdater(args.mission, args)
    # If auxtypes were specified
    # if a list of files was specified
    # Loop on Aux Types if auxtypes were specified
    error_files = []
    updated_aux_files = []
    global_result = OK
    if aux_types:
        for auxtype in aux_types:
            # Create a target folder by auxtype, date interval
            temp_dir = os.path.join(working_dir, auxtype)
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)
            print("Processing type ", auxtype)
            if args.mission and args.mission == 'S1':
                if auxtype == "AUX_POEORB_S1":
                    auxtype = "AUX_POEORB"
                if auxtype == "AUX_PREORB_S1":
                    auxtype = "AUX_PREORB"
            #    Get List of Aux Files for AuxType, Day interval
            #    For each file, get the whole record, including Attributes
            aux_files_records = auxip_client.get_aux_file_records(args.mission, auxtype, from_date, to_date)
            aux_files_list = [aux_rec['Name'] for aux_rec in aux_files_records]
            result = update_aux_files_records(aux_files_records, temp_dir,
                                              args.path_to_mc, args.bucket,
                                              # auxip_client,
                                              auxip_db_client,
                                              attributes_to_update, error_files,
                                              args.mode)
            # Write list of error files to error ouutput
            print ("Files that failed update: ", error_files)
            updated_aux_files.extend([aux_file
                                     for aux_file in aux_files_list
                                     if aux_file not in error_files])

            global_result = global_result if result == OK else result
    else:
        aux_files_list = get_aux_names_from_file(args.input_file)
        aux_files_records = auxip_client.get_aux_records_from_names(aux_files_list)
        global_result = update_aux_files_records(aux_files_records, working_dir,
                                              args.path_to_mc, args.bucket,
                                              # auxip_client,
                                              auxip_db_client,
                                              attributes_to_update, error_files,
                                              args.mode)
            # Write list of error files to error ouutput
        # Write list of error files to error ouutput
        print ("Files that failed update: ", error_files)
        # COmpute list of updated aux files, by remoeing fiels with errors from aux_files_records
        updated_aux_files = [aux_file
                            for aux_file in aux_files_list
                            if aux_file not in error_files]

        print("Updated Aux Products: ", updated_aux_files)
        print(" Aux Products not updated for errors: ", error_files)
    sys.exit(global_result)

if __name__ == "__main__":
    main()
