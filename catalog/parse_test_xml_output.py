#!/usr/bin/env python
"""
Note: Must pass in BUILD_NAME environment since it is indirectly required by
      TestSuite module.
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
from catalog_modules.test_catalog import TestCatalog


helpers.set_env('IS_GOBOT', 'False')
helpers.set_env('AUTOBOT_LOG', './myrobot.log')


class TestCollection(object):
    def __init__(self, in_files, out_suites, out_testcases,
                 is_regression=False, is_baseline=False):
        self._suites = []
        self._input_files = in_files
        self._output_suites = out_suites
        self._output_testcases = out_testcases
        self._is_regression = is_regression
        self._is_baseline = is_baseline

    def dump_records_to_json_file(self, filename, records):
        helpers.file_write_append_once(filename,
                                       helpers.to_json(records)
                                       + '\n')

    def load_suites(self):
        """
        This is the workhorse. It reads each output.xml file and extract the
        various test attributes.
        """
        suite_records = []
        test_records = []
        for filename in self._input_files:
            filename = filename.strip()

            if helpers.file_not_empty(filename):
                print("Reading %s" % filename)
                try:
                    suite = TestSuite(filename,
                                      is_regression=self._is_regression,
                                      is_baseline=self._is_baseline)
                except:
                    print("ERROR: Unable to parse %s. Test suite will not be added to Test Catalog."
                          % filename)
                    print helpers.exception_info()
                else:
                    suite.extract_attributes()
                    self._suites.append(suite)
                    suite_records.append(suite.suite())
                    test_records = test_records + suite.tests()
        self.dump_records_to_json_file(self._output_suites, suite_records)
        self.dump_records_to_json_file(self._output_testcases, test_records)

        # Import baseline data into DB (if not regression data)
        if self._is_regression == False:
            f = self._output_suites
            print("Importing %s into Mongo test suites collection" % f)
            (status, output, error, error_code) = helpers.run_cmd2(
                                  cmd="./mongoimport_suites_collection.sh %s" % f,
                                  shell=True)
            print("Status:\n'%s'" % helpers.indent_str(status))
            print("Output:\n'%s'" % helpers.indent_str(output))
            print("Error:\n'%s'" % helpers.indent_str(error))
            print("Error code:\n'%s'" % helpers.indent_str(error_code))

            f = self._output_testcases
            print("Importing %s into Mongo test case collection" % f)
            (status, output, error, error_code) = helpers.run_cmd2(
                                  cmd="./mongoimport_testcases_collection.sh %s" % f,
                                  shell=True)
            print("Status:\n'%s'" % helpers.indent_str(status))
            print("Output:\n'%s'" % helpers.indent_str(output))
            print("Error:\n'%s'" % helpers.indent_str(error))
            print("Error code:\n'%s'" % helpers.indent_str(error_code))

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
Parse the Robot output.xml files and generate/populate the collections for the
Test Catalog (MongoDB) database.
"""
    parser = argparse.ArgumentParser(prog='parse_test_xml_output',
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description=descr)
    parser.add_argument('--build',
                        help=("Jenkins build string,"
                              " e.g., 'bvs main #2007'"))
    parser.add_argument('--input', required=True,
                        help=("Input file which contains a list of Robot"
                              " output.xml files  with complete pathnames"))
    parser.add_argument('--output-suites', required=True,
                        help=("JSON output file containing test suites"))
    parser.add_argument('--output-testcases', required=True,
                        help=("JSON output file containing test cases"))
    parser.add_argument('--is-baseline',
                        action='store_true', default=False,
                        help=("Specify this option if generating baseline"
                              " data"))
    parser.add_argument('--is-regression',
                        action='store_true', default=False,
                        help=("Specify this option if analyzing regression"
                              " results"))
    _args = parser.parse_args()

    # _args.build <=> env BUILD_NAME
    if not _args.build and 'BUILD_NAME' in os.environ:
        _args.build = os.environ['BUILD_NAME']
    elif not _args.build:
        helpers.error_exit("Must specify --build option or set environment"
                           " variable BUILD_NAME")
    else:
        os.environ['BUILD_NAME'] = _args.build

    if not _args.is_baseline and not _args.is_regression:
        helpers.error_exit("Must specify --is-regression or --is-baseline")

    return _args


if __name__ == '__main__':
    args = prog_args()
    input_files = helpers.file_read_once(args.input, to_list=True)
    t = TestCollection(in_files=input_files,
                       out_suites=args.output_suites,
                       out_testcases=args.output_testcases,
                       is_regression=args.is_regression,
                       is_baseline=args.is_baseline,
                       )
    t.load_suites()
    print "Total suites: %s" % t.total_suites()
    print "Total tests: %s" % t.total_tests()
