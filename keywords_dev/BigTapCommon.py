import autobot.helpers as helpers
import autobot.test as test


class BigTapCommon(object):
    
    def __init__(self):
        t = test.Test()
        c = t.controller()
        url = '%s/auth/login' % c.base_url
        helpers.log("url: %s" % url)
        result = c.rest.post(url, {"user":"admin", "password":"adminadmin"})
        helpers.log("result: %s" % helpers.to_json(result))
        session_cookie = result['content']['session_cookie']
        c.rest.set_session_cookie(session_cookie)

###################################################
# All Bigtap Show Commands Go Here:
###################################################
    def rest_show_bigtap_policy(self, policyName,numFIntf,numDIntf):
        '''Parse the output of cli command 'show bigtap policy <policy_name>'
        
        The first input item `policyName` which is the name of the policy being parsed
        The second input item `numFIntf` is the number of configured Filter Interfaces in the policy
        The third input item `numDIntf` is the number of configured Delivery Interfaces in the policy
        
        The policy returns True if and only if all the following conditions are True 
            a) Policy name is seen correctly in the output
            b) Config-Status is either "active and forwarding" or "active and rate measure"
            c) Type is "Configured"
            d) Runtime Status is "installed"
            e) Delivery interface count is numDIntf
            f) Filter Interface count is numFIntf
            g) deltailed status is either "installed to forward" or "installed to measure rate"
        
        The function executes a REST GET for 
            http://<CONTROLLER_IP>:8082/api/v1/data/controller/applications/bigtap/view/policy[name="<POLICY_NAME>"]/info
        
        Return value is True/False
        '''
        t = test.Test()
        c = t.controller()
        helpers.test_log("Input arguments: policy = %s" % policyName )
        c.http_port=8082
        url ='http://%s:%s/api/v1/data/controller/applications/bigtap/view/policy[name="%s"]/info' % (c.ip,c.http_port, policyName)
        c.rest.get(url)
        helpers.test_log("Ouput: %s" % c.rest.result_json())
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
        content = c.rest.content()
                
        if content[0]['name'] == str(policyName):
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
            
        if content[0]['delivery-interface-count'] == int(numDIntf) :
                helpers.test_log("Policy correctly reports number of delivery interfaces as : %s" % content[0]['delivery-interface-count'])
        else:
                helpers.test_failure("Policy does not correctly report number of delivery interfaces  : %s" % content[0]['delivery-interface-count'])                
                return False
                      
        if content[0]['filter-interface-count'] == int(numFIntf):
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

    def rest_show_switch_dpid(self,switchAlias):
        '''Returns switch DPID, given a switch alias
        
        Input `switchAlias` refers to switch alias
        
        The function executes a REST GET for 
            http://<CONTROLLER_IP>:8082/api/v1/data/controller/core/switch?select=alias
        and greps for switch-alias, and returns switch-dpid
        
        Return value is switch DPID
        '''
        t = test.Test()
        c = t.controller()
        aliasExists=0
        c.http_port=8082
        url ='http://%s:%s/api/v1/data/controller/core/switch?select=alias'   % (c.ip,c.http_port)
        c.rest.get(url)
        content = c.rest.content()
        for i in range(0,len(content)) :
                if content[i]['alias'] == str(switchAlias) :
                        switchDpid = content[i]['dpid']
                        aliasExists=1
        if(aliasExists):
            return switchDpid
        else:
            return False
    
    def rest_show_switch_flow(self,switchDpid):
        '''Returns number of flows on a switch
        
        Input 'switchDpid' is the switch DPID
        
        The function executes a REST GET for 
            http://<CONTROLLER_IP>:8082/api/v1/data/controller/core/switch[dpid="<SWITCH_DPID>"]?select=stats/table
        and returns number of active flows
        
        Return valuse is the number of active flows on the switch
        '''
        t = test.Test()
        c = t.controller()
        c.http_port=8082
        url ='http://%s:%s/api/v1/data/controller/core/switch[dpid="%s"]?select=stats/table' % (c.ip,c.http_port,str(switchDpid))
        c.rest.get(url)
        content = c.rest.content()
        helpers.log("Return value for number of flows is %s" % content[0]['stats']['table'][1]['active-count'])
        return content[0]['stats']['table'][1]['active-count']

