#!/usr/bin/env python

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
# import autobot.devconf as devconf

helpers.set_env('IS_GOBOT', 'False')
helpers.set_env('AUTOBOT_LOG', './myrobot.log')


DB_SERVER = 'qadashboard-mongo.bigswitch.com'
DB_PORT = 27017

client = MongoClient(DB_SERVER, DB_PORT)
db = client.test_catalog2

testcases = db.test_cases
testsuites = db.test_suites

suites = testsuites.find()
tc = testcases.find({ "tags": {"$all": ["ironhorse"]}})

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

