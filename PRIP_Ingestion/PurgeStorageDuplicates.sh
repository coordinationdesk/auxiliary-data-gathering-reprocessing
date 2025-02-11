#!/bin/bash 

source ${PWD}/InitFuncs.sh
echo "$# Arguments"
if [ $# -lt 1 ]; then
  echo "$0 duplicates_files_list"
  exit 1
fi

# CHECK IF ANOTHER INSTANCE IS RUNNING
# Processes include: containing bash, bash, and grep
if [ `ps ax | grep $0 | wc -l` -gt 3 ]; then  
  echo "$0 Already running"
create_folder $WORK_FOLDER
#EXECUTION DATE
EXEC_DATE=$(date '+%Y-%m-%d')
  #exit 0
fi


DUPL_FILES=$1
IFS="," DUPL_FILES_LIST=($DUPL_FILES)

# For each input file , execute purge storage duplicates
for dupl_f in ${DUPL_FILES_LIST[@]}; do
 echo $dupl_f;
python3 -u ${CUR_DIR}/ingestion/storage_purge_duplicates.py -au $AUXIP_USER -apw $AUXIP_PASS -mc $MCPATH -m prod -f $dupl_f -o ${dupl_f}.out -b "wasabi-auxip-archives/"${S3_BUCKET}
done
