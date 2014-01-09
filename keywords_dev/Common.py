import autobot.helpers as helpers
import autobot.test as test
import re
import subprocess
import os

class Common(object):
# This is for all the common function   - Mingtao
    def __init__(self):
        t = test.Test()
        c = t.controller()

        url = '%s/auth/login' % c.base_url
        result = c.rest.post(url, {"user":"admin", "password":"adminadmin"})
        session_cookie = result['content']['session_cookie']
        c.rest.set_session_cookie(session_cookie)
        
        

##################################### 
# files to be staged to product
########################################

    def rest_get_switch_dpid(self,switch_alias):
        """ Get the switch id from the switch alias
            Mingtao
        """
        t = test.Test()
        c = t.controller()
        aliasExists=0
        url='%s/api/v1/data/controller/core/switch?select=alias'   % (c.base_url)
        c.rest.get(url)
        content = c.rest.content()
        for i in range(0,len(content)) :
                if content[i]['alias'] == str(switch_alias) :
                        switch_dpid = content[i]['dpid']
                        aliasExists=1
        if(aliasExists):
            return switch_dpid
        else:
            return False

    def rest_verify_switch_flow(self,sw_name,num_flow):
        """ verify the number of flows in switch and compare with expected number
        """
        t = test.Test()
        c = t.controller()
        c.http_port=8082
        
        sw_dpid = self.rest_get_switch_dpid(str(sw_name))       
        helpers.log("name: %s ===> DPID: %s" % (str(sw_name), str(sw_dpid)))
        
        url ='%s/api/v1/data/controller/core/switch[dpid="%s"]?select=stats/table' % (c.base_url,str(sw_dpid))
        
        c.rest.get(url)
        helpers.test_log("Json Ouput: %s" % c.rest.result_json())             
        helpers.test_log("Ouput: %s" % c.rest.content()) 
        
        content = c.rest.content()
        helpers.log("Return value for number of flows is %s" % content[0]['stats']['table'][1]['active-count'])
        flows = content[0]['stats']['table'][1]['active-count']    
    
        if flows == int(num_flow) :
            helpers.test_log("Switch %s is correctly programmed with %s of flows" % (str(sw_name), str(flows)) ) 
        else:
            debug_url= '%s/api/v1/data/controller/core/switch[dpid="%s"]?select=stats/flow' % (c.base_url,str(sw_dpid)) 
            c.rest.get(url) 
            helpers.test_log("******debug  Ouput******* \n %s" % c.rest.result_json())                
            helpers.test_failure("Switch %s is NOT correctly programmed with flows,  expect: %s  Actual: %s" % (str(sw_name), str(num_flow), str(flows)) )                      
            return False  
                  
    def rest_get_switch_flow(self,sw_name ):
        """ get the number of flows in switch  
        """
        t = test.Test()
        c = t.controller()
        c.http_port=8082
        
        sw_dpid = self.rest_get_switch_dpid(str(sw_name))       
        helpers.log("name: %s ===> DPID: %s" % (str(sw_name), str(sw_dpid)))
        
        url ='%s/api/v1/data/controller/core/switch[dpid="%s"]?select=stats/table' % (c.base_url,str(sw_dpid))
        
        c.rest.get(url)
        helpers.test_log("Json Ouput: %s" % c.rest.result_json())             
        helpers.test_log("Ouput: %s" % c.rest.content()) 
        
        content = c.rest.content()
        helpers.log("Return value for number of flows is %s" % content[0]['stats']['table'][1]['active-count'])
        flows = content[0]['stats']['table'][1]['active-count']    
    
        return flows
                        

    def bigtap_clean_up(self, feature):
        """ Clean up the features
            Mingtao
            complete:   policy    address-group    l3-l4-mode
            Usage:  bigtap_clean_up   policy
            
            TBD:  give multiple at one line
        """
        
        t = test.Test()
        c = t.controller()       
        if ( feature == 'policy'):
            url = '%s/api/v1/data/controller/applications/bigtap/view/policy?select=info' % (c.base_url)
            c.rest.get(url)
            content = c.rest.content()
            if not c.rest.status_code_ok():
                helpers.test_failure(c.rest.error())
                return False
            helpers.log("Output: %s" % c.rest.result_json()) 
            length =len(content)
              
            helpers.log("Number of Policies is: %s" % str(length))        
            for index in range(length):
                name = content[index]['name']
                helpers.log("this is the %s Policy to be cleaned: %s" % (str(index), str(name)))
                url = '%s/api/v1/data/controller/applications/bigtap/view[name="admin-view"]/policy[name="%s"]' % (c.base_url,str(name))   
                c.rest.delete(url) 
                if not c.rest.status_code_ok():
                    helpers.test_failure(c.rest.error())                    
                                
        if ( feature == 'address-group'):
            url = '%s/api/v1/data/controller/applications/bigtap/ip-address-set' % (c.base_url)      
            c.rest.get(url) 
            content = c.rest.content()
            if not c.rest.status_code_ok():
                helpers.test_failure(c.rest.error())
                return False 
            length =len(content)  
            helpers.log("Number of address group is: %s" % str(length))        
            for index in range(length):
                name = content[index]['name']
                helpers.log("this is the %s Address-group to be cleaned: %s" % (str(index), str(name)))
                url = '%s/api/v1/data/controller/applications/bigtap/ip-address-set[name="%s"]' % (c.base_url,str(name))   
                c.rest.delete(url) 
                if not c.rest.status_code_ok():
                    helpers.test_failure(c.rest.error())                                   
        if ( feature == 'l3-l4-mode'):
            url = '%s/api/v1/data/controller/applications/bigtap/feature/l3-l4-mode' % (c.base_url)      
            c.rest.delete(url) 
            if not c.rest.status_code_ok():
                helpers.test_failure(c.rest.error())
        return True   


    def rest_bigtap_verify_interface_name(self,name,role,switch,if_name):
        """ verify bigtap  interface role
            Mingtao
            
        """
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
            
            if (str(name) == c.rest.content()[0]['name']) and (str(role)==c.rest.content()[0]['role']):           
                return  True
            else:
                helpers.test_log("ERROR  Name %s and role %s does not match" % (str(name),str(role))) 
                helpers.test_failure(c.rest.error())
                return False
        else :
            helpers.test_log("ERROR bigtap role does not exist. Error seen: %s" % (c.rest.result_json()))
            return False        
        

    def rest_bigtap_setup_role(self,sw_name,intf,role,int_name):
        """ setup bigtap interface role
           usage:  REST bigtap setup role    S204    ethernet49    filter     S204-49 
        """
        
        t = test.Test()
        c = t.controller()
  
        sw_dpid = self.rest_get_switch_dpid(str(sw_name))       
        helpers.log("name: %s ===> DPID: %s" % (str(sw_name), str(sw_dpid)))

        url = '%s/api/v1/data/controller/applications/bigtap/interface-config[interface="%s"][switch="%s"]' % (c.base_url, str(intf), str(sw_dpid))
        c.rest.put(url, {"interface": str(intf), "switch": str(sw_dpid), 'role':str(role),'name':str(int_name)})
        helpers.test_log("Ouput: %s" % c.rest.result_json())
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
            return False
        else:
            helpers.test_log(c.rest.content_json())
            return True      
        

    def get_next_address(self,addr_type,base,incr): 
        """ Generate the next address bases on the base and step.
            Mingtao
            Usage:    ipAddr = self.get_next_address(ipv4,'10.0.0.0','0.0.0.1')
                      ipAddr = self.get_next_address(ipv6,'f001:100:0:0:0:0:0:0','0:0:0:0:0:0:0:1:0')
        """
       
        helpers.log("the base address is: %s,  the step is: %s,  "  % (str(base), str(incr)))   
        if addr_type == 'ipv4': 
            ip = list(map(int, base.split(".")))
            step = list(map(int, incr.split(".")))            
            ipAddr = []
            for i in range(3,0,-1):
                ip[i] += step[i]
                if ip[i] >= 256:
                    ip[i] = 0
                    ip[i-1] +=1
            ip[0] += step[0]        
            if ip[0] >= 256:
                ip[0] = 0
             
            ipAddr  = '.'.join(map(str,ip)) 
                        
        if addr_type == 'ipv6' :
            ip = base.split(":")
            step =  incr.split(":")
            helpers.log("IP list is %s" % ip)
            
            ipAddr = []
            hexip = []  
                                 
            for i in range(0,7):
                index = 7 - int(i)
                ip[index] = int(ip[index], 16) + int(step[index], 16)
                ip[index] = hex(ip[index])
                if ip[index] >= 'ffff':
                    ip[index] = 0
                    ip[index-1] = int(ip[index-1],16) + 1
                    ip[index-1] = hex(ip[index-1])
                  
                    
            ip[0] = int(ip[0],16) + int(step[0],16)        
            if ip[0] >= 65535:
                ip[0] = 0
                    
            ip[0]=hex(ip[0])    
                
            for i in range(0,8):
                hexip.append('{0:x}'.format(int(ip[i],16)))  
                                      
            ipAddr  = ':'.join(map(str,hexip))  
                 
        return ipAddr
 
      
    def rest_bigtap_create_addrgroup(self, name,addr_type):
        """ create the address group and associate the type
            Mingtao
            Usage: REST bigtap create addgroup     Ipv4   ipv4  
            type - ipv4 :  ipv6
        """
        t = test.Test()
        c = t.controller()
        url = '%s/api/v1/data/controller/applications/bigtap/ip-address-set[name="%s"]'% (c.base_url, str(name)) 
        c.rest.put(url,{"name": str(name)})
        helpers.sleep(1)        
              
        url = '%s/api/v1/data/controller/applications/bigtap/ip-address-set[name="%s"]' % (c.base_url, str(name)) 
        
        c.rest.patch(url,{"ip-address-type": str(addr_type)})
        helpers.sleep(1)
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
            return False
        else:
            helpers.test_log(c.rest.content_json())
            return True
  
  
    def rest_bigtap_add_addrgroup(self,name,addr,mask,flag="true"):
        """Config address for address group
           Mingtao
           Usage: 
           Flag:  true  -   configuration should go through
                  negative  - configuration should not go though
        """
        # create the address group and associate the type
        t = test.Test()
        c = t.controller()
             
        url = '%s/api/v1/data/controller/applications/bigtap/ip-address-set[name="%s"]/address-mask-set[ip="%s"][ip-mask="%s"]' % (c.base_url, str(name),str(addr),str(mask)) 
        
        c.rest.put(url,{"ip": str(addr), "ip-mask": str(mask)})
        helpers.sleep(1)
        helpers.test_log(c.rest.content_json())
        if (flag == 'negative'):
            if not c.rest.status_code_ok():
                return True
            else:
                helpers.test_failure(c.rest.error())
                return False 
        else:    
            if not c.rest.status_code_ok():
                helpers.test_failure(c.rest.error())
                return False
            else:
                return True  
     
    
    def rest_bigtap_create_policy(self,view,policy,action="inactive"):
        """ Create bigtap policy
            Usage: rest_bigtap_create_policy("admin-view", Policy1)
        """
        t = test.Test()
        c = t.controller()
        c.http_port=8082
        url='http://%s:%s/api/v1/data/controller/applications/bigtap/view[name="%s"]/policy[name="%s"]' % (c.ip,c.http_port, str(view), str(policy))
        c.rest.put(url,{'name':str(policy)})
        helpers.test_log("Ouput: %s" % c.rest.result_json())
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
        c.rest.patch(url,{"action": str(action) })
        helpers.test_log("Ouput: %s" % c.rest.result_json())
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
            return False
        else:
            helpers.test_log(c.rest.content_json())
            return True 

    def rest_bigtap_add_policy_match(self,view,policy,sequence,data,flag="true"):
        """  add policy match to policy.
             Usage:     REST bigtap add policy match   admin-view  IPv4_ADD   10   {"sequence": 10, "src-ip-list": "IPV4", "ether-type": 2048} 
             Flag:   true  -  the configuration should go through
                     negative  -  the configuration should not go through
        """
        t = test.Test()
        c = t.controller()
        c.http_port=8082
        url='http://%s:%s/api/v1/data/controller/applications/bigtap/view[name="%s"]/policy[name="%s"]/rule[sequence=%s]'  % (c.ip,c.http_port,str(view),str(policy),str(sequence))
        data_dict = helpers.from_json(data)
        helpers.log("the data in match is %s" % data)
        c.rest.put(url,data_dict)
        helpers.test_log(c.rest.result_json())
        helpers.test_log(c.rest.content_json()) 
        if (flag == 'negative'):
            if not c.rest.status_code_ok():
                return True
            else:
                helpers.test_failure(c.rest.error())
                return False 
        else:    
            if not c.rest.status_code_ok():
                helpers.test_failure(c.rest.error())
                return False
            else:
                return True  

    def rest_bigtap_config_l34(self,l3_l4,flag="true"):
        """ configure L3_l4 mode
            Mingtao
            Flag:  true    -  expect configuration go through
                   negative  - expect configuration not go through
        """
        t = test.Test()
        c = t.controller()
        
        url ='%s/api/v1/data/controller/applications/bigtap/feature' % (c.base_url)
        c.rest.patch(url, {"l3-l4-mode": str(l3_l4)})
              
        helpers.test_log(c.rest.result_json())
        helpers.test_log(c.rest.content_json()) 
        if (flag == 'negative'):
            if not c.rest.status_code_ok():
                return True
            else:
                helpers.test_failure(c.rest.error())
                return False 
        else:    
            if not c.rest.status_code_ok():
                helpers.test_failure(c.rest.error())
                return False
            else:
                return True    

    def rest_bigtap_verify_l34(self, l3_l4="False"):
        """ verify bigtap L3_l4 mode
            Mingtao
        """
        t = test.Test()
        c = t.controller()
        
        url = '%s/api/v1/data/controller/applications/bigtap/info' % (c.base_url)
        c.rest.get(url)
        helpers.log("Output: %s" % c.rest.result_json())
                
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
        data = c.rest.content()
        helpers.log("Content is Output: %s" % data)
         
        if str(data[0]['l3-l4-mode']) == str(l3_l4):            
            helpers.test_log("Bigtap correctly reports L3-L4-mode as: %s " % data[0]['l3-l4-mode'])
            return True
        else:
            helpers.test_failure("Bigtap NOT correctly reports L3-L4-mode as : %s --- Expect: %s " % (data[0]['l3-l4-mode'], str(l3_l4)))               
            return False     
   


    def bigtap_gen_config_addrgroup(self,group,addr_type,base,incr,mask,number):
        """ Generate and apply #number of ipv4/ipv6 for address-group  
            Mingtao
            Usage:
                bigtap_gen_config_addrgroup     IPV4    ipv4     10.0.0.0     0.1.0.1        255.255.255.0     20
                bigtap_gen_config_addrgroup     IPV6    ipv6     f001:100:0:0:0:0:0:0     0:0:0:0:0:0:0:1     ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff     20
        """
        t = test.Test()
        c = t.controller()
        
        helpers.log("the base address is: %s,  the step is: %s,  the mask is: %s,  the Num is: %s"  % (str(base), str(incr), str(mask),  str(number)))   
         
