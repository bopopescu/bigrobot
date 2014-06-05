#!/bin/sh -x
# 'infile': a file which contains a list of output.xml files (path included).
#

#export BUILD_NAME="bvs master #1995"
#export BUILD_NAME="bvs master #1989"
#export BUILD_NUMBER
#export BUILD_URL

ts=`date "+%Y-%m-%d_%H%M%S"`

if [ $# -eq 0 ]; then
    # If ../testlogs exists then look for output.xml there
    if [ -d ../testlogs ]; then
        infile=input_list.$ts
        echo "Looking for output.xml files in ../testlogs/ directory."
        find ../testlogs -name output.xml > $infile
        if [ ! -s $infile ]; then
            echo "Did not find any output.xml file."
            exit 0
        fi

        # ... Found a valid output.xml. Proceed with parsing.
        cat $infile

    else
        echo "Usage: $0 <infile>"
        exit 0
    fi
else
    infile=$1
fi

progname=`basename $0`
outfile=${progname}_output.$ts.log

rm -f test_suites_regression.json test_cases_regression.json

./parse_test_xml_output.py \
        --input=$infile \
        --output-suites=test_suites_regression.json \
        --output-testcases=test_cases_regression.json \
        --is-regression > $outfile 2>&1

