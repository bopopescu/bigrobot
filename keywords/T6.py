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
    
    def rest_verify_vswitch_portgroup(self, link=12):
        ''' function to verify the vswitch portgroup
        '''
        t = test.Test()
        c = t.controller('master')
        url = '/api/v1/data/controller/applications/bcf/info/fabric/port-group' % ()
        c.rest.get(url)
        data = c.rest.content()
        count = 0
        for i in range(0, len(data)):
            if data[i]["mode"] == "static-auto-vswitch-inband":
                count = count + 1
            else:
                continue
        if int(count) == int(link):
            helpers.log("Expected vswitch portgroups are present No of link %s" % link)
            return True
        else:
            helpers.log("Fail: Expected vswitch portgroups are not present in the controller expected = %d, Actual = %d" % (link, count))
            return False

