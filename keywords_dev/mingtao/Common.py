import autobot.helpers as helpers
import autobot.test as test
import keywords.BigTap as BigTap
import re
import time
 

class Common(object):
# This is for all the common function   - Mingtao
    def __init__(self):
        pass
 



##################################
##  Finalize API
## 
 
  
 
 
  
    def rest_show_policy(self,policy):
        """ Get the rest output of "show bigtap policy XX"
            -- Mingtao
            Usage:                     
        """ 
        t = test.Test()
        c= t.controller('master')
        url ='/api/v1/data/controller/applications/bigtap/view/policy[name="%s"]/info' % (policy)  
        c.rest.get(url)           
 
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())               
        if(c.rest.content()):
            helpers.log("INFO: name: %s" % c.rest.content()[0]['name'])
            if c.rest.content()[0]['name'] == str(policy):          
                return c.rest.content()[0]                     
            else:
                helpers.test_failure("ERROR: Policy does not correctly report policy name  : %s" % c.rest.content()[0]['name'])                
                return False 
        helpers.test_failure("ERROR: Policy does not correctly report " )      
        return False
 

      
    def verify_policy(self, input_dict, policy, action=None):
        """ Vrify the policy field 
            -- Mingtao
            need to enhance to take care of all possible field
            Usage:                     
        """ 
        helpers.log("input_dict: %s" % input_dict)
        
        if input_dict['name'] == str(policy ):
            helpers.test_log("INFO: Policy correctly reports policy name as : %s" % input_dict['name'])
        else:
            helpers.test_failure("ERROR: Policy does not correctly report policy name  : %s" % input_dict['name'])                
            return False    
            
        if action:
            if action == "forward":
                if input_dict['config-status'] == "active and forwarding":
                    helpers.test_log("INFO: Policy correctly reports config status as : %s" % input_dict['config-status'])
                else:
                    helpers.test_log("ERROR: Policy NOT correctly report config status  EXPECT : active  --  ACTUAL: %s " % input_dict['config-status'])
                    return False                                    
                      
                if input_dict['runtime-status'] == "installed":
                    helpers.test_log("INFO: Policy correctly reports runtime status as : %s" % input_dict['runtime-status'])         
                else:
                    helpers.test_failure("ERROR: Policy NOT correctly report runtime status EXPECT : installed  -- ACTUAL: %s" % input_dict['runtime-status'])
                    return False
                
            if action == "rate-measure":
                if input_dict['config-status'] == "active and rate measure":
                    helpers.test_log("INFO: Policy correctly reports config status as : %s" % input_dict['config-status'])          
                else:
                    helpers.test_failure("ERROR: Policy NOT correctly report config status  EXPECT : rate measure  --  ACTUAL: %s " % input_dict['config-status'])
                    return False                                    
                      
                if input_dict['runtime-status'] == "installed":
                    helpers.test_log("INFO: Policy correctly reports runtime status as : %s" % input_dict['runtime-status'])         
                else:
                    helpers.test_log("ERROR: Policy NOT correctly report runtime status EXPECT : installed  -- ACTUAL: %s" % input_dict['runtime-status'])
                    return False
                                
                
            if action == "inactive":
                if input_dict['config-status'] == "inactive":
                    helpers.test_log("INFO: Policy correctly reports config status as : %s" % input_dict['config-status'])               
                else:
                    helpers.test_log("ERROR: Policy NOT correctly report config status  EXPECT: inactive  -- ACTUAL: %s" % input_dict['config-status'])
                    return False
                       
                if input_dict['runtime-status'] == "inactive":
                    helpers.test_log("INFO: Policy correctly reports runtime status as : %s" % input_dict['runtime-status'])         
                else:
                    helpers.test_log("ERROR: Policy NOT correctly report runtime status EXPECT: inactive  -- ACTUAL:  %s" % input_dict['runtime-status'])
                    return False                
            
        return True
 
 
 
 

