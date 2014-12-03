#!/usr/bin/env python
# Given BUILD_NAME, return releases which map to the product.

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
cat = TestCatalog()
releases = cat.get_releases_for_build_name(build_name)
print ' '.join(releases)

