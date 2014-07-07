#!/usr/bin/env python
# Check the database collection 'builds' for a record which matches the env
# BUILD_NAME. If found, return 0 (succcess), else return 1 (failure).

import os
import sys

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

col = TestCatalog().db()['builds']
build_count = col.find({"build_name": os.environ['BUILD_NAME']}).count()
print("Build_name: '%s', found %s instance(s)"
      % (os.environ['BUILD_NAME'], build_count))

if build_count > 0:
    sys.exit(0)  # Found record(s) matching build name
else:
    sys.exit(1)  # Build name not found
