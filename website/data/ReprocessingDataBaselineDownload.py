#!/bin/python
# -*- coding: utf-8 -*-

#!/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import argparse
import datetime 
import time
import requests

import glob
import csv


ADG_DOMAIN="auxiliary.copernicus.eu"
client_id="reprocessing-preparation"
def get_token_info(user,password):
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {"username":user, "password":password,"client_id":client_id,"grant_type":"password"}
    token_endpoint = f"https://{ADG_DOMAIN}/auth/realms/reprocessing-preparation/protocol/openid-connect/token"

    # print(token_endpoint)
    response = requests.post(token_endpoint,data=data,headers=headers)
    return response.json()

def rdb_service(user,password,mission,unit,product_type,l0_names="",start="",stop=""):

    token_info = get_token_info(user,password)
    reprobase_access_token = token_info['access_token']

    if l0_names:
        request = f"https://{ADG_DOMAIN}/rdb.svc/getReprocessingDataBaseline(l0_names='%s',mission='%s',unit='%s',product_type='%s')" % (l0_names,mission,unit,product_type)
    else:
        request = f"https://{ADG_DOMAIN}/rdb.svc/getReprocessingDataBaseline(start=%s,stop=%s,mission='%s',unit='%s',product_type='%s')" % (start,stop,mission,unit,product_type)

    headers = {'Content-Type': 'application/json','Authorization' : 'Bearer %s' % reprobase_access_token }
    response = requests.get(request,headers=headers)

    aux_file_links = {}
    try:
        print("Aux Files for each L0 to be processed:")
        for l0_aux in response.json()["value"]:

            print("Level0 :%s " % l0_aux["Level0"] )
            print("AuxDataFiles :" )
            for aux in l0_aux["AuxDataFiles"]:
                print("\tName :%s " % aux["Name"])
                print("\tAuxipLink :%s " % aux["AuxipLink"])
                aux_file_links[aux["Name"]] = aux["AuxipLink"]

    except Exception as e:
        print(response.json())
        print(e)
    return aux_file_links


def auxip_download(auxip_link, name,access_token, output_folder, timeout=20):
    # Get output file path
    file_path = os.path.join(output_folder, name)
    headers = {'Content-Type': 'application/json','Authorization' : 'Bearer %s' % access_token }
    print("\n[BEGIN] Downloading %s " % (name))
    print("\n[BEGIN] Downloading %s " % (file_path))
    try:
        # get ID and size of the product
        product_response = requests.get(auxip_link,
                                        headers=headers,
                                        timeout=timeout,
                                        stream=True, verify=False)
        if product_response.status_code == 200:
            total_length = int(product_response.headers.get('content-length'))
            if not total_length: # no content length header
                 fid.write(product_response.content)
            else:
                downloaded_bytes = 0
                print("Starting download")
                with open(file_path,"wb") as fid:
                    for data in product_response.iter_content(chunk_size=4096):
                        downloaded_bytes += len(data)
                        fid.write(data)
                        sys.stdout.write("\r...Downloaded %s/%s bytes" %( downloaded_bytes,total_length))
                        sys.stdout.flush()
                        # done = int(50 * downloaded_bytes / total_length)
                        # sys.stdout.write("\r[%s%s] %s bps" % ('=' * done, ' ' * (50-done), downloaded_bytes//(time.perf_counter() - start)))
                        # sys.stdout.flush()
            print("[END] Download Done\n")
        elif product_response.status_code == 404:
            raise Exception("Not found on the server : "+auxip_link)
        else:
            print (product_response.json())
    except requests.Timeout as to_exc:
        print("Request For product  ", id, " info and download failed after timeout (", req_timeout,"): ", str(to_exc))
        product_response = None
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        print(e)
        raise e

