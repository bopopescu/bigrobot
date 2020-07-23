import autobot.helpers as helpers
import autobot.test as test
import re


class T5Fabric(object):

    def __init__(self):
#        t = test.Test()
#        c = t.controller()
        pass        
#        url = '%s/api/v1/auth/login' % c.base_url
#        result = c.rest.post(url, {"user":"admin", "password":"adminadmin"})
#        session_cookie = result['content']['session_cookie']
#        c.rest.set_session_cookie(session_cookie)
        
       
    def rest_show_fabric_switch(self):
        '''Return the list of connected switches
                                       
            Returns: gives list of connected switches
        '''
        t = test.Test()
        c = t.controller()
        url = '%s/api/v1/data/controller/core/switch' % (c.base_url)
        c.rest.get(url)
        
        return True
    
    def rest_show_fabric_link(self):
        '''Return the list of fabric links       
                    
            Returns: Print the Total fabric links
        '''
        t = test.Test()
        c = t.controller()
        
        url = '%s/api/v1/data/controller/applications/bvs/info/fabric?select=link' % (c.base_url)       
        c.rest.get(url)
        
        return True
    
    def rest_add_switch(self, switch):
        '''add the fabric switch 
        
            Input:
                    switch        Name of the switch
                                       
            Returns: add the fabric switch
        '''
        t = test.Test()
        c = t.controller()
                        
        url = '%s/api/v1/data/controller/core/switch-config[name="%s"]' % (c.base_url, switch)       
        c.rest.put(url, {"name": switch})
        
        if not c.rest.status_code_ok():
            helpers.log("Error: Invalid argument: syntax: expected [a-zA-Z][-.0-9a-zA-Z_]*$ for: %s" % (switch))
            helpers.test_failure(c.rest.error())

        return c.rest.content()
    
    def rest_add_dpid(self, switch, dpid):
        t = test.Test()
        c = t.controller()
        
        url = '%s/api/v1/data/controller/core/switch-config[name="%s"]' % (c.base_url, switch)       
        c.rest.patch(url, {"dpid": dpid})
        
        if not c.rest.status_code_ok():
            helpers.log("Error: Invalid argument: Invalid switch id (8-hex bytes): %s; switch %s doesn't exist" % (dpid,switch)) 
            helpers.test_failure(c.rest.error())

        return c.rest.content() 
    
    def rest_add_fabric_role(self, switch, role):
        t = test.Test()
        c = t.controller()
        
        url = '%s/api/v1/data/controller/core/switch-config[name="%s"]' % (c.base_url, switch)       
        c.rest.patch(url, {"fabric-role": role})
        
        if not c.rest.status_code_ok():
            helpers.log("Error: no matching commands")
            helpers.test_failure(c.rest.error())

        return c.rest.content() 
    
    def rest_add_leaf_group(self, switch, group):
        t = test.Test()
        c = t.controller()
        
        url = '%s/api/v1/data/controller/core/switch-config[name="%s"]' % (c.base_url, switch)       
        c.rest.patch(url, {"leaf-group": group})
        
        if not c.rest.status_code_ok():
            helpers.log("Error: Invalid argument: syntax: expected [a-zA-Z][-.0-9a-zA-Z_]*$ for: %s" % (group))
            helpers.test_failure(c.rest.error())
            
        return c.rest.content()
    
    def rest_delete_leaf_group(self, switch, group=None):
        ''' 
           Function to delete the specific leaf group
           Input:  Switch name
        '''
        t = test.Test()
        c = t.controller()
        url = '%s/api/v1/data/controller/core/switch-config[name="%s"]/leaf-group' % (c.base_url, switch)
        c.rest.delete(url, {"leaf-group": None}) 
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
        return c.rest.content()   
    
    def rest_delete_fabric_switch(self, switch=None):
        t = test.Test()
        c = t.controller()
        
        url = '%s/api/v1/data/controller/core/switch-config[name="%s"]' % (c.base_url, switch)       
        c.rest.delete(url, {"name": switch})
        
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
            
        return c.rest.content() 
    
    def rest_verify_fabric_switch_all(self):
        t = test.Test()
        c = t.controller()
        url = '%s/api/v1/data/controller/core/switch' % (c.base_url)       
        c.rest.get(url)
        data = c.rest.content()
        for i in range (0,len(data)):
            if data[i]["fabric-switch-info"]["suspended"] is True and (data[i]["fabric-switch-info"]["fabric-role"] == "leaf" or data[i]["fabric-switch-info"]["fabric-role"] == "spine"):
                helpers.test_failure("Fabric manager status is incorrect")
            elif data[i]["fabric-switch-info"]["suspended"] is False and (data[i]["fabric-switch-info"]["fabric-role"] == "virtual"):
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
                helpers.test_failure("%s Fabric Links not deleted" % str(data[i]["link"]["dst"]["switch-info"]["switch-name"])) 
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
                helpers.test_log("%s Fabric Links not deleted" % str(data[i]["link"]["dst"]["switch-info"]["switch-name"])) 
                                                             
        return True 
                         
    def rest_verify_fabric_switch_role(self, dpid, role):
        t = test.Test()
        c = t.controller()
        url = '%s/api/v1/data/controller/core/switch' % (c.base_url)       
        c.rest.get(url)
        data = c.rest.content()
        status = False
        for i in range (0,len(data)):
            if data[i]["dpid"] == dpid and data[i]["fabric-switch-info"]["fabric-role"] == role:
                helpers.test_log("Fabric switch Role of %s is %s" % (str(data[i]["dpid"]), str(data[i]["fabric-switch-info"]["fabric-role"])))
                status = True
                return True
                break
        if status == False:
            helpers.test_failure("Fabric switch role removal Test Failed")      
                                                                              
        return False

    def rest_delete_fabric_role(self, switch, role=None):
        t = test.Test()
        c = t.controller()
        
        url = '%s/api/v1/data/controller/core/switch-config[name="%s"]/fabric-role' % (c.base_url, switch)       
        c.rest.delete(url, {"fabric-role": role})
        helpers.test_log("Output: %s" % c.rest.content_json())
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
            
        return c.rest.content()  
           
    def rest_verify_fabric_lag(self, switch):
        ''' 
          Function to verify Lag formation from the fabric switches
          Input : specific switch name
          output : Will provide the No of lag it is suppose to form between Spine and Leaf in Dual Rack or single rack setup
        '''   
        t = test.Test()
        c = t.controller()
        url = '%s/api/v1/data/controller/core/switch[name="%s"]/interface' % (c.base_url, switch)       
        c.rest.get(url)
        data = c.rest.content()
        url1 = '%s/api/v1/data/controller/core/switch[name="%s"]' % (c.base_url, switch)
        c.rest.get(url1)
        data1 = c.rest.content()
        url2 = '%s/api/v1/data/controller/core/switch[name="%s"]?select=fabric-lag' % (c.base_url, switch)
        c.rest.get(url2)
        data3 = c.rest.content()
        if str(data1[0]["fabric-switch-info"]["switch-name"]) == str(switch):
            if data1[0]["fabric-switch-info"]["fabric-role"] == "spine":
                fabric_interface = 0
                rack_lag = 0
                for i in range(0,len(data)):
                    if data[i]["type"] == "leaf":
                        fabric_interface = fabric_interface + 1
                for i in range(0,len(data3[0]["fabric-lag"])):  
                        if (data3[0]["fabric-lag"][i]["lag-type"]) == "rack-lag":
                            rack_lag = rack_lag + int(len(data3[0]["fabric-lag"][i]["member"]))
                if (int(rack_lag) == int(fabric_interface)): 
                                helpers.log("No of Rack lag from  %s is correct,Expected = %d, Actual = %d " % (switch, fabric_interface, rack_lag))
                                return True
                else:
                                helpers.test_failure("No of Rack lag from %s is incorrect,Expected = %d, Actual = %d " % (switch, fabric_interface, rack_lag))
                                return False 
            elif data1[0]["fabric-switch-info"]["fabric-role"] == "leaf":
                    fabric_spine_interface = 0
                    fabric_peer_interface = 0
                    for i in range(0,len(data)):
                                if data[i]["type"] == "spine":
                                    fabric_spine_interface = fabric_spine_interface + 1
                                    
                                elif data[i]["type"] == "leaf":
                                    fabric_peer_interface = fabric_peer_interface + 1
                                     
                    for i in range(0,len(data3[0]["fabric-lag"])):
                                        if data3[0]["fabric-lag"][i]["lag-type"] == "spine-lag":
                                            if (int(len(data3[0]["fabric-lag"][i]["member"])) == int(fabric_spine_interface)):  
                                                helpers.log("Spine lag formation from leaf switch %s is correct,Expected = %d, Actual = %d, " % (switch, fabric_spine_interface, len(data3[0]["fabric-lag"][i]["member"])))
                                                return True
                                            else:
                                                helpers.test_failure(" Spine lag formation from leaf %s switch is not correct,Expected = %d, Actual = %d" % (switch, fabric_spine_interface, len(data3[0]["fabric-lag"][i]["member"])))
                                                return False 
                                        elif data3[0]["fabric-lag"][i]["lag-type"] == "spine-broadcast-lag":
                                                if len(data3[0]["fabric-lag"][i]["member"]) == (int(self.rest_verify_no_of_rack()) * fabric_spine_interface):
                                                    helpers.log("Spine Broadcast lag from leaf switch %s is correct , Actual = %d , Expected = %d" % (switch, int(self.rest_get_no_of_rack()), fabric_spine_interface))
                                                    return True
                                                else:
                                                        helpers.test_failure("Spine Broadcast lag from leaf switch %s is not correct,expected = %d,actual = %d" % (switch, (int(self.rest_get_no_of_rack()) * fabric_spine_interface), len(data3[0]["fabric-lag"][i]["member"])))
                                                        return False
                                        elif data3[0]["fabric-lag"][i]["lag-type"] == "leaf-lag":       
                                            if len(data3[0]["fabric-lag"][i]["member"]) == fabric_peer_interface:  
                                                helpers.log("Peer lag formation from leaf switch %s is correct,Expected = %d, Actual = %d" % (switch, fabric_peer_interface, len(data3[0]["fabric-lag"][i]["member"])))
                                                return True
                                            else:
                                                helpers.test_failure(" Spine lag formation from leaf %s switch is not correct,expected= %d,Actual= %d" % (switch, fabric_peer_interface, len(data3[0]["fabric-lag"][i]["member"])))
                                                return False
        else :
            return False
    
    
    def rest_verify_fabric_switch(self, dpid):
        # Function verify fabric switch status for default as well after fabric role configuration
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
                elif data[0]["fabric-switch-info"]["suspended"] == True:
                        helpers.log("Default fabric role is virtual for not added fabric switches")
                        return True
                else: 
                        helpers.test_failure("Fabric role is virual but suspended = False ") 
                        return False                        
            elif data[0]["fabric-switch-info"]["suspended"] == False or data[0]["fabric-switch-info"]["suspended"] == True:
                helpers.test_failure("Fail: Switch is not connected , Fabric switch status still exists")
                return False    
        else :
            return False
      
    def rest_verify_fabric_link(self):
        t = test.Test()
        c = t.controller()
        url = '%s/api/v1/data/controller/core/switch/interface' % (c.base_url)      
        c.rest.get(url)
        data = c.rest.content()  
        fabric_interface = 0
        for i in range(0,len(data)):
            if data[i]["type"] == "leaf" or data[i]["type"] == "spine":
                fabric_interface = fabric_interface + 1
        url1 = '%s/api/v1/data/controller/applications/bvs/info/fabric?select=link' % (c.base_url)
        c.rest.get(url1)
        data1 = c.rest.content()
        bidir_link = 0
        if not((data1 and True) or False):       
            for i in range(0,len(data1[0]["link"])):
                if data1[0]["link"][i]["link-direction"] == "bidirectional":
                    bidir_link = bidir_link + 1
                    if bidir_link == fabric_interface/2:
                        helpers.log("Pass: All Fabric links states are bidirectional")
                    else:
                        helpers.test_failure("Fail: Inconsistent state of fabric links. Fabric_Interface = %d , bidir_link = %d" % (fabric_interface, bidir_link))
        else:
            helpers.log("Fabric switches are misconfigued")
                        
    def rest_verify_no_of_rack(self):
        t = test.Test()
        c = t.controller()
        url = '%s/api/v1/data/controller/core/switch' % (c.base_url)
        c.rest.get(url)
        data = c.rest.content()
        rack = []
        rack_count = 0
        for i in range(0,len(data)):
            if data[i]["fabric-switch-info"]["fabric-role"] == "leaf":
                if data[i]["fabric-switch-info"]["leaf-group"] == None:
                    rack_count = rack_count + 1
                elif not data[i]["fabric-switch-info"]["leaf-group"] in rack:
                    rack.append(data[i]["fabric-switch-info"]["leaf-group"]) 
                   
        total_rack = rack_count + len(rack)
        helpers.log("Total Rack in the Topology: %d" % total_rack)
        return total_rack
    
    def rest_verify_no_of_spine(self):
        t = test.Test()
        c = t.controller()
        url = '%s/api/v1/data/controller/core/switch' % (c.base_url)
        c.rest.get(url)
        data = c.rest.content()
        list_spine = []
        for i in range(0,len(data)):
            if data[i]["fabric-switch-info"]["fabric-role"] == "spine":
                list_spine.append(data[i]["fabric-switch-info"]["switch-name"]) 
                   
        helpers.log("Total Spine in the topology: %d" % len(list_spine))
        return list_spine
    
    def rest_verify_rack_lag_from_leaf(self, switcha, switchb):
        '''Verify Rack lag formation for the leaf switch mentioned in the variables to all the racks
            Input: Leaf switch name  , any down event you are expecting to verify on
            Output: Will check the total no of spine switches and compare against the rack connection spine switches.
        ''' 
        t = test.Test()
        c = t.controller()
        url = '%s/api/v1/data/controller/core/switch[name="%s"]?select=fabric-lag' % (c.base_url, switcha)
        c.rest.get(url)
        data = c.rest.content()
        for i in range(0,len(data[0]["fabric-lag"])):
            if data[0]["fabric-lag"][i]["lag-type"] == "rack-lag":
                actual_spine = []
                for j in range(0,len(data[0]["fabric-lag"][i]["member"])):
                    if data[0]["fabric-lag"][i]["member"][j]["dst-switch"] not in actual_spine:
                        actual_spine.append(data[0]["fabric-lag"][i]["member"][j]["dst-switch"])
                for j in range(0,len(actual_spine)):
                    if (str(actual_spine[j]) == str(switchb)):
                        helpers.log("Rack connectivity from leaf switch %s using all the spine switches are up" % switcha)
                        return True
                           
    def rest_verify_forwarding_lag(self, dpid, switch):
        '''Verify Edge port  Information in Controller Forwarding Table
        
            Input:  Specific DPID of the switch and also the switch name of the specific device     
            
            Return: Match forwarding table lag/Port for peer switch edge ports
        '''
        t = test.Test()
        c = t.controller()
        url = '%s/api/v1/data/controller/applications/bvs/info/forwarding/network/switch[switch-name="%s"]/lag-table' % (c.base_url, switch)
        c.rest.get(url)
        data = c.rest.content()
        url1 = '%s/api/v1/data/controller/core/switch[dpid="%s"]' % (c.base_url, dpid)
        c.rest.get(url1)
        data1 = c.rest.content()
        url2 = '%s/api/v1/data/controller/core/switch[name="%s"]?select=fabric-lag' % (c.base_url, switch)
        c.rest.get(url2)
        data2 = c.rest.content()
        peer_intf = []
        for i in range(0,len(data2[0]["fabric-lag"])):
            if data2[0]["fabric-lag"][i]["lag-type"] == "leaf-lag":
                interface = re.sub("\D", "", data2[0]["fabric-lag"][i]["member"][0]["src-interface"])
                peer_intf.append(int(interface))                            
        if data1[0]["fabric-switch-info"]["leaf-group"] == None:
            for i in range(0,len(data)):
                for j in range(0,len(data[i]["port"])):
                    if (data[i]["port"][j]["port-num"] == peer_intf[0]):
                        helpers.test_failure("Peer switch edge ports are not deleted from lag table")
                        return False
                    else:
                        helpers.log("Peer switch edge ports are deleted from forwarding lag table")  
                        return True
        else:
                for i in range(0,len(data)):
                    for j in range(0,len(data[i]["port"])):
                        if (data[i]["port"][j]["port-num"]) == (peer_intf[0]):
                            helpers.log("Peer switch edge ports are properly added in forwarding table")
                            return True
                        else:
                            helpers.test_failure("Peer switch edge ports are not added in forwarding table")
                            return False
                    
    def rest_verify_fabric_interface_lacp(self, switch, intf):
        t = test.Test()
        c = t.controller()
        url = '%s/api/v1/data/controller/core/switch[name="%s"]/interface[name="%s"]' % (c.base_url, switch, intf)      
        c.rest.get(url)
        data = c.rest.content()  
        if data[0]["lacp-active"] == True:
            if data[0]["lacp-partner-info"]["system-mac"] != None:
                helpers.log("LACP Neibhour Is Up and active")
                return True
            else:
                helpers.test_failure("LACP is enabled , LACP Partner is not seen , check the floodlight logs")
                return False
        else:
            helpers.log("LACP is not enabled on the %s = %s" % (switch, intf))
            
    def rest_verify_fabric_error_dual_tor_peer_link(self, rack):
        t = test.Test()
        c = t.controller()
        url = '%s/api/v1/data/controller/applications/bvs/info/fabric/errors/dual-tor/peer-link-absent' % (c.base_url)      
        c.rest.get(url)
        data = c.rest.content()
        if not((data and True) or False):  
            if len(data) != 0:
                if data["name"] == rack:
                    helpers.log("Fabric error reported for %s" % data["name"])
                    return True
                else:
                    helpers.test_failure("No Fabric error Reported for dual tor no peer link for rack %s" % data["name"])
                    return False
            else:
                helpers.log("Fabric error will be none")              
                
    def rest_verify_forwarding_port_table(self, switch): 
        t = test.Test()
        c = t.controller()
        url = '%s/api/v1/data/controller/applications/bvs/info/forwarding/network/switch[switch-name="%s"]/port-table' % (c.base_url, switch) 
        c.rest.get(url)          
        if not c.rest.status_code_ok():
            helpers.log("Error: forwarding output table is not returning any value") 
            helpers.test_failure(c.rest.error())        
                
    def rest_show_fabric_interface(self, switch, intf):
        ''' 
        Function to get the fabric interface status for validation
        Input: switch name and interface
        Output" Rest output of the fabric interface for various validation
        '''
        t = test.Test()
        c = t.controller()
        url = '%s/api/v1/data/controller/core/switch[name="%s"]/interface[name="%s"]' % (c.base_url, switch, intf) 
        c.rest.get(url) 
        return c.rest.content()
    
    def rest_verify_fabric_interface(self, switch, intf): 
        ''' 
        Function to verify the specific fabric interface status 
        Input:  Rest Output from the function (show_fabric_interface())
        Output" validation of the fabric interface status
        '''
        t = test.Test()
        c = t.controller()
        url = '%s/api/v1/data/controller/core/switch[name="%s"]/interface[name="%s"]' % (c.base_url, switch, intf) 
        c.rest.get(url)  
        data = c.rest.content()
        helpers.log("Data %s" % data)
        if len(data) != 0:
            if data[0]["state"] == "down" and data[0]["type"] == "unknown":
                helpers.log("Interface is connected to spine or Physical Interface status is down for the leaf switch") 
            elif data[0]["state"] == "up" and data[0]["type"] == "edge":
                    helpers.log("Inteface is connected to leaf and it is a edge port")
            elif data[0]["state"] == "up" and data[0]["type"] == "leaf" or data[0]["state"] == "up" and data[0]["type"] == "spine":
                    helpers.log("Interface is fabric interface")
            else:
                    helpers.test_failure("Interface status is not known to the fabric system , Please check the logs")
        else:
            helpers.test_failure("Given fabric interface is not valid")              
                          
                 
    def rest_verify_forwarding_port_edge(self, switcha, switchb): 
        t = test.Test()
        c = t.controller()
        url_a = '%s/api/v1/data/controller/applications/bvs/info/forwarding/network/switch[switch-name="%s"]/port-table' % (c.base_url, switcha) 
        c.rest.get(url_a)          
        data = c.rest.content()
        url_b = '%s/api/v1/data/controller/applications/bvs/info/forwarding/network/switch[switch-name="%s"]/port-table' % (c.base_url, switchb)
        c.rest.get(url_b)
        data1 = c.rest.content()
        if data[0]["lag-id"] == data1[0]["lag-id"]: 
            helpers.log("Portgroup Lag id creation in forwarding table is correct for dual rack") 
        else:
            helpers.test_failure("Portgroup Lag id creation in forwarding table does not match for dual rack , check the logs") 
            
    def ixia_verify_traffic_rate(self, tx_value, rx_value):
        tx = int(tx_value)
        rx = int(rx_value)
        if (rx >= (tx - 5)) and (rx <= (tx + 5)):
            helpers.log("Pass:Traffic forwarded between 2 endpoints tx_rate:%d,rx_rate:%d" % (tx, rx))
            return True
        else:
            helpers.test_failure("Fail:Traffic forward between 2 endpoints tx_rate:%d,rx_rate:%d" % (tx, rx))
            return False
                                   
     
    def Dump_Show_Commands(self):
        t = test.Test()
        c = t.controller('main')
        cmdList = [
           'show running-config',
           'show debug counters',
           'show cluster details',
           'show switch',
           'show fabric switch',
           'show fabric interface',
           'show fabric lacp',
           'show fabric lag',
           'show fabric link',
           'show fabric error',
           'show tenant',
           'show vns',
           'show endpoints',
           'show forwarding',
           ]
        content=""
        for cmd in cmdList:
            c.cli(cmd)
            content = content + c.cli_content()
        return content