from datetime import datetime

odata_datetime_format = "%Y-%m-%dT%H:%M:%S.%fZ"

def get_odata_datetime_format(datetime_string):

    odata_format = datetime_string
    if datetime_string == "9999-99-99T99:99:99":
        datetime_string = "9999-12-31T23:59:59"

    try:
        datetime.strptime(datetime_string, odata_datetime_format)
    except ValueError:

        # Try these following fomats
        # "%Y%m%dT%H%M%S"  20201013T065032
        try:
            date_time = datetime.strptime(datetime_string, "%Y%m%dT%H%M%S")
            odata_format = datetime.strftime(date_time, odata_datetime_format)
        except ValueError:
            pass

        # 2021-02-23T05:29:16 in S1 .EOF  and S2 files
        try:
            date_time = datetime.strptime(datetime_string, "%Y-%m-%dT%H:%M:%S")
            odata_format = datetime.strftime(date_time, odata_datetime_format)
        except ValueError:
            pass

        # 2024/02/21-21:52:36.767 in MANPRE files
        try:
            date_time = datetime.strptime(datetime_string, "%Y/%m/%d-%H:%M:%S.%f")
            odata_format = datetime.strftime(date_time, odata_datetime_format)
        except ValueError:
            pass

        # 2020-10-06T00:00:00.000000   ( Z is missing )
        try:
            date_time = datetime.strptime(datetime_string, "%Y-%m-%dT%H:%M:%S.%f")
            odata_format = datetime_string + 'Z'
        except ValueError:
            pass

    return odata_format