##  End of finalized APIs to be committed 

#########################
############################
# APIs to be committed to production
########################
   
    def bigtap_test_setup(self):
        test.Test()
        bigtap = BigTap.BigTap()
        bigtap.bigtap_delete_all()
        bigtap.rest_disable_feature(feature_name='l3-l4-mode')
        bigtap.rest_disable_feature(feature_name='tracked-host')        
      

    def bigtap_test_teardown(self):
#       self.bigtap_delete_all()
        pass


    def rest_show_feature(self, l3_l4=None,inport_mask =None):
        """ verify bigtap mode: l3_l4 and inport_mask
            -- Mingtao
        """
        t = test.Test()
        c= t.controller('master')
        
        url = '/api/v1/data/controller/applications/bigtap/info'  
        c.rest.get(url)

        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
        data = c.rest.content()
          
        if l3_l4:
            helpers.test_log("INFO: Bigtap  reports L3-L4-mode as: %s " % data[0]['l3-l4-mode'])
            return str(data[0]['l3-l4-mode'])
                          
        if inport_mask:
            if str(data[0]['inport-mask']) == str(inport_mask):            
                helpers.test_log("INFO: Bigtap  reports inport-mask as: %s " % data[0]['inport-mask'])
                return str(data[0]['inport-mask'])
        return True                
        



 

    def rest_show_switch_attribute(self, dpid=None, node=None, attr="type"):
        """ show switch attibut,  can get type 
            -- Mingtao
        """
        t = test.Test()
        c= t.controller('master')
        bigtap = BigTap.BigTap()

        if dpid is None:
            helpers.test_log("INFO: Need to get dpid for switch %s " % node )
            swid = bigtap.rest_show_switch_dpid(node)
        else:
            swid = dpid
        url = '/api/v1/data/controller/core/switch[dpid="%s"]?select=attributes'  % swid          
        c.rest.get(url)

        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
        data = c.rest.content()[0]["attributes"]
    
        if attr == "type":       
            helpers.test_log("INFO: Switch  %s  type is %s " % (swid, data["description-data"]["hardware-description"]))              
            return   data["description-data"]["hardware-description"] 
        
        return True

    def verify_switch_tcam(self, node=None, l3_l4_mode=None):
        """ verify the switch tcam size
            -- Mingtao
        """   
#        t = test.Test()
        bigtap = BigTap.BigTap()
        
