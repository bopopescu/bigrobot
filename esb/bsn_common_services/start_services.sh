#!/bin/sh
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
hostname=`uname -n`
set -x
export BIGROBOT_ESB=True
(celery -A $app worker --app $app.celery_app:app --hostname $hostname --loglevel info -n $app 2>&1 | tee -a $log)
set +x