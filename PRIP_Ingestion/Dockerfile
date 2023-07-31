ARG DEBIAN_FRONTEND noninteractive
FROM ubuntu:20.04
MAINTAINER CS SI

ENV TZ=UTC

#    && RUN echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections

RUN apt-get update -y \
    && apt-get upgrade -y \
    && apt-get update \
    && apt-get install -y  tzdata \
    && apt-get install -y  --no-install-recommends apt-utils rclone cron ca-certificates lsb-core wget gnupg2 \
    && apt-get install -y  --no-install-recommends python3-requests python3-lxml python3-pip \
    && pip3 install numpy \
    && apt-get clean

    
ADD ingest_s2files.py /
ADD ingestion /ingestion
ADD PRIP_Ingestion.py /
ADD FileUtils.py /
ADD PRIP_S2.py /
ADD PRIP_Ingestion.sh /
ADD template.json /
ADD update_base.py /
ADD mc /
ADD file_types.tgz /

RUN chmod a+x /PRIP_Ingestion.sh
RUN chmod a+x /mc
ADD prip-cron /etc/cron.d/
ADD setenv.sh /setenv.sh
RUN chmod a+x /setenv.sh \
    && chmod a+x /etc/cron.d/prip-cron \
    && chmod a+x /etc/cron.d/prip-cron \
    && crontab /etc/cron.d/prip-cron

CMD echo "ENTRYPOINT, $S3_ENDPOINT"
CMD ["/setenv.sh"]
