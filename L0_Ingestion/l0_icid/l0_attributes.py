# coding=utf-8
import datetime
import hashlib
import os
import shutil
import sys

import xml.etree.ElementTree as ET
from time_formats import odata_datetime_format

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



def _get_S1_file_attributes(file_path):

    filename_zip, filename, extension = _get_product_path_components(file_path)
    print("Extracting metadata attributes for S1 product ", filename_zip)
    attributes = None
    try:
        # ==========================================================================================
        #                      S1 .SAFE FILES
        # ==========================================================================================
        if extension is not None and extension == 'SAFE':
            # manifest_file = _get_zip_manifest(file_path)
            try:
                xml_file = _get_S1_SAFE_manifest(file_path, filename, filename_zip)

                attributes = _get_S1_SAFE_attributes(xml_file)
                os.remove(xml_file)
            except Exception as ex:
                print("Failed to read Metadata file from ", file_path)
        else:
            product_type = filename[9:19]
            print("Extracting Attributes for Product Type: ", product_type)

            # ==========================================================================================
            #                      S1 .EOF FILES
            # ==========================================================================================
            xml_file = filename
            _uncompress(file_path)
            attributes = _get_EOF_file_attributes(xml_file)
            os.remove(xml_file)
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
    instrumentConfigurationId = getValueByName(generalProductInformation[0], 'instrumentConfigurationID')
    #print("ICID: ", instrumentConfigurationId)
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








def get_S1_L0_attributes(l0_file_path):
    # Do not extract Checksum, we need only Product metadata
    filename_zip = os.path.basename(l0_file_path)
    satellite = filename_zip[:2]
    try:
        if satellite == 'S1':
            # ======================================================================
            #                      S1  FILES
            # ======================================================================
            attributes = _get_S1_file_attributes(l0_file_path)
        else:
            attributes = None
    except Exception as e:
        print( e )
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        attributes = None
        # shutil.rmtree(filename, ignore_errors=True)

    return attributes

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
