
# coding=utf-8
import csv
import datetime
import hashlib
import json
import os
import re
import copy
import shutil
import subprocess
import sys
import tarfile

import xml.etree.ElementTree as ET
from .time_formats import odata_datetime_format

# We are getting the value, since we return the "text" of the element
#   and how are we selecting the attribute
def getValueByName(root_node, attribute_name):
    if root_node is None:
        raise Exception("No node passed to retrieve attribute {} value".format(attribute_name))
    for elt in root_node:
        if attribute_name in elt.tag:
            return elt.text

    return None

# We are getting the whole Element, i.e. the node
def getNodeByName(root_node, node_name):
    if root_node is None:
        raise Exception("No node passed to retrieve node with name {} ".format(node_name))
    for elt in root_node:
        if node_name in elt.tag:
            return elt

    return None

def getNodeByID(metadat_section,ID):
    if metadat_section is None:
        raise Exception("No section passed to retrieve node with ID {} ".format(ID))
    for elt in metadat_section:
        if ID == elt.get('ID'):
            return elt

    return None


def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(524288), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


# # EOF Metadata attributes extraction
def _extract_EOF_from_product(file_path):
    if '.zip' in file_path:
        filename_zip = os.path.basename(file_path)
        eof_filename = filename_zip.split('.zip')[0]
        _unzip_file(file_path)
    else:
        print("EOF file not compressed ")
        # File not compressed, take as it is
        eof_filename = file_path
    return eof_filename


def _get_EOF_file_attributes(eof_file_path):
    # TODO: Check if xml file is reachable for parse command
    tree = ET.parse(eof_file_path)
    fixed_header = tree.getroot()[0][0]
    source_node = getNodeByName(fixed_header, 'Source')
    validity_period = getNodeByName(fixed_header, 'Validity_Period')
    attributes = {
        "productType": getValueByName(fixed_header, 'File_Type'),
        "platformShortName": getValueByName(fixed_header, 'Mission'),
        "platformSerialIdentifier": getValueByName(fixed_header, 'Mission'),
        "processingDate": getValueByName(source_node, 'Creation_Date').split('UTC=')[1],
        "beginningDateTime": getValueByName(validity_period, 'Validity_Start').split('UTC=')[1],
        "endingDateTime": getValueByName(validity_period, 'Validity_Stop').split('UTC=')[1],
        "processingCenter": getValueByName(source_node, 'System'),
        "processorName": getValueByName(source_node, 'Creator'),
        "processorVersion": getValueByName(source_node, 'Creator_Version')
    }
    return attributes


def _EOF_get_attributes(file_path):
    eof_filename = _extract_EOF_from_product(file_path)
    attributes = _get_EOF_file_attributes(eof_filename)
    if '.zip' in file_path:
        # EOF products compressed are composed of only the EOF file
        os.remove(eof_filename)
    return attributes


def _is_compressed(aux_filename):
    return '.zip' in aux_filename or '.TGZ' in aux_filename


def _get_product_path_components(file_path):
    filename_zip = os.path.basename(file_path)
    # TODO: modifiy in order to handle also non cmopressed files!
    if '.zip' in filename_zip:
        filename = filename_zip.split('.zip')[0]
    elif '.TGZ' in filename_zip:
        filename = filename_zip.split('.TGZ')[0]
    else:
        filename = filename_zip
    try:
        extension = filename[filename.index('.') + 1:]
    except:
        extension = None
    #filename_parts = filename.split('.', 1)[-1]
    #extension = filename_parts[1] if len(filename_parts) else None

    return filename_zip, filename, extension


S1_MPL_types = ['REP__MACP_', 'REP__MCSF_', 'REP__SMPR_',
                'TLM__REQ_A', 'TLM__REQ_B', 'TLM__REQ_C',
                'TLM__REQ_D', 'TLM__REQ_E', 'TLM__REQ_F']


