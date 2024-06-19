#!/bin/python
# -*- coding: utf-8 -*-

import psycopg2
import argparse
from L0_Fields_parse import parse_start_stop_fields


if __name__ == "__main__": 

    parser = argparse.ArgumentParser(description="This script allows you to upload to the Task 3 a listing of L0 files for S1",  # main description for help
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
        conn = psycopg2.connect(host=host,port=port,database=database,user=user,password=password)

        s1_l0=args.inputFile

        with open(s1_l0,"r") as fid:
            lines = fid.readlines()
            for line in lines:
            
                l0_name = line.replace('\n','').strip()
                #start = l0_name[17:17+15]
                #stop = l0_name[17+16:17+16+15]
                #print(l0_name)
                # S1B_IW_RAW__0SDV_20190822T145111_20190822T145143_017700_0214CF_EBA5.SAFE.zip
                start, stop = parse_start_stop_fields(l0_name, start=17, field_len=15)

                cursor = conn.cursor()
                sql = """INSERT INTO l0_products(name,validitystart,validitystop) VALUES(%s,%s,%s);"""
                try:
                    cursor.execute(sql, (l0_name,start,stop))
                except Exception as e:
                    print(e)
                    cursor.execute("ROLLBACK")

            conn.commit()
    except Exception as e:
        print(e)


