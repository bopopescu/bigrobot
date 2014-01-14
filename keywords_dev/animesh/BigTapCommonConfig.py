import autobot.helpers as helpers
import autobot.test as test
from BigTapCommonShow import BigTapCommonShow

class BigTapCommonConfig(object):

    def __init__(self):
        t = test.Test()
        self.btc=BigTapCommonShow()
        if(self.btc.rest_is_c1_master_controller()):
            c = t.controller('c1')
            c.http_port=8082
        else:
            c = t.controller('c2')
            c.http_port=8082

        url = '%s/auth/login' % c.base_url
        
        helpers.log("url: %s" % url)
        result = c.rest.post(url, {"user":"admin", "password":"adminadmin"})

        helpers.log("result: %s" % helpers.to_json(result))

        session_cookie = result['content']['session_cookie']
        c.rest.set_session_cookie(session_cookie)
        
#Assign filter/delivery/service node characteristics to particular switch interfaces.
#Same as bigtap role filter interface-name F1    
    def rest_bigtap_setup_interface(self,intf_name,intf_type,intf_nickname,switch_alias=None, sw_dpid=None):
        '''Execute the CLI command 'bigtap role filter interface-name F1'
        
            Input: 
                `switch_dpid` : DPID of the switch
                `intf_name`    : Interface Name viz. etherenet1, ethernet2 etc.
                `intf_type`    : Interface Type viz. filter, delivery, service
                `intf_nickname`    : Nickname for the interface for eg. F1, D1, S1 etc.
            
            Returns: True if configuration is successful, false otherwise
        '''
        t=test.Test()
        try:
            t.controller('c2')
        except:
            c = t.controller('c1')
            c.http_port=8082
        else:
            if(self.rest_is_c1_master_controller()):
                c = t.controller('c1')
                c.http_port=8082
            else:
                c = t.controller('c2')
                c.http_port=8082
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
            url='http://%s:%s/api/v1/data/controller/applications/bigtap/interface-config[interface="%s"][switch="%s"]' % (c.ip,c.http_port,str(intf_name), str(switch_dpid))
            c.rest.put(url, {"interface": str(intf_name), "switch": str(switch_dpid), 'role':str(intf_type),'name':str(intf_nickname)})
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
 
# Delete filter/service/delivery interface from switch configuration   
    def rest_bigtap_delete_interface_role(self,intf_name,intf_type,intf_nickname,switch_alias=None, sw_dpid=None):
        '''Delete filter/service/delivery interface from switch configuration. Similar to executing the CLI command 'no bigtap role filter interface-name F1'
         
            Input: 
                `switch_dpid` : DPID of the switch
                `intf_name`    : Interface Name viz. etherenet1, ethernet2 etc.
                `intf_type`    : Interface Type viz. filter, delivery, service
                `intf_nickname`    : Nickname for the interface for eg. F1, D1, S1 etc.
            
            Returns: True if delete is successful, false otherwise       
        '''
        t=test.Test()
        try:
            t.controller('c2')
        except:
            c = t.controller('c1')
            c.http_port=8082
        else:
            if(self.rest_is_c1_master_controller()):
                c = t.controller('c1')
                c.http_port=8082
            else:
                c = t.controller('c2')
                c.http_port=8082
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

            url='http://%s:%s/api/v1/data/controller/applications/bigtap/interface-config[interface="%s"][switch="%s"]' % (c.ip,c.http_port, str(intf_name), str(switch_dpid)) 
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
#            
    def rest_bigtap_delete_interface(self,intf_name,switch_alias=None, sw_dpid=None):
        '''Delete interface from switch
         
            Input: 
                `switch_dpid` : DPID of the switch
                `intf_name`    : Interface Name viz. etherenet1, ethernet2 etc.
            
            Returns: True if delete is successful, false otherwise       
        '''
        t=test.Test()
        try:
            t.controller('c2')
        except:
            c = t.controller('c1')
            c.http_port=8082
        else:
            if(self.rest_is_c1_master_controller()):
                c = t.controller('c1')
                c.http_port=8082
            else:
                c = t.controller('c2')
                c.http_port=8082
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
            url='http://%s:%s/api/v1/data/controller/core/switch[dpid="%s"]/interface[name=""]'  % (c.ip,c.http_port, str(switch_dpid), str(intf_name))
            c.rest.delete(url1, {})
        except:
            helpers.test_failure(c.rest.error())
            return False
        else:  
            if not c.rest.status_code_ok():
                helpers.test_failure(c.rest.error())
                return False
            else:
                return True
    
    def rest_bigtap_add_policy(self,viewName,policyName,policyAction):
        t = test.Test()
        if(self.btc.rest_is_c1_master_controller()):
            c = t.controller('c1')
            c.http_port=8082
        else:
            c = t.controller('c2')
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
    
    def rest_bigtap_delete_policy(self,viewName,policyName):
        t = test.Test()
        if(self.btc.rest_is_c1_master_controller()):
            c = t.controller('c1')
            c.http_port=8082
        else:
            c = t.controller('c2')
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
    
    def rest_bigtap_add_policy_interface(self,viewName,policyName,intfNick,intfType):
        t = test.Test()
        if(self.btc.rest_is_c1_master_controller()):
            c = t.controller('c1')
            c.http_port=8082
        else:
            c = t.controller('c2')
            c.http_port=8082
        if "filter" in str(intfType) :
            intf_type = "filter-group"
        else :
            intf_type = "delivery-group"
        url='http://%s:%s/api/v1/data/controller/applications/bigtap/view[name="%s"]/policy[name="%s"]/%s[name="%s"]' % (c.ip,c.http_port, str(viewName), str(policyName),str(intf_type),str(intfNick))
        c.rest.put(url,{"name": str(intfNick)})
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
            return False
        else:
            helpers.test_log(c.rest.content_json())
            return True
    
    def rest_bigtap_delete_policy_interface(self,viewName,policyName,intfNick,intfType):
        t = test.Test()
        if(self.btc.rest_is_c1_master_controller()):
            c = t.controller('c1')
            c.http_port=8082
        else:
            c = t.controller('c2')
            c.http_port=8082
        if "filter" in str(intfType) :
            intf_type = "filter-group"
        else :
            intf_type = "delivery-group"
        url='http://%s:%s/api/v1/data/controller/applications/bigtap/view[name="%s"]/policy[name="%s"]/%s[name="%s"]' % (c.ip,c.http_port, str(viewName), str(policyName),str(intf_type),str(intfNick))
        c.rest.delete(url,{})
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
            return False
        else:
            helpers.test_log(c.rest.content_json())
            return True
    
