import autobot.helpers as helpers
import autobot.restclient as restclient
import autobot.test as test
import re
from netaddr import *




class BsnCommon(object):

    def __init__(self):
        pass

#######################################################
# All Common Controller Show Commands Go Here:
#######################################################

    def cli_walk_command(self, command, cmd_argument_count, cmd_argument=None, soft_error=False):
        '''
            Execute CLI walk on controller
        '''
        try:
            t = test.Test()
            c = t.controller('main')
        except:
            return False
        else:
            cli_string = command + ' ?'
            c.send(cli_string, no_cr=True)
            c.expect(r'[\r\n\x07][\w-]+[#>] ')
            content = c.cli_content()
            temp = helpers.strip_cli_output(content)
            temp = helpers.str_to_list(temp)
            helpers.log("********new_content:************\n%s" % helpers.prettify(temp))
            c.send(helpers.ctrl('u'))
            c.expect()
            c.cli('')
            num = len(temp)
            if num == int(cmd_argument_count):
                helpers.log("Correct number of arguments found in CLI help output")
            else:
                helpers.test_error("Correct number of arguments not returned", soft_error)
                return False

            if (cmd_argument is not None) :
                if (' ' in cmd_argument):
                    new_string = cmd_argument.split()
                    helpers.log("New String is %s" % new_string)
                    helpers.log("Temp is %s" % content)
                    for index in range(len(new_string)):
                        if (str(new_string[index]) in content):
                            helpers.log("Argument %s found in CLI help output" % new_string[index])
                        else:
                            helpers.test_error("Argument %s NOT found in CLI help output. Error was %s " % (new_string[index], soft_error))
                            return False
                else:
                    if (str(cmd_argument) in content):
                        helpers.log("Argument %s found in CLI help output" % cmd_argument)
                    else:
                        helpers.test_error("Argument %s NOT found in CLI help output. Error was %s " % (cmd_argument, soft_error))
                        return False
            return True

    def rest_is_c1_main_controller(self):
        '''Returns True if c1 (defined in .topo file) is Main, False otherwise
        '''
        t = test.Test()
        try:
            t.controller('c2')
        except:
            helpers.log('C1 is MASTER')
            return True
        else:
            c1 = t.controller('c1')
            c2 = t.controller('c2')
            url0 = '/rest/v1/system/ha/role'
            c1.rest.get(url0)
            content1 = c1.rest.content()
            c1role = content1['role']
            url0 = '/rest/v1/system/ha/role'
            c2.rest.get(url0)
            content2 = c2.rest.content()
            c2role = content2['role']
            if c1role == "MASTER":
                helpers.log('C1 is MASTER')
                return True
            else:
                helpers.log('C2 is MASTER')
                return False

    def rest_show_version(self):
        '''Return version of controller s/w
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('main')
            try:
                url = '/rest/v1/system/version'
                c.rest.get(url)
                content = c.rest.content()
            except:
                helpers.test_failure(c.rest.error())
                return False
            else:
                helpers.log("Output: %s" % content[0]['controller'])
                return content[0]['controller']

    def rest_ha_role(self):
        '''Return Current Controller Role viz. Main/Subordinate
        
            Input: N/A
            
            Returns: Current Controller Role viz. Main/Subordinate
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('main')
            try:
                url = '/system/ha/role'
                c.rest.get(url)
            except:
                helpers.test_failure(c.rest.error())
                return False
            else:
                if not c.rest.status_code_ok():
                    helpers.test_failure(c.rest.error())
                content = c.rest.content()
                return content['role']

    def rest_controller_id(self):
        '''Return Current Controller ID
        
            Input: N/A
            
            Returns: Return Current Controller ID
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('main')
            try:
                url = '/rest/v1/system/controller'
                c.rest.get(url)
            except:
                helpers.test_failure(c.rest.error())
                return False
            else:
                content = c.rest.content()
                return content['id']

    def rest_verify_dict_key(self, content, index, key):
        ''' Given a dictionary, return the value for a particular key
        
            Input:Dictionary, index and required key.
            
            Return Value:  return the value for a particular key
        '''
        return content[int(index)][str(key)]

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
            c = t.controller('main')
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

    def return_switch_dpid(self, switch_dict, ip_address):
            '''Return DPID of switch, when dictionary from o/p of `rest show switch` and IP Address is provided
            
               Input: 
                   switch_dict    dictionary of switch
                   ip_address        IP Address of Switch
                
               Return: Switch IP Address
            '''
            return switch_dict[str(ip_address)]

    def return_switch_dpid_from_alias(self, switch_alias):
        '''Given a switch alias, find the corresponding switch DPID
        
            Input:
                  switch_alias:    Alias of the switch
            
            Return:    Switch DPID
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('main')
            try:
                url = '/api/v1/data/controller/core/switch?select=alias'
                c.rest.get(url)
            except:
                helpers.test_failure(c.rest.error())
                return False
            else:
                content = c.rest.content()
                flag = False
                for x in range (0, len(content)):
                    if str(content[x]['alias']) == str(switch_alias):
                        return content[x]['dpid']
                return False

    def return_switch_interface_mac(self, interface_name, switch_alias=None, sw_dpid=None):
        '''Return the MAC/Hardware Address of a given interface
        
            Input: 
                `switch_dpid`       DPID of the Switch
                `interface_name`    Interface Name e.g. ethernet13
            
            Returns: Hardware/MAC Address of Interface
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('main')
            try:
                if (switch_alias is None and sw_dpid is not None):
                    switch_dpid = sw_dpid
                elif (switch_alias is None and sw_dpid is None):
                    helpers.log('Either Switch DPID or Switch Alias has to be provided')
                    return False
                elif (switch_alias is not None and sw_dpid is None):
                    switch_dpid = self.return_switch_dpid_from_alias(switch_alias)
                else:
                    switch_dpid = sw_dpid
                url = '/api/v1/data/controller/core/switch[interface/name="%s"][dpid="%s"]?select=interface[name="%s"]' % (interface_name, switch_dpid, interface_name)
                c.rest.get(url)
            except:
                helpers.test_failure(c.rest.error())
                return False
            else:
                if not c.rest.status_code_ok():
                    helpers.test_failure(c.rest.error())
                content = c.rest.content()
                return content[0]['interface'][0]['hardware-address']

    def restart_process_controller(self, process_name, controller_role):
        '''Restart a process on controller
        
            Input:
               processName        Name of process to be restarted
               controller_role        Where to execute the command. Accepted values are `Main` and `Subordinate`
           
           Return Value:  True if the configuration is successful, false otherwise 
        '''
        try:
            t = test.Test()
            if (controller_role == 'Main'):
                c = t.controller('main')
            else:
                c = t.controller('subordinate')
            conn = SSH2()
            conn.connect(c.ip)
            conn.login(Account("admin", "adminadmin"))
            conn.execute('enable')
            conn.execute('debug bash')
            input = 'service ' + str(process_name) + ' restart'
            conn.execute(input)
            conn.send('logout\r')
            conn.send('logout\r')
            conn.close()
        except:
            helpers.test_failure(c.rest.error())
            return False
        else:
            return True

    def execute_controller_command_return_output(self, input, controller_role):
        '''Execute a generic command on the controller and return output.
        
            Input:
                controller_role        Where to execute the command. Accepted values are `Main` and `Subordinate`
                input            Command to be executed on switch
                
            Return Value: Output from command execution
        '''
        try:
            t = test.Test()
            if (controller_role == 'Main'):
                c = t.controller('main')
            else:
                c = t.controller('subordinate')
            conn = SSH2()
            conn.connect(c.ip)
            conn.login(Account("admin", "adminadmin"))
            conn.execute('enable')
            conn.execute('debug bash')
            conn.execute(input)
            output = conn.response
            conn.send('logout\r')
            conn.send('logout\r')
            conn.close()
        except:
            return False
        else:
            return output

    def return_main_subordinate_ip_address(self):
        '''Returns main and subordinate IP addresses as a dictionary
        '''
        t = test.Test()
        ip_address_list = {}
        try:
            t.controller('subordinate')
        except:
            return {'Main':str(t.controller('main').ip)}
        else:
            ip_address_list = {'Main':str(t.controller('main').ip), 'Subordinate':str(t.controller('subordinate').ip)}
            return (ip_address_list)

########################################################
# All Common Controller Verification Commands Go Here:
########################################################

    def verify_interface_is_up(self, interface_name, switch_alias=None, sw_dpid=None):
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
            c = t.controller('main')
            try:
                if (switch_alias is None and sw_dpid is not None):
                    switch_dpid = sw_dpid
                elif (switch_alias is None and sw_dpid is None):
                    helpers.log('Either Switch DPID or Switch Alias has to be provided')
                    return False
                elif (switch_alias is not None and sw_dpid is None):
                    switch_dpid = self.return_switch_dpid_from_alias(switch_alias)
                else:
                    switch_dpid = sw_dpid
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

########################################################
# All Common Controller Configuration Commands Go Here:
########################################################
#   Objective: Set Switch alias via command "switch-alias <switch_alias>"
#   Input: Switch DPID and Switch Alias
#   Return Value:  True/False
    def rest_set_switch_alias(self, switch_dpid, switch_alias):
        '''Set Switch alias via command "switch-alias <switch_alias>"
        
            Input:
                `switch_dpid`        DPID of switch
                `switch_alias`        Desired alias for switch
            
            Return: true if configuration is successful, false otherwise
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('main')
            try:
                url = '/api/v1/data/controller/core/switch[dpid="%s"]' % (str(switch_dpid))
                c.rest.patch(url, {"alias": str(switch_alias)})
            except:
                helpers.test_failure(c.rest.error())
                return False
            else:
                helpers.test_log(c.rest.content_json())
                return True

    def rest_execute_ha_failover(self):
        '''Execute HA failover from main controller
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('main')
            try:
                url1 = '/rest/v1/system/ha/failback'
                c.rest.put(url1, {})
            except:
                helpers.test_failure(c.rest.error())
                return False
            else:
                helpers.test_log(c.rest.content_json())
                return True

    def flap_eth0_controller(self, controller_role):
        ''' Flap eth0 on Controller
        
            Input:
               controller_role        Where to execute the command. Accepted values are `Main` and `Subordinate`
           
           Return Value:  True if the configuration is successful, false otherwise 
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            try:
                if (controller_role == 'Main'):
                    c = t.controller('main')
                else:
                    c = t.controller('subordinate')
            except:
                helpers.test_failure(c.rest.error())
                return False
            else:
                try:
                    conn = SSH2()
                    conn.connect(c.ip)
                    conn.login(Account("admin", "adminadmin"))
                    conn.execute('debug bash')
                    conn.execute("echo '#!/bin/bash' > test.sh")
                    conn.execute("echo 'sleep 15' >> test.sh")
                    conn.execute("echo 'sudo ifconfig eth0 down' >> test.sh")
                    conn.execute("echo 'sleep 10' >> test.sh")
                    conn.execute("echo 'sudo ifconfig eth0 up' >> test.sh")
                    conn.execute("echo 'sleep 10' >> test.sh")
                    conn.execute("sh test.sh &")
                    helpers.sleep(float(30))
                    conn.send('exit\r')
                    conn.close()
                except:
                    helpers.test_failure(c.rest.error())
                    return False
                else:
                    return True

