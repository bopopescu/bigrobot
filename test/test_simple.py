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


def setup():
    """Nose fixture: setup"""
    print("\nInside nose_setup")


def teardown():
    """Nose fixture: teardown"""
    print("\nInside nose_teardown")


#
# Test case definitions
#

@with_setup(setup, teardown)
def test_01_verify_environment():
    def func():
        MyTest().strip_control_char_test()
        assert helpers.bigrobot_path() != None
        assert helpers.bigrobot_log_path_exec_instance() != None
        assert helpers.bigrobot_suite() != None
        print()
        helpers.print_bigrobot_env(minimum=True)
        assert 1 != 1
    return run(func)


@with_setup(setup, teardown)
def test_02_verify_decorator():
    def func():
        assert 1 == 2
        print("**** I am here")
    return run(func)


if __name__ == '__main__':
    test_01_verify_environment()
