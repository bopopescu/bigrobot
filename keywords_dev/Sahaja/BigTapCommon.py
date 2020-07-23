import autobot.helpers as helpers
import autobot.test as test
import re

class BigTapCommon(object):

    def __init__(self):
        pass


###################################################
# All Bigtap Show Commands Go Here:
###################################################
    def rest_show_bigtap_policy(self, policy_name, num_filter_intf, num_delivery_intf):
        '''Parse the output of cli command 'show bigtap policy <policy_name>'

        The first input item `policy_name` which is the name of the policy being parsed
        The second input item `num_filter_intf` is the number of configured Filter Interfaces in the policy
        The third input item `num_delivery_intf` is the number of configured Delivery Interfaces in the policy

        The policy returns True if and only if all the following conditions are True
            a) Policy name is seen correctly in the output
            b) Config-Status is either "active and forwarding" or "active and rate measure"
            c) Type is "Configured"
            d) Runtime Status is "installed"
            e) Delivery interface count is num_delivery_intf
            f) Filter Interface count is num_filter_intf
            g) deltailed status is either "installed to forward" or "installed to measure rate"

        The function executes a REST GET for
            http://<CONTROLLER_IP>:8082/api/v1/data/controller/applications/bigtap/view/policy[name="<POLICY_NAME>"]/info

        Return value is True/False
        '''
        try:
            t = test.Test()
            c = t.controller('main')
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

            if content[0]['config-status'] == "active and forwarding":
                    helpers.test_log("Policy correctly reports config status as : %s" % content[0]['config-status'])
            elif content[0]['config-status'] == "active and rate measure":
                    helpers.test_log("Policy correctly reports config status as : %s" % content[0]['config-status'])
            else:
                    helpers.test_failure("Policy does not correctly report config status as : %s" % content[0]['config-status'])
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

            if content[0]['delivery-interface-count'] == int(num_delivery_intf) :
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

    def rest_get_switch_dpid(self, switch_alias):
        '''Returns switch DPID, given a switch alias

        Input `switchAlias` refers to switch alias

        The function executes a REST GET for
            http://<CONTROLLER_IP>:8082/api/v1/data/controller/core/switch?select=alias
        and greps for switch-alias, and returns switch-dpid

        Return value is switch DPID
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('main')
            try:
                url = '/api/v1/data/controller/core/switch?select=alias'
                c.rest.get(url)
                content = c.rest.content()
                flag = False
                for x in range (0, len(content)):
                    if str(content[x]['alias']) == str(switch_alias):
                        return content[x]['dpid']
                return False
            except:
                return False

    def rest_get_switch_flow(self, switch_alias=None, sw_dpid=None):
        '''Returns number of flows on a switch

        Input 'switch_dpid' is the switch DPID

        The function executes a REST GET for
            http://<CONTROLLER_IP>:8082/api/v1/data/controller/core/switch[dpid="<SWITCH_DPID>"]?select=stats/table
        and returns number of active flows

        Return valuse is the number of active flows on the switch
        '''
        t = test.Test()
        try:
            c = t.controller('main')
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
                    switch_dpid = self.rest_get_switch_dpid(switch_alias)
                else:
                    switch_dpid = sw_dpid
                # url ='http://%s:%s/api/v1/data/controller/core/switch[dpid="%s"]?select=stats/table' % (c.ip,c.http_port,str(switch_dpid))
                url = '/api/v1/data/controller/core/switch[dpid="%s"]?select=stats/table' % (str(switch_dpid))
                c.rest.get(url)
                content = c.rest.content()
            except:
                helpers.test_failure("Could not execute command")
                return False
            else:
                helpers.log("Return value for number of flows is %s" % content[0]['stats']['table'][1]['active-count'])
                return content[0]['stats']['table'][1]['active-count']



###################################################
# All Bigtap Verify Commands Go Here:
###################################################

# Do a rest query and check if a particular key exists in the policy.
# index is the index of the dictionary.
# Values for method are info/rule/filter-interface/delivery-interface/service-interface/core-interface/failed-paths
    def rest_check_policy_key(self, policy_name, method, index, key):
        '''Execute a rest get and verify if a particular key exists in a policy

            Inputs:
                `policy_name` : Policy Name being tested for
                `method`    : Methods can be info/rule/filter-interface/delivery-interface/service-interface/core-interface/failed-paths
                `index`    : Index in the array
                `key`      : Particular key we are looking for.

            Example:
                rest_check_policy_key('testPolicy','ip-proto',0,'rule') would check execute a REST get on "http://<CONTROLLER_IP>:8082/api/v1/data/controller/applications/bigtap/view/policy[name="testPolicy"]/rule
                and return the value "ip-proto"

            Return Value: is value of key if the key exists, False if it does not.
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('main')
            # url ='http://%s:%s/api/v1/data/controller/applications/bigtap/view/policy[name="%s"]/%s' % (c.ip,c.http_port,str(policy_name),str(method))
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
                else :
                    helpers.test_log("ERROR Policy %s does not exist. Error seen: %s" % (str(policy_name), c.rest.result_json()))
                    return False

