import autobot.helpers as helpers
import autobot.test as test
import re
import keywords.T5 as T5
import keywords.T5Platform as T5Platform 
 
class T5_longevity(object):
# This is for all the common function   - Mingtao
    def __init__(self):
        pass


################  start of commit #############
 
    def first_boot_controller_menu_cluster_option_apply(self,node,
                           join_cluster = 'no',
                           cluster_ip ='',
                           cluster_passwd='adminadmin',
                           cluster_name='T5cluster',
                           cluster_descr='T5cluster',
                           admin_password='adminadmin',
                           ntp_server='',
                            ):
        """
       First boot setup Menu :   Update Cluster Name
        """
        t = test.Test()
        n = t.node(node)
        helpers.log("Entering ====> Update Cluster Option for node: '%s'" % node)
        Platform = T5Platform.T5Platform()
        
        helpers.log("Getting the console session for '%s'" % node)
        n_console = n.console()
        n_console.expect(r'\[1\] > ')                
        content = n_console.content()
        helpers.log("USER INFO: the content is '%s'" % content) 
        match = re.search(r'\[\s*(\d+)\] Update Cluster Option.*[\r\n$]', content)
        if match:
            option = match.group(1)
            helpers.log("USER INFO: the option is %s" % option) 
        else:
            helpers.log("USER ERROR: there is no match" )             
            return False                 
        n_console.send(option)  # Apply settings         
        n_console.expect(r'Please choose a cluster option:.*')
        n_console.expect(r'> ')
        
        if join_cluster == 'yes':
            n_console.send('2')  # join existing cluster     
            n_console.expect(r'Existing node IP.*> ')
            n_console.send(cluster_ip)     
        else:      
            n_console.send('1')  # Start a new cluster
            n_console.expect(r'Cluster name > ')
            n_console.send(cluster_name)
            n_console.expect(r'Cluster description .* > ')
            n_console.send(cluster_descr)
            n_console.expect('')
        try:
            options = n_console.expect([r'\[1\] > ', r'[^\]]> '])
        except:
            content = n_console.content()    
            helpers.log("*****Output is :*******\n%s" % content)           
            helpers.log("USER ERROR: there is no match") 
            helpers.test_failure('There is no match')
             
        else:    
            content = n_console.content()    
            helpers.log("*****Output is :*******\n%s" % content)  
       
            if options[0] == 0 :                 
                helpers.log("*****Matched   [1] > can apply setting now*******  "  )       
            elif options[0] == 1:
                helpers.log("*****Matched >  can NOT apply setting now*******  "  ) 
            
                match = re.search(r'\[\s*(\d+)\].*<NOT SET, UPDATE REQUIRED>.*[\r\n$]', content)
                if match:
                    helpers.log("USER INFO:  need to configure ntp"  )                       
                    option = match.group(1)
                    helpers.log("USER INFO: the option is %s" % option)                      
                    n_console.send(option)
                    n_console.expect(r'Enter NTP server.* > ')
                    n_console.send('')    
                    n_console.expect(r'\[1\] > ')             
                                    
            n_console.send('')  # Apply settings
            n_console.expect(r'Initializing system.*[\r\n]')
            n_console.expect(r'Configuring controller.*[\r\n]')
              
            n_console.expect(r'IP address on eth0 is (.*)[\r\n]')
            content = n_console.content()
         
            helpers.log("content is:  %s" % content)              
            match = re.search(r'IP address on eth0 is (\d+\.\d+\.\d+\.\d+).*[\r\n]', content)
            new_ip_address = match.group(1)
            helpers.log("new_ip_address: '%s'" % new_ip_address)  
                         
            n_console.expect(r'Configuring cluster.*[\r\n]')
            n_console.expect(r'First-time setup is complete.*[\r\n]')
            n_console.expect(r'Press enter to continue > ')
            n_console.send('')
            helpers.sleep(3)  # Sleep for a few seconds just in case...
            return new_ip_address
               
             
    def first_boot_controller_menu_reset(self,node):
        """
       First boot setup Menu :   reset 
        """
        t = test.Test()
        n = t.node(node)
        helpers.log("Entering ====> Reset and start over for node: '%s'" % node)
        helpers.log("Getting the console session for '%s'" % node)
        n_console = n.console()
        n_console.expect(r'\[1\] > ')                
        content = n_console.content()
        helpers.log("USER INFO: the content is '%s'" % content) 
        match = re.search(r'\[\s*(\d+)\] Reset and start over.*[\r\n$]', content)
        if match:
            option = match.group(1)
            helpers.log("USER INFO: the option is %s" % option) 
        else:
            helpers.log("USER ERROR: there is no match" )             
            return False                 
        n_console.send(option) 
  
        return True
    
    
    
    def first_boot_controller_menu_apply_negative(self,node, **kwargs):
        """
        First boot setup III: connect to the console to apply the setting. 
            this is negative, if wrong gw is given. then NTP and DNS can not be reached
        First boot setup Menu :  Apply settings
    
        Author: Mingtao       
        """
        t = test.Test()
        n = t.node(node)
        helpers.log("Entering ====>  first_boot_controller_menu_1 for node: '%s'" % node)
        helpers.log("Getting the console session for '%s'" % node)
        n_console = n.console() 
        n_console.expect(r'\[1\] > ')
        helpers.log("[1] Apply settings " )      
        content = n_console.content()
        helpers.log("USER INFO: the content is '%s'" % content) 
        match = re.search(r'\[\s*(\d+)\] Apply settings.*[\r\n$]', content)
        if match:
            option = match.group(1)
            helpers.log("USER INFO: the option is %s" % option) 
        else:
            helpers.log("USER ERROR: there is no match" )             
            return False                 
                  
        n_console.send(option)  # Apply settings
        n_console.expect(r'Initializing system.*[\r\n]')
        n_console.expect(r'Configuring controller.*[\r\n]')
        n_console.expect(r'Waiting for network configuration.*[\r\n]')        
        options=n_console.expect([r'Unable to resolve domains with DNS.*[\r\n]',r'No route to host.*[\r\n]'],timeout=300)
        if options[0] == 0:
            n_console.expect(r'Retrieving time from NTP server.*[\r\n]',timeout=120)
            n_console.expect(r'unreachable now.*[\r\n]',timeout=120)        
            n_console.expect(r'Configuring cluster.*[\r\n]',timeout=120) 
        if options[0] == 1 : 
            helpers.log("USER INFO: need to correct cluster ip") 
        try:
            options = n_console.expect([r'\[1\] >', r'First-time setup is complete.*[\r\n]'], timeout =120)    
        except:
            content = n_console.content()    
            helpers.log("*****Output is :*******\n%s" % content)           
            helpers.log("USER ERROR: there is no match") 
            helpers.test_failure('There is no match')
        else:
            content = n_console.content()    
            helpers.log("*****Output is :*******\n%s" % content)  
       
            if options[0] == 0 :                 
                helpers.summary_log("*****Need to correct parameter *******  "  )       
                if 'gateway' in kwargs:
                    gateway=kwargs.get('gateway')
                    match = re.search(r'\[\s*(\d+)\] Update Gateway.*[\r\n$]', content)
                    if match:
                        option = match.group(1)
                        helpers.log("USER INFO: the option is %s" % option) 
                    else:
                        helpers.log("USER ERROR: there is no match" )             
                        return False                 
                    n_console.send(option)  # Apply settings     
                    n_console.expect(r'Gateway.*')               
                    n_console.expect(r'Default gateway address.*> ')
                    n_console.send(gateway)
                    n_console.expect(r'\[1\] >')
                    content = n_console.content()  
                if 'dns' in kwargs:
                    dns=kwargs.get('dns')
                    match = re.search(r'\[\s*(\d+)\] Update DNS Server.*[\r\n$]', content)
                    if match:
                        option = match.group(1)
                        helpers.log("USER INFO: the option is %s" % option) 
                    else:
                        helpers.log("USER ERROR: there is no match" )             
                        return False                 
                    n_console.send(option)  # Apply settings     
                    n_console.expect(r'DNS Server.*')               
                    n_console.expect(r'DNS server address.* > ')
                    n_console.send(dns)
                    n_console.expect(r'\[1\] >')
                if 'cluster_ip' in kwargs:
                    clusterip=kwargs.get('cluster_ip')
                    match = re.search(r'\[\s*(\d+)\] Update Existing Node IP Address.*[\r\n$]', content)
                    if match:
                        option = match.group(1)
                        helpers.log("USER INFO: the option is %s" % option) 
                    else:
                        helpers.log("USER ERROR: there is no match" )             
                        return False                 
                    n_console.send(option)  # Apply settings     
                    n_console.expect(r'Existing Node IP Address.*')               
                    n_console.expect(r'Existing node IP.* > ')
                    n_console.send(clusterip)
                    n_console.expect(r'\[1\] >')
                                            
                n_console.send('')  # Apply settings
                n_console.expect(r'Initializing system.*[\r\n]',timeout=120)
                n_console.expect(r'Configuring controller.*[\r\n]',timeout=120)                              
                n_console.expect(r'Configuring cluster.*[\r\n]',timeout=120)
                n_console.expect(r'First-time setup is complete.*[\r\n]',timeout=120)
                n_console.expect(r'Press enter to continue > ')
                n_console.send('')
                helpers.sleep(3)  # Sleep for a few seconds just in case...
                return True             
               
            if options[0] == 1 :                 
                helpers.log("*****first boot complete *******  "  )   
                n_console.expect(r'Press enter to continue > ')
                n_console.send('')    
                helpers.summary_log('First boot complete even the NTP/DNS not reachable' )
        helpers.sleep(3)  # Sleep for a few seconds just in case...
        return True

    def cli_show_local_config(self,node):
        '''
        show the local node config
        '''
      
        t = test.Test()
        c = t.controller(node)
    
        c.enable('')
        c.enable("show local-config")
        content = c.cli_content()
        helpers.log("*****Output is :\n%s" % content)
        temp = helpers.strip_cli_output(content)
        temp = helpers.str_to_list(temp)
        helpers.log("*****Output list   is :\n%s" % temp)
             
        localinfo = {}    
        for line in temp:          
            line = line.lstrip()
            helpers.log(" line is - %s" % line)            
            if (re.match(r'.*hostname .*', line)): 
                match = re.match(r'.*hostname (.*)', line)        
                localinfo['hostname'] = match.group(1)
            
            elif (re.match(r'.*dns search.*', line)): 
                match = re.match(r'.*dns search (.*)', line)        
                localinfo['domain'] = match.group(1)
             
            elif (re.match(r'.*dns server.*', line)): 
                match = re.match(r'.*dns server (.*)', line)        
                localinfo['dns'] = match.group(1)
            
            elif (re.match(r'.*ip.* gateway.*', line)): 
                match = re.match(r'.*ip (\d+\.\d+\.\d+\.\d+)/(\d+) gateway (\d+\.\d+\.\d+\.\d+)', line)        
                localinfo['ip'] = match.group(1)
                localinfo['mask'] = match.group(2)
                localinfo['gateway'] = match.group(3)
             
            helpers.log("INFO: *** local node info *** \n  %s" % localinfo)      
        return localinfo      
        
  