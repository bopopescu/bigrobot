#!/bin/sh

database=test_catalog
collection=test_cases
mongo_server=qadashboard-mongo.bigswitch.com

for json_file in `echo test_cases*.json`; do
    echo "*** Mongo importing ${json_file}..."
    mongoimport \
        --host $mongo_server \
        --port 27017 \
        --db $database \
        --collection $collection \
        --stopOnError \
        --jsonArray \
        --file $json_file
done

echo "Done."
