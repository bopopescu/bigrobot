#!/usr/bin/env python

import os
import sys
import argparse
from pymongo import MongoClient
# import robot

# Determine BigRobot path(s) based on this executable (which resides in
# the bin/ directory.
bigrobot_path = os.path.dirname(__file__) + '/..'
exscript_path = bigrobot_path + '/vendors/exscript/src'

sys.path.insert(0, bigrobot_path)
sys.path.insert(1, exscript_path)

import autobot.helpers as helpers
# import autobot.devconf as devconf

helpers.set_env('IS_GOBOT', 'False')
helpers.set_env('AUTOBOT_LOG', './myrobot.log')


TEST_TYPES = ["feature", "scaling", "performance", "solution", "longevity",
              "negative", "robustness"]
FEATURES_IRONHORSE = ["ha", "span", "testpath", "pod", "l2", "l3", "snmp",
                      "ntp", "traffic", "logging", "rsyslog", "rsyslogd",
                      "install", "initialconfig", "rebootswitch",
                      "firstboot", "upgrade", "singlenode", "bpdu_guard",
                      "fabric", "fabric_qos", "qos", "ztn", "file management",
                      "filemanagement", "running-config", "initialconfig",
                      "virtualip", "openstack", "dhcp", "dhcp-relay",
                      "ecmp", "policy", "policy-vlanrewrite"]


