#!/usr/bin/env bash
VERSION="1.0"

shopt -s extglob

CUR_DIR="$( cd "$(dirname "$0")" ; pwd -P )"

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

rm -rf source
rm -rf source_jpadatasource

mkdir source
cp -r ${CUR_DIR}/../../../ReproBaseAPI/!(distribution) source/
mkdir source_jpadatasource
cp -r ${CUR_DIR}/../../../JPADatasource/* source_jpadatasource/


docker run --rm -v ${CUR_DIR}/docker_build/source:/source -v ${CUR_DIR}/docker_build/source_jpadatasource:/source_datasource global_build:01.00.00


cd ${CUR_DIR}

cd docker_binary

[ -d tmp_dir ] && rm -r tmp_dir

mkdir tmp_dir



cp -r ReproBaseline-template tmp_dir/ReproBaseline-${VERSION}

mkdir tmp_dir/ReproBaseline-${VERSION}/lib

cp ../docker_build/source/rba-service/target/rba-service-*.jar tmp_dir/ReproBaseline-${VERSION}/lib/

sed -i 's+<version>+'${VERSION}'+'  tmp_dir/ReproBaseline-${VERSION}/launch.bash

cp Dockerfile tmp_dir/
sed -i 's+<version>+'${VERSION}'+g'  tmp_dir/Dockerfile

cd tmp_dir 
tar cvzf  ReproBaseline-${VERSION}.tar.gz  ReproBaseline-${VERSION}

docker build -t reprobaseline:${VERSION} .

cd ${CUR_DIR}
