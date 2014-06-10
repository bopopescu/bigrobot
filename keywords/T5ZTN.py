import autobot.helpers as helpers
import autobot.test as test
from keywords.BsnCommon import BsnCommon as bsnCommon
import re
import ast
import urllib2
import traceback

class T5ZTN(object):

    def bash_verify_sl_images(self, node='master'):
        """
        Check if SwitchLight images are present on the controller

        Inputs:
        | node | reference to switch/controller as defined in .topo file |

        Return Value:
        - True if images are present, False otherwise
        """
        t = test.Test()
        c = t.controller(node)
        helpers.log("Verifying if Switch images"
                    " are present on node %s" % node)
        c.bash("ls -l /usr/share/floodlight/zerotouch")
        output = c.cli_content()
        output = helpers.strip_cli_output(output)
        output = helpers.str_to_list(output)
        if len(output) != 3:
            return helpers.test_failure("Too many files in images"
                                        " directory - %s" % str(len(output)))

        if (re.match(r'.*internal.*', output[1])
            or re.match(r'.*internal.*', output[2])):
            return helpers.test_failure("SL internal image in the bundle!")

        helpers.log("Trying to check if SL installer is in %s" % output[2])
        if not re.match(r'.*switchlight-.*release.ztn.*installer', output[2]):
            return helpers.test_failure("SL installer not found")
        helpers.log("Trying to check if SL SWI image is in %s" % output[1])
        if not re.match(r'.*switchlight-.*release-bcf.*swi', output[1]):
            return helpers.test_failure("SL SWI image not found")
        helpers.log("Switch Light installer and SWI image are present")

        return True

    def bash_verify_sl_manifests(self, node='master'):
        """
        Check if SwitchLight images are accompanied
        by appropriate manifest files

        Inputs:
        | node | reference to switch/controller as defined in .topo file |

        Return Value:
        - True if manifest files are present, False otherwise
        """
        t = test.Test()
        c = t.controller(node)
        helpers.log("Verifying if SwitchLight manifests"
                    " are present on node %s" % node)
        c.bash("unzip -p /usr/share/floodlight/zerotouch/"
               "switchlight*installer zerotouch.json")
        output = c.cli_content()
        output = helpers.strip_cli_output(output)
        installer_manifest = ast.literal_eval(output)
        installer_release = installer_manifest['release']
        installer_platform = installer_manifest['platform']
        installer_operation = installer_manifest['operation']
        installer_sha1 = installer_manifest['sha1']
        installer_manifest_version = installer_manifest['manifest_version']
        if installer_operation != 'os-install':
            helpers.test_failure("Wrong installer operation - %s"
                                  % installer_operation)
        c.bash("unzip -p /usr/share/floodlight/zerotouch/switchlight*swi"
               " zerotouch.json")
        output = c.cli_content()
        output = helpers.strip_cli_output(output)
        swi_manifest = ast.literal_eval(output)
        swi_release = swi_manifest['release']
        swi_platform = swi_manifest['platform']
        swi_operation = swi_manifest['operation']
        swi_sha1 = swi_manifest['sha1']
        swi_manifest_version = swi_manifest['manifest_version']
        if swi_operation != 'ztn-runtime':
            helpers.test_failure("Wrong swi operation - %s"
                                  % installer_operation)
        return True

    def bash_get_supported_platforms(self, image):
        """
        Get list of platforms supported by SWI or SwitchLight installer

        Inputs:
        | image |  Image - SWI or installer |

        Return Value:
        - List of supported platforms or None in case of errors
        """
        t = test.Test()
        c = t.controller('master')
        helpers.log("Getting list of supported platforms"
                    " for SwitchLight %s" % image)
        if image == "installer":
            c.bash("unzip -p /usr/share/floodlight/zerotouch/"
                   "switchlight*installer zerotouch.json")
        elif image == "swi":
            c.bash("unzip -p /usr/share/floodlight/zerotouch/"
                   "switchlight*swi zerotouch.json")
        else:
            helpers.test_failure("Requested platforms for neither SWI"
                                 " nor Installer image")
        output = c.cli_content()
        output = helpers.strip_cli_output(output)
        if len(output) == 0:
            helpers.test_failure("List of supported platforms is empty")
            return None
        manifest = ast.literal_eval(output)
        platform = manifest['platform']
        platform_list = platform.split(',')
        return platform_list

    def test_console(self, node):
        """
        Test telnet access to given node

        Inputs:
        | node | Alias of the node to use |

        Return Value:
        - N/A
        """
        t = test.Test()
        con = t.dev_console(node)
        con.send("help")
        helpers.log(con.cli('')['content'])

    def telnet_wait_for_switch_to_reload(self, node):
        """
        Test telnet access to given node

        Inputs:
        | node | Alias of the node to use |

        Return Value:
        - N/A
        """
        t = test.Test()
        con = t.dev_console(node, modeless=True)
        con.expect("Starting OpenFlow Agent: ofad", timeout=1000)
        con.expect(r'.*login:.*$', timeout=60)
        return True

    def telnet_verify_ztn_discovery_failed(self, node):
        """
        Verify that ZTN Discovery process failed

        Inputs:
        | node | Alias of the node to use |

        Return Value:
        - True if ZTN Discovery process failed
        """
        t = test.Test()
        con = t.dev_console(node, modeless=True)
        con.expect("ZTN Discovery Failed", timeout=1000)
        return True

    def telnet_verify_ztn_discovery_succeeded(self, node):
        """
        Verify that ZTN Discovery process succeeded

        Inputs:
        | node | Alias of the node to use |

        Return Value:
        - True if ZTN Discovery process succeeded
        """
        t = test.Test()
        con = t.dev_console(node, modeless=True)
        con.expect("Discovered Switch Light manifest from url", timeout=1000)
        con.expect("ZTN Manifest validated")
        con.expect("Booting")
        return True

    def telnet_verify_onie_discovery_failed(self, node):
        """
        Verify that ONIE Discovery process failed

        Inputs:
        | node | Alias of the node to use |

        Return Value:
        - True if ONIE Discovery process succeeded
        """
        t = test.Test()
        con = t.dev_console(node, modeless=True)
        con.expect("ONIE: Starting ONIE Service Discovery")
        con.expect("ONIE: Starting ONIE Service Discovery")
        return True

    def modeless_console(self, node):
        """
        Test telnet access to given node

        Inputs:
        | node | Alias of the node to use |

        Return Value:
        - N/A
        """
        t = test.Test()
        con = t.dev_console(node, modeless=True)
        #con.send("\x03")
        con.send(helpers.ctrl('c'))
        con.expect("=> ")
        con.send("help")
        con.expect("help")
        con.expect("=> ")
        con.send("printenv")
        con.expect("printenv")
        con.expect("=> ")
        con.send("boot")
        con.expect(r'.*login:.*$')

    def telnet_switch_reload(self, node):
        """
        Issue reload command on given node (switch)

        Inputs:
        | node | Alias of the node to use |

        Return Value:
        - N/A
        """
        t = test.Test()
        con = t.dev_console(node)
        con.enable("show running-config")
        helpers.log(con.cli('')['content'])
        con.enable("enable")
        con.send("reload now")
        helpers.sleep(90)

    def telnet_set_ma1_state(self, node, state):
        """
        Run "no interface ma1" command on switch

        Inputs:
        | node | Alias of the node to use |

        Return Value:
        - N/A
        """
        t = test.Test()
        s = t.dev_console(node, modeless=True)
        s.send(helpers.ctrl('c'))
        options = s.expect([r'[\r\n]*.*login:', r'root@.*:', s.get_prompt()],
                           timeout=1000)
        if options[0] == 0: #login prompt
            s.cli('admin')
        if options[0] == 1: #bash mode
            s.cli('exit')
        s.cli('enable; config')
        if state == 'up':
            helpers.log("Setting interface MA1 up")
            s.cli('interface ma1 ip-address dhcp')
        elif state == 'down':
            helpers.log("Setting interface MA1 down")
            s.cli('no interface ma1 ip-address dhcp')
        else:
            helpers.log("%s is not a valid state. Use 'up' or 'down'" % state)
            return helpers.test_failure("Wrong state of interface")
        return True

    def telnet_switch_reload_and_execute_loader_shell_commands(self,
        node, commands):
        """
        Issue reload command on given node (switch), stop at shell loader
        and execute commands

        Inputs:
        | node | Alias of the node to use |
        | commands | List of commands to execute in loader shell |

        Return Value:
        - N/A
        """
        t = test.Test()
        con = t.dev_console(node)
        con.enable("show running-config")
        helpers.log(con.cli('')['content'])
        con.enable("enable")
        con.send("reload now")
        con.expect("Press Control-C now to enter loader shell")
        helpers.log("Entering loader shell")
        con.send("\x03")
        for command in commands:
            helpers.log("Executing command %s" % command)
            con.send(command)
        helpers.log("Entering loader shell")
        con.send("reboot")
        con.expect(r'.*login:.*$')

    def telnet_switch_reload_and_verify_using_cached_SWI_and_config(self, node):
        """
        Issue reload command on given node (switch) and verify it uses
        cached SWI and config

        Inputs:
        | node | Alias of the node to use |

        Return Value:
        - N/A
        """
        t = test.Test()
        con = t.dev_console(node)
        con.enable("show running-config")
        helpers.log(con.cli('')['content'])
        con.enable("enable")
        con.send("reload now")
        con.expect("Discovered Switch Light manifest from neighbor discovery")
        con.expect("Using cached ZTN SWI")
        con.expect("Using cached ZTN startup-config")
        con.expect(r'.*login:.*$')

    def telnet_switch_reload_and_verify_using_new_SWI_and_cached_config(self,
        node):
        """
        Issue reload command on given node (switch) and verify it uses
        new SWI and cached config

        Inputs:
        | node | Alias of the node to use |

        Return Value:
        - N/A
        """
        t = test.Test()
        con = t.dev_console(node)
        con.enable("show running-config")
        helpers.log(con.cli('')['content'])
        con.enable("enable")
        con.send("reload now")
        con.expect("Discovered Switch Light manifest from neighbor discovery")
        con.expect("Downloading new ZTN SWI")
        con.expect("Using cached ZTN startup-config")
        con.expect("Caching ZTN SWI")
        con.expect(r'.*login:.*$')

    def telnet_switch_reload_and_verify_using_cached_SWI_and_new_config(self,
        node):
        """
        Issue reload command on given node (switch) and verify it uses
        new SWI and cached config

        Inputs:
        | node | Alias of the node to use |

        Return Value:
        - N/A
        """
        t = test.Test()
        con = t.dev_console(node)
        con.enable("show running-config")
        helpers.log(con.cli('')['content'])
        con.enable("enable")
        con.send("reload now")
        con.expect("Discovered Switch Light manifest from neighbor discovery")
        con.expect("Using cached ZTN SWI")
        con.expect("Downloading new startup-config")
        con.expect("Caching ZTN startup-config")
        con.expect(r'.*login:.*$')

    def telnet_switch_reload_and_verify_using_new_SWI_and_config(self, node):
        """
        Issue reload command on given node (switch) and verify it uses cached
        SWI and config

        Inputs:
        | node | Alias of the node to use |

        Return Value:
        - N/A
        """
        t = test.Test()
        con = t.dev_console(node)
        con.enable("show running-config")
        helpers.log(con.cli('')['content'])
        con.enable("enable")
        con.send("reload now")
        con.expect("Discovered Switch Light manifest from neighbor discovery")
        con.expect("Downloading new ZTN SWI")
        con.expect("Downloading new startup-config")
        con.expect("Caching ZTN SWI")
        con.expect("Caching ZTN startup-config")
        con.expect(r'.*login:.*$')

    def curl_get_switch_startup_config(self, mac):
        """
        Get startup-config for given switch by executing CURL command
        against the active controller

        Inputs:
        | mac | MAC address of switch |

        Return Value:
        - List with startup config lines or None
        """
        t = test.Test()
        bsn_common = bsnCommon()
        master_ip = bsn_common.get_node_ip('master')
        single = False
        try:
            slave_ip = bsn_common.get_node_ip('slave')
        except:
            helpers.log("Single node cluster")
            single = True

        if not single:
            url = ("http://%s/ztn/switch/%s/startup_config?proxy=1"
                   % (str(slave_ip), str(mac)))
            helpers.log("Verifying that Slave controller does not provide"
                        " any startup-config for the switch")
            helpers.log("Trying to get switch startup config at %s" % url)
            try:
                req = urllib2.Request(url)
                res = urllib2.urlopen(req)
                helpers.log("Response is: %s" % res)
                config = res.read()
                helpers.log("Response is: %s" % ''.join(config))
                helpers.log("Slave responded with startup-config. Erroring out")
                helpers.test_failure("Slave responded with startup-config")
            except urllib2.HTTPError as err:
                if err.code == 404:
                    helpers.log("Error 404 trying to get startup-config"
                                " from Slave - it is expected")
                else:
                    return helpers.test_failure("Error connecting to Slave")
            except:
                return helpers.test_failure("Other error connecting to Slave")

        url = ("http://%s/ztn/switch/%s/startup_config?proxy=1&internal=1"
               % (str(master_ip), str(mac)))
        helpers.log("Trying to get switch startup config at %s" % url)
        try:
            req = urllib2.Request(url)
            res = urllib2.urlopen(req)
            helpers.log("Response is: %s" % res)
            config = res.read()
            helpers.log("Response is: %s" % ''.join(config))
        except:
            helpers.log(traceback.print_exc())
            return helpers.test_failure("Error trying to get startup-config"
                   " from Master")
        config = config.replace('\\x', '\\0x')
        config = config.split('\n')
        return config


    def verify_switch_startup_config(self, mac, hostname):
        """
        Fetch startup-config for switch and compare with running-config
        on the controller

        Inputs:
        | mac | MAC address of switch |
        | hostname | Alias of switch |

        Return Value:
        - True if startup config is correct, False otherwise
        """

        t = test.Test()
        c = t.controller('master')
        bsn_common = bsnCommon()
        master_ip = bsn_common.get_node_ip('master')
        #If this is s0, s1, ... then get hostname of topo file
        #otherwise just use the provided hostname
        if re.match(r's\d*$', hostname):
            switch_name = bsn_common.get_node_alias(hostname)
            helpers.log("Switch alias is %s" % switch_name)
        else:
            switch_name = hostname
        helpers.log("Expected switch hostname is %s" % switch_name)

        single = False
        try:
            slave_ip = bsn_common.get_node_ip('slave')
        except:
            helpers.log("Single node cluster")
            single = True

        startup_config = self.curl_get_switch_startup_config(mac)
        missing_startup = []
        extra_startup = []

        ztn_config = c.config("show running-config")['content']
        ztn_config = helpers.strip_cli_output(ztn_config)
        ztn_config = helpers.str_to_list(ztn_config)

        ztn_config_temp = []
        for ztn_config_line in ztn_config:
            if re.match(r'snmp-server|ntp', ztn_config_line):
                ztn_config_temp.append(ztn_config_line)
                helpers.log("Keeping line in ztn-config: %s" % ztn_config_line)
        ztn_config = ztn_config_temp
        ztn_config.append("interface ma1 ip-address dhcp")
        ztn_config.append("hostname %s" % switch_name)
        ztn_config.append("datapath id 00:00:%s" % mac)
        ztn_config.append("controller %s port 6653" % master_ip)
        ztn_config.append("ssh enable")
        ztn_config.append("telnet enable")
        ztn_config.append("logging host %s" % master_ip)
        if not single:
            ztn_config.append("controller %s port 6653" % slave_ip)
            ztn_config.append("logging host %s" % slave_ip)

        startup_config_temp = []
        for startup_config_line in startup_config:
            if not re.match(r'!|^\s*$', startup_config_line):
                if "ntp sync" in startup_config_line:
                    helpers.log("Skipping line: %s" % startup_config_line)
                    continue
                if "ntp enable" in startup_config_line:
                    helpers.log("Skipping line: %s" % startup_config_line)
                    continue
                if "timezone UTC" in startup_config_line:
                    helpers.log("Skipping line: %s" % startup_config_line)
                    continue
                startup_config_temp.append(startup_config_line)
                helpers.log("Keeping line in startup-config: %s"
                            % startup_config_line)
        startup_config = startup_config_temp

        for idx, ztn_config_line in enumerate(ztn_config):
            if "snmp-server host" in ztn_config_line:
                if "udp-port" in ztn_config_line:
                    ztn_config[idx] = ztn_config_line.replace("udp-port",
                                "traps public udp-port")
                else:
                    ztn_config[idx] = (ztn_config_line +
                                       " traps public udp-port 162")
                helpers.log("Rearranging config line: %s" % ztn_config[idx])
            if "snmp-server enable traps" in ztn_config_line:
                ztn_config[idx] = "snmp-server enable"
                helpers.log("Rearranging config line: %s" % ztn_config[idx])
            if "ntp time-zone" in ztn_config_line:
                ztn_config[idx] = ztn_config_line.replace("ntp time-zone",
                                  "timezone")
                helpers.log("Rearranging config line: %s" % ztn_config[idx])

        for ztn_config_line in ztn_config:
            if ztn_config_line not in startup_config:
                missing_startup.append(ztn_config_line)
        for startup_config_line in startup_config:
            if startup_config_line not in ztn_config:
                extra_startup.append(startup_config_line)

        if len(missing_startup) > 0:
            for line in missing_startup:
                helpers.log("Startup-config is missing line: %s" % line)
        if len(extra_startup) > 0:
            for line in extra_startup:
                helpers.log("Startup-config has extra line: %s" % line)

        if len(missing_startup) > 0 or len(extra_startup) > 0:
            return helpers.test_failure("Failure due to missing lines")
        else:
            helpers.log("Startup-config for switch %s is correct" % mac)
            return True

    def verify_switch_running_config(self, mac, hostname):
        """
        Fetch startup-config for switch and compare with running-config
        on the switch

        Inputs:
        | mac | MAC address of switch |
        | hostname | Alias of switch |

        Return Value:
        - True if startup config is correct, False otherwise
        """

        t = test.Test()

        startup_config = self.curl_get_switch_startup_config(mac)
        missing_startup = []
        extra_startup = []

        s = t.dev_console(hostname, modeless=True)
        s.send(helpers.ctrl('c'))
        options = s.expect([r'[\r\n]*.*login:', r'[Pp]assword:', r'.*@.*:',
                           s.get_prompt()])
        if options[0] == 0:
            s.cli('admin')
        if options[0] == 2:
            s.cli('exit')
        s.cli('enable')
        s.cli('config')
        running_config = s.cli("show running-config")['content']
        running_config = helpers.str_to_list(running_config)
        #skipping first line
        running_config = running_config[1:]

        startup_config_temp = []
        for startup_config_line in startup_config:
            if not re.match(r'!|^\s*$', startup_config_line):
                if "ntp sync" in startup_config_line:
                    helpers.log("Skipping line: %s" % startup_config_line)
                    continue
                if "timezone UTC" in startup_config_line:
                    helpers.log("Skipping line: %s" % startup_config_line)
                    continue
                if re.match(r'controller .* port 6653', startup_config_line):
                    helpers.log("Skipping port number in %s" %
                                startup_config_line)
                    temp_line = startup_config_line.replace(" port 6653", "")
                    startup_config_temp.append(temp_line)
                    continue
                startup_config_temp.append(startup_config_line)
                helpers.log("Keeping line in startup-config: %s"
                            % startup_config_line)
        startup_config = startup_config_temp

        running_config_temp = []
        for running_config_line in running_config:
            helpers.log("Analyzing line %s" % running_config_line)
            # Excluding comments and empty lines
            if not re.match(r'!|^\s*$', running_config_line):
                if "timezone Etc/UTC" in running_config_line:
                    helpers.log("Skipping line: %s" % running_config_line)
                    continue
                if "username recovery" in running_config_line:
                    helpers.log("Skipping line: %s" % running_config_line)
                    continue
                if "snmp-server location 'Not set'" in running_config_line:
                    helpers.log("Skipping line: %s" % running_config_line)
                    continue
                if "snmp-server contact 'Not set'" in running_config_line:
                    helpers.log("Skipping line: %s" % running_config_line)
                    continue
                if re.match(r'snmp-server community ro public$',
                            running_config_line):
                    helpers.log("Skipping line: %s" % running_config_line)
                    continue
                running_config_temp.append(running_config_line)
                helpers.log("Keeping line in running-config: %s"
                            % running_config_line)
        running_config = running_config_temp

        for running_config_line in running_config:
            if running_config_line not in startup_config:
                missing_startup.append(running_config_line)
        for startup_config_line in startup_config:
            if startup_config_line not in running_config:
                extra_startup.append(startup_config_line)

        if len(missing_startup) > 0:
            for line in missing_startup:
                helpers.log("Running-config has extra line: %s" % line)
        if len(extra_startup) > 0:
            for line in extra_startup:
                helpers.log("Running-config is missing line: %s" % line)

        if len(missing_startup) > 0 or len(extra_startup) > 0:
            return helpers.test_failure("Failure due to missing lines")
        else:
            helpers.log("Startup-config for switch %s is correct" % mac)
            return True

    def rest_get_switch_fabric_role(self, node, switch):
        """
        Get fabric role of the switch

        Inputs:
        | node | Alias of the controller node |
        | switch | Alias of the switch |

        Return Value:
        - Fabric role of the switch or None if empty/error
        """
        t = test.Test()
        c = t.controller(node)
        url = ('/api/v1/data/controller/applications/bvs/info/fabric/'
               'switch[name="%s"]' % str(switch))
        helpers.log("Trying to get switch fabric role via url %s" % url)
        c.rest.get(url)
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())

        content = c.rest.content()
        helpers.log('content is: %s' % content)
        if content:
            return_val = content[0]['fabric-role']
            return return_val
        else:
            helpers.log("Error when getting switch fabric role")
            helpers.test_failure(c.rest.error())
            return None

    def rest_get_switch_fabric_connection_state(self, node, switch):
        """
        Get fabric connection state of the switch

        Inputs:
        | node | Alias of the controller node |
        | switch | Alias of the switch |

        Return Value:
        - Return fabric-connection-state value (connected, not_connected) or
          None in case of errors
        """
        t = test.Test()
        c = t.controller(node)
        url = ('/api/v1/data/controller/applications/bvs/info/fabric/'
               'switch[name="%s"]' % str(switch))
        helpers.log("Trying to get switch fabri connection state via url %s"
                    % url)
        c.rest.get(url)
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())

        content = c.rest.content()
        helpers.log('content is: %s' % content)
        if content:
            return_val = content[0]['fabric-connection-state']
            return return_val
        else:
            helpers.log("Error when getting switch fabri connetion state")
            helpers.test_failure(c.rest.error())
            return None

    def rest_get_switch_suspended_reason(self, node, switch):
        """
        Get suspended reason for the switch

        Inputs:
        | node | Alias of the controller node |
        | switch | Alias of the switch |

        Return Value:
        - Return value of suspended-reason or None in case of errors
        """
        t = test.Test()
        c = t.controller(node)
        url = ('/api/v1/data/controller/applications/bvs/info/fabric/'
               'switch[name="%s"]' % str(switch))
        helpers.log("Trying to get switch fabri connection state via url %s"
                    % url)
        c.rest.get(url)
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())

        content = c.rest.content()
        helpers.log('content is: %s' % content)
        if content:
            return_val = content[0]['suspended-reason']
            return return_val
        else:
            helpers.log("Error when getting switch fabric connection state")
            helpers.test_failure(c.rest.error())
            return None

    def rest_get_switch_connection_state(self, node, switch):
        """
        Get connection state of the switch

        Inputs:
        | node | Alias of the controller node |
        | switch | Alias of the switch |

        Return Value:
        - True if switch connected, False if not connected, None in case of
          errors
        """
        t = test.Test()
        c = t.controller(node)
        url = ('/api/v1/data/controller/applications/bvs/info/fabric/'
               'switch[name="%s"]' % str(switch))
        helpers.log("Trying to get switch connection state  via url %s" % url)
        c.rest.get(url)
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())

        content = c.rest.content()
        helpers.log('content is: %s' % content)
        if content:
            return_val = content[0]['connected']
            return return_val
        else:
            helpers.log("Error when getting switch connection state")
            helpers.test_failure(c.rest.error())
            return None

    def rest_get_switch_handshake_state(self, node, switch):
        """
        Get handshake state of the switch

        Inputs:
        | node | Alias of the controller node |
        | switch | Alias of the switch |

        Return Value:
        - Return value of handshake-state or None in case of errors
        """
        t = test.Test()
        c = t.controller(node)
        url = ('/api/v1/data/controller/applications/bvs/info/fabric/'
               'switch[name="%s"]' % str(switch))
        helpers.log("Trying to get switch handshake state  via url %s" % url)
        c.rest.get(url)
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())

        content = c.rest.content()
        helpers.log('content is: %s' % content)
        if content:
            return_val = content[0]['handshake-state']
            return return_val
        else:
            helpers.log("Error when getting switch handshake state")
            helpers.test_failure(c.rest.error())
            return None

    def rest_get_switch_ip_address(self, node, switch):
        """
        Get IP address of the switch

        Inputs:
        | node | Alias of the controller node |
        | switch | Alias of the switch |

        Return Value:
        - IP address of the switch or None if empty/error
        """
        t = test.Test()
        c = t.controller(node)
        url = ('/api/v1/data/controller/applications/bvs/info/fabric/'
               'switch[name="%s"]' % str(switch))
        helpers.log("Trying to get switch IP address via url %s" % url)
        c.rest.get(url)
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())

        content = c.rest.content()
        helpers.log('content is: %s' % content)
        if content:
            if content[0]['connected'] == False:
                return helpers.test_failure("Switch %s not connected" % switch)
            ip_address = content[0]['inet-address']['ip']
            return ip_address
        else:
            helpers.log("Error when getting switch IP address")
            helpers.test_failure(c.rest.error())
            return None

    def telnet_reboot_switch(self, switch):
        """
        Issue reboot command for switch

        Inputs:
        | switch | Alias of the switch |

        Return Value:
        - True if reboot triggered successfully, False otherwise
        """
        t = test.Test()
        s = t.dev_console(switch, modeless=True)
        s.send(helpers.ctrl('c'))
        options = s.expect([r'[\r\n]*.*login:', r'[Pp]assword:', r'root@.*:',
                            r'ONIE:/ #', r'=> ', r'loader#', s.get_prompt(),
                            r'Trying manifest'], timeout=1000)
        if options[0] == 0: #login prompt
            s.cli('admin')
            s.cli('enable; config')
            s.send('reload now')
        if options[0] == 2: #bash mode
            s.cli('exit')
            s.cli('enable; config')
            s.send('reload now')
        if options[0] == 3: #ONIE loader
            s.send('reboot')
        if options[0] == 4: #U-boot
            s.send('boot')
        if options[0] == 5: #SL Loader
            s.send('reboot')
        if options[0] == 6: #CLI
            s.cli('enable; config')
            s.send('reload now')
        if options[0] == 7: #SL Loader
            s.send(helpers.ctrl('c'))
            s.send('reboot')
        try:
            if options[0] == 4:
                s.expect(r'\(Re\)start USB')
            else:
                s.expect(r'Clock Configuration:', timeout=1000)
            helpers.log("Switch %s rebooted" % switch)
        except:
            helpers.log(s.cli('')['content'])
            return helpers.test_failure("Error rebooting switch %s" % switch)

        return True

    def telnet_stop_autoboot(self, switch):
        """
        Enter switch u-boot shell while switch is booting up

        Inputs:
        | switch | Alias of the switch |

        Return Value:
        - True if successfully entered u-boot shell, False otherwise
        """
        t = test.Test()
        s = t.dev_console(switch, modeless=True)
        try:
            s.expect("Hit any key to stop autoboot")
        except:
            return helpers.test_failure("Unable to stop at u-boot shell")

        s.send("\ ")
        s.send(helpers.ctrl('c'))
        options = s.expect([r'[\r\n]*.*login:', r'\=\>'], timeout=100)
        if options[0] == 0:
            helpers.log("Something went wrong, trying again")
            s.send("admin")
            s.send("enable; config; reload now")
            s.expect("Hit any key to stop autoboot")
            s.send("\ ")
            s.send(helpers.ctrl('c'))
            s.expect(r'\=\>')
            helpers.log("U-boot shell entered")
            return True
        if options[0] == 1:
            helpers.log("U-boot shell entered")
            return True

    def enter_loader_shell(self, switch):
        """
        Enter Switch Light loader shell while switch is booting up

        Inputs:
        | switch | Alias of the switch |

        Return Value:
        - True if successfully entered loader shell, False otherwise
        """
        t = test.Test()
        s = t.dev_console(switch, modeless=True)
        try:
            s.expect("Press Control-C now to enter loader shell")
        except:
            return helpers.test_failure("Unable to stop at loader shell")

        helpers.log("Entering loader shell")
        s.send("\x03")
        s.expect(r'loader#')
        helpers.log("Loader shell entered")
        return True
