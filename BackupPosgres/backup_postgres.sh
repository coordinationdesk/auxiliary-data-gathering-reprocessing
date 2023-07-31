#!/bin/bash

CUR_DIR="$( cd "$(dirname "$0")" ; pwd -P )"
CUR_DIR="$( cd "$(dirname "$0")" ; pwd -P )"

if [ $# -lt 1 ]; then
    echo "backup_postgres.sh REP_BACKUP"
    exit 1
fi

echo "RCLONE_CONFIG_WASABI_SECRET_ACCESS_KEY: "${RCLONE_CONFIG_WASABI_SECRET_ACCESS_KEY}
echo "RCLONE_CONFIG_WASABI_ACCESS_KEY_ID: "${RCLONE_CONFIG_WASABI_ACCESS_KEY_ID}
echo "RCLONE_CONFIG_WASABI_BUCKET: "${RCLONE_CONFIG_WASABI_BUCKET}
echo "REPROBASE_POSTGRES_PASSWORD: "${REPROBASE_POSTGRES_PASSWORD}
echo "AUXIP_POSTGRES_PASSWORD: "${AUXIP_POSTGRES_PASSWORD}
echo "REPROCESSINGDATABASELINE_POSTGRES_PASSWORD: "${REPROCESSINGDATABASELINE_POSTGRES_PASSWORD}
BACKUP_FOLDER=$1
BUCKET=${RCLONE_CONFIG_WASABI_BUCKET}

#verify stuffs
if [[ ! -d ${BACKUP_FOLDER} ]];then
    echo ${BACKUP_FOLDER}" folder doesn't exists"
    exit 1
fi

AUXIP_BACKUP=${BACKUP_FOLDER}/AUXIP
REPROBASE_BACKUP=${BACKUP_FOLDER}/REPROBASE
REPROCESSINGDATABASELINE_BACKUP=${BACKUP_FOLDER}/REPROCESSINGDATABASELINE


mkdir -p ${AUXIP_BACKUP}
mkdir -p ${REPROBASE_BACKUP}
ERROR_FOLDER=$BACKUP_FOLDER/errors
mkdir -p ${ERROR_FOLDER}
ERROR_BUCKET_FOLDER=$BACKUP_FOLDER/errors_bucket
mkdir -p ${ERROR_BUCKET_FOLDER}


cd ${AUXIP_BACKUP}
DUMP_FILE=dump_auxip_`date +%d-%m-%Y"_"%H_%M_%S`.gz
export PGPASSWORD=${AUXIP_POSTGRES_PASSWORD};pg_dumpall -c -U auxip -d 'postgresql://database_auxip_olingo/auxip' | gzip > ${DUMP_FILE}

code=$?
if [ $code -ne 0 ]; then
    echo "Error while connecting to database"
    if [-f "${DUMP_FILE}" ]; then
       mv dump_auxip_*gz ${ERROR_BUCKET_FOLDER}
    fi
else
    if [ ! -z "${RCLONE_CONFIG_WASABI_SECRET_ACCESS_KEY}" ]; then
	if [ -z "${BUCKET}" ]; then
	    echo "No RCLONE_CONFIG_WASABI_BUCKET found in env"
	    mv dump_auxip_*gz ${ERROR_BUCKET_FOLDER}
	else
	    #tar the whole stuff
	    rclone copy dump_auxip*gz wasabi:${BUCKET}/
	    code=$?
	    if [ $code -ne 0 ]; then
		echo "RCLONE failed to transfer"
		mv dump_auxip*gz ${ERROR_BUCKET_FOLDER}
	    else
		rm dump_auxip*gz
	    fi
	fi
    else
	echo "No RCLONE_CONFIG_WASABI_SECRET_ACCESS_KEY found in env"
	rm ${ERROR_FOLDER}/dump_auxip*gz
	mv dump_auxip_*gz ${ERROR_FOLDER}
    fi
fi

cd ${REPROBASE_BACKUP}
DUMP_FILE=dump_reprobaseline_`date +%d-%m-%Y"_"%H_%M_%S`.gz


export PGPASSWORD=${REPROBASE_POSTGRES_PASSWORD};pg_dumpall -c -U reprobaseline -d 'postgresql://database/reprobaseline' | gzip  > ${DUMP_FILE}

code=$?
if [ $code -ne 0 ]; then
    echo "Error while connecting to database"
    if [-f "${DUMP_FILE}" ]; then
       mv dump_reprobaseline_*gz ${ERROR_BUCKET_FOLDER}
    fi
else
    if [ ! -z "${RCLONE_CONFIG_WASABI_SECRET_ACCESS_KEY}" ]; then
	if [ -z "${BUCKET}" ]; then
	    echo "No RCLONE_CONFIG_WASABI_BUCKET found in env"
	    mv dump_reprobaseline_*gz ${ERROR_BUCKET_FOLDER}
	else
	    rclone copy dump_reprobaseline*gz wasabi:${BUCKET}/
	    code=$?
	    if [ $code -ne 0 ]; then
		echo "RCLONE failed to transfer"
		mv dump_reprobaseline*gz ${ERROR_BUCKET_FOLDER}
	    else
		rm dump_reprobaseline*gz
	    fi
	fi
    else
	echo "No RCLONE_CONFIG_WASABI_SECRET_ACCESS_KEY found in env"
	rm ${ERROR_FOLDER}/dump_reprobaseline*gz
	mv dump_reprobaseline*gz ${ERROR_FOLDER}
    fi
fi

if [ `date +%d` -lt 8 ]; then
	# The backup is launched every saturday, and we need to launch the backup of the ReprocessingDataBaseline once a month

	cd ${REPROCESSINGDATABASELINE_BACKUP}
	DUMP_FILE=dump_reprocessingdatabaseline_`date +%d-%m-%Y"_"%H_%M_%S`.gz

	export PGPASSWORD=${REPROCESSINGDATABASELINE_POSTGRES_PASSWORD};pg_dumpall -c -U reprocessingdatabaseline -d 'postgresql://database_reprocessing/reprocessingdatabaseline' |  gzip > ${DUMP_FILE}

	code=$?
	if [ $code -ne 0 ]; then
		echo "Error while connecting to database"
		if [-f "${DUMP_FILE}" ]; then
		mv dump_reprocessingdatabaseline_*gz ${ERROR_BUCKET_FOLDER}
		fi
	else
		if [ ! -z "${RCLONE_CONFIG_WASABI_SECRET_ACCESS_KEY}" ]; then
		if [ -z "${BUCKET}" ]; then
			echo "No RCLONE_CONFIG_WASABI_BUCKET found in env"
			mv dump_reprocessingdatabaseline_*gz ${ERROR_BUCKET_FOLDER}
		else
			rclone copy dump_reprocessingdatabaseline_*gz wasabi:${BUCKET}/
			code=$?
			if [ $code -ne 0 ]; then
			echo "RCLONE failed to transfer"
			mv dump_reprocessingdatabaseline_*gz ${ERROR_BUCKET_FOLDER}
			else
			rm dump_reprocessingdatabaseline_*gz
			fi
		fi
		else
		echo "No RCLONE_CONFIG_WASABI_SECRET_ACCESS_KEY found in env"
		rm ${ERROR_FOLDER}/dump_reprocessingdatabaseline_*gz
		mv dump_reprocessingdatabaseline_*gz ${ERROR_FOLDER}
		fi
	fi
fi

cd ${CUR_DIR}


echo "Done !!"
