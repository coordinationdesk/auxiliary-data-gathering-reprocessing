import requests
import time,sys,os
from ingestion.lib.auxip import get_latest_of_type,are_file_availables,get_token_info,are_file_availables_w_checksum
from ingestion.lib.oauth2_token_provider import AdgsOauth2TokenProvider
from ingestion.odata_request import build_paginated_request

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

class ADGS_Authentication:
    def __init__(self, user, password, secret):
        print("Creating token provider with secret ", secret)
        self._token_provider = AdgsOauth2TokenProvider(secret)
        self._user = user
        self._password = password
        self._mode = 'prod'

    def get_auth_header(self):
        return self._token_provider.get_auth_header(self._user, self._password, self._mode)

class ADGS_Retrieval:
    def __init__(self, base_url, adgs_auth):
        self._base_url = base_url
        self._adgs_auth = adgs_auth

    def _build_lta_simple_base_request(self):
        lta_request = self._base_url + "/Products?$orderby=PublicationDate asc"
        return lta_request

    def _build_lta_names_base_request(self,
                                      names_list):
        lta_request = self._build_lta_simple_base_request() + \
                    "&$filter="
        lta_request += "("
        lta_request += f"contains(Name,'{names_list[0]}')"
        for prod_name in names_list[1:]:
            if prod_name:
                lta_request += f" or contains(Name,'{prod_name}')"
        lta_request += ")"
        return lta_request

    def _build_lta_base_request(self,
                               type_list, sat,
                               from_date, to_date):
        # Check: if not type and no date was specified,
        # request cannot be build
        if not from_date and not to_date and len(type_list) == 0:
             raise Exception("Archive Request without either type or date condition cannot be issued")
        # TODO: Modify to manage from_date not specified
        lta_request = self._build_lta_simple_base_request() + \
                    "&$filter="
        if from_date and len(from_date):
            lta_request = lta_request + " PublicationDate gt " + from_date
        if to_date and len(to_date):
            conjunction = " and " if from_date else " "
            lta_request = lta_request + conjunction + " PublicationDate lt " + to_date
        if from_date or to_date:
            # And conjunction is needed if at least one time condition was specified
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
    
    def _get_lta_file_results(self, lta_request, max_results, req_timeout=30):
        next_trial_time = 60 # seconds
        file_list = []
        headers = {'Content-type': 'application/json'}
        step=min(200, max_results)
        max_retry = 3
        for i in range(0, max_results, step):
            request_top = build_paginated_request(lta_request, i, step)
            print("[BEGIN] LTA Request : ", request_top)
            ntrials = 0
            while ntrials < max_retry:
                if ntrials > 0:
                    time.sleep(ntrials * next_trial_time)
                try:
                   #  response = requests.get(request_top, auth=HTTPBasicAuth(user, password),
                    req_headers = dict(headers)
                    req_headers.update(self._adgs_auth.get_auth_header())
                    #print("Executing request ", request_top, ", timeout: ", req_timeout)
                    response = requests.get(request_top, 
                                            headers=req_headers,
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
                    print("[END] Failed LTA Request ", request_top, " after ", ntrials, " retries")
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

    def get_lta_files_from_names(self,
                                 names_list,
                                 batch_size=20,
                                 max_results=MAX_SESSION_RESULTS):
        print("Querying LTA (", self._lta_base_url, "), for Names ")
        retrieved_results = []
        # NUmber of names to be included in each single request
        req_num_names = batch_size
        # Retrieve List of files from LTA
        # get results on small subsets of names list
        for i in range(0, len(names_list), req_num_names): 
            names_sublist = names_list[i: min(i + req_num_names, len(names_list))] 
            print("\nRequesting names: ", names_sublist)
            if names_sublist[0]:
                lta_request = self._build_lta_names_base_request(names_sublist)
                retrieved_results.extend( self._get_lta_file_results(lta_request, max_results))
        return retrieved_results


    def get_lta_files(self, type_list, sat,
                      from_date, to_date="",
                      max_results=MAX_SESSION_RESULTS):
        print("Querying LTA (", self._base_url, "), for Sat ", sat, ", from date ", from_date, ", max results: ", max_results)
        # Retrieve List of files from LTA
        lta_request = self._build_lta_base_request(type_list, sat, from_date, to_date)
        return self._get_lta_file_results(lta_request, max_results)

def prip_list_from_names(auth_mgr,  auxip_user, auxip_password,
                         lta_base_url,aux_names, mode="prod"):
    file_list = []
    print("[BEGIN] Get List of products from auxiliary names")
    adgs_retriever = ADGS_Retrieval(lta_base_url, auth_mgr)
    lta_files = adgs_retriever.get_lta_files_from_names(aux_names)

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
    print("[END] Get List of products from auxiliary names")
    return  auxip_missing_files

# TODO: Define a class for AUXIP Client, to issue requests to AUXIP REST
def compute_retrieval_interval(from_date, to_date, 
                               auxip_user, auxip_password,
                               type_list,
                               sat, mode):
    latest_pub_date = from_date
    if latest_pub_date is None:
        # TODO: get TOken and use for are_file_available
        latest_pub_date = get_latest_pub_date(auxip_user, auxip_password,
                                              type_list,
                                              sat, mode)
        to_date = None
        if latest_pub_date is None:
            print("No file available in auxip for types : ", type_list)
            return from_date, to_date
        print("Publication date to query on LTA retrieved from AUXIP: ", latest_pub_date)
    return latest_pub_date, to_date

# latest_pub_date is set to from_date, specified by caller
# if not specified, it is taken from auxip latest publication date
#  for all the specified types
# Expected date in format: YYYY-mm-DDTHH:MM:SS.mmmmmmZ
def prip_list(token_auth_handler, auxip_user, auxip_password,
              lta_base_url, type_list,
              sat, mode="prod", from_date=None, to_date=None):
    file_list = []
    if len(type_list) == 0:
        return file_list
    print("[BEGIN] Querying ADGS/LTA for types ", type_list, ", Sat: ", sat,
          ", From date: ", from_date, ", to ", to_date)
    # TODO: only if auxip publication date to be used as a reference
    # otherwise, save somewhere (auxip?) latest ADGS retrieval
    retrieve_from, retrieve_to = compute_retrieval_interval(from_date, to_date,
                               auxip_user, auxip_password,
                               type_list,
                               sat, mode)
    #latest_pub_date = from_date
    #     auth_obj = HTTPAuthentication(user, password)
    # TODO: pass Basic Auth Handler!
    adgs_retriever = ADGS_Retrieval(lta_base_url, token_auth_handler)
    lta_files = adgs_retriever.get_lta_files(type_list,
                                             sat, retrieve_from, retrieve_to)
    # lta_files is a list of pairs: first item is ID, secondi item is filename
    filename_list = [f_rec[1] for f_rec in lta_files]
    # Get list of files that are present in AUZIP
    availables = are_file_availables(auxip_user, auxip_password, filename_list,
                                     step=10, mode=mode)
    #print("Files already present in AUXIP: ", availables)
    auxip_missing_files = [f for f in lta_files if f[1] not in availables]
    print("[END] Queried ADGS/LTA for types ", type_list, ", Sat: ", sat)
    return auxip_missing_files

# latest_pub_date is set to from_date, specified by caller
# if not specified, it is taken from auxip latest publication date
#  for all the specified types
# Expected date in format: YYYY-mm-DDTHH:MM:SS.mmmmmmZ
def adgs_list(token_auth_handler, auxip_user, auxip_password,
              lta_base_url, type_list,
              sat, mode="prod", from_date=None, to_date=None):
    file_list = []
    if len(type_list) == 0:
        return file_list
    print("[BEGIN] Querying ADGS/LTA for types ", type_list, ", Sat: ", sat,
          ", From date: ", from_date, ", to ", to_date)
    # TODO: only if auxip publication date to be used as a reference
    # otherwise, save somewhere (auxip?) latest ADGS retrieval
    retrieve_from, retrieve_to = compute_retrieval_interval(from_date, to_date,
                               auxip_user, auxip_password,
                               type_list,
                               sat, mode)
    # if auth_secret is None:
    #     auth_obj = HTTPAuthentication(user, password)
    adgs_retriever = ADGS_Retrieval(lta_base_url, token_auth_handler)
    lta_files = adgs_retriever.get_lta_files(type_list,
                                             sat, retrieve_from, retrieve_to)
    # lta_files is a list of pairs: first item is ID, secondi item is filename
    filename_list = [f_rec[1] for f_rec in lta_files]
    # Get list of files that are present in AUZIP
    availables = are_file_availables(auxip_user, auxip_password, filename_list,
                                     step=10, mode=mode)
    #print("Files already present in AUXIP: ", availables)
    # add in Third position, a FLag if file is available in LTA_FILES
    adgs_files_w_availability = [f[:2]+(f[1] in availables,)+f[2:] for f in lta_files]
    print("[END] Queried ADGS/LTA for types ", type_list, ", Sat: ", sat)
    return adgs_files_w_availability

# TOOD: Extend to use a generich authorization handler, 
# that could either use basic authentication or OAUTH2 token auth
def prip_download(id, name, token_auth_handler,
                  base_url, output_folder, req_timeout=30):
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
                req_headers = dict(headers)
                req_headers.update(token_auth_handler.get_auth_header())
                product_response = requests.get(base_url+"/Products(%s)/$value" % id,
                                                #auth=HTTPBasicAuth(user, password),
                                                headers=req_headers,
                                                timeout=req_timeout,
                                                stream=True, verify=False)
                if product_response.status_code == 404:
                    raise Exception("Not found on the server : "+base_url+"/Products(%s)/$value" % id)
                total_length = int(product_response.headers.get('content-length'))
                if not total_length: # no content length header
                     fid.write(product_response.content)
                else:
                    with open(file_path,"wb") as fid:
                        print("Starting download of ", name)
                        start = time.perf_counter()
                        downloaded_bytes = 0
                        for data in product_response.iter_content(chunk_size=4096):
                            downloaded_bytes += len(data)
                            fid.write(data)
                            sys.stdout.write("\r...Downloaded %s/%s bytes" %( downloaded_bytes,total_length))
                            sys.stdout.flush()
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
        print("\n[END] Downloaded %s " % (name))
    except Exception as e:
        print(e)
        raise e