def _get_S1_file_attributes(file_path):

    filename_zip, filename, extension = _get_product_path_components(file_path)
    print("Extracting metadata attributes for ", filename_zip)

    try:
        # ==========================================================================================
        #                      S1 .SAFE FILES
        # ==========================================================================================
        if extension is not None and extension == 'SAFE':
            # manifest_file = _get_zip_manifest(file_path)
            xml_file = _get_S1_SAFE_manifest(file_path, filename, filename_zip)

            attributes = _get_S1_SAFE_attributes(xml_file)
            os.remove(xml_file)
        else:
            product_type = filename[9:19]
            print("Extracting Attributes for Product Type: ", product_type)
            if product_type in S1_MPL_types:
                print("Extracting attributes from MPL HDR file inside compress tar")
                attributes = _HDR_get_attributes(file_path, filename, product_type)
            elif product_type in ['MPL_MANPRE']:
                print("Extracting attributes for MANeuver file")
                #  product is compressed prod_filename ;
                #  uncompressed file is removed in function
                attributes = _get_MANPRE_file_attributes(file_path,
                                                         'Sentinel-1',
                                                         product_type)
            elif product_type in ['REP_MP_MP_']:
                print("Extracting attributes for Mission Plan Report file")
                #  product is compressed prod_filename ;
                #  uncompressed file is removed in function
                attributes = _get_MP_REP_file_attributes(file_path,
                                                         'Sentinel-1',
                                                         product_type)

            # ==========================================================================================
            #                      S1 .EOF FILES
            # ==========================================================================================
            else:
                xml_file = filename
                _uncompress(file_path)
                attributes = _get_EOF_file_attributes(xml_file)
                os.remove(xml_file)
        # with open(os.path.join(filename_zip + ".json"), 'w') as json_file:
        #     json.dump(attributes, json_file)
        # TOOD: CHECK: not valid for MANPRE (no XML, no pruct folder to remove)
        shutil.rmtree(filename, ignore_errors=True)
    except Exception as ex:
        print("Failure extracting attributes: ", ex)
        raise ex
    return attributes


def _get_S1_SAFE_attributes( xml_file):
    """
     Extract attributes from SAFE manifest XML file
     xml_file: path to the xml file to be parsed

    """
    tree = ET.parse(xml_file)
    root = tree.getroot()
    metadataSection = getNodeByName(root, 'metadataSection')
    print("Checking if Metadata are present in manifest file")
    if metadataSection is None:
        raise Exception("Metadata Section missing in SAFE manifest file: could not extract product attributes")
    processing_node = getNodeByID(metadataSection, 'processing')
    platform_node = getNodeByID(metadataSection, 'platform')
    generalProductInformation = getNodeByID(metadataSection, 'generalProductInformation')
    if generalProductInformation is None:  # for AUX_PP1,AUX_PP2,AUX_CAL,AUX_INS
        # print("Getting Standalone  Product Information node ")
        generalProductInformation = getNodeByID(metadataSection, 'standAloneProductInformation')
    processing_metadata_container = getNodeByName(getNodeByName(processing_node, 'metadataWrap'), 'xmlData')
    processing_metadata = processing_metadata_container[0][0]
    print("Identified main nodes; reading attributes")
    generalProductInformation = getNodeByName(getNodeByName(generalProductInformation, 'metadataWrap'), 'xmlData')
    platform_metadata = getNodeByName(getNodeByName(platform_node, 'metadataWrap'),
                                      'xmlData') if platform_node is not None else None
    # print("Getting Begin validity from General Product Information")
    beginningDateTime = getValueByName(generalProductInformation[0], 'validity')
    product_type = getValueByName(generalProductInformation[0], 'auxProductType')
    instrumentConfigurationId = getValueByName(generalProductInformation[0], 'instrumentConfigurationId')
    if product_type in ['AUX_ICE', 'AUX_WAV', 'AUX_WND']:
        start_dt = datetime.datetime.strptime(beginningDateTime, "%Y-%m-%dT%H:%M:%S.%f")
        stop_dt = start_dt + datetime.timedelta(days=1)
        endingDateTime = datetime.datetime.strftime(stop_dt, odata_datetime_format)
    else:
        endingDateTime = "2100-01-01T00:00:00"
    attributes = {
        "productType": product_type,
        "processingDate": processing_metadata_container[0].get('start'),
        "beginningDateTime": beginningDateTime,
        "endingDateTime": endingDateTime,
        "processingCenter": processing_metadata.get('site'),
        'InstrumentConfigurationID': instrumentConfigurationId
    }
    # try to get processorName / processorVersion
    # these attributes are missing in some .SAFE files ( may be are missing in all of them )
    try:
        processorName = getNodeByName(processing_metadata, 'software').get('name')
        processorVersion = getNodeByName(processing_metadata, 'software').get('version')

        attributes["processorName"] = processorName
        # BUG: FIXED : processorName was assigned to attribute processorVersion!
        attributes["processorVersion"] = processorVersion

    except Exception as e:
        pass
    if platform_metadata is not None:
        attributes.update({
            "platformShortName": getValueByName(platform_metadata[0], 'familyName'),
            "platformSerialIdentifier": getValueByName(platform_metadata[0], 'number'),
        })
    return attributes


