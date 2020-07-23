import autobot.helpers as helpers
import autobot.test as test

class BigTapCommonConfig(object):

    def __init__(self):
        pass
        
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
        try:
            t = test.Test()
        except:
            return False
        else:
            c= t.controller('main')
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
                url='/api/v1/data/controller/applications/bigtap/interface-config[interface="%s"][switch="%s"]' % (str(intf_name), str(switch_dpid))
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
        try:
            t = test.Test()
        except:
            return False
        else:
            c= t.controller('main')
            try:
                if (switch_alias is None and sw_dpid is not None):
                    switch_dpid = sw_dpid
                elif (switch_alias is None and sw_dpid is None):
                    helpers.log('Either Switch DPID or Switch Alias has to be provided')
                    helpers.test_failure(c.rest.error())
                    return False
                elif (switch_alias is not None and sw_dpid is None):
                    switch_dpid = self.rest_get_switch_dpid(switch_alias)
                else:
                    switch_dpid = sw_dpid
                url='/api/v1/data/controller/applications/bigtap/interface-config[interface="%s"][switch="%s"]' % (str(intf_name), str(switch_dpid)) 
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
        try:
            t = test.Test()
        except:
            return False
        else:
            c= t.controller('main')
            try:
                if (switch_alias is None and sw_dpid is not None):
                    switch_dpid = sw_dpid
                elif (switch_alias is None and sw_dpid is None):
                    helpers.log('Either Switch DPID or Switch Alias has to be provided')
                    helpers.test_failure(c.rest.error())
                    return False
                elif (switch_alias is not None and sw_dpid is None):
                    switch_dpid = self.rest_get_switch_dpid(switch_alias)
                else:
                    switch_dpid = sw_dpid
                url='/api/v1/data/controller/core/switch[dpid="%s"]/interface[name=""]'  % (str(switch_dpid), str(intf_name))
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
    
    def rest_bigtap_add_policy(self,view_name,policy_name,policy_action='inactive'):
        try:
            t = test.Test()
        except:
            return False
        else:
            c= t.controller('main')
            try:
                url='/api/v1/data/controller/applications/bigtap/view[name="%s"]/policy[name="%s"]' % (str(view_name), str(policy_name))
                c.rest.put(url,{'name':str(policy_name)})
            except:
                helpers.test_failure(c.rest.error())
                return False
            else:
                if not c.rest.status_code_ok():
                    helpers.test_failure(c.rest.error())
                try:
                    c.rest.patch(url,{"action": str(policy_action) })
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
    
    def rest_bigtap_delete_policy(self,view_name,policy_name):
        try:
            t = test.Test()
        except:
            return False
        else:
            c= t.controller('main')
            try:
                url='/api/v1/data/controller/applications/bigtap/view[name="%s"]/policy[name="%s"]' % (str(view_name), str(policy_name))
                c.rest.delete(url,{})
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
    
    def rest_bigtap_add_policy_interface(self,view_name,policy_name,intf_nick,type_intf):
        try:
            t = test.Test()
        except:
            return False
        else:
            c= t.controller('main')
            try:
                if "filter" in str(type_intf) :
                    intf_type = "filter-group"
                else :
                    intf_type = "delivery-group"
                url='/api/v1/data/controller/applications/bigtap/view[name="%s"]/policy[name="%s"]/%s[name="%s"]' % (str(view_name), str(policy_name),str(intf_type),str(intf_nick))
                c.rest.put(url,{"name": str(intf_nick)})
            except:
                helpers.test_failure(c.rest.error())
                return False
            else:
                helpers.test_log(c.rest.content_json())
                return True
    
    def rest_bigtap_delete_policy_interface(self,view_name,policy_name,intf_nick,type_intf):
        try:
            t = test.Test()
        except:
            return False
        else:
            c= t.controller('main')
            try:
                if "filter" in str(type_intf) :
                    intf_type = "filter-group"
                else :
                    intf_type = "delivery-group"
                url='/api/v1/data/controller/applications/bigtap/view[name="%s"]/policy[name="%s"]/%s[name="%s"]' % (str(view_name), str(policy_name),str(intf_type),str(intf_nick))
                c.rest.delete(url,{})
            except:
                helpers.test_failure(c.rest.error())
                return False
            else:
                helpers.test_log(c.rest.content_json())
                return True
    
# Add a match condition to a policy    
    def rest_bigtap_add_policy_match(self,view_name,policy_name,match_number,data):
        try:
            t = test.Test()
        except:
            return False
        else:
            c= t.controller('main')
            try:
                url='/api/v1/data/controller/applications/bigtap/view[name="%s"]/policy[name="%s"]/rule[sequence=%s]'  % (str(view_name),str(policy_name),str(match_number))
                data_dict = helpers.from_json(data)
                c.rest.put(url,data_dict)
            except:
                return False
            else:
                if not c.rest.status_code_ok():
                    helpers.test_failure(c.rest.error())
                    return False
                else:
                    helpers.test_log(c.rest.content_json())
                    return True
    
# delete a match condition from a policy
    def rest_bigtap_delete_policy_match(self,view_name,policy_name,match_number):
        try:
            t = test.Test()
        except:
            return False
        else:
            c= t.controller('main')
            try:
                url='/api/v1/data/controller/applications/bigtap/view[name="%s"]/policy[name="%s"]/rule[sequence="%s"]'  % (str(view_name),str(policy_name),str(match_number))
                c.rest.delete(url,{})
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