#########################################################
# All Common Controller Platform related Commands Go Here
#########################################################

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
            c = t.controller('main')
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
            c = t.controller('main')
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
            c = t.controller('main')
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
            c = t.controller('main')
            try:
                url = '/rest/v1/model/ntp-server/'
                c.rest.get(url)
            except:
                helpers.test_failure(c.rest.error())
                return False
            else:
                content = c.rest.content()
                return content[0]
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
            c = t.controller('main')
            try:
                url = '/rest/v1/model/ntp-server/'
                c.rest.put(url, {"enabled": True, "server": str(ntp_server)})
            except:
                helpers.test_failure(c.rest.error())
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
            c = t.controller('main')
            try:
                url = '/rest/v1/model/ntp-server/?enabled=True&server=%s' % (str(ntp_server))
                c.rest.delete(url, {})
            except:
                helpers.test_failure(c.rest.error())
                return False
            else:
                helpers.test_log(c.rest.content_json())
                return True

# #SNMP##

############### SNMP SHOW COMMANDS ########################

    def rest_snmp_show(self):
        '''Execute CLI Command "show snmp"
        
            Input: N/A
            
            Returns: dictionary of SNMP related values
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('main')
            try:
                url = '/rest/v1/model/snmp-server-config/'
                c.rest.get(url)
            except:
                helpers.test_failure(c.rest.error())
                return False
            else:
                content = c.rest.content()
                return content

    def rest_snmp_get(self, snmp_community, snmp_oid):
        '''Execute SNMP Walk from local machine for a particular SNMP OID
        
            Input: SNMP Community and OID
            
            Return Value:  return the SNMP Walk O/P
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('main')
            try:
                url = "/usr/bin/snmpwalk -v2c -c %s %s %s" % (str(snmp_community), c.ip, str(snmp_oid))
                returnVal = subprocess.Popen([url], stdout=subprocess.PIPE, shell=True)
                (out, err) = returnVal.communicate()
            except:
                helpers.test_failure(err)
                return False
            else:
                helpers.log("URL: %s Output: %s" % (url, out))
                return out


    def rest_snmp_getnext(self, snmp_community, snmp_oid):
        '''Execute snmpgetnext from local machine for a particular SNMP OID
        
            Input: SNMP Community and OID
            
            Return Value:  return the SNMP Walk O/P
        '''
        t = test.Test()
        c = t.controller()
        url = "/usr/bin/snmpgetnext -v2c -c %s %s %s" % (str(snmp_community), c.ip, str(snmp_oid))
        returnVal = subprocess.Popen([url], stdout=subprocess.PIPE, shell=True)
        (out, err) = returnVal.communicate()
        helpers.log("URL: %s Output: %s" % (url, out))
        return out


    def rest_snmp_cmd(self, snmp_cmd, snmp_options, snmp_community, snmp_oid):
        '''Execute a generic snmp command from local machine for a particular SNMP OID
        
            Input: 
                `snmp_cmd`        SNMP Command (snmpbulkget/snmpbulkwalk)
                `snmp_options`     SNMP Command options
                `snmp_community`   SNMP Community
                `snmp_oid`         SNMP OID to perform walk on
            
            Return Value:  return the SNMP Walk O/P
        '''
        t = test.Test()
        c = t.controller()
        if snmp_options == "None" or snmp_options == "none":
                snmp_options = " "
        url = "/usr/bin/%s -v2c %s -c %s %s %s" % (str(snmp_cmd), str(snmp_options), str(snmp_community), c.ip, str(snmp_oid))
        returnVal = subprocess.Popen([url], stdout=subprocess.PIPE, shell=True)
        (out, err) = returnVal.communicate()
        helpers.log("URL: %s Output: %s" % (url, out))
        return out

