#!/bin/python
# -*- coding: utf-8 -*-

# PUrpose of this script is to verify alignment of L0 Names in db
# vs LTA
# 1. retrieve from lta list of l0 names for mission for interval
# 2. retrieve from reprobase list of l0 namesfor mission for interval
# 3. compare the two lists and extract:
#    list of l0 names not present in reprobase
#    list of l0 names not present in LTA
import argparse
import datetime as dt
import time
import sys
import re
import psycopg2
from psycopg2 import IntegrityError

#from time_formats import odata_datetime_format

from L0_lta_retriever import LtaL0Retriever

class L0_NamesRetriever:
    SAT_LEN = 3
    #   We retrieve all the satellite/satellte_sensor for a mission
    # Unit is satellite + any possible sensor/subsystem
    _query_sql = """SELECT name FROM l0_products where SUBSTRING(name, 0, 3) = '%s' and validitystart >= '%s' and validitystart <= '%s';"""
    @staticmethod
    def add_arguments(parser) :
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

    def __init__(self, mission, db_args, numdays ):
        print("Initializing L0 Retriever for mission", mission)
        host=db_args.host
        port=db_args.port
        database=db_args.dbName
        user=db_args.user
        password=db_args.password
        db_conn = psycopg2.connect(host=host, port=port, database=database,
                                    user=user, password=password)
        self._db_conn = db_conn
        self._mission = mission
        self._num_days = int(numdays)
        self._now_time = dt.datetime.utcnow()

    def get_l0_names(self, l0_type, fromtime):
        print("Retrieving from db l0 names for type ", l0_type, ", from time " , fromtime, ", num days: ", self._num_days)
        to_date = from_date + dt.timedelta(days=self._num_days)
        print("computed to date: ", to_date)
        end_time = min (to_date, self._now_time)
        with self._db_conn as conn:
            with conn.cursor() as cursor:
                print("Executing ", self._query_sql % (self._mission, fromtime, end_time ))
                cursor.execute(self._query_sql % (self._mission, fromtime, end_time))
                results = cursor.fetchall()
                #print("Query returned: ", results)
                # each record in result contains: unit, date
        # return a dict unit/lastest_date
        return [rec[0] for rec in results]

def compare_lta_db_names_lists(lta_list, db_list):
    # Build list union
    # For each name in list union
    #  specify if: aligned, only LTA, only DB
    # This is returned in detail structure list of tuples/named tuples
    # Add also a flag for LTA presence, DB Presence
    #  extract by category: list of names aligned, list of names only on lta, list of names only on DB
    # this is returned in summary structure dictionary, each element value is a list
    comparison_table = {}
    comparison_table['aligned'] = [ name for name in lta_list if name in db_list]
    comparison_table['only_lta'] = [ name for name in lta_list if name not in db_list]
    comparison_table['only_db'] = [name for name in db_list if name not in lta_list]
    return comparison_table

def print_l0_names(names_list):
    print('\n'.join(names_list))

def print_l0_names_comparison(names_comparison_table):
    print(len(names_comparison_table['aligned']), " L0 names aligned")
    num_only_lta = len(names_comparison_table['only_lta'])
    num_only_db = len(names_comparison_table['only_db'])
    print(num_only_lta, " L0 names not ingested from LTA")
    print(num_only_db, " L0 names not present on LTA")
    if num_only_lta:
        # print("L0 names not ingested: ")
        # answer = input("Return to print...")
        # print(','.join(names_comparison_table['only_lta']))
        print("L0 names not ingested: ", ','.join(names_comparison_table['only_lta']))
    if num_only_db:
        print("L0 names not present in LTA: ")
        answer = input("Return to print...")
        print(','.join(names_comparison_table['only_db']))
        #print(names_comparison_table['only_db'])

def get_command_arguments():
    print("Called with command line: ", sys.argv)
    parser = argparse.ArgumentParser(description="This script allows you to upload to the Task 3 a listing of L0 files for Mission",  # main description for help
            epilog='\n\n', formatter_class=argparse.RawTextHelpFormatter)  # displayed after help
    parser.add_argument("-m", "--mission",
                        help="Mission for L0 files",
                        required=True)
    parser.add_argument("-n", "--numDays",
                        help="Num Days for L0 files",
                        required=False)
    L0_NamesRetriever.add_arguments(parser) 
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
    parser.add_argument("-md", "--mode",
                        type=str,
                        choices=['LTA', 'DB', 'Compare'],
                        help="Mode of execution: LTA only, DB only, Compare",
                        required=False, default="Compare")
    arg_values = parser.parse_args()
    print("Command line arguments: ", arg_values)
    if arg_values.ltaurl is  None or arg_values.ltauser is None or arg_values.ltapassword is None:
        parser.error("LTA arguments shall be all specified")
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
    mission=args.mission
    mode = args.mode

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
        l0_retriever = L0_NamesRetriever(mission, args, num_days)

        # if input file is defined,get from input file
        # get validities from input file!!
        # Get Max validity for all types related to mission
        lta_retriever = LtaL0Retriever(mission, args.ltaurl, args.ltauser, args.ltapassword, num_days, True)
        if 'from_datetime' in vars(args):
            from_date = args.from_datetime
            last_l0_type_table = {}
            for l0_type in mission_l0_types[mission]:
                last_l0_type_table[l0_type] = {}
                for unit in mission_units.get(mission):
                    last_l0_type_table[l0_type].update({unit: from_date})
        lta_l0_names = []
        db_l0_products = []
        for l0_type in mission_l0_types[mission]:
            # for each satellite, or satellite_sensoor:
            print("L0 type ", l0_type)
            for unit, val_time in last_l0_type_table[l0_type].items():
                if mode in ['LTA', 'Compare']:
                    # Get from LTA a list of L0 names, for N days (or up to today),
                    lta_l0_names.extend(lta_retriever.get_lta_l0_names(unit, l0_type, val_time))
                    print("Retrieved ", len(lta_l0_names), " names for unit: ", unit)
                    #print("Retrieved L0 names for unit: ", unit, ": ", [prod['Name'] for prod in lta_l0_names])
                if mode in ['DB', 'Compare']:
                    # With N from command line, with default if not specified (or default got from config file)
                    # Add the l0 names to db
                    db_l0_products.extend(l0_retriever.get_l0_names(l0_type, val_time))

        if mode == 'Compare':
            l0_names_comparison = compare_lta_db_names_lists(lta_l0_names, db_l0_products)
            print("Results of comparison: ")
            print_l0_names_comparison(l0_names_comparison)
        elif mode == 'LTA':
            print("L0 Names on LTA")
            answer = input("Return to print...")
            print("Found following names on LTA")
            print_l0_names(lta_l0_names)
        else:
            print("L0 Names on ADG-RPP")
            answer = input("Return to print...")
            print("Found following names on AUXIP")
            print_l0_names(db_l0_products)
    except Exception as e:
        print(e)

    exit(0)
