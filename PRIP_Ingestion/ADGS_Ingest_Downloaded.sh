#!/bin/bash 

source ${PWD}/InitFuncs.sh
source ${PWD}/IngestDownloaded_funcs.sh

echo "$# Arguments"
if [ $# -lt 3 ]; then
  echo "$0 tmp_dir INPUT_FOLDER MISSION"
  exit 1
fi

# CHECK IF ANOTHER INSTANCE IS RUNNING
# Processes include: containing bash, bash, and grep
if [ `ps ax | grep $0 | wc -l` -gt 3 ]; then  
  echo "$0 Already running"
  echo "ps returned $(ps ax | grep $0 ) items"
  #exit 0
fi

WORK_FOLDER=$1
echo "WORK_FOLDER : "$WORK_FOLDER
INPUT_FOLDER=$2
echo "INPUT_FOLDER : $INPUT_FOLDER"
MISSION=$3
echo "MISSION : $MISSION"


init_adgs_variables
init_variables

create_folder $WORK_FOLDER
#EXECUTION DATE
EXEC_DATE=$(date '+%Y-%m-%d')

# MOVE Folders creation inside ingest mission, to be done for each mission!
init_folders $EXEC_DATE

function ingest_mission() {
  # Expecting argument for MISSION to be ingested
  #  From/TO date arguments (with option included) are defined
  #   using global variables
  if [[ $# != 2 ]] ; then
      echo "Called ingest_mission function without MISSION and INPUT_FOLDER argument"
      exit 1
  fi
  MISSION=$1
  INPUT_FOLDER=$2
  MISSION_TEMP_FOLDER=${TEMP_FOLDER}/$MISSION
  MISSION_TEMP_FOLDER_LISTING=${TEMP_FOLDER_LISTING}/${MISSION}
  MISSION_TEMP_FOLDER_JSONS=${TEMP_FOLDER_JSONS}/${MISSION}
  create_folder $MISSION_TEMP_FOLDER
  create_folder $MISSION_TEMP_FOLDER_LISTING
  create_folder $MISSION_TEMP_FOLDER_JSONS
  code=0
  ingest_downloaded_files $MISSION $code $INPUT_FOLDER "${MISSION_TEMP_FOLDER_LISTING}" 
  #ingest_replace_downloaded_files $MISSION $code $INPUT_FOLDER "${MISSION_TEMP_FOLDER_LISTING}" 
  ingestion_code=$?
  master_code=$ingestion_code
  if [ $master_code -eq 0 ]; then
      echo "No errors for $MISSION ingestion"
  echo "Removing temporary folders"
    echo "Removing TEMP Folder ${MISSION_TEMP_FOLDER:?}"
    rm -rf "${MISSION_TEMP_FOLDER:?}"
    echo "Removing TEMP LISTING Folder ${MISSION_TEMP_FOLDER_LISTING:?}"
    rm -rf ${MISSION_TEMP_FOLDER_LISTING:?}
    echo "Removing TEMP Reprobase JSON Folder ${TEMP_FOLDER_JSONS:?}"
    rm -rf ${MISSION_TEMP_FOLDER_JSONS:?}
  else
    echo "Ingestion failure - Keeping Temporary files "
  fi
    echo "[END] Completed Ingestion of Mission ${MISSION} "
    echo "[END] Completed Ingestion of Mission ${MISSION} " >> ${ERROR_FILE_LOG}
  return $master_code
}


echo "Starting ADGS Downloaded files ingestion"
    echo "Ingesting mission $MISSION from INput Folder $INPUT_FOLDER"
    ingest_mission ${MISSION} ${INPUT_FOLDER}
    result=$?

echo "Done"

# Removing the error log if the number of lines equals 3 : one line per tmp directories created at the beginning
if [ "$( wc -l < ${ERROR_FILE_LOG} )" -eq 3 ]; then
  echo "No errors during ingestion : deleting error file"
  rm $ERROR_FILE_LOG
fi