############### SNMP CONFIGURATION COMMANDS ########################

    def rest_set_snmp_server_community(self, snmp_community):
        '''Set SNMP Community String. Similar to CLI command "snmp-server community ro public"
        
           Input: `snmp_community`    SNMP Community name
           
           Return Value:  True if the configuration is successful, false otherwise 
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('main')
            try:
                url = '/rest/v1/model/snmp-server-config/'
                c.rest.put(url, {"id": "snmp", "community": str(snmp_community)})
            except:
                helpers.test_failure(c.rest.error())
                return False
            else:
                helpers.test_log(c.rest.content_json())
                return True

    def rest_set_snmp_server_contact(self, snmp_contact):
        '''Set SNMP Contact. Similar to CLI command "snmp-server contact 'Animesh Patcha'"
        
           Input: `snmp_contact`    SNMP Contact Name
           
           Return Value:  True if the configuration is successful, false otherwise 
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('main')
            try:
                url = '/rest/v1/model/snmp-server-config/?id=snmp'
                c.rest.put(url, {"contact": str(snmp_contact)})
            except:
                helpers.test_failure(c.rest.error())
                return False
            else:
                helpers.test_log(c.rest.content_json())
                return True

    def rest_set_snmp_server_location(self, snmp_location):
        '''Set SNMP Location. Similar to CLI command "snmp-server location 'Mountain View'"
        
           Input: `snmp_contact`    SNMP Location Name
           
           Return Value:  True if the configuration is successful, false otherwise 
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('main')
            try:
                url = '/rest/v1/model/snmp-server-config/?id=snmp'
                c.rest.put(url, {"location": str(snmp_location)})
            except:
                helpers.test_failure(c.rest.error())
                return False
            else:
                helpers.test_log(c.rest.content_json())
                return True

    def rest_set_snmp_server_enable(self):
        '''Enable SNMP Server. Similar to cli command "snmp-server enable"
            
           Input: N/A
           
           Return Value:  True if the configuration is successful, false otherwise 
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('main')
            try:
                url = '/rest/v1/model/snmp-server-config/?id=snmp'
                c.rest.put(url, {"server-enable": True})
            except:
                helpers.test_failure(c.rest.error())
                return False
            else:
                helpers.test_log(c.rest.content_json())
                return True

    def rest_set_snmp_trapserver(self, trap_ip, trap_port):
        '''Configure SNMP Trap Server. Similar to cli command ""snmp-server trap server 10.192.3.22 161"
            
           Input: 
               `trap_ip`    SNMP Trap Server IP Address
               
               `trap_port`  SNMP Trap Server Port Number
           
           Return Value:  True if the configuration is successful, false otherwise 
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('main')
            try:
                url = '/rest/v1/model/snmp-server-config/?id=snmp'
                c.rest.put(url, {"trap-enable": True, "trap-server": str(trap_ip), "trap-port": str(trap_port)})
            except:
                helpers.test_failure(c.rest.error())
                return False
            else:
                helpers.test_log(c.rest.content_json())
                return True

#   Objective: Enable SNMP-TrapServer. Similar to CLI command "snmp-server trap enable"
#   Input: N/A
#   Return Value:  True/False
    def rest_enable_snmp_trapserver(self):
        '''Enable SNMP Trap Server. Similar to cli command "snmp-server trap enable"
            
           Input: N/A
           
           Return Value:  True if the configuration is successful, false otherwise 
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('main')
            try:
                url = '/rest/v1/model/snmp-server-config/?id=snmp'
                c.rest.put(url, {"trap-enable": True, "id": "snmp"})
            except:
                helpers.test_failure(c.rest.error())
                return False
            else:
                helpers.test_log(c.rest.content_json())
                return True

