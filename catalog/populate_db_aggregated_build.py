#!/usr/bin/env python
# Search for test cases matching build names in the aggregated_builds list.
# If found, insert/update test cases in documents with matching BUILD_NAME.

import os
import sys

# Determine BigRobot path(s) based on this executable (which resides in
# the bin/ directory.
bigrobot_path = os.path.dirname(__file__) + '/..'
exscript_path = bigrobot_path + '/vendors/exscript/src'

sys.path.insert(0, bigrobot_path)
sys.path.insert(1, exscript_path)

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
                aggr_cursor = self.catalog().find_test_cases_archive(query)
                if aggr_cursor.count() != 1:
                    print("WARNING: Expecting only one aggregated test case, but result is '%s'"
                          % aggr_cursor.count())
                aggr_tc = aggr_cursor[0]
                if 'build_name_list' in aggr_tc:
                    tc['build_name_list'] = aggr_tc['build_name_list'] + [build]
                else:
                    tc['build_name_list'] = [build]

                tc['build_name_orig'] = build
                tc['build_name'] = self.aggregated_build()
                doc = self.catalog().upsert_doc('test_cases_archive',
                                                tc,
                                                query)
                if doc == None:
                    print("\n*** doc: %s, name:'%s', product_suite:'%s'"
                          % (doc, tc['name'], tc['product_suite']))
                else:
                    print("\n*** doc: %s" % doc)
                sys.exit(0)


if __name__ == '__main__':
    aggr_build = AggregatedBuild(os.environ['BUILD_NAME'])
    aggr_build.do_it()
