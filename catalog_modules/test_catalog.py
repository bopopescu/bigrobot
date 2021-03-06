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

    def testbeds(self, product_name):
        """
        Returns a list of testbeds for a product.
        """
        if product_name in self.configs()['testbeds']:
            return self.configs()['testbeds'][product_name]
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

    def build_groups_collection(self):
        return self.db()['build_groups']

    def aggregated_builds_collection(self):
        return self.db()['aggregated_builds']

    def test_suite_author_mapping(self, build_name):
        query = {"build_name": build_name}
        cursor = self.test_suites_collection().find(query)
        test_suite_author_map = {}
        for tc in cursor:
            test_suite_author_map[helpers.utf8(tc["product_suite"])] = helpers.utf8(tc["author"])
        return test_suite_author_map


    # Helpers

    def timestamp(self):
        return helpers.ts_long_local()

    def match_build_name(self, build_name, field=None):
        """
        See the BUILD_NAME convention wiki guide at:
        https://bigswitch.atlassian.net/wiki/pages/viewpage.action?pageId=58327098
        "BUILD_NAME Convention (Regression System)"

        Sample BUILD_NAME:
            ihplus_bcf_40g-132_Special_security_patch
            ^      ^   ^   ^   ^
            |      |   |   |   |
            |      |   |   |   +-- build description (optional)
            |      |   |   +------ build id
            |      |   +---------- testbed name (e.g., 10g, 40g, common, virtual)
            |      +-------------- product name (including image tag)
            +--------------------- release name

        Returns:
           - None on no match
           - regex object on match.
                 match.group(1) == image release name
                 match.group(2) == product name
                 match.group(3) == testbed
                 match.group(4) == build id
                 match.group(5) == build description
           - string matching the field
        """

        # !!! FIXME: The regex match is not very stringent at this point.
        #            Will need to tighten down on requirements in the future.
        match = re.match(r'^([A-Za-z0-9-]+)_([A-Za-z0-9-]+)_([A-Za-z0-9-]+)-(\d+)(.*)', build_name)
        result = None
        if match:
            if field == 'release':
                result = match.group(1)
            elif field == 'product':
                result = match.group(2)
            elif field == 'testbed':
                result = match.group(3)
            elif field == 'build_id':
                result = match.group(4)
            elif field == 'build_descr':
                result = match.group(5).lstrip('-_')
            else:
                result = match
        return result

    def in_build_name_group(self, build_name):
        """
        Check if build_name belongs in a group. E.g.,
        Build name 'ironhorse_bcf_10G-4083' and 'ironhorse_bcf_virtual-4083'
        are in the same group - 'ironhorse_bcf_*-4083'.

        If checks to make sure that the testbed exists for the product
        (as defined in configs/catalog.yaml).

        Returns:
          - True if in group
          - False if not in group or does not match the build_name format
        """
        match = self.match_build_name(build_name)
        if not match:
            return False
        product = match.group(2)
        testbed = match.group(3)
        testbeds = self.testbeds(product)
        return helpers.in_list(testbeds, testbed)

    def get_build_name_group(self, build_name):
        """
        Returns the build_name group, e.g., 'ironhorse_bcf_*-4083' or None
        if not in group.
        """
        if not self.in_build_name_group(build_name):
            return None
        testbed = self.match_build_name(build_name, 'testbed')
        return build_name.replace("_%s-" % testbed, "_*-")

    def get_product_for_build_name(self, build_name):
        """
        Returns the product which matches a build name or None for no match.
        E.g.,
        - build_name='ihplus_bcf-104' matches 'bcf' product.
        - build_name='corsair_bigtap-99' matches 'bigtap' product.
        """
        for product in self.products():
            match = self.match_build_name(build_name)
            if match:
                if re.search(product, match.group(2), re.I):
                    return product
        return None

    def get_base_release_for_build_name(self, build_name, product):
        """
        'product' is the product name as defined in configs/catalog.yaml
        (e.g., 'bcf', 'bigtap', etc).

        Returns the release name in the build_name string.
        """
        match = self.match_build_name(build_name)
        base_release = None
        if match:
            image_release = match.group(1)
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


    # DB query/update

    def aggregated_build(self, build_name):
        """
        Returns a list of actual builds in an aggregated build. Data is
        retrieved from the aggregated_build collection.
        """
        query = {"build_name": build_name}
        cursor = self.aggregated_builds_collection().find(query)
        count = cursor.count()

        if count >= 1:
            return cursor[0]['build_names']
        else:
            return []

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
                     "build_name": aggregated_build_name}
        cursor = self.aggregated_builds_collection().find(query)
        count = cursor.count()
        if count >= 1:
            # Found aggregated build which contains the build_name.
            if not quiet: print "Found aggregated build with '%s'." % build_name
            if count > 1:
                print "WARNING: Did not expect multiple results."
            return cursor[0]

        query = {"build_name": aggregated_build_name}
        cursor = self.aggregated_builds_collection().find(query)

        if cursor.count() >= 1:
            # Aggregated build for year/week exists. Add build_name to list.
            if not quiet: print "Build '%s' not found. Found aggregated build '%s'." % (build_name, aggregated_build_name)
            doc = cursor[0]
            doc["build_names"].append(build_name)
            doc["updatetime"] = self.timestamp()
            _ = self.upsert_doc('aggregated_builds', doc, query)
            return doc
        else:
            # Aggregated build for year/week does not exist. Create it.
            if not quiet: print "Not found aggregated build '%s'. Creating." % aggregated_build_name
            doc = {"build_name": aggregated_build_name,
                   "build_id": "wk" + week_num + ", " + year,
                   "release": self.match_build_name(build_name, "release"),
                   "week_num": week_num,
                   "year": year,
                   "build_names": [build_name],
                   "createtime": self.timestamp(),
                   "updatetime": self.timestamp(),
                   "created_by": getpass.getuser(),
                   "comments": '',
                   }
            _ = self.insert_doc('aggregated_builds', doc)
            return doc

    def find_and_add_build_name(self, build_name, regression_tags=None,
                                quiet=True):
        """
        Check whether 'build_name' is found in builds collection.
        - If found, return the document.
        - If not found, create a new build document, and return it.
        """
        if self.in_build_name_group(build_name):
            testbed = self.match_build_name(build_name, "testbed")
        else:
            testbed = None

        # Default regression_tags is "virtual" for virtual testbeds, and
        # "daily" for all other testbeds.
        if regression_tags == None:
            if testbed == "virtual":
                regression_tags = "virtual"
            else:
                regression_tags = "daily"

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
            # Create: Build does not exist.
            if not quiet: print "Not found build '%s'. Creating." % build_name

            if testbed:
                testbeds = [testbed]
            else:
                testbeds = []

            doc = {"build_name": build_name,
                   "build_id": self.match_build_name(build_name, "build_id"),
                   "release": self.match_build_name(build_name, "release"),
                   "createtime": self.timestamp(),
                   "updatetime": self.timestamp(),
                   "created_by": getpass.getuser(),
                   "testbeds": testbeds,
                   "regression_tags": [regression_tags],
                   "is_toxic": False,
                   "comments": '',
                   }
            _ = self.insert_doc('builds', doc)
            return doc

    def find_and_add_build_name_group(self,
                                      build_name,
                                      createtime=None,
                                      updatetime=None,
                                      quiet=True):
        """
        Check whether 'build_name' is found in build_groups collection.
        - If found, update testbeds, build_names, and regression_tags, then
          return the document.
        - If not found, create a new build document, and return it.

        If build_name does not match the group format, add it to the
        build_groups collection anyway as a standalone document.
        """
        if self.in_build_name_group(build_name):
            testbed = self.match_build_name(build_name, "testbed")
            build_group_name = self.get_build_name_group(build_name)
        else:
            testbed = None
            build_group_name = build_name

        query = {"build_name": build_group_name}
        cursor = self.build_groups_collection().find(query)
        count = cursor.count()
        regression_tags = self.get_regression_tags(build_name)
        if createtime == None:
            createtime = self.timestamp()
        if updatetime == None:
            updatetime = self.timestamp()

        if count >= 1:
            # Update: Found build group.
            if not quiet: print "Found build with '%s'." % build_group_name
            if count > 1:
                print "WARNING: Did not expect multiple results. Will only look at first result."
            found_doc = cursor[0]

            # Update testbeds field
            if testbed and not helpers.in_list(found_doc["testbeds"], testbed):
                found_doc["testbeds"].append(testbed)

            # Update build_names field
            if not helpers.in_list(found_doc["build_names"], build_name):
                found_doc["build_names"].append(build_name)

            # Update updatetime field
            found_doc["updatetime"] = updatetime

            # Update regression_tags field
            if "regression_tags" in found_doc:
                found_doc["regression_tags"] = regression_tags
                for n in found_doc["build_names"]:
                    tags = self.get_regression_tags(n)
                    found_doc["regression_tags"] = helpers.set_union(
                                        found_doc["regression_tags"],
                                        tags)
            else:
                found_doc["regression_tags"] = regression_tags

            # Update document
            doc = self.upsert_doc("build_groups", found_doc, query)
            return doc
        else:
            # Create: Build group does not exist.
            if not quiet: print "Not found build '%s'. Creating." % build_group_name

            if testbed:
                testbeds = [testbed]
            else:
                testbeds = []

            doc = {"build_name": build_group_name,
                   "build_id": self.match_build_name(build_name, "build_id"),
                   "release": self.match_build_name(build_name, "release"),
                   "createtime": createtime,
                   "updatetime": updatetime,
                   "created_by": getpass.getuser(),
                   "testbeds": testbeds,
                   "build_names": [build_name],
                   "regression_tags": regression_tags,
                   "comments": '',
                   }
            _ = self.insert_doc('build_groups', doc)
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

    def get_regression_tags(self, build_name):
        query = {"build_name": build_name}
        cursor = self.find_docs(collection="builds", query=query)
        if cursor.count() > 0:
            return cursor[0]['regression_tags']
        else:
            return []

    def update_regression_tags(self, build_name, tags):
        """
        Update the regression_tags field in builds collection. Then update
        the build_groups collection. Also change the update timestamp.

        Note: tags argument must be a list type.
        """
        query = {"build_name": build_name}
        cursor = self.find_docs(collection="builds", query=query)
        if cursor.count() > 0:
            found_doc = cursor[0]
            found_doc['regression_tags'] = tags
            found_doc['updatetime'] = self.timestamp()
            updated_doc = self.upsert_doc("builds", found_doc, query)
            self.find_and_add_build_name_group(build_name)
            return updated_doc
        else:
            return None

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