#   Objective: Modify any SNMP Key. Allows you to change community string, contact info string and/or location string
#   Input: SNMP Key, SNMP Value  for example  SNMP Key can be community, and SNMP Value can be bigswitch
#   Return Value:  True/False
    def rest_modify_snmp_key(self, snmpKey, snmpValue):
        '''Modify any SNMP Key. Allows you to change community string, contact info string and/or location string
        
            Input:
                `snmpKey`    SNMP Key to be changed.  for example  SNMP Key can be community, and SNMP Value can be bigswitc
                `snmpValue`  New value that will take effect.
           
           Return Value:  True if the configuration is successful, false otherwise 
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('main')
            try:
                url = '/rest/v1/model/snmp-server-config/?id=snmp'
                if snmpValue == "null":
                        snmpValue1 = None
                else:
                        snmpValue1 = str(snmpValue)

                helpers.test_log("snmpValue1: %s" % snmpValue1)
                c.rest.put(url, { str(snmpKey) : snmpValue1})
            except:
                helpers.test_failure(c.rest.error())
                return False
            else:
                helpers.test_log(c.rest.content_json())
                return True

#   Objective: Modify Firewall to allow port 161 for SNMP Requests from external hosts
#   Input: Controller ID
#   Return Value:  True/False
    def rest_firewall_allow_snmp(self, controller_id):
        '''Modify Firewall to allow port 161 for SNMP Requests from external hosts
            
           Input: N/A
           
           Return Value:  True if the configuration is successful, false otherwise 
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('main')
            try:
                url = '/rest/v1/model/firewall-rule/'
                controller_interface = "%s|Ethernet|0" % (str(controller_id))
                c.rest.put(url, {"interface": str(controller_interface), "vrrp-ip": "", "port": 161, "src-ip": "", "proto": "udp"})
            except:
                helpers.test_failure(c.rest.error())
                return False
            else:
                helpers.test_log(c.rest.content_json())
                return True

