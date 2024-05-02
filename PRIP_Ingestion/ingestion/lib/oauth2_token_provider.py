import sys
import time

import requests
import json
from .attributes import get_attributes
import os
from datetime import datetime
import datetime as dt
import traceback

from .time_formats import odata_datetime_format, get_odata_datetime_format

class OAuth2TokenProvider:
    DEFAULT_EXPIRES = 0
    def __init__(self, auth_endpoint, client_id, secret=None):
        self._auth_endpoint = auth_endpoint
        self._client_id = client_id
        self._auth_secret = secret
        if self._auth_secret is None:
            print("Initialized OAuth2Token provider without specifying secret")
        self._access_token = None
        self.timer_start = None
        self._auth_timeout = self.DEFAULT_EXPIRES

    def _get_token_info(self, json_data, mode='dev'):
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        token_request =  self._auth_endpoint
        print("Request : ", token_request)
        # print("Request payload: ", json_data)
        # print("Request headers: ", headers)
        response = requests.post(token_request, data=json_data, headers=headers)
        if response.status_code != 200:
            print(response.json())
            raise Exception("Bad return code ({})".format(response.status_code))
        # print(response)
        print("Received Token")
        return response.json()

    def get_token_info(self, user, password, mode):
        data = {"username":user, "password":password,
                "client_id": self._client_id,
                "grant_type": "password"}
        if self._auth_secret is not None:
            data.update({'client_secret': self._auth_secret})
        try:
            return self._get_token_info(data, mode)
        except Exception as ex:
            raise Exception("Error " + str(ex) +"when getting access token")

    def get_auth_header(self, user, password, mode):
        timer_stop = time.time()
        token_expired = False
        if self.timer_start is not None:
            elapsed_seconds = timer_stop - self.timer_start
            token_expired = elapsed_seconds > self._auth_timeout
        if token_expired or self._access_token is None:
            token_info = self.get_token_info(user, password, mode)
            # print("Received token info: ", token_info)
            self._access_token = token_info['access_token']
            self._auth_timeout = token_info.setdefault('expires', self.DEFAULT_EXPIRES)
            self.timer_start = time.time()
        return { 'Authorization' : 'Bearer %s' % self._access_token }
        

def _get_adg_domain(mode):
    base_domain = "https://dev.reprocessing-preparation.ml"
    if mode == 'prod':
        base_domain = "https://reprocessing-auxiliary.copernicus.eu"
    return base_domain

def _get_adgs_domain(mode):
    # TODO: Get from Env Var ADGS_URL or ADGS_ENDPOINT
    return "https://adgs.copernicus.eu"

class AuxipOauth2TokenPRovider(OAuth2TokenProvider):
    def __init__(self, mode):
        tk_realm = "reprocessing-preparation"
        auth_endpoint = self._get_auth_base_endpoint(mode)
        auxip_auth_endpoint = "{}/realms/{}/protocol/openid-connect/token".format(auth_endpoint, tk_realm)
        OAuth2TokenProvider.__init__(self, auxip_auth_endpoint, "reprocessing-preparation")

    def _get_auth_base_endpoint(self, mode):
        endpoint_domain = _get_adg_domain(mode) 
        service_endpoint = "auth"
        base_endpoint = f"{endpoint_domain}/{service_endpoint}"
        return base_endpoint


class AdgsOauth2TokenProvider(OAuth2TokenProvider):
    def __init__(self, secret):
        # TODO: read endpoint and client id from configuration/environment
        adgs_auth_endpoint = _get_adgs_domain('prod') + "/" + "getAuthToken"
        client_id = "adgs-client"
        OAuth2TokenProvider.__init__(self, adgs_auth_endpoint, client_id, secret)

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


