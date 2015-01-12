#!/usr/bin/env python
# Description:
#   Check for test suites which do not have the correct topo files. E.g.,
#     - detect suites with generic topo file or no topo file
#     - detect suites with <suite>.<virtual|physical>.topo file

import os
import sys
import re
from pymongo import MongoClient


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

testsuites = db.test_suites


def get_suites():
    return testsuites.find({"build_name": os.environ['BUILD_NAME']},
                           { "author": 1, "source": 1, "topo_type": 1, "_id": 1})


def get_topo_file(text_file, topo_type='generic-topology'):
    _suite = os.path.splitext(text_file)[0]
    _suite = re.sub(r'^bigrobot/', '', _suite)
    if topo_type == 'generic-topology':
        return "../" + _suite + ".topo"
    elif topo_type == 'physical':
        return "../" + _suite + ".physical.topo"
    elif topo_type == 'virtual':
        return "../" + _suite + ".virtual.topo"
    else:
        return "missing-topology"


def get_topo_type(text_file):
    _topo_file = get_topo_file(text_file, "generic-topology")
    if helpers.file_exists(_topo_file):
        return "generic-topology"
    else:
        return "missing-topology"


print_all = False
print_unknown = True
print_mv_commands = False


# There may be
text_names = {}


if print_all:
    for x in sorted(get_suites(), key=lambda k: k['author']):
        print("%10s   %-12s %s" % (x["topo_type"], x["author"], x["source"]))

if print_unknown:
    for x in sorted(get_suites(), key=lambda k: k['author']):
        if x["topo_type"] in ['unknown', 'generic-topology', 'missing-topology']:
            print("%10s   %-12s %s" % (get_topo_type(x["source"]), x["author"], x["source"]))
