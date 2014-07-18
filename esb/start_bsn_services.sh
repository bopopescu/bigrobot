#!/bin/sh

app=bsn_services
output=$0.$$
#celery worker --app $app --loglevel info --logfile output.log
celery worker --app $app --loglevel info
