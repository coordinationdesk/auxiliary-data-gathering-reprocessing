import sys
import time

import requests
import json
from .attributes import get_attributes
import os
from datetime import datetime
#import datetime as dt
import traceback

from .time_formats import odata_datetime_format, get_odata_datetime_format



def _get_auth_base_endpoint(mode):
    base_endpoint = "https://dev.reprocessing-preparation.ml/auth"
    if mode == 'prod':
        base_endpoint = "https://reprocessing-auxiliary.copernicus.eu/auth"
    return base_endpoint

def _get_token_info(json_data, mode='dev'):
    auth_endpoint = _get_auth_base_endpoint(mode)
    tk_realm = "reprocessing-preparation"
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    token_request = "{}/realms/{}/protocol/openid-connect/token".format(auth_endpoint, tk_realm)
    print("Request : ", token_request)
    response = requests.post(token_request,data=json_data,headers=headers)
    if response.status_code != 200:
        #print(response.json())
        raise Exception("Bad return code ({})".format(response.status_code))
    # print(response)
    print("Received Token")
    return response.json()

# TODO: replace mode argument with endpoint baseurl
# Add Realm argument (or read from configuration)
# TODO: Separate in two: get_token info (with generic data payload),
#   get_access_token that defines payload and executes get_token_info with
#     access request payload
def get_token_info(user,password,mode='dev'):
    data = {"username":user, "password":password,"client_id":"reprocessing-preparation","grant_type":"password"}
    try:
        return _get_token_info(data, mode)
    except Exception as ex:
        raise Exception("Error " + str(ex) +"when getting access token")


def refresh_token_info(token_info,timer,mode='dev'):
    # access_token expires_in 900 seconds (15 minutes) 
    if timer < 900 :
        # access_token is still valid
        return token_info
    else:
        # TODO: Move token request to a get_token_info method, passing data payload
        data = {"refresh_token":token_info['refresh_token'],"client_id":"reprocessing-preparation","grant_type":"refresh_token"}
        try:
            return _get_token_info(data, mode)
        except Exception as ex:
            raise Exception("Error " + str(ex) +"when refreshing token")

def get_auxip_base_endpoint(mode):
    base_endpoint = "https://dev.reprocessing-preparation.ml/auxip.svc"
    if mode == 'prod':
        base_endpoint = "https://reprocessing-auxiliary.copernicus.eu/auxip.svc"
    return base_endpoint

# TODO: Move Auxip Endpoint baseurl to Function
# Receive Auxip baseurl as a parameter!
def get_latest_of_type(access_token,aux_type_list,sat,mode='dev'):
    try:
        headers = {'Content-Type': 'application/json',
                   'Authorization' : 'Bearer %s' % access_token }
        if len(aux_type_list) == 0:
            return aux_type_list
        auxip_endpoint = get_auxip_base_endpoint(mode)
        request = auxip_endpoint + "/Products?$filter=contains(Name,'" + aux_type_list[0] + "')"
        for idx in range(1, len(aux_type_list)):
            request = request + " or contains(Name,'" + aux_type_list[idx] + "')"
        request = request + " and startswith(Name,'"+sat+"')&$orderby=PublicationDate desc&$top=1"
        print("Auxip Request for last date: ", request)
        # print("Headers: ", headers)
        response = requests.get(request,headers=headers)
        # print(response.text)
        #print(access_token)
        if response.status_code != 200:
            print(response.status_code)
            print(response.text)
            raise Exception("Error while accessing auxip")
        json_resp = response.json()
        if len(json_resp["value"]) != 1:
            return None
        # TODO: Replace with Orign Date!
        return json_resp["value"][0]["PublicationDate"]
    except Exception as e:
        print("%s ==> get ends with error " % request )
        print(e)
        raise e


def is_file_available(access_token,aux_data_file_name,mode='dev'):
    try:
        headers = {'Content-Type': 'application/json','Authorization' : 'Bearer %s' % access_token }
        auxip_endpoint = get_auxip_base_endpoint(mode)
        auxip_request = "{}/Products?$filter=contains(Name,'{}')".format(auxip_endpoint, aux_data_file_name)
        response = requests.get(auxip_request, headers=headers)
        if response.status_code != 200:
            print(response.status_code)
            print(response.text)
            raise Exception("Error while accessing auxip")
        json_resp = response.json()
        return len(json_resp["value"]) > 0
    except Exception as e:
        print("%s ==> get ends with error " % aux_data_file_name )
        print(e)
        raise e

