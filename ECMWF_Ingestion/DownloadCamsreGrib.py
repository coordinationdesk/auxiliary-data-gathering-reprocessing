import cdsapi
import datetime, threading, time, os

# TODO: Use a class, with specialization for CAMSAN/CAMSRE
# TODO: Separate between Reuest generation (and data retrieval)
#  And manageing workflow of downloads (if only one thread required, do not launch threads!)
#    so to be different if for recovery of big gaps, or operationsl execution)
def downloadCamsreGribForSmallPeriod(start, stop, outputFilePathName,
                                                cams_url, api_key, api_user):
   # full_key = "{0}:{1}".format(api_user, api_key)
   full_key = api_key
   cdsclient = cdsapi.Client(url=cams_url, key=full_key, debug=True)

   dataset =  'cams-global-reanalysis-eac4'
   request_dict = {
          'format': 'grib',
          'variable': [
              'black_carbon_aerosol_optical_depth_550nm',
              'dust_aerosol_optical_depth_550nm',
              'organic_matter_aerosol_optical_depth_550nm',
              'sea_salt_aerosol_optical_depth_550nm',
              'sulphate_aerosol_optical_depth_550nm',
              'surface_geopotential',
              'total_aerosol_optical_depth_1240nm',
              'total_aerosol_optical_depth_469nm',
              'total_aerosol_optical_depth_550nm',
              'total_aerosol_optical_depth_670nm',
              'total_aerosol_optical_depth_865nm',
          ],
          'date': start.strftime('%Y-%m-%d')+'/'+stop.strftime('%Y-%m-%d'),
          'time': [
              '00:00', '03:00', '06:00',
              '09:00', '12:00', '15:00',
              '18:00', '21:00',
          ],
      }
   # TODO Catch exception for data not found
   # cdsinf.exceptions.BadRequestException
   # message/reason: There is no data matching your request.
   try:
       cdsclient.retrieve(dataset, request_dict, outputFilePathName).download()
   except cdsinf.exceptions.BadRequestException as reqEx:
       print("Error retrieving data from ECMWF (Data not found): ", reqEx)
       raise reqEx
   except Exception as ex:
       raise ex


def determine_parallel_periods(startDate, stopDate):
    #
    # Preparing the launch of parallel downloads by dividing the whole period
    # into smaller ones in order to launch smaller requests
    #
    daysBetweenStartAndStop = (stopDate - startDate).days
    periods = {}
    periodDivider = 30
    for period in range(int(daysBetweenStartAndStop / periodDivider)):
        periodStart = startDate + datetime.timedelta(days = period * periodDivider)
        periodStop = periodStart + datetime.timedelta(days = periodDivider - 1)
        periods[periodStart] = periodStop

    lastPeriodStart = startDate + datetime.timedelta(days = len(periods) * periodDivider)
    lastPeriodStop = stopDate
    periods[lastPeriodStart] = lastPeriodStop

    return periods

def downloadCamsreGribInParallel(parallel_periods,
                                 outputFileDir, rawGribNamePattern,
                                 cams_url,
                                 api_key, api_user):
    # Multiple threads only if multiple periods!!
    nbMaxThreads = 6
    generatedGribId = 0
    threadsToWait = []

    #
    # Launching downloads in parallel
    #
    for (periodStart, periodStop) in parallel_periods.items():
        generatedGribId += 1
        gribName = rawGribNamePattern % str(generatedGribId)
        outputFileNamePath = os.path.join(outputFileDir, gribName)
        downloadThread = threading.Thread(target=downloadCamsreGribForSmallPeriod,
                                          args=(periodStart, periodStop, outputFileNamePath,
                                                cams_url, api_key, api_user))
        threadsToWait.append(downloadThread)
        while threading.active_count() > nbMaxThreads:
            time.sleep(5)
        downloadThread.start()
        
    # Wait for all threads to end before returning
    for thread in threadsToWait:
        thread.join()

def download_Cams_reGrib(startDate, stopDate,
                         outputFileDir, rawGribNamePattern,
                         cams_url,
                         api_key, api_user,):
    parallel_periods = determine_parallel_periods(startDate, stopDate)
    if len(parallel_periods) > 1:
        downloadCamsreGribInParallel(parallel_periods,
                                     outputFileDir, rawGribNamePattern,
                                     cams_url,
                                     api_key, api_user)
    else:
        gribName = rawGribNamePattern % str(0)
        outputFileNamePath = os.path.join(outputFileDir, gribName)
        downloadCamsreGribForSmallPeriod(startDate, stopDate, outputFileNamePath,
                                                cams_url, api_key, api_user)
