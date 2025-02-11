#!/bin/bash
source InitFuncs.sh
init_variables
function get_storage_list_by_type() {
  OUT_FOLDER=$1

  AUX_TYPE=$2
  TODAY_STR=$(date '+%Y%m%d')
  STORAGE_LIST_FILE="${AUX_TYPE}_Wasabi_${TODAY_STR}.lst"
  echo "Saving to file  ${OUT_FOLDER}/${STORAGE_LIST_FILE}"
  # rclone ls auxip-tpz:auxip --include-from rclon2_r2eqog_filter  > $STORAGE_LIST_FILE
  # Alias is set in init_variables
  ${MCPATH} ls --recursive "${STORAGE_ALIAS}"/${PRIPS2_S3_BUCKET} | grep  ${AUX_TYPE} > ${OUT_FOLDER}/${STORAGE_LIST_FILE}

  echo "Extracted list of $AUX_TYPE files in archive at bucket $PRIPS2_S3_BUCKET"
  #cut -d " " -f 5 ${OUT_FOLDER}/$STORAGE_LIST_FILE | cut -d "/" --output-delimiter="," -f2,1 | sort -t, -k2 | awk -F, -f JoinLinesByKey.awk | awk -F, 'BEGIN {OFS=",";} { print NF-1, $0; }' >  ${OUT_FOLDER}/$STORAGE_LIST_FILE.dupl_count.lst
  awk -F" " '{ print $NF;}'  ${OUT_FOLDER}/$STORAGE_LIST_FILE | cut -d "/" --output-delimiter="," -f2,1 | sort -t, -k2 | awk -F, -f JoinLinesByKey.awk | awk -F, 'BEGIN {OFS=",";} { print NF-1, $0; }' >  ${OUT_FOLDER}/$STORAGE_LIST_FILE.dupl_count.lst

  # extract records for file with duplicates (keep  the first field, the counter)
  egrep -v "^1," ${OUT_FOLDER}/${STORAGE_LIST_FILE}.dupl_count.lst > ${OUT_FOLDER}/${STORAGE_LIST_FILE}.duplicates.lst 
  echo "Extracted list of duplicates (filename + id list)"

  # extract records for file without duplicates (remove the first field, the counter)
  echo "Extracted list of not duplicated (filename + id)"

  egrep "^1," ${OUT_FOLDER}/${STORAGE_LIST_FILE}.dupl_count.lst | cut -d "," -f 2- > ${OUT_FOLDER}/${STORAGE_LIST_FILE}.not_duplicated.lst 

  echo "Done"
}

if [ $# != 1 ]; then
 echo "Please, specifiy Aux Type "
 exit 1
fi

  AUX_TYPE=$1
  TIMESTAMP=$(date '+%Y%m%d%H%M')
TARGET_FOLDER=ARCHIVE_DUPLS_AFTER
mkdir -p ${TARGET_FOLDER}
get_storage_list_by_type ${TARGET_FOLDER} $AUX_TYPE

#python3 storage_purge_duplicates.py -au $AUXIP_USER -apw $AUXIP_PASS -m $MODE -mc $MCPATH -b ${STORAGE_ALIAS}/${PRIPS2_S3_BUCKET}  -f ${STORAGE_LIST_FILE}.duplicates.lst -o ${STORAGE_LIST_FILE}.out  2>&1 | tee /tmp/${AUX_TYPE}_cleanup_${TIMESTAMP}.out

#mkdir -p ${TARGET_FOLDER}
#get_storage_list_by_type ${TARGET_FOLDER} $AUX_TYPE
