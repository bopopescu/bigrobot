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
        t.teardown()
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

    def verify_dict_key(self, content, index, key):
        ''' Given a dictionary, return the value for a particular key
        
            Input:Dictionary, index and required key.
            
            Return Value:  return the value for a particular key
        '''
        return content[index][key]

    def add_ntp_server(self, node=None, ntp_server='0.bigswitch.pool.ntp.org'):
        '''
            Objective: Add an NTP server.
            
            Inputs:
            | node | reference to switch/controller as defined in .topo file|
            | ntp_server | ntp server that is being configured|
            
            Return Values:
            - True, if configuration add is successful.
            - False, if configuration add is unsuccessful.
        '''
        t = test.Test()
        n = t.node(node)
        if helpers.is_switch(node):
            helpers.log("Node is a switch")
            if helpers.is_switchlight(n.platform()):
                ''' 
                NTP Configuration at Switch
                '''
                helpers.log("The node is a SwitchLight switch")
                switch = t.switch(node)
                cli_input_1 = "ntp server " + str(ntp_server)
                switch.config(cli_input_1)
                cli_input_2 = "ntp enable"
                switch.config(cli_input_2)
                return True
            else:
                helpers.test_error("Unsupported Platform %s" % (node))
        elif helpers.is_controller(node):
            helpers.log("The node is a controller")
            if helpers.is_bigtap(node):
                '''
                BigTap NTP Configuration goes here
                '''
                helpers.log("The node is a BigTap Controller")
                c = t.controller('master')
                url = '/rest/v1/model/ntp-server/'
                c.rest.put(url, {"enabled": True, "server": str(ntp_server)})
                helpers.test_log("Ouput: %s" % c.rest.result_json())
                if not c.rest.status_code_ok():
                    helpers.test_failure(c.rest.error())
                    return False
                else:
                    helpers.test_log(c.rest.content_json())
                    return True
            elif helpers.is_bigwire(node):
                '''
                BigWire NTP Configuration goes here
                '''
                helpers.log("The node is a BigWire Controller")
                c = t.controller('master')
                url = '/rest/v1/model/ntp-server/'
                c.rest.put(url, {"enabled": True, "server": str(ntp_server)})
                helpers.test_log("Ouput: %s" % c.rest.result_json())
                if not c.rest.status_code_ok():
                    helpers.test_failure(c.rest.error())
                    return False
                else:
                    helpers.test_log(c.rest.content_json())
                    return True
            elif helpers.is_t5(node):
                '''
                    T5 Controller
                '''
                helpers.log("The node is a T5 Controller")
                c = t.controller()
                url = '/api/v1/data/controller/os/config/global/time-config'
                c.rest.put(url, {"ntp-servers": [ntp_server]})
                if not c.rest.status_code_ok():
                    helpers.test_log(c.rest.error())
                    return False
                else:
                    return True
            else:
                helpers.test_error("Unsupported Platform %s" % (node))
        else:
            helpers.test_error("Unsupported Platform %s" % (node))

    def delete_ntp_server(self, node, ntp_server):
        '''
            Objective: Delete a NTP server.
            
            Inputs:
            | node | reference to switch/controller as defined in .topo file|
            | ntp_server | ntp server that is being configured|
            
            Return Values:
            - True, if configuration delete is successful.
            - False, if configuration delete is unsuccessful.
        '''
        t = test.Test()
        n = t.node(node)
        if helpers.is_switch(node):
            helpers.log("Node is a switch")
            if helpers.is_switchlight(n.platform()):
                ''' 
                    NTP Deletion at Switch
                '''
                switch = t.switch(node)
                cli_input_1 = "no ntp server " + str(ntp_server)
                switch.config(cli_input_1)
                cli_input_2 = "no ntp enable"
                switch.config(cli_input_2)
                return True
            else:
                helpers.test_error("Unsupported Platform %s" % (node))
        elif helpers.is_controller(node):
            helpers.log("The node is a controller")
            if  helpers.is_bigtap(node):
                '''
                    BigTap NTP Server Deletion goes here
                '''
                c = t.controller('master')
                try:
                    url = '/rest/v1/model/ntp-server/?enabled=True&server=%s' % (str(ntp_server))
                    c.rest.delete(url, {})
                except:
                    helpers.test_failure(c.rest.error())
                    return False
                else:
                    helpers.test_log(c.rest.content_json())
                    return True
            elif helpers.is_bigwire(node):
                '''
                    BigWire NTP Server Deletion goes here
                '''
                c = t.controller('master')
                try:
                    url = '/rest/v1/model/ntp-server/?enabled=True&server=%s' % (str(ntp_server))
                    c.rest.delete(url, {})
                except:
                    helpers.test_failure(c.rest.error())
                    return False
                else:
                    helpers.test_log(c.rest.content_json())
                    return True
            elif helpers.is_t5(node):
                '''
                    T5 Controller NTP Server Deletion goes here
                '''
                c = t.controller()
                url = '/api/v1/data/controller/os/config/global/time-config'
                c.rest.delete(url, {"ntp-servers": [ntp_server]})
                if not c.rest.status_code_ok():
                    helpers.test_log(c.rest.error())
                    return False
                else:
                    return True
            else:
                helpers.test_error("Unsupported Platform %s" % (node))
        else:
            helpers.test_error("Unsupported Platform %s" % (node))

    def verify_ntp(self, node, ntp_server):
        '''
            Objective: Verify NTP Server Configuration is seen in running-config and in output of "show ntp server"
            
             Inputs:
            | node | reference to switch/controller as defined in .topo file|
            | ntp_server | ntp server that is being configured|
            
            Return Values:
            - True, if configuration delete is successful.
            - False, if configuration delete is unsuccessful.           
        '''
        t = test.Test()
        n = t.node(node)
        if helpers.is_switch(node):
            helpers.log("Node is a switch")
            if helpers.is_switchlight(n.platform()):
                ''' 
                    NTP Verification at Switch
                '''
                switch = t.switch(node)
                pass_count = 0
                cli_input_1 = "show ntp"
                switch.enable(cli_input_1)
                show_output = switch.cli_content()
                if ntp_server in show_output:
                    helpers.test_log("PASS: NTP Server %s was seen in o/p of 'show ntp'" % (ntp_server))
                    pass_count = pass_count + 1
                else:
                    helpers.test_log("FAIL: NTP Server %s was not seen in o/p of 'show ntp'" % (ntp_server))

                switch.enable("show running-config ntp")
                show_output_1 = switch.cli_content()
                if "ntp enable" in show_output_1:
                    helpers.test_log("PASS: Keyword 'ntp enable' was seen in o/p of 'show running-config ntp'")
                    pass_count = pass_count + 1
                else:
                    helpers.test_log("FAIL: Keyword 'ntp enable' was not seen in o/p of 'show running-config ntp'")
                cli_check = "ntp server " + str(ntp_server)
                if cli_check in show_output_1:
                    helpers.test_log("PASS: Keyword 'ntp server %s' was seen in o/p of 'show running-config ntp'" % (ntp_server))
                    pass_count = pass_count + 1
                else:
                    helpers.test_log("FAIL: Keyword 'ntp server %s' was not seen in o/p of 'show running-config ntp'" % (ntp_server))

                if pass_count == 3:
                    return True
                else:
                    return False
        elif helpers.is_controller(node):
            helpers.log("The node is a controller")
            if  helpers.is_bigtap(node):
                '''
                    BigTap NTP Server Verification goes here
                '''
                c = t.controller('master')
                try:
                    url = '/rest/v1/model/ntp-server/'
                    c.rest.get(url)
                except:
                    helpers.test_failure(c.rest.error())
                    return False
                else:
                    content = c.rest.content()
                    pass_flag = False
                    for x in range(0, len(content)):
                        if content[x] == str(ntp_server):
                            pass_flag = True
                    if pass_flag:
                        return True
                    else:
                        return False

            elif helpers.is_bigwire(node):
                '''
                    BigWire NTP Server Verification goes here
                '''
                c = t.controller('master')
                try:
                    url = '/rest/v1/model/ntp-server/'
                    c.rest.get(url)
                except:
                    helpers.test_failure(c.rest.error())
                    return False
                else:
                    content = c.rest.content()
                    pass_flag = False
                    for x in range(0, len(content)):
                        if content[x] == str(ntp_server):
                            pass_flag = True
                    if pass_flag:
                        return True
                    else:
                        return False

            elif helpers.is_t5(node):
                '''
                    T5 Controller NTP Server Verification goes here
                '''
            else:
                helpers.test_error("Unsupported Platform %s" % (node))
        else:
            helpers.test_error("Unsupported Platform %s" % (node))