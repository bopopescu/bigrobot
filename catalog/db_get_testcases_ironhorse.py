#!/usr/bin/env python
# Check the database collection 'test_cases' and retrieve all the test cases
# for IronHorse release which matches the env BUILD_NAME. Return the list
# of test cases.

import os
import sys
import pymongo

# Determine BigRobot path(s) based on this executable (which resides in
# the bin/ directory.
bigrobot_path = os.path.dirname(__file__) + '/..'
exscript_path = bigrobot_path + '/vendors/exscript/src'

sys.path.insert(0, bigrobot_path)
sys.path.insert(1, exscript_path)

import autobot.helpers as helpers
from catalog_modules.test_catalog import TestCatalog

if not 'BUILD_NAME' in os.environ:
    helpers.error_exit("Environment variable BUILD_NAME is not defined.", 1)

release = 'ironhorse'
build_name = os.environ['BUILD_NAME']
cat = TestCatalog()
testsuites = cat.find_test_suites_matching_build(build_name)
testcases = cat.find_test_cases_matching_build(build_name, release)

product_suites = {}
for testsuite in testsuites:
    product_suites[testsuite["product_suite"]] = testsuite["author"]

testcase_count = testcases.count()
print("Total test cases: %d" % testcase_count)

for testcase in testcases.sort([("product_suite", pymongo.ASCENDING),
                                ("name", pymongo.ASCENDING)]):
    product_suite = helpers.unicode_to_ascii(testcase["product_suite"])
    testcase_name = helpers.unicode_to_ascii(testcase["name"])
    author = product_suites[product_suite]
    print("%-10s %-60s %s"
          % (author, product_suite, testcase_name))

sys.exit(0)
