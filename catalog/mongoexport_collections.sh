#!/bin/sh -x
# Export all the collections in a given Mongo database ('database' key
# in catalog.yaml).

if [ ! -x ../bin/gobot ]; then
    echo "Error: This script must be executed in the bigrobot/catalog/ directory."
    exit 1
fi

type mongoexport > /dev/null 2>&1 || { echo >&2 "Mongo client is not installed. Aborting."; exit 1; }

ts=`date "+%Y-%m-%d_%H%M%S"`
config="../configs/catalog.yaml"
mongo_server=`python -c "import yaml; print yaml.load(open('${config}'))['db_server']"`
mongo_port=`python -c "import yaml; print yaml.load(open('${config}'))['db_port']"`
database=`python -c "import yaml; print yaml.load(open('${config}'))['database']"`
export_path="mongodb_${database}_${ts}"

for collection in `./db_get_collection_names.py`; do
    mongoexport \
        --host $mongo_server \
        --port $mongo_port \
        --db $database \
        --collection $collection \
        --out $export_path/$collection
done

echo "Done."
