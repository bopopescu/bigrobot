''' 
###  WARNING !!!!!!!
###  
###  This is where common code for BigWire will go in.
###  
###  To commit new code, please contact the Library Owner: 
###  Animesh Patcha (animesh.patcha@bigswitch.com)
###
###  DO NOT COMMIT CODE WITHOUT APPROVAL FROM LIBRARY OWNER
###
###  Last Updated: 01/30/2014
###
###  WARNING !!!!!!!
'''
import autobot.helpers as helpers
import autobot.test as test
import keywords.AppController as AppController

class BigWire(object):

    def __init__(self):
        pass

###################################################
# All Bigtap Show Commands Go Here:
###################################################

    def rest_show_bigwire_command(self, bigwire_key):
        '''
            Objective:
             - Execute CLI Commands "show bigwire summary", "show bigwire tenant", "show bigwire pseudowire" and "show bigwire  datacenter"
        
            Input:
            | 'bigwire_key' | BigWire Keyword  datacenter for "show bigwire  datacenter",  pseudowire for "show bigwire pseudowire", tenant for "show bigwire tenant" and "summary" for "show bigwire summary" |

            Return Value: 
            - Content as a dictionary after execution of command.
                
        '''

        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('main')
            try:
                if bigwire_key == "datacenter":
                    bwKeyword = "datacenter-info"  # "show bigwire datacenter"
                elif bigwire_key == "pseudowire":
                    bwKeyword = "pseudowire-info"  # "show bigwire pseudowire"
                elif bigwire_key == "tenant":
                    bwKeyword = "tenant-info"  # "show bigwire tenant"
                else :
                    bwKeyword = "info"  # "show bigwire summary"
                url = '/api/v1/data/controller/applications/bigwire/%s' % (str(bwKeyword))
                c.rest.get(url)
            except:
                helpers.test_failure(c.rest.error())
                return False
            else:
                if not c.rest.status_code_ok():
                    helpers.test_failure(c.rest.error())
                content = c.rest.content()
                return content

###################################################
# All Bigtap Verify Commands Go Here:
###################################################


