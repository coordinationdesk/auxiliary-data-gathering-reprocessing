#!/usr/bin/env bash
VERSION="0.0.2"


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

cd  ${CUR_DIR}/build_package

rm -rf source

mkdir source
cp -r ${CUR_DIR}/../../AUXIP_OLINGO/!(distribution) source/

docker run --rm -v ${CUR_DIR}/build_package/source:/source global_build:01.00.00


cd ${CUR_DIR}

cd build_docker

[ -d tmp_dir ] && rm -r tmp_dir

mkdir tmp_dir



cp -r Auxip-template tmp_dir/Auxip-${VERSION}

mkdir  tmp_dir/Auxip-${VERSION}/lib

cp ../build_package/source/target/auxip-*.jar tmp_dir/Auxip-${VERSION}/lib/

sed -i 's+<version>+'${VERSION}'+'  tmp_dir/Auxip-${VERSION}/launch.bash

cp Dockerfile tmp_dir/
sed -i 's+<version>+'${VERSION}'+g'  tmp_dir/Dockerfile

cd tmp_dir 
tar cvzf  Auxip-${VERSION}.tar.gz  Auxip-${VERSION}

docker build -t auxip_olingo:${VERSION} .

cd ${CUR_DIR}
