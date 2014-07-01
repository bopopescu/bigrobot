#!/bin/sh

if [ ! -x ../bin/gobot ]; then
    echo "Error: This script must be executed in the bigrobot/catalog/ directory."
    exit 1
fi

RELEASE='ironhorse'
config="../configs/catalog.yaml"

phase1=1    # Find all test suites in product areas, report totals
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
    time ./total_suites_by_areas.sh
fi

if [ $phase2 -eq 1 ]; then
    rm -f test_*.json

    subject "Running all the test suites in dry-run mode"

    for product in `python -c "import yaml; print '\n'.join(yaml.load(open('${config}'))['products'])" | grep -v '^#'`; do
        file=raw_data.total_suites_by_areas.sh.${product}.suite_files
        dryrun_out=${file}.dryrun
        xml_logs=${file}.dryrun.output_xml.log

        if [ $phase2a -eq 1 ]; then
            subject2 "Dry run for ${file}. Dump output to $dryrun_out ..."
            time ./run_suites.sh ${file} > $dryrun_out
        fi


        subject2 "Generating JSON for test results in $xml_logs ..."
        time ./parse_test_xml_output.py \
                --input=$xml_logs \
                --output-suites=raw_data.test_suites_${product}.json \
                --output-testcases=raw_data.test_cases_${product}.json
    done
fi

if [ $phase3 -eq 1 ]; then
    subject2 "Total IronHorse test cases"
    grep -i $RELEASE raw_data.test_cases_*.json | wc -l

    subject2 "Total manual test cases"
    grep -i manual raw_data.test_cases_*.json | wc -l

    subject2 "Total manual-untested test cases"
    grep -i manual-untested raw_data.test_cases_*.json | wc -l
fi

echo "End time: `date`"