# Add a match condition to a policy    
    def rest_bigtap_add_policy_match(self,viewName,policyName,match_number,data):
        t = test.Test()
        if(self.btc.rest_is_c1_master_controller()):
            c = t.controller('c1')
            c.http_port=8082
        else:
            c = t.controller('c2')
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
    def rest_bigtap_delete_policy_match(self,viewName,policyName,match_number):
        t = test.Test()
        if(self.btc.rest_is_c1_master_controller()):
            c = t.controller('c1')
            c.http_port=8082
        else:
            c = t.controller('c2')
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
    def rest_bigtap_add_service(self,serviceName,intfPreNick,intfPostNick):
        t = test.Test()
        if(self.btc.rest_is_c1_master_controller()):
            c = t.controller('c1')
            c.http_port=8082
        else:
            c = t.controller('c2')
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
    def rest_bigtap_delete_service(self,serviceName) :
        t = test.Test()
        if(self.btc.rest_is_c1_master_controller()):
            c = t.controller('c1')
            c.http_port=8082
        else:
            c = t.controller('c2')
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
    def rest_bigtap_add_interface_service(self,serviceName,intfType,intfNick):
        t = test.Test()
        if(self.btc.rest_is_c1_master_controller()):
            c = t.controller('c1')
            c.http_port=8082
        else:
            c = t.controller('c2')
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
    def rest_bigtap_delete_service_intf(self,serviceName,intfNick,intfType) :
        t = test.Test()
        if(self.btc.rest_is_c1_master_controller()):
            c = t.controller('c1')
            c.http_port=8082
        else:
            c = t.controller('c2')
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
    def rest_bigtap_add_service_to_policy(self,viewName,policyName,serviceName,sequenceNumber) :
        t = test.Test()
        if(self.btc.rest_is_c1_master_controller()):
            c = t.controller('c1')
            c.http_port=8082
        else:
            c = t.controller('c2')
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
    def rest_bigtap_delete_service_from_policy(self,viewName,policyName,serviceName) :
        t = test.Test()
        if(self.btc.rest_is_c1_master_controller()):
            c = t.controller('c1')
            c.http_port=8082
        else:
            c = t.controller('c2')
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
    def rest_bigtap_change_policy_action(self,viewName,policyName,policyAction):
        t = test.Test()
        if(self.btc.rest_is_c1_master_controller()):
            c = t.controller('c1')
            c.http_port=8082
        else:
            c = t.controller('c2')
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
    def rest_bigtap_disable_feature(self,featureName):
        t = test.Test()
        if(self.btc.rest_is_c1_master_controller()):
            c = t.controller('c1')
            c.http_port=8082
        else:
            c = t.controller('c2')
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
    def rest_bigtap_enable_feature(self,featureName):
        t = test.Test()
        if(self.btc.rest_is_c1_master_controller()):
            c = t.controller('c1')
            c.http_port=8082
        else:
            c = t.controller('c2')
            c.http_port=8082
        url ='http://%s:%s/api/v1/data/controller/applications/bigtap/feature'  % (c.ip,c.http_port)
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