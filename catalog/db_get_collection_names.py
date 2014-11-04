#!/usr/bin/env python
# Print a list of collection names.

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

#if not 'BUILD_NAME' in os.environ:
#    helpers.error_exit("Environment variable BUILD_NAME is not defined.", 1)
#
#build_name = os.environ['BUILD_NAME']

db = TestCatalog()
cols = db.db().collection_names()

for col in cols:
    if col == "system.indexes":
        continue
    print col
