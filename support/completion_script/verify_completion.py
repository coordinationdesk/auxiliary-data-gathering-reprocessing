import argparse
import datetime

import requests
from pip._vendor.requests import auth

odata_datetime_format = "%Y-%m-%dT%H:%M:%SZ[GMT]"
odata_datetime_nosec_format = "%Y-%m-%dT%H:%MZ[GMT]"
url = "https://reprocessing-auxiliary.copernicus.eu/reprocessing.svc/AuxFiles"
test_dur=True
test_miss=False

def send_request(request, token):
    print("Request Sent : " + request)
    headers = {'Content-type': 'application/json','Authorization' : 'Bearer %s' % token}
    resp = requests.get(request, headers=headers)
    if resp.status_code != 200:
        raise Exception("Bad return code for request: "+request)
    res = resp.json()
    resp.close()
    return res


def main():
    parser = argparse.ArgumentParser(description="",  # main description for help
            epilog='Beta', formatter_class=argparse.RawTextHelpFormatter)  # displayed after help
    parser.add_argument("-s", "--step",
                        help="step of the search in hours",
                        required=True)
    parser.add_argument("-t", "--type",
                        help="type to search",
                        required=True)
    parser.add_argument("-tk", "--token",
                        help="token to access API",
                        required=True)
    parser.add_argument("-m", "--mission",
                        help="Satellite trigram",
                        required=True)
    parser.add_argument("-o", "--output",
                        help="Output data directory (report file): ex report.txt'",
                        required=True)
    parser.add_argument("-ss", "--sensitivity",
                        help="Sensitivity of the test for gaps and overlaps : a gap/overlap will not be considered one if it is shorter than the sensitivity. Sensitivity format : dd-HH-MM-SS",
                        required=False)

    args = parser.parse_args()

    if args.sensitivity is None:
        args.sensitivity = "00-00-00-01"

    parsed_sensitivity=args.sensitivity.split('-')
    gap_sensitivity = datetime.timedelta(days=int(parsed_sensitivity[0]), hours=int(parsed_sensitivity[1]), minutes=int(parsed_sensitivity[2]), seconds=int(parsed_sensitivity[3]))

    with open(args.output, mode='w') as report:
        report.write("##### Report start : type : " + args.type + " , step :  " + args.step + " hours ########\n")
        request = url + "?$orderby=ValidityStart,ValidityStop asc&$filter=contains(FullName,'"+args.type+"') and startswith(FullName,'"+args.mission+"')"
        if "ECMWFD" in args.type:
            request += " and contains(FullName,'ADG')"
        result = send_request(request, args.token)
        print("Request returned result: ", result)
        working_list = []
        report.write("Number of found files : "+str(len(result['value']))+"\n")
        if len(result['value']) == 0 :
            report.write("ERROR : no file found !!!!!\n")
            report.write("##### Report end ########\n")
            return
        # For each file, build a time interval from the file start, long Step hours. 
        # associate to the file
        for f in result['value']:
            start_date_str = f['ValidityStart']
            stop_date_str = f['ValidityStart']
            # TODO: use function to parse time string
            startDateFormat = ""
            stopDateFormat = ""
            if len(start_date_str) == 22:
                startDateFormat = odata_datetime_nosec_format
            else:
                startDateFormat = odata_datetime_format

            if len(stop_date_str) == 22:
                stopDateFormat = odata_datetime_nosec_format
            else:
                stopDateFormat = odata_datetime_format

            start_dt = datetime.datetime.strptime(start_date_str, startDateFormat)
            stop_dt = datetime.datetime.strptime(stop_date_str, stopDateFormat)
            # Stop = ValidityStart + Step
            stop_dt += datetime.timedelta(hours = int(args.step))

            working_list.append((start_dt, stop_dt, f))

        start_date_str = result['value'][0]['ValidityStart']
        stop_date_str = result['value'][-1]['ValidityStart']
        if len(start_date_str) == 22:
            startDateFormat = odata_datetime_nosec_format
        else:
            startDateFormat = odata_datetime_format

        if len(stop_date_str) == 22:
            stopDateFormat = odata_datetime_nosec_format
        else:
            stopDateFormat = odata_datetime_format

        start_dt = datetime.datetime.strptime(start_date_str, startDateFormat)
        stop_dt = datetime.datetime.strptime(stop_date_str, stopDateFormat)
        # Stop = ValidityStart + Step
        stop_dt += datetime.timedelta(hours = int(args.step))

        report.write("Start date : "+start_dt.strftime(startDateFormat)+"\n")
        report.write("Stop date : " +stop_dt.strftime(stopDateFormat) +"\n")
        work_dt = start_dt
        found = 0
        idx = 0
        if test_miss:
            report.write("#### Testing steps start ####\n")
            #test if there is only one file for a given date using the step
            while work_dt < stop_dt:
                idx = idx - found
                found = 0
                found_list = []
                while idx < len(working_list):
                    #The file validity is valid for the tested date
                    # If file start <= current Analzed time < file stop (current analyzed time is no more than STEP hours after file validity start)
                    if working_list[idx][0] <= work_dt and working_list[idx][1] > work_dt:
                        found = found + 1
                        found_list.append(working_list[idx][2]["FullName"]+ " : "+str(working_list[idx][0])+ " / "+str(working_list[idx][1]))
                    #The file is after the tested date, finishing test
                    if working_list[idx][0] > work_dt:
                        if found == 0:
                            report.write("No file found for date :"+datetime.datetime.strftime(work_dt, odata_datetime_format).replace("Z[GMT]","")+"\n")
                        if found > 1:
                            report.write("More than one file found for date :"+datetime.datetime.strftime(work_dt, odata_datetime_format).replace("Z[GMT]","")+"\n")
                            for l in found_list:
                                report.write(" - "+l+"\n")
                        break
                    idx = idx + 1
                try:
                    work_dt = work_dt + datetime.timedelta(hours=int(args.step))
                except OverflowError as e:
                    work_dt = stop_dt
            report.write("#### Testing steps stop ####\n")
        if test_dur:
            report.write("#### Testing if file have validity longer than the step duration starts ####\n")
            for f in working_list:
                if f[1] - f[0] > datetime.timedelta(hours=int(args.step)):
                    report.write("Extend more than the step : " + f[2]['FullName'] +" : " +str(f[0])+" / " +str(f[1])+" : "+ str(f[1] - f[0])+"\n")
            report.write("#### Testing that file duration is larger than the step duration stop ####\n")
        report.write("#### Testing overlaps/gaps start ####\n")
        # test if there is only one file for a given date using the step
        idx = 1
        while idx < len(working_list):
            # Test Gap: compare File start with previous file Validity Start
            if len(working_list[idx][2]['ValidityStart']) == 22:
                startDateFormat = odata_datetime_nosec_format
            else:
                startDateFormat = odata_datetime_format

            if len(working_list[idx-1][2]['ValidityStart']) == 22:
                stopDateFormat = odata_datetime_nosec_format
            else:
                stopDateFormat = odata_datetime_format
            # The file validity is valid for the tested date
            # item [1] is the file stop time
            # item [0] is the file start time
            # file with index idx -1 is the file earlier than current file
            if working_list[idx-1][1] > working_list[idx][0] and working_list[idx-1][1] - working_list[idx][0] > gap_sensitivity:
                report.write("overlap: " + working_list[idx-1][2]['FullName'] + " and "+working_list[idx][2]['FullName']+" : "+
                             (working_list[idx-1][1].strftime(stopDateFormat)).replace("Z[GMT]","")+" / "+
                             (working_list[idx][0].strftime(startDateFormat)).replace("Z[GMT]","")+"\n")
            if working_list[idx-1][1] < working_list[idx][0] and working_list[idx][0] - working_list[idx-1][1] > gap_sensitivity:
                report.write("gap: " + working_list[idx-1][2]['FullName'] + " and "+working_list[idx][2]['FullName']+" : "+
                             (working_list[idx-1][1].strftime(stopDateFormat)).replace("Z[GMT]","")+" / "+
                             (working_list[idx][0].strftime(startDateFormat)).replace("Z[GMT]","")+" not covered\n")
            idx = idx + 1
        report.write("#### Testing overlaps/gaps stop ####\n")

        report.write("##### Report end ########\n")




if __name__ == "__main__":
    main()
