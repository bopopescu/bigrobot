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
        
        return True
    
    def rest_show_fabric_link(self):
        t = test.Test()
        c = t.controller()
        
        url = '%s/api/v1/data/controller/applications/bvs/info/fabric?select=link' % (c.base_url)       
        c.rest.get(url)
        
        return True
    
    def rest_configure_switch(self, switch):
        t = test.Test()
        c = t.controller()
                        
        url = '%s/api/v1/data/controller/core/switch-config[name="%s"]' % (c.base_url, switch)       
        c.rest.put(url, {"name": switch})
        
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())

        return c.rest.content()
    
    def rest_configure_dpid(self, switch, dpid):
        t = test.Test()
        c = t.controller()
        
        url = '%s/api/v1/data/controller/core/switch-config[name="%s"]' % (c.base_url, switch)       
        c.rest.patch(url, {"dpid": dpid})
        
        if not c.rest.status_code_ok():
            helpers.log("Error: Invalid argument: Invalid switch id (8-hex bytes): %s; switch %s doesn't exist" % (dpid,switch)) 
            helpers.test_failure(c.rest.error())

        return c.rest.content() 
    
    def rest_configure_fabric_role(self, switch, role):
        t = test.Test()
        c = t.controller()
        
        url = '%s/api/v1/data/controller/core/switch-config[name="%s"]' % (c.base_url, switch)       
        c.rest.patch(url, {"fabric-role": role})
        
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())

        return c.rest.content() 
    
    def rest_configure_leaf_group(self, switch, group):
        t = test.Test()
        c = t.controller()
        
        url = '%s/api/v1/data/controller/core/switch-config[name="%s"]' % (c.base_url, switch)       
        c.rest.patch(url, {"leaf-group": group})
        
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
            
        return c.rest.content() 
    
    def rest_remove_fabric_switch(self, switch=None):
        t = test.Test()
        c = t.controller()
        
        url = '%s/api/v1/data/controller/core/switch-config[name="%s"]' % (c.base_url, switch)       
        c.rest.delete(url, {"name": switch})
        
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
            
        return c.rest.content() 
    
    def rest_check_fabric_switch_connectivity(self):
        t = test.Test()
        c = t.controller()
        url = '%s/api/v1/data/controller/core/switch' % (c.base_url)       
        c.rest.get(url)
        data = c.rest.content()
        url1 = '%s/api/v1/data/controller/core/switch-config?config=true' % (c.base_url)
        c.rest.get(url1)
        data1 = c.rest.content()
        for i in range (0,len(data)):
            if data[i]["fabric-switch-info"]["suspended"] is True and (data1[i]["fabric-role"] == "leaf" or data1[i]["fabric-role"] == "spine"):
               helpers.test_failure("Fabric manager status is incorrect")
        helpers.log("Fabric manager status is correct")     
                                                                                 
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
                         
    def rest_check_fabric_switch_role(self, dpid, role):
        t = test.Test()
        c = t.controller()
        url = '%s/api/v1/data/controller/core/switch' % (c.base_url)       
        c.rest.get(url)
        data = c.rest.content()
        status = False
        helpers.log("data %s" % data[0])
        for i in range (0,len(data)):
            if data[i]["dpid"] == dpid and data[i]["fabric-switch-info"]["fabric-role"] == role:
                helpers.test_log("Fabric switch Role of %s is %s" % (str(data[i]["dpid"]), str(data[i]["fabric-switch-info"]["fabric-role"])))
                status = True
                return True
                break
        if status == False:
            helpers.test_failure("Fabric switch role removal Test Failed")      
                                                                              
        return False

    def rest_remove_fabric_role(self, switch, role=None):
        t = test.Test()
        c = t.controller()
        
        url = '%s/api/v1/data/controller/core/switch-config[name="%s"]/fabric-role' % (c.base_url, switch)       
        c.rest.delete(url, {"fabric-role": role})
        helpers.test_log("Output: %s" % c.rest.content_json())
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
            
        return c.rest.content()  
    
    def rest_verify_fabric_lag_from_leaf(self, dpid):
        # Function verifying the Lag type formation from the leaf nodes.
        t = test.Test()
        c = t.controller()
        url = '%s/api/v1/data/controller/core/switch[dpid="%s"]?select=fabric-lag' % (c.base_url, dpid)       
        c.rest.get(url)
        data = c.rest.content()
        helpers.log("lag-type content %d" % len(data[0]["fabric-lag"]))
        if data[0]["dpid"] == dpid:
            for i in range(0,len(data[0]["fabric-lag"])):
               if data[0]["fabric-lag"][i]["lag-type"] == "leaf-lag":
                   leaf_lag = len(data[0]["fabric-lag"][i]["member"])
               elif data[0]["fabric-lag"][i]["lag-type"] == "rack-lag":    
                   rack_lag = len(data[0]["fabric-lag"][i]["member"])
               elif data[0]["fabric-lag"][i]["lag-type"] == "spine-lag":
                   spine_lag = len(data[0]["fabric-lag"][i]["member"])
               elif data[0]["fabric-lag"][i]["lag-type"] == "spine-broadcast-lag":    
                   spine_bcast_lag = len(data[0]["fabric-lag"][i]["member"])
        helpers.log("data content %d %d %d %d" % (leaf_lag, rack_lag, spine_lag, spine_bcast_lag))
        url1 = '%s/api/v1/data/controller/core/switch' % (c.base_url)
        c.rest.get(url1)
        data1 = c.rest.content()
        spine_switch = 0
        for i in range(0,len(data1)):
             if data1[i]["fabric-switch-info"]["fabric-role"] == "spine":
                      spine_switch = spine_switch + 1
        if spine_switch == 2:
               if rack_lag == 4 and spine_lag == 4 and spine_bcast_lag == 4:
                  helpers.test_log("Fabric Lag formation for Dual rack Dual spine is correct") 
                  return True
               else:
                   helpers.test_failure("All Fabric lag for %s in dual rack is not formed" % dpid)
        elif spine_switch == 1:
               if rack_lag == 2 and spine_lag == 2 and spine_bcast_lag == 2:
                  helpers.test_log("Fabric Lag formation for Dual rack Single spine is correct") 
                  return True
               else:
                   helpers.test_failure("All fabric lag for %s dual rack single spine is not formed" % dpid)      
        else :
            return False
        
    def rest_verify_fabric_lag_from_spine(self, dpid):
        # Function verifying the Lag type formation from the spine nodes.
        t = test.Test()
        c = t.controller()
        url = '%s/api/v1/data/controller/core/switch[dpid="%s"]?select=fabric-lag' % (c.base_url, dpid)       
        c.rest.get(url)
        data = c.rest.content()
        helpers.log("lag-type content %d" % len(data[0]["fabric-lag"]))
        if data[0]["dpid"] == dpid:
            for i in range(0,len(data[0]["fabric-lag"])):
               if data[0]["fabric-lag"][i]["lag-type"] == "leaf-lag":
                   leaf_lag = len(data[0]["fabric-lag"][i]["member"])
               elif data[0]["fabric-lag"][i]["lag-type"] == "rack-lag":    
                   rack_lag = len(data[0]["fabric-lag"][i]["member"])
               elif data[0]["fabric-lag"][i]["lag-type"] == "spine-lag":
                   spine_lag = len(data[0]["fabric-lag"][i]["member"])
               elif data[0]["fabric-lag"][i]["lag-type"] == "spine-broadcast-lag":    
                   spine_bcast_lag = len(data[0]["fabric-lag"][i]["member"])
        helpers.log("data content %d %d %d %d" % (leaf_lag, rack_lag, spine_lag, spine_bcast_lag))
        url1 = '%s/api/v1/data/controller/core/switch' % (c.base_url)
        c.rest.get(url1)
        data1 = c.rest.content()
        spine_switch = 0
        for i in range(0,len(data1)):
             if data1[i]["fabric-switch-info"]["fabric-role"] == "spine":
                      spine_switch = spine_switch + 1
        if spine_switch == 2:
               if rack_lag == 4 and spine_lag == 4 and spine_bcast_lag == 4:
                  helpers.test_log("Fabric Lag formation for Dual rack Dual spine is correct") 
                  return True
               else:
                   helpers.test_failure("All Fabric lag for %s in dual rack is not formed" % dpid)
        elif spine_switch == 1:
               if rack_lag == 2 and spine_lag == 2 and spine_bcast_lag == 2:
                  helpers.test_log("Fabric Lag formation for Dual rack Single spine is correct") 
                  return True
               else:
                   helpers.test_failure("All fabric lag for %s dual rack single spine is not formed" % dpid)      
        else :
            return False
    
    
    def rest_verify_fabric_switch(self, dpid):
        t = test.Test()
        c = t.controller()
        url = '%s/api/v1/data/controller/core/switch[dpid="%s"]' % (c.base_url, dpid)       
        c.rest.get(url)
        data = c.rest.content()
        if data[0]["dpid"] == dpid:
            if data[0]["connected"]:
                if data[0]["fabric-switch-info"]["fabric-role"] != "virtual":
                    if data[0]["fabric-switch-info"]["fabric-role"] == "spine" and data[0]["fabric-switch-info"]["suspended"] == False:
                        helpers.log("Pass: Fabric switch connection status for spine is correct")
                        return True
                    elif data[0]["fabric-switch-info"]["fabric-role"] == "leaf" and data[0]["fabric-switch-info"]["suspended"] == False and data[0]["fabric-switch-info"]["leaf-group"] != '':
                        if data[0]["dpid"] == dpid and data[0]["fabric-switch-info"]["lacp-port-offset"] == 0:
                            helpers.log("Pass: Fabric switch connection status for %s dual leaf is correct" % str(data[0]["fabric-switch-info"]["switch-name"]))
                            return True
                        elif data[0]["dpid"] == dpid and data[0]["fabric-switch-info"]["lacp-port-offset"] == 100:
                            helpers.log("Pass: Fabric switch connection status for %s dual leaf is correct" % str(data[0]["fabric-switch-info"]["switch-name"]))
                            return True
                else:
                   helpers.log("Default fabric role is virtual for not configured fabric switches")                        
            elif data[0]["fabric-switch-info"]["suspended"] == False or data[0]["fabric-switch-info"]["suspended"] == True:
                helpers.test_failure("Fail: Switch is not connected , Fabric switch status still exists")
                return True    
        else :
            return False
      
    def rest_verify_fabric_link(self):
        t = test.Test()
        c = t.controller()
        url = '%s/api/v1/data/controller/core/switch/interface' % (c.base_url)      
        c.rest.get(url)
        data = c.rest.content()  
        fabric_interface = 0 
        for i in range(0,len(data[0])):
            if data[i]["type"] == "leaf" or data[i]["type"] == "spine":
                fabric_interface = fabric_interface + 1
        url1 = '%s/api/v1/data/controller/applications/bvs/info/fabric?select=link' % (c.base_url)
        c.rest.get(url1)
        data1 = c.rest.content()
        bidir_link = 0
        for i in range(0,len(data1[0]["link"])):
            if data1[0]["link"][i]["link-direction"] == "bidirectional":
                bidir_link = bidir_link + 1
        if bidir_link == fabric_interface/2:
            helpers.log("Pass: All Fabric links states are bidirectional")
        else:
            helpers.test_failure("Fail: Inconsistent state of fabric links. Fabric_Interface = %d , bidir_link = %d" % (fabric_interface, bidir_link))
        
                        
               
                  
        