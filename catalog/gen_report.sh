#!/bin/sh
# Description:
#  A convenient wrapper to generate a report and also post it on the web server.
#  You need to modify the "build" variable below.

#build="bvs master #2.0.0-beta1-SNAPSHOT"
#build="bvs master #beta1-31"
#build="bvs master #2287"
#build="bvs master #bcf_vft-hash-reconcile_10"
#build="bvs master #2502"
#build="bvs master ironhorse beta1 aggregated"
build="bvs master #2685"
#build="bvs master #2710"
#build="bvs master #2742"
#build="bvs master aggregated 2014 wk31"


usage() {
    if [ $# -ne 0 ]; then
        echo `basename $0`: ERROR: $* 1>&2
    fi
    echo usage: `basename $0` '[-no-scp]' 1>&2
    exit 1
}


no_scp=0

while :
do
    case "$1" in
    -no-scp) no_scp=1;;
    --) shift; break;;
    -h) usage;;
    -help) usage;;
    -*) usage "bad argument $1";;
    *) break;;
    esac
    shift
done

build_str=`echo $build | sed -e 's/#//' -e 's/ /_/g'`
if [ ! -x ../bin/gobot ]; then
    echo "Error: This script must be executed in the bigrobot/catalog/ directory."
    exit 1
fi

ts=`date "+%Y-%m-%d_%H%M%S"`

release=IronHorse
output=raw_data.db_collect_stats.py.${ts}.${build_str}.txt
output_no_timestamp=regression_report.${build_str}.txt

echo "Timestamp: $ts" >> $output
echo "Build: $build" >> $output
echo "Output: $output" >> $output

#./db_collect_stats.py --release $release --build "$build" | tee -a $output
#./db_collect_stats.py --release $release --build "$build" --show-suites | tee -a $output
./db_collect_stats.py --release $release --build "$build" --show-suites --no-show-functional-areas | tee -a $output
#./db_collect_stats.py --release $release --build "$build" --show-untested | tee -a $output
#./db_collect_stats.py --release $release --build "$build" --show-untested --show-suites | tee -a $output

echo ""

if [ $no_scp -eq 0 ]; then
    echo ""
    echo "Press Control-C if you don't want to copy the report to the web server..."
    scp $output root@qa-tools1.qa.bigswitch.com:/var/www/test_catalog/$output_no_timestamp
    echo ""
    echo "Report is available at http://qa-tools1.qa.bigswitch.com/test_catalog/$output_no_timestamp"
fi