#        sw = t.switch(node)
        node_type = self.rest_show_switch_attribute(node=node)
        size = bigtap.rest_show_switch_flow(switch_alias=node, return_value='maximum-entries')
          
        if l3_l4_mode == "True":           
            if "LB9" in node_type:
                if size == 4088:
                    helpers.test_log("INFO: Switch  - %s  type - %s  and - L3-l4 mode, tcam size - %s " % (node, node_type, str(size)))  
                    return True
                else:
                    helpers.test_log("ERROR: Switch - %s  type - %s  and - L3-l4 mode, tcam size expect - 4088, actual - %s " % (node, node_type, str(size)))  
                    return False  
           
        else:
            if "LB9" in node_type:
                if size == 2044:
                    helpers.test_log("INFO: Switch - %s  type - %s, mode -  not L3-l4, tcam size - %s " % (node, node_type, str(size)))  
                    return True
                else:
                    helpers.test_log("ERROR: Switch - %s  type -%s, mode - not L3-l4, tcam size expect: - 2044, actual - %s " % (node, node_type, str(size)))  
                    return False  
          
        return True

 
    def cli_show_l3_l4(self):
        t = test.Test()
        c= t.controller('master')
        string = 'show running-config bigtap |  grep l3-l4 | wc -l '
        c.cli(string)
        content = c.cli_content()
        helpers.log("***** content: %s" % content)
        lines = content.split('\r\n')
        helpers.log("***** lines: %s" % lines)
        if int(lines[1]) == 0:
            helpers.log("INFO: the l3_l4 is not configured" )  
            return "False"
        elif int(lines[1]) == 1:
            helpers.log("INFO: the l3_l4 is not configured" )    
            return "True"     
        else:
            helpers.test_failure(c.rest.error())         
            return False














 
 

    def rest_bigtap_verify_interface_name(self,name,role,switch,if_name):
        """ verify bigtap  interface role
            -- Mingtao
            Usage: 
        """
        t = test.Test()
        c= t.controller('master')
        url = '/api/v1/data/controller/applications/bigtap/interface-config'  
        c.rest.get(url)
        
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
                return False
        else :
            helpers.test_log("ERROR bigtap role does not exist. Error seen: %s" % (c.rest.result_json()))
            return False        
        




 
 
    def bigtap_gen_addrgroup_file(self,file_name,group,addr_type,base,incr,mask,number,flag='new'):
        ''' Generate # of address for a address group and put to a local file
            -- Mingtao
            Usage: 
                bigtap_gen_addrgroup_file     IP1_500       G1_500      ipv4     200.0.0.0     0.1.0.1        255.255.255.255     500       flag=append
                bigtap_gen_addrgroup_file     IP2_500       G2_500      ipv4     110.0.0.0     0.1.0.1        255.255.255.255     500       
        '''         
        helpers.log("the base address is: %s,  the step is: %s,  the mask is: %s,  the Number is: %s"  
                    % (str(base), str(incr), str(mask),  str(number)))   
         
        if flag == 'append':
            fo = open(file_name,'a')
            temp ='' 
        else:
            fo = open(file_name,'w')
            temp = "bigtap address-group %s \n ip type %s \n" % (str(group), str(addr_type))
 
        temp = temp + " ip %s %s \n"  % (str(base),str(mask))   
        Num = int(number) - 1
        for _ in range(0,int(Num)):    
            ipAddr = helpers.get_next_address(addr_type,base,incr) 
            base = ipAddr
            temp = temp+" ip %s %s \n"  % (str(ipAddr),str(mask)) 
            
        fo.write(str(temp))                  
        fo.close()  
        return True         
    
 
     

 

 




    
        
