#!/bin/sh

usage() {
    echo "Usage: BUILD_NAME=\"bvs master #<id>\" $0"
    exit 0
}

if [ ! -x ../bin/gobot ]; then
    echo "Error: This script must be executed in the bigrobot/catalog/ directory."
    exit 1
fi

if [ "$BUILD_NAME"x = x ]; then
    usage
fi

ts=`date "+%Y-%m-%d_%H%M%S"`
outfile=raw_data.populate_db_aggregated_build.$ts.log

#BUILD_NAME="$BUILD_NAME" ./db_remove_build_baselines.py --y
BUILD_NAME="$BUILD_NAME" time ./populate_db_dryrun.sh
BUILD_NAME="$BUILD_NAME" time ./populate_db_aggregated_build.py > $outfile

