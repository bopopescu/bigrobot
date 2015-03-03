''' 
###  WARNING !!!!!!!
###  
###  This is where common code for BigTap will go in.
###  
###  To commit new code, please contact the Library Owner: 
###  Animesh Patcha (animesh.patcha@bigswitch.com)
###
###  DO NOT COMMIT CODE WITHOUT APPROVAL FROM LIBRARY OWNER
###  
###  Last Updated: 01/30/2014
###  
###  WARNING !!!!!!!
'''

import autobot.helpers as helpers
import autobot.test as test
import keywords.AppController as AppController
import json
import re
import time
from BsnCommon import BsnCommon as bsnCommon
from datetime import datetime
from time import mktime

class BigTap(object):

    def __init__(self):
        pass

###################################################
# All Bigtap Show Commands Go Here:
###################################################


    def rest_show_switch_flow(self, node, switch_alias=None, sw_dpid=None, return_value=None):
        '''
        Objective: 
        - Returns number of flows on a switch
        
        Input: 
        | 'switch_dpid' |  Datapath ID of the switch | 
        
        Description:
        - The function executes a REST GET for http://<CONTROLLER_IP>:8082/api/v1/data/controller/core/switch[dpid="<SWITCH_DPID>"]?select=stats/table
        - Returns number of active flows
        
        Return value: 
        - Number of active flows on the switch
        '''
        t = test.Test()
        try:
            c = t.controller('master')
            AppCommon = AppController.AppController()
        except:
            return False
        else:
            try:
                if (switch_alias is None and sw_dpid is not None):
                    switch_dpid = sw_dpid
                elif (switch_alias is None and sw_dpid is None):
                    switch_dpid = AppCommon.rest_return_switch_dpid_from_ip(node)
                elif (switch_alias is not None and sw_dpid is None):
                    switch_dpid = AppCommon.rest_return_switch_dpid_from_alias(switch_alias)
                else:
                    switch_dpid = sw_dpid
                url = '/api/v1/data/controller/core/switch[dpid="%s"]?select=stats/table' % (str(switch_dpid))
                c.rest.get(url)
                content = c.rest.content()
            except:
                helpers.test_log("Could not execute command")
                return False
            else:
                if return_value is not None:
                    return content[0]['stats']['table'][0][return_value]
                else:
                    return content[0]['stats']['table'][0]['active-count']

    def rest_return_switch_flow(self, node, flow_index, flow_key, flow_id=0, switch_alias=None, sw_dpid=None, soft_error=False):
        '''
            Objective: Verify flow is pushed via controller
            
            Input:
            | node | Specify switch as defined in topo file|
            |flow_index| Index in flow you want returned|
            |_key| Key in the index you want returned|
            
            Return Value:
            Value of the specified key
        '''
        t = test.Test()
        try:
            c = t.controller('master')
            AppCommon = AppController.AppController()
        except:
            return False
        else:
            try:
                if (switch_alias is None and sw_dpid is not None):
                    switch_dpid = sw_dpid
                elif (switch_alias is None and sw_dpid is None):
                    switch_dpid = AppCommon.rest_return_switch_dpid_from_ip(node)
                elif (switch_alias is not None and sw_dpid is None):
                    switch_dpid = AppCommon.rest_return_switch_dpid_from_alias(switch_alias)
                else:
                    switch_dpid = sw_dpid
                url = '/api/v1/data/controller/core/switch[dpid="%s"]?select=stats/flow' % (str(switch_dpid))
                c.rest.get(url)
                content = c.rest.content()
            except:
                helpers.test_log("Could not execute command")
                return False
            else:
                return content[0]['stats']['flow'][int(flow_id)]['match-field'][int(flow_index)][str(flow_key)]



# Mingtao
    def rest_show_address_group(self, group):
        """ 
            Objective:
            Return output of show address-group group_name.
            
            Input:
            | group | Name of IP Address Group|

            Return Value:
            - Returns dictionary of elements on success
            - Returns False on failure.
        """
        t = test.Test()
        c = t.controller('master')
        url = '/api/v1/data/controller/applications/bigtap/ip-address-set[name="%s"]' % (str(group))
        c.rest.get(url)
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())

        if(c.rest.content()):
            helpers.log("INFO: name: %s" % c.rest.content()[0]['name'])
            helpers.log("INFO: type: %s" % c.rest.content()[0]['ip-address-type'])
            return c.rest.content()[0]

        return False

# Mingtao
    def rest_show_policy_optimize(self, policy):
        ''' 
            Objective:
            Return number of optimized matches per given policy.
            
            Input:
            | policy | Name of policy|

            Return Value:
            - Returns number of optimized matches
            - Returns False on failure.
        '''
        t = test.Test()
        c = t.controller('master')

        helpers.test_log("Input arguments: policy = %s " % (policy))
        url = '/api/v1/data/controller/applications/bigtap/view/policy[name="%s"]/debug' % policy
        c.rest.get(url)

        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())

        content = c.rest.content()
        if content[0]['name'] == str(policy):
            helpers.test_log("Policy correctly reports policy name as : %s" % content[0]['name'])
            temp = content[0]['optimized-match'].strip()
            temp = temp.split('\n')
        else:
            helpers.test_log("Policy does not correctly report policy name  : %s" % content[0]['name'])
            return False
        return len(temp)
# Mingtao
    def rest_show_run_policy(self, policy):
        """ Get the rest output of "show run bigtap policy XX"
            -- Mingtao
            Usage:                     
        """
        t = test.Test()
        c = t.controller('master')
        url = '/api/v1/data/controller/applications/bigtap/view[policy/name="%s"]?config=true&select=policy[name="%s"]' % (policy, policy)
        c.rest.get(url)

        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
        if(c.rest.content()):
            helpers.log("INFO: name: %s" % c.rest.content()[0]['policy'][0])
            if c.rest.content()[0]['policy'][0]['name'] == str(policy):
                return c.rest.content()[0]['policy'][0]
            else:
                helpers.test_log("ERROR: Policy does not correctly report policy name  : %s" % c.rest.content()[0]['policy'][0]['name'])
                return False
        helpers.test_log("ERROR: Policy does not correctly report ")
        return False

# Mingtao
    def rest_get_run_policy_feild(self, input_dict, policy, match=None):
        """ Get the rest output of "show bigtap policy XX"
            -- Mingtao
            Usage:                     
        """
        helpers.log("Output: input_dict: %s" % input_dict)

        if input_dict['name'] == str(policy):
            helpers.test_log("INFO: Policy correctly reports policy name as : %s" % input_dict['name'])
        else:
            helpers.test_log("ERROR: Policy does not correctly report policy name  : %s" % input_dict['name'])
            return False

        if match:
            temp = input_dict['rule']
            helpers.test_log("INFO: Policy  %s has %d of matches" % (policy, len(temp)))
            return len(temp)

        return True

# Mingtao
    def cli_show_bigtap_policy(self):
        t = test.Test()
        c = t.controller('master')
        string = 'show running-config bigtap policy'
        c.cli(string)
        content = c.cli_content()
        return content



# Mingtao
    def rest_show_feature(self, feature="l3-l4-mode"):
        """ 
            Objective: Verify bigtap mode: l3_l4 and inport_mask
            
            Input: 
            |Feature | Name of Feature being verified|
        """
        t = test.Test()
        c = t.controller('master')
        c.rest.get('/rest/v1/system/version')
        content = c.rest.content()
        version_string = content[0]['controller']
        helpers.log("version string is %s" % version_string)
        url = '/api/v1/data/controller/applications/bigtap/info'
        c.rest.get(url)
        if not c.rest.status_code_ok():
            helpers.test_log(c.rest.error())
            return False
        data = c.rest.content()
        if ("3.1.1" in str(version_string)) or ("3.1.0" in str(version_string)) or ("3.0.0" in str(version_string)):
            if not data[0][feature]:
                helpers.test_log("INFO: ***********Bigtap does not have the %s shown *******" % feature)
                return "False"
            helpers.test_log("INFO: Bigtap reports feature: %s  -  as: %s " % (feature, data[0][feature]))
            return str(data[0][feature])
        else:
            if ("l3-l4" in feature) or ("full-match" in feature):
                if "l3-l4-mode" in feature:
                    matchcondition = "bigtap-l3l4"
                elif "offset" in feature:
                    matchcondition = "bigtap-offset-match"
                else:
                    matchcondition = "bigtap-full-match"
                if (data[0]["match-mode"] == matchcondition):
                    return "True"
                else:
                    helpers.test_log("INFO: ***********Bigtap does not have the %s shown *******" % feature)
                    return "False"
            else:
                if not data[0][feature]:
                    helpers.test_log("INFO: ***********Bigtap does not have the %s shown *******" % feature)
                    return "False"
                helpers.test_log("INFO: Bigtap reports feature: %s  -  as: %s " % (feature, data[0][feature]))
                return str(data[0][feature])


#  Mingtao
    def cli_show_feature(self, feature_name="l3-l4"):
        t = test.Test()
        c = t.controller('master')
        string = "show running-config bigtap |  grep " + str(feature_name) + " | wc -l "
        c.cli(string)
        content = c.cli_content()
        lines = content.split('\r\n')
        helpers.log("***** lines: %s" % lines)
        if int(lines[1]) == 0:
            helpers.log("INFO: the %s  NOT configured" % str(feature_name))
            # return "False"
            return False
        elif int(lines[1]) == 1:
            helpers.log("INFO: the %s  is configured" % str(feature_name))
            # return "True"
            return True
        else:
            helpers.test_log(c.rest.error())
            return False

    def cli_show_l3_l4(self):
        t = test.Test()
        c = t.controller('master')
        string = "show running-config bigtap |  grep l3-l4 | wc -l "
        c.cli(string)
        content = c.cli_content()
        lines = content.split('\r\n')
        helpers.log("***** lines: %s" % lines)
        if int(lines[1]) == 0:
            helpers.log("INFO: the l3-l4  NOT configured")
            return False
        elif int(lines[1]) == 1:
            helpers.log("INFO: the l3-l4  is configured")
            return True
        else:
            helpers.test_failure(c.rest.error())
            return False

    def cli_show_trackhost(self):
        t = test.Test()
        c = t.controller('master')
        string = 'show running-config bigtap |  grep trackhost | wc -l '
        c.cli(string)
        content = c.cli_content()
        lines = content.split('\r\n')
        helpers.log("***** lines: %s" % lines)
        if int(lines[1]) == 0:
            helpers.log("INFO: the trackhost Not configured")
            return "False"
        elif int(lines[1]) == 1:
            helpers.log("INFO: the trackhost  configured")
            return "True"
        else:
            helpers.test_failure(c.rest.error())
            return False

# Tomasz
    def cli_configure_user(self, username, passwd=None):
        '''
            Objective:
            - Execute the CLI command 'user username'
            - Execute the CLI command 'password passwd' (if non-empty)
        
            Input:
            | `username` |  Username | 
            | `passwd` | Password |
            
            Return Value: 
            - True if configuration is successful
            - False otherwise
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('master')

            try:
                string = "user %s" % str(username)

                if (passwd is not None):
                    string = string + "; password %s" % str(passwd)
                helpers.test_log("Issue command: %s" % string)
                result = c.config(string)
                helpers.log("Output: %s" % result)

                return True
            except:
                helpers.test_failure("Something went wrong")
                return False

###################################################
# All Bigtap Verify Commands Go Here:
###################################################
    def rest_verify_bigtap_policy(self, policy_name, num_filter_intf=None, num_delivery_intf=None, return_value=None, flag=False, action='forward', user="admin", password="adminadmin"):
        '''
        Objective:
        Parse the output of cli command 'show bigtap policy <policy_name>'
              
        Inputs:
        
        | `policy_name` | Name of the policy being parsed | 
        | `num_filter_intf` | Number of configured Filter Interfaces in the policy | 
        | `num_delivery_intf` | Number of configured Delivery Interfaces in the policy | 
        | `return_value` | If you need a particular value from the dictionary|
        
        Description:
        The function executes a REST GET for http://<CONTROLLER_IP>:8082/api/v1/data/controller/applications/bigtap/view/policy[name="<POLICY_NAME>"]/info
        The policy returns True if and only if all the following conditions are True 
        - Policy name is seen correctly in the output
        - Config-Status is either "active and forwarding" or "active and rate measure"
        - Type is "Configured"
        - Runtime Status is "installed"
        - Delivery interface count is num_delivery_intf
        - Filter Interface count is num_filter_intf
        - Detailed status is either "installed to forward" or "installed to measure rate"        
        
        Return value: 
        - True on success
        - False otherwise
        '''
        try:
            t = test.Test()
            c = t.controller('master')
        except:
            helpers.test_log("Could not execute command")
            return False
        else:
            url = '/api/v1/data/controller/applications/bigtap/view/policy[name="%s"]/info' % str(policy_name)
            if "admin" not in user:
                c_user = t.node_spawn(ip=c.ip(), user=str(user), password=password)
                c_user.rest.get(url)
                if not c_user.rest.status_code_ok():
                    helpers.test_log(c_user.rest.error())
                    return False
                content = c_user.rest.content()
                c_user.close()
            else:
                c.rest.get(url)
                if not c.rest.status_code_ok():
                    helpers.test_log(c.rest.error())
                    return False
                content = c.rest.content()
            if len(content) == 0:
                return False
            else:
                if (return_value is not None) :
                    return content[0][return_value]
                else:
                    if content[0]['name'] == str(policy_name):
                        helpers.test_log("Policy correctly reports policy name as : %s" % content[0]['name'])
                    else:
                        helpers.test_log("Policy does not correctly report policy name  : %s" % content[0]['name'])
                        return False

                    if (content[0]['config-status'] == "active and forwarding") and (str(action) == "forward"):
                        helpers.test_log("Policy correctly reports config status as : %s" % content[0]['config-status'])
                    elif (content[0]['config-status'] == "active and rate measure") and (str(action) == "rate-measure"):
                        helpers.test_log("Policy correctly reports config status as : %s" % content[0]['config-status'])
                    elif (content[0]['config-status'] == "inactive") and (str(action) == "inactive"):
                        helpers.test_log("Policy correctly reports config status as : %s" % content[0]['config-status'])
                    else:
                        helpers.test_log("Policy does not correctly report config status as : %s and passed action value is %s" % (content[0]['config-status'], str(action)))
                        return False

                    if content[0]['type'] == "Configured":
                        helpers.test_log("Policy correctly reports type as : %s" % content[0]['type'])
                    elif content[0]['type'] == "Dynamic":
                        helpers.test_log("Policy correctly reports type as : %s" % content[0]['type'])
                    else:
                        helpers.test_log("Policy does not correctly report type. Type seen is : %s" % content[0]['type'])
                        return False

                    if "installed" in content[0]['runtime-status']:
                        helpers.test_log("Policy correctly reports runtime status as : %s" % content[0]['runtime-status'])
                    elif "installed to drop" in content[0]['runtime-status']:
                        helpers.test_log("Policy correctly reports runtime status as : %s" % content[0]['runtime-status'])
                    elif "inactive" in content[0]['runtime-status'] and flag is True:
                        helpers.test_log("Policy correctly reports runtime status as : %s" % content[0]['runtime-status'])
                    else:
                        helpers.test_log("Policy does not correctly report runtime status as : %s" % content[0]['runtime-status'])
                        return False

                    if (num_delivery_intf is not None):
                        if content[0]['delivery-interface-count'] == int(num_delivery_intf):
                            helpers.test_log("Policy correctly reports number of delivery interfaces as : %s" % content[0]['delivery-interface-count'])
                        else:
                            helpers.test_log("Policy does not correctly report number of delivery interfaces  : %s" % content[0]['delivery-interface-count'])
                            return False
                    if (num_filter_intf is not None):
                        if content[0]['filter-interface-count'] == int(num_filter_intf):
                            helpers.test_log("Policy correctly reports number of filter interfaces as : %s" % content[0]['filter-interface-count'])
                        else:
                            helpers.test_log("Policy does not correctly report number of filter interfaces  : %s" % content[0]['filter-interface-count'])
                            return False

                    if "installed to forward" in content[0]['detailed-status']:
                        helpers.test_log("Policy correctly reports detailed status as : %s" % content[0]['detailed-status'])
                    elif ("installed to measure rate" in content[0]['detailed-status']) or ("installed to drop" in content[0]['detailed-status']):
                        helpers.test_log("Policy correctly reports detailed status as : %s" % content[0]['detailed-status'])
                    elif ("installed with service(s) not on all component policies" in content[0]['detailed-status']):
                        helpers.test_log("Policy correctly reports detailed status as : %s" % content[0]['detailed-status'])
                    elif "inactive" in content[0]['detailed-status'] and flag is True:
                        helpers.test_log("Policy correctly reports detailed status as : %s" % content[0]['detailed-status'])
                    else:
                        helpers.test_log("Policy does not correctly report detailed status as : %s" % content[0]['detailed-status'])
                        return False
                    return True

    def rest_verify_service_interface_state_in_policy(self, node, policy_name, service_name, service_pre_interface=None, service_post_interface=None):
        try:
            t = test.Test()
            c = t.controller('master')
            AppCommon = AppController.AppController()

        except:
            helpers.test_log("Could not execute command")
            return False
        else:
            url = '/api/v1/data/controller/applications/bigtap/view/policy[name="%s"]/service-interface' % str(policy_name)
            c.rest.get(url)
            if not c.rest.status_code_ok():
                helpers.test_log(c.rest.error())
                return False
            content = c.rest.content()


            if ' ' in (service_name.strip()):
                service_nodes = re.split(' ', service_name)
            else:
                service_nodes = [service_name]

            if service_pre_interface is not None:
                if ' ' in (service_pre_interface.strip()):
                    service_pre_interface_name = re.split(' ', service_pre_interface)
                else:
                    service_pre_interface_name = [service_pre_interface]

            if service_post_interface is not None:
                if ' ' in (service_post_interface.strip()):
                    service_post_interface_name = re.split(' ', service_post_interface)
                else:
                    service_post_interface_name = [service_post_interface]

            for x in range(0, len(content)):
                if content[x]['switch'] == AppCommon.rest_return_switch_dpid_from_ip(node):
                    helpers.log("Policy correctly shows switch dpid for service")
                else:
                    helpers.log("Policy does not correctly shows switch dpid for service")
                    return False
                if content[x]['state'] == "up":
                    helpers.log("Policy correctly shows interface state for service as up")
                else:
                    helpers.log("Policy does not correctly show interface state for service as up")
                    return False
                service_fail = 0
                for y in range(0, len(service_nodes)):
                    if content[x]['service-name'] == service_nodes[y]:
                        helpers.log("Policy correctly shows Service Name")
                    else:
                        service_fail = service_fail + 1
                if service_fail == len(service_nodes):
                    helpers.log("Service Name %s was not found in Policy" % service_name)
                    return False
                if service_pre_interface is not None:
                    service_fail = 0
                    for y in range(0, len(service_pre_interface_name)):
                        if content[x]['direction'] == "tx" and content[x]['bigtapinterface'] == service_pre_interface_name[y]:
                            helpers.log("Policy correctly shows Pre Service Name")
                        else:
                            service_fail = service_fail + 1
                    if service_fail == len(content):
                        helpers.log("Service Name %s was not found in Policy" % service_pre_interface)
                        return False
                if service_post_interface is not None:
                    service_fail = 0
                    for y in range(0, len(service_post_interface_name)):
                        if content[x]['direction'] == "rx" and content[x]['bigtapinterface'] == service_post_interface_name[y]:
                            helpers.log("Policy correctly shows Post Service Name")
                        else:
                            service_fail = service_fail + 1
                    if service_fail == len(content):
                        helpers.log("Service Name %s was not found in Policy" % service_post_interface)
                        return False
                return True

    def rest_verify_policy_key(self, policy_name, method, index, key):
        '''
            Objective:
            - Execute a rest get and verify if a particular key exists in a policy
        
            Inputs
            | `policy_name` |  Policy Name being tested for| 
            | `method`    |  Methods can be info/rule/filter-interface/delivery-interface/service-interface/core-interface/failed-paths| 
            | `index`    |  Index in the array| 
            | `key`      |  Particular key we are looking for.| 
            
            Description:
                rest_check_policy_key('testPolicy','ip-proto',0,'rule') would check execute a REST get on "http://<CONTROLLER_IP>:8082/api/v1/data/controller/applications/bigtap/view/policy[name="testPolicy"]/rule
                and return the value "ip-proto"
            
            Return Value: 
            - Value of key if the key exists, 
            - False if it does not.
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('master')
            try:
                url = '/api/v1/data/controller/applications/bigtap/view/policy[name="%s"]/%s' % (str(policy_name), str(method))
                c.rest.get(url)
            except:
                return False
            else:
                if(c.rest.content()):
                    content = c.rest.content()
                    return content[int(index)][str(key)]
                else:
                    helpers.test_log("ERROR Policy %s does not exist. Error seen: %s" % (str(policy_name), c.rest.result_json()))
                    return False

