import autobot.helpers as helpers
import autobot.test as test
import re

class Common(object):
# This is for all the common function   - Mingtao
    def __init__(self):
        t = test.Test()
        c = t.controller()

        url = '%s/auth/login' % c.base_url
        result = c.rest.post(url, {"user":"admin", "password":"adminadmin"})
        session_cookie = result['content']['session_cookie']
        c.rest.set_session_cookie(session_cookie)
        
    def rest_show_version(self):
        # perform show version and reture the version number
        t = test.Test()
        c = t.controller()
        c.http_port = 8000
        url='http://%s:%s/rest/v1/system/version' % (c.ip,c.http_port)
         
       # url = '%s/rest/v1/system/version' % (c.base_url)
        c.rest.get(url)
        helpers.log("Output: %s" % c.rest.result_json())

        content_json = c.rest.content_json()
        helpers.log(content_json)
        
        content = c.rest.content()[0]
        helpers.log("content: %s" % content)
        
        output = content['controller']
        helpers.log(output)
        
       #
       # matchobj = re.match(r'.*Big Tap*', output)
        ##   helpers.log("This is Big Tap controller")
            
        #else:
         #   helpers.test_failure("this is not Big Tap controller")
            
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())

        return c.rest.content()[0]
    
    
    def rest_show_user(self):
        t = test.Test()
        c = t.controller()
         
        url = '%s/api/v1/data/controller/core/aaa/group' % (c.base_url)
        c.rest.get(url)
        helpers.log("Output: %s" % c.rest.result_json())
    

        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())

        return c.rest.content()
    
    def rest_show_controller(self):
        t = test.Test()
        c = t.controller()
        c.http_port = 8000
        #  TBD need to find the rest api 
      
        url = 'http://%s:%s/rest/v1/model/controller-node' % (c.ip, c.http_port)
        c.rest.get(url)
        helpers.log("Output: %s" % c.rest.result_json())
    
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())

        return c.rest.content()
    
    def rest_show_bigtap(self):
        t = test.Test()
        c = t.controller()
        c.http_port = 8000
        #  TBD need to find the rest api 
      
        url = '%s/api/v1/data/controller/applications/bigtap/info' % (c.base_url)
        c.rest.get(url)
        helpers.log("Output: %s" % c.rest.result_json())
    
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())

        return c.rest.content()
    
    def rest_bigtap_create_addgroup(self,groupName,ipType):
        # create the address group and associate the type
        t = test.Test()
        c = t.controller()
        url = '%s/api/v1/data/controller/applications/bigtap/ip-address-set[name="%s"]'% (c.base_url, str(groupName)) 
        c.rest.put(url,{"name": str(groupName)})
        helpers.sleep(1)        
              
        url = '%s/api/v1/data/controller/applications/bigtap/ip-address-set[name="%s"]' % (c.base_url, str(groupName)) 
        
        c.rest.patch(url,{"ip-address-type": str(ipType)})
        helpers.sleep(1)
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
            return False
        else:
            helpers.test_log(c.rest.content_json())
            return True
    
    
    def rest_bigtap_add_address(self,groupName,ipAddr,ipMask,Flag="true"):
        # create the address group and associate the type
        t = test.Test()
        c = t.controller()
             
        url = '%s/api/v1/data/controller/applications/bigtap/ip-address-set[name="%s"]/address-mask-set[ip="%s"][ip-mask="%s"]' % (c.base_url, str(groupName),str(ipAddr),str(ipMask)) 
        
        c.rest.put(url,{"ip": str(ipAddr), "ip-mask": str(ipMask)})
        helpers.sleep(1)
        if (Flag == 'negative'):
            if not c.rest.status_code_ok():
                helpers.test_log(c.rest.content_json())
                return True
            else:
                helpers.test_failure(c.rest.error())
                return False 
        else:    
            if not c.rest.status_code_ok():
                helpers.test_failure(c.rest.error())
                return False
            else:
                helpers.test_log(c.rest.content_json())
                return True  
    
    
    def rest_bigtap_show_address_group(self,groupName,ipType):
        t = test.Test()
        c = t.controller()
        url = '%s/api/v1/data/controller/applications/bigtap/ip-address-set[name="%s"]' % (c.base_url,str(groupName))
  
        c.rest.get(url)
        helpers.test_log("Json Ouput: %s" % c.rest.result_json())             
        helpers.test_log("Ouput: %s" % c.rest.content()) 
                 
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
        if(c.rest.content()):
            helpers.log("name: %s" % c.rest.content()[0]['name'])
            helpers.log("type: %s" % c.rest.content()[0]['ip-address-type'])
            if (str(groupName) == c.rest.content()[0]['name']) and (str(ipType)==c.rest.content()[0]['ip-address-type']):           
                return  True
            else:
                helpers.test_log("ERROR Address group Name %s and type %s does not match" % (str(groupName),str(ipType))) 
                helpers.test_failure(c.rest.error())
                return False
        else :
            helpers.test_log("ERROR Address group %s does not exist. Error seen: %s" % (str(groupName),c.rest.result_json()))
            return False
   
    def rest_bigtap_setup_role(self,swDpid,intf,role,intfName):
        t = test.Test()
        c = t.controller()
        
       # swDpid = rest_get_switch_dpid(str(swName))       
       #helpers.log("name: %s , DPID %s" % str(swName), str(swDpid))
        
        url = '%s/api/v1/data/controller/applications/bigtap/interface-config[interface="%s"][switch="%s"]' % (c.base_url, str(intfName), str(swDpid))
        c.rest.put(url, {"interface": str(intf), "switch": str(swDpid), 'role':str(role),'name':str(intfName)})
        helpers.test_log("Ouput: %s" % c.rest.result_json())
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
            return False
        else:
            helpers.test_log(c.rest.content_json())
            return True      
        
    def rest_get_switch_dpid(self,switchAlias):
        t = test.Test()
        c = t.controller()
        aliasExists=0
        url='%s/api/v1/data/controller/core/switch?select=alias'   % (c.base_url)
        c.rest.get(url)
        content = c.rest.content()
        for i in range(0,len(content)) :
                if content[i]['alias'] == str(switchAlias) :
                        switchDpid = content[i]['dpid']
                        aliasExists=1
        if(aliasExists):
            return switchDpid
        else:
            return False
        
    def rest_bigtap_show_interface_name(self,Name,Role,Switch,ifName):
        # compare part is not right
        t = test.Test()
        c = t.controller()
        url = '%s/api/v1/data/controller/applications/bigtap/interface-config' % (c.base_url)
  
        c.rest.get(url)
        helpers.test_log("Json Ouput: %s" % c.rest.result_json())             
        helpers.test_log("Ouput: %s" % c.rest.content()) 
                 
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
        if(c.rest.content()):
            helpers.log("interface: %s" % c.rest.content()[0]['interface'])
            helpers.log("name: %s" % c.rest.content()[0]['name'])
            helpers.log("role: %s" % c.rest.content()[0]['role'])
            helpers.log("switch: %s" % c.rest.content()[0]['switch']) 
            
            if (str(Name) == c.rest.content()[0]['name']) and (str(Role)==c.rest.content()[0]['role']):           
                return  True
            else:
                helpers.test_log("ERROR  Name %s and role %s does not match" % (str(Name),str(Role))) 
                helpers.test_failure(c.rest.error())
                return False
        else :
            helpers.test_log("ERROR bigtap role does not exist. Error seen: %s" % (c.rest.result_json()))
            return False        
        
        