FROM ubuntu:22.04
MAINTAINER CS SI

ADD backup_postgres.sh /
ADD rclone.conf /root/.config/rclone/

RUN chmod a+x /backup_postgres.sh
RUN apt-get update -y \
    && apt-get upgrade -y \
    && apt-get install -y  --no-install-recommends apt-utils rclone cron ca-certificates lsb-core wget gnupg2 \
    && apt-get clean \
    && sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list' \
    && wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - \
    && apt-get update \
    && apt-get install -y  --no-install-recommends postgresql-client
    

ADD rolling-cron /etc/cron.d/
ADD setenv.sh /setenv.sh
RUN chmod a+x /setenv.sh \
    && chmod a+x /etc/cron.d/rolling-cron \
    && chmod a+x /etc/cron.d/rolling-cron \
    && crontab /etc/cron.d/rolling-cron

CMD ["/setenv.sh"]

#ENTRYPOINT ["/bin/bash"]
