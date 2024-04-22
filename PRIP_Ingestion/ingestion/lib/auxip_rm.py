import sys
import time

import requests
import json
from .attributes import get_attributes
import os
from datetime import datetime
import datetime as dt
import traceback
from .auxip import get_odata_datetime_format, get_auxip_base_endpoint


# post auxdata file to the auxip.svc
def remove_from_auxip(access_token,aux_data_file_name,uuid,mode='dev'):
    try:

        # =================================================================
        # Post to auxip.svc
        # =================================================================
        if mode == 'dev':
            print("Remove ", aux_data_file_name, " with uuid: ", uuid)
            return 0
        else:
            headers = {'Content-Type': 'application/json','Authorization' : 'Bearer %s' % access_token }
            auxip_base_endpoint = get_auxip_base_endpoint(mode)
            auxip_endpoint = f"{auxip_base_endpoint}/Products"

            auxip_request = f"{auxip_endpoint}({uuid})"
            print("Executing delete on url ", auxip_request)
            response = requests.delete(auxip_request,
                                    headers=headers)

            # print( "Sending product to auxip.svc", product)
            if response.status_code == 204 :
                print("%s ==> sent to auxip.svc successfully " % aux_data_file_name )
                return 0
            else:
                print( response.json() )
                print("%s ==> post ends with error %d" % (aux_data_file_name, response.status_code) )
                return 1
    except Exception as e:
        print("%s ==> post ends with error " % aux_data_file_name )

        print( e )
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)

        return 1

# put auxdata file update to the auxip.svc
def update_to_auxip(access_token,path_to_auxiliary_data_file,uuid,mode='dev'):
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

            auxip_put_url = f"{auxip_endpoint}?Id={uuid}"
            response = requests.put(auxip_put_url,data=json.dumps(product),
                                    headers=headers)

            # print( "Sending product update to auxip.svc", product)
            if response.status_code == 201 :
                print("%s ==> sent to auxip.svc successfully " % path_to_auxiliary_data_file )
                return 0
            else:
                print( response.json() )
                print("%s ==> put ends with error " % path_to_auxiliary_data_file )
                return 1
    except Exception as e:
        print("%s ==> put ends with error " % path_to_auxiliary_data_file )

        print( e )
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)

        return 3
