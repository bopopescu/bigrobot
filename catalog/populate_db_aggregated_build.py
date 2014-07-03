#!/usr/bin/env python
# Remove documents in test_suites and test_cases collections which match
# BUILD_NAME.

import os
import sys

# Determine BigRobot path(s) based on this executable (which resides in
# the bin/ directory.
bigrobot_path = os.path.dirname(__file__) + '/..'

sys.path.insert(0, bigrobot_path)

import autobot.helpers as helpers
from catalog_modules.test_catalog import TestCatalog

if not 'BUILD_NAME' in os.environ:
    helpers.error_exit("Environment variable BUILD_NAME is not defined.", 1)


class AggregatedBuild(object):
    def __init__(self, build):
        self._aggregated_build = build
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

    def aggregated_build(self): return self._aggregated_build

    def builds(self): return self._builds

    def do_it(self):
        for build in self.builds():
            cursor = self.catalog().find_test_cases_archive_matching_build(build)
            for tc in cursor:
                query = { "name": tc['name'],
                          "product_suite": tc['product_suite'],
                          "build_name": self.aggregated_build(),
                         }
                tc['build_name_orig'] = build
                tc['build_name'] = self.aggregated_build()
                doc = self.catalog().upsert_doc('test_cases_archive',
                                                tc,
                                                query)
                print "*** doc: %s" % doc


if __name__ == '__main__':
    aggr_build = AggregatedBuild(os.environ['BUILD_NAME'])
    aggr_build.do_it()
