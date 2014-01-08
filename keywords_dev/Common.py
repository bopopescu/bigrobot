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
        
        
        
    def sleep_now(self, Flag):
        if (Flag == 'short'):
            helpers.sleep(float(5))
        if (Flag == 'very short'):
            helpers.sleep(float(2))    
        if (Flag == 'long'):
            helpers.sleep(float(10))    
            
            
            
            
     
    def bigtap_clean_up(self, Feature):
        t = test.Test()
        c = t.controller()       
        if ( Feature == 'policy'):
            url = '%s/api/v1/data/controller/applications/bigtap/view/policy?select=info' % (c.base_url)
            c.rest.get(url)
            content = c.rest.content()
            if not c.rest.status_code_ok():
                helpers.test_failure(c.rest.error())
                return False
            helpers.log("Output: %s" % c.rest.result_json()) 
            length =len(content)
             
#            helpers.log("Content Output: \n %s " % content )
            helpers.log("Number of Policies is: %s" % str(length))        
            for index in range(length):
                name = content[index]['name']
                helpers.log("this is the %s Policy to be cleaned: %s" % (str(index), str(name)))
                url = '%s/api/v1/data/controller/applications/bigtap/view[name="admin-view"]/policy[name="%s"]' % (c.base_url,str(name))   
                c.rest.delete(url) 
                if not c.rest.status_code_ok():
                    helpers.test_failure(c.rest.error())                    
                                
        if ( Feature == 'address-group'):
            url = '%s/api/v1/data/controller/applications/bigtap/ip-address-set' % (c.base_url)      
            c.rest.get(url) 
            content = c.rest.content()
            if not c.rest.status_code_ok():
                helpers.test_failure(c.rest.error())
                return False
            helpers.log("Output: %s" % c.rest.result_json()) 
            length =len(content)  
 #           helpers.log("Content Output: \n %s " % content )
            helpers.log("Number of address group is: %s" % str(length))        
            for index in range(length):
                name = content[index]['name']
                helpers.log("this is the %s Address-group to be cleaned: %s" % (str(index), str(name)))
                url = '%s/api/v1/data/controller/applications/bigtap/ip-address-set[name="%s"]' % (c.base_url,str(name))   
                c.rest.delete(url) 
                if not c.rest.status_code_ok():
                    helpers.test_failure(c.rest.error())                                   
        if ( Feature == 'l3-l4-mode'):
            url = '%s/api/v1/data/controller/applications/bigtap/feature/l3-l4-mode' % (c.base_url)      
            c.rest.delete(url) 
            if not c.rest.status_code_ok():
                helpers.test_failure(c.rest.error())
        return True   
        
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
    
    def rest_bigtap_verify_l34(self, l3_l4="False"):
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
   
    def rest_show_run_bigtap_policy(self, pName=None):
        t = test.Test()
        c = t.controller()
        
        if pName is None:
            url = '%s/api/v1/data/controller/applications/bigtap/view?config=true' % (c.base_url)
        else:
            url = '%s/api/v1/data/controller/applications/bigtap/view[policy/name="%s"]?config=true&select=policy[name="%s"]' % (c.base_url, str(pName), str(pName)) 
            
        c.rest.get(url)
        helpers.log("Output: %s" % c.rest.result_json())
    
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())

        return c.rest.content() 
 
 # same as rest _add_policy  in bigtapcommonconfig
    def rest_bigtap_add_policy(self,viewName,policyName,policyAction):
        t = test.Test()
        c = t.controller()
        c.http_port=8082
        url='http://%s:%s/api/v1/data/controller/applications/bigtap/view[name="%s"]/policy[name="%s"]' % (c.ip,c.http_port, str(viewName), str(policyName))
        c.rest.put(url,{'name':str(policyName)})
        helpers.test_log("Ouput: %s" % c.rest.result_json())
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
        c.rest.patch(url,{"action": str(policyAction) })
        helpers.test_log("Ouput: %s" % c.rest.result_json())
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
            return False
        else:
            helpers.test_log(c.rest.content_json())
            return True 
    
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
        helpers.test_log(c.rest.content_json())
        if (Flag == 'negative'):
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
        #mingtao  -  TBD
        #swDpid = self.rest_get_switch_dpid(str(swName))       
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
        

    def rest_get_switch_flow(self,swName,numFlow):
        t = test.Test()
        c = t.controller()
        c.http_port=8082
        
        swDpid = self.rest_get_switch_dpid(str(swName))       
        helpers.log("name: %s ===> DPID: %s" % (str(swName), str(swDpid)))
        
        url ='%s/api/v1/data/controller/core/switch[dpid="%s"]?select=stats/table' % (c.base_url,str(swDpid))
        
        c.rest.get(url)
        helpers.test_log("Json Ouput: %s" % c.rest.result_json())             
        helpers.test_log("Ouput: %s" % c.rest.content()) 
        
        content = c.rest.content()
        helpers.log("Return value for number of flows is %s" % content[0]['stats']['table'][1]['active-count'])
        flows = content[0]['stats']['table'][1]['active-count']    
    
        if flows == int(numFlow) :
            helpers.test_log("Switch %s is correctly programmed with %s of flows" % (str(swName), str(flows)) ) 
        else:
            debug_url= '%s/api/v1/data/controller/core/switch[dpid="%s"]?select=stats/flow' % (c.base_url,str(swDpid)) 
            c.rest.get(url) 
            helpers.test_log("******debug  Ouput******* \n %s" % c.rest.result_json())                
            helpers.test_failure("Switch %s is NOT correctly programmed with flows,  expect: %s  Actual: %s" % (str(swName), str(numFlow), str(flows)) )                      
            return False  
                  
 #  the same as Animesh,  add Flag
    def rest_bigtap_add_policy_match(self,viewName,policyName,match_number,data,Flag="true"):
        t = test.Test()
        c = t.controller()
        c.http_port=8082
        url='http://%s:%s/api/v1/data/controller/applications/bigtap/view[name="%s"]/policy[name="%s"]/rule[sequence=%s]'  % (c.ip,c.http_port,str(viewName),str(policyName),str(match_number))
        data_dict = helpers.from_json(data)
        c.rest.put(url,data_dict)
        helpers.test_log(c.rest.result_json())
        helpers.test_log(c.rest.content_json()) 
        if (Flag == 'negative'):
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
        
    def rest_bigtap_config_l34(self,l3_l4,Flag="true"):
        t = test.Test()
        c = t.controller()
        
        url ='%s/api/v1/data/controller/applications/bigtap/feature' % (c.base_url)
        c.rest.patch(url, {"l3-l4-mode": str(l3_l4)})
              
        helpers.test_log(c.rest.result_json())
        helpers.test_log(c.rest.content_json()) 
        if (Flag == 'negative'):
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
            

    def bigtap_gen_address_group(self,fName,gName,Type,base,incr,Mask,Num):
        t = test.Test()
        c = t.controller()
        
        helpers.log("the base address is: %s,  the step is: %s,  the mask is: %s,  the Num is: %s"  % (str(base), str(incr), str(Mask),  str(Num)))   
         
        fo = open(fName,'w')
        temp = "bigtap address-group %s \n ip type %s \n ip %s %s \n"  % (str(fName), str(gName),str(base),str(Mask)) 
        fo.write(str(temp)) 
                
        if Type == 'ipv4': 
            ip = list(map(int, base.split(".")))
            step = list(map(int, incr.split(".")))
            
            ipAdd = []
            Num = int(Num) - 1
            
            for num in range(0,int(Num)):
                ip[3] += step[3]
                if ip[3] >= 256:
                    ip[3] = 0
                    ip[2] +=1
                ip[2] += step[2]   
                if ip[2] >= 256:
                    ip[2] = 0
                    ip[1] +=1
                ip[1] += step[1]     
                if ip[1] >= 256:
                    ip[1] = 0
                    ip[0] +=1
                    
                ip[0] += step[0]        
                if ip[0] >= 256:
                    ip[0] = 0
                
                ipAdd  = '.'.join(map(str,ip)) 
                temp = " ip %s %s \n"  % (str(ipAdd),str(Mask)) 
                fo.write(str(temp)) 
                                
