# -*- coding: utf-8 -*-

#
#
# Telespazio S.p.A.


import os
import csv
import sys

from ftplib import FTP
from zipfile import ZipFile
import shutil


class FtpRepository:
    def __init__(self, hostname, ftpuser, ftppwd, start_folder, user_home=False):
    	#with FTP(hostname) as ftp:
        self._ftp_conn = FTP(hostname)
        self._ftp_conn.login(ftpuser, ftppwd)
        print("Connected ...")
        if user_home:
            # Data is put under user named folder under root
            self._ftp_conn.cwd(ftpuser)
            print("..Moved to home dir: ", ftpuser)
        # cd start folder
        self._ftp_conn.cwd(start_folder)
        print("..Moved to start dir: ", start_folder)

    def close():
        self._ftp_conn.quit()

    def download_interval_products(self, from_day, n_days, dest_dir):
        # loop on each day
        #
        pass

    # to be called with a string for the day
    # e.g: yyyy/mm/dd
    def download_day_products(self, date_str, dest_dir):
        # convert date_str to folder structure
        # date_folders = 
        date_parts = date_str.split("-")
        date_path = os.path.join(*date_parts)
        # List product folders
        daily_products = self.list_day_products(date_path)
        # download_products
        self._download_products_folders(date_path, daily_products, dest_dir)
        self._compress_downloaded_products(date_str, daily_products, dest_dir)
        self._remove_products_folders(date_str, daily_products, dest_dir)

    def _remove_products_folders(self, date_str, product_folders, target_dir):
        for folder in product_folders:
            self._remove_product_folder(date_str, folder, target_dir)

    def _remove_product_folder(self, date_str, product_folder, target_dir):
            folder_path = os.path.join(target_dir, product_folder)
            shutil.rmtree(folder_path, ignore_errors=True)

    # to be called with a string for the day
    # e.g: yyyy/mm/dd
    def list_day_products(self, date_str):
        # convert date_str to folder structure
        # date_folders = 
        date_folders = [date_str]
        print("Listing products for date ", date_str)
        # cd to day folder at end of folder structure
        # List product folders
        aux_files = []
        # TODO: change return type to generator
        for aux_folder in date_folders:
            print("Trying folder ", aux_folder)
            # List files in Aux Folder
            print(list(self._ftp_conn.mlsd(aux_folder)))
            products = [item[0]
                        for item in self._ftp_conn.mlsd(aux_folder)
                        if item[0] != '.' and item[0] != '..']
            aux_files.extend(products)
        return aux_files

    def _download_products_folders(self, main_folder, folders_list, dest_dir):
        self._ftp_conn.cwd(main_folder)
        # Read file with Aux names list
        for aux_folder in folders_list:
            print("Trying product ", aux_folder)
            # Create folder in dest path with product name
            target_folder = os.path.join(dest_dir, aux_folder)
            try:
                os.mkdir(target_folder)
            except OSError as e:
                if not os.path.exists(target_folder):
                    raise

            print("Created destination folder")
            # List files in Aux Folder
            aux_files = [item[0]
                        for item in self._ftp_conn.mlsd(aux_folder)
                        if item[0] != '.' and item[0] != '..']
            for aux_file in aux_files:
                print(".. Downloading product file: ", aux_file)
                with open(os.path.join(target_folder, aux_file), 'wb') as out_f:
                    self._ftp_conn.retrbinary(f"RETR {aux_folder}/{aux_file}", out_f.write)
                    #self._compress_folder()
                    #self._remove_folder()
                print(".. Downloaded product file: ", aux_file)
            print(".... Downloaded product")
        self._ftp_conn.cwd('..')
        print(".... Downloaded all ", main_folder, " products")
    
    def _compress_product(self, product_folder, dest_dir):
        print("[BEG] Compressing  product ", product_folder)
        prod_zip_filename = product_folder+".zip"
        prod_zip_path = os.path.join(dest_dir, prod_zip_filename)
        product_path = os.path.join(dest_dir, product_folder)
        print("Creating zip file ", prod_zip_path)
        with ZipFile(prod_zip_path, 'w') as zip_product:
            #zip_product.write(product_folder)
            for strRoot, listDirNames, listFileNames in os.walk(product_path):
                for prod_file in listFileNames:
                    print("Adding file ", prod_file, " to zip at path: ", product_folder)
                    prod_file_path = os.path.join(product_path, prod_file)
                    zip_product.write(prod_file_path,
                                      os.path.join(product_folder, prod_file))
        print("[END] Product ", product_folder, " compressed")

    def _compress_downloaded_products(self, date_str, products_list, dest_dir):
        print("[BEG] Compressing downloaded products")
        for product in products_list:
            self._compress_product(product, dest_dir)
        print("[END] Compressed downloaded products")

    def period_checksums(self, year, month=None):
        self._ftp_conn.cwd(str(year))
        if month is not None:
            month_list = [month]
        else:
            month_list = self._ftp_conn.msld()
        # List of pairs filename/checksum
        cksum_list = []
        # TODO: if year, list alll months, then list all products
        # if month, list only the specified month
        for m in month_list:
            # LIst folders in each subdirectory of month m
            # execute checksum on folder/files in all month days
           for filename, information in ftp.mlsd():
               file_cksum_answer = ftp.sendcmd(f"XMD5 {filename}")
               # Extract checksum and command result, check if success
               ck_res, file_cksum = file_cksum_answer.split(' ')
               cksum_list.append((filename, information['size'], file_cksum))
               #append to result
        return ckum_list

def ftp_list_files_checksums(hostname, ftpuser, ftppwd, out_file):
    with FTP(hostname) as ftp:
        ftp.login(ftpuser, ftppwd)
        print("Connected...")
        with open(out_file, 'w') as out_f:
            out_f_writer = csv.writer(out_f)
            for filename, information in ftp.mlsd():
                sys.stdout.write("\r.. Processing %s" % filename)
                sys.stdout.flush()
                file_cksum_answer = ftp.sendcmd(f"XMD5 {filename}")
                # Extract checksum and command result, check if success
                ck_res, file_cksum = file_cksum_answer.split(' ')
                out_f_writer.writerow([file_cksum, filename, information['size']])
            print()

