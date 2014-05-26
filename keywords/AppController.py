''' 
###  WARNING !!!!!!!
###  
###  This is where common code for BigTap/BigWire Controllers will go in.
###  
###  To commit new code, please contact the Library Owner: 
###  Animesh Patcha (animesh.patcha@bigswitch.com)
###
###  DO NOT COMMIT CODE WITHOUT APPROVAL FROM LIBRARY OWNER
###  
###  Last Updated: 02/08/2014
###  
###  WARNING !!!!!!!
'''

import autobot.helpers as helpers
import autobot.test as test
import subprocess
import re

class AppController(object):

    def __init__(self):
        pass



###################################################
# All Show Commands Go Here:
###################################################



    def cli_upgrade_image(self, node=None, package=None, timeout=200, sleep_time=200):
        '''
            Objective:
            - Execute CLI commands to download given upgrade package to Master (and Slave if exists) Controllers and upgrade them

            Input:
            | `package` |  URL to the upgrade package | 
            | `node` |  Node to be upgraded. Leave empty to upgrade all nodes in your topology | 
            | `timeout` |  Timeout (in seconds) for "upgrade" command to be execute | 
            | `sleep` |  Time (in seconds) of sleep after upgrade, before next actions | 
            
            Return Value: 
            - True if configuration is successful
            - False otherwise
        '''

        t = test.Test()

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
                    n = t.controller('slave')
                else:
                    n = node_handles[0]

                helpers.log("Upgrade '%s' to image '%s'" % (n.name(), package))
                n.bash("cd /home/images/")
                n.bash("sudo rm *")
                n.bash("sudo wget  %s" % package)
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
                helpers.sleep(sleep_time)
            except:
                helpers.test_failure("Output: %s" % n.cli_content())
                return False
        return True


    def rest_return_switch_dpid_from_alias(self, switch_alias):
        '''
        Objective: Returns switch DPID, given a switch alias
        
        Input:  
        | `switch_alias` |  User defined switch alias | 
        
        Description:
        The function 
        - executes a REST GET for http://<CONTROLLER_IP>:8082/api/v1/data/controller/core/switch?select=alias
        - and greps for switch-alias, and returns switch-dpid
        
        Return value
        - Switch DPID on success
        - False on failure
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('master')
            try:
                url = '/api/v1/data/controller/core/switch?select=alias'
                c.rest.get(url)
                content = c.rest.content()
                for x in range(0, len(content)):
                    if str(content[x]['alias']) == str(switch_alias):
                        return content[x]['dpid']
                return False
            except:
                return False

    def rest_return_switch_dpid_from_ip(self, node, soft_error=False):
        '''
        Objective: Returns switch DPID, given a switch alias
        
        Input:  
        | `node` |  Reference to node as defined in .topo file | 
        
        Description:
        The function 
        - executes a REST GET for http://<CONTROLLER_IP>:8082/api/v1/data/controller/core/switch?select=alias
        - and greps for switch-alias, and returns switch-dpid
        
        Return value
        - Switch DPID on success
        - False on failure
        '''
        try:
            t = test.Test()
            c = t.controller('master')
            url_to_get = '/api/v1/data/controller/core/switch'
            c.rest.get(url_to_get)
            switch = t.switch(node)
        except:
            helpers.test_error("URL Get Failed", soft_error)
            return False
        else:
            content = c.rest.content()
            for x in range(0, len(content)):
                if content[x].has_key('inet-address'):
                    if str(content[x]['inet-address']['ip']) == switch.ip():
                        return content[x]['dpid']
                else:
                    helpers.log("Looks like %s is a disconnected switch" % (content[x]['dpid']))
            return False

    def rest_show_switch(self):
        '''Return dictionary containing DPID,IP Addresses for every switch connected to current controller
        
            Input: N/A
            
            Returns: Dictionary of Switch DPID and IP Addresses
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('master')
            try:
                url = '/api/v1/data/controller/core/switch'
                c.rest.get(url)
            except:
                helpers.test_failure(c.rest.error())
                return False
            else:
                content = c.rest.content()
                switch_dict = {}
                for x in range (0, len(content)):
                    switch_dict[str(content[x]['inet-address']['ip'])] = str(content[x]['dpid'])
                return switch_dict
