'''
###  WARNING !!!!!!!
###
###  This is where common code for all Controller Platforms will go in.
###
###  To commit new code, please contact the Library Owner:
###  Vui Le (vui.le@bigswitch.com)
###
###  DO NOT COMMIT CODE WITHOUT APPROVAL FROM LIBRARY OWNER
###
###  Last Updated: 02/05/2014
###
###  WARNING !!!!!!!
'''

import autobot.helpers as helpers
import autobot.test as test
import Controller
import subprocess
from Exscript.protocols import SSH2
from Exscript import Account, Host

class BsnCommon(object):

    def __init__(self):
        pass

    def base_suite_setup(self):
        test.Test().topology()
        obj = Controller.Controller()
        obj.cli_save_running_config()

    def base_suite_teardown(self):
        t = test.Test()
        t.teardown()
        for n in t.topology():
            node = t.node(n)
            if helpers.is_controller(n) or helpers.is_mininet(n):
                helpers.log("Closing device connection for node '%s'" % n)
                node.dev.close()

    def base_test_setup(self):
        test.Test()

    def base_test_teardown(self):
        pass

    def mock_untested(self):
        print("MOCK UNTESTED")

    def mock_passed(self):
        print("MOCK PASSED")

    def mock_failed(self):
        raise AssertionError("MOCK FAILED")

    def manual_untested(self):
        print("MANUAL UNTESTED")

    def manual_passed(self):
        print("MANUAL PASSED")

    def manual_failed(self):
        raise AssertionError("MANUAL FAILED")

    def summary_log(self, msg):
        helpers.summary_log(msg, level=2)

    def show_test_topology_params(self):
        t = test.Test()
        helpers.log("Test topology params: %s" % helpers.prettify(t.topology_params()))

    def expr(self, s):
        result = eval(s)
        helpers.log("Express '%s' evaluated to '%s'" % (s, result))
        return result

    def ixia_verify_traffic_rate(self, tx_value, rx_value, rangev=5):
        tx = int(tx_value)
        rx = int(rx_value)
        vrange = int(rangev)
        if (rx >= (tx - vrange)) and (rx <= (tx + vrange)):
            helpers.log("Pass:Traffic forwarded between 2 endpoints tx:%d, rx:%d" % (tx, rx))
            return True
        else:
            helpers.test_failure("Fail:Traffic forward between 2 endpoints tx:%d, rx:%d" % (tx, rx))
            return False

    def verify_switch_pkt_stats(self, count1, count2, range1=95, range2=5):
        ''' Verify is value is within range
        '''
        if (count1 >= range1 and count2 < range2) or (count2 >= range1 and count1 < range2):
            helpers.log("Pass: Value is in range")
            return True
        else:
            helpers.test_failure("Fail:Value is not in range")
            return False

    def verify_value_is_in_range(self, count1, range1=0, range2=30):
        ''' Verify is value within range
        '''
        helpers.log("Count is %s and range1 is %s and range2 is %s" % (count1, range1, range2))
        if (int(range1) <= int(count1)) and (int(count1) <= int(range2)):
            helpers.log("Pass: Value is in range")
            return True
        else:
            helpers.test_failure("Fail:Value is not in range")
            return False

    def rest_return_dictionary_from_get(self, url):
        t = test.Test()
        c = t.controller('master')
        c.rest.get(url)
        content = c.rest.content()
        return content

    def params(self, *args, **kwargs):
        """
        Return the value for a params (topo) attribute.

        Inputs:
        | node | reference to switch/controller as defined in .topo file |
        | key  | name of attribute (e.g., 'ip') |
        | default | (option) if attribute is undefined, return the value defined by default |

        Return Value:
        - Value for attribute
        """
        t = test.Test()
        return t.params(*args, **kwargs)

    def verify_dict_key(self, content, index, key):
        ''' Given a dictionary, return the value for a particular key

            Input:Dictionary, index and required key.

            Return Value:  return the value for a particular key
        '''
        return content[index][key]

    def verify_json_key(self, content, index, key):
        ''' Given a dictionary, return the value for a particular key

            Input:Dictionary, index and required key.

            Return Value:  return the value for a particular key
        '''
        return content[int(index)][str(key)]

    def verify_value_exist(self, value, content1, content2):
        '''
            Objective:
            - Given two CLI outputs, verify given string exists in either of them
        '''
        if (value in content1) or (value in content2):
            return True
        else:
            return False

    def rest_show_version(self, node="master", string="version", user="admin", password="adminadmin", local=True):
        t = test.Test()
        n = t.node(node)
        if helpers.is_switch(n.platform()):
            helpers.log("Node is a switch")
            if helpers.is_switchlight(n.platform()):
                '''
                    Switch
                '''
                helpers.log("The node is a SwitchLight switch")
                switch = t.switch(node)
                cli_input_1 = "show version"
                switch.enable(cli_input_1)
                show_output = switch.cli_content()
                return show_output
            else:
                helpers.test_error("Unsupported Platform %s" % (node))
        elif helpers.is_controller(node):
            helpers.log("The node is a controller")
            if helpers.is_bigtap(n.platform()):
                '''
                    BigTap Controller
                '''
                c = t.controller('master')
                url = '/rest/v1/system/version'
                if user == "admin":
                    c.rest.get(url)
                    content = c.rest.content()
                else:
                    c_user = t.node_reconnect(node='master', user=str(user), password=password)
                    c_user.rest.get(url)
                    content = c_user.rest.content()
                    t.node_reconnect(node='master')
                return content[0]['controller']
            elif helpers.is_bigwire(n.platform()):
                '''
                    BigWire Controller
                '''
                c = t.controller('master')
                url = '/rest/v1/system/version'
                if user == "admin":
                    c.rest.get(url)
                    content = c.rest.content()
                else:
                    c_user = t.node_reconnect(node='master', user=str(user), password=password)
                    c_user.rest.get(url)
                    content = c_user.rest.content()
                    t.node_reconnect(node='master')
                return content[0]['controller']
            elif helpers.is_t5(n.platform()):
                '''
                    T5 Controller
                '''
                helpers.log("The node is a T5 Controller")
                c = t.controller()
                url = '/api/v1/data/controller/core/version/appliance'
                if user == "admin":
                    try:
                        c.rest.get(url)
                        content = c.rest.content()
                        output_value = content[0][string]
                    except:
                        return False
                    else:
                        return output_value
                else:
                    try:
                        c_user = t.node_reconnect(node='master', user=str(user), password=password)
                        c_user.rest.get(url)
                        content = c_user.rest.content()
                        output_value = content[0][string]
                    except:
                        t.node_reconnect(node='master')
                        return False
                    else:
                        if local is True:
                            t.node_reconnect(node='master')
                        return output_value
            else:
                helpers.test_error("Unsupported Platform %s" % (node))
        else:
            helpers.test_error("Unsupported Platform %s" % (node))

    def add_ntp_server(self, node=None, ntp_server='0.bigswitch.pool.ntp.org'):
        '''
            Objective: Add an NTP server.

            Inputs:
            | node | reference to switch/controller as defined in .topo file|
            | ntp_server | ntp server that is being configured|

            Return Values:
            - True, if configuration add is successful.
            - False, if configuration add is unsuccessful.
        '''
        t = test.Test()
        n = t.node(node)
        if helpers.is_switch(n.platform()):
            helpers.log("Node is a switch")
            if helpers.is_switchlight(n.platform()):
                '''
                NTP Configuration at Switch
                '''
                helpers.log("The node is a SwitchLight switch")
                switch = t.switch(node)
                cli_input_1 = "ntp server " + str(ntp_server)
                switch.config(cli_input_1)
                cli_input_2 = "ntp enable"
                switch.config(cli_input_2)
                return True
            else:
                helpers.test_error("Unsupported Platform %s" % (node))
        elif helpers.is_controller(node):
            helpers.log("The node is a controller")
            if helpers.is_bigtap(n.platform()):
                '''
                BigTap NTP Configuration goes here
                '''
                helpers.log("The node is a BigTap Controller")
                c = t.controller('master')
                url = '/rest/v1/model/ntp-server/'
                c.rest.put(url, {"enabled": True, "server": str(ntp_server)})
                helpers.test_log("Ouput: %s" % c.rest.result_json())
                if not c.rest.status_code_ok():
                    helpers.test_failure(c.rest.error())
                    return False
                else:
                    helpers.test_log(c.rest.content_json())
                    return True
            elif helpers.is_bigwire(n.platform()):
                '''
                BigWire NTP Configuration goes here
                '''
                helpers.log("The node is a BigWire Controller")
                c = t.controller('master')
                url = '/rest/v1/model/ntp-server/'
                c.rest.put(url, {"enabled": True, "server": str(ntp_server)})
                helpers.test_log("Ouput: %s" % c.rest.result_json())
                if not c.rest.status_code_ok():
                    helpers.test_failure(c.rest.error())
                    return False
                else:
                    helpers.test_log(c.rest.content_json())
                    return True
            elif helpers.is_t5(n.platform()):
                '''
                    T5 Controller
                '''
                helpers.log("The node is a T5 Controller")
                c = t.controller()
                url = '/api/v1/data/controller/os/config/global/time-config'
                c.rest.put(url, {"ntp-server": [ntp_server]})
                if not c.rest.status_code_ok():
                    helpers.test_log(c.rest.error())
                    return False
                else:
                    return True
            else:
                helpers.test_error("Unsupported Platform %s" % (node))
        else:
            helpers.test_error("Unsupported Platform %s" % (node))

    def delete_ntp_server(self, node, ntp_server):
        '''
            Objective: Delete a NTP server.

            Inputs:
            | node | reference to switch/controller as defined in .topo file|
            | ntp_server | ntp server that is being configured|

            Return Values:
            - True, if configuration delete is successful.
            - False, if configuration delete is unsuccessful.
        '''
        t = test.Test()
        n = t.node(node)
        if helpers.is_switch(node):
            helpers.log("Node is a switch")
            if helpers.is_switchlight(n.platform()):
                '''
                    NTP Deletion at Switch
                '''
                switch = t.switch(node)
                cli_input_1 = "no ntp server " + str(ntp_server)
                switch.config(cli_input_1)
                cli_input_2 = "no ntp enable"
                switch.config(cli_input_2)
                return True
            else:
                helpers.test_error("Unsupported Platform %s" % (node))
        elif helpers.is_controller(node):
            helpers.log("The node is a controller")

            if  helpers.is_bigtap(node):
                '''
                    BigTap NTP Server Deletion goes here
                '''
                c = t.controller('master')
                try:
                    url = '/rest/v1/model/ntp-server/?enabled=True&server=%s' % (str(ntp_server))
                    c.rest.delete(url, {})
                except:
                    helpers.test_failure(c.rest.error())
                    return False
                else:
                    helpers.test_log(c.rest.content_json())
                    return True
            elif helpers.is_bigwire(node):
                '''
                    BigWire NTP Server Deletion goes here
                '''
                c = t.controller('master')
                try:
                    url = '/rest/v1/model/ntp-server/?enabled=True&server=%s' % (str(ntp_server))
                    c.rest.delete(url, {})
                except:
                    helpers.test_failure(c.rest.error())
                    return False
                else:
                    helpers.test_log(c.rest.content_json())
                    return True
            elif helpers.is_t5(node):
                '''
                    T5 Controller NTP Server Deletion goes here
                '''
                c = t.controller()
                url = '/api/v1/data/controller/os/config/global/time-config'
                c.rest.delete(url, {"ntp-servers": [ntp_server]})
                if not c.rest.status_code_ok():
                    helpers.test_log(c.rest.error())
                    return False
                else:
                    return True
            else:
                helpers.test_error("Unsupported Platform %s" % (node))
        else:
            helpers.test_error("Unsupported Platform %s" % (node))

    def verify_ntp(self, node, ntp_server):
        '''
            Objective: Verify NTP Server Configuration is seen in running-config and in output of "show ntp server"

             Inputs:
            | node | reference to switch/controller as defined in .topo file|
            | ntp_server | ntp server that is being configured|

            Return Values:
            - True, if configuration delete is successful.
            - False, if configuration delete is unsuccessful.
        '''
        t = test.Test()
        n = t.node(node)
        if helpers.is_switch(node):
            helpers.log("Node is a switch")
            if helpers.is_switchlight(n.platform()):
                '''
                    NTP Verification at Switch
                '''
                switch = t.switch(node)
                pass_count = 0
                cli_input_1 = "show ntp"
                switch.enable(cli_input_1)
                show_output = switch.cli_content()
                if ntp_server in show_output:
                    helpers.test_log("PASS: NTP Server %s was seen in o/p of 'show ntp'" % (ntp_server))
                    pass_count = pass_count + 1
                else:
                    helpers.test_log("FAIL: NTP Server %s was not seen in o/p of 'show ntp'" % (ntp_server))

                switch.enable("show running-config ntp")
                show_output_1 = switch.cli_content()
                if "ntp enable" in show_output_1:
                    helpers.test_log("PASS: Keyword 'ntp enable' was seen in o/p of 'show running-config ntp'")
                    pass_count = pass_count + 1
                else:
                    helpers.test_log("FAIL: Keyword 'ntp enable' was not seen in o/p of 'show running-config ntp'")
                cli_check = "ntp server " + str(ntp_server)
                if cli_check in show_output_1:
                    helpers.test_log("PASS: Keyword 'ntp server %s' was seen in o/p of 'show running-config ntp'" % (ntp_server))
                    pass_count = pass_count + 1
                else:
                    helpers.test_log("FAIL: Keyword 'ntp server %s' was not seen in o/p of 'show running-config ntp'" % (ntp_server))

                if pass_count == 3:
                    return True
                else:
                    return False
        elif helpers.is_controller(node):
            helpers.log("The node is a controller")
            if  helpers.is_bigtap(n.platform()):
                '''
                    BigTap NTP Server Verification goes here
                '''
                c = t.controller('master')
                try:
                    url = '/rest/v1/model/ntp-server/'
                    c.rest.get(url)
                except:
                    helpers.test_failure(c.rest.error())
                    return False
                else:
                    content = c.rest.content()
                    pass_flag = False
                    for x in range(0, len(content)):
                        if content[x] == str(ntp_server):
                            pass_flag = True
                    if pass_flag:
                        return True
                    else:
                        return False

            elif helpers.is_bigwire(n.platform()):
                '''
                    BigWire NTP Server Verification goes here
                '''
                c = t.controller('master')
                try:
                    url = '/rest/v1/model/ntp-server/'
                    c.rest.get(url)
                except:
                    helpers.test_failure(c.rest.error())
                    return False
                else:
                    content = c.rest.content()
                    pass_flag = False
                    for x in range(0, len(content)):
                        if content[x] == str(ntp_server):
                            pass_flag = True
                    if pass_flag:
                        return True
                    else:
                        return False

            elif helpers.is_t5(n.platform()):
                '''
                    T5 Controller NTP Server Verification goes here
                '''
                c = t.controller('master')
                try:
                    url = '/api/v1/data/controller/os/action/time/ntp'
                    c.rest.get(url)
                except:
                    helpers.test_failure(c.rest.error())
                    return False
                else:
                    content = c.rest.content()
                    pass_flag = False
                    helpers.log("Length of content is %s" % len(content))
                    for x in range(0, len(content)):
                        helpers.log("Value of content is %s" % content[x])
                        if content[x] == str(ntp_server):
                            pass_flag = True
                    if pass_flag:
                        return True
                    else:
                        return False
            else:
                helpers.test_error("Unsupported Platform %s" % (node))
        else:
            helpers.test_error("Unsupported Platform %s" % (node))



