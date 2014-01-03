import autobot.helpers as helpers
import autobot.test as test


class T5Fabric(object):

    def __init__(self):
        t = test.Test()
        c = t.controller()
        
        url = '%s/api/v1/auth/login' % c.base_url
        result = c.rest.post(url, {"user":"admin", "password":"adminadmin"})
        session_cookie = result['content']['session_cookie']
        c.rest.set_session_cookie(session_cookie)
        
       
    def rest_show_fabric_switch(self):
        t = test.Test()
        c = t.controller()
        url = '%s/api/v1/data/controller/core/switch' % (c.base_url)
        c.rest.get(url)
        helpers.test_log("Output: %s" % c.rest.content_json())
        return True
    
    def rest_show_fabric_link(self):
        t = test.Test()
        c = t.controller()
        
        url = '%s/api/v1/data/controller/applications/bvs/info/fabric?select=link' % (c.base_url)       
        c.rest.get(url)
        helpers.test_log("Output: %s" % c.rest.content_json())
        return True
    
    def rest_configure_switch(self, switch):
        t = test.Test()
        c = t.controller()
                        
        url = '%s/api/v1/data/controller/core/switch-config[name="%s"]' % (c.base_url, switch)       
        c.rest.put(url, {"name": switch})
        helpers.test_log("Output: %s" % c.rest.content_json())
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())

        return c.rest.content()
    def rest_configure_dpid(self, switch, dpid):
        t = test.Test()
        c = t.controller()
        
        url = '%s/api/v1/data/controller/core/switch-config[name="%s"]' % (c.base_url, switch)       
        c.rest.patch(url, {"dpid": dpid})
        helpers.test_log("Output: %s" % c.rest.content_json())
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())

        return c.rest.content() 
    def rest_configure_fabric_role(self, switch, role):
        t = test.Test()
        c = t.controller()
        
        url = '%s/api/v1/data/controller/core/switch-config[name="%s"]' % (c.base_url, switch)       
        c.rest.patch(url, {"fabric-role": role})
        helpers.test_log("Output: %s" % c.rest.content_json())
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())

        return c.rest.content() 
    def rest_configure_leaf_group(self, switch, group):
        t = test.Test()
        c = t.controller()
        
        url = '%s/api/v1/data/controller/core/switch-config[name="%s"]' % (c.base_url, switch)       
        c.rest.patch(url, {"leaf-group": group})
        helpers.test_log("Output: %s" % c.rest.content_json())
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
        return c.rest.content() 
    
    def rest_remove_fabric_switch(self, switch=None):
        t = test.Test()
        c = t.controller()
        
        url = '%s/api/v1/data/controller/core/switch-config[name="%s"]' % (c.base_url, switch)       
        c.rest.delete(url, {"name": switch})
        helpers.test_log("Output: %s" % c.rest.content_json())
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
        return c.rest.content() 
    
    def rest_check_fabric_switch_connectivity(self):
        t = test.Test()
        c = t.controller()
        url = '%s/api/v1/data/controller/core/switch' % (c.base_url)       
        c.rest.get(url)
        data = c.rest.content()
        for i in range (0,len(data)):
            if data[i]["fabric-switch-info"]["suspended"] is True and data[i]["connected"] is True:
                helpers.test_failure("Fabric switch %s is not Configured" % str(data[i]["dpid"])) 
                                                                                 
        return True
    
    def rest_verify_fabric_link_after_switch_removal(self, switch):
        t = test.Test()
        c = t.controller()
        url = '%s/api/v1/data/controller/applications/bvs/info/fabric?select=link' % (c.base_url)       
        c.rest.get(url)
        data = c.rest.content()       
        for i in range (0,len(data)):
            if data[i]["link"]["dst"]["switch-info"]["switch-name"] == switch and data[i]["link"]["link-direction"] == "bidirectional":
                helpers.test_failure("%s Fabric Links not Removed" % str(data[i]["link"]["dst"]["switch-info"]["switch-name"])) 
                break 
                                              
        return True 
    
    def rest_verify_fabric_link_common(self, switch):
        t = test.Test()
        c = t.controller()
        url = '%s/api/v1/data/controller/applications/bvs/info/fabric?select=link' % (c.base_url)       
        c.rest.get(url)
        data = c.rest.content()
        for i in range (0,len(data)):
            if data[i]["link"]["dst"]["switch-info"]["switch-name"] == switch and data[i]["link"]["link-direction"] == "bidirectional":
                helpers.test_log("%s Fabric Links not Removed" % str(data[i]["link"]["dst"]["switch-info"]["switch-name"])) 
                                                             
        return True 
                         
    def rest_check_fabric_switch_role(self, switch, role):
        t = test.Test()
        c = t.controller()
        url = '%s/api/v1/data/controller/core/switch' % (c.base_url)       
        c.rest.get(url)
        data = c.rest.content()
        status = False
        for i in range (0,len(data)):
            if data[i]["fabric-switch-info"]["switch-name"] == switch and data[i]["fabric-switch-info"]["fabric-role"] == role:
                helpers.test_log("Fabric switch Role of %s is %s" % (str(data[i]["fabric-switch-info"]["switch-name"]), str(data[i]["fabric-switch-info"]["fabric-role"])))
                status = True
                return True
                break
        if status == False:
            helpers.test_failure("Fabric switch role removal Test Failed")      
                                                                              
        return False

    def rest_remove_fabric_role(self, switch, role=None):
        t = test.Test()
        c = t.controller()
        
        url = '%s/api/v1/data/controller/core/switch-config[name="%s"]' % (c.base_url, switch)       
        c.rest.delete(url, {"fabric-role": role})
        helpers.test_log("Output: %s" % c.rest.content_json())
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
        return c.rest.content()  
    
    def rest_show_fabric_lag(self, dpid):
        t = test.Test()
        c = t.controller()
        
        url = '%s/api/v1/data/controller/core/switch[dpid="%s"]?select=fabric-lag' % (c.base_url, dpid)       
        c.rest.get(url)
        data = c.rest.content()
        leaf_lag = len(data[0]["fabric-lag"][0]["member"])
        rack_lag = len(data[0]["fabric-lag"][1]["member"])
        spine_lag = len(data[0]["fabric-lag"][2]["member"])
        spine_bcast_lag = len(data[0]["fabric-lag"][3]["member"])
        url1 = '%s/api/v1/data/controller/core/switch' % (c.base_url)
        c.rest.get(url1)
        data1 = c.rest.content()
        spine_switch = 0
        for i in range(0,len(data1)):
            if data1[i]["fabric-switch-info"]["fabric-role"] == "spine":
                spine_switch = spine_switch + 1
                  
        if spine_switch == 2 and rack_lag == 2 and spine_lag == 2 and spine_bcast_lag == 2:
            helpers.test_log("Fabric Lag formation for Dual rack Dual spine is correct") 
        if spine_switch == 1 and rack_lag == 1 and spine_lag == 1 and spine_bcast_lag == 1:
            helpers.test_log("Fabric Lag formation for Dual rack Single spine is correct")       
        
        if not c.rest.status_code_ok():
           helpers.test_failure(c.rest.error())
        return c.rest.content()  
        