def _get_S1_SAFE_manifest(file_path, filename, filename_zip):
    # the function is not considering TGZ files
    xml_file = "%s/manifest.safe" % filename
    unzip_command = "unzip -qq %s %s" % (file_path, xml_file)
    if '.TGZ' in filename_zip:
        unzip_command = "tar xzf %s %s" % (file_path, xml_file)
    try:
        os.system(unzip_command)
    except Exception as e:
        print(e)
    return xml_file

def _get_S3_SAFE_manifest(file_path, filename, filename_zip):
    manifest_file = "%s/xfdumanifest.xml" % filename
    unzip_command = "unzip %s %s" % (file_path, manifest_file)
    os.system(unzip_command)
    return manifest_file

HDR_FOLDER_PRODUCT_TYPES = ['AUX_ECMWFD', 'AUX_UT1UTC']
def _extract_hdr_from_product(file_path, filename, product_type):
    print("Extracting HDR File from product file ")

    # extract to separate function (hdr_file, product_type, filename)
    # PARSE extracted uncompressed file (XML File)
    # UNCOMPRESS HDR file (Tar gzip)
    hdr_filename = "%s.HDR" % filename
    # Not specifying 'z' in the options automatically un-tars
    #   even if the file is not compressed
    # tar_options = "xzf"
    tar_options = "xf"
    # SOME TYPES could have the files under a folder with the product name
    if product_type in HDR_FOLDER_PRODUCT_TYPES:
        print("Trying if Product File is a compressed Tar without a folder")
        tar_process = subprocess.run(["tar", tar_options, file_path, hdr_filename])
        if tar_process.returncode != 0:
            # TODO: Check hdr_file is not used!!
            print("Product File is a compressed Tar with a folder")
            hdr_filename = "%s/%s % (filename, hdr_filename)"
            tar_process = subprocess.run(["tar", tar_options, file_path, hdr_filename])
            if tar_process.returncode != 0:
                raise Exception("Impossible to get the HDR file in the file " + filename)
    else:
        print("Product File is a compressed Tar without a folder")
        tar_handler = tarfile.open(file_path)
        for taritem in tar_handler.getnames():
            if taritem.endswith('HDR'):
                tar_handler.extract(taritem, ".")
                hdr_filename = taritem
        # NOTE: Missing handling of HDR File missing in TAR
        # tar_command = "tar %s %s %s" % (tar_options, file_path, hdr_filename)
        # os.system(tar_command)
    return hdr_filename
    
def _get_MANPRE_file_attributes(manpre_file, mission, product_type):
    """

    """
    # Filename contains: generation time, end of validity
    prod_filename = _uncompress(manpre_file)
    # The platform identifier is the first character after the mission
    short_mission = prod_filename[:2]
    platform = prod_filename[3]
    # Extract attributes reading product file as a CSV
    with open(prod_filename, "r") as ifile:
        report_reader = csv.reader(ifile, delimiter=' ')
        # Skip file header
        header = next(report_reader)
        first_row = next(report_reader)
        generation_time = first_row[0]
        # Skip Optimisation Row
        next(report_reader)
        # SKip maneuvers header
        man_header = next(report_reader)
        first_man = True
        for row in report_reader:
            if first_man:
                first_man_row = row
                first_man = False
            last_row = row
        fist_man_time = first_man_row[0]
        last_man_time = last_row[0]

    # get generation time, /end validity from filename
    attributes = {
        "productType": product_type,
        "platformShortName": mission,
        "platformSerialIdentifier": platform,
        "processingDate": generation_time,
        "beginningDateTime": fist_man_time,
        "endingDateTime": last_man_time,
        "processingCenter": f'{short_mission}MPL',
    }
    os.remove(prod_filename)
    return attributes

