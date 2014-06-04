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
db = client.test_catalog

testcases = db.test_cases
testsuites = db.test_suites

tc = testcases.find(
        { "$and": [
            {"tags": {"$all": ["ironhorse"]}},
            {"tags": {"$nin": ["feature", "scaling", "performance", "solution", "longevity", "traffic", "negative"]}}
            ] },
        { "product_suite": 1, "name": 1, "tags": 1, "_id": 0 }
        ).sort("product")

tc_dict = {}
for x in tc:
    product_suite = helpers.utf8(x['product_suite'])
    if product_suite not in tc_dict:
        tc_dict[product_suite] = []
    tc_dict[product_suite].append(helpers.utf8(x['name']))

for key, value in tc_dict.items():
    ts = testsuites.find_one( { "product_suite": key } )
    print "Name: %s, Source file: %s" % (ts["author"], ts["source"])
    for x in ["\t%s" % x for x in value]:
        print x
    print ""

#print helpers.prettify(tc_dict)

