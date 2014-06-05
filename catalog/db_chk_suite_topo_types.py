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

testsuites = db.test_suites

suites = testsuites.find( {}, { "author": 1, "source": 1, "topo_type": 1, "_id": 1})
for x in sorted(suites, key=lambda k: k['author']):
    print("%10s   %-10s %s" % (x["topo_type"], x["author"], x["source"]))