if __name__ == "__main__": 

    parser = argparse.ArgumentParser(description="This script allows you to execute the reprocessing data baseline service for a given l0_names,mission,satellite unit and product type and download the Aux Files.",  # main description for help
            epilog='Usage samples : \
            \n\tpython ReprocessingDataBaseline.py -u username -pw password -l0 S3A_OL_0_EFR____20200203T205636_20200203T214023_20200203T224521_2627_054_271______LN1_O_NT_002.SEN3 -m S3OLCI -su A -pt L1EFR \
            \tpython ReprocessingDataBaseline.py -u username -pw password -t0 2020-10-30T13:15:30Z -t1 2020-10-30T22:15:30Z -m S3OLCI -su B -pt L1EFR\n\n',
            formatter_class=argparse.RawTextHelpFormatter)  # displayed after help
    parser.add_argument("-u", "--user",
                        help="Reprocessing preparation username",
                        required=True)
    parser.add_argument("-pw", "--password",
                        help="User password ",
                        required=True)

    parser.add_argument("-l0", "--l0_names",
                        help="Comma separated list of level 0 products names.",
                        default="",
                       required=False)

    parser.add_argument("-m", "--mission",
                        help="Mission, can be one of the following : S3OLCI,S3SLSTR,S3SRAL,S3SYN,S3MWR,S2MSI,S1SAR",
                       required=True)
    parser.add_argument("-t0", "--start",
                        help="Sensing Time Start in UTC format (2019-11-05T13:15:30Z)",
                        default="",
                        required=False)
    parser.add_argument("-t1", "--stop",
                        help="Sensing Time Stop in UTC format (2020-11-05T13:15:30Z)",
                        default="",
                        required=False)
    parser.add_argument("-su", "--unit",
                        help="Satellite unit : A,B",
                       required=True)
    parser.add_argument("-d", "--download",
                        help="By default ReprocessingDataBaseline tool will only list all auxiliary data files matching your request\nuse '-d true' option to download the listing.",
                        default=False,
                        required=False)

    parser.add_argument("-pt", "--product_type",
                        help="Product type to be reprocessed, this type is mission dependent:\n\
                            S1SAR : { 'L1SLC', 'L1GRD', 'L2OCN' }  \n\
                            S2MSI : { 'L1A', 'L1B', 'L1C', 'L2A' }  \n\
                            S3MWR : { 'L1CAL', 'L1MWR' } \n\
                            S3OLCI : {'L1EFR', 'L1ERR' , 'L2LFR', 'L2LRR' } \n\
                            S3SLSTR : { 'L1RBT', 'L2LST', 'L2FRP' } \n\
                            S3SRAL : { 'L1CAL', 'L1SRA', 'L2LAN' } \n\
                            S3SYN : { 'L1MISR', 'L2' }",
                        required=True)
    args = parser.parse_args()
    user = args.user
    password = args.password
    mission  = args.mission
    unit     = args.unit
    product_type = args.product_type
    download = args.download
    if download in ["TRUE","True","true","1",True]:
        download = True
    if download in ["FALSE","False","false","0",False]:
        download = False

    l0_names = args.l0_names
    start = args.start
    stop = args.stop


    if l0_names == "" and start == "" and stop == "":
        print(parser.epilog)
        sys.exit(1)

    if (l0_names != "" and start != "") or (l0_names != "" and stop != ""):
        print(parser.epilog)
        sys.exit(1)

    # Create the output folder 
    output_folder ="%s_%s_%s_%s" % (mission,unit,start.replace("-","").replace(":","").replace("Z",""),stop.replace("-","").replace(":","").replace("Z",""))
    if download:
        os.makedirs(output_folder,exist_ok=True)

    requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

    aux_links = rdb_service(user,password,mission,unit,product_type,l0_names,start,stop)
    print("==========================")
    token_info = get_token_info(user,password)
    auxip_access_token = token_info['access_token']
    print("All the Aux files to be downloaded:")
    for aux_file, aux_link in aux_links.items():
        print("Aux File Name: %s" %aux_file)
        print("\tDownload Link:  %s" %aux_link)
        if download:
            auxip_download(aux_link, aux_file, auxip_access_token, output_folder)