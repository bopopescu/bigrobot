#!/bin/sh
# Usage:
#   $ ./run_suites.sh total_suites_by_areas.sh.T5.text_files
# Description:
#   It takes an input file which contains a list of test suites (with path).
#   Gobot dryrun is executed against these files to produce the data files
#   (output.xml) which will be processed later.

f=$1

unset BIGROBOT_TESTBED
unset BIGROBOT_PARAMS_INPUT
export BIGROBOT_CI=True
export BIGROBOT_LOG_PATH=/Users/vui/Documents/ws/myforks/bigrobot/catalog/bigrobot_logs

rm -rf $BIGROBOT_LOG_PATH
for x in `cat $f`; do
    echo Running $x
    y=`echo $x | sed 's/.txt//'`
    echo $y
    export BIGROBOT_SUITE=$y

    # Notes:
    #   We include the test cases which are tagged as 'manual-untested'
    gobot test --dryrun --include-manual-untested
done

find $BIGROBOT_LOG_PATH -name output.xml > dryrun.$f.output_xml.log
