import getpass
import re
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
        """
        Returns a list of features for a release.
        """
        return self.configs()['features'][release]

    def products(self):
        """
        Returns a list of defined products.
        """
        return self.configs()['products'].keys()

    def releases(self, product):
        """
        Returns a list of releases for a product or empty list for no match.
        """
        if product in self.products():
            releases_list = self.configs()['products'][product]['releases']
            releases = helpers.list_flatten([rel.keys() for rel in releases_list])
            return releases
        return []

    def get_product_for_build_name(self, build_name):
        """
        Returns the product which matches a build name or None for no match.
        E.g.,
        - build_name='ihplus_bcf-104' matches 'bcf' product.
        - build_name='corsair_bigtap-99' matches 'bigtap' product.
        """
        for product in self.products():
            if re.search(product, build_name, re.I):
                return product
        return None

    def get_base_release_for_build_name(self, build_name, product):
        """
        'product' is the product name as defined in configs/catalog.yaml
        (e.g., 'bcf', 'bigtap', etc).

        Returns the release name in the build_name string. See the BUILD_NAME
        convention wiki guide at:
        https://bigswitch.atlassian.net/wiki/pages/viewpage.action?pageId=58327098

        Sample BUILD_NAME:
            AS5710-54X_ihplus_bcf-132
                       ^^^^^^ image release name
        """
        match = re.match(r'^([\w-]+)_(\w+)_.*$', build_name)
        base_release = None
        if match:
            image_release = match.group(2)
            releases_list = self.configs()['products'][product]['releases']
            for release in releases_list:
                r = release.keys()[0]
                if image_release in release[r]['software_image_map']:
                    base_release = r
                    break
        return base_release

    def get_releases_for_build_name(self, build_name):
        """
        Returns a list of releases which match a build name or empty list
        for no match.
        E.g.,
        - build_name='ihplus_bcf-104' matches
            ['ironhorse', 'ironhorse-plus']
        - build_name='corsair400_bigtap-99' matches
            ['augusta', 'blackbird', 'corsair-4.0.0']
        """
        product = self.get_product_for_build_name(build_name)
        base_release = self.get_base_release_for_build_name(build_name, product)
        releases = self.releases(product)

        # Only matches releases up to the base release. For example, if the
        # base release is IronHorse-Plus, only matches IronHorse and
        # IronHorse-Plus but not JackFrost.
        if base_release in releases:
            return releases[ : releases.index(base_release) + 1 ]
        else:
            return releases

    def aggregated_build(self, build_name):
        """
        Returns a list of actual builds in an aggregated build. Data is
        retrieved from the aggregated_build collection.
        """
        query = {"name": build_name}
        cursor = self.aggregated_builds_collection().find(query)
        count = cursor.count()

        if count >= 1:
            return cursor[0]['build_names']
        else:
            return []


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

    def builds_collection(self):
        return self.db()['builds']

    def aggregated_builds_collection(self):
        return self.db()['aggregated_builds']

    def test_suite_author_mapping(self, build_name):
        query = {"build_name": build_name}
        cursor = self.test_suites_collection().find(query)
        test_suite_author_map = {}
        for tc in cursor:
            test_suite_author_map[helpers.utf8(tc["product_suite"])] = helpers.utf8(tc["author"])
        return test_suite_author_map

    # DB query/update

    def find_and_add_aggregated_build(self, build_name,
                                      aggregated_build_name=None,
                                      quiet=True):
        """
        Check whether 'build_name' is found in aggregated_builds collection.
        - If found, return the document.
        - If not found, create a new aggregated build document indexed by
          current year and week. Then return the document.
        """
        week_num = helpers.week_num()
        year = helpers.year()
        if not aggregated_build_name:
            aggregated_build_name = ("bvs master aggregated %s wk%s"
                                     % (year, week_num))
            query = {"build_names": {"$all": [build_name]}}
        else:
            query = {"build_names": {"$all": [build_name]},
                     "name": aggregated_build_name}
        cursor = self.aggregated_builds_collection().find(query)
        count = cursor.count()
        if count >= 1:
            # Found aggregated build which contains the build_name.
            if not quiet: print "Found aggregated build with '%s'." % build_name
            if count > 1:
                print "WARNING: Did not expect multiple results."
            return cursor[0]

        query = {"name": aggregated_build_name}
        cursor = self.aggregated_builds_collection().find(query)
        ts = helpers.ts_long_local()

        if cursor.count() >= 1:
            # Aggregated build for year/week exists. Add build_name to list.
            if not quiet: print "Build '%s' not found. Found aggregated build '%s'." % (build_name, aggregated_build_name)
            doc = cursor[0]
            doc["build_names"].append(build_name)
            doc["updatetime"] = ts
            _ = self.upsert_doc('aggregated_builds', doc, query)
            return doc
        else:
            # Aggregated build for year/week does not exist. Create it.
            if not quiet: print "Not found aggregated build '%s'. Creating." % aggregated_build_name
            doc = {"name": aggregated_build_name,
                   "week_num": week_num,
                   "year": year,
                   "build_names": [build_name],
                   "createtime": ts,
                   "updatetime": ts,
                   }
            _ = self.insert_doc('aggregated_builds', doc)
            return doc

    def find_and_add_build_name(self, build_name, quiet=True):
        """
        Check whether 'build_name' is found in builds collection.
        - If found, return the document.
        - If not found, create a new build document, and return it.
        """
        query = {"build_name": build_name}
        cursor = self.builds_collection().find(query)
        count = cursor.count()
        if count >= 1:
            # Found build which contains the build_name.
            if not quiet: print "Found build with '%s'." % build_name
            if count > 1:
                print "WARNING: Did not expect multiple results."
            return cursor[0]
        else:
            # Build does not exist. Create it.
            if not quiet: print "Not found build '%s'. Creating." % build_name
            ts = helpers.ts_long_local()
            doc = {"build_name": build_name,
                   "createtime": ts,
                   "created_by": getpass.getuser()
                   }
            _ = self.insert_doc('builds', doc)
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