##############################  end APIs to be committed to production   #######################     
 
    def rest_bigtap_setup_role(self,sw_name,intf,role,int_name):
        """ setup bigtap interface role
            usage:  REST bigtap setup role    S204    ethernet49    filter     S204-49 
            Animish fix to take both alias and dpid
        """
        
        t = test.Test()
        c = t.controller()
  
        sw_dpid = self.rest_get_switch_dpid(str(sw_name))       
        helpers.log("name: %s ===> DPID: %s" % (str(sw_name), str(sw_dpid)))

        url = '/api/v1/data/controller/applications/bigtap/interface-config[interface="%s"][switch="%s"]' % (str(intf), str(sw_dpid))
        c.rest.put(url, {"interface": str(intf), "switch": str(sw_dpid), 'role':str(role),'name':str(int_name)})
        helpers.test_log("Ouput: %s" % c.rest.result_json())
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
            return False
        else:
            helpers.test_log(c.rest.content_json())
            return True      
        

    def rest_bigtap_config_l34(self,l3_l4,flag="true"):
        """ configure L3_l4 mode
            Mingtao
            Flag:  true    -  expect configuration go through
                   negative  - expect configuration not go through
            Mingtao - remove
        """
        t = test.Test()
        c = t.controller()
        
        url ='/api/v1/data/controller/applications/bigtap/feature'  
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
 

    def bigtap_gen_poliy_match(self,file_name,policy,addr_type,modify_field,base,incr,mask,number,sequence, common=''):
        """ Generate # of matches for a policy and put to a file
            Mingtao
            TBD - file can be new or append
        """
          
        helpers.log("the base address is: %s,  the step is: %s,  the mask is: %s,  the Num is: %s, the common field: %s"  
                    % (str(base), str(incr), str(mask),  str(number), str(common)))   
         
        fo = open(file_name,'w')
        temp = "bigtap policy %s \n"  % (str(policy)) 
        fo.write(str(temp)) 
               
        if addr_type == 'ip' or addr_type == 'ip6':
            temp = "%d match %s %s %s %s %s\n"  % (int(sequence),str(addr_type), str(addr_type), str(base),str(mask), str(common))              
            fo.write(str(temp))       
            if modify_field == 'src-ip' or modify_field == 'dst-ip':            
                Num = int(number) - 1            
                for num in range(0,int(Num)):  
                
                    ipAddr = helpers.get_next_address(addr_type,base,incr)                
                    base = ipAddr   
                    new_sequence = int(sequence) + num + 1
                    temp = "%d match %s %s %s %s %s\n"  % (new_sequence, str(addr_type), str(modify_field), str(ipAddr), str(mask), str(common))                   
                    fo.write(str(temp))  
 
        fo.close()  
        return True                         
 
  


    def bigtap_gen_config_match(self,pname,match_type,field,base,incr,mask=None,number='10',sequence='100', **kwargs):
        """ add multiple match entries to a policy 
            Mingtao
            Done: ipv4/ipv6  src_ip,  dst_ip
            Usage: 
                bigtap_gen_config_match_new   IP1   ip  src_ip  10.0.0.0  0.0.0.1  255.255.255.255  10  100 
                bigtap_gen_config_match_new   IP1   tcp  dst_port  100  1   number=10  sequence=200 
            To BE Done:  other fields: port    mac   vlan ....
                 common: dst-ip=100 100.100.100.1, dst-ip-mask=255.255.255.0   
            
        """
        helpers.log("policy Name is: %s, mtype is: %s, cType is : %s, base is: %s,   step is: %s,  mask is: %s,  Num is: %s,  common: %s" 
                     % (str(pname), str(match_type), str(field), str(base), str(incr), str(mask),  str(number), kwargs ))   
     
        if field in ('src_ip', 'dst_ip'): 
            #match type is:  ip  ip6  ipv4  ipv6 
            Num = int(number)         
            for num in range(0,int(Num)): 
                kwargs[field] = base
                kwargs[field + '_mask'] = mask                            
                helpers.log("the num is:  %s ;  kwargs is : %s" % (str(num), kwargs))   
                mNum = int(num) + int(sequence)                 
                match_string = self.bigtap_construct_match(ip_type=match_type, sequence=mNum, **kwargs) 
                self.rest_bigtap_add_policy_match("admin-view", pname,mNum,match_string)         
                                                        
                ipAddr = helpers.get_next_address(match_type,base,incr)
                base = ipAddr 
                    
        if field in ('dst_port', 'src_port'): 
            # match_type is:  tcp  udp, tcp6  udp6
            Num = int(number)         
            for num in range(0,int(Num)): 
                kwargs[field] = base                                        
                helpers.log("the num is:  %s ;  kwargs is : %s" % (str(num), kwargs))   
                mNum = int(num) + int(sequence)                 
                match_string = self.bigtap_construct_match(ip_proto=match_type, sequence=mNum, **kwargs) 
                self.rest_bigtap_add_policy_match("admin-view", pname,mNum,match_string)                                                                                
                base = int(base) + int(incr) 
                                       
        if field in ('vlan'): 
            # match_type is: ip ipv6  tcp tcp6 udp udp6  
            Num = int(number)         
            for num in range(0,int(Num)): 
                kwargs[field] = base                                        
                helpers.log("the num is:  %s ;  kwargs is : %s" % (str(num), kwargs))   
                mNum = int(num) + int(sequence)    
                if match_type == 'ip' or  match_type == 'ipv4' or  match_type == 'ip6' or match_type == 'ipv6':          
                    match_string = self.bigtap_construct_match(ip_type=match_type, sequence=mNum, **kwargs) 
                if match_type == 'tcp' or  match_type == 'tcp6' or  match_type == 'udp' or match_type == 'udp6':  
                    match_string = self.bigtap_construct_match(ip_proto=match_type, sequence=mNum, **kwargs)                                   
                self.rest_bigtap_add_policy_match("admin-view", pname,mNum,match_string)                                                                                
                base = int(base) + int(incr) 

                        
        if field in ('src_mac','dst_mac'): 
            # match_type is: ip ipv6  tcp tcp6 udp udp6  
            Num = int(number)         
            for num in range(0,int(Num)): 
                kwargs[field] = base                                        
                helpers.log("the num is:  %s ;  kwargs is : %s" % (str(num), kwargs))   
                mNum = int(num) + int(sequence)    
                if match_type == 'ip' or  match_type == 'ipv4' or  match_type == 'ip6' or match_type == 'ipv6':          
                    match_string = self.bigtap_construct_match(ip_type=match_type, sequence=mNum, **kwargs) 
                if match_type == 'tcp' or  match_type == 'tcp6' or  match_type == 'udp' or match_type == 'udp6':  
                    match_string = self.bigtap_construct_match(ip_proto=match_type, sequence=mNum, **kwargs)   
                                                    
                self.rest_bigtap_add_policy_match("admin-view", pname,mNum,match_string)  
                macAddr = helpers.get_next_mac(base,incr)                                                                              
                base = macAddr

        if field in ('protocol'): 
            # match_type is: ip ipv6   ip6
            Num = int(number)         
            for num in range(0,int(Num)): 
                kwargs['ip_proto'] = base                                        
                helpers.log("the num is:  %s ;  kwargs is : %s" % (str(num), kwargs))   
                
                mNum = int(num) + int(sequence)    
                match_string = self.bigtap_construct_match(ether_type=match_type, sequence=mNum, **kwargs) 
                self.rest_bigtap_add_policy_match("admin-view", pname,mNum,match_string)                                                                  
                base = int(base) + int(incr) 
        
        return True   

    def copy_to_controller(self,fName,dst_name):
        '''  copy a file to controller.  
             -- Mingtao
             Usage: copy_to_controller       IP1_500     /opt/bigswitch/run/saved-configs/IP1_500 
        '''
        t = test.Test()
        c= t.controller('master')
        helpers.test_log("Input arguments: File Name = %s, Dest Name = %s" % (fName,dst_name))         
        helpers.scp_put(c.ip, fName, dst_name)           
        return True
        

    def cli_copy_to_running(self,fName):
        '''  copy a file to running configureation.  
             -- Mingtao
             Usage: li_copy_to_running      IP1_500
        '''
        t = test.Test()
        c= t.controller('master')
        helpers.test_log("copy File Name = %s " % fName ) 
        string = "copy file://%s running-config" % fName 
        result = c.config(string)
        helpers.log("Output: %s" % result)         
        
        return True
        

    def rest_bigtap_verify_policy(self, policy_name, action=None):
        ''' check the policy config-status and runtime-status
            -- Mingtao
            Usage:   self.rest_bigtap_verify_policy('SC','inactive')
           TBD:  enhance for other field
        '''   
        t = test.Test()
        c= t.controller('master')
        url ='/api/v1/data/controller/applications/bigtap/view/policy[name="%s"]/info' % (policy_name)
        c.rest.get(url)
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
        content = c.rest.content()
     
        if content[0]['name'] == str(policy_name):
            helpers.test_log("Policy correctly reports policy name as : %s" % content[0]['name'])
        else:
            helpers.test_failure("Policy does not correctly report policy name  : %s" % content[0]['name'])                
            return False
 
        if action:
            if action == "forward":
                if content[0]['config-status'] == "active and forwarding":
                    helpers.test_log("Policy correctly reports config status as : %s" % content[0]['config-status'])
                else:
                    helpers.test_failure("Policy NOT correctly report config status  EXPECT : active  --  ACTUAL: %s " % content[0]['config-status'])
                    return False                                    
                      
                if content[0]['runtime-status'] == "installed":
                    helpers.test_log("Policy correctly reports runtime status as : %s" % content[0]['runtime-status'])         
                else:
                    helpers.test_failure("Policy NOT correctly report runtime status EXPECT : installed  -- ACTUAL: %s" % content[0]['runtime-status'])
                    return False
                
            if action == "rate-measure":
                if content[0]['config-status'] == "active and rate measure":
                    helpers.test_log("Policy correctly reports config status as : %s" % content[0]['config-status'])          
                else:
                    helpers.test_failure("Policy NOT correctly report config status  EXPECT : rate measure  --  ACTUAL: %s " % content[0]['config-status'])
                    return False                                    
                      
                if content[0]['runtime-status'] == "installed":
                    helpers.test_log("Policy correctly reports runtime status as : %s" % content[0]['runtime-status'])         
                else:
                    helpers.test_failure("Policy NOT correctly report runtime status EXPECT : installed  -- ACTUAL: %s" % content[0]['runtime-status'])
                    return False
                                
                
            if action == "inactive":
                if content[0]['config-status'] == "inactive":
                    helpers.test_log("Policy correctly reports config status as : %s" % content[0]['config-status'])               
                else:
                    helpers.test_failure("Policy NOT correctly report config status  EXPECT: inactive  -- ACTUAL: %s" % content[0]['config-status'])
                    return False
                       
                if content[0]['runtime-status'] == "inactive":
                    helpers.test_log("Policy correctly reports runtime status as : %s" % content[0]['runtime-status'])         
                else:
                    helpers.test_failure("Policy NOT correctly report runtime status EXPECT: inactive  -- ACTUAL:  %s" % content[0]['runtime-status'])
                    return False             
 
            return True
        
        return True


    
    
