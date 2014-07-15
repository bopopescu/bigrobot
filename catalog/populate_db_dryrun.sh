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
outfile=raw_data.`basename $0`_output.$ts.log

./_doit.sh > $outfile 2>&1