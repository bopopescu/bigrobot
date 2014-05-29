#!/usr/bin/env python
"""
"""

import os
import sys
import re
import datetime
import xmltodict
import argparse
import robot


# Determine BigRobot path(s) based on this executable (which resides in
# the bin/ directory.
bigrobot_path = os.path.dirname(__file__) + '/..'
exscript_path = bigrobot_path + '/vendors/exscript/src'

sys.path.insert(0, bigrobot_path)
sys.path.insert(1, exscript_path)

import autobot.helpers as helpers
# import autobot.devconf as devconf

helpers.set_env('IS_GOBOT', 'False')
helpers.set_env('AUTOBOT_LOG', '/tmp/myrobot.log')


def format_robot_timestamp(ts, is_datestamp=False):
    """
    Robot Framework uses the following timestamp format:
        20140523 16:49:38.051
    Concert it to UTC ISO time format:
        2014-05-23T23:49:38.051Z
    """
    match = re.match(r'(\d{4})(\d{2})(\d{2})\s+(\d+):(\d+):(\d+)\.(\d+)$', ts)
    if not match:
        helpers.environment_failure("Incorrect time format: '%s'" % ts)
    (year, month, date, hour, minute, sec, msec) = match.groups()
    hour = int(hour) + 7  # change PST to UTC
    if is_datestamp:
        s = '%s-%s-%s' % (year, month, date)
    else:
        s = '%s-%s-%sT%s:%s:%s.%sZ' % (year, month, date, hour, minute, sec, msec)
    return s


def format_robot_datestamp(ts):
    return format_robot_timestamp(ts, is_datestamp=True)


class TestSuite(object):
    def __init__(self, filename):
        """
        filename: output.xml file (with path)
        """
        self._suite = {}
        self._tests = []
        self._total_tests = 0
        self._filename = filename

        # Remove first line: <?xml version="1.0" encoding="UTF-8"?>
        self.xml_str = ''.join(helpers.file_read_once(self._filename,
                                                      to_list=True)[1:])

        self._data = xmltodict.parse(self.xml_str)

    def data(self):
        """
        Handle to the XML data from input file (output.xml).
        """
        if 'robot' not in self._data:
            helpers.environment_failure("Fatal error: expecting data['robot']")
        if 'suite' not in self._data['robot']:
            helpers.environment_failure("Fatal error: expecting data['robot']['suite']")
        if 'test' not in self._data['robot']['suite']:
            helpers.environment_failure("Fatal error: expecting data['robot']['suite']['test']")
        return self._data

    def extract_suite_attributes(self):
        suite = self.data()['robot']['suite']
        timestamp = format_robot_timestamp(self.data()['robot']['@generated'])
        datestamp = format_robot_datestamp(self.data()['robot']['@generated'])
        source = helpers.utf8(suite['@source'])
        match = re.match(r'.+bigrobot/(\w+/([\w-]+)/.+)$', source)
        if match:
            github_link = ('https://github.com/bigswitch/bigrobot/blob/master/'
                           + match.group(1))
            product = match.group(2)
        else:
            helpers.environment_failure(
                "Fatal error: Source file has invalid format ('%s')" % source)
        name_actual = os.path.splitext(os.path.basename(source))[0]

        self._suite = {
                    'source': source,
                    'timestamp': helpers.utf8(timestamp),
                    'datestamp': helpers.utf8(datestamp),
                    'github_link': github_link,
                    'name_actual': name_actual,
                    'name': helpers.utf8(suite['@name']),
                    'product': product,
                    'product_suite': product + "_" + name_actual,
                    'author': None,
                    'total_tests': None,
                    }

    def extract_test_attributes(self):
        tests = self.data()['robot']['suite']['test']
        for a_test in tests:
            test_id = helpers.utf8(a_test['@id'])
            name = helpers.utf8(a_test['@name'])
            if (('tags' in a_test and a_test['tags'] != None)
                and 'tag' in a_test['tags']):
                tags = helpers.utf8(a_test['tags']['tag'])
            else:
                tags = []

            # This should contain the complete list of attributes. Some may
            # be populated by the Script Catalog while others may be populated
            # later by Regression execution.
            test = {'test_id': test_id,
                    'name': name,
                    'tags': tags,
                    'job_name_id': None,
                    'executed': False,
                    'status': None,
                    'starttime': None,
                    'endtime': None,
                    'duration': None,
                    'origin_script_catalog': True,
                    'origin_regression_catalog': False,
                    'product_suite': self._suite['product_suite'],
                    }
            self._tests.append(test)

            # Add test cases to test suite
            # self._suite['tests'] = self._tests

        self.total_tests()

    def suite_name(self):
        return self._suite['name']

    def suite(self):
        return self._suite

    def tests(self):
        return self._tests

    def total_tests(self):
        self._suite['total_tests'] = len(self.tests())
        return self._suite['total_tests']

    def dump_suite(self, to_file=None, to_json=False):
        if to_json:
            if to_file:
                helpers.file_write_append_once(to_file,
                                               helpers.to_json(self.suite())
                                               + '\n')
            else:
                print(helpers.to_json(self.suite()))
        else:
            if to_file:
                helpers.file_write_append_once(to_file,
                                               helpers.prettify(self.suite())
                                               + '\n')
            else:
                print(helpers.prettify(self.suite()))

    def dump_suite_to_file(self, filename, to_json=False):
        self.dump_suite(filename, to_json)

    def dump_tests(self, to_file=None, to_json=False):
        if to_json:
            if to_file:
                helpers.file_write_append_once(to_file,
                                               helpers.to_json(self.tests())
                                               + '\n')
            else:
                print(helpers.to_json(self.tests()))
        else:
            if to_file:
                helpers.file_write_append_once(to_file,
                                               helpers.prettify(self.tests())
                                               + '\n')
            else:
                print(helpers.prettify(self.tests()))

    def dump_tests_to_file(self, filename, to_json=False):
        self.dump_tests(filename, to_json)

    def dump_raw(self):
        print(helpers.prettify(self.data()))

    def dump_xml(self):
        print("%s" % helpers.prettify_xml(self.xml_str))


class TestCatalog(object):
    def __init__(self):
        self._suites = []

    def load_suites(self, filenames):
        for filename in filenames:
            filename = filename.strip()

            if helpers.file_not_empty(filename):
                print("Reading %s" % filename)
                suite = TestSuite(filename)
                suite.extract_suite_attributes()
                suite.extract_test_attributes()
                suite.dump_suite_to_file("test_suites.json", to_json=True)
                suite.dump_tests_to_file("test_cases.json", to_json=True)
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

if __name__ == '__main__':
    descr = """\
Parse the Robot output.xml files to generate the collections for the
Test Catalog (MongoDB) database.
"""

    parser = argparse.ArgumentParser(prog='parse_test_xml_output',
                                     description=descr)

    input_file = sys.argv[1]
    input_files = helpers.file_read_once(input_file, to_list=True)

    t = TestCatalog()
    t.load_suites(input_files)
    print "Total suites: %s" % t.total_suites()
    print "Total tests: %s" % t.total_tests()