def _get_MP_REP_file_attributes(rep_file, mission, product_type):
    """

    """
    # Filename contains: generation time, end of validity
    prod_filename = _uncompress(rep_file)
    # The platform identifier is the first character after the mission
    short_mission = prod_filename[:2]
    platform = prod_filename[3]
    # Extract attributes
    tree = ET.parse(prod_filename)
    root = tree.getroot()
    report_node = root
    # get generation time, /end validity from filename
    attributes = {
        "productType": product_type,
        "platformShortName": mission,
        "platformSerialIdentifier": platform,
        "processingDate": getValueByName(report_node, 'ReportingTime'),
        "beginningDateTime": getValueByName(report_node, 'ValidityStart'),
        "endingDateTime": getValueByName(report_node, 'ValidityStop'),
        "processingCenter": f'{short_mission}MPL',
    }
    os.remove(prod_filename)
    return attributes

S2_BAND_AUX_TYPES = ['GIP_VIEDIR', 'GIP_R2EQOG',
                     'GIP_R2DEFI', 'GIP_R2WAFI',
                     'GIP_R2L2NC', 'GIP_R2DENT',
                     'GIP_R2DECT', 'GIP_R2EOB2']
def _get_hdr_file_attributes(hdr_file):
    print("Extracting attributes from HDR file: ", hdr_file)
    tree = ET.parse(hdr_file)
    root = tree.getroot()
    if root.tag == 'Earth_Explorer_File':  # pug in S2 Files
        root = root[0]
    product_type = getValueByName(root[0], 'File_Type')
    if product_type in S2_BAND_AUX_TYPES:
        # add band to product_type
        band = hdr_file.split('_')[-1].split('.')[0]
        product_type = product_type + '_' + band
    source_node = getNodeByName(root[0], 'Source')
    validity_period = getNodeByName(root[0], 'Validity_Period')
    attributes = {
        "productType": product_type,
        "platformShortName": getValueByName(root[0], 'Mission'),
        "platformSerialIdentifier": getValueByName(root[0], 'Mission'),
        "processingDate": getValueByName(source_node, 'Creation_Date').split('UTC=')[1],
        "beginningDateTime": getValueByName(validity_period, 'Validity_Start').split('UTC=')[1],
        "endingDateTime": getValueByName(validity_period, 'Validity_Stop').split('UTC=')[1],
        "processingCenter": getValueByName(source_node, 'System'),
        "processorName": getValueByName(source_node, 'Creator'),
        "processorVersion": getValueByName(source_node, 'Creator_Version')
    }
    return attributes


def _HDR_get_attributes(file_path, product_name, prod_type):
    print("Extracting attributes from product with HDR file")
    try:
        hdr_file = _extract_hdr_from_product(file_path,
                                             product_name,
                                             prod_type)
    except Exception as ex:
        print("Error extracting Attributs from HDR:", ex)
    attributes = _get_hdr_file_attributes(hdr_file)
    os.remove(hdr_file)
    shutil.rmtree(product_name, ignore_errors=True)
    return attributes


def _unzip_file(file_path):
    unzip_command = "unzip %s" % file_path
    # print("Zip command: ", unzip_command)
    try:
        os.system(unzip_command)
    except Exception as e:
        print(e)


def _uncompress(compressed_filepath):
    if '.zip' in compressed_filepath:
        filename_zip = os.path.basename(compressed_filepath)
        uncompressed_filename = filename_zip.split('.zip')[0]
        _unzip_file(compressed_filepath)
    else:
        raise Exception(f"{compressed_filepath} not a ZIP File")
    return uncompressed_filename


