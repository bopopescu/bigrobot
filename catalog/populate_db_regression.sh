#!/bin/sh
# Search for all the BigRobot test structured log files (output.xml).
# Parse the log files and populate the test catalog database with the
# test results.
#
# 'infile': If specified, it is a file which contains a list of output.xml
#           files (path included).
#

usage() {
    echo "Usage: BUILD_NAME=\"bvs master #<id>\" $0 <infile>"
    exit 0
}

if [ ! -x ../bin/gobot ]; then
    echo "Error: This script must be executed in the bigrobot/catalog/ directory."
    exit 1
fi

if [ "$BUILD_NAME"x = x ]; then
    usage
fi

# !!! FIXME: This code is duplicated from run_repopulate_build_baseline.sh.
if [ "$TEST_CATALOG_LOG_DIR"x = x ]; then
    ts=`date "+%Y-%m-%d_%H%M%S"`
    dest=.data.$ts
    mkdir $dest
    export TEST_CATALOG_LOG_DIR=$dest
    echo "TEST_CATALOG_LOG_DIR='$TEST_CATALOG_LOG_DIR'"
fi

ts=`date "+%Y-%m-%d_%H%M%S"`

./db_chk_build_name.py
if [ $? -eq 0 ]; then
    echo "Baseline data for build '$BUILD_NAME' exists."
else
    echo "No baseline data for build '$BUILD_NAME'. Start collecting baseline."
    time ./populate_db_dryrun.sh
    ./db_chk_and_add_wk_aggregated_build.py
fi

if [ $# -eq 0 ]; then
    # If ../testlogs exists then look for output.xml there
    if [ -d ../testlogs ]; then
        infile=${TEST_CATALOG_LOG_DIR}/input_list.$ts.txt
        echo "Looking for output.xml files in ../testlogs/ directory."
        find ../testlogs -name output.xml > $infile
        if [ ! -s $infile ]; then
            echo "Did not find any output.xml file."
            exit 0
        fi

        # ... Found a valid output.xml. Proceed with parsing.
        cat $infile

    else
        usage
    fi
else
    infile=$1
fi

progname=`basename $0`
outfile=${TEST_CATALOG_LOG_DIR}/raw_data.${progname}.output.$ts.log

#rm -f test_suites_regression.json test_cases_regression.json

time ./parse_test_xml_output.py \
        --input=$infile \
        --output-suites=${TEST_CATALOG_LOG_DIR}/test_suites_regression.json \
        --output-testcases=${TEST_CATALOG_LOG_DIR}/test_cases_regression.json \
        --is-regression > $outfile 2>&1

