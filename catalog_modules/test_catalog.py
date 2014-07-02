from pymongo import MongoClient
import catalog_modules.cat_helpers as cat_helpers


class TestCatalog(object):
    def __init__(self):
        self._configs = None
        self._db = None
        self._connected = False
        self.connect()

    def configs(self):
        if not self._configs:
            self._configs = cat_helpers.load_config_catalog()
        return self._configs

    def connect(self):
        server = self.configs()['db_server']
        port = self.configs()['db_port']
        database = self.configs()['database']
        client = MongoClient(server, port)
        self._db = client[database]

    def db(self):
        if not self._connected:
            self.connect()
            self._connected = True
        return self._db

    def test_suites(self):
        return self.db()['test_suites']

    def test_cases(self):
        return self.db()['test_cases']

    def test_cases_archive(self):
        return self.db()['test_cases_archive']

    def test_types(self):
        return self.configs()['test_types']

    def features(self, release):
        return self.configs()['features'][release]

    def aggregated_build(self, build_name):
        config = self.configs()
        if 'aggregated_builds' not in config:
            return None
        if build_name not in config['aggregated_builds']:
            return None
        return ['aggregated_builds'][build_name]

    def remove_docs(self, collection, query):
        count = self.db()[collection].find(query).count()
        if count > 0:
            self.db()[collection].remove(query)
        return count

    def remove_test_suites_matching_build(self, build_name):
        return self.remove_docs(collection='test_suites',
                                query={"build_name": build_name})

    def remove_test_cases_matching_build(self, build_name):
        return self.remove_docs(collection='test_cases',
                                query={"build_name": build_name})
