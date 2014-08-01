import autobot.helpers as helpers
import autobot.test as test
import re
import keywords.T5 as T5
import keywords.T5Platform as T5Platform 
import keywords.T5L3 as T5L3
import keywords.BsnCommon as BsnCommon
from mingtao_services import tasks as tasks

 
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
        helpers.log("***Entering==> spawn_log_in   \n" )
        
        t = test.Test()
        ip = bsn.get_node_ip('master')
  
        for loop in range (0, int(sessions)): 
            helpers.log('USR info:  this is loop:  %d' % loop )
            n = t.node_spawn(ip)                    
            content= n.cli('show session')
            
        helpers.log("***Exiting==> spawn_log_in   \n" )

        return True



    def check_controller(self):
       
        bsn =  BsnCommon.BsnCommon()    
        helpers.log("***Etnering==> spawn_log_in   \n" )
        num = bsn.get_all_controller_nodes()       
              
        helpers.log("*there are %d of controller   \n" % len(num) )

        return True

    def cli_upgrade_launch_break(self, breakpoint=None,node='master',option=''):
        '''
          upgrade launch break  -  break out of the upgrade at various point
          Author: Mingtao
          input:  node  - controller
                          master, slave, c1 c2
                option -  revert, suspend
                breakpoint - None:   no break
                            proceed:  send no   when proceed is prompt
                            upgrade:  send no   when upgrade is prompt   
                            phase1:   send ctrl c  during phase1   

          usage:
          output: True  - upgrade launched successfully
                  False  -upgrade launched Not successfully
        '''

        t = test.Test()
        c = t.controller(node)
        bsn = BsnCommon.BsnCommon()
        
        helpers.log('INFO: Entering ==> cli_upgrade_launch ')
        c.config('')
        string = 'upgrade launch ' + option
