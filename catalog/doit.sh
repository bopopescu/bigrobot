#!/bin/sh

phase1=1
phase2=1
phase3=1

echo "Start time: `date`"
rm -f test_suites.json


if [ $phase1 -eq 1 ]; then
    echo "***"
    echo "*** Finding all the test suites"
    echo "***"
    time ./total_suites_by_areas.sh
fi

if [ $phase2 -eq 1 ]; then
    echo ""
    echo "***"
    echo "*** Running all the test suites in dry-run mode"
    echo "***"

    #for x in `echo total_suites_by_areas.sh.*.suite_files`; do
    #for x in `echo total_suites_by_areas.sh.SwitchLight.suite_files`; do
    for x in `echo total_suites_by_areas.sh.T5.suite_files total_suites_by_areas.sh.SwitchLight.suite_files`; do

        dryrun_out=dryrun.$x
        xml_logs=dryrun.$x.output_xml.log

        echo ""
        echo "*** Dry run for $x. Dump output to $dryrun_out ..."
        time ./run_suites.sh $x > $dryrun_out


        echo ""
        echo "*** Generating JSON for test results in $xml_logs ..."
        time ./parse_test_xml_output.py $xml_logs

    done
fi

if [ $phase3 -eq 1 ]; then
    echo ""
    echo "***"
    echo "*** Total IronHorse test cases"
    echo "***"
    grep -i ironhorse test_suites.json | wc -l
fi

echo "End time: `date`"
