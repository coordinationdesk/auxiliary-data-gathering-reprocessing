#!/bin/bash

source ${PWD}/InitFuncs.sh
CUR_DIR="$(
  cd "$(dirname "$0")"
  pwd -P
)"

if [ $# -lt 1 ]; then
  echo "ECMWF_Ingestion.sh tmp"
  exit 1
fi

if [ -z ${TIME_PERIOD+x} ]; then
  echo "TIME_PERIOD not set"
  exit 1
fi
echo "TIME_PERIOD : "$TIME_PERIOD
WORK_FOLDER=$1
echo "WORK_FOLDER : "$WORK_FOLDER

init_ecmwf_variables
init_ecmwf_mode
init_variables
create_folder $WORK_FOLDER


ERROR_FILE_LOG="${WORK_FOLDER}/$(date '+%Y-%m-%d')_ECMWF_error.log"
echo "START_DATE: "$START_DATE
echo "STOP_DATE: "$STOP_DATE
echo "START : ${START_DATE} - STOP : ${STOP_DATE}" >> $ERROR_FILE_LOG

if [ -z ${STOP_DATE+x} ]; then
    STOP_DATE=$(date '+%Y-%m-%d' -d "5 day ago")
fi
if [ -z ${START_DATE+x} ]; then
    START_DATE=$(date '+%Y-%m-%d' -d "$((TIME_PERIOD + 5)) day ago")
fi

init_folders $START_DATE CAMSAN
init_ecmwf_folders 
echo "Temporary folder : "$TEMP_FOLDER
TEMP_FOLDER_AUX=$(mktemp -p $WORK_FOLDER -d)
echo "TEMP_FOLDER_JSONS : ${TEMP_FOLDER_AUX}" >> $ERROR_FILE_LOG

MISSION=S2
echo "Starting ECMWF download from $START_DATE to $STOP_DATE"
python3 -u ${CUR_DIR}/ECMWF_Ingestion.py -k ${ECMWF_PASS} -w ${TEMP_FOLDER} -s $START_DATE -e $STOP_DATE -u ${ECMWF_URL} -m ${ECMWF_USER} -o ${TEMP_FOLDER_AUX}
code=$?
if [ $code -ne 0 ]; then
  echo "ECMWF Retrieve failed"
  echo "ECMWF Retrieve failed" >> $ERROR_FILE_LOG
else
  echo "ECMWF download done"
  echo "Starting AUXIP ingestion"
    python3 -u ${CUR_DIR}/ingestion/replace_aux_products.py -i ${TEMP_FOLDER_AUX} -u ${AUXIP_USER} -pw ${AUXIP_PASS} -mc ${MCPATH} -b "wasabi-auxip-archives/"${S3_BUCKET} -o ${TEMP_FOLDER_LISTING}/file_list_${MISSION}.txt -e ${TEMP_FOLDER_LISTING}/error_list_${MISSION}.txt -m ${MODE}
  code=$?
  if [ $code -ne 0 ]; then
    echo "AUXIP ingestion failed"
    echo "AUXIP ingestion failed" >> $ERROR_FILE_LOG
  else
    echo "AUXIP ingestion done"
    echo "Starting Reprobase jsons generation - Ingestion of S2 Files"
    python3 -u ${CUR_DIR}/ingest_s2files.py -i ${TEMP_FOLDER_LISTING}/file_list_${MISSION}.txt -f ${CUR_DIR}/file_types -t ${CUR_DIR}/template.json -o ${TEMP_FOLDER_JSONS}/
    code=$?
    if [ $code -ne 0 ]; then
      echo "Reprobase jsons generation failed"
      echo "Reprobase jsons generation failed" >> $ERROR_FILE_LOG
    else
      echo "Reprobase json generation done"
      master_code=0
      for f in $(find ${TEMP_FOLDER_JSONS} -name '*.json'); do
        echo "Pushing "$f" to reprobase"
        python3 ${CUR_DIR}/update_base.py -i $f -u ${AUXIP_USER} -pw ${AUXIP_PASS} -m ${MODE}
        code=$?
        if [ $code -ne 0 ]; then
          echo "Reprobase ingestion failed for file "$f
          master_code=$code
        fi
      done
      if [ $master_code -ne 0 ]; then
            echo "Reprobase ingestion failed"
            echo "Reprobase ingestion failed" >> $ERROR_FILE_LOG
      else
        echo "Removing temporary folders"
        rm -r ${TEMP_FOLDER}
        rm -r ${TEMP_FOLDER_AUX}
        rm -r ${TEMP_FOLDER_JSONS}
        rm -r ${TEMP_FOLDER_LISTING}
      echo "Done"
      fi
    fi
  fi
fi

# Removing the error log if the number of lines equals 5 : one line per tmp directories created at the beginning plus one for the period
if [ "$( wc -l < ${ERROR_FILE_LOG} )" -eq 5 ]; then
  echo "No errors during ingestion : deleting error file"
  rm $ERROR_FILE_LOG
fi
