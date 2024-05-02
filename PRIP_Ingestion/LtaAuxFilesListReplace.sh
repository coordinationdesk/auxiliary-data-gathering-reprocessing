#!/bin/bash 

source InitFuncs.sh
source FilesUtils.sh
source IngestDownloaded_funcs.sh

echo "$# Arguments"
if [ $# -lt 1 ]; then
  echo "LtaAuxFilesListIngest.sh tmp_dir input_file MISSION "
  echo "Ingest from LTA Aux files for MISSION, with names from input_file"
  exit 1
fi

WORK_FOLDER=$1
echo "WORK_FOLDER : "$WORK_FOLDER

echo "Num arguments: $#"
if [[ $# -lt 3 ]]; then
  read -p "Enter Mission: " MISSION 
else
 MISSION=$3
fi
AUX_NAMES_FILE=""
if [[ $# -lt 2 ]]; then
  read -p "Enter Input File: " AUX_NAMES_FILE 
else
 AUX_NAMES_FILE=$2
fi

# OPTIONAL ARGUMENT: Reference DATE
# IF NOT SPECIFIED; get it from AUXIP
init_lta_variables
init_variables

create_folder $WORK_FOLDER
#EXECUTION DATE
EXEC_DATE=$(date '+%Y-%m-%d')

# MOVE Folders creation inside ingest mission, to be done for each mission!
init_folders $EXEC_DATE


function ingest_aux_files_from_names() {

  # Expecting argument for MISSION to be ingested
  #  From/TO date arguments (with option included) are defined
  #   using global variables
  if [[ $# != 2 ]] ; then
      echo "Called ingest_from_file function without file argument"
      exit 1
  fi
  AUX_LIST_FILE=$1
  REPLACE_EXISTING=$2
  MISSION_TEMP_FOLDER=${TEMP_FOLDER}/$AUX_LIST_FILE
  MISSION_TEMP_FOLDER_LISTING=${TEMP_FOLDER_LISTING}/${AUX_LIST_FILE}
  MISSION_TEMP_FOLDER_JSONS=${TEMP_FOLDER_JSONS}/${AUX_LIST_FILE}
  create_folder $MISSION_TEMP_FOLDER
  create_folder $MISSION_TEMP_FOLDER_LISTING
  create_folder $MISSION_TEMP_FOLDER_JSONS
    echo "[BEGIN] Function ingest_from_file: Ingesting Mission ${MISSION} , Aux Names file: : $AUX_LIST_FILE"
    echo "[BEGIN] Function ingest_from_file: Ingesting Mission ${MISSION} , Aux Names file: : $AUX_LIST_FILE" >> ${ERROR_FILE_LOG}
  echo "Function ingest_mission: Ingesting Aux Files with names from file  ${AUX_LIST_FILE}"
  python3 -u ${CUR_DIR}/LtaAuxFiles_Download.py  -u ${PRIP_USER} -pw ${PRIP_PASS} \
        -w ${MISSION_TEMP_FOLDER} \
        -lu ${PRIP_ENDPOINT} -au ${AUXIP_USER} -apw ${AUXIP_PASS} \
        -f ${AUX_LIST_FILE}

  code=$?
  if [ $code -ne 0 ]; then
    echo "PRIP Retrieve failed"
    echo "PRIP Retrieve failed" >> ${ERROR_FILE_LOG}
  fi
  if [ $REPLACE_EXISTING -eq 0 ]; then
      ingest_downloaded_files $MISSION $code "$MISSION_TEMP_FOLDER" "${MISSION_TEMP_FOLDER_LISTING}" "${MISSION_TEMP_FOLDER_JSONS}"
  else
      ingest_replace_downloaded_files $MISSION $code "$MISSION_TEMP_FOLDER" "${MISSION_TEMP_FOLDER_LISTING}" "${MISSION_TEMP_FOLDER_JSONS}"
  fi
  ingestion_code=$?
  echo "Removing temporary folders"
    if [ $ingestion_code -eq 0 ]; then
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
    echo "[END] Completed Ingestion of Mission ${MISSION} , Aux Names file: : $AUX_LIST_FILE"
    echo "[END] Completed Ingestion of Mission ${MISSION} , Aux Names file: : $AUX_LIST_FILE" >> ${ERROR_FILE_LOG}
  return $ingestion_code
}


REPLACE=1
echo "Starting AUX Files download"
AUX_FILES=$(split_file $AUX_NAMES_FILE 50 LTA_AUX_FILE_BATCH_)
echo "$AUX_FILES"
#AUX_FILES=Acri_files_set1.txt
# Split Input file in Bathes of N (50) lines
# Put list of gnerated files in AUX_FILES
ingestion_code=0
for aux_list_file in ${AUX_FILES}
do
    echo "Ingesting mission $mission $FROM_DATE_ARG $TO_DATE_ARG"
    ingest_aux_files_from_names ${aux_list_file} $REPLACE
    result=$?
    (( ingestion_code=$result||$ingestion_code ))
done
# Remove temporary folders if ALL missions have been successful
  echo "Completed all missions ingestion: Removing temporary folders"
  if [ $ingestion_code -eq 0 ]; then
    echo "No Errors Found"
    echo "Removing TEMP Folder ${TEMP_FOLDER:?}"
    rm -rf "${TEMP_FOLDER:?}"/
    echo "Removing TEMP LISTING Folder ${TEMP_FOLDER_LISTING:?}"
    rm -rf ${TEMP_FOLDER_LISTING:?}/
    echo "Removing TEMP Reprobase JSON Folder ${TEMP_FOLDER_JSONS:?}"
    rm -rf ${TEMP_FOLDER_JSONS:?}/
  else
     echo "Errors found during ingestion - Keeping temporary folders"
  fi

echo "Done"

# Removing the error log if the number of lines equals 3 : one line per tmp directories created at the beginning
if [ "$( wc -l < ${ERROR_FILE_LOG} )" -eq 3 ]; then
  echo "No errors during ingestion : deleting error file"
  rm $ERROR_FILE_LOG
fi
