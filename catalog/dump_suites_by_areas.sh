#!/bin/sh
# Usage:
#   $ cd .../bigrobot/catalog
#   $ ./dump_suites_by_areas.sh
# Description:
#   Create data files containing the suite names for all the products defined
#   in the catalog.yaml config.
# Assumptions:
#   - This script can only be executed inside the bigrobot/catalog/ directory.

if [ ! -x ../bin/gobot ]; then
    echo "Error: This script must be executed in the bigrobot/catalog/ directory."
    exit 1
fi

testsuite_path=`pwd | sed 's/catalog$//'`testsuites
config="../configs/catalog.yaml"
output=raw_data.total_suites_by_areas.sh

rm -f ${output}.*

for product in `python -c "import yaml; print '\n'.join(yaml.load(open('${config}'))['products'])" | grep -v '^#'`; do
    echo "Total text files for ${product}:"

    files=${output}.$product
    suite_files=${files}.suite_files
    resource_files=${files}.resource_files

    find ${testsuite_path}/${product} -name "*.txt" | wc -l

    for suite in `find ${testsuite_path}/${product} -name "*.txt"`; do
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

