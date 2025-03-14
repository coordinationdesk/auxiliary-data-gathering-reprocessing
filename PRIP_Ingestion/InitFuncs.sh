function init_lta_variables() {
if [ -z ${PRIP_ENDPOINT+x} ]; then
  echo "PRIP_ENDPOINT not set"
  exit 1
fi
echo "PRIP_ENDPOINT: "${PRIP_ENDPOINT}
if [ -z ${PRIP_USER+x} ]; then
  echo "PRIP_USER not set"
  exit 1
fi
echo "PRIP_USER: "${PRIP_USER}
if [ -z ${PRIP_PASS+x} ]; then
  echo "PRIP_PASS not set"
  exit 1
fi
#echo "PRIP_PASS: "${PRIP_PASS}
}
function init_adgs_variables() {
if [ -z ${ADGS_ENDPOINT+x} ]; then
  echo "ADGS_ENDPOINT not set"
  exit 1
fi
echo "ADGS_ENDPOINT: "${ADGS_ENDPOINT}
if [ -z ${ADGS_USER+x} ]; then
  echo "ADGS_USER not set"
  exit 1
fi
echo "ADGS_USER: "${ADGS_USER}
if [ -z ${ADGS_PASS+x} ]; then
  echo "ADGS_PASS not set"
  exit 1
fi
#echo "ADGS_PASS: "${ADGS_PASS}
}
function init_variables() {
if [ -z ${AUXIP_USER+x} ]; then
  echo "AUXIP_USER not set"
  exit 1
fi
echo "AUXIP_USER: "${AUXIP_USER}
if [ -z ${AUXIP_PASS+x} ]; then
  echo "AUXIP_PASS not set"
  exit 1
fi
#echo "AUXIP_PASS: "${AUXIP_PASS}
if [ -z ${MODE+x} ]; then
  echo "MODE not set"
  exit 1
fi
echo "MODE: "${MODE}

if [ $MODE != "prod" ]; then
  echo "Due to IP restriction the PRIP ingestion can't be launched in dev mode"
#  exit 1
fi
#S3 stuff
if [ -z ${S3_ACCESS_KEY+x} ]; then
  echo "S3_ACCESS_KEY not set, no S3"
  MCPATH="mc"
else
  if [ -z ${MCPATH+x} ]; then
   echo "MCPATH not set"
   exit 1
  fi
  echo "MCPATH : "$MCPATH
  #echo "S3_ACCESS_KEY: "${S3_ACCESS_KEY}
  if [ -z ${S3_SECRET_KEY+x} ]; then
   echo "S3_SECRET_KEY not set"
   exit 1
  fi
  echo "S3_SECRET_KEY: "${S3_SECRET_KEY}
  if [ -z ${S3_ENDPOINT+x} ]; then
   echo "S3_ENDPOINT not set"
   exit 1
  fi
  echo "S3_ENDPOINT: "${S3_ENDPOINT}
  if [ -z ${S3_BUCKET+x} ]; then
   echo "S3_BUCKET not set"
   exit 1
  fi
  echo "S3_BUCKET: "${S3_BUCKET}
  STORAGE_ALIAS="wasabi-auxip-archives"
  ${MCPATH} alias set $STORAGE_ALIAS ${S3_ENDPOINT} ${S3_ACCESS_KEY} ${S3_SECRET_KEY} --api S3v4
fi
}

function create_folder() {
  NEW_FOLDER=$1

  if [[ ! -d $NEW_FOLDER ]]; then
    mkdir -p $NEW_FOLDER
    if [[ ! -d $NEW_FOLDER ]]; then
      echo $NEW_FOLDER" folder can't be created and doesnt exists"
      exit 1
    fi
  fi
}


function init_folders() {
  local START_DATE=$1
  ERROR_FILE_LOG="${WORK_FOLDER}/${START_DATE}_PRIP_error.log"
  TEMP_FOLDER=$(mktemp -p $WORK_FOLDER -d)
  echo "TEMP_FOLDER : ${TEMP_FOLDER}" >> $ERROR_FILE_LOG
  TEMP_FOLDER_LISTING=$(mktemp -p $WORK_FOLDER -d)
  echo "TEMP_FOLDER_LISTING : ${TEMP_FOLDER_LISTING}" >> $ERROR_FILE_LOG
  TEMP_FOLDER_JSONS=$(mktemp -p $WORK_FOLDER -d)
  echo "TEMP_FOLDER_JSONS : ${TEMP_FOLDER_JSONS}" >> $ERROR_FILE_LOG

  create_folder $TEMP_FOLDER
  create_folder $TEMP_FOLDER_LISTING
  create_folder $TEMP_FOLDER_JSONS
  echo "Temporary folder : "$TEMP_FOLDER
}

# Verify if other copies of this shell are running
function test_single_exec() {
  # Processes include: containing bash, bash
  if [ $(ps ax | grep $0 | grep -v grep | wc -l) -gt 3 ]; then  
    echo "$0 Already running"
    # echo "ps returned $(ps ax | grep $0 | wc -l) items"
    # echo "ps returned $(ps ax | grep $0 ) items"
    return 1
  fi
  return 0
}

CUR_DIR="$(
  cd "$(dirname "$0")"
  pwd -P
)"