###################################################
# All Bigtap Configuration Commands Go Here:
###################################################
    def rest_bigtap_setup_interface(self, intf_name, intf_type, intf_nickname, switch_alias=None, sw_dpid=None):
        '''Execute the CLI command 'bigtap role filter interface-name F1'

            Input:
                `switch_dpid` : DPID of the switch
                `intf_name`    : Interface Name viz. etherenet1, ethernet2 etc.
                `intf_type`    : Interface Type viz. filter, delivery, service
                `intf_nickname`    : Nickname for the interface for eg. F1, D1, S1 etc.

            Returns: True if configuration is successful, false otherwise
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('main')
            try:
                if (switch_alias is None and sw_dpid is not None):
                    switch_dpid = sw_dpid
                elif (switch_alias is None and sw_dpid is None):
                    helpers.log('Either Switch DPID or Switch Alias has to be provided')
                    return False
                elif (switch_alias is not None and sw_dpid is None):
                    switch_dpid = self.rest_get_switch_dpid(switch_alias)
                else:
                    switch_dpid = sw_dpid
                # url='http://%s:%s/api/v1/data/controller/applications/bigtap/interface-config[interface="%s"][switch="%s"]' % (c.ip,c.http_port,str(intf_name), str(switch_dpid))
                url = '/api/v1/data/controller/applications/bigtap/interface-config[interface="%s"][switch="%s"]' % (str(intf_name), str(switch_dpid))
                c.rest.put(url, {"interface": str(intf_name), "switch": str(switch_dpid), 'role':str(intf_type), 'name':str(intf_nickname)})
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

    def rest_bigtap_delete_interface_role(self, intf_name, intf_type, intf_nickname, switch_alias=None, sw_dpid=None):
        '''Delete filter/service/delivery interface from switch configuration. Similar to executing the CLI command 'no bigtap role filter interface-name F1'

            Input:
                `switch_dpid` : DPID of the switch
                `intf_name`    : Interface Name viz. etherenet1, ethernet2 etc.
                `intf_type`    : Interface Type viz. filter, delivery, service
                `intf_nickname`    : Nickname for the interface for eg. F1, D1, S1 etc.

            Returns: True if delete is successful, false otherwise
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('main')
            try:
                if (switch_alias is None and sw_dpid is not None):
                    switch_dpid = sw_dpid
                elif (switch_alias is None and sw_dpid is None):
                    helpers.log('Either Switch DPID or Switch Alias has to be provided')
                    return False
                elif (switch_alias is not None and sw_dpid is None):
                    switch_dpid = self.rest_get_switch_dpid(switch_alias)
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

    def rest_bigtap_delete_interface(self, intf_name, switch_alias=None, sw_dpid=None):
        '''Delete interface from switch

            Input:
                `switch_dpid` : DPID of the switch
                `intf_name`    : Interface Name viz. etherenet1, ethernet2 etc.

            Returns: True if delete is successful, false otherwise
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('main')
            try:
                if (switch_alias is None and sw_dpid is not None):
                    switch_dpid = sw_dpid
                elif (switch_alias is None and sw_dpid is None):
                    helpers.log('Either Switch DPID or Switch Alias has to be provided')
                    return False
                elif (switch_alias is not None and sw_dpid is None):
                    switch_dpid = self.rest_get_switch_dpid(switch_alias)
                else:
                    switch_dpid = sw_dpid
                url = '/api/v1/data/controller/core/switch[dpid="%s"]/interface[name=""]' % (str(switch_dpid), str(intf_name))
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

    def rest_bigtap_add_policy(self, rbac_view_name, policy_name, policy_action="inactive"):
        '''Add a bigtap policy.

            Input:
                `rbac_view_name`    :    RBAC View Name for eg. admin-view
                `policy_name`  :    Policy Name
                `policy_action`:    Policy action. The permitted values are "forward" or "rate-measure", default is inactive

            Returns: True if policy configuration is successful, false otherwise
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('main')
            try:
                url = '/api/v1/data/controller/applications/bigtap/view[name="%s"]/policy[name="%s"]' % (str(rbac_view_name), str(policy_name))
                c.rest.put(url, {'name':str(policy_name)})
            except:
                helpers.test_failure(c.rest.error())
                return False
            else:
                try:
                    c.rest.patch(url, {"action": str(policy_action) })
                except:
                    helpers.test_failure(c.rest.error())
                    return False
                else:
                    return True

    def rest_bigtap_delete_policy(self, rbac_view_name, policy_name):
        '''Delete a bigtap policy.

            Input:
                `rbac_view_name`    :    RBAC View Name for eg. admin-view
                `policy_name`  :    Policy Name

            Returns: True if policy delete is successful, False otherwise
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('main')
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

    def rest_bigtap_add_policy_interface(self, rbac_view_name, policy_name, intf_nickname, intf_type):
        '''Add a bigtap policy interface viz. Add a filter-interface and/or delivery-interface under a bigtap policy.

            Input:
                `rbac_view_name`    :    RBAC View Name for eg. admin-view
                `policy_name`  :    Policy Name
                `intf_nickname`    :    Interface Nick-Name for eg. F1 or D1
                `intf_type`    :    Interface Type. Allowed values are `filter` or `delivery`

            Returns: True if policy configuration is successful, false otherwise
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('main')
            try:
                if "filter" in str(intf_type) :
                    intf_type = "filter-group"
                else :
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

    def rest_bigtap_delete_policy_interface(self, rbac_view_name, policy_name, intf_nickname, intf_type):
        '''Delete a bigtap policy interface viz. Delete a filter-interface and/or delivery-interface from a bigtap policy.

            Input:
                `rbac_view_name`    :    RBAC View Name for eg. admin-view
                `policy_name`  :    Policy Name
                `intf_nickname`    :    Interface Nick-Name for eg. F1 or D1
                `intf_type`    :    Interface Type. Allowed values are `filter` or `delivery`

            Returns: True if policy delete is successful, false otherwise
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('main')
            try:
                if "filter" in str(intf_type) :
                    intf_type = "filter-group"
                else :
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

    def rest_bigtap_add_policy_match(self, rbac_view_name, policy_name, match_number, data):
        '''Add a bigtap policy match condition.

            Input:
                `rbac_view_name`    :    RBAC View Name for eg. admin-view
                `policy_name`  :    Policy Name
                `match_number`    :    Match number like the '1' in  '1 match tcp
                `data`    :    Formatted data field like  {"ether-type": 2048, "dst-tp-port": 80, "ip-proto": 6, "sequence": 1}

            Returns: True if policy configuration is successful, false otherwise
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('main')
            try:
                url = '/api/v1/data/controller/applications/bigtap/view[name="%s"]/policy[name="%s"]/rule[sequence=%s]' % (str(rbac_view_name), str(policy_name), str(match_number))
                data_dict = helpers.from_json(data)
                c.rest.put(url, data_dict)
            except:
                helpers.test_failure(c.rest.error())
                return False
            else:
                if not c.rest.status_code_ok():
                    helpers.test_failure(c.rest.error())
                    return False
                else:
                    return True

    def rest_bigtap_delete_policy_match(self, rbac_view_name, policy_name, match_number):
        '''Delete a bigtap policy match condition.

            Input:
                `rbac_view_name`    :    RBAC View Name for eg. admin-view
                `policy_name`  :    Policy Name
                `match_number`    :    Match number like the '1' in  '1 match tcp

            Returns: True if policy delete is successful, false otherwise
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('main')
            try:
                url = '/api/v1/data/controller/applications/bigtap/view[name="%s"]/policy[name="%s"]/rule[sequence="%s"]' % (str(rbac_view_name), str(policy_name), str(match_number))
                c.rest.delete(url, {})
            except:
                helpers.test_failure(c.rest.error())
                return False
            else:
                return True

# Add a service with Pre-Service and Post Service interface.
    def rest_bigtap_add_service(self, service_name, pre_service_intf_nickname, post_service_intf_nickname):
        '''Add a bigtap service.

            Input:
                `service_name`        : Name of Service
                `pre_service_intf_nickname`        : Name of pre-service interface
                `post_service_intf_nickname`       : Name of post-service interface

            Returns: True if service addition is successful, false otherwise

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
            c = t.controller('main')
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
    def rest_bigtap_delete_service(self, service_name) :
        '''Delete a bigtap service.

            Input:
                `service_name`        : Name of Service

            Returns: True if service deletion is successful, false otherwise

        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('main')
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

    def rest_bigtap_add_interface_service(self, service_name, intf_type, intf_nickname):
        '''Add a service interface to a service. This is similar to executing CLI command "post-service S1-LB7_E4-HP1_E4-POST"

            Input:
                `service_name`        : Name of Service
                `intf_type`           : Interface Type. Acceptable values are `pre` or `post`
                `post_service_intf_nickname`       : Name of pre/post-service interface for e.g. S1-LB7_E4-HP1_E4-POST

            Returns: True if addition of interface to service is successful, false otherwise

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
            c = t.controller('main')
            try:
                if "pre" in str(intf_type) :
                    url_add_intf = '/api/v1/data/controller/applications/bigtap/service[name="%s"]/pre-group[name="%s"]' % (str(service_name), str(intf_nickname))
                else :
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

    def rest_bigtap_delete_interface_service(self, service_name, intf_nickname, intf_type) :
        '''Delete an interface from a service. This is similar to executing CLI command "no post-service S1-LB7_E4-HP1_E4-POST"

            Input:
                `service_name`        : Name of Service
                `intf_type`           : Interface Type. Acceptable values are `pre` or `post`
                `post_service_intf_nickname`       : Name of pre/post-service interface for e.g. S1-LB7_E4-HP1_E4-POST

            Returns: True if addition of interface to service is successful, false otherwise

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
            c = t.controller('main')
            try:
                if "pre" in str(intf_type) :
                    url_add_intf = '/api/v1/data/controller/applications/bigtap/service[name="%s"]/pre-group[name="%s"]' % (str(service_name), str(intf_nickname))
                else :
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

    def rest_bigtap_add_service_to_policy(self, rbac_view_name, policy_name, service_name, sequence_number) :
        '''Add a service to a policy. This is similar to executing CLI command "use-service S1-LB7 sequence 1"

            Input:
                `rbac_view_name`           :    RBAC View Name for eg. admin-view
                `policy_name`         :    Policy Name
                `service_name`        : Name of Service
                `sequence_number`     : Sequence number of the policy, to determine order in which policies are processed

            Returns: True if addition of service to policy is successful, false otherwise

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
            c = t.controller('main')
            try:
                url_to_add = '/api/v1/data/controller/applications/bigtap/view[name="%s"]/policy[name="%s"]/service[sequence=%s]' % (str(rbac_view_name), str(policy_name), str(sequence_number))
                c.rest.put(url_to_add, {"name":str(service_name), "sequence" : int(sequence_number)})
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

    def rest_bigtap_delete_service_from_policy(self, rbac_view_name, policy_name, service_name) :
        '''Delete a service from a policy. This is similar to executing CLI command "no use-service S1-LB7 sequence 1"

            Input:
                `rbac_view_name`           :    RBAC View Name for eg. admin-view
                `policy_name`         :    Policy Name
                `service_name`        : Name of Service

            Returns: True if deletion of service from policy is successful, false otherwise

        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('main')
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
    def rest_bigtap_change_policy_action(self, rbac_view_name, policy_name, policy_action):
        '''Change a bigtap policy action from forward --> Rate-Measure, Forward --> Inactive, Rate-Measure--> Forward, Rate-Measure--> Inactive etc.

           Input:
                `rbac_view_name`           :    RBAC View Name for eg. admin-view

                `policy_name`         :    Policy Name

                `policy_action`       :    Desired action. Values are `forward`, `rate-measure` and `inactive`

           Returns: True if action change for policy is successful, false otherwise
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
            c = t.controller('main')
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

