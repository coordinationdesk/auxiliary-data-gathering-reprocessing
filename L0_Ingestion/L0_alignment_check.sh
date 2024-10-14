#!/bin/bash
source ${PWD}/InitFuncs.sh


if [[  $# != 4 ]]; then
  echo "Utility script to  check L0 Names alignment vs LTA "
  echo "Usage: $0 <Work Dir> <From Date> <To Date>  <Mission>"
  echo "Date in format: YYYY-mm-dd"
  exit 1
fi
FROM_DATE=$2
TO_DATE=$3
WORK_DIR=$1
REQ_MISSION=$4


if [[ ! -z $REQ_MISSION ]]; then
   # CHeck Mission is valid
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
MISSIONS="S1 S2 S3"
if [[ ! -z ${REQ_MISSION} ]]; then
  echo "Ingesting only Mission  $REQ_MISSION"
    MISSIONS="$REQ_MISSION"
fi
init_lta_variables

create_folder $WORK_DIR


function check_mission() {
MISSION=$1
N_DAYS=$2
echo ""

START_DATE=$FROM_DATE
 
export START_DATE 
while [[ $START_DATE < $TO_DATE ]] ; do 
    echo "Executing  check for $N_DAYS from $START_DATE "
    BATCH_WORK_DIR=$WORK_DIR/Recover_$START_DATE
    mkdir $BATCH_WORK_DIR 
    echo "Execution" 2>&1 | tee /tmp/l0_ingestion/l0_names_check_from_$START_DATE.out
python3 -d l0_names_check_lta.py -m $MISSION -p 5432 -dbn reprocessingdatabaseline -dbu reprocessingdatabaseline -dbp ${REPROCESSINGDATABASELINE_POSTGRES_PASSWORD} -dbh 127.0.0.1 -lu $PRIP_ENDPOINT -u $PRIPS2_USER -pw $PRIPS2_PASS -fd $START_DATE -n $N_DAYS -md Compare 2>&1 | tee /tmp/l0_ingestion/l0_names_check_from_$START_DATE.out
     # export START_DATE=$(date -d "$START_DATE +1 days" +%Y-%m-%d); 
    export START_DATE=$(date -d "$START_DATE +${N_DAYS} days" +%Y-%m-%d); 
    # If Stop date - start date is less than num_days, adjust num_days
done
}


ingestion_code=0
for mission in ${MISSIONS}
do
    NUM_DAYS=30
    if [[ $mission == "S2" ]]; then
       NUM_DAYS=5
    fi
    echo "Checking L0 Names from $FROM_DATE to $TO_DATE $NUM_DAYS days at time for Mission: $mission"
    check_mission ${mission} ${NUM_DAYS}
    result=$?
    (( ingestion_code=$result||$ingestion_code ))
done
read -p "Continue?" ANSWER
if [[ $ANSWER == "N" ]]; then
 exit 1
fi

echo "Check completed"

