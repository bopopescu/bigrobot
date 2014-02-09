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

class BigTap(object):

    def __init__(self):
        pass

###################################################
# All Bigtap Show Commands Go Here:
###################################################


    def rest_show_switch_flow(self, switch_alias=None, sw_dpid=None, return_value=None):
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
        except:
            return False

        else:
            try:
                if (switch_alias is None and sw_dpid is not None):
                    switch_dpid = sw_dpid
                elif (switch_alias is None and sw_dpid is None):
                    helpers.log('Either Switch DPID or Switch Alias has to be provided')
                    return False
                elif (switch_alias is not None and sw_dpid is None):
                    switch_dpid = self.rest_show_switch_dpid(switch_alias)
                else:
                    switch_dpid = sw_dpid
                url = '/api/v1/data/controller/core/switch[dpid="%s"]?select=stats/table' % (str(switch_dpid))
                c.rest.get(url)
                content = c.rest.content()
            except:
                helpers.test_failure("Could not execute command")
                return False
            else:
                if return_value:
                    return content[0]['stats']['table'][1][return_value]
                else:
                    return content[0]['stats']['table'][1]['active-count']

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
            helpers.test_failure("Policy does not correctly report policy name  : %s" % content[0]['name'])
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
                helpers.test_failure("ERROR: Policy does not correctly report policy name  : %s" % c.rest.content()[0]['policy'][0]['name'])
                return False
        helpers.test_failure("ERROR: Policy does not correctly report ")
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
            helpers.test_failure("ERROR: Policy does not correctly report policy name  : %s" % input_dict['name'])
            return False

        if match:
            temp = input_dict['rule']
            helpers.test_log("INFO: Policy  %s has %d of matches" % (policy, len(temp)))
            return len(temp)

        return True
