#!/bin/bash 

source ${PWD}/InitFuncs.sh

if [ $# -lt 1 ]  ; then
  echo "$0 tmp_dir [NUM_DAYS [MISSION]]"
    exit 0
fi
# CHECK IF ANOTHER INSTANCE IS RUNNING
# Processes include: containing bash, bash, and grep
if [ `ps ax | grep $0 | wc -l` -gt 3 ]; then  
  echo "$0 Already running"
  echo "ps returned $(ps ax | grep $0 | wc -l) items"
  echo "ps returned $(ps ax | grep $0 ) items"
  #exit 0
fi



WORK_FOLDER=$1
echo "WORK_FOLDER : "$WORK_FOLDER

REQ_MISSION=""
if [[ $# -gt 1 ]]; then
  NUM_DAYS=$2
  echo "Ingesting $NUM_DAYS days of product names"
  if [[ $# -gt 2 ]]; then
    # CHeck Mission is valid
    REQ_MISSION=$3
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
fi

if [[ -z ${NUM_DAYS} ]]; then
  NUM_DAYS_ARG=""
else
  NUM_DAYS_ARG="-n ${NUM_DAYS}"
fi

set -a MISSIONS

MISSIONS="S1 S2 S3"
if [[ ! -z ${REQ_MISSION} ]]; then
  echo "Ingesting only Mission  $REQ_MISSION"
    MISSIONS="$REQ_MISSION"
fi
init_lta_variables

create_folder $WORK_FOLDER
#EXECUTION DATE
START_DATE=$(date '+%Y-%m-%d')
# MOVE Folders creation inside ingest mission, to be done for each mission!
init_folders $START_DATE

function ingest_mission() {
  # Expecting argument for MISSION to be ingested
  #  From/TO date arguments (with option included) are defined
  #   using global variables
  if [[ $# != 1 ]] ; then
      echo "Called ingest_mission function without MISSION argument"
      exit 1
  fi
  MISSION=$1
  echo "Function ingest_mission: Ingesting L0 names of Mission ${MISSION}  for  $NUM_DAYS days "
  python3 -u ${CUR_DIR}/baseline_l0.py -m ${MISSION} \
        -dbh ${DATABASELINE_POSTGRES_HOST} -p 5432 -dbn ${DATABASELINE_POSTGRES_DB}  -dbu ${DATABASELINE_POSTGRES_USER} -dbp ${DATABASELINE_POSTGRES_PASS}    \
        -lu ${PRIP_ENDPOINT} -u ${PRIP_USER} -pw ${PRIP_PASS} \
        ${NUM_DAYS_ARG} 
  code=$?
   if [ $code -ne 0 ]; then
    echo "L0 Retrieve failed"
    echo "L0 Retrieve failed" >> ${ERROR_FILE_LOG}
  fi
  ingestion_code=$?
  return $ingestion_code
}


echo "Starting L0 Names  download"
ingestion_code=0
for mission in ${MISSIONS}
do
    echo "Ingesting mission $mission $MAX_L0_DAYS "
    ingest_mission ${mission}
    result=$?
    (( ingestion_code=$result||$ingestion_code ))
done
# Remove temporary folders if ALL missions have been successful
  #ingestion_code=$?
  echo "Completed all missions ingestion"
  if [ $ingestion_code -eq 0 ]; then
    echo "No Errors Found"
  else
     echo "Errors found during ingestion - Keeping temporary folders"
  fi
  #return $ingestion_code

echo "Done"

# Removing the error log if the number of lines equals 3 : one line per tmp directories created at the beginning
if [ "$( wc -l < ${ERROR_FILE_LOG} )" -eq 3 ]; then
  echo "No errors during ingestion : deleting error file"
  rm $ERROR_FILE_LOG
fi
