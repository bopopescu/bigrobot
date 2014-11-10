from __future__ import print_function
import os
import sys
import re
from nose.exc import SkipTest


# Derive BigRobot path from the script's location, which should be
# in the bigrobot/test directory.
bigrobot_path = os.path.dirname(__file__) + '/..'
exscript_path = bigrobot_path + '/vendors/exscript/src'
sys.path.insert(0, exscript_path)
sys.path.insert(0, bigrobot_path)


import autobot.helpers as helpers
import autobot.setup_env as setup_env
from autobot.nose_support import run, log_to_console, wait_until_keyword_succeeds, Singleton
from keywords.BsnCommon import BsnCommon
from keywords.T5 import T5

helpers.remove_env('BIGROBOT_TOPOLOGY', quiet=True)
# Test suite is defined as the name of the test script minus its extension.
helpers.bigrobot_suite(os.path.basename(__file__).split('.')[0])
setup_env.standalone_environment_setup()


class TestTemplate:
    __metaclass__ = Singleton

    def __init__(self):
        pass

    def tc_setup(self):
        log_to_console("Inside test case setup (common)")

    def tc_teardown(self, tc_failed=False):
        log_to_console("Inside test case teardown (common)")
        if tc_failed:
            log_to_console("test case teardown: test case FAILED: running additional keywords...")

    #
    # Test case definitions
    #

    def test_01_verify_environment(self):
        """
        Test case: test_01_verify_environment
        """
        def func():
            assert helpers.bigrobot_path() != None
            assert helpers.bigrobot_log_path_exec_instance() != None
            assert helpers.bigrobot_suite() != None
            helpers.print_bigrobot_env(minimum=True)
        return run(func, setup=self.tc_setup, teardown=self.tc_teardown)

    def test_02_verify_cloud_fabric_version(self):
        """
        Test case: test_02_verify_cloud_fabric_version
        """
        def func():
            result = BsnCommon().cli('c1', 'show version')
            content = result['content']
            match = re.search(r'^Name\s+:\s+(.*)$', content, re.M)
            assert match, "Version string not found"
            version = match.group(1)
            helpers.log("version: %s" % version)
            match = re.match(r'.*Big Cloud Fabric.*', version)
            assert match, "Big Cloud Fabric not found"
        return run(func, setup=self.tc_setup, teardown=self.tc_teardown)

    def test_03_verify_tenant_creation(self):
        """
        Test case: test_03_verify_tenant_creation
        """
        def func():
            T5().rest_add_tenant('ABC')
            T5().rest_show_tenant('ABC')
        return run(func, setup=self.tc_setup, teardown=self.tc_teardown)

    def test_04_force_failure(self):
        """
        Test case: test_04_force_failure
        An example of a logic error.
        """
        def func():
            assert 1 == 0
        return run(func, setup=self.tc_setup, teardown=self.tc_teardown)

    def test_05_force_error(self):
        """
        Test case: test_05_force_error
        An example of a runtime error.
        """
        def func():
            assert 1 / 0
        return run(func, setup=self.tc_setup, teardown=self.tc_teardown)

    def test_06_skip_this(self):
        """
        Test case: test_06_skip_this
        Skip this test.
        """
        def func():
            raise SkipTest("not ready")
        run(test=func, setup=self.tc_setup, teardown=self.tc_teardown)

