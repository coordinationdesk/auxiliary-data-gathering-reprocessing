import argparse
import datetime
import json
import requests
from ingestion.lib.auxip import get_token_info

odata_datetime_format = "%Y-%m-%dT%H:%M:%SZ[GMT]"
odata_datetime_nosec_format = "%Y-%m-%dT%H:%MZ[GMT]"


def send_request(jsonload, mode, access_token):
    headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer %s' % access_token}
    res = jsonload
    if "Id" in jsonload:
        auxip_endpoint = "https://dev.reprocessing-preparation.ml/reprocessing.svc/AuxFiles(" + jsonload["Id"]+")"
        if mode == 'prod':
            auxip_endpoint = "https://auxiliary.copernicus.eu/reprocessing.svc/AuxFiles(" + jsonload["Id"]+")"
    elif "LongName" in jsonload:
        auxip_endpoint = "https://dev.reprocessing-preparation.ml/reprocessing.svc/AuxTypes('" + jsonload["LongName"]+"')"
        if mode == 'prod':
            auxip_endpoint = "https://auxiliary.copernicus.eu/reprocessing.svc/AuxTypes('" + jsonload["LongName"]+"')"
    resp = requests.put(auxip_endpoint,headers=headers, json=jsonload)
    if resp.status_code != 200:
        print(resp.status_code)
        print(resp.text)
        raise Exception("Bad return code for request: "+auxip_endpoint)
    res = resp.json()
    resp.close()
    return res


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
    with open(args.input) as f:
        json_base = json.load(f)
    token_info = get_token_info(args.user, args.password,args.mode)
    access_token = token_info['access_token']
    result = send_request(json_base,args.mode,access_token)
    print(result)


if __name__ == "__main__":
    main()
