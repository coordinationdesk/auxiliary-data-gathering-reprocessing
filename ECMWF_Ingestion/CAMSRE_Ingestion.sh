#!/bin/bash
source ${PWD}/InitFuncs.sh

# TODO UNIFY with ECMWF Ingestion, add parameter

# CHECK IF ANOTHER INSTANCE IS RUNNING
# Processes include: containing bash, bash, and grep
if [ `ps ax | grep $0 | wc -l` -gt 3 ]; then
  echo "$0 Already running"
  exit 0
fi

echo "$# Arguments"
if [ $# -lt 1 ]; then
  echo "$0 tmp_dir [START_DATE [END_DATE]]"
  echo "START_DATE: YYYY-mm-DD  (Only data from Start Date will be ingested)"
  echo "END_DATE: YYYY-mm-DD    (Only data for selected mission will be ingested)"
  echo "If Start Date is not specified, default End date is today - 5 days; "
  echo "   start date is defined by env variable TIME_PERIOD"
  echo "if start date is specified, and end date is not specified, "
  echo "   end date is defined by adding env variable TIME_PERIOD"
  echo "If start date and end date are both specified, data for this interval will be ingested"
  exit 1

else
  WORK_FOLDER=$1
  echo "WORK_FOLDER : "$WORK_FOLDER
  if [ $# -lt 3 ]; then
    # TIME Period is used if we don't have specified a END
    if [ -z ${TIME_PERIOD+x} ]; then
      echo "TIME_PERIOD not set"
      exit 1
    fi
    echo "TIME_PERIOD : "$TIME_PERIOD
  fi
  if [ $# -gt 1 ]; then
    # Check if a correct start date was set
    START_DATE=$2
    # Check if a correct end  date was set
# Check if Start Date in  '+%Y-%m-%d'
  if [[ ! $START_DATE =~ ^([0-9]{4})\-(0[0-9]|1[0-2])\-(0[1-9]|[1-2][0-9]|3[0-1])$ ]]
  then
    echo "Second argument (Reference date) should be in the format: YYYY-mm-DD ($START_DATE)"
    exit 1
  else
    echo "Ingesting from START date $START_DATE"
  fi
    #   If not specified, STOP_ DATE is PERIOD after start date
    if [ $# -gt 2 ]; then
       STOP_DATE=$3
# Check if Start Date in  '+%Y-%m-%d'
  if [[ ! $STOP_DATE =~ ^([0-9]{4})\-(0[0-9]|1[0-2])\-(0[1-9]|[1-2][0-9]|3[0-1])$ ]]
  then
    echo "Third argument (STOP date) should be in the format: YYYY-mm-DD ($STOP_DATE)"
    exit 1
  else
    echo "Ingesting from Reference date $STOP_DATE"
  fi
    else
       STOP_DATE=$(date '+%Y-%m-%d' -d "$START_DATE +$TIME_PERIOD days")
    fi
    
  fi
    
fi

init_ecmwf_variables
init_ecmwf_mode
init_variables

create_folder $WORK_FOLDER


if [ -z ${STOP_DATE+x} ]; then
    STOP_DATE=$(date '+%Y-%m-%d' -d "5 day ago")
fi
if [ -z ${START_DATE+x} ]; then
    # TODO: CHANGE: TIME PERIOD BEFORE STOP DATE!!!
    START_DATE=$(date '+%Y-%m-%d' -d "$(($TIME_PERIOD + 5)) day ago")
fi
#EXECUTION DATE
#START_DATE=$(date '+%Y-%m-%d')

# MOVE Folders creation inside ingest mission, to be done for each mission!
init_folders $START_DATE CAMSRE
init_ecmwf_folders 


echo "START_DATE: "$START_DATE
echo "STOP_DATE: "$STOP_DATE
echo "START : ${START_DATE} - STOP : ${STOP_DATE}" >> $ERROR_FILE_LOG

echo "Starting CAMSRE download from $START_DATE to $STOP_DATE"

# TODO: Align to PRIP INgestione SH driver script, that does not use nested IFs
python3 -u ${CUR_DIR}/CAMSRE_Ingestion.py -k ${ECMWF_PASS} -wd ${TEMP_FOLDER} -start $START_DATE -stop $STOP_DATE -u ${ECMWF_URL} -m ${ECMWF_USER} -o ${TEMP_FOLDER_AUX}
code=$?
if [ $code -ne 0 ]; then
  echo "ECMWF Retrieve failed"
  echo "ECMWF Retrieve failed" >> $ERROR_FILE_LOG
else
  echo "ECMWF download done"
  # exit 0
  echo "Starting AUXIP ingestion"
  python3 -u ${CUR_DIR}/ingestion/ingestion.py -i ${TEMP_FOLDER_AUX} -u ${AUXIP_USER} -pw ${AUXIP_PASS} -mc ${MCPATH} -b "wasabi-auxip-archives/"${S3_BUCKET} -o ${TEMP_FOLDER_LISTING}/file_list_S2.txt -m ${MODE}
  code=$?
  if [ $code -ne 0 ]; then
    echo "AUXIP ingestion failed"
    echo "AUXIP ingestion failed" >> $ERROR_FILE_LOG
  else
    echo "AUXIP ingestion done"
    echo "Starting Reprobase jsons generation - Ingestion of S2 Files"
    python3 -u ${CUR_DIR}/ingest_s2files.py -i ${TEMP_FOLDER_LISTING}/file_list_S2.txt -f ${CUR_DIR}/file_types -t ${CUR_DIR}/template.json -o ${TEMP_FOLDER_JSONS}/
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
