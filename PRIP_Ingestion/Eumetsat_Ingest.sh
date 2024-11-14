#!/bin/bash 

source InitFuncs.sh
source IngestDownloaded_funcs.sh


function list_day_aux_files() {
  if [[ $# != 4 ]] ; then
      echo "ingest_from_file function arguments: TEMP_FOLDER MISSION AUX_TYPE DAY "
      echo "Received: $@"
      exit 1
  fi
  TEMP_ROOT=$1
  MISSION=$2
  AUX_TYPE=$3
  DAY=$4
  create_folder ${TEMP_ROOT}/${MISSION}
  python3 -u ${CUR_DIR}/eumetsat_provider/Eumetsat_ingest_products.py  -u ${FTP_USER} -pw ${FTP_PASS} \
        -w ${TEMP_ROOT}/${MISSION} \
        -fh ${FTP_HOST} \
        -sf ${FTP_FOLDER} \
        -d $DAY -l
  code=$?
  if [ $code -ne 0 ]; then
    echo "EUMETSAT list failed"
    echo "EUMETSAT list failed" >> ${ERROR_FILE_LOG}
  fi
}
# TODO: pass FTP Access variables + START_FOLDER
function ingest_day_aux_files() {

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
  MISSION_TEMP_FOLDER_LISTING=${MISSION_TEMP_ROOT}/FILES_LISTING
  MISSION_TEMP_FOLDER_JSONS=${MISSION_TEMP_ROOT}/BASELINE_JSONS
  create_folder $MISSION_TEMP_FOLDER
  create_folder $MISSION_TEMP_FOLDER/${MISSION}
  create_folder $MISSION_TEMP_FOLDER_LISTING
  create_folder $MISSION_TEMP_FOLDER_JSONS
    echo "[BEGIN] Ingesting Mission ${MISSION} , Aux Type : : $AUX_TYPE for day $DAY"
    echo "[BEGIN] Ingesting Mission ${MISSION} , Aux Type : : $AUX_TYPE for day $DAY" >> ${ERROR_FILE_LOG}
  # TODO: python script is not using a TEMP FOLDER!!!
  python3 -u ${CUR_DIR}/eumetsat_provider/Eumetsat_ingest_products.py  -u ${FTP_USER} -pw ${FTP_PASS} \
        -w ${MISSION_TEMP_FOLDER}/${MISSION} \
        -fh ${FTP_HOST} \
        -sf ${FTP_FOLDER} \
        -d $DAY
  code=$?
  if [ $code -ne 0 ]; then
    echo "EUMETSAT Retrieve failed"
    echo "EUMETSAT Retrieve failed" >> ${ERROR_FILE_LOG}
  fi
  ingest_downloaded_files $MISSION $code "$MISSION_TEMP_FOLDER" "${MISSION_TEMP_FOLDER_LISTING}" "${MISSION_TEMP_FOLDER_JSONS}"
  ingestion_code=$?
  master_code=$ingestion_code
  if [ $ingestion_code -eq 0 ]; then
  # AUXIP Ingested Files: Generation of related JSONs to put in ReproBase
   ingest_reprobase $MISSION $ingestion_code "${MISSION_TEMP_FOLDER_LISTING}"  "${MISSION_TEMP_FOLDER_JSONS}"
   code=$?
   master_code_reprobase=$code
    master_code=$master_code_reprobase
  fi
  echo "Removing daily temporary folders"
  if [ $master_code -eq 0 ]; then
      echo "No errors for $MISSION ingestion"
      echo "Removing temporary folders"
      echo "Removing TEMP Folder ${MISSION_TEMP_FOLDER:?}"
      rm -rf "${MISSION_TEMP_FOLDER:?}"/
      REM_RES=$?
      echo "Removal result: $REM_RES"
      echo "Removing TEMP LISTING Folder ${MISSION_TEMP_FOLDER_LISTING:?}"
      rm -rf ${MISSION_TEMP_FOLDER_LISTING:?}/
      REM_RES=$?
      echo "Removal result: $REM_RES"
      echo "Removing TEMP Reprobase JSON Folder ${MISSION_TEMP_FOLDER_JSONS:?}"
      rm -rf ${MISSION_TEMP_FOLDER_JSONS:?}/
      REM_RES=$?
      echo "Removal result: $REM_RES"

    else
      echo "Ingestion failure - Keeping Temporary files "
    fi
    echo "[END] Completed Ingestion of Mission ${MISSION} "
    echo "[END] Completed Ingestion of Mission ${MISSION} " >> ${ERROR_FILE_LOG}
  ingestion_code=$?
  echo "Removing temporary folders"
  return $master_code
}



function list_mission_date_interval() {
#   Input arguments:
#  TEMP_FOLDER MISSION AUX_TYPE FROM_DATE NUM_DAYS 
# Loop: set CURR_DATE = START_DATE

   local WORK_FOLDER=$1
   local MISSION=$2
   local AUX_TYPE=$3
   local CURR_DATE=$4

   #EXECUTION DATE
   EXEC_DATE=$(date '+%Y-%m-%d')

   # MOVE Folders creation inside ingest mission, to be done for each BATCH
   init_folders $EXEC_DATE

   NLOOPS=$5
   echo "Mission $MISSION: Executing $NLOOPS one day ingestions from date $CURR_DATE"
   # Loop N times 
    for in in $(seq $NLOOPS); do 
        echo "Starting list for date $CURR_DATE"
        list_day_aux_files $TEMP_FOLDER $MISSION $AUX_TYPE $CURR_DATE 
# INCREMENT curr_date
        CURR_DATE=$(date -d "${CURR_DATE} +1 days" +${DATE_FORMAT})
    done
}

function ingest_mission_date_interval() {
#   Input arguments:
#  TEMP_FOLDER MISSION AUX_TYPE FROM_DATE NUM_DAYS 
# Loop: set CURR_DATE = START_DATE

   local WORK_FOLDER=$1
   local MISSION=$2
   local AUX_TYPE=$3
   local CURR_DATE=$4

   #EXECUTION DATE
   EXEC_DATE=$(date '+%Y-%m-%d')

   # MOVE Folders creation inside ingest mission, to be done for each BATCH
   init_folders $EXEC_DATE

   NLOOPS=$5
   echo "Mission $MISSION: Executing $NLOOPS one day ingestions from date $CURR_DATE"
   # Loop N times 
    for in in $(seq $NLOOPS); do 
        echo "Starting ingestion for date $CURR_DATE"
        ingest_day_aux_files $TEMP_FOLDER $MISSION $AUX_TYPE $CURR_DATE 
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