#   Objective: Delete SNMP. Similar to "no snmp-server enable"
#   Input: N/A
#   Return Value:  True/False
    def rest_delete_snmp_trapserver(self, trap_port):
        '''Delete SNMP trapserver. Similar to "no snmp-server trap server 10.192.3.22 161"
            
           Input: N/A
           
           Return Value:  True if the configuration is successful, false otherwise 
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('main')
            try:
                url1 = '/rest/v1/model/snmp-server-config/?id=snmp'
                helpers.test_log(url1)
                c.rest.put(url1, {"trap-enable": False, "trap-server": "", "trap-port": int(trap_port)})
            except:
                helpers.test_failure(c.rest.error())
                return False
            else:
                return True

#   Objective: Delete SNMP. Similar to "no snmp-server enable"
#   Input: N/A
#   Return Value:  True/False
    def rest_delete_snmp(self):
        '''Delete SNMP. Similar to "no snmp-server enable"
            
           Input: N/A
           
           Return Value:  True if the configuration is successful, false otherwise 
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('main')
            try:
                url1 = '/rest/v1/model/snmp-server-config/?id=snmp'
                helpers.test_log(url1)
                c.rest.delete(url1, {})
            except:
                helpers.test_failure(c.rest.error())
                return False
            else:
                return True