#                helpers.log("the address is: %s"  % (str(ipAdd)))    
                               
        if Type == 'ipv6' :
            ip = base.split(":")
            step =  incr.split(":")
            
            helpers.log("IP list is %s" % ip)
            
            ipAdd = []
            hexip = []
            Num = int(Num) - 1
            
            for index,item in enumerate(ip):
                helpers.log("The list is:  %s -- %s "  % (str(index), str(item)))   
                
            for num in range(0,int(Num)):   
                hexip = []             
                for i in range(0,7):
                    index = 7 - int(i)
                    helpers.log("The %s value is (%s): %d"  % (int(index), ip[index], int(ip[index], 16)))                     
 
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
                    
                    
                ipAdd  = ':'.join(map(str,hexip)) 
                temp = " ip %s %s \n"  % (str(ipAdd),str(Mask)) 
                fo.write(str(temp)) 
                                
 
 
        fo.close()  
        return True                         

    def bigtap_gen_match(self,fName,pName,mType,cType,base,incr,Mask,Num,common=''):
        t = test.Test()
        c = t.controller()
        
        helpers.log("the base address is: %s,  the step is: %s,  the mask is: %s,  the Num is: %s, the common field: %s"  % (str(base), str(incr), str(Mask),  str(Num), str(common)))   
         
        fo = open(fName,'w')
        temp = "bigtap policy %s \n"  % (str(pName)) 
        fo.write(str(temp)) 
                
        if mType == 'ip': 
            if cType == 'src-ip' or cType == 'dst-ip':   
                temp = "10 match ip %s %s %s %s\n"  % (str(cType), str(base),str(Mask), str(common))  
                fo.write(str(temp))       
                ip = list(map(int, base.split(".")))
                step = list(map(int, incr.split(".")))            
                ipAdd = []
                Num = int(Num) - 1
            
                for num in range(0,int(Num)):
                    ipAdd = [] 
                    for i in range(3,0,-1):
                        ip[i] += step[i]
                        if ip[i] >= 256:
                            ip[i] = 0
                            ip[i-1] +=1
                    ip[0] += step[0]        
                    if ip[0] >= 256:
                        ip[0] = 0
                
                    ipAdd  = '.'.join(map(str,ip)) 
                    mNum = int(num) + 100 
                    temp = "%d match ip %s %s %s %s\n"  % (mNum, str(cType), str(ipAdd),str(Mask), str(common)) 
                    fo.write(str(temp))  
                               
        if mType == 'ip6' :  
            if cType == 'src-ip' or cType == 'dst-ip':               
                temp = "10 match ip6 %s %s %s %s\n"  % (str(cType), str(base),str(Mask), str(common))  
                fo.write(str(temp))       
                ip = base.split(":")
                step =  incr.split(":")
                helpers.log("IP list is %s" % ip)
            
                ipAdd = []
                hexip = []
                Num = int(Num) - 1
 
                for num in range(0,int(Num)):   
                    hexip = []             
                    for index in range(7,0,-1):
                        helpers.log("The %s value is (%s): %d"  % (int(index), ip[index], int(ip[index], 16)))                     
 
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
                                        
                    ipAdd  = ':'.join(map(str,hexip)) 
                    mNum = int(num) + 100 
                    temp = "%d match ip6 %s %s %s %s\n"  % (mNum, str(cType), str(ipAdd),str(Mask), str(common)) 
                    fo.write(str(temp)) 
                                
 
 
        fo.close()  
        return True                         
 
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
        
    def rest_copy_file_to_running(self,fName):
        """  there is no REST API for it,  need to reconsider
        
        """
        t = test.Test()
        c = t.controller()
        
        helpers.test_log("Input arguments: File Name = %s, Dest Name = %s" % (fName,dst_name)) 
        
        url ='%s/api/v1/data/controller/applications/bigtap/view/policy[name="IP1"]/debug' % (c.base_url)
        
        return True
 
 
 
 
    def bigtap_apply_address_group(self,gName,Type,base,incr,Mask,Num):
        """ Generate and apply #Num of ipv4/ipv6 for address-group  
            Mingtao
            Usage:
                bigtap_apply_address_group     IPV4    ipv4     10.0.0.0     0.1.0.1        255.255.255.0     20
                bigtap_apply_address_group     IPV6    ipv6     f001:100:0:0:0:0:0:0     0:0:0:0:0:0:0:1     ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff     20
        """
        t = test.Test()
        c = t.controller()
        
        helpers.log("the base address is: %s,  the step is: %s,  the mask is: %s,  the Num is: %s"  % (str(base), str(incr), str(Mask),  str(Num)))   
         
        self.rest_bigtap_create_addgroup(gName,Type)
        self.rest_bigtap_add_address(gName,base,Mask)

        Num = int(Num) - 1            
        for num in range(0,int(Num)):    
           
            ipAddr = self.get_next_address(Type,base,incr)
            self.rest_bigtap_add_address(gName,ipAddr,Mask)
            base = ipAddr
            helpers.log("the applied address is: %s %s %s "  % (Type, str(ipAddr), str(Mask)))     
        
        return True         
 
 
    def get_next_address(self,Type,base,incr): 
        """ Generate the next address bases on the base and step.
            Mingtao
            Usage:    ipAddr = self.get_next_address(ipv4,'10.0.0.0','0.0.0.1')
        """
        t = test.Test()
        c = t.controller()
           
        helpers.log("the base address is: %s,  the step is: %s,  "  % (str(base), str(incr)))   
        if Type == 'ipv4': 
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
             
            
        if Type == 'ipv6' :
            ip = base.split(":")
            step =  incr.split(":")
            helpers.log("IP list is %s" % ip)
            
            ipAddr = []
            hexip = []  
            
