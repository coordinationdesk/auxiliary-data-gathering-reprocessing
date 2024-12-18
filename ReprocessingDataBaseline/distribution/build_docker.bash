#!/usr/bin/env bash
VERSION="1.1.0"


CUR_DIR="$( cd "$(dirname "$0")" ; pwd -P )"

shopt -s extglob 

docker image inspect global_build:01.00.00 > /dev/null
if [ $? -ne 0 ]; then
    echo "Building docker for build"
    cd ${CUR_DIR}/../../Utilities/DockerBuild
    docker build -t global_build:01.00.00 .
fi

docker image inspect global_exec:01.00.00 > /dev/null
if [ $? -ne 0 ]; then
    echo "Building docker for build"
    cd ${CUR_DIR}/../../Utilities/DockerExec
    docker build -t global_exec:01.00.00 .
fi

cd ${CUR_DIR}/docker_build

rm -r source*

mkdir source
cp -r ../../../ReprocessingDataBaseline/!(distribution) source/

docker run --rm -v ${CUR_DIR}/docker_build/source:/source global_build:01.00.00


cd ${CUR_DIR}

cd docker_binary

[ -d tmp_dir ] && rm -r tmp_dir

mkdir tmp_dir


cp -r ReprocessingData-template tmp_dir/ReprocessingData-${VERSION}

mkdir tmp_dir/ReprocessingData-${VERSION}/lib

cp ../docker_build/source/target/*.jar tmp_dir/ReprocessingData-${VERSION}/lib/

sed -i 's+<version>+'${VERSION}'+'  tmp_dir/ReprocessingData-${VERSION}/launch.bash

cp Dockerfile tmp_dir/
sed -i 's+<version>+'${VERSION}'+g'  tmp_dir/Dockerfile

cd tmp_dir 
tar cvzf  ReprocessingData-${VERSION}.tar.gz  ReprocessingData-${VERSION}

docker build -t reprocessing_data_baseline:${VERSION} .

cd ${CUR_DIR}
