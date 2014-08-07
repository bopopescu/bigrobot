#!/bin/sh -x
# Description:
#  A convenient wrapper to generate a report and also post it on the web server.
#  You need to modify the "build" variable below.

#build="bvs master aggregated 2014 wk32"
#build="bvs master #beta2_15"
build="bvs master ironhorse beta2 aggregated"


if [ ! -x ../bin/gobot ]; then
    echo "Error: This script must be executed in the bigrobot/catalog/ directory."
    exit 1
fi


usage() {
    if [ $# -ne 0 ]; then
        echo `basename $0`: ERROR: $* 1>&2
    fi
    echo usage: `basename $0` '[-summary] [-detailed] [-no-scp] [-out <file>]' 1>&2
    echo ''
    echo '  -summary  : provide summary report'
    echo '  -detailed : provide detailed report'
    echo '  -no-scp   : do not copy the report (using scp) to the web server'
    echo ''

    exit 1
}


scp_to_web() {
    no_scp=$1
    output=$2
    if [ $is_scp -eq 0 ]; then
        echo ""
        echo "Press Control-C if you don't want to copy the report to the web server..."
        set -x
        scp $output root@qa-tools1.qa.bigswitch.com:/var/www/test_catalog/$output
        echo ""
        echo "Report is available at http://qa-tools1.qa.bigswitch.com/test_catalog/$output"
    fi
}


no_scp=0

ts=`date "+%Y-%m-%d_%H%M%S"`
release=IronHorse
build_str=`echo $build | sed -e 's/#//' -e 's/ /_/g'`
output_summary=raw_data.db_collect_stats.py.${ts}.${build_str}.summary.txt
output_summary_no_timestamp=regression_report.${build_str}.summary.txt
output_detailed=raw_data.db_collect_stats.py.${ts}.${build_str}.detailed.txt
output_detailed_no_timestamp=regression_report.${build_str}.detailed.txt

while :
do
    case "$1" in
    -no-scp) no_scp=1;;
    -summary) summary=1;;
    -detailed) detailed=1;;
    --) shift; break;;
    -h) usage;;
    -help) usage;;
    -*) usage "bad argument $1";;
    *) break;;
    esac
    shift
done

if [ "$summary"x = x -a "$detailed"x = x ]; then
    summary=1
fi

if [ "$summary"x != x ]; then
    output=$output_summary_no_timestamp
    echo "Timestamp: $ts" >> $output
    echo "Build: $build" >> $output
    echo "Output: $output" >> $output
    echo ""
    ./db_collect_stats.py --release $release --build "$build" --show-suites | tee -a $output
    echo ""
    scp_to_web $no_scp $output
fi

if [ "$detailed"x != x ]; then
    output=$output_detailed_no_timestamp
    echo "Timestamp: $ts" >> $output
    echo "Build: $build" >> $output
    echo "Output: $output" >> $output
    echo ""
    ./db_collect_stats.py --release $release --build "$build" --show-suites --show-untested | tee -a $output
    echo ""
    scp_to_web $no_scp $output
fi
