import autobot.helpers as helpers
import autobot.test as test
import keywords.BigTap as BigTap
import keywords.AppController as AppController 

class Common(object):
# This is for all the common function   - Mingtao
    def __init__(self):
        pass
 



    def cli_show_l3_l4(self):
        t = test.Test()
        c= t.controller('main')
        string = 'show running-config bigtap |  grep l3-l4 | wc -l '
        c.cli(string)
        content = c.cli_content()
        lines = content.split('\r\n')
        helpers.log("***** lines: %s" % lines)
        if int(lines[1]) == 0:
            helpers.log("INFO: the l3_l4  NOT configured" )  
            return "False"
        elif int(lines[1]) == 1:
            helpers.log("INFO: the l3_l4 configured" )    
            return "True"     
        else:
            helpers.test_failure(c.rest.error())         
            return False

    def cli_show_trackhost(self):
        t = test.Test()
        c= t.controller('main')
        string = 'show running-config bigtap |  grep trackhost | wc -l '
        c.cli(string)
        content = c.cli_content()
        lines = content.split('\r\n')
        helpers.log("***** lines: %s" % lines)
        if int(lines[1]) == 0:
            helpers.log("INFO: the trackhost Not configured" )  
            return "False"
        elif int(lines[1]) == 1:
            helpers.log("INFO: the trackhost  configured" )    
            return "True"     
        else:
            helpers.test_failure(c.rest.error())         
            return False


    def cli_show_bigtap_policy(self):
        t = test.Test()
        c= t.controller('main')
        string = 'show running-config bigtap policy'
        c.cli(string)
        content = c.cli_content()
        return content


 
 
    def rest_show_feature(self, feature="l3-l4-mode"):
        """ verify bigtap mode: l3_l4 and inport_mask
            -- Mingtao
        """
        t = test.Test()
        c= t.controller('main')
        
        url = '/api/v1/data/controller/applications/bigtap/info'  
        c.rest.get(url)

        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
            return False 
        data = c.rest.content()
        if not data[0][feature]:
            helpers.test_log("INFO: ***********Bigtap does not have the %s shown *******"  % feature)           
            return "False"
        helpers.test_log("INFO: Bigtap reports feature: %s  -  as: %s " % (feature,data[0][feature]))
        return str(data[0][feature])
        
         

    def verify_switch_tcam_max(self, node=None, l3_l4_mode=None):
        """ verify the switch tcam size
            Usage:  verify_switch_tcam   S203    L3_l4_mode= True
            -- Mingtao
        """   
        t = test.Test()
        s = t.switch(node) 
        bigtap = BigTap.BigTap()
        node_type =  s.info('model')
        size = bigtap.rest_show_switch_flow(node=node, return_value='maximum-entries')
                 
        if l3_l4_mode == "True":           
            if node_type == 'LB9':
                if size == 4088:
                    helpers.test_log("INFO: Switch  - %s  type - %s  and - L3-l4 mode, tcam size - %s " % (node, node_type, str(size)))  
                    return True
                else:
                    helpers.test_log("ERROR: Switch - %s  type - %s  and - L3-l4 mode, tcam size expect - 4088, actual - %s " % (node, node_type, str(size)))  
                    return False  
            elif node_type == 'LY2':
                if size == 2040:
                    helpers.test_log("INFO: Switch  - %s  type - %s  and - L3-l4 mode, tcam size - %s " % (node, node_type, str(size)))  
                    return True
                else:
                    helpers.test_log("ERROR: Switch - %s  type - %s  and - L3-l4 mode, tcam size expect - 4088, actual - %s " % (node, node_type, str(size)))  
                    return False  
                          
        else:
            if node_type == 'LB9':
                if size == 2044:
                    helpers.test_log("INFO: Switch  - %s  type - %s  and - L3-l4 mode, tcam size - %s " % (node, node_type, str(size)))  
                    return True
                else:
                    helpers.test_log("ERROR: Switch - %s  type - %s  and - L3-l4 mode, tcam size expect - 4088, actual - %s " % (node, node_type, str(size)))  
                    return False  
            elif node_type == 'LY2':
                if size == 1020:
                    helpers.test_log("INFO: Switch  - %s  type - %s  and - L3-l4 mode, tcam size - %s " % (node, node_type, str(size)))  
                    return True
                else:
                    helpers.test_log("ERROR: Switch - %s  type - %s  and - L3-l4 mode, tcam size expect - 4088, actual - %s " % (node, node_type, str(size)))  
                    return False  
           
        return True
 
 

    def verify_switch_tcam_limitaion(self, node,policy, match_type='mixed',base='10.0.0.0',step='0.1.0.1',v6base='1001:0:0:0:0:0:0:0',v6step='0:0:1:0:1:0:0:0'):
        """ verify the switch tcam flow limitaion 
            Usage:  verify_switch_tcam   S203    type
                    type - 'ipv4'   'ipv6'   mixed
            return:  the tcam flow entries
            -- Mingtao
        """   
        t = test.Test()
        c = t.controller('main') 
        bigtap = BigTap.BigTap()    
        i = 0
        sequence = 0
        expect_flow = 0     
        ether_type = []
        if match_type == 'ipv4':    
            ether_type.extend(['2048'])  
            v6Flag = None
            v4Flag = True                      
        elif match_type == 'ipv6':     
            ether_type.extend(['34525'])  
            v6Flag = True
            v4Flag = None                                
        else:
            ether_type.extend(['2048'])              
            ether_type.extend(['34525'])   
            v6Flag = True
            v4Flag = True                                                                             
        
        for num in ['100','20','5','1']:      
            if v4Flag is not None:
                v4Flag = True
            if v6Flag is not None:
                v6Flag = True     
            while v4Flag or v6Flag:        
                i = i + 1      
                g_size = int(num)      
                if match_type == 'ipv4' or match_type == 'mixed' :                            
                    name = 'G_'+str(i)+'_'+num
                    bigtap.rest_add_address_group(name,'ipv4')                
                    bigtap.gen_add_address_group_entries(name,'ipv4',base,step, '255.255.255.255', g_size)
                    base = helpers.get_next_address('ipv4', base,'5.0.0.0')    
                if match_type == 'ipv6' or match_type == 'mixed' :                            
                    name6 = 'G6_'+str(i)+'_'+num
                    bigtap.rest_add_address_group(name6,'ipv6')                
                    bigtap.gen_add_address_group_entries(name6,'ipv6',v6base,v6step, 'FFFF:FFFF:FFFF:FFFF:FFFF:FFFF:FFFF:FFFF', g_size)
                    v6base = helpers.get_next_address('ipv6', v6base,'11:0:0:0:0:0:0:0')  
                                   
                for loop in range(0,8):  
                    if not v4Flag and not v6Flag:
                        helpers.log("INFO:  ********* break of of the loop *****"   )                       
                        break                                                                                        
                    for ether in ether_type:
                        if ether == '2048':
                            Gname = name
                            if not v4Flag:
                                continue 
                        elif ether == '34525':
                            Gname = name6
                            if not v6Flag:
                                continue 
                            
                        sequence = sequence + 10                                                       
                        if loop == 0:                
                            data = '{'+'"sequence":'+ str(sequence) +','+'"src-ip-list":'+'"'+Gname+'"'+','+'"ether-type":'+ ether+'}' 
                        elif loop == 1:
                            data = '{'+'"sequence":'+ str(sequence) +','+'"dst-ip-list":'+'"'+Gname+'"'+','+'"ether-type":'+ ether+'}'    
                        elif loop == 2:
                            data = '{'+'"sequence":'+ str(sequence) +','+'"src-ip-list":'+'"'+Gname+'"'+','+'"ip-proto": 6,'+'"src-tp-port":80,'+'"ether-type":'+ ether+'}' 
                        elif loop == 3:
                            data = '{'+'"sequence":'+ str(sequence) +','+'"src-ip-list":'+'"'+Gname+'"'+','+'"ip-proto": 6,'+'"dst-tp-port":100,'+'"ether-type":'+ ether+'}' 
                        elif loop == 2:
                            data = '{'+'"sequence":'+ str(sequence) +','+'"dst-ip-list":'+'"'+Gname+'"'+','+'"ip-proto": 6,'+'"src-tp-port":120,'+'"ether-type":'+ ether+'}' 
                        elif loop == 3:
                            data = '{'+'"sequence":'+ str(sequence) +','+'"dst-ip-list":'+'"'+Gname+'"'+','+'"ip-proto": 6,'+'"dst-tp-port":140,'+'"ether-type":'+ ether+'}' 
                        elif loop == 4:
                            data = '{'+'"sequence":'+ str(sequence) +','+'"src-ip-list":'+'"'+Gname+'"'+','+'"ip-proto": 17,'+'"dst-tp-port":160,'+'"ether-type":'+ ether+'}' 
                        elif loop == 5:                        
                            data = '{'+'"sequence":'+ str(sequence) +','+'"src-ip-list":'+'"'+Gname+'"'+','+'"ip-proto": 17,'+'"src-tp-port":200,'+'"ether-type":'+ ether+'}'                                                                                                                                                                                                          
                        elif loop == 6:
                            data = '{'+'"sequence":'+ str(sequence) +','+'"dst-ip-list":'+'"'+Gname+'"'+','+'"ip-proto": 17,'+'"dst-tp-port":240,'+'"ether-type":'+ ether+'}' 
                        else:                        
                            data = '{'+'"sequence":'+ str(sequence) +','+'"dst-ip-list":'+'"'+Gname+'"'+','+'"ip-proto": 17,'+'"src-tp-port":280,'+'"ether-type":'+ ether+'}'                                                                                                                      
                    
                                                                                                                                  
                        helpers.log("INFO:  ********* data is  %s*****"  % data)
                        if not bigtap.rest_add_policy_match('admin-view', policy, sequence, data):  
                            helpers.test_failure(c.rest.error())                               
                              
                        expect_flow =  expect_flow + g_size   
                                                                                 
                        helpers.sleep(30)      
                        flow = bigtap.rest_show_switch_flow(node=node )
                        if flow == expect_flow:
                            helpers.test_log("INFO: Switch - %s  tcam entry - %s" % (node,  str(flow)))                                                                                    
                        elif  flow == 0:
                            helpers.test_log("ERROR: Switch - %s  tcam expect -  %s,  actual - %s" % (node, str(expect_flow), str(flow)))  
                            if not bigtap.rest_delete_policy_match('admin-view', policy,sequence):  
                                helpers.test_failure(c.rest.error())                                         
                            expect_flow =  expect_flow - g_size  
                            helpers.sleep(60)      
                            flow = bigtap.rest_show_switch_flow(node=node)       
                            if flow == expect_flow:  
                                if ether == '2048':              
                                    v4Flag = False   
                                elif ether == '34525':              
                                    v6Flag = False          
                                helpers.test_log("INFO: ****Finished group - %s type - %s entries - %s ***" % (num, str(ether), str(expect_flow)) )                                             

                                if num == '1' and not v4Flag and not v6Flag:    
                                    helpers.test_log("INFO: **** # of flows is switch  - %s ***" %  str(flow))                                 
                                    return  expect_flow                                                                                                                                                                      
                                continue
                            else:  
                                helpers.test_failure("ERROR: mismatch  Switch - %s  tcam expect -  %s,  actual - %s" % (node, str(expect_flow), str(flow)))                                                                  
                        else:
                            helpers.test_log("ERROR: Switch - %s  tcam expect -  %s,  actual - %s" % (node, str(expect_flow), str(flow)))  
                            helpers.test_failure("ERROR: mismatch  Switch - %s  tcam expect -  %s,  actual - %s" % (node, str(expect_flow), str(flow)))     



         



