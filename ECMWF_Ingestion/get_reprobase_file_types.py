import argparse
import datetime
import os
import json
import requests
from ingestion.lib.auxip import get_token_info

odata_datetime_format = "%Y-%m-%dT%H:%M:%SZ[GMT]"
odata_datetime_nosec_format = "%Y-%m-%dT%H:%MZ[GMT]"


verify_cert=True
def send_request(mode, access_token):
    headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer %s' % access_token}
    auxip_endpoint = "https://dev.reprocessing-preparation.ml/reprocessing.svc/AuxTypes?$expand=ProductLevels"
    res = None
    if mode == 'prod':
        auxip_endpoint = "https://auxiliary.copernicus.eu/reprocessing.svc/AuxTypes?$expand=ProductLevels"
    resp = requests.get(auxip_endpoint,headers=headers,verify=verify_cert)
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
    parser.add_argument("-o", "--output",
                        help="output json folder",
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
    print("Called with user ", args.user, " mode: ", args.mode)
    token_info = get_token_info(args.user, args.password, args.mode)
    access_token = token_info['access_token']
    result = send_request(args.mode,access_token)
    print(result)
    for v in result["value"]:
        with open(os.path.join(args.output,v["LongName"]+".json"),"w") as f:
            json.dump(v,f)


if __name__ == "__main__":
    main()
