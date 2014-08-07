#!/bin/sh

usage() {
    echo "Usage: BUILD_NAME=\"bvs master #<id>\" $0 [-force-overwrite]"
    echo ""
    echo "-force-overwrite - Rebuild the baseline data set"
    exit 0
}

if [ ! -x ../bin/gobot ]; then
    echo "Error: This script must be executed in the bigrobot/catalog/ directory."
    exit 1
fi

if [ "$BUILD_NAME"x = x ]; then
    usage
fi

while :
do
    case "$1" in
    -force-overwrite) force_overwrite=1;;
    --) shift; break;;
    -h) usage;;
    -help) usage;;
    -*) usage "bad argument $1";;
    *) break;;
    esac
    shift
done

ts=`date "+%Y-%m-%d_%H%M%S"`
outfile=raw_data.populate_db_aggregated_build.$ts.log


if [ "$force_overwrite"x = 1x ]; then
    echo "Force-overwrite specified. Removing baseline data for '$BUILD_NAME'."
    ./db_remove_build_baselines.py --y
fi
exit 1

./db_chk_build_name.py
if [ $? -eq 0 ]; then
    echo "Baseline data for build '$BUILD_NAME' exists."
else
    echo "No baseline data for build '$BUILD_NAME'. Start collecting baseline."
    time ./populate_db_dryrun.sh
fi

BUILD_NAME="$BUILD_NAME" time ./populate_db_aggregated_build.py > $outfile