###################################################
# All Bigtap Verify Commands Go Here:
###################################################

# Do a rest query and check if a particular key exists in the policy.
# index is the index of the dictionary.
# Values for method are info/rule/filter-interface/delivery-interface/service-interface/core-interface/failed-paths    
    def rest_check_policy_key(self,policyName,method,index,key):
        '''Execute a rest get and verify if a particular key exists in a policy
        
            Inputs:
                `policyName` : Policy Name being tested for
                `method`    : Methods can be info/rule/filter-interface/delivery-interface/service-interface/core-interface/failed-paths
                `index`    : Index in the array
                `key`      : Particular key we are looking for.
            
            Example:
                rest_check_policy_key('testPolicy','ip-proto',0,'rule') would check execute a REST get on "http://<CONTROLLER_IP>:8082/api/v1/data/controller/applications/bigtap/view/policy[name="testPolicy"]/rule
                and return the value "ip-proto"
            
            Return Value: is value of key if the key exists, False if it does not.
        '''
        t = test.Test()
        c = t.controller()
        c.http_port=8082
        url ='http://%s:%s/api/v1/data/controller/applications/bigtap/view/policy[name="%s"]/%s' % (c.ip,c.http_port,str(policyName),str(method))
        c.rest.get(url)
        helpers.test_log("Ouput: %s" % c.rest.result_json())
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
        if(c.rest.content()):
            content = c.rest.content()
            return content[index][key]
        else :
            helpers.test_log("ERROR Policy %s does not exist. Error seen: %s" % (str(policyName),c.rest.result_json()))
            return False