#        self.rest_bigtap_create_addgroup(group,addr_type)
        self.rest_bigtap_add_addrgroup(group,base,mask)

        Num = int(number) - 1            
        for num in range(0,int(Num)):    
           
            ipAddr = self.get_next_address(addr_type,base,incr)
            self.rest_bigtap_add_addrgroup(group,ipAddr,mask)
            base = ipAddr
            helpers.log("the applied address is: %s %s %s "  % (addr_type, str(ipAddr), str(mask)))     
        
        return True         
 
 
    def bigtap_gen_addrgroup(self,file_name,group,addr_type,base,incr,mask,number):
        """ Generate # of address for a address group and put to a file
            Mingtao
            TBD - file can be new or append
        """
        
        t = test.Test()
        c = t.controller()
        
        helpers.log("the base address is: %s,  the step is: %s,  the mask is: %s,  the Number is: %s"  % (str(base), str(incr), str(mask),  str(number)))   
         
        fo = open(file_name,'w')
        temp = "bigtap address-group %s \n ip type %s \n ip %s %s \n"  % (str(group), str(addr_type),str(base),str(mask)) 
        fo.write(str(temp)) 
                
        Num = int(number) - 1
        for num in range(0,int(Num)):    
           
            ipAddr = self.get_next_address(addr_type,base,incr)
            self.rest_bigtap_add_addrgroup(group,ipAddr,mask)
            base = ipAddr
            temp = " ip %s %s \n"  % (str(ipAddr),str(mask)) 
            fo.write(str(temp)) 
                                 
        fo.close()  
        return True         

    def bigtap_gen_poliy_match(self,file_name,policy,addr_type,modify_field,base,incr,mask,number,sequence, common=''):
        """ Generate # of matches  for a policy and put to a file
            Mingtao
            TBD - file can be new or append
        """
        t = test.Test()
        c = t.controller()
        
        helpers.log("the base address is: %s,  the step is: %s,  the mask is: %s,  the Num is: %s, the common field: %s"  % (str(base), str(incr), str(mask),  str(number), str(common)))   
         
        fo = open(file_name,'w')
        temp = "bigtap policy %s \n"  % (str(policy)) 
        fo.write(str(temp)) 
               
        if addr_type == 'ip' or addr_type == 'ip6':
            temp = "%d match %s %s %s %s %s\n"  % (int(sequence),str(addr_type), str(addr_type), str(base),str(mask), str(common))              
            fo.write(str(temp))       
            if modify_field == 'src-ip' or modify_field == 'dst-ip':            
                Num = int(number) - 1            
                for num in range(0,int(Num)):  
                
                    ipAddr = self.get_next_address(addr_type,base,incr)                
                    base = ipAddr   
                    new_sequence = int(sequence) + num + 1
                    temp = "%d match %s %s %s %s %s\n"  % (new_sequence, str(addr_type), str(modify_field), str(ipAddr), str(mask), str(common))                   
                    fo.write(str(temp))  
 
        fo.close()  
        return True                         
 
    def rest_bigtap_show_run_policy(self, policy=None):
        """ show running configuration for bigtap policy
            Mingtao
            Usage:  policy name is provided,  return only that policy
                    policy name is not provided, return all policies
        """ 
        t = test.Test()
        c = t.controller()
        
        if policy is None:
            url = '%s/api/v1/data/controller/applications/bigtap/view?config=true' % (c.base_url)
        else:
            url = '%s/api/v1/data/controller/applications/bigtap/view[policy/name="%s"]?config=true&select=policy[name="%s"]' % (c.base_url, str(policy), str(policy)) 
            
        c.rest.get(url)
        helpers.log("Output: %s" % c.rest.result_json())
    
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())

        return c.rest.content() 
   
    def rest_bigtap_verify_addrgroup(self,group,addr_type):
        """ verify the name and type for bigtap address group
            Mingtao
            Usage:  
                    
        """ 
        t = test.Test()
        c = t.controller()
        url = '%s/api/v1/data/controller/applications/bigtap/ip-address-set[name="%s"]' % (c.base_url,str(group))
  
        c.rest.get(url)
        helpers.test_log("Json Ouput: %s" % c.rest.result_json())             
        helpers.test_log("Ouput: %s" % c.rest.content()) 
                 
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
        if(c.rest.content()):
            helpers.log("name: %s" % c.rest.content()[0]['name'])
            helpers.log("type: %s" % c.rest.content()[0]['ip-address-type'])
            if (str(group) == c.rest.content()[0]['name']) and (str(addr_type)==c.rest.content()[0]['ip-address-type']):           
                return  True
            else:
                helpers.test_log("ERROR Address group Name %s and type %s does not match" % (str(group),str(addr_type))) 
                helpers.test_failure(c.rest.error())
                return False
        else :
            helpers.test_log("ERROR Address group %s does not exist. Error seen: %s" % (str(group),c.rest.result_json()))
            return False
   






 