# TODO: Define a Unit Test, and a Functional test against a AUXIP test service
# step: number of files to be checked in same request
def _are_file_availables(auxip_user,auxip_password,aux_data_files_names,step,mode):
    availables = []
    timer_start = time.time()
    token_info = get_token_info(auxip_user, auxip_password,mode=mode)
    access_token = token_info['access_token']
    print("Checking availability on AUXIP of ", len(aux_data_files_names), " files")
    try:

        auxip_endpoint = get_auxip_base_endpoint(mode)

        for f in range(0, len(aux_data_files_names), step):
            # refesh token if necessary
            timer_stop = time.time()
            elapsed_seconds = timer_stop - timer_start
            if elapsed_seconds > 350:
                timer_start = time.time()
                token_info = get_token_info(auxip_user, auxip_password, mode=mode)
                access_token = token_info['access_token']
            sys.stdout.write("\rRequest for index from %s to %s" % (f, f+step-1))
            sys.stdout.flush()
            headers = {'Content-Type': 'application/json', 
                       'Authorization': 'Bearer %s' % access_token}
            auxip_request = "{}/Products?$filter=contains(Name,'{}')".format(auxip_endpoint, 
                                                                             aux_data_files_names[f])
            for t in range(min(len(aux_data_files_names),f+1), 
                           min(len(aux_data_files_names),f+step),
                           1):
                auxip_request = auxip_request + " or contains(Name,'"+aux_data_files_names[t]+"')"
            # print("Chcking if files are present in AUXIP: ", aux_data_files_names)
            response = requests.get(auxip_request, headers=headers)
            if response.status_code != 200:
                print(response.status_code)
                print(response.text)
                raise Exception("Error while accessing auxip")
            json_resp = response.json()
            # print(json_resp)
        # Return Name, checksum
            print("Received %d results" % len(json_resp["value"]))
            for g in json_resp["value"]:
                file_id = g["Id"]
                file_size = g["ContentLength"]
                if "Checksum" in g and len(g["Checksum"]):
                    cksum_info = g["Checksum"][0]
                    file_cksum = cksum_info["Value"]
                    cksum_alg = cksum_info["Algorithm"]
                    cksum_date = cksum_info["ChecksumDate"]
                else:
                    file_cksum = ''
                    cksum_alg = ''
                    cksum_date = ''
                availables.append((g["Name"], file_cksum, cksum_alg, cksum_date, file_size, file_id))
    except Exception as e:
        print("==> get ends with error ")
        print(e)
        traceback.print_exc()
        raise e
    print("Found ", len(availables), " files in Auxip from requested files")
    return availables

def are_file_availables(auxip_user,auxip_password,aux_data_files_names,step,mode='dev'):
   auxip_availables = _are_file_availables(auxip_user, auxip_password, aux_data_files_names, step, mode)
   return [file[0] for file in auxip_availables]
    
def available_files_status(auxip_user,auxip_password,aux_data_files_names,step,mode='dev'):
   # Return a list of available files, among those passed in aux_data_files_names
   # for each of them report also the checksum info
   return _are_file_availables(auxip_user, auxip_password, aux_data_files_names, step, mode)

def are_file_availables_w_checksum(auxip_user,auxip_password,aux_files_names_cksum,step,mode='dev'):
   print("Checking AUXIP availability for: ", "\n".join((str(a) for a in aux_files_names_cksum)))
   # input: list of tuples: filename + checksum, + chksum alg)
   # Build a lookup dictionary to find checksum for filenames
   in_aux_checksums = { af[0]: af[1] for af in aux_files_names_cksum}
   print("File Checksums received: ",
         "\n".join(f"{k}\t{v}" for k, v in in_aux_checksums.items()))
   aux_data_files_names = list(in_aux_checksums.keys())
   auxip_availables = _are_file_availables(auxip_user, auxip_password,
                                           aux_data_files_names, step, mode)
   print("Found Auxip Files: ", auxip_availables)
   auxip_cksum_availables = [file[0] for file in auxip_availables if file[1] == in_aux_checksums[file[0]]]
   auxip_cksum_changed = [file for file in auxip_availables if file[1] != in_aux_checksums[file[0]]]
   print("Auxip Files with different Checksum: ", "\n".join([f"{file} - {in_aux_checksums[file[0]]}"
                                                             for file in auxip_cksum_changed]))
   # each availabel auxip file specifies the checksum (and the alog)
   # Select the files with the cksum = in both auxip and input
   return auxip_cksum_availables, [file[0] for file in auxip_cksum_changed]

