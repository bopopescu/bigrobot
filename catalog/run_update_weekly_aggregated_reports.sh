#!/bin/sh

usage() {
    echo "Usage: $0"
    echo ""
    echo "This wrapper performs the following tasks:"
    echo "  1) generate baseline data for the aggregate"
    echo "  2) populate aggregate with data from various builds"
    echo "  3) generate QA Dashboard reports for the aggregate"
    echo ""
    echo "The BUILD_NAME is not a required argument as it is automatically calculated by looking at the"
    echo "current week number."
    echo ""
    echo "Options:"
    echo "  -no-baseline  : Don't generate baseline data"
    echo "  -no-aggregate : Don't aggregate data from various builds"
    echo "  -no-report    : Don't generate QA Dashboard reports"
    exit 0
}

if [ ! -x ../bin/gobot ]; then
    echo "Error: This script must be executed in the bigrobot/catalog/ directory."
    exit 1
fi

no_baseline=0
no_aggregate=0
no_report=0
do_it=0

while :
do
    case "$1" in
    -no-baseline) no_baseline=1;;
    -no-aggregate) no_aggregate=1;;
    -no-report) no_report=1;;
    -yes) do_it=1;;
    -y) do_it=1;;
    --) shift; break;;
    -h) usage;;
    -help) usage;;
    -*) usage "bad argument $1";;
    *) break;;
    esac
    shift
done

ts=`date "+%Y-%m-%d_%H%M%S"`
year=`../bin/helpers year`
week_num=`../bin/helpers week_num`
export BUILD_NAME="bvs master aggregated ${year} wk${week_num}"

if [ $do_it -eq 0 ]; then
    echo "Did you sync with your git repo? Rerun with option '-y' to proceed."
    exit 1
fi

echo "Start updating data for aggregated build '$BUILD_NAME'..."

if [ $no_baseline -eq 0 ]; then
    ./run_repopulate_build_baseline.sh
fi

if [ $no_aggregate -eq 0 ]; then
    ./run_populate_aggregated_build.sh
fi

if [ $no_report -eq 0 ]; then
    ./gen_report.sh -all
fi

exit 0
