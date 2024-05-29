#!/usr/bin/env bash


CUR_DIR="$( cd "$(dirname "$0")" ; pwd -P )"


rm -rf ${CUR_DIR}/AUXIP_OLINGO/distribution/build_docker/tmp_dir
rm -rf ${CUR_DIR}/AUXIP_OLINGO/distribution/build_package/source

rm -rf ${CUR_DIR}/ReproBaseAPI/distribution/build/docker_binary/tmp_dir
rm -rf ${CUR_DIR}/ReproBaseAPI/distribution/build/docker_build/source*

rm -rf ${CUR_DIR}/ReprocessingDataBaseline/distribution/docker_binary/tmp_dir
rm -rf ${CUR_DIR}/ReprocessingDataBaseline/distribution/docker_build/source



