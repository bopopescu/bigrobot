#!/usr/bin/env python
# Given BUILD_NAME, return releases (a string) which map to the product.
# On error condition, return empty string.

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

product = cat.get_product_for_build_name(build_name)
if not product:
    #helpers.error_exit("BUILD_NAME ('%s') does not contain a valid product."
    #                   % build_name, 1)
    print ''
    sys.exit(1)

base_release = cat.get_base_release_for_build_name(build_name, product)
if not base_release:
    #helpers.error_exit("BUILD_NAME ('%s') for '%s' product does not contain"
    #                   " a valid release name - matching software_image_map"
    #                   " in config/catalog.yaml."
    #                   % (build_name, product), 1)
    print ''
    sys.exit(1)    

releases = cat.get_releases_for_build_name(build_name)
print ' '.join(releases)
sys.exit(0)
