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
from catalog_modules.authors import Authors
from catalog_modules.pseudo_yaml import PseudoYAML, sanitize_yaml_string


class VerificationFileBuilder(object):
    def __init__(self, build, user, overwrite):
        self._aggregated_build_name = build
        self._user = user
        self._is_overwrite = overwrite
        self._cat = None
        self._builds = self.catalog().aggregated_build(build)
        self._test_case_dict = {}

        if not self._builds:
            helpers.error_exit(
                "Aggregated build '%s' is not defined in the database."
                % build)
        # dictionary of test suites indexed by product_suite key.
        self._product_suites = {}

        self.load_product_suites_dict()

    def verification_header_template(self):
        return '../templates/verification_header.yaml'

    def verification_file(self, author):
        build_str = re.sub(' ', '_', self.aggregated_build_name())
        build_str = re.sub('#', '', build_str)
        path = '../data/verification/%s' % build_str
        if helpers.file_not_exists(path):
            helpers.mkdir_p(path)
        return ('%s/verification_%s.yaml'
                % (path, author))

    def catalog(self):
        if not self._cat:
            self._cat = TestCatalog()
        return self._cat

    def aggregated_build_name(self): return self._aggregated_build_name

    def builds(self): return self._builds

    def load_product_suites_dict(self):
        test_suites = self.catalog().find_test_suites(
                                {"build_name": self.aggregated_build_name()})
        for ts in test_suites:
            self._product_suites[ts['product_suite']] = ts

    def author(self, product_suite):
        if product_suite not in self._product_suites:
            return "unknown"
        return self._product_suites[product_suite]['author']

    def write_entry_to_file(self, entry, outfile):
        doc_str = """
- name: %s
  product_suite: %s
  status: %s
""" % (entry['name'], entry['product_suite'], entry['status'])

        if 'build_name_verified' in entry:
            build_name_verified = entry['build_name_verified']
        else:
            build_name_verified = "bvs master #nnn"
        doc_str += "  build_name_verified: '%s'\n" % build_name_verified

        if 'jira' in entry and entry['jira']:
            doc_str += "  jira: %s\n" % entry['jira']
        else:
            doc_str += "  jira: \n"

        if 'notes' in entry and entry['notes']:
            doc_str += "  notes: %s\n" % entry['notes']
        else:
            doc_str += "  notes: \n"

        helpers.file_write_append_once(outfile, doc_str)

    def do_it(self):

        # Search for failed test cases. Verification list will be built/updated
        # based on the failed test cases.
        query = { "build_name": self.aggregated_build_name(),
                  "status": 'FAIL',
                  # "tags": { "$all": ['ironhorse']},
                 }
        aggr_cursor = self.catalog().find_test_cases_archive(query)
        fail_count = aggr_cursor.count()
        print("Total failed test cases in build '%s': %s"
              % (self.aggregated_build_name(), fail_count))

        if self._user == 'all':
            pass
        elif self._user not in Authors().get().values():
            helpers.error_exit("User '%s' is not defined in the test catalog."
                               % self._user)

        # Initialize test case dictionary for each author if not exist
        for author in Authors().get().values():
            file_name = self.verification_file(author)

            if helpers.file_exists(file_name):
                # print "Loading file %s" % file_name
                tc_list = PseudoYAML(file_name).load_yaml_file()
                self._test_case_dict[author] = {}

                if tc_list:
                    # Test cases found
                    for tc in tc_list:
                        tc_key = tc['product_suite'] + ' ' + tc['name']
                        self._test_case_dict[author][tc_key] = tc
            else:
                self._test_case_dict[author] = {}

        first_pass = {}
        for tc in aggr_cursor:
            product_suite = tc['product_suite']
            tc_name = tc['name']
            status = tc['status']
            # build_name = build_name_last = tc['build_name']
            if 'build_name_list' in tc and tc['build_name_list']:
                build_name_last = tc['build_name_list'][-1]
            author = self.author(product_suite)
            file_name = self.verification_file(author)
            new_file_name = file_name + ".new"

            if self._user == 'all' or self._user == author:
                pass  # do action
            else:
                continue

            if new_file_name not in first_pass:
                if helpers.file_exists(new_file_name):
                    print "Removing file %s" % new_file_name
                    helpers.file_remove(new_file_name)

                helpers.file_copy(self.verification_header_template(),
                                  new_file_name)
                print "Creating file %s" % new_file_name
                first_pass[new_file_name] = file_name

            key = product_suite + ' ' + tc_name
            if key in self._test_case_dict[author]:
                if status == self._test_case_dict[author][key]['status']:
                    self._test_case_dict[author][key]['name'] = \
                        sanitize_yaml_string(
                            self._test_case_dict[author][key]['name'])
                    self.write_entry_to_file(self._test_case_dict[author][key],
                                             new_file_name)
                else:
                    helpers.file_write_append_once(
                            new_file_name,
                            "\n### status: %s in recent '%s'"
                            % (status, build_name_last))
                    self._test_case_dict[author][key]['name'] = \
                        sanitize_yaml_string(
                            self._test_case_dict[author][key]['name'])
                    self.write_entry_to_file(self._test_case_dict[author][key],
                                             new_file_name)
                del self._test_case_dict[author][key]
            else:
                helpers.file_write_append_once(
                            new_file_name,
                            "\n### new entry in recent '%s'"
                            % (build_name_last))
                rec = {
                       "name": sanitize_yaml_string(tc_name),
                       "product_suite": product_suite,
                       "status": status,
                       }
                if 'jira' in tc and tc['jira']:
                    rec['jira'] = tc['jira']
                if 'jira' in tc and tc['jira']:
                    rec['jira'] = tc['jira']
                if 'notes' in tc and tc['notes']:
                    rec['notes'] = tc['notes']
                self.write_entry_to_file(rec, new_file_name)

        # Dump remaining test cases from YAML
        for author in self._test_case_dict:

            if self._user == 'all' or self._user == author:
                pass  # do action
            else:
                continue

            file_name = self.verification_file(author)
            new_file_name = file_name + ".new"

            for key in self._test_case_dict[author]:

                if not helpers.file_exists(new_file_name):
                    helpers.file_copy(self.verification_header_template(),
                                      new_file_name)

                tc = self._test_case_dict[author][key]
                if tc['status'] == 'FAIL':
                    if tc['jira'] or (tc['notes'] and
                                      tc['notes'] != "No description."):
                        # Contains user comments
                        helpers.file_write_append_once(
                                new_file_name,
                                "\n### Previously verified. Not reported as"
                                " FAIL in recent report so is likely PASSing.")
                        tc['name'] = sanitize_yaml_string(tc['name'])
                        self.write_entry_to_file(tc, new_file_name)
                    else:
                        # User didn't get a chance to verify it previously.
                        # So just silently ignore it.
                        pass
                else:
                    # Contains user comments
                    tc['name'] = sanitize_yaml_string(tc['name'])
                    self.write_entry_to_file(tc, new_file_name)

        # for key, value in first_pass.iteritems():
        #    if helpers.file_not_exists(value):
        #        helpers.file_rename(key, value)
        #        print "Renamed file to %s" % value


def prog_args():
    descr = """\
Search for all FAILed test cases in a (aggregated) build and generate
verification records for each failed test case.

The specified build (BUILD_NAME) must be the name of an aggregated build.

Examples:
    -- Generate the verification file for 'mingtao'
    % BUILD_NAME="bvs master bcf-2.0.0 fcs" ./create_or_update_verification_file.py --user mingtao

    -- Generate the verification files for all QA engineers
    % BUILD_NAME="bvs master bcf-2.0.0 fcs" ./create_or_update_verification_file.py --user all
"""
    parser = argparse.ArgumentParser(
                prog='create_or_update_verification_file',
                formatter_class=argparse.RawDescriptionHelpFormatter,
                description=descr)
    parser.add_argument(
                '--build',
                help=("Build name,"
                      " e.g., 'bvs master ironhorse beta2 aggregated'"))
    parser.add_argument(
                '--user',
                required=True,
                help=("Create verification file for user (as defined in"
                      " test catalog)."))
    parser.add_argument(
                '--force-overwrite',
                action='store_true',
                default=False,
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
    verification_builder = VerificationFileBuilder(args.build,
                                                   args.user,
                                                   args.force_overwrite)
    verification_builder.do_it()
