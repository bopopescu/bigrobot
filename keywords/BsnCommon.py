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
from paramiko.client import SSHClient
from paramiko.ssh_exception import BadHostKeyException, \
                                   AuthenticationException, \
                                   SSHException
from Exscript.protocols import SSH2
from Exscript import Account
import autobot.utils as br_utils
import autobot.node as a_node
from keywords.Host import Host


class BsnCommon(object):

    def __init__(self):
        pass

    def base_suite_setup(self):
        t = test.Test()
        t.topology()

    def base_suite_teardown(self):
        """
        Attention: It is critical that suite teardown keywords don't fail.
        If suite teardown fails, Robot will flag all the test cases as failed
        even if some or all may have passed. So you might want to handle the
        exceptions to ensure that suite teardown doesn't fail... unless you
        purposely want it to fail - there may be good reasons for doing that
        also.
        """
        if helpers.bigrobot_nose_setup().lower() == 'false':
            from robot.libraries.BuiltIn import BuiltIn
            suite_status = BuiltIn().get_variable_value("${SUITE_STATUS}")
            helpers.bigrobot_test_suite_status(suite_status)
            helpers.log("Test suite status: %s" % suite_status)

        try:
            t = test.Test()
            t.teardown()
            helpers.log("Closing all device connections")
            t.node_disconnect()
        except:
            # Some teardown actions failed. But we don't want suite teardown
            # to ever fail...
            pass

        if self.get_active_node_names():
            # This is mostly like caused when users call t.node_spawn(<ip>) but
            # then forget to close the session. Nodes which are spawned in this
            # manner are not automatically garbage collected.
            helpers.warn("Active nodes found during teardown. Possible memory leaks.")
        return True

    def base_test_setup(self):
        test.Test()
        # helpers.log("Test case status: %s"
        #            % helpers.bigrobot_test_case_status())

    def base_test_teardown(self):
        if helpers.bigrobot_nose_setup().lower() == 'false':
            # Test postmortem is not supported by Nose framework. As a
            # workaround, define it explicitly in the test case instead.
            from robot.libraries.BuiltIn import BuiltIn
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

    def test_passed(self):
        print("TEST PASSED")

    def test_failed(self):
        helpers.test_failure("TEST FAILED")

    def summary_log(self, msg):
        helpers.summary_log(msg, level=2)

    def trace(self, msg):
        helpers.trace(msg, level=2)

    def info(self, msg):
        helpers.info(msg, level=2)

    def warn(self, msg):
        helpers.warn(msg, level=2)

    def debug(self, msg):
        helpers.debug(msg, level=2)

    def show_test_topology_params(self):
        t = test.Test()
        helpers.log("Test topology params: %s"
                    % helpers.prettify(t.topology_params()))

    def expr(self, s):
        """
        We implemented this keyword before becoming aware of the Robot
        built-in 'evaluate' keyword. Please use 'evaluate' instead.
        """
        result = eval(s)
        helpers.log("Express '%s' evaluated to '%s'" % (s, result))
        return result

    def run_cmd(self, *args, **kwargs):
        """
        Execute a command and return its execution status, output, and error
        code.

        Examples:
        | ${output} = | run_cmd | cmd=ls -la /etc | shell=${true} |

        Return Value:
        - Tuple of (<status_flag>,  "<output>", "<err_str>", <errorcode>)

        See helpers.run_cmd2() for more info.
        """
        return helpers.run_cmd2(*args, **kwargs)

    def scp_put(self, server, file_path, dest_path, user="admin", password="adminadmin"):
        """
        Example:
            helpers.scp_get(c.ip(),
                            remote_file='/var/log',
                            local_path='/tmp',
                            user='recovery',
                            password='bsn')

        Limitations: Does not support wildcards.
        """
        helpers.scp_put(server, file_path, dest_path, user, password)

    def scp_get(self, server, remote_file_path, dest_path, user="admin", password="adminadmin"):
        """
        Example:
            helpers.scp_get(c.ip(),
                            remote_file='/var/log',
                            local_path='/tmp',
                            user='recovery',
                            password='bsn')

        Limitations: Does not support wildcards.
        """
        helpers.scp_get(server, remote_file_path, dest_path, user, password)

    def bcf_controller_postmortem(self, node, server, server_devconf,
                                  user, password, dest_path, test_descr=None):
        """
            Generates Support Bundle and SCPs out to File server
        """
        helpers.log("Collecting postmortem information for BCF controller '%s'"
                    % node)

        import keywords.T5Support as T5Support
        support = T5Support.T5Support()
        helpers.log("Deleting old Support Bundles from the BCF Controller: %s" % node)
        support.delete_support_bundles(node)
        result = support.cli_generate_support(node)
        helpers.log("Support File : %s" % str(result))
        support_file = support.get_support_bundle_fs_path(node)
        Host().bash_scp(node,
                        source=support_file,
                        dest='%s@%s:%s' % (user, server, dest_path),
                        password=password, timeout=60)
        helpers.log("Successfully copied Support Files '%s' to '%s:%s'"
                    % (node, server, dest_path))

        # Make sure that all log files are readable. Also compress them to
        # save space.
        server_devconf.sudo('chmod -R +r %s' % dest_path)
        server_devconf.bash('cd %s' % dest_path)
        server_devconf.sudo('gzip -9 --quiet --force'
                            ' *.log *.log.[0-9] *.log.[0-9][0-9]')

    def mininet_postmortem(self, node, server, server_devconf,
                           user, password, dest_path, test_descr=None):
        """
        Executes the Mininet postmortem command.
        Save the command output to the archiver.
        """
        helpers.log("Collecting postmortem information for mininet '%s'"
                    % node)
        output_dir = helpers.bigrobot_log_path_exec_instance()
        show_cmd_file = (output_dir + '/' + test_descr + '_' + node +
                         '/show_cmd_out.txt')
        d = os.path.dirname(show_cmd_file)
        if not os.path.exists(d):
            os.makedirs(d)
        fh = open(show_cmd_file, 'w')

        # Mininet postmortem commands and output
        # May need to separate this section if postmortem is different between
        # T6 Mininet and BigTap Mininet.
        content = self.cli(node, 'bugreport')['content']

        match = re.search(r'^Tarball left at (.+)$', content, re.M)
        fh.write(content)
        fh.write('\n')
        helpers.log("Successfully run all debug commands. Saved to %s."
                    % show_cmd_file)
        fh.close()

        helpers.scp_put(server, show_cmd_file, dest_path, user, password)

        if match:
            mininet_log = match.group(1).strip()
            Host().bash_scp(node,
                            source=mininet_log,
                            dest='%s@%s:%s' % (user, server, dest_path),
                            password=password, timeout=60)
            helpers.log("Successfully copied Mininet log on '%s' to '%s:%s'"
                        % (node, server, dest_path))
        else:
            helpers.log("Mininet log not found.")

    def base_test_postmortem(self, test_descr=None):
        t = test.Test()

        helpers.log("Postmortem begins for test case '%s'" % test_descr)
        server = helpers.bigrobot_log_archiver()
        tester = helpers.get_env('USER')  # individual who executed the script
        user = 'root'
        password = 'bsn'
        dest_path_rel = ("%s/%s" %
                         (tester,
                          helpers.bigrobot_log_path_exec_instance_relative()))
        dest_path = '/var/www/regression_logs/%s' % dest_path_rel
        dest_url = 'http://%s/regression_logs/%s' % (server, dest_path_rel)

        helpers.log("Test case '%s' failed. Performing postmortem."
                    % test_descr)
        if not test_descr:
            test_descr = "no_test_case_descr"
        # convert non-alpha and white spaces to underscores
        test_descr = re.sub(r'[\W\s]', '_', test_descr)

        helpers.log("Creating directory on log archiver %s:%s"
                    % (server, dest_path))

        h = t.node_spawn(ip=server, user=user, password=password,
                         device_type='host')

        for node in t.topology():
            test_dest_path = dest_path + '/' + test_descr + '/' + node
            h.sudo('mkdir -p %s' % test_dest_path)

            if helpers.is_controller(node):
                if helpers.is_bcf(t.node(node).platform()):
                    self.bcf_controller_postmortem(node,
                                               server=server,
                                               server_devconf=h,
                                               user=user, password=password,
                                               dest_path=test_dest_path,
                                               test_descr=test_descr)
                elif helpers.is_bigtap(t.node(node).platform()):
                    # Placeholder for BigTap postmortem
                    pass
            elif helpers.is_mininet(node):
                self.mininet_postmortem(node,
                                        server=server,
                                        server_devconf=h,
                                        user=user, password=password,
                                        dest_path=test_dest_path,
                                        test_descr=test_descr)
            elif helpers.is_switch(node):
                # Placeholder for switch postmortem
                pass

        # Only print the postmortem URL once.
        if t.settings('postmortem_url_is_printed') == None:
            helpers.warn("Postmortem logs are available at %s\n" % dest_url)
            t.settings('postmortem_url_is_printed', True)

        helpers.log("Postmortem logs are also available at\n%s:%s\n"
                    "Note: Files are removed after 30 days unless"
                    " KEEP_FOREVER.txt is found in the directory.%s"
                    % (server, dest_path,
                       br_utils.end_of_output_marker()))
        # In smoketest/regression environment, assume we want to keep the
        # logs forever
        if helpers.bigrobot_continuous_integration().lower() == 'true':
            filename = dest_path + "/KEEP_FOREVER.txt"
            helpers.trace("In regression environment; touch %s" % filename)
            h.sudo("touch %s" % filename)

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
            helpers.log("Pass: Transmit:%d, Receive:%d" % (tx, rx))
            return True
        else:
            helpers.log("Fail: Transmit:%d, Receive:%d" % (tx, rx))
            return False

    def verify_switch_pkt_stats(self, count1, count2, range1=95, range2=5):
        ''' Verify is value is within range
        '''
        if (count1 >= range1 and count2 < range2) or (count2 >= range1 and count1 < range2):
            helpers.log("Pass: Value is in range")
            return True
        else:
            helpers.test_log("Fail:Value is not in range")
            return False

    def verify_value_is_in_range(self, count1, range1=0, range2=30):
        ''' Verify is value within range
        '''
        helpers.log("Count is %s and range1 is %s and range2 is %s" % (count1, range1, range2))
        if (int(range1) <= int(count1)) and (int(count1) <= int(range2)):
            helpers.log("Pass: Value is in range")
            return True
        else:
            helpers.test_log("Fail:Value is not in range")
            return False

    def rest_return_dictionary_from_get(self, url):
        t = test.Test()
        c = t.controller('master')
        c.rest.get(url)
        content = c.rest.content()
        return content

    def params(self, *args, **kwargs):
        """
        Return the value for a params attributes. This will include non-node
        params, such as 'common'.

        Inputs:
        | node | reference to switch/controller as defined in .topo file |
        | key  | name of attribute (e.g., 'ip') |
        | default | (option) if attribute is undefined, return the value defined by default |

        Return Value:
        - Value for attribute
        """
        t = test.Test()
        return t.params(*args, **kwargs)

    def interfaces(self, node, if_name=None, soft_error=False):
        """
        Return the interface on node which is connected to a peer device. The
        convention is to define an interface bundle in the topo file which
        contains the key/value pairs for all the peer connections. The key is
        the alias for the peer and the value is the actual interface on the
        node. Multiple interfaces to the same peer can be specified using the
        format '<alias>_<n>' where <n> is an integer.

        Example topology definition:

           s1:
             interfaces:
               ixia_1: ethernet2
               ixia_2: ethernet3
               s2: ethernet3

        Example usage:

           ${ixia_if} =    interfaces   node=s1   if_name=ixia_1

        Inputs:
        | node | reference to switch/controller as defined in .topo file |
        | if_name  | name of interface in node, e.g., 'ixia_1' |
        | soft_error | Default (False) is to generate an exception on error (e.g., can't find interface). If True, then return (False) and user will perform their own error handling. |

        Return Value:
        - If if_name is not specified, return the whole interfaces dictionary
        - If if_name is specified, return the actual interface name
        """
        node_bundle = self.params(node)
        if 'interfaces' not in node_bundle:
            return helpers.test_error("Node '%s' does not have an interfaces bundle defined"
                                      % node, soft_error=soft_error)
        interfaces = node_bundle['interfaces']
        if if_name == None:
            return interfaces
        if if_name not in interfaces:
            return helpers.test_error("Node '%s' does not have the interface '%s' defined"
                                      % (node, if_name), soft_error=soft_error)
        return interfaces[if_name]

    interface = interfaces

    def params_global(self, *args, **kwargs):
        """
        Return the value for a 'global' params attributes.

        Inputs:
        | key  | name of attribute (e.g., 'my_test_knob') |
        | default | (option) if attribute is undefined, return the value defined by default |

        Return Value:
        - Value for attribute
        """
        t = test.Test()
        return t.params_global(*args, **kwargs)

    def params_nodes(self, *args, **kwargs):
        """
        Return the value for a params node(s) attributes.

        Inputs:
        | node | reference to switch/controller as defined in .topo file |
        | key  | name of attribute (e.g., 'ip') |
        | default | (option) if attribute is undefined, return the value defined by default |

        Return Value:
        - Value for attribute
        """
        t = test.Test()
        return t.params_nodes(*args, **kwargs)

    def verify_dict_key(self, content, index, key):
        ''' Given a dictionary, return the value for a particular key

            Input:Dictionary, index and required key.

            Return Value:  return the value for a particular key
        '''
        return content[index][key]

    def verify_nested_dict_key(self, content, *args):
        ''' Given a nested dictionary, return the final value of the key

            Input:Dictionary, index and required key.

            Return Value:  return the value for a particular key
        '''
        final_result = ''
        for arg in args:
            final_result = content[arg]
            content = content [arg]

        return final_result

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

    def check_version(self, node, version_str, op=">="):
        """
        Compare the node's version string with the specified version_str.
        Supported operations are:
        - node_version_str == version_str
        - node_version_str != version_str
        - node_version_str >  version_str  (default)
        - node_version_str >= version_str
        - node_version_str <  version_str
        - node_version_str <= version_str

        Inputs:
        | node | logical device name (e.g., 'c1', 'c2', 'master', 'slave', 's1', etc.) |
        | version_str | the version string to match against (e.g., '2.1.0') |
        | op | version comparison operator. Default is '>='. Also accepts '==', '!=', '>', '<', '<='. |

        Examples:
        | check_version | node=c1 | version_str=2.0.0 |       | node version must equal or be greater than 2.0.0 (default) |
        | check_version | node=c1 | version_str=2.0.0 | op=== | node version must match 2.0.0 (==) |

        Return Value:
        - True if version comparison matches
        - False if version comparison fails
        """
        def _sanitize_version_str(s):
            """
            Strip cruds in version string to reveal only the version number: x.y.z
            """
            match = re.match(r'^(\d+\.\d+\.\d+).*', s)
            if match:
                return match.group(1)
            else:
                helpers.test_error("Unrecognized version string: '%s'" % s)

        def _version_tuple(s):
            return tuple(map(int, (s.split("."))))

        node_version_str = self.rest_show_version(node, reconnect=False)
        node_version_str = _sanitize_version_str(node_version_str)
        version_str = _sanitize_version_str(version_str)

        if op == '==':
            status = _version_tuple(node_version_str) == _version_tuple(version_str)
        elif op == '!=':
            status = _version_tuple(node_version_str) != _version_tuple(version_str)
        elif op == '>':
            status = _version_tuple(node_version_str) > _version_tuple(version_str)
        elif op == '>=':
            status = _version_tuple(node_version_str) >= _version_tuple(version_str)
        elif op == '<':
            status = _version_tuple(node_version_str) < _version_tuple(version_str)
        elif op == '<=':
            status = _version_tuple(node_version_str) <= _version_tuple(version_str)
        else:
            helpers.test_error("Unsupported version comparison operator: '%s'" % op)

        s = "Version check %s %s %s: %s" % (node_version_str, op, version_str, status)
        if status == False:
            helpers.warn(s, level=3)
        else:
            helpers.log(s, level=3)
        return status

    def rest_show_version(self, node="master", string="version", user="admin", password="adminadmin", local=True, reconnect=True):
        """
        The scope of this function is a bit more than simply 'show version'. It's also used
        to test accounting/authorization (hence the inclusion of node_reconnect). At some
        future time, we should consider splitting this into 2 separate functions - one to perform
        strictly 'show version' and another to do 'show version' via a different
        account/authorization.
        !!! FIXME: Basically, this function is trying to do too much.
        """
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
                        if reconnect:
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
                    except:
                        t.node_reconnect(node='master')
                        return False
                    else:
                        if local is True:
                            t.node_reconnect(node='master', user=str(user), password=password)
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
                c = t.controller('master')
                url = '/api/v1/data/controller/core/version/appliance'
                if user == "admin":
                    try:
                        if reconnect:
                            t.node_reconnect(node='master', user=str(user), password=password)
                        c.rest.get(url)
                        content = c.rest.content()
                        output_value = content[0][string]
                    except:
                        return helpers.test_error("Node connect failed",
                                                  soft_error=True)
                    else:
                        return output_value
                else:
                    try:
                        c_user = t.node_spawn(ip=c.ip(), user=str(user), password=password)
                        c_user.rest.get(url)
                        content = c_user.rest.content()
                        output_value = content[0][string]
                        c_user.close()
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

    def add_ntp_server(self, node='master', ntp_server='0.bigswitch.pool.ntp.org'):
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
                # NTP Configuration at Switch
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
                # BigTap NTP Configuration goes here
                helpers.log("The node is a BigTap Controller")
                c = t.controller(node)
                url = '/rest/v1/model/ntp-server/'
                c.rest.put(url, {"enabled": True, "server": str(ntp_server)})
                helpers.test_log("Ouput: %s" % c.rest.result_json())
                if not c.rest.status_code_ok():
                    helpers.test_log(c.rest.error())
                    return False
                else:
                    helpers.test_log(c.rest.content_json())
                    return True
            elif helpers.is_bigwire(n.platform()):
                # BigWire NTP Configuration goes here
                helpers.log("The node is a BigWire Controller")
                c = t.controller(node)
                url = '/rest/v1/model/ntp-server/'
                c.rest.put(url, {"enabled": True, "server": str(ntp_server)})
                helpers.test_log("Ouput: %s" % c.rest.result_json())
                if not c.rest.status_code_ok():
                    helpers.test_log(c.rest.error())
                    return False
                else:
                    helpers.test_log(c.rest.content_json())
                    return True
            elif helpers.is_t5(n.platform()):
                # T5 Controller
                helpers.log("The node is a T5 Controller")
                c = t.controller(node)
                url_get_ntp = '/api/v1/data/controller/os/config/global/time?config=true'
                c.rest.get(url_get_ntp)
                content = c.rest.content()
                if ('ntp-server' in content[0]):
                    ntp_list = content[0]['ntp-server']
                    ntp_list.append(ntp_server)
                    url = '/api/v1/data/controller/os/config/global/time/ntp-server'
                    c.rest.patch(url, ntp_list)
                else:
                    url = '/api/v1/data/controller/os/config/global/time/ntp-server'
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

    def delete_ntp_server(self, node, ntp_server='0.bigswitch.pool.ntp.org'):
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
                # NTP Deletion at Switch
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
                # BigTap NTP Server Deletion goes here
                c = t.controller(node)
                try:
                    url = '/rest/v1/model/ntp-server/?enabled=True&server=%s' % (str(ntp_server))
                    c.rest.delete(url, {})
                except:
                    helpers.test_log(c.rest.error())
                    return False
                else:
                    helpers.test_log(c.rest.content_json())
                    return True
            elif helpers.is_bigwire(n.platform()):
                # BigWire NTP Server Deletion goes here
                c = t.controller(node)
                try:
                    url = '/rest/v1/model/ntp-server/?enabled=True&server=%s' % (str(ntp_server))
                    c.rest.delete(url, {})
                except:
                    helpers.test_log(c.rest.error())
                    return False
                else:
                    helpers.test_log(c.rest.content_json())
                    return True
            elif helpers.is_t5(n.platform()):
                # T5 Controller NTP Server Deletion goes here
                c = t.controller(node)
                url = '/api/v1/data/controller/os/config/global/time/ntp-server'
                helpers.log("URL is %s" % url)
                ntp_servers = c.rest.get(url)['content']
                helpers.log("Currently configured servers are %s" % ntp_servers)
                if ntp_server in ntp_servers:
                    while ntp_server in ntp_servers:
                        ntp_servers.remove(ntp_server)
                    helpers.log("List of servers after deleting %s is %s"
                                % (ntp_server, ntp_servers))
                    c.rest.put(url, ntp_servers)
                    if not c.rest.status_code_ok():
                        helpers.test_log(c.rest.error())
                        return False
                    updated_ntp_servers = c.rest.get(url)['content']
                    if helpers.list_compare(ntp_servers, updated_ntp_servers):
                        helpers.log("Successfully removed '%s'"
                                    " from NTP server list." % ntp_server)
                        return True
                    else:
                        helpers.log("Unsuccessfully removed '%s'"
                                    " from NTP server list." % ntp_server)
                        return False
                else:
                    helpers.log("NTP server not configured. Nothing to delete.")
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
                # TimeZone Configuration at Switch
                return True
            else:
                helpers.test_error("Unsupported Platform %s" % (node))
        elif helpers.is_controller(node):
            helpers.log("The node is a controller")
            if helpers.is_bigtap(n.platform()):
                # BigTap TimeZone Configuration goes here
                helpers.log("The node is a BigTap Controller")
                c = t.controller(node)
                url = '/rest/v1/model/controller-node/'
                c.rest.get(url)
                content = c.rest.content()
                count = 0
                for j in range(0, 2):
                    controller_id = content[j]['id']
                    url1 = '/rest/v1/model/controller-node/?id=%s' % controller_id
                    c.rest.put(url1, {"time-zone": str(time_zone)})
                    if not c.rest.status_code_ok():
                        helpers.test_log(c.rest.error())
                        return False
                    else:
                        count = count + 1
                if count == 2:
                    return True
                else:
                    return False
            elif helpers.is_bigwire(n.platform()):
                # BigWire TimeZone Configuration goes here
                helpers.log("The node is a BigTap Controller")
                c = t.controller(node)
                url = '/rest/v1/model/controller-node/'
                c.rest.get(url)
                content = c.rest.content()
                count = 0
                for j in range(0, 2):
                    controller_id = content[j]['id']
                    url1 = '/rest/v1/model/controller-node/?id=%s' % controller_id
                    c.rest.put(url1, {"time-zone": str(time_zone)})
                    if not c.rest.status_code_ok():
                        helpers.test_log(c.rest.error())
                        return False
                    else:
                        count = count + 1
                if count == 2:
                    return True
                else:
                    return False
            elif helpers.is_t5(n.platform()):
                # T5 Controller
                helpers.log("The node is a T5 Controller")
                c = t.controller(node)
                url = '/api/v1/data/controller/os/config/global/time'
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
                # TimeZone Configuration at Switch
                return True
            else:
                helpers.test_error("Unsupported Platform %s" % (node))
        elif helpers.is_controller(node):
            helpers.log("The node is a controller")
            if helpers.is_bigtap(n.platform()):
                # BigTap TimeZone Configuration goes here
                pass
            elif helpers.is_bigwire(n.platform()):
                # BigWire TimeZone Configuration goes here
                pass
            elif helpers.is_t5(n.platform()):
                # T5 Controller
                helpers.log("The node is a T5 Controller")
                c = t.controller(node)
                url = '/api/v1/data/controller/os/config/global/time/time-zone'
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
                # NTP Verification at Switch
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
                # BigTap NTP Server Verification goes here
                c = t.controller(node)
                try:
                    url = '/rest/v1/model/ntp-server/'
                    c.rest.get(url)
                except:
                    helpers.test_log(c.rest.error())
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
                # BigWire NTP Server Verification goes here
                c = t.controller(node)
                try:
                    url = '/rest/v1/model/ntp-server/'
                    c.rest.get(url)
                except:
                    helpers.test_log(c.rest.error())
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
                # T5 Controller NTP Server Verification goes here
                c = t.controller(node)
                try:
                    url = '/api/v1/data/controller/os/action/time/ntp'
                    c.rest.get(url)
                except:
                    helpers.test_log(c.rest.error())
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
                        if ntp_server in content[x]['status']:
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
                controller_time_zone = out[1].replace('\r', '')
                helpers.log("Time Zone in Controller: %s Expected: %s\n" % (controller_time_zone, ntp_zone))

                if controller_time_zone in ntp_zone:
                    helpers.log("Expected Time Zone is present")
                    return True
                else:
                    helpers.error_msg("Expected Time Zone is NOT present")
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
                    helpers.test_log(c.rest.error())
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
                    helpers.test_log(c.rest.error())
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
                    url = '/api/v1/data/controller/os/config/global/snmp'
                    c.rest.get(url)
                except:
                    helpers.test_log(c.rest.error())
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
                    helpers.test_log(c.rest.error())
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
                    helpers.test_log(c.rest.error())
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
                    url = '/api/v1/data/controller/os/config/global/snmp'
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
                    url = '/api/v1/data/controller/os/config/global/snmp/trap-host[server="%s"]' % str(host)
                    c.rest.put(url, {"server": str(host), "udp-port": int(udp_port)})
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
                    url = '/api/v1/data/controller/os/config/global/snmp/trap-host[server="%s"]' % str(host)
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

    def return_snmp_value(self, orignal_string, offset=1):
        temp_array = orignal_string.split()
        array_length = len(temp_array)
        temp_array[array_length - int(offset)] = temp_array[array_length - int(offset)].strip()
        temp_array[array_length - int(offset)] = temp_array[array_length - int(offset)].strip('"')
        return temp_array[array_length - int(offset)]

