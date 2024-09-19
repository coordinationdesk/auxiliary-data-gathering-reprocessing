#!/bin/python
# -*- coding: utf-8 -*-

import argparse
import datetime as dt
import time
import sys
import re
import psycopg2
from psycopg2 import IntegrityError
import requests
from requests.auth import HTTPBasicAuth
from time_formats import odata_datetime_format
from L0_Fields_parse import parse_start_stop_fields

from L0_lta_retriever import LtaL0Retriever

lta_baseurl = "aip.acri-st.fr"

# l0_product_type
# S1_L0_types = ["RAW__0S"]
# S3_L0_Types = ["MW_0_MWR___", "OL_0_EFR___", "SL_0_SLT___", "SR_0_SRA___"]

class L0_NameParser:
    def __init__(self, start_pos, field_len, type_start, type_len):
        print("Name parser: start: ", start_pos,
              ", field len: ", field_len,
              ", L0 Type field start: ", type_start, ", len: ", type_len)
        self._start_pos = start_pos
        self._field_len = field_len
        self.type_start = type_start
        self.type_len = type_len

    def get_start_stop(self, l0_name):
        print(l0_name)
        field_start_pos = self._start_pos
        field_end_pos = field_start_pos + self._field_len
        start_time = l0_name[field_start_pos:field_end_pos]
        # move to next field
        field_start_pos = field_end_pos + 1
        # field_start_pos += self._field_len + 1
        field_end_pos = field_start_pos + self._field_len
        stop_time = l0_name[field_start_pos:field_end_pos]
        return start_time, stop_time

class L0_name_parser_factory:
    mission_validity_parameters = {
        'S1': { 'start': 17, 'len': 15, 'type_start': 8, 'type_len': 7},
        'S2': { 'start': 27, 'len': 15, 'type_start': 10, 'type_len': 10},
        'S3': { 'start': 16, 'len': 15, 'type_start': 5, 'type_len': 11},
    }

    @classmethod
    def get_l0_name_parser(cls, mission):
        if mission not in cls.mission_validity_parameters:
            raise Exception(f"Mission {mission} not valid")
        mission_parms = cls.mission_validity_parameters.get(mission)
        start = mission_parms.get('start')
        num_chars = mission_parms.get('len')
        type_len = mission_parms.get('type_len')
        type_start = mission_parms.get('type_start')
        return L0_NameParser(start, num_chars, type_start, type_len)

class L0_validity_factory:
    @classmethod
    def get_l0_validity_extractor(cls, mission):
        if mission in ('S1', 'S3'):
            return L0_validity_name_extractor(mission)
        elif mission == 'S2':
            return L0_validity_attributes_extractor(mission)
        else:
            raise Exception("Mission not supported")

class L0_validity_extractor:
    def __init__(self, mission):
        self._mission = mission
        self._l0_name_parser = L0_name_parser_factory.get_l0_name_parser(mission)

    @property
    def type_start(self):
        return self._l0_name_parser.type_start

    @property
    def type_len(self):
        return self._l0_name_parser.type_len

    @property
    def mission(self):
        return self._mission

    def get_product_validity(self, product_record):
        raise Exception("Base Class method not callable")

class L0_validity_attributes_extractor(L0_validity_extractor):
    def __init__(self, mission):
        L0_validity_extractor.__init__(self, mission)

    def _getValidityFromAttributes(self, attributes):

        validityDate = ''

        for attributeDict in attributes:
            if attributeDict['Name'] == 'productGroupId':
                validityDate = attributeDict['Value'].split('_')[1]
                break

        return validityDate

    # second type: read from record the L0 proudct name,
    #      and attributes; retrieve from attributes the validity
    def get_product_validity(self, product_record):
        l0_name = product_record['Name']
        start = stop = self._getValidityFromAttributes(product_record['Attributes'])
        return l0_name, start, stop

class L0_validity_name_extractor(L0_validity_extractor):
    def __init__(self, mission):
        L0_validity_extractor.__init__(self, mission)

    # first type: read from record the L0 product name, extract validity from name
    def get_product_validity(self, product_record):
        l0_name = product_record['Name']
        prod_start, prod_stop = self._l0_name_parser.get_start_stop(l0_name)
        return l0_name, prod_start, prod_stop

class L0_NamesLoader:
    SAT_LEN = 3
    _insert_sql = """INSERT INTO l0_products(name, validitystart, validitystop) VALUES(%s, %s, %s);"""
    #   We retrieve all the satellite/satellte_sensor for a mission
    # Unit is satellite + any possible sensor/subsystem
    _query_sql = """SELECT SUBSTRING(name, 0, %d) unit, SUBSTRING(name, %d, %d) l0type, MAX(validitystart) FROM l0_products where SUBSTRING(name, 0, 3) = '%s' group by l0type, unit;"""
    def __init__(self, mission, dbconn):
        print("Initializing L0 Loader for mission", mission)
        self._db_conn = dbconn
        self._l0_validity_extractor = L0_validity_factory.get_l0_validity_extractor(mission)
        self._mission = mission

    def get_l0_latest_validity(self):
        type_last_val_dict = {}
        with self._db_conn as conn:
            with conn.cursor() as cursor:
                print("Executing ", self._query_sql % (self.SAT_LEN + 1, self._l0_validity_extractor.type_start, self._l0_validity_extractor.type_len, self._mission))
                cursor.execute(self._query_sql % (self.SAT_LEN + 1, self._l0_validity_extractor.type_start, self._l0_validity_extractor.type_len, self._mission))
                results = cursor.fetchall()
                print("Query returned: ", results)
                # each record in result contains: unit, date
                for row in results:
                    l0type = row[1]
                    unit = row[0]
                    type_last_val_dict.setdefault(l0type, {}).update({unit: row[2]})
        # return a dict unit/lastest_date
        return type_last_val_dict

    def _get_lta_l0_validities(self, l0_products):
        # Appliy validity extractor to LTA query results
        return sorted((self._l0_validity_extractor.get_product_validity(l0_product)
                for l0_product in l0_products))

    def add_l0_name_validities(self, l0_validities):
        with self._db_conn as conn:
            for l0_record in l0_validities:
                l0_name, start, stop = l0_record
                with conn.cursor() as cursor:
                    try:
                        print("Executing ", self._insert_sql % (l0_name, start, stop))
                        cursor.execute(self._insert_sql, (l0_name, start, stop))
                        conn.commit()
                    except IntegrityError as ie:
                        print("Record already existing, not inserted")
                        print(ie)
                        conn.rollback()
                    except Exception as e:
                        print(e)
                        conn.rollback()

    def add_l0_name(self, l0_name, start, stop):
        with self._db_conn as conn:
            with conn.cursor() as cursor:

                try:
                    cursor.execute(self._insert_sql, (l0_name, start, stop))
                    conn.commit()
                except Exception as e:
                    print(e)
                    conn.rollback()
    def add_l0_products(self, l0_products):
        l0_validities = self._get_lta_l0_validities(l0_products)
        self.add_l0_name_validities(l0_validities)


