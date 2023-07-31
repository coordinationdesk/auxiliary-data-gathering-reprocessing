import requests
from requests.auth import HTTPBasicAuth
import time,sys,os
from ingestion.lib.auxip import get_latest_of_type,are_file_availables,get_token_info


verify_cert=True
def prip_list(user, password, auxip_user, auxip_password, base_url, type_list, sat, mode="prod"):
    file_list = []
    file_name_list = []
    token_info = get_token_info(auxip_user, auxip_password, mode=mode)
    #print(token_info['access_token'])
    headers = {'Content-type': 'application/json'}
    if len(type_list) == 0:
        return file_list
    latest_pub_date = get_latest_of_type(access_token=token_info['access_token'],aux_type_list=type_list,sat=sat,mode=mode)
    if latest_pub_date is None:
        print("No file available in auxip for types : ")
        print(type_list)
        return file_list
    request = base_url + "Products?$orderby=PublicationDate asc&$filter=PublicationDate gt " + latest_pub_date + " and (contains(Name,'" + \
              type_list[0] + "')"
    for idx in range(1,len(type_list)):
        request = request + " or contains(Name,'"+type_list[idx]+"')"
    request = request + ") and startswith(Name,'"+sat+"')"
    step=200
    for i in range(0,100000,step):
        start = i
        stop = i + step
        request_top= request+"&$top="+str(step)+"&$skip="+str(start)
        print("Request : "+request_top)
        response = requests.get(request_top, auth=HTTPBasicAuth(user, password),headers=headers,verify=verify_cert)
        if response is not None:
            if response.status_code == 200:
                resp_json = response.json()
                print("Number of element found : "+str(len(resp_json["value"])))
                if len(resp_json["value"]) == 0:
                    break
                print(resp_json["value"][0])
                for f in resp_json["value"]:
                    ID = f["Id"]
                    file_list.append((ID,f["Name"]))
                    file_name_list.append(f["Name"])
            else:
                raise Exception("Error on request code : "+str(response.status_code))
    availables = are_file_availables(auxip_user,auxip_password,file_name_list,step=10,mode=mode)
    real_file_list = []
    for f in file_list:
        if f[1] not in availables:
            real_file_list.append(f)
    return real_file_list


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
            product_response = requests.get(base_url+"Products(%s)/$value" % id ,auth=HTTPBasicAuth(user, password),
                                            headers=headers,stream=True,verify=verify_cert)
            if product_response.status_code == 404:
                raise Exception("Not found on the server : "+base_url+"/Products(%s)/$value" % id)
            total_length = int(product_response.headers.get('content-length'))
            if total_length is None or total_length == 0: # no content length header
                 fid.write(product_response.content)
            else:
                dl = 0
                print("Starting download")
                for data in product_response.iter_content(chunk_size=4096):
                    dl += len(data)
                    fid.write(data)
                    done = int(50 * dl / total_length)
                    #sys.stdout.write("\r[%s%s] %s bps" % ('=' * done, ' ' * (50-done), dl//(time.perf_counter() - start)))
                    #sys.stdout.flush()
                    # fid.write(product_response.content)
                print("Download Done")
            fid.close()
    except Exception as e:
        print(e)
        raise e
