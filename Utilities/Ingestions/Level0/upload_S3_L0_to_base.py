#!/bin/python
# -*- coding: utf-8 -*-

import psycopg2
import argparse
from L0_Fields_parse import parse_start_stop_fields


if __name__ == "__main__": 

    parser = argparse.ArgumentParser(description="This script allows you to upload to the Task 3 a listing of L0 files for S2",  # main description for help
            epilog='\n\n', formatter_class=argparse.RawTextHelpFormatter)  # displayed after help
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
    parser.add_argument("-u", "--user",
                        help="User for DataBase authentication",
                        required=True)
    parser.add_argument("-pwd", "--password",
                        help="Password for DataBase authentication",
                        required=True)

    args = parser.parse_args()

    host=args.host
    port=args.port
    database=args.dbName
    user=args.user
    password=args.password

    try:
        l0_list_file = args.inputFile
        sql = """INSERT INTO l0_products(name,validitystart,validitystop) VALUES(%s,%s,%s);"""
        with psycopg2.connect(host=host,port=port,database=database,user=user,password=password) as conn:

            with open(l0_list_file, "r") as fid:
                lines = fid.readlines()
                for line in lines:
                    l0_name = line.rstrip('\n')
                    # S3A_SR_0_CAL____20220403T135114_20220403T135129_20220403T143818_0014_083_366______PS1_O_NR_004.SEN3.zip
                    start, stop = parse_start_stop_fields(l0_name, start_pos=16, field_len=15)
                
                    with conn.cursor() as cursor:
                        try:
                            cursor.execute(sql, (l0_name,start,stop))
                        except Exception as e:
                            print(e)
                            conn.rollback()
                        conn.commit()