def _get_S2_file_attributes(file_path):
    # PARSE extracted uncompressed file (XML File)
    filename_zip, filename, extension = _get_product_path_components(file_path)
    product_type = filename[9:19]
    print("Getting attributes for file of type ", product_type)
    if product_type in ['MPL_ORBRES', 'MPL_ORBPRE', 'REP__SUP__']:
        print("Extracting attributes for EOF file")
        #
        attributes = _EOF_get_attributes(file_path)
    elif product_type in ['MPL_MANPRE']:
        print("Extracting attributes for MANeuver file")
        attributes = _get_MANPRE_file_attributes(file_path, 'Sentinel-2', product_type)
    else:
        attributes = _HDR_get_attributes(file_path, filename, product_type)
    # with open(os.path.join(filename_zip + ".json"), 'w') as json_file:
    #     json.dump(attributes, json_file)
    return attributes


def _get_S3_SAFE_file_attributes(manifest_file):
    # TODO: Put Parsing in a general SAFE_Maniferst Parser module
    tree = ET.parse(manifest_file)
    root = tree.getroot()
    metadataSection = getNodeByName(root, 'metadataSection')
    processing = getNodeByID(metadataSection, 'processing')
    generalProductInformation = getNodeByID(metadataSection, 'generalProductInformation')
    processing = getNodeByName(getNodeByName(processing, 'metadataWrap'), 'xmlData')[0]
    generalProductInformation = getNodeByName(getNodeByName(generalProductInformation, 'metadataWrap'), 'xmlData')[0]
    facility = getNodeByName(processing, 'facility')
    attributes = {
        "productType": getValueByName(generalProductInformation, 'fileType'),
        "timeliness": getValueByName(generalProductInformation, 'timeliness'),
        "platformShortName": getValueByName(generalProductInformation, 'familyName'),
        "platformSerialIdentifier": getValueByName(generalProductInformation, 'number'),
        "processingDate": getValueByName(generalProductInformation, 'creationTime'),
        "beginningDateTime": getValueByName(generalProductInformation, 'validityStartTime'),
        "endingDateTime": getValueByName(generalProductInformation, 'validityStopTime'),
        "processingCenter": facility.get('site'),
        "processorName": getNodeByName(facility, 'software').get('name'),
        "processorVersion": getNodeByName(facility, 'software').get('version')
    }
    return attributes

def _get_S3_file_attributes(file_path):
    filename_zip, filename, extension = _get_product_path_components(file_path)
    if extension != 'EOF':
        manifest_file = _get_S3_SAFE_manifest(file_path, filename, extension)
        attributes = _get_S3_SAFE_file_attributes(manifest_file)
        shutil.rmtree(filename, ignore_errors=True)
    else:
        attributes = _EOF_get_attributes(file_path)

    # with open(os.path.join(filename_zip + ".json"), 'w') as json_file:
    #     json.dump(attributes, json_file)
    return attributes



mission_attributes_funcs = {
    'S1': _get_S1_file_attributes,
    'S2': _get_S2_file_attributes,
    'S3': _get_S3_file_attributes
}

def get_attributes(path_to_aux_data_file):

    try:
        file_path = path_to_aux_data_file
        filename_zip = os.path.basename(path_to_aux_data_file)
        satellite = filename_zip[:2]
        # compute the md5 checksum
        checksum = md5(file_path)

        #_retrieve_attributes_fun = mission_attributes_funcs.get(satellite, None)
        #if _retrieve_attributes_fun is not None:
        #    attributes = mission_attributes_funcs(file_path)

        if satellite == 'S1':
            # ======================================================================
            #                      S1  FILES
            # ======================================================================
            attributes = _get_S1_file_attributes(file_path)
        elif satellite == 'S2':
            # ======================================================================
            #                      S2  FILES
            # ======================================================================
            attributes = _get_S2_file_attributes(file_path)
        else: # S3
            # ======================================================================
            #                      S3 FILES
            # ======================================================================
            attributes = _get_S3_file_attributes(file_path)

    except Exception as e:
        print( e )
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        attributes = None
        # shutil.rmtree(filename, ignore_errors=True)
    if attributes is not None:
        attributes.update({
            "md5": checksum,
            "length": os.path.getsize(file_path)
        })

    return attributes
