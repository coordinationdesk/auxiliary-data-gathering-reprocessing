#!/bin/bash 

source InitFuncs.sh

echo "$# Arguments"
if [ $# -lt 1 ]; then
  echo "PRIP_Ingestion.sh tmp_dir [REFERENCE_DATE [MISSION]]"
  echo "REFERENCE_DATE: YYYY-mm-DD  (Only data for Reerence Date will be ingested)"
  echo "MISSION: S1|S2|S3   (Only data for selected mission will be ingested)"
  exit 1
fi

WORK_FOLDER=$1
echo "WORK_FOLDER : "$WORK_FOLDER


# OPTIONAL ARGUMENT: Reference DATE
# IF NOT SPECIFIED; get it from AUXIP
PUBLICATION_DATE_FORMAT="%Y-%m-%d"
REFERENCE_DATE=""
REQ_MISSION=""
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

# TODO: Add Options to allow differentiate REFERENCE DATE AND MISSION
# OR: SPECIFY MISSION ONLY IF REFERNCE DATE IS SPECIFIED
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

set -a MISSIONS
#MISSIONS="S1 S2 S3"
MISSIONS="S1 S2 S3"
if [[ ! -z ${REQ_MISSION} ]]; then
  echo "Ingesting only Mission  $REQ_MISSION"
    MISSIONS="$REQ_MISSION"
fi
init_variables

create_folder $WORK_FOLDER
#EXECUTION DATE
START_DATE=$(date '+%Y-%m-%d')

# MOVE Folders creation inside ingest mission, to be done for each mission!
init_folders $START_DATE

function ingest_downloaded_files() {
  MISSION=$1
  code=$2
  DWL_TEMP_FOLDER=$3
  LISTING_FOLDER=$4
  JSONS_FOLDER=$5
  echo "Ingesting downloaded files: Download folder: $DWL_TEMP_FOLDER, Listing folder: $LISTING_FOLDER, Folder for JSONS: $JSONS_FOLDER"
  master_code=$code
  if [ $code -eq 0 ]; then
    echo "PRIP download done"

    echo "Starting AUXIP ingestion $MISSION"
    python3 -u ${CUR_DIR}/ingestion/ingestion.py -i ${DWL_TEMP_FOLDER} -u ${AUXIP_USER} -pw ${AUXIP_PASS} -mc ${MCPATH} -b "wasabi-auxip-archives/"${S3_BUCKET} -o ${LISTING_FOLDER}/file_list_${MISSION}.txt -m ${MODE}
    code=$?
    master_code_auxip=$code
    if [ $code -ne 0 ]; then
       echo "Auxip ingestion failed for Mission ${MISSION} with error $code" 
       echo "Auxip ingestion failed for Mission ${MISSION} with error $code" >> ${ERROR_FILE_LOG}
    fi
    if [ $master_code_auxip -ne 0 ]; then
       echo "AUXIP ingestion failed"
       echo "AUXIP ingestion for mission ${MISSION} failed" >> ${ERROR_FILE_LOG}
    fi
    master_code=$master_code_auxip
  fi
	# AUXIP Ingested Files: Generation of related JSONs to put in ReproBase
  if [ $master_code -eq 0 ]; then
      echo "AUXIP ingestion done"
      echo "Removing files downloaded from LTA (Ingested on AUXIP)..."
      rm  -rf "${DWL_TEMP_FOLDER}"
      echo "Removed files downloaded from LTA"
      if [ -s "${LISTING_FOLDER}/file_list_${MISSION}.txt" ]; then
        echo "Starting Reprobase jsons generation for $MISSION"
        MISSION_LOWER=${MISSION,,}
        python3 -u ${CUR_DIR}/ingest_${MISSION_LOWER}files.py -i ${LISTING_FOLDER}/file_list_${MISSION}.txt -f ${CUR_DIR}/file_types -t ${CUR_DIR}/template.json -o ${JSONS_FOLDER}
        code=$?
        master_code_reprobase=$code
        if [ $code -ne 0 ]; then
         echo "Reprobase jsons generation failed for ${MISSION}" 
         echo "Reprobase jsons generation failed for ${MISSION}" >> ${ERROR_FILE_LOG}
        fi
      else
        echo "Reprobase Jsons generation skipped: no files found on LTA"
        master_code_reprobase=0
      fi
      if [ $master_code_reprobase -ne 0 ]; then
        echo "Reprobase jsons generation failed"
        echo "Reprobase jsons generation failed" >> ${ERROR_FILE_LOG}
      fi
      master_code=$master_code_reprobase
  fi
	# Adding auxip related JSONS into ReproBase 
  if [ $master_code -eq 0 ]; then
      echo "Reprobase json generation done"
      master_code=0
      if [ -s "${LISTING_FOLDER}/file_list_${MISSION}.txt" ]; then
        for f in $(find ${JSONS_FOLDER} -name '*.json'); do
          echo "Pushing "$f" to reprobase"
          python3 -u ${CUR_DIR}/update_base.py -i $f -u ${AUXIP_USER} -pw ${AUXIP_PASS} -m ${MODE}
          code=$?
          if [ $code -ne 0 ]; then
            echo "Reprobase ingestion failed for file "$f
            echo "Reprobase ingestion failed for file "$f >> ${ERROR_FILE_LOG}
            master_code=$code
          fi
        done
      else
        echo "Reprobase Jsons ingestion skipped: no files found on LTA"
        master_code=0
      fi
      if [ $master_code -ne 0 ]; then
        echo "Reprobase ingestion for mission ${MISSION} failed at least one JSON"
        echo "Reprobase ingestion for mission ${MISSION} failed at least one JSON" >> ${ERROR_FILE_LOG}
      fi
  fi
  return $master_code
}

function ingest_mission() {
  # Expecting argument for MISSION to be ingested
  #  From/TO date arguments (with option included) are defined
  #   using global variables
  if [[ $# != 1 ]] ; then
      echo "Called ingest_mission function without MISSION argument"
      exit 1
  fi
  MISSION=$1
  MISSION_TEMP_FOLDER=${TEMP_FOLDER}/$MISSION
  MISSION_TEMP_FOLDER_LISTING=${TEMP_FOLDER_LISTING}/${MISSION}
  MISSION_TEMP_FOLDER_JSONS=${TEMP_FOLDER_JSONS}/${MISSION}
  create_folder $MISSION_TEMP_FOLDER
  create_folder $MISSION_TEMP_FOLDER_LISTING
  create_folder $MISSION_TEMP_FOLDER_JSONS
  echo "Function ingest_mission: Ingesting Mission ${MISSION} with arg ${FROM_DATE_ARG} and ${TO_DATE_ARG}"
  python3 -u ${CUR_DIR}/PRIP_Ingestion.py -m ${MISSION} -lu ${PRIP_ENDPOINT} -u ${PRIP_USER} -pw ${PRIP_PASS} \
        -w ${MISSION_TEMP_FOLDER} \
        -au ${AUXIP_USER} -apw ${AUXIP_PASS}    \
        -fd file_types \
        ${FROM_DATE_ARG} ${TO_DATE_ARG}
  code=$?
  if [ $code -ne 0 ]; then
    echo "PRIP Retrieve failed"
    echo "PRIP Retrieve failed" >> ${ERROR_FILE_LOG}
  fi
  ingest_downloaded_files $MISSION $code "$MISSION_TEMP_FOLDER" "${MISSION_TEMP_FOLDER_LISTING}" "${MISSION_TEMP_FOLDER_JSONS}"
  ingestion_code=$?
  echo "Removing temporary folders"
  if [ $ingestion_code -eq 0 ]; then
    echo "Removing TEMP Folder ${MISSION_TEMP_FOLDER:?}"
    rm -r "${MISSION_TEMP_FOLDER:?}/*"
    echo "Removing TEMP LISTING Folder ${MISSION_TEMP_FOLDER_LISING:?}"
    rm -r ${MISSION_TEMP_FOLDER_LISTING:?}/*
    echo "Removing TEMP Reprobase JSON Folder ${TEMP_FOLDER_JSONS:?}"
    rm -r ${MISSION_TEMP_FOLDER_JSONS:?}/*
  fi
  return $ingestion_code
}
function ingest_mission_types() {
    if [[ $# != 2 ]] ; then
      echo "Called ingest_mission_types function without MISSION  and type list argument"
      exit 1
    fi
    MISSION=$1
    # set -a AUX_TYPES
    AUX_TYPES=$2
    MISSION_TYPE_TEMP_FOLDER=${TEMP_FOLDER}/${AUX_TYPES}
  MISSION_TYPE_TEMP_FOLDER_LISTING=${TEMP_FOLDER_LISTING}/${AUX_TYPES}
  MISSION_TYPE_TEMP_FOLDER_JSONS=${TEMP_FOLDER_JSONS}/${AUX_TYPES}
    mkdir -p ${MISSION_TYPE_TEMP_FOLDER}
    mkdir -p ${MISSION_TYPE_TEMP_FOLDER_LISTING}
    mkdir -p ${MISSION_TYPE_TEMP_FOLDER_JSONS}
    echo "[BEGIN] Function ingest_mission_types: Ingesting Mission ${MISSION} , Types: $AUX_TYPES, with arg ${FROM_DATE_ARG} and ${TO_DATE_ARG}"
    echo "[BEGIN] Function ingest_mission_types: Ingesting Mission ${MISSION} , Types: $AUX_TYPES, with arg ${FROM_DATE_ARG} and ${TO_DATE_ARG}" >> ${ERROR_FILE_LOG}
    python3 -u ${CUR_DIR}/PRIP_Ingestion.py -m ${MISSION} -lu ${PRIP_ENDPOINT}  -u ${PRIP_USER} -pw ${PRIP_PASS} \
          -w ${MISSION_TYPE_TEMP_FOLDER}    \
          -au ${AUXIP_USER} -apw ${AUXIP_PASS}    \
          -t ${AUX_TYPES} \
          ${FROM_DATE_ARG} ${TO_DATE_ARG}
    code=$?
    if [ $code -ne 0 ]; then
      echo "PRIP Retrieve for mission $MISSION, type ${AUX_TYPES} failed"
      echo "PRIP Retrieve  for mission $MISSION, type ${AUX_TYPES} failed (error: $code)" >> ${ERROR_FILE_LOG}
    fi
    ingest_downloaded_files $MISSION $code "${MISSION_TYPE_TEMP_FOLDER}" "${MISSION_TYPE_TEMP_FOLDER_LISTING}" "${MISSION_TYPE_TEMP_FOLDER_JSONS}"
    ingestion_code=$?
    if [ $ingestion_code -eq 0 ]; then
      echo "No errors for $MISSION ingestion"
      echo "Removing temporary folders"
      echo "Removing TEMP Folder ${MISSION_TYPE_TEMP_FOLDER:?}"
      rm -rf "${MISSION_TYPE_TEMP_FOLDER:?}"/*
      REM_RES=$?
      echo "Removal result: $REM_RES"
      echo "Removing TEMP LISTING Folder ${MISSION_TYPE_TEMP_FOLDER_LISTING:?}"
      rm -rf ${MISSION_TYPE_TEMP_FOLDER_LISTING:?}/*
      REM_RES=$?
      echo "Removal result: $REM_RES"
      echo "Removing TEMP Reprobase JSON Folder ${MISSION_TYPE_TEMP_FOLDER_JSONS:?}"
      rm -rf ${MISSION_TYPE_TEMP_FOLDER_JSONS:?}/*
      REM_RES=$?
      echo "Removal result: $REM_RES"

    else
      echo "Ingestion failure - Keeping Temporary files "
    fi
    echo "[END] Completed Ingestion of Mission ${MISSION} , Types: $AUX_TYPES, with arg ${FROM_DATE_ARG} and ${TO_DATE_ARG}"
    echo "[END] Completed Ingestion of Mission ${MISSION} , Types: $AUX_TYPES, with arg ${FROM_DATE_ARG} and ${TO_DATE_ARG}" >> ${ERROR_FILE_LOG}
    return $ingestion_code
}

function ingest_mission_type_by_type() {
  # Expecting argument for MISSION to be ingested
  #  From/TO date arguments (with option included) are defined
  #   using global variables
  if [[ $# != 1 ]] ; then
      echo "Called ingest_mission function without MISSION argument"
      exit 1
  fi
  MISSION=$1
  echo "Function ingest_mission_type_by_type: Ingesting Mission ${MISSION} with arg ${FROM_DATE_ARG} and ${TO_DATE_ARG}"
  # FOr S2, specify types to downldao, instead of specifying the type folder
  set -a MISSION_AUX_TYPES
  MISSION_AUX_TYPES=$(python3 -u ${CUR_DIR}/mission_aux_types.py -m $MISSION -fd ${CUR_DIR}/file_types)
  echo "Retrieved types for mission : $MISSION_AUX_TYPES"
  echo "Retrieved aux types for mission ${MISSION}"
  OIFS=$IFS

  IFS=',' AUX_TYPES_LIST=($MISSION_AUX_TYPES)
  IFS=$OIFS
  echo "TYPES: ${AUX_TYPES_LIST[@]}"
  tt_ingestion_code=0
  for aux_t in "${AUX_TYPES_LIST[@]}"
  do
    echo "[BEG] Ingesting aux type $aux_t for mission $MISSION from $FROM_DATE_ARG to $TO_DATE_ARG"
    ingest_mission_types $mission $aux_t
    t_result=$?
    (( tt_ingestion_code=$t_result||$tt_ingestion_code ))
    echo "[END] Completed Ingestion of  aux type $aux_t for mission $MISSION from $FROM_DATE_ARG to $TO_DATE_ARG"
  done
  echo "Completed Ingesting aux files for mission $MISSION"
  #ingest_mission_types S2 "_UT1UTC_ _ECMWFD_ADG_
  return $tt_ingestion_code
}

echo "Starting PRIP download"
ingestion_code=0
for mission in ${MISSIONS}
do
    echo "Ingesting mission $mission $FROM_DATE_ARG $TO_DATE_ARG"
    #ingest_mission ${mission}
    ingest_mission_type_by_type ${mission}
    result=$?
    (( ingestion_code=$result||$ingestion_code ))
done
# Remove temporary folders if ALL missions have been successful
  #ingestion_code=$?
  echo "Completed all missions ingestion: Removing temporary folders"
  if [ $ingestion_code -eq 0 ]; then
    echo "No Errors Found"
    echo "Removing TEMP Folder ${TEMP_FOLDER:?}"
    rm -rf "${TEMP_FOLDER:?}"/*
    echo "Removing TEMP LISTING Folder ${TEMP_FOLDER_LISTING:?}"
    rm -rf ${TEMP_FOLDER_LISTING:?}/*
    echo "Removing TEMP Reprobase JSON Folder ${TEMP_FOLDER_JSONS:?}"
    rm -rf ${TEMP_FOLDER_JSONS:?}/*
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
