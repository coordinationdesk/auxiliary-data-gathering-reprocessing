import argparse
import datetime
import glob
import json
import time
import os
import sys
import requests
from ingestion.lib.auxip import get_token_info

odata_datetime_format = "%Y-%m-%dT%H:%M:%SZ[GMT]"
odata_datetime_nosec_format = "%Y-%m-%dT%H:%MZ[GMT]"

def get_reprobase_base_endpoint(mode):
    base_endpoint = "https://dev.reprocessing-preparation.ml/reprocessing.svc"
    if mode == 'prod':
        base_endpoint = "https://reprocessing-auxiliary.copernicus.eu/reprocessing.svc"
    return base_endpoint

def send_request(request, jsonload, access_token):
    headers = {'Content-type': 'application/json','Authorization' : 'Bearer %s' % access_token}
    try:
        resp = requests.put(request, headers=headers, json=jsonload)
    except Exception as e:
        time.sleep(1)
        resp = requests.put(request, headers=headers, json=jsonload)

    if resp.status_code != 200:
        print(resp.status_code)
        print(resp.text)
        raise Exception("Bad return code for request: "+request)
    try:
        res = resp.json()
    except Exception as e:
        print(resp)
        print(resp.text)
        raise
    finally:
        resp.close()
    return res

def upload_json(json_file, base_url, token_info):
    result = True
    with open(json_file) as f:
        json_base = json.load(f)
    if "Id" in json_base:
        request = base_url + "/AuxFiles(" + json_base["Id"]+")"
    else:
        request = base_url + "/AuxTypes('" + json_base["LongName"]+"')"
    print(request)
    try:
        result = send_request(request, json_base, token_info['access_token'])
        print(result)
    except Exception as e:
        print(e)
        print("Le fichier {0} n'a pas été uploadé sur reprobase".format(json_file))
        result = False
    print("Success: ", result)
    return result

def main():
    parser = argparse.ArgumentParser(description="",  # main description for help
            epilog='Beta', formatter_class=argparse.RawTextHelpFormatter)  # displayed after help
    parser.add_argument("-i", "--input",
                        help="input json file",
                        required=True)
    parser.add_argument("-u", "--user",
                        help="Auxip user with reporting role",
                        required=True)
    parser.add_argument("-pw", "--password",
                        help="User password ",
                        required=True)
    parser.add_argument("-m", "--mode",
                        help="dev or prod",
                        default="dev",
                        required=False)
    args = parser.parse_args()
    token_info = get_token_info(args.user, args.password, args.mode)
    access_token = token_info['access_token']
    template_base = None

    fileUploadError=[]

    url = get_reprobase_base_endpoint(args.mode)
        
    if os.path.isfile(args.input):
        if not upload_json(args.input, url, token_info):
            fileUploadError.append(args.input)
    else:
        timer_start = time.time()
        for j in glob.glob(os.path.join(args.input,"*.json")):
            # refesh token if necessary
            timer_stop = time.time()
            elapsed_seconds = timer_stop - timer_start
            if elapsed_seconds > 300 :
                timer_start = time.time()
                token_info = get_token_info(args.user, args.password, mode=args.mode)
            if not upload_json(j, url, token_info):
                fileUploaderror.append(j)
    if len(fileUploadError) > 0:
        print("Une erreur s'est produite pour l'upload des fichiers suivants :")       
        for f in fileUploadError:
            print(f)
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