##################################### 
# files to be staged to product
########################################




        
    def sleep_now(self, Flag):
        if (Flag == 'short'):
            helpers.sleep(float(5))
        if (Flag == 'very short'):
            helpers.sleep(float(2))    
        if (Flag == 'long'):
            helpers.sleep(float(10))    
              
        
    def rest_show_version(self):
        # perform show version and reture the version number
        t = test.Test()
        c = t.controller()
        c.http_port = 8000
        url='http://%s:%s/rest/v1/system/version' % (c.ip,c.http_port)
        c.rest.get(url)
        helpers.log("Output: %s" % c.rest.result_json())

        content_json = c.rest.content_json()
        helpers.log(content_json)
        
        content = c.rest.content()[0]
        helpers.log("content: %s" % content)
        
        output = content['controller']
        helpers.log(output)
        
        
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
    




     

            

                


    def rest_bigtap_show_policy_optimize(self, policyName,numMatch):
        t = test.Test()
        c = t.controller()
         
        helpers.test_log("Input arguments: policy = %s, numMatch = %s" % (policyName,numMatch))  
        url ='%s/api/v1/data/controller/applications/bigtap/view/policy[name="IP1"]/debug' % (c.base_url)
        c.rest.get(url)
        helpers.test_log("Ouput: %s" % c.rest.result_json())
        
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
            
        content = c.rest.content() 
        helpers.log("content Output : %s" % content) 
                 
        if content[0]['name'] == str(policyName):
                helpers.test_log("Policy correctly reports policy name as : %s" % content[0]['name'])
        else:
                helpers.test_failure("Policy does not correctly report policy name  : %s" % content[0]['name'])                
                return False        
        if len(content[0]['optimized-match']) == "numMatch":
                helpers.test_log("Policy correctly  optimize the match entries: %s" % numMatch  )
        else:
                helpers.test_failure("ERROR: Policy does not correctly optimized match expect : %s  -----  actual:  %s " % (numMatch, len(content[0]['optimized-match'])))
                return False                
        
        return True

    def copy_to_controller(self,fName,dst_name):
        t = test.Test()
        c = t.controller()
        helpers.test_log("Input arguments: File Name = %s, Dest Name = %s" % (fName,dst_name)) 
        
        helpers.scp_put(c.ip, fName, dst_name)   
        
        return True
        
   


    def bigtap_apply_match(self,pName,mType,cType,base,incr,Mask,Num,match_num, common=''):
        """ add multiple match's to a policy -   Mingtao
            Done: ipv4/ipv6  src_ip,  dst_ip
            To BE Done:  other fields: port    mac   vlan ....
        """
        t = test.Test()
        c = t.controller()
   
        helpers.log("the policy Name is: %s, mtype is: %s, cType is : %s, base is: %s,  the step is: %s,  the mask is: %s,  the Num is: %s, the common field: %s"  % (str(pName), str(mType), str(cType), str(base), str(incr), str(Mask),  str(Num), str(common)))   
                               
        if mType == 'ip': 
            if cType == 'src_ip' or cType == 'dst_ip':    
                match_string = self.bigtap_construct_match(ip=mType, src_ip=base, src_ip_mask=Mask, sequence=match_num) 
                self.rest_bigtap_add_policy_match("admin-view", pName,match_num,match_string,Flag="true")   
                helpers.log("the Match string is : %s" % match_string)                    
                Num = int(Num) - 1            
                for num in range(0,int(Num)):    
                    ipAddr = self.get_next_address("ipv4",base,incr)
                    base = ipAddr 
                    mNum = int(num) + int(match_num) + 1 
                    if cType == 'src_ip':
                        match_string = self.bigtap_construct_match(ip=mType, src_ip=ipAddr, src_ip_mask=Mask,sequence=mNum) 
                    if cType == 'dst_ip': 
                        match_string = self.bigtap_construct_match(ip=mType, dst_ip=ipAddr, dst_ip_mask=Mask,sequence=mNum) 
                    helpers.log("the Match string is : %s" % match_string)     
                    self.rest_bigtap_add_policy_match("admin-view", pName,mNum,match_string,Flag="true")   

        if mType == 'ipv6': 
            if cType == 'src_ip' or cType == 'dst_ip':    
                match_string = self.bigtap_construct_match(ip6=mType, src_ip=base, src_ip_mask=Mask, sequence=match_num) 
                self.rest_bigtap_add_policy_match("admin-view", pName,match_num,match_string,Flag="true")   
                helpers.log("the Match string is : %s" % match_string)                    
                Num = int(Num) - 1            
                for num in range(0,int(Num)):    
                    ipAddr = self.get_next_address("ipv6",base,incr)
                    base = ipAddr 
                    mNum = int(num) + int(match_num) + 1 
                    if cType == 'src_ip':
                        match_string = self.bigtap_construct_match(ip6=mType, src_ip=ipAddr, src_ip_mask=Mask,sequence=mNum) 
                    if cType == 'dst_ip': 
                        match_string = self.bigtap_construct_match(ip6=mType, dst_ip=ipAddr, dst_ip_mask=Mask,sequence=mNum) 
                    helpers.log("the Match string is : %s" % match_string)     
                    self.rest_bigtap_add_policy_match("admin-view", pName,mNum,match_string,Flag="true")   
                             
 
        return True   


