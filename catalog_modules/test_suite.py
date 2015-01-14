import os
import re
import xmltodict
import getpass
import autobot.helpers as helpers
from catalog_modules.test_catalog import TestCatalog
from catalog_modules.authors import Authors


class TestSuite(object):
    def __init__(self, filename, is_regression=False, is_baseline=False):
        """
        filename: output.xml file (with path)
        """
        self._build = {}
        self._suite = {}
        self._tests = []
        self._total_tests = 0
        self._filename = filename
        self._db = TestCatalog().db()

        self._is_regression = is_regression
        self._is_baseline = is_baseline

        # Remove first line: <?xml version="1.0" encoding="UTF-8"?>
        self.xml_str = ''.join(helpers.file_read_once(self._filename,
                                                      to_list=True)[1:])
        self._data = xmltodict.parse(self.xml_str)

    def db(self):
        return self._db

    def db_count_testcases(self):
        testcases = self.db().test_cases
        count = testcases.count()
        return count

    def db_insert(self, rec, collection):
        col = self.db()[collection]
        _id = col.insert(rec)

        # Side effect of insert operation is that it will insert the ObjectID
        # into rec, which may cause subsequent operations to fail (e.g.,
        # to_json(). So we remove the ObjectID.
        del rec['_id']
        return _id

    def db_find_and_modify_regression_testcase(self, rec):
        testcases = self.db().test_cases_archive

        tc = testcases.find_and_modify(
                query={ "name": rec['name'],
                        "product_suite" : rec['product_suite'],
                        "build_name": rec['build_name'] },
                        # "build_number": rec['build_number'] },
                        # "starttime_datestamp" : rec['starttime_datestamp'],
                update={ "$set": rec },  # update entire record
                upsert=True
                )
        arg_str = (' (name:"%s", product_suite:"%s", build_name:"%s",'
                   ' date:"%s", status:"%s")'
                   % (rec['name'], rec['product_suite'], rec['build_name'],
                      rec['starttime_datestamp'], rec['status']))
        if tc:
            print('Successfully updated Regression "test_cases_archive" record'
                  + arg_str)
        else:
            print('Did not find Regression "test_cases_archive" record'
                  + arg_str)

    def db_find_and_modify_testcase(self, rec):
        testcases = self.db().test_cases

        tc = testcases.find_and_modify(
                query={ "name": rec['name'],
                        "product_suite" : rec['product_suite'],
                        },
                update={ "$set": rec },
                # upsert=True
                )
        arg_str = (' (name:"%s", product_suite:"%s", build_name:"%s",'
                   ' date:"%s", status:"%s")'
                   % (rec['name'], rec['product_suite'], rec['build_name'],
                      rec['starttime_datestamp'], rec['status']))
        if tc:
            print('Successfully updated "test_cases" record' + arg_str)
        else:
            print('CRITICAL ERROR: Did not find "test_cases" record' + arg_str)

    def db_add_if_not_found_build(self, rec):
        builds = self.db().builds

        build = builds.find_one({ "build_name": rec['build_name'] })
        arg_str = ' (build_name:"%s")' % (rec['build_name'])
        if build:
            print('Found build record'
                  + arg_str + '. Skipping insertion.')
        else:
            print('Did not find build record'
                  + arg_str + '. Inserting new record.')
            self.db_insert(rec, collection="builds")

    def db_add_if_not_found_suite(self, rec):
        suites = self.db().test_suites

        suite = suites.find_one({ "product_suite" : rec['product_suite'],
                                  "build_name": rec['build_name'],
                                  })
        arg_str = (' (name:"%s", product_suite:"%s", build_name:"%s")'
                   % (rec['name'], rec['product_suite'], rec['build_name']))
        if suite:
            print('Found suite record'
                  + arg_str + '. Skipping insertion.')

        else:
            print('Did not find suite record'
                  + arg_str + '. Inserting new record.')
            self.db_insert(rec, collection="test_suites")

    def db_add_if_not_found_testcase(self, rec):
        testcases = self.db().test_cases

        tc = testcases.find_one({ "name": rec['name'],
                                  "product_suite": rec['product_suite'],
                                  "build_name": rec['build_name'],
                                   })
        arg_str = (' (name:"%s", product_suite:"%s", build_name:"%s")'
                   % (rec['name'], rec['product_suite'], rec['build_name']))
        if tc:
            print('Found test case record'
                  + arg_str + '. Skipping insertion.')
        else:
            print('Did not find test case record'
                  + arg_str + '. Inserting new record.')
            self.db_insert(rec, collection="test_cases")

    def data(self):
        """
        Handle to the XML data from input file (output.xml).
        """
        if 'robot' not in self._data:
            helpers.environment_failure(
                    "Fatal error: expecting data['robot']")
        if 'suite' not in self._data['robot']:
            helpers.environment_failure(
                    "Fatal error: expecting data['robot']['suite']")
        if 'test' not in self._data['robot']['suite']:
            helpers.environment_failure(
                    "Fatal error: expecting data['robot']['suite']['test']")
        return self._data

    def git_auth(self, filename):
        filename = re.sub(r'.*bigrobot/', '../', filename)
        (status, output, err_out, err_code) = helpers.run_cmd2("./git-auth " + filename, shell=True)
        output = output.strip()
        authors = Authors.get()
        if output in authors:
            return authors[output]
        elif status == False:
            helpers.log(
                    "ERROR: Shell command error (code:'%s', mesg:'%s') for file '%s'. Using 'unknown' author."
                    % (err_code, err_out, filename))
        else:
            helpers.log(
                    "ERROR: Author '%s' does not exist for file '%s'. Using 'unknown' author."
                    % (output, filename))
        return authors['Unknown']

    def check_topo_type(self, suite):
        """
        Give the 'suite' input which is the path to a suite file (minus the
        '.txt' extension). Check whether it has <suite>.virtual.topo or
        <suite>.physical.topo.

        Return value:
          'virtual'
          'physical'
          'unknown'  - neither virtual nor physical
        """
        if helpers.file_exists(suite + ".virtual.topo"):
            return "virtual"
        if helpers.file_exists(suite + ".physical.topo"):
            return "physical"
        if helpers.file_exists(suite + ".topo"):
            return "generic-topology"
        return "missing-topology"

    def db_populate_suite(self):
        if self._is_regression:
            pass
        elif self._is_baseline:
            self.db_add_if_not_found_suite(self._suite)

    def db_populate_test_case(self, test):
        if self._is_regression:
            if 'BUILD_NUMBER' in os.environ:
                test['build_number'] = os.environ['BUILD_NUMBER']
            if 'BUILD_URL' in os.environ:
                test['build_url'] = os.environ['BUILD_URL']
            self.db_find_and_modify_regression_testcase(test)
        elif self._is_baseline:
            self.db_add_if_not_found_testcase(test)

    def extract_suite_attributes(self):
        """
        Extract test data from XML, create test suite data structure.
        Note: Need to extract test case attributes first to get the
        total_tests data.
        """
        suite = self.data()['robot']['suite']
        timestamp = helpers.format_robot_timestamp(
                            self.data()['robot']['@generated'])
        datestamp = helpers.format_robot_datestamp(self.data()['robot']['@generated'])
        source = source_file = helpers.utf8(suite['@source'])
        match = re.match(r'.+bigrobot/(\w+/([\w-]+)/.+)$', source)
        if match:
            source = "bigrobot/" + match.group(1)
            github_link = ('https://github.com/bigswitch/bigrobot/blob/master/'
                           + match.group(1))
            product = match.group(2)
        else:
            helpers.environment_failure(
                "Fatal error: Source file has invalid format ('%s')" % source)
        author = self.git_auth(source)
        name_actual = os.path.splitext(os.path.basename(source))[0]
        product_suite = os.path.splitext(source)[0]
        product_suite = re.sub(r'.*bigrobot/testsuites/', '', product_suite)
        topo_type = self.check_topo_type(os.path.splitext(source_file)[0])

        self._suite = {
                    'source': source,
                    'createtime': helpers.ts_long_local(),
                    'starttime': helpers.utf8(timestamp),
                    'starttime_datestamp': helpers.utf8(datestamp),
                    'github_link': github_link,
                    'name_actual': name_actual,
                    'name': helpers.utf8(suite['@name']),
                    'product': product,
                    'product_suite': product_suite,
                    'author': author,
                    'total_tests': self.total_tests(),
                    'topo_type': topo_type,
                    'notes': None,
                    'build_name': os.environ['BUILD_NAME'],
                    'created_by': getpass.getuser(),
                    }

    def extract_test_attributes(self, test_xml):
        # print "['@id']: " + '@id'
        # print "a_test['@id']: " + a_test['@id']
        # print "*** a_test: %s" % a_test
        test_id = helpers.utf8(test_xml['@id'])
        name = helpers.utf8(test_xml['@name'])
        if (('tags' in test_xml and test_xml['tags'] != None)
            and 'tag' in test_xml['tags']):
            tags = helpers.utf8(test_xml['tags']['tag'])

            # Normalize data - convert tags to lowercase
            tags = [x.lower() for x in tags]
        else:
            tags = []

        if self._is_regression:
            # Regression
            # Analyzing regression results which should have PASS/FAIL
            # status.
            status = helpers.utf8(test_xml['status']['@status'])
            starttime = helpers.format_robot_timestamp(
                            helpers.utf8(test_xml['status']['@starttime']))
            starttime_datestamp = helpers.format_robot_datestamp(
                            helpers.utf8(test_xml['status']['@starttime']))
            endtime = helpers.format_robot_timestamp(
                            helpers.utf8(test_xml['status']['@endtime']))
            endtime_datestamp = helpers.format_robot_datestamp(
                            helpers.utf8(test_xml['status']['@endtime']))
            executed = True
        else:
            # Baseline
            status = None
            starttime = starttime_datestamp = None
            endtime = endtime_datestamp = None
            executed = False
            # starttime_datestamp = self._suite['starttime_datestamp']
            #   starttime_datestamp = '2014-05-28'

        # This should contain the complete list of attributes. Some may
        # be populated by the Script Catalog while others may be populated
        # later by Regression execution.
        test = {'test_id': test_id,
                'name': name,
                'tags': tags,
                'executed': executed,
                'status': status,
                'createtime': helpers.ts_long_local(),
                'starttime': starttime,
                'starttime_datestamp': starttime_datestamp,
                'endtime': endtime,
                'endtime_datestamp': endtime_datestamp,
                'duration': None,
                'origin_script_catalog': not self._is_regression,
                'origin_regression_catalog': self._is_regression,
                'product_suite': self._suite['product_suite'],
                'build_number': None,
                'build_url': None,
                'build_name': os.environ['BUILD_NAME'],
                'notes': None,
                'created_by': getpass.getuser(),
                }
        return test

    def extract_test_attributes_and_db_populate(self):
        """
        Extract test data from XML, create test case data structure.
        For regression, it also populates the test data into the DB.
        For baseline, it doesn't populate the DB - this step is deferred
        until later for performance reason.
        """
        tests = self.data()['robot']['suite']['test']

        if not helpers.is_list(tests):
            # In a suite with only a single test case, convert into list
            tests = [tests]

        if self._is_regression:
            helpers.debug("DB testcase count (BEFORE): %s"
                          % self.db_count_testcases())

        for a_test in tests:
            test = self.extract_test_attributes(a_test)
            if self._is_regression:
                self.db_populate_test_case(test)
            self._tests.append(test)

        self.total_tests()

    def extract_attributes(self):
        """
        Populate regression test data into the DB. For baseline data, we defer
        DB update until later for performance reason.
        """
        self.extract_suite_attributes()
        self.extract_test_attributes_and_db_populate()
        if self._is_regression:
            self.db_populate_suite()

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
                helpers.log("Writing to file '%s'" % to_file)
                helpers.file_write_append_once(to_file,
                                               helpers.to_json(self.tests())
                                               + '\n')
            else:
                print(helpers.to_json(self.tests()))
        else:
            if to_file:
                helpers.log("Writing to file '%s'" % to_file)
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