# ## Author: Sahaja
    def rest_verify_snmp_controller(self, node, val, param):
        '''
        Verify if the value is correct
        Input: Value from snmp walk and which type(ex: CPU temperature, Fan, etc)
        Output : True or False
        '''
        # helpers.test_log("Arguments got are 1: {} 2: {} 3: {}".format(node, val, param))
        try:
            t = test.Test()
            n = t.node(node)
        except:
            return False
        else:
            try:
                url = "/rest/v1/environment/data/default/controller/localhost/summary"
                n.rest.get(url)
                out = n.rest.content()
                snmp_dic = dict(zip(map(lambda x: x.lower(), out.keys()), out.values()))
                # helpers.test_log("Here is the hash we got {} and value is {}".format(out, snmp_dic[param.lower()]))
                diff = int(val) - int(snmp_dic[param.lower()].split()[0])
            except:
                return False
            else:
                if abs(diff) < 3:
                    helpers.log("Values are almost the same for module{} observed value is {} expected value is {}".format(param, int(snmp_dic[param.lower()].split()[0]), val))
                    return True
                else:
                    helpers.log("Values are not almost same for module{} observed value is {} expected value is {}".format(param, int(snmp_dic[param.lower()].split()[0]), val))
                    return False

# ## Author: Sahaja

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
                    url = '/api/v1/data/controller/os/config/local/network/interface[type="ethernet"][number=0]/service[name="%s"]' % str(service)
                    c1.rest.put(url, {"name": str(service)})
                    c2.rest.put(url, {"name": str(service)})
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
                helpers.log("The node is a BigTap Controller")
                controller1 = t.controller('master')
                controller2 = t.controller('slave')
                try:
                    # Get Cluster Names:
                    url1 = "/rest/v1/system/ha/role reply"

                    controller1.rest.get(url1)
                    master_output = controller1.rest.content()
                    master_clustername = master_output['clustername']
                    interface_master = master_clustername + "|Ethernet|0"
                    urlmaster_delete = '/rest/v1/model/firewall-rule/?interface=' + interface_master + '&vrrp-ip=&port=' + str(proto_port) + '&src-ip=&proto=' + str(protocol)
                    # controller1.rest.put(interface_slave, {})
                    controller1.rest.put(urlmaster_delete, {})
                except:
                    helpers.log(controller1.rest.error())
                else:
                    try:
                        controller2.rest.get(url1)
                        slave_output = controller2.rest.content()
                        slave_clustername = slave_output['clustername']
                        interface_slave = slave_clustername + "|Ethernet|0"
                        urlslave_delete = '/rest/v1/model/firewall-rule/?interface=' + interface_slave + '&vrrp-ip=&port=' + str(proto_port) + '&src-ip=&proto=' + str(protocol)
                        controller2.rest.put(urlslave_delete, {})
                    except:
                        helpers.log(controller2.rest.error())
                        return False
                    else:
                        return True

            elif helpers.is_bigwire(n.platform()):
                helpers.log("The node is a BigWire Controller")
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
                    # c1.rest.put(interface_slave, {})
                    c1.rest.put(urlmaster_delete, {})
                    c2.rest.put(urlslave_delete, {})
                except:
                    helpers.log(c1.rest.error())
                    helpers.log(c2.rest.error())
                    return False
                else:
                    return True
            elif helpers.is_t5(n.platform()):
                helpers.log("The node is a T5 Controller")
                c1 = t.controller('master')
                c2 = t.controller('slave')
                try:
                    url = '/api/v1/data/controller/os/config/local/network/interface[type="ethernet"][number=0]/service[name="%s"]' % str(service)
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
    def snmp_cmd(self, node, snmp_cmd, snmpCommunity, snmpOID=None):
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
            if snmpOID is not None :
                url = "/usr/bin/%s -v2c -c %s %s %s" % (str(snmp_cmd), str(snmpCommunity), node.ip(), str(snmpOID))
            else:
                url = "/usr/bin/%s -v2c -c %s %s " % (str(snmp_cmd), str(snmpCommunity), node.ip())
            helpers.log("Executing SNMP_CMD: %s" % url)
            returnVal = subprocess.Popen([url], stdout=subprocess.PIPE, shell=True)
            (out, _) = returnVal.communicate()
            return out
        except:
            helpers.test_log("Could not execute command. Please check log for errors")
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
            helpers.test_log("Could not execute command. Please check log for errors")
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
            userinput = "cat /var/log/snmptt/snmptt.log | grep " + str(message)
            conn.execute(userinput)
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
            helpers.test_log("Unable to restart process '%s'"
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

    def monitor_reauth(self, node, *args, **kwargs):
        t = test.Test()
        if helpers.is_controller_or_error(node):
            n = t.node(node)
            return n.monitor_reauth(*args, **kwargs)

    def cli_add_controller_idle_and_reauth_timeout(self, node, *args, **kwargs):
        """
        Reconfigure the idle timeout and reauth timeout on the controller.

        Input:
        | node | Reference to switch (as defined in .topo file) |
        | reconfig_idle | Default is ${true}. Set to $[false} if you don't want to reconfigure idle timeout. |
        | reconfig_reauth | Default is ${true}. Set to $[false} if you don't want to reconfigure reauth timeout. |

        Return Value:
        - ${true} on success, else ${false} on failure.

        """
        t = test.Test()
        return t.cli_add_controller_idle_and_reauth_timeout(node, *args, **kwargs)

    def node_disconnect(self, node):
        """
        Disconnect the devconf session (SSH/Telnet) on the specified node.
        """
        t = test.Test()
        t.node_disconnect(node)

    def get_node_name(self, node):
        """
        Get the name of a node

        Input:
        | node | logical node name, e.g., 'c1', 'master', 'slave', etc. |

        Return Value:  actual node name, e.g., 'c1', 'c2', 's1'
        """
        t = test.Test()
        n = t.node(node)
        return n.name()

    def get_node_hostname(self, node, soft_error=False):
        """
        Get the hostname of a node

        Input:
        | node | logical node name, e.g., 'c1', 'master', 'slave', etc. |
        | soft_error | Default is ${false} which will generate an exception if hostname does not exist. If ${true} then return ${none} if hostname does not exist. |

        Return Value:  actual hostname of the node
        """
        t = test.Test()
        n = t.node(node)
        hostname = n.hostname()
        if hostname == None:
            helpers.test_error("Hostname for '%s' is not defined" % node,
                               soft_error=soft_error,
                               dump_error_stack=False)
        return hostname

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

    def get_node_alias(self, node):
        """
        Get the alias of a node

        Input: logical node name, e.g., 's1', 's2', etc.

        Return Value:  node alias (e.g., 'spine0', 'leaf1-a'). See
        https://bigswitch.atlassian.net/wiki/display/QA/Topology+Descriptions+in+BigRobot
        for the list of supported aliases.
        """
        t = test.Test()
        n = t.node(node)
        val = n.alias()
        if helpers.is_list(val):
            return val[0]
        else:
            return val

    def get_all_nodes(self):
        """
        Get the names of all nodes used in the test suite.

        Return Value:  List of node names, e.g., ['c1', 'c2', 's1', etc.]
        """
        t = test.Test()
        nodes = t.topology().keys()
        helpers.debug("Nodes used in test suite: %s" % nodes)
        return nodes

    def get_active_node_names(self):
        """
        Return a list of node names which are still active, i.e., open sessions.
        """
        t = test.Test()
        return t.active_node_names()

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

    def get_switch_mac_topo(self, node):
        '''
        Return the Mac secified in Topo file against give switch node
        '''
        t = test.Test()
        if node in t.params():
            return '00:00:' + t.params(node, 'mac')
        else:
            helpers.log("No Node: %s  Defined in Topo File.." % str(node))
            return False

    def get_switch_int_topo(self, node, int_key):
        '''
        Return the Interface name defined in Topo for the swtich with key int_key like below:
        s1:
            interfaces:
                int_key: ethernet24

        Note: There's a BsnCommon.interfaces keyword which is more robust. Consider using it instead.
        '''
        t = test.Test()
        if node in t.params():
            interfaces = t.params(node, 'interfaces')
            if int_key in interfaces:
                return interfaces[int_key]
            else:
                helpers.log("No Interfaces with key: %s defined for node: %s in topo file" % (int_key, node))
                return False
                # helpers.log("Exiting ..to resolve above issue..")
                # helpers.exit_robot_immediately("Please fix above issue")
        else:
            helpers.log("No Node: %s  Defined in Topo File.." % str(node))
            return False

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

    def extreme_save_config(self, node):
        """
        Save the configuration on Extreme switch.
        """
        t = test.Test()
        n = t.node(node)
        n.send("save configuration")
        n.expect(r'Do you want to save configuration .+ and overwrite it\? \(y/N\) ')
        n.send("y")
        n.expect()

    def node_reconnect(self, node, user=None, password=None):
        """
        Reconnect to a node.
        """
        t = test.Test()
        n = t.node_reconnect(node, user=user, password=password)
        return n

    def bigrobot_test_ztn(self, new_value=False):
        return helpers.bigrobot_test_ztn(new_value)

    def reconnect_switch_ips(self, node=None):
        """
        Reconnects the Switches IP by getting them from consoles
        """
        t = test.Test()
        helpers.bigrobot_no_auto_reload("True")
        if node is None:
            params = t.topology_params_nodes()
            for key in params:
                t.setup_ztn_phase2(key)
        else:
            t.setup_ztn_phase2(node)
        return True

    def get_snmp_id(self, interface=None):
        '''
            This function is use to convert given interface to snmp id to check on data traps
            To FIX:   support Breakout cables
            -Arun mallina
        '''
        if interface is None:
            helpers.log("Please interface name like: ethernet45, ethernet47")
            helpers.exit_robot_immediately("Exiting to fix passing interface ..")
        match = re.match(r"ethernet(.*)", interface)
        if match:
            id_string = match.group(1)
        if len(id_string) == 1:
            return "100" + id_string
        else:
            return "10" + id_string

    def get_gpid_switch_int(self, interface=None):
        '''
            This function is use to convert given interface to snmp id to check on data traps
            To FIX:   support Breakout cables
            -Arun mallina
        '''
        if interface is None:
            helpers.log("Please interface name like: ethernet45, ethernet47")
            helpers.exit_robot_immediately("Exiting to fix passing interface ..")
        match = re.match(r"ethernet(.*)", interface)
        id_string = ''
        if match:
            id_string = match.group(1)
        return id_string

    def pretty_log(self, *args, **kwargs):
        """
        To print out a Python data structure, consider using this keyword.
        It formats the object to make it more readable. By default, it will
        also convert the \n found in the string into newline.

        Examples:
        | pretty log | ${data} |  | Pretty print data structure, converting \n to newline |
        | pretty log | ${data} | format_newline=${false} | Pretty print data structure, preserve \n in result |
        """
        helpers.pretty_log(*args, **kwargs)

    def get_time_now_in_utc_format(self):
        """
        Objective:
        Return the current time in UTC format, e.g., "2013-09-26T15:57:49.123Z"
        """
        return helpers.ts_long()

