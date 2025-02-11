

function ingest_downloaded_files() {
  MISSION=$1
  code=$2
  DWL_TEMP_FOLDER=$3
  LISTING_FOLDER=$4
  echo "Ingesting downloaded files: Download folder: $DWL_TEMP_FOLDER, Listing folder: $LISTING_FOLDER"
  master_code=$code
  if [ $code -eq 0 ]; then
    echo "LTA download completed succesfully: $(ls $DWL_TEMP_FOLDER | wc -l) files downloaded"
    echo "LTA download completed succesfully: $(ls $DWL_TEMP_FOLDER | wc -l) files downloaded" >> ${ERROR_FILE_LOG}
    ls $DWL_TEMP_FOLDER/${MISSION}

    echo "Starting AUXIP ingestion $MISSION"
    #python3 -u ${CUR_DIR}/ingestion/ingestion.py -f -i ${DWL_TEMP_FOLDER} -u ${AUXIP_USER} -pw ${AUXIP_PASS} -mc ${MCPATH} -b "wasabi-auxip-archives/"${S3_BUCKET} -o ${LISTING_FOLDER}/file_list_${MISSION}.txt -m ${MODE}
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
      while read ingested_file ; do
          rm   "${DWL_TEMP_FOLDER}/$ingested_file"
      done < ${LISTING_FOLDER}/file_list_${MISSION}.txt 
      echo "Removed files downloaded from LTA and ingested on AUXIP"
  else
      
      echo "AUXIP ingestion done with some errors"
      echo "Removing files downloaded from LTA ( only those ingested on AUXIP)..."
  fi
  if [  -f ${LISTING_FOLDER}/file_list_${MISSION}.txt ]; then
     master_code=0
     echo "$(wc -l ${LISTING_FOLDER}/file_list_${MISSION}.txt) Files ingested into Auxip"
     echo "$(wc -l ${LISTING_FOLDER}/file_list_${MISSION}.txt) Files ingested into Auxip" >> ${ERROR_FILE_LOG}
  fi
  return $master_code
}
function ingest_reprobase() {
  MISSION=$1
  code=$2
  LISTING_FOLDER=$3
  JSONS_FOLDER=$4
  echo "Ingesting Info about downloaded files to Reprobase: Listing folder: $LISTING_FOLDER, Folder for JSONS: $JSONS_FOLDER"
  master_code=$code
  if [ $master_code -eq 0 ]; then
      if [ -s "${LISTING_FOLDER}/file_list_${MISSION}.txt" ]; then
        echo "[BEG] Starting Reprobase jsons generation for $MISSION"
        echo "[BEG] Starting Reprobase jsons generation for $MISSION" >> ${ERROR_FILE_LOG}
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
      echo "[END] Completed Reprobase jsons generation for $MISSION"
      echo "[END] Completed Reprobase jsons generation for $MISSION" >> ${ERROR_FILE_LOG}
      master_code=$master_code_reprobase
  fi
  # Adding auxip related JSONS into ReproBase 
  if [ $master_code -eq 0 ]; then
      echo "Reprobase json generation done"
      master_code=0
      if [ -s "${LISTING_FOLDER}/file_list_${MISSION}.txt" ]; then
        echo "[BEG] Starting Pushing jsons for $MISSION to Reprobase"
        echo "[BEG] Starting Pushing jsons for $MISSION to Reprobase" >> ${ERROR_FILE_LOG}
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
        echo "Reprobase Jsons ingestion skipped: no files found on FTP REPO"
        master_code=0
      fi
      if [ $master_code -ne 0 ]; then
        echo "Reprobase ingestion for mission ${MISSION} failed at least one JSON"
        echo "Reprobase ingestion for mission ${MISSION} failed at least one JSON" >> ${ERROR_FILE_LOG}
      fi
      echo "[END] Completed Pushing jsons for $MISSION to Reprobase"
      echo "[END] Completed Pushing jsons for $MISSION to Reprobase"  >> ${ERROR_FILE_LOG}
  fi
  return $master_code
}

function ingest_replace_downloaded_files() {
  MISSION=$1
  code=$2
  DWL_TEMP_FOLDER=$3
  LISTING_FOLDER=$4
# Try ingestion/ingestion
# If error: 
# Remove uploaded file
# If not error:
#      Remove aux file from: storage, auxip
#      Remove aux file from Reprobase
#    Generate Reprobase Json, Ingest to Reprobase
  echo "Ingesting/Replacing downloaded files: Download folder: $DWL_TEMP_FOLDER, Listing folder: $LISTING_FOLDER, Folder for JSONS: $JSONS_FOLDER"
  master_code=$code
  if [ $code -eq 0 ]; then
    echo "FTP REPO download done"

    echo "Starting AUXIP ingestion $MISSION"
    # -- TODO -- : Add list of files with errors (Fileanme + UUID)
    python3 -u ${CUR_DIR}/ingestion/replace_aux_products.py -i ${DWL_TEMP_FOLDER} -u ${AUXIP_USER} -pw ${AUXIP_PASS} -mc ${MCPATH} -b "wasabi-auxip-archives/"${S3_BUCKET} -o ${LISTING_FOLDER}/file_list_${MISSION}.txt -e ${LISTING_FOLDER}/error_list_${MISSION}.txt -m ${MODE}
    code=$?
    master_code_auxip=$code
    if [ $code -ne 0 ]; then
       echo "Auxip ingestion failed for Mission ${MISSION} with error $code" 
       echo "Auxip ingestion failed for Mission ${MISSION} with error $code" >> ${ERROR_FILE_LOG}
    fi
    if [ $master_code_auxip -ne 0 ]; then
    # -- TODO -- : If successful, remove RECORDS from REPROBASE
       echo "AUXIP ingestion failed"
       echo "AUXIP ingestion for mission ${MISSION} failed" >> ${ERROR_FILE_LOG}
    fi
    master_code=$master_code_auxip
  if [ $master_code -eq 0 ]; then
      echo "AUXIP ingestion done"
      echo "Removing files downloaded from LTA (Ingested on AUXIP)..."
      rm  -rf "${DWL_TEMP_FOLDER}"
      echo "Removed files downloaded from LTA"
  fi
  fi
  return $master_code
}

