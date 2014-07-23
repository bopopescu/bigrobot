#!/bin/sh

app=bsn_services
output=$0.$$
#celery worker --app $app --loglevel info --logfile output.log
#celery worker --app $app --loglevel info --config=celery_init
set -x
celery -A bsn_services worker --app bsn_services.celery_app:app --loglevel info
