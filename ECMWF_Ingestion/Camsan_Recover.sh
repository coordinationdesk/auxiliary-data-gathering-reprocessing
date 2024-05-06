#!/bin/bash
if [[  $# != 3 ]]; then
  echo "Usage: $0 <Work Dir> <From Date> <To Date>"
  echo "Date in format: YYYY-mm-dd"
  exit 1
fi
FROM_DATE=$2
TO_DATE=$3
WORK_DIR=$1
mkdir $WORK_DIR

echo "Recovering CAMSAN from $FROM_DATE to $TO_DATE"
read -p "Continue?" ANSWER
if [[ $ANSWER == "N" ]]; then
 exit 1
fi

NUM_DAYS=14
START_DATE=$FROM_DATE
STOP_DATE=$(date -d "$START_DATE +$NUM_DAYS days" +%Y-%m-%d)
 
export START_DATE STOP_DATE
while [[ $STOP_DATE < $TO_DATE ]] ; do 
    echo "Executing from $START_DATE to $STOP_DATE"
    mkdir $WORK_DIR/Recover_$START_DATE
    /ECMWF_IngestionReplace.sh $WORK_DIR/Recover_$START_DATE 2>&1 | tee /ecmwf/C_camsan_recover_from_$START_DATE.out
    echo "Execution" 2>&1 | tee /ecmwf/C_camsan_recover_from_$DATE1.out
    export START_DATE=$(date -d "$STOP_DATE +1 days" +%Y-%m-%d); 
    export STOP_DATE=$(date -d "$START_DATE +$NUM_DAYS days" +%Y-%m-%d); 
done
echo "Recover completed"

