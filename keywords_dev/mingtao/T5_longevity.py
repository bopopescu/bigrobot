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
        c = t.controller('main')         
        cli= 'show endpoint | grep ' + pattern + ' | wc -l'
        content = c.cli(cli)['content']   
        temp = helpers.strip_cli_output(content)        
        return temp
    
    def cli_get_links_nodes(self,node1, node2):
        '''
        '''
        helpers.test_log("Entering ==> cli_get_links_nodes: %s  - %s"  %( node1, node2) )           
        t = test.Test()
        c = t.controller('main')         
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
        ip = bsn.get_node_ip('main')
  
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

    def cli_upgrade_launch_break(self, breakpoint=None,node='main',option=''):
        '''
          upgrade launch break  -  break out of the upgrade at various point
          Author: Mingtao
          input:  node  - controller
                          main, subordinate, c1 c2
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
            #  need to split for main or standby 
            if node == 'main':
                role = 'active'
            elif node == 'subordinate':
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
                
                


####### no use of this one    
    def bash_get_blocked_thread(self, node):
        ''' do df in debug bash
        ouput: index:  directory  with all the field
        '''
        t = test.Test()
        n = t.node(node)
        content = n.bash('sudo jps -l')['content']
        lines = helpers.strip_cli_output(content, to_list=True) 
        helpers.log("lines: %s" % lines)
        for line in lines:
            line = line.lstrip()
            helpers.log(" line is - %s" % line) 
            if (re.match(r'(\d+) org.projectfloodlight.core.Main', line)):
                match = re.match(r'(\d+) .*projectfloodlight.*', line)
                pid = match.group(1)
                helpers.log("INFO: ***floodlight pid is \n  %s" % pid)
                break
        string = 'sudo jstack -F -l ' + pid + ' > /tmp/jstack.log'
        content = n.bash(string, timeout=3600)['content']  
        content = n.bash('cat /tmp/jstack.log | grep BLOCKED | wc -l' )['content'] 
        temp = helpers.strip_cli_output(content)
        temp = helpers.str_to_list(temp)
        helpers.log("*****Output list   is :\n%s" % temp)
        temp.pop(0)
        for line in temp:
            line = line.lstrip()
            helpers.log(" line is - %s" % line) 
            if (re.match(r'(\d+).*', line)):               
                helpers.log("INFO:blocked threads are \n  %s" % match.group(1))
                return  match.group(1)
                break        
        return True
        

  