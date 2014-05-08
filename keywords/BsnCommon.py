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
import subprocess
import math
import sys
import os
import re
import socket
import paramiko
import os
import pexpect
from paramiko.client import SSHClient
from paramiko.ssh_exception import BadHostKeyException, \
                                   AuthenticationException, \
                                   SSHException
from Exscript.protocols import SSH2
from Exscript import Account
from robot.libraries.BuiltIn import BuiltIn


class BsnCommon(object):

    def __init__(self):
        pass

    def base_suite_setup(self):
        t = test.Test()
        t.topology()

    def base_suite_teardown(self):
        t = test.Test()
        for node in t.topology():
            n = t.node(node)
            if helpers.is_controller(node) or helpers.is_mininet(node):
                helpers.log("Closing device connection for node '%s'" % node)
                n.devconf().close()
        t.teardown()

    def base_test_setup(self):
        test.Test()
        # helpers.log("Test case status: %s"
        #            % helpers.bigrobot_test_case_status())

    def base_test_teardown(self):
        test_status = BuiltIn().get_variable_value("${TEST_STATUS}")
        test_descr = BuiltIn().get_variable_value("${TEST_NAME}")
        if test_status == 'FAIL':
            if helpers.bigrobot_test_postmortem().lower() == 'false':
                helpers.log("Env BIGROBOT_TEST_POSTMORTEM is False."
                            " Skipping test postmortem.")
            else:
                self.base_test_postmortem(test_descr=test_descr)

            if helpers.bigrobot_test_pause_on_fail().lower() == 'true':
                helpers.log("Env BIGROBOT_TEST_PAUSE_ON_FAIL is True.")
                self.pause_on_fail(keyword=test_descr)

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

    def base_test_postmortem(self, test_descr=None):
        t = test.Test()

        helpers.log("Test case '%s' failed. Performing postmortem."
                    % test_descr)
        for node in t.topology():
            # Do postmortem thingy here...
            # - Save output file(s) to bigrobot log directory. The log path is:
            #     bigrobot_path = helpers.bigrobot_log_path_exec_instance()
            # - Look at https://github.com/bigswitch/t6-misc/blob/master/t6-support/run_show_cmds.py
            # - Execute the command using helpers.run_cmd(), e.g.,
            #     cmd = 'cd <bigrobot_log>; <path>/ run_show_cmds.py'
            #     status, msg = helpers.run_cmd(cmd, shell=True)
            # - Name tarbar using the test_descr (be sure to convert
            #   whitespace to underscore).
            if re.match(r'c\d+', node):
                helpers.log("Collecting information for Controller node '%s' (%s)"
                            % (node, self.get_node_ip(node)))
                output_dir = helpers.bigrobot_log_path_exec_instance()
                helpers.log("Outpput dir for var logs : %s" % output_dir)
                # sys.exit(1)
                temp_dir = test_descr.replace(' ', '_')
                show_cmd_out_file = output_dir + '/' + temp_dir + '_' + node + '/shw_cmd_out.txt'
                d = os.path.dirname(show_cmd_out_file)
                if not os.path.exists(d):
                    os.makedirs(d)
                out_file = open(show_cmd_out_file, 'w')
                cmdlist = [
                           'show running-config details',
                           'show debug counters',
                           'show bvssetting',
                           'show cluster details',
                           'show switch all details',
                           'show switch all interface',
                           'show switch all interface properties',
                           'show lacp',
                           'show lag',
                           'show link',
                           'show port-group',
                           'show fabric warn',
                           'show fabric error',
                           'show tenant',
                           'show vns',
                           'show endpoint',
                           'show attachment-points',
                           'show router',
                           'show segment-interface',
                           'show tenant-interface',
                           'show forwarding',
                           'show forwarding internal',
                           'show vft',
                           'show debug events',
                           ]
                for cmd in cmdlist:
                        helpers.log("running cmd : %s" % cmd)
                        content = self.config(node, cmd)
                        out_file.write(content['content'])
                        out_file.write('\n')
                helpers.log("Success running all debug Show cmds!!!!")
                out_file.close()
                scpChild = pexpect.spawn('scp -o "UserKnownHostsFile /dev/null" -o "StrictHostKeyChecking no" -r recovery@%s:/var/log/* %s/.'
                                         % (self.get_node_ip(node), d))
                # Fetch the floodlight logs and dump them in techsupport
                opt = scpChild.expect (['password:', 'yes/no'])
                if opt == 1:
                    scpChild.sendline('yes')
                    scpChild.expect('password')
                password = 'bsn'
                scpChild.sendline (password)
                scpChild.wait()
                helpers.log("Success SCPing all the var logs contents from Controller %s!!" % self.get_node_ip(node))
                # Generate a tar file of the output
                tar_file = temp_dir + '_' + node + ".tar.gz"
                output_dir = d
                subprocess.Popen(['tar', '-pczf', tar_file, output_dir])
                helpers.log('Tech support present in tar file %s' % tar_file)

    def pause_on_fail(self, keyword=None, msg=None):
        """
        Pause execution. Press Control-D to continue.

        Inputs:
        | msg | Message to display when paused. Else print "Pausing... Press Ctrl-D to continue." |

        Return Value:
        - True
        """
        descr = ("Pausing due to test failure...\n'%s' failed." % keyword)
        if helpers.bigrobot_continuous_integration().lower() == 'false':
            return self.pause(descr + "\nPress Ctrl-D to continue...")

        lock = os.path.join(helpers.bigrobot_log_path_exec_instance(),
                            'pause_on_fail_test.lock')
        helpers.file_touch(lock)
        if not msg:
            msg = ("%s\nTo unpause, remove lock '%s'." % (descr, lock))
        helpers.warn(msg)
        while True:
            if helpers.file_exists(lock):
                helpers.sleep(1)
            else:
                helpers.warn("Lock is removed ('%s'). Unpausing..." % lock)
                break
        return True

    def pause(self, msg=None):
        """
        Pause execution. Press Control-D to continue.

        Inputs:
        | msg | Message to display when paused. Else print "Pausing... Press Ctrl-D to continue..." |

        Return Value:
        - True
        """
        if not msg:
            msg = "Pausing... Press Ctrl-D to continue..."
        helpers.warn(msg)
        for _ in sys.stdin:
            pass
        return True

    def ixia_verify_traffic_rate(self, tx_value, rx_value, rangev=5):
        tx = math.ceil(float(tx_value))
        rx = math.ceil(float(rx_value))
        vrange = int(rangev)
        if (rx >= (tx - vrange)) and (rx <= (tx + vrange)):
            helpers.log("Pass: Value1:%d, Value2:%d" % (tx, rx))
            return True
        else:
            helpers.test_failure("Fail: Value1:%d, Value2:%d" % (tx, rx))
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
                    try:
                        t.node_reconnect(node='master')
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
                    except:
                        t.node_reconnect(node='master')
                        return False
                    else:
                        if local is True:
                            t.node_reconnect(node='master')
                        return output_value
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
                        t.node_reconnect(node='master')
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
        helpers.log("Platform is %s" % (n.platform()))
        if helpers.is_switch(node):
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
                helpers.test_error("Unsupported Switch Platform %s" % (node))
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
                url_get_ntp = '/api/v1/data/controller/os/config/global/time-config?config=true'
                c.rest.get(url_get_ntp)
                content = c.rest.content()
                if ('ntp-server' in content[0]):
                    ntp_list = content[0]['ntp-server']
                    ntp_list.append(ntp_server)
                    url = '/api/v1/data/controller/os/config/global/time-config/ntp-server'
                    c.rest.patch(url, ntp_list)
                else:
                    url = '/api/v1/data/controller/os/config/global/time-config/ntp-server'
                    helpers.log("URL is %s \n and \n ntp server is %s" % (url, ntp_server))
                    c.rest.patch(url, [str(ntp_server)])
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

            if  helpers.is_bigtap(n.platform()):
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
            elif helpers.is_bigwire(n.platform()):
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
            elif helpers.is_t5(n.platform()):
                '''
                    T5 Controller NTP Server Deletion goes here
                '''
                c = t.controller()
                url = '/api/v1/data/controller/os/config/global/time-config'
                helpers.log("URL is %s" % url)
                c.rest.delete(url, {"ntp-servers": [ntp_server]})
                if not c.rest.status_code_ok():
                    helpers.test_log(c.rest.error())
                    return False
                else:
                    helpers.sleep(1)
                    return True
            else:
                helpers.test_error("Unsupported Platform %s" % (node))
        else:
            helpers.test_error("Unsupported Platform %s" % (node))

    def add_ntp_timezone(self, node=None, time_zone='America/Los_Angeles'):
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
                TimeZone Configuration at Switch
                '''
                return True
            else:
                helpers.test_error("Unsupported Platform %s" % (node))
        elif helpers.is_controller(node):
            helpers.log("The node is a controller")
            if helpers.is_bigtap(n.platform()):
                '''
                BigTap TimeZone Configuration goes here
                '''
                helpers.log("The node is a BigTap Controller")
                c = t.controller('master')
                url = '/rest/v1/model/controller-node/'
                c.rest.get(url)
                content = c.rest.content()
                count = 0
                for j in range(0, 2):
                    controller_id = content[j]['id']
                    url1 = '/rest/v1/model/controller-node/?id=%s' % controller_id
                    c.rest.put(url1, {"time-zone": str(time_zone)})
                    if not c.rest.status_code_ok():
                        helpers.test_failure(c.rest.error())
                        return False
                    else:
                        count = count + 1
                if count == 2:
                    return True
                else:
                    return False
            elif helpers.is_bigwire(n.platform()):
                '''
                BigWire TimeZone Configuration goes here
                '''
                helpers.log("The node is a BigTap Controller")
                c = t.controller('master')
                url = '/rest/v1/model/controller-node/'
                c.rest.get(url)
                content = c.rest.content()
                count = 0
                for j in range(0, 2):
                    controller_id = content[j]['id']
                    url1 = '/rest/v1/model/controller-node/?id=%s' % controller_id
                    c.rest.put(url1, {"time-zone": str(time_zone)})
                    if not c.rest.status_code_ok():
                        helpers.test_failure(c.rest.error())
                        return False
                    else:
                        count = count + 1
                if count == 2:
                    return True
                else:
                    return False
            elif helpers.is_t5(n.platform()):
                '''
                    T5 Controller
                '''
                helpers.log("The node is a T5 Controller")
                c = t.controller()
                url = '/api/v1/data/controller/os/config/global/time-config'
                helpers.log("URL is %s \n and \n ntp server is %s" % (url, time_zone))
                c.rest.patch(url, {"time-zone": str(time_zone)})
                if not c.rest.status_code_ok():
                    helpers.test_log(c.rest.error())
                    return False
                else:
                    return True
            else:
                helpers.test_error("Unsupported Platform %s" % (node))
        else:
            helpers.test_error("Unsupported Platform %s" % (node))


    def delete_ntp_timezone(self, node=None, time_zone='America/Los_Angeles'):
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
                TimeZone Configuration at Switch
                '''
                return True
            else:
                helpers.test_error("Unsupported Platform %s" % (node))
        elif helpers.is_controller(node):
            helpers.log("The node is a controller")
            if helpers.is_bigtap(n.platform()):
                '''
                BigTap TimeZone Configuration goes here
                '''
            elif helpers.is_bigwire(n.platform()):
                '''
                BigWire TimeZone Configuration goes here
                '''
            elif helpers.is_t5(n.platform()):
                '''
                    T5 Controller
                '''
                helpers.log("The node is a T5 Controller")
                c = t.controller()
                url = '/api/v1/data/controller/os/config/global/time-config/time-zone'
                helpers.log("URL is %s \n and \n ntp server is %s" % (url, time_zone))
                c.rest.delete(url, {})
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
                c = t.controller(node)
                try:
                    url = '/api/v1/data/controller/os/action/time/ntp'
                    c.rest.get(url)
                except:
                    helpers.test_failure(c.rest.error())
                    return False
                else:
                    content = c.rest.content()
                    pass_flag = False
                    bashcommand = "/usr/bin/host %s" % (str(ntp_server))
                    returnVal = subprocess.Popen([bashcommand], stdout=subprocess.PIPE, shell=True)
                    (out, _) = returnVal.communicate()
                    iparray = re.split('\s+', out)
                    helpers.log("NTP Server IP is %s" % iparray[3])
                    helpers.log("Length of content is %s" % len(content))
                    for x in range(0, len(content)):
                        if iparray[3] in content[x]['status']:
                            helpers.log("Value of content is %s" % content[x]['status'])
                            pass_flag = True
                            break
                    if pass_flag:
                        return True
                    else:
                        return False
            else:
                helpers.test_error("Unsupported Platform %s" % (node))
        else:
            helpers.test_error("Unsupported Platform %s" % (node))



    def verify_timezone(self, node, ntp_zone):
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
        elif helpers.is_controller(node):
            helpers.log("The node is a controller")
            if  helpers.is_bigtap(n.platform()):
                '''
                    BigTap NTP Server Verification goes here
                '''

            elif helpers.is_bigwire(n.platform()):
                '''
                    BigWire NTP Server Verification goes here
                '''

            elif helpers.is_t5(n.platform()):
                '''
                    T5 Controller NTP Server Verification goes here
                '''
                c = t.controller(node)
                bashcommand = "date +%Z"
                returnVal = c.bash(bashcommand)
                helpers.log("Output is %s" % returnVal['content'])
                out = returnVal['content'].split('\n')
                helpers.log("Output is %s" % out)
                if str(ntp_zone) in out[1] :
                    return True
                else:
                    return False
            else:
                helpers.test_error("Unsupported Platform %s" % (node))
        else:
            helpers.test_error("Unsupported Platform %s" % (node))