#   Objective: Execute snmpgetnext from local machine for a particular SNMP OID
#   Input: SNMP Community and OID
#   Return Value:  return the SNMP Walk O/P
    def snmp_cmd(self, node, snmp_cmd, snmpCommunity, snmpOID):
        '''
            Objective:
            - Execute snmp command which do not require options from local machine for a particular SNMP OID

            Input:
            | node | Reference to switch (as defined in .topo file) |
            | snmp_cmd | SNMP Command like snmpwalk, snmpget, snmpgetnext etc. |
            | snmpCommunity | SNMP Community |
            | snmpOID | OID for which walk is being performed |

            Return Value:
            - Output from SNMP Walk.
        '''
        try:
            t = test.Test()
            if "master" in node:
                node = t.controller("master")
            elif "slave" in node:
                node = t.controller("slave")
            else:
                node = t.switch(node)
            url = "/usr/bin/%s -v2c -c %s %s %s" % (str(snmp_cmd), str(snmpCommunity), node.ip(), str(snmpOID))
            returnVal = subprocess.Popen([url], stdout=subprocess.PIPE, shell=True)
            (out, _) = returnVal.communicate()
            helpers.log("URL: %s Output: %s" % (url, out))
            return out
        except:
            helpers.test_failure("Could not execute command. Please check log for errors")
            return False

    def snmp_cmd_opt(self, node, snmp_cmd, snmpOpt, snmpCommunity, snmpOID):
        '''
            Objective:
            - Execute snmp command which  require options from local machine for a particular SNMP OID

            Input:
            | node | Reference to switch (as defined in .topo file) |
            | snmp_cmd | SNMP Command like snmpwalk, snmpget, snmpgetnext etc. |
            | snmpCommunity | SNMP Community |
            | snmpOID | OID for which walk is being performed |

            Return Value:
            - Output from SNMP Walk.
        '''
        try:
            t = test.Test()
            if "master" in node:
                node = t.controller("master")
            elif "slave" in node:
                node = t.controller("slave")
            else:
                node = t.switch(node)
            url = "/usr/bin/%s  -v2c %s -c %s %s %s" % (str(snmp_cmd), str(snmpOpt), str(snmpCommunity), node.ip(), str(snmpOID))
            returnVal = subprocess.Popen([url], stdout=subprocess.PIPE, shell=True)
            (out, _) = returnVal.communicate()
            helpers.log("URL: %s Output: %s" % (url, out))
            return out
        except:
            helpers.test_failure("Could not execute command. Please check log for errors")
            return False

    def snmp_get(self, node, snmp_community, snmp_oid):
        '''Execute SNMP Walk from local machine for a particular SNMP OID

            Input: SNMP Community and OID

            Return Value:  return the SNMP Walk O/P
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            if "master" in node:
                node = t.controller("master")
            elif "slave" in node:
                node = t.controller("slave")
            else:
                node = t.switch(node)
            try:
                url = "/usr/bin/snmpwalk -v2c -c %s %s %s" % (str(snmp_community), node.ip(), str(snmp_oid))
                returnVal = subprocess.Popen([url], stdout=subprocess.PIPE, shell=True)
                (out, _) = returnVal.communicate()
            except:
                return False
            else:
                helpers.log("URL: %s Output: %s" % (url, out))
                return out

    def snmp_getnext(self, node, snmp_community, snmp_oid):
        '''Execute snmpgetnext from local machine for a particular SNMP OID

            Input: SNMP Community and OID

            Return Value:  return the SNMP Walk O/P
        '''
        t = test.Test()
        if "master" in node:
            node = t.controller("master")
        elif "slave" in node:
            node = t.controller("slave")
        else:
            node = t.switch(node)
        url = "/usr/bin/snmpgetnext -v2c -c %s %s %s" % (str(snmp_community), node.ip(), str(snmp_oid))
        returnVal = subprocess.Popen([url], stdout=subprocess.PIPE, shell=True)
        (out, err) = returnVal.communicate()
        helpers.log("URL: %s Output: %s" % (url, out))
        return out

    def clear_snmpttlog(self, server):
        t = test.Test()
        try:
            conn = SSH2()
            conn.connect(server)
            conn.login(Account("root", "bsn"))
            conn.execute("echo > /var/log/snmptt/snmptt.log")
        except:
            return False
        else:
            return True

    def  return_snmptrap_output(self, server, message):
        try:
            conn = SSH2()
            conn.connect(server)
            conn.login(Account("root", "bsn"))
            input = "cat /var/log/snmptt/snmptt.log | grep " + str(message)
            conn.execute(input)
            output = conn.response
        except:
            return False
        else:
            return output

    def cli(self, node, *args, **kwargs):
        t = test.Test()
        n = t.node(node)
        return n.cli(*args, **kwargs)

    def enable(self, node, *args, **kwargs):
        t = test.Test()
        n = t.node(node)
        return n.enable(*args, **kwargs)

    def config(self, node, *args, **kwargs):
        t = test.Test()
        n = t.node(node)
        return n.config(*args, **kwargs)

    def bash(self, node, *args, **kwargs):
        t = test.Test()
        n = t.node(node)
        return n.bash(*args, **kwargs)

    def sudo(self, node, *args, **kwargs):
        t = test.Test()
        n = t.node(node)
        return n.sudo(*args, **kwargs)

    def cli_content(self, node, *args, **kwargs):
        t = test.Test()
        n = t.node(node)
        return n.cli_content(*args, **kwargs)

    def cli_result(self, node, *args, **kwargs):
        t = test.Test()
        n = t.node(node)
        return n.cli_result(*args, **kwargs)

    def bash_content(self, node, *args, **kwargs):
        t = test.Test()
        n = t.node(node)
        return n.bash_content(*args, **kwargs)

    def bash_result(self, node, *args, **kwargs):
        t = test.Test()
        n = t.node(node)
        return n.bash_result(*args, **kwargs)

    def post(self, node, *args, **kwargs):
        t = test.Test()
        n = t.node(node)
        return n.post(*args, **kwargs)

    def get(self, node, *args, **kwargs):
        t = test.Test()
        n = t.node(node)
        return n.get(*args, **kwargs)

    def put(self, node, *args, **kwargs):
        t = test.Test()
        n = t.node(node)
        return n.put(*args, **kwargs)

    def patch(self, node, *args, **kwargs):
        t = test.Test()
        n = t.node(node)
        return n.patch(*args, **kwargs)

    def delete(self, node, *args, **kwargs):
        t = test.Test()
        n = t.node(node)
        return n.delete(*args, **kwargs)

    def rest_content(self, node, *args, **kwargs):
        t = test.Test()
        n = t.node(node)
        return n.rest_content(*args, **kwargs)

    def rest_result(self, node, *args, **kwargs):
        t = test.Test()
        n = t.node(node)
        return n.rest_result(*args, **kwargs)

    def rest_content_json(self, node, *args, **kwargs):
        t = test.Test()
        n = t.node(node)
        return n.rest_content_json(*args, **kwargs)

    def rest_result_json(self, node, *args, **kwargs):
        t = test.Test()
        n = t.node(node)
        return n.rest_result_json(*args, **kwargs)
