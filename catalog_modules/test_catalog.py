from pymongo import MongoClient
import catalog_modules.cat_helpers as cat_helpers


class TestCatalog(object):
    _configs = None
    _db = None
    _connected = False

    @classmethod
    def configs(self):
        if not TestCatalog._configs:
            TestCatalog._configs = cat_helpers.load_config_catalog()
        return TestCatalog._configs

    @classmethod
    def connect(self):
        server = TestCatalog.configs()['db_server']
        port = TestCatalog.configs()['db_port']
        database = TestCatalog.configs()['database']
        client = MongoClient(server, port)
        TestCatalog._db = client[database]
        TestCatalog._test_types = TestCatalog.configs()['test_types']

    @classmethod
    def db(self):
        if not TestCatalog._connected:
            TestCatalog.connect()
            TestCatalog._connected = True
        return TestCatalog._db

    @classmethod
    def test_suites(self):
        return TestCatalog.db()['test_suites']

    @classmethod
    def test_cases(self):
        return TestCatalog.db()['test_cases']

    @classmethod
    def test_cases_archive(self):
        return TestCatalog.db()['test_cases_archive']

    @classmethod
    def test_types(self):
        return TestCatalog.configs()['test_types']

    @classmethod
    def features(self, release):
        return TestCatalog.configs()['features'][release]

    @classmethod
    def aggregated_build(self, build_name):
        _config = TestCatalog.configs()
        if 'aggregated_builds' not in _config:
            return None
        if build_name not in _config['aggregated_builds']:
            return None
        return ['aggregated_builds'][build_name]

    @classmethod
    def remove_docs(self, collection, query):
        count = TestCatalog.db()[collection].find(query).count()
        if count > 0:
            TestCatalog.db()[collection].remove(query)
        return count

    @classmethod
    def remove_test_suites_matching_build(self, build_name):
        return TestCatalog.remove_docs(collection='test_suites',
                                       query={"build_name": build_name})

    @classmethod
    def remove_test_cases_matching_build(self, build_name):
        return TestCatalog.remove_docs(collection='test_cases',
                                       query={"build_name": build_name})
