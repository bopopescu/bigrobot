#!/usr/bin/env python
"""
"""

import os
import sys
import argparse
# import robot


# Determine BigRobot path(s) based on this executable (which resides in
# the bin/ directory.
bigrobot_path = os.path.dirname(__file__) + '/..'
exscript_path = bigrobot_path + '/vendors/exscript/src'

sys.path.insert(0, bigrobot_path)
sys.path.insert(1, exscript_path)

import autobot.helpers as helpers
from catalog_modules.test_suite import TestSuite


helpers.set_env('IS_GOBOT', 'False')
helpers.set_env('AUTOBOT_LOG', './myrobot.log')


class TestCollection(object):
    def __init__(self, in_files, out_suites, out_testcases,
                 is_regression=False):
        self._suites = []
        self._input_files = in_files
        self._output_suites = out_suites
        self._output_testcases = out_testcases
        self._is_regression = is_regression

    def load_suites(self):
        for filename in self._input_files:
            filename = filename.strip()

            if helpers.file_not_empty(filename):
                print("Reading %s" % filename)
                suite = TestSuite(filename, is_regression=self._is_regression)
                suite.extract_attributes()
                suite.dump_tests_to_file(self._output_testcases, to_json=True)
                suite.dump_suite_to_file(self._output_suites, to_json=True)
                self._suites.append(suite)

    def suites(self):
        return self._suites

    def total_suites(self):
        return len(self.suites())

    def total_tests(self):
        tests = 0
        i = 0
        for suite in self.suites():
            i += 1
            tests += suite.total_tests()
            print "Suite %02d: %s (%s tests)" % (i,
                                                 suite.suite_name(),
                                                 suite.total_tests())
        return tests


def prog_args():
    descr = """\
Parse the Robot output.xml files to generate the collections for the
Test Catalog (MongoDB) database.
"""
    parser = argparse.ArgumentParser(prog='parse_test_xml_output',
                                     description=descr)
    parser.add_argument('--build',
                        help=("Jenkins build string,"
                              " e.g., 'bvs master #2007'"))
    parser.add_argument('--input', required=True,
                        help=("Contains a list of Robot output.xml files"
                              "  with complete pathnames"))
    parser.add_argument('--output-suites', required=True,
                        help=("JSON output file containing test suites"))
    parser.add_argument('--output-testcases', required=True,
                        help=("JSON output file containing test cases"))
    parser.add_argument('--is-regression',
                        action='store_true', default=False,
                        help=("Specify this option if analyzing regression results"))
    _args = parser.parse_args()

    # _args.build <=> env BUILD_NAME
    if not _args.build and 'BUILD_NAME' in os.environ:
        _args.build = os.environ['BUILD_NAME']
    elif not _args.build:
        helpers.error_exit("Must specify --build option or set environment variable BUILD_NAME")
    else:
        os.environ['BUILD_NAME'] = _args.build

    return _args


if __name__ == '__main__':
    args = prog_args()
    input_files = helpers.file_read_once(args.input, to_list=True)
    t = TestCollection(in_files=input_files,
                       out_suites=args.output_suites,
                       out_testcases=args.output_testcases,
                       is_regression=args.is_regression)
    t.load_suites()
    print "Total suites: %s" % t.total_suites()
    print "Total tests: %s" % t.total_tests()
