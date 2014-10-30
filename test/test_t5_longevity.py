from __future__ import print_function
import os
import sys
from nose.tools import with_setup
from nose.exc import SkipTest


# Derive BigRobot path from the script's location, which should be
# in the bigrobot/test directory.
bigrobot_path = os.path.dirname(__file__) + '/..'
exscript_path = bigrobot_path + '/vendors/exscript/src'
sys.path.insert(0, exscript_path)
sys.path.insert(0, bigrobot_path)


import autobot.helpers as helpers
from autobot.setup_env import environment_setup, run, log_to_console, sleep
from keywords.BsnCommon import BsnCommon
from keywords.Controller import Controller
from keywords.Mininet import Mininet
from keywords.Host import Host
from keywords.Ixia import Ixia
from keywords.T5 import T5
from keywords.T5L3 import T5L3
from keywords.T5Platform import T5Platform
from keywords.SwitchLight import SwitchLight
from keywords.T5Utilities import T5Utilities


helpers.set_env('BIGROBOT_TEST_POSTMORTEM', 'False', quiet=True)
helpers.set_env('BIGROBOT_TEST_SETUP', 'False', quiet=True)
helpers.set_env('BIGROBOT_TEST_CLEAN_CONFIG', 'False', quiet=True)
helpers.set_env('BIGROBOT_TEST_TEARDOWN', 'False', quiet=True)
helpers.remove_env('BIGROBOT_TOPOLOGY', quiet=True)

# Test suite is defined as the name of the test script minus its extension.
helpers.bigrobot_suite(os.path.basename(__file__).split('.')[0])
environment_setup()
assert helpers.bigrobot_path() != None
assert helpers.bigrobot_log_path_exec_instance() != None
assert helpers.bigrobot_suite() != None
helpers.print_bigrobot_env(minimum=True)


# Global variables (Test controls)
LOOP = 5
INEVENT = 300


#
# Test case setup and teardown annotations.
#

def setup():
    """Nose fixture: setup"""
    # print("\nInside nose_setup")


def teardown():
    """Nose fixture: teardown"""
    # print("\nInside nose_teardown")


#
# Supporting keywords
#

def cli_show_commands_for_debug():
    BsnCommon().cli('master', 'show ver', timeout=60)
    BsnCommon().enable('master', 'show running-config switch', timeout=60)
    BsnCommon().enable('master', 'show switch', timeout=60)
    BsnCommon().enable('master', 'show link', timeout=60)
    BsnCommon().cli('master', 'show ver', timeout=60)
    BsnCommon().cli('slave', 'show ver', timeout=60)


def controller_node_event_ha_failover(during=30):
    log_to_console("=============HA failover ===============")
    cli_show_commands_for_debug()
    T5Platform().cli_cluster_take_leader()
    sleep(during)
    cli_show_commands_for_debug()
#
# Test case definitions
#

def test_00_suite_setup():
    # Suite setup should be the first test. Raise critical error if setup fails.
    def func():
        # raise SkipTest("not ready")
        BsnCommon().base_suite_setup()
        for i in range(0, 500):
            BsnCommon().config('master', 'no tenant FLAP%s' % i)
    return run(func, exit_on_failure=True)


@with_setup(setup, teardown)
def test_01_controller_node_event_failover():
    def func():
        for i in range(0, LOOP):
            log_to_console("\n******* controller node failover: %s*******" % i)
            controller_node_event_ha_failover(INEVENT)
            sleep(INEVENT)
    return run(func)


@with_setup(setup, teardown)
def test_02_t5_longevity_show_fabric_links():
    def func():
        raise SkipTest("not ready")
    return run(func)


@with_setup(setup, teardown)
def test_03_t5_longevity_show_running_config():
    def func():
        raise SkipTest("not ready")
    return run(func)


def test_99_t5_longevity_suite_teardown():
    # Suite teardown should be the last test.
    def func():
        BsnCommon().base_suite_teardown()
    return run(func)

