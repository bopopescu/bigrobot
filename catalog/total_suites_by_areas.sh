#!/bin/sh
p=/Users/vui/Documents/ws/myforks/bigrobot/testsuites
d=suites.data

rm -f total_suites_by_areas.sh.*

for x in `cat $d | grep -v '^#'`; do

    echo "Total text files for $x:"

    files=total_suites_by_areas.sh.$x
    text_files=$files.text_files
    suite_files=$files.suite_files
    resource_files=$files.resource_files

    find $p/$x -name "*.txt" | wc -l
    find $p/$x -name "*.txt" > $text_files

    for y in `cat $text_files`; do
        grep -i -e '^*' $y | grep -i -e 'testcase' -e 'test case' > /dev/null
        if [ $? -eq 0 ]; then
            echo $y >> $suite_files
        else
            echo $y >> $resource_files
        fi
    done

    if [ -f $resource_files ]; then
        wc -l $resource_files
    fi
    if [ -f $suite_files ]; then
        wc -l $suite_files
    fi

done

