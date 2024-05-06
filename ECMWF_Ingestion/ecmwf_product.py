def create_hdr(cams_header_xml,
               current_date, validity_start, validity_stop,
               hdr_filename,
	       cams_ns,
               xml_time_format):
    #
    # Create HDR file
    #
    valid_start_xml = validity_start.strftime(xml_time_format)
    valid_stop_xml = validity_stop.strftime(xml_time_format)
    crea_time_xml = current_date.strftime(xml_time_format)
    cams_header_xml.find("File_Name", cams_ns).text = hdr_filename
    val_period_element = cams_header_xml.find("Validity_Period", cams_ns)
    val_period_element.find("Validity_Start",cams_ns).text = valid_start_xml
    val_period_element.find("Validity_Stop", cams_ns).text = valid_stop_xml
    cams_header_xml.find("Source", cams_ns).find("Creation_Date", cams_ns).text = valid_stop_xml
    print(cams_header_xml.find("File_Name",cams_ns).text)
    print(val_period_element.find("Validity_Start",cams_ns).text)


