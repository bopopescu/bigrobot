#!/bin/sh
# 'infile': a file which contains a list of output.xml files (path included).
#

ts=`date "+%Y-%m-%d_%H%M%S"`

if [ $# -eq 0 ]; then
    echo "Usage: $0 <infile>"
fi

infile=$1
progname=`basename $0`
outfile=${prog_name}_output.$ts.log

rm -f test_suites_regression.json test_cases_regression.json

./parse_test_xml_output.py \
        --input=$infile \
        --output-suites=test_suites_regression.json \
        --output-testcases=test_cases_regression.json \
        --is-regression > $outfile 2>&1

