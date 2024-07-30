ARG DEBIAN_FRONTEND noninteractive
FROM ubuntu:20.04

MAINTAINER CS SI

ENV TZ=UTC

#    && RUN echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections

RUN apt-get update -y \
    && apt-get upgrade -y \
    && apt-get install -y  tzdata unzip \
    && apt-get install -y  --no-install-recommends apt-utils cron ca-certificates lsb-core wget gnupg2 \
    && apt-get install -y  --no-install-recommends python3-requests python3-lxml python3-pip \
    && pip install  psycopg2-binary \
    && apt-get clean

    
ADD baseline_l0.py time_formats.py L0_Fields_parse.py /

ADD InitFuncs.sh L0_Ingestion.sh /

RUN chmod a+x /L0_Ingestion.sh
ADD l0names-cron /etc/cron.d/
ADD setenv.sh /setenv.sh
RUN chmod a+x /setenv.sh \
    && chmod a+x /etc/cron.d/l0names-cron 
#\
#    && crontab /etc/cron.d/l0names-cron

CMD ["/setenv.sh"]