###################################################
# All Bigtap Verify Commands Go Here:
###################################################
    def rest_verify_bigtap_policy(self, policy_name, num_filter_intf=None, num_delivery_intf=None, action='forward'):
        '''
        Objective:
        Parse the output of cli command 'show bigtap policy <policy_name>'
              
        Inputs:
        | `policy_name` | Name of the policy being parsed | 
        | `num_filter_intf` | Number of configured Filter Interfaces in the policy | 
        | `num_delivery_intf` | Number of configured Delivery Interfaces in the policy | 
        
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
            url = '/api/v1/data/controller/applications/bigtap/view/policy[name="%s"]/info' % (policy_name)
            c.rest.get(url)
            if not c.rest.status_code_ok():
                helpers.test_failure(c.rest.error())
            content = c.rest.content()
        except:
            helpers.test_failure("Could not execute command")
            return False
        else:
            if content[0]['name'] == str(policy_name):
                helpers.test_log("Policy correctly reports policy name as : %s" % content[0]['name'])
            else:
                helpers.test_failure("Policy does not correctly report policy name  : %s" % content[0]['name'])
                return False

            if (content[0]['config-status'] == "active and forwarding") and (str(action) == "forward"):
                helpers.test_log("Policy correctly reports config status as : %s" % content[0]['config-status'])
            elif (content[0]['config-status'] == "active and rate measure") and (str(action) == "rate-measure"):
                helpers.test_log("Policy correctly reports config status as : %s" % content[0]['config-status'])
            elif (content[0]['config-status'] == "inactive") and (str(action) == "inactive"):
                helpers.test_log("Policy correctly reports config status as : %s" % content[0]['config-status'])
            else:
                helpers.test_failure("Policy does not correctly report config status as : %s and passed action value is %s" % (content[0]['config-status'], str(action)))
                return False

            if content[0]['type'] == "Configured":
                helpers.test_log("Policy correctly reports type as : %s" % content[0]['type'])
            else:
                helpers.test_failure("Policy does not correctly report type as : %s" % content[0]['type'])
                return False

            if content[0]['runtime-status'] == "installed":
                helpers.test_log("Policy correctly reports runtime status as : %s" % content[0]['runtime-status'])
            else:
                helpers.test_failure("Policy does not correctly report runtime status as : %s" % content[0]['runtime-status'])
                return False

            if content[0]['delivery-interface-count'] == int(num_delivery_intf):
                helpers.test_log("Policy correctly reports number of delivery interfaces as : %s" % content[0]['delivery-interface-count'])
            else:
                helpers.test_failure("Policy does not correctly report number of delivery interfaces  : %s" % content[0]['delivery-interface-count'])
                return False

            if content[0]['filter-interface-count'] == int(num_filter_intf):
                helpers.test_log("Policy correctly reports number of filter interfaces as : %s" % content[0]['filter-interface-count'])
            else:
                helpers.test_failure("Policy does not correctly report number of filter interfaces  : %s" % content[0]['filter-interface-count'])
                return False

            if content[0]['detailed-status'] == "installed to forward":
                helpers.test_log("Policy correctly reports detailed status as : %s" % content[0]['detailed-status'])
            elif content[0]['detailed-status'] == "installed to measure rate":
                helpers.test_log("Policy correctly reports detailed status as : %s" % content[0]['detailed-status'])
            else:
                helpers.test_failure("Policy does not correctly report detailed status as : %s" % content[0]['detailed-status'])
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
                if not c.rest.status_code_ok():
                    helpers.test_failure(c.rest.error())
                    return False
                if(c.rest.content()):
                    content = c.rest.content()
                    return content[index][key]
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


###################################################
# All Bigtap Configuration Commands Go Here:
###################################################
#    def rest_add_switch_alias(self, switch_dpid, switch_alias):
#        '''Set Switch alias via command "switch-alias <switch_alias>"
#
#            Input:
#                `switch_dpid`        DPID of switch
#                `switch_alias`        Desired alias for switch
#
#            Return: true if configuration is successful, false otherwise
#        '''
#        try:
#            t = test.Test()
#        except:
#            return False
#        else:
#            c = t.controller('master')
#            try:
#                url = '/api/v1/data/controller/core/switch[dpid="%s"]' % (str(switch_dpid))
#                c.rest.patch(url, {"alias": str(switch_alias)})
#            except:
#                helpers.test_failure(c.rest.error())
#                return False
#            else:
#                helpers.test_log(c.rest.content_json())
#                return True


    def rest_add_interface_role(self, intf_name, intf_type, intf_nickname, switch_alias=None, sw_dpid=None):
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
            AppCommon = AppController.AppController()
            try:
                if (switch_alias is None and sw_dpid is not None):
                    switch_dpid = sw_dpid
                elif (switch_alias is None and sw_dpid is None):
                    helpers.log('Either Switch DPID or Switch Alias has to be provided')
                    return False
                elif (switch_alias is not None and sw_dpid is None):
                    switch_dpid = AppCommon.rest_return_switch_dpid_from_alias(switch_alias)
                else:
                    switch_dpid = sw_dpid
                url = '/api/v1/data/controller/applications/bigtap/interface-config[interface="%s"][switch="%s"]' % (str(intf_name), str(switch_dpid))
                c.rest.put(url, {"interface": str(intf_name), "switch": str(switch_dpid), 'role':str(intf_type), 'name':str(intf_nickname)})
            except:
                helpers.test_failure(c.rest.error())
                return False
            else:
                if not c.rest.status_code_ok():
                    helpers.test_log(c.rest.error())
                    return False
                else:
                    helpers.test_log(c.rest.content_json())
                    return True

    def rest_delete_interface_role(self, intf_name, intf_type, intf_nickname, switch_alias=None, sw_dpid=None):
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
            AppCommon = AppController.AppController()
            try:
                if (switch_alias is None and sw_dpid is not None):
                    switch_dpid = sw_dpid
                elif (switch_alias is None and sw_dpid is None):
                    helpers.test_log('Either Switch DPID or Switch Alias has to be provided')
                    return False
                elif (switch_alias is not None and sw_dpid is None):
                    switch_dpid = AppCommon.rest_return_switch_dpid_from_alias(switch_alias)
                else:
                    switch_dpid = sw_dpid

                url = '/api/v1/data/controller/applications/bigtap/interface-config[interface="%s"][switch="%s"]' % (str(intf_name), str(switch_dpid))
                c.rest.delete(url, {'role':str(intf_type), "name": str(intf_nickname)})
            except:
                helpers.test_failure(c.rest.error())
                return False
            else:
                if not c.rest.status_code_ok():
                    helpers.test_failure(c.rest.error())
                    return False
                else:
                    return True

    def rest_delete_interface(self, intf_name, switch_alias=None, sw_dpid=None):
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
            AppCommon = AppController.AppController()
            try:
                if (switch_alias is None and sw_dpid is not None):
                    switch_dpid = sw_dpid
                elif (switch_alias is None and sw_dpid is None):
                    helpers.log('Either Switch DPID or Switch Alias has to be provided')
                    return False
                elif (switch_alias is not None and sw_dpid is None):
                    switch_dpid = AppCommon.rest_return_switch_dpid_from_alias(switch_alias)
                else:
                    switch_dpid = sw_dpid
                url = '/api/v1/data/controller/core/switch[dpid="%s"]/interface[name="%s"]' % (str(switch_dpid), str(intf_name))
                c.rest.delete(url, {})
            except:
                helpers.test_failure(c.rest.error())
                return False
            else:
                if not c.rest.status_code_ok():
                    helpers.test_failure(c.rest.error())
                    return False
                else:
                    return True

    def rest_add_policy(self, rbac_view_name, policy_name, policy_action="inactive"):
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
                c.rest.put(url, {'name':str(policy_name)})
            except:
                helpers.test_failure(c.rest.error())
                return False
            else:
                try:
                    c.rest.patch(url, {"action":str(policy_action)})
                except:
                    helpers.test_failure(c.rest.error())
                    return False
                else:
                    return True

    def rest_delete_policy(self, rbac_view_name, policy_name):
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
                c.rest.delete(url, {})
            except:
                helpers.test_failure(c.rest.error())
                return False
            else:
                if not c.rest.status_code_ok():
                    helpers.test_failure(c.rest.error())
                    return False
                else:
                    return True

    def rest_add_policy_interface(self, rbac_view_name, policy_name, intf_nickname, intf_type):
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
                c.rest.put(url, {"name": str(intf_nickname)})
            except:
                helpers.test_failure(c.rest.error())
                return False
            else:
                if not c.rest.status_code_ok():
                    helpers.test_failure(c.rest.error())
                    return False
                else:
                    return True

    def rest_delete_policy_interface(self, rbac_view_name, policy_name, intf_nickname, intf_type):
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
                c.rest.delete(url, {})
            except:
                helpers.test_failure(c.rest.error())
                return False
            else:
                if not c.rest.status_code_ok():
                    helpers.test_failure(c.rest.error())
                    return False
                else:
                    return True

    def rest_add_policy_match(self, rbac_view_name, policy_name, match_number, data):
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
                url = '/api/v1/data/controller/applications/bigtap/view[name="%s"]/policy[name="%s"]/rule[sequence=%s]' % (str(rbac_view_name), str(policy_name), str(match_number))
                data_dict = helpers.from_json(data)
                c.rest.put(url, data_dict)
            except:
                helpers.test_failure(c.rest.error())
                return False
            else:
                if not c.rest.status_code_ok():
                    return False
                else:
                    return True

    def rest_delete_policy_match(self, rbac_view_name, policy_name, match_number):
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
                url = '/api/v1/data/controller/applications/bigtap/view[name="%s"]/policy[name="%s"]/rule[sequence="%s"]' % (str(rbac_view_name), str(policy_name), str(match_number))
                c.rest.delete(url, {})
            except:
                helpers.test_failure(c.rest.error())
                return False
            else:
                return True

