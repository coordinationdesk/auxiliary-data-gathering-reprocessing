import requests
from requests.auth import HTTPBasicAuth
import time,sys,os
from ingestion.lib.auxip import get_latest_of_type,are_file_availables,get_token_info

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

def _add_odata_top(odata_request, top_num_result):
    return odata_request + "&$top="+str(top_num_result)

def _add_odata_skip(odata_request, skip_results):
    return odata_request + "&$skip="+str(skip_results)

def get_lta_files(user, password, lta_base_url,
                  type_list, sat,
                  from_date, to_date="",
                  max_results=100000):
    print("Querying LTA (", lta_base_url, "), for Sat ", sat, ", from date ", from_date)
    # Retrieve List of files from LTA
    file_list = []
    headers = {'Content-type': 'application/json'}
    lta_request = lta_base_url + "Products?$orderby=PublicationDate asc" + \
                "&$filter=PublicationDate gt " + from_date
    if to_date and len(to_date):
        lta_request = lta_request + " and PublicationDate lt " + to_date
    lta_request = lta_request + " and "
    if len(type_list) > 1:
        lta_request += "("
    lta_request += f"contains(Name,'{type_list[0]}')"
    for prod_type in type_list[1:]:
        lta_request += f" or contains(Name,'{prod_type}')"
    if len(type_list) > 1:
        lta_request += ")"
    lta_request += " and startswith(Name,'"+sat+"')"
    step=min(200, max_results)
    for i in range(0, max_results, step):
        start = i
        stop = i + step
        request_top = _add_odata_top(lta_request, step)
        request_top = _add_odata_skip(request_top, start)
        print("LTA Request : ", request_top)
        response = requests.get(request_top, auth=HTTPBasicAuth(user, password),
                                headers=headers,
                                verify=False)
        if response is not None:
            if response.status_code == 200:
                resp_json = response.json()
                print("Number of element found with curr request: ", len(resp_json["value"]))
                if len(resp_json["value"]) == 0:
                    break
                #print(resp_json["value"][0])
                for aux_file in resp_json["value"]:
                    ID = aux_file["Id"]
                    file_size = aux_file["ContentLength"]
                    file_list.append((ID, aux_file["Name"], file_size))
            else:
                raise Exception("Error on request code : "+str(response.status_code))
    return file_list

# TODO: Update to use latest_pub_date specified by caller
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


def prip_download(id, name,user, password,base_url,output_folder):
    try:
        headers = {'Content-type': 'application/json'}
        # get ID and size of the product
        id_folder = output_folder
        os.makedirs(id_folder,exist_ok=True)
        file_path = os.path.join(id_folder, name)
        if os.path.exists(file_path) and os.path.getsize(file_path) != 0:
            print("\nFile already exists and is not empty %s " % (name))
            return
        print("\nDownloading %s " % (name))
        with open(file_path,"wb") as fid:
            start = time.perf_counter()
            product_response = requests.get(base_url+"Products(%s)/$value" % id,
                                            auth=HTTPBasicAuth(user, password),
                                            headers=headers,
                                            stream=True, verify=False)
            if product_response.status_code == 404:
                raise Exception("Not found on the server : "+base_url+"/Products(%s)/$value" % id)
            total_length = int(product_response.headers.get('content-length'))
            if not total_length: # no content length header
                 fid.write(product_response.content)
            else:
                print("Starting download")
                downloaded_bytes = 0
                for data in product_response.iter_content(chunk_size=4096):
                    downloaded_bytes += len(data)
                    fid.write(data)
                    done = int(50 * downloaded_bytes / total_length)
                    #sys.stdout.write("\r[%s%s] %s bps" % ('=' * done, ' ' * (50-done), downloaded_bytes//(time.perf_counter() - start)))
                    #sys.stdout.flush()
                    # fid.write(product_response.content)
                print("Download Done")
            # No need to close if using "with"
            fid.close()
    except Exception as e:
        print(e)
        raise e