# Mingtao
    def verify_address_group(self, input_dict, group_name, group_type=None, entry=None):
        """ Verify the  type or/and entry number bigtap address group
            -- Mingtao
            Usage: 
             verify_address_group        ${input_dict}    IPV4   group_type=ipv4   entry=1                    
        """
        helpers.log("input_dict: %s" % input_dict)
        if str(group_name) == input_dict['name']:
            if group_type:
                if group_type == input_dict['ip-address-type']:
                    helpers.log("INFO: type is correctly reported as %s" % group_type)
                else:
                    helpers.log("ERROR: type NOT correctly reported: EXPECT: %s  - ACTUAL:  %s" % (group_type, input_dict['ip-address-type']))
                    return False

            if entry:
                if int(entry) == len(input_dict['address-mask-set']):
                    helpers.log("INFO: number of entries: %s" % len(input_dict['address-mask-set']))
                else :
                    helpers.log("ERROR: entry NOT correctly reported: EXPECT: %s  - ACTUAL: %s " % (entry, len(input_dict['address-mask-set'])))
                    return False
        else:
            helpers.log("ERROR: Not correctly report the Name: EXPECT: %s  - ACTUAL: %s " % (group_name, input_dict['name']))
            return False

        return True

# Mingtao
    def verify_switch_tcam_max(self, node=None, l3_l4_mode=None):
        """ verify the switch tcam size
            Usage:  verify_switch_tcam   S203    L3_l4_mode= True
            -- Mingtao
        """
        t = test.Test()
        s = t.switch(node)
        node_type = s.info('model')
        size = self.rest_show_switch_flow(node=node, return_value='maximum-entries')

        if l3_l4_mode == "True":
            if node_type == 'LB9':
                if size == 4088:
                    helpers.test_log("INFO: Switch  - %s  type - %s  and - L3-l4 mode, tcam size - %s " % (node, node_type, str(size)))
                    return True
                else:
                    helpers.test_log("ERROR: Switch - %s  type - %s  and - L3-l4 mode, tcam size expect - 4088, actual - %s " % (node, node_type, str(size)))
                    return False
            elif node_type == 'LY2':
                if size == 2040:
                    helpers.test_log("INFO: Switch  - %s  type - %s  and - L3-l4 mode, tcam size - %s " % (node, node_type, str(size)))
                    return True
                else:
                    helpers.test_log("ERROR: Switch - %s  type - %s  and - L3-l4 mode, tcam size expect - 4088, actual - %s " % (node, node_type, str(size)))
                    return False

        else:
            if node_type == 'LB9':
                if size == 2044:
                    helpers.test_log("INFO: Switch  - %s  type - %s  and - L3-l4 mode, tcam size - %s " % (node, node_type, str(size)))
                    return True
                else:
                    helpers.test_log("ERROR: Switch - %s  type - %s  and - L3-l4 mode, tcam size expect - 4088, actual - %s " % (node, node_type, str(size)))
                    return False
            elif node_type == 'LY2':
                if size == 1020:
                    helpers.test_log("INFO: Switch  - %s  type - %s  and - L3-l4 mode, tcam size - %s " % (node, node_type, str(size)))
                    return True
                else:
                    helpers.test_log("ERROR: Switch - %s  type - %s  and - L3-l4 mode, tcam size expect - 4088, actual - %s " % (node, node_type, str(size)))
                    return False

        return True


# Mingtao
    def verify_switch_tcam_limitaion(self, node, policy, match_type='mixed', base='10.0.0.0', step='0.1.0.1', v6base='1001:0:0:0:0:0:0:0', v6step='0:0:1:0:1:0:0:0'):
        """ verify the switch tcam flow limitaion 
            Usage:  verify_switch_tcam   S203    type
                    type - 'ipv4'   'ipv6'   mixed
            return:  the tcam flow entries
            -- Mingtao
        """
        t = test.Test()
        c = t.controller('master')
        i = 0
        sequence = 0
        expect_flow = 0
        ether_type = []
        if match_type == 'ipv4':
            ether_type.extend(['2048'])
            v6Flag = None
            v4Flag = True
        elif match_type == 'ipv6':
            ether_type.extend(['34525'])
            v6Flag = True
            v4Flag = None
        else:
            ether_type.extend(['2048'])
            ether_type.extend(['34525'])
            v6Flag = True
            v4Flag = True

        for num in ['100', '20', '5', '1']:
            if v4Flag is not None:
                v4Flag = True
            if v6Flag is not None:
                v6Flag = True
            while v4Flag or v6Flag:
                i = i + 1
                g_size = int(num)
                if match_type == 'ipv4' or match_type == 'mixed' :
                    name = 'G_' + str(i) + '_' + num
                    self.rest_add_address_group(name, 'ipv4')
                    self.gen_add_address_group_entries(name, 'ipv4', base, step, '255.255.255.255', g_size)
                    base = helpers.get_next_address('ipv4', base, '5.0.0.0')
                if match_type == 'ipv6' or match_type == 'mixed' :
                    name6 = 'G6_' + str(i) + '_' + num
                    self.rest_add_address_group(name6, 'ipv6')
                    self.gen_add_address_group_entries(name6, 'ipv6', v6base, v6step, 'FFFF:FFFF:FFFF:FFFF:FFFF:FFFF:FFFF:FFFF', g_size)
                    v6base = helpers.get_next_address('ipv6', v6base, '11:0:0:0:0:0:0:0')

                for loop in range(0, 8):
                    if not v4Flag and not v6Flag:
                        helpers.log("INFO:  ********* break of of the loop *****")
                        break
                    for ether in ether_type:
                        if ether == '2048':
                            Gname = name
                            if not v4Flag:
                                continue
                        elif ether == '34525':
                            Gname = name6
                            if not v6Flag:
                                continue

                        sequence = sequence + 10
                        if loop == 0:
                            data = '{' + '"sequence":' + str(sequence) + ',' + '"src-ip-list":' + '"' + Gname + '"' + ',' + '"ether-type":' + ether + '}'
                        elif loop == 1:
                            data = '{' + '"sequence":' + str(sequence) + ',' + '"dst-ip-list":' + '"' + Gname + '"' + ',' + '"ether-type":' + ether + '}'
                        elif loop == 2:
                            data = '{' + '"sequence":' + str(sequence) + ',' + '"src-ip-list":' + '"' + Gname + '"' + ',' + '"ip-proto": 6,' + '"src-tp-port":80,' + '"ether-type":' + ether + '}'
                        elif loop == 3:
                            data = '{' + '"sequence":' + str(sequence) + ',' + '"src-ip-list":' + '"' + Gname + '"' + ',' + '"ip-proto": 6,' + '"dst-tp-port":100,' + '"ether-type":' + ether + '}'
                        elif loop == 2:
                            data = '{' + '"sequence":' + str(sequence) + ',' + '"dst-ip-list":' + '"' + Gname + '"' + ',' + '"ip-proto": 6,' + '"src-tp-port":120,' + '"ether-type":' + ether + '}'
                        elif loop == 3:
                            data = '{' + '"sequence":' + str(sequence) + ',' + '"dst-ip-list":' + '"' + Gname + '"' + ',' + '"ip-proto": 6,' + '"dst-tp-port":140,' + '"ether-type":' + ether + '}'
                        elif loop == 4:
                            data = '{' + '"sequence":' + str(sequence) + ',' + '"src-ip-list":' + '"' + Gname + '"' + ',' + '"ip-proto": 17,' + '"dst-tp-port":160,' + '"ether-type":' + ether + '}'
                        elif loop == 5:
                            data = '{' + '"sequence":' + str(sequence) + ',' + '"src-ip-list":' + '"' + Gname + '"' + ',' + '"ip-proto": 17,' + '"src-tp-port":200,' + '"ether-type":' + ether + '}'
                        elif loop == 6:
                            data = '{' + '"sequence":' + str(sequence) + ',' + '"dst-ip-list":' + '"' + Gname + '"' + ',' + '"ip-proto": 17,' + '"dst-tp-port":240,' + '"ether-type":' + ether + '}'
                        else:
                            data = '{' + '"sequence":' + str(sequence) + ',' + '"dst-ip-list":' + '"' + Gname + '"' + ',' + '"ip-proto": 17,' + '"src-tp-port":280,' + '"ether-type":' + ether + '}'


                        helpers.log("INFO:  ********* data is  %s*****" % data)
                        if not self.rest_add_policy_match('admin-view', policy, sequence, data):
                            helpers.test_failure(c.rest.error())

                        expect_flow = expect_flow + g_size

                        helpers.sleep(30)
                        flow = self.rest_show_switch_flow(node=node)
                        if flow == expect_flow:
                            helpers.test_log("INFO: Switch - %s  tcam entry - %s" % (node, str(flow)))
                        elif  flow == 0:
                            helpers.test_log("ERROR: Switch - %s  tcam expect -  %s,  actual - %s" % (node, str(expect_flow), str(flow)))
                            if not self.rest_delete_policy_match('admin-view', policy, sequence):
                                helpers.test_failure(c.rest.error())
                            expect_flow = expect_flow - g_size
                            helpers.sleep(60)
                            flow = self.rest_show_switch_flow(node=node)
                            if flow == expect_flow:
                                if ether == '2048':
                                    v4Flag = False
                                elif ether == '34525':
                                    v6Flag = False
                                helpers.test_log("INFO: ****Finished group - %s type - %s entries - %s ***" % (num, str(ether), str(expect_flow)))

                                if num == '1' and not v4Flag and not v6Flag:
                                    helpers.test_log("INFO: **** # of flows is switch  - %s ***" % str(flow))
                                    return  expect_flow
                                continue
                            else:
                                helpers.test_failure("ERROR: mismatch  Switch - %s  tcam expect -  %s,  actual - %s" % (node, str(expect_flow), str(flow)))
                        else:
                            helpers.test_log("ERROR: Switch - %s  tcam expect -  %s,  actual - %s" % (node, str(expect_flow), str(flow)))
                            helpers.test_failure("ERROR: mismatch  Switch - %s  tcam expect -  %s,  actual - %s" % (node, str(expect_flow), str(flow)))

