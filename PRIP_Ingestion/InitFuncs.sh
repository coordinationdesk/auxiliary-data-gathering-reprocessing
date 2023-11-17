function init_variables() {
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
  ${MCPATH} alias set "wasabi-auxip-archives" ${S3_ENDPOINT} ${S3_ACCESS_KEY} ${S3_SECRET_KEY} --api S3v4
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
  START_DATE=$1
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

CUR_DIR="$(
  cd "$(dirname "$0")"
  pwd -P
)"

