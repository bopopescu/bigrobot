import autobot.helpers as helpers
from catalog_modules.test_catalog import TestCatalog


class BuildStats(object):
    def __init__(self, release, build):
        self._release = release
        self._build_name = build
        self._authors = {}
        self._catalog = TestCatalog()

    def catalog(self):
        return self._catalog

    def release(self):
        return self._release

    def release_lowercase(self):
        return self._release.lower()

    def testcases(self, release=None, build=None, collection_testcases=None):
        """
        Returns a Mongo cursor to test case documents.
        """
        collection_testcases = (collection_testcases or 'test_cases')
        testcases = self.catalog().db()[collection_testcases]
        query = {}
        if release:
            query["tags"] = { "$all": [release] }
        if build:
            query['build_name'] = build
        else:
            query['build_name'] = self._build_name
        return testcases.find(query)

    def testcases_archive(self, release=None, build=None, collection_testcases=None):
        collection_testcases = (collection_testcases or 'test_cases_archive')
        return self.testcases(release=release, build=build,
                              collection_testcases=collection_testcases)

    def testsuites(self, **kwargs):
        """
        Returns a list containing product_suite, total_tests, and author.
        """
        testsuites = self.catalog().test_suites_collection()
        collection_suites = testsuites.find({"build_name": self._build_name},
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
                suite_names[name] = 1  # initialization
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
        testcases = self.catalog().db()["test_cases_archive"]
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
        testsuites = self.catalog().db()[collection]
        suites = testsuites.find()
        for x in suites:
            product_suite = x['product_suite']
            author = x['author']
            self._authors[product_suite] = author
        return self._authors

    def manual_by_tag(self, tag=None, collection="test_cases"):
        authors = self.suite_authors()

        if tag == None:
            tags = helpers.list_flatten([self.release_lowercase(),
                                         "manual"])
        else:
            tags = helpers.list_flatten([self.release_lowercase(),
                                         "manual", tag])

        query = {"tags": { "$all": tags },
                 "build_name": self._build_name}
        testcases = self.catalog().db()[collection]
        cases = testcases.find(query)
        tests = []
        for x in cases:
            tests.append("%s %s %s %s"
                         % (authors[x['product_suite']],
                            x['product_suite'],
                            x['name'],
                            [helpers.utf8(tag) for tag in x['tags']]))
        return tests

    def manual_untested_by_tag(self, tag=None, collection="test_cases"):
        authors = self.suite_authors()

        if tag == None:
            tags = helpers.list_flatten([self.release_lowercase(),
                                         "manual-untested"])
        else:
            tags = helpers.list_flatten([self.release_lowercase(),
                                         "manual-untested", tag])

        query = {"tags": { "$all": tags },
                 "build_name": self._build_name}
        testcases = self.catalog().db()[collection]
        cases = testcases.find(query)
        tests = []
        for x in cases:
            tests.append("%s %s %s %s"
                         % (authors[x['product_suite']],
                            x['product_suite'],
                            x['name'],
                            [helpers.utf8(tag) for tag in x['tags']]))
        return tests

    def total_testcases_by_tag(self, tag, collection="test_cases"):
        """
        tag - can be a single tag or a list of tags.
        """
        tags = [self.release_lowercase(), tag]
        if helpers.is_list(tag):
            tags = helpers.list_flatten(tags)
        query = {"tags": { "$all": tags },
                 "build_name": self._build_name}
        testcases = self.catalog().db()[collection]
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

    def total_testcases_by_tag_executed(self, tag):
        """
        tag - can be a single tag or a list of tags.
        """
        tags = tag
        if helpers.is_list(tag):
            tags = helpers.list_flatten(tags)

        tags_and_release = helpers.list_flatten([self.release_lowercase(),
                                                 tag])
        return self.total_testcases_by_tag(tags_and_release,
                                           collection="test_cases_archive")

    def total_executable_testcases_executed(self, build_name=None):
        total = self.total_testcases_executed(build_name=build_name)
        return total
