#!/bin/sh -x
# Usage:
#   $ cd .../bigrobot/catalog
#   $ ./run_suites.sh dump_suites_by_areas.sh.T5.text_files
# Description:
#   Take an input file which contains a list of test suites (with full path).
#   Then execute Gobot dryrun against these files to produce the Robot data
#   file (output.xml).
# Assumptions:
#   - This script can only be executed inside the bigrobot/catalog/ directory.

usage() {
    echo "Usage: $0 <input_file>"
    exit 0
}

# !!! FIXME: This code is duplicated from run_repopulate_build_baseline.sh.
# This is really not neccessary since it's primarily catalog/_doit.sh which
# calls this script.
if [ "$TEST_CATALOG_LOG_DIR"x = x ]; then
    ts=`date "+%Y-%m-%d_%H%M%S"`
    dest=.data.$ts
    mkdir $dest
    export TEST_CATALOG_LOG_DIR=$dest
    echo "TEST_CATALOG_LOG_DIR='$TEST_CATALOG_LOG_DIR'"
fi

ts=`date "+%Y-%m-%d_%H%M%S"`

if [ ! -x ../bin/gobot ]; then
    echo "Error: This script must be executed in the bigrobot/catalog/ directory."
    exit 1
fi

if [ $# -ne 1 ]; then
    usage
fi

#
# f should be a <name>.dryrun.output_xml.log. It should also contain
# $TEST_CATALOG_LOG_DIR in the path.
#
f=$1

if [ ! -f $f ]; then
    echo "Error: File '$f' is not found."
    exit 1
fi

unset BIGROBOT_TESTBED
unset BIGROBOT_PARAMS_INPUT
unset BIGROBOT_TOPOLOGY
  # In regression environment, BIGROBOT_TOPOLOGY may be pointing to a reference
  # topology. So unset it. The established convention is for each test suite
  # to have a companion topology file of the same suite name.  

export BIGROBOT_CI=True
if [ "$BIGROBOT_PATH"x = x ]; then
    export BIGROBOT_PATH=`pwd`/..
fi
export BIGROBOT_LOG_PATH=${BIGROBOT_PATH}/catalog/${TEST_CATALOG_LOG_DIR}/bigrobot_logs

if [ -d $BIGROBOT_LOG_PATH ]; then
    #rm -rf $BIGROBOT_LOG_PATH
    mv $BIGROBOT_LOG_PATH ${BIGROBOT_LOG_PATH}.${ts}
fi

for x in `cat $f`; do
    if [ `expr $x : '.*/deprecated/.*'` -gt 0 ]; then
        echo "Ignoring $x (deprecated)"
    else
        echo Running $x
        y=`echo $x | sed 's/.txt//'`

        ls -la ${y}*

        # Notes:
        #   We need to count the test cases which are tagged as 'manual-untested'
        #   as well.
        BIGROBOT_SUITE=$y ../bin/gobot validate
    fi
done

find $BIGROBOT_LOG_PATH -name output.xml > $f.dryrun.output_xml.log

