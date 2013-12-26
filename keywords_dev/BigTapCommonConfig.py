import autobot.helpers as helpers
import autobot.test as test


class BigTapCommonConfig(object):

    def __init__(self):
        t = test.Test()
        c = t.controller()

        url = '%s/auth/login' % c.base_url
        
        helpers.log("url: %s" % url)
        result = c.rest.post(url, {"user":"admin", "password":"adminadmin"})

        helpers.log("result: %s" % helpers.to_json(result))

        session_cookie = result['content']['session_cookie']
        c.rest.set_session_cookie(session_cookie)
        
#Assign filter/delivery/service node characteristics to particular switch interfaces.
#Same as bigtap role filter interface-name F1    
    def rest_setup_bigtap_interfaces(self,switchDpid,intfName,intfType,intfNick):
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
 
# Delete filter/service/delivery interface from switch configuration   
    def rest_delete_interface_role(self,swName,intfName,intfType,intfNick):
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
#            
    def rest_delete_interface(self,swName,intfName,intfType):
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
    
# Add a match condition to a policy    
    def rest_add_policy_match(self,viewName,policyName,match_number,data):
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
    
# delete a match condition from a policy
    def rest_delete_policy_match(self,viewName,policyName,match_number):
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
 
#Add interface to service
    def rest_add_interface_service(self,serviceName,intfType,intfNick):
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

#Delete interface from service
    def rest_delete_bigtap_service_intf(self,serviceName,intfNick,intfType) :
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

#Add service to policy
    def rest_add_service_to_policy(self,viewName,policyName,serviceName,sequenceNumber) :
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

#Delete service from policy
    def rest_delete_service_from_policy(self,viewName,policyName,serviceName) :
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
        if ((flow1 == flowVal1) and (flow2 == flowVal2 )) or ((flow2 == flowVal1) and (flow1 == flowVal2 )) :
            return True
        else :
            return False

#Generic Sleep Function
    def sleep_now(self,intTime):
        helpers.sleep(float(intTime))