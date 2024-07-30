#!/bin/python
# -*- coding: utf-8 -*-

import psycopg2
import argparse
import requests
import datetime as dt
import time
from time_formats import odata_datetime_format
from requests.auth import HTTPBasicAuth
from L0_Fields_parse import parse_start_stop_fields

lta_baseurl = "aip.acri-st.fr"

# l0_product_type
# S1_L0_types = ["RAW__0S"]
# S3_L0_Types = ["MW_0_MWR___", "OL_0_EFR___", "SL_0_SLT___", "SR_0_SRA___"]
class lta_l0_retriever:
    #coreURL = f"{lta_baseurl}/odata/v1/Products?$filter=ContentDate/Start gt %04d-%02d-%02dT%02d:%02d:%02d.000000Z and ContentDate/Start lt %04d-%02d-%02dT23:59:59.999999Z and contains(Name,'_RAW__0S')&$top=200"
    #coreURL = f"{lta_baseurl}/odata/v1/Products?$filter=ContentDate/Start gt %s and ContentDate/Start lt %s and startswith(Name, '%s') and contains(Name,'%s')&$top=200&$expand=Attributes"
    nbRequestsMaxTries = 5
    headers = {'Content-type': 'application/json'}
    def __init__(self, lta_url, lta_user, lta_passw, num_days):
        self._authentication = HTTPBasicAuth(lta_user, lta_passw)
        self._num_days = int(num_days)
        self._now_time = dt.datetime.utcnow()
        self.coreURL = f"{lta_url}/Products?$filter=ContentDate/Start gt %s and ContentDate/Start lt %s and startswith(Name, '%s') and contains(Name,'%s')&$top=200"


    # TODO: do we get from a time, or from the start of a day?
    def _get_names(self, unit, l0_type, from_date, to_date, req_timeout=30):
        # Build request replacing from_date, from_time and to_date
        request = ""
        next_trial_time = 60 # seconds
        names = []
        resp = None
        requestTriesLeft = self.nbRequestsMaxTries

        #Construction de la requête
        request = (self.coreURL + "&$count=true") % (from_date, to_date, unit, l0_type)
        print(request)
 
        while ((resp is None) or (resp.status_code != 200)) and (requestTriesLeft > 0):
            ntrials = self.nbRequestsMaxTries - requestTriesLeft
            if ntrials > 0: 
                # Make another try, until max_retry reached
                print("Resp ", "None" if resp is None else resp.status_code, ": Waiting for next retry ", ntrials * next_trial_time, " secs")
                time.sleep(ntrials * next_trial_time)
            requestTriesLeft -= 1
            print('Sending request try : [%s/%s]' % (self.nbRequestsMaxTries - requestTriesLeft, self.nbRequestsMaxTries))
            try:
                resp = requests.get(request, auth=self._authentication,headers=self.headers, timeout=req_timeout)
            except requests.Timeout as to_exc:
                print("Request  failed after timeout (", req_timeout,"): ", str(to_exc))
                resp = None

        if resp is None:
            raise Exception("All trials failed after timeout")
        elif resp.status_code == 200:
            count = int(resp.json()["@odata.count"])
            nb_steps = int(count/200)
                
            for aux in resp.json()["value"]:
                print("Lta record: ", aux)
                names.append(aux['Name'])

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
                        print("Lta record: ", aux)
                        names.append(aux['Name'])
                else:
                    raise Exception("Bad return code ", resp.status_code, " for request: "+request)
        else:
            raise Exception("Bad return code ", resp.status_code, " for request: "+request)
        return sorted(names)

    def get_lta_l0_names(self, unit_name, l0_type, from_date):
        # adjust the dates, by getting the minimum between today and the date + N days (end of day)
        to_date = from_date + dt.timedelta(days=self._num_days)
        end_time = min (to_date, self._now_time)
        # Set time for end_time to 23:59:59
        # TBD: do we pass date objects, or strings? Better to leave to query function the format of the date string
        end_time_str =  dt.datetime.strftime(end_time, odata_datetime_format)
        from_date_str =  dt.datetime.strftime(from_date, odata_datetime_format)
        return self._get_names(unit_name, l0_type, from_date_str, end_time_str)

class L0_name_parser:
    def __init__(self, start_pos, field_len, unit_len):
        print("Name parser: start: ", start_pos, ", field len: ", field_len, ", Unit field len: ", unit_len)
        self._start_pos = start_pos
        self._field_len = field_len
        self.unit_len = unit_len

    def get_start_stop(self, l0_name):
        print(l0_name)
        start = l0_name[self._start_pos:self._start_pos+self._field_len]
        start_pos = self._start_pos + self._field_len + 1
        stop = l0_name[self._start_pos:self._start_pos+self._field_len]
        return start, stop

class L0_name_parser_factory:
    mission_validity_parameters = {
        'S1': { 'start': 17, 'len': 15, 'unit_len': 3},
        # 'S2': { 'start': 27, 'len': 15, 'unit_len': 3},
        'S3': { 'start': 16, 'len': 15, 'unit_len': 6},
    }

    @classmethod
    def get_l0_name_parser(cls, mission):
        if mission not in cls.mission_validity_parameters:
            raise Exception(f"Mission {mission} not valid")
        mission_parms = cls.mission_validity_parameters.get(mission)
        start = mission_parms.get('start')
        num_chars = mission_parms.get('len')
        unit_len = mission_parms.get('unit_len')
        return L0_name_parser(start, num_chars, unit_len)

