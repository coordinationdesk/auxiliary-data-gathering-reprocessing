import requests
import requests
import json
from .attributes import get_attributes
import os
from datetime import datetime
import datetime as dt

odata_datetime_format = "%Y-%m-%dT%H:%M:%S.%fZ"

verify_cert=True
def get_odata_datetime_format(datetime_string):

    odata_format = datetime_string

    try:
        datetime.strptime(datetime_string, odata_datetime_format)
    except ValueError:
        
        # Try these following fomats 
        # "%Y%m%dT%H%M%S"  20201013T065032
        try:
            date_time = datetime.strptime(datetime_string, "%Y%m%dT%H%M%S")
            odata_format = datetime.strftime(date_time, odata_datetime_format)
        except ValueError:
            pass

        # 2021-02-23T05:29:16 in S1 .EOF  and S2 files
        try:
            date_time = datetime.strptime(datetime_string, "%Y-%m-%dT%H:%M:%S")
            odata_format = datetime.strftime(date_time, odata_datetime_format)
        except ValueError:
            pass

        # 2020-10-06T00:00:00.000000   ( Z is missing )
        try:
            date_time = datetime.strptime(datetime_string, "%Y-%m-%dT%H:%M:%S.%f")
            odata_format = datetime_string + 'Z'
        except ValueError:
            pass

    return odata_format


def get_token_info(user,password,mode='dev'):
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {"username":user, "password":password,"client_id":"reprocessing-preparation","grant_type":"password"}

    token_endpoint = "https://dev.reprocessing-preparation.ml/auth/realms/reprocessing-preparation/protocol/openid-connect/token"
    if mode == 'prod':
        token_endpoint = "https://reprocessing-auxiliary.copernicus.eu/auth/realms/reprocessing-preparation/protocol/openid-connect/token"
    print(token_endpoint)
    response = requests.post(token_endpoint,data=data,headers=headers)
    if response.status_code != 200:
        print(response.json())
        raise Exception("Bad return code when getting token")
    return response.json()


def refresh_token_info(token_info,timer,mode='dev'):
    # access_token expires_in 900 seconds (15 minutes) 

    if timer < 900 :
        # access_token is still valid
        return token_info
    else:
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = {"refresh_token":token_info['refresh_token'],"client_id":"reprocessing-preparation","grant_type":"refresh_token"}
        token_endpoint = "https://dev.reprocessing-preparation.ml/auth/realms/reprocessing-preparation/protocol/openid-connect/token"
        if mode == 'prod':
            token_endpoint = "https://reprocessing-auxiliary.copernicus.eu/auth/realms/reprocessing-preparation/protocol/openid-connect/token"
        response = requests.post(token_endpoint,data=data,headers=headers)
        if response.status_code != 200:
            print(response.json())
            raise Exception("Bad return code when refreshing token")
        return response.json()  


def is_file_available(access_token,aux_data_file_name,mode='dev'):
    try:
        headers = {'Content-Type': 'application/json','Authorization' : 'Bearer %s' % access_token }
        auxip_endpoint = "https://dev.reprocessing-preparation.ml/auxip.svc/Products"
        if mode == 'prod':
            auxip_endpoint = "https://reprocessing-auxiliary.copernicus.eu/auxip.svc/Products"

        response = requests.get(auxip_endpoint+"?$filter=contains(Name,'"+aux_data_file_name+"')",headers=headers,verify=verify_cert)
        if response.status_code != 200:
            print(response.status_code)
            print(response.text)
            raise Exception("Error while accessing auxip")
        print(response.text)
        json_resp = response.json()
        return len(json_resp["value"]) > 0
    except Exception as e:
        print("%s ==> get ends with error " % aux_data_file_name )
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
            return 1
        # Preparing the json to be posted 
        print(attributes)
        # convert attributes to an array of dicts 
        attributes_list = []
        for att in attributes:
            if att not in ['uuid','md5','length']:
                value = attributes[att]
                if "Date" in att:
                    value_type = "DateTimeOffset"
                    value = get_odata_datetime_format(attributes[att])
                else:
                    value_type = "String"

                attributes_list.append({
                    "ValueType":value_type,
                    "Value":value,
                    "Name":att
                })
                
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
            auxip_endpoint = "https://dev.reprocessing-preparation.ml/auxip.svc/Products"
            if mode == 'prod':
                auxip_endpoint = "https://reprocessing-auxiliary.copernicus.eu/auxip.svc/Products"

            response = requests.post(auxip_endpoint,data=json.dumps(product),headers=headers)

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

        return 1
