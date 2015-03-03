#!/usr/bin/env python

import sys
from robot.api import TestData

def print_suite(suite):
    print 'Suite:', suite.name
    for test in suite.testcase_table:
        print '-', test.name
    for child in suite.children:  # recurse through testsuite directory
        print_suite(child)

suite = TestData(source=sys.argv[1])
print_suite(suite)

