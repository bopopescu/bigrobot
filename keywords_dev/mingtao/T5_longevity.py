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
        
  