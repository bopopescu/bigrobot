import autobot.helpers as helpers
import autobot.test as test
import re
import keywords.T5 as T5
 
class T5_longevity(object):
# This is for all the common function   - Mingtao
    def __init__(self):
        pass


################  start of commit #############
    def console_boot_factory_default(self, node, timeout=360):
        """
        Runs boot factory-default from console, the can be used when controller is setup using dhcp 
        
        not working for expect 
        """
        
        t = test.Test()
        n = t.node(node)
        helpers.log("Entering ===> console_boot_factory_default: '%s'" % node)
        helpers.log("Getting the console session for '%s'" % node)
        n_console = n.console()
        helpers.summary_log('BVS boot factory may take a bit of time. Setting timeout to %s seconds.' % timeout)
        '''
        # vui-bvs> enable
        # vui-bvs# boot factory-default
        # boot factory default: will over-write the alternate partition
        # proceed ("yes" or "y" to continue): y
        # boot factory default: loading image into stage partition
        # boot factory default: checking integrity of new partition
        # boot factory default: New Partition Ready
        # factory default: ready for reboot
        # boot factory default: reboot? ("yes" or "y" to continue): y
        #
        # Broadcast message from root@blah
        #    (unknown) at 20:32 ...
        #
        # The system is going down for reboot NOW!
        # Connection to 10.192.104.2 closed by remote host.
        # Connection to 10.192.104.2 closed.
        n_console.expect(r'Escape character.*[\r\n]')
        n_console.send('')  # press <Enter> and expect to see the login prompt

        # We might be in midst of a previously failed first boot setup.
        # Interrupt it (Control-C) and press <Enter> to log out...
        '''
        n_console.send(helpers.ctrl('c'))
        helpers.sleep(2)
        n_console.send('')
        helpers.sleep(2)        
        n_console.send('')       
        options = n_console.expect([r'Big Virtual Switch Appliance.*[\r\n]', r'.*> '])   
        if options[0] =='0':
            n_console.expect(r'.*login: ')
            n_console.send('admin')
            n_console.expect(r'[Pp]assword: ')
            n_console.send('adminadmin')
            n_console.expect(r'[#>] ')
        
        n_console.send('enable')
        n_console.expect('#')
        n_console.send('boot factory-default')
        n_console.expect(r'proceed \("yes" or "y" to continue\)')
        n_console.send('y')
        n_console.expect(r'loading image into stage partition', timeout=timeout)
        n_console.expect(r'checking integrity of new partition', timeout=timeout)
        n_console.expect(r'New Partition Ready', timeout=timeout)
        n_console.expect(r'ready for reboot', timeout=timeout)
        n_console.expect(r'"yes" or "y" to continue\): ', timeout=timeout)
        n_console.send('y')
        
        helpers.summary_log("'%s' has been rebooted." % node)
        helpers.log("Boot factory-default completed on '%s'. System should be rebooting." % node)
        return True
  
  
    def first_boot_controller_initial_node_setup(self,
                           node,
                           dhcp = 'no',
                           ip_address=None,
                           netmask='18',
                           gateway='10.192.64.1',
                           dns_server='10.192.3.1',
                           dns_search='bigswitch.com',                          
                           hostname='MY-T5-C',                           
                            ):
        """
        First boot setup fpr BVS - It will then connect to the console to
        complete the first-boot configuration steps (call
        'cli add first boot').
        """
        t = test.Test()
        n = t.node(node)

        if not ip_address:
            ip_address = n.ip()

        helpers.log("Getting the console session for '%s'" % node)
        n_console = n.console()

        options = n_console.expect([r'Escape character.*[\r\n]', r'login:',r'Local Node Configuration'])
        print("*****USER INFO:  options is ****\n %s" % (options,))        
        content = n_console.content()
        helpers.log("*****Output is :*******\n%s" % content)
        if options[0]<2:
            if options[0] == 0 :
                helpers.log("USER INFO:  need to Enter " )
                n_console.send('')   
                n_console.send(helpers.ctrl('c'))
                helpers.sleep(2)
                n_console.send('')
                n_console.expect(r'Big Virtual Switch Appliance.*[\r\n]')
                n_console.expect(r'login:')            
            elif options[0] == 1:
                helpers.log("INFO:  need to login as  admin" )        
            n_console.send('admin')
            n_console.expect(r'Do you accept the EULA.* > ')
            n_console.send('Yes')
            n_console.expect(r'Local Node Configuration')
        
        n_console.expect(r'Password for emergency recovery user > ')
        n_console.send('bsn')
        n_console.expect(r'Retype Password for emergency recovery user > ')
        n_console.send('bsn')
        n_console.expect(r'Please choose an IP mode:.*[\r\n]')
        n_console.expect(r'> ')
        if dhcp == 'no':
            n_console.send('1')  # Manual
            n_console.expect(r'IP address .* > ')
            n_console.send(ip_address)
    
            if not re.match(r'.*/\d+', ip_address):
                # Send netmask if IP address doesn't contain prefix length
                n_console.expect(r'CIDR prefix length .* > ')
                n_console.send(netmask)
    
            n_console.expect(r'Default gateway address .* > ')
            n_console.send(gateway)
            n_console.expect(r'DNS server address .* > ')
            n_console.send(dns_server)
            n_console.expect(r'DNS search domain .* > ')
            n_console.send(dns_search)
            n_console.expect(r'Hostname > ')
            n_console.send(hostname)
        else:
            # dhcp 
            n_console.send('2')  #DHCP
    
        return True
    
    def first_boot_controller_initial_cluster_setup(self,
                           node,
                           join_cluster = 'no',
                           cluster_ip ='',
                           cluster_passwd='adminadmin',
                           cluster_name='T5cluster',
                           cluster_descr='T5cluster',
                           admin_password='adminadmin',
                           ntp_server='',
                           ):
        """
        First boot setup fpr BVS - It will then connect to the console to
        complete the first-boot configuration steps (call
        'cli add first boot').
        """

  
        t = test.Test()
        n = t.node(node)
 
        helpers.log("Getting the console session for '%s'" % node)
        n_console = n.console()        
        n_console.expect(r'Controller Clustering')
        n_console.expect(r'> ')
        
        if join_cluster == 'yes':
            n_console.send('2')  # join existing cluster     
            n_console.expect(r'Existing node IP.*> ')
            n_console.send(cluster_ip)     
            n_console.expect(r'Administrator password for cluster.*> ')
            n_console.send(cluster_passwd)     
            n_console.expect(r'Retype Administrator password for cluster.*> ')
            n_console.send(cluster_passwd)     
        else:      
            n_console.send('1')  # Start a new cluster
            n_console.expect(r'Cluster name > ')
            n_console.send(cluster_name)
            n_console.expect(r'Cluster description .* > ')
            n_console.send(cluster_descr)
            n_console.expect(r'Administrator password for cluster > ')
            n_console.send(admin_password)
            n_console.expect(r'Retype .* > ')
            n_console.send(admin_password)    
            n_console.expect(r'System Time')
            n_console.expect(r'Enter NTP server .* > ')
            n_console.send(ntp_server)
            
 
        helpers.log("USER INFO:  Please choose an option"  )
                
        return True

    def first_boot_controller_menu_apply(self,node):
        """
        menu   1
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
          
        n_console.expect(r'IP address on eth0 is (.*)[\r\n]')
        content = n_console.content()
     
        helpers.log("content is:  %s" % content)              
        match = re.search(r'IP address on eth0 is (.*)[\r\n]', content)
        new_ip_address = match.group(1)
        helpers.log("new_ip_address: %s" % new_ip_address)  
                     
        n_console.expect(r'Configuring cluster.*[\r\n]')
        n_console.expect(r'First-time setup is complete.*[\r\n]')
        n_console.expect(r'Press enter to continue > ')
        n_console.send('')
        #helpers.log("Closing console connection for '%s'" % node)
        n.console_close()

        helpers.sleep(3)  # Sleep for a few seconds just in case...
        return new_ip_address

     
    def first_boot_controller(self, node,
                           join_cluster = 'no',
                           dhcp='no',
                           ip_address=None,
                           netmask='18',
                           gateway='10.192.64.1',
                           dns_server='10.92.3.1',
                           dns_search='bigswitch.com',                          
                           hostname='MY-T5-C',                           
                           cluster_ip ='',
                           cluster_passwd='adminadmin',
                           cluster_name='T5cluster',
                           cluster_descr='T5cluster',
                           admin_password='adminadmin',
                           platform='bvs',
                           ntp_server='',
                        ):
        
        """
        First boot setup fpr BVS - It will then connect to the console to
        complete the first-boot configuration steps (call
        'cli add first boot').
        """ 
        helpers.log("Entering ====>  first_boot_controller node:'%s' " % node)
        
        self.first_boot_controller_initial_node_setup(node,dhcp,ip_address,netmask)
        self.first_boot_controller_initial_cluster_setup(node,join_cluster,cluster_ip )        
        new_ip_address = self.first_boot_controller_menu_apply(node)
        helpers.sleep(3)  # Sleep for a few seconds just in case...
        loss = helpers.ping(new_ip_address)
        if loss < 50:
            helpers.log("Node '%s' has survived first-boot!" % node)
            return True
        else:
            return False
        
        
        
    def first_boot_controller_menu_recovery(self,node,passwd='bsn'):
        """  menu   3
        """
        t = test.Test()
        n = t.node(node)
        helpers.log("Entering ====>  Update Emergency Recovery Password for node: '%s'" % node)
        helpers.log("Getting the console session for '%s'" % node)
        n_console = n.console()
        n_console.expect(r'\[1\] > ')            
        content = n_console.content()
        helpers.log("USER INFO: the content is '%s'" % content) 
        match = re.search(r'\[\s*(\d+)\] Update Emergency Recovery Password.*[\r\n$]', content)
        if match:
            option = match.group(1)
            helpers.log("USER INFO: the optin is %s" % option) 
        else:
            helpers.log("USER ERROR: there is no match" )             
            return False       
        if option != '3':
            helpers.summary_log("choice %s not 2" % option)                        
        n_console.send(option)  # Apply settings            
        n_console.expect(r'Password for emergency recovery user > ')
        n_console.send(passwd)
        n_console.expect(r'Retype Password for emergency recovery user > ')
        n_console.send(passwd)
        n_console.expect(r'Please choose an option:.*[\r\n$]')   
       
        helpers.sleep(3)  # Sleep for a few seconds just in case...
        return True
    
    def first_boot_controller_menu_IP(self,node,ip_addr,netmask='24',invalid_input=False):
        """
        menu   5
        """
        t = test.Test()
        n = t.node(node)
        helpers.log("Entering ====> Update Local IP Address for node: '%s'" % node)
        helpers.log("Getting the console session for '%s'" % node)
        n_console = n.console()
        options = n_console.expect([r'\[1\] > ', r'IP address .* >'])                                     
        content = n_console.content()
        helpers.log("USER INFO: the content is '%s'" % content) 
        if options[0] == 0:   
            match = re.search(r'\[\s*(\d+)\] Update Local IP Address.*[\r\n$]', content)
            if match:
                option = match.group(1)
                helpers.log("USER INFO: the optin is %s" % option) 
            else:
                helpers.log("USER ERROR: there is no match" )             
                return False                 
            if option != '5':
                helpers.summary_log("choice %s not 5" % option)      
            n_console.send(option)  # Apply settings            
            n_console.expect(r'IP address .* > ')
        n_console.send(ip_addr)
        if invalid_input:
            helpers.log("USER INFO: in invalid input,  this is negative case" ) 
            n_console.expect(r'Error:.*')  
            return True                                  
        else:
            n_console.expect(r'Please choose an option:.*[\r\n$]')   
       
        if not re.match(r'.*/\d+', ip_addr):
            # to make sure the next table has CIDR entry
            n_console.expect(r'\[1\] > ') 
            content = n_console.content()
            helpers.log("USER INFO: the content is '%s'" % content) 
            match = re.search(r'\[\s*(\d+)\] Update CIDR Prefix Length.*[\r\n$]', content)
            if match:
                option = match.group(1)
                helpers.log("USER INFO: the option is %s" % option) q
            else:
                helpers.log("USER ERROR: there is no match" )             
                return False                 
            n_console.send(option)  # Apply settings            
            n_console.expect(r'CIDR prefix length \[24\].* > ')
            n_console.send(netmask)
        helpers.sleep(3)  # Sleep for a few seconds just in case...          
        return True


    def first_boot_controller_menu_prefix(self,node,netmask,invalid_input=False):
        """
        menu   6
        """
        t = test.Test()
        n = t.node(node)
        helpers.log("Entering ====> Update CIDR Prefix Length for node: '%s'" % node)
        helpers.log("Getting the console session for '%s'" % node)
        n_console = n.console()
         
        options = n_console.expect([r'\[1\] > ', r'CIDR prefix length.* >'])    
        content = n_console.content()      
        helpers.log("USER INFO: the content:  %s" % content)        
        if options[0] == 0:   
            match = re.search(r'\[\s*(\d+)\] Update CIDR Prefix Length.*[\r\n$]', content)
            if match:
                option = match.group(1)
                helpers.log("USER INFO: the option is %s" % option) 
            else:
                helpers.log("USER ERROR: there is no match" )             
                return False                 
            n_console.send(option)  # Apply settings            
            n_console.expect(r'CIDR prefix length \[24\].* > ')
        n_console.send(netmask)
        if invalid_input:
            helpers.log("USER INFO: in invalid input,  this is negative case" ) 
            n_console.expect(r'Error:.*')                                    
        else:
            n_console.expect(r'Please choose an option:.*[\r\n$]')   
                
        helpers.sleep(3)  # Sleep for a few seconds just in case...          
        return True




    def first_boot_controller_menu_gateway(self,node,gateway):
        """
        menu   6
        """
        t = test.Test()
        n = t.node(node)
        helpers.log("Entering ====> Update Gateway for node: '%s'" % node)
        helpers.log("Getting the console session for '%s'" % node)
        n_console = n.console()
        n_console.expect(r'\[1\] > ')                
        content = n_console.content()
        helpers.log("USER INFO: the content is '%s'" % content) 
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
        n_console.expect(r'Please choose an option:.*[\r\n$]')    
          
        helpers.sleep(3)  # Sleep for a few seconds just in case...
        return True
    
    def first_boot_controller_menu_dnsserver(self,node,dnsserver,invalid_input=False):
        """
        menu   7
        """
        t = test.Test()
        n = t.node(node)
        helpers.log("Entering ====> Update DNS Server for node: '%s'" % node)
        helpers.log("Getting the console session for '%s'" % node)
        n_console = n.console()
        
        options = n_console.expect([r'\[1\] > ', r'DNS server address.* >'])    
        content = n_console.content()      
        helpers.log("USER INFO: the content:  %s" % content)        
        if options[0] == 0:   
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
            
        n_console.send(dnsserver)
        if invalid_input:
            helpers.log("USER INFO: in invalid input,  this is negative case" ) 
            n_console.expect(r'Error: Invalid.*')                                    
        else:
            n_console.expect(r'Please choose an option:.*[\r\n$]')   
          
        helpers.sleep(3)  # Sleep for a few seconds just in case...
        return True

    def first_boot_controller_menu_domain(self,node,domain):
        """
        menu   8
        """
        t = test.Test()
        n = t.node(node)
        helpers.log("Entering ====> Update DNS Search Domain for node: '%s'" % node)
        helpers.log("Getting the console session for '%s'" % node)
        n_console = n.console()
        n_console.expect(r'\[1\] > ')                
        content = n_console.content()
        helpers.log("USER INFO: the content is '%s'" % content) 
        match = re.search(r'\[\s*(\d+)\] Update DNS Search Domain.*[\r\n$]', content)
        if match:
            option = match.group(1)
            helpers.log("USER INFO: the optin is %s" % option) 
        else:
            helpers.log("USER ERROR: there is no match" )             
            return False                 
        n_console.send(option)  # Apply settings    
        n_console.expect(r'DNS Search Domain.*')                
        n_console.expect(r'DNS search domain.* > ')
        n_console.send(domain)
        n_console.expect(r'Please choose an option:.*[\r\n$]')   
          
        helpers.sleep(3)  # Sleep for a few seconds just in case...
        return True
     
    def first_boot_controller_menu_name(self,node,name):
        """
        menu   9
        """
        t = test.Test()
        n = t.node(node)
        helpers.log("Entering ====> Update Hostname for node: '%s'" % node)
        helpers.log("Getting the console session for '%s'" % node)
        n_console = n.console()
        n_console.expect(r'\[1\] > ')                
        content = n_console.content()
        helpers.log("USER INFO: the content is '%s'" % content) 
        match = re.search(r'\[\s*(\d+)\] Update Hostname.*[\r\n$]', content)
        if match:
            option = match.group(1)
            helpers.log("USER INFO: the optin is %s" % option) 
        else:
            helpers.log("USER ERROR: there is no match" )             
            return False                 
      
        n_console.send(option)  # Apply settings    
        n_console.expect(r'Hostname.*')                
        n_console.expect(r'Hostname.* > ')
        n_console.send(name)
        n_console.expect(r'Please choose an option:.*[\r\n$]')   
          
        helpers.sleep(3)  # Sleep for a few seconds just in case...
        return True
            
    def first_boot_controller_menu_cluster_name(self,node,name='MY-T5-C'):
        """
        menu   13
        """
        t = test.Test()
        n = t.node(node)
        helpers.log("Entering ====> Update Cluster Name for node: '%s'" % node)
        helpers.log("Getting the console session for '%s'" % node)
        n_console = n.console()
        n_console.expect(r'\[1\] > ')                
        content = n_console.content()
        helpers.log("USER INFO: the content is '%s'" % content) 
        match = re.search(r'\[\s*(\d+)\] Update Cluster Name.*[\r\n$]', content)
        if match:
            option = match.group(1)
            helpers.log("USER INFO: the optin is %s" % option) 
        else:
            helpers.log("USER ERROR: there is no match" )             
            return False                 
        n_console.send(option)  # Apply settings    
        n_console.expect(r'Cluster Name.*')                
        n_console.expect(r'Cluster name.* > ')
        n_console.send(name)
        n_console.expect(r'Please choose an option:.*[\r\n$]')   
          
        helpers.sleep(3)  # Sleep for a few seconds just in case...
        return True
 
    def first_boot_controller_menu_cluster_desr(self,node,descr='MY-T5-C'):
        """
        menu   13
        """
        t = test.Test()
        n = t.node(node)
        helpers.log("Entering ====> Update Cluster Description for node: '%s'" % node)
        helpers.log("Getting the console session for '%s'" % node)
        n_console = n.console()
        n_console.expect(r'\[1\] > ')                
        content = n_console.content()
        helpers.log("USER INFO: the content is '%s'" % content) 
        match = re.search(r'\[\s*(\d+)\] Update Cluster Description.*[\r\n$]', content)
        if match:
            option = match.group(1)
            helpers.log("USER INFO: the optin is %s" % option) 
        else:
            helpers.log("USER ERROR: there is no match" )             
            return False                 
        n_console.send(option)  # Apply settings    
        n_console.expect(r'Cluster Description.*')                
        n_console.expect(r'Cluster description.* > ')
        n_console.send(descr)
        n_console.expect(r'Please choose an option:.*[\r\n$]')   
          
        helpers.sleep(3)  # Sleep for a few seconds just in case...
        return True
    
    def first_boot_controller_menu_cluster_passwd(self,node,passwd='adminadmin'):
        """
        menu   13
        """
        t = test.Test()
        n = t.node(node)
        helpers.log("Entering ====> Update Cluster Admin Password  for node: '%s'" % node)
        helpers.log("Getting the console session for '%s'" % node)
        n_console = n.console()
        n_console.expect(r'\[1\] > ')                
        content = n_console.content()
        helpers.log("USER INFO: the content is '%s'" % content) 
        match = re.search(r'\[\s*(\d+)\] Update Cluster Admin Password.*[\r\n$]', content)
        if match:
            option = match.group(1)
            helpers.log("USER INFO: the optin is %s" % option) 
        else:
            helpers.log("USER ERROR: there is no match" )             
            return False                 
        n_console.send(option)  # Apply settings    
        n_console.expect(r'Cluster Admin Password.*')                
        n_console.expect(r'Administrator password for cluster.* > ')
        n_console.send(passwd)
        n_console.expect(r'Retype Administrator password for cluster.* > ')
        n_console.send(passwd)
        n_console.expect(r'Please choose an option:.*[\r\n$]')   
        helpers.sleep(3)  # Sleep for a few seconds just in case...
        return True
         