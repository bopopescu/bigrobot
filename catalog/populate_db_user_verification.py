#!/usr/bin/env python
# Read the verification file (YAML format) under bigrobot/manual_verification/
# and populate the database document which matches the build.

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
import catalog_modules.cat_helpers as cat_helpers
from catalog_modules.test_catalog import TestCatalog


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

    def is_test_case_verified(self, tc):
        verified = False
        if 'jira' in tc and tc['jira']:
            verified = True
        if 'notes' in tc and tc['notes']:
            verified = True
        return verified

    def sanitize_test_case_data(self, tc):
        if 'status' not in tc:
            cat_helpers.formatted_error_exit(
                    "Entry missing 'status' field (%s)" % tc)
        if 'build_name_verified' not in tc:
            cat_helpers.formatted_error_exit(
                    "Entry missing 'build_name_verified' field (%s)" % tc)
        if 'notes' not in tc:
            cat_helpers.formatted_error_exit(
                    "Entry missing 'notes' field (%s)" % tc)

        if re.match(r'^fail(ed)?$', tc['status'], re.I):
            tc['status'] = 'FAIL'
        elif re.match(r'^pass(ed)?$', tc['status'], re.I):
            tc['status'] = 'PASS'
        else:
            cat_helpers.formatted_error_exit(
                    "'status' field has invalid value (%s)" % tc)

        if tc['notes'] == None:
            tc['notes'] = "No description."
            # cat_helpers.formatted_error_exit(
            #        "'notes' field must contain a description (%s)" % tc)

    def sanitize_verification_data(self):
        test_cases = helpers.from_yaml(helpers.file_read_once(
                                                    self._verification_file))

        if test_cases == None:
            # No test cases found
            return True

        for tc in test_cases:
            if self.is_test_case_verified(tc) == False:
                continue
            self.sanitize_test_case_data(tc)
        return True

    def populate_db_with_verification_data(self):
        test_cases = helpers.from_yaml(helpers.file_read_once(
                                                    self._verification_file))
        print "Updating documents in build '%s'" % self.aggregated_build_name()

        if test_cases == None:
            # No test cases found
            return True

        for tc in test_cases:
            self.sanitize_test_case_data(tc)
            query = { "name": tc['name'],
                      "product_suite": tc['product_suite'],
                      "build_name": self.aggregated_build_name(),
                     }

            aggr_cursor = self.catalog().find_test_cases_archive(query)
            count = aggr_cursor.count()

            if count == 0:
                cat_helpers.warn("Cannot find document matching below query."
                                 " No update made.\n%s"
                                 % helpers.prettify(query))
            else:
                if count != 1:
                    cat_helpers.warn("Expecting only one aggregated test case,"
                                     " but result is '%s'" % count)

                doc = dict(aggr_cursor[0])  # create a copy of dictionary
                if 'build_name_list' in doc:
                    if doc['build_name_list'][-1] != tc['build_name_verified']:
                        doc['build_name_list'] = (
                            doc['build_name_list'] +
                            [tc['build_name_verified']])
                else:
                    doc['build_name_list'] = [tc['build_name_verified']]

                doc['status'] = tc['status']
                doc['build_name_verified'] = tc['build_name_verified']
                doc['build_name_orig'] = self.aggregated_build_name()
                doc['jira'] = tc['jira']
                doc['notes'] = tc['notes']
                doc['status'] = tc['status']
                doc['createtime'] = helpers.ts_long_local()
                doc['starttime'] = doc['starttime_datestamp'] = None
                doc['endtime'] = doc['endtime_datestamp'] = None
                doc['build_number'] = None


                # print("Updating document:\n%s" % helpers.prettify(doc))
                print("Updating suite '%s', test case '%s'"
                      % (doc['product_suite'], doc['name']))
                new_doc = self.catalog().upsert_doc('test_cases_archive',
                                                    doc,
                                                    query)
                if new_doc == None:
                    cat_helpers.warn("Cannot find document. Upsert failed"
                                     " for: %s, name:'%s', product_suite:'%s'\n"
                                     % (doc, tc['name'], tc['product_suite']))
                else:
                    # print("\n new_doc: %s\n" % new_doc)
                    pass


def prog_args():
    descr = """\
Populate the QA Dashboard database with data found in the user-entered
verification files (in bigrobot/data/verification/).

The specified build (BUILD_NAME) must be the name of an aggregated build.

Examples:
    -- Sanity check the data. It will not update the database.
    % BUILD_NAME="bvs main bcf-2.0.0 fcs" ./populate_db_user_verification.py \\
             --infile ../data/verification/bvs_main_bcf-2.0.0_fcs/verification_kranti.yaml \\
             --sanitize-data

    -- If everything looks good. Update the database.
    % BUILD_NAME="bvs main bcf-2.0.0 fcs" ./populate_db_user_verification.py \\
             --infile ../data/verification/bvs_main_bcf-2.0.0_fcs/verification_kranti.yaml

"""
    parser = argparse.ArgumentParser(prog='db_manual_verification',
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description=descr)
    parser.add_argument('--build',
                        help=("Build name,"
                              " e.g., 'bvs main ironhorse beta2 aggregated'"))
    parser.add_argument('--infile', required=True,
                        help=("Input verification file"))
    parser.add_argument('--sanitize-data', action='store_true', default=False,
                        help=("Check data file for formatting errors"))
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

    verification_build = ManualVerificationBuild(args.build, args.infile)
    if args.sanitize_data:
        if verification_build.sanitize_verification_data():
            print "Data format is correct."
        else:
            print "Error found in data format."
    else:
        verification_build.populate_db_with_verification_data()
