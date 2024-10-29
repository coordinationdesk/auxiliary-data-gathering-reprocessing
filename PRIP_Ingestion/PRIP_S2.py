import requests
from requests.auth import HTTPBasicAuth
import time,sys,os
from ingestion.lib.auxip import get_latest_of_type,are_file_availables,get_token_info,are_file_availables_w_checksum
from odata_request import build_paginated_request

# MAXIMUM RESULTS to retrieve 
# in a single session
# defined to limit the number of files downloaded 
# within a single session
MAX_SESSION_RESULTS = 350

# TODO: Define class to hold AUXIP, LTA credentials, lta_base_url
#  type_list, satellite, mode
# 
def get_latest_pub_date(auxip_user, auxip_password, type_list, sat, mode):
    # Get latest published product for types
    token_info = get_token_info(auxip_user, auxip_password, mode=mode)
    # print("Access Token: ", token_info['access_token'])
    return get_latest_of_type(access_token=token_info['access_token'],
                              aux_type_list=type_list,
                              sat=sat,mode=mode)

def _build_lta_simple_base_request(base_url):
    lta_request = base_url + "Products?$orderby=PublicationDate asc"
    return lta_request

def _build_lta_names_base_request(base_url,
                           names_list):
    lta_request = _build_lta_simple_base_request(base_url) + \
                "&$filter="
    lta_request += "("
    lta_request += f"contains(Name,'{names_list[0]}')"
    for prod_name in names_list[1:]:
        if prod_name:
            lta_request += f" or contains(Name,'{prod_name}')"
    lta_request += ")"
    return lta_request

def _build_lta_base_request(base_url,
                           type_list, sat,
                           from_date, to_date,
                           date_parameter='PublicationDate'):
    lta_request = _build_lta_simple_base_request(base_url) + \
                "&$filter="+ date_parameter + " gt " + from_date
    if to_date and len(to_date):
        lta_request = lta_request + " and " + date_parameter + " lt " + to_date
    lta_request = lta_request + " and "
    if len(type_list) > 1:
        lta_request += "("
    lta_request += f"contains(Name,'{type_list[0]}')"
    for prod_type in type_list[1:]:
        lta_request += f" or contains(Name,'{prod_type}')"
    if len(type_list) > 1:
        lta_request += ")"
    lta_request += " and startswith(Name,'"+sat+"')"
    return lta_request
    
def _get_lta_aux_files(response):
    aux_files = []
    resp_json = response.json()
    print("Number of element found with curr request: ", len(resp_json["value"]))
    if len(resp_json["value"]) == 0:
        return []
    #print(resp_json["value"][0])
    for aux_file in resp_json["value"]:
        ID = aux_file["Id"]
        file_size = aux_file["ContentLength"]
        aux_files.append((ID, aux_file["Name"], file_size))
    return aux_files

def _get_lta_file_results(user, password, lta_request, max_results, req_timeout=30):
    next_trial_time = 60 # seconds
    file_list = []
    headers = {'Content-type': 'application/json'}
    step=min(200, max_results)
    max_retry = 3
    auth_data = HTTPBasicAuth(user, password)
    for i in range(0, max_results, step):
        request_top = build_paginated_request(lta_request, i, step)
        print("[BEGIN] LTA Request : ", request_top)
        ntrials = 0
        while ntrials < max_retry:
            if ntrials > 0:
                time.sleep(ntrials * next_trial_time)
            try:
                response = requests.get(request_top, auth=auth_data,
                                        headers=headers,
                                        timeout=req_timeout,
                                        verify=False)
                break
            except requests.Timeout as to_exc:
                print("Request from ", i, " failed after timeout (", req_timeout,"): ", str(to_exc))
                response = None
                # Make another try, until max_retry reached
                ntrials += 1
                print("Waiting for next retry ", ntrials * next_trial_time, " secs")
            if ntrials == max_retry:
                print("[END] Failed LTA Request after ", ntrials, " retries")
        if response is not None:
            if response.status_code == 200:
                resp_json = response.json()
                print("Number of element found with curr request: ", len(resp_json["value"]))
                 # if len(resp_json["value"]) == 0:
                 #   break
                #print(resp_json["value"][0])
                for aux_file in resp_json["value"]:
                    print(aux_file)
                    ID = aux_file["Id"]
                    file_size = aux_file["ContentLength"]
                    cksum_info = aux_file["Checksum"][0]
                    file_cksum = cksum_info["Value"]
                    cksum_alg = cksum_info["Algorithm"]
                    cksum_date = cksum_info["ChecksumDate"]
                    file_list.append((ID, aux_file["Name"], file_cksum, cksum_alg, cksum_date, file_size))
                if len(resp_json["value"]) < step:
                    break
            else:
                raise Exception(f"Error on request - code : {response.status_code}, text: {response.text}")
    return file_list

