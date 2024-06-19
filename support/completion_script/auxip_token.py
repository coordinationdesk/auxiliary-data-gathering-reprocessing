#!/bin/python
# -*- coding: utf-8 -*-

#import sys
import os
import argparse


import requests
import json

def get_api_base_url(mode='dev'):
    api_base_url = "https://dev.reprocessing-preparation.ml/auth/realms/reprocessing-preparation"
    if mode == 'prod':
        api_base_url = "https://reprocessing-auxiliary.copernicus.eu/auth/realms/reprocessing-preparation"
    return api_base_url

def get_token_endpoint(mode='dev'):
	base_url = get_api_base_url(mode)
	return f"{base_url}/protocol/openid-connect/token"

def get_token_info(user,password,mode='dev'):
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {"username":user, "password":password,"client_id":"reprocessing-preparation","grant_type":"password"}
    token_endpoint = get_token_endpoint(mode)

    response = requests.post(token_endpoint,data=data,headers=headers)
    if response.status_code != 200:
        print(response.json())
        raise Exception("Bad return code when getting token")
    return response.json()


    # access_token expires_in 900 seconds (15 minutes) 

    if timer < 900 :
        # access_token is still valid
        return token_info
    else:
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = {"refresh_token":token_info['refresh_token'],"client_id":"reprocessing-preparation","grant_type":"refresh_token"}
        token_endpoint = get_token_endpoint(mode)
        response = requests.post(token_endpoint,data=data,headers=headers)
        if response.status_code != 200:
            print(response.json())
            raise Exception("Bad return code when refreshing token")
        return response.json()

def main():

    parser = argparse.ArgumentParser(description="",  # main description for help
            epilog='Beta', formatter_class=argparse.RawTextHelpFormatter)  # displayed after help
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
    parser.add_argument(
            "-o",
            "--output",
            help="Output file where to store token ",
            required=True)
    args = parser.parse_args()
    auxip_token = get_token_info(args.user, args.password, args.mode)
    # Write token to specified file (overwrite)
    with open(args.output, 'w+') as token_file:
    	json.dump(auxip_token, token_file)
    print(auxip_token['access_token'])

if __name__ == "__main__":
	main()