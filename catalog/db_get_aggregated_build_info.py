#!/usr/bin/env python
# Given the aggregated build (BUILD_NAME argument), print the list of actual builds.

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
build_names = db.aggregated_build(build_name)

print "%s" % helpers.prettify([helpers.unicode_to_ascii(x) for x in build_names])
