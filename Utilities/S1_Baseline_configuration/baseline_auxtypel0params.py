#!/bin/python
# -*- coding: utf-8 -*-

import argparse
import datetime as dt
import time
import sys
import re
import psycopg2
from psycopg2 import IntegrityError
#from time_formats import odata_datetime_format
import csv




class L0_AuxTypeL0ParamsLoader:
    SAT_LEN = 3
    _insert_sql = """INSERT INTO auxtype_l0parametervalues(auxtype, name, value, mission) VALUES(%s, %s, %s, %s);"""
    #   We retrieve all the aux type l0 parameter values  for a mission
    # Unit is satellite + any possible sensor/subsystem
    _query_sql = """SELECT auxtype, mission, name, value FROM auxtype_l0parametervalues where mission  = '%s';"""
    def __init__(self, mission, dbconn):
        print("Initializing AuxType L0 Parameters configurtion Loader for mission", mission)
        self._db_conn = dbconn
        self._mission = mission

    def get_l0_aux_types_l0_parameters(self):
        type_last_val_dict = {}
        with self._db_conn as conn:
            with conn.cursor() as cursor:
                print("Executing ", self._query_sql % (self._mission))
                cursor.execute(self._query_sql % (self._mission))
                results = cursor.fetchall()
                print("Query returned: ", results)
                # each record in result contains: unit, date
                for row in results:
                    mission = row[1]
                    auxtype = row[0]
                    paramname = row[2]
                    paramvalue = row[3]
                    type_last_val_dict.setdefault(auxtype, {}).update({paramname: paramvalue})
        # return a dict unit/lastest_date
        return type_last_val_dict


    def add_aux_type_l0_config(self, aux_type_l0_params):
        with self._db_conn as conn:
            for aux_type_param_value in aux_type_l0_params:
                aux_type, name, value = aux_type_param_value
                with conn.cursor() as cursor:
                    try:
                        print("Executing ", self._insert_sql % (aux_type, name, value, self._mission))
                        cursor.execute(self._insert_sql, (aux_type, name, value, self._mission))
                        conn.commit()
                    except IntegrityError as ie:
                        print("Record already existing, not inserted")
                        print(ie)
                        conn.rollback()
                    except Exception as e:
                        print(e)
                        conn.rollback()

    def add_aux_type_l0_param(self, aux_type, name, value):
        with self._db_conn as conn:
            with conn.cursor() as cursor:

                try:
                    cursor.execute(self._insert_sql, (aux_type, name, value, self._mission))
                    conn.commit()
                except Exception as e:
                    print(e)
                    conn.rollback()


def get_command_arguments():
    print("Called with command line: ", sys.argv)
    parser = argparse.ArgumentParser(description="This script allows you to upload to the Task 3 the configurazione w.r.t. L0 attributes of AuxTypes",  # main description for help
            epilog='\n\n', formatter_class=argparse.RawTextHelpFormatter)  # displayed after help
    parser.add_argument("-m", "--mission",
                        help="Mission for L0 files",
                        required=True)
    parser.add_argument("-i", "--inputFile",
                        help="Input listing file",
                        required=True)
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
    arg_values = parser.parse_args()
    print("Command line arguments: ", arg_values)
    return arg_values


if __name__ == "__main__":

    args = get_command_arguments()
    host=args.host
    port=args.port
    database=args.dbName
    user=args.user
    password=args.password
    mission=args.mission

    try:
        rdb_conn = psycopg2.connect(host=host, port=port, database=database,
                                    user=user, password=password)

        auxtype_config_file = args.inputFile
        config_loader = L0_AuxTypeL0ParamsLoader(mission, rdb_conn)

        # auxtype, paramname, paramvalue
        # in csv format
        if auxtype_config_file is not None:
            with open(auxtype_config_file, "r") as fid:
                aux_reader = csv.reader(fid, delimiter=",")
                for aux_cfg in aux_reader:
                    # S1B_IW_RAW__0SDV_20190822T145111_20190822T145143_017700_0214CF_EBA5.SAFE.zip
                    aux_type, paramname, paramvalue = aux_cfg
                    config_loader.add_aux_type_l0_param(aux_type, paramname, paramvalue)

        else:
            print("Last L0 validity for each Type for mission ", mission, ": ", last_l0_type_table)
            aux_type_l0_parameters = l0_loader.get_l0_aux_types_l0_parameters(mission)
            print("Retrieved Parameter values for aux types: ",  aux_type_l0_parameters)

    except Exception as e:
        print(e)
        if rdb_conn:
             rdb_conn.rollback()
