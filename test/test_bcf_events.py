from __future__ import print_function
import os
import sys
import random
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


class TestBcfEvents:
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

        self.SPINE_LIST = None  # initialized later during setup
        self.LEAF_LIST = None  # initialized later during setup

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
        T5Torture().cli_cluster_take_leader()
        sleep(during)
        self.cli_show_commands_for_debug()

    def verify_all_switches_connected_back(self):
        switches = T5Torture().rest_get_disconnect_switch('master')
        self.cli_show_commands_for_debug()
        helpers.log("the disconnected switches are %s" % switches)
        assert switches == []  # Should be empty

    def switch_node_down_up_event(self, node):
        helpers.log("reload switch")
        log_to_console("================ Rebooting %s ===============" % node)
        self.cli_show_commands_for_debug()
        T5Torture().cli_reboot_switch('master', node)
        self.cli_show_commands_for_debug()
        sleep(self.LONG)
        wait_until_keyword_succeeds(60 * 10, 30,
                                    self.verify_all_switches_connected_back)

    def disable_links_between_nodes(self, node, intf):
        self.cli_show_commands_for_debug()
        T5Torture().rest_disable_fabric_interface(node, intf)

    def enable_links_between_nodes(self, node, intf):
        self.cli_show_commands_for_debug()
        T5Torture().rest_enable_fabric_interface(node, intf)

    def data_link_down_up_event_between_nodes(self, node1, node2):
        log_to_console("================ data link down/up for %s and %s ===============" % (node1, node2))
        helpers.log("disable/enable link from nodes")
        _list = T5Torture().cli_get_links_nodes_list(node1, node2)
        for intf in _list:
            self.disable_links_between_nodes(node1, intf)
            sleep(60)
            self.enable_links_between_nodes(node1, intf)
            sleep(60)

    def clear_stats_in_controller_switch(self):
        BsnCommon().enable("master", "clear switch all interface all counters")
        self.cli_show_commands_for_debug()

    def tenant_configuration_add_remove(self, tnumber, vnumber, sleep_timer=1):
        log_to_console("================tenant configuration changes: %s===============" % tnumber)
        self.clear_stats_in_controller_switch()
        BsnCommon().enable("master", "copy running-config config://config_tenant_old")
        BsnCommon().cli("master", "")  # press the return key in CLI (empty command)

        helpers.log("Big scale configuration tenant add")
        T5Torture().rest_add_tenant_vns_scale(
                    tenantcount=tnumber, tname="FLAP", vnscount=vnumber,
                    vns_ip="yes", base="1.1.1.1", step="0.0.1.0")
        BsnCommon().cli("master", "show running-config tenant FLAP0")
        vlan = 1000
        for i in range(0, tnumber):
            T5Torture().rest_add_interface_to_all_vns(
                    tenant="FLAP%s" % i, switch=self.LEAF1A, intf="ethernet3",
                    vlan=vlan)
            BsnCommon().cli("master", "show running-config tenant FLAP%s" % i)
            vlan = vlan + vnumber
            sleep(sleep_timer)
        BsnCommon().cli("master", "show running-config tenant", timeout=120)
        BsnCommon().enable("master", "copy running-config config://config_tenant_new")

        helpers.log("big scale configuration tenant delete")
        for i in range(0, tnumber):
            BsnCommon().config("master", "no tenant FLAP%s" % i)
        BsnCommon().cli("master", "show running-config tenant", timeout=120)

    def vns_configuration_add_remove(self, vnumber, sleep_timer=1):
        log_to_console("================vns configuration changes: %s===============" % vnumber)
        BsnCommon().enable("master", "copy running-config config://config_vns_old")

        vlan = 1000
        T5Torture().rest_add_tenant_vns_scale(
                tenantcount=1, tname="FLAP", vnscount=vnumber,
                vns_ip="yes", base="1.1.1.1", step="0.0.1.0")
        T5Torture().rest_add_interface_to_all_vns(
                tenant="FLAP0", switch=self.LEAF1A, intf="ethernet3",
                vlan=vlan)
        sleep(sleep_timer)
        BsnCommon().cli("master", "show running-config tenant", timeout=120)
        BsnCommon().enable("master", "copy running-config config://config_vns_new")

        helpers.log("Big scale configuration tenant delete")
        BsnCommon().config("master", "tenant FLAP0")

        vns = 1 + vnumber
        for i in range(1, vns):
            BsnCommon().config("master", "no segment V%s" % i)
        BsnCommon().config("master", "logical-router")
        for i in range(1, vns):
            BsnCommon().config("master", "no interface segment V%s" % i)
        BsnCommon().config("master", "no tenant FLAP0")
        BsnCommon().cli("master", "show running-config tenant", timeout=120)


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

            self.SPINE_LIST = T5Torture().rest_get_spine_switch_names()
            self.LEAF_LIST = T5Torture().rest_get_leaf_switch_names()

            # Note: You can run tests on a subset of switches also (see below).
            # self.SPINE_LIST = [self.SPINE1, self.SPINE2]
            # self.LEAF_LIST = [self.LEAF1A, self.LEAF1B, self.LEAF2A, self.LEAF2B]

        return run(func, setup=self.tc_setup, teardown=self.tc_teardown,
                   critical_failure=True)

    def test_01_controller_node_event_failover(self):  # T23
        """
        Test case: test_01_controller_node_event_failover
        """
        def func():
            # raise SkipTest("removed from regression")

            for i in range(0, self.LOOP):
                log_to_console("\n******* controller node failover: %s *******" % i)
                self.controller_node_event_ha_failover(self.INEVENT)
                sleep(self.INEVENT)
        return run(func, setup=self.tc_setup, teardown=self.tc_teardown)

    def test_02_spine_switch_node_down_up_event(self):  # T21
        """
        Test case: test_02_spine_switch_node_down_up_event
        """
        def func():
            # raise SkipTest("removed from regression")

            for i in range(0, self.LOOP):
                log_to_console("\n******* spine switch node down/up event: %s ********" % i)
                for spine in [self.SPINE_LIST]:
                    self.switch_node_down_up_event(spine)
                    sleep(self.INEVENT)
        return run(func, setup=self.tc_setup, teardown=self.tc_teardown)

    def test_03_leaf_switch_node_down_up_event(self):  # T22
        """
        Test case: test_02_leave_switch_node_down_up_event
        """
        def func():
            raise SkipTest("removed from regression")

            for i in range(0, self.LOOP):
                log_to_console("\n******* leaf switch node down/up event: %s ********" % i)
                for leaf in self.LEAF_LIST:
                    self.switch_node_down_up_event(leaf)
                    sleep(self.INEVENT)
        return run(func, setup=self.tc_setup, teardown=self.tc_teardown)

    def test_04_data_link_down_up_event_between_leaf_and_spine(self):  # T27
        """
        Test case: test_04_data_link_down_up_event_between_leaf_and_spine
        """
        def func():
            # raise SkipTest("removed from regression")

            for i in range(0, self.LOOP):
                log_to_console("\n******* data link down/up event between leaf and spine: %s ********" % i)

                T5Torture().cli_event_link_flap(self.SPINE_LIST, self.LEAF_LIST, interval=self.LINKFLAP)
                T5Torture().cli_event_link_flap(self.LEAF_LIST, self.SPINE_LIST, interval=self.LINKFLAP)

                sleep(self.INEVENT)
        return run(func, setup=self.tc_setup, teardown=self.tc_teardown)

    def test_05_data_link_down_up_event_between_leafs(self):  # T28
        """
        Test case: test_05_data_link_down_up_event_between_leafs
        """
        def func():
            # raise SkipTest("removed from regression")

            for i in range(0, self.LOOP):
                log_to_console("\n******* date link down/up %s*******" % i)

                T5Torture().cli_event_link_flap(self.LEAF_LIST, self.LEAF_LIST, interval=self.LINKFLAP)

                sleep(self.INEVENT)
        return run(func, setup=self.tc_setup, teardown=self.tc_teardown)

    def test_06_big_configuration_changes_around_500_tenants(self):  # T26
        """
        Test case: test_06_big_configuration_changes_around_500_tenants
        """
        def func():
            # raise SkipTest("removed from regression")

            for i in range(0, self.LOOP):
                log_to_console("\n******* big configuration changes tenant %s*******" % i)
                self.tenant_configuration_add_remove(self.TFLAPNUM, 3)
                sleep(self.BIGCONFIGSLEEP)
        return run(func, setup=self.tc_setup, teardown=self.tc_teardown)

    def test_07_big_configuration_changes_around_500_vns(self):  # T25
        """
        Test case: test_07_big_configuration_changes_around_500_vns
        """
        def func():
            # raise SkipTest("removed from regression")

            for i in range(0, self.LOOP):
                log_to_console("\n******* big configuration changes vns %s*******" % i)
                self.vns_configuration_add_remove(self.VFLAPNUM)
                sleep(self.BIGCONFIGSLEEP)
        return run(func, setup=self.tc_setup, teardown=self.tc_teardown)

    def test_08_continues_event(self):  # T51
        """
        Test case: test_08_continues_event
        """
        def func():
            # raise SkipTest("removed from regression")

            helpers.log("randomize execution of all the event test cases")  # from T23 to T30
            for i in range(0, self.REPEAT):
                log_to_console("\n========******* in continues event loop: %s out of %s ******======" % (i, self.REPEAT))
                tc_index = random.randint(1, 6)
                log_to_console("--------random number is %s --------" % tc_index)
                if tc_index == 1:
                    self.test_02_spine_switch_node_down_up_event()
                # elif tc_index = 2:
                #    test_03_leaf_switch_node_down_up_event()
                elif tc_index == 2:
                    self.test_04_data_link_down_up_event_between_leaf_and_spine()
                elif tc_index == 3:
                    self.test_05_data_link_down_up_event_between_leafs()
                elif tc_index == 4:
                    self.test_06_big_configuration_changes_around_500_tenants()
                elif tc_index == 5:
                    self.test_07_big_configuration_changes_around_500_vns()
                elif tc_index == 6:
                    self.test_01_controller_node_event_failover()
                sleep(self.BETWEENEVENT)
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

