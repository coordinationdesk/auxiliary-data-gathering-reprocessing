import requests
from requests.auth import HTTPBasicAuth
import time,sys,os
from ingestion.lib.auxip import get_token_info
from ingestion.odata_request import build_paginated_request

# MAXIMUM RESULTS to retrieve 
# in a single session
# defined to limit the number of files downloaded 
# within a single session
MAX_SESSION_REQUESTS = 10

# TODO: Define class to hold AUXIP, LTA credentials, lta_base_url
#  type_list, satellite, mode
# 


def _build_reprobase_simple_base_request(base_url):
    api_request = base_url + "/AuxFiles?$orderby=Unit asc"
    return api_request

def _build_reprobase_names_base_request(base_url,
                           names_list):
                 # "&$expand=AuxType" \
    api_request = _build_reprobase_simple_base_request(base_url) + \
                "&$filter="
    api_request += "("
    api_request += f"contains(FullName,'{names_list[0]}')"
    for prod_name in names_list[1:]:
        if prod_name:
            api_request += f" or contains(FullName,'{prod_name}')"
    api_request += ")"
    return api_request

def _get_response_aux_files(response):
    aux_files = []
    resp_json = response.json()
    print("Received response: ", resp_json)
    print("Number of element found with curr request: ", len(resp_json["value"]))
    if len(resp_json["value"]) == 0:
        return []
    #print(resp_json["value"][0])
    for aux_file in resp_json["value"]:
        ID = aux_file["Id"]
        file_name = aux_file["FullName"]
        other_values =  [value for key, value in aux_file.items()
                         if key not in ("Id", "FullName")]
        #file_list.append((ID, aux_file["Name"], file_name))
        aux_files.append((ID, file_name, *other_values))
    return aux_files


def _get_api_file_results(user, password, api_request, mode, req_timeout=30):
    # Handle periodic token retrieval
    timer_start = time.time()
    token_info = get_token_info(user, password,mode=mode)
    access_token = token_info['access_token']
    
    next_trial_time = 60 # seconds
    file_list = []
    headers = {'Content-type': 'application/json'}
    max_retry = 3
    print("[BEGIN] REPROBASE Request : ", api_request)
    ntrials = 0
    while ntrials < max_retry:
        if ntrials > 0:
            time.sleep(ntrials * next_trial_time)
        try:
            # get token if previous one expired
            timer_stop = time.time()
            elapsed_seconds = timer_stop - timer_start
            if elapsed_seconds > 350:
                timer_start = time.time()
                token_info = get_token_info(user, password, mode=mode)
                access_token = token_info['access_token']
            headers.update({ 'Authorization': 'Bearer %s' % access_token})
            print("num trial : ", ntrials + 1, ", timeout: ", req_timeout, "s")
            response = requests.get(api_request, 
                                    headers=headers,
                                    timeout=req_timeout,
                                    verify=False)
            break
        except requests.Timeout as to_exc:
            print("Request   failed after timeout (", req_timeout,"): ", str(to_exc))
            response = None
            # Make another try, until max_retry reached
            ntrials += 1
            print("Waiting for next retry ", ntrials * next_trial_time, " secs")
        if ntrials == max_retry:
            print("[END] Failed REPROBASE Request after ", ntrials, " retries")
    if response is not None:
        if response.status_code == 200:
            file_list = _get_response_aux_files(response)
        else:
            raise Exception("Error on request code : "+str(response.status_code))
    return file_list


def get_reprobase_base_endpoint(mode):
    base_endpoint = "https://dev.reprocessing-preparation.ml/reprocessing.svc"
    if mode == 'prod':
        base_endpoint = "https://reprocessing-auxiliary.copernicus.eu/reprocessing.svc"
    return base_endpoint


# Delete Reprobase data with specified id 
# Delete Reprobase data with specified filename 
def _remove_from_reprobase(access_token,reprobase_endpoint, aux_data_file_name,uuid,mode='dev'):
    try:

        # =================================================================
        # DELETE from reprocessing.svc
        # =================================================================
        if mode == 'dev':
            print("Remove ", aux_data_file_name, " with uuid: ", uuid)
            return 0
        else:
            headers = {'Content-Type': 'application/json','Authorization' : 'Bearer %s' % access_token }

            reprobase_request = f"{reprobase_endpoint}({uuid})"
            print("[BEGIN] REPROBASE Delete Request : ", reprobase_request)
            response = requests.delete(reprobase_request,
                                    headers=headers)

            # print( "Sending product to reprocessing.svc", product)
            if response.status_code == 204 :
                print("%s ==> sent to reprocessing.svc successfully " % aux_data_file_name )
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

def remove_reprobase_files(user, password,
                           id_names_list,
                           mode="prod"):
    # NUmber of names to be included in each single request
    reprobase_base_endpoint = get_reprobase_base_endpoint(mode)
    reprobase_endpoint = f"{reprobase_base_endpoint}/AuxFiles"
    print("Removin Reprocessing Record ReprocessingSvc (",reprobase_endpoint, "), for Names ")
    timer_start = time.time()
    token_info = get_token_info(user, password,mode=mode)
    access_token = token_info['access_token']
    retrieved_results = []
    for aux_id, aux_file in id_names_list:
        print("Trying ID: ", aux_id, ", FullName: ", aux_file)
        timer_stop = time.time()
        elapsed_seconds = timer_stop - timer_start
        if elapsed_seconds > 350:
            timer_start = time.time()
            token_info = get_token_info(user, password, mode=mode)
            access_token = token_info['access_token']
        if _remove_from_reprobase(access_token,reprobase_endpoint, aux_file,aux_id, mode) == 0:
            retrieved_results.append((aux_id, aux_file))
    return retrieved_results

def get_reprobase_files_from_names(user, password, 
                                   names_list,
                                   mode="prod",
                                   max_request_names=MAX_SESSION_REQUESTS):
    # NUmber of names to be included in each single request
    reprobase_api_base_url = get_reprobase_base_endpoint(mode)
    print("Querying ReprocessingSvc (", reprobase_api_base_url, "), for Names ")
    retrieved_results = []

    # Retrieve List of files from LTA
    #   Retrieve at most N files at time
    # get results on small subsets of names list
    for i in range(0, len(names_list), max_request_names):
        names_sublist = names_list[i: min(i + max_request_names, len(names_list))]
        print("\nRequesting names: ", names_sublist)
        api_request = _build_reprobase_names_base_request(reprobase_api_base_url, names_sublist)
        retrieved_results.extend( _get_api_file_results(user, password, api_request, mode))
    return retrieved_results

