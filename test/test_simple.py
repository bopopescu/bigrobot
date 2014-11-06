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
from autobot.nose_support import run, log_to_console, wait_until_keyword_succeeds, Singleton
# from keywords.BsnCommon import BsnCommon

helpers.remove_env('BIGROBOT_TOPOLOGY', quiet=True)
# Test suite is defined as the name of the test script minus its extension.
helpers.bigrobot_suite(os.path.basename(__file__).split('.')[0])
setup_env.standalone_environment_setup()


class TestSimple:
    __metaclass__ = Singleton

    def __init__(self):
        self.val = 0

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
        run(test=func, setup=self.tc_setup, teardown=self.tc_teardown)

    def test_02_run_additional_keywords_on_fail(self):
        """
        Test case: test_02_run_additional_keywords_on_fail
        """
        def func():
            try:
                assert 1 == 2
            except:
                # Run additional keywords on fail
                log_to_console("keyword #1:  1 + 2 + 3 = %s" % (1 + 2 + 3))
                log_to_console("keyword #2:  A + B + C = %s" % ('A' + 'B' + 'C'))
                # Still raise it as a test failure
                raise
        run(test=func, setup=self.tc_setup, teardown=self.tc_teardown)

    def test_03_skip(self):
        """
        Test case: test_03_skip
        """
        def func():
            raise SkipTest("not ready")
        run(test=func, setup=self.tc_setup, teardown=self.tc_teardown)

    def test_04_run_until_keyword_succeeds(self):
        """
        Test case: test_04_run_until_keyword_succeeds
        """
        def kw():
            self.val += 1
            assert self.val == 3

        def func():
            wait_until_keyword_succeeds(10, 2, kw)
        run(test=func, setup=self.tc_setup, teardown=self.tc_teardown)