#    REST bigtap add policy match       admin-view  IP1   10   {"dst-tp-port-min": 16, "ether-type": 2048, "dst-tp-port-max": 31, "ip-proto": 6, "sequence": 10}   
  
    def bigtap_construct_match(self,
                               ip=None, ip6=None, ether_type=None,
                               src_mac = None,
                               dst_mac = None,
                               udp=None, tcp=None,
                               icmp=None, icmp_code=None, icmp_type=None,
                               vlan_id = None, vlan_min=None, vlan_max=None,  
                               src_ip_list =None, src_ip =None, src_ip_mask =None, 
                               dst_ip_list =None, dst_ip =None, dst_ip_mask =None, 
                               tos_bit =None,
                               src_port=None,src_port_min=None,src_port_max=None,
                               dst_port=None,dst_port_min=None,dst_port_max=None,
                               sequence=10):
        """ bigtap: construct the match string for policy
            Get_args format
            Mingtao
        """
        args = helpers.get_args(self.bigtap_construct_match)
#        helpers.log("args: %s" % helpers.prettify(args))
        
        ip = args['ip']
        ip6 = args['ip6']
        src_ip = args['src_ip']
        src_ip_mask = args['src_ip_mask']
                
        t = test.Test()
        c = t.controller()  
        temp = '{'

  
        if src_mac:
            temp += '"src-mac": "%s",' %src_mac
        if dst_mac:
            temp += '"dst-mac": "%s",' %dst_mac
        
        if icmp:
            temp += '"ip-proto": 1,'        
            if icmp_code:
                temp += '"dst-tp-port": %s,' % icmp_code      
            if icmp_type:
                temp += '"src-tp-port": %s,' % icmp_type
                  
        if ether_type:
            if ether_type == 'ipv6':
                temp += '"ether-type": 34525,'
            elif ether_type == 'ip':
                temp += '"ether-type": 2048,'
            else:
                temp += '"ether-type": %s,' % ether_type
        elif ip6:
            temp += '"ether-type": 34525,' 
        else:
            temp += '"ether-type": 2048,'
                
        if tcp:
            temp +='"ip-proto": 6,'  
        elif udp:
            temp +='"ip-proto": 17,'   

        if vlan_id:
            temp +='"vlan-id":  %s ,' % vlan_id  
        else:
            if vlan_min:
                temp +='"src-tp-port-min": %s,' % vlan_min  
            if vlan_max:
                temp +='"src-tp-port-min": %s,' % vlan_max  
                    
        if src_ip_list:
            temp += '"src-ip-list": "%s",' % src_ip_list
        else:
            if src_ip:
                temp += '"src-ip": "%s",' % src_ip  
            if src_ip_mask:
                temp += '"src-ip-mask": "%s",' % src_ip_mask  

        if dst_ip_list:
            temp += '"dst-ip-list": "%s",' % dst_ip_list
        else:
            if dst_ip:
                temp += '"dst-ip": "%s",' % dst_ip  
            if dst_ip_mask:
                temp += '"dst-ip-mask": "%s",' % dst_ip_mask  

        if tos_bit:
            temp +='"ip-tos": %s,' % tos_bit
 
        if src_port:
            temp +='"src-tp-port":  %s ,' % src_port  
        else:
            if src_port_min:
                temp +='"src-tp-port-min": %s,' % src_port_min  
            if src_port_max:
                temp +='"src-tp-port-min": %s,' % src_port_max   
                            
        if dst_port:
            temp +='"dst-tp-port":  %s ,' % dst_port  
        else:
            if dst_port_min:
                temp +='"dst-tp-port-min": %s,' % dst_port_min  
            if dst_port_max:
                temp +='"dst-tp-port-min": %s,' % dst_port_max   
                 
        temp +='"sequence": %s}' % sequence                              
        helpers.log("the temp is: %s"  % (str(temp)) )  
                    
        return temp 
    
    
    

    
    
    
    
                              