def search_in_auxip(name,access_token,mode='dev'):
    try:
        headers = {'Content-Type': 'application/json',
                   'Authorization' : 'Bearer %s' % access_token }
        auxip_endpoint = get_auxip_base_endpoint(mode)

        response = requests.get(auxip_endpoint+"/Products?$filter=contains(Name,'"+name+"')&$expand=Attributes",
                                headers=headers)
        if response.status_code != 200:
            print(response.status_code)
            print(response.text)
            raise Exception("Error while accessing auxip")
        json_resp = response.json()
        return json_resp["value"]
    except Exception as e:
        print("%s ==> get ends with error " % name )
        print(e)
        raise e


# post auxdata file to the auxip.svc
def post_to_auxip(access_token,path_to_auxiliary_data_file,uuid,mode='dev'):
    try:
        aux_data_file_name = os.path.basename(path_to_auxiliary_data_file)

        # Get attributes for this aux data file
        attributes = get_attributes(path_to_auxiliary_data_file)

        if attributes is None:
            print("%s ==> Error occured while getting attributes " % path_to_auxiliary_data_file )
            return 2
        # Preparing the json to be posted 

        # convert attributes to an array of dicts 
        attributes_list = []
        for attr_name, attr_value in attributes.items():
            if attr_name not in ['uuid','md5','length']:
                if "Date" in attr_name:
                    value_type = "DateTimeOffset"
                    attr_value = get_odata_datetime_format(attr_value)
                else:
                    value_type = "String"

                attributes_list.append({
                    "ValueType":value_type,
                    "Value":attr_value,
                    "Name":attr_name
                })
        # TODO: It should read "PublicationDate" from attributes, and set now
        #      only if attribute is not set
        publicationdate = datetime.strftime(datetime.utcnow(), odata_datetime_format)
    
        product = {
            "Id" : uuid,
            "ContentLength": int(attributes['length']),
            "ContentType": "application/octet-stream",
            "EvictionDate": datetime.strftime(datetime.utcnow() + dt.timedelta(weeks=5346), odata_datetime_format),
            "Name": aux_data_file_name,
            "OriginDate": get_odata_datetime_format(attributes['processingDate']),
            "PublicationDate": publicationdate,
            "ContentDate" : {
                "Start": get_odata_datetime_format(attributes['beginningDateTime']),
                "End": get_odata_datetime_format(attributes['endingDateTime']),
            },
            "Checksum":[
                {
                    "Algorithm":"MD5",
                    "Value": attributes['md5'],
                    "ChecksumDate": publicationdate
                }
            ],
            "Attributes" : attributes_list
        }

        # =================================================================
        # Post to auxip.svc
        # =================================================================
        if mode == 'dev':
            print(product)
            return 0
        else:
            headers = {'Content-Type': 'application/json','Authorization' : 'Bearer %s' % access_token }
            auxip_base_endpoint = get_auxip_base_endpoint(mode)
            auxip_endpoint = f"{auxip_base_endpoint}/Products"

            response = requests.post(auxip_endpoint,data=json.dumps(product),
                                    headers=headers)

            # print( "Sending product to auxip.svc", product)
            if response.status_code == 201 :
                print("%s ==> sent to auxip.svc successfully " % path_to_auxiliary_data_file )
                return 0
            else:
                print( response.json() )
                print("%s ==> post ends with error " % path_to_auxiliary_data_file )
                return 1
    except Exception as e:
        print("%s ==> post ends with error " % path_to_auxiliary_data_file )

        print( e )
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)

        return 3
