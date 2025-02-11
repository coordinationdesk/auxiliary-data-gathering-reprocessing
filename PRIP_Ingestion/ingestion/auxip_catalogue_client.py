import time
import json
import requests
from odata_request import build_paginated_request
from odata_request_builder import ODataRequestBuilder
from auxip_client import AuxipClient
from lib.auxip_rm import remove_from_auxip

# MAXIMUM RESULTS to retrieve
# in a single session
# defined to limit the number of files downloaded
# within a single session
MAX_SESSION_RESULTS = 350

# TODO: Define class to hold AUXIP, LTA credentials, lta_base_url
#  type_list, satellite, mode
#



class AuxipCatalogueClient(AuxipClient):

    def __init__(self, user, password, mode):
        AuxipClient.__init__(self, user, password, mode)

    def _transform_file_results(self, aux_file_records):
        # Transform Auxip Query result to list of
        # records of form:
        # ID, AuxFileName, CksumValue, CksumAlg, CksumDate, FileSize
        file_list = []
        for aux_file in aux_file_records:
            print(aux_file)
            ID = aux_file["Id"]
            file_size = aux_file["ContentLength"]
            cksum_info = aux_file["Checksum"][0]
            file_cksum = cksum_info["Value"]
            cksum_alg = cksum_info["Algorithm"]
            cksum_date = cksum_info["ChecksumDate"]
            file_list.append((ID, aux_file["Name"], file_cksum, cksum_alg, cksum_date, file_size))
        return file_list

    def _get_aux_file_results(self, get_request, max_results, req_timeout=30):
        next_trial_time = 60 # seconds
        file_responses = []
        headers = {'Content-Type': 'application/json'}
        step=min(200, max_results)
        max_retry = 3
        for i in range(0, max_results, step):
            request_top = build_paginated_request(get_request, i, step)
            print("[BEGIN] AUXIP Request : ", request_top)
            ntrials = 0
            while ntrials < max_retry:
                if ntrials > 0:
                    time.sleep(ntrials * next_trial_time)
                try:
                    req_headers = dict(headers)
                    access_header = self._get_access_header()
                    req_headers.update(access_header)
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
                    print("[END] Failed AUXIP Request ", request_top, " after ", ntrials, " retries")
            if response is not None:
                if response.status_code == 200:
                    resp_json = response.json()
                    print("Number of element found with curr request: ", len(resp_json["value"]))
                     # if len(resp_json["value"]) == 0:
                     #   break
                    #print(resp_json["value"][0])
                    file_responses.extend(resp_json["value"])
                    if len(resp_json["value"]) < step:
                        break
                else:
                    raise Exception(f"Error on request - code : {response.status_code}, text: {response.text}")
        return file_responses

    def insert_into_auxip(self, product_record):
        headers = {'Content-Type': 'application/json'}
        access_header = self._get_access_header()
        headers.update(access_header)
        products_endpoint = f"{self._auxip_endpoint}/Products"

        print("Sending post request to AUXIP")
        response = requests.post(products_endpoint,data=json.dumps(product_record),
                                headers=headers)

        # print( "Sending product to auxip.svc", product)
        if response.status_code == 201 :
            print("%s ==> sent to auxip.svc successfully " % product_record['Name'] )
            return 0
        print( response.json() )
        print("%s ==> post ends with error %d" % (product_record['Name'], response.status_code))
        return 1

    def get_auxip_files(self, type_list, sat,
                        from_date, to_date="",
                        max_results=MAX_SESSION_RESULTS):
        req_builder = ODataRequestBuilder(self._auxip_endpoint)
        print("Querying OData Service (", self._auxip_endpoint,
              "), for Sat ", sat, ", from date ", from_date, 
              ", max results: ", max_results)
        # Retrieve List of files from LTA
        get_request = req_builder.build_get_base_request(type_list, sat, from_date, to_date, True)
        get_results = self._get_aux_file_results(get_request, max_results)
        return self._transform_file_results(get_results)

    def get_aux_file_records(self, mission, auxtype, from_date, to_date,
                             max_results=MAX_SESSION_RESULTS):
        req_builder = ODataRequestBuilder(self._auxip_endpoint)
        auxip_request = req_builder.build_get_base_request([auxtype], mission, from_date, to_date, True)
        # print("Chcking if files are present in AUXIP: ", aux_data_files_names)
        get_results = self._get_aux_file_results(auxip_request, max_results)
        print("Received %d results" % len(get_results))
        return get_results

    def get_aux_records_from_names(self,
                                 names_list,
                                 batch_size=20,
                                 max_results=MAX_SESSION_RESULTS):
        """
             Retrieves Aux Files records for the product names in the
             input names_list
             Perform the requests with batches of length 20
        """
        req_builder = ODataRequestBuilder(self._auxip_endpoint)
        print("Querying Service (", self._auxip_endpoint, "), for Names ")
        retrieved_results = []
        # NUmber of names to be included in each single request
        req_num_names = batch_size
        # Retrieve List of files from LTA
        # get results on small subsets of names list
        for i in range(0, len(names_list), req_num_names):
            names_sublist = names_list[i: min(i + req_num_names, len(names_list))]
            print("\nRequesting names: ", names_sublist)
            if names_sublist[0]:
                get_request = req_builder.build_get_names_base_request(names_sublist, True)
                retrieved_results.extend( self._get_aux_file_results(get_request, max_results))
        return retrieved_results

   # get_aux_files(self, aux_type, from_date, to_date)
    def update_aux_file(self, aux_file_record):
        aux_id = aux_file_record['Id']
        filename = aux_file_record['Name']
        #tk = self._get_token()
        # Remove file from catalogue, by id
        # catch any error
        # result = remove_from_auxip(tk, filename, aux_id, self._mode)
        # insert file to catalogue
        # TODO: only update catalogue, wihtout archiving
        result = self.insert_into_auxip(aux_file_record)
        return result
