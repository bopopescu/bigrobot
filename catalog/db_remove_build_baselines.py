#!/usr/bin/env python
# Remove documents in test_suites and test_cases collections which match
# BUILD_NAME.

import os
import sys

# Determine BigRobot path(s) based on this executable (which resides in
# the bin/ directory.
bigrobot_path = os.path.dirname(__file__) + '/..'

sys.path.insert(0, bigrobot_path)

import autobot.helpers as helpers
from catalog_modules.test_catalog import TestCatalog

if not 'BUILD_NAME' in os.environ:
    helpers.error_exit("Environment variable BUILD_NAME is not defined.", 1)


def remove_test_data():
    cat = TestCatalog()
    suite_count = cat.remove_test_suites_matching_build(
                        os.environ['BUILD_NAME'])
    test_count = cat.remove_test_cases_matching_build(
                        os.environ['BUILD_NAME'])
    print("Removed %s suites and %s test matching build '%s'."
          % (suite_count, test_count, os.environ['BUILD_NAME']))
    return (suite_count, test_count)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--y':
        remove_test_data()
    else:
        print("To remove the matching documents, specify argument --y.")
