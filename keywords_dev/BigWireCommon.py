import autobot.helpers as helpers
import autobot.test as test
from BigTapCommonShow import BigTapCommonShow
from Exscript.protocols import SSH2
from Exscript import Account, Host


class BigWireCommon(object):

    def __init__(self):
        t = test.Test()
        self.btc=BigTapCommonShow()
        if(self.btc.rest_is_c1_master_controller()):
            c = t.controller('c1')
            c.http_port=8082
        else:
            c = t.controller('c2')
            c.http_port=8082
        url='http://%s:%s/auth/login' % (c.ip,c.http_port)
        result = c.rest.post(url, {"user":"admin", "password":"adminadmin"})
        helpers.log("result: %s" % helpers.to_json(result))
        session_cookie = result['content']['session_cookie']
        c.rest.set_session_cookie(session_cookie)

###################################################
# All Bigtap Show Commands Go Here:
###################################################

    def rest_show_bigwire_command(self,bwKey):
        '''Execute CLI Commands "show bigwire summary", "show bigwire tenant", "show bigwire pseudowire" and "show bigwire  datacenter"
        
            Input:
            
                'bwKey'    :    BigWire Keyword  datacenter for "show bigwire  datacenter",  pseudowire for "show bigwire pseudowire", tenant for "show bigwire tenant" and "summary" for "show bigwire summary"

            Return: Content as a dictionary after execution of command.
                
        '''
        t = test.Test()
        try:
            t.controller('c2')
        except:
            c = t.controller('c1')
            c.http_port=8082
        else:
            if(self.btc.rest_is_c1_master_controller()):
                c = t.controller('c1')
                c.http_port=8082
            else:
                c = t.controller('c2')
                c.http_port=8082  
        url='http://%s:%s/auth/login' % (c.ip,c.http_port)
        result = c.rest.post(url, {"user":"admin", "password":"adminadmin"})
        helpers.log("result: %s" % helpers.to_json(result))
        session_cookie = result['content']['session_cookie']
        c.rest.set_session_cookie(session_cookie) 
        if bwKey == "datacenter":
            bwKeyword = "datacenter-info" # "show bigwire datacenter"
        elif bwKey == "pseudowire":
            bwKeyword = "pseudowire-info" #"show bigwire pseudowire"
        elif bwKey == "tenant":
            bwKeyword = "tenant-info" #"show bigwire tenant"
        else :                      
            bwKeyword = "info"      # "show bigwire summary"        
        url = 'http://%s:%s/api/v1/data/controller/applications/bigwire/%s' % (c.ip, c.http_port,str(bwKeyword))
        c.rest.get(url)
        helpers.test_log("Ouput: %s" % c.rest.result_json())
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

    def rest_create_bigwire_datacenter(self,dcName):
        '''Create BigWire Datacenter. Similar to cli command "bigwire datacenter dcName"
        
            Input:    
                dcName        Datacenter Name
            
            Returns: True if configuration is successful, false otherwise
        '''
        t = test.Test()
        try:
            t.controller('c2')
        except:
            c = t.controller('c1')
            c.http_port=8082
        else:
            if(self.btc.rest_is_c1_master_controller()):
                c = t.controller('c1')
                c.http_port=8082
            else:
                c = t.controller('c2')
                c.http_port=8082  
                
        url='http://%s:%s/auth/login' % (c.ip,c.http_port)
        result = c.rest.post(url, {"user":"admin", "password":"adminadmin"})
        helpers.log("result: %s" % helpers.to_json(result))
        session_cookie = result['content']['session_cookie']
        c.rest.set_session_cookie(session_cookie) 
        url='http://%s:%s/api/v1/data/controller/applications/bigwire/datacenter[name="%s"]' % (c.ip,c.http_port,str(dcName))
        c.rest.put(url, {"name": str(dcName)})
        helpers.test_log("Ouput: %s" % c.rest.result_json())
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
            return False
        else:
            helpers.test_log(c.rest.content_json())
            return True
    
    def rest_add_switch_datacenter(self,dcName,swDpid,zoneName):
        '''Add switch to a datacenter
        
           Input:
               dcName        Datacenter Name
               
               swDpid        DPID of switch
               
               zoneName     Zone to which switch belongs
           
          Returns: True if configuration is successful, false otherwise
        '''
        t = test.Test()
        try:
            t.controller('c2')
        except:
            c = t.controller('c1')
            c.http_port=8082
        else:
            if(self.btc.rest_is_c1_master_controller()):
                c = t.controller('c1')
                c.http_port=8082
            else:
                c = t.controller('c2')
                c.http_port=8082  
                
        url='http://%s:%s/auth/login' % (c.ip,c.http_port)
        result = c.rest.post(url, {"user":"admin", "password":"adminadmin"})
        helpers.log("result: %s" % helpers.to_json(result))
        session_cookie = result['content']['session_cookie']
        c.rest.set_session_cookie(session_cookie) 
        url='http://%s:%s/api/v1/data/controller/applications/bigwire/datacenter[name="%s"]/member-switch[dpid="%s"]' % (c.ip,c.http_port,str(dcName),str(swDpid))
        c.rest.put(url, {"zone": str(zoneName), "dpid": str(swDpid)})
        helpers.test_log("Ouput: %s" % c.rest.result_json())
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
            return False
        else:
            helpers.test_log(c.rest.content_json())
            return True        
    
    def rest_create_bigwire_pseudowire(self,pseudoName,switchDpid1,intfName1,switchDpid2,inftName2,vlan=0):
        '''Create a bigwire pseudowire
        
            Input:
                pseudoName     Name of bigwire pseudowire
                switchDpid1    DPID of first Switch
                intfName1      Uplink port/interface name for first Switch
                switchDpid2    DPID of second Switch
                intfName2      Uplink port/interface name for second Switch
                Vlan           Vlan Number (in case of Vlan Mode, defaults to 0 for port-mode)
           
          Returns: True if configuration is successful, false otherwise
        '''
        t = test.Test()
        try:
            t.controller('c2')
        except:
            c = t.controller('c1')
            c.http_port=8082
        else:
            if(self.btc.rest_is_c1_master_controller()):
                c = t.controller('c1')
                c.http_port=8082
            else:
                c = t.controller('c2')
                c.http_port=8082  
                
        url='http://%s:%s/auth/login' % (c.ip,c.http_port)
        result = c.rest.post(url, {"user":"admin", "password":"adminadmin"})
        helpers.log("result: %s" % helpers.to_json(result))
        session_cookie = result['content']['session_cookie']
        c.rest.set_session_cookie(session_cookie) 
        url='http://%s:%s/api/v1/data/controller/applications/bigwire/pseudo-wire[name="%s"]' % (c.ip,c.http_port,str(pseudoName))
        if vlan == 0:
            c.rest.put(url, {"interface1": str(intfName1), "switch2": str(switchDpid2), "switch1": str(switchDpid1), "interface2": str(inftName2), "name": str(pseudoName)})
        else:
            c.rest.put(url, {"interface1": str(intfName1), "switch2": str(switchDpid2), "switch1": str(switchDpid1), "interface2": str(inftName2), "name": str(pseudoName), "vlan": int(vlan) })
        helpers.test_log("Ouput: %s" % c.rest.result_json())
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
            return False
        else:
            helpers.test_log(c.rest.content_json())
            return True        

    def rest_create_bigwire_tenant(self,tenantName):
        '''Create BigWire Tenant. Similar to cli command "bigwire tenant bw5bw7"
        
            Input:    
                tenantName        Tenant Name
            
            Returns: True if configuration is successful, false otherwise
        '''
        t = test.Test()
        try:
            t.controller('c2')
        except:
            c = t.controller('c1')
            c.http_port=8082
        else:
            if(self.btc.rest_is_c1_master_controller()):
                c = t.controller('c1')
                c.http_port=8082
            else:
                c = t.controller('c2')
                c.http_port=8082
                
        url='http://%s:%s/auth/login' % (c.ip,c.http_port)
        result = c.rest.post(url, {"user":"admin", "password":"adminadmin"})
        helpers.log("result: %s" % helpers.to_json(result))
        session_cookie = result['content']['session_cookie']
        c.rest.set_session_cookie(session_cookie) 
        url='http://%s:%s/api/v1/data/controller/applications/bigwire/tenant[name="%s"]' % (c.ip,c.http_port,str(tenantName))
        c.rest.put(url, {"name": str(tenantName)})
        helpers.test_log("Ouput: %s" % c.rest.result_json())
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
            return False
        else:
            helpers.test_log(c.rest.content_json())
            return True
    
    def rest_add_switch_to_tenant(self,tenantName,switchDpid,interfaceName,vlan=0):
        '''Add switch to a tenant
        
           Input:
               tenantName    Tenant Name
               
               switchDpid        DPID of switch
               
               interfaceName     Interface Name
               
               Vlan            Tenant Vlan Number
           
          Returns: True if configuration is successful, false otherwise
        '''
        t = test.Test()
        try:
            t.controller('c2')
        except:
            c = t.controller('c1')
            c.http_port=8082
        else:
            if(self.btc.rest_is_c1_master_controller()):
                c = t.controller('c1')
                c.http_port=8082
            else:
                c = t.controller('c2')
                c.http_port=8082
                
        url='http://%s:%s/auth/login' % (c.ip,c.http_port)
        result = c.rest.post(url, {"user":"admin", "password":"adminadmin"})
        helpers.log("result: %s" % helpers.to_json(result))
        session_cookie = result['content']['session_cookie']
        c.rest.set_session_cookie(session_cookie) 
        url='http://%s:%s/api/v1/data/controller/applications/bigwire/tenant[name="%s"]/tenant-interface[interface="%s"][switch="%s"]' %(c.ip,c.http_port,str(tenantName),str(interfaceName),str(switchDpid))
        if vlan == 0:
            c.rest.put(url,{"interface": str(interfaceName), "switch": str(switchDpid)})
        else:
            c.rest.put(url,{"interface": str(interfaceName), "tenant-vlan": [{"vlan": int(vlan)}], "switch": str(switchDpid)})
        helpers.test_log("Ouput: %s" % c.rest.result_json())
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
            return False
        else:
            helpers.test_log(c.rest.content_json())
            return True

    def rest_delete_tenant(self,tenantName):
        '''Delete a tenant
        
           Input:
               tenantName    Tenant Name
           
          Returns: True if configuration is successful, false otherwise
        '''
        t = test.Test()
        try:
            t.controller('c2')
        except:
            c = t.controller('c1')
            c.http_port=8082
        else:
            if(self.btc.rest_is_c1_master_controller()):
                c = t.controller('c1')
                c.http_port=8082
            else:
                c = t.controller('c2')
                c.http_port=8082
        url='http://%s:%s/auth/login' % (c.ip,c.http_port)
        result = c.rest.post(url, {"user":"admin", "password":"adminadmin"})
        helpers.log("result: %s" % helpers.to_json(result))
        session_cookie = result['content']['session_cookie']
        c.rest.set_session_cookie(session_cookie)
        url='http://%s:%s/api/v1/data/controller/applications/bigwire/tenant[name="%s"]'  % (c.ip,c.http_port,str(tenantName))    
        c.rest.delete(url, {})
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
            return False
        else:
            helpers.test_log(c.rest.content_json())
            return True
    
    def rest_delete_pseudowire(self,pseudoName):
        '''Delete a pseudowire
        
           Input:
               pseudoName    Pseudowire Name
           
          Returns: True if configuration is successful, false otherwise
        '''
        t = test.Test()
        try:
            t.controller('c2')
        except:
            c = t.controller('c1')
            c.http_port=8082
        else:
            if(self.btc.rest_is_c1_master_controller()):
                c = t.controller('c1')
                c.http_port=8082
            else:
                c = t.controller('c2')
                c.http_port=8082
        url='http://%s:%s/auth/login' % (c.ip,c.http_port)
        result = c.rest.post(url, {"user":"admin", "password":"adminadmin"})
        helpers.log("result: %s" % helpers.to_json(result))
        session_cookie = result['content']['session_cookie']
        c.rest.set_session_cookie(session_cookie)
        url='http://%s:%s/api/v1/data/controller/applications/bigwire/pseudo-wire[name="%s"]'  % (c.ip,c.http_port,str(pseudoName))    
        c.rest.delete(url, {})
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
            return False
        else:
            helpers.test_log(c.rest.content_json())
            return True        
    
    def rest_delete_datacenter(self,dcName):
        '''Delete a dcName
        
           Input:
               dcName    datacenter Name
           
          Returns: True if configuration is successful, false otherwise
        '''
        t = test.Test()
        try:
            t.controller('c2')
        except:
            c = t.controller('c1')
            c.http_port=8082
        else:
            if(self.btc.rest_is_c1_master_controller()):
                c = t.controller('c1')
                c.http_port=8082
            else:
                c = t.controller('c2')
                c.http_port=8082
        url='http://%s:%s/auth/login' % (c.ip,c.http_port)
        result = c.rest.post(url, {"user":"admin", "password":"adminadmin"})
        helpers.log("result: %s" % helpers.to_json(result))
        session_cookie = result['content']['session_cookie']
        c.rest.set_session_cookie(session_cookie)
        url='http://%s:%s/api/v1/data/controller/applications/bigwire/datacenter[name="%s"]'  % (c.ip,c.http_port,str(dcName))    
        c.rest.delete(url, {})
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
            return False
        else:
            helpers.test_log(c.rest.content_json())
            return True  