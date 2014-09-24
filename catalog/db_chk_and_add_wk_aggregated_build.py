#!/usr/bin/env python
# Check the database collection 'aggregated_builds' for a document which
# matches the env BUILD_NAME.
#   - If found, return the aggregated build name.
#   - If not found, create a new document, then return the aggregated build name.

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

build_name = os.environ['BUILD_NAME']
db = TestCatalog()
doc = db.find_and_add_aggregated_build(build_name)

#print "Doc: %s" % helpers.prettify(doc)
print "%s" % doc["name"]
