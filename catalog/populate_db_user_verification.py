#!/usr/bin/env python
# Read the verification file (YAML format) under bigrobot/manual_verification/
# and populate the database document which matches the build.

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

if not 'BUILD_NAME' in os.environ:
    helpers.error_exit("Environment variable BUILD_NAME is not defined.", 1)


class ManualVerificationBuild(object):
    def __init__(self, build, infile):
        self._aggregated_build_name = build
        self._verification_file = infile
        self._cat = None
        self._builds = self.catalog().aggregated_build(build)
        if not self._builds:
            helpers.error_exit(
                "Aggregated build '%s' is not defined in catalog.yaml."
                % build)

    def catalog(self):
        if not self._cat:
            self._cat = TestCatalog()
        return self._cat

    def aggregated_build_name(self): return self._aggregated_build_name

    def builds(self): return self._builds

    def do_it(self):
        test_cases = helpers.from_yaml(helpers.file_read_once(self._verification_file))

        for tc in test_cases:
            query = { "name": tc['name'],
                      "product_suite": tc['product_suite'],
                      "build_name": self.aggregated_build_name(),
                     }
            print("query:\n%s" % helpers.prettify(query))
            sys.exit(1)

            aggr_cursor = self.catalog().find_test_cases_archive(query)

            tc['build_name_orig'] = build
            tc['build_name'] = self.aggregated_build_name()

            count = aggr_cursor.count()
            if count == 0:
                print("Inserting document: %s" % query)
                tc['build_name_list'] = [build]

                doc = self.catalog().insert_doc('test_cases_archive',
                                                tc)
            else:
                if count != 1:
                    print("WARNING: Expecting only one aggregated"
                          " test case, but result is '%s'"
                          % count)

                print("Updating document: %s" % query)
                aggr_tc = aggr_cursor[0]
                if 'build_name_list' in aggr_tc:
                    tc['build_name_list'] = (
                            aggr_tc['build_name_list'] + [build])
                else:
                    tc['build_name_list'] = [build]

                doc = self.catalog().upsert_doc('test_cases_archive',
                                                tc,
                                                query)
            if doc == None:
                print("\n*** doc: %s, name:'%s', product_suite:'%s'"
                      % (doc, tc['name'], tc['product_suite']))
            else:
                print("\n*** doc: %s" % doc)


def prog_args():
    descr = """\
Populate the QA Dashboard database with data found in the user-entered
verification files (in bigrobot/data/verification/).

The specified build (BUILD_NAME) must be the name of an aggregated build.
"""
    parser = argparse.ArgumentParser(prog='db_manual_verification',
                                     description=descr)
    parser.add_argument('--build',
                        help=("Build name,"
                              " e.g., 'bvs master ironhorse beta2 aggregated'"))
    parser.add_argument('--infile', required=True,
                        help=("Input verification file"))
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
    if not helpers.file_exists(args.infile):
        helpers.error_exit("File '%s' is not found." % args.infile, 1)

    aggr_build = ManualVerificationBuild(args.build, args.infile)
    aggr_build.do_it()
