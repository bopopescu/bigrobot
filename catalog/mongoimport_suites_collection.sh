#!/bin/sh

if [ ! -x ../bin/gobot ]; then
    echo "Error: This script must be executed in the bigrobot/catalog/ directory."
    exit 1
fi

type mongoimport > /dev/null 2>&1 || { echo >&2 "Mongo client is not installed. Aborting."; exit 1; }

collection=test_suites
json_files=$*

config="../configs/catalog.yaml"
mongo_server=`python -c "import yaml; print yaml.load(open('${config}'))['db_server']"`
mongo_port=`python -c "import yaml; print yaml.load(open('${config}'))['db_port']"`
database=`python -c "import yaml; print yaml.load(open('${config}'))['database']"`

set -x
for json_file in $json_files; do
    if [ ! -f $json_file ]; then
        echo "ERROR: JSON file '$json_file' is not found."
        continue
    fi
    echo "*** Mongo importing ${json_file}..."
    mongoimport \
        --host $mongo_server \
        --port $mongo_port \
        --db $database \
        --collection $collection \
        --stopOnError \
        --jsonArray \
        --file $json_file
done
set +x

echo "Done."
