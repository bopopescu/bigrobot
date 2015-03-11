#!/bin/bash
# Description:
#  A wrapper script to start up the Celery process to put your tasks into
#  service. This is intended for developing new services in a user sandbox
#  and not production.

if [ ! -f celery_app.py ]; then
    echo "ERROR: This script can only be executed within the ESB services directory."
    exit 1
fi

pwd=`pwd`
app=`basename $pwd`
set -x
export BIGROBOT_ESB=True
export BIGROBOT_LOG_PATH='/tmp/bigrobot_esb_log'
log=${BIGROBOT_LOG_PATH}/start_services-${app}.log
cd ..
(celery -A $app worker --app $app.celery_app:app --loglevel info -n $app 2>&1 | tee -a $log)
set +x