#            for index,item in enumerate(ip):
#               helpers.log("The list is:  %s -- %s "  % (str(index), str(item)))   
                     
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
 
    def bigtap_apply_match(self,pName,mType,cType,base,incr,Mask,Num,common=''):
        """ not done  Mingtao
        """
        t = test.Test()
        c = t.controller()
        
        helpers.log("the base address is: %s,  the step is: %s,  the mask is: %s,  the Num is: %s, the common field: %s"  % (str(base), str(incr), str(Mask),  str(Num), str(common)))   
         
 
        temp = "bigtap policy %s \n"  % (str(pName)) 
                 
        if mType == 'ip': 
            if cType == 'src-ip' or cType == 'dst-ip':   
                temp = "10 match ip %s %s %s %s\n"  % (str(cType), str(base),str(Mask), str(common))  
  
                Num = int(Num) - 1
            
                for num in range(0,int(Num)):
                    mNum = int(num) + 100 
                    temp = "%d match ip %s %s %s %s\n"  % (mNum, str(cType), str(ipAdd),str(Mask), str(common)) 
                    data = self.bigtap_construct_match()
                    self.rest_bigtap_add_policy_match(admin-view, pName,mNum,data,Flag="true") 
        return True   


#    REST bigtap add policy match       admin-view  IP1   10   {"dst-tp-port-min": 16, "ether-type": 2048, "dst-tp-port-max": 31, "ip-proto": 6, "sequence": 10}   
  
    def bigtap_construct_match(self,
                               ip=None, ip6=None, ether_type=None,
                               src_mac = None,
                               dst_mac = None,
                               udp=None, tcp=None,
                               vlan_id = None, vlan_min=None, vlan_max=None,  
                               src_ip_list =None, src_ip =None, src_ip_mask =None, 
                               dst_ip_list =None, dst_ip =None, dst_ip_mask =None, 
                               tos_bit =None,
                               dst_port_min=None,
                               dst_port_max=None,
                               sequence=10):
        """ bigtap: construct the match string for policy
            Mingtao
        """
        
        
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
            if ether_type == ipv6:
                temp += '"ether-type": 34525,'
            elif ether_type == ip:
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
 
        if src-port:
            temp +='"src-tp-port":  %s ,' % src-port  
        else:
            if src_port_min:
                temp +='"src-tp-port-min": %s,' % src_port_min  
            if src_port_max:
                temp +='"src-tp-port-min": %s,' % src_port_max   
                            
        if dst-port:
            temp +='"dst-tp-port":  %s ,' % dst-port  
        else:
            if dst_port_min:
                temp +='"dst-tp-port-min": %s,' % dst_port_min  
            if dst_port_max:
                temp +='"dst-tp-port-min": %s,' % dst_port_max   
                 
        temp +='"sequence": %s}' % sequence                              
        helpers.log("the temp is: %s"  % (str(temp)) )  
                    
        return temp 
                              