# Add a service with Pre-Service and Post Service interface.
    def rest_add_service(self, service_name, pre_service_intf_nickname, post_service_intf_nickname):
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
                helpers.test_failure(c.rest.error())
                return False
            else:
                try:
                    # Add Pre-Service Interface
                    url_add_intf = '/api/v1/data/controller/applications/bigtap/service[name="%s"]/pre-group[name="%s"]' % (str(service_name), str(pre_service_intf_nickname))
                    c.rest.put(url_add_intf, {"name":str(pre_service_intf_nickname)})
                except:
                    helpers.test_failure(c.rest.error())
                    return False
                else:
                    try:
                        # Add Post-Service Interface
                        url_add_intf = '/api/v1/data/controller/applications/bigtap/service[name="%s"]/post-group[name="%s"]' % (str(service_name), str(post_service_intf_nickname))
                        c.rest.put(url_add_intf, {"name":str(post_service_intf_nickname)})
                    except:
                        helpers.test_failure(c.rest.error())
                        return False
                    else:
                        helpers.test_log(c.rest.content_json())
                        return True

# Delete a service
    def rest_delete_service(self, service_name):
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
                c.rest.delete(url, {})
            except:
                helpers.test_failure(c.rest.error())
                return False
            else:
                if not c.rest.status_code_ok():
                    helpers.test_failure(c.rest.error())
                    return False
                else:
                    helpers.test_log(c.rest.content_json())
                    return True

    def rest_add_interface_service(self, service_name, intf_type, intf_nickname):
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
                c.rest.post(url_add_intf, {"name":str(intf_nickname)})
            except:
                helpers.test_failure(c.rest.error())
                return False
            else:
                if not c.rest.status_code_ok():
                    helpers.test_failure(c.rest.error())
                    return False
                else:
                    helpers.test_log(c.rest.content_json())
                    return True

    def rest_delete_interface_service(self, service_name, intf_nickname, intf_type):
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
                c.rest.delete(url_add_intf, {})
            except:
                helpers.test_failure(c.rest.error())
                return False
            else:
                if not c.rest.status_code_ok():
                    helpers.test_failure(c.rest.error())
                    return False
                else:
                    helpers.test_log(c.rest.content_json())
                    return True

    def rest_add_service_to_policy(self, rbac_view_name, policy_name, service_name, sequence_number):
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
                c.rest.put(url_to_add, {"name":str(service_name), "sequence": int(sequence_number)})
            except:
                helpers.test_failure(c.rest.error())
                return False
            else:
                if not c.rest.status_code_ok():
                    helpers.test_failure(c.rest.error())
                    return False
                else:
                    helpers.test_log(c.rest.content_json())
                    return True

    def rest_delete_service_from_policy(self, rbac_view_name, policy_name, service_name):
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
                c.rest.delete(url, {})
            except:
                helpers.test_failure(c.rest.error())
                return False
            else:
                if not c.rest.status_code_ok():
                    helpers.test_failure(c.rest.error())
                    return False
                else:
                    helpers.test_log(c.rest.content_json())
                    return True