# Disable bigtap feature overlap/inport-mask/tracked-host/l3-l4-mode
    def rest_bigtap_disable_feature(self, feature_name):
        '''Disable a bigtap feature

           Input:
                `feature_name`           :    Bigtap Feature Name. Currently allowed feature names are `overlap`,`inport-mask`,`tracked-host`,`l3-l4-mode`

           Returns: True if feature is disabled successfully, false otherwise
            Examples:
                | rest disable feature  |  overlap |
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('main')
            try:
                url = '/api/v1/data/controller/applications/bigtap/feature'
                c.rest.patch(url, {str(feature_name): False})
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

# Enable bigtap feature overlap/inport-mask/tracked-host/l3-l4-mode
    def rest_bigtap_enable_feature(self, feature_name):
        '''Enable a bigtap feature

           Input:
                `feature_name`           :    Bigtap Feature Name. Currently allowed feature names are `overlap`,`inport-mask`,`tracked-host`,`l3-l4-mode`

           Returns: True if feature is enabled successfully, false otherwise
            Examples:
                | rest enable feature  |  overlap |
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('main')
            try:
                url = '/api/v1/data/controller/applications/bigtap/feature'
                c.rest.patch(url, {str(feature_name): True})
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

# Compare coreswitch flows
    def rest_compare_coreswitch_flows(self, flow_1, flow_2, flow_value_1, flow_value_2):
        '''Compare coreswitch flow counts. Useful when we have multiple core-switches.

            Inputs:
                flow_1: Number of flows on core switch 1
                flow_2: Number of flows on core switch 2
                flow_value_1: Desired number of flows on switch 1 or switch 2
                flow_value_2: Desired number of flows on switch 1 or switch 2

            Returns True if flow is found on switch
        '''
        if ((flow_1 == flow_value_1) and (flow_2 == flow_value_2)) or ((flow_2 == flow_value_1) and (flow_1 == flow_value_2)) :
            return True
        else :
            return False

    def rest_cleanconfig_switch_config(self):
        ''' Get all the list of switches configured and delete first the role and then delete the switch

        Input: none

        example show command: "show running-config switch"

        Return value is if the deletion succeeded or not
        '''
        t = test.Test()
        try:
            c = t.controller('main')
        except:
            return False
        show_url = '/api/v1/data/controller/applications/bigtap/interface-config?config=true'
        c.rest.get(show_url)
        switch_data = c.rest.content()
        url = '/api/v1/data/controller/applications/bigtap/interface-config[interface="%s"][switch="%s"]'
       # url = '/api/v1/data/controller/applications/bigtap/interface-config[interface="%s"][switch="%s"] {"role": "filter"}'
        helpers.test_log("type of switch_data is %s" % (type(switch_data)))
        if len(switch_data) != 0:
            for intf in switch_data:
                helpers.test_log("type of intf is %s" % (type(intf)))
                if "interface" and "name" and "role" and "switch" in intf.keys():
                    helpers.test_log("Now will be deleting :: %s %s %s %s" % (intf["switch"], intf["role"], intf["interface"], intf["name"]))
                    final_url = url % (intf["interface"], intf["switch"])
                    c.rest.delete(url % (intf["interface"], intf["switch"]), {'role':intf["role"]})
        else:
            helpers.test_log("Switch data is empty no switches configured")
            return True

        # Make sure there is no config left after deletion of roles
        c.rest.get(show_url)
        role_data_after_delete = c.rest.content()
        if len(role_data_after_delete) == 0:
            helpers.test_log("All the roles have been deleted for all the switch interfaces")
        else:
            helpers.test_failure("Few roles are still left %s" % (role_data_after_delete))
            return False

        # Delete Switches as roles are deleted
        switch_url = '/api/v1/data/controller/core/switch?config=true'
        c.rest.get(switch_url)
        data = c.rest.content()
        for switch in data:
            if "dpid" in switch.keys():
                helpers.test_log("Going to delete: %s" % (switch["dpid"]))
                switch_delete_url = '/api/v1/data/controller/core/switch[dpid="%s"]' % (switch["dpid"])
                c.rest.delete(switch_delete_url)
        # Make sure all switches have been deleted
        c.rest.get(switch_url)
        data = c.rest.content()
        if len(data) == 0:
             helpers.test_log("All the switches have been deleted")
        else:
             helpers.test_failure("Few switches have not been deleted %s" % (data))



    def rest_cleanconfig_bigtap_add_grp(self):
        '''Get all the list of address groups and delete them

        Input: None

        show command used: show running-config bigtap address-group

        Output: Return false if any address-groups are left after deletion

        '''
        t = test.Test()
        try:
            c = t.controller('main')
        except:
            return False

        show_url = "/api/v1/data/controller/applications/bigtap/ip-address-set?config=true"
        try:
            c.rest.get(show_url)
            addr_grp_data = c.rest.content()
        except:
            helpers.test_failure(c.rest.error())
            return False
        delete_url = '/api/v1/data/controller/applications/bigtap/ip-address-set[name="%s"]'
        if len(addr_grp_data) != 0:
            for add_grp in addr_grp_data:
                helpers.test_log("type of add_grp is %s" % (type(add_grp)))
                if "name" in add_grp.keys():
                    c.rest.delete(delete_url % (add_grp['name']))
                else:
                    helpers.test_failure("There is no name field for %s" % add_grp)
        else:
            helpers.test_log("Add-grp data is empty")
            return True

        # Make sure all the address-groups have been deleted
        c.rest.get(show_url)
        delete_addr_grp_data = c.rest.content()
        if len(delete_addr_grp_data) == 0:
            helpers.test_log("All the address-groups have been deleted")
        else:
            helpers.test_failure("Few address-groups have not been deleted %s" % (delete_addr_grp_data))
            return False


    def rest_cleanconfig_bigtap_user_defined_offset(self):
        '''Get all the user-defined-groups and delete them

        Input: None

        show command used: show running-config bigtap user-defined-group

        Output: Return false if groups are not deleted properly
        '''
        t = test.Test()
        try:
            c = t.controller('main')
        except:
            return False

        show_url = "/api/v1/data/controller/applications/bigtap/user-defined-offset?config=true"
        try:
            c.rest.get(show_url)
            show_data = c.rest.content()
        except:
            helpers.test_failure(c.rest.error())
            return False
        delete_url = "/api/v1/data/controller/applications/bigtap/user-defined-offset/%s/anchor {}"
        if len(show_data) != 0:
            for ugrp in show_data:
                for grp in ugrp.keys():
                    helpers.test_log("Deleting the group %s" % (grp))
                    c.rest.delete(delete_url % (grp))
        else:
            helpers.test_log("There are no user-defined offsets to delete")
            return True
        # Make sure the deletion is successful
