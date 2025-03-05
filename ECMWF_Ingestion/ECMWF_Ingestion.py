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

    timestampsToAddToDBL = [0,6,12,18,24,30]
    workingDir = args.working

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
    template_filename_cams = os.path.join(os.path.dirname(os.path.realpath(__file__)),"hdr_template.xml")
    #template_filename_cams = os.path.join(os.path.dirname(os.path.realpath(__file__)),"hdr_template_cams.xml")
    print("template hdr : "+template_filename_cams)
    hdr_namespace_table = dict([node for _, node in ET.iterparse(template_filename_cams, events = ['start-ns'])])
    tree_hdr_cams = ET.parse(template_filename_cams)
    root_hdr_cams = tree_hdr_cams.getroot()
    fixed_header_hdr_cams = root_hdr_cams.find("Fixed_Header",namespaces=hdr_namespace_table)


    #CAMS
    print("Starting CAMS data handling")
    # Init client with access for application
    # full_key = "{0}:{1}".format(args.user, args.key)
    full_key = args.key
    cdsclient = cdsapi.Client(url=args.url, key=full_key, debug=True)
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

    request_3_target = os.path.join(workingDir, "request3.grib")
    request_3.target = request_3_target
    request_3.date_begin = args.startdate
    request_3.date_end = args.enddate
    # request_3_filename = os.path.join(workingDir, "request3.req")
    # request_3.write_to_file(request_3_filename)
    # Write to file if a log is needed of request issued
   #Exec request
    cdsclient.retrieve(request_3.dataset, request_3.request_as_dict(), request_3.target).download()
    #Split the grib into pieces to recompose afterword
    request_3_split_folder = os.path.join(workingDir, "request_3_split")
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
    request_4_target = os.path.join(workingDir, "request4.grib")
    request_4.target = request_4_target
    # request_4_filename = os.path.join(workingDir, "request4.req")
    # request_4.write_to_file(request_4_filename)
    cdsclient.retrieve(request_4.dataset, request_4.request_as_dict(), request_4.target).download()
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
    dataValidityLength = 36
    #
    # Loop from beginning of the period to the end of it
    #

    work_date_pyt = start_date_pyt
    CAMS_working_dir = os.path.join(workingDir, "CAMS_Files")
    os.makedirs(CAMS_working_dir, exist_ok=True)
    while work_date_pyt <= end_date_pyt:
        print("Processing date ", work_date_pyt)
        files_to_tar = []

        work_date_str = work_date_pyt.strftime("%Y%m%d%H%M%S")

        # for t in [0,12,24]:
        for t in timestampsToAddToDBL:
            cur_date_pyt = work_date_pyt + datetime.timedelta(hours=t)
            curr_date_str = cur_date_pyt.strftime("%Y%m%d")
            curr_hour_str = cur_date_pyt.strftime("%H")
            # find request 1 grib file
            file_to_search = f"z_cams_c_ecmf_{curr_date_str}_prod_an_sfc_{curr_hour_str}*.grib"
            print("Searching files for date ", curr_date_str, ", hour ", curr_hour_str)
            req_cams_grib_files = glob.glob(os.path.join(request_3_split_folder, file_to_search))
            if len(req_cams_grib_files) != request_num_params:
                print("Error on getting request cams file for date " + file_to_search)
                print(req_cams_grib_files)
                exit(1)
            # The file has been found
            for cams_file in req_cams_grib_files:
                #Create the GRIB output files
                grib_output_filename = f"z_cams_c_ecmf_{work_date_str}_prod_an_sfc_"+"{:03d}".format(t)+cams_file[str(cams_file).rfind("_"):]
                print("Copying CAMS file ", cams_file, " to file ", grib_output_filename)

                #Agglomerate both files
                shutil.copyfile(cams_file,os.path.join(CAMS_working_dir,grib_output_filename))
                files_to_tar.append(grib_output_filename)
        #create HDR file
        valid_start_time = work_date_pyt
        valid_start = valid_start_time.strftime(FILENAME_TIME_FORMAT)
        valid_stop_time = work_date_pyt + datetime.timedelta(hours=dataValidityLength)
        valid_stop = valid_stop_time.strftime(FILENAME_TIME_FORMAT)
        hdr_filename = f"S2__OPER_AUX_CAMSAN_ADG__{work_date_pyt.strftime(FILENAME_TIME_FORMAT)}_V{valid_start}_{valid_stop}"
        print(hdr_filename)
        valid_start_xml = valid_start_time.strftime(XML_TIME_FORMAT)
        valid_stop_xml = valid_stop_time.strftime(XML_TIME_FORMAT)
        crea_time_xml = work_date_pyt.strftime(XML_TIME_FORMAT)
        fixed_header_hdr_cams.find("File_Name", hdr_namespace_table).text = hdr_filename
        fixed_header_hdr_cams.find("Validity_Period",hdr_namespace_table).find("Validity_Start",hdr_namespace_table).text = valid_start_xml
        fixed_header_hdr_cams.find("Validity_Period", hdr_namespace_table).find("Validity_Stop",
                                                                     hdr_namespace_table).text = valid_stop_xml
        fixed_header_hdr_cams.find("Source", hdr_namespace_table).find("Creation_Date",
                                                                         hdr_namespace_table).text = valid_stop_xml
        print(fixed_header_hdr_cams.find("File_Name",hdr_namespace_table).text)
        print(fixed_header_hdr_cams.find("Validity_Period", hdr_namespace_table).find("Validity_Start",hdr_namespace_table).text)

        print("Starting HDR file write : " + os.path.join(workingDir, hdr_filename + ".HDR"))
        tree_hdr_cams.write(os.path.join(workingDir,hdr_filename+".HDR"),encoding="UTF-8")
        print("Starting DBL file write : " + os.path.join(workingDir, hdr_filename + ".DBL"))
        # Create DBL
        process_dbl = subprocess.run(["tar", "cf",
                                      os.path.join(workingDir,hdr_filename+".DBL"),
                                      "-C", CAMS_working_dir]+files_to_tar)
        if process_dbl.returncode != 0:
          print("Failed tar the DBL for date "+cur_date_pyt.strftime("%Y-%m-%dT%H:%M:%S"))
          exit(1)
        # Create TGZ
        product_file_path = os.path.join(workingDir, hdr_filename + ".TGZ")
        process_tgz = subprocess.run(["tar", "czf",
                                      product_file_path,
                                      "-C", workingDir,
                                      hdr_filename+".DBL",
                                      hdr_filename+".HDR"])
        if process_tgz.returncode != 0:
           print("Failed tar the DBL for date " + cur_date_pyt.strftime("%Y-%m-%dT%H:%M:%S"))
           exit(1)
        shutil.move(product_file_path, os.path.join(args.output, hdr_filename + ".TGZ"))
        print("TGZ file wrote : " + os.path.join(args.output, hdr_filename + ".TGZ"))
        work_date_pyt = work_date_pyt + datetime.timedelta(days=1)
