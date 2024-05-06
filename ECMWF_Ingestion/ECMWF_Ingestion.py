#!/bin/python
# -*- coding: utf-8 -*-

import argparse
import os,re,subprocess,datetime,glob,shutil
import request_generator
import cdsapi
from lxml import etree as ET


def save_to_xml_file(root_node, xml_filepath):
    print("Writing %s", xml_filepath)
    tree = ET.ElementTree(root_node)

    with open(xml_filepath, "w") as fi:
        fi.write(ET.tostring(tree, xml_declaration=True, method="xml",
                            encoding="UTF-8").decode())
        fi.close()
    print("%s Created", xml_filepath)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="This script generates the ECMXF files for a period",  # main description for help
            epilog='Usage samples : \n\tpython ECMWF_Ingestion.py -u ads_url -pw userkey \n\n', formatter_class=argparse.RawTextHelpFormatter)  # displayed after help
    parser.add_argument("-k", "--key",
                        help="Mars ADS key",
                        required=True)
    parser.add_argument("-u", "--url",
                        help="Mars ADS url",
                        required=True)
    parser.add_argument("-m", "--user",
                        help="Mars ADS User id ",
                        required=True)
    parser.add_argument("-w", "--working",
                        help="Working folder",
                        required=True)
    parser.add_argument("-o", "--output",
                        help="Output folder",
                        required=True)
    parser.add_argument("-s", "--startdate",
                        help="starting date",
                        required=True)
    parser.add_argument("-e", "--enddate",
                        help="ending date",
                        required=True)
    args = parser.parse_args()

    pattern_date = re.compile("[0-9]{4}-[0-9]{2}-[0-9]{2}")
    if not re.search(pattern_date,args.startdate):
        print("The start date doesn't respect the pattern 2015-06-23")
        exit(1)
    if not re.search(pattern_date,args.enddate):
        print("The end date doesn't respect the pattern 2015-06-23")
        exit(1)

    start_date_pyt = datetime.datetime.strptime(args.startdate, "%Y-%m-%d")
    end_date_pyt = datetime.datetime.strptime(args.enddate, "%Y-%m-%d")

    #Open HDR template file
    template_filename = os.path.join(os.path.dirname(os.path.realpath(__file__)),"hdr_template.xml")
    print("template hdr : "+template_filename)
    my_namespaces = dict([node for _, node in ET.iterparse(template_filename, events = ['start-ns'])])
    tree_hdr = ET.parse(template_filename)
    root_hdr = tree_hdr.getroot()
    fixed_header_hdr = root_hdr.find("Fixed_Header",namespaces=my_namespaces)
    #Open HDR template file
    template_filename_cams = os.path.join(os.path.dirname(os.path.realpath(__file__)),"hdr_template_cams.xml")
    print("template hdr _cams filenames: "+template_filename_cams)
    my_namespaces_cams = dict([node for _, node in ET.iterparse(template_filename_cams, events = ['start-ns'])])
    tree_hdr_cams = ET.parse(template_filename_cams)
    root_hdr_cams = tree_hdr_cams.getroot()
    fixed_header_hdr_cams = root_hdr_cams.find("Fixed_Header",namespaces=my_namespaces)


    #CAMS
    print("Starting CAMS data handling")
    # TODO: Change: basic cds_request, ADG_CAMS_Request, ADG_CAMSAN_request, ADG_CAMSRE_request
    # PUt dwonload in a separate module/function
    request_3 = request_generator.RequestGenerator()
    request_3.param_list = ['black_carbon_aerosol_optical_depth_550nm',
                           'dust_aerosol_optical_depth_550nm',
                            'organic_matter_aerosol_optical_depth_550nm',
                            'sea_salt_aerosol_optical_depth_550nm',
                            'sulphate_aerosol_optical_depth_550nm', 'surface_geopotential',
                            'total_aerosol_optical_depth_1240nm',
                            'total_aerosol_optical_depth_469nm',
                            'total_aerosol_optical_depth_550nm',
                            'total_aerosol_optical_depth_670nm',
                            'total_aerosol_optical_depth_865nm']
    request_num_params = len(request_3.param_list)
    request_3.domain = None

    #request_3.dataset = "cams_nrealtime"
    request_3.grid = "0.4/0.4"
    #request_3.classid = "mc"
    request_3.time_list = ["00:00","06:00","12:00","18:00"]
    request_3.type = "analysis"
    #request_3.type = "an"
    #request_3.step = None

    request_3_target = os.path.join(args.working, "request3.grib")
    request_3.target = request_3_target
    request_3.date_begin = args.startdate
    request_3.date_end = args.enddate
    # request_3_filename = os.path.join(args.working, "request3.req")
    # request_3.write_to_file(request_3_filename)
    # Write to file if a log is needed of request issued
   #Exec request
    full_key = "{0}:{1}".format(args.user, args.key)
    cdsclient = cdsapi.Client(url=args.url, key=full_key, debug=True)
    cdsclient.retrieve(request_3.dataset, request_3.request_as_dict(), request_3.target)
    #Split the grib into pieces to recompose afterword
    request_3_split_folder = os.path.join(args.working, "request_3_split")
    os.makedirs(request_3_split_folder, exist_ok=True)
    process_3 = subprocess.run(["grib_copy", request_3_target, os.path.join(request_3_split_folder,
                                                                          "z_cams_c_ecmf_[dataDate]_prod_an_sfc_[time]_[shortName].grib")])
    if process_3.returncode != 0:
      print("Failed to cut grib for request 3")
      exit(1)
    request_4 = request_3
    request_4.time_list = ["00:00","06:00"]
    request_4.date_begin = (end_date_pyt+datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    # TODO: Investigate: what happens for End date not specified?
    request_4.date_end = None
    request_4_target = os.path.join(args.working, "request4.grib")
    request_4.target = request_4_target
    # request_4_filename = os.path.join(args.working, "request4.req")
    # request_4.write_to_file(request_4_filename)
    cdsclient.retrieve(request_4.dataset, request_4.request_as_dict(), request_4.target)
    #test if grib is here
    if not os.path.exists(request_4_target):
       print("Output grib for request 4 is not available")
       exit(1)
    #Split the grib into pieces to recompose afterword
    process_4 = subprocess.run(["grib_copy", request_4_target, os.path.join(request_3_split_folder,
                                                                            "z_cams_c_ecmf_[dataDate]_prod_an_sfc_[time]_[shortName].grib")])
    if process_4.returncode != 0:
      print("Failed to cut grib for request 4")
      exit(1)

    print("CAMS Data gribs retrieved and splitted")
    #Put in each output files
    XML_TIME_FORMAT = "UTC=%Y-%m-%dT%H:%M:%S"
    FILENAME_TIME_FORMAT = "%Y%m%dT%H%M%S"

    work_date_pyt = start_date_pyt
    CAMS_working_dir = os.path.join(args.working, "CAMS_Files")
    os.makedirs(CAMS_working_dir, exist_ok=True)
    while work_date_pyt <= end_date_pyt:
        print("Processing date ", work_date_pyt)
        files_to_tar = []
        # for t in [0,12,24]:
        for t in [0,6,12,18,24,30]:
            cur_date_pyt = work_date_pyt + datetime.timedelta(hours=t)
            # find request 1 grib file
            file_to_search = "z_cams_c_ecmf_"+cur_date_pyt.strftime("%Y%m%d")+"_prod_an_sfc_"+cur_date_pyt.strftime("%H")+"*.grib"
            print("Searching files for date ", cur_date_pyt.strftime("%Y%m%d"), ", hour ", cur_date_pyt.strftime("%H"))
            req_cams_grib_files = glob.glob(os.path.join(request_3_split_folder, file_to_search))
            if len(req_cams_grib_files) != request_num_params:
                print("Error on getting request cams file for date " + file_to_search)
                print(req_cams_grib_files)
                exit(1)
            for cams_file in req_cams_grib_files:
                #Create the GRIB output files
                grib_output_filename = "z_cams_c_ecmf_"+work_date_pyt.strftime("%Y%m%d%H%M%S")+"_prod_an_sfc_"+"{:03d}".format(t)+cams_file[str(cams_file).rfind("_"):]
                print("Copying CAMS file ", cams_file, " to file ", grib_output_filename)
                #Agglomerate both files
                shutil.copyfile(cams_file,os.path.join(CAMS_working_dir,grib_output_filename))
                files_to_tar.append(grib_output_filename)
        #create HDR file
        valid_start_time = work_date_pyt
        valid_start = valid_start_time.strftime("%Y%m%dT%H%M%S")
        valid_stop_time = work_date_pyt + datetime.timedelta(hours=36)
        valid_stop = valid_stop_time.strftime("%Y%m%dT%H%M%S")
        hdr_filename = "S2__OPER_AUX_CAMSAN_ADG__"+work_date_pyt.strftime("%Y%m%dT%H%M%S")+"_V"+valid_start+"_"+valid_stop
        print(hdr_filename)
        valid_start_xml = valid_start_time.strftime(XML_TIME_FORMAT)
        valid_stop_xml = valid_stop_time.strftime(XML_TIME_FORMAT)
        crea_time_xml = work_date_pyt.strftime(XML_TIME_FORMAT)
        fixed_header_hdr_cams.find("File_Name", my_namespaces).text = hdr_filename
        fixed_header_hdr_cams.find("Validity_Period",my_namespaces).find("Validity_Start",my_namespaces).text = valid_start_xml
        fixed_header_hdr_cams.find("Validity_Period", my_namespaces).find("Validity_Stop",
                                                                     my_namespaces).text = valid_stop_xml
        fixed_header_hdr_cams.find("Source", my_namespaces).find("Creation_Date",
                                                                         my_namespaces).text = valid_stop_xml
        print(fixed_header_hdr_cams.find("File_Name",my_namespaces).text)
        print(fixed_header_hdr_cams.find("Validity_Period", my_namespaces).find("Validity_Start",my_namespaces).text)

        print("Starting HDR file write : " + os.path.join(args.working, hdr_filename + ".HDR"))
        tree_hdr_cams.write(os.path.join(args.working,hdr_filename+".HDR"),encoding="UTF-8")
        print("Starting DBL file write : " + os.path.join(args.working, hdr_filename + ".DBL"))
        # Create DBL
        process_dbl = subprocess.run(
             ["tar", "cf", os.path.join(args.working,hdr_filename+".DBL"), "-C", CAMS_working_dir]+files_to_tar)
        if process_dbl.returncode != 0:
          print("Failed tar the DBL for date "+cur_date_pyt.strftime("%Y-%m-%dT%H:%M:%S"))
          exit(1)
        # Create TGZ
        process_tgz = subprocess.run(
               ["tar", "czf", os.path.join(args.working, hdr_filename + ".TGZ"), "-C", args.working, hdr_filename+".DBL",
                hdr_filename+".HDR"])
        if process_tgz.returncode != 0:
           print("Failed tar the DBL for date " + cur_date_pyt.strftime("%Y-%m-%dT%H:%M:%S"))
           exit(1)
        shutil.move(os.path.join(args.working, hdr_filename + ".TGZ"),os.path.join(args.output, hdr_filename + ".TGZ"))
        print("TGZ file wrote : " + os.path.join(args.output, hdr_filename + ".TGZ"))
        work_date_pyt = work_date_pyt + datetime.timedelta(days=1)