###################################################
# All Config Commands Go Here:
###################################################

    def rest_add_switch_alias(self, node, switch_alias):
        '''
            Objective:
            - Configure switch alias
            
            Inputs:
            | node | Reference to switch as defined in .topo file |
            | switch_alias | alias of switch |
            
            Return Value:
            | True | On configuration success|
            | False | On configuration failure |
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('master')
            try:
                switch_dpid = self.rest_return_switch_dpid_from_ip(node)
            except:
                return False
            else:
                try:
                    url = '/api/v1/data/controller/core/switch[dpid="%s"]' % switch_dpid
                    c.rest.put(url, {"dpid": str(switch_dpid)})
                except:
                    return False
                else:
                    if not c.rest.status_code_ok():
                        helpers.test_log(c.rest.error())
                        return False
                    else:
                        try:
                            url = '/api/v1/data/controller/core/switch[dpid="%s"]' % switch_dpid
                            c.rest.patch(url, {"alias": str(switch_alias)})
                        except:
                            return False
                        else:
                            if not c.rest.status_code_ok():
                                helpers.test_log(c.rest.error())
                                return False
                            else:
                                helpers.test_log(c.rest.content_json())
                                return True

    def rest_delete_switch_alias(self, node):
        '''
            Objective:
            - Delete switch alias
            
            Inputs:
            | node | Reference to switch as defined in .topo file |
            
            Return Value:
            | True | On configuration success|
            | False | On configuration failure |        
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('master')
            try:
                switch_dpid = self.rest_return_switch_dpid_from_ip(node)
            except:
                return False
            else:
                try:
                    url = '/api/v1/data/controller/core/switch[dpid="%s"][dpid="%s"]/alias' % (switch_dpid, switch_dpid)
                    c.rest.delete(url, {})
                except:
                    return False
                else:
                    if not c.rest.status_code_ok():
                        helpers.test_log(c.rest.error())
                        return False
                    else:
                        helpers.test_log(c.rest.content_json())
                        return True

    def rest_delete_switch(self, node):
        '''
            Objective:
            - Delete switch 
            - Execute cli command 'switch 00:00:5c:16:c7:1c:16:f2'
            
            Inputs:
            | node | Reference to switch as defined in .topo file |
            
            Return Value:
            | True | On configuration success|
            | False | On configuration failure |        
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('master')
            try:
                switch_dpid = self.rest_return_switch_dpid_from_ip(node)
            except:
                return False
            else:
                try:
                    url = '/api/v1/data/controller/core/switch[dpid="%s"]' % (switch_dpid)
                    c.rest.delete(url, {})
                except:
                    return False
                else:
                    if not c.rest.status_code_ok():
                        helpers.test_log(c.rest.error())
                        return False
                    else:
                        helpers.test_log(c.rest.content_json())
                        return True

    def flap_eth0_controller(self, controller_role):
        ''' Flap eth0 on Controller
        
            Input:
               controller_role        Where to execute the command. Accepted values are `Master` and `Slave`
           
           Return Value:  True if the configuration is successful, false otherwise 
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            try:
                if (controller_role == 'Master'):
                    c = t.controller('master')
                else:
                    c = t.controller('slave')
            except:
                helpers.test_failure(c.rest.error())
                return False
            else:
                try:
                    c.bash("echo '#!/bin/bash' > test.sh")
                    c.bash("echo 'sleep 15' >> test.sh")
                    c.bash("echo 'sudo ifconfig eth0 down' >> test.sh")
                    c.bash("echo 'sudo ifconfig eth0 down' >> test.sh")
                    c.bash("echo 'sleep 20' >> test.sh")
                    c.bash("echo 'sudo ifconfig eth0 up' >> test.sh")
                    c.bash("echo 'sleep 10' >> test.sh")
                    c.bash("echo 'sudo /etc/init.d/networking restart' >> test.sh ")
                    c.bash("echo 'sleep 10' >> test.sh")
                    c.bash("sh test.sh &")
                except:
                    helpers.test_failure(c.rest.error())
                    return False
                else:
                    return True

    def rest_execute_ha_failover(self):
        '''Execute HA failover from master controller
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('master')
            try:
                url1 = '/rest/v1/system/ha/failback'
                c.rest.put(url1, {})
            except:
                helpers.test_failure(c.rest.error())
                return False
            else:
                helpers.test_log(c.rest.content_json())
                return True

    def restart_controller(self, controller_role):
        '''Restart a process on controller
        
            Input:
               processName        Name of process to be restarted
               controller_role        Where to execute the command. Accepted values are `Master` and `Slave`
           
           Return Value:  True if the configuration is successful, false otherwise 
        '''
        try:
            t = test.Test()
            if (controller_role == 'Master'):
                c = t.controller('master')
            else:
                c = t.controller('slave')

            c.bash("echo '#!/bin/bash' > test_reboot.sh")
            c.bash("echo 'sleep 15' >> test_reboot.sh")
            c.bash("echo 'sudo reboot' >> test_reboot.sh")
            c.bash("sh test_reboot.sh &")
            helpers.sleep(300)
        except:
            helpers.test_failure(c.rest.error())
            return False
        else:
            return True

###################################################
# All Verify Commands Go Here:
###################################################
    def rest_verify_interface_is_up(self, node, interface_name):
        '''Verify if a given interface on a given switch is up
        
            Input: 
                `switch_dpid`       DPID of the Switch
                `interface_name`    Interface Name e.g. ethernet13
            
            Returns: True if the interface is up, false otherwise
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('master')
            try:
                switch_dpid = self.rest_return_switch_dpid_from_ip(node)
                url = '/api/v1/data/controller/core/switch[interface/name="%s"][dpid="%s"]?select=interface[name="%s"]' % (interface_name, switch_dpid, interface_name)
                c.rest.get(url)
            except:
                helpers.test_failure(c.rest.error())
                return False
            else:
                if not c.rest.status_code_ok():
                    helpers.test_failure(c.rest.error())
                content = c.rest.content()
                if (content[0]['interface'][0]['state-flags'] == 0):
                        return True
                else:
                        return False