######################################################################
##########   PLATFORM SNMP
######################################################################

    def rest_show_snmp(self, node="master"):
        '''Execute CLI Command "show snmp"

            Input: N/A

            Returns: dictionary of SNMP related values
        '''
        t = test.Test()
        n = t.node(node)
        if helpers.is_controller(node):
            helpers.log("The node is a controller")
            if helpers.is_bigtap(n.platform()):
                '''
                BigTap SNMP Configuration goes here
                '''
                helpers.log("The node is a BigTap Controller")
                c = t.controller('master')
                try:
                    url = '/rest/v1/model/snmp-server-config/'
                    c.rest.get(url)
                except:
                    helpers.test_failure(c.rest.error())
                    return False
                else:
                    content = c.rest.content()
                    return content
            elif helpers.is_bigwire(n.platform()):
                '''
                BigWire SNMP Configuration goes here
                '''
                helpers.log("The node is a BigTap Controller")
                c = t.controller('master')
                try:
                    url = '/rest/v1/model/snmp-server-config/'
                    c.rest.get(url)
                except:
                    helpers.test_failure(c.rest.error())
                    return False
                else:
                    content = c.rest.content()
                    return content
            elif helpers.is_t5(n.platform()):
                '''
                    T5 Controller
                '''
                helpers.log("The node is a T5 Controller")
                c = t.controller('master')
                try:
                    url = '/api/v1/data/controller/os/config/global/snmp-config'
                    c.rest.get(url)
                except:
                    helpers.test_failure(c.rest.error())
                    return False
                else:
                    content = c.rest.content()
                    return content
            else:
                helpers.test_error("Unsupported Platform %s" % (node))
        else:
            helpers.test_error("Unsupported Platform %s" % (node))

    def rest_show_snmp_host(self, node="master"):
        '''Execute CLI Command "show snmp"

            Input: N/A

            Returns: dictionary of SNMP related values
        '''
        t = test.Test()
        n = t.node(node)
        if helpers.is_controller(node):
            helpers.log("The node is a controller")
            if helpers.is_bigtap(n.platform()):
                '''
                BigTap SNMP Configuration goes here
                '''
                helpers.log("The node is a BigTap Controller")
                c = t.controller('master')
                try:
                    url = '/rest/v1/model/snmp-host-config/'
                    c.rest.get(url)
                except:
                    helpers.test_failure(c.rest.error())
                    return False
                else:
                    content = c.rest.content()
                    return content
            elif helpers.is_bigwire(n.platform()):
                '''
                BigWire SNMP Configuration goes here
                '''
                helpers.log("The node is a BigTap Controller")
                c = t.controller('master')
                try:
                    url = '/rest/v1/model/snmp-host-config/'
                    c.rest.get(url)
                except:
                    helpers.test_failure(c.rest.error())
                    return False
                else:
                    content = c.rest.content()
                    return content
            else:
                helpers.test_error("Unsupported Platform %s" % (node))
        else:
            helpers.test_error("Unsupported Platform %s" % (node))

    def rest_add_snmp_keyword(self, keyword, value, node="master"):
        '''
            Objective:
            - Add snmp-server community, contact, location etc

            Input:
                `keyword`       DPID of the Switch

            Returns: True if the interface is up, false otherwise
        '''
        t = test.Test()
        n = t.node(node)
        if helpers.is_controller(node):
            helpers.log("The node is a controller")
            if helpers.is_bigtap(n.platform()):
                '''
                BigTap SNMP Configuration goes here
                '''
                helpers.log("The node is a BigTap Controller")
                c = t.controller('master')
                try:
                        url = '/rest/v1/model/snmp-server-config/?id=snmp'
                        if "trap-enable" in keyword:
                            if "True" in value:
                                c.rest.put(url, {"trap-enable": True})
                            else:
                                c.rest.put(url, {"trap-enable": False})
                        elif "null" in value:
                            c.rest.put(url, {str(keyword): None})
                        else:
                            c.rest.put(url, {str(keyword): str(value)})
                except:
                        helpers.log(c.rest.error())
                        return False
                else:
                        return True
            elif helpers.is_bigwire(n.platform()):
                '''
                BigWire SNMP Configuration goes here
                '''
                helpers.log("The node is a BigTap Controller")
                c = t.controller('master')
                try:
                        url = '/rest/v1/model/snmp-server-config/?id=snmp'
                        if "trap-enable" in keyword:
                            if "True" in value:
                                c.rest.put(url, {"trap-enable": True})
                            else:
                                c.rest.put(url, {"trap-enable": False})
                        elif "null" in value:
                            c.rest.put(url, {str(keyword): None})
                        else:
                            c.rest.put(url, {str(keyword): str(value)})
                except:
                        helpers.log(c.rest.error())
                        return False
                else:
                        return True
            elif helpers.is_t5(n.platform()):
                '''
                    T5 Controller
                '''
                helpers.log("The node is a T5 Controller")
                try:
                    c = t.controller("master")
                    url = '/api/v1/data/controller/os/config/global/snmp-config'
                    if "trap-enabled" in keyword:
                        if "True" in value:
                            c.rest.patch(url, {"trap-enabled": True})
                        else:
                            c.rest.patch(url, {"trap-enable": False})
                    elif "null" in value:
                        url1 = url + '/' + str(keyword)
                        c.rest.delete(url1, {})
                    else:
                        c.rest.patch(url, {str(keyword): str(value)})
                except:
                        helpers.log(c.rest.error())
                        return False
                else:
                        return True
            else:
                helpers.test_error("Unsupported Platform %s" % (node))
        else:
            helpers.test_error("Unsupported Platform %s" % (node))


    def rest_add_snmp_host (self, host, udp_port, node="master"):
        '''
            Objective:
            - Add snmp-server host

            Input:
                `host`       DPID of the Switch
                `udp_port`    UDP Port

            Returns: True if the interface is up, false otherwise
        '''
        t = test.Test()
        n = t.node(node)
        if helpers.is_controller(node):
            helpers.log("The node is a controller")
            if helpers.is_bigtap(n.platform()):
                '''
                BigTap SNMP Configuration goes here
                '''
                helpers.log("The node is a BigTap Controller")
                c = t.controller('master')
                try:
                    url = '/rest/v1/model/snmp-host-config/'
                    c.rest.put(url, {"host": str(host), "udp-port": int(udp_port)})
                except:
                    helpers.log(c.rest.error())
                    return False
                else:
                    return True
            elif helpers.is_bigwire(n.platform()):
                '''
                BigWire SNMP Configuration goes here
                '''
                helpers.log("The node is a BigTap Controller")
                c = t.controller('master')
                try:
                    url = '/rest/v1/model/snmp-host-config/'
                    c.rest.put(url, {"host": str(host), "udp-port": int(udp_port)})
                except:
                    helpers.log(c.rest.error())
                    return False
                else:
                    return True
            elif helpers.is_t5(n.platform()):
                '''
                    T5 Controller
                '''
                helpers.log("The node is a T5 Controller")
                c = t.controller('master')
                try:
                    url = '/api/v1/data/controller/os/config/global/snmp-config/trap-host[ipaddr="%s"]' % str(host)
                    c.rest.put(url, {"ipaddr": str(host), "udp-port": int(udp_port)})
                except:
                    helpers.log(c.rest.error())
                    return False
                else:
                    return True
            else:
                helpers.test_error("Unsupported Platform %s" % (node))
        else:
            helpers.test_error("Unsupported Platform %s" % (node))


    def rest_delete_snmp_host(self, host, udp_port, node="master"):
        '''
            Objective:
            - Delete snmp-server host

            Input:
                `host`       DPID of the Switch
                `udp_port`    UDP Port

            Returns: True if the interface is up, false otherwise
        '''
        t = test.Test()
        n = t.node(node)
        if helpers.is_controller(node):
            helpers.log("The node is a controller")
            if helpers.is_bigtap(n.platform()):
                '''
                BigTap SNMP Configuration goes here
                '''
                helpers.log("The node is a BigTap Controller")
                c = t.controller('master')
                try:
                    url = '/rest/v1/model/snmp-host-config/?host=%s&udp-port=%s' % (host, udp_port)
                    c.rest.delete(url, {})
                except:
                    helpers.log(c.rest.error())
                    return False
                else:
                    return True
            elif helpers.is_bigwire(n.platform()):
                '''
                BigWire SNMP Configuration goes here
                '''
                helpers.log("The node is a BigTap Controller")
                c = t.controller('master')
                try:
                    url = '/rest/v1/model/snmp-host-config/?host=%s&udp-port=%s' % (host, udp_port)
                    c.rest.delete(url, {})
                except:
                    helpers.log(c.rest.error())
                    return False
                else:
                    return True
            elif helpers.is_t5(n.platform()):
                '''
                    T5 Controller
                '''
                helpers.log("The node is a T5 Controller")
                c = t.controller('master')
                try:
                    url = '/api/v1/data/controller/os/config/global/snmp-config/trap-host[ipaddr="%s"]' % str(host)
                    c.rest.delete(url, {"udp-port": int(udp_port)})
                except:
                    helpers.log(c.rest.error())
                    return False
                else:
                    return True
            else:
                helpers.test_error("Unsupported Platform %s" % (node))
        else:
            helpers.test_error("Unsupported Platform %s" % (node))

    def return_snmp_value(self, orignal_string):
        temp_array = orignal_string.split()
        array_length = len(temp_array)
        return temp_array[array_length - 1]

    def rest_add_firewall_rule(self, service="snmp", protocol="udp", proto_port="162", node="master"):
        '''
            Objective:
            - Open firewall port to allow UDP port

            Input:
                `udp_port`    UDP Port

            Returns: True if the configuration is successful, false otherwise
        '''
        t = test.Test()
        n = t.node(node)
        if helpers.is_controller(node):
            helpers.log("The node is a controller")
            if helpers.is_bigtap(n.platform()):
                '''
                BigTap SNMP Configuration goes here
                '''
                helpers.log("The node is a BigTap Controller")
                c1 = t.controller('master')
                c2 = t.controller('slave')
                try:
                    # Get Cluster Names:
                    url1 = "/rest/v1/system/controller"
                    c1.rest.get(url1)
                    master_output = c1.rest.content()
                    c2.rest.get(url1)
                    slave_output = c2.rest.content()
                    master_clustername = master_output['id']
                    slave_clustername = slave_output['id']
                    # Open Firewall
                    url2 = '/rest/v1/model/firewall-rule/'
                    interface_master = master_clustername + "|Ethernet|0"
                    interface_slave = slave_clustername + "|Ethernet|0"
                    c1.rest.put(url2, {"interface": str(interface_master), "vrrp-ip": "", "port": int(proto_port), "src-ip": "", "proto": str(protocol)})
                    c2.rest.put(url2, {"interface": str(interface_slave), "vrrp-ip": "", "port": int(proto_port), "src-ip": "", "proto": str(protocol)})
                except:
                    helpers.log(c1.rest.error())
                    helpers.log(c2.rest.error())
                    return False
                else:
                    return True
            elif helpers.is_bigwire(n.platform()):
                '''
                BigWire SNMP Configuration goes here
                '''
                helpers.log("The node is a BigTap Controller")
                c1 = t.controller('master')
                c2 = t.controller('slave')
                try:
                    # Get Cluster Names:
                    url1 = "/rest/v1/system/controller"
                    c1.rest.get(url1)
                    master_output = c1.rest.content()
                    c2.rest.get(url1)
                    slave_output = c2.rest.content()
                    master_clustername = master_output['id']
                    slave_clustername = slave_output['id']
                    # Open Firewall
                    url2 = '/rest/v1/model/firewall-rule/'
                    interface_master = master_clustername + "|Ethernet|0"
                    interface_slave = slave_clustername + "|Ethernet|0"
                    c1.rest.put(url2, {"interface": str(interface_master), "vrrp-ip": "", "port": int(proto_port), "src-ip": "", "proto": str(protocol)})
                    c2.rest.put(url2, {"interface": str(interface_slave), "vrrp-ip": "", "port": int(proto_port), "src-ip": "", "proto": str(protocol)})
                except:
                    helpers.log(c1.rest.error())
                    helpers.log(c2.rest.error())
                    return False
                else:
                    return True
            elif helpers.is_t5(n.platform()):
                '''
                    T5 Controller
                '''
                helpers.log("The node is a T5 Controller")
                c1 = t.controller('master')
                c2 = t.controller('slave')
                try:
                    url = '/api/v1/data/controller/os/config/local-node/network-config/network-interface[type="ethernet"][number=0]/service[service-name="%s"]' % str(service)
                    c1.rest.put(url, {"service-name": str(service)})
                    c2.rest.put(url, {"service-name": str(service)})
                except:
                    return False
                else:
                    return True
            else:
                helpers.test_error("Unsupported Platform %s" % (node))
        else:
            helpers.test_error("Unsupported Platform %s" % (node))

    def rest_delete_firewall_rule(self, service="snmp", protocol="udp", proto_port="162", node="master"):
        '''
            Objective:
            - Open firewall port to allow UDP port

            Input:
                `udp_port`    UDP Port

            Returns: True if the configuration is successful, false otherwise
        '''
        t = test.Test()
        n = t.node(node)
        if helpers.is_controller(node):
            helpers.log("The node is a controller")
            if helpers.is_bigtap(n.platform()):
                '''
                BigTap SNMP Configuration goes here
                '''
                helpers.log("The node is a BigTap Controller")
                c1 = t.controller('master')
                c2 = t.controller('slave')
                try:
                    # Get Cluster Names:
                    url1 = "/rest/v1/system/ha/role reply"
                    c1.rest.get(url1)
                    master_output = c1.rest.content()
                    c2.rest.get(url1)
                    slave_output = c2.rest.content()
                    master_clustername = master_output['clustername']
                    slave_clustername = slave_output['clustername']
                    # Open Firewall
                    interface_master = master_clustername + "|Ethernet|0"
                    interface_slave = slave_clustername + "|Ethernet|0"
                    urlmaster_delete = '/rest/v1/model/firewall-rule/?interface=' + interface_master + '&vrrp-ip=&port=' + str(proto_port) + '&src-ip=&proto=' + str(protocol)
                    urlslave_delete = '/rest/v1/model/firewall-rule/?interface=' + interface_slave + '&vrrp-ip=&port=' + str(proto_port) + '&src-ip=&proto=' + str(protocol)
                    c1.rest.put(interface_slave, {})
                    c2.rest.put(urlslave_delete, {})
                except:
                    helpers.log(c1.rest.error())
                    helpers.log(c2.rest.error())
                    return False
                else:
                    return True
            elif helpers.is_bigwire(n.platform()):
                '''
                BigWire SNMP Configuration goes here
                '''
                helpers.log("The node is a BigTap Controller")
                c1 = t.controller('master')
                c2 = t.controller('slave')
                try:
                    # Get Cluster Names:
                    url1 = "/rest/v1/system/ha/role reply"
                    c1.rest.get(url1)
                    master_output = c1.rest.content()
                    c2.rest.get(url1)
                    slave_output = c2.rest.content()
                    master_clustername = master_output['clustername']
                    slave_clustername = slave_output['clustername']
                    # Open Firewall
                    interface_master = master_clustername + "|Ethernet|0"
                    interface_slave = slave_clustername + "|Ethernet|0"
                    urlmaster_delete = '/rest/v1/model/firewall-rule/?interface=' + interface_master + '&vrrp-ip=&port=' + str(proto_port) + '&src-ip=&proto=' + str(protocol)
                    urlslave_delete = '/rest/v1/model/firewall-rule/?interface=' + interface_slave + '&vrrp-ip=&port=' + str(proto_port) + '&src-ip=&proto=' + str(protocol)
                    c1.rest.put(interface_slave, {})
                    c2.rest.put(urlslave_delete, {})
                except:
                    helpers.log(c1.rest.error())
                    helpers.log(c2.rest.error())
                    return False
                else:
                    return True
            elif helpers.is_t5(n.platform()):
                '''
                    T5 Controller
                '''
                helpers.log("The node is a T5 Controller")
                c1 = t.controller('master')
                c2 = t.controller('slave')
                try:
                    url = '/api/v1/data/controller/os/config/local-node/network-config/network-interface[type="ethernet"][number=0]/service[service-name="%s"]' % str(service)
                    c1.rest.delete(url, {})
                    c2.rest.delete(url, {})
                except:
                    return False
                else:
                    return True
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

    def return_snmptrap_output(self, server, message):
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

    def restart_process_on_controller(self, process_name, node, soft_error=False):
        '''Restart a process on controller

            Input:
               processName        Name of process to be restarted
               controller_role        Where to execute the command. Accepted values are `Master` and `Slave`

           Return Value:  True if the configuration is successful, false otherwise
        '''
        t = test.Test()
        c = t.controller(node)
        try:
            helpers.log("Restarting %s on '%s'" % (process_name, node))
            c.sudo("service %s restart" % process_name)
        except:
            helpers.test_failure("Unable to restart process '%s'"
                                 % process_name, soft_error)
            return False
        else:
            return True

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

    def console(self, node, *args, **kwargs):
        t = test.Test()
        n = t.node(node)
        return n.console(*args, **kwargs)

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

    def get_node_name(self, node):
        """
        Get the name of a node

        Input: logical node name, e.g., 'c1', 'master', 'slave', etc.

        Return Value:  actual node name, e.g., 'c1', 'c2', 's1'
        """
        t = test.Test()
        n = t.node(node)
        return n.name()

    def get_node_id(self, node):
        """
        Get the node-id of a node.

        Input: logical node name, e.g., 'c1', 'master', 'slave', etc.

        Return Value:  actual node-id for BVS platform, else None
        """
        t = test.Test()
        n = t.node(node)
        return n.node_id()

    def get_node_ip(self, node):
        """
        Get the IP address of a node

        Input: logical node name, e.g., 'c1', 'master', 'slave', etc.

        Return Value:  actual IP address
        """
        t = test.Test()
        n = t.node(node)
        return n.ip()

    def get_all_nodes(self):
        """
        Get the names of all nodes used in the test suite.

        Return Value:  List of node names, e.g., ['c1', 'c2', 's1', etc.]
        """
        t = test.Test()
        nodes = t.topology().keys()
        helpers.debug("Nodes used in test suite: %s" % nodes)
        return nodes

    def get_all_controller_nodes(self):
        """
        Get the names of all controller nodes used in the test suite.

        Return Value:  List of controller node names, e.g., ['c1', 'c2', etc.]
        """
        t = test.Test()
        nodes = [n for n in t.topology().keys() if helpers.is_controller(n)]
        helpers.debug("Controller nodes used in test suite: %s" % nodes)
        return nodes

    def get_all_switch_nodes(self):
        """
        Get the names of all switch nodes used in the test suite.

        Return Value:  List of switch node names, e.g., ['s1', 's2', etc.]
        """
        t = test.Test()
        nodes = [n for n in t.topology().keys() if helpers.is_switch(n)]
        helpers.debug("Switch nodes used in test suite: %s" % nodes)
        return nodes

    def get_all_host_nodes(self):
        """
        Get the names of all host nodes used in the test suite.

        Return Value:  List of host node names, e.g., ['h1', 'h2', etc.]
        """
        t = test.Test()
        nodes = [n for n in t.topology().keys() if helpers.is_host(n)]
        helpers.debug("Host nodes used in test suite: %s" % nodes)
        return nodes

    def get_next_mac(self, *args, **kwargs):
        """
        Contributor: Mingtao Yang
        Objective:
        - Generate the next mac/physical address based on the base and step.

        Inputs:
          | base | starting mac address |
          | incr | Value by which we will increment the mac/physical address |

        Usage:
          | macAddr = self.get_next_mac(base,incr) |
        """
        return helpers.get_next_mac(*args, **kwargs)

    def get_next_address(self, *args, **kwargs):
        """
        Contributor: Mingtao Yang
        Objective:
        Generate the next address bases on the base and step.

        Input:
        | addr_type | IPv4/IpV6|
        | base | Starting IP address |
        | incr | Value by which we will increment the IP address|

        Usage:    ipAddr = self.get_next_address(
                              ipv4,'10.0.0.0','0.0.0.1')
                  ipAddr = self.get_next_address(
                              ipv6,'f001:100:0:0:0:0:0:0','0:0:0:0:0:0:0:1:0')
        """
        return helpers.get_next_address(*args, **kwargs)

    def verify_ssh_connection(self, node, sleep=10, iterations=5,
                              user='dummy', password='dummy'):
        """
        Test the SSH connection to see whether it is working.
        SSH authentication is considered a success (it may be because we
        provided a bad user name or password). SSH time out and other
        exceptions will result in failure.

        Inputs:
          - node: 'c1', 's1', 'h1', 'master', etc.
          - sleep: number of seconds to sleep before retry (on failure). Default is 10.
          - iterations: number of retries (on failure). Default is 5.
          - user: user name. Default is 'dummy' which will result in authen failure, but that's okay.
          - password: Default is 'dummy' which will result in authen failure, but that's okay.

        Return Value:
          - True on success
          - False on failure
        """
        t = test.Test()
        n = t.node(node)
        ip = n.ip()

        iterations = int(iterations)
        status = False

        while not status and iterations > 0:
            try:
                ssh = SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(ip, username=user, password=password, timeout=5)
            except AuthenticationException as e:
                print("SSH error: %s But that's okay." % e)
                status = True
            except (BadHostKeyException, SSHException, socket.error) as e:
                print("SSH error: %s" % e)
            else:
                status = True

            iterations -= 1
            if not status and iterations > 0:
                helpers.sleep(sleep)

        return status


