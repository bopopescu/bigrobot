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
    def cli_upgrade_image(self, node=None, package=None, timeout=200, sleep_time=200):
        '''
            Objective:
            - Execute CLI commands to download given upgrade package to Master (and Slave if exists) Controllers and upgrade them

            Input:
            | `package` |  URL to the upgrade package | 
            | `node` |  Node to be upgraded. Leave empty to upgrade all nodes in your topology | 
            | `timeout` |  Timeout (in seconds) for "upgrade" command to be execute | 
            | `sleep` |  Time (in seconds) of sleep after upgrade, before next actions | 
            
            Return Value: 
            - True if configuration is successful
            - False otherwise
        '''

        t = test.Test()

        if not package:
            helpers.test_error("You must specify a package name")
        if not node:
            # assume all controllers if node is not specified
            node_handles = t.controllers()
            controller_qty = len(t.controllers())
        else:
            node_handles = [t.controller(node)]
            controller_qty = 1


        helpers.log("Number of controllers %s" % controller_qty)

        if controller_qty > 2 or controller_qty < 1:
            helpers.test_failure("More than two controllers or no controller configured")
            return False


        for i in range(0, controller_qty):
            try:
                if controller_qty > 1:
                    n = t.controller('slave')
                else:
                    n = node_handles[0]

                helpers.log("Upgrade '%s' to image '%s'" % (n.name(), package))
                n.bash("cd /home/images/")
                n.bash("sudo rm *")
                n.bash("sudo wget  %s" % package)
                n.bash("exit")
                helpers.log("Image downloaded successfully")

                n.enable('enable')
                n.send("upgrade")
                n.expect(r"\(yes to continue\)")
                n.send("yes")
                n.expect(r"Password:")
                n.enable("adminadmin", timeout=timeout)
                n.send("reload")
                n.expect(r"Confirm Reload \(yes to continue\)")
                n.send("yes")
                helpers.sleep(sleep_time)
            except:
                helpers.test_failure("Output: %s" % n.cli_content())
                return False
        return True


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
                    if content[x].has_key('inet-address'):
                        if str(content[x]['inet-address']['ip']) == switch.ip():
                            return content[x]['dpid']
                    else:
                        helpers.log("Looks like %s is a disconnected switch" % (content[x]['dpid']))
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
