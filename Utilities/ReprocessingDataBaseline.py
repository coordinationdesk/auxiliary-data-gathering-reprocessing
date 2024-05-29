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


def get_token_info(user,password):
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {"username":user, "password":password,"client_id":"reprocessing-preparation","grant_type":"password"}
    token_endpoint = "https://auxiliary.copernicus.eu/auth/realms/reprocessing-preparation/protocol/openid-connect/token"

    # print(token_endpoint)
    response = requests.post(token_endpoint,data=data,headers=headers)
    return response.json()

def rdb_service(user,password,mission,unit,product_type,l0_names="",start="",stop=""):

    token_info = get_token_info(user,password)
    reprobase_access_token = token_info['access_token']

    if l0_names:
        request = "https://auxiliary.copernicus.eu/rdb.svc/getReprocessingDataBaseline(l0_names='%s',mission='%s',unit='%s',product_type='%s')" % (l0_names,mission,unit,product_type)
    else:
        request = "https://auxiliary.copernicus.eu/rdb.svc/getReprocessingDataBaseline(start=%s,stop=%s,mission='%s',unit='%s',product_type='%s')" % (start,stop,mission,unit,product_type)

    headers = {'Content-Type': 'application/json','Authorization' : 'Bearer %s' % reprobase_access_token }
    response = requests.get(request,headers=headers)

    try:
        for l0_aux in response.json()["value"]:

            print("Level0 :%s " % l0_aux["Level0"] )
            print("AuxDataFiles :" )
            for aux in l0_aux["AuxDataFiles"]:
                print("\tName :%s " % aux["Name"])
                print("\tAuxipLink :%s " % aux["AuxipLink"])

    except Exception as e:
        print(response.json())
        print(e)

if __name__ == "__main__": 

    parser = argparse.ArgumentParser(description="This script allows you to execute the reprocessing data baseline service for a given l0_names,mission,satellite unit and product type.",  # main description for help
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

    l0_names = args.l0_names
    start = args.start
    stop = args.stop


    if l0_names == "" and start == "" and stop == "":
        print(parser.epilog)
        sys.exit(1)

    if (l0_names != "" and start != "") or (l0_names != "" and stop != ""):
        print(parser.epilog)
        sys.exit(1)

    rdb_service(user,password,mission,unit,product_type,l0_names,start,stop)