class L0_names_loader:
    _insert_sql = """INSERT INTO l0_products(name, validitystart, validitystop) VALUES(%s, %s, %s);"""
    #   We retrieve all the satellite/satellte_sensor for a mission
    _query_sql = """SELECT SUBSTRING(name, 0, %d) unit, MAX(validitystart) FROM l0_products where SUBSTRING(name, 0, 3) = '%s' group by unit;"""
    def __init__(self, mission, host, port, database, user, password):
        print("Initializing L0 Loader for mission", mission)
        self._l0_name_parser = L0_name_parser_factory.get_l0_name_parser(mission)
        self._db_conn = psycopg2.connect(host=host,port=port,database=database,user=user,password=password)
        self._mission = mission

    def get_l0_latest_validity(self):
        type_last_val_dict = {}
        with self._db_conn as conn:
            with self._db_conn.cursor() as cursor:
                print("Executing ", self._query_sql % (self._l0_name_parser.unit_len + 1, self._mission))
                cursor.execute(self._query_sql % (self._l0_name_parser.unit_len + 1, self._mission))
                results = cursor.fetchall()
                print("Query returned: ", results)
                # each record in result contains: unit, date
                for row in results:
                    l0_name = row[0]
                    type_last_val_dict[l0_name] = row[1]
        # return a dict unit/lastest_date
        return type_last_val_dict

    def add_l0_names(self, l0_names):
        with self._db_conn as conn:
            with conn.cursor() as cursor:
                for l0_name in l0_names:
                    start, stop = self._l0_name_parser.get_start_stop(l0_name)
                    try:
                        cursor.execute(self._insert_sql, (l0_name, start, stop))
                        conn.commit()
                    except Exception as e:
                        print(e)
                        conn.rollback()

    def add_l0_name(self, l0_name):
        # S1B_IW_RAW__0SDV_20190822T145111_20190822T145143_017700_0214CF_EBA5.SAFE.zip
        start, stop = self._l0_name_parser.get_start_stop(l0_name)
        with self._db_conn as conn:
            with conn.cursor() as cursor:

                try:
                    cursor.execute(self._insert_sql, (l0_name, start, stop))
                    conn.commit()
                except Exception as e:
                    print(e)
                    conn.rollback()


        
if __name__ == "__main__": 

    parser = argparse.ArgumentParser(description="This script allows you to upload to the Task 3 a listing of L0 files for Mission",  # main description for help
            epilog='\n\n', formatter_class=argparse.RawTextHelpFormatter)  # displayed after help
    parser.add_argument("-m", "--mission",
                        help="Mission for L0 files",
                        required=True)
    parser.add_argument("-i", "--inputFile",
                        help="Input listing file",
                        required=False)
    parser.add_argument("-n", "--numDays",
                        help="Num Days for L0 files",
                        required=False)
    parser.add_argument("-dbh", "--host",
                        help="IP of the host of the DataBase",
                        required=True)
    parser.add_argument("-p", "--port",
                        help="Port on which the host of the DataBase is listening for DB requests",
                        required=True)
    parser.add_argument("-dbn", "--dbName",
                        help="Name of the DataBase",
                        required=True)
    parser.add_argument("-dbu", "--user",
                        help="User for DataBase authentication",
                        required=True)
    parser.add_argument("-dbp", "--password",
                        help="Password for DataBase authentication",
                        required=True)
    parser.add_argument("-lu", "--ltaurl",
                        help="Prip/Lta Endpoint Url",
                        required=False)
    parser.add_argument("-u", "--ltauser",
                        help="Prip user",
                        required=False)
    parser.add_argument("-pw", "--ltapassword",
                        help="Prip password ",
                        required=False)

    args = parser.parse_args()

    print("arguments: ", args)
    host=args.host
    port=args.port
    database=args.dbName
    user=args.user
    password=args.password
    mission=args.mission
    if args.inputFile is None and (args.ltaurl is  None or args.ltauser is None or args.ltapassword is None):
         parser.error("LTA arguments shall be all specified, if you are not using input File")

    _default_num_days = 15
    num_days = args.numDays if args.numDays is not None else _default_num_days
    mission_l0_types = {
        'S1': ["RAW__0S"],
        'S2': ["L0__DS_"],
        'S3':  ["MW_0_MWR___", "OL_0_EFR___", "SL_0_SLT___", "SR_0_SRA___"]
    }
    try:
        l0_loader = L0_names_loader(mission, host, port, database, user, password) 

        l0_list_file = args.inputFile

        # if input file is defined,get from input file 
        if l0_list_file is not None:
            with open(l0_list_file, "r") as fid:
                for line in fid.readlines():
                    l0_name = line.rstrip('\n')
                    l0_loader.add_l0_name(l0_name)

        else:
            # Get Max validity for all types related to mission
            for l0_type in mission_l0_types[mission]:
                last_l0_type_table = l0_loader.get_l0_latest_validity() 
                print("Last L0 validity for each Type for mission ", mission, ": ", last_l0_type_table)
                lta_retriever = lta_l0_retriever(args.ltaurl, args.ltauser, args.ltapassword, num_days)
                # for each satellite, or satellite_sensoor:
                for unit, val_time in last_l0_type_table.items():
                    # Get from LTA a list of L0 names, for N days (or up to today),
                    unit_l0_names = lta_retriever.get_lta_l0_names(unit, l0_type, val_time)
                    print("Retrieved L0 names for unit: ", unit, ": ", unit_l0_names)
                    # With N from command line, with default if not specified (or default got from config file)
                    # Add the l0 names to db
                    l0_loader.add_l0_names(unit_l0_names)


    except Exception as e:
        print(e)
        # if conn:
        #     conn.rollback()