def get_lta_files_from_names(user, password, lta_base_url,
                  names_list,
                  batch_size,
                  max_results=MAX_SESSION_RESULTS):
    print("Querying LTA (", lta_base_url, "), for Names ")
    retrieved_results = []
    # NUmber of names to be included in each single request
    req_num_names = batch_size
    # Retrieve List of files from LTA
    # get results on small subsets of names list
    for i in range(0, len(names_list), req_num_names): 
        names_sublist = names_list[i: min(i + req_num_names, len(names_list))] 
        print("\nRequesting names: ", names_sublist)
        if names_sublist[0]:
            lta_request = _build_lta_names_base_request(lta_base_url, names_sublist)
        retrieved_results.extend( _get_lta_file_results(user, password, lta_request, max_results))
    return retrieved_results


def get_lta_files(user, password, lta_base_url,
                  type_list, sat,
                  from_date, to_date="",
                  date_parameter='PublicationDate',
                  max_results=MAX_SESSION_RESULTS):
    print("Querying LTA (", lta_base_url, "), for Sat ", sat, ", from date ", from_date)
    # Retrieve List of files from LTA
    lta_request = _build_lta_base_request(lta_base_url, type_list, sat, from_date, to_date)
    return _get_lta_file_results(user, password, lta_request, max_results)

def prip_list_from_names(user, password, auxip_user, auxip_password,
                         lta_base_url,aux_names, mode="prod"):
    file_list = []
    lta_files = get_lta_files_from_names(user, password, lta_base_url,
                              aux_names)
    # lta_files is a list of pairs: first item is ID, secondi item is filename, third is size,
    # fourth is checksum, fifth is checksum algorithm
    filename_checksum_list = [(f_rec[1],f_rec[2],f_rec[3],f_rec[4]) for f_rec in lta_files]
    # Get list of files that are present in AUZIP, with same checksum
    availables, cksum_changed = are_file_availables_w_checksum(auxip_user, auxip_password,
                                     filename_checksum_list,
                                     step=10, mode=mode)
    print("Of ", len(aux_names), " requested Aux Names, ",
          len(availables), " Files are already present in AUXIP",
          len(cksum_changed), " Files have different Cksum")
    auxip_missing_files = [f for f in lta_files if f[1] not in availables]
    return  auxip_missing_files

# latest_pub_date is set to from_date, specified by caller
# if not specified, it is taken from auxip latest publication date
#  for all the specified types
# Expected date in format: YYYY-mm-DDTHH:MM:SS.mmmmmmZ
def prip_list(user, password, auxip_user, auxip_password,
              lta_base_url, type_list,
              sat, mode="prod", from_date=None, to_date=None):
    file_list = []
    if len(type_list) == 0:
        return file_list
    print("Querying LTA for types ", type_list, ", Sat: ", sat,
          ", From date: ", from_date, ", to ", to_date)
    latest_pub_date = from_date
    if latest_pub_date is None:
        # TODO: get TOken and use for are_file_available
        latest_pub_date = get_latest_pub_date(auxip_user, auxip_password,
                                              type_list,
                                              sat, mode)
        to_date = None
        if latest_pub_date is None:
            print("No file available in auxip for types : ", type_list)
            return file_list
        print("Publication date to query on LTA retrieved from AUXIP: ", latest_pub_date)
    lta_files = get_lta_files(user, password, lta_base_url,
                              type_list,
                              sat, latest_pub_date, to_date)
    # lta_files is a list of pairs: first item is ID, secondi item is filename
    filename_list = [f_rec[1] for f_rec in lta_files]
    # Get list of files that are present in AUZIP
    availables = are_file_availables(auxip_user, auxip_password, filename_list,
                                     step=10, mode=mode)
    #print("Files already present in AUXIP: ", availables)
    auxip_missing_files = [f for f in lta_files if f[1] not in availables]
    return auxip_missing_files


