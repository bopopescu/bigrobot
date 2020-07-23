import autobot.helpers as helpers
import autobot.test as test
import keywords.T5 as T5
import string
import telnetlib
import re


class  T5SwitchTraffic(object):
    
    
    def __init__(self):
        pass
     
    def rest_get_switch_dpid(self, switch):
        '''
        To get Switch DPID and use in the same class object
        '''
        t = test.Test()
        c = t.controller('main')

        url = '/api/v1/data/controller/applications/bcf/info/fabric/switch[name="%s"]' % (switch)
        c.rest.get(url)
        data = c.rest.content()
        dpid = data[0]["dpid"]
        return dpid
     
    def rest_clear_switch_interface_counter (self, switch, intf):
        
            ''' Function to clear the switch interface counter. 
            input - switch, interface 
            output - none
           ''' 
            t = test.Test()
            c = t.controller('main')
            T5 = T5.T5()
            dpid = self.rest_get_switch_dpid(switch)
            helpers.log("The switch is %s,dpid is %s and interface is %s"  % (switch, dpid, intf))
            url = ('/api/v1/data/controller/applications/bcf/info/statistic/interface-counter[switch-dpid="%s"]/interface[name="%s"]' % dpid, intf)
            
            try:
                helpers.log("The switch dpid is %s and interface is %s"  % (dpid, intf) )
                c.rest.delete(url, {})
                return  True
            
            except:
                helpers.log("Could not get the rest output.see log for errors\n")
                return  False    
    
    def rest_get_switch_interface_stats (self, switch, intf, stat="txstat"):
            ''' Function to clear the switch interface counter. 
                input - switch, interface 
                output - none
            '''
            t = test.Test()
            fabric = T5.T5()
            c = t.controller('main')
            dpid = fabric.rest_get_dpid(switch)
            #dpid = self.rest_get_switch_dpid(switch)
            helpers.log("The switch is %s,dpid is %s and interface is %s"  % (switch, dpid, intf))
            url = '/api/v1/data/controller/applications/bcf/info/statistic/interface-counter[interface/name="%s"][switch-dpid="%s"]?select=interface[name="%s"]' % (intf, dpid, intf)
            
            try:
                c.rest.get(url)
                data = c.rest.content()
                helpers.log("The output data is %s" % data[0])
                intf1 = data[0]["interface"][0]["name"]
                txstat1 = data[0]["interface"][0]["counter"]["tx-unicast-packet"]
                rxstat1 = data[0]["interface"][0]["counter"]["rx-unicast-packet"]
                helpers.log("The output intf %s, tx %d , rx %d" % (intf1, txstat1, rxstat1))
                helpers.log("The return asked is %s" % stat)
                if ("txstat" in stat):
                    return  txstat1
                if ("rxstat" in stat):
                    return  rxstat1
                else:
                    return  True
            
            except:
                helpers.log("Could not get the rest output.see log for errors\n")
                return  False
            
            