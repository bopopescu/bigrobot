#!/bin/sh

if [ ! -x ../bin/gobot ]; then
    echo "Error: This script must be executed in the bigrobot/catalog/ directory."
    exit 1
fi

if [ "$TEST_CATALOG_LOG_DIR"x = x ]; then
    echo "Error: Env var TEST_CATALOG_LOG_DIR is not defined."
    exit 1
fi

usage() {
    echo "Usage: `basename $0`"
    echo ""
    echo "If RELEASE_NAME env is provided then print additional stats for the release."
    echo "Examples of release name: 'ironhorse', 'ironhorse-plus', 'jackfrost', 'blackbird', 'corsair', etc."
    echo ""

    exit 1
}


release=$RELEASE_NAME

phase1=1    # Find all test suites in test areas, report totals
phase2=1    # Dry-run to generate output.xml, and generate JSON files
phase2a=1   #   Step a: Dry-run to generate output.xml
phase2b=1   #   Step b: Generate JSON files
phase3=1    # Report summary

subject() {
    s=$1
    echo ""
    echo "***"
    echo "*** $s"
    echo "***"
}

subject2() {
    s=$1
    echo ""
    echo "--- $s"
}

echo "Start time: `date`"


if [ $phase1 -eq 1 ]; then
    subject "Finding all the test suites"
    time ./dump_suites_by_areas.sh
fi

if [ $phase2 -eq 1 ]; then
    rm -f test_*.json

    subject "Running all the test suites in dry-run mode"

    # Production test suites are located in test area folders under
    # bigrobot/testsuites/. E.g.,
    #    SwitchLight
    #    BigWire
    #    BigTap
    #    SwitchLight
    #    BigChain
    #    T5

    for test_area in `cd ../testsuites; find . ! -path . -type d -maxdepth 1 | xargs -I {} basename {}`; do
        file=${TEST_CATALOG_LOG_DIR}/raw_data.dump_suites_by_areas.sh.${test_area}.suite_files
        dryrun_out=${file}.dryrun
        xml_logs=${file}.dryrun.output_xml.log

        if [ $phase2a -eq 1 ]; then
            subject2 "Dry run for ${file}. Dump output to $dryrun_out ..."
            time ./run_suites.sh ${file} > $dryrun_out
        fi


        subject2 "Generating JSON for test results in $xml_logs ..."
        time ./parse_test_xml_output.py \
                --input=$xml_logs \
                --is-baseline \
                --output-suites=${TEST_CATALOG_LOG_DIR}/raw_data.test_suites_${test_area}.json \
                --output-testcases=${TEST_CATALOG_LOG_DIR}/raw_data.test_cases_${test_area}.json
    done
fi

if [ $phase3 -eq 1 ]; then
    
    if [ "$release"x != x ]; then
        subject2 "Total $release test cases"
        grep -i $release ${TEST_CATALOG_LOG_DIR}/raw_data.test_cases_*.json | wc -l
    fi

    subject2 "Total manual test cases"
    grep -i manual ${TEST_CATALOG_LOG_DIR}/raw_data.test_cases_*.json | wc -l

    subject2 "Total manual-untested test cases"
    grep -i manual-untested ${TEST_CATALOG_LOG_DIR}/raw_data.test_cases_*.json | wc -l
fi

echo "End time: `date`"

