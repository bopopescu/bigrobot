#!/usr/bin/env python
# Search for all FAILed test cases in a (aggregated) build and generate
# verification records for each failed test case.
#
# Create file bigrobot/data/verification/verification.<build>.<user>.yaml
# where:
#      - <build> is the build name, likely of an aggregated build
#      - <user>  is the user responsible for doing the verification
#
# The verification file contains test case entries in the format:
#
#   - name: 'Verify L3 traffic honor more specific routes with ecmp group'
#     product_suite: 'T5/L3/T5_L3_physical_inter/t5_layer3_physical_inter'
#     status: PASS
#     build_name_verified: 'bvs master #2794'
#     jira:
#     notes: 'I manually verified this and it works.'
#   ... and so on ...
#

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


if not 'BUILD_NAME' in os.environ:
    helpers.error_exit("Environment variable BUILD_NAME is not defined.", 1)


class VerificationFileBuilder(object):
    def __init__(self, build, overwrite):
        self._aggregated_build_name = build
        self._is_overwrite = overwrite
        self._cat = None
        self._builds = self.catalog().aggregated_build(build)
        if not self._builds:
            helpers.error_exit(
                "Aggregated build '%s' is not defined in catalog.yaml."
                % build)
        # dictionary of test suites indexed by product_suite key.
        self._product_suites = {}

        self.load_product_suites_dict()

    def catalog(self):
        if not self._cat:
            self._cat = TestCatalog()
        return self._cat

    def aggregated_build_name(self): return self._aggregated_build_name

    def builds(self): return self._builds

    def warn(self, msg):
        print "\n"
        print "WARNING: " + msg

    def exit(self, msg):
        print "\n"
        helpers.error_exit(msg, 1)

    def load_product_suites_dict(self):
        test_suites = self.catalog().find_test_suites({"build_name": self.aggregated_build_name()})
        for ts in test_suites:
            self._product_suites[ts['product_suite']] = ts

    def author(self, product_suite):
        if product_suite not in self._product_suites:
            self.exit("Cannot find product_suite '%s'" % product_suite)
        return self._product_suites[product_suite]['author']

    def verification_header_template(self):
        return '../templates/verification_header.yaml'

    def verification_file(self, author):
        build_str = re.sub(' ', '_', self.aggregated_build_name())
        build_str = re.sub('#', '', build_str)
        return '../data/verification/verification.%s.%s.yaml' % (build_str, author)

    def do_it(self):
        query = { "build_name": self.aggregated_build_name(),
                  "status": 'FAIL',
                 }
        aggr_cursor = self.catalog().find_test_cases_archive(query)
        fail_count = aggr_cursor.count()
        print "Total failed test cases in build '%s': %s" % (self.aggregated_build_name(), fail_count)
        file_dict = {}

        for tc in aggr_cursor:
            product_suite = tc['product_suite']
            tc_name = tc['name']
            author = self.author(product_suite)
            file_name = self.verification_file(author)

            doc_str = """
- name: '%s'
  product_suite: '%s'
  status:
  build_name_verified: 'bvs master #nnn'
  jira:
  notes:
""" % (tc_name, product_suite)

            if file_name not in file_dict:
                # First time we're writing to this file
                file_dict[file_name] = True
                if not helpers.file_exists(file_name):
                    helpers.file_copy(self.verification_header_template(),
                                      self.verification_file(author))

            helpers.file_write_append_once(file_name, doc_str)




def prog_args():
    descr = """\
Search for all FAILed test cases in a (aggregated) build and generate
verification records for each failed test case.

The specified build (BUILD_NAME) must be the name of an aggregated build.
"""
    parser = argparse.ArgumentParser(prog='create_verification_files',
                                     description=descr)
    parser.add_argument('--build',
                        help=("Build name,"
                              " e.g., 'bvs master ironhorse beta2 aggregated'"))
    parser.add_argument('--force-overwrite', action='store_true', default=False,
                        help=("Overwrite the existing verification files"))
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
    verification_builder = VerificationFileBuilder(args.build, args.force_overwrite)
    verification_builder.do_it()
