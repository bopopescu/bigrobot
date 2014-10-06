#!/bin/sh -x

if [ ! -x ../bin/gobot ]; then
    echo "Error: This script must be executed in the bigrobot/catalog/ directory."
    exit 1
fi

type mongoexport > /dev/null 2>&1 || { echo >&2 "Mongo client is not installed. Aborting."; exit 1; }

config="../configs/catalog.yaml"
mongo_server=`python -c "import yaml; print yaml.load(open('${config}'))['db_server']"`
mongo_port=`python -c "import yaml; print yaml.load(open('${config}'))['db_port']"`
database=`python -c "import yaml; print yaml.load(open('${config}'))['database']"`

collections="test_suites test_cases test_cases_archive"
ts=`date "+%Y-%m-%d_%H%M%S"`

for collection in `echo $collections`; do
    out="`basename $0`_${ts}_${collection}"
    mongoexport \
        --host $mongo_server \
        --port $mongo_port \
        --db $database \
        --collection $collection \
        --out $out
done

echo "Done."
