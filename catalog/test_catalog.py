import cat_helpers
from pymongo import MongoClient


class TestCatalog(object):
    _configs = None
    _db = None
    _connected = False

    @classmethod
    def connect(self):
        TestCatalog._configs = cat_helpers.load_config_catalog()
        server = TestCatalog._configs['db_server']
        port = TestCatalog._configs['db_port']
        database = TestCatalog._configs['database']
        client = MongoClient(server, port)
        TestCatalog._db = client[database]
        TestCatalog._test_types = TestCatalog._configs['test_types']

    @classmethod
    def db(self):
        if not TestCatalog._connected:
            TestCatalog.connect()
            TestCatalog._connected = True
        return TestCatalog._db

    @classmethod
    def test_cases(self):
        return TestCatalog.db()['test_cases']

    @classmethod
    def test_suites(self):
        return TestCatalog.db()['test_suites']

    @classmethod
    def test_types(self):
        return TestCatalog._configs['test_types']

    @classmethod
    def features(self, release):
        return TestCatalog._configs['features'][release]
