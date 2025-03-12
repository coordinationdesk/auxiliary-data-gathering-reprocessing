#!/bin/python
# -*- coding: utf-8 -*-

import time
import argparse
import psycopg2
from psycopg2 import IntegrityError

from baseline_l0_client import L0_NamesLoader
from L0_Fields_parse import parse_start_stop_fields
# l0_product_type
# S1_L0_types = ["RAW__0S"]
# S3_L0_Types = ["MW_0_MWR___", "OL_0_EFR___", "SL_0_SLT___", "SR_0_SRA___"]


class S1_L0_NamesLoader(L0_NamesLoader):
    SAT_LEN = 3
    _insert_sql = """INSERT INTO l0_products(name, validitystart, validitystop, icid) VALUES(%s, %s, %s, %s);"""
    _upsert_sql = """INSERT INTO l0_products(name, validitystart, validitystop, icid) VALUES(%s, %s, %s, %s) ON CONFLICT (name) DO UPDATE SET (icid) = ROW(EXCLUDED.icid);"""
    #   We retrieve all the satellite/satellte_sensor for a mission
    # Unit is satellite + any possible sensor/subsystem
    #_query_sql = """SELECT SUBSTRING(name, 0, %d) unit, SUBSTRING(name, %d, %d) l0type, MAX(validitystart) FROM l0_products where SUBSTRING(name, 0, 3) = '%s' group by l0type, unit;"""
    def __init__(self, dbargs, update=False):
        print("Initializing S1 L0 Loader for mission")
        L0_NamesLoader.__init__(self, 'S1', dbargs)
        # If it was requested to update existing records, use
        # the upsert expression
        self._sql_statement = self._insert_sql if not update else self._upsert_sql

    def _get_lta_l0_validities(self, l0_products):
        # Appliy validity extractor to LTA query results
        # Add ICID from L0 Product
        return sorted((self._l0_validity_extractor.get_product_validity(l0_product) + (l0_product[3])
                for l0_product in l0_products))

    def add_l0_name_validities(self, l0_validities):
        with self._db_conn as conn:
            for l0_record in l0_validities:
                if len(l0_record) < 4:
                    print("Found a record with less than 4 fields: skipping")
                    continue
                l0_name, start, stop, icid = l0_record
                with conn.cursor() as cursor:
                    try:
                        print("Executing ", self._sql_statement % (l0_name, start, stop, icid))
                        cursor.execute(self._sql_statement, (l0_name, start, stop))
                        conn.commit()
                    except IntegrityError as ie:
                        print("Record already existing, not inserted")
                        print(ie)
                        conn.rollback()
                    except Exception as e:
                        print(e)
                        conn.rollback()

    def add_l0_name(self, l0_name, start, stop, icid):
        with self._db_conn as conn:
            with conn.cursor() as cursor:

                try:
                    cursor.execute(self._sql_statement, (l0_name, start, stop, icid))
                    conn.commit()
                except Exception as e:
                    print(e)
                    conn.rollback()
    def add_l0_products(self, l0_products):
        l0_validities = self._get_lta_l0_validities(l0_products)
        self.add_l0_name_validities(l0_validities)

