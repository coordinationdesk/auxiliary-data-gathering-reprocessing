#!/bin/bash
# Expect two date arguments and working folder
if [ $# != 3 ]; then
   echo "Expected 3 arguments: START_DATE STOP_DATE WORKING_FOLDER"
   exit -1
fi
# execute ingestion with these two date arguments
START_DATE=$1 STOP_DATE=$2 ./ECMWF_Ingestion.sh $3
