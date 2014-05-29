#!/bin/sh

d=suites.data
phase1=1
phase2=1
phase3=1

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

    for x in `cat $d | grep -v '^#'`; do
        file=total_suites_by_rea.sh.${x}.suite_files
        dryrun_out=dryrun.${file}
        xml_logs=dryrun.${file}.output_xml.log

        subject2 "Dry run for ${file}. Dump output to $dryrun_out ..."
        time ./run_suites.sh ${file} > $dryrun_out


        subject2 "Generating JSON for test results in $xml_logs ..."
        time ./parse_test_xml_output.py $xml_logs

    done
fi

if [ $phase3 -eq 1 ]; then
    subject2 "Total IronHorse test cases"
    grep -i ironhorse test_suites.json | wc -l

    subject2 "Total manual test cases"
    grep -i manual test_suites.json | wc -l

    subject2 "Total manual-untested test cases"
    grep -i manual-untested test_suites.json | wc -l
fi

echo "End time: `date`"

