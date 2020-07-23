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


class TestBcfEvents:
    __metaclass__ = Singleton

    def __init__(self):
        self.link_flap_sleep = BsnCommon().params_global('link_flap_sleep')
        self.in_event_sleep = BsnCommon().params_global('in_event_sleep')
        self.between_event_sleep = BsnCommon().params_global('between_event_sleep')
        self.tflapnum = BsnCommon().params_global('tflapnum')
        self.vflapnum = BsnCommon().params_global('vflapnum')
        self.big_config_sleep = BsnCommon().params_global('big_config_sleep')
        self.loop = BsnCommon().params_global('loop')
        self.repeat = BsnCommon().params_global('repeat')

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

            spines = BsnCommon().params_global('spine_list')
            leafs = BsnCommon().params_global('leaf_list')

            if not spines:
                spines = T5Torture().rest_get_spine_switch_names()
                BsnCommon().params_global('spine_list', spines)
            if not leafs:
                leafs = T5Torture().rest_get_leaf_switch_names()
                BsnCommon().params_global('leaf_list', leafs)

            helpers.log("spine list: %s" % BsnCommon().params_global('spine_list'))
            helpers.log("leaf list: %s" % BsnCommon().params_global('leaf_list'))

        return run(func, critical_failure=True)

    def test_01_controller_node_event_failover(self):  # T23
        """
        Test case:      test_01_controller_node_event_failover
        Description:    Failover for controller node is performed by issuing 'system failover' in standby controller.
                        The event is repeated self.LOOP times. The event runs at the gap of self.INEVENT seconds
        Output:         Previous active controller becomes standby controller, standby controller becomes active controller.
        Requirement:    2 controller nodes
        Pass criteria:  Controller nodes switch roles.
        """
        def func():
            for i in range(0, self.loop):
                log_to_console("\n******* controller node failover: %s *******" % i)
                T5Torture().controller_node_event_ha_failover()
                sleep(self.in_event_sleep)
        return run(func, setup=self.tc_setup, teardown=self.tc_teardown)

    def test_02_controller_node_event_main_reload(self):  # new test case
        """
        Test case:      test_02_controller_node_event_main_reload
        Description:    Failover for controllers nodes is performed by issuing 'system reload controller' in active controller.
                        The event is repeated self.LOOP times. The event runs at the gap of self.INEVENT seconds
        Output:         Active controller vm get rebooted, previous active controller becomes standby controller, standby
                        controller becomes active controller.
        Requirement:    2 controller nodes
        Pass criteria:  Controller nodes switch roles.

        """
        def func():
            # raise SkipTest("removed from regression")

            for i in range(0, self.loop):
                log_to_console("\n******* controller node failover: %s *******" % i)
                T5Torture().controller_node_event_reload_active()
                sleep(self.in_event_sleep)
        return run(func, setup=self.tc_setup, teardown=self.tc_teardown)

    def test_03_spine_switch_node_down_up_event(self):  # T21
        """
        Test case:      test_03_spine_switch_node_down_up_event
        Description:    Spine nodes is rebooted by issuing 'system reboot switch SWITCH' in active controller.
                        The event is repeated self.LOOP times. The event runs at the gap of self.INEVENT seconds
        Input:          self.SPINE_LIST- spines in the list is rebooted one by one.  SPINE_LIST can be modified by .....
        Output:         spine switches reboot.
        Requirement:    2 or more spines to guarantee at any time at least 1 spine is function
        Pass criteria:  Spine joins the fabric after it comes back
        """
        def func():
            T5Torture().randomize_spines()
            for i in range(0, self.loop):
                log_to_console("\n******* spine switch node down/up event: %s ********" % i)
                for spine in BsnCommon().params_global('spine_list'):
                    T5Torture().switch_node_down_up_event(spine)
                    sleep(self.in_event_sleep)
        return run(func, setup=self.tc_setup, teardown=self.tc_teardown)

    def test_04_leaf_switch_node_down_up_event(self):  # T22
        """
        Test case:      test_04_leaf_switch_node_down_up_event
        Description:    Leaf switch is rebooted by issuing 'system reboot switch SWITCH' in active controller.
                        The event is repeated self.LOOP times. The event runs at the gap of self.INEVENT seconds
        Input:          self.LEAF_LIST- leafs in the list is rebooted one by one.  LEAF_LIST can be modified by .....
        Output:         leaf switch reboots.
        Requirement:    2 leafs in a rack
                        Host is connected to leaf switches through port group
        Pass criteria:  Leaf joins the fabric after it comes back
        """
        def func():
            for i in range(0, self.loop):
                log_to_console("\n******* leaf switch node down/up event: %s ********" % i)
                T5Torture().randomize_leafs()
                for leaf in BsnCommon().params_global('leaf_list'):
                    T5Torture().switch_node_down_up_event(leaf)
                    sleep(self.in_event_sleep)
        return run(func, setup=self.tc_setup, teardown=self.tc_teardown)

    def test_05_data_link_down_up_event_between_leaf_and_spine(self):  # T27
        """
        Test case:      test_05_data_link_down_up_event_between_leaf_and_spine
        Description:    Link between spine switch and leaf switch is flapped by calling API to controller
                        to disable and enable the interface. The flap is executed at both spine side and leaf side.
                        The event is repeated self.LOOP times. The event runs at the gap of self.INEVENT seconds
                        self.SPINE_LIST- spines in the list is rebooted one by one.  SPINE_LIST can be modified by .....
                        self.LEAF_LIST- spines in the list is rebooted one by one.  LEAF_LIST can be modified by .....
        Output:         Links are flapped.
        Requirement:    More than 1 spines or 2 leafs in a rack or 2 links between spine and leaf
        Pass criteria:  Link is removed from fabric when it is disabled, and link appears in fabric when it is enabled.         """
        def func():
            for i in range(0, self.loop):
                log_to_console("\n******* data link down/up event between leaf and spine: %s ********" % i)

                T5Torture().randomize_spines_and_leafs()
                T5Torture().cli_event_link_flap(
                        BsnCommon().params_global('spine_list'),
                        BsnCommon().params_global('leaf_list'),
                        interval=self.link_flap_sleep)
                T5Torture().randomize_spines_and_leafs()
                T5Torture().cli_event_link_flap(
                        BsnCommon().params_global('leaf_list'),
                        BsnCommon().params_global('spine_list'),
                        interval=self.link_flap_sleep)

                sleep(self.in_event_sleep)
        return run(func, setup=self.tc_setup, teardown=self.tc_teardown)

    def test_06_data_link_down_up_event_between_leafs(self):  # T28
        """
        Test case:      test_06_data_link_down_up_event_between_leafs
        Description:    Link between leaf pair switches is flapped by calling API to controller
                        to disable and enable the interface. The flap is executed at both sides for each connection.
                        The event is repeated self.LOOP times. The event runs at the gap of self.INEVENT seconds
        Input:          self.LEAF_LIST- spines in the list is rebooted one by one.  LEAF_LIST can be modified by .....
        Output:         leaf switch reboots.
        Requirement:    More than 1 spines or 2 leafs in a rack or 2 links between spine and leaf
        Pass criteria:  Link is removed from fabric when it is disabled, and link appears in fabric when it is enabled.
        """
        def func():
            for i in range(0, self.loop):
                log_to_console("\n******* date link down/up %s*******" % i)

                T5Torture().randomize_leafs()
                T5Torture().cli_event_link_flap(
                        BsnCommon().params_global('leaf_list'),
                        BsnCommon().params_global('leaf_list'),
                        interval=self.link_flap_sleep)

                sleep(self.in_event_sleep)
        return run(func, setup=self.tc_setup, teardown=self.tc_teardown)

    def test_07_big_configuration_changes_tenants(self):  # T26
        """
        Test case:      test_07_big_configuration_changes_tenants
        Description:    Tenants are created and deleted by calling API to controller
                        The event is repeated self.LOOP times. The event runs at the gap of self.INEVENT seconds
        Input:          self.TFLAPNUM - the number of tenants to be created and deleted.  self.TFLAPNUM can be modified by .....
        Output:         None
        Requirement:    More than 1 spines or 2 leafs in a rack or 2 links between spine and leaf
        Pass criteria:  Tenants are created and deleted successfully.
        """
        def func():
            for i in range(0, self.loop):
                log_to_console("\n******* big configuration changes tenant %s*******" % i)
                T5Torture().tenant_configuration_add_remove(
                        self.tflapnum, 3,
                        sw_dut=BsnCommon().params_global('switch_dut'),
                        sw_intf_dut=BsnCommon().params_global('switch_interface_dut'))
                sleep(self.big_config_sleep)
        return run(func, setup=self.tc_setup, teardown=self.tc_teardown)

    def test_08_big_configuration_changes_vns(self):  # T25
        """
        Test case:      test_08_big_configuration_changes_vns
        Description:    Segments are created and deleted by calling API to controller
                        The event is repeated self.LOOP times. The event runs at the gap of self.INEVENT seconds
        Input:          self.VFLAPNUM -  the number of segments to be created and deleted.  self.TFLAPNUM can be modified by .....
        Output:         None
        Requirement:    More than 1 spines or 2 leafs in a rack or 2 links between spine and leaf
        Pass criteria:  Segments are created and deleted successfully.
        """
        def func():
            for i in range(0, self.loop):
                log_to_console("\n******* big configuration changes vns %s*******" % i)
                T5Torture().vns_configuration_add_remove(
                        self.vflapnum,
                        sw_dut=BsnCommon().params_global('switch_dut'),
                        sw_intf_dut=BsnCommon().params_global('switch_interface_dut'))
                sleep(self.big_config_sleep)
        return run(func, setup=self.tc_setup, teardown=self.tc_teardown)

    def test_09_continues_event(self):  # T51
        """
        Test case:      test_09_continues_event
        Description:    This test executes a combination of all the test cases.
                        A random number is generated and based on the random number, a testcase event is executed.
                        Total of self.REPEAT random numbers are generated. The event runs at the gap of self.BETWEENEVENT seconds
        Input:          self.REPEAT -  the times random number to be generated.  self.TFLAPNUM can be modified by .....
                        self.BETWEENEVENT - idle timer between events - this can be modified by .....
        Output:         None
        Requirement:    More than 1 spines or 2 leafs in a rack or 2 links between spine and leaf
        Pass criteria:  Multiple success behaviors (depending on which test cases are executed).
        """
        def func():
            helpers.log("randomize execution of all the event test cases")  # from T23 to T30
            for i in range(0, self.repeat):
                log_to_console("\n========******* in continues event loop: %s out of %s ******======" % (i, self.repeat))
                tc_index = random.randint(1, 6)
                log_to_console("--------random number is %s --------" % tc_index)
                if tc_index == 1:
                    self.test_02_controller_node_event_main_reload()
                elif tc_index == 2:
                    self.test_03_spine_switch_node_down_up_event()
                # elif tc_index = 3:
                #    test_04_leaf_switch_node_down_up_event()
                elif tc_index == 3:
                    self.test_05_data_link_down_up_event_between_leaf_and_spine()
                elif tc_index == 4:
                    self.test_06_data_link_down_up_event_between_leafs()
                elif tc_index == 5:
                    self.test_07_big_configuration_changes_tenants()
                elif tc_index == 6:
                    self.test_08_big_configuration_changes_vns()
                elif tc_index == 7:
                    self.test_01_controller_node_event_failover()
                sleep(self.between_event_sleep)
        return run(func, setup=self.tc_setup, teardown=self.tc_teardown)

    # Attention: This is special.
    def test_99_suite_teardown(self):
        """
        Test case: test_00_suite_teardown
        Suite teardown should be the last test in suite.
        """
        def func():
            BsnCommon().base_suite_teardown()
        return run(func)

