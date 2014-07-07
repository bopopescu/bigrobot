#!/usr/bin/env python
# Description:
#   Check for test suites which do not have the correct topo files. E.g.,
#     - detect suites with no topo file
#     - detect suites with <suite>.topo (but should be 'virtual' or 'physical')

import os
import sys
import re
from pymongo import MongoClient
import robot

# Determine BigRobot path(s) based on this executable (which resides in
# the bin/ directory.
bigrobot_path = os.path.dirname(__file__) + '/..'
exscript_path = bigrobot_path + '/vendors/exscript/src'

sys.path.insert(0, bigrobot_path)
sys.path.insert(1, exscript_path)

import autobot.helpers as helpers
import catalog_modules.cat_helpers as cat_helpers

helpers.set_env('IS_GOBOT', 'False')
helpers.set_env('AUTOBOT_LOG', './myrobot.log')

if not 'BUILD_NAME' in os.environ:
    helpers.error_exit("Environment variable BUILD_NAME is not defined.", 1)

configs = cat_helpers.load_config_catalog()
db_server = configs['db_server']
db_port = configs['db_port']
database = configs['database']

client = MongoClient(db_server, db_port)
db = client[database]


print_all = False
print_unknown = True
print_mv_commands = True


testsuites = db.test_suites

suites = testsuites.find( {"build_name": os.environ['BUILD_NAME']},
                          { "author": 1, "source": 1, "topo_type": 1, "_id": 1}
                          )

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
            suite = re.sub(r'^bigrobot/', '', suite)

            topo_file_current = "../" + suite + ".topo"
            topo_file_new = "../" + suite + ".physical.topo"

            if helpers.file_exists(topo_file_current):
                #print("mv %s %s" % (topo_file_current, topo_file_new))
                print("git mv %s %s" % (topo_file_current, topo_file_new))
                #print("ls -la %s" % topo_file_current)
