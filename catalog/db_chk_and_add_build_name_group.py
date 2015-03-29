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
Check the database collection 'build_groups' for a document which matches the
BUILD_NAME group.
   - If found, return the build name group.
   - If not found, create a new document, then return the build name group.
"""
    parser = argparse.ArgumentParser(prog='db_chk_and_add_build_name_group',
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description=descr)
    parser.add_argument('--verbose', action='store_true',
                        default=False,
                        help=("Print verbose output"))
    parser.add_argument('--build',
                        help=("Jenkins build string,"
                              " e.g., 'bvs master #2007'"))
    parser.add_argument('--createtime',
                        help=("Build creation time,"
                              " e.g., '2015-03-06T12:54:58.130'"))
    parser.add_argument('--updatetime',
                        help=("Build updated time,"
                              " e.g., '2015-03-06T12:54:58.130'"))
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

    doc = db.find_and_add_build_name_group(args.build,
                                           createtime=args.createtime,
                                           updatetime=args.updatetime,
                                           quiet=not args.verbose)
    if args.verbose: print "Doc: %s" % helpers.prettify(doc)

