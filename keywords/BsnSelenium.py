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
import SeleniumLibrary


class BsnSelenium(object):

    def __init__(self):
        pass

    def title_should_contain(self, title):
        """Verifies that current page title contains `title`."""
        # actual = self._selenium.get_title()
        actual = SeleniumLibrary.SeleniumLibrary().get_title()
        if  not title in actual:
            raise AssertionError("Title %s should have contained '%s' but failed"
                                  % (actual, title))
        helpers.log("Page title is '%s'." % title)
        print("******** Page title is '%s'." % title)