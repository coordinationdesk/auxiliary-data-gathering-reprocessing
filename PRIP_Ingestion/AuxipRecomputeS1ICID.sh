#source InitFuncs.sh
# Function receives: Day of work, temp folder,
# AuxType
#  From environment variables:
# Auxip credentials, Archive credentials,
function recompute_day_ICID() {
  # Expecting argument for MISSION to be ingested
  #  From/TO date arguments (with option included) are defined
  #   using global variables
  if [[ $# != 4 ]] ; then
      echo "ingest_from_file function arguments: TEMP_FOLDER MISSION AUX_TYPE DAY "
      echo "Received: $@"
      exit 1
  fi
  TEMP_ROOT=$1
  MISSION=$2
  AUX_TYPE=$3
  DAY=$4
  # Change format of DAY from YYYY-MM-DD to YYYY/MM/DD
  MISSION_TEMP_ROOT=${TEMP_ROOT}/$AUX_TYPE/$DAY
  MISSION_TEMP_FOLDER=${MISSION_TEMP_ROOT}/DOWNLOAD
  MISSION_TEMP_FOLDER_LOGS=${MISSION_TEMP_ROOT}/LOGS
  create_folder $MISSION_TEMP_FOLDER
  create_folder $MISSION_TEMP_FOLDER_LOGS
    echo "Starting ICID update for Aux Type $AUX_TYPE from DAY $DAY"
  # Create Interval Arguments
  # Or change to receive both start and STOP
  # Day Interval Length to be computed in caller 
FROM_DATE_ARG=""
TO_DATE_ARG=""
if [[ ! -z ${DAY} ]]; then
  # IF a REFERENCE DATE WAS SPECIFIED, ingest 1 DAY of data
  FROM_DATE_ARG="-from ${DAY}"
      TO_DATE=$(date -d "$DAY +1 days" +${DATE_FORMAT} )
  echo " TO DATE: $TO_DATE"
  TO_DATE_ARG="-to ${TO_DATE}"
fi

    python3 -u ${CUR_DIR}/ingestion/auxip_update_archived.py -mi $MISSION -t ${AUX_TYPE} -w ${MISSION_TEMP_FOLDER} -au ${AUXIP_USER} -apw ${AUXIP_PASS} -mc ${MCPATH} -b ${STORAGE_ALIAS}/${S3_BUCKET} -m ${MODE} -e ${MISSION_TEMP_FOLDER_LOGS}/failed_list.txt ${FROM_DATE_ARG} ${TO_DATE_ARG} -dbh ${AUXIP_POSTGRES_HOST} -dbn ${AUXIP_POSTGRES_DB}  -dbu ${AUXIP_POSTGRES_USER}  -dbp $AUXIP_POSTGRES_PASSWORD -p ${DB_PORT} 
    code=$?
    master_code_auxip=$code
    if [ $code -ne 0 ]; then
       echo "ICID update failed for Mission ${MISSION} and type ${AUX_TYPE} with error $code" 
       echo "ICID update ingestion failed for Mission ${MISSION} and type ${AUX_TYPE} with error $code" >> ${ERROR_FILE_LOG}
    fi
    if [ $master_code_auxip -ne 0 ]; then
       echo "ICID update failed"
       echo "ICID update for mission ${MISSION} and type ${AUX_TYPE} failed" >> ${ERROR_FILE_LOG}
    fi
    master_code=$master_code_auxip
  echo "Removing daily temporary folders"
  if [ $master_code -eq 0 ]; then
      echo "No errors for $MISSION $AUX_TYPE ingestion"
      echo "Removing temporary folders"
      echo "Removing TEMP Folder ${MISSION_TEMP_FOLDER:?}"
      rm -rf "${MISSION_TEMP_FOLDER:?}"/
      REM_RES=$?
      echo "Removal result: $REM_RES"
      #echo "Removing TEMP LISTING Folder ${MISSION_TEMP_FOLDER_LOGS:?}"
      #rm -rf ${MISSION_TEMP_FOLDER_LOGS:?}/
      #REM_RES=$?
      echo "Removal result: $REM_RES"

    else
      echo "Ingestion failure - Keeping Temporary files "
    fi
    echo "[END] Completed ICID UPdate of Mission ${MISSION} $AUX_TYPE"
    echo "[END] Completed ICID Update of Mission ${MISSION} $AUX_TYPE" >> ${ERROR_FILE_LOG}
  ingestion_code=$?
  return $master_code
}
function update_products_mission_date_interval() {
# Arugments: $TEMP_FOLDER $MISSION $AUX_TYPE BATCH_START_DAY NDAYS
# Check number of arguments
if [ $# != 5 ]; then
  echo "Batch main function received $# arguments instead of 5"
  exit 1
fi
local DWL_TEMP_FOLDER=$1
local MISSION=$2
local AUX_TYPE=$3
   local CURR_DATE=$4
   local NLOOPS=$5
# Loop: set CURR_DATE = START_DATE

   #EXECUTION DATE
   EXEC_DATE=$(date '+%Y-%m-%d')

   # MOVE Folders creation inside ingest mission, to be done for each BATCH
   init_folders $EXEC_DATE

   echo "Mission $MISSION: Executing $NLOOPS one day ingestions from date $CURR_DATE"
   # Loop N times 
    for in in $(seq $NLOOPS); do 
        echo "Starting updating products of Aux TYpe $AUX_TYPE for date $CURR_DATE"
        recompute_day_ICID $WORK_FOLDER $MISSION $AUX_TYPE $CURR_DATE 
# INCREMENT curr_date
        CURR_DATE=$(date -d "${CURR_DATE} +1 days" +${DATE_FORMAT})
    done

ingestion_code=0
# Remove temporary folders if ALL missions have been successful
#  if [ $ingestion_code -eq 0 ]; then
#    echo "No Errors Found"
#    echo "Removing TEMP Folder ${TEMP_FOLDER:?}"
#    rm -rf "${TEMP_FOLDER:?}"/
#    echo "Removing TEMP LISTING Folder ${TEMP_FOLDER_LISTING:?}"
#    rm -rf ${TEMP_FOLDER_LISTING:?}/
#    echo "Removing TEMP Reprobase JSON Folder ${TEMP_FOLDER_JSONS:?}"
#    rm -rf ${TEMP_FOLDER_JSONS:?}/
#  else
#     echo "Errors found during ingestion - Keeping temporary folders"
#  fi

echo "Done"

# Removing the error log if the number of lines equals 3 : one line per tmp directories created at the beginning
if [ "$( wc -l < ${ERROR_FILE_LOG} )" -eq 3 ]; then
  echo "No errors during ingestion : deleting error file"
  rm $ERROR_FILE_LOG
fi
} 
