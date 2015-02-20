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
###  Last Updated: 11/13/2014
###  Last updated: Sahaja
###  WARNING !!!!!!!
'''

import autobot.helpers as helpers
import autobot.test as test
import subprocess
import re
import string


syslogMonitorFlag = False  # ## To check if Syslog monitoring is currently enabled

class AppController(object):

    def __init__(self):
        pass



###################################################
# All Show Commands Go Here:
###################################################



    def cli_upgrade_image(self, node=None, package=None, timeout=600, sleep_time=600):
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
            helpers.test_log("More than two controllers or no controller configured")
            return False

        for i in range(0, controller_qty):
            try:
                if controller_qty > 1:
                    n = t.controller('slave')
                else:
                    n = node_handles[0]

                helpers.log("No %s : Upgrade '%s' to image '%s'" % (i, n.name(), package))
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
                helpers.test_log("Output: %s" % n.cli_content())
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
                helpers.test_log(c.rest.error())
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
                helpers.test_log(c.rest.error())
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
                    helpers.test_log(c.rest.error())
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
                helpers.test_log(c.rest.error())
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
            helpers.test_log(c.rest.error())
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
                helpers.test_log(c.rest.error())
                return False
            else:
                if not c.rest.status_code_ok():
                    helpers.test_log(c.rest.error())
                    return False
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
                helpers.test_log(c.rest.error())
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
                helpers.test_log(c.rest.error())
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
                helpers.test_log(c.rest.error())
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
                if user == "admin":
                    c.enable("show banner")
                    content = c.cli_content()
                else:
                    c_user = t.node_spawn(ip=c.ip(), user=str(user), password=password)
                    c_user.enable("show banner")
                    content = c_user.cli_content()
                    c_user.close()
                    t.node_reconnect(node='master')
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
                    c_user = t.node_spawn(ip=c.ip(), user=str(username), password=password)
                    c_user.put(url, data)
                    c_user.close()
                    t.node_reconnect(node='master')
            except:
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
                    c_user = t.node_spawn(ip=c.ip(), user=str(user), password=password)
                    c_user.enable(command)
                    content = c_user.cli_content()
                    c_user.close()
                else:
                    c.enable(command)
                    content = c.cli_content()
            except:
                helpers.test_log(c.rest.error())
                return False
            else:
                return content

    def strip_character_from_string(self, test_string, search, replace):
        if str(replace) == 'blank':
            replace = ''
        return  test_string.replace(str(search), str(replace))

# ## Added by Sahaja
    def start_syslog_monitor(self):
        '''
        Start monitoring the log.
        Kill the existing tail process if any and start new tail
        '''
        global syslogMonitorFlag

        try:
            t = test.Test()
            c1 = t.controller('c1')
            c2 = t.controller('c2')
            c1_pidList = self.get_syslog_monitor_pid('c1')
            c2_pidList = self.get_syslog_monitor_pid('c2')
            for c1_pid in c1_pidList:
                # if (re.match("^d", c1_pid)):
                c1.sudo('kill -9 %s' % (c1_pid))
            for c2_pid in c2_pidList:
                # if (re.match("^d", c2_pid)):
                c2.sudo('kill -9 %s' % (c2_pid))
            # Add rm of the file if file already exist in case of a new test
            # for i in range(1, 21):
            #    c1.bash("sudo sed -i -e '$G' /var/log/syslog")
            #    c2.bash("sudo sed -i -e '$G' /var/log/syslog")
            c1.bash("tail -n 0 -f /var/log/syslog | grep --line-buffered '#011' > %s &" % "c1_syslog_dump.txt")
            c2.bash("tail -n 0 -f /var/log/syslog | grep --line-buffered '#011' > %s &" % "c2_syslog_dump.txt")
            syslogMonitorFlag = True
            return True
        except:
            helpers.log("Exception occured while starting the syslog monitor")
            return False

# ## Added by Sahaja
    def restart_syslog_monitor(self, node):
        '''
        Restart the monitoring both the files will start logging again
        Input: Node, c1, c2, etc
        '''
        global syslogMonitorFlag
        if(syslogMonitorFlag):
            t = test.Test()
            c = t.controller(node)
            result = c.sudo('ls *_dump.txt')
            filename = re.split('\n', result['content'])[2:-1]
            c.bash("tail -f /var/log/syslog/syslog.log | grep --line-buffered '#011' >> %s &" % filename[0].strip('\r'))
            return True
        else:
            return True

# ## Added by Sahaja
    def stop_syslog_monitor(self):
        '''
        Stop the monitoring by killing the pid of tail process
        Input: None
        '''
        global syslogMonitorFlag
        if(syslogMonitorFlag):
            c1_pidList = self.get_syslog_monitor_pid('c1')
            c2_pidList = self.get_syslog_monitor_pid('c2')
            t = test.Test()
            c1 = t.controller('c1')
            c2 = t.controller('c2')
            helpers.log("Stopping syslog Monitor on C1")
            for c1_pid in c1_pidList:
                helpers.log("PID on C1 is %s: " % (c1_pid))
                c1.sudo('kill -9 %s' % (c1_pid))
            helpers.log("Stopping syslog Monitor on C2")
            for c2_pid in c2_pidList:
                helpers.log("PID on C2 is %s: " % (c2_pid))
                c2.sudo('kill -9 %s' % (c2_pid))
            syslogMonitorFlag = False
            try:
                helpers.log("****************    syslog Log From C1    ****************")
                result = c1.sudo('cat c1_syslog_dump.txt')
                split = re.split('\n', result['content'])[2:-1]
            except:
                helpers.log("Split failed for c1")
                return False

            else:
                if split:
                    helpers.warn("syslog Errors Were Detected %s At: %s " % (split, helpers.ts_long_local()))
                    helpers.sleep(2)
                    return False
                else:
                    helpers.log("No Errors From syslog Monitor on C1")

            try:
                helpers.log("****************    syslog Log From C2    ****************")
                result = c2.sudo('cat c2_syslog_dump.txt')
                split = re.split('\n', result['content'])[2:-1]
            except:
                helpers.log("Split failed for c2")
                return False
            else:
                if split:
                    helpers.warn("syslog Errors Were Detected %s At: %s " % (split, helpers.ts_long_local()))
                    helpers.sleep(2)
                    return False
                else:
                    helpers.log("No Errors From syslog Monitor on C2")
                    helpers.sleep(2)
                    return True
        else:
            helpers.log("syslogMonitorFlag is not set: Returning")
            helpers.sleep(2)
            return False

# ## Added by Sahaja
    def get_syslog_monitor_pid(self, role):
        '''Get the pid of tail processes
        Input: c1,c2,etc
        '''
        t = test.Test()
        c = t.controller(role)
        helpers.log("Verifing for monitor job")
        c_result = c.bash('ps ax | pgrep tail | awk \'{print $1}\'')
        split = re.split('\n', c_result['content'])
        pidList = split[1:-1]
        return pidList

# ## Added by Sahaja
    def rest_cleanconfig_switch_config(self):
        ''' Get all the list of switches configured and delete first the role and then delete the switch

        Input: none

        example show command: "show running-config switch"

        Return value is if the deletion succeeded or not
        '''
        t = test.Test()
        try:
            c = t.controller('master')
        except:
            return False
        show_url = '/api/v1/data/controller/applications/bigtap/interface-config?config=true'
        c.rest.get(show_url)
        switch_data = c.rest.content()
        url = '/api/v1/data/controller/applications/bigtap/interface-config[interface="%s"][switch="%s"]'
        helpers.test_log("type of switch_data is %s" % (type(switch_data)))
        if len(switch_data) != 0:
            for intf in switch_data:
                helpers.test_log("type of intf is %s" % (type(intf)))
                if "interface" and "name" and "role" and "switch" in intf.keys():
                    helpers.test_log("Now will be deleting :: %s %s %s %s" % (intf["switch"], intf["role"], intf["interface"], intf["name"]))
                    # final_url = url % (intf["interface"], intf["switch"])
                    c.rest.delete(url % (intf["interface"], intf["switch"]), {'role':intf["role"]})
        else:
            helpers.test_log("Switch data is empty no switches configured")
            return True

        # Make sure there is no config left after deletion of roles
        c.rest.get(show_url)
        role_data_after_delete = c.rest.content()
        if len(role_data_after_delete) == 0:
            helpers.test_log("All the roles have been deleted for all the switch interfaces")
        else:
            helpers.test_log("Few roles are still left %s" % (role_data_after_delete))
            return False

        # Delete Switches as roles are deleted
        switch_url = '/api/v1/data/controller/core/switch?config=true'
        c.rest.get(switch_url)
        data = c.rest.content()
        for switch in data:
            if "dpid" in switch.keys():
                helpers.test_log("Going to delete: %s" % (switch["dpid"]))
                switch_delete_url = '/api/v1/data/controller/core/switch[dpid="%s"]' % (switch["dpid"])
                c.rest.delete(switch_delete_url)
        # Make sure all switches have been deleted
        c.rest.get(switch_url)
        data = c.rest.content()
        if len(data) == 0:
            helpers.test_log("All the switches have been deleted")
            return True
        else:
            helpers.test_log("Few switches have not been deleted %s" % (data))
            return False


# ## Added by Sahaja
    def rest_cleanconfig_bigtap_add_grp(self):
        '''Get all the list of address groups and delete them

        Input: None

        show command used: show running-config bigtap address-group

        Output: Return false if any address-groups are left after deletion

        '''
        t = test.Test()
        try:
            c = t.controller('master')
        except:
            return False

        show_url = "/api/v1/data/controller/applications/bigtap/ip-address-set?config=true"
        try:
            c.rest.get(show_url)
            addr_grp_data = c.rest.content()
        except:
            helpers.test_failure(c.rest.error())
            return False
        delete_url = '/api/v1/data/controller/applications/bigtap/ip-address-set[name="%s"]'
        if len(addr_grp_data) != 0:
            for add_grp in addr_grp_data:
                helpers.test_log("type of add_grp is %s" % (type(add_grp)))
                if "name" in add_grp.keys():
                    c.rest.delete(delete_url % (add_grp['name']))
                else:
                    helpers.test_log("There is no name field for %s" % add_grp)
                    return False
        else:
            helpers.test_log("Add-grp data is empty")
            return True

        # Make sure all the address-groups have been deleted
        c.rest.get(show_url)
        delete_addr_grp_data = c.rest.content()
        if len(delete_addr_grp_data) == 0:
            helpers.test_log("All the address-groups have been deleted")
            return True
        else:
            helpers.test_log("Few address-groups have not been deleted %s" % (delete_addr_grp_data))
            return False

# ## Added by Sahaja
    def rest_cleanconfig_bigtap_user_defined_offset(self):
        '''Get all the user-defined-groups and delete them

        Input: None

        show command used: show running-config bigtap user-defined-group

        Output: Return false if groups are not deleted properly
        '''
        t = test.Test()
        try:
            c = t.controller('master')
        except:
            return False

        show_url = "/api/v1/data/controller/applications/bigtap/user-defined-offset?config=true"
        try:
            c.rest.get(show_url)
            show_data = c.rest.content()
        except:
            helpers.test_failure(c.rest.error())
            return False
        delete_url = "/api/v1/data/controller/applications/bigtap/user-defined-offset/%s/anchor {}"
        if len(show_data) != 0:
            for ugrp in show_data:
                for grp in ugrp.keys():
                    helpers.test_log("Deleting the group %s" % (grp))
                    c.rest.delete(delete_url % (grp))
                    return True
        else:
            helpers.test_log("There are no user-defined offsets to delete")
            return True

# ## Added by Sahaja

    def rest_cleanconfig_bigtap_policy(self):
        '''Get all the policy and associated view names and delete them

        Input: None

        show commands used: 'show running-config bigtap policy', 'show bigtap rbac-permission'

        Output: Return false if deletion is not successful
        '''
        t = test.Test()
        try:
            c = t.controller('master')
        except:
            return False

        delete_url = "/api/v1/data/controller/applications/bigtap/view[name='%s']/policy[name='%s'] {}"
        show_policy_url = "/api/v1/data/controller/applications/bigtap/view/policy?config=true"
        show_view_url = "/api/v1/data/controller/applications/bigtap/view?select=policy/name"

        c.rest.get(show_policy_url)
        policy_data = c.rest.content()

        c.rest.get(show_view_url)
        view_data = c.rest.content()

        # GET THE POLICY NAMES
        lis_p = []
        if len(policy_data) != 0:
            for pol in policy_data:
                lis_p.append(pol['name'])
        else:
            helpers.test_log("No list of policies to delete")
            return True

        for pol_n in lis_p:
            for elem in view_data:
                for pol in elem['policy']:
                    if cmp(pol_n, pol['name']) == 0:
                        helpers.test_log("Will be deleting policy %s with view %s" % (pol_n, elem['name']))
                        c.rest.delete(delete_url % (elem['name'], pol_n))

        c.rest.get(show_policy_url)
        delete_policy_data = c.rest.content()
        if len(delete_policy_data) == 0:
            helpers.test_log("All the user-defined-groups have been deleted")
            return True
        else:
            helpers.test_log("Few policies have not been deleted %s" % (delete_policy_data))
            return False

# ## Added by Sahaja
    def write_version_to_file(self):
        '''Touch a file and write the version of the controller to file
        '''
        t = test.Test()
        try:
            c = t.controller('master')
        except:
            return False
        show_version_url = "/rest/v1/system/version"
#        vf = open("/var/lib/libvirt/bigtap_regressions/ver.txt", "wb")
        vf = open("/var/tmp/ver.txt", "wb")
        c.rest.get(show_version_url)
        ver_data = c.rest.content()
        helpers.test_log("Version string got is: %s" % (ver_data))
        if ver_data:
            ver = re.search('(.+?)(\(.+)\)', ver_data[0]["controller"])
            if ver:
                vf.write("%s %s" % (ver.group(1), ver.group(2)))
                return True
            else:
                helpers.test_log("Did not match the version format, got %s" % (ver))
                return False
        else:
            helpers.test_log("Version string is empty")
            return False

# ## Animesh
    def return_version_number(self, node="master", user="admin", password="adminadmin", local=True):
        t = test.Test()
        n = t.node(node)
        if helpers.is_bigtap(n.platform()):
            c = t.controller('master')
            url = '/rest/v1/system/version'
            if user == "admin":
                try:
                    t.node_reconnect(node='master', user=str(user), password=password)
                    c.rest.get(url)
                    content = c.rest.content()
                    output_value = content[0]['controller']
                except:
                    return False
                else:
                    return output_value
            else:
                try:
                    c_user = t.node_reconnect(node='master', user=str(user), password=password)
                    c_user.rest.get(url)
                    content = c_user.rest.content()
                    output_value = content[0]['controller']
                    output_string = output_value.split(' ')

                except:
                    t.node_reconnect(node='master')
                    return False
                else:
                    if local is True:
                        t.node_reconnect(node='master', user=str(user), password=password)
                    return output_string[3]