# Add a service with Pre-Service and Post Service interface.
    def rest_bigtap_add_service(self,service_name,intf_pre_nick,intf_post_nick):
        try:
            t = test.Test()
        except:
            return False
        else:
            c= t.controller('main')
            try:
                url='/api/v1/data/controller/applications/bigtap/service[name="%s"]' % (str(service_name))
                c.rest.put(url,{"name":str(service_name)})
            except:
                helpers.test_failure(c.rest.error())
                return False
            else:
                #Add Pre-Service Interface
                try:
                    url_add_intf ='/api/v1/data/controller/applications/bigtap/service[name="%s"]/pre-group[name="%s"]'  % (str(service_name),str(intf_pre_nick))
                    c.rest.put(url_add_intf, {"name":str(intf_pre_nick)})
                except:
                    helpers.test_failure(c.rest.error())
                    return False
                #Add Post-Service Interface
                try:
                    url_add_intf ='/api/v1/data/controller/applications/bigtap/service[name="%s"]/post-group[name="%s"]'  % (str(service_name),str(intf_post_nick))
                    c.rest.put(url_add_intf, {"name":str(intf_post_nick)})
                except:
                    helpers.test_failure(c.rest.error())
                    return False
                else:
                    helpers.test_log(c.rest.content_json())
                    return True
 
# Delete a service
    def rest_bigtap_delete_service(self,service_name) :
        try:
            t = test.Test()
        except:
            return False
        else:
            c= t.controller('main')
            try:
                url='/api/v1/data/controller/applications/bigtap/service[name="%s"]'  % (str(service_name))
                c.rest.delete(url,{})
            except:
                helpers.test_failure(c.rest.error())
                return False
            else:
                return True
 
#Add interface to service
    def rest_bigtap_add_interface_service(self,service_name,intf_type,intf_nick):
        try:
            t = test.Test()
        except:
            return False
        else:
            c= t.controller('main')
            try:
                if "pre" in str(intf_type) :
                    url_add_intf ='/api/v1/data/controller/applications/bigtap/service[name="%s"]/pre-group[name="%s"]'  % (str(service_name),str(intf_nick))
                else :
                    url_add_intf ='/api/v1/data/controller/applications/bigtap/service[name="%s"]/post-group[name="%s"]'  % (str(service_name),str(intf_nick))
                c.rest.post(url_add_intf, {"name":str(intf_nick)})
            except:
                helpers.test_failure(c.rest.error())
                return False
            else:
                helpers.test_log(c.rest.content_json())
                return True

#Delete interface from service
    def rest_bigtap_delete_service_intf(self,service_name,intf_nick,intf_type) :
        try:
            t = test.Test()
        except:
            return False
        else:
            c= t.controller('main')
            try:
                if "pre" in str(intf_type) :
                    url_add_intf ='/api/v1/data/controller/applications/bigtap/service[name="%s"]/pre-group[name="%s"]'  % (str(service_name),str(intf_nick))
                else :
                    url_add_intf ='/api/v1/data/controller/applications/bigtap/service[name="%s"]/post-group[name="%s"]'  % (str(service_name),str(intf_nick))
                c.rest.delete(url_add_intf, {})
            except:
                helpers.test_failure(c.rest.error())
                return False
            else:
                helpers.test_log(c.rest.content_json())
                return True

#Add service to policy
    def rest_bigtap_add_service_to_policy(self,view_name,policy_name,service_name,seq_no) :
        try:
            t = test.Test()
        except:
            return False
        else:
            c= t.controller('main')
            try:
                url_to_add ='/api/v1/data/controller/applications/bigtap/view[name="%s"]/policy[name="%s"]/service[sequence=%s]' % (str(view_name),str(policy_name),str(seq_no))
                c.rest.put(url_to_add, {"name":str(service_name), "sequence" : int(seq_no)})
            except:
                helpers.test_failure(c.rest.error())
                return False
            else:
                helpers.test_log(c.rest.content_json())
                return True

#Delete service from policy
    def rest_bigtap_delete_service_from_policy(self,view_name,policy_name,service_name) :
        try:
            t = test.Test()
        except:
            return False
        else:
            c= t.controller('main')
            try:
                url ='/api/v1/data/controller/applications/bigtap/view[name="%s"]/policy[name="%s"]/service[name="%s"]' % (str(view_name),str(policy_name),str(service_name))
                c.rest.delete(url, {})
            except:
                helpers.test_failure(c.rest.error())
                return False
            else:
                helpers.test_log(c.rest.content_json())
                return True

#Change policy action
    def rest_bigtap_change_policy_action(self,view_name,policy_name,policy_action='inactive'):
        try:
            t = test.Test()
        except:
            return False
        else:
            c= t.controller('main')
            try:
                url ='/api/v1/data/controller/applications/bigtap/view[name="%s"]/policy[name="%s"]' % (str(view_name),str(policy_name))
                c.rest.patch(url,{"action":str(policy_action)})
            except:
                helpers.test_failure(c.rest.error())
                return False
            else:
                helpers.test_log(c.rest.content_json())
                return True

#Disable bigtap feature overlap/inport-mask/tracked-host/l3-l4-mode
    def rest_bigtap_disable_feature(self,feature_name):
        try:
            t = test.Test()
        except:
            return False
        else:
            c= t.controller('main')
            try:
                url ='/api/v1/data/controller/applications/bigtap/feature'
                c.rest.patch(url,{str(feature_name): False})
            except:
                helpers.test_failure(c.rest.error())
                return False
            else:
                helpers.test_log(c.rest.content_json())
                return True
    
#Enable bigtap feature overlap/inport-mask/tracked-host/l3-l4-mode
    def rest_bigtap_enable_feature(self,feature_name):
        try:
            t = test.Test()
        except:
            return False
        else:
            c= t.controller('main')
            try:
                url ='/api/v1/data/controller/applications/bigtap/feature'
                c.rest.patch(url,{str(feature_name): True})
            except:
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