'''
###  WARNING !!!!!!!
###
###  This is where common code for all BSN Selenium will go in.
###
###  To commit new code, please contact the Library Owner:
###  Vui Le (vui.le@bigswitch.com)
###
###  DO NOT COMMIT CODE WITHOUT APPROVAL FROM LIBRARY OWNER
###
###  Last Updated: 08/25/2014
###
###  WARNING !!!!!!!
'''

import autobot.helpers as helpers
import autobot.test as test
from robot.libraries.BuiltIn import BuiltIn


class BsnSelenium(object):

    def __init__(self):
        pass

    def title_should_contain(self, title):
        """Verifies that current page title contains `title`."""

        seleniumlib = BuiltIn().get_library_instance('SeleniumLibrary')
        actual = seleniumlib.get_title()

        if  not title in actual:
            raise AssertionError("Title %s should have contained '%s' but failed"
                                  % (actual, title))
        helpers.log("Page title is '%s' (actual is '%s')." % (title, actual))
