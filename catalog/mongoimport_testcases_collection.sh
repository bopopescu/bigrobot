#!/bin/sh

if [ ! -x ../bin/gobot ]; then
    echo "Error: This script must be executed in the bigrobot/catalog/ directory."
    exit 1
fi

config="../configs/catalog.yaml"
mongo_server=`python -c "import yaml; print yaml.load(open('${config}'))['db_server']"`
mongo_port=`python -c "import yaml; print yaml.load(open('${config}'))['db_port']"`
database=`python -c "import yaml; print yaml.load(open('${config}'))['database']"`

collection=test_cases

for json_file in `echo test_cases*.json`; do
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

echo "Done."
