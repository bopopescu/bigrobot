#!/usr/bin/env python
# Check the database collection 'test_cases' and retrieve all the test cases
# for IronHorse release which matches the env BUILD_NAME. Return the list
# of test cases.

import os
import sys
import pymongo
import argparse


# Determine BigRobot path(s) based on this executable (which resides in
# the bin/ directory.
bigrobot_path = os.path.dirname(__file__) + '/..'
exscript_path = bigrobot_path + '/vendors/exscript/src'

sys.path.insert(0, bigrobot_path)
sys.path.insert(1, exscript_path)

import autobot.helpers as helpers
from catalog_modules.test_catalog import TestCatalog


def prog_args():
    descr = """
Display test data for a specific build. Example:

% RELEASE_NAME="<release>" BUILD_NAME="bvs main #3271" \\
        ./db_get_test_data.py --tags manual-untested \\
                              --no-show-header
"""
    parser = argparse.ArgumentParser(
                        prog='db_get_test_data',
                        formatter_class=argparse.RawDescriptionHelpFormatter,
                        description=descr)
    parser.add_argument('--build',
                        help=("Jenkins build string,"
                              " e.g., 'bvs main #2007'"))
    parser.add_argument('--release',
                        help=("Product release, e.g., 'ironhorse', 'ironhorse-plus', 'jackfrost', etc."))
    parser.add_argument('--tags', metavar=('tag1', 'tag2'), nargs='*',
                        help='Test case tags to include, e.g., manual-untested, scaling, ztn, etc.')
    parser.add_argument('--no-show-header', action='store_true', default=False,
                        help=("Don't show header info (build name, release, total)"))
    _args = parser.parse_args()

    # _args.build <=> env BUILD_NAME
    if not _args.build and 'BUILD_NAME' in os.environ:
        _args.build = os.environ['BUILD_NAME']
    elif not _args.build:
        helpers.error_exit("Must specify --build option or set environment"
                           " variable BUILD_NAME")
    else:
        os.environ['BUILD_NAME'] = _args.build

    # _args.release <=> env RELEASE_NAME
    if not _args.release and 'RELEASE_NAME' in os.environ:
        _args.release = os.environ['RELEASE_NAME']
    elif not _args.release:
        helpers.error_exit("Must specify --release option or set environment"
                           " variable RELEASE_NAME")
    else:
        os.environ['RELEASE_NAME'] = _args.release
    _args.release = _args.release.lower()

    return _args


def print_data(args):
    cat = TestCatalog()
    testsuites = cat.find_test_suites_matching_build(args.build)
    testcases = cat.find_test_cases_matching_build(
                        build_name=args.build,
                        release=args.release,
                        tags=args.tags,
                        )
    product_suites = {}
    for testsuite in testsuites:
        product_suites[testsuite["product_suite"]] = testsuite["author"]
    testcase_count = testcases.count()

    if args.no_show_header == False:
        print("Build name       : '%s'" % args.build)
        print("Release          : %s" % args.release)
        if args.tags: print("Test case tags   : %s" % args.tags)
        print("Total test cases : %d" % testcase_count)
        print("==============================================================")
        print("")

    for testcase in testcases.sort([("product_suite", pymongo.ASCENDING),
                                    ("name", pymongo.ASCENDING)]):
        product_suite = helpers.unicode_to_ascii(testcase["product_suite"])
        testcase_name = helpers.unicode_to_ascii(testcase["name"])
        author = product_suites[product_suite]
        print("%-10s %-60s %s"
              % (author, product_suite, testcase_name))


if __name__ == '__main__':
    print_data(prog_args())
    sys.exit(0)
