#!/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import argparse
import uuid as UUID
import datetime 
import time
import requests

def get_token_info(user,password):
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {"username":user, "password":password,"client_id":"preparation","grant_type":"password"}
    token_endpoint = "https://auxiliary.copernicus.eu/auth/realms/reprocessing-preparation/protocol/openid-connect/token"

    # print(token_endpoint)
    response = requests.post(token_endpoint,data=data,headers=headers)
    return response.json()

def refresh_token_info(token_info,timer):
    # access_token expires_in 900 seconds (15 minutes) 

    if timer < 900 :
        # access_token is still valid
        return token_info
    else:
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = {"refresh_token":token_info['refresh_token'],"client_id":"preparation","grant_type":"refresh_token"}
        token_endpoint = "https://auxiliary.copernicus.eu/auth/realms/reprocessing-preparation/protocol/openid-connect/token" 
        response = requests.post(token_endpoint,data=data,headers=headers)
        return response.json() 


def auxip_download(aux_name,access_token,output_folder,contains="*",exclude="none",download=False):
    try:
        headers = {'Content-Type': 'application/json','Authorization' : 'Bearer %s' % access_token }
        auxip_endpoint = "https://auxiliary.copernicus.eu/auxip.svc/Products?$filter=contains(Name,'%s')" % aux_name

        response = None
        if contains != "*":
            if contains in aux_name and exclude not in contains:
                response = requests.get(auxip_endpoint,headers=headers)

        else:
            if exclude not in aux_name:
                response = requests.get(auxip_endpoint,headers=headers)

        if response is not None:
            if response.status_code == 200:

                if len(response.json()["value"]) > 0 :
                    ID = response.json()["value"][0]["Id"]
                    length = float(response.json()["value"][0]["ContentLength"])
                    slength = "%.03f MB" % (length*1.e-6) if  length < 1.e9 else "%.03f GB" % (length*1.e-9)

                    if download == True:
                        # get ID and size of the product 
                        print( "\nDownloading %s : %s" % (aux_name,slength) )
                        with open(output_folder +"/"+aux_name,"wb") as fid:
                            start = time.time()
                            product_response = requests.get("https://auxiliary.copernicus.eu/auxip.svc/Products(%s)/$value" % ID ,headers=headers,stream=True)
                            total_length = int(product_response.headers.get('content-length'))
                            if total_length is None: # no content length header
                                fid.write(product_response.content)
                            else:
                                dl = 0
                                for data in product_response.iter_content(chunk_size=4096):
                                    dl += len(data)
                                    fid.write(data)
                                    done = int(50 * dl / total_length)
                                    sys.stdout.write("\r[%s%s] %s bps" % ('=' * done, ' ' * (50-done), dl//(time.time() - start)))
                                    sys.stdout.flush()
                            # fid.write(product_response.content)
                            fid.close()
                    else:
                        print( "%s : %s - Id : %s" % (aux_name,slength,ID) )
                else:
                    print( "%s : Not Found by the Auxip service" % aux_name )
            else:
                print (response.json())
                # print(response.json()["error"]["message"])

    except Exception as e:
        print(e)

if __name__ == "__main__": 
    parser = argparse.ArgumentParser(description="This script allows you to download Auxiliary Data Files for a given mission,period and satellite unit.",  # main description for help
            epilog='Usage samples : \n\tpython getBaseline.py -u username -pw password -m S3OLCI -t0 2019-11-05T13:15:30Z -t1 2020-11-05T13:15:30Z -su B -c S3B_AX___FRO_AX \n\tpython getBaseline.py -u username -pw password -m S3OLCI -t0 2019-11-05T13:15:30Z -t1 2020-11-05T13:15:30Z -su B -e S3B_OL_2_ACP_AX -d true \n\n', formatter_class=argparse.RawTextHelpFormatter)  # displayed after help
    parser.add_argument("-u", "--user",
                        help="Auxip and Reprobase username,\nYour attention please ! : \nThis script assumes that you have the same account for both services Auxip.svc and Reprobase.svc \n(This supposition will be automatically satisfied in the next release of Reprocessing Preparation Package)",
                        required=True)
    parser.add_argument("-pw", "--password",
                        help="User password ",
                        required=True)
    parser.add_argument("-m", "--mission",
                        help="Mission, can be one of the following : S3OLCI,S3SLSTR,S3SRAL,S3SYN,S3MWR,S2MSI,S1SAR",
                       required=True)
    parser.add_argument("-t0", "--start",
                        help="Sensing Time Start in UTC format (2019-11-05T13:15:30Z)",
                        required=True)
    parser.add_argument("-t1", "--stop",
                        help="Sensing Time Stop in UTC format (2020-11-05T13:15:30Z)",
                        required=True)
    parser.add_argument("-su", "--unit",
                        help="Satellite unit : A,B,_, default = _",
                        default="_",
                       required=False)
    parser.add_argument("-c", "--contains",
                        help="Downloads only auxiliary data files with names containing CONTAINS",
                        default="*",
                        required=False)
    parser.add_argument("-e", "--exclude",
                        help="Exclude from downloading all auxiliary data files with names containing EXCLUDE",
                        default="none",
                        required=False)
    parser.add_argument("-d", "--download",
                        help="By default getBaseline tool will only list all auxiliary data files matching your request\nuse '-d true' option to download the listing.",
                        default=False,
                        required=False)
    args = parser.parse_args()

    try:
        # get token_info for AUXIP and Reprobase services
        timer_start = time.time()
        token_info = get_token_info(args.user,args.password)
        access_token = token_info['access_token']

        mission = args.mission
        unit = args.unit
        start = args.start
        stop = args.stop
        contains = args.contains
        exclude = args.exclude
        download = args.download
        if download in ["TRUE","True","true","1",True]:
            download = True
        if download in ["FALSE","False","false","0",False]:
            download = False

        # print( mission,unit,start,stop)
        headers = {'Content-Type': 'application/json','Authorization' : 'Bearer %s' % access_token }
        reprobase_endpoint = "https://auxiliary.copernicus.eu/reprocessing.svc/GetReproBaselineNamesForPeriod(Mission='%s',Unit='%s',SensingTimeStart='%s',SensingTimeStop='%s')" % (mission,unit,start,stop)
        response = requests.get(reprobase_endpoint,headers=headers)

        if response.status_code == 200:
            # Create the output folder 
            output_folder ="%s_%s_%s_%s" % (mission,unit,start.replace("-","").replace(":","").replace("Z",""),stop.replace("-","").replace(":","").replace("Z",""))

            if download == True:
                if not os.path.exists(output_folder):
                    os.mkdir(output_folder)
                    print("Folder %s Created " % output_folder)
                else:    
                    print("Folder %s already exists" % output_folder)

            aux_list = response.json()["value"]
            # loop over auxfile names
            for aux_name in sorted(aux_list): 
                # refesh token if necessary 
                timer_stop = time.time()
                elapsed_seconds = timer_stop - timer_start
                token_info = refresh_token_info(token_info,elapsed_seconds)
                if access_token != token_info['access_token']:
                    timer_start = time.time()
                    access_token = token_info['access_token']

                auxip_download(aux_name.strip(),access_token,output_folder,contains,exclude,download)

        else:
            print(response.json()["error"]["message"])
        
    except Exception as e:
        print(e)

