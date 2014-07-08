import autobot.helpers as helpers
import autobot.test as test
import re
import keywords.T5 as T5
import keywords.T5Platform as T5Platform 
import keywords.T5L3 as T5L3
import keywords.BsnCommon as BsnCommon


 
class T5_longevity(object):
# This is for all the common function   - Mingtao
    def __init__(self):
        pass


################  start of commit #############
    def rest_add_tenant_vns_scale(self, tenantcount='1', tname='T', tenant_create=None,
                                        vnscount='1',  vname='V', vns_create='yes',
                                        vns_ip=None, base="100.0.0.100", step="0.1.0.0", mask="24" 
                                        ):
        '''
        Function to add l3 endpoint to all created vns
        Input: tennat , switch , interface
        The ip address is taken from the logical interface, the last byte is modified to 253
        output : will add end into all vns in a tenant 
        '''

        t = test.Test()
        c = t.controller('master')         
 
        t5 = T5.T5() 
        l3 = T5L3.T5L3()           
        helpers.test_log("Entering ==> rest_add_tenant_vns_scale " )  
                
        for count in range(0,int(tenantcount)):
            tenant = tname+str(count)
            
            if tenant_create == 'yes':
                if not t5.rest_add_tenant(tenant):      
                    helpers.test_failure("USER Error: tenant is NOT configured successfully")           
            elif  tenant_create is None:                 
                if (re.match(r'None.*', self.cli_show_tenant(tenant))):                              
                    helpers.test_log("tenant: %s  does not exist,  creating tenant" )      
                    if not t5.rest_add_tenant(tenant):      
                        helpers.test_failure("USER Error: tenant is NOT configured successfully")   
                                                
            if vns_create == 'yes' :  
                helpers.test_log("creating tenant L2 vns" )            
                if not t5.rest_add_vns_scale(tenant, vnscount,vname):
                    helpers.test_failure("USER Error: VNS is NOT configured successfully for tenant %s" % tenant)  
            if vns_ip is not None:
                i = 1
                while  (i<=int(vnscount)):
                    vns=vname + str(i)
                    l3.rest_add_router_intf(tenant, vns)
                    if not l3.rest_add_vns_ip(tenant,vns,base,mask): 
                        helpers.test_failure("USER Error: VNS is NOT configured successfully for tenant %s" % tenant) 
                    ip_addr  = helpers.get_next_address('ipv4', base, step)
                    base = ip_addr 
                    i = i + 1                                 
            content = c.cli('show running-config tenant')['content']                       
            
        return True

                   
        
 






    def cli_show_tenant(self, tenant):
        '''
        show tenant
        Input: tenant  
        Output:  
        Author: Mingtao
        '''
        t = test.Test()
        c = t.controller('master')         
        cli= 'show tenant ' + tenant
        content = c.cli(cli)['content']    
        temp = helpers.strip_cli_output(content)        
        return temp

    def cli_show_vns(self, tenant,vns):
        '''
        show tenant
        Input: tenant  
        Output:  
        Author: Mingtao
        '''
        t = test.Test()
        c = t.controller('master')   
       
        cli= 'show tenant ' + tenant + ' segment ' + vns
        content = c.cli(cli)['content']    
        temp = helpers.strip_cli_output(content)        
        return temp


                   
 
    def console_switch_copy_config_start(self, node,password='adminadmin'):
        """
        config given node (switch)

        Inputs:
        | node | Alias of the node to use |
        | config|  config string

        Return Value:
        - True
        """
        t = test.Test()
        s = t.dev_console(node, modeless=True)
        s.send("\r")
        options = s.expect([r'[\r\n]*.*login:', s.get_prompt()],
                           timeout=300)
        if options[0] == 0: #login prompt
            s.send('admin')
            options = s.expect([ r'[Pp]assword:', s.get_prompt()])
            if options[0] == 0:
                helpers.log("Logging in as admin with password %s" % password)
                s.cli(password)
        s.cli('enable')
        s.send('copy running-config startup-config')
        helpers.log(s.cli('')['content'])
        return True

 
    def cli_show_endpoint_pattern(self,pattern):
        '''
        '''
        helpers.test_log("Entering ==> cli_show_endpoint_filter: %s"  % pattern)           
        t = test.Test()
        c = t.controller('master')         
        cli= 'show endpoint | grep ' + pattern + ' | wc -l'
        content = c.cli(cli)['content']   
        temp = helpers.strip_cli_output(content)        
        return temp
    
    def cli_get_links_nodes(self,node1, node2):
        '''
        '''
        helpers.test_log("Entering ==> cli_get_links_nodes: %s  - %s"  %( node1, node2) )           
        t = test.Test()
        c = t.controller('master')         
        cli= 'show link | grep ' + node1 + ' | grep ' + node2  
        content = c.cli(cli)['content']   
        temp = helpers.strip_cli_output(content, to_list=True)  
        helpers.log("INFO: *** output  *** \n  %s" %temp)             
        linkinfo = {}  
        linkinfo[node1]={}
        linkinfo[node2]={}
          
        for line in temp:          
            line = line.lstrip()
            fields = line.split()
            helpers.log("fields: %s" % fields)
            N1 = fields[1]
            N2 = fields[3]
            match = re.match(r'.*-(.*)',fields[2])
            intf1= match.group(1)
            match  = re.match(r'.*-(.*)',fields[4])
            intf2= match.group(1)
           
            linkinfo[N1][intf1]= {}
            linkinfo[N1][intf1]['name']=  intf1          
            linkinfo[N1][intf1]['nbr']= N2
            linkinfo[N1][intf1]['nbr-intf']= intf2

            linkinfo[N2][intf2]= {}
            linkinfo[N2][intf2]['name']=  intf2          
            linkinfo[N2][intf2]['nbr']= N1
            linkinfo[N2][intf2]['nbr-intf']= intf1
  
                  
        helpers.log("INFO: *** link info *** \n  %s" % helpers.prettify(linkinfo))  
            
        return linkinfo      



    def spawn_log_in(self,sessions):
       
        bsn =  BsnCommon.BsnCommon()    
        helpers.log("***Etnering==> spawn_log_in   \n" )
        
        t = test.Test()
        ip = bsn.get_node_ip('master')
  
        for _ in range (0, int(sessions)):     
            n = t.node_spawn(ip)                    
            content= n.cli('show session')
            
        helpers.log("***Entering==> spawn_log_in   \n" )

        return True

    def check_controller(self):
       
        bsn =  BsnCommon.BsnCommon()    
        helpers.log("***Etnering==> spawn_log_in   \n" )
        num = bsn.get_all_controller_nodes()       
              
        helpers.log("*there are %d of controller   \n" % len(num) )

        return True


 