ARG DEBIAN_FRONTEND noninteractive
FROM ubuntu:20.04
MAINTAINER CS SI

ENV TZ=UTC
RUN apt-get update -y \
    && apt-get upgrade -y \
    && apt-get update \
    && apt-get install -y  tzdata \
    && apt-get install -y  --no-install-recommends apt-utils rclone cron ca-certificates lsb-core wget gnupg2 \
    && apt-get install -y  --no-install-recommends python3-requests python3-lxml python3-pip libeccodes-tools \
    && pip3 install cdsapi \
    && apt-get clean 

ADD ingest_s2files.py /
ADD ingestion /ingestion
ADD ECMWF_Ingestion.py /
ADD request_generator.py /
ADD FileUtils.py /
ADD ECMWF_Ingestion.sh /
ADD ECMWF_IngestionReplace.sh /
ADD ECMWF_Recover_Ingestion.sh /
ADD Camsan_Recover.sh /
ADD InitFuncs.sh /
ADD template.json /
ADD hdr_template.xml /
ADD hdr_template_cams.xml /
ADD update_base.py /
ADD get_reprobase_file_types.py /
ADD mc /
ADD file_types.tgz /

RUN chmod a+x /ECMWF_Ingestion.sh
RUN chmod a+x /ECMWF_Recover_Ingestion.sh
RUN chmod a+x /ECMWF_IngestionReplace.sh
RUN chmod a+x /Camsan_Recover.sh 
RUN chmod a+x /mc

#ENTRYPOINT ["/ECMWF_Ingestion.sh"]

ADD ecmwf-cron /etc/cron.d/
ADD setenv.sh /setenv.sh
RUN chmod a+x /setenv.sh \
    && chmod a+x /etc/cron.d/ecmwf-cron \
    && crontab /etc/cron.d/ecmwf-cron

CMD ["/setenv.sh"]
