from __future__ import print_function
import os
import sys
from nose.exc import SkipTest


# Derive BigRobot path from the script's location, which should be
# in the bigrobot/test directory.
bigrobot_path = os.path.dirname(__file__) + '/..'
exscript_path = bigrobot_path + '/vendors/exscript/src'
sys.path.insert(0, exscript_path)
sys.path.insert(0, bigrobot_path)


import autobot.helpers as helpers
import autobot.setup_env as setup_env
from autobot.nose_support import run, log_to_console, wait_until_keyword_succeeds, sleep
from keywords.BsnCommon import BsnCommon
from keywords.Controller import Controller
from keywords.Mininet import Mininet
from keywords.Host import Host
from keywords.Ixia import Ixia
from keywords.T5 import T5
from keywords.T5L3 import T5L3
from keywords.T5Platform import T5Platform
from keywords.T5Utilities import T5Utilities
from keywords.T5ZTN import T5ZTN
from keywords.SwitchLight import SwitchLight


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


class TestT5Longevity:
    def __init__(self):

        #
        # Constants - test controls
        #
        self.SHORT = 1
        self.MEDIUM = 3
        self.LONG = 30
        self.VERY_LONG = 120

        self.LINKFLAP = 120
        self.INEVENT = 300
        self.BETWEENEVENT = 600

        self.TFLAPNUM = 100
        self.VFLAPNUM = 100
        self.BIGCONFIGSLEEP = 300

        self.LOOP = 1  # 5
        self.REPEAT = 60

        self.LEAF1A = "dt-leaf1a"
        self.LEAF1B = "dt-leaf1b"
        self.LEAF2A = "dt-leaf2a"
        self.LEAF2B = "dt-leaf2b"

        self.SPINE1 = "dt-spine1"
        self.SPINE2 = "dt-spine2"

    #
    # Test case setup & teardown
    #

    def tc_setup(self):
        BsnCommon().base_test_setup()


    def tc_teardown(self, tc_failed=False):
        BsnCommon().base_test_teardown()
        if tc_failed:
            # Test case failed. You can run additional keywords here,
            # e.g., test postmortem.
            pass

    #
    # Supporting keywords
    #

    def cli_show_commands_for_debug(self):
        BsnCommon().cli('master', 'show ver', timeout=60)
        BsnCommon().enable('master', 'show running-config switch', timeout=60)
        BsnCommon().enable('master', 'show switch', timeout=60)
        BsnCommon().enable('master', 'show link', timeout=60)
        BsnCommon().cli('master', 'show ver', timeout=60)
        BsnCommon().cli('slave', 'show ver', timeout=60)


    def controller_node_event_ha_failover(self, during=30):
        log_to_console("=============HA failover ===============")
        self.cli_show_commands_for_debug()
        T5Platform().cli_cluster_take_leader()
        sleep(during)
        self.cli_show_commands_for_debug()


    def verify_all_switches_connected_back(self):
        switches = T5Platform().rest_get_disconnect_switch('master')
        self.cli_show_commands_for_debug()
        helpers.log("the disconnected switches are %s" % switches)
        assert switches == []  # Should be empty


    def switch_node_down_up_event(self, node):
        helpers.log("reload switch")
        log_to_console("================ Rebooting ${node} ===============")
        self.cli_show_commands_for_debug()
        T5ZTN().cli_reboot_switch('master', node)
        self.cli_show_commands_for_debug()
        sleep(self.LONG)
        wait_until_keyword_succeeds(60 * 10, 30,
                                    self.verify_all_switches_connected_back())

    #
    # Test case definitions
    #

    # Attention: This is special.
    def test_00_suite_setup(self):
        """
        Test case: test_00_suite_setup
        Suite setup should be the first test in suite. Raise critical error
        if setup fails.
        """

        def func():
            BsnCommon().base_suite_setup()
            for i in range(0, 500):
                BsnCommon().config('master', 'no tenant FLAP%s' % i)
        return run(func, setup=self.tc_setup, teardown=self.tc_teardown,
                   critical_failure=True)


    def test_01_controller_node_event_failover(self):
        """
        Test case: test_01_controller_node_event_failover
        """
        def func():
            for i in range(0, self.LOOP):
                log_to_console("\n******* controller node failover: %s *******" % i)
                self.controller_node_event_ha_failover(self.INEVENT)
                sleep(self.INEVENT)
        return run(func, setup=self.tc_setup, teardown=self.tc_teardown)


    def test_02_spine_switch_node_down_up_event(self):
        """
        Test case: test_02_spine_switch_node_down_up_event
        """
        def func():
            for i in range(0, self.LOOP):
                log_to_console("\n******* spine switch node down/up event: %s ********" % i)
                self.switch_node_down_up_event(self.SPINE1)
                sleep(self.INEVENT)
                self.switch_node_down_up_event(self.SPINE2)
                sleep(self.INEVENT)
        return run(func, setup=self.tc_setup, teardown=self.tc_teardown)


    def test_03_t5_longevity_show_running_config(self):
        """
        Test case: test_03_t5_longevity_show_running_config
        """
        def func():
            raise SkipTest("not ready")
        return run(func, setup=self.tc_setup, teardown=self.tc_teardown)

    # Attention: This is special.
    def test_99_suite_teardown(self):
        """
        Test case: test_00_suite_teardown
        Suite teardown should be the last test in suite.
        """
        def func():
            BsnCommon().base_suite_teardown()
        return run(func, setup=self.tc_setup, teardown=self.tc_teardown)

