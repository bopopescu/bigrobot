''' 
###  WARNING !!!!!!!
###  
###  This is where common code for all Controller Platforms will go in.
###  
###  To commit new code, please contact the Library Owner: 
###  Vui Le (vui.le@bigswitch.com)
###
###  DO NOT COMMIT CODE WITHOUT APPROVAL FROM LIBRARY OWNER
###
###  Last Updated: 02/05/2014
###
###  WARNING !!!!!!!
'''

import autobot.helpers as helpers
import autobot.test as test
import Controller


class BsnCommon(object):

    def __init__(self):
        pass

    def base_suite_setup(self):
        test.Test().topology()
        obj = Controller.Controller()
        obj.cli_save_running_config()

    def base_suite_teardown(self):
        t = test.Test()
        for n in t.topology():
            node = t.node(n)
            if helpers.is_controller(n) or helpers.is_mininet(n):
                helpers.log("Closing device connection for node '%s'" % n)
                node.dev.close()

    def base_test_setup(self):
        test.Test()

    def base_test_teardown(self):
        pass

    def mock_untested(self):
        print("MOCK UNTESTED")

    def mock_passed(self):
        print("MOCK PASSED")

    def mock_failed(self):
        raise AssertionError("MOCK FAILED")

    def manual_untested(self):
        print("MANUAL UNTESTED")

    def manual_passed(self):
        print("MANUAL PASSED")

    def manual_failed(self):
        raise AssertionError("MANUAL FAILED")

    def show_test_topology_params(self):
        t = test.Test()
        helpers.log("Test topology params: %s" % helpers.prettify(t.topology_params()))

    def expr(self, s):
        result = eval(s)
        helpers.log("Express '%s' evaluated to '%s'" % (s, result))
        return result