# Change policy action
    def rest_add_policy_action(self, rbac_view_name, policy_name, policy_action):
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
                c.rest.patch(url, {"action":str(policy_action)})
            except:
                helpers.test_failure(c.rest.error())
                return False
            else:
                if not c.rest.status_code_ok():
                    helpers.test_failure(c.rest.error())
                    return False
                else:
                    helpers.test_log(c.rest.content_json())
                    return True

# Alias
    def rest_update_policy_action(self, rbac_view_name, policy_name, policy_action):
        return self.rest_add_policy_action(rbac_view_name, policy_name, policy_action)


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
                url = '/api/v1/data/controller/applications/bigtap/feature'
                c.rest.patch(url, {str(feature_name): False})
            except:
                helpers.test_failure(c.rest.error())
                return False
            else:
                if not c.rest.status_code_ok():
                    helpers.test_log(c.rest.error())
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
            | `feature_name` | Bigtap Feature Name. \n Currently allowed feature names are `overlap`,`inport-mask`,`tracked-host`,`l3-l4-mode` | 
            
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
                url = '/api/v1/data/controller/applications/bigtap/feature'
                c.rest.patch(url, {str(feature_name): True})
            except:
                helpers.test_failure(c.rest.error())
                return False
            else:
                if not c.rest.status_code_ok():
                    helpers.test_log(c.rest.error())
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
                helpers.test_failure(c.rest.error())
        else:
            url = '/api/v1/data/controller/applications/bigtap/view/policy?select=info'
            c.rest.get(url)
            content = c.rest.content()
            if not c.rest.status_code_ok():
                helpers.test_failure(c.rest.error())
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
                    helpers.test_failure(c.rest.error())
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
        t = test.Test()
        c = t.controller('master')
        url = '/api/v1/data/controller/applications/bigtap/ip-address-set[name="%s"]' % (str(name))
        c.rest.put(url, {"name": str(name)})
        helpers.sleep(1)

        url = '/api/v1/data/controller/applications/bigtap/ip-address-set[name="%s"]' % (str(name))

        c.rest.patch(url, {"ip-address-type": str(addr_type)})
        helpers.sleep(1)
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
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
        t = test.Test()
        c = t.controller('master')

        url = ('/api/v1/data/controller/applications/bigtap/ip-address-set[name="%s"]/address-mask-set[ip="%s"][ip-mask="%s"]'
               % (str(name), str(addr), str(mask)))

        c.rest.put(url, {"ip": str(addr), "ip-mask": str(mask)})
        helpers.sleep(1)
        helpers.test_log(c.rest.content_json())

        if not c.rest.status_code_ok():
            return False
        else:
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
