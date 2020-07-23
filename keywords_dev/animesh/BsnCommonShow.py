import autobot.helpers as helpers
import autobot.test as test
import subprocess
from BigTapCommonShow import BigTapCommonShow
from Exscript.protocols import SSH2
from Exscript import Account, Host

class BsnCommonShow(object):

    def __init__(self):
        pass


# Generic Sleep Function
    def sleepnow(self, intTime):
        helpers.sleep(float(intTime))

#   Objective: Execute CLI command "show version"
#   Input: N/A
#   Return Value:  Version String
    def rest_show_version(self):
        t = test.Test()
        c = t.controller('main')
        # url='http://%s:%s/rest/v1/system/version' % (c.ip,c.http_port)
        url = '/rest/v1/system/version'
        c.rest.get(url)
        content = c.rest.content()
        helpers.log("Output: %s" % content[0]['controller'])
        return content[0]['controller']


#   Objective: Return Current Controller Role viz. Main/Subordinate
#   Input: N/A
#   Return Value:  Current Controller Role viz. Main/Subordinate
    def rest_ha_role(self):
        t = test.Test()
        c = t.controller('main')
        # url = '%s/system/ha/role'  % (c.base_url)
        url = '/rest/v1/system/ha/role'
        c.rest.get(url)
        helpers.test_log("Ouput: %s" % c.rest.result_json())
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
        content = c.rest.content()
        return content['role']

#   Objective: Return Current Controller ID
#   Input: N/A
#   Return Value:  Return Current Controller ID
    def rest_controller_id(self):
        t = test.Test()
        c = t.controller('main')
        url = 'http://%s:%s/rest/v1/system/controller' % (c.ip, c.http_port)
        url = '/rest/v1/system/controller'
        c.rest.get(url)
        content = c.rest.content()
        helpers.log("Output: %s" % content['id'])
        return content['id']

#   Objective: Execute CLI Command "show snmp"
#   Input: N/A
#   Return Value:  Return a dictionary of SNMP related values
    def rest_snmp_show(self):
        t = test.Test()
        c = t.controller('main')
        url = 'http://%s:%s/rest/v1/model/snmp-server-config/' % (c.ip, c.http_port)
        url = '/rest/v1/model/snmp-server-config/'
        c.rest.get(url)
        content = c.rest.content()
        helpers.log("Output: %s" % content)
        return content

#   Objective: Given a dictionary, return the value for a particular key
#   Input: Dictionary, index and required key.
#   Return Value:  return the value for a particular key
    def rest_verify_dict_key(self, content, index, key):
        return content[int(index)][str(key)]

#   Objective: Execute SNMP Walk from local machine for a particular SNMP OID
#   Input: SNMP Community and OID
#   Return Value:  return the SNMP Walk O/P
    def rest_snmp_get(self, snmpCommunity, snmpOID):
        t = test.Test()
        c = t.controller('main')
        url = "/usr/bin/snmpwalk -v2c -c %s %s %s" % (str(snmpCommunity), c.ip, str(snmpOID))
        returnVal = subprocess.Popen([url], stdout=subprocess.PIPE, shell=True)
        (out, err) = returnVal.communicate()
        helpers.log("URL: %s Output: %s" % (url, out))
        return out

#   Objective: Execute snmpgetnext from local machine for a particular SNMP OID
#   Input: SNMP Community and OID
#   Return Value:  return the SNMP Walk O/P
    def rest_snmp_getnext(self, snmpCommunity, snmpOID):
        t = test.Test()
        c = t.controller('main')
        url = "/usr/bin/snmpgetnext -v2c -c %s %s %s" % (str(snmpCommunity), c.ip, str(snmpOID))
        returnVal = subprocess.Popen([url], stdout=subprocess.PIPE, shell=True)
        (out, err) = returnVal.communicate()
        helpers.log("URL: %s Output: %s" % (url, out))
        return out


#   Objective: Execute snmpgetnext from local machine for a particular SNMP OID
#   Input: SNMP Community and OID
#   Return Value:  return the SNMP Walk O/P
    def rest_snmp_cmd(self, snmp_cmd, snmpOptions, snmpCommunity, snmpOID):
        t = test.Test()
        c = t.controller('main')
        if snmpOptions == "None" or snmpOptions == "none":
                snmpOptions = " "
        url = "/usr/bin/%s -v2c %s -c %s %s %s" % (str(snmp_cmd), str(snmpOptions), str(snmpCommunity), c.ip, str(snmpOID))
        returnVal = subprocess.Popen([url], stdout=subprocess.PIPE, shell=True)
        (out, err) = returnVal.communicate()
        helpers.log("URL: %s Output: %s" % (url, out))
        return out

