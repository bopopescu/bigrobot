from pymongo import MongoClient
import autobot.helpers as helpers


class TestCatalog(object):
    """
    The data model for the test_catalog database in MongoDB.
    """
    def __init__(self):
        self._configs = None
        self._db = None
        self._connected = False
        self.connect()


    # Config file access

    def configs(self):
        if not self._configs:
            self._configs = helpers.bigrobot_config_test_catalog()
        return self._configs

    def test_types(self):
        return self.configs()['test_types']

    def features(self, release):
        return self.configs()['features'][release]

    def aggregated_build(self, build_name):
        """
        Returns a list of actual builds in an aggregated build.
        """
        config = self.configs()
        if 'aggregated_builds' not in config:
            return {}
        if build_name not in config['aggregated_builds']:
            return {}
        return config['aggregated_builds'][build_name]


    # DB access

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

    def test_suites_collection(self):
        return self.db()['test_suites']

    def test_cases_collection(self):
        return self.db()['test_cases']

    def test_cases_archive_collection(self):
        return self.db()['test_cases_archive']

    def aggregated_builds_collection(self):
        return self.db()['aggregated_builds']


    # DB query/update

    def find_and_add_aggregated_build(self, build_name):
        """
        Check whether 'build_name' is found in aggregated_builds collection.
        - If found, return the document.
        - If not found, create a new aggregated build document indexed by
          current year and week. Then return the document.
        """
        query = {"build_names": {"$all": [build_name]}}
        cursor = self.aggregated_builds_collection().find(query)
        count = cursor.count()
        if count >= 1:
            # Found aggregated build which contains the build_name.
            # print "***** Found aggregated build with '%s'." % build_name
            if count > 1:
                print "WARNING: Did not expect multiple results."
            return cursor[0]

        week_num = helpers.week_num()
        year = helpers.year()
        aggregated_build_name = ("bvs master aggregated %s wk%s"
                                 % (year, week_num))
        query = {"name": aggregated_build_name}
        cursor = self.aggregated_builds_collection().find(query)
        if cursor.count() >= 1:
            # Aggregated build for year/week exists. Add build_name to list.
            # print "***** Build '%s' not found. Found aggregated build '%s'." % (build_name, aggregated_build_name)
            doc = cursor[0]
            doc["build_names"].append(build_name)
            doc["updatetime"] = helpers.ts_long_local()
            _ = self.upsert_doc('aggregated_builds', doc, query)
            return doc
        else:
            # Aggregated build for year/week does not exist. Create it.
            # print "***** Not found aggregated build '%s'. Creating." % aggregated_build_name
            doc = {"name": aggregated_build_name,
                   "week_num": week_num,
                   "year": year,
                   "build_names": [build_name],
                   "createtime": helpers.ts_long_local(),
                   "updatetime": helpers.ts_long_local(),
                   }
            _ = self.insert_doc('aggregated_builds', doc)
            return doc

    def find_test_suites(self, query):
        return self.test_suites_collection().find(query)

    def find_test_cases_archive(self, query):
        return self.test_cases_archive_collection().find(query)

    def insert_doc(self, collection, document):
        if '_id' in document:
            del document['_id']
        return self.db()[collection].insert(document)

    def upsert_doc(self, collection, document, query):
        if '_id' in document:
            del document['_id']
        return self.db()[collection].find_and_modify(
                query=query,
                update={ "$set": document },
                upsert=True
                )

    def find_docs(self, collection, query):
        return self.db()[collection].find(query)

    def find_builds_matching_build(self, build_name):
        return self.find_docs(collection='builds',
                              query={"build_name": build_name})

    def find_test_suites_matching_build(self, build_name):
        query = {"build_name": build_name}
        return self.find_docs(collection='test_suites',
                              query=query)

    def find_test_cases_matching_build(self,
                                       build_name,
                                       release=None,
                                       tags=None,
                                       collection='test_cases'):
        query = {"build_name": build_name}
        if release:
            query["tags"] = { "$all": helpers.list_flatten([release, tags]) }
        return self.find_docs(collection=collection,
                              query=query)

    def find_test_cases_archive_matching_build(self, *args, **kwargs):
        new_kwargs = dict(kwargs)
        if 'collection' not in new_kwargs:
            new_kwargs['collection'] = 'test_cases_archive'
        return self.find_test_cases_matching_build(*args, **new_kwargs)

    def remove_docs(self, collection, query):
        count = self.db()[collection].find(query).count()
        if count > 0:
            self.db()[collection].remove(query)
        return count

    def remove_builds_matching_build(self, build_name):
        return self.remove_docs(collection='builds',
                                query={"build_name": build_name})

    def remove_test_suites_matching_build(self, build_name):
        return self.remove_docs(collection='test_suites',
                                query={"build_name": build_name})

    def remove_test_cases_matching_build(self,
                                         build_name,
                                         release=None,
                                         tags=None,
                                         collection='test_cases'):
        query = {"build_name": build_name}
        if release:
            query["tags"] = { "$all": helpers.list_flatten([release, tags]) }
        return self.remove_docs(collection=collection,
                                query=query)

    def remove_test_cases_archive_matching_build(self, *args, **kwargs):
        new_kwargs = dict(kwargs)
        if 'collection' not in new_kwargs:
            new_kwargs['collection'] = 'test_cases_archive'
        return self.remove_test_cases_matching_build(*args, **new_kwargs)