class ReleaseStats(object):
    def __init__(self,
                 release,
                 db_server='qadashboard-mongo.bigswitch.com',
                 db_port=27017,
                 db='test_catalog2'):
        self._release = release
        self._db_server = db_server
        self._db_port = db_port
        client = MongoClient(self._db_server, self._db_port)
        self._db = client[db]
        self._authors = {}

    def release(self):
        return self._release.lower

    def release_lowercase(self):
        return self._release.lower()

    def db(self):
        return self._db

    def testcases(self, release=None, build=None, collection_testcases=None):
        """
        Returns a Mongo cursor to test case documents.
        """
        collection_testcases = (collection_testcases or 'test_cases')
        testcases = self.db()[collection_testcases]
        query = {}
        if release:
            query["tags"] = { "$all": [release] }
        if build:
            query['build_name'] = build
        return testcases.find(query)

    def testsuites(self, **kwargs):
        """
        Returns a list containing product_suite, total_tests, and author.
        """
        testsuites = self.db()['test_suites']
        collection_suites = testsuites.find({},
                                            {"product_suite": 1, "author": 1,
                                             "total_tests": 1, "_id": 0})
        suites_lookup = {}
        for s in collection_suites:
            name = helpers.utf8(s['product_suite'])
            suites_lookup[name] = s

        testcases = self.testcases(**kwargs)
        suite_names = {}
        for tc in testcases:
            name = helpers.utf8(tc['product_suite'])
            if name not in suite_names:
                suite_names[name] = 0
            else:
                suite_names[name] += 1
        suites = []
        for k, v in suite_names.items():
            if k in suites_lookup:
                author = suites_lookup[k]['author']
            else:
                author = '???'
            suites.append({
                            "product_suite": k,
                            "total_tests": v,
                            "author": author,
                            })
        return suites

    def total_testcases(self, **kwargs):
        return self.testcases(**kwargs).count()

    def total_testsuites(self, **kwargs):
        suites = self.testsuites(**kwargs)
        return len(suites)


    #
    # The methods below need to be refactored.
    #

    def _total_testsuites_and_testcases(self, query=None):
        if query == None:
            query = {"tags": { "$all": [self.release_lowercase()] }}
        testcases = self.db()["test_cases_archive"]
        cases = testcases.find(query)
        suites = {}
        total_testcases = 0
        total_pass = 0
        total_fail = 0
        for x in cases:
            name = x['product_suite']
            if name not in suites:
                suites[name] = 0
            status = x['status']
            if status == 'PASS':
                total_pass += 1
            elif status == 'FAIL':
                total_fail += 1
            suites[name] += 1
            total_testcases += 1
        return len(suites), total_testcases, total_pass, total_fail

    def suite_authors(self, collection="test_suites"):
        testsuites = self.db()[collection]
        suites = testsuites.find()
        for x in suites:
            product_suite = x['product_suite']
            author = x['author']
            self._authors[product_suite] = author
        return self._authors

    def manual_untested_by_tag(self, tag, collection="test_cases"):
        authors = self.suite_authors()
        tags = helpers.list_flatten([self.release_lowercase(), "manual-untested", tag])
        query = {"tags": { "$all": tags }}
        testcases = self.db()[collection]
        cases = testcases.find(query)
        tests = []
        for x in cases:
            tests.append("%s %s %s %s"
                         % (authors[x['product_suite']],
                            x['product_suite'],
                            x['name'],
                            [helpers.utf8(tag) for tag in x['tags']]))
        return tests

    def total_testcases_by_tag(self, tag, collection="test_cases", query=None):
        """
        tag - can be a single tag or a list of tags.
        """
        tags = [self.release_lowercase(), tag]
        if helpers.is_list(tag):
            tags = helpers.list_flatten(tags)
        if query == None:
            query = {"tags": { "$all": tags }}
        testcases = self.db()[collection]
        cases = testcases.find(query)
        total_testcases = 0
        total_pass = 0
        total_fail = 0
        for x in cases:
            total_testcases += 1
            status = x['status']
            if status == 'PASS':
                total_pass += 1
            elif status == 'FAIL':
                total_fail += 1

        return total_testcases, total_pass, total_fail

    def total_executable_testcases(self):
        total = (self.total_testcases(release=self.release_lowercase())
                 - self.total_testcases_by_tag('manual-untested')[0])
        return total

    # Tests executed. Query based on build_name

    def total_testsuites_executed(self, build_name=None):
        query = {"tags": { "$all": [self.release_lowercase()] },
                 "build_name": build_name}
        total_suites, _, total_pass, total_fail = \
                self._total_testsuites_and_testcases(query)
        return total_suites, total_pass, total_fail

    def total_testcases_executed(self, build_name=None):
        query = {"tags": { "$all": [self.release_lowercase()] },
                 "build_name": build_name}
        _, total_testcases, total_pass, total_fail = \
                self._total_testsuites_and_testcases(query)
        return total_testcases, total_pass, total_fail

    def total_testcases_by_tag_executed(self, tag, build_name=None):
        """
        tag - can be a single tag or a list of tags.
        """
        tags = tag
        if helpers.is_list(tag):
            tags = helpers.list_flatten(tags)

        tags_and_release = helpers.list_flatten([self.release_lowercase(), tag])
        query = {"tags": { "$all": tags_and_release },
                 "build_name": build_name}
        return self.total_testcases_by_tag(tags,
                                           collection="test_cases_archive",
                                           query=query)

    def total_executable_testcases_executed(self, build_name=None):
        total = self.total_testcases_executed(build_name=build_name)
        return total


def print_stat(descr, val, untested=None):
    if untested != None:
        print("%-67s %18s  manual-untested(%s)" % (descr, val, untested))
    else:
        print("%-67s %18s" % (descr, val))


def print_testcases(testcases):
    print "\n".join(sorted(["\t%s" % helpers.utf8(x) for x in testcases]))


def print_suites(suites):
    i = 0
    total_tests = 0
    for n in suites:
        i += 1
        print "\t%3d. %-15s (%3s test cases) %s" % (i, n['author'], n['total_tests'], n['product_suite'])
        total_tests += n['total_tests']
    print "\t%d total test cases" % total_tests


def print_suites_not_executed(suites, suites_executed):
    suite_executed_lookup = {}
    for n in suites_executed:
        name = n['product_suite']
        suite_executed_lookup[name] = True
    i = 0
    for n in suites:
        name = n['product_suite']
        if name not in suite_executed_lookup:
            i += 1
            print "\t%3d. %-15s %s" % (i, n['author'], name)


