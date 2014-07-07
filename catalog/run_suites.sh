#!/bin/sh
# Usage:
#   $ cd .../bigrobot/catalog
#   $ ./run_suites.sh total_suites_by_areas.sh.T5.text_files
# Description:
#   Take an input file which contains a list of test suites (with full path).
#   Then execute Gobot dryrun against these files to produce the Robot data
#   file (output.xml).
# Assumptions:
#   - This script can only be executed inside the bigrobot/catalog/ directory.

if [ ! -x ../bin/gobot ]; then
    echo "Error: This script must be executed in the bigrobot/catalog/ directory."
    exit 1
fi

f=$1

unset BIGROBOT_TESTBED
unset BIGROBOT_PARAMS_INPUT
export BIGROBOT_CI=True
export BIGROBOT_LOG_PATH=`pwd`/bigrobot_logs

rm -rf $BIGROBOT_LOG_PATH
for x in `cat $f`; do
    echo Running $x
    y=`echo $x | sed 's/.txt//'`
    echo $y
    export BIGROBOT_SUITE=$y

    # Notes:
    #   We include the test cases which are tagged as 'manual-untested'
    ../bin/gobot test --dryrun --include-manual-untested
done

find $BIGROBOT_LOG_PATH -name output.xml > $f.dryrun.output_xml.log
