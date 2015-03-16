import autobot.helpers as helpers
import autobot.test as test
from keywords.BsnCommon import BsnCommon as bsnCommon
import re
import ast
import urllib2
import traceback

class T5ZTN(object):

    def bash_verify_switchlight_images(self, node='master'):
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
        if len(output) != 5:
            return helpers.test_failure("Too many files in images"
                                        " directory - %s" % str(len(output)))

        if (re.match(r'.*internal.*', output[1])
            or re.match(r'.*internal.*', output[2])
            or re.match(r'.*internal.*', output[3])
            or re.match(r'.*internal.*', output[4])):
            return helpers.test_failure("SL internal image in the bundle!")
        helpers.log("Trying to check if SL amd64 installer is in %s"
                    % output[3])
        if not re.match(r'.*switchlight.*ZTN-amd64-release.*installer',
                        output[3]):
            return helpers.test_failure("SL amd64 installer not found")
        helpers.log("Trying to check if SL amd64 SWI image is in %s"
                    % output[1])
        if not re.match(r'.*switchlight.*amd64-release.*swi',
                        output[1]):
            return helpers.test_failure("SL amd64 SWI image not found")
        helpers.log("Switch Light amd64 installer and SWI image are present")

        helpers.log("Trying to check if SL powerpc installer is in %s"
                    % output[4])
        if not re.match(r'.*switchlight.*ZTN-powerpc-release.*installer',
                        output[4]):
            return helpers.test_failure("SL powerpc installer not found")
        helpers.log("Trying to check if SL powerpc SWI image is in %s"
                    % output[2])
        if not re.match(r'.*switchlight.*powerpc-release.*swi',
                        output[2]):
            return helpers.test_failure("SL powerpc SWI image not found")
        helpers.log("Switch Light powerpc installer and SWI image are present")
        c.config("enable")

        return True

    def bash_verify_switchlight_manifests(self, node='master'):
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
        helpers.log("Verifying if SwitchLight powerpc manifests"
                    " are present on node %s" % node)
        c.bash("unzip -p /usr/share/floodlight/zerotouch/"
               "switchlight*powerpc*installer zerotouch.json")
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
        c.bash("unzip -p /usr/share/floodlight/zerotouch/"
               "switchlight*powerpc*swi zerotouch.json")
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
                                  % swi_operation)

        helpers.log("Verifying if SwitchLight amd64 manifests"
                    " are present on node %s" % node)
        c.bash("unzip -p /usr/share/floodlight/zerotouch/"
               "switchlight*amd64*installer zerotouch.json")
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
        c.bash("unzip -p /usr/share/floodlight/zerotouch/"
               "switchlight*amd64*swi zerotouch.json")
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
                                  % swi_operation)
        c.config("")

        return True

    def bash_get_switchlight_version(self, image, node='master',
                                     arch='powerpc'):
        """
        Get SWI or Installer Versions in the controller bundle

        Inputs:
        | image | SL image - swi or installer |
        | node | reference to switch/controller as defined in .topo file |
        | arch | Architecture type - powerpc or amd64 |

        Return Value:
        - SWI or Installer Versions, None in case of errors
        """
        t = test.Test()
        c = t.controller(node)
        helpers.log("Verifying if SwitchLight %s manifests"
                    " are present on node %s" % (arch, node))
        if image != 'swi' and image != 'installer':
            helpers.log("Please use \'swi\' or \'installer\'")
            return None
        if arch != 'powerpc' and arch != 'amd64':
            helpers.log("Please use \'powerpc\' or \'amd64\'")
            return None
        if image == 'installer':
            c.bash("unzip -p /usr/share/floodlight/zerotouch/"
                   "switchlight*%s*installer zerotouch.json" % arch)
            output = c.cli_content()
            output = helpers.strip_cli_output(output)
            installer_manifest = ast.literal_eval(output)
            installer_release = installer_manifest['sha1']
            return installer_release
        if image == 'swi':
            c.bash("unzip -p /usr/share/floodlight/zerotouch/switchlight*%s*swi"
                   " zerotouch.json" % arch)
            output = c.cli_content()
            output = helpers.strip_cli_output(output)
            swi_manifest = ast.literal_eval(output)
            swi_release = swi_manifest['sha1']
            return swi_release

    def controller_get_release_string(self, node='master'):
        """
        Get Release String of the controller bundle

        Inputs:
        | node | reference to controller as defined in .topo file |

        Return Value:
        - Controller release string, None in case of errors
        """
        t = test.Test()
        c = t.controller(node)
        content = c.config("show version | grep Version")['content']
        output = helpers.strip_cli_output(content)
        temp = output.split(': ')
        temp = temp[1].strip()
        return temp


    def telnet_get_switch_switchlight_version(self, image, hostname,
                                              password='adminadmin'):
        """
        Get SWI or Installer Versions in the controller bundle

        Inputs:
        | image | SL image - swi or installer |
        | node | reference to switch/controller as defined in .topo file |

        Return Value:
        - SWI or Installer Versions, None in case of errors
        """

        if image != 'swi' and image != 'installer':
            helpers.log("Please use \'swi\' or \'installer\'")
            return None

        t = test.Test()
        n = t.node(hostname)
        s = t.dev_console(hostname)
        # s.send(helpers.ctrl('c'))
        # options = s.expect([r'[\r\n]*.*login: $',r'[Pp]assword:',r'root@.*:\~\#',
        #                   s.get_prompt()])
        # if options[0] == 0:  # login prompt
        #    s.send('admin')
        #    options = s.expect([r'[Pp]assword:', s.get_prompt()])
        #    if options[0] == 0:
        #        helpers.log("Logging in as admin with password %s" % password)
        #        s.cli(password)
        # if options[0] == 2:  # bash mode
        #    s.cli('exit')
        output = s.cli("show version")['content']
        output = helpers.str_to_list(output)

        version = ''

        if image == 'installer':
            line1 = "Loader Version: "
            line2 = "Loader Build: "
        if image == 'swi':
            line1 = "Software Image Version: "
            line2 = "Internal Build Version: "
        for line in output:
            if line1 in line:
                version = line.replace(line1, '')
            if line2 in line:
                line = line.replace(line2, '')
                if ' ' in line:
                    line = line.replace(' ', '')
                version = version + " (" + line + ")"
        n.console_close()
        return version

    def bash_get_supported_platforms(self, image, arch='powerpc'):
        """
        Get list of platforms supported by SWI or SwitchLight installer

        Inputs:
        | image |  Image - SWI or installer |
        | arch | Architecture type - powerpc or amd64 |

        Return Value:
        - List of supported platforms or None in case of errors
        """
        t = test.Test()
        c = t.controller('master')
        helpers.log("Getting list of supported platforms"
                    " for SwitchLight %s" % image)
        if image == "installer":
            c.bash("unzip -p /usr/share/floodlight/zerotouch/"
                   "switchlight*%s*installer zerotouch.json" % arch)
        elif image == "swi":
            c.bash("unzip -p /usr/share/floodlight/zerotouch/"
                   "switchlight*%s*swi zerotouch.json" % arch)
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
        c.config("")
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
        n = t.node(node)
        s = t.dev_console(node, modeless=True)
        # s.expect(r'[\r\n]Switch Light OS', timeout=120)
        s.send("\n")
        options = s.expect([r'=> ', r'[\r\n].*login: $',
                            r'Installer Mode Enabled', s.get_prompt()],
                            timeout=200)
        if options[0] == 0:  # Uboot prompt
            s.send('boot')
            s.expect(r'[\r\n].*login: $', timeout=200)
        elif options[0] == 2:
            s.send('reboot')
            s.expect(r'[\r\n].*login: $', timeout=200)
        elif options[0] == 3:
            n.console_close()
            helpers.test_failure("Switch did not reboot. Returning False")
            return False
        n.console_close()
        return True

    def telnet_wait_for_switch_to_find_manifest(self, node):
        """
        Test telnet access to given node

        Inputs:
        | node | Alias of the node to use |

        Return Value:
        - N/A
        """
        t = test.Test()
        s = t.dev_console(node, modeless=True)
        s.expect("Discovered Switch Light manifest", timeout=120)
        return True

    def telnet_wait_for_switch_to_start_booting(self, node):
        """
        Test telnet access to given node

        Inputs:
        | node | Alias of the node to use |

        Return Value:
        - N/A
        """
        t = test.Test()
        s = t.dev_console(node, modeless=True)
        s.expect("ZTN Manifest validated", timeout=120)
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
        n = t.node(node)
        s = t.dev_console(node, modeless=True)
        s.send("\n")
        options = s.expect([r'=> ', "ZTN Discovery Failed"], timeout=120)
        if options[0] == 0:
            s.send("boot")
            s.expect("ZTN Discovery Failed", timeout=120)
        s.expect("ZTN Discovery Failed", timeout=30)
        n.console_close()
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
        s = t.dev_console(node, modeless=True)
        s.expect("Discovered Switch Light manifest from url", timeout=120)
        s.expect("ZTN Manifest validated")
        s.expect("Booting")
        return True

    def telnet_verify_onie_discovery_failed(self, node):
        """
        Verify that ONIE Discovery process failed

        Inputs:
        | node | Alias of the node to use |

        Return Value:
        - True if ONIE Discovery process failed
        """
        t = test.Test()
        n = t.node(node)
        s = t.dev_console(node, modeless=True)
        s.expect("ONIE: Starting ONIE Service Discovery", timeout=60)
        s.expect("ONIE: Starting ONIE Service Discovery", timeout=60)
        n.console_close()
        return True

    def telnet_verify_onie_discovery_succeeded(self, node):
        """
        Verify that ONIE Discovery process succeeded

        Inputs:
        | node | Alias of the node to use |

        Return Value:
        - True if ONIE Discovery process succeeded
        """
        t = test.Test()
        n = t.node(node)
        s = t.dev_console(node, modeless=True)
        s.expect("ONIE: Executing installer", timeout=60)
        n.console_close()
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
        s = t.dev_console(node, modeless=True)
        # s.send("\x03")
        s.send(helpers.ctrl('c'))
        s.expect("=> ")
        s.send("help")
        s.expect("help")
        s.expect("=> ")
        s.send("printenv")
        s.expect("printenv")
        s.expect("=> ")
        s.send("boot")
        s.expect(r'.*login: $')

    def telnet_set_ma1_state(self, node, state):
        """
        Run "no interface ma1" command on switch

        Inputs:
        | node | Alias of the node to use |

        Return Value:
        - N/A
        """
        t = test.Test()
        n = t.node(node)
        s = t.dev_console(node, modeless=True)
        s.send(helpers.ctrl('c'))
        options = s.expect([r'[\r\n]*.*login: $', r'root@.*:\~\#',
                            r'=> ', r'loader#', s.get_prompt(),
                            r'ZTN Discovery'], timeout=120)
        if options[0] == 0:  # login prompt
            s.send('admin')
        if options[0] == 1:  # bash mode
            s.send('exit')
        if options[0] == 2:
            helpers.log("Switch rebooting")
            s.send('boot')
            n.console_close()
            return True
        if options[0] == 3:
            helpers.log("Switch in ZTN loader")
            s.send('reboot')
            n.console_close()
            return True
        if options[0] == 5:
            helpers.log("Switch in ZTN Discovery process. Doing nothing")
            s.send(helpers.ctrl('c'))
            s.send('reboot')
            n.console_close()
            return True
        s.send('enable; config')
        if state == 'up':
            helpers.log("Setting interface MA1 up")
            # s.send('interface ma1 ip-address dhcp')
            s.send("debug bash")
            s.send("ifconfig ma1 up")
            s.send("exit")
        elif state == 'down':
            helpers.log("Setting interface MA1 down")
            # s.send('no interface ma1 ip-address dhcp')
            s.send("debug bash")
            s.send("ifconfig ma1 down")
            s.send("exit")
        elif state == 'flap':
            helpers.log("Setting interface MA1 down and up")
            # s.send('no interface ma1 ip-address dhcp')
            # helpers.sleep(10)
            # s.send('interface ma1 ip-address dhcp')
            s.send("debug bash")
            s.send("ifconfig ma1 down")
            helpers.sleep(10)
            s.send("ifconfig ma1 up")
            helpers.sleep(10)
            s.send("exit")
        else:
            helpers.log("%s is not a valid state. Use 'up' or 'down'" % state)
            n.console_close()
            return helpers.test_failure("Wrong state of interface")
        n.console_close()
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
        con.expect(r'.*login: $')

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
        con.expect(r'.*login: $')

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
        con.expect(r'.*login: $')

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
        con.expect(r'.*login: $')

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
        con.expect(r'.*login: $')

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

            url = ("http://%s/ztn/switch/%s/startup_config?internal=1&proxy=1"
                   % (str(slave_ip), str(mac)))
            helpers.log("Verifying that Slave can compute startup config"
                        " for us if internal=1 flag attached")
            helpers.log("Trying to get switch startup config at %s" % url)
            try:
                req = urllib2.Request(url)
                res = urllib2.urlopen(req)
                helpers.log("Response is: %s" % res)
                slave_config = res.read()
                helpers.log("Response is: %s" % ''.join(slave_config))
            except:
                helpers.log(traceback.print_exc())
                return helpers.test_failure("Other error connecting to Slave")

        url = ("http://%s/ztn/switch/%s/startup_config?proxy=1"
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

        if not single:
            slave_config = slave_config.replace('\\x', '\\0x')
            slave_config = slave_config.split('\n')
            if slave_config == config:
                helpers.log("Master: %s" % config)
                helpers.log("Slave: %s" % slave_config)
                helpers.log("Configs generated by Master and Slave are equal")
                return config
            else:
                helpers.log("Master: %s" % config)
                helpers.log("Slave: %s" % slave_config)
                return helpers.test_failure("Slave and Master generated"
                       " different startup configs")
        return config


    def curl_get_switch_manifest(self, mac):
        """
        Get manifest for given switch by executing CURL command
        against the active controller

        Inputs:
        | mac | MAC address of switch |

        Return Value:
        - List with manifest lines or None
        """
        t = test.Test()
        bsn_common = bsnCommon()
        master_ip = bsn_common.get_node_ip('master')

        url = ("http://%s/ztn/switch/%s/switch_light_manifest?platform=powerpc-as5710-54x-r0b"
               % (str(master_ip), str(mac)))
        helpers.log("Trying to get switch manifest at %s" % url)
        try:
            req = urllib2.Request(url)
            res = urllib2.urlopen(req)
            helpers.log("Response is: %s" % res)
            manifest = res.read()
            helpers.log("Response is: %s" % ''.join(manifest))
        except:
            helpers.log(traceback.print_exc())
            return helpers.test_failure("Error trying to get manifest"
                   " from Master")
        return manifest


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
        # If this is s0, s1, ... then get hostname of topo file
        # otherwise just use the provided hostname
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

        c.cli('reauth admin adminadmin')
        c.config("")
        ztn_config = c.config("show running-config")['content']
        ztn_config = helpers.strip_cli_output(ztn_config)
        ztn_config = helpers.str_to_list(ztn_config)


        startup_config_temp = []
        for startup_config_line in startup_config:
            if not re.match(r'!|^\s*$', startup_config_line):
                if "ntp sync" in startup_config_line:
                    helpers.log("Skipping line: %s" % startup_config_line)
                    continue
                if "snmp-server enable" in startup_config_line:
                    helpers.log("Skipping line: %s" % startup_config_line)
                    continue
                if "ntp enable" in startup_config_line:
                    helpers.log("Skipping line: %s" % startup_config_line)
                    continue
                if "timezone UTC" in startup_config_line:
                    helpers.log("Skipping line: %s" % startup_config_line)
                    continue
                if re.match(r'snmp-server contact|snmp-server location',
                             startup_config_line):
                    temp_line = startup_config_line.replace("\"", "")
                    startup_config_temp.append(temp_line)
                    helpers.log("Rearranging line: %s" % temp_line)
                    continue
                startup_config_temp.append(startup_config_line)
                helpers.log("Keeping line in startup-config: %s"
                            % startup_config_line)
        startup_config = startup_config_temp

        ztn_config_temp = []
        for ztn_config_line in ztn_config:
            if re.match(r'snmp-server|ntp|logging remote', ztn_config_line):
                if re.match(r'logging remote$', ztn_config_line):
                    helpers.log("skipping line: %s" % ztn_config_line)
                    continue
                if "snmp-server host" in ztn_config_line:
                    if "snmp-server enable traps" in ztn_config:
                        if "udp-port" in ztn_config_line:
                            ztn_config_line = ztn_config_line.replace(
                               "udp-port", "traps public udp-port")
                        else:
                            ztn_config_line = (ztn_config_line +
                                               " traps public udp-port 162")
                        helpers.log("Rearranging config line: %s"
                                    % ztn_config_line)
                    else:
                        helpers.log(("Skipping line - %s - because"
                        " snmp-server traps are not enabled") % ztn_config_line)
                        continue
                if "snmp-server switch trap" in ztn_config_line:
                    helpers.log("SNMP traps enabled")
                    if "snmp-server enable traps" in ztn_config:
                        helpers.log("Rearranging line: %s" % ztn_config_line)
                        ztn_config_line = ztn_config_line.replace(
                           "snmp-server switch trap cpu-load",
                           "snmp-server trap cpu-load threshold")
                        ztn_config_line = ztn_config_line.replace(
                           "snmp-server switch trap mem-free",
                           "snmp-server trap mem-total-free threshold")
                        ztn_config_line = ztn_config_line.replace(
                           "snmp-server switch trap l2-flow-table-util",
                           "snmp-server trap flow-table-l2-util threshold")
                        ztn_config_line = ztn_config_line.replace(
                           "snmp-server switch trap fm-flow-table-util",
                           "snmp-server trap flow-table-tcam-fm-util threshold")
                        ztn_config_line = ztn_config_line.replace(
                           "snmp-server switch trap auth-fail",
                           "snmp-server trap authenticationFailure")
                        ztn_config_line = ztn_config_line.replace(
                           "snmp-server switch trap link-status",
                           "snmp-server trap linkUpDown interval")
                        ztn_config_line = ztn_config_line.replace(
                           "snmp-server switch trap psu-status",
                           "snmp-server trap psu all status all interval")
                        ztn_config_line = ztn_config_line.replace(
                           "snmp-server switch trap fan-status",
                           "snmp-server trap fan all status all interval")
                        if "mem-total-free" in ztn_config_line:
                            helpers.log("Need to divide value in %s "
                                        "by 1024" % ztn_config_line)
                            split = ztn_config_line.split(" ")
                            value = split[len(split) - 1]
                            helpers.log("Value is %s" % value)
                            new_value = int(int(value) / 1024)
                            helpers.log("New value is %s" % new_value)
                            ztn_config_line = ztn_config_line.replace(
                                             value, str(new_value))
                    else:
                        helpers.log(("Skipping line - %s - because"
                        " snmp-server traps are not enabled") % ztn_config_line)
                        continue
                if "snmp-server enable traps" in ztn_config_line:
                    helpers.log("Skipping line: %s" % ztn_config_line)
                    continue
                if re.match(r'snmp-server contact|snmp-server location',
                             ztn_config_line):
                    temp_line = ztn_config_line.replace("\'", "")
                    ztn_config_temp.append(temp_line)
                    helpers.log("Rearranging line: %s" % temp_line)
                    continue
                if "ntp time-zone" in ztn_config_line:
                    ztn_config_line = ztn_config_line.replace("ntp time-zone",
                                      "timezone")
                    helpers.log("Rearranging config line: %s" % ztn_config_line)
                if "logging remote" in ztn_config_line:
                    ztn_config_line = ztn_config_line.replace("remote",
                                      "host")
                    if len(ztn_config_line.split(' ')) > 3:
                        port = ztn_config_line.split(' ')[3]
                        ztn_config_line = ztn_config_line.replace(
                                          port, "port %s" % port)
                    else:
                        ztn_config_line = (ztn_config_line +
                                           " port 514")

                    helpers.log("Rearranging config line: %s" % ztn_config_line)
                ztn_config_temp.append(ztn_config_line)
                helpers.log("Keeping line in ztn-config: %s" % ztn_config_line)
        ztn_config = ztn_config_temp
        ztn_config.append("interface ma1 ip-address dhcp")
        ztn_config.append("hostname %s" % switch_name)
        ztn_config.append("datapath id 00:00:%s" % mac.lower())
        ztn_config.append("controller %s port 6653" % master_ip)
        ztn_config.append("ssh enable")
        ztn_config.append("logging host %s" % master_ip)
        if not single:
            ztn_config.append("controller %s port 6653" % slave_ip)
            ztn_config.append("logging host %s" % slave_ip)

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
        - True if running config is correct, False otherwise
        """

        t = test.Test()
        n = t.node(hostname)

        startup_config = self.curl_get_switch_startup_config(mac)
        missing_startup = []
        extra_startup = []
        psu_lines = ["snmp-server trap PSU 1 status good",
                     "snmp-server trap PSU 1 status failed",
                     "snmp-server trap PSU 1 status missing",
                     "snmp-server trap PSU 2 status good",
                     "snmp-server trap PSU 2 status failed",
                     "snmp-server trap PSU 2 status missing"]
        fan_lines = ["snmp-server trap Fan 1 status good",
                     "snmp-server trap Fan 1 status failed",
                     "snmp-server trap Fan 1 status missing",
                     "snmp-server trap Fan 2 status good",
                     "snmp-server trap Fan 2 status failed",
                     "snmp-server trap Fan 2 status missing",
                     "snmp-server trap Fan 3 status good",
                     "snmp-server trap Fan 3 status failed",
                     "snmp-server trap Fan 3 status missing",
                     "snmp-server trap Fan 4 status good",
                     "snmp-server trap Fan 4 status failed",
                     "snmp-server trap Fan 4 status missing",
                     "snmp-server trap Fan 5 status good",
                     "snmp-server trap Fan 5 status failed",
                     "snmp-server trap Fan 5 status missing",
                     "snmp-server trap Fan 6/7 status good",
                     "snmp-server trap Fan 6/7 status failed",
                     "snmp-server trap Fan 6/7 status missing"]

        s = t.dev_console(hostname, modeless=True)
        s.send("\n")
        # s.send(helpers.ctrl('c'))
        # s.send("\x03")
        options = s.expect([r'[\r\n]*.*login: $', r'[Pp]assword:',
                            r'[\r\n]* root@.*:\~\#', r'loader\#', r'=> ',
                            s.get_prompt()], timeout=30)
        if options[0] == 0:
            s.cli('admin')
        elif options[0] == 2:
            s.cli('exit')
        elif options[0] == 3:
            s.cli('reboot')
            helpers.log("Switch is rebooting. Waiting for full reboot")
            helpers.sleep(120)
            s.expect(r'[\r\n]*.*login: $', timeout=30)
            s.send('admin')
        elif options[0] == 4:
            s.cli('boot')
            helpers.test_failure("Switch is rebooting. Waiting for full reboot")
            helpers.sleep(120)
            s.expect(r'[\r\n]*.*login: $', timeout=30)
            s.send('admin')
        s.cli('enable')
        s.cli('config')
        switch_type = "unknown"
        switch_platform = "unknown"
        version = s.cli("show version")['content']
        if "AS6700-32X" in version:
            switch_type = "spine"
        elif "AS5710-54X" in version:
            switch_type = "leaf"
        if "Accton" in version:
            switch_platform = "powerpc"
        elif "DELL" in version:
            switch_platform = "x86"

        if switch_platform == "x86":
            fan_lines.append("snmp-server trap Fan 8 status good")
            fan_lines.append("snmp-server trap Fan 8 status failed")
            fan_lines.append("snmp-server trap Fan 8 status missing")
        # helpers.log(fan_lines)


        running_config = s.cli("show running-config")['content']
        running_config = helpers.str_to_list(running_config)
        if len(running_config) < 5:
            helpers.log("RC not parsed correctly. Trying again")
            running_config = s.cli("show running-config")['content']
            running_config = helpers.str_to_list(running_config)
        # skipping first line
        running_config = running_config[1:]

        startup_config_temp = []
        for startup_config_line in startup_config:
            if not re.match(r'!|^\s*$', startup_config_line):
                if "ntp sync" in startup_config_line:
                    helpers.log("Skipping line: %s" % startup_config_line)
                    continue
                if "snmp-server enable" in startup_config_line:
                    helpers.log("Skipping line: %s" % startup_config_line)
                    continue
                if re.match(r'snmp-server trap psu', startup_config_line):
                    interval = startup_config_line.split("interval ")[1]
                    helpers.log("Expanding line %s" % startup_config_line)
                    helpers.log("Interval is %s" % str(interval))
                    for psu_line in psu_lines:
                        startup_config_temp.append("%s interval %s"
                             % (psu_line, str(interval)))
                    continue
                if re.match(r'snmp-server trap fan', startup_config_line):
                    interval = startup_config_line.split("interval ")[1]
                    helpers.log("Expanding line %s" % startup_config_line)
                    helpers.log("Interval is %s" % str(interval))
                    for fan_line in fan_lines:
                        startup_config_temp.append("%s interval %s"
                             % (fan_line, str(interval)))
                    continue
                if "timezone UTC" in startup_config_line:
                    temp_line = startup_config_line.replace("UTC", "Etc/UTC")
                    startup_config_temp.append(temp_line)
                    helpers.log("Rearranging line: %s" % startup_config_line)
                    continue
                if re.match(r'snmp-server contact|snmp-server location',
                             startup_config_line):
                    temp_line = startup_config_line.replace("\"", "")
                    startup_config_temp.append(temp_line)
                    helpers.log("Rearranging line: %s" % temp_line)
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
        startup_config_temp.append("username recovery")
        startup_config = startup_config_temp

        helpers.log("Startup config after adjustments:")
        for line in startup_config:
            helpers.log("SC contains line: %s" % line)
        running_config_temp = []
        for running_config_line in running_config:
            helpers.log("Analyzing line %s" % running_config_line)
            # Excluding comments and empty lines
            if not re.match(r'!|^\s*$', running_config_line):
                if "show running-config" in running_config_line:
                    helpers.log("Skipping line: %s" % running_config_line)
                    continue
                if "no telnet enable" in running_config_line:
                    helpers.log("Skipping line: %s" % running_config_line)
                    continue
                if "username recovery" in running_config_line:
                    running_config_line = "username recovery"
                    running_config_temp.append(running_config_line)
                    helpers.log("Rearranging line: %s" % running_config_line)
                    continue
                if "snmp-server location 'Not set'" in running_config_line:
                    helpers.log("Skipping line: %s" % running_config_line)
                    continue
                if "snmp-server contact 'Not set'" in running_config_line:
                    helpers.log("Skipping line: %s" % running_config_line)
                    continue
                if "snmp-server enable" in running_config_line:
                    helpers.log("Skipping line: %s" % running_config_line)
                    continue
                if re.match(r'snmp-server trap Fan 6|snmp-server trap Fan 7',
                             running_config_line):
                    if "Fan 6" in running_config_line:
                        tmp_ln = running_config_line.replace("Fan 6", "Fan 6/7")
                    elif "Fan 7" in running_config_line:
                        tmp_ln = running_config_line.replace("Fan 7", "Fan 6/7")
                    running_config_temp.append(tmp_ln)
                    helpers.log("Rearranging line: %s" % tmp_ln)
                    continue
                if re.match(r'snmp-server contact|snmp-server location',
                             running_config_line):
                    temp_line = running_config_line.replace("\'", "")
                    running_config_temp.append(temp_line)
                    helpers.log("Rearranging line: %s" % temp_line)
                    continue
                if re.match(r'^hash.*', running_config_line):
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
            n.console_close()
            return helpers.test_failure("Failure due to missing lines")
        else:
            helpers.log("Running-config for switch %s is correct" % mac)
            n.console_close()
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
        url = ('/api/v1/data/controller/applications/bcf/info/fabric/'
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
        url = ('/api/v1/data/controller/applications/bcf/info/fabric/'
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
        url = ('/api/v1/data/controller/applications/bcf/info/fabric/'
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
        url = ('/api/v1/data/controller/applications/bcf/info/fabric/'
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
        url = ('/api/v1/data/controller/applications/bcf/info/fabric/'
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
        url = ('/api/v1/data/controller/applications/bcf/info/fabric/'
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

    def telnet_reboot_switch(self, switch, password='adminadmin'):
        """
        Issue reboot command for switch

        Inputs:
        | switch | Alias of the switch |

        Return Value:
        - True if reboot triggered successfully, False otherwise
        """
        t = test.Test()
        n = t.node(switch)
        s = t.dev_console(switch, modeless=True)
        s.send(helpers.ctrl('c'))
        s.send("\x03")
        options = s.expect([r'[\r\n]*.*login: $', r'[Pp]assword:', r'root@.*:\~\#',
                            r'onie:/ #', r'=> ', r'loader#', s.get_prompt(),
                            r'press control-c now to enter loader shell',
                            r'Trying manifest'], timeout=120)
        if options[0] == 0:  # login prompt
            s.send('admin')
            options = s.expect([r'[Pp]assword:', s.get_prompt()])
            if options[0] == 0:
                helpers.log("Logging in as admin with password %s" % password)
                s.cli(password)
            s.cli('enable; config')
            s.send('reload now')
        elif options[0] == 1:  # password prompt
            s.send(helpers.ctrl('c'))
            s.send('admin')
            options = s.expect([r'[Pp]assword:', s.get_prompt()])
            if options[0] == 0:
                helpers.log("Logging in as admin with password %s" % password)
                s.cli(password)
            s.cli('enable; config')
            s.send('reload now')
        elif options[0] == 2:  # bash mode
            s.cli('exit')
            s.cli('enable; config')
            s.send('reload now')
        elif options[0] == 3:  # ONIE loader
            s.send('reboot')
        elif options[0] == 4:  # U-boot
            s.send('boot')
        elif options[0] == 5:  # SL Loader
            s.send('reboot')
        elif options[0] == 6:  # CLI
            s.cli('enable; config')
            s.send('reload now')
        elif options[0] == 7:  # SL Loader
            s.send(helpers.ctrl('c'))
            s.send("\x03")
            s.send('reboot')
        elif options[0] == 8:  # SL Loader
            helpers.log("Switch %s is already rebooting. Doing nothing." % switch)
            n.console_close()
            return True
        try:
            if options[0] == 4:
                s.expect(r'\(Re\)start USB')
            # else:
            #    s.expect(r'Clock Configuration:', timeout=120)
            helpers.log("Switch %s rebooted" % switch)
        except:
            helpers.log(s.cli('')['content'])
            n.console_close()
            return helpers.test_failure("Error rebooting switch %s" % switch)

        n.console_close()
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

        s.send(" ")
        helpers.sleep(1)
        s.send("abc")
        helpers.sleep(1)
        s.send(helpers.ctrl('c'))
        helpers.sleep(1)
        s.send("\x03")
        options = s.expect([r'[\r\n]*.*login: $', r'\=\>'], timeout=100)
        if options[0] == 0:
            helpers.log("Something went wrong, trying again")
            s.send("admin")
            s.send("enable; config; reload now")
            s.expect("Hit any key to stop autoboot")
            s.send(" ")
            s.send(helpers.ctrl('c'))
            s.send("\x03")
            s.expect(r'\=\>')
            helpers.log("U-boot shell entered")
            return True
        if options[0] == 1:
            helpers.log("U-boot shell entered")
            return True

    def telnet_reset_switch_to_factory_default(self, switch):
        """
        Enter switch u-boot shell while switch is booting up
        and reset environment variables to default

        Inputs:
        | switch | Alias of the switch |

        Return Value:
        - True if successfully restored factory settings, False otherwise
        """
        t = test.Test()
        self.telnet_reboot_switch(switch)
        s = t.dev_console(switch, modeless=True)
        try:
            s.expect("Hit any key to stop autoboot")
        except:
            return helpers.test_failure("Unable to stop at u-boot shell")

        s.send("")
        s.expect([r'\=\>'], timeout=30)
        s.send("env default -a")
        s.expect([r'\=\>'], timeout=30)
        s.send("saveenv")
        s.expect([r'\=\>'], timeout=30)
        s.send("reset")
        s.expect("Hit any key to stop autoboot", timeout=100)
        return True

    def telnet_reinstall_switchlight(self, switch):
        """
        Enter switch u-boot shell while switch is booting up
        and request switchlight reinstall

        Inputs:
        | switch | Alias of the switch |

        Return Value:
        - True if successfully requested switchlight reinstall, False otherwise
        """
        t = test.Test()
        n = t.node(switch)
        s = t.dev_console(switch, modeless=True)
        self.power_down_switch(switch)
        helpers.sleep(10)
        self.power_up_switch(switch)
        try:
            options = s.expect([r"Hit any key to stop autoboot",
                     "Press enter to boot the selected OS"], timeout=100)
        except:
            return helpers.test_failure("Unable to stop at u-boot shell")

        if options[0] == 0:
            s.send("")
            s.expect([r'\=\>'], timeout=30)
            s.send("setenv onie_boot_reason install")
            s.expect([r'\=\>'], timeout=30)
            s.send("run onie_bootcmd")
            s.expect("Loading Open Network Install Environment")
        elif options[0] == 1:
            s.send("v")
            s.send("")
            s.expect([r'Loading ONIE'], timeout=30)
            s.expect([r'ONIE: Install OS'], timeout=30)
        n.console_close()
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

    def cli_reboot_switch(self, node, switch):
        """
        Reboot switch, switches from controller's CLI

        Inputs:
        | node | reference to controller as defined in .topo file |
        | switch | Alias, IP, MAC of the switch, or All |

        Return Value:
        - True if successfully executed reboot command, False otherwise
        """
        t = test.Test()
        c = t.controller(node)
        c.config("")
        helpers.log("Executing 'system reboot switch %s' command"
                    " on node %s" % (switch, node))
        try:
            c.send("system reboot switch %s" % switch)
            helpers.log(c.cli_content())
            options = c.expect([r'to continue', c.get_prompt(),
                                r'Waiting for reconnect'], timeout=30)
            if options[0] == 0:
                helpers.log("Switch has fabric role configured. Confirming.")
                c.send("yes")
                c.expect(c.get_prompt(), timeout=120)
            if options[0] == 2:
                helpers.log("Rebooting all switches. Waiting for CLI prompt...")
                c.expect(c.get_prompt(), timeout=120)
            if 'Error' in c.cli_content():
                helpers.log(c.cli_content())
                helpers.log("Error rebooting the switch")
                return False
        except:
            helpers.log(c.cli_content())
            helpers.log("Error rebooting the switch")
            return False

        helpers.log("Reboot command executed successfully")
        return True

    def cli_reset_connection_switch(self, node, switch):
        """
        Reset connection with switch, switches from controller's CLI

        Inputs:
        | node | reference to controller as defined in .topo file |
        | switch | Alias, IP, MAC of the switch, or All |

        Return Value:
        - True if successfully executed reboot command, False otherwise
        """
        t = test.Test()
        c = t.controller(node)
        c.config("")
        helpers.log("Executing 'system reset-connection switch %s' command"
                    " on node %s" % (switch, node))
        try:
            c.send("system reset-connection switch %s" % switch)
            helpers.log(c.cli_content())
            options = c.expect([r'to continue', c.get_prompt()], timeout=30)
            if options[0] == 0:
                helpers.log("Switch has fabric role configured. Confirming.")
                c.send("yes")
                c.expect(c.get_prompt(), timeout=15)
            if 'Error' in c.cli_content():
                helpers.log(c.cli_content())
                helpers.log("Error rebooting the switch")
                return False
        except:
            helpers.log(c.cli_content())
            helpers.log("Error resetting connection with the switch")
            return False

        helpers.log("Reset connection command executed successfully")
        return True

    def console_bash_switch_mode_nonztn(self, node):
        """
        Set the bootmode for switch - non ztn
        Author- Mingtao
        Inputs:
        | node | Alias of the switch |
        Return Value:  True
        """

        t = test.Test()
        s = t.dev_console(node)
        content = s.bash('cat /mnt/flash/boot-config')['content']
        temp = helpers.strip_cli_output(content)

        helpers.log('USR OUTPUT: %s ' % temp)

        if (re.match(r'.*BOOTMODE=ztn.*', temp, flags=re.DOTALL)):
            helpers.log('The switch: %s is in ZTN mode ' % node)
            image = 'SWI=http://10.192.74.102/export/switchlight/autobuilds/master/latest.switchlight-powerpc-release-bcf.swi'
            sedstring = 's;^BOOTMODE.*;' + image + ';'
            line = 'sed -i.orig \'' + sedstring + '\'  /mnt/flash/boot-config'
            s.bash(line)
            s.bash('cat /mnt/flash/boot-config')
            helpers.log(s.bash('')['content'])
        elif (re.match(r'.*SWI=.*', temp, flags=re.DOTALL)):
            helpers.log('The switch: %s is NOT in  ztn mode ' % node)
        else:
            helpers.log('ERROR:  not able to figure out the boot mode of switch: %s ' % node)
            helpers.test_failure('ERROR:  not able to figure out the boot mode')

        s.cli('')
        return True

    def console_bash_switch_mode_ztn(self, node):
        """
        Set the bootmode for switch - ztn
        Author- Mingtao
        Inputs:
        | node | Alias of the switch |
        Return Value:  True
        """
        t = test.Test()
        s = t.dev_console(node)
        content = s.bash('cat /mnt/flash/boot-config')['content']
        temp = helpers.strip_cli_output(content)
        helpers.log('USR OUTPUT: %s ' % temp)

        if (re.match(r'.*SWI=.*', temp, flags=re.DOTALL)):
            helpers.log('The switch: %s is NOT in  ztn mode, setting to ztn ' % node)
            bootmode = 'BOOTMODE=ztn'
            sedstring = 's;^SWI=.*;' + bootmode + ';'
            line = 'sed -i.orig \'' + sedstring + '\'  /mnt/flash/boot-config'
            s.bash(line)
            s.bash('cat /mnt/flash/boot-config')
            helpers.log(s.bash('')['content'])
        elif (re.match(r'.*BOOTMODE=ztn.*', temp, flags=re.DOTALL)):
            helpers.log('The switch: %s is in  ztn mode ' % node)
        else:
            helpers.log('ERROR:  not able to figure out the boot mode of switch: %s ' % node)
            helpers.test_failure('ERROR:  not able to figure out the boot mode')
        s.cli('')
        return True

    def console_bash_switch_add_ztnserver(self, node, ztnserver):
        """
        add ztn server to switch
        Author- Mingtao
        Inputs:
            node  -  Alias of the switch
            ztnserver  - ztnservers

        Return Value:  True
        """
        t = test.Test()
        s = t.dev_console(node)
        content = s.bash('cat /mnt/flash/boot-config')['content']
        temp = helpers.strip_cli_output(content)
        helpers.log('USR OUTPUT: %s ' % temp)
        if (re.match(r'.*ZTNSERVERS.*', temp, flags=re.DOTALL)):
            helpers.log('The switch: %s has ZTNSERVER, remove it ' % node)
            # line= 'cat /mnt/flash/boot-config | sed -i.orig \''+ '/^ZTNSERVERS.*/d\' > /mnt/flash/boot-config'
            line = "sed -i.orig '/^ZTNSERVERS.*/d' /mnt/flash/boot-config"
            helpers.log("the sed line is:  '%s'" % line)
            s.bash(line)
            s.bash('cat /mnt/flash/boot-config')
            helpers.log(s.bash('')['content'])

        else:
            helpers.log('The switch: %s does NOT have ZTNSERVER' % node)
        helpers.log('Adding ZTNSERVER  %s to switch %s' % (ztnserver, node))
        line = 'echo ' + '\"ZTNSERVERS=' + ztnserver + '\"' + " >> " + '/mnt/flash/boot-config'
        s.bash(line)
        s.bash('cat /mnt/flash/boot-config')
        helpers.log(s.bash('')['content'])

        s.cli('')
        return True

    def console_bash_switch_delete_ztnserver(self, node):
        """
        remove ztn server to switch
        Author- Mingtao
        Inputs:
            node  -  Alias of the switch

        Return Value:  True
        """
        t = test.Test()

        s = t.dev_console(node)
        content = s.bash('cat /mnt/flash/boot-config')['content']
        temp = helpers.strip_cli_output(content)
        helpers.log('USR OUTPUT: %s ' % temp)
        if (re.match(r'.*ZTNSERVERS.*', temp, flags=re.DOTALL)):
            helpers.log('The switch: %s has ZTNSERVER, remove it ' % node)
            line = "sed -i.orig '/^ZTNSERVERS.*/d\'  /mnt/flash/boot-config"
            helpers.log('the sed line is:  %s' % line)
            s.bash(line)
            s.bash('cat /mnt/flash/boot-config')
            helpers.log(s.bash('')['content'])
        else:
            helpers.log('The switch: %s does NOT have ZTNSERVER' % node)
        s.cli('')
        return True

    def console_bash_switch_default_boot_config(self, node):
        """
        remove ztn server to switch
        Author- Mingtao
        Inputs:
            node  -  Alias of the switch

        Return Value:  True
        """
        t = test.Test()

        s = t.dev_console(node)
        content = s.bash('cat /mnt/flash/boot-config')['content']
        temp = helpers.strip_cli_output(content)
        helpers.log('USR OUTPUT: %s ' % temp)
        s.bash('echo " NETDEV=ma1" > /mnt/flash/boot-config')
        s.bash('echo " NETAUTO=dhcp" >> /mnt/flash/boot-config')
        s.bash('echo " BOOTMODE=ztn" >> /mnt/flash/boot-config')

        s.bash('cat /mnt/flash/boot-config')
        helpers.log(s.bash('')['content'])

        s.cli('')
        return True





    def power_cycle_switch(self, switch, minutes=0):
        """
        Power cycle a switch

        Inputs:
        | switch | Alias of the switch |

        Return Value:
        - True if successfully power cycled the switch, False otherwise
        """
        t = test.Test()
        t.power_cycle(switch, minutes=minutes)
        return True
    def power_down_switch(self, switch, minutes=0):
        """
        Power cycle a switch

        Inputs:
        | switch | Alias of the switch |

        Return Value:
        - True if successfully powered down the switch, False otherwise
        """
        t = test.Test()
        t.power_down(switch, minutes=minutes)
        return True

    def power_up_switch(self, switch, minutes=0):
        """
        Power cycle a switch

        Inputs:
        | switch | Alias of the switch |

        Return Value:
        - True if successfully powered up the switch, False otherwise
        """
        t = test.Test()
        t.power_up(switch, minutes=minutes)
        return True

    def cli_get_switch_image(self, image, switch):
        """
        Get SWI or Installer Versions in the switch from the controller

        Inputs:
        | image | SL image - swi or installer |
        | switch | reference to switch/controller as defined in .topo file |

        Return Value:
        - SWI or Installer Versions, None in case of errors
        """

        if image != 'swi' and image != 'installer':
            helpers.log("Please use \'swi\' or \'installer\'")
            return None

        t = test.Test()
        c = t.controller('master')
        helpers.log('INFO: Entering ==> cli_get_switch_image ')
        c.cli('show switch %s version ' % switch)
        content = c.cli_content()
        temp = helpers.strip_cli_output(content)
        temp = helpers.str_to_list(temp)

        version = ''

        if image == 'installer':
            line1 = "Loader Version: "
            line2 = "Loader Build: "
        if image == 'swi':
            line1 = "Software Image Version: "
            line2 = "Internal Build Version: "
        for line in temp:
            if line1 in line:
                version = line.replace(line1, '')
            if line2 in line:
                line = line.replace(line2, '')
                if ' ' in line:
                    line = line.replace(' ', '')
                version = version + " (" + line + ")"
        return version

    def telnet_run(self, switch, cmd):
        """
        Issue given command for a switch

        Inputs:
        | switch | Alias of the switch |

        Return Value:
        - True if reboot triggered successfully, False otherwise
        """
        t = test.Test()
        n = t.node(switch)
        s = t.dev_console(switch)
        helpers.log("Running command %s" % cmd)
        s.config(cmd)
        return True

    def telnet_delete_ztn_cache(self, resource, switch):
        """
        Delete ZTN cache on a switch by executing bash command

        Inputs:
        | switch | Alias of the switch |

        Return Value:
        - True if cache cleared successfully, False otherwise
        """
        t = test.Test()
        n = t.node(switch)
        s = t.dev_console(switch)
        if resource == 'all':
            helpers.log("Running command 'ztn --delete' in bash mode")
            s.bash("ztn --delete")
        elif resource == 'swi':
            helpers.log("Running command 'rm -r /mnt/flash2/ztn/cache/swi/' in bash mode")
            s.bash("rm -r /mnt/flash2/ztn/cache/swi/")
        elif resource == 'startup':
            helpers.log("Running command 'rm -r /mnt/flash2/ztn/cache/startup-config/' in bash mode")
            s.bash("rm -r /mnt/flash2/ztn/cache/startup-config/")
        else:
            helpers.log("Resource is none of all, swi, startup")
            return False
        n.console_close()
        return True
