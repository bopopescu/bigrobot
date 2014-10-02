#!/usr/bin/env python

import os
import sys
import argparse
import pymongo

# Determine BigRobot path(s) based on this executable (which resides in
# the bin/ directory.
bigrobot_path = os.path.dirname(__file__) + '/..'
exscript_path = bigrobot_path + '/vendors/exscript/src'

sys.path.insert(0, bigrobot_path)
sys.path.insert(1, exscript_path)

import autobot.helpers as helpers
from catalog_modules.test_catalog import TestCatalog


def prog_args():
    descr = """\
Given the build (BUILD_NAME argument), print the list of failed test cases.
If release is not specified, default to 'IronHorse' release.

Examples:
   % BUILD_NAME="bvs master bcf-2.0.0 fcs" ./dump_test_cases_failed.py
   % BUILD_NAME="bvs master aggregated 2014 wk40" ./dump_test_cases_failed.py --release ironhorse

"""
    parser = argparse.ArgumentParser(prog='dump_test_cases_failed',
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description=descr)
    parser.add_argument('--build',
                        help=("Jenkins build string,"
                              " e.g., 'bvs master #2007'"))
    parser.add_argument('--release', required=False, default='IronHorse',
                        help=("Product release, e.g., 'IronHorse'"))
    _args = parser.parse_args()

    # _args.build <=> env BUILD_NAME
    if not _args.build and 'BUILD_NAME' in os.environ:
        _args.build = os.environ['BUILD_NAME']
    elif not _args.build:
        helpers.error_exit("Must specify --build option or set environment"
                           " variable BUILD_NAME")
    else:
        os.environ['BUILD_NAME'] = _args.build

    return _args


def print_failed_tests(args):
    release = args.release.lower()

    db = TestCatalog()

    ts_author_dict = db.test_suite_author_mapping(args.build)

    query = {"build_name": args.build,
             "tags": {"$all": [release]},
             "status": "FAIL",
             }
    tc_archive_collection = db.test_cases_archive_collection().find(query).sort(
                                            [("product_suite", pymongo.ASCENDING),
                                             ("name", pymongo.ASCENDING)])
    total_tc = tc_archive_collection.count()
    i = 0
    for tc in tc_archive_collection:
        i += 1
        print("TC-%03d: %12s  %-55s  %s"
              % (i,
                 ts_author_dict[tc["product_suite"]],
                 tc["product_suite"],
                 tc["name"]))
    print "\nTotal test cases failed: %s" % total_tc



if __name__ == '__main__':
    print_failed_tests(prog_args())
