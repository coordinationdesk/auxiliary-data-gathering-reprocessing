#!/usr/bin/env bash


# Launch script for the service

CUR_DIR="$( cd "$(dirname "$0")" ; pwd -P )"

echo "Datasource password: "${DATASOURCE_PASSWORD}
echo "S3_ACCESS_KEY: "${S3_ACCESS_KEY}
echo "S3_SECRET_KEY: "${S3_SECRET_KEY}

#java -jar $CUR_DIR/lib/auxip-<version>.jar --spring.config.location=file:$CUR_DIR/conf/ $*
#java -jar $CUR_DIR/lib/auxip-<version>.jar --spring.config.location=file:$CUR_DIR/conf/ -Ddatasource.password=${DATASOURCE_PASSWORD} -Ds3.access_key='${S3_ACCESS_KEY}' $*
java -jar $CUR_DIR/lib/auxip-<version>.jar --spring.config.location=file:$CUR_DIR/conf/application.properties -Ddatasource.password=${DATASOURCE_PASSWORD} -Ds3.secret_key='${S3_ACCESS_KEY}' -D's3.access_key=${S3_ACCESS_KEY}' $*
