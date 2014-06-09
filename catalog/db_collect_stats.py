#!/usr/bin/env python

import os
import sys
import argparse
from pymongo import MongoClient
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
helpers.set_env('AUTOBOT_LOG', './myrobot.log')


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

    def release(self):
        return self._release

    def release_lc(self):
        return self._release.lower()

    def db(self):
        return self._db

    def total_of_all_testsuites(self, collection="test_suites"):
        testsuites = self.db()[collection]
        total_suites = testsuites.find().count()
        return total_suites

    def total_of_all_testcases(self, collection="test_cases"):
        testcases = self.db()[collection]
        total_cases = testcases.find().count()
        return total_cases

    def _total_testsuites_and_testcases(self,
                                        collection="test_cases",
                                        query=None):
        if query == None:
            query = {"tags": { "$all": [self.release_lc()] }}
        testcases = self.db()[collection]
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

    def total_testsuites(self, collection="test_cases"):
        total_suites, _, _, _ = \
                self._total_testsuites_and_testcases(collection)
        return total_suites

    def total_testcases(self, collection="test_cases"):
        _, total_testcases, _, _ = \
                self._total_testsuites_and_testcases(collection)
        return total_testcases

    def total_testcases_by_tag(self, tag, collection="test_cases",
                               query=None):
        """
        tag - can be a single tag or a list of tags.
        """
        tags = [self.release_lc(), tag]
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

    def total_executable_testcases(self, collection="test_cases"):
        total = (self.total_testcases(collection)
                 - self.total_testcases_by_tag('manual-untested',
                                               collection)[0])
        return total

    # Tests executed. Query based on build_name

    def total_testsuites_executed(self, collection="test_cases_archive",
                                  build_name=None):
        query = {"tags": { "$all": [self.release_lc()] },
                 "build_name": build_name}
        total_suites, _, total_pass, total_fail = \
                self._total_testsuites_and_testcases(collection, query)
        return total_suites, total_pass, total_fail

    def total_testcases_executed(self, collection="test_cases_archive",
                                 build_name=None):
        query = {"tags": { "$all": [self.release_lc()] },
                 "build_name": build_name}
        _, total_testcases, total_pass, total_fail = \
                self._total_testsuites_and_testcases(collection, query)
        return total_testcases, total_pass, total_fail

    def total_testcases_by_tag_executed(self, tag,
                                        collection="test_cases_archive",
                                        build_name=None):
        tags = [self.release_lc(), tag]
        query = {"tags": { "$all": tags },
                 "build_name": build_name}
        return self.total_testcases_by_tag(tag, collection, query)

    def total_executable_testcases_executed(self,
                                            collection="test_cases_archive",
                                            build_name=None):
        total = self.total_testcases_executed(collection,
                                              build_name=build_name)
        return total


def print_stat(descr, val, untested=None):
    if untested != None:
        print("%-60s %15s  manual-untested(%s)" % (descr, val, untested))
    else:
        print("%-60s %15s" % (descr, val))

def collect_stats():
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
    args = parser.parse_args()
    build = args.build

    ih = ReleaseStats(args.release)

    print_stat("Total of all test suites:", ih.total_of_all_testsuites())
    print_stat("Total of all test cases:", ih.total_of_all_testcases())

    print ""
    print "%s Release Metrics (Build: %s)" % (args.release, build)
    print "====================================================="
    print_stat("Total test suites:",
               ih.total_testsuites())
    print_stat("Total test cases:",
               ih.total_testcases())
    print_stat("Total feature tests:",
               ih.total_testcases_by_tag("feature")[0])
    print_stat("Total scaling tests:",
               ih.total_testcases_by_tag("scaling")[0])
    print_stat("Total performance tests:",
               ih.total_testcases_by_tag("performance")[0])
    print_stat("Total solution tests:",
               ih.total_testcases_by_tag("solution")[0])
    print_stat("Total longevity tests:",
               ih.total_testcases_by_tag("longevity")[0])
    print_stat("Total negative tests:",
               ih.total_testcases_by_tag("negative")[0])
    print_stat("Total manual tests:",
               ih.total_testcases_by_tag("manual")[0])
    print_stat("Total manual-untested tests:",
               ih.total_testcases_by_tag("manual-untested")[0])
    print_stat("Total executable test cases:",
               ih.total_executable_testcases())

    print ""
    print_stat("Total test suites executed:",
               ih.total_testsuites_executed(build_name=build)[0])
    print_stat("Total test cases (executed, passed, failed):",
               ih.total_testcases_executed(build_name=build))

    for feature in ["feature", "scaling", "performance", "solution",
                    "longevity", "negative"]:
        untested = ih.total_testcases_by_tag([feature, "manual-untested"])[0]
        print_stat("Total %s tests (executed, passed, failed):" % feature,
               ih.total_testcases_by_tag_executed(feature,
                                                  build_name=build), untested)

    print_stat("Total manual tests (executed, passed, failed):",
               ih.total_testcases_by_tag_executed("manual",
                                                  build_name=build))
    print_stat("Total manual-untested tests (executed, passed, failed):",
               ih.total_testcases_by_tag_executed("manual-untested",
                                                  build_name=build))
    print_stat("Total executable test cases (executed, passed, failed):",
               ih.total_executable_testcases_executed(build_name=build))


if __name__ == '__main__':
    collect_stats()
