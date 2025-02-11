#!/bin/python
# -*- coding: utf-8 -*-

import time
import argparse
import psycopg2
from psycopg2 import IntegrityError


class AuxipProductUpdater:
    _insert_string_attr_sql = """INSERT INTO product_stringattributes(product_id, name, value, valuetype) VALUES(%s, %s, %s, 'String');"""
    #   We retrieve all the satellite/satellte_sensor for a mission
    # Unit is satellite + any possible sensor/subsystem
    _query_sql = """SELECT SUBSTRING(name, 0, %d) unit, SUBSTRING(name, %d, %d) l0type, MAX(validitystart) FROM l0_products where SUBSTRING(name, 0, 3) = '%s' group by l0type, unit;"""
    @staticmethod
    def add_arguments(parser):
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

    def __init__(self, mission, dbargs):
        print("Initializing L0 Loader for mission", mission)
        host=dbargs.host
        port=dbargs.port
        database=dbargs.dbName
        user=dbargs.user
        password=dbargs.password
        db_conn = psycopg2.connect(host=host, port=port, database=database,
                                    user=user, password=password)
        self._db_conn = db_conn
        self._mission = mission

    def add_auxip_product_string_attributes(self, product_attributes):
        # Product Attributes: list of: product_id, attribute name, attribute value
        print("Updating string attributes: ", product_attributes)
        with self._db_conn as conn:
            for attr_record in product_attributes:
                product_id, attr_name, attr_value = attr_record
                with conn.cursor() as cursor:
                    try:
                        print("Executing ", self._insert_string_attr_sql % (product_id, attr_name, attr_value))
                        cursor.execute(self._insert_string_attr_sql, (product_id, attr_name, attr_value))
                        conn.commit()
                    except IntegrityError as ie:
                        print("Record already existing, not inserted")
                        print(ie)
                        conn.rollback()
                    except Exception as e:
                        print(e)
                        conn.rollback()

    def add_auxip_product_string_attribute(self, attr_name, attr_value, product_id):
        with self._db_conn as conn:
            with conn.cursor() as cursor:

                try:
                    cursor.execute(self._insert_string_attr_sql, (product_id, attr_name, attr_value))
                    conn.commit()
                except Exception as e:
                    print(e)
                    conn.rollback()

    def update_aux_file(self, auxip_record, attrs_to_update):
        record_list = []
        product_id = auxip_record['Id']
        print("Updating Product ", product_id, " attributes: ", attrs_to_update)
        catalogue_attributes = auxip_record["Attributes"]
        print("Product attributes: ", catalogue_attributes)

        for attr_name in attrs_to_update:
            # Take from record data for attribute:
            record_attribute_item = next(
                           (item for item in catalogue_attributes if item['Name'] == attr_name),
                              None)
            if record_attribute_item is not None:
                attr_value = record_attribute_item['Value']
                # attr_type = record_attribute_item['Type']
                record_list.append((product_id, attr_name, attr_value))
        self.add_auxip_product_string_attributes(record_list)
        return True
