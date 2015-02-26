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

# !!! FIXME: This code is duplicated from populate_db_regression.sh.
if [ "$TEST_CATALOG_LOG_DIR"x = x ]; then
    ts=`date "+%Y-%m-%d_%H%M%S"`
    dest=.data.$ts
    mkdir $dest
    export TEST_CATALOG_LOG_DIR=$dest
    echo "TEST_CATALOG_LOG_DIR='$TEST_CATALOG_LOG_DIR'"
fi

BUILD_NAME="$BUILD_NAME" ./db_remove_build_baselines.py --y
BUILD_NAME="$BUILD_NAME" time ./populate_db_dryrun.sh

