''' 
###  WARNING !!!!!!!
###  
###  This is where common code for BigTap/BigWire Controllers will go in.
###  
###  To commit new code, please contact the Library Owner: 
###  Animesh Patcha (animesh.patcha@bigswitch.com)
###
###  DO NOT COMMIT CODE WITHOUT APPROVAL FROM LIBRARY OWNER
###  
###  Last Updated: 02/08/2014
###  
###  WARNING !!!!!!!
'''

import autobot.helpers as helpers
import autobot.test as test

class AppController(object):

    def __init__(self):
        pass



###################################################
# All Show Commands Go Here:
###################################################
    def rest_return_switch_dpid_from_alias(self, switch_alias):
        '''
        Objective: Returns switch DPID, given a switch alias
        
        Input:  
        | `switch_alias` |  User defined switch alias | 
        
        Description:
        The function 
        - executes a REST GET for http://<CONTROLLER_IP>:8082/api/v1/data/controller/core/switch?select=alias
        - and greps for switch-alias, and returns switch-dpid
        
        Return value
        - Switch DPID on success
        - False on failure
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('master')
            try:
                url = '/api/v1/data/controller/core/switch?select=alias'
                c.rest.get(url)
                content = c.rest.content()
                for x in range(0, len(content)):
                    if str(content[x]['alias']) == str(switch_alias):
                        return content[x]['dpid']
                return False
            except:
                return False

    def rest_return_switch_dpid_from_ip(self, node):
        '''
        Objective: Returns switch DPID, given a switch alias
        
        Input:  
        | `node` |  Reference to node as defined in .topo file | 
        
        Description:
        The function 
        - executes a REST GET for http://<CONTROLLER_IP>:8082/api/v1/data/controller/core/switch?select=alias
        - and greps for switch-alias, and returns switch-dpid
        
        Return value
        - Switch DPID on success
        - False on failure
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('master')
            switch = t.switch(node)
            try:
                url = '/api/v1/data/controller/core/switch'
                c.rest.get(url)
                content = c.rest.content()
                for x in range(0, len(content)):
                    if str(content[x]['inet-address']['ip']) == switch.ip():
                        return content[x]['dpid']
                return False
            except:
                return False

    def rest_show_switch(self):
        '''Return dictionary containing DPID,IP Addresses for every switch connected to current controller
        
            Input: N/A
            
            Returns: Dictionary of Switch DPID and IP Addresses
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('master')
            try:
                url = '/api/v1/data/controller/core/switch'
                c.rest.get(url)
            except:
                helpers.test_failure(c.rest.error())
                return False
            else:
                content = c.rest.content()
                switch_dict = {}
                for x in range (0, len(content)):
                    switch_dict[str(content[x]['inet-address']['ip'])] = str(content[x]['dpid'])
                return switch_dict
###################################################
# All Config Commands Go Here:
###################################################
    def rest_add_switch_alias(self, node, switch_alias):
        '''
            Objective:
            - Configure switch alias
            
            Inputs:
            | node | Reference to switch as defined in .topo file |
            | switch_alias | alias of switch |
            
            Return Value:
            | True | On configuration success|
            | False | On configuration failure |
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('master')
            try:
                switch_dpid = self.rest_return_switch_dpid_from_ip(node)
            except:
                return False
            else:
                try:
                    url = '/api/v1/data/controller/core/switch[dpid="%s"]' % switch_dpid
                    c.rest.put(url, {"dpid": str(switch_dpid)})
                except:
                    return False
                else:
                    if not c.rest.status_code_ok():
                        helpers.test_log(c.rest.error())
                        return False
                    else:
                        try:
                            url = '/api/v1/data/controller/core/switch[dpid="%s"]' % switch_dpid
                            c.rest.patch(url, {"alias": str(switch_alias)})
                        except:
                            return False
                        else:
                            if not c.rest.status_code_ok():
                                helpers.test_log(c.rest.error())
                                return False
                            else:
                                helpers.test_log(c.rest.content_json())
                                return True

    def rest_delete_switch_alias(self, node):
        '''
            Objective:
            - Delete switch alias
            
            Inputs:
            | node | Reference to switch as defined in .topo file |
            
            Return Value:
            | True | On configuration success|
            | False | On configuration failure |        
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('master')
            try:
                switch_dpid = self.rest_return_switch_dpid_from_ip(node)
            except:
                return False
            else:
                try:
                    url = '/api/v1/data/controller/core/switch[dpid="%s"][dpid="%s"]/alias' % (switch_dpid, switch_dpid)
                    c.rest.delete(url, {})
                except:
                    return False
                else:
                    if not c.rest.status_code_ok():
                        helpers.test_log(c.rest.error())
                        return False
                    else:
                        helpers.test_log(c.rest.content_json())
                        return True

    def rest_delete_switch(self, node):
        '''
            Objective:
            - Delete switch 
            - Execute cli command 'switch 00:00:5c:16:c7:1c:16:f2'
            
            Inputs:
            | node | Reference to switch as defined in .topo file |
            
            Return Value:
            | True | On configuration success|
            | False | On configuration failure |        
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('master')
            try:
                switch_dpid = self.rest_return_switch_dpid_from_ip(node)
            except:
                return False
            else:
                try:
                    url = '/api/v1/data/controller/core/switch[dpid="%s"]' % (switch_dpid)
                    c.rest.delete(url, {})
                except:
                    return False
                else:
                    if not c.rest.status_code_ok():
                        helpers.test_log(c.rest.error())
                        return False
                    else:
                        helpers.test_log(c.rest.content_json())
                        return True

###################################################
# All Verify Commands Go Here:
###################################################
    def rest_verify_interface_is_up(self, node, interface_name):
        '''Verify if a given interface on a given switch is up
        
            Input: 
                `switch_dpid`       DPID of the Switch
                `interface_name`    Interface Name e.g. ethernet13
            
            Returns: True if the interface is up, false otherwise
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('master')
            try:
                switch_dpid = self.rest_return_switch_dpid_from_ip(node)
                url = '/api/v1/data/controller/core/switch[interface/name="%s"][dpid="%s"]?select=interface[name="%s"]' % (interface_name, switch_dpid, interface_name)
                c.rest.get(url)
            except:
                helpers.test_failure(c.rest.error())
                return False
            else:
                if not c.rest.status_code_ok():
                    helpers.test_failure(c.rest.error())
                content = c.rest.content()
                if (content[0]['interface'][0]['state-flags'] == 0):
                        return True
                else:
                        return False
