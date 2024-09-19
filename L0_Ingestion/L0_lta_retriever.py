
import requests

import datetime as dt
import time
from requests.auth import HTTPBasicAuth
from time_formats import odata_datetime_format


lta_baseurl = "aip.acri-st.fr"

# l0_product_type
# S1_L0_types = ["RAW__0S"]
# S3_L0_Types = ["MW_0_MWR___", "OL_0_EFR___", "SL_0_SLT___", "SR_0_SRA___"]
class LtaL0Retriever:
    nbRequestsMaxTries = 5
    headers = {'Content-type': 'application/json'}
    NO_EXP_CORE_URL = "{baseurl}/Products?$filter=ContentDate/Start gt %s and ContentDate/Start lt %s and startswith(Name, '%s') and contains(Name,'%s')&$top=200"
    _core_urls = {
      'S1': NO_EXP_CORE_URL,
      'S2': NO_EXP_CORE_URL + '&$expand=Attributes',
      'S3': NO_EXP_CORE_URL
    }
    def __init__(self, mission, lta_url, lta_user, lta_passw, num_days, debug_print=False):
        self._authentication = HTTPBasicAuth(lta_user, lta_passw)
        self._num_days = int(num_days)
        self._now_time = dt.datetime.utcnow()
        self.coreURL = self._core_urls.get(mission).format(baseurl= lta_url)
        self._debug_print = debug_print


    # TODO: do we get from a time, or from the start of a day?
    def _get_names(self, unit, l0_type, from_date, to_date, req_timeout=30):
        # Build request replacing from_date, from_time and to_date
        next_trial_time = 60 # seconds
        results = []
        resp = None
        requestTriesLeft = self.nbRequestsMaxTries

        #Construction de la requête
        request = (self.coreURL + "&$count=true") % (from_date, to_date, unit, l0_type)
        print(request)

        while ((resp is None) or (resp.status_code != 200)) and (requestTriesLeft > 0):
            ntrials = self.nbRequestsMaxTries - requestTriesLeft
            if ntrials > 0:
                # Make another try, until max_retry reached
                print("Resp ", "None" if resp is None else resp.status_code,
                      ": Waiting for next retry ", ntrials * next_trial_time, " secs")
                time.sleep(ntrials * next_trial_time)
            requestTriesLeft -= 1
            print('Sending request try : [%s/%s]' % (self.nbRequestsMaxTries - requestTriesLeft, self.nbRequestsMaxTries))
            try:
                resp = requests.get(request, auth=self._authentication,
                                    headers=self.headers, timeout=req_timeout)
            except requests.Timeout as to_exc:
                print("Request  failed after timeout (", req_timeout,"): ", str(to_exc))
                resp = None

        if resp is None:
            raise Exception("All trials failed after timeout")
        elif resp.status_code == 200:
            count = int(resp.json()["@odata.count"])
            nb_steps = int(count/200)

            for aux in resp.json()["value"]:
                if self._debug_print:
                    print("Lta record: ", aux)
                results.append(aux)

            for step in range( nb_steps ):
                # On boucle sur toutes les pages de 200 fichiers L0

                # Mise à jour de la requete
                request = (self.coreURL + "&$skip=%d") % (from_date, to_date, unit, l0_type, (step+1)*200)
                print(request)

                resp = None
                requestTriesLeft = self.nbRequestsMaxTries

                while ((resp is None) or (resp.status_code != 200)) and (requestTriesLeft > 0):
                    requestTriesLeft -= 1
                    print('Sending request try : [%s/%s]' % (self.nbRequestsMaxTries - requestTriesLeft, self.nbRequestsMaxTries))
                    # TODO: Apply Timout handling also HERE:
                    # Move to function Request execution and handling of response
                    resp = requests.get(request, auth=self._authentication,headers=self.headers)

                if resp.status_code == 200:
                    for aux in resp.json()["value"]:
                        if self._debug_print:
                            print("Lta record: ", aux)
                        results.append(aux)
                else:
                    raise Exception("Bad return code ", resp.status_code, " for request: "+request)
        else:
            raise Exception("Bad return code ", resp.status_code, " for request: "+request)
        return results

    def get_lta_l0_products(self, unit_name, l0_type, from_date):
        print("Retrieving L0 products for unit ", unit_name, ", l0 type: ", l0_type, " from date ", from_date)
        # adjust the dates, by getting the minimum between today and the date + N days (end of day)
        to_date = from_date + dt.timedelta(days=self._num_days)
        end_time = min (to_date, self._now_time)
        # Set time for end_time to 23:59:59
        # TBD: do we pass date objects, or strings? Better to leave to query function the format of the date string
        end_time_str =  dt.datetime.strftime(end_time, odata_datetime_format)
        from_date_str =  dt.datetime.strftime(from_date, odata_datetime_format)
        lta_results = self._get_names(unit_name, l0_type, from_date_str, end_time_str)
        return lta_results

    def get_lta_l0_names(self, unit_name, l0_type, from_date):
        lta_results = self.get_lta_l0_products(unit_name, l0_type, from_date)
        print("Found ", len(lta_results), " on LTA")
        return [rec['Name'] for rec in lta_results]

