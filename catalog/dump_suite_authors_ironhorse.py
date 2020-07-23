#!/usr/bin/env python
# Description:
#   Display a list of test suites and their authors for IronHorse release.
#
# Usage:
#   % BUILD_NAME="bvs main #2761" ./dump_suite_authors_ironhorse.py
#
#   <Output>
#   ...
#   animesh      SwitchLight/switchlight_platform
#   animesh      SwitchLight/switchlight_user_management
#   ...
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

if not 'BUILD_NAME' in os.environ:
    helpers.error_exit("Environment variable BUILD_NAME is not defined.", 1)

configs = helpers.bigrobot_config_test_catalog()
db_server = configs['db_server']
db_port = configs['db_port']
database = configs['database']

client = MongoClient(db_server, db_port)
db = client[database]


testcases = db.test_cases
testsuites = db.test_suites

suites = testsuites.find()
tc = testcases.find({ "build_name": os.environ['BUILD_NAME'], "tags": {"$all": ["ironhorse"]}})

authors = {}
ironhorse_suites = {}


for x in suites:
    product_suite = helpers.utf8(x['product_suite'])
    authors[product_suite] = helpers.utf8(x['author'])

for x in tc:
    product_suite = helpers.utf8(x['product_suite'])
    ironhorse_suites[product_suite] = authors[product_suite]

authors_list = []
for suite, author in ironhorse_suites.items():
    authors_list.append("%-12s %s" % (author, suite))

print "\n".join(sorted(authors_list))

print ""
print "Total suites: %s" % len(authors_list)

