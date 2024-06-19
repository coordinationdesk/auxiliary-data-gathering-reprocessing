import time
import sys
import traceback
import json
import requests
from .lib.auxip import _get_adg_domain, get_token_info
from .lib.auxip import get_auxip_base_endpoint, are_file_availables, is_file_available
from .lib.auxip_rm import remove_from_auxip
from .lib.auxip import post_to_auxip

# TODO: Integrate with oauth2 password mode
# def are_file_availables(auxip_user,auxip_password,aux_data_files_names,step,mode='dev'):
# is file id available (auxip_user, auxip_password, aux_filename, aux_id, mode=dev)
class AuxipClient:
   auxip_get_step = 20
   TOKEN_DURATION = 350
   def __init__(self, user, password, mode):
       self._user = user
       self._password = password
       #self._base_url = _get_adg_domain(mode)
       self._mode = mode
       self._auxip_endpoint = get_auxip_base_endpoint(mode)
       self._access_token = None

   def _get_token(self):
       tk = get_token_info(self._user, self._password, self._mode)
       return tk['access_token']

   # TODO: Move time handling to get_token;
   # Just call get_token and fill the header here
   def _get_access_header(self):
       if self._access_token is None:
           self.timer_start = time.time()
           # TODO Manage first request, and expiration time
           self._access_token = self._get_token()
       else:
           timer_stop = time.time()
           elapsed_seconds = timer_stop - self.timer_start
           if elapsed_seconds > self.TOKEN_DURATION:
                print("Elapsed ", elapsed_seconds," seconds")
                print("Reacquiring token")
                self.timer_start = time.time()
                self._access_token = self._get_token()

       return {'Authorization': 'Bearer %s' % self._access_token}
   
   def get_file_ids_availability(self, aux_file, id_list):
       '''
         aux_file: filename of the product
         id_list: list of UUID for the product (key on auxip)
         returns: two lists of IDs: the first one: ids of products available on AUXIP,
                 the second one: ids of products not available on auxip
       '''
       print("Checking availability of filename ", aux_file)
       file_availability = self.available_files_status([aux_file], self.auxip_get_step)
       print("Availability returned: ", file_availability)
       # return: list of tuples: filename, file_cksum, cksum_alg, cksum_date, file_size, file_id))

       available_ids = [aux_rec[5] for aux_rec in file_availability]
       print("Matching available IDs vs list of IDs on Storage, to extract not catalogued IDs: ", id_list)
       unavailable_ids = [id for id in id_list if id not in available_ids]
       print("Extracted not catalogued ids: ", unavailable_ids)
       # match against id_list and convert to: 
       # two list of ids: the first one for available products, the second one for not available products
       return available_ids, unavailable_ids
       

   def remove_auxip_file(self, filename, aux_id):
       tk = self._get_token()
       return remove_from_auxip(tk, filename, aux_id, self._mode)
   
   def _build_products_name_filter_request(self, aux_file_names, from_indx, step):
       auxip_request = "{}/Products?$filter=contains(Name,'{}')".format(self._auxip_endpoint, 
                                                                     aux_file_names[from_indx])
       for t in range(min(len(aux_file_names),from_indx+1), 
                      min(len(aux_file_names),from_indx+step),
                      1):
           auxip_request = auxip_request + " or contains(Name,'"+aux_file_names[t]+"')"
       return auxip_request

   # TODO: Define a Unit Test, and a Functional test against a AUXIP test service
   # step: number of files to be checked in same request
   def _are_file_availables(self, aux_data_files_names,step):
       availables = []
       # TODO: Use TOkenAhuth Handler class, and just request AuthHeader for each request
       print("Checking availability on AUXIP of ", len(aux_data_files_names), " files")
       try:


           for f in range(0, len(aux_data_files_names), step):
               access_header = self._get_access_header() 
               sys.stdout.write("\rRequest for index from %s to %s" % (f, f+step-1))
               sys.stdout.flush()
               headers = {'Content-Type': 'application/json'} 
               headers.update(access_header)
               auxip_request = self._build_products_name_filter_request(aux_data_files_names, f, step)
               # print("Chcking if files are present in AUXIP: ", aux_data_files_names)
               response = requests.get(auxip_request, headers=headers)
               if response.status_code != 200:
                   print(response.status_code)
                   print(response.text)
                   raise Exception("Error while accessing auxip")
               json_resp = response.json()
               # print(json_resp)
              # Return Name, checksum
               print("Received %d results" % len(json_resp["value"]))
               for g in json_resp["value"]:
                   file_id = g["Id"]
                   file_size = g["ContentLength"]
                   if "Checksum" in g and len(g["Checksum"]):
                       cksum_info = g["Checksum"][0]
                       file_cksum = cksum_info["Value"]
                       cksum_alg = cksum_info["Algorithm"]
                       cksum_date = cksum_info["ChecksumDate"]
                   else:
                       file_cksum = ''
                       cksum_alg = ''
                       cksum_date = ''
                   availables.append((g["Name"], file_cksum, cksum_alg, cksum_date, file_size, file_id))
       except Exception as e:
           print("==> get ends with error ")
           print(e)
           traceback.print_exc()
           raise e
       print("Found ", len(availables), " files in Auxip from requested files")
       return availables

   def are_file_availables(self, aux_data_files_names,step):
      auxip_availables = self._are_file_availables( aux_data_files_names, step)
      return [file[0] for file in auxip_availables]
       
   def available_files_status(self, aux_data_files_names, step):
      # Return a list of available files, among those passed in aux_data_files_names
      # for each of them report also the checksum info
      return self._are_file_availables( aux_data_files_names, step)

   def _is_file_available(self, aux_file):
       access_tk = self._get_token()
       return is_file_available(access_tk, aux_file, mode=self._mode)

   def catalogue_product(self, aux_data_file_path, aux_id):
       
       access_tk = self._get_token()
       result = post_to_auxip(access_tk, aux_data_file_path, aux_id, mode=self._mode)
       return result

   def catalogue_products(self, in_folder, aux_file_name_uuid_pairs):
       '''
          aux-file_name_uuid_pairs: list of tuples: each tuple contains
            (aux file name, uuid)
       '''
       for aux_file, aux_id in aux_file_name_uuid_pairs:
           if not self._is_file_available(aux_file):
               aux_file_path = os.path.join(in_folder, aux_file)
               self.catalogue_product(aux_file_path, aux_id)

