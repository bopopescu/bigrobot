#!/bin/sh
# Description:
#  A convenient wrapper to generate a report and also post it on the web server.
#  To specify the build info, you can modify the "build" variable below or
#  set the env BUILD_NAME.

if [ ! -x ../bin/gobot ]; then
    echo "Error: This script must be executed in the bigrobot/catalog/ directory."
    exit 1
fi


usage() {
    if [ $# -ne 0 ]; then
        echo `basename $0`: ERROR: $* 1>&2
    fi
    echo "Usage: [RELEASE_NAME=\"<release>\"] BUILD_NAME=\"bvs master #<id>\" `basename $0` [-summary] [-detailed] [-all] [-no-scp] [-out <file>]"
    echo ''
    echo 'If RELEASE_NAME is specified then generate report only for that release.'
    echo 'If RELEASE_NAME is not specified then derive the product name from BUILD_NAME,'
    echo '  then generate reports for all releases for that product.'
    echo ''
    echo 'Arguments:'
    echo '  -summary  : provide summary report'
    echo '  -detailed : provide detailed report'
    echo '  -all      : equivalent to -summary and -detailed'
    echo '  -no-scp   : do not copy the report (using scp) to the web server'
    echo ''

    exit 1
}


scp_to_web() {
    no_scp=$1
    src=$2
    dst=$3
    server=qa-tools1.qa.bigswitch.com
    if [ $no_scp -eq 0 ]; then
        echo ""
        echo "Press Control-C if you don't want to copy the report to the web server..."
        set -x
        ../bin/passwordless_scp $server $src /var/www/test_catalog/$dst
        echo ""
        echo "Report is available at http://$server/test_catalog/$dst"
    fi
}


if [ "$BUILD_NAME"x = x ]; then
    usage
fi

while :
do
    case "$1" in
    -no-scp) no_scp=1;;
    -all) summary=1; detailed=1;;
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

build=$BUILD_NAME
no_scp=0
ts=`date "+%Y-%m-%d_%H%M%S"`
build_str=`echo $build | sed -e 's/#//' -e 's/ /_/g'`


if [ "$RELEASE_NAME"x = x ]; then
    releases=`./db_get_releases_for_build_name.py`
else
    releases=$RELEASE_NAME
fi

for release in $releases; do
    RELEASE_NAME=$release
    export RELEASE_NAME
    release_str=$RELEASE_NAME

    output_summary=raw_data.db_collect_stats.py.${ts}.${build_str}.${release_str}.summary.txt
    output_summary_no_timestamp=regression_report.${build_str}.${release_str}.summary.txt
    output_detailed=raw_data.db_collect_stats.py.${ts}.${build_str}.${release_str}.detailed.txt
    output_detailed_no_timestamp=regression_report.${build_str}.${release_str}.detailed.txt

    echo "Generating stats for build '$build' (release '$release')..."

    if [ "$summary"x != x ]; then
        output=$output_summary
        echo "Timestamp: $ts" >> $output
        echo "Build:     $build" >> $output
        echo "Release:   $release" >> $output
        echo "Output:    $output" >> $output
        echo ""
        ./db_collect_stats.py --release $release --build "$build" --show-suites | tee -a $output
        echo ""
        gzip -9 $output
        scp_to_web $no_scp ${output}.gz ${output_summary_no_timestamp}.gz
    fi

    if [ "$detailed"x != x ]; then
        output=$output_detailed
        echo "Timestamp: $ts" >> $output
        echo "Build: $build" >> $output
        echo "Output: $output" >> $output
        echo ""
        ./db_collect_stats.py --release $release --build "$build" --show-suites --show-untested --show-manual | tee -a $output
        echo ""
        gzip -9 $output
        scp_to_web $no_scp ${output}.gz ${output_detailed_no_timestamp}.gz
    fi

done