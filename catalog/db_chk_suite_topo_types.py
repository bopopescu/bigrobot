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

print_all = True
print_unknown = False
print_mv_commands = False


client = MongoClient(DB_SERVER, DB_PORT)
db = client.test_catalog2

testsuites = db.test_suites

suites = testsuites.find( {}, { "author": 1, "source": 1, "topo_type": 1, "_id": 1})

if print_all:
    for x in sorted(suites, key=lambda k: k['author']):
        print("%10s   %-10s %s" % (x["topo_type"], x["author"], x["source"]))

if print_unknown:
    for x in sorted(suites, key=lambda k: k['author']):
        if x["topo_type"] == 'unknown':
            print("%10s   %-10s %s" % (x["topo_type"], x["author"], x["source"]))
            #x["dest_source"] = os.path.splitext(x["source"])[0] + ".physical.topo"
            #print("mv %s %s" % (x["source"], x["dest_source"]))

if print_mv_commands:
    for x in sorted(suites, key=lambda k: k['author']):
        if x["topo_type"] == 'unknown':
            suite = os.path.splitext(x["source"])[0]
            #print("mv %s %s" % (suite + ".topo", suite + ".physical.topo"))
            print("ls -la ../../%s" % (suite + ".topo"))
