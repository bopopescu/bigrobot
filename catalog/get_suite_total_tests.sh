#!/bin/sh
# Description:
#   Execute the test suite in dry-run mode to figure out the total number of
#   test cases.

usage() {
    echo "Usage: $0 <full-path-suite-name>"
    exit 1
}

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


(cd $dir; BIGROBOT_SUITE=$base gobot test --dryrun --include-manual-untested | grep "tests total")

grep -qi manual-untested $textfile
if [ $? -eq 0 ]; then
    untested=`(cd $dir; BIGROBOT_SUITE=$base gobot test --dryrun --include-manual-untested --include=manual-untested | grep "tests total" | awk '{print $1}')`
    echo "  Manual-untested: $untested"
else
    echo "  Manual-untested: 0"
fi