##################end files to be staged to production ################### 
 

 
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
         
        url = '/api/v1/data/controller/core/aaa/group'  
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
    


    def rest_show_switch_by_ip(self,ip,feild=None):
        # not working
        t = test.Test()
        c = t.controller('master')
        url = 'api/v1/data/controller/core/switch?select=alias'  
        c.rest.get(url)
 
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
            return False
        
        content = c.rest.content()       
        if feild:
            if ip == content[0]['inet-address']['ip']:
                return content[0]['feild']
        return content[0]['alias']
  



    def  bigtap_longevity(self, during='300', flap='60'):
             
        helpers.log("INFO:   longevity test for up to %s sec " % (during))      
        step = int(flap)*2 
        for i in range (0,int(during),step):
            # change the action      
            helpers.log("INFO:  ==========this is the  %s sec =========== " % str(i) )             
            self.rest_bigtap_set_policy_action('admin-view','SC','inactive')
            time.sleep(int(flap))           
            self.rest_bigtap_verify_policy('SC','inactive')

            self.rest_bigtap_set_policy_action('admin-view','SC','forward')            
            time.sleep(int(flap))    
            self.rest_bigtap_verify_policy('SC','forward') 
           
        return True
    
 


        
##############  switch  API  start   
    def cli_bigtap_sw_show(self, sw_name, cli_show):
        t = test.Test()
        sw = t.switch(sw_name)
        helpers.log("switch is: %s;  the show command is:  %s" % (sw, cli_show ))
        result = sw.cli(cli_show)       
        
        helpers.log("Output: %s" % result)        
        return result


    def cli_bigtap_sw_show_walk(self, sw_name):
        t = test.Test()
        sw = t.switch(sw_name)
        helpers.log("switch is: %s;" % sw )
        result = sw.cli('show ?')     
        content = result.content()
        temp = content.split('\r\n')
        
        helpers.log("Output: %s" % content) 
        helpers.log("Output in list: %s" % temp)                
        return result







################### switch end  

        
        
        