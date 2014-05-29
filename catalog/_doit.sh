#!/bin/sh

product_file=products.data

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

    for product in `cat $product_file | grep -v '^#'`; do
        file=total_suites_by_areas.sh.${product}.suite_files
        dryrun_out=dryrun.${file}
        xml_logs=dryrun.${file}.output_xml.log

        if [ $phase2a -eq 1 ]; then
            subject2 "Dry run for ${file}. Dump output to $dryrun_out ..."
            time ./run_suites.sh ${file} > $dryrun_out
        fi


        subject2 "Generating JSON for test results in $xml_logs ..."
        time ./parse_test_xml_output.py \
                --input=$xml_logs \
                --output-suites=test_suites_${product}.json \
                --output-testcases=test_cases_${product}.json
    done
fi

if [ $phase3 -eq 1 ]; then
    subject2 "Total IronHorse test cases"
    grep -i ironhorse test_cases_*.json | wc -l

    subject2 "Total manual test cases"
    grep -i manual test_cases_*.json | wc -l

    subject2 "Total manual-untested test cases"
    grep -i manual-untested test_cases_*.json | wc -l
fi

echo "End time: `date`"