def prog_args():
    descr = """\
Display test execution stats collected for a specific build.
"""
    parser = argparse.ArgumentParser(prog='db_collect_stats',
                                     description=descr)
    parser.add_argument('--release', required=True,
                        help=("Product release, e.g., 'IronHorse'"))
    parser.add_argument('--build', required=True,
                        help=("Jenkins build string,"
                              " e.g., 'bvs master #2007'"))
    parser.add_argument('--show-untested', action='store_true', default=False,
                        help=("Show the manual-untested test cases"))
    parser.add_argument('--show-suites', action='store_true', default=False,
                        help=("Show the test suites"))
    return parser.parse_args()


def display_stats(args):
    build = args.build

    ih = ReleaseStats(args.release)

    print_stat("Total of all test suites:", ih.total_testsuites())
    print_stat("Total of all test cases:", ih.total_testcases())

    print ""
    print "%s Release Metrics (Build: %s)" % (args.release, build)
    print "====================================================="
    total_testsuites_in_release = ih.total_testsuites(
               release=ih.release_lowercase())
    print_stat("Total test suites:", total_testsuites_in_release)
    print_stat("Total test cases:",
               ih.total_testcases(release=ih.release_lowercase()))

    for functionality in TEST_TYPES:
        print_stat("Total %s tests:" % functionality,
                   ih.total_testcases_by_tag(functionality)[0])

    print_stat("Total executable test cases:",
               ih.total_executable_testcases())

    total_testsuites_in_release_executed = ih.total_testsuites_executed(
               build_name=build)[0]
    print_stat("Total test suites executed:",
               total_testsuites_in_release_executed)
    if args.show_suites:
        suites_executed = ih.testsuites(
                               release=ih.release_lowercase(),
                               build=build,
                               collection_testcases="test_cases_archive")
        print_suites(suites_executed)

    print_stat("Total test suites not executed:",
               total_testsuites_in_release - total_testsuites_in_release_executed)
    if args.show_suites:
        suites_executed = ih.testsuites(
                               release=ih.release_lowercase(),
                               build=build,
                               collection_testcases="test_cases_archive")
        suites_in_release = ih.testsuites(release=ih.release_lowercase())
        print_suites_not_executed(suites_in_release, suites_executed)


    print ""
    print_stat("Total test cases (executed, passed, failed):",
               ih.total_testcases_executed(build_name=build),
               untested=ih.total_testcases_by_tag(["manual-untested"])[0])

    for functionality in TEST_TYPES + ["manual", "manual-untested"]:
        untested = ih.total_testcases_by_tag([functionality,
                                              "manual-untested"])[0]
        print_stat("Total %s tests (executed, passed, failed):"
                   % functionality,
                   ih.total_testcases_by_tag_executed(functionality,
                                                      build_name=build),
                   untested)
        if args.show_untested:
            print_testcases(ih.manual_untested_by_tag(functionality))

    print ""
    functionality = "feature"
    for feature in FEATURES_IRONHORSE:
        untested = ih.total_testcases_by_tag([functionality, feature,
                                              "manual-untested"])[0]
        print_stat("Total %s+%s tests (executed, passed, failed):"
                   % (functionality, feature),
                   ih.total_testcases_by_tag_executed([functionality, feature],
                                                      build_name=build),
                   untested)
        if args.show_untested:
            print_testcases(ih.manual_untested_by_tag([functionality, feature]))

#    print ""
#    print_stat("Total manual tests (executed, passed, failed):",
#               ih.total_testcases_by_tag_executed("manual",
#                                                  build_name=build))
#    print_stat("Total manual-untested tests (executed, passed, failed):",
#               ih.total_testcases_by_tag_executed("manual-untested",
#                                                  build_name=build))
#    print_stat("Total executable test cases (executed, passed, failed):",
#               ih.total_executable_testcases_executed(build_name=build))


if __name__ == '__main__':
    display_stats(prog_args())
