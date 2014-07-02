#!/usr/bin/env python
# Check the database collection 'builds' for a record which matches the env
# BUILD_NAME. If found, return 0 (succcess), else return 1 (failure).

import os
import sys
from pymongo import MongoClient

# Determine BigRobot path(s) based on this executable (which resides in
# the bin/ directory.
bigrobot_path = os.path.dirname(__file__) + '/..'
exscript_path = bigrobot_path + '/vendors/exscript/src'

sys.path.insert(0, bigrobot_path)
sys.path.insert(1, exscript_path)

import autobot.helpers as helpers
import cat_helpers

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
builds = db['builds']
build = builds.find({"build_name": os.environ['BUILD_NAME']})

if build.count() > 0:
    sys.exit(0)  # Found record(s) matching build name
else:
    sys.exit(1)  # Build name not found
