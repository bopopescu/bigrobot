#!/bin/sh
# Import all the collections into a Mongo database. You must specify the
# Mongo server, database name, and the directory which contains the collections
# (stored as JSON files).
#
# Example:
#   ./mongoimport_collections.sh \
#           -db-server localhost \
#           -db-name newdb \
#           -input-path mongodb_test_catalog_201410_2014-10-20_133256

if [ ! -x ../bin/gobot ]; then
    echo "Error: This script must be executed in the bigrobot/catalog/ directory."
    exit 1
fi

type mongoexport > /dev/null 2>&1 || { echo >&2 "Mongo client is not installed. Aborting."; exit 1; }

usage() {
    echo "Usage: $0 -db-server <ip> [-db-port <27017>] -db-name <db-name> -input-path <path>"
    exit 0
}

mongo_port=27017
while :
do
    case "$1" in
    -db-server) shift; mongo_server=$1;;
    -db-port) shift; mongo_port=$1;;
    -db-name) shift; database=$1;;
    -input-path) shift; import_path=$1;;
    --) shift; break;;
    -h) usage;;
    -help) usage;;
    -*) usage "bad argument $1";;
    *) break;;
    esac
    shift
done

if [ "$mongo_server"x = x ]; then usage; fi
if [ "$mongo_port"x = x ]; then usage; fi
if [ "$database"x = x ]; then usage; fi
if [ "$import_path"x = x ]; then usage; fi


collections=`(cd $import_path; echo *)`

set -x
for collection in `echo $collections`; do
    input="$import_path/${collection}"
    mongoimport \
        --host $mongo_server \
        --port $mongo_port \
        --db $database \
        --collection $collection \
        --file $input
done

echo "Done."