# #SYSLOG
############### SYSLOG SHOW COMMANDS ########################
    def rest_show_syslog(self):
        '''Execute CLI command "show syslog" and return o/p
        
            Returns dictionary of o/p
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('master')
            try:
                url = '/rest/v1/model/syslog-server/'
                helpers.log("URL is %s  " % url)
                c.rest.get(url)
            except:
                helpers.test_failure(c.rest.error())
                return False
            else:
                content = c.rest.content()
                return content[0]

    def cli_verify_syslog(self, syslog_server, syslog_level):
        '''Execute CLI command "show syslog" and return o/p
        
            Returns dictionary of o/p
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('master')
            try:
                c.enable("show syslog")
            except:
                return False
            else:
                content = c.cli_content()
                str_search = str(syslog_server) + " " + str(syslog_level)
                if str(str_search) in content:
                    return True
                else:
                    return False
############### SYSLOG CONFIG COMMANDS ########################
    def rest_configure_syslog(self, syslog_server, log_level):
        '''Configure Syslog server
        
            Inputs:
                syslog_server: Name of Syslog server 
                log_level    :  Logging Level, 0-9
            
            Returns: True if configuration is successful, false otherwise
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('master')
            try:
                url = '/rest/v1/model/syslog-server/'
                c.rest.put(url, {"logging-enabled": True, "logging-server": str(syslog_server), "logging-level":int(log_level)})
            except:
                helpers.test_failure(c.rest.error())
                return False
            else:
                helpers.test_log(c.rest.content_json())
                return True

    def rest_delete_syslog(self, syslog_server, log_level):
        '''Delete Syslog server
        
            Inputs:
                syslog_server: Name of Syslog server 
                log_level    :  Logging Level, 0-9
            
            Returns: True if configuration is successful, false otherwise
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('master')
            try:
                url = '/rest/v1/model/syslog-server/?logging-enabled=True&logging-server=%s&logging-level=%d' % (str(syslog_server), int(log_level))
                c.rest.delete(url, {})
            except:
                helpers.test_failure(c.rest.error())
                return False
            else:
                helpers.test_log(c.rest.content_json())
                return True
# #NTP

