#!/bin/sh
# Usage:
#   $ cd .../bigrobot/catalog
#   $ ./dump_suites_by_areas.sh
# Description:
#   Create data files containing the suite names for all the test areas under
#   bigrobot/testsuites/.
# Assumptions:
#   - This script can only be executed inside the bigrobot/catalog/ directory.

if [ ! -x ../bin/gobot ]; then
    echo "Error: This script must be executed in the bigrobot/catalog/ directory."
    exit 1
fi

if [ "$TEST_CATALOG_LOG_DIR"x = x ]; then
    echo "Error: Env var TEST_CATALOG_LOG_DIR is not defined."
    exit 1
fi

testsuite_path=`pwd | sed 's/catalog$//'`testsuites
output=${TEST_CATALOG_LOG_DIR}/raw_data.dump_suites_by_areas.sh

rm -f ${output}.*

for test_area in `cd ../testsuites; find . -maxdepth 1 -type d ! -path . | xargs -I {} basename {}`; do
    echo "Total text files for ${test_area}:"

    files=${output}.$test_area
    suite_files=${files}.suite_files
    resource_files=${files}.resource_files

    find ${testsuite_path}/${test_area} -name "*.txt" | wc -l

    for suite in `find ${testsuite_path}/${test_area} -name "*.txt"`; do
        grep -i -e '^*' $suite | grep -i -e 'testcase' -e 'test case' > /dev/null
        if [ $? -eq 0 ]; then
            echo $suite >> $suite_files
        else
            # Text file is not a test suite (no test cases specified).
            # It's likely a resource file.
            #echo $suite >> $resource_files
            : "noop"
        fi
    done

    if [ -f $resource_files ]; then
        wc -l $resource_files
    fi
    if [ -f $suite_files ]; then
        wc -l $suite_files
    fi
done

