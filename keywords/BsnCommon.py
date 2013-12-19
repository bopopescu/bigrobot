import autobot.helpers as helpers
import autobot.test as test


class BsnCommon(object):

    def __init__(self):
        pass
        
    def base_suite_setup(self):
        t = test.Test()

    def base_suite_teardown(self):
        pass

    def base_test_setup(self):
        t = test.Test()

    def base_test_teardown(self):
        pass

    def mock_passed(self):
        #helpers.sleep(2)
        print("MOCK PASSED")

    def mock_failed(self):
        raise AssertionError("MOCK FAILED")

    def manual_passed(self):
        print("MANUAL PASSED")

    def manual_failed(self):
        raise AssertionError("MANUAL FAILED")