###################################################
# All Bigtap Configuration Commands Go Here:
###################################################    
    def rest_setup_bigtap_interfaces(self,switchDpid,intfName,intfType,intfNick):
        '''Execute the CLI command 'bigtap role filter interface-name F1'
        
            Input: 
                `switchDpid` : DPID of the switch
                `intfName`    : Interface Name viz. etherenet1, ethernet2 etc.
                `intfType`    : Interface Type viz. filter, delivery, service
                `intfNick`    : Nickname for the interface for eg. F1, D1, S1 etc.
            
            Returns: True if configuration is successful, false otherwise
        '''
        t = test.Test()
        c = t.controller()
        c.http_port=8082
        url='http://%s:%s/api/v1/data/controller/applications/bigtap/interface-config[interface="%s"][switch="%s"]' % (c.ip,c.http_port,str(intfName), str(switchDpid))
        c.rest.put(url, {"interface": str(intfName), "switch": str(switchDpid), 'role':str(intfType),'name':str(intfNick)})
        helpers.test_log("Ouput: %s" % c.rest.result_json())
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
            return False
        else:
            helpers.test_log(c.rest.content_json())
            return True

    def rest_delete_interface_role(self,swName,intfName,intfType,intfNick):
        '''Delete filter/service/delivery interface from switch configuration. Similar to executing the CLI command 'no bigtap role filter interface-name F1'
         
            Input: 
                `switchDpid` : DPID of the switch
                `intfName`    : Interface Name viz. etherenet1, ethernet2 etc.
                `intfType`    : Interface Type viz. filter, delivery, service
                `intfNick`    : Nickname for the interface for eg. F1, D1, S1 etc.
            
            Returns: True if delete is successful, false otherwise       
        '''
        t = test.Test()
        c = t.controller()
        c.http_port=8082
        url='http://%s:%s/api/v1/data/controller/applications/bigtap/interface-config[interface="%s"][switch="%s"]' % (c.ip,c.http_port, str(intfName), str(swName)) 
        c.rest.delete(url, {'role':str(intfType), "name": str(intfNick)})
        helpers.test_log("Ouput: %s" % c.rest.result_json())
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
            return False
        else:
            helpers.test_log(c.rest.content_json())
            return True

    def rest_delete_interface(self,swName,intfName):
        '''Delete interface from switch
         
            Input: 
                `switchDpid` : DPID of the switch
                `intfName`    : Interface Name viz. etherenet1, ethernet2 etc.
            
            Returns: True if delete is successful, false otherwise       
        '''
        t = test.Test()
        c = t.controller()
        c.http_port=8082
        url='http://%s:%s/api/v1/data/controller/core/switch[dpid="%s"]/interface[name=""]'  % (c.ip,c.http_port, str(swName), str(intfName))
        c.rest.delete(url1, {})
        helpers.test_log("Ouput: %s" % c.rest.result_json())
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
            return False
        else:
            helpers.test_log(c.rest.content_json())
            return True

    def rest_add_policy(self,viewName,policyName,policyAction):
        '''Add a bigtap policy.
        
            Input:
                `viewName`    :    RBAC View Name for eg. admin-view
                `policyName`  :    Policy Name
                `policyAction`:    Policy action. The permitted values are "forward" or "rate-measure"
            
            Returns: True if policy configuration is successful, false otherwise       
        '''
        t = test.Test()
        c = t.controller()
        c.http_port=8082
        url='http://%s:%s/api/v1/data/controller/applications/bigtap/view[name="%s"]/policy[name="%s"]' % (c.ip,c.http_port, str(viewName), str(policyName))
        c.rest.put(url,{'name':str(policyName)})
        helpers.test_log("Ouput: %s" % c.rest.result_json())
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
        c.rest.patch(url,{"action": str(policyAction) })
        helpers.test_log("Ouput: %s" % c.rest.result_json())
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
            return False
        else:
            helpers.test_log(c.rest.content_json())
            return True

    def rest_delete_policy(self,viewName,policyName):
        '''Delete a bigtap policy.
        
            Input:
                `viewName`    :    RBAC View Name for eg. admin-view
                `policyName`  :    Policy Name
            
            Returns: True if policy delete is successful, False otherwise       
        '''
        t = test.Test()
        c = t.controller()
        c.http_port=8082
        url='http://%s:%s/api/v1/data/controller/applications/bigtap/view[name="%s"]/policy[name="%s"]' % (c.ip,c.http_port, str(viewName), str(policyName))
        c.rest.delete(url,{})
        helpers.test_log("Ouput: %s" % c.rest.result_json())
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
            return False
        else:
            helpers.test_log(c.rest.content_json())
            return True

    def rest_add_policy_interface(self,viewName,policyName,intfNick,intfType):
        '''Add a bigtap policy interface viz. Add a filter-interface and/or delivery-interface under a bigtap policy.
        
            Input:
                `viewName`    :    RBAC View Name for eg. admin-view
                `policyName`  :    Policy Name
                `intfNick`    :    Interface Nick-Name for eg. F1 or D1
                `intfType`    :    Interface Type. Allowed values are `filter` or `delivery`
            
            Returns: True if policy configuration is successful, false otherwise       
        '''
        t = test.Test()
        c = t.controller()
        if "filter" in str(intfType) :
            intf_type = "filter-group"
        else :
            intf_type = "delivery-group"
        c.http_port=8082
        url='http://%s:%s/api/v1/data/controller/applications/bigtap/view[name="%s"]/policy[name="%s"]/%s[name="%s"]' % (c.ip,c.http_port, str(viewName), str(policyName),str(intf_type),str(intfNick))
        c.rest.put(url,{"name": str(intfNick)})
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
            return False
        else:
            helpers.test_log(c.rest.content_json())
            return True
    
    def rest_delete_policy_interface(self,viewName,policyName,intfNick,intfType):
        '''Delete a bigtap policy interface viz. Delete a filter-interface and/or delivery-interface from a bigtap policy.
        
            Input:
                `viewName`    :    RBAC View Name for eg. admin-view
                `policyName`  :    Policy Name
                `intfNick`    :    Interface Nick-Name for eg. F1 or D1
                `intfType`    :    Interface Type. Allowed values are `filter` or `delivery`
            
            Returns: True if policy delete is successful, false otherwise   
        '''
        t = test.Test()
        c = t.controller()
        if "filter" in str(intfType) :
            intf_type = "filter-group"
        else :
            intf_type = "delivery-group"
        c.http_port=8082
        url='http://%s:%s/api/v1/data/controller/applications/bigtap/view[name="%s"]/policy[name="%s"]/%s[name="%s"]' % (c.ip,c.http_port, str(viewName), str(policyName),str(intf_type),str(intfNick))
        c.rest.delete(url,{})
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
            return False
        else:
            helpers.test_log(c.rest.content_json())
            return True
  
    def rest_add_policy_match(self,viewName,policyName,match_number,data):
        '''Add a bigtap policy match condition.
        
            Input:
                `viewName`    :    RBAC View Name for eg. admin-view
                `policyName`  :    Policy Name
                `match_number`    :    Match number like the '1' in  '1 match tcp
                `data`    :    Formatted data field like  {"ether-type": 2048, "dst-tp-port": 80, "ip-proto": 6, "sequence": 1} 
            
            Returns: True if policy configuration is successful, false otherwise       
        '''
        t = test.Test()
        c = t.controller()
        c.http_port=8082
        url='http://%s:%s/api/v1/data/controller/applications/bigtap/view[name="%s"]/policy[name="%s"]/rule[sequence=%s]'  % (c.ip,c.http_port,str(viewName),str(policyName),str(match_number))
        data_dict = helpers.from_json(data)
        c.rest.put(url,data_dict)
        helpers.test_log(c.rest.result_json())
        if not c.rest.status_code_ok():
            helpers.test_log(c.rest.content_json())
            helpers.test_failure(c.rest.error())
            return False
        else:
            helpers.test_log(c.rest.content_json())
            return True
    
    def rest_delete_policy_match(self,viewName,policyName,match_number):
        '''Delete a bigtap policy match condition.
        
            Input:
                `viewName`    :    RBAC View Name for eg. admin-view
                `policyName`  :    Policy Name
                `match_number`    :    Match number like the '1' in  '1 match tcp
            
            Returns: True if policy delete is successful, false otherwise       
        '''
        t = test.Test()
        c = t.controller()
        c.http_port=8082
        url='http://%s:%s/api/v1/data/controller/applications/bigtap/view[name="%s"]/policy[name="%s"]/rule[sequence="%s"]'  % (c.ip,c.http_port,str(viewName),str(policyName),str(match_number))
        c.rest.delete(url,{})
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
            return False
        else:
            helpers.test_log(c.rest.content_json())
            return True
        
