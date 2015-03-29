#!/usr/bin/env python

import os
import sys
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
    descr = """\
Check the database collection 'builds' for a document which matches the env
BUILD_NAME.
   - If found, return the build name.
   - If not found, create a new document, then return the build name.
"""
    parser = argparse.ArgumentParser(
                    prog='db_chk_and_add_build_name',
                    formatter_class=argparse.RawDescriptionHelpFormatter,
                    description=descr)
    parser.add_argument('--verbose', action='store_true',
                        default=False,
                        help=("Print verbose output"))
    parser.add_argument('--build',
                        help=("Jenkins build string,"
                              " e.g., 'bvs master #2007'"))
    parser.add_argument('--regression-tags',
                        help=("Supported regression tags are 'daily' or 'full'."))
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

    doc = db.find_and_add_build_name(args.build,
                                     regression_tags=args.regression_tags,
                                     quiet=not args.verbose)
    if args.verbose: print "Doc: %s" % helpers.prettify(doc)

    doc = db.find_and_add_build_name_group(args.build, quiet=not args.verbose)
    if args.verbose: print "Doc: %s" % helpers.prettify(doc)

