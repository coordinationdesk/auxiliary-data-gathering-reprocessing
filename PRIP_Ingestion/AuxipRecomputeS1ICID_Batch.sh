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
source AuxipRecomputeS1ICID.sh
#source AuxipRecomputeIcidTest.sh

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

function read_cmd_arguments() {
echo "$# Arguments"
if [ $# -lt 1 ]; then
  echo "$0 tmp_dir START_DATE [END_DATE]" 
  echo "START_DATE   YYYY-MM-DD"
  exit 1
fi

DATE_FORMAT="%Y-%m-%d"
WORK_FOLDER=$1
echo "WORK_FOLDER : "$WORK_FOLDER

MISSION=S1
START_DATE=$1
if   ! date -d $START_DATE +${DATE_FORMAT} >&2
then
   echo "${START_DATE}: wrong format; expected ${DATE_FORMAT}"
   return -1
fi
# TODO CHECK FORMAT!!

if [ $# -eq 2 ]; then
  END_DATE=$2
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
   if [ -m ${NDAYS} ]; then
     # Default number of executions in one batch is 7
     NDAYS=7
   fi
#  check if BATCH_DELAY is set, to set the time to wait for next batch to be started (in seconds)
# BATCH_DELAY env var with default
   if [[ -z ${BATCH_DELAY+x} ]]; then
     # Default wait time between batches: 30'
     BATCH_DELAY=180
   fi
}



# TODO: Extend Command Arguments parsing to use a description of arguments
read_cmd_arguments $@
read_env_variables

# TODO If Env Variable not defined, set a default value for list of AUX TYPES
set -a AUX_TYPES
if [ -z ${ICID_AUX_TYPES+x} ]; then
   AUX_TYPES=("AUX_WAV AUX_WND AUX_ICE AUX_ECE AUX_PP2 AUX_SCS AUX_PP1 AUX_INS AUX_CAL")
else
   AUX_TYPES=(${ICID_AUX_TYPES})
fi
echo "Updating Aux TYpes: ${AUX_TYPES[*]}"


# IF NOT SPECIFIED; get it from AUXIP
init_variables

# CREATE a tree of temp folders for each batch
# Use start date as Root of temp folders
# For each day ingestion, create three temporary folders for JSONS, Listing file, downloaded products area
create_folder $WORK_FOLDER

# ### START DATE
# Check if start date is set
#   Read START_DAY from Command Line
#  If Last Date File is present, use Last Date File Value
INGESTION_START=$START_DATE
echo "INGESTION START env variable value before calling read_start_date: ${INGESTION_START}"
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
echo "Starting loop; BATCH_START_DAY: ${BATCH_START_DAY}; END DAY: ${END_DAY}"
echo ""
echo $([[ ${BATCH_START_DAY} > ${END_DAY} ]])
until [[ ${BATCH_START_DAY} > ${END_DAY} ]]; do
   # SET Next_current_day (current_day + N_DAYS)
   NEXT_START_DAY=$(date -d "${BATCH_START_DAY} +${NDAYS} days" +${DATE_FORMAT})
    echo "Next loop will have START DAY: ${NEXT_START_DAY}"    
   # check if next current date is beyound end date to adjust number of days of batch
   # Check if next_current_day > END_DAY
    if [[ ${NEXT_START_DAY} > $END_DAY ]]; then
      echo "Setting Batch Num Days to reach END DAY: ${END_DAY}"
      #  If yes, compute N-DAYS as: END_DAY - CURRENT_DAY
      NDAYS=$(( ($(date +%s -d ${NEXT_START_DAY})-$(date +%s -d ${END_DAY}))/86400 ))
      NEXT_START_DAY=$END_DAY
    fi

   # Define a work Folder under WORK_FOLDER
   TEMP_FOLDER=${WORK_FOLDER}/${BATCH_START_DAY}
   create_folder $TEMP_FOLDER

   #    execute UPdate of ICID  from current date for Num Days
   #    Call Loop Internal Function: current_day, N_Days
   #              (Execute Daily Update Function N times, one day at time)

   # Loop on TYPES
   echo "Starting ICID update batch from $BATCH_START_DAY of $NDAYS days"
   for AUX_TYPE in ${AUX_TYPES[@]}; do
       echo "Starting ICID update batch for $AUX_TYPE from $BATCH_START_DAY of $NDAYS days"
       update_products_mission_date_interval $TEMP_FOLDER $MISSION $AUX_TYPE $BATCH_START_DAY $NDAYS 
       # Check return code
       batch_code=$?
   done

   #    Check if any error occurred
   #    if end date was not set, set it to  today

   BATCH_START_DAY=$NEXT_START_DAY

   #    Save CURRENT_DAY to FILE
   echo "Updating Last DATE on file"
   update_last_date $BATCH_START_DAY $MISSION ${WORK_FOLDER}

   #    Wait a configured TIME (seconds)
   echo "Pausing $BATCH_DELAY seconds"
   sleep  ${BATCH_DELAY}s
   # Actually it's no needed, unless we roll over midnight;
   # it has been set before loop
   if [ -z ${END_DATE} ]; then
      END_DAY=$(date '+%Y-%m-%d')
   else
      END_DAY=${END_DATE}
   fi
   echo "Next END_DAY: ${END_DAY}"
done
echo "Completed Ingestion"
