#!/usr/bin/env python
"""
"""

import os
import sys
import re
import xmltodict
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

authors = {
    'https://github.com/bigswitch/bigrobot/blob/master/testsuites_dev/vui/test_robot.txt': 'vui'
}


class TestCase(object):
    def __init__(self, test_id, name, tags):
        self._test_id = test_id
        self._name = name
        self._tags = tags

    def test_id(self): return self._test_id

    def name(self): return self._name

    def tags(self): return self._tags

    def dump(self):
        return {'test_id': self.test_id(),
                'name': self.name(),
                'tags': self.tags()
                }


class TestSuite(object):
    def __init__(self, filename):
        """
        filename: output.xml file (with path)
        """
        self._suite = {}
        self._tests = []
        self._total_tests = 0
        self.filename = filename

        # Remove first line: <?xml version="1.0" encoding="UTF-8"?>
        self.xml_str = ''.join(helpers.file_read_once(self.filename,
                                                      to_list=True)[1:])
        self.data = xmltodict.parse(self.xml_str)
        self.extract_attributes()

    def extract_attributes(self):
        suite = self.data['robot']['suite']
        self._suite['source'] = helpers.utf8(suite['@source'])
        match = re.match(r'.+bigrobot/(.+)$', self._suite['source'])
        if match:
            self._suite['source_github'] = (
                    'https://github.com/bigswitch/bigrobot/blob/master/'
                     + match.group(1))
        self._suite['name'] = helpers.utf8(suite['@name'])
        if self._suite['source_github'] in authors:
            self._suite['author'] = authors[self._suite['source_github']]
        else:
            self._suite['author'] = None

        # Test cases
        tests = suite['test']
        for a_test in tests:
            test_id = helpers.utf8(a_test['@id'])
            name = helpers.utf8(a_test['@name'])
            if (('tags' in a_test and a_test['tags'] != None)
                and 'tag' in a_test['tags']):
                tags = helpers.utf8(a_test['tags']['tag'])
            else:
                tags = []
            self._tests.append(TestCase(test_id=test_id,
                                        name=name,
                                        tags=tags))
        self.total_tests()

    def suite(self):
        return self._suite

    def suite_name(self):
        return self._suite['name']

    def tests(self):
        return self._tests

    def total_tests(self):
        self._suite['total_tests'] = len(self.tests())
        return self._suite['total_tests']

    def dump_suite(self):
        print(helpers.prettify(self.suite()))

    def dump_tests(self):
        for test in self.tests():
            print(test.dump())

    def dump_raw(self):
        print(helpers.prettify(self.data))

    def dump_xml(self):
        print("%s" % helpers.prettify_xml(self.xml_str))


class TestCatalog(object):
    def __init__(self):
        self._suites = []

    def load_suites(self, filenames):
        for filename in filenames:
            filename = filename.strip()
            suite = TestSuite(filename)
            suite.dump_suite()
            suite.dump_tests()
            print "-----------------------"
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
    input_file = sys.argv[1]
    input_files = helpers.file_read_once(input_file, to_list=True)

    t = TestCatalog()
    t.load_suites(input_files)
    print "Total suites: %s" % t.total_suites()
    print "Total tests: %s" % t.total_tests()