# Add a service with Pre-Service and Post Service interface.
    def rest_add_bigtap_service(self,serviceName,intfPreNick,intfPostNick):
        '''Add a bigtap service.
        
            Input:
                `serviceName`        : Name of Service
                `intfPreNick`        : Name of pre-service interface
                `intfPostNick`       : Name of post-service interface
            
            Returns: True if service addition is successful, false otherwise
        
            Examples:
                | rest add bigtap service  |  S1-LB7  |  S1-LB7_E3-HP1_E3-PRE  |  S1-LB7_E4-HP1_E4-POST  |  
                Result is 
                bigtap service S1-LB7
                  post-service S1-LB7_E4-HP1_E4-POST
                  pre-service S1-LB7_E3-HP1_E3-PRE
        '''
        t = test.Test()
        c = t.controller()
        #Add Service
        c.http_port=8082
        url='http://%s:%s/api/v1/data/controller/applications/bigtap/service[name="%s"]' % (c.ip,c.http_port,str(serviceName))
        c.rest.put(url,{"name":str(serviceName)})
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
            return False
        else :
            helpers.test_log(c.rest.content_json())
        #Add Pre-Service Interface
        url_add_intf ='http://%s:%s/api/v1/data/controller/applications/bigtap/service[name="%s"]/pre-group[name="%s"]'  % (c.ip,c.http_port,str(serviceName),str(intfPreNick))
        c.rest.put(url_add_intf, {"name":str(intfPreNick)})
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
            return False
        else :
            helpers.test_log(c.rest.content_json())
        #Add Post-Service Interface
        url_add_intf ='http://%s:%s/api/v1/data/controller/applications/bigtap/service[name="%s"]/post-group[name="%s"]'  % (c.ip,c.http_port,str(serviceName),str(intfPostNick))
        c.rest.put(url_add_intf, {"name":str(intfPostNick)})
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
            return False
        else:
            helpers.test_log(c.rest.content_json())
            return True
 
