#!/usr/bin/env python

import os
import sys
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


class IronHorseStats(object):
    def __init__(self,
                 db_server='qadashboard-mongo.bigswitch.com',
                 db_port=27017,
                 db='test_catalog2'):
        self._db_server = db_server
        self._db_port = db_port
        client = MongoClient(self._db_server, self._db_port)
        self._db = client[db]

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

    def _total_testsuites_and_testcases(self, collection="test_cases"):
        testcases = self.db()[collection]
        cases = testcases.find({"tags": { "$all": ["ironhorse"] }}, { "product_suite": 1, "_id": 0})
        suites = {}
        total_testcases = 0
        for x in cases:
            name = x['product_suite']
            if name not in suites:
                suites[name] = 0
            suites[name] += 1
            total_testcases += 1
        return len(suites), total_testcases

    def total_testsuites(self, collection="test_cases"):
        total_suites, _ = self._total_testsuites_and_testcases(collection)
        return total_suites

    def total_testcases(self, collection="test_cases"):
        _, total_testcases = self._total_testsuites_and_testcases(collection)
        return total_testcases

    def total_testcases_by_tag(self, tag, collection="test_cases"):
        testcases = self.db()[collection]
        tags = ["ironhorse", tag]
        total = testcases.find({"tags": { "$all": tags }}).count()
        return total

    def total_executable_testcases(self, collection="test_cases"):
        total = (self.total_testcases(collection)
                 - self.total_testcases_by_tag('manual-untested', collection))
        return total


def print_stat(descr, val):
    print("%-30s %10s" % (descr, val))


ih = IronHorseStats()

print_stat("Total of all test suites:", ih.total_of_all_testsuites())
print_stat("Total of all test cases:", ih.total_of_all_testcases())
print ""
print "Iron Horse Release Metrics"
print "=========================="
print_stat("Total test suites:", ih.total_testsuites())
print_stat("Total test cases:", ih.total_testcases())

print_stat("Total feature tests:", ih.total_testcases_by_tag("feature"))
print_stat("Total scaling tests:", ih.total_testcases_by_tag("scaling"))
print_stat("Total performance tests:", ih.total_testcases_by_tag("performance"))
print_stat("Total solution tests:", ih.total_testcases_by_tag("solution"))
print_stat("Total longevity tests:", ih.total_testcases_by_tag("longevity"))
print_stat("Total negative tests:", ih.total_testcases_by_tag("negative"))
print_stat("Total manual tests:", ih.total_testcases_by_tag("manual"))
print_stat("Total manual-untested tests:", ih.total_testcases_by_tag("manual-untested"))
print_stat("Total executable test cases:", ih.total_executable_testcases())
