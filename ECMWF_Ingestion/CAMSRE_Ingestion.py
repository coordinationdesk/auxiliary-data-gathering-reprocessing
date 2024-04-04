import os,re,subprocess,datetime,glob,shutil,argparse
import sys
from lxml import etree as ET
import DownloadCamsreGrib
from ecmwf_product import create_hdr

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="This script generates the CAMSRE files for a period",  # main description for help
                                     epilog='Usage samples : \n\tpython CAMSRE_Ingestion.py -strt \'2021-01-01\' -stp \'2021-01-31\' -o CAMSRE_Generation/ \n\n',
                                     formatter_class=argparse.RawTextHelpFormatter)  # displayed after help
    parser.add_argument("-k", "--key",
                        help="Mars ADS key",
                        required=True)
    parser.add_argument("-u", "--url",
                        help="Mars ADS url",
                        required=True)
    parser.add_argument("-m", "--user",
                        help="Mars ADS User id ",
                        required=True)
    parser.add_argument("-start", "--start",
                        help="Date of the start of the CAMSRE generation",
                        required=True)
    parser.add_argument("-stop", "--stop",
                        help="Date of the end of the CAMSRE generation",
                        required=True)
    parser.add_argument("-wd", "--workingDir",
                        help="Working directory of the script",
                        required=True)
    parser.add_argument("-o", "--output",
                        help="Output folder",
                        required=True)
    args = parser.parse_args()

    # Timestamps of every grib files that need to appear in the final DBL file
    timestampsToAddToDBL = [0,3,6,9,12,15,18,21,24,27]

    startDate = datetime.datetime.strptime(args.start, "%Y-%m-%d")
    stopDate = datetime.datetime.strptime(args.stop, "%Y-%m-%d")

    workingDir = args.workingDir

    # Pattern of the main grib files downloaded
    RAW_GRIB_NAME_PATTERN = 'r%s.grib'

    # Launching downloads
    stopDateToDownload = stopDate
    # We modifiy the end date of download
    # to take into account all the timeStamps we want into the DBL archive
    # e.g. if we extend beyond the 24 H, take the additional dates after the end date
    # that could be necessary
    if timestampsToAddToDBL[-1]/24 > 1:
        stopDateToDownload += datetime.timedelta(days=int(timestampsToAddToDBL[-1]/24))
    # TODO: Number of measures to be retrieved from class in charge of creating requests
    num_measures = 11
    DownloadCamsreGrib.download_Cams_reGrib(startDate, stopDateToDownload,
                                            workingDir, RAW_GRIB_NAME_PATTERN,
                                            args.url,
                                            args.key, args.user)

    output_dir = args.output
    # outputDir = os.path.join(workingDir, "Output_CAMSRE")
    # os.makedirs(outputDir, exist_ok=True)

    # Directory used to extract all the grib files contained in the main grib file
    # downloaded
    initialGribExtractionDir = os.path.join(workingDir, 'initialGribExtraction')
    os.makedirs(initialGribExtractionDir, exist_ok=True)

    # Open HDR template file
    template_filename_cams = os.path.join(os.path.dirname(os.path.realpath(__file__)),"hdr_template_camsre.xml")
    print("template hdr _cams: "+template_filename_cams)
    hdr_namespace_table = dict([node for _, node in ET.iterparse(template_filename_cams, events = ['start-ns'])])
    tree_hdr_cams = ET.parse(template_filename_cams)
    root_hdr_cams = tree_hdr_cams.getroot()
    fixed_header_hdr_cams = root_hdr_cams.find("Fixed_Header",
                                               namespaces=hdr_namespace_table)

    for file in os.listdir(workingDir):
        # Iterate over all files of the current directory

        if re.fullmatch(RAW_GRIB_NAME_PATTERN % '\\d{1}', file) or re.fullmatch(RAW_GRIB_NAME_PATTERN % '\\d{2}', file) or re.fullmatch(RAW_GRIB_NAME_PATTERN % '\\d{3}', file):
            # The file is a main grib file downloaded

            # Split the grib into pieces to recompose afterward
            gribPattern = 'z_cams_c_ecmf_[dataDate]_prod_an_sfc_[time]_[shortName].grib'

            # Launch the split
            process_4 = subprocess.run(["grib_copy",
                                        os.path.join(workingDir, file),
                                        os.path.join(initialGribExtractionDir,
                                        gribPattern)])

            if process_4.returncode != 0:
                # The command to extract grib files from the main one has failed
                print("Failed to cut grib for request 4")
                sys.exit(1)

    print("Initial CAMS data retrieved")

    # Date used to loop over every day between the start and the end period given in parameters
    work_date_pyt = startDate

    # Directory where the final grib files will be stored
    CAMS_working_dir = os.path.join(workingDir, 'ReworkedExtractedGribFiles')
    os.makedirs(CAMS_working_dir, exist_ok=True)

    XML_TIME_FORMAT = "UTC=%Y-%m-%dT%H:%M:%S"
    FILENAME_TIME_FORMAT = "%Y%m%dT%H%M%S"
    dataValidityLength = 30
    #
    # Loop from beginning of the period to the end of it
    #
    while work_date_pyt <= stopDate:

        # Files that will be part of the DBL archive
        files_to_tar = []

        work_date_str = work_date_pyt.strftime("%Y%m%d%H%M%S")
        #
        # Taking into account the timestamps that are wanted int the final DBL file
        #
        for time_offset in timestampsToAddToDBL:
            # Adding the timestamp to the current date of grib to generate a new date
            # whose associated grib will be searched among the initially extracted grib files
            cur_date_pyt = work_date_pyt + datetime.timedelta(hours=time_offset)
            # Find the grib file among the initially extracted grib files
            curr_date_str = cur_date_pyt.strftime("%Y%m%d")
            curr_hour_str = cur_date_pyt.strftime("%H")
            file_to_search = f"z_cams_c_ecmf_{curr_date_str}_prod_an_sfc_{curr_hour_str}*.grib"
            req_cams_grib_file = glob.glob(os.path.join(initialGribExtractionDir, file_to_search))
            if len(req_cams_grib_file) != num_measures:
                # The grib file has not been found
                print("Error on getting the requested cams file for date " + file_to_search)
                print(req_cams_grib_file)
                sys.exit(1)

            # The file has been found
            for c in req_cams_grib_file:
                # Generate the new grib file name to create the GRIB output files
                grib_output_filename = f"z_cams_c_ecmf_{work_date_str}_prod_an_sfc_{time_offset:03d}"+c[str(c).rfind("_"):]
                # Agglomerate both files
                shutil.copyfile(c,os.path.join(CAMS_working_dir,grib_output_filename))
                # Add the file to the grib files that need to be part of the final DBL archive
                files_to_tar.append(grib_output_filename)

        # Validity of the final CAMSRE file
        valid_start_time = work_date_pyt
        validity_start_time_str = valid_start_time.strftime(FILENAME_TIME_FORMAT)
        # Number of hours that the file covers : it is set to 30 to match the already ingested
        # CAMSRE on base.
        valid_stop_time = work_date_pyt + datetime.timedelta(hours=dataValidityLength)
        validity_stop_time_str = valid_stop_time.strftime(FILENAME_TIME_FORMAT)

        work_date_str = work_date_pyt.strftime("%Y%m%dT%H%M%S")
        base_filename = f"S2__OPER_AUX_CAMSRE_ADG__{work_date_str}_V{validity_start_time_str}_{validity_stop_time_str}"
        print(base_filename)
        # File length was originally 36 hours, but it is in contrast with filename validity stop
        # we pass already set start/stop validity, as date/time
        # to be formatted with xml time format
        create_hdr(fixed_header_hdr_cams,
                   work_date_pyt, valid_start_time, valid_stop_time,
                   base_filename, hdr_namespace_table,
                   XML_TIME_FORMAT)
        print("Starting HDR file write : " + os.path.join(workingDir, base_filename + ".HDR"))
        # NOTE: we replace for each product the HDR xml in memory, and write to a different file
        # (filename changes due to validity interval change)
        tree_hdr_cams.write(os.path.join(workingDir,base_filename+".HDR"),encoding="UTF-8")
        print("Starting DBL file write : " + os.path.join(workingDir, base_filename + ".DBL"))

        # Create DBL
        process_dbl = subprocess.run(["tar", "cf",
                                      os.path.join(workingDir,base_filename+".DBL"),
                                      "-C",
                                      CAMS_working_dir]+files_to_tar)
        if process_dbl.returncode != 0:
            print("Failed tar the DBL for date "+cur_date_pyt.strftime("%Y-%m-%dT%H:%M:%S"))
            sys.exit(1)

        # Create TGZ
        product_file_path = os.path.join(workingDir, base_filename + ".TGZ")
        process_tgz = subprocess.run(["tar", "czf",
                                      product_file_path,
                                      "-C", workingDir,
                                      base_filename+".DBL",
                                      base_filename+".HDR"])
        if process_tgz.returncode != 0:
            print("Failed tar the DBL for date " + cur_date_pyt.strftime("%Y-%m-%dT%H:%M:%S"))
            sys.exit(1)
        dest_product_file_path = os.path.join(output_dir, base_filename + ".TGZ")
        shutil.move(product_file_path, dest_product_file_path)
        print("TGZ file wrote : ", dest_product_file_path)

        # Iteration of the current day
        work_date_pyt = work_date_pyt + datetime.timedelta(days=1)
