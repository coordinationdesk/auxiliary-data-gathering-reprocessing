#!/bin/bash


DATE_FORMAT="%Y-%m-%d"
function get_date_file_name() {
MISS=$1
ROOT_F=$2
if [[ -z ${ROOT_F} ]]; then
   ROOT_F=${CUR_DIR}
fi
echo "${ROOT_F}/${MISS}_AlignLastDate.txt"
}
function read_start_date() {
MISSION=$1
ROOT_F=$2

  DATE_FILE=$(get_date_file_name $MISSION ${ROOT_F})
  echo "Checking start date from date file: $DATE_FILE" >&2
  if [ -f ${DATE_FILE} ]; then
    # Read Date from file
    echo "Align Last Date file found" >&2
    read -r LAST_DATE < ${DATE_FILE}
    if [ -z ${LAST_DATE} ]; then
       echo "No date set in Last Date File" >&2
       exit -1
    else
      # Redirect command to avoid mixing output with this function otuput
      if   date -d $LAST_DATE +${DATE_FORMAT} >&2
      then
         #START_DATE=$(date -d "$LAST_DATE +1 days" +${DATE_FORMAT} )
         START_DATE=$LAST_DATE
      else
        echo "Date in Last Date file has wrong format" >&2
        exit -1
      fi
    fi
  else
    # Read Date from Env Variable
    echo "Align Last Date file ${DATE_FILE} not found" >&2
    if [ -z "${INGESTION_START}" ]; then
      echo "INGESTION_START not set" >&2
      exit -1
    fi
  
    START_DATE=${INGESTION_START}
    echo "Env Var: $START_DATE" >&2
    if  ! date -d $START_DATE +${DATE_FORMAT} >&2
    then
      echo "Environment Variable L0_ALIGN_Start has wrong date format" >&2
      exit -1
    fi
  fi
  echo "Returning start date: $START_DATE - " >&2
  # Print result
  echo  "$START_DATE"
}

function update_last_date() {
LAST_DATE=$1
MISSION=$2
TARGET_F=$3
  DATE_FILE=$(get_date_file_name $MISSION ${TARGET_F})
echo ${LAST_DATE} > $DATE_FILE
}