# Objective: Return dictionary containing DPID,IP Addresses for every switch connected to current controller
# Input : N/A
# Output: Dictionary of Switch DPID and IP Addresses
    def rest_show_switch(self):
        t = test.Test()
        c = t.controller('main')
        # url='http://%s:%s/api/v1/data/controller/core/switch' % (c.ip,c.http_port)
        url = '/api/v1/data/controller/core/switch'
        helpers.log("URL is %s  " % url)
        c.rest.get(url)
        content = c.rest.content()
        switchDict = {}
        for x in range (0, len(content)):
            switchDict[str(content[x]['inet-address']['ip'])] = str(content[x]['dpid'])
        return switchDict

# Objective: Return DPID of switch, when IP Address is provided
# Input : dictionary of switch
# Output: Dictionary of Switch DPID and IP Addresses
    def return_switch_dpid(self, switchDict, ipAddr):
        helpers.log('Dictionary is %s' % switchDict)
        return switchDict[str(ipAddr)]


    def return_switch_dpid_from_alias(self, switch_alias):
        t = test.Test()
        c = t.controller('main')
        try:
            # url ='http://%s:%s/api/v1/data/controller/core/switch?select=alias' %(c.ip,c.http_port)
            url = '/api/v1/data/controller/core/switch?select=alias'
            c.rest.get(url)
            content = c.rest.content()
            flag = False
            for x in range (0, len(content)):
                if str(content[x]['alias']) == str(switch_alias):
                    return content[x]['dpid']
            return False
        except:
            return False
        return False

    def return_switch_interface_mac(self, interface_name, switch_alias=None, sw_dpid=None):
        '''Return the MAC/Hardware Address of a given interface

            Input:
                `switch_dpid`       DPID of the Switch
                `interface_name`    Interface Name e.g. ethernet13

            Returns: Hardware/MAC Address of Interface
        '''
        t = test.Test()
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
            # url='http://%s:%s/api/v1/data/controller/core/switch[interface/name="%s"][dpid="%s"]?select=interface[name="%s"]' %(c.ip,c.http_port,interface_name,switch_dpid,interface_name)
            c.rest.get(url)
        except:
            helpers.test_failure(c.rest.error())
            return False
        else:
            if not c.rest.status_code_ok():
                helpers.test_failure(c.rest.error())
            content = c.rest.content()
            return content[0]['interface'][0]['hardware-address']

    def verify_interface_is_up(self, interface_name, switch_alias=None, sw_dpid=None):
        '''Verify if a given interface on a given switch is up

            Input:
                `switch_dpid`       DPID of the Switch
                `interface_name`    Interface Name e.g. ethernet13

            Returns: True if the interface is up, false otherwise
        '''
        t = test.Test()
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
            # url='http://%s:%s/api/v1/data/controller/core/switch[interface/name="%s"][dpid="%s"]?select=interface[name="%s"]' %(c.ip,c.http_port,interface_name,switch_dpid,interface_name)
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

    def restart_process_controller(self, process_name, controllerRole):
        '''Restart a process on controller

            Input:
               processName        Name of process to be restarted
               controllerRole        Where to execute the command. Accepted values are `Main` and `Subordinate`
        '''
        t = test.Test()
        if (controllerRole == 'Main'):
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
        return True

    def execute_controller_command_return_output(self, input, controllerRole):
        '''Execute a generic command on the controller and return ouput.

            Input:
                controllerRole        Where to execute the command. Accepted values are `Main` and `Subordinate`
                input            Command to be executed on switch

            Return Value: Output from command execution

            Example:

            |${syslog_op}=  |  execute switch command return output | 10.192.75.7  |  debug ofad 'help; cat /var/log/syslog | grep \"Disabling port port-channel1\"' |

        '''
        t = test.Test()
        if (controllerRole == 'Main'):
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
        return output

    def return_main_subordinate_ip_address(self):
        t = test.Test()
        ip_address_list = {}
        try:
            t.controller('c2')
        except:
            return {'Main':str(t.controller('c1').ip)}
        else:
            if(self.btc.rest_is_c1_main_controller()):
                ip_address_list = {'Main':str(t.controller('c1').ip), 'Subordinate':str(t.controller('c2').ip)}
                return (ip_address_list)
            else:
                ip_address_list = {'Main':str(t.controller('c2').ip), 'Subordinate':str(t.controller('c1').ip)}
                return (ip_address_list)

    def rest_show_ntp(self):
        t = test.Test()
        c = t.controller('main')
        # url='http://%s:%s/rest/v1/model/ntp-server/' % (c.ip,c.http_port)
        url = '/rest/v1/model/ntp-server/'
        helpers.log("URL is %s  " % url)
        c.rest.get(url)
        content = c.rest.content()
        return content[0]


    def rest_show_syslog(self):
        t = test.Test()
        c = t.controller('main')
        # url='http://%s:%s/rest/v1/model/syslog-server/' % (c.ip,c.http_port)
        url = '/rest/v1/model/syslog-server/'
        helpers.log("URL is %s  " % url)
        c.rest.get(url)
        content = c.rest.content()
        return content[0]


    def rest_show_running_config(self):
        t = test.Test()
        c = t.controller()

        # url = '%s/api/v1/data/controller/os/config' % (c.base_url)
        # c.rest.get(url)
        # url = '%s/api/v1/data/controller/core/aaa/local-user' % (c.base_url)
        # c.rest.get(url)
        # url = '%s/api/v1/data/controller/os/config/global/snmp-config' % (c.base_url)
        # c.rest.get(url)
        # url = '%s/api/v1/data/controller/core/switch-config' % (c.base_url)
        # c.rest.get(url)
        # url = '%s/api/v1/data/controller/fabric/port-group' % (c.base_url)
        # c.rest.get(url)
        # url = '%s/api/v1/data/controller/applications/bvs/tenant' % (c.base_url)
        # c.rest.get(url)

        url = '%s/api/v1/data/controller/os/config?config=true reply "[ ]"' % (c.base_url)
        c.rest.get(url)
        url = '%s/api/v1/data/controller/core/aaa/local-user?config=true reply "[ ]"' % (c.base_url)
        c.rest.get(url)
        url = '%s/api/v1/data/controller/os/config/global/snmp?config=true reply "[ ]"' % (c.base_url)
        c.rest.get(url)
        url = '%s/api/v1/data/controller/core/switch-config?config=true reply "[ ]"' % (c.base_url)
        c.rest.get(url)
        url = '%s/api/v1/data/controller/applications/bcf/port-group?config=true reply "[ ]"' % (c.base_url)
        c.rest.get(url)
        url = '%s/api/v1/data/controller/applications/bcf/tenant?config=true reply "[ ]"' % (c.base_url)
        c.rest.get(url)

