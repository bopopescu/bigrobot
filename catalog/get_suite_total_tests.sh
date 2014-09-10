#!/bin/sh
# Description:
#   Execute the test suite in dry-run mode to figure out the total number of
#   test cases.

usage() {
    echo "Usage: $0 <full-path-suite-name>"
    echo "Example:
% ./get_suite_total_tests.sh /Users/vui/Documents/ws/myforks/bigrobot/testsuites/T5/T5-Platform/t5_switch_from_controller.txt
28 tests total, 28 passed, 0 failed
  Manual-untested: 0
"
    exit 1
}

if [ ! -x ../bin/gobot ]; then
    echo "Error: This script must be executed in the bigrobot/catalog/ directory."
    exit 1
fi

if [ $# -lt 1 ]; then
    usage
fi

suite=$1
suite=`echo $suite | sed -e s/.txt$// -e s/.topo$//`

if [ `expr $suite : '^/.*bigrobot/testsuites/.*'` -eq 0 ]; then
    suite="../testsuites/$suite"
fi

textfile="${suite}.txt"
if [ ! -f $textfile ]; then
    echo "ERROR: Test suite file $textfile' is not found"
    exit 1
else
    : echo "Found test suite file '$textfile'"
fi

base=`basename $suite`
dir=`dirname $suite`


(cd $dir; BIGROBOT_SUITE=$base gobot validate | grep "tests total")

grep -qi manual-untested $textfile
if [ $? -eq 0 ]; then
    untested=`(cd $dir; BIGROBOT_SUITE=$base gobot test --dryrun --include-manual-untested --include=manual-untested | grep "tests total" | awk '{print $1}')`
    echo "  Manual-untested: $untested"
else
    echo "  Manual-untested: 0"
fi

