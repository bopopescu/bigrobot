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
from autobot.setup_env import environment_setup, run
from keywords_dev.vui.MyTest import MyTest

helpers.remove_env('BIGROBOT_TOPOLOGY', quiet=True)
# Test suite is defined as the name of the test script minus its extension.
helpers.bigrobot_suite(os.path.basename(__file__).split('.')[0])
environment_setup()


def test_setup():
    """Nose fixture: Test case setup"""


def test_teardown():
    """Nose fixture: Test case teardown"""


#
# Test case definitions
#

@with_setup(test_setup, test_teardown)
def test_01_verify_environment():
    def func():
        MyTest().strip_control_char_test()
        assert helpers.bigrobot_path() != None
        assert helpers.bigrobot_log_path_exec_instance() != None
        assert helpers.bigrobot_suite() != None
        print()
        helpers.print_bigrobot_env(minimum=True)
    return run(func)


@with_setup(test_setup, test_teardown)
def test_02_show_config_commands():
    def func():
        MyTest().my_config_commands('c1')
    return run(func)


@with_setup(test_setup, test_teardown)
def test_03_assert():
    def func():
        raise SkipTest("not ready")
    return run(func)


@with_setup(test_setup, test_teardown)
def test_04_forced_failure():
    def func():
        assert 1 / 0
    return run(func)
