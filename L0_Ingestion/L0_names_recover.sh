#!/bin/bash
if [[  $# != 4 ]]; then
  echo "Utility script to  ingest L0 Names in the past"
  echo "Usage: $0 <Work Dir> <From Date> <To Date>  <Mission>"
  echo "Date in format: YYYY-mm-dd"
  exit 1
fi
FROM_DATE=$2
TO_DATE=$3
WORK_DIR=$1
MISSION=$4
mkdir $WORK_DIR

NUM_DAYS=5
echo "Recovering L0 Names from $FROM_DATE to $TO_DATE $NUM_DAYS days at time for Mission: $MISSION"
read -p "Continue?" ANSWER
if [[ $ANSWER == "N" ]]; then
 exit 1
fi

echo ""

START_DATE=$FROM_DATE
 
export START_DATE 
while [[ $START_DATE < $TO_DATE ]] ; do 
    echo "Executing  ingestion for $NUM_DAYS from $START_DATE "
    BATCH_WORK_DIR=$WORK_DIR/Recover_$START_DATE
    mkdir $BATCH_WORK_DIR 
    $PWD/L0_Ingestion.sh $BATCH_WORK_DIR $START_DATE $NUM_DAYS $MISSION 2>&1 | tee /tmp/l0_ingestion/l0_names_recover_from_$START_DATE.out
    echo "Execution" 2>&1 | tee /tmp/l0_ingestion/l0_names_recover_from_$START_DATE.out
     # export START_DATE=$(date -d "$START_DATE +1 days" +%Y-%m-%d); 
    export START_DATE=$(date -d "$START_DATE +${NUM_DAYS} days" +%Y-%m-%d); 
    # If Stop date - start date is less than num_days, adjust num_days
done
echo "Recover completed"