###################################################
# All Bigtap Configuration Commands Go Here:
###################################################

    def rest_add_interface_role(self, node, intf_name, intf_type, intf_nickname=None, switch_alias=None, sw_dpid=None, rewrite_vlan=5000):
        '''
            Objective:
            - Execute the CLI command 'bigtap role filter interface-name F1'
        
            Input: 
            | `switch_dpid` |  DPID of the switch | 
            | `intf_name`    |  Interface Name viz. etherenet1, ethernet2 etc. | 
            | `intf_type`    |  Interface Type viz. filter, delivery, service | 
            | `intf_nickname` |  Nickname for the interface for eg. F1, D1, S1 etc. | 
            
            Return Value: 
            - True if configuration is successful
            - False otherwise
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('master')
            switch = t.switch(node)
            AppCommon = AppController.AppController()

            try:
                if (switch_alias is None and sw_dpid is not None):
                    switch_dpid = sw_dpid
                elif (switch_alias is None and sw_dpid is None):
                    switch_dpid = AppCommon.rest_return_switch_dpid_from_ip(node)
                elif (switch_alias is not None and sw_dpid is None):
                    switch_dpid = AppCommon.rest_return_switch_dpid_from_alias(switch_alias)
                else:
                    switch_dpid = sw_dpid

                if(intf_nickname is None):
                    if ((intf_type is "filter") or (intf_type is "Filter")):
                        intfName = intf_name
                        intfNick = str(switch.ip()).replace(".", "-") + "-F" + intfName[-2:]
                    elif ((intf_type is "delivery") or (intf_type is "Delivery")):
                        intfName = intf_name
                        intfNick = str(switch.ip()).replace(".", "-") + "-D" + intfName[-2:]
                    else:
                        intfName = intf_name
                        intfNick = str(switch.ip()).replace(".", "-") + "-S" + intfName[-2:]
                else:
                    intfNick = intf_nickname

                url = '/api/v1/data/controller/applications/bigtap/interface-config[interface="%s"][switch="%s"]' % (str(intf_name), str(switch_dpid))
                helpers.log("URL is %s" % url)
                if int(rewrite_vlan) > 4096:
                    helpers.log("Input Values are interface %s : switch %s : role %s : name %s " % (str(intf_name), str(switch_dpid), str(intf_type), str(intfNick)))
                    c.rest.put(url, {"interface": str(intf_name), "switch": str(switch_dpid), 'role':str(intf_type), 'name':str(intfNick)})
                else:
                    c.rest.put(url, {"interface": str(intf_name), "switch": str(switch_dpid), 'role':str(intf_type), 'name':str(intfNick), "rewrite-vlan": int(rewrite_vlan)})
            except:
                helpers.test_log(c.rest.error())
                return False
            else:
                helpers.test_log(c.rest.content_json())
                return True

    def rest_delete_interface_role(self, node, intf_name, intf_type, intf_nickname=None, switch_alias=None, sw_dpid=None):
        '''
            Objective:
            - Delete filter/service/delivery interface from switch configuration. 
         
            Input: 
             | `switch_dpid` | Datapath ID of the switch | 
             | `intf_name` |  Interface Name viz. etherenet1, ethernet2 etc. | 
             | `intf_type` | Interface Type viz. filter, delivery, service | 
             | `intf_nickname` | Nickname for the interface for eg. F1, D1, S1 etc. | 
                
            Description:
            - Similar to executing the CLI command 'no bigtap role filter interface-name F1'
            
            Return Value: 
            - True if configuration is successful
            - False otherwise    
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('master')
            switch = t.switch(node)
            AppCommon = AppController.AppController()
            try:
                if (switch_alias is None and sw_dpid is not None):
                    switch_dpid = sw_dpid
                elif (switch_alias is None and sw_dpid is None):
                    switch_dpid = AppCommon.rest_return_switch_dpid_from_ip(node)
                elif (switch_alias is not None and sw_dpid is None):
                    switch_dpid = AppCommon.rest_return_switch_dpid_from_alias(switch_alias)
                else:
                    switch_dpid = sw_dpid
                if(intf_nickname is None):
                    if ((intf_type is "filter") or (intf_type is "Filter")):
                        intfName = intf_name
                        intfNick = str(switch.ip()).replace(".", "-") + "-F" + intfName[-2:]
                    elif ((intf_type is "delivery") or (intf_type is "Delivery")):
                        intfName = intf_name
                        intfNick = str(switch.ip()).replace(".", "-") + "-D" + intfName[-2:]
                    else:
                        intfName = intf_name
                        intfNick = str(switch.ip()).replace(".", "-") + "-S" + intfName[-2:]
                else:
                    intfNick = intf_nickname
                url = '/api/v1/data/controller/applications/bigtap/interface-config[interface="%s"][switch="%s"]' % (str(intf_name), str(switch_dpid))
                c.rest.delete(url, {'role':str(intf_type), "name": str(intfNick)})
            except:
                helpers.test_log(c.rest.error())
                return False
            else:
                return True

    def rest_delete_interface(self, node, intf_name, switch_alias=None, sw_dpid=None):
        '''
            Objective
            - Delete interface from switch
         
            Input: 
             | `switch_dpid` | DPID of the switch | 
             | `intf_name` | Interface Name viz. etherenet1, ethernet2 etc. | 
            
            Return Value: 
            - True if configuration delete is successful
            - False otherwise       
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('master')
            switch = t.switch(node)
            AppCommon = AppController.AppController()
            try:
                if (switch_alias is None and sw_dpid is not None):
                    switch_dpid = sw_dpid
                elif (switch_alias is None and sw_dpid is None):
                    switch_dpid = AppCommon.rest_return_switch_dpid_from_ip(node)
                elif (switch_alias is not None and sw_dpid is None):
                    switch_dpid = AppCommon.rest_return_switch_dpid_from_alias(switch_alias)
                else:
                    switch_dpid = sw_dpid
                url = '/api/v1/data/controller/core/switch[dpid="%s"]/interface[name="%s"]' % (str(switch_dpid), str(intf_name))
                c.rest.delete(url, {})
            except:
                helpers.test_log(c.rest.error())
                return False
            else:
                return True

    # def rest_add_interface_group(self, group_name, group_type, rbac_view="admin-view", user="admin", password="adminadmin"):
    def rest_add_interface_group(self, group_name, group_type, rbac_view="admin-view", user="admin", password="adminadmin", version="Corsair"):
        '''
            Objective
            - Create a filter-interface-group or delivery-interface-group
            
            Input:
            | group_name | Name of Group |
            | group_type | Filter or Delivery|
            
            
            Return Value:
            - True if configuration add is successful
            - False otherwise              
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('master')
            try:
                if ("filter" in str(group_type)) or ("Filter" in str(group_type)):
                    if "Augusta" in str(version):
                        url = '/api/v1/data/controller/applications/bigtap/view[name="%s"]/filter-interface-group[name="%s"]' % (str(rbac_view), str(group_name))
                    else:
                        url = '/api/v1/data/controller/applications/bigtap/filter-interface-group[name="{}"]'.format(str(group_name))
                elif ("delivery" in str(group_type)) or  ("Delivery" in str(group_type)):
                    if "Augusta" in str(version):
                        url = '/api/v1/data/controller/applications/bigtap/view[name="%s"]/delivery-interface-group[name="%s"]' % (str(rbac_view), str(group_name))
                    else:
                        url = '/api/v1/data/controller/applications/bigtap/delivery-interface-group[name="{}"]'.format(str(group_name))
                else:
                    helpers.test_log("Invalid Group Type was assigned to variable group_type")
                    return False
                if "admin" not in user:
                    c_user = t.node_spawn(ip=c.ip(), user=str(user), password=password)
                    c_user.rest.put(url, {"name": str(group_name)})
                    c_user.close()
                else:
                    c.rest.put(url, {"name": str(group_name)})
            except:
                helpers.test_log(c.rest.error())
                return False
            else:
                return True

    def rest_delete_interface_group(self, group_name, group_type, user="admin", password="adminadmin", rbac_view="admin-view", version="Corsair"):
        '''
            Objective
            - Delete an existing filter-interface-group or delivery-interface-group
            
            Input:
            | group_name | Name of Group |
            | group_type | Filter or Delivery|
            
            
            Return Value:
            - True if configuration delete is successful
            - False otherwise              
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('master')
            try:
                if ("filter" in str(group_type)) or ("Filter" in str(group_type)):
                    if "Augusta" in str(version):
                        url = '/api/v1/data/controller/applications/bigtap/view[name="%s"]/filter-interface-group[name="%s"]' % (str(rbac_view), str(group_name))
                    else:
                        url = '/api/v1/data/controller/applications/bigtap/filter-interface-group[name="{}"]'.format(str(group_name))
                elif ("delivery" in str(group_type)) or  ("Delivery" in str(group_type)):
                    if "Augusta" in str(version):
                        url = '/api/v1/data/controller/applications/bigtap/view[name="%s"]/delivery-interface-group[name="%s"]' % (str(rbac_view), str(group_name))
                    else:
                        url = '/api/v1/data/controller/applications/bigtap/delivery-interface-group[name="{}"]'.format(str(group_name))
                else:
                    return False
                if "admin" not in user:
                    c_user = t.node_spawn(ip=c.ip(), user=str(user), password=password)
                    c_user.rest.delete(url, {})
                    c_user.close()
                else:
                    c.rest.delete(url, {})
            except:
                helpers.test_log(c.rest.error())
                return False
            else:
                return True

    # def rest_add_interface_to_interface_group(self, group_name, group_type, interface_name, , user="admin", password="adminadmin"):
    def rest_add_interface_to_interface_group(self, group_name, group_type, interface_name, user="admin", password="adminadmin", rbac_view="admin-view", version="Corsair"):
        '''
            Objective
            - Create a filter-interface-group or delivery-interface-group
            
            Input:
            | group_name | Name of Group |
            | group_type | Filter or Delivery|
            | interface_name | Name of interface being added to interface-group |
            
            
            Return Value:
            - True if configuration add is successful
            - False otherwise              
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('master')
            try:
                if ("filter" in str(group_type)) or ("Filter" in str(group_type)):
                    if "Augusta" in str(version):
                        url = '/api/v1/data/controller/applications/bigtap/view[name="%s"]/filter-interface-group[name="%s"]/filter-group[name="%s"]' % (str(rbac_view), str(group_name), str(interface_name))
                    else:
                        url = '/api/v1/data/controller/applications/bigtap/filter-interface-group[name="{}"]/filter-group[name="{}"]'.format(str(group_name), str(interface_name))
                elif ("delivery" in str(group_type)) or  ("Delivery" in str(group_type)):
                    if "Augusta" in str(version):
                        url = '/api/v1/data/controller/applications/bigtap/view[name="%s"]/delivery-interface-group[name="%s"]/delivery-group[name="%s"]' % (str(rbac_view), str(group_name), str(interface_name))
                    else:
                        url = '/api/v1/data/controller/applications/bigtap/delivery-interface-group[name="{}"]/delivery-group[name="{}"]'.format(str(group_name), str(interface_name))
                else:
                    return False
                if "admin" not in user:
                    c_user = t.node_spawn(ip=c.ip(), user=str(user), password=password)
                    c_user.rest.put(url, {"name": str(interface_name)})
                    c_user.close()
                else:
                    c.rest.put(url, {"name": str(interface_name)})
            except:
                helpers.test_log(c.rest.error())
                return False
            else:
                return True

    # def rest_delete_interface_from_interface_group(self, group_name, group_type, interface_name, rbac_view="admin-view", user="admin", password="adminadmin"):
    def rest_delete_interface_from_interface_group(self, group_name, group_type, interface_name, user="admin", password="adminadmin", rbac_view="admin-view", version="Corsair"):
        '''
            Objective
            - Delete a interface from an interface group
            
            Input:
            | group_name | Name of Group |
            | group_type | Filter or Delivery|
            | interface_name | Name of interface being added to interface-group |
            
            
            Return Value:
            - True if configuration add is successful
            - False otherwise              
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('master')
            try:
                if ("filter" in str(group_type)) or ("Filter" in str(group_type)):
                    if "Augusta" in str(version):
                        url = '/api/v1/data/controller/applications/bigtap/view[name="%s"]/filter-interface-group[name="%s"]/filter-group[name="%s"]' % (str(rbac_view), str(group_name), str(interface_name))
                    else:
                        url = '/api/v1/data/controller/applications/bigtap/filter-interface-group[name="{}"]/filter-group[name="{}"]'.format(str(group_name), str(interface_name))
                elif ("delivery" in str(group_type)) or  ("Delivery" in str(group_type)):
                    if "Augusta" in str(version):
                        url = '/api/v1/data/controller/applications/bigtap/view[name="%s"]/delivery-interface-group[name="%s"]/delivery-group[name="%s"]' % (str(rbac_view), str(group_name), str(interface_name))
                    else:
                        url = '/api/v1/data/controller/applications/bigtap/delivery-interface-group[name="{}"]/delivery-group[name="{}"]'.format(str(group_name), str(interface_name))
                else:
                    return False
                if "admin" not in user:
                    c_user = t.node_spawn(ip=c.ip(), user=str(user), password=password)
                    c_user.rest.delete(url, {})
                    c_user.close()
                else:
                    c.rest.delete(url, {})
            except:
                helpers.test_log(c.rest.error())
                return False
            else:
                return True

    def rest_add_interface_group_to_policy(self, policy_name, group_name, group_type, rbac_view="admin-view", user="admin", password="adminadmin", version="Corsair"):
        '''
            Objective
            - Add filter-interface-group or delivery-interface-group to policy
            
            Input:
            | policy_name | Name of policy to which group is added|
            | group_name | Name of Group |
            | group_type | Filter or Delivery|

            
            
            Return Value:
            - True if configuration add is successful
            - False otherwise              
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('master')
            try:

                #
                if ("filter" in str(group_type)) or ("Filter" in str(group_type)):
                    if "Augusta" in str(version):
                        url = '/api/v1/data/controller/applications/bigtap/view[name="%s"]/policy[name="%s"]' % (str(rbac_view), str(policy_name))
                        # data = {"filter-intf-group": str(group_name)}
                    else:
                        url = '/api/v1/data/controller/applications/bigtap/view[name="%s"]/policy[name="%s"]/filter-intf-group[name="%s"]' % (str(rbac_view), str(policy_name), str(group_name))
                    data = {"name": str(group_name)}
                elif ("delivery" in str(group_type)) or  ("Delivery" in str(group_type)):
                    if "Augusta" in str(version):
                        url = '/api/v1/data/controller/applications/bigtap/view[name="%s"]/policy[name="%s"]' % (str(rbac_view), str(policy_name))
                        # data = {"delivery-intf-group": str(group_name)}
                    else:
                        url = '/api/v1/data/controller/applications/bigtap/view[name="%s"]/policy[name="%s"]/delivery-intf-group[name="%s"]' % (str(rbac_view), str(policy_name), str(group_name))
                    data = {"name": str(group_name)}
                else:
                    return False
                if "admin" not in user:
                    c_user = t.node_spawn(ip=c.ip(), user=str(user), password=password)
                    c_user.rest.put(url, data)
                    c_user.close()
                else:
                    # c.rest.patch(url, data)
                    c.rest.put(url, data)
            except:
                helpers.test_log(c.rest.error())
                return False
            else:
                return True

    def rest_delete_interface_group_from_policy(self, policy_name, group_name, group_type, rbac_view="admin-view", user="admin", password="adminadmin", version="Corsair"):
        '''
            Objective
            - Delete filter-interface-group or delivery-interface-group to policy
            
            Input:
            | policy_name | Name of policy to which group is added|
            | group_name | Name of Group |
            | group_type | Filter or Delivery|

            
            
            Return Value:
            - True if configuration add is successful
            - False otherwise              
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('master')
            try:

                if ("filter" in str(group_type)) or ("Filter" in str(group_type)):
                    url = '/api/v1/data/controller/applications/bigtap/view[name="%s"]/policy[name="%s"][filter-intf-group="None"]/filter-intf-group' % (str(rbac_view), str(policy_name))
                elif ("delivery" in str(group_type)) or  ("Delivery" in str(group_type)):
                    url = '/api/v1/data/controller/applications/bigtap/view[name="%s"]/policy[name="%s"][delivery-intf-group="None"]/delivery-intf-group' % (str(rbac_view), str(policy_name))
                else:
                    return False
                if "admin" not in user:
                    c_user = t.node_spawn(ip=c.ip(), user=str(user), password=password)
                    c_user.rest.delete(url, {})
                    c_user.close()
                else:
                    c.rest.delete(url, {})
            except:
                helpers.test_log(c.rest.error())
                return False
            else:
                return True

    def rest_add_policy(self, rbac_view_name, policy_name, policy_action="inactive", user="admin", password="adminadmin"):
        '''
            Objective:
            - Add a bigtap policy.
        
            Input:
             | rbac_view_name` | RBAC View Name for eg. admin-view | 
             | `policy_name` | Policy Name | 
             | `policy_action` | Policy action. The permitted values are "forward" or "rate-measure", default is inactive | 
            
            Return Value: 
            - True if configuration is successful
            - False otherwise       
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('master')
            try:
                url = '/api/v1/data/controller/applications/bigtap/view[name="%s"]/policy[name="%s"]' % (str(rbac_view_name), str(policy_name))
                if "admin" not in user:
                    c_user = t.node_spawn(ip=c.ip(), user=str(user), password=password)
                    c_user.rest.put(url, {'name':str(policy_name)})
                    c_user.close()
                else:
                    c.rest.put(url, {'name':str(policy_name)})
            except:
                helpers.test_log(c.rest.error())
                return False
            else:
                try:
                    if "admin" not in user:
                        c_user = t.node_spawn(ip=c.ip(), user=str(user), password=password)
                        c_user.rest.patch(url, {"action":str(policy_action)})
                        c_user.close()
                    else:
                        c.rest.patch(url, {"action":str(policy_action)})
                except:
                    helpers.test_log(c.rest.error())
                    return False
                else:
                    return True

    def rest_delete_policy(self, rbac_view_name, policy_name, user="admin", password="adminadmin"):
        '''
            Objective:
            - Delete a bigtap policy.
        
            Input:
             | `rbac_view_name` | RBAC View Name for eg. admin-view | 
             | `policy_name` | Policy Name | 
            
            Return Value: 
            - True if configuration delete is successful
            - False if configuration delete is unsuccessful          
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('master')
            try:
                url = '/api/v1/data/controller/applications/bigtap/view[name="%s"]/policy[name="%s"]' % (str(rbac_view_name), str(policy_name))
                if "admin" not in user:
                    c_user = t.node_spawn(ip=c.ip(), user=str(user), password=password)
                    c_user.rest.delete(url, {})
                    c_user.close()
                else:
                    c.rest.delete(url, {})
            except:
                helpers.test_log(c.rest.error())
                return False
            else:
                return True

    def rest_update_policy_priority(self, rbac_view_name, policy_name, policy_priority=100):
        '''
            Objective:
            - Update bigtap policy priority. Default value is 100.
        
            Input:
             | `rbac_view_name` | RBAC View Name for eg. admin-view | 
             | `policy_name` | Policy Name | 
             | policy_priority| New priority value|
            
            Return Value: 
            - True if configuration delete is successful
            - False if configuration delete is unsuccessful          
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('master')
            try:
                url = '/api/v1/data/controller/applications/bigtap/view[name="%s"]/policy[name="%s"]' % (str(rbac_view_name), str(policy_name))
                c.rest.patch(url, {"priority": int(policy_priority)})
            except:
                helpers.test_log(c.rest.error())
                return False
            else:
                return True

    def rest_add_timed_policy(self, rbac_view_name, policy_name, duration, starttime, pktcount):
        '''
            Objective:
            - Update bigtap policy with start time, duration etc.
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('master')
            try:
                if "+" in starttime:
                    url = '/api/v1/data/controller/applications/bigtap/view[name="%s"]/policy[name="%s"]' % (str(rbac_view_name), str(policy_name))
                    sttime = starttime[:-1]
                    helpers.log("Passed from .txt file %s" % str(sttime))
                    stime = int(time.time() + int(sttime))
                    helpers.log("STIME is %d" % int(stime))
                    c.rest.patch(url, {"start-time": int(stime) , "delivery-packet-count": int(pktcount), "duration": int(duration)})
                elif "now" in starttime:
                    unixTime = int(time.time())
                    url = '/api/v1/data/controller/applications/bigtap/view[name="%s"]/policy[name="%s"]' % (str(rbac_view_name), str(policy_name))
                    c.rest.patch(url, {"start-time": unixTime, "delivery-packet-count": int(pktcount), "duration": int(duration)})
                elif ("T" in starttime) and (":" in starttime) and ("-" in starttime):
                    UT = datetime.strptime(starttime, '%Y-%m-%dT%H:%M:%S')
                    unixTime = int(mktime(UT.timetuple()))
                    url = '/api/v1/data/controller/applications/bigtap/view[name="%s"]/policy[name="%s"]' % (str(rbac_view_name), str(policy_name))
                    c.rest.patch(url, {"start-time": int(unixTime), "delivery-packet-count": int(pktcount), "duration": int(duration)})
                elif ("stop" in starttime):
                    url = '/api/v1/data/controller/applications/bigtap/view[name="%s"]/policy[name="%s"]' % (str(rbac_view_name), str(policy_name))
                    c.rest.patch(url, {"duration": 1, "start-time": 0, "delivery-packet-count": 0})
                else:
                    helpers.log("IN HERE")
                    UT = datetime.strptime(starttime, '%Y-%m-%d %H:%M:%S')
                    unixTime = int(mktime(UT.timetuple()))
                    url = '/api/v1/data/controller/applications/bigtap/view[name="%s"]/policy[name="%s"]' % (str(rbac_view_name), str(policy_name))
                    c.rest.patch(url, {"start-time": int(unixTime), "delivery-packet-count": int(pktcount), "duration": int(duration)})
            except:
                helpers.test_log(c.rest.error())
                return False
            else:
                return True

    def rest_add_vlan_rewrite(self, rbac_view_name, policy_name, rewrite_vlan):
        '''
            Objective:
            - Update bigtap policy priority. Default value is 100.
        
            Input:
             | `rbac_view_name` | RBAC View Name for eg. admin-view | 
             | `policy_name` | Policy Name | 
             | policy_priority| New priority value|
            
            Return Value: 
            - True if configuration delete is successful
            - False if configuration delete is unsuccessful          
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('master')
            try:
                url = '/api/v1/data/controller/applications/bigtap/view[name="%s"]/policy[name="%s"]' % (str(rbac_view_name), str(policy_name))
                c.rest.patch(url, {"rewrite-vlan": int(rewrite_vlan)})
            except:
                helpers.test_log(c.rest.error())
                return False
            else:
                return True

    def rest_delete_vlan_rewrite(self, rbac_view_name, policy_name, rewrite_vlan):
        '''
            Objective:
            - Update bigtap policy priority. Default value is 100.
        
            Input:
             | `rbac_view_name` | RBAC View Name for eg. admin-view | 
             | `policy_name` | Policy Name | 
             | policy_priority| New priority value|
            
            Return Value: 
            - True if configuration delete is successful
            - False if configuration delete is unsuccessful          
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('master')
            try:
                url = '/api/v1/data/controller/applications/bigtap/view[name="%s"]/policy[name="%s"][rewrite-vlan=None]/rewrite-vlan' % (str(rbac_view_name), str(policy_name))
                c.rest.delete(url, {})
            except:
                helpers.test_log(c.rest.error())
                return False
            else:
                return True

    def rest_add_policy_interface(self, rbac_view_name, policy_name, intf_nickname, intf_type, user="admin", password="adminadmin"):
        '''
            Objective:
            - Add a bigtap policy interface viz. Add a filter-interface and/or delivery-interface under a bigtap policy.
        
            Input:
             | `rbac_view_name` |   RBAC View Name for eg. admin-view| 
             | `policy_name` |  Policy Name| 
             | `intf_nickname` |  Interface Nick-Name for eg. F1 or D1 | 
             | `intf_type` |  Interface Type. Allowed values are `filter` or `delivery` | 
            
            Return Value: 
            - True if configuration delete is successful
            - False if configuration delete is unsuccessful     
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('master')
            try:
                if "filter" in str(intf_type):
                    intf_type = "filter-group"
                else:
                    intf_type = "delivery-group"
                url = '/api/v1/data/controller/applications/bigtap/view[name="%s"]/policy[name="%s"]/%s[name="%s"]' % (str(rbac_view_name), str(policy_name), str(intf_type), str(intf_nickname))
                if "admin" not in user:
                    c_user = t.node_spawn(ip=c.ip(), user=str(user), password=password)
                    c_user.rest.put(url, {"name": str(intf_nickname)})
                    c_user.close()
                else:
                    c.rest.put(url, {"name": str(intf_nickname)})
            except:
                helpers.test_log(c.rest.error())
                return False
            else:
                return True

    def rest_delete_policy_interface(self, rbac_view_name, policy_name, intf_nickname, intf_type, user="admin", password="adminadmin"):
        '''
            Objective:
            - Delete a bigtap policy interface viz. 
            - Delete a filter-interface and/or delivery-interface from a bigtap policy.
        
            Input:
            | `rbac_view_name` | RBAC View Name for eg. admin-view | 
            | `policy_name` | Policy Name | 
            | `intf_nickname` | Interface Nick-Name for eg. F1 or D1 | 
            | `intf_type` | Interface Type. Allowed values are `filter` or `delivery` | 
            
            Return Value: 
            - True if configuration delete is successful
            - False if configuration delete is unsuccessful    
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('master')
            try:
                if "filter" in str(intf_type):
                    intf_type = "filter-group"
                else:
                    intf_type = "delivery-group"
                url = '/api/v1/data/controller/applications/bigtap/view[name="%s"]/policy[name="%s"]/%s[name="%s"]' % (str(rbac_view_name), str(policy_name), str(intf_type), str(intf_nickname))
                if "admin" not in user:
                    c_user = t.node_spawn(ip=c.ip(), user=str(user), password=password)
                    c_user.rest.delete(url, {})
                    c_user.close()
                else:
                    c.rest.delete(url, {})
            except:
                helpers.test_log(c.rest.error())
                return False
            else:
                return True

    def rest_add_policy_match(self, rbac_view_name, policy_name, match_number, data, flag=False, user="admin", password="adminadmin"):
        '''
            Objective:
            - Add a bigtap policy match condition.
        
            Input:
            | `rbac_view_name`| RBAC View Name for eg. admin-view | 
            | `policy_name` | Policy Name | 
            | `match_number` |  Match number like the '1' in  '1 match tcp | 
            | `data` | Formatted data field like  {"ether-type": 2048, "dst-tp-port": 80, "ip-proto": 6, "sequence": 1} | 
            
            Return Value: 
            - True if configuration add is successful
            - False if configuration add is unsuccessful         
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('master')
            try:
                helpers.log("Input data is %s" % data)
                url = '/api/v1/data/controller/applications/bigtap/view[name="%s"]/policy[name="%s"]/rule[sequence=%s]' % (str(rbac_view_name), str(policy_name), str(match_number))
                if not flag:
                    data_dict = helpers.from_json(data)
                else:
                    data_dict = data
                helpers.log("Input dictionary is %s" % data_dict)
                if "admin" not in user:
                    c_user = t.node_spawn(ip=c.ip(), user=str(user), password=password)
                    c_user.rest.put(url, data_dict)
                    c_user.close()
                else:
                    c.rest.put(url, data_dict)
            except:
                return False
            else:
                return True

    def rest_delete_policy_match(self, rbac_view_name, policy_name, match_number, user="admin", password="adminadmin"):
        '''
            Objective:
            - Delete a bigtap policy match condition.
        
            Input:
            | `rbac_view_name` |  RBAC View Name for eg. admin-view | 
            | `policy_name` | Policy Name | 
            | `match_number` |  Match number like the '1' in  '1 match tcp | 
            
            Return Value: 
            - True if configuration delete is successful
            - False if configuration delete is unsuccessful         
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('master')
            try:
                url = '/api/v1/data/controller/applications/bigtap/view[name="%s"]/policy[name="%s"]/rule[sequence=%s]' % (str(rbac_view_name), str(policy_name), str(match_number))
                if "admin" not in user:
                    c_user = t.node_spawn(ip=c.ip(), user=str(user), password=password)
                    c_user.rest.delete(url, {})
                    c_user.close()
                else:
                    c.rest.delete(url, {})
            except:
                helpers.test_log(c.rest.error())
                return False
            else:
                return True

# Add a bigtap filter-set
    def rest_add_filter_set(self, filter_set_name, rbac_view_name="admin-view", user="admin", password="adminadmin"):
        '''
            Objective:
            - Add a filter set.
        
            Input:
            | `filter_set_name`| Name of filter set | 
            | `rbac_view_name`| Name of RBAC View. Default is admin-view | 
            
            Return Value: 
            - True if configuration add is successful
            - False if configuration add is unsuccessful  
        
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('master')
            try:
                url = '/api/v1/data/controller/applications/bigtap/filter-set[name="%s"]' % (str(filter_set_name))
                if "admin" not in user:
                    c_user = t.node_spawn(ip=c.ip(), user=str(user), password=password)
                    c_user.rest.put(url, {"name": str(filter_set_name)})
                    c_user.close()
                else:
                    c.rest.put(url, {"name": str(filter_set_name)})
            except:
                helpers.test_log(c.rest.error())
                return False
            else:
                return True

# delete a bigtap filter-set
    def rest_delete_filter_set(self, filter_set_name, rbac_view_name="admin-view", user="admin", password="adminadmin"):
        '''
            Objective:
            - Add a filter set.
        
            Input:
            | `filter_set_name`| Name of filter set | 
            | `rbac_view_name`| Name of RBAC View. Default is admin-view | 
            
            Return Value: 
            - True if configuration add is successful
            - False if configuration add is unsuccessful  
        
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('master')
            try:
                url = '/api/v1/data/controller/applications/bigtap/filter-set[name="%s"]' % (str(filter_set_name))
                if "admin" not in user:
                    c_user = t.node_spawn(ip=c.ip(), user=str(user), password=password)
                    c_user.rest.delete(url, {})
                    c_user.close()
                else:
                    c.rest.delete(url, {})
            except:
                helpers.test_log(c.rest.error())
                return False
            else:
                return True

# Add match condition to filter set
    def rest_add_match_to_filter_set(self, filter_set_name, match_number, data, rbac_view_name="admin-view", user="admin", password="adminadmin"):
        '''
            Objective:
            - Add a bigtap match condition to a filtet set
        
            Input:
            | `filter_set_name` | Name of filter set | 
            | `match_number` |  Match number like the '1' in  '1 match tcp | 
            | `data` | Formatted data field like  {"ether-type": 2048, "dst-tp-port": 80, "ip-proto": 6, "sequence": 1} | 
            | `rbac_view_name`| RBAC View Name for eg. admin-view | 
            
            Return Value: 
            - True if configuration add is successful
            - False if configuration add is unsuccessful         
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('master')
            try:
                helpers.log("Input data is %s" % data)
                url = '/api/v1/data/controller/applications/bigtap/filter-set[name="%s"]/rule[sequence=%s]' % (str(filter_set_name), str(match_number))
                data_dict = helpers.from_json(data)
                if "admin" not in user:
                    c_user = t.node_spawn(ip=c.ip(), user=str(user), password=password)
                    c_user.rest.put(url, data_dict)
                    c_user.close()
                else:
                    c.rest.put(url, data_dict)
            except:
                return False
            else:
                return True

# Delete a match condition to filter set
    def rest_delete_match_from_filter_set(self, filter_set_name, match_number, rbac_view_name="admin-view", user="admin", password="adminadmin"):
        '''
            Objective:
            - Add a bigtap match condition to a filtet set
        
            Input:
            | `filter_set_name` | Name of filter set | 
            | `match_number` |  Match number like the '1' in  '1 match tcp | 
            | `data` | Formatted data field like  {"ether-type": 2048, "dst-tp-port": 80, "ip-proto": 6, "sequence": 1} | 
            | `rbac_view_name`| RBAC View Name for eg. admin-view | 
            
            Return Value: 
            - True if configuration add is successful
            - False if configuration add is unsuccessful         
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('master')
            try:
                url = '/api/v1/data/controller/applications/bigtap/filter-set[name="%s"]/rule[sequence=%s]' % (str(filter_set_name), str(match_number))
                if "admin" not in user:
                    c_user = t.node_spawn(ip=c.ip(), user=str(user), password=password)
                    c_user.rest.delete(url, {})
                    c_user.close()
                else:
                    c.rest.delete(url, {})
            except:
                return False
            else:
                return True

# Add filter-set to policy
    def rest_add_filterset_to_policy(self, policy_name, filter_set_name, match_number, rbac_view_name="admin-view", user="admin", password="adminadmin"):
        '''
            Objective:
            - Add a bigtap match condition to a filtet set
        
            Input:
            | `policy_name` |  Name of policy  |
            | `filter_set_name` | Name of filter set | 
            | `match_number` |  Match number like the '1' in  '1 match tcp | 
            | `rbac_view_name`| RBAC View Name for eg. admin-view | 
            
            Return Value: 
            - True if configuration add is successful
            - False if configuration add is unsuccessful         
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('master')
            try:
                url = '/api/v1/data/controller/applications/bigtap/view[name="%s"]/policy[name="%s"]/rule[sequence=%s]' % (str(rbac_view_name), str(policy_name), str(match_number))
                if "admin" not in user:
                    c_user = t.node_spawn(ip=c.ip(), user=str(user), password=password)
                    c_user.rest.put(url, {"filter-set-name": str(filter_set_name), "sequence": int(match_number)})
                    c_user.close()
                else:
                    c.rest.put(url, {"filter-set-name": str(filter_set_name), "sequence": int(match_number)})
            except:
                return False
            else:
                return True

# Delete filter-set from policy
    def rest_delete_filterset_from_policy(self, policy_name, filter_set_name, match_number, rbac_view_name="admin-view", user="admin", password="adminadmin"):
        '''
            Objective:
            - Add a bigtap match condition to a filtet set
        
            Input:
            | `policy_name` |  Name of policy  |
            | `filter_set_name` | Name of filter set | 
            | `match_number` |  Match number like the '1' in  '1 match tcp | 
            | `rbac_view_name`| RBAC View Name for eg. admin-view | 
            
            Return Value: 
            - True if configuration add is successful
            - False if configuration add is unsuccessful         
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('master')
            try:
                url = '/api/v1/data/controller/applications/bigtap/view[name="%s"]/policy[name="%s"]/rule[sequence=%s]' % (str(rbac_view_name), str(policy_name), str(match_number))
                if "admin" not in user:
                    c_user = t.node_spawn(ip=c.ip(), user=str(user), password=password)
                    c_user.rest.delete(url, {"filter-set-name": str(filter_set_name)})
                    c_user.close()
                else:
                    c.rest.delete(url, {"filter-set-name": str(filter_set_name)})
            except:
                return False
            else:
                return True



# Add strip-vlan
    def rest_add_stripvlan_to_policy(self, policy_name, rbac_view_name="admin-view", user="admin", password="adminadmin"):
        '''
            Objective:
            - Strip Vlan from incoming traffic that matches policy.
        
            Input:
            | `policy_name`| Name of Policy | 
            | `rbac_view_name`| Name of RBAC View. Default is admin-view | 
            
            Return Value: 
            - True if configuration add is successful
            - False if configuration add is unsuccessful  
        
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('master')
            try:
                url = '/api/v1/data/controller/applications/bigtap/view[name="%s"]/policy[name="%s"]' % (str(rbac_view_name), str(policy_name))
                if "admin" not in user:
                    c_user = t.node_spawn(ip=c.ip(), user=str(user), password=password)
                    c_user.rest.patch(url, {"strip-vlan": True})
                    c_user.close()
                else:
                    c.rest.patch(url, {"strip-vlan": True})
            except:
                helpers.test_log(c.rest.error())
                return False
            else:
                return True

# Add strip-vlan
    def rest_delete_stripvlan_from_policy(self, policy_name, rbac_view_name="admin-view", user="admin", password="adminadmin"):
        '''
            Objective:
            - Stop removing Vlans from incoming traffic that matches policy.
        
            Input:
            | `policy_name`| Name of Policy | 
            | `rbac_view_name`| Name of RBAC View. Default is admin-view | 
            
            Return Value: 
            - True if configuration add is successful
            - False if configuration add is unsuccessful  
        
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('master')
            try:
                url = '/api/v1/data/controller/applications/bigtap/view[name="%s"]/policy[name="%s"][strip-vlan="None"]/strip-vlan' % (str(rbac_view_name), str(policy_name))
                if "admin" not in user:
                    c_user = t.node_spawn(ip=c.ip(), user=str(user), password=password)
                    c_user.rest.delete(url, {})
                    c_user.close()
                else:
                    c.rest.delete(url, {})
            except:
                helpers.test_log(c.rest.error())
                return False
            else:
                return True

# Add a service with Pre-Service and Post Service interface.
    def rest_add_service(self, service_name, pre_service_intf_nickname, post_service_intf_nickname, user="admin", password="adminadmin"):
        '''
            Objective:
            - Add a bigtap service.
        
            Input:
            | `service_name`| Name of Service | 
            | `pre_service_intf_nickname`| Name of pre-service interface | 
            | `post_service_intf_nickname`| Name of post-service interface | 
            
            Return Value: 
            - True if configuration add is successful
            - False if configuration add is unsuccessful  
        
            Examples:
                | rest add bigtap service  |  S1-LB7  |  S1-LB7_E3-HP1_E3-PRE  |  S1-LB7_E4-HP1_E4-POST  |  
                Result is 
                bigtap service S1-LB7
                  post-service S1-LB7_E4-HP1_E4-POST
                  pre-service S1-LB7_E3-HP1_E3-PRE
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('master')
            try:
                url = '/api/v1/data/controller/applications/bigtap/service[name="%s"]' % (str(service_name))
                c.rest.put(url, {"name":str(service_name)})
            except:
                helpers.test_log(c.rest.error())
                return False
            else:
                try:
                    # Add Pre-Service Interface
                    url_add_intf = '/api/v1/data/controller/applications/bigtap/service[name="%s"]/pre-group[name="%s"]' % (str(service_name), str(pre_service_intf_nickname))
                    if "admin" not in user:
                        c_user = t.node_spawn(ip=c.ip(), user=str(user), password=password)
                        c_user.rest.put(url_add_intf, {"name":str(pre_service_intf_nickname)})
                        c_user.close()
                    else:
                        c.rest.put(url_add_intf, {"name":str(pre_service_intf_nickname)})
                except:
                    helpers.test_log(c.rest.error())
                    return False
                else:
                    try:
                        # Add Post-Service Interface
                        url_add_intf = '/api/v1/data/controller/applications/bigtap/service[name="%s"]/post-group[name="%s"]' % (str(service_name), str(post_service_intf_nickname))
                        if "admin" not in user:
                            c_user = t.node_spawn(ip=c.ip(), user=str(user), password=password)
                            c_user.rest.put(url_add_intf, {"name":str(post_service_intf_nickname)})
                            c_user.close()
                        else:
                            c.rest.put(url_add_intf, {"name":str(post_service_intf_nickname)})
                    except:
                        helpers.test_log(c.rest.error())
                        return False
                    else:
                        helpers.test_log(c.rest.content_json())
                        return True

# Delete a service
    def rest_delete_service(self, service_name, user="admin", password="adminadmin"):
        '''
            Objective:
            - Delete a bigtap service.
        
            Input:
            | `service_name` | Name of Service |
            
            Return Value: 
            - True if configuration delete is successful
            - False if configuration delete is unsuccessful  
        
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('master')
            try:
                url = '/api/v1/data/controller/applications/bigtap/service[name="%s"]' % (str(service_name))
                if "admin" not in user:
                    c_user = t.node_spawn(ip=c.ip(), user=str(user), password=password)
                    c_user.rest.delete(url, {})
                    c_user.close()
                else:
                    c.rest.delete(url, {})
            except:
                helpers.test_log(c.rest.error())
                return False
            else:
                return True

    def rest_add_interface_service(self, service_name, intf_type, intf_nickname, user="admin", password="adminadmin"):
        '''
            Objective:
            - Add a service interface to a service. 
            - This is similar to executing CLI command "post-service S1-LB7_E4-HP1_E4-POST"
        
            Input:
            | `service_name` | Name of Service |
            | `intf_type`  | Interface Type. Acceptable values are `pre` or `post` |
            | `post_service_intf_nickname` | Name of pre/post-service interface for e.g. S1-LB7_E4-HP1_E4-POST |
            
            Return Value: 
            - True if configuration add is successful
            - False if configuration add is unsuccessful  
        
            Examples:
                | rest add interface service  |  S1-LB7  |  post  |  S1-LB7_E4-HP1_E4-POST  |  
                Result is 
                bigtap service S1-LB7
                  post-service S1-LB7_E4-HP1_E4-POST
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('master')
            try:
                if "pre" in str(intf_type):
                    url_add_intf = '/api/v1/data/controller/applications/bigtap/service[name="%s"]/pre-group[name="%s"]' % (str(service_name), str(intf_nickname))
                else:
                    url_add_intf = '/api/v1/data/controller/applications/bigtap/service[name="%s"]/post-group[name="%s"]' % (str(service_name), str(intf_nickname))
                if "admin" not in user:
                    c_user = t.node_spawn(ip=c.ip(), user=str(user), password=password)
                    c_user.rest.post(url_add_intf, {"name":str(intf_nickname)})
                    c_user.close()
                else:
                    c.rest.post(url_add_intf, {"name":str(intf_nickname)})
            except:
                helpers.test_log(c.rest.error())
                return False
            else:
                return True

    def rest_delete_interface_service(self, service_name, intf_nickname, intf_type, user="admin", password="adminadmin"):
        '''
            Objective:
            - Delete an interface from a service. This is similar to executing CLI command "no post-service S1-LB7_E4-HP1_E4-POST"
        
            Input:
            | `service_name` | Name of Service |
            | `intf_type` | Interface Type. Acceptable values are `pre` or `post` |
            | `post_service_intf_nickname` | Name of pre/post-service interface for e.g. S1-LB7_E4-HP1_E4-POST |
            
            Return Value: 
            - True if configuration add is successful
            - False if configuration add is unsuccessful  
        
            Examples:
                | rest delete interface service  |  S1-LB7  |  post  |  S1-LB7_E4-HP1_E4-POST  |  
                Result is 
                bigtap service S1-LB7
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('master')
            try:
                if "pre" in str(intf_type):
                    url_add_intf = '/api/v1/data/controller/applications/bigtap/service[name="%s"]/pre-group[name="%s"]' % (str(service_name), str(intf_nickname))
                else:
                    url_add_intf = '/api/v1/data/controller/applications/bigtap/service[name="%s"]/post-group[name="%s"]' % (str(service_name), str(intf_nickname))
                if "admin" not in user:
                    c_user = t.node_spawn(ip=c.ip(), user=str(user), password=password)
                    c_user.rest.delete(url_add_intf, {})
                    c_user.close()
                else:
                    c.rest.delete(url_add_intf, {})
            except:
                helpers.test_log(c.rest.error())
                return False
            else:
                return True

    def rest_add_service_to_policy(self, rbac_view_name, policy_name, service_name, sequence_number, optional=False, user="admin", password="adminadmin"):
        '''
          Objective:
          - Add a service to a policy. This is similar to executing CLI command "use-service S1-LB7 sequence 1"
        
          Input:
            |`rbac_view_name` | RBAC View Name for eg. admin-view |
            |`policy_name` | Policy Name |
            |`service_name` | Name of Service |
            |`sequence_number`| Sequence number of the policy, to determine order in which policies are processed |
            
          Return Value:
            - True if action add for policy is successful
            - False if action add for policy is unsuccessful
        
          Examples:
                | rest add service to policy  |  admin-view  |  testPolicy  |  S1-LB7  |  1  |  
                Result is 
                bigtap policy testPolicy rbac-permission admin-view
                    ...
                    ...
                    ...
                    use-service S1-LB7 sequence 1
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('master')
            try:
                url_to_add = '/api/v1/data/controller/applications/bigtap/view[name="%s"]/policy[name="%s"]/service[sequence=%s]' % (str(rbac_view_name), str(policy_name), str(sequence_number))
                if "admin" not in user:
                    c_user = t.node_spawn(ip=c.ip(), user=str(user), password=password)
                    c_user.rest.put(url_to_add, {"optional": bool(optional), "name":str(service_name), "sequence": int(sequence_number)})
                    c_user.close()
                else:
                    c.rest.put(url_to_add, {"optional": bool(optional), "name":str(service_name), "sequence": int(sequence_number)})
            except:
                helpers.test_log(c.rest.error())
                return False
            else:
                return True

    def rest_delete_service_from_policy(self, rbac_view_name, policy_name, service_name, user="admin", password="adminadmin"):
        '''
            Objective:
            - Delete a service from a policy. This is similar to executing CLI command "no use-service S1-LB7 sequence 1"
        
            Input:
            |`rbac_view_name`| RBAC View Name for eg. admin-view |
            |`policy_name` | Policy Name |
            |`service_name` | Name of Service |
            
            Return Value:
            - True if action delete for policy is successful
            - False if action delete for policy is unsuccessful
        
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('master')
            try:
                url = '/api/v1/data/controller/applications/bigtap/view[name="%s"]/policy[name="%s"]/service[name="%s"]' % (str(rbac_view_name), str(policy_name), str(service_name))
                if "admin" not in user:
                    c_user = t.node_spawn(ip=c.ip(), user=str(user), password=password)
                    c_user.rest.delete(url, {})
                    c_user.close()
                else:
                    c.rest.delete(url, {})
            except:
                helpers.test_log(c.rest.error())
                return False
            else:
                return True

# Change policy action
    def rest_add_policy_action(self, rbac_view_name, policy_name, policy_action, user="admin", password="adminadmin"):
        '''
          Objective:
          - Change the action field in a bigtap policy
        
          Input:
           |`rbac_view_name`|RBAC View Name for eg. admin-view |    
           |`policy_name`|Policy Name |
           |`policy_action`|Desired action. Values are `forward`, `rate-measure` and `inactive` |

          
          Description: 
          Change a bigtap policy action from 
          - Forward --> Rate-Measure, 
          - Forward --> Inactive, 
          - Rate-Measure--> Forward, 
          - Rate-Measure--> Inactive
          
          Return Value:
            - True if action change for policy is successful
            - False if action change for policy is unsuccessful

          Examples:
                | rest change policy action  |  admin-view  |  testPolicy  |  rate-measure |  
                Result is 
                bigtap policy testPolicy rbac-permission admin-view
                    action rate-measure
                    ...
                    ...
                    ...
        
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('master')
            try:
                url = '/api/v1/data/controller/applications/bigtap/view[name="%s"]/policy[name="%s"]' % (str(rbac_view_name), str(policy_name))
                if "admin" not in user:
                    c_user = t.node_spawn(ip=c.ip(), user=str(user), password=password)
                    c_user.rest.delete(url, {})
                    c_user.close()
                else:
                    c.rest.patch(url, {"action":str(policy_action)})
            except:
                helpers.test_log(c.rest.error())
                return False
            else:
                return True

# Alias
    def rest_update_policy_action(self, rbac_view_name, policy_name, policy_action, user="admin", password="adminadmin"):
        return self.rest_add_policy_action(rbac_view_name, policy_name, policy_action, user="admin", password="adminadmin")


# Disable bigtap feature overlap/inport-mask/tracked-host/l3-l4-mode
    def rest_disable_feature(self, feature_name):
        '''
            Objective:
            - Disable a bigtap feature
        
           Input:
            | `feature_name` | Bigtap Feature Name. \n Currently allowed feature names are `overlap`,`inport-mask`,`tracked-host`,`l3-l4-mode` | 
            
            Return Value 
            - True if feature is enabled
            - False if feature could not be enabled
            
            Examples:
                | rest disable feature  |  overlap |  
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('master')
            try:
                c.rest.get('/rest/v1/system/version')
                content = c.rest.content()
                version_string = content[0]['controller']
                helpers.log("version string is %s" % version_string)
                if ("3.0.0" in str(version_string)) or ("3.1.0" in str(version_string)) or ("3.1.1" in str(version_string)):
                    data = {str(feature_name): False}
                else:
                    if ("l3-l4" in str(feature_name)):
                        matchcondition = "full-match"
                        data = {"match-mode": str(matchcondition)}
                        helpers.log("Data to be patched is %s" % data)
                    else:
                        data = {str(feature_name): False}
                        helpers.log("Data to be patched is %s" % data)
            except:
                helpers.test_log(c.rest.error())
                return False
            else:
                try:
                    url = '/api/v1/data/controller/applications/bigtap/feature'
                    c.rest.patch(url, data)
                except:
                    return False
                else:
                    helpers.test_log(c.rest.content_json())
                    return True

# Enable bigtap feature overlap/inport-mask/tracked-host/l3-l4-mode
    def rest_enable_feature(self, feature_name):
        '''
            Objective:
            - Enable a bigtap feature
        
           Input:
            | `feature_name` | Bigtap Feature Name. \n Currently allowed feature names are `overlap`,`inport-mask`,`tracked-host`,`l3-l4-mode`, `tunneling` | 
            
            Return Value 
            - True if feature is enabled
            - False if feature could not be enabled
            
            Examples:
                | rest enable feature  |  overlap |  
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('master')
            try:
                c.rest.get('/rest/v1/system/version')
                content = c.rest.content()
                version_string = content[0]['controller']
                helpers.log("version string is %s" % version_string)
                if ("3.1.1" in str(version_string)) or ("3.1.0" in str(version_string)) or ("3.0.0" in str(version_string)):
                    data = {str(feature_name): True}
                else:
                    if ("l3-l4" in str(feature_name)) or ("full-match" in str(feature_name)):
                        if "l3-l4-mode" in str(feature_name):
                            matchcondition = "l3-l4-match"
                        elif "offset" in str(feature_name):
                            matchcondition = "l3-l4-offset-match"
                        else:
                            matchcondition = "full-match"
                        data = {"match-mode": str(matchcondition)}
                        helpers.log("Data to be patched is %s" % data)
                    else:
                        data = {str(feature_name): True}
                        helpers.log("Data to be patched is %s" % data)

            except:
                return False
            else:
                try:
                    url = '/api/v1/data/controller/applications/bigtap/feature'
                    c.rest.patch(url, data)
                except:
                    return False
                else:
                    helpers.test_log(c.rest.content_json())
                    return True


# Compare coreswitch flows
    def rest_verify_coreswitch_flows(self, flow_1, flow_2, flow_value_1, flow_value_2):
        '''
            Objective
            - Compare coreswitch flow counts. Useful when we have multiple core-switches.
        
            Inputs:
            | flow_1 | Number of flows on core switch 1 | 
            | flow_2 | Number of flows on core switch 2 | 
            | flow_value_1 | Desired number of flows on switch 1 or switch 2 | 
            | flow_value_2 | Desired number of flows on switch 1 or switch 2 | 
        
            Return Value 
            - True if flow is found on switch
            - False if flow is not found on switch
        '''
        if ((flow_1 == flow_value_1) and (flow_2 == flow_value_2)) or ((flow_2 == flow_value_1) and (flow_1 == flow_value_2)):
            return True
        else:
            return False

# Mingtao
    def bigtap_delete_all(self):
        """ Clean up bigtap configuration in order: policy, address-group
           -- Mingtao
         """
        self.bigtap_delete_policy()
        self.bigtap_delete_address_group()
        return True

# Mingtao
    def bigtap_delete_policy(self, policy=None, rbac_view='admin-view'):
        ''' 
            Objective: 
            Delete a Policy
            
            Input:
            | policy | Name of policy  |
            | rbac_view | Name of rbac_view in which the policy resides. |
            
            Return Values:
            | True |  if configuration delete is successful.|
            | False | if configuration delete is unsuccessful.|
        '''
        t = test.Test()
        c = t.controller('master')

        if policy:
            helpers.log("Policy to be deleted: %s" % (policy))
            url = '/api/v1/data/controller/applications/bigtap/view[name="%s"]/policy[name="%s"]' % (rbac_view, policy)
            c.rest.delete(url)
            if not c.rest.status_code_ok():
                helpers.test_log(c.rest.error())
                return False
        else:
            url = '/api/v1/data/controller/applications/bigtap/view/policy?select=info'
            c.rest.get(url)
            content = c.rest.content()
            if not c.rest.status_code_ok():
                helpers.test_log(c.rest.error())
                return False
            helpers.log("Output: %s" % c.rest.result_json())
            length = len(content)
            helpers.log("Number of Policies to be deleted: %s" % str(length))
            for index in range(length):
                name = content[index]['name']
                helpers.log("Policy being deleted is %s in view: %s" % (str(name), str(rbac_view)))
                url = '/api/v1/data/controller/applications/bigtap/view[name="%s"]/policy[name="%s"]' % (str(rbac_view), str(name))
                c.rest.delete(url)
                if not c.rest.status_code_ok():
                    helpers.test_log(c.rest.error())
                    return False
        return True

# Mingtao
    def bigtap_delete_address_group(self, addr_group=None):
        ''' 
            Objective: 
            Delete an address-group
            
            Input:
            | addr_group | Name of Address Group |
            
            Return Values:
            | True | configuration delete is successful.|
            | False | configuration delete is unsuccessful.|
        '''
        t = test.Test()
        c = t.controller('master')

        if addr_group:
            helpers.log("Address Group to be deleted is: %s" % (addr_group))
            url = '/api/v1/data/controller/applications/bigtap/ip-address-set[name="%s"]' % (addr_group)
            c.rest.delete(url)
            if not c.rest.status_code_ok():
                helpers.test_failure(c.rest.error())
        else:
            url = '/api/v1/data/controller/applications/bigtap/ip-address-set'
            c.rest.get(url)
            content = c.rest.content()
            if not c.rest.status_code_ok():
                helpers.test_failure(c.rest.error())
                return False
            length = len(content)
            helpers.log("Number of address group is: %s" % str(length))
            for index in range(length):
                name = content[index]['name']
                helpers.log("this is the %s Address-group to be deleted: %s" % (str(index), str(name)))
                url = '/api/v1/data/controller/applications/bigtap/ip-address-set[name="%s"]' % (str(name))
                c.rest.delete(url)
                if not c.rest.status_code_ok():
                    helpers.test_failure(c.rest.error())
                    return False
        return True

# Mingtao
    def bigtap_delete_service(self, service=None):
        ''' 
            Objective: 
            Delete a service
            
            Input:
            | service | Name of service |
            
            Return Values:
            | True | configuration delete is successful.|
            | False | configuration delete is unsuccessful.|
        '''
        t = test.Test()
        c = t.controller('master')

        if service:
            helpers.log("this is the Service to be deleted: %s" % (service))
            url = '/api/v1/data/controller/applications/bigtap/service[name="%s"]' % (service)
            c.rest.delete(url)
            if not c.rest.status_code_ok():
                helpers.test_failure(c.rest.error())
        else:
            url = '/api/v1/data/controller/applications/bigtap/service'
            c.rest.get(url)
            content = c.rest.content()
            if not c.rest.status_code_ok():
                helpers.test_failure(c.rest.error())
                return False
            length = len(content)
            helpers.log("Number of services is: %s" % str(length))
            for index in range(length):
                name = content[index]['name']
                helpers.log("this is the %s service to be deleted: %s" % (str(index), str(name)))
                url = '/api/v1/data/controller/applications/bigtap/service[name="%s"]' % str(name)
                c.rest.delete(url)
                if not c.rest.status_code_ok():
                    helpers.test_failure(c.rest.error())
                    return False
        return True

# Mingtao
    def rest_add_address_group(self, name, addr_type):
        ''' 
            Objective: 
            Add a IPv4/IPv6 Address Group
            
            Input:
            | name | Name of Address Group |
            | addr_type | IPv4 or IPv6 |
            
            Return Values:
            | True | configuration add is successful.|
            | False | configuration add is unsuccessful.|
        '''
        try:
            t = test.Test()
            c = t.controller('master')
            url = '/api/v1/data/controller/applications/bigtap/ip-address-set[name="%s"]' % (str(name))
            c.rest.put(url, {"name": str(name)})
            helpers.sleep(1)

            url = '/api/v1/data/controller/applications/bigtap/ip-address-set[name="%s"]' % (str(name))

            c.rest.patch(url, {"ip-address-type": str(addr_type)})
            helpers.sleep(1)
        except:
            return False
        else:
            helpers.test_log(c.rest.content_json())
            return True

# Mingtao
    def rest_add_address_group_entry(self, name, addr, mask):
        ''' 
            Objective: 
            Add an IPv4/IPv6 Address Group
            
            Input:
            | name | Name of Address Group |
            | addr_type | IPv4 or IPv6 |
            
            Return Values:
            | True | configuration add is successful.|
            | False | configuration add is unsuccessful.|
        '''
        # create the address group and associate the type
        try:
            t = test.Test()
            c = t.controller('master')

            url = ('/api/v1/data/controller/applications/bigtap/ip-address-set[name="%s"]/address-mask-set[ip="%s"][ip-mask="%s"]'
                   % (str(name), str(addr), str(mask)))

            c.rest.put(url, {"ip": str(addr), "ip-mask": str(mask)})
            helpers.sleep(1)
            helpers.test_log(c.rest.content_json())
        except:
            return False
        else:
            helpers.test_log(c.rest.content_json())
            return True



# Mingtao
    def gen_add_address_group_entries(self, group, addr_type, base, incr, mask, number):
        """ 
            Objective:
            Generate IPv4 and/or IPv6 addresses for an address group.
            
            Input:
            | group | Name of IP Address Group|
            | addr_type | IPv4/IpV6|
            | base | Starting IP address |
            | incr | Value by which we will incrememnt the IP address|
            | mask | Subnet Mask |
            | number | number of addresses to be generated|

            Usage:
                gen_add_address_group_entries     IPV4    ipv4     10.0.0.0     0.1.0.1        255.255.255.0     20
                gen_add_address_group_entries     IPV6    ipv6     f001:100:0:0:0:0:0:0     0:0:0:0:0:0:0:1     
                                                    ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff     20
        """
        helpers.log("the base address is: %s,  the step is: %s,  the mask is: %s,  the Num is: %s"
                      % (str(base), str(incr), str(mask), str(number)))

        self.rest_add_address_group_entry(group, base, mask)

        Num = int(number) - 1
        for _ in range(0, int(Num)):

            ip_address = helpers.get_next_address(addr_type, base, incr)
            self.rest_add_address_group_entry(group, ip_address, mask)
            base = ip_address
            helpers.log("the applied address is: %s %s %s " % (addr_type, str(ip_address), str(mask)))

        return True

# Mingtao
    def construct_policy_match(self,
                               ip_type=None,
                               ether_type=None,
                               src_mac=None,
                               dst_mac=None,
                               ip_proto=None,
                               icmp=None,
                               icmp_code=None,
                               icmp_type=None,
                               vlan=None,
                               vlan_min=None,
                               vlan_max=None,
                               src_ip_list=None,
                               src_ip=None,
                               src_ip_mask=None,
                               dst_ip_list=None,
                               dst_ip=None,
                               dst_ip_mask=None,
                               tos_bit=None,
                               src_port=None,
                               src_port_min=None,
                               src_port_max=None,
                               dst_port=None,
                               dst_port_min=None,
                               dst_port_max=None,
                               sequence=10):
        """ bigtap: construct the match string for policy
            Mingtao
        """
        temp = '{'

        if src_mac:
            temp += '"src-mac": "%s",' % src_mac
        if dst_mac:
            temp += '"dst-mac": "%s",' % dst_mac

        if icmp:
            temp += '"ip-proto": 1,'
            if icmp_code:
                temp += '"dst-tp-port": %s,' % icmp_code
            if icmp_type:
                temp += '"src-tp-port": %s,' % icmp_type

        if ether_type:
            if ether_type == 'ipv6' or ether_type == 'ip6':
                temp += '"ether-type": 34525,'
            elif ether_type == 'ip' or ether_type == 'ipv4':
                temp += '"ether-type": 2048,'
            else:
                temp += '"ether-type": %s,' % ether_type
        elif ip_type:
            if ip_type == 'ip' or  ip_type == 'ipv4':
                temp += '"ether-type": 2048,'
            else:
                temp += '"ether-type": 34525,'

        if ip_proto:
            if ip_proto == 'tcp':
                temp += '"ether-type": 2048,'
                temp += '"ip-proto": 6,'
            elif ip_proto == 'tcp6':
                temp += '"ether-type": 34525,'
                temp += '"ip-proto": 6,'
            elif ip_proto == 'udp':
                temp += '"ether-type": 2048,'
                temp += '"ip-proto": 17,'
            elif ip_proto == 'udp6':
                temp += '"ether-type": 34525,'
                temp += '"ip-proto": 17,'
            else:
                temp += '"ip-proto": %s,' % ip_proto


        if vlan:
            temp += '"vlan":  %s ,' % vlan
        else:
            if vlan_min:
                temp += '"src-tp-port-min": %s,' % vlan_min
            if vlan_max:
                temp += '"src-tp-port-min": %s,' % vlan_max

        if src_ip_list:
            temp += '"src-ip-list": "%s",' % src_ip_list
        else:
            if src_ip:
                temp += '"src-ip": "%s",' % src_ip
            if src_ip_mask:
                temp += '"src-ip-mask": "%s",' % src_ip_mask

        if dst_ip_list:
            temp += '"dst-ip-list": "%s",' % dst_ip_list
        else:
            if dst_ip:
                temp += '"dst-ip": "%s",' % dst_ip
            if dst_ip_mask:
                temp += '"dst-ip-mask": "%s",' % dst_ip_mask

        if tos_bit:
            temp += '"ip-tos": %s,' % tos_bit

        if src_port:
            temp += '"src-tp-port":  %s ,' % src_port
        else:
            if src_port_min:
                temp += '"src-tp-port-min": %s,' % src_port_min
            if src_port_max:
                temp += '"src-tp-port-min": %s,' % src_port_max

        if dst_port:
            temp += '"dst-tp-port":  %s ,' % dst_port
        else:
            if dst_port_min:
                temp += '"dst-tp-port-min": %s,' % dst_port_min
            if dst_port_max:
                temp += '"dst-tp-port-min": %s,' % dst_port_max

        temp += '"sequence": %s}' % sequence
        helpers.log("the temp is: %s" % (str(temp)))

        return temp

############################################
############ CORSAIR: TUNNELLING ### START #
############################################

    def rest_add_tunnel_interface(self, node, tunnel_name, switch_alias=None, sw_dpid=None, loopback=None, pinterface=None, tdirection=None, sip=None, mask=None, dip=None, gip=None, vpnkey=1234, user="admin", password="adminadmin", soft_error=False):
        t = test.Test()
        try:
            c = t.controller('master')
            AppCommon = AppController.AppController()
        except:
            return False
        else:
            try:
                if (switch_alias is None and sw_dpid is not None):
                    switch_dpid = sw_dpid
                elif (switch_alias is None and sw_dpid is None):
                    switch_dpid = AppCommon.rest_return_switch_dpid_from_ip(node)
                elif (switch_alias is not None and sw_dpid is None):
                    switch_dpid = AppCommon.rest_return_switch_dpid_from_alias(switch_alias)
                else:
                    switch_dpid = sw_dpid
            except:
                return False
            else:
                url = '/api/v1/data/controller/core/switch[dpid="%s"]/interface[name="%s"]' % (str(switch_dpid), str(tunnel_name))
                if "admin" not in user:
                    helpers.test_error("Non-Admin users cannot create tunnel interfaces", soft_error)
                    return False
                else:
                    c.rest.put(url, {"name": str(tunnel_name)})

                if pinterface is not None:
                    if "admin" not in user:
                        helpers.test_error("Non-Admin users cannot create tunnel interfaces", soft_error)
                        return False
                    else:
                        if "ethernet" not in pinterface:
                            helpers.test_error("Parent interface name needs to contain prefix ethernet", soft_error)
                            return False
                        else:
                            c.rest.patch(url, {"parent-interface": str(pinterface)})
                            if not c.rest.status_code_ok():
                                helpers.test_log(c.rest.error())
                                return False

                if tdirection is not None:
                    if (tdirection == 'bidir') or (tdirection == 'bidirectional'):
                        direction = 'bidirectional'
                        if loopback is None:
                            helpers.log("Loopback interface needs to be specified when tunnel direction is bidirectional")
                            return False
                    elif (tdirection == 'tx') or (tdirection == 'transmit-only'):
                        direction = 'transmit-only'
                        if loopback is None:
                            helpers.log("Loopback interface needs to be specified when tunnel transmit-only is bidirectional")
                            return False
                    elif (tdirection == 'rx') or (tdirection == 'receive-only'):
                        direction = 'receive-only'
                    else:
                        helpers.test_error("Incorrect tunnel-direction value was passed. Please check your txt file", soft_error)
                        return False
                    if "admin" not in user:
                        helpers.test_error("Non-Admin users cannot create tunnel interfaces", soft_error)
                        return False
                    else:
                        if (direction == 'bidirectional') or (direction == 'transmit-only'):
                            c.rest.patch(url, {"direction": str(direction), "loopback-interface": str(loopback), "type": "tunnel"})
                        else:
                            c.rest.patch(url, {"direction": str(direction), "type": "tunnel"})
                        if not c.rest.status_code_ok():
                            helpers.test_log(c.rest.error())
                            return False

                ip_url = '/api/v1/data/controller/core/switch[dpid="%s"]/interface[name="%s"]/ip-config' % (str(switch_dpid), str(tunnel_name))
                if (sip is not None) and (gip is not None) and (mask is not None):
                    c.rest.put(ip_url, {"source-ip": str(sip), "ip-mask": str(mask), "gateway-ip": str(gip)})
                    if not c.rest.status_code_ok():
                        helpers.test_log(c.rest.error())
                        return False

                if (dip is not None):
                    c.rest.put(ip_url, {"destination-ip": str(dip)})
                    if not c.rest.status_code_ok():
                        helpers.test_log(c.rest.error())
                        return False

                if "admin" not in user:
                    helpers.test_error("Non-Admin users cannot create tunnel interfaces", soft_error)
                    return False
                else:
                    c.rest.patch(url, {"vpn-key": int(vpnkey), "encap-type": "gre"})
                return True

    def rest_verify_tunnel_status(self, node, tunnel_name, switch_alias=None, sw_dpid=None, tunnel_number=None, runtime_state=None, parent_interface=None, tunnel_direction=None, sip=None, mask=None, dip=None, gip=None, user="admin", password="adminadmin", soft_error=False):
        t = test.Test()
        try:
            c = t.controller('master')
            AppCommon = AppController.AppController()
        except:
            return False
        else:
            try:
                if (switch_alias is None and sw_dpid is not None):
                    switch_dpid = sw_dpid
                elif (switch_alias is None and sw_dpid is None):
                    switch_dpid = AppCommon.rest_return_switch_dpid_from_ip(node)
                elif (switch_alias is not None and sw_dpid is None):
                    switch_dpid = AppCommon.rest_return_switch_dpid_from_alias(switch_alias)
                else:
                    switch_dpid = sw_dpid
            except:
                return False
            else:
                url = '/api/v1/data/controller/core/switch[dpid="%s"][interface/name="%s"][dpid="%s"]?select=interface[name="%s"]' % (str(switch_dpid), str(tunnel_name), str(switch_dpid), str(tunnel_name))
                c.rest.get(url)
                content = c.rest.content()
                if content[0]['interface'][0] == None:
                    return False
                else:
                    if content[0]['interface'][0]['name'] == str(tunnel_name):
                        helpers.test_log("Tunnel Name is correctly reported as : %s" % content[0]['interface'][0]['name'])
                    else:
                        helpers.test_log("Tunnel Name is not correctly reported as  : %s" % content[0]['interface'][0]['name'], soft_error)
                        return False

                    if content[0]['dpid'] == str(switch_dpid):
                        helpers.test_log("Switch DPID is corretcly reported as : %s" % content[0]['dpid'])
                    else:
                        helpers.test_log("Switch DPID is not corretcly reported as  : %s" % content[0]['dpid'], soft_error)
                        return False

                    if tunnel_number is not None:
                        if 'number' not in content[0]['interface'][0]:
                            return False
                        else:
                            if int(content[0]['interface'][0]['number']) == int(tunnel_number):
                                helpers.test_log("Tunnel Number is corretcly reported as : %s" % content[0]['interface'][0]['number'])
                            else:
                                helpers.test_log("Tunnel Number is not corretcly reported as  : %s" % content[0]['interface'][0]['number'], soft_error)
                                return False

                    if runtime_state is not None:
                        if content[0]['interface'][0]['runtime-state'] is None :
                            return False
                        else:
                            if content[0]['interface'][0]['runtime-state'] == str(runtime_state):
                                helpers.test_log("Runtime State is corretcly reported as : %s" % content[0]['interface'][0]['runtime-state'])
                            else:
                                helpers.test_log("Runtime State is not corretcly reported as  : %s" % content[0]['interface'][0]['runtime-state'], soft_error)
                                return False


                    if parent_interface is not None:
                        if content[0]['interface'][0]['parent-interface'] is None :
                            return False
                        else:
                            if content[0]['interface'][0]['parent-interface'] == str(parent_interface):
                                helpers.test_log("Parent Interface is corretcly reported as : %s" % content[0]['interface'][0]['parent-interface'])
                            else:
                                helpers.test_log("Parent Interface is not corretcly reported as  : %s" % content[0]['interface'][0]['parent-interface'], soft_error)
                                return False

                    if tunnel_direction is not None:
                        if (tunnel_direction == 'bidir') or (tunnel_direction == 'bidirectional'):
                            direction = 'bidirectional'
                        elif (tunnel_direction == 'tx') or (tunnel_direction == 'transmit-only'):
                            direction = 'transmit-only'
                        elif (tunnel_direction == 'rx') or (tunnel_direction == 'receive-only'):
                            direction = 'receive-only'
                        else:
                            helpers.log("Incorrect tunnel-direction value was passed. Please check your txt file")
                            return False
                        if content[0]['interface'][0]['direction'] is None :
                            return False
                        else:
                            if content[0]['interface'][0]['direction'] == str(direction):
                                helpers.test_log("Tunnel direction is  corretcly reported as : %s" % content[0]['interface'][0]['direction'])
                            else:
                                helpers.test_log("Tunnel direction is not corretcly reported as  : %s" % content[0]['interface'][0]['direction'], soft_error)
                                return False

                    if sip is not None:
                        if content[0]['interface'][0]['ip-config']['source-ip'] is None :
                            return False
                        else:
                            if content[0]['interface'][0]['ip-config']['source-ip'] == str(sip):
                                helpers.test_log("Source IP is corretcly reported as : %s" % content[0]['interface'][0]['ip-config']['source-ip'])
                            else:
                                helpers.test_log("Source IP is not corretcly reported as  : %s" % content[0]['interface'][0]['ip-config']['source-ip'], soft_error)
                                return False

                    if dip is not None:
                        if content[0]['interface'][0]['ip-config']['destination-ip'] is None :
                            return False
                        else:
                            if content[0]['interface'][0]['ip-config']['destination-ip'] == str(dip):
                                helpers.test_log("Destinantion IP is corretcly reported as : %s" % content[0]['interface'][0]['ip-config']['destination-ip'])
                            else:
                                helpers.test_log("Destinantion IP is not corretcly reported as  : %s" % content[0]['interface'][0]['ip-config']['destination-ip'], soft_error)
                                return False


                    if gip is not None:
                        if content[0]['interface'][0]['ip-config']['gateway-ip']  is None :
                            return False
                        else:
                            if content[0]['interface'][0]['ip-config']['gateway-ip'] == str(gip):
                                helpers.test_log("Gateway IP is corretcly reported as : %s" % content[0]['interface'][0]['ip-config']['gateway-ip'])
                            else:
                                helpers.test_log("Gateway IP is not corretcly reported as  : %s" % content[0]['interface'][0]['ip-config']['gateway-ip'], soft_error)
                                return False

                    if mask is not None:
                        if content[0]['interface'][0]['ip-config']['ip-mask'] is None :
                            return False
                        else:
                            if content[0]['interface'][0]['ip-config']['ip-mask'] == str(mask):
                                helpers.test_log("IP Mask is corretcly reported as : %s" % content[0]['interface'][0]['ip-config']['ip-mask'])
                            else:
                                helpers.test_log("IP Mask is not corretcly reported as  : %s" % content[0]['interface'][0]['ip-config']['ip-mask'], soft_error)
                                return False

                return True

    def rest_delete_tunnel_interface(self, node, tunnel_name, switch_alias=None, sw_dpid=None, user="admin", password="adminadmin", soft_error=False):
        t = test.Test()
        try:
            c = t.controller('master')
            AppCommon = AppController.AppController()
        except:
            return False
        else:
            try:
                if (switch_alias is None and sw_dpid is not None):
                    switch_dpid = sw_dpid
                elif (switch_alias is None and sw_dpid is None):
                    switch_dpid = AppCommon.rest_return_switch_dpid_from_ip(node)
                elif (switch_alias is not None and sw_dpid is None):
                    switch_dpid = AppCommon.rest_return_switch_dpid_from_alias(switch_alias)
                else:
                    switch_dpid = sw_dpid
            except:
                return False
            else:
                url = '/api/v1/data/controller/core/switch[dpid="%s"]/interface[name="%s"]' % (str(switch_dpid), str(tunnel_name))
                if "admin" not in user:
                    helpers.test_error("Non-Admin users cannot delete tunnel interfaces", soft_error)
                    return False
                else:
                    c.rest.delete(url, {})
                    if not c.rest.status_code_ok():
                        helpers.test_log(c.rest.error())
                        return False
                    else:
                        return True

    def rest_delete_tunnel_items(self, node, tunnel_name, switch_alias=None, sw_dpid=None, item=None, user="admin", password="adminadmin", soft_error=False):
        t = test.Test()
        try:
            c = t.controller('master')
            AppCommon = AppController.AppController()
        except:
            return False
        else:
            try:
                if (switch_alias is None and sw_dpid is not None):
                    switch_dpid = sw_dpid
                elif (switch_alias is None and sw_dpid is None):
                    switch_dpid = AppCommon.rest_return_switch_dpid_from_ip(node)
                elif (switch_alias is not None and sw_dpid is None):
                    switch_dpid = AppCommon.rest_return_switch_dpid_from_alias(switch_alias)
                else:
                    switch_dpid = sw_dpid
            except:
                return False
            else:
                if item is None:
                    helpers.test_error("User needs to pass a value to 'item' to delete", soft_error)
                    return False
                if 'tunnel-source' in item:
                    url1 = '/api/v1/data/controller/core/switch[dpid="%s"]/interface[name="%s"]/ip-config/source-ip' % (str(switch_dpid), str(tunnel_name))
                    if "admin" not in user:
                        helpers.test_error("Non-Admin users cannot delete tunnel sub-items", soft_error)
                        return False
                    else:
                        c.rest.delete(url1, {})
                        if not c.rest.status_code_ok():
                            helpers.test_log(c.rest.error())
                            return False
                        else:
                            return True
                    url2 = '/api/v1/data/controller/core/switch[dpid="%s"]/interface[name="%s"]/ip-config/ip-mask' % (str(switch_dpid), str(tunnel_name))
                    if "admin" not in user:
                        helpers.test_error("Non-Admin users cannot delete tunnel sub-items", soft_error)
                        return False
                    else:
                        c.rest.delete(url2, {})
                        if not c.rest.status_code_ok():
                            helpers.test_log(c.rest.error())
                            return False
                        else:
                            return True
                    url3 = '/api/v1/data/controller/core/switch[dpid="%s"]/interface[name="%s"]/ip-config/gateway-ip' % (str(switch_dpid), str(tunnel_name))
                    if "admin" not in user:
                        helpers.test_error("Non-Admin users cannot delete tunnel sub-items", soft_error)
                        return False
                    else:
                        c.rest.delete(url3, {})
                        if not c.rest.status_code_ok():
                            helpers.test_log(c.rest.error())
                            return False
                        else:
                            return True
                else:
                    if 'tunnel-interface' in item:
                        url = '/api/v1/data/controller/core/switch[dpid="%s"]/interface[name="%s"][parent-interface="None"][name="%s"]/parent-interface' % (str(switch_dpid), str(tunnel_name), str(tunnel_name))
                    elif 'tunnel-encap-type' in item:
                        url = '/api/v1/data/controller/core/switch[dpid="%s"]/interface[name="%s"][encap-type="None"][name="%s"]/encap-type' % (str(switch_dpid), str(tunnel_name), str(tunnel_name))
                    elif 'tunnel-direction' in item:
                        url = '/api/v1/data/controller/core/switch[dpid="%s"]/interface[name="%s"][direction="None"][name="%s"]/direction' % (str(switch_dpid), str(tunnel_name), str(tunnel_name))
                    elif 'tunnel-destination' in item:
                        url = '/api/v1/data/controller/core/switch[dpid="%s"]/interface[name="%s"]/ip-config/destination-ip' % (str(switch_dpid), str(tunnel_name))
                    elif 'tunnel-type' in item:
                        url = '/api/v1/data/controller/core/switch[dpid="%s"]/interface[name="%s"][type="None"][name="%s"]/type' % (str(switch_dpid), str(tunnel_name), str(tunnel_name))
                    else:
                        helpers.test_error("Invalid field passed to keyword. Please check your .txt file", soft_error)
                        return False

                    if "admin" not in user:
                        helpers.test_error("Non-Admin users cannot delete tunnel sub-items", soft_error)
                        return False
                    else:
                        c.rest.delete(url, {})
                        if not c.rest.status_code_ok():
                            helpers.test_log(c.rest.error())
                            return False
                        else:
                            return True

############################################
############ CORSAIR: TUNNELLING ### END ###
############################################
###################################################
# BigTap User Management
###################################################

    def rest_add_user(self, username):
        '''
            Objective:
            - Add a user
            
            Inputs:
            |username| Desired username for user|
            
            Return Value:
            | True | On Configuration success|
            | False | On Configuration failure|
            
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('master')
            try:
                url = '/api/v1/data/controller/core/aaa/local-user[user-name="%s"] ' % (str(username))
                c.rest.put(url, {"user-name": str(username)})
            except:
                helpers.test_log(c.rest.error())
                return False
            else:
                return True

    def rest_delete_user(self, username):
        '''
            Objective:
            - Add a user
            
            Inputs:
            |username| Desired username for user|
            
            Return Value:
            | True | On Configuration success|
            | False | On Configuration failure|
            
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('master')
            try:
                url = '/api/v1/data/controller/core/aaa/local-user[user-name="%s"] ' % (str(username))
                c.rest.delete(url, {})
            except:
                helpers.test_log(c.rest.error())
                return False
            else:
                return True



    def rest_add_user_password(self, username, password):
        '''
            Objective:
            - Set password for given user
            
            Inputs:
            |username| username for which password is being configured|
            |password| Password to be configured|            
            
            Return Value:
            | True | On Configuration success|
            | False | On Configuration failure|
            
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('master')
            try:
                # Get the hashed value of password
                t.node_reconnect(node='master')
                helpers.log("Password is %s" % json.dumps(password))
                url1 = '/api/v1/data/controller/core/aaa/hash-password[password=%s]' % json.dumps(password)
                c.rest.get(url1)
                myHash = c.rest.content()
                myHashPass = myHash[0]['hashed-password']
                # Assign password to user
                url2 = '/api/v1/data/controller/core/aaa/local-user[user-name="%s"]' % str(username)
                c.rest.patch(url2, {"password": str(myHashPass)})
            except:
                helpers.test_log(c.rest.error())
                return False
            else:
                return True

    def rest_add_rbac_group(self, group_name, rbac_view):
        '''
            Objective:
            - Create a group and assign bigtap rbac-permission
            
            Inputs:
            |group_name| Group Name that is being configured|
            |rbac_view| RBAC View to be associated with group|            
            
            Return Value:
            | True | On Configuration success|
            | False | On Configuration failure|
            
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('master')
            try:
                # Create a group first
                url1 = '/api/v1/data/controller/core/aaa/group[name="%s"]' % str(group_name)
                c.rest.put(url1, {"name": str(group_name)})
                # Add rbac-view to Group
                url2 = '/api/v1/data/controller/core/aaa/group[name="%s"]/rbac-permission' % str(group_name)
                c.rest.patch(url2, [str(rbac_view)])
            except:
                helpers.test_log(c.rest.error())
                return False
            else:
                return True

    def rest_delete_rbac_group(self, group_name):
        '''
            Objective:
            - Create a group and assign bigtap rbac-permission
            
            Inputs:
            |group_name| Group Name that is being configured|
            |rbac_view| RBAC View to be associated with group|            
            
            Return Value:
            | True | On Configuration success|
            | False | On Configuration failure|
            
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('master')
            try:
                # Create a group first
                url1 = '/api/v1/data/controller/core/aaa/group[name="%s"]' % str(group_name)
                c.rest.delete(url1, {})
            except:
                helpers.test_log(c.rest.error())
                return False
            else:
                return True

    def rest_add_user_to_group(self, username, group_name):
        '''
            Objective:
            - Add a user to group
            
            Inputs:
            |group_name| Group Name that is being configured|
            |username| username which is being assigned to the group|            
            
            Return Value:
            | True | On Configuration success|
            | False | On Configuration failure|
            
        '''
        try:
            t = test.Test()
            # t.node_reconnect(node='master')
        except:
            return False
        else:
            c = t.controller('master')
            try:
                #
                url = '/api/v1/data/controller/core/aaa/group[name="%s"]' % str(group_name)
                c.rest.get(url)
                content = c.rest.content()
                data1 = []
                url1 = '/api/v1/data/controller/core/aaa/group[name="%s"]/user' % str(group_name)
                if not "user" in content[0]:
                    helpers.log("User does not exist")
                    c.rest.patch(url1, [username])
                else:
                    data1 = content[0]['user']
                    data1.append(username)
                    helpers.log("User exists and data1 is %s" % data1)
                    c.rest.patch(url1, data1)
            except:
                helpers.test_log(c.rest.error())
                return False
            else:
                return True

    def cli_delete_user_from_group(self, username, group_name):
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('master')
            try:
                t.node_reconnect(node='master')
                cli_input_1 = str("group ") + str(group_name)
                c.config(cli_input_1)
                cli_input_2 = "no associate user " + str(username)
                c.config(cli_input_2)
            except:
                helpers.test_log(helpers.exception_info())
                return False
            else:
                return True

    def rest_add_rbac_permission(self, rbac_view):
        '''
            Objective:
            - Add a user to group
            
            Inputs:
            |rbac_view| RBAC group name that is being configured|
            
            Return Value:
            | True | On Configuration success|
            | False | On Configuration failure|
            
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('master')
            try:
                # Add user to Group
                url1 = '/api/v1/data/controller/core/aaa/rbac-permission[name="%s"]' % str(rbac_view)
                c.rest.put(url1, {"name": str(rbac_view)})
            except:
                helpers.test_log(c.rest.error())
                return False
            else:
                return True

    def rest_delete_rbac_permission(self, rbac_view):
        '''
            Objective:
            - Delete an rbac permission
            
            Inputs:
            |rbac_view| RBAC group name that is being configured|
            
            Return Value:
            | True | On Configuration success|
            | False | On Configuration failure|
            
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('master')
            try:
                # Add user to Group
                url1 = '/api/v1/data/controller/core/aaa/rbac-permission[name="%s"]' % str(rbac_view)
                c.rest.delete(url1, {})
            except:
                helpers.test_log(c.rest.error())
                return False
            else:
                return True

    def rest_add_filter_interface_to_rbac(self, rbac_view, filter_name='allow-all'):
        '''
            Objective:
            - Add a filter-interface to rbac-permission
            
            Inputs:
            |rbac_view| RBAC group name that is being configured|
            |filter_name| Filter Interface that is being added|      
            
            Return Value:
            | True | On Configuration success|
            | False | On Configuration failure|
            
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('master')
            try:
                if 'allow-all' in filter_name:
                    url1 = '/api/v1/data/controller/core/aaa/rbac-permission[name="%s"]/bigtap' % str(rbac_view)
                    c.rest.patch(url1, {"allow-all-filter-interface": True})
                else:
                    url1 = '/api/v1/data/controller/core/aaa/rbac-permission[name="%s"]/bigtap/allowed-filter-interface[name="%s"]' % (str(rbac_view), str(filter_name))
                    c.rest.put(url1, {"name": str(filter_name)})
            except:
                helpers.test_log(c.rest.error())
                return False
            else:
                return True

    def rest_add_delivery_interface_to_rbac(self, rbac_view, delivery_name='allow-all'):
        '''
            Objective:
            - Add a delivery interface to rbac-permission
            
            Inputs:
            |rbac_view| RBAC group name that is being configured|
            |delivery_name| Delivery Interface that is being added|      
            
            Return Value:
            | True | On Configuration success|
            | False | On Configuration failure|
            
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('master')
            try:
                if 'allow-all' in delivery_name:
                    url1 = '/api/v1/data/controller/core/aaa/rbac-permission[name="%s"]/bigtap' % str(rbac_view)
                    c.rest.patch(url1, {"allow-all-delivery-interface": True})
                else:
                    url1 = '/api/v1/data/controller/core/aaa/rbac-permission[name="%s"]/bigtap/allowed-delivery-interface[name="%s"]' % (str(rbac_view), str(delivery_name))
                    c.rest.put(url1, {"name": str(delivery_name)})
            except:
                helpers.test_log(c.rest.error())
                return False
            else:
                return True


    def rest_add_service_to_rbac(self, rbac_view, service_name='allow-all'):
        '''
            Objective:
            - Add a service to rbac-permission
            
            Inputs:
            |rbac_view| RBAC group name that is being configured|
            |service_name| Service that is being added|      
            
            Return Value:
            | True | On Configuration success|
            | False | On Configuration failure|
            
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('master')
            try:
                if 'allow-all' in service_name:
                    url1 = '/api/v1/data/controller/core/aaa/rbac-permission[name="%s"]/bigtap' % str(rbac_view)
                    c.rest.patch(url1, {"allow-all-service": True})
                else:
                    url1 = '/api/v1/data/controller/core/aaa/rbac-permission[name="%s"]/bigtap/allowed-service[name="%s"]' % (str(rbac_view), str(service_name))
                    c.rest.put(url1, {"name": str(service_name)})
            except:
                helpers.test_log(c.rest.error())
                return False
            else:
                return True



    def rest_add_match_to_rbac(self, rbac_view, match_name='allow-all'):
        '''
            Objective:
            - Add a service to rbac-permission
            
            Inputs:
            |rbac_view| RBAC group name that is being configured|
            |service_name| Service that is being added|      
            
            Return Value:
            | True | On Configuration success|
            | False | On Configuration failure|
            
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('master')
            try:
                if 'allow-all' in match_name:
                    url1 = '/api/v1/data/controller/core/aaa/rbac-permission[name="%s"]/bigtap' % str(rbac_view)
                    c.rest.patch(url1, {"allow-all-match": True})
                # Currently not available
                else:
                    helpers.test_log(c.rest.error())
                    return False
#                    url1 = '/api/v1/data/controller/core/aaa/rbac-permission[name="%s"]/bigtap/allowed-service[name="%s"]' % (str(rbac_view), str(match_name))
#                    c.rest.put(url1, {"name": str(match_name)})
            except:
                helpers.test_log(c.rest.error())
                return False
            else:
                return True

    def return_match(self, protocol=None, ip_type=None, ether_type=None, dst_mac=None, src_mac=None, src_ip=None, dst_ip=None, src_port=None, src_port_min=None, src_port_max=None, dst_port_max=None, dst_port_min=None, dst_port=None, ip_tos=None, vlan=None, vlan_max=None, vlan_min=None):
        dictionary = {}
        data_P1 = {"sequence": 1}
        data_P2 = {"sequence": 1}
        chkArray_P1 = []
        chkArray_P2 = []

        if src_ip is not None and dst_ip is not None:
            if ":" in src_ip and ":" in dst_ip:
                ipv6_flag = True
            else:
                ipv6_flag = False

        if dst_mac is not None:
            dictionary['dst-mac'] = str(dst_mac)

        if src_mac is not None:
            dictionary['src-mac'] = str(src_mac)

        if src_ip is not None:
            dictionary['src-ip'] = str(src_ip)

        if dst_ip is not None:
            dictionary['dst-ip'] = str(dst_ip)

        if ip_tos is not None:
            dictionary['ip-tos'] = int(ip_tos)

        if vlan is not None:
            dictionary['vlan'] = int(vlan)

        if src_port is not None:
            dictionary['src-tp-port'] = int(src_port)

        if dst_port is not None:
            dictionary['dst-tp-port'] = int(dst_port)

        if src_port_max is not None:
            dictionary['src-tp-port-max'] = int(src_port_max)

        if dst_port_max is not None:
            dictionary['dst-tp-port-max'] = int(dst_port_max)

        if vlan_max is not None:
            dictionary['vlan-max'] = int(vlan_max)

        if protocol is not None:
            data_P1['ip-proto'] = int(protocol)
            data_P2['ip-proto'] = int(protocol)
            chkArray_P1.append('ip-proto')
            chkArray_P2.append('ip-proto')

        if ip_type is not None:
            data_P1['ether-type'] = int(ip_type)
            data_P2['ether-type'] = int(ip_type)
            chkArray_P1.append('ether-type')
            chkArray_P2.append('ether-type')

        if ether_type is not None:
            data_P1['ether-type'] = int(ether_type)
            data_P2['ether-type'] = int(ether_type)
            chkArray_P1.append('ether-type')
            chkArray_P2.append('ether-type')
        helpers.log("Dictionary is %s" % dictionary)
        tuples = [(x, y) for x in dictionary for y in dictionary if x != y]
        helpers.log("Dictionary is %s" % dictionary)
        match1 = []
        match2 = []
        for entry in tuples:
            if (entry[1], entry[0]) in tuples:
                tuples.remove((entry[1], entry[0]))
        for pair in tuples:
            data_P1[pair[0]] = dictionary[pair[0]]
            data_P2[pair[1]] = dictionary[pair[1]]
            chkArray_P1.append(pair[0])
            chkArray_P2.append(pair[1])
            if pair[0] == "src-ip" :
                if ipv6_flag:
                    data_P1['src-ip-mask'] = "ffff:ffff:ffff:ffff:0:0:0:0"
                else:
                    data_P1['src-ip-mask'] = "255.255.255.0"
            if pair[0] == "dst-ip" :
                if ipv6_flag:
                    data_P1['dst-ip-mask'] = "ffff:ffff:ffff:ffff:0:0:0:0"
                else:
                    data_P1['dst-ip-mask'] = "255.255.255.0"
            if pair[0] == "src-tp-port-max" :
                    data_P1['src-tp-port-min'] = int(src_port_min)
            if pair[0] == "dst-tp-port-max" :
                    data_P1['dst-tp-port-min'] = int(dst_port_min)
            if pair[0] == "vlan-max" :
                    data_P1['vlan-min'] = int(vlan_min)
            if pair[1] == "src-ip" :
                if ipv6_flag:
                    data_P2['src-ip-mask'] = "ffff:ffff:ffff:ffff:0:0:0:0"
                else:
                    data_P2['src-ip-mask'] = "255.255.255.0"
            if pair[1] == "dst-ip" :
                if ipv6_flag:
                    data_P2['dst-ip-mask'] = "ffff:ffff:ffff:ffff:0:0:0:0"
                else:
                    data_P2['dst-ip-mask'] = "255.255.255.0"
            if pair[1] == "src-tp-port-max" :
                    data_P2['src-tp-port-min'] = int(src_port_min)
            if pair[1] == "dst-tp-port-max" :
                    data_P2['dst-tp-port-min'] = int(dst_port_min)
            if pair[1] == "vlan-max" :
                    data_P2['vlan-min'] = int(vlan_min)
            match1.append(data_P1)
            match2.append(data_P2)
        match = match1 + match2
        helpers.log("Match is %s" % match)
        return (match)

    def rest_execute_generic_get(self, url, user="admin", password="adminadmin"):
        t = test.Test()
        c = t.controller('master')
        if "admin" not in user:
            c_user = t.node_spawn(ip=c.ip(), user=str(user), password=password)
            c_user.rest.get(url)
            content = c_user.rest.content()
            c_user.close()
        else:
            c.rest.get(url)
            content = c.rest.content()
        return content

    def cli_walk_exec(self, string='', file_name=None, padding=''):
        ''' cli_exec_walk
           walk through exec/login mode CLI hierarchy
           output:   file cli_exec_walk
        '''
        t = test.Test()
        c = t.controller('master')
        c.cli('')
        helpers.log("********* Entering cli_exec_walk ----> string: %s, file name: %s" % (string, file_name))
        if string == '':
            cli_string = '?'
        else:
            cli_string = string + ' ?'
        c.send(cli_string, no_cr=True)
        c.expect(r'[\r\n\x07][\w-]+[#>] ')
        content = c.cli_content()
        temp = helpers.strip_cli_output(content)
        temp = helpers.str_to_list(temp)
        helpers.log("********new_content:************\n%s" % helpers.prettify(temp))
        c.send(helpers.ctrl('u'))
        c.expect()
        c.cli('')

        string_c = string

        if file_name:
            helpers.log("opening file: %s" % file_name)
            fo = open(file_name, 'a')
            lines = []
            lines.append((padding + string))
            lines.append((padding + '----------'))
            for line in temp:
                lines.append((padding + line))
            lines.append((padding + '=================='))
            content = '\n'.join(lines)
            fo.write(str(content))
            fo.write("\n")

            fo.close()

        num = len(temp)
        padding = "   " + padding

        # Loop through commands and sub-commands
        for line in temp:
            string = string_c
            helpers.log(" line is - %s" % line)
            line = line.lstrip()
            keys = line.split(' ')
            temp_key = keys.pop(0)
            key = temp_key.strip()
            helpers.log("*** key is - %s" % key)
            helpers.log("*** string is - %s" % string)
            helpers.log("*** stringc is - %s" % string_c)

            if key is '':
                helpers.log("Ignore line %s" % line)
                num = num - 1
                continue
            # Ignoring lines which do not contain actual commands
            if re.match(r'For', line) or line == "Commands:":
                helpers.log("Ignoring line - %s" % line)
                num = num - 1
                continue

            # ## DELETE THIS (Temporary to Bypass failed command)
            # if re.match(r'config', line) :
            #    helpers.log("Ignore line %s" % line)
            #    num = num - 1
            #    continue

            # Ignoring commands which are either disruptive or are only one level commands
            # These commands would have already been displayed with corresponding help in a previous top-level hierarchy
            if key == "reauth" or key == "echo" or key == "help" or key == "logout" or key == "ping" or key == "watch":
                helpers.log("Ignore line %s" % line)
                num = num - 1
                continue

            # Ignoring sub-commands under 'debug'
            if key == "bash" or key == "connect" or key == "cassandra-cli" or key == "cli" or key == "cli-backtrace" or key == "cli-batch" or key == "description" or key == "netconfig" or key == "python" or key == "rest":
                helpers.log("Ignore line %s" % line)
                num = num - 1
                continue

            # Ignoring options that require user input or comments in <>
            if re.match(r'^<.+', line) and not re.match(r'^<cr>', line):
                helpers.log("Ignoring line - %s" % line)
                num = num - 1
                continue

            # Ignoring some sub-commands that may impact test run
            if ((key == '<cr>' and (re.match(r' set length term', string))) or re.match(r' show debug counters', string) or re.match(r' show debug events details', string)):
                helpers.log("Ignoring line - %s" % string)
                num = num - 1
                continue

            # skip 'show session' (PR BSC-5233)
            if (re.match(r' show session', string)):
                helpers.log("Ignoring line - %s" % string)
                num = num - 1
                continue

            # for interface related commands, only iterate through "all"
            if (re.match(r' show(.*)interface(.*)', string)):
                if key != 'all':
                    helpers.log("Ignoring line - %s" % string)
                    num = num - 1
                    continue

            # for switch related commands, only iterate through "all"
            if (re.match(r' show(.*)switch(.*)', string)):
                if key != 'all':
                    helpers.log("Ignoring line - %s" % string)
                    num = num - 1
                    continue

            # skip 'show logging', 'show lacp interface', 'show stats interface-history interface', 'show stats interface-history switch' and 'show running-config' - no need to iterate through options
            if (re.match(r' show logging', string)):
                helpers.log("Ignoring line - %s" % string)
                num = num - 1
                continue

            # issue the <cr> to test that the command actually works
            if key == '<cr>':

                if re.match(r'boot.*', string) or re.match(r'.*compare.*', string) or re.match(r'.*configure.*', string) or re.match(r'.*copy.*', string) or re.match(r'.*delete.*', string) or re.match(r'.*enable.*', string) or re.match(r'.*end.*', string) or re.match(r'.*exit.*', string) or re.match(r'.*failover.*', string) or re.match(r'.*logout.*', string):
                    helpers.log("Ignoring line - %s" % string)
                    num = num - 1
                    continue

                if re.match(r'.*show controller.*', string) or re.match(r'.*no.*', string) or re.match(r'.*ping.*', string) or re.match(r'.*reauth.*', string) or re.match(r'.*set .*', string) or re.match(r'.*show logging.*', string) or re.match(r'.*system.*', string) or re.match(r'.*test.*', string) or re.match(r'.*upgrade.*', string) or re.match(r'.*watch.*', string):
                    helpers.log("Ignoring line - %s" % string)
                    num = num - 1
                    continue

                helpers.log(" complete CLI show command: ******%s******" % string)
                c.cli(string)

                if num == 1:
                    helpers.log("AT END: ******%s******" % string)
                    return string

            # If command has sub-commands, call the function again to walk through sub-command options
            else:
                string = string + ' ' + key
                helpers.log("key - %s" % (key))
                helpers.log("string - %s" % (string))

                helpers.log("***** Call the cli walk again with  --- %s" % string)
                self.cli_walk_exec(string, file_name, padding)

    def cli_walk_command(self, command, cmd_argument_count, cmd_argument=None, soft_error=False):
        '''
            Execute CLI walk on controller
            Arguments:
            | command | Command to be executed |
            | cmd_argument_count | Number of lines in command help |
            | cmd_argument | Specific arguments that you want the function to look for in the command help|

            Description:
            This function checks for couple of things:
            | 1 | Number of lines in help output is what user has specified |
            | 2 | The CLI command does not have '<cr> <cr>' in its help output|
            | 3 | The CLI command is not missing a help string for some sub command |
            | 4 | if user has specified one or more arguments, those arguments are present in the help string|

            Example:
            |cli walk command |  show switch all | 6 | |
            |cli walk command |  show tenant | 14 | tenant1 tenant2 tenant3|
            |cli walk command |  show switch | 9 | leaf0-a leaf0-b spine0|

            example output of command:
            kk-mcntrlr-c1> show switch <====== Here number of lines are 13, but ideally you should see only 9. (this would be an error). THIS WOULD BE CAUGHT
            Keyword Choices:
                <cr>                            Show fabric information for selected switch
                all                             Show fabric information for selected switch
            Switch Name:Enter a switch name:Name of the switch.
            The field here primarily is a weak reference to that configured
            under core/switch-config/name.
                leaf0-a                         Switch Name selection of
                leaf0-b                         Switch Name selection of
                spine0                          Switch Name selection of
            core/proxy/controller/dpid:MAC Address
            core/proxy/environment/dpid:MAC Address
            core/proxy/inventory/dpid:MAC Address
            switch-name:Switch Name Selection:Switch Name selection
            kk-mcntrlr-c1>

            alpha-cont1> show switch all
            <cr> <cr><================================ THIS WOULD BE CAUGHT
            <cr>            Show fabric information for selected switch
            agent-counters  Show counters for various agents on the Switch
            connections     Show fabric information for selected switch
            details         Show fabric information for selected switch
            interface       <help missing> SHOW_INTERFACE_STATS_COMMAND_DESCRIPTION <====THIS WOULD BE CAUGHT
        '''
        try:
            t = test.Test()
            c = t.controller('master')
        except:
            return False
        else:
            c.cli('')
            cli_string = command + ' ?'
            helpers.log("Sending command ====> %s" % cli_string)
            c.send(str(cli_string), no_cr=True)
            c.expect(r'[\r\n\x07][\w-]+[#>] ')
            content = c.cli_content()
            temp = helpers.strip_cli_output(content)
            temp = helpers.str_to_list(temp)
            helpers.log("********content:************\n%s" % content)
            helpers.log("********new_content:************\n%s" % helpers.prettify(temp))
            c.send(helpers.ctrl('u'))
            c.expect()
            c.cli('')
            if temp[-1] == '':
                num = len(temp) - 1
            else:
                num = len(temp)
            helpers.log("Number of arguments in show command are %s" % num)
            if num == int(cmd_argument_count):
                helpers.log("Correct number of arguments found in CLI help output")
            else:
                helpers.test_error("Correct number of arguments not returned", soft_error)
                return False

            if "<cr> <cr>" in content:
                helpers.test_error("CLI command has an incorrect help string '<cr> <cr>'", soft_error)

            if "<help missing>" in content:
                helpers.test_error("CLI command has an mnissing help", soft_error)

            if (cmd_argument is not None) :
                if (' ' in cmd_argument):
                    new_string = cmd_argument.split()
                    helpers.log("New String is %s" % new_string)
                    helpers.log("Temp is %s" % content)
                    for index in range(len(new_string)):
                        if (str(new_string[index]) in content):
                            helpers.log("Argument %s found in CLI help output" % new_string[index])
                        else:
                            helpers.test_error("Argument %s NOT found in CLI help output. Error was %s " % (new_string[index], soft_error))
                            return False
                else:
                    if (str(cmd_argument) in content):
                        helpers.log("Argument %s found in CLI help output" % cmd_argument)
                    else:
                        helpers.test_error("Argument %s NOT found in CLI help output. Error was %s " % (cmd_argument, soft_error))
                        return False
            return True

    def cli_verify_command(self, command, cmd_argument_count, cmd_argument=None, soft_error=False):
        try:
            t = test.Test()
            c = t.controller('master')
        except:
            return False
        else:
            c.cli(command)
            content = c.cli_content()
            temp_content = content.split('\n')
            # helpers.log("Output is %s \n " % temp_content)
            num = len(temp_content)
            # helpers.log("Length is %s and passed argument is %s \n" % (num, cmd_argument_count))
            if (num != int(cmd_argument_count)) :
                # helpers.log("Number of arguments in CLI Command Output is different")
                return False
            else:
                helpers.log("Correct number of arguments found\n.")
            if ("None" in temp_content[0]) and (num == 1):
                return True
            elif ("None" in temp_content[0]) and (num > 2):
                helpers.log("Number of lines ")
                return False
            if cmd_argument is not None :
                # helpers.log("Argument passed is %s \n" % (cmd_argument))
                for line in temp_content:
                    # helpers.log("Line is %s \n" % line)
                    if (cmd_argument in line) and (num == int(cmd_argument_count)):
                        return True
                return False
            return True

    def convert_integer_to_tcpflag(self, integer_passed):
        binary_number = bin(int(integer_passed))[2:].zfill(6)
        binary_number = map(int, binary_number)
        return binary_number

    def rest_add_bigtap_udf(self, udf_number, udf_anchor, udf_offset, soft_error=False):
        try:
            t = test.Test()
            c = t.controller('master')
        except:
            return False
        else:
            if "l3" in udf_anchor:
                anchor = str("l3-start")
            else:
                anchor = str("l4-start")

            url = '/api/v1/data/controller/applications/bigtap/user-defined-offset/udf%s' % str(udf_number)
            c.rest.patch(url, {"anchor": str(anchor), "offset": int(udf_offset)})
            if not c.rest.status_code_ok():
                helpers.test_log(c.rest.error())
                return False
            else:
                return True

    def rest_return_policy_stats(self, policy, interface_type='filter', interface_name=None, stat_info='packet-count', switch_dpid=None, interface_direction=None, service_name=None):
        '''
        '''
        try:
            t = test.Test()
            c = t.controller('master')
        except:
            return False
        else:
            if str(interface_type) == "filter":
                url = '/api/v1/data/controller/applications/bigtap/view/policy[name="%s"]/filter-interface' % str(policy)
            elif str(interface_type) == "delivery":
                url = '/api/v1/data/controller/applications/bigtap/view/policy[name="%s"]/delivery-interface' % str(policy)
            elif str(interface_type) == "core":
                url = '/api/v1/data/controller/applications/bigtap/view/policy[name="%s"]/core-interface' % str(policy)
            elif str(interface_type) == "service":
                url = '/api/v1/data/controller/applications/bigtap/view/policy[name="%s"]/service-interface' % str(policy)
            else:
                helpers.log("The value passed to function for interface_type is not supported\n")
                return False
            c.rest.get(url)
            content = c.rest.content()
            if len(content) == 1:
                return content[0][str(stat_info)]
            else:
                if str(interface_type) == "core":
                    for i in range(0, len(content)):
                        if content[i]['switch'] == str(switch_dpid) and content[i]['direction'] == str(interface_direction):
                            return content[i][str(stat_info)]
                elif str(interface_type) == "service":
                    for i in range(0, len(content)):
                        if content[i]['switch'] == str(switch_dpid) and content[i]['direction'] == str(interface_direction) and content[i]['service-name'] == str(service_name):
                            return content[i][str(stat_info)]
                else:
                    for i in range(0, len(content)):
                        if content[i]['bigtapinterface'] == str(interface_name):
                            return content[i][str(stat_info)]
                return False

    def rest_return_switch_interface_stats(self, switch_dpid, switch_interface, stat_info):
        '''
            This function returns the specific value after executing command "show switch <dpid> interface <interface_name> details"
            Arguments:
            | switch_dpid | DPID of the switch |
            | switch_interface | Name of the interface|
            | stat_info | Specific index for which value has to be returned|
        '''
        try:
            t = test.Test()
            c = t.controller('master')
        except:
            return False
        else:
            url = '/api/v1/data/controller/core/switch[stats/interface/interface/name="%s"][dpid="%s"]?select=stats/interface[interface/name="%s"]' % (str(switch_interface), str(switch_dpid), str(switch_interface))
            helpers.log("URL is %s" % url)
            c.rest.get(url)
            content = c.rest.content()
            if content[0]['stats']['interface'][0][str(stat_info)]:
                return content[0]['stats']['interface'][0][str(stat_info)]
            else:
                return False

    def rest_return_info_of_core_interface_carrying_flow(self, switch_dpid, policy_name, interface_direction=None, stat_info='interface'):
        '''
        '''
        try:
            t = test.Test()
            c = t.controller('master')
        except:
            return False
        else:
            url = '/api/v1/data/controller/applications/bigtap/view/policy[name="%s"]/core-interface' % str(policy_name)
            c.rest.get(url)
            content = c.rest.content()
            for i in range(0, len(content)):
                if content[i]['switch'] == str(switch_dpid) and content[i]['direction'] == str(interface_direction):
                    return content[i][str(stat_info)]
            return False

    def rest_return_switch_interface_details(self, switch_dpid, switch_interface, return_index):
        '''
            This function returns the specific value after executing command "show switch <dpid> interface <interface_name> details"
            Arguments:
            | switch_dpid | DPID of the switch |
            | switch_interface | Name of the interface|
            | return_index | Specific index for which value has to be returned|
        '''
        try:
            t = test.Test()
            c = t.controller('master')
        except:
            return False
        else:
            url = '/api/v1/data/controller/core/switch[interface/name="%s"][dpid="%s"]?select=interface[name="%s"]' % (str(switch_interface), str(switch_dpid), str(switch_interface))
            c.rest.get(url)
            content = c.rest.content()
            if content[0]['interface'][0][str(return_index)]:
                return content[0]['interface'][0][str(return_index)]
            else:
                return False

    def rest_verify_interswitch_link(self, node1, node2, interface1="ethernet13", interface2="ethernet14"):
        try:
            t = test.Test()
            c = t.controller('master')
            AppCommon = AppController.AppController()
        except:
            return False
        else:
            switch_dpid1 = AppCommon.rest_return_switch_dpid_from_ip(node1)
            switch_dpid2 = AppCommon.rest_return_switch_dpid_from_ip(node2)
            url = '/api/v1/data/controller/topology/link'
            c.rest.get(url)
            content = c.rest.content()
            for element in content:
                if element['src']['switch-dpid'] == str(switch_dpid1)  and element['dst']['switch-dpid'] == str(switch_dpid2):
                    if element['src']['interface']['name'] == str(interface1) and element['dstr']['interface']['name'] == str(interface2):
                        return True
                elif element['src']['switch-dpid'] == str(switch_dpid2)  and element['dst']['switch-dpid'] == str(switch_dpid1):
                    if element['src']['interface']['name'] == str(interface2) and element['dstr']['interface']['name'] == str(interface1):
                        return True
            helpers.test_log("No interswitch links found")
            return False

    def rest_clear_bigtap_statistics(self):
        try:
            t = test.Test()
            c = t.controller('master')
        except:
            return False
        else:
            url = '/api/v1/data/controller/applications/bigtap/clear-stats'
            c.rest.get(url)
            if not c.rest.status_code_ok():
                helpers.test_log(c.rest.error())
                return False
            else:
                return True

    def bt_cli_run(self, node, command, cmd_timeout=45, user='admin', password='adminadmin', soft_error=False):
        """
        Run given CLI command

        Inputs:
        | node | Reference to switch/controller as defined in .topo file |
        | command | CLI command to run |
        | cmd_timeout | Timeout for given command to be executed and controller prompt to be returned |
        | user | Username to use when logging into the node |
        | password | Password for the user |
        | soft_error | Soft Error flag |

        Return Value:
        - True if command executed with no errors, False otherwise
        """

        helpers.test_log("Running command: %s on node %s" % (command, node))
        t = test.Test()
        bsn_common = bsnCommon()
        ip_addr = bsn_common.get_node_ip(node)
        c = t.node_spawn(ip=ip_addr, user=user, password=password)
        try:
            c.cli(command, timeout=cmd_timeout)
            if "Error" in c.cli_content():
                c.close()
                helpers.test_failure(c.cli_content(), soft_error)
                return False
        except:
            c.close()
            helpers.test_failure(c.cli_content(), soft_error)
            return False
        else:
            c.close()
            return True
