#!/bin/sh
# Description:
#    Generate baseline test suites and test cases for the specified build.
#    This should be done as the first step for every new build.

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

if [ "$TEST_CATALOG_LOG_DIR"x = x ]; then
    echo "Error: Env var TEST_CATALOG_LOG_DIR is not defined."
    exit 1
fi

ts=`date "+%Y-%m-%d_%H%M%S"`
outfile=${TEST_CATALOG_LOG_DIR}/raw_data.`basename $0`_output.$ts.log
errfile=${TEST_CATALOG_LOG_DIR}/raw_data.`basename $0`_errors.$ts.log

#./mv_logs.sh
./db_chk_and_add_build_name.py
./_doit.sh > $outfile 2>&1

server=`uname -n`
pwd=`pwd`
logfile="${server}:${pwd}/$outfile"
if [ "$BUILD_URL"x = x ]; then
     build_url=None
else
     build_url=$BUILD_URL
fi

../bin/send_mail.py \
    --sender vui.le@bigswitch.com \
    --receiver bigrobot_stats_collection@bigswitch.com \
    --subject "Dashboard baseline: '$BUILD_NAME'" \
    --message "Script executed: $0
User: $USER
Log file: $logfile
BUILD_URL: $build_url" \
    --infile $outfile

# Reporting potential test suite errors
# grep -n -e "ERROR" -e "^Exception" -e "traceback" $outfile > $errfile
grep -n -e "ERROR" -e "^Exception" -e "traceback" *.log > $errfile
if [ -s $errfile ]; then
    ../bin/send_mail.py \
        --sender vui.le@bigswitch.com \
        --receiver bigrobot_stats_collection@bigswitch.com \
        --subject "ERROR in Dashboard baseline: '$BUILD_NAME'" \
        --message "Log file: $logfile
BUILD_URL: $build_url" \
        --infile $errfile
fi