############### NTP SHOW COMMANDS ########################
    def rest_show_ntp(self):
        '''Execute CLI command "show ntp" and return o/p
        
            Returns dictionary of o/p
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('master')
            try:
                url = '/rest/v1/model/ntp-server/'
                c.rest.get(url)
            except:
                return False
            else:
                content = c.rest.content()
                return content[0]

    def rest_verify_ntp(self):
        '''Execute CLI command "show ntp" and return o/p
        
            Returns dictionary of o/p
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('master')
            try:
                c.bash("ntpq -p")
            except:
                return False
            else:
                content = c.cli_content()
                return content

    def cli_verify_ntp(self, ntp_server="0.bigswitch.pool.ntp.org"):
        '''Execute CLI command "show ntp" and return o/p
        
            Returns dictionary of o/p
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('master')
            try:
                c.enable("show ntp")
            except:
                return False
            else:
                content = c.cli_content()
                if str(ntp_server) in content:
                    return True
                else:
                    return False
############### NTP CONFIG COMMANDS ########################

    def rest_configure_ntp(self, ntp_server):
        '''Configure NTP server
        
            Inputs:
                ntp_server: Name of NTP server 
            
            Returns: True if configuration is successful, false otherwise
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('master')
            try:
                url = '/rest/v1/model/ntp-server/'
                c.rest.put(url, {"enabled": True, "server": str(ntp_server)})
            except:
                return False
            else:
                helpers.test_log(c.rest.content_json())
                return True

    def rest_delete_ntp(self, ntp_server):
        '''Delete NTP server
        
            Inputs:
                ntp_server: Name of NTP server 
            
            Returns: True if configuration is successful, false otherwise
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('master')
            try:
                url = '/rest/v1/model/ntp-server/?enabled=True&server=%s' % (str(ntp_server))
                c.rest.delete(url, {})
            except:
                return False
            else:
                helpers.test_log(c.rest.content_json())
                return True

# ##Banner
    def rest_set_banner(self, banner_message):
        '''Set Banner on controller
        
            Inputs:
                banner_message: Message to be set 
            
            Returns: True if configuration is successful, false otherwise
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('master')
            try:
                url = '/rest/v1/model/banner/'
                c.rest.put(url, {"message": str(banner_message), "id": "banner"})
            except:
                return False
            else:
                helpers.test_log(c.rest.content_json())
                return True

    def rest_verify_banner(self):
        '''Set Banner on controller
        
            Inputs:
                banner_message: Message to be set 
            
            Returns: True if configuration is successful, false otherwise
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('master')
            try:
                url = '/rest/v1/model/banner/?id=banner'
                c.rest.get(url)
            except:
                return False
            else:
                content = c.rest.content()
                return content[0]

    def cli_verify_banner(self, banner_message, user="admin", password="adminadmin"):
        '''Execute CLI command "show ntp" and return o/p
        
            Returns dictionary of o/p
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('master')
            try:
                if "admin" not in user:
                    c_user = t.node_reconnect(node='master', user=str(user), password=password)
                    c_user.enable("show banner")
                    content = c_user.cli_content()
                    t.node_reconnect(node='master')
                else:
                    c.enable("show banner")
                    content = c.cli_content()
            except:
                return False
            else:
                if str(banner_message) in content:
                    return True
                else:
                    return False

    def rest_delete_banner(self):
        '''delete Banner on controller
        
            Inputs:
                banner_message: Message to be set 
            
            Returns: True if configuration is successful, false otherwise
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('master')
            try:
                url = '/rest/v1/model/banner/?id=banner'
                c.rest.delete(url, {})
            except:
                return False
            else:
                return True

    def rest_add_tacacs_authentication(self, tacacs=True, tacacs_priority=1, local=True, local_priority=2, username="admin", password="adminadmin"):
        '''
            Objective: Add TACACS configuration
            
            Input:
            | tacacs_server |  Tacacs Server |
            
            Return Value:
            True on Success
            False on Failure
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('master')
            # Configure AAA/Authentication
            try:
                url = '/api/v1/data/controller/core/aaa/authenticator'
                if (tacacs is True) and (local is True):
                    data = [{"priority": int(tacacs_priority), "name": "tacacs"}, {"priority": int(local_priority), "name": "local"}]
                elif (tacacs is True) and (local is False):
                    data = [{"priority": int(tacacs_priority), "name": "tacacs"}]
                elif (tacacs is False) and (local is True):
                    data = [{"priority": int(local_priority), "name": "local"}]
                else:
                    helpers.log("THIS IS AN IMPOSSIBLE SITUATION")

                if username == "admin":
                    c.rest.put(url, data)
                else:
                    c_user = t.node_reconnect(node='master', user=str(username), password=password)
                    c_user.put(url, data)
                    if local is True:
                        t.node_reconnect(node='master')
            except:
                t.node_reconnect(node='master')
                helpers.test_log(c.rest.error())
                return False
            else:
                return True

    def rest_delete_tacacs_authentication(self):
        '''
            Objective: Add TACACS configuration
            
            Input:
            | tacacs_server |  Tacacs Server |
            
            Return Value:
            True on Success
            False on Failure
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('master')
            # Configure AAA/Authentication
            try:
                url = '/api/v1/data/controller/core/aaa/authenticator'
                c.rest.delete(url, {})
            except:
                helpers.test_log(c.rest.error())
                return False
            else:
                return True


    def rest_add_tacacs_authorization(self):
        '''
            Objective: Add TACACS configuration
            
            Input:
            | tacacs_server |  Tacacs Server |
            
            Return Value:
            True on Success
            False on Failure
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('master')
            # Configure AAA/authorization
            try:
                url = '/api/v1/data/controller/core/aaa/authorizer'
                c.rest.put(url, [{"priority": 1, "name": "tacacs"}, {"priority": 2, "name": "local"}])
            except:
                helpers.test_log(c.rest.error())
                return False
            else:
                return True

    def rest_delete_tacacs_authorization(self):
        '''
            Objective: Add TACACS configuration
            
            Input:
            | tacacs_server |  Tacacs Server |
            
            Return Value:
            True on Success
            False on Failure
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('master')
            # Configure AAA/authorization
            try:
                url = '/api/v1/data/controller/core/aaa/authorizer'
                c.rest.delete(url, {})
            except:
                helpers.test_log(c.rest.error())
                return False
            else:
                return True

    def rest_add_tacacs_server(self, tacacs_server, key, timeout=90):
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('master')
            # Get encoded password from key
            try:
                url = '/api/v1/data/controller/core/aaa/tacacs/encode-password[password="%s"]' % str(key)
                c.rest.get(url)
                content = c.rest.content()
            except:
                helpers.test_log(c.rest.error())
                return False
            else:
            # Configure tacacse server
                encoded_password = content[0]['encoded-password']
                try:
                    url = '/api/v1/data/controller/core/aaa/tacacs/server[server-address="%s"]' % str(tacacs_server)
                    c.rest.put(url, {"server-address": str(tacacs_server), "secret": str(encoded_password), "timeout": int(timeout)})
                except:
                    helpers.test_log(c.rest.error())
                    return False
                else:
                    return True

    def rest_delete_tacacs_server(self, tacacs_server):
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('master')
            # Get encoded password from key
            try:
                url = '/api/v1/data/controller/core/aaa/tacacs/server[server-address="%s"]/secret' % str(tacacs_server)
                c.rest.delete(url, {})
            except:
                helpers.test_log(c.rest.error())
                return False
            else:
                try:
                    url = '/api/v1/data/controller/core/aaa/tacacs/server[server-address="%s"]/timeout' % str(tacacs_server)
                    c.rest.delete(url, {})
                except:
                    helpers.test_log(c.rest.error())
                    return False
                else:
                    try:
                        url = '/api/v1/data/controller/core/aaa/tacacs/server[server-address="%s"]' % str(tacacs_server)
                        c.rest.delete(url, {})
                    except:
                        helpers.test_log(c.rest.error())
                        return False
                    else:
                        return True

    def cli_execute_show_command(self, command, user="admin", password="adminadmin"):
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('master')
            # Get encoded password from key
            try:
                if "admin" not in user:
                    c_user = t.node_reconnect(node='master', user=str(user), password=password)
                    c_user.enable(command)
                    content = c_user.cli_content()
                    t.node_reconnect(node='master')
                else:
                    c.enable(command)
                    content = c.cli_content()
            except:
                helpers.test_log(c.rest.error())
                return False
            else:
                return content
