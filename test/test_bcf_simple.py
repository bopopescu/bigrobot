from __future__ import print_function
import os
import sys
import random


# Derive BigRobot path from the script's location, which should be
# in the bigrobot/test directory.
bigrobot_path = os.path.dirname(__file__) + '/..'
exscript_path = bigrobot_path + '/vendors/exscript/src'
sys.path.insert(0, exscript_path)
sys.path.insert(0, bigrobot_path)


import autobot.helpers as helpers
import autobot.setup_env as setup_env
from autobot.nose_support import run, log_to_console, sleep, Singleton
from keywords.BsnCommon import BsnCommon
from keywords.T5Torture import T5Torture


helpers.set_env('BIGROBOT_TEST_POSTMORTEM', 'False', quiet=True)
helpers.set_env('BIGROBOT_TEST_SETUP', 'False', quiet=True)
helpers.set_env('BIGROBOT_TEST_CLEAN_CONFIG', 'False', quiet=True)
helpers.set_env('BIGROBOT_TEST_TEARDOWN', 'False', quiet=True)
helpers.remove_env('BIGROBOT_TOPOLOGY', quiet=True)
# Test suite is defined as the name of the test script minus its extension.
helpers.bigrobot_suite(os.path.basename(__file__).split('.')[0])
setup_env.standalone_environment_setup()

assert helpers.bigrobot_path() != None
assert helpers.bigrobot_log_path_exec_instance() != None
assert helpers.bigrobot_suite() != None
helpers.print_bigrobot_env(minimum=True)


class TestBcfEvents(object):
    __metaclass__ = Singleton

    def __init__(self):
        self.spine_list = None  # initialized later during setup
        self.leaf_list = None  # initialized later during setup

    #
    # Test case setup & teardown
    #

    def tc_setup(self):
        # BsnCommon().base_test_setup()
        pass


    def tc_teardown(self, tc_failed=False):
        # BsnCommon().base_test_teardown()
        # if tc_failed:
        #    # Test case failed. You can run additional keywords here,
        #    # e.g., test postmortem.
        #    pass
        pass

    #
    # Test case definitions
    #
    def test_00_suite_setup(self):
        """
        Test case: test_00_suite_setup
        Suite setup should be the first test in suite. Raise critical error
        if setup fails.
        """
        def func():
            BsnCommon().base_suite_setup()

            self.spine_list = T5Torture().rest_get_spine_switch_names()
            self.leaf_list = T5Torture().rest_get_leaf_switch_names()

            helpers.log("spine_list: %s" % self.spine_list)
            helpers.log("leaf_list: %s" % self.leaf_list)

        return run(func, setup=self.tc_setup, teardown=self.tc_teardown,
                   critical_failure=True)

    def test_01_get_switch_aliases(self):  # T23
        """
        Test case: test_01_get_switch_aliases
        """
        def func():
            # raise SkipTest("removed from regression")
            # switch_names = T5().rest_get_switch_names()
            # helpers.log("switch_names: %s" % switch_names)

            helpers.log("spine_list: %s" % self.spine_list)
            helpers.log("leaf_list: %s" % self.leaf_list)

        return run(func, setup=self.tc_setup, teardown=self.tc_teardown)