###################################################
# All Bigtap Configuration Commands Go Here:
###################################################

    def rest_add_bigwire_datacenter(self, datacenter_name):
        '''
            Objective:
            - Create BigWire Datacenter. 
            - Similar to cli command "bigwire datacenter datacenter_name"
        
            Input:    
            | datacenter_name | Datacenter Name |
            
            Return value: 
            - True on success
            - False otherwise
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('main')
            try:
                url = '/api/v1/data/controller/applications/bigwire/datacenter[name="%s"]' % (str(datacenter_name))
                c.rest.put(url, {"name": str(datacenter_name)})
            except:
                helpers.test_failure(c.rest.error())
                return False
            else:
                if not c.rest.status_code_ok():
                    helpers.test_failure(c.rest.error())
                    return False
                else:
                    return True

    def rest_add_switch_datacenter(self, node, datacenter_name, zone_name):
        '''
            Objective:
            - Add switch to a datacenter
        
           Input:
            | datacenter_name | Datacenter Name | 
            | switch_dpid | DPID of switch | 
            | zone_name | Zone to which switch belongs | 
           
            Return value: 
            - True on success
            - False otherwise
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('main')
            AppCommon = AppController.AppController()
            switch_dpid = AppCommon.rest_return_switch_dpid_from_ip(node)
            try:
                url = '/api/v1/data/controller/applications/bigwire/datacenter[name="%s"]/member-switch[dpid="%s"]' % (str(datacenter_name), str(switch_dpid))
                c.rest.put(url, {"zone": str(zone_name), "dpid": str(switch_dpid)})
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

    def rest_add_bigwire_pseudowire(self, pseudowire_name, node_1, intf_name_1, node_2, intf_name_2, vlan=0):
        '''
            Objective:
            - Create a bigwire pseudowire
        
            Input:
            | pseudowire_name | Name of bigwire pseudowire | 
            | switch_dpid_1 | DPID of first Switch | 
            | intf_name_1 | Uplink port/interface name for first Switch | 
            | switch_dpid_2 | DPID of second Switch | 
            | intf_name_2 | Uplink port/interface name for second Switch | 
            | Vlan | Vlan Number (in case of Vlan Mode, defaults to 0 for port-mode) | 
           
            Return value: 
            - True on success
            - False otherwise
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('main')
            AppCommon = AppController.AppController()
            switch_dpid_1 = AppCommon.rest_return_switch_dpid_from_ip(node_1)
            switch_dpid_2 = AppCommon.rest_return_switch_dpid_from_ip(node_2)
            try:
                url = '/api/v1/data/controller/applications/bigwire/pseudo-wire[name="%s"]' % (str(pseudowire_name))
                if vlan == 0:
                    c.rest.put(url, {"interface1": str(intf_name_1), "switch2": str(switch_dpid_2), "switch1": str(switch_dpid_1), "interface2": str(intf_name_2), "name": str(pseudowire_name)})
                else:
                    c.rest.put(url, {"interface1": str(intf_name_1), "switch2": str(switch_dpid_2), "switch1": str(switch_dpid_1), "interface2": str(intf_name_2), "name": str(pseudowire_name), "vlan": int(vlan) })
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

    def rest_add_bigwire_tenant(self, tenant_name):
        '''
            Objective:
            - Create BigWire Tenant. 
            - Similar to cli command "bigwire tenant bw5bw7"
        
            Input:    
            | tenant_name | Tenant Name |
                
            Return value: 
            - True on success
            - False otherwise
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('main')
            try:
                url = '/api/v1/data/controller/applications/bigwire/tenant[name="%s"]' % (str(tenant_name))
                c.rest.put(url, {"name": str(tenant_name)})
            except:
                helpers.test_failure(c.rest.error())
                return False
            else:
                helpers.test_log(c.rest.content_json())
                return True

    def rest_add_switch_to_tenant(self, node, tenant_name, intf_name, vlan=0):
        '''
            Objective:
            - Add switch to a tenant
        
           Input:
           | tenant_name    Tenant Name  
           | switch_dpid        DPID of switch
               
               intf_name     Interface Name
               
               Vlan            Tenant Vlan Number
           
            Return value: 
            - True on success
            - False otherwise
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('main')
            AppCommon = AppController.AppController()
            switch_dpid = AppCommon.rest_return_switch_dpid_from_ip(node)
            try:
                url = '/api/v1/data/controller/applications/bigwire/tenant[name="%s"]/tenant-interface[interface="%s"][switch="%s"]' % (str(tenant_name), str(intf_name), str(switch_dpid))
                if vlan == 0:
                    c.rest.put(url, {"interface": str(intf_name), "switch": str(switch_dpid)})
                else:
                    c.rest.put(url, {"interface": str(intf_name), "tenant-vlan": [{"vlan": int(vlan)}], "switch": str(switch_dpid)})
            except:
                helpers.test_failure(c.rest.error())
                return False
            else:
                helpers.test_log(c.rest.content_json())
                return True

    def rest_delete_switch_from_tenant(self, node, tenant_name, intf_name, vlan=0):
        '''
            Objective:
            - Delete switch from a tenant
        
           Input:
           | tenant_name    Tenant Name  
           | switch_dpid        DPID of switch
               
               intf_name     Interface Name
               
               Vlan            Tenant Vlan Number
           
            Return value: 
            - True on success
            - False otherwise
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('main')
            AppCommon = AppController.AppController()
            switch_dpid = AppCommon.rest_return_switch_dpid_from_ip(node)
            try:
                if vlan == 0:
                    url = '/api/v1/data/controller/applications/bigwire/tenant[name="%s"]/tenant-interface[interface="%s"][switch="%s"]' % (str(tenant_name), str(intf_name), str(switch_dpid))
                    c.rest.delete(url, {})
                else:
                    url = '/api/v1/data/controller/applications/bigwire/tenant[name="%s"]/tenant-interface[switch="%s"][interface="%s"]/tenant-vlan[vlan=%d]' % (str(tenant_name), str(switch_dpid), str(intf_name), int(vlan))
                    c.rest.delete(url, {})
            except:
                return False
            else:
                helpers.test_log(c.rest.content_json())
                return True

    def rest_delete_tenant(self, tenant_name):
        '''
        Objective:
        - Delete a tenant
        
        Input:
        | tenant_name | Tenant Name |
        
        Return value: 
        - True on success
        - False otherwise
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('main')
            try:
                url = '/api/v1/data/controller/applications/bigwire/tenant[name="%s"]' % (str(tenant_name))
                c.rest.delete(url, {})
            except:
                helpers.test_failure(c.rest.error())
                return False
            else:
                helpers.test_log(c.rest.content_json())
                return True

    def rest_delete_pseudowire(self, pseudowire_name):
        '''
        Objective:
        - Delete a pseudowire
        
        Input:
        | pseudowire_name | Pseudowire Name |
           
        Return value: 
        - True on success
        - False otherwise
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('main')
            try:
                url = '/api/v1/data/controller/applications/bigwire/pseudo-wire[name="%s"]' % (str(pseudowire_name))
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

    def rest_delete_datacenter(self, datacenter_name):
        '''
        Objective:
        - Delete a datacenter_name
        
        Input:
        | datacenter_name | datacenter name | 
           
        Return value: 
        - True on success
        - False otherwise
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('main')
            try:
                url = '/api/v1/data/controller/applications/bigwire/datacenter[name="%s"]' % (str(datacenter_name))
                c.rest.delete(url, {})
            except:
                helpers.test_failure(c.rest.error())
                return False
            else:
                helpers.test_log(c.rest.content_json())
                return True

    def rest_verify_dict_key(self, content, index, key):
        ''' Given a dictionary, return the value for a particular key
        
            Input:Dictionary, index and required key.
            
            Return Value:  return the value for a particular key
        '''
        return content[int(index)][str(key)]
