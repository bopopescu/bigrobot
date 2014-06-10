#!/bin/sh

database=test_catalog2
mongo_server=qadashboard-mongo.bigswitch.com
collections="test_suites test_cases test_cases_archive"
ts=`date "+%Y-%m-%d_%H%M%S"`

for collection in `echo $collections`; do
    out="`basename $0`_${ts}_${collection}"
    mongoexport \
        --host $mongo_server \
        --port 27017 \
        --db $database \
        --collection $collection \
        --out $out
done

echo "Done."