def prip_sensing_list(user, password, auxip_user, auxip_password,
              lta_base_url, type_list,
              sat, mode="prod", from_date=None, to_date=None):
    file_list = []
    if len(type_list) == 0:
        return file_list
    print("Querying LTA for types ", type_list, ", Sat: ", sat,
          ", From date: ", from_date, ", to ", to_date)
    latest_pub_date = from_date
    # NOTE: we are retrieving from LTA based on sensing,
    # but we are checking last publication date on AUXIP
    if latest_pub_date is None:
        # TODO: get TOken and use for are_file_available
        latest_pub_date = get_latest_pub_date(auxip_user, auxip_password,
                                              type_list,
                                              sat, mode)
        to_date = None
        if latest_pub_date is None:
            print("No file available in auxip for types : ", type_list)
            return file_list
        print("Publication date to query on LTA retrieved from AUXIP: ", latest_pub_date)
    lta_files = get_lta_files(user, password, lta_base_url,
                              type_list,
                              sat, latest_pub_date, to_date,
                              date_parameter='ContentDate/Start')
    # lta_files is a list of pairs: first item is ID, secondi item is filename
    filename_list = [f_rec[1] for f_rec in lta_files]
    # Get list of files that are present in AUZIP
    availables = are_file_availables(auxip_user, auxip_password, filename_list,
                                     step=10, mode=mode)
    #print("Files already present in AUXIP: ", availables)
    auxip_missing_files = [f for f in lta_files if f[1] not in availables]
    return auxip_missing_files
def prip_download(id, name,user, password,base_url,output_folder, req_timeout=30):
    next_trial_time = 60 # seconds
    try:
        headers = {'Content-type': 'application/json'}
        # Get output file path
        id_folder = output_folder
        os.makedirs(id_folder,exist_ok=True)
        file_path = os.path.join(id_folder, name)
        if os.path.exists(file_path) and os.path.getsize(file_path) != 0:
            print("\nFile already exists and is not empty %s " % (name))
            return
        print("\n[BEGIN] Downloading %s " % (name))
        # get ID and size of the product
        ntrials = 0
        max_retry = 3
        while ntrials < max_retry:
            time.sleep(ntrials * next_trial_time)
            try:
                product_response = requests.get(base_url+"Products(%s)/$value" % id,
                                                auth=HTTPBasicAuth(user, password),
                                                headers=headers,
                                                timeout=req_timeout,
                                                stream=True, verify=False)
                if product_response.status_code == 404:
                    raise Exception("Not found on the server : "+base_url+"/Products(%s)/$value" % id)
                total_length = int(product_response.headers.get('content-length'))
                if not total_length: # no content length header
                     fid.write(product_response.content)
                else:
                    with open(file_path,"wb") as fid:
                        print("Starting download")
                        start = time.perf_counter()
                        downloaded_bytes = 0
                        max_chunk_size = 4096
                        num_batches = 0 
                        progress_period = total_length / max_chunk_size / 10 + 1
                        for data in product_response.iter_content(chunk_size=4096):
                            downloaded_bytes += len(data)
                            fid.write(data)
                            if (num_batches % progress_period) == 0:
                                sys.stdout.write("\r...Downloaded %s/%s bytes" %( downloaded_bytes,total_length))
                                sys.stdout.flush()
                            num_batches += 1
                            # done = int(50 * downloaded_bytes / total_length)
                            # sys.stdout.write("\r[%s%s] %s bps" % ('=' * done, ' ' * (50-done), downloaded_bytes//(time.perf_counter() - start)))
                            # sys.stdout.flush()
                            # fid.write(product_response.content)
                        dwl_time = time.perf_counter() - start
                        print("Download took ", dwl_time, " [s] - ", downloaded_bytes/dwl_time/1024/1024, " [Mb/s]")
                print("[END] Download Done\n")
                break
            except requests.Timeout as to_exc:
                print("Request For product  ", id, " info and download failed after timeout (", req_timeout,"): ", str(to_exc))
                response = None
                if os.path.exists(file_path):
                    os.remove(file_path)
                # Make another try, until max_retry reached
                ntrials += 1
                print("Waiting for next retry ", ntrials * next_trial_time, " secs")
            if ntrials == max_retry:
                print("[END] Failed download of product ", id, " after ", ntrials, " retries")
                raise Exception("Failed download of product {} after {} retries".format(id, ntrials))
    except Exception as e:
        print(e)
        raise e
