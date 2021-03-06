#!/usr/bin/env python
# Remove documents in test_suites and test_cases collections which match
# BUILD_NAME.

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


def find_test_data():
    cat = TestCatalog()
    build_count = cat.find_builds_matching_build(
                        os.environ['BUILD_NAME']).count()
    suite_count = cat.find_test_suites_matching_build(
                        os.environ['BUILD_NAME']).count()
    test_count = cat.find_test_cases_matching_build(
                        os.environ['BUILD_NAME']).count()
    print("Found builds(%s), suites(%s), and tests(%s) matching build '%s'."
          % (build_count, suite_count, test_count, os.environ['BUILD_NAME']))
    return (build_count, suite_count, test_count)

def remove_test_data():
    cat = TestCatalog()
    build_count = cat.remove_builds_matching_build(
                        os.environ['BUILD_NAME'])
    suite_count = cat.remove_test_suites_matching_build(
                        os.environ['BUILD_NAME'])
    test_count = cat.remove_test_cases_matching_build(
                        os.environ['BUILD_NAME'])
    print("Removed builds(%s), suites(%s), and tests(%s) matching build '%s'."
          % (build_count, suite_count, test_count, os.environ['BUILD_NAME']))
    return (build_count, suite_count, test_count)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--y':
        remove_test_data()
    else:
        find_test_data()
        print("To remove the matching documents, specify argument --y.")