# Delete a service
    def rest_delete_bigtap_service(self,serviceName) :
        '''Delete a bigtap service.
        
            Input:
                `serviceName`        : Name of Service
            
            Returns: True if service deletion is successful, false otherwise
        
        '''
        t = test.Test()
        c = t.controller()
        c.http_port=8082
        url='http://%s:%s/api/v1/data/controller/applications/bigtap/service[name="%s"]'  % (c.ip,c.http_port,str(serviceName))
        c.rest.delete(url,{})   
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
            return False
        else:
            helpers.test_log(c.rest.content_json())
        return True
    
    def rest_add_interface_service(self,serviceName,intfType,intfNick):
        '''Add a service interface to a service. This is similar to executing CLI command "post-service S1-LB7_E4-HP1_E4-POST"
        
            Input:
                `serviceName`        : Name of Service
                `intfType`           : Interface Type. Acceptable values are `pre` or `post`
                `intfPostNick`       : Name of pre/post-service interface for e.g. S1-LB7_E4-HP1_E4-POST
            
            Returns: True if addition of interface to service is successful, false otherwise
        
            Examples:
                | rest add interface service  |  S1-LB7  |  post  |  S1-LB7_E4-HP1_E4-POST  |  
                Result is 
                bigtap service S1-LB7
                  post-service S1-LB7_E4-HP1_E4-POST
        '''
        t = test.Test()
        c = t.controller()
        c.http_port=8082
        if "pre" in str(intfType) :
            url_add_intf ='http://%s:%s/api/v1/data/controller/applications/bigtap/service[name="%s"]/pre-group[name="%s"]'  % (c.ip,c.http_port,str(serviceName),str(intfNick))
        else :
            url_add_intf ='http://%s:%s/api/v1/data/controller/applications/bigtap/service[name="%s"]/post-group[name="%s"]'  % (c.ip,c.http_port,str(serviceName),str(intfNick))
        c.rest.post(url_add_intf, {"name":str(intfNick)})
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
            return False
        else:
            helpers.test_log(c.rest.content_json())
            return True

    def rest_delete_interface_service(self,serviceName,intfNick,intfType) :
        '''Delete an interface from a service. This is similar to executing CLI command "no post-service S1-LB7_E4-HP1_E4-POST"
        
            Input:
                `serviceName`        : Name of Service
                `intfType`           : Interface Type. Acceptable values are `pre` or `post`
                `intfPostNick`       : Name of pre/post-service interface for e.g. S1-LB7_E4-HP1_E4-POST
            
            Returns: True if addition of interface to service is successful, false otherwise
        
            Examples:
                | rest delete interface service  |  S1-LB7  |  post  |  S1-LB7_E4-HP1_E4-POST  |  
                Result is 
                bigtap service S1-LB7
        '''
        t = test.Test()
        c = t.controller()
        c.http_port=8082
        if "pre" in str(intfType) :
            url_add_intf ='http://%s:%s/api/v1/data/controller/applications/bigtap/service[name="%s"]/pre-group[name="%s"]'  % (c.ip,c.http_port,str(serviceName),str(intfNick))
        else :
            url_add_intf ='http://%s:%s/api/v1/data/controller/applications/bigtap/service[name="%s"]/post-group[name="%s"]'  % (c.ip,c.http_port,str(serviceName),str(intfNick))
        c.rest.delete(url_add_intf, {})
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
            return False
        else:
            helpers.test_log(c.rest.content_json())
            return True

    def rest_add_service_to_policy(self,viewName,policyName,serviceName,sequenceNumber) :
        '''Add a service to a policy. This is similar to executing CLI command "use-service S1-LB7 sequence 1"
        
            Input:
                `viewName`           :    RBAC View Name for eg. admin-view
                `policyName`         :    Policy Name
                `serviceName`        : Name of Service
                `sequenceNumber`     : Sequence number of the policy, to determine order in which policies are processed
            
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
        t = test.Test()
        c = t.controller()
        c.http_port=8082
        url_to_add ='http://%s:%s/api/v1/data/controller/applications/bigtap/view[name="%s"]/policy[name="%s"]/service[sequence=%s]' % (c.ip,c.http_port,str(viewName),str(policyName),str(sequenceNumber))
        c.rest.put(url_to_add, {"name":str(serviceName), "sequence" : int(sequenceNumber)})
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
            return False
        else:
            helpers.test_log(c.rest.content_json())
            return True

    def rest_delete_service_from_policy(self,viewName,policyName,serviceName) :
        '''Delete a service from a policy. This is similar to executing CLI command "no use-service S1-LB7 sequence 1"
        
            Input:
                `viewName`           :    RBAC View Name for eg. admin-view
                `policyName`         :    Policy Name
                `serviceName`        : Name of Service
            
            Returns: True if deletion of service from policy is successful, false otherwise
        
        '''
        t = test.Test()
        c = t.controller()
        c.http_port=8082
        url ='http://%s:%s/api/v1/data/controller/applications/bigtap/view[name="%s"]/policy[name="%s"]/service[name="%s"]' % (c.ip,c.http_port,str(viewName),str(policyName),str(serviceName))
        c.rest.delete(url, {})
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
            return False
        else:
            helpers.test_log(c.rest.content_json())
            return True

#Change policy action
    def rest_change_policy_action(self,viewName,policyName,policyAction):
        '''Change a bigtap policy action from forward --> Rate-Measure, Forward --> Inactive, Rate-Measure--> Forward, Rate-Measure--> Inactive etc.
        
           Input:
                `viewName`           :    RBAC View Name for eg. admin-view
                `policyName`         :    Policy Name
                `policyAction`       :    Desired action. Values are `forward`, `rate-measure` and `inactive`
        
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
        t = test.Test()
        c = t.controller()
        c.http_port=8082
        url ='http://%s:%s/api/v1/data/controller/applications/bigtap/view[name="%s"]/policy[name="%s"]' % (c.ip,c.http_port,str(viewName),str(policyName))
        c.rest.patch(url,{"action":str(policyAction)})
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
            return False
        else:
            helpers.test_log(c.rest.content_json())
            return True

