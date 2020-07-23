#!/usr/bin/env python
# Description:
#   Check each test case in the production test suites to make sure that each has a proper
#   test type defined (tag contains "feature", "scaling", "performance", "solution",
#   "longevity", "negative", "robustness", and so on).
#
#   For a complete list of test types, see:
#   https://bigswitch.atlassian.net/wiki/display/QA/Test+Case+Tagging+in+BigRobot
#
#   Usage:
#     % RELEASE_NAME=ironhorse BUILD_NAME="bvs main #2761" ./data_validation_find_testcases_with_missing_test_types.py
#

import os
import sys
from pymongo import MongoClient
import robot

# Determine BigRobot path(s) based on this executable (which resides in
# the bin/ directory.
bigrobot_path = os.path.dirname(__file__) + '/..'
exscript_path = bigrobot_path + '/vendors/exscript/src'

sys.path.insert(0, bigrobot_path)
sys.path.insert(1, exscript_path)

import autobot.helpers as helpers

helpers.set_env('IS_GOBOT', 'False')
helpers.set_env('AUTOBOT_LOG', './myrobot.log')

if not 'RELEASE_NAME' in os.environ:
    helpers.error_exit("Environment variable RELEASE_NAME is not defined.", 1)
if not 'BUILD_NAME' in os.environ:
    helpers.error_exit("Environment variable BUILD_NAME is not defined.", 1)

RELEASE = os.environ['RELEASE_NAME'].lower()


configs = helpers.bigrobot_config_test_catalog()
db_server = configs['db_server']
db_port = configs['db_port']
database = configs['database']
test_types = configs['test_types']

client = MongoClient(db_server, db_port)
db = client[database]

testcases = db.test_cases
testsuites = db.test_suites

tc = testcases.find(
        { "build_name": os.environ['BUILD_NAME'],
          "$and": [
            {"tags": {"$all": [RELEASE]}},
            {"tags": {"$nin": test_types}}
            ] },
        { "product_suite": 1, "name": 1, "tags": 1, "_id": 0 }
        ).sort("product")

tc_dict = {}
for x in tc:
    product_suite = helpers.utf8(x['product_suite'])
    if product_suite not in tc_dict:
        tc_dict[product_suite] = []
    tc_dict[product_suite].append("%s, %s" % (helpers.utf8(x['name']), x['tags']))

count = 0

for key, value in tc_dict.items():
    ts = testsuites.find_one({ "product_suite": key })
    print "Name: %s, Source file: %s" % (ts["author"], ts["source"])
    for x in ["\t%s" % x for x in value]:
        print x
        count += 1
    print ""

print "Total test cases affected: %d" % count

