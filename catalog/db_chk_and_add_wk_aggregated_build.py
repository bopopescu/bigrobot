#!/usr/bin/env python

import os
import sys
import argparse
import re

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
Check the database collection 'aggregated_builds' for a document which
matches the env BUILD_NAME.
   - If found, return the aggregated build name.
   - If not found and build_name matches a typical build name (e.g., 'bvs master #1234'),
     create a new document, then return the weekly aggregated build name.
   - If not found and build_name does not match a typical build name (e.g., a Beta build
     does not have a typical build name - 'bvs master #bcf-2.0.0_13'), don't create a
     new document. You should instead rerun command and specify the aggregated beta build name
     using the option --aggregated-build-name.

Examples:
   % BUILD_NAME="bvs master #3436" ./db_chk_and_add_wk_aggregated_build.py
   % BUILD_NAME="bvs master #bcf-2.0.0_13" ./db_chk_and_add_wk_aggregated_build.py \\
                     --aggregated-build-name "bvs master bcf-2.0.0 aggregated"
"""
    parser = argparse.ArgumentParser(
                        prog='db_chk_and_add_wk_aggregated_build',
                        formatter_class=argparse.RawDescriptionHelpFormatter,
                        description=descr)
    parser.add_argument('--verbose', action='store_true',
                        default=False,
                        help=("Print verbose output"))
    parser.add_argument('--build',
                        help=("Jenkins build string,"
                              " e.g., 'bvs master #2007'"))
    parser.add_argument('--aggregated-build-name',
                        help=("Aggregated build name,"
                              " e.g., 'bvs master bcf-2.0.0 aggregated'"))
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


if __name__ == '__main__':
    args = prog_args()

    db = TestCatalog()
    doc = db.find_and_add_aggregated_build(
                    args.build,
                    aggregated_build_name=args.aggregated_build_name,
                    quiet=not args.verbose)

    if args.verbose: print "Doc: %s" % helpers.prettify(doc)
    print "%s" % doc["build_name"]
    sys.exit(0)
