#!/bin/bash

if [ $# -lt 1 ]; then
  echo "$0 tmp"
  exit 1
fi

source InitFuncs.sh

WORK_FOLDER=$1
echo "WORK_FOLDER : "$WORK_FOLDER
# OPTIONAL ARGUMENT: Reference DATE
# IF NOT SPECIFIED; get it from AUXIP
PUBLICATION_DATE_FORMAT="%Y-%m-%d"
REFERENCE_DATE=""

if [[ $# -gt 1 ]]; then
  REFERENCE_DATE=$2
  echo "Ingesting from Date $REFERENCE_DATE"
# Check if Start Date in  '+%Y-%m-%d'
  if [[ ! $REFERENCE_DATE =~ ^([0-9]{4})\-(0[0-9]|1[0-2])\-(0[1-9]|[1-2][0-9]|3[0-1])$ ]]
  then
    echo "Second argument (Reference date) should be in the format: YYYY-mm-DD ($REFERENCE_DATE)"
    exit 1
  else
    echo "Ingesting from Reference date $REFERENCE_DATE"
  fi
fi

if [[ -z ${REFERENCE_DATE} ]]; then
  FROM_DATE_ARG=""
  TO_DATE_ARG=""
else
  # IF a REFERENCE DATE WAS SPECIFIED, ingest 1 DAY of data
  FROM_DATE_ARG="-from ${REFERENCE_DATE}"
  TO_DATE=$(date -d "$REFERENCE_DATE +1 days" +${PUBLICATION_DATE_FORMAT} )
  echo " TO DATE: $TO_DATE"
  # Convert to_date to expected format
  #TO_DATE_STR=$(date --date "$TO_DATE" +"${PUBLICATION_DATE_FORMAT}" )
  TO_DATE_ARG="-to ${TO_DATE}"
fi

init_variables

create_folder "$WORK_FOLDER"

#EXECUTION DATE
START_DATE=$(date '+%Y-%m-%d')

init_folders $START_DATE

function list_mission() {
  # Expecting argument for MISSION to be ingested
  #  From/TO date arguments (with option included) are defined
  #   using global variables
  if [[ $# != 1 ]] ; then
      echo "Called ingest_mission function without MISSION argument"
      exit 1
  fi
  MISSION=$1
  echo "Function ingest_mission: Ingesting Mission ${MISSION} with arg ${FROM_DATE_ARG} and ${TO_DATE_ARG}"
  python3 -u ${CUR_DIR}/PRIP_Ingestion.py --list_only -m ${MISSION} -u ${PRIP_USER} -pw ${PRIP_PASS} \
        -w ${TEMP_FOLDER} -au ${AUXIP_USER} -apw ${AUXIP_PASS}    \
        -fd file_types \
        ${FROM_DATE_ARG} ${TO_DATE_ARG}
  code=$?
  if [ $code -ne 0 ]; then
    echo "PRIP Retrieve failed"
    echo "PRIP Retrieve failed" >> ${ERROR_FILE_LOG}
  fi
  if [ $code -eq 0 ]; then
        echo "Removing temporary folders"
        rm -r ${TEMP_FOLDER}
        rm -r ${TEMP_FOLDER_LISTING}
        rm -r ${TEMP_FOLDER_JSONS}
        echo "Done"
  fi
}

echo "Starting PRIP List"
set -a MISSIONS
MISSIONS="S1 S2 S3"
#MISSIONS="S1 S3"
for sat in ${MISSIONS}
do
    echo "Listing  $sat $FROM_DATE_ARG $TO_DATE_ARG"
    list_mission $sat
done

# Removing the error log if the number of lines equals 3 : one line per tmp directories created at the beginning
if [ "$( wc -l < ${ERROR_FILE_LOG} )" -eq 3 ]; then
  echo "No errors during ingestion : deleting error file"
  rm $ERROR_FILE_LOG
fi
