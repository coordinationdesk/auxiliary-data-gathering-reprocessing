

import time
import os
import sys
import requests
from L0_lta_retriever import LtaL0Retriever

from l0_attributes import get_attributes


# l0_product_type
# S1_L0_types = ["RAW__0S"]
# S3_L0_Types = ["MW_0_MWR___", "OL_0_EFR___", "SL_0_SLT___", "SR_0_SRA___"]
class L0IcidExtractor(LtaL0Retriever):
    DOWNLOAD_URL = "{baseurl}/Products(%s)/$value"
    def __init__(self, mission, lta_url, lta_user, lta_passw, num_days, debug_print=False):
        LtaL0Retriever.__init__(self, mission, lta_url,
                                  lta_user, lta_passw, num_days, debug_print)
        self.core_download_URL = self.DOWNLOAD_URL.format(baseurl= lta_url)

    def get_l0_names_ids(self, unit_list, from_date, l0_type):
        name_id_list = []
        l0_products = {}
        #
        # Get from LTA a list of L0 names, for N days (or up to today),
        for unit in unit_list:
            # Get only 1st item in day
            l0_products[unit] = self.get_lta_l0_products(unit, l0_type, from_date, max_results=1)
            print("Retrieved L0 names for unit: ", unit, ": ",
                  [prod['Name'] for prod in l0_products[unit]])
            if len(l0_products[unit]):
                first_product_name = l0_products[unit][0]['Name']
                first_product_id = l0_products[unit][0]['Id']
                first_product_date = l0_products[unit][0]['ContentDate']['Start']
                print(l0_products[unit])
                name_id_list.append((first_product_name, first_product_id, first_product_date))
        # Get pairs of name and id, so that:
        # we have a name for each unit for each day
        # names are taken from days at N days interval
        return name_id_list
    # TODO: do we get from a time, or from the start of a day?

    # Expected flow for icid extraction:
    # 1. make query on LTA for products on date/dates
    # 2. Collect name/id from results
    # 3. Select name/id to be used
    # 4. Loop on name/id (N at time) and execute:
    #    download of name/id to target folder
    # 5 request extraction of ICD for the list of names
    def download_lta_l0_product(self, product_name, product_id, target_folder, req_timeout=30):
        next_trial_time = 60 # seconds
        print("Downloading L0 product ", product_name, " with id: ", product_id)

        try:
            # Get output file path
            id_folder = target_folder
            os.makedirs(id_folder,exist_ok=True)
            file_path = os.path.join(id_folder, product_name)
            if os.path.exists(file_path) and os.path.getsize(file_path) != 0:
                print("\nFile already exists and is not empty %s " % (product_name))
                return
            print("\n[BEGIN] Downloading %s " % (product_name))
            # get ID and size of the product
            ntrials = 0
            max_retry = 3
            product_request = self.core_download_URL % product_id
            #Construction de la requête
            print(product_request)
            while ntrials < max_retry:
                time.sleep(ntrials * next_trial_time)
                try:
                    product_response = requests.get(product_request,
                                                    auth=self._authentication,
                                                    headers=self.headers, timeout=req_timeout,
                                                    stream=True, verify=False)
                    if product_response.status_code == 404:
                        raise Exception("Not found on the server : "+product_request)
                    total_length = int(product_response.headers.get('content-length'))
                    print("Size of product to download: ", total_length)
                    with open(file_path,"wb") as fid:
                        if not total_length: # no content length header
                            print("No length received: Writing the content to file")
                            fid.write(product_response.content)
                        else:
                            print("Starting download")
                            start = time.perf_counter()
                            downloaded_bytes = 0
                            max_chunk_size = 4096
                            num_batches = 0
                            progress_period = int(total_length / max_chunk_size / 10 + 1)
                            print("Period to update progress = ", progress_period)
                            for data in product_response.iter_content(chunk_size=4096):
                                downloaded_bytes += len(data)
                                fid.write(data)
                                if (num_batches % progress_period) == 0:
                                    sys.stdout.write("\r...Downloaded %s/%s bytes" \
                                                    %( downloaded_bytes,total_length))
                                    sys.stdout.flush()
                                num_batches += 1
                                # done = int(50 * downloaded_bytes / total_length)
                                # sys.stdout.write("\r[%s%s] %s bps" % ('=' * done, ' ' * (50-done), \
                                #                  downloaded_bytes//(time.perf_counter() - start)))
                                # sys.stdout.flush()
                                # fid.write(product_response.content)
                            dwl_time = time.perf_counter() - start
                            print("Download took ", dwl_time, " [s] - ", downloaded_bytes/dwl_time/1024/1024, " [Mb/s]")
                    print("[END] Download Done\n")
                    break
                except requests.Timeout as to_exc:
                    print("Request For product  ", id,
                          " info and download failed after timeout (",
                          req_timeout,"): ", str(to_exc))
                    if os.path.exists(file_path):
                        os.remove(file_path)
                    # Make another try, until max_retry reached
                    ntrials += 1
                    print("Waiting for next retry ", ntrials * next_trial_time, " secs")
                if ntrials == max_retry:
                    print("[END] Failed download of product ", product_id,
                          " after ", ntrials, " retries")
                    raise Exception('Failed download of product {} after {} retries'.format(product_id,
                                     ntrials))
        except Exception as e:
            print(e)
            raise e

    def get_l0_icid(self, l0_name, target_folder):
        # compose path
        l0_product_file = os.path.join(target_folder, l0_name)
        # Extract attribtues
        l0_attributes = get_attributes(l0_product_file)
        if l0_attributes is not None:
            # Read Icid Attribute
            icid = l0_attributes.setdefault('InstrumentConfigurationID', None)

            # Print L0 Name + Icid attribute
            print(l0_name, " ICID: ", icid if icid is not None else "N/A")
        # remove L0 Product file
        os.remove(l0_product_file)
        return icid
