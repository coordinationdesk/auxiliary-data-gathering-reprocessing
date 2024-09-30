#!/bin/bash

source ${PWD}/InitFuncs.sh
# 1. starting from date in file
#  2. execute on all missions the ingestion for that date
#  3. go to next date
# repeat for N (parameter) days
# update with last day processed
#

# activate on cron each two hours
# TODO: save a list of files: with info if downloaded, catalogued, saved on reprobase
#   Align LTA for a date interval
# Execute Ingestion for n (batch_len) days in date interval (start date, interval_len days)
# Read Num Days (interval_len) from environment , with default = 7
#    batch_len default = 1 (to be defined if can be read from environment)
# 1. Get start Date from file/env
#    If no LastDate file is present, read from environment
#    After executing all ingestions, save last date to LastDate File
# VARIABLES:
#  ALIGN_NUM_DAYS (interval_len)
#  ALIGN_START_DATE (first date to be ingested)
# FileName = AlignLastDate.txt  (file containing last date)
# Arguments: Temp Dir, Mission
# if mission not specified, all missions

DATE_FORMAT="%Y-%m-%d"
DATE_FILE=${CUR_DIR}/AlignLastDate.txt
function read_start_date() {
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
         START_DATE=$(date -d "$LAST_DATE +1 days" +${DATE_FORMAT} )
      else
        echo "Date in Last Date file has wrong format" >&2
        exit -1
      fi
    fi
  else
    # Read Date from Env Variable
    echo "Align Last Date file not found" >&2
    if [ -z ${L0_ALIGN_START+x} ]; then
      echo "L0_ALIGN_START not set" >&2
      exit -1
    fi
  
    START_DATE=${L0_ALIGN_START}
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
echo ${LAST_DATE} > $DATE_FILE
}

#test_single_exec
if [[ $? -ne 0 ]]; then
   echo "Cannot run, bye"
   exit 1
fi

echo "$# Arguments"
if [ $# -lt 1 ]; then
  echo "$0 tmp_dir [MISSION]"
  echo "MISSION: S1|S2|S3   (Only data for selected mission will be ingested)"
  exit 1
fi


WORK_FOLDER=$1
echo "WORK_FOLDER : "$WORK_FOLDER


REQ_MISSION=""
if [[ $# -gt 1 ]]; then
    # CHeck Mission is valid
    REQ_MISSION=$2
    case $REQ_MISSION in
        S1|S2|S3)
        # do nothing
        ;;
      *)
         # error
         echo ' MISSION ($REQ_MISSION) not valid  ' >&2
         exit 1
     esac
    
fi

MISSIONS=""
if [[ ! -z ${REQ_MISSION} ]]; then
  echo "Ingesting only Mission  $REQ_MISSION"
    MISSIONS="$REQ_MISSION"
fi

CURR_DATE=$(read_start_date)
if [[ $? -eq 0 ]]; then 
  echo "Start date is: $CURR_DATE"
fi

# Define a work Folder under WORK_FOLDER
TEMP_FOLDER=${WORK_FOLDER}/${CURR_DATE}
create_folder $TEMP_FOLDER

NLOOPS=${LTA_ALIGN_BATCH_LEN}
if [[ -z ${NLOOPS} ]]; then
  # Default number of executions in one batch is 7
  NLOOPS=7
fi
echo "Executing $NLOOPS one day ingestions from date $CURR_DATE"
 # Loop N times 
for in in $(seq $NLOOPS); do 
    $CUR_DIR/PRIP_Ingestion.sh ${TEMP_FOLDER} $CURR_DATE
    CURR_DATE=$(date -d "${CURR_DATE} +1 days" +${DATE_FORMAT})
done
update_last_date $CURR_DATE