#        c.send('upgrade launch')
        c.send(string)
        c.expect(r'[\r\n].+ \("yes" or "y" to continue\):', timeout=180)
        content = c.cli_content()
        helpers.log("*****USER INFO:\n%s" % content)
        if breakpoint == 'proceed':
            c.send('no')
            helpers.log("USER INFO: terminate upgrade at proceed: %s" % node)            
            return True
        else:
            c.send("yes")
        options = c.expect([r'fabric is redundant', r'.* HITFULL upgrade \(y or yes to continue\):'])
        content = c.cli_content()
        helpers.log("USER INFO: the content:  %s" % content)
        if options[0] == 1:
            if breakpoint == 'upgrade':
                c.send("no")
                helpers.log("USER INFO: terminate upgrade at upgrade: %s" % node)                  
                return True
            else:
                c.send("yes")               

        if breakpoint is None:                
            try:
                c.expect(r'[\r\n].+[R|r]ebooting.*')
                content = c.cli_content()
                helpers.log("*****Output is :\n%s" % content)
            except:
                helpers.log('ERROR: upgrade launch NOT successfully')
                return False
            else:
                helpers.log('INFO: upgrade launch  successfully')
                return True
        else:
            #  need to split for master or standby 
            if node == 'master':
                role = 'active'
            elif node == 'slave':
                role = 'stand-by'
            else:
                role = bsn.rest_get_node_role(node)
            if role == 'active':
                helpers.log("USER INFO: %s is %s \n%s" % (node, role ))                                
                c.expect(r'waiting for standby to begin \"upgrade launch\"',timeout=360)
                c.expect(r'config updates are frozen for update',timeout=360)
                c.expect(r'standby has begun upgrade',timeout=360)
                c.expect(r'waiting for standby to complete switch handoff',timeout=360)
                c.expect(r'waiting for upgrade to complete \(remove-standby-controller-config-completed\)',timeout=360)
                c.expect(r'new state: phase-1-migrate',timeout=360)
                if breakpoint == 'phase1':
                    c.send(helpers.ctrl('c'))
                    helpers.summary_log('Ctrl C is hit during phase-1-migrate')
                    return True         
                c.expect(r'waiting for upgrade to complete \(phase-1-migrate\)',timeout=360)   
                c.expect(r'new state: phase-2-migrate',timeout=360)
                if breakpoint == 'phase2':
                    c.send(helpers.ctrl('c'))
                    helpers.summary_log('Ctrl C is hit during phase-1-migrate')
                    return True         
                c.expect(r'waiting for upgrade to complete \(phase-2-migrate\)',timeout=360)   
                c.expect(r'The system is going down for reboot NOW!',timeout=360)
                                                    
                return True         

            elif role == 'stand-by':
                c.expect(r'waiting for active to begin \"upgrade launch\"',timeout=360)
                c.expect(r'upgrader nonce',timeout=360)
                c.expect(r'Leader->begin-upgrade-old state: begin-completed',timeout=360)
                c.expect(r'Leader->partition state: partition-completed',timeout=360)
                c.expect(r'Leader->remove-standby-controller-config state: remove-standby-controller-config-completed',timeout=360)
                c.expect(r'[R|r]ebooting',timeout=360)
                
                return True
                
                
    def upgrade_copy_image_HA_parallel(self,nodes,image):
       
        helpers.log("***Entering==> upgrade_copy_image_HA_parallel   \n" )
        t = test.Test()
        
        results = []
        result_dict = {}
        task = tasks.UpgradeCommands()
        #
        # Parallel execution happens below
        #     
        for node in nodes:
            res1 = task.cli_copy_upgrade_pkg.delay(t.params(),src=image,node=node)
            results.append(res1)
            task_id = results[-1].task_id
            result_dict[task_id] = { "node": node, "action": "cli_copy_upgrade_pkg" }
  
        # Check task status - are we done yet?
        #
        
        self.task_finish_check_parallel(results,result_dict)        
        helpers.log("***Exiting==> upgrade_copy_image_HA_parallel  \n" )

        return True             
    
    def upgrade_statge_image_HA_parallel(self,nodes):
       
        helpers.log("***Entering==> upgrade_statge_image_HA_parallel   \n" )
        t = test.Test()
        
        results = []
        result_dict = {}
        task = tasks.UpgradeCommands()
        #
        # Parallel execution happens below
        #     
        for node in nodes:
            res1 = task.cli_stage_upgrade_pkg.delay(t.params(),node=node)
            results.append(res1)
            task_id = results[-1].task_id
            result_dict[task_id] = { "node": node, "action": "cli_copy_upgrade_pkg" }
  
        # Check task status - are we done yet?
        self.task_finish_check_parallel(results,result_dict)
        
        helpers.log("***Exiting==> upgrade_statge_image_HA_parallel  \n" )
       
        return True      
    
    def upgrade_launch_image_HA_parallel(self,nodes):
       
        helpers.log("***Entering==> upgrade_launch_image_HA_parallel   \n" )
        t = test.Test()
        
        results = []
        result_dict = {}
        task = tasks.UpgradeCommands()
        #
        # Parallel execution happens below
        #     
        for node in nodes:
            res1 = task.cli_launch_upgrade_pkg.delay(t.params(),node=node)
            results.append(res1)
            task_id = results[-1].task_id
            result_dict[task_id] = { "node": node, "action": "cli_copy_upgrade_pkg" }
  
        # Check task status - are we done yet?
        self.task_finish_check_parallel(results,result_dict)
        
        helpers.log("***Exiting==> upgrade_launch_image_HA_parallel  \n" )
       
        return True      
        
           
    
    def task_finish_check_parallel(self,results,result_dict):
       
        helpers.log("***Entering==> task_finish_check_parallel   \n" )
        is_pending = True
        iteration = 0
        while is_pending:
            is_pending = False
            iteration += 1
            helpers.sleep(1)
            helpers.log("USR INFO:  result is %s" %results)                             
           
            for res in results:
                task_id = res.task_id
                action = result_dict[task_id]["node"] + ' ' + result_dict[task_id]["action"]
                if res.ready() == True:
                    helpers.log("****** %d.READY     - task_id(%s)['%s']"
                                % (iteration, res.task_id, action))
                else:
                    helpers.log("****** %d.NOT-READY - task_id(%s)['%s']"
                                % (iteration, res.task_id, action))
                    is_pending = True
        helpers.log("*** Parallel tasks completed")
        
        #
        # Check task output
        #
        for res in results:
            task_id = res.task_id
            helpers.log_task_output(task_id)
            output = res.get()
            result_dict[task_id]["result"] = output
        helpers.log("***** result_dict:\n%s" % helpers.prettify(result_dict))
        return True             
    

  