#        c.rest.get(show_url)
#        delete_ugrp_data = c.rest.content()
#        if len(delete_ugrp_data) == 1:
#            helpers.test_log("All the user-defined-groups have been deleted")
#        else:
#            helpers.test_failure("Few user-defined-groups have not been deleted %s" % (delete_ugrp_data))
#            return False


    def rest_cleanconfig_bigtap_policy(self):
        '''Get all the policy and associated view names and delete them

        Input: None

        show commands used: 'show running-config bigtap policy', 'show bigtap rbac-permission'

        Output: Return false if deletion is not successful
        '''
        t = test.Test()
        try:
            c = t.controller('main')
        except:
            return False

        delete_url = "/api/v1/data/controller/applications/bigtap/view[name='%s']/policy[name='%s'] {}"
        show_policy_url = "/api/v1/data/controller/applications/bigtap/view/policy?config=true"
        show_view_url = "/api/v1/data/controller/applications/bigtap/view?select=policy/name"

        c.rest.get(show_policy_url)
        policy_data = c.rest.content()

        c.rest.get(show_view_url)
        view_data = c.rest.content()

        # GET THE POLICY NAMES
        lis_p = []
        if len(policy_data) != 0:
            for pol in policy_data:
                lis_p.append(pol['name'])
        else:
            helpers.test_log("No list of policies to delete")
            return True

        for pol_n in lis_p:
            for elem in view_data:
                for pol in elem['policy']:
                    if cmp(pol_n, pol['name']) == 0:
                        helpers.test_log("Will be deleting policy %s with view %s" % (pol_n, elem['name']))
                        c.rest.delete(delete_url % (elem['name'], pol_n))

        c.rest.get(show_policy_url)
        delete_policy_data = c.rest.content()
        if len(delete_policy_data) == 0:
             helpers.test_log("All the user-defined-groups have been deleted")
        else:
             helpers.test_failure("Few policies have not been deleted %s" % (delete_policy_data))
             return False

    def write_version_to_file(self):
        '''Touch a file and write the version of the controller to file
        '''
        t = test.Test()
        try:
            c = t.controller('main')
        except:
            return False
        show_version_url = "/rest/v1/system/version"
        vf = open("/var/lib/libvirt/bigtap_regressions/ver.txt", "wb")
        c.rest.get(show_version_url)
        ver_data = c.rest.content()
        helpers.test_log("Version string got is: %s" % (ver_data))
        if ver_data:
            ver = re.search('(.+?)(\(.+)\)', ver_data[0]["controller"])
            if ver:
                vf.write("%s %s" % (ver.group(1), ver.group(2)))
            else:
                helpers.test_failure("Did not match the version format, got %s" % (ver))
                return False
        else:
            helpers.test_failure("Version string is empty")
            return False