'''
    def mininet_dump_switch(self, switch):
        t = test.Test()
        mn = t.mininet()
        mn.cli('dumpt6 %s' % (switch))
        helpers.log(mn.cli_content())
curl -g -H 'Cookie: session_cookie=V_00W0VngoQL004KdrZJknmxsZtFrz5c'  'http://127.0.0.1:8080/api/v1/data/controller/os/config'
curl -g -H 'Cookie: session_cookie=V_00W0VngoQL004KdrZJknmxsZtFrz5c'  'http://127.0.0.1:8080/api/v1/data/controller/core/aaa/local-user'
curl -g -H 'Cookie: session_cookie=V_00W0VngoQL004KdrZJknmxsZtFrz5c'  'http://127.0.0.1:8080/api/v1/data/controller/os/config/global/snmp'
curl -g -H 'Cookie: session_cookie=V_00W0VngoQL004KdrZJknmxsZtFrz5c'  'http://127.0.0.1:8080/api/v1/data/controller/core/switch-config'
curl -g -H 'Cookie: session_cookie=V_00W0VngoQL004KdrZJknmxsZtFrz5c'  'http://127.0.0.1:8080/api/v1/data/controller/fabric/port-group'
curl -g -H 'Cookie: session_cookie=V_00W0VngoQL004KdrZJknmxsZtFrz5c'  'http://127.0.0.1:8080/api/v1/data/controller/applications/bvs/tenant'
curl -g -H 'Cookie: session_cookie=V_00W0VngoQL004KdrZJknmxsZtFrz5c'  'http://127.0.0.1:8080/api/v1/data/controller/applications/bvs/tenant?config=true reply "[ ]"'


'''
