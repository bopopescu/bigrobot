'''
###  WARNING !!!!!!!
###
###  This is where common code for all T6 will go in.
###  If existing T5 keywords can be enhanced to support T6 features
###  (e.g., IVS), then you can enhance the T5 library. This T6 library
###  is intended for new T6 keywords.
###
###  To commit new code, please contact the Library Owner:
###  Prashanth Padubidry (prashanth.padubidry@bigswitch.com)
###
###  DO NOT COMMIT CODE WITHOUT APPROVAL FROM LIBRARY OWNER
###
###  Last Updated: 01/28/2015
###
###  WARNING !!!!!!!
'''

import autobot.helpers as helpers
import autobot.test as test


class T6(object):

    def rest_show_t6_dummy(self, node):
        """
        This is a dummy keyword...
        """
        t = test.Test()
        c = t.controller(node)

        helpers.log("Dummy T6 keyword...")
        return True


