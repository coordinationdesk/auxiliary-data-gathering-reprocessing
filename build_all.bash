#!/usr/bin/env bash


CUR_DIR="$( cd "$(dirname "$0")" ; pwd -P )"


cd ${CUR_DIR}/AUXIP_OLINGO/distribution

./build_docker.bash

cd ${CUR_DIR}/ReproBaseAPI/distribution/build/

./build_docker.bash

#cd ${CUR_DIR}/AUXIP/distribution

#./build_docker.bash

cd ${CUR_DIR}/RollingArchive

docker build -t rollingarchive:1.0.0 .

cd ${CUR_DIR}/ReprocessingDataBaseline/distribution

./build_docker.bash

cd ${CUR_DIR}/BackupPosgres

docker build -t backup_postgres:1.0.0 .


cd ${CUR_DIR}/PRIP_Ingestion

docker build -t prip_ingestion:1.1.1 .
docker build -f Dockerfile.adgs -t adgs_ingestion:1.1.0 .

cd ${CUR_DIR}/ECMWF_Ingestion

docker build -t ecmwf_ingestion:1.0.1 .

cd ${CUR_DIR}/L0_Ingestion

docker build -t l0_ingestion:1.0.0 .


cd ${CUR_DIR}

