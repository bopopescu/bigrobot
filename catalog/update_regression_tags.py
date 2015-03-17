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
Update the regression tags for a build. The currently supported tags are
'daily' and 'full'.

Example:
% BUILD_NAME=ihplus_bcf_10G-490 ./update_regression_tags.py --tags full
"""
    parser = argparse.ArgumentParser(prog='update_regression_tags',
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description=descr)
    parser.add_argument('--verbose', action='store_true',
                        default=False,
                        help=("Print verbose output"))
    parser.add_argument('--build',
                        help=("Jenkins build string,"
                              " e.g., 'bvs master #2007'"))
    parser.add_argument('--tags', metavar=('tag1', 'tag2'), nargs='*',
                        help=("Regression tags,"
                              " e.g., 'full', 'daily'"))
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
    doc = db.update_regression_tags(args.build, tags=args.tags)

    if doc:
        print("build_name: %s, changed regression_tags from '%s' to '%s'."
              % (doc["build_name"], [helpers.unicode_to_ascii(x) for x in doc["regression_tags"]], args.tags))
        sys.exit(0)
    else:
        print "ERROR: build_name '%s' not in the catalog." % args.build
        sys.exit(1)
