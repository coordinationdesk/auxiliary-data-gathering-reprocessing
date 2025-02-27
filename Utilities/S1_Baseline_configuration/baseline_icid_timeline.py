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




class L0_IcidTimelineLoader:
    _insert_sql = """INSERT INTO icid_timeline(icid, fromdate, todate, unit) VALUES(%s, %s, %s, %s);"""
    #   We retrieve all the aux type l0 parameter values  for a mission
    # Unit is satellite + any possible sensor/subsystem
    _query_sql = """SELECT icid, fromdate, todate, unit FROM icid_timeline ;"""
    def __init__(self, mission, dbconn):
        print("Initializing  L0 ICID Timeline configurtion Loader for mission", mission)
        self._db_conn = dbconn
        self._mission = mission

    def get_l0_icid_timeline(self):
        unit_timeline_table = {}
        with self._db_conn as conn:
            with conn.cursor() as cursor:
                print("Executing ", self._query_sql )
                cursor.execute(self._query_sql )
                results = cursor.fetchall()
                # each record in result contains: unit, date
                for row in results:
                    fromdate = row[1]
                    icid = row[0]
                    todate = row[2]
                    unit = row[3]
                    unit_timeline_table.setdefault(unit, []).append((fromdate, todate, icid))
        # return a dict unit/lastest_date
        return unit_timeline_table


    def add_icid_intervals(self, icid_intervals):
        with self._db_conn as conn:
            for interval in icid_intervals:
                unit, fromdate, todate, icid = interval
                with conn.cursor() as cursor:
                    try:
                        print("Executing ", self._insert_sql % (icid, fromdate, todate, unit))
                        cursor.execute(self._insert_sql, (icid, fromdate, todate, unit))
                        conn.commit()
                    except IntegrityError as ie:
                        print("Record already existing, not inserted")
                        print(ie)
                        conn.rollback()
                    except Exception as e:
                        print(e)
                        conn.rollback()

    def add_unit_icid_interval(self, unit, fromdate, todate, icid):
        with self._db_conn as conn:
            with conn.cursor() as cursor:

                try:
                    cursor.execute(self._insert_sql, (icid, fromdate, todate, unit))
                    conn.commit()
                except Exception as e:
                    print(e)
                    conn.rollback()

def get_command_arguments():
    print("Called with command line: ", sys.argv)
    parser = argparse.ArgumentParser(description="This script allows you to load the configuration of the S1 L0 ICID Timeline ",  # main description for help
            epilog='\n\n', formatter_class=argparse.RawTextHelpFormatter)  # displayed after help
    parser.add_argument("-m", "--mission",
                        help="Mission for L0 files",
                        required=True)
    parser.add_argument("-i", "--inputFile",
                        help="Input listing file",
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
        config_loader = L0_IcidTimelineLoader(mission, rdb_conn)

        # auxtype, paramname, paramvalue
        # in csv format
        if auxtype_config_file is not None:
            with open(auxtype_config_file, "r") as fid:
                icid_reader = csv.reader(fid, delimiter=",")
                for icid_line in icid_reader:
                    print("Reading: ", icid_line)
                    # S1B_IW_RAW__0SDV_20190822T145111_20190822T145143_017700_0214CF_EBA5.SAFE.zip
                    unit, fromdate, todate, icid = icid_line
                    fromdate = fromdate if fromdate else None
                    todate = todate if todate else None
                    config_loader.add_unit_icid_interval(unit, fromdate, todate, icid)

        else:
            print("Current configuration stored in database")
            icid_timeline = config_loader.get_l0_icid_timeline()
            for unit, unit_timeline in icid_timeline.items():
                print("Retrieved current ICID Timeline for unit: ",unit)
                for interval in unit_timeline:
                    print(interval)
    except Exception as e:
        print(e)
        if rdb_conn:
             rdb_conn.rollback()

