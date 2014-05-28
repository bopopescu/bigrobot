#!/bin/sh
p=/Users/vui/Documents/ws/myforks/bigrobot/testsuites
echo "Total suites:"
find $p -name "*.txt" | wc -l
find $p -name "*.txt" > total_suites.sh.out