def get_command_arguments():
    print("Called with command line: ", sys.argv)
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
    parser.add_argument("-fd", "--fromdate",
                        help="Ingest products from date ",
                        required=False)
    arg_values = parser.parse_args()
    print("Command line arguments: ", arg_values)
    if arg_values.inputFile is None and (arg_values.ltaurl is  None or arg_values.ltauser is None or arg_values.ltapassword is None):
        parser.error("LTA arguments shall be all specified, if you are not using input File")
    #date_pattern = re.compile("([0-9]{8}T[0-9]{6})")
    #date_pattern = re.compile("([0-9]{8}})")
    date_pattern = re.compile("([0-9]{4}})-([0-1][0-2])-([0-3][0-9])")
    print(arg_values.fromdate)
    if arg_values.fromdate is not None:
        from_date_str = arg_values.fromdate +  '000000'
        # TODO put under try/except to print error if format wrong
        from_datetime = dt.datetime.strptime(from_date_str, '%Y-%m-%d%H%M%S')
        arg_values.from_datetime = from_datetime
    # if arg_values.fromdate is not None and not date_pattern.match(arg_values.fromdate):
    #     print(date_pattern.match(arg_values.fromdate))
    #     parser.error("From Date format:  YYYYMMDD")
    # check that date is in correct format
    return arg_values


if __name__ == "__main__":

    args = get_command_arguments()
    host=args.host
    port=args.port
    database=args.dbName
    user=args.user
    password=args.password
    mission=args.mission

    _default_num_days = 15
    num_days = args.numDays if args.numDays is not None else _default_num_days
    mission_l0_types = {
        'S1': ["RAW__0S"],
        'S2': ["MSI_L0__DS"],
        'S3': ["MW_0_MWR___", "OL_0_EFR___", "SL_0_SLT___", "SR_0_SRA___"]
    }
    mission_units = {
        'S1': ["S1A", "S1B"],
        'S2': ["S2A", "S2B"],
        'S3':  ["S3A", "S3B"]
    }
    try:
        rdb_conn = psycopg2.connect(host=host, port=port, database=database,
                                    user=user, password=password)
        l0_loader = L0_NamesLoader(mission, rdb_conn)

        l0_list_file = args.inputFile

        # if input file is defined,get from input file
        # get validities from input file!!
        # Name, start, stop
        # in csv format
        if l0_list_file is not None:
            with open(l0_list_file, "r") as fid:
                for line in fid.readlines():
                    l0_validities = line.rstrip('\n').split(' ')
                    # S1B_IW_RAW__0SDV_20190822T145111_20190822T145143_017700_0214CF_EBA5.SAFE.zip
                    # start, stop = self._l0_name_parser.get_start_stop(l0_name)
                    l0_name, start, stop = l0_validities
                    l0_loader.add_l0_name(l0_name, start, stop)

        else:
            #if args.fromdate:
            #    # set time to 00:00:00
            #    from_datetime_str = args.fromdate+"000000"
            #    from_date = dt.datetime.strptime(from_datetime_str, '%Y%m%d%H%M%S')
            #    # TODO: set the same from date for all types
            # Get Max validity for all types related to mission
            lta_retriever = LtaL0Retriever(mission, args.ltaurl, args.ltauser, args.ltapassword, num_days)
            if 'from_datetime' in vars(args):
                from_date = args.from_datetime
                last_l0_type_table = {}
                for l0_type in mission_l0_types[mission]:
                    last_l0_type_table[l0_type] = {}
                    for unit in mission_units.get(mission):
                        last_l0_type_table[l0_type].update({unit: from_date})
            else:
                last_l0_type_table = l0_loader.get_l0_latest_validity()
            print("Last L0 validity for each Type for mission ", mission, ": ", last_l0_type_table)
            print("Loop")
            for l0_type in mission_l0_types[mission]:
                # for each satellite, or satellite_sensoor:
                print("L0 type ", l0_type)
                for unit, val_time in last_l0_type_table[l0_type].items():
                    # Get from LTA a list of L0 names, for N days (or up to today),
                    l0_products = lta_retriever.get_lta_l0_products(unit, l0_type, val_time)
                    print("Retrieved L0 names for unit: ", unit, ": ", [prod['Name'] for prod in l0_products])
                    # With N from command line, with default if not specified (or default got from config file)
                    # Add the l0 names to db
                    l0_loader.add_l0_products(l0_products)

    except Exception as e:
        print(e)
        # if conn:
        #     conn.rollback()
