#!/bin/sh
p=/Users/vui/Documents/ws/myforks/bigrobot/testsuites/T5
echo "Total suites:"
find $p -name "*.txt" | wc -l
find $p -name "*.txt" > total_suites_t5.sh.out
