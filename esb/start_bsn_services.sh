#!/bin/sh

app=bsn_services
celery worker --app $app --loglevel info

