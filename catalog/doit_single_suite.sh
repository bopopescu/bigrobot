#!/bin/sh -x
# Description:
#   Dry run for a single test suite. The input is the absolute path to the
#   test suite. E.g.,
#     /Users/vui/Documents/ws/myforks/bigrobot/testsuites/T5/T5-Platform/t5_platform_HA_L2.txt
# Usage:
#   % BUILD_NAME="bvs master #beta2_31" ./doit_single_suite.sh \
#        /Users/vui/Documents/ws/myforks/bigrobot/testsuites/T5/T5-Platform/t5_platform_visibility_regress.txt
#
subject2() {
    s=$1
    echo ""
    echo "--- $s"
}

test_suite=$1
suite_list=raw_data.doit_single_suite.log
echo $test_suite > $suite_list

file=raw_data.doit_single_suite.sh
dryrun_out=${file}.dryrun
xml_logs=${suite_list}.dryrun.output_xml.log

subject2 "Dry run for ${suite_list}. Dump output to $dryrun_out ..."
time ./run_suites.sh ${suite_list} > $dryrun_out

subject2 "Generating JSON for test results in $xml_logs ..."
time ./parse_test_xml_output.py \
        --input=$xml_logs \
        --output-suites=raw_data.test_suites_${product}.json \
        --output-testcases=raw_data.test_cases_${product}.json
