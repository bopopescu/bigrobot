import autobot.helpers as helpers
import autobot.test as test
import re
import keywords.T5 as T5
import keywords.T5Platform as T5Platform 
 
class T5_longevity(object):
# This is for all the common function   - Mingtao
    def __init__(self):
        pass


################  start of commit #############
 
    def rest_add_tenant_vns_scale(self, tenantcount, vnscount):
 
        t5 = T5.T5()   
        
        for count in range(0,int(tenantcount)):
            tenant = 'T'+str(count)
            if not t5.rest_add_tenant(tenant):      
                helpers.test_failure("USER Error: tenant is NOT configured successfully")               
            if not t5.rest_add_vns_scale(tenant, vnscount):
                helpers.test_failure("USER Error: VNS is NOT configured successfully for tenant %s" % tenant)  
  
        return True
                   
    def ip_to_list(self,ip):
        helpers.test_log("Entering ==> ip to list: %s"  % ip)           
        return  ip.split('.')


    def rest_get_fabric_interface_info(self, switch, intf):
        '''
        Function to get the specific fabric interface status
        Input:  Rest Output from the function (show_fabric_interface())
        Output: validation of the fabric interface status
        '''
        helpers.test_log("Entering ==> rest_get_fabric_interface  for switch: %s  interface: %s"  % (switch,  intf))     
        t = test.Test()
        c = t.controller('master')
        url1 = '/api/v1/data/controller/core/switch[name="%s"]' % (switch)
        c.rest.get(url1)
        data1 = c.rest.content()
        dpid = data1[0]["dpid"]
        url = '/api/v1/data/controller/core/switch[interface/name="%s"][dpid="%s"]?select=interface[name="%s"]' % (intf, dpid, intf)
        c.rest.get(url)
        intfinfo={}
        data = c.rest.content()
        if len(data) != 0:
            intfinfo['state'] = data[0]["interface"][0]["state"]
            intfinfo['name']= data[0]["interface"][0]["name"]
            intfinfo['type']= data[0]["interface"][0]["type"]
            intfinfo['lacp']= data[0]["interface"][0]["lacp-state"]  
            try:  
                intfinfo['downreason']= data[0]["interface"][0]["interface-down-reason"]   
            except:
                helpers.test_log("interface-down-reason does not exist for:  %s"  % intf)  
            helpers.test_log("interface info is: %s"  % intfinfo)                          
            return intfinfo
        else:
            helpers.test_failure("Given fabric interface is not valid")
            return False
           
           
           
           