#Disable bigtap feature overlap/inport-mask/tracked-host/l3-l4-mode
    def rest_disable_feature(self,featureName):
        '''Disable a bigtap feature
        
           Input:
                `featureName`           :    Bigtap Feature Name. Currently allowed feature names are `overlap`,`inport-mask`,`tracked-host`,`l3-l4-mode`
        
           Returns: True if feature is disabled successfully, false otherwise
            Examples:
                | rest disable feature  |  overlap |  
        '''
        t = test.Test()
        c = t.controller()
        c.http_port=8082
        url ='http://%s:%s/api/v1/data/controller/applications/bigtap/feature'  % (c.ip,c.http_port,)
        c.rest.patch(url,{str(featureName): False})
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
            return False
        else:
            helpers.test_log(c.rest.content_json())
            return True
    
#Enable bigtap feature overlap/inport-mask/tracked-host/l3-l4-mode
    def rest_enable_feature(self,featureName):
        '''Enable a bigtap feature
        
           Input:
                `featureName`           :    Bigtap Feature Name. Currently allowed feature names are `overlap`,`inport-mask`,`tracked-host`,`l3-l4-mode`
        
           Returns: True if feature is enabled successfully, false otherwise
            Examples:
                | rest enable feature  |  overlap |  
        '''
        t = test.Test()
        c = t.controller()
        c.http_port=8082
        url ='http://%s:%s/api/v1/data/controller/applications/bigtap/feature'  % (c.ip,c.http_port,)
        c.rest.patch(url,{str(featureName): True})
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
            return False
        else:
            helpers.test_log(c.rest.content_json())
            return True
        
#Compare coreswitch flows
    def rest_compare_coreswitch_flows(self,flow1,flow2,flowVal1,flowVal2):
        '''Compare coreswitch flow counts. Useful when we have multiple core-switches.
        
            Inputs:
                flow1: Number of flows on core switch 1
                flow2: Number of flows on core switch 2
                flowVal1: Desired number of flows on switch 1 or switch 2
                flowVal2: Desired number of flows on switch 1 or switch 2
        
            Returns True if flow is found on switch
        '''
        if ((flow1 == flowVal1) and (flow2 == flowVal2 )) or ((flow2 == flowVal1) and (flow1 == flowVal2 )) :
            return True
        else :
            return False