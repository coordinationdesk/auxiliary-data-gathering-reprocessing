import requests
from requests.auth import HTTPBasicAuth
import time,sys,os

def prip_list(user, password, base_url, type):
    file_list = []
    headers = {'Content-type': 'application/json'}
    request = base_url+"Products?$filter=contains(Name,'"+type+"')"
    response = requests.get(request, auth=HTTPBasicAuth(user, password),headers=headers,verify=False)
    if response is not None:
        if response.status_code == 200:
            for f in response.json()["value"]:
                ID = f["Id"]
                file_list.append((ID,f["Name"]))
    return file_list


def prip_download(id, name,user, password,base_url,output_folder):
    try:
        headers = {'Content-type': 'application/json'}
        # get ID and size of the product
        print( "\nDownloading %s " % (name) )
        id_folder = output_folder
        os.makedirs(id_folder,exist_ok=True)
        file_path = os.path.join(id_folder, name)
        with open(file_path,"wb") as fid:
            start = time.perf_counter()
            product_response = requests.get(base_url+"/Products(%s)/$value" % id ,auth=HTTPBasicAuth(user, password),
                                            headers=headers,stream=True,verify=False)
            total_length = int(product_response.headers.get('content-length'))
            if total_length is None: # no content length header
                 fid.write(product_response.content)
            else:
                dl = 0
                for data in product_response.iter_content(chunk_size=4096):
                    dl += len(data)
                    fid.write(data)
                    done = int(50 * dl / total_length)
                    sys.stdout.write("\r[%s%s] %s bps" % ('=' * done, ' ' * (50-done), dl//(time.perf_counter() - start)))
                    sys.stdout.flush()
                    # fid.write(product_response.content)
            fid.close()
    except Exception as e:
        print(e)