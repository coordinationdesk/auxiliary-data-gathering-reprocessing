#!/bin/bash
# Copyright
# Telespazio.com
#
# This script controls Continuous ingesiton Control.
# Starting from a Start date, up to an end date
# It executes the Ingestion script for N days
# Then waits a configurable time
# and continues until the end date is reached
source InitFuncs.sh
source LastDateFile.sh
source Eumetsat_Ingest.sh
#source Eumetsat_Ingest_test.sh

#REQ_MISSION=""
#if [[ $# -gt 1 ]]; then
#    # CHeck Mission is valid
#    REQ_MISSION=$2
#    case $REQ_MISSION in
#        S1|S2|S3)
#        # do nothing
#        ;;
#      *)
#         # error
#         echo ' MISSION ($REQ_MISSION) not valid  ' >&2
#         exit 1
#     esac
#    
#fi

function init_ftp_variables() {
export FTP_USER=sentinel_exchanges
export FTP_PASS=ntzANHyeUpCgxcE6gec1
export FTP_HOST=cdrftp.eumetsat.int
export FTP_FOLDER=fromEUM_toESA/AX___MA1_AX_v2
if [ -z ${FTP_HOST+x} ]; then
  echo "FTP_HOST not set"
  exit 1
fi
echo "FTP_HOST: "${FTP_HOST}
if [ -z ${FTP_USER+x} ]; then
  echo "FTP_USER not set"
  exit 1
fi
echo "FTP_USER: "${FTP_USER}
if [ -z ${FTP_PASS+x} ]; then
  echo "FTP_PASS not set"
  exit 1
fi
#echo "FTP_PASS: "${FTP_PASS}
if [ -z ${FTP_FOLDER+x} ]; then
  echo "FTP_FOLDER not set"
  exit 1
fi
echo "FTP_FOLDER: "${FTP_FOLDER}
}
function read_cmd_arguments() {
echo "$# Arguments"
if [ $# -lt 4 ]; then
  echo "$0 tmp_dir MISSION AUX_TYPE START_DATE [END_DATE]" 
  echo "MISSION: S1|S2|S3   (Only data for selected mission will be ingested)"
  echo "START_DATE   YYYY-MM-DD"
  exit 1
fi

DATE_FORMAT="%Y-%m-%d"
WORK_FOLDER=$1
echo "WORK_FOLDER : "$WORK_FOLDER

MISSION=$2
AUX_TYPE=$3
START_DATE=$4
if   ! date -d $START_DATE +${DATE_FORMAT} >&2
then
   echo "${START_DATE}: wrong format; expected ${DATE_FORMAT}"
   return -1
fi
# TODO CHECK FORMAT!!

if [ $# -eq 5 ]; then
  END_DATE=$5
  if   ! date -d $END_DATE +${DATE_FORMAT} >&2
  then
     echo "${END_DATE}: wrong format; expected ${DATE_FORMAT}"
     return -1
  fi
else
  END_DATE="" 
fi
}


function read_env_variables() {
# BATCH_LEN env var with default
   NDAYS=${BATCH_LEN}
   if [[ -z ${NDAYS+x} ]]; then
     # Default number of executions in one batch is 7
     NDAYS=7
   fi
#  check if BATCH_DELAY is set, to set the time to wait for next batch to be started (in seconds)
# BATCH_DELAY env var with default
   if [[ -z ${BATCH_DELAY+x} ]]; then
     # Default wait time between batches: 30'
     BATCH_DELAY=1800
   fi
}

# TODO: Extend Command Arguments parsing to use a description of arguments
read_cmd_arguments $@
read_env_variables


# IF NOT SPECIFIED; get it from AUXIP
init_variables

init_ftp_variables
# CREATE a tree of temp folders for each batch
# Use start date as Root of temp folders
# For each day ingestion, create three temporary folders for JSONS, Listing file, downloaded products area
create_folder $WORK_FOLDER

# ### START DATE
# Check if start date is set
#   Read START_DAY from Command Line
#  If Last Date File is present, use Last Date File Value
INGESTION_START=$START_DATE
echo "ingestion start env before calling read_start_date: ${INGESTION_START}"
# start from START_DAY, save as Current DAY
CURR_DATE=$(read_start_date ${MISSION} ${WORK_FOLDER})
if [[ $? -eq 0 ]]; then 
    echo "Start date is: $CURR_DATE"
    BATCH_START_DAY=$CURR_DATE
else
    BATCH_START_DAY=$START_DATE
fi

# ### END DATE
# check if end date is set (or specified on command line: otherwise current date is END_DATE (at each loop)
if [ -z ${END_DATE+x} ]; then
   END_DAY=$(date '+%Y-%m-%d')
else
   END_DAY=${END_DATE}
fi


#  IF CURRENT_DAY > END_DAY .... Exit loop
# Format of date make it possible to compare dates 
# by comparing string order
# END_DAY is either END_DATE, or today, if END_DATE was not specified
until [[ ${BATCH_START_DAY} > ${END_DAY} ]]; do
   # SET Next_current_day (current_day + N_DAYS)
   NEXT_START_DAY=$(date -d "${BATCH_START_DAY} +${NDAYS} days" +${DATE_FORMAT})
        
   # check if next current date is beyound end date to adjust number of days of batch
   # Check if next_current_day > END_DAY
    if [[ ${NEXT_START_DAY} > $END_DAY ]]; then
      echo "Setting Batch Num Days to reach END DAY: ${END_DAY}"
      #  If yes, compute N-DAYS as: END_DAY - CURRENT_DAY
      NDAYS=$(( ($(date +%s -d ${NEXT_START_DAY})-$(date +%s -d ${END_DAY}))/86400 ))
    fi

   # Define a work Folder under WORK_FOLDER
   TEMP_FOLDER=${WORK_FOLDER}/${BATCH_START_DAY}
   create_folder $TEMP_FOLDER

   #    execute Eumetsat Ingestion from current date for Num Days
   #    Call Loop Internal Function: current_day, N_Days
   #              (Execute Daily Ingestion Function N times, one day at time)

   echo "Starting ingestion batch from $BATCH_START_DAY of $NDAYS days"
   ingest_mission_date_interval $TEMP_FOLDER $MISSION $AUX_TYPE $BATCH_START_DAY $NDAYS 
   # Check return code
   batch_code=$?

   #    Check if any error occurred
   #    if end date was not set, set it to  today

   BATCH_START_DAY=$NEXT_START_DAY

   #    Save CURRENT_DAY to FILE
   update_last_date $BATCH_START_DAY $MISSION ${WORK_FOLDER}

   #    Wait a configured TIME (seconds)
   echo "Pausing $BATCH_DELAY seconds"
   sleep  $BATCH_DELAY
   if [ -z ${END_DATE} ]; then
      END_DAY=$(date '+%Y-%m-%d')
   else
      END_DAY=${END_DATE}
   fi
done
echo "Completed Ingestion"
