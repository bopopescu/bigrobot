import autobot.helpers as helpers
import autobot.restclient as restclient


class TestRail(object):
    '''
    Interface to the TestRail API
    '''

    def __init__(self):
        self.configs = self.load_configs()
        u = self.configs['user']
        p = self.configs['password']
        self.url = self.configs['url']
        self.rest = restclient.RestClient(u, p)

    def load_configs(self):
        try:
            config_file = helpers.bigrobot_config_path + "/testrail.yaml"
            config = helpers.load_config(config_file)
        except IOError:
            s = "Unable to open TestRail config file %s" % config_file
            helpers.error_exit(s)
        return config

    #
    # The following methods perform CRUD operations on the TestRail API
    #

    def get_projects(self):
        return self.rest.get(self.url + "/get_projects")

    def get_project(self, project_id):
        return self.rest.get(self.url + "/get_project/%s" % project_id)

    def get_testsuites(self, project_id):
        return self.rest.get(self.url + "/get_suites/%s" % project_id)

    def get_testsuite(self, testsuite_id):
        return self.rest.get(self.url + "/get_suite/%s" % testsuite_id)

    def get_testsections(self, project_id, testsuite_id):
        return self.rest.get(
            self.url +
            "/get_sections/%s&suite_id=%s" %
            (project_id, testsuite_id))

    def get_testsection(self, testsection_id):
        return self.rest.get(self.url + "/get_section/%s" % testsection_id)

    def get_testcases(self, project_id, testsuite_id, testsection_id=None):
        if testsection_id:
            return self.rest.get(
                self.url +
                "/get_cases/%s&suite_id=%s&section_id=%s" %
                (project_id, testsuite_id, testsection_id))
        else:
            return self.rest.get(
                self.url +
                "/get_cases/%s&suite_id=%s" %
                (project_id, testsuite_id))

    def get_testcase(self, testcase_id):
        return self.rest.get(self.url + "/get_case/%s" % testcase_id)
