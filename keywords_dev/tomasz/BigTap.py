import autobot.helpers as helpers
import autobot.test as test
import time



class BigTap(object):
    
    def __init__(self):
        pass


######### To Be Added #########
    def cli_configure_user(self, username, passwd=None):
        '''
            Objective:
            - Execute the CLI command 'user username'
            - Execute the CLI command 'password passwd' (if non-empty)
        
            Input:
            | `username` |  Username | 
            | `passwd` | Password |
            
            Return Value: 
            - True if configuration is successful
            - False otherwise
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c= t.controller('main')
            
            try:
                string = "user %s" % str(username)

                if (passwd is not None):
                    string =  string + "; password %s" % str(passwd)
                helpers.test_log("Issue command: %s" %string) 
                result = c.config(string)
                helpers.log("Output: %s" % result) 

                return True
            except:
                helpers.test_failure("Something went wrong") 
                return False


    def rest_open_gui_port(self):
        '''
            Objective:
            - Execute the CLI command 'firewall allow tcp 8443' on interface Ethernet 0
        
            Input:
            | `username` |  Username | 
            | `passwd` | Password is set to 'adminadmin' if True |
            
            Return Value: 
            - True if configuration is successful
            - False otherwise
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c= t.controller('main')

            try:
                url = '/rest/v1/model/controller-alias/'
                c.rest.get(url)
                if not c.rest.status_code_ok():
                    helpers.test_failure(c.rest.error())
                content = c.rest.content()
                controller_name = str(content[0]['controller'])
                
                url = '/rest/v1/model/firewall-rule/' 
                interface_string = controller_name + "|Ethernet|0"
                c.rest.put(url, {"interface": str(interface_string), "vrrp-ip": str(""), "port": 8443, "src-ip": str(""), "proto": str("tcp")})

            except:
                helpers.test_failure(c.rest.error())
                return False
            else:  
                if not c.rest.status_code_ok():
                    helpers.test_failure(c.rest.error())
                    return False
                else:
                    helpers.test_log(c.rest.content_json())
                    return True


    def CLI_start_mininet_server(self, topo):
        '''
            Objective:
            - Execute CLI commands to start a Mininet server
        
            Input:
            | `topo` |  Topology | 
            
            Return Value: 
            - True if configuration is successful
            - False otherwise
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c= t.controller()

            try:
                c.bash("sudo mn --mac  --topo=%s" % topo)
                helpers.log("Mininet server started successfully")
                return True
            except:
                helpers.test_failure("Output: %s" % c.cli_content()) 
                return False

####### End Here #######
    def cli_download_image_and_upgrade(self, package):
        '''
            Objective:
            - Execute CLI commands to download given upgrade package to Main (and Subordinate if exists) Controllers
        
            Input:
            | `image` |  URL to the upgrade package | 
            
            Return Value: 
            - True if configuration is successful
            - False otherwise
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c= t.controllers()
            
            if len(c) == 2:
                node = t.controller('subordinate')
            elif len(c) == 1:
                node = t.controller('main')
            else:
                helpers.test_failure("More than two controllers or no controller configured") 
                return False
                
            
            for i in range (0,len(c)):
                try:
                    result = node.config("debug bash")
                    result = node.config("cd /home/images/")
                    result = node.config("sudo rm *")
                    result = node.config("sudo wget  %s" %  package)
                    helpers.log("Output: %s" % result)
                    self.cli_upgrade(node)
                    time.sleep(120)
                except:
                    helpers.test_failure("Output: %s" % result) 
                    return False
                
                if len(c) == 2:
                    node = t.controller('subordinate')
            
            return True
            
    def cli_upgrade_old(self, node):
        '''
            Objective:
            - Execute CLI commands to upgrade given controller
        
            Input:
            | `node` |  Controller to be upgraded | 
            
            Return Value: 
            - True if configuration is successful
            - False otherwise
        '''
        try:
            node.enable('')
            node.send("upgrade")
            node.expect(r"\(yes to continue\)")
            node.send("yes")
            node.expect(r"Password:")
            node.enable("adminadmin", timeout=300)
            node.send("reload")
            node.expect(r"Confirm Reload \(yes to continue\)")
            node.send("yes")
            #node.expect(r"The system is going down for reboot NOW")
            helpers.log("Output: %s" % node.cli_content())
        except:
            helpers.test_failure("Output: %s" % node.cli_content()) 
            helpers.log("Output: %s" % node.cli_content()) 
            return False
        
        
        
    def upgrade_to(self, package):
        '''
            Objective:
            - Execute CLI commands to download given upgrade package to Main (and Subordinate if exists) Controllers and upgrade them
        
            Input:
            | `package` |  URL to the upgrade package | 
            
            Return Value: 
            - True if configuration is successful
            - False otherwise
        '''
        
        try:
            t = test.Test()
        except:
            return False
        else:
            c= t.controllers()
            controller_qty = len(c)
            
            if controller_qty == 2:
                node = t.controller('subordinate')
            elif controller_qty == 1:
                node = t.controller('main')
            else:
                helpers.test_failure("More than two controllers or no controller configured") 
                return False
            
            for i in range (0, controller_qty):
                try:
                    #node.config("debug bash")
                    node.bash("cd /home/images/")
                    node.bash("sudo rm *")
                    node.bash("sudo wget  %s" %  package)
                    node.bash("exit")
                    helpers.log("Image downloaded successfully")
                    
                    node.enable('enable')
                    node.send("upgrade")
                    node.expect(r"\(yes to continue\)")
                    node.send("yes")
                    node.expect(r"Password:")
                    node.enable("adminadmin", timeout=300)
                    node.send("reload")
                    node.expect(r"Confirm Reload \(yes to continue\)")
                    node.send("yes")
                    time.sleep(120)
                except:
                    helpers.test_failure("Output: %s" % node.cli_content()) 
                    return False
                
                if controller_qty == 2:
                    node = t.controller('subordinate')
            
            return True
                
        
    def PUSHED_cli_upgrade_image(self, node=None, package=None,  timeout=200, sleep=200):
        '''
            Objective:
            - Execute CLI commands to download given upgrade package to Main (and Subordinate if exists) Controllers and upgrade them
        
            Input:
            | `package` |  URL to the upgrade package | 
            | `node` |  Node to be upgraded. Leave empty to upgrade all nodes in your topology | 
            | `timeout` |  Timeout (in seconds) for "upgrade" command to be execute | 
            | `sleep` |  Time (in seconds) of sleep after upgrade, before next actions | 
            
            Return Value: 
            - True if configuration is successful
            - False otherwise
        '''
        try:
            t = test.Test()
        except:
            return False

          
        if not package:
            helpers.test_error("You must specify a package name")
        if not node:
            # assume all controllers if node is not specified
            node_handles = t.controllers()
            controller_qty = len(t.controllers())
        else:
            node_handles = [t.controller(node)]
            controller_qty = 1

        helpers.log("Number of controllers %s" % controller_qty)
        
        if controller_qty > 2 or controller_qty < 1:
            helpers.test_failure("More than two controllers or no controller configured") 
            return False
    
        for i in range(0, controller_qty):
            try:
                if controller_qty > 1: 
                    n = t.controller('subordinate')
                else:
                    n = node_handles[0]
                    
                helpers.log("Upgrade '%s' to image '%s'" % (n.name(), package))
                n.bash("cd /home/images/")
                n.bash("sudo rm *")
                n.bash("sudo wget  %s" %   package)
                n.bash("exit")
                helpers.log("Image downloaded successfully")
                
                n.enable('enable')
                n.send("upgrade")
                n.expect(r"\(yes to continue\)")
                n.send("yes")
                n.expect(r"Password:")
                n.enable("adminadmin", timeout=timeout)
                n.send("reload")
                n.expect(r"Confirm Reload \(yes to continue\)")
                n.send("yes")
                time.sleep(float(sleep))
            except:
                helpers.test_failure("Output: %s" % n.cli_content()) 
                return False
        return True   
    
    
    
    
                 
    def cli_upgrade_backup(self, node):
        '''
            Objective:
            - Execute CLI commands to upgrade given controller
        
            Input:
            | `node` |  Main, Main-Blocked or Subordinate | 
            
            Return Value: 
            - True if configuration is successful
            - False otherwise
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c= t.controllers()
            
            if len(c) == 2:
                main = t.controller('main')
                subordinate = t.controller('subordinate')
                
            elif len(c) == 1:
                main = t.controller('main')
            else:
                helpers.test_failure("More than two controllers or no controller configured") 
                return False

            if node == 'Subordinate':
                node = subordinate
            elif node == 'Main':
                node = main
            else:
                helpers.test_failure("Trying to upgrade node other than Main or Subordinate") 
                return False
            
            result = "Empty"
                
            try:
                node.enable('')
                node.send("upgrade")
                node.expect(r"\(yes to continue\)")
                node.send("yes")
                node.expect(r"Password:")
                node.enable("adminadmin", timeout=300)
                node.send("reload")
                node.expect(r"Confirm Reload \(yes to continue\)")
                node.send("yes")
                node.expect(r"The system is going down for reboot NOW")
                helpers.log("Output: %s" % node.cli_content())
                
                return True
            except:
                helpers.test_failure("Output: %s" ) 
                helpers.log("Output: %s" % result) 
                return False                            
