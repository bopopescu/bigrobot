"""
Keyword library: Controller
"""
import autobot.helpers as helpers
import autobot.test as test


class Controller(object):

    def __init__(self):
        pass

    def cli_show_user(self, node, user=None):
        t = test.Test()
        c = t.controller(node)
        cmd = 'show user'
        if user:
            cmd = ''.join((cmd, ' ', user))
        c.cli(cmd)

    def cli_show_question_mark(self, node):
        t = test.Test()
        n = t.controller(node)
        n.send("show ?")
        n.set_prompt()
        helpers.log("***** I am here")

    def _boot_switchlight(self, node):
        t = test.Test()
        n = t.node(node)
        n.send("reload now")
        n.expect('The system is going down for reboot')

    def _boot_bvs(self, node):
        t = test.Test()
        n = t.node(node)
        n.enable("reboot", prompt="Confirm Reboot (yes to continue) ")
        n.enable("yes", prompt='Broadcast message from root@controller ')

    def _boot_bigtap_bigwire(self, node):
        t = test.Test()
        n = t.controller(node)
        n.send("reload")
        n.expect(r'Confirm Reload \(yes to continue\)')
        n.send("yes")
        n.expect('The system is going down for reboot')

    def cli_reload(self, node):
        """
        Reloads (aka reboots) a controller - BigTap, BigWire, BVS, or
        SwitchLight.
        """
        t = test.Test()
        n = t.controller(node)

        platform = n.platform()
        helpers.log("Reloading '%s' (platform=%s)" % (n.name(), n.platform()))

        if helpers.is_bigwire(platform) or helpers.is_bigtap(platform):
            self._boot_bigtap_bigwire(node)
        elif helpers.is_bvs(platform):
            self._boot_bvs(node)
        elif helpers.is_switchlight(platform):
            self._boot_switchlight(node)
        else:
            helpers.test_error("Reload does not recognize platform '%s'"
                               % platform)

        helpers.log("Device '%s' has rebooted" % n.name)

    def cli_reboot(self, *args, **kwargs):
        """
        Alias for 'cli reload'.
        """
        return self.cli_reload(*args, **kwargs)

    def cli_save_running_config(self, node=None):
        """
        Save the running configuration on the controller.
        This will write the config file to
        /opt/bigswitch/run/saved-configs/running-config-bigrobot

        :param node: (Str) Node name. If not specified, run command on
                           all controller nodes.
        """
        t = test.Test()
        if node:
            helpers.is_controller_or_error(node)
            node_list = [node]
        else:
            node_list = t.controllers()

        for name in node_list:
            helpers.log("Copying running-config to file on node '%s'" % name)
            _node = t.topology(name)
            _node.enable('copy running-config file://running-config-bigrobot')

    def cli_boot_factory_default(self, node):
        """
        Runs boot factory-default. This will cause the SSH connection to disappear and the session would need to be restarted.
        """
        t = test.Test()
        n = t.node(node)
        n.enable("boot factory-default", prompt=r'Do you want to continue \[no\]\? ')
        n.enable("yes", prompt='Enter NEW admin password: ')
        n.enable("adminadmin", prompt='Repeat NEW admin password: ')
        n.enable("adminadmin", prompt='UNAVAILABLE localhost')

        # At this point, device is rebooted and we lose the session handle.
        # Connect to device console to complete first-boot.
        helpers.log("Boot factory-default completed on '%s'. System should be rebooting." % node)

    def cli_add_first_boot(self,
                           node,
                           ip_address,
                           netmask='',
                           gateway='',
                           dns_server='',
                           dns_search='',
                           ntp_server='',
                           timezone='America/Los_Angeles'):
        """
        First boot setup - It will then connect to the console to complete the
        first-boot configuration steps (call 'cli add first boot').
        """
        t = test.Test()

        helpers.log("Getting the console telnet session for '%s'" % node)
        n = t.node(node).console()

        n.send('')  # press <Enter> and expect to see the login prompt
        helpers.sleep(3)
        n.expect('Big Tap Controller')
        n.expect('Log in as .+? to configure')
        n.expect('localhost login: ')

        # For some unknown reason, Exscript will receive '%admin' as the input
        # (extra '%' character somehow got added) which will cause authen to
        # fail. The steps below is to get past the authen failure and retry
        # the login/password. It should pass the 2nd time around.

        n.send('admin')  # first attempt - expect failure
        n.expect('Password: ')
        n.send('')
        n.expect('Password: ')
        n.send('')
        n.expect('Login incorrect')
        n.expect('localhost login: ')

        n.send('admin')  # second attempt - expect success
        n.expect('Password: ')
        n.send('adminadmin')

        # First boot questionaire
        #   Configuration IPv4 Address: 10.192.5.191
        #   IPv4 subnet mask [255.255.255.0]: 255.255.252.0
        #   Default gateway IPv4 address [10.192.4.1]: 10.192.4.1
        #   Hostname (optional):
        #   DNS server 1 IPv4 address (optional): 192.168.15.2
        #   DNS server 2 IPv4 address (optional):
        #   DNS search domain (optional): bigswitch.com
        #   NTP server hostname or address [0.bigswitch.pool.ntp.org]: 0.bigswitch.pool.ntp.org
        #   ...
        #   Apply these settings [yes]? yes

        n.expect('Configuration IPv4 Address: ')
        n.send(ip_address)
        n.expect(r'IPv4 subnet mask .+?: ')
        n.send(netmask)
        n.expect(r'Default gateway IPv4 address .+?: ')
        n.send(gateway)
        n.expect(r'Hostname \(optional\): ')
        n.send('')  # don't configure a hostname (press <Enter> for default)
        n.expect(r'DNS server 1 IPv4 address .+?: ')
        n.send(dns_server)
        n.expect(r'DNS server 2 IPv4 address .+?: ')
        n.send('')  # don't configure a 2nd DNS server
        n.expect(r'DNS search domain .+?: ')
        n.send(dns_search)
        n.expect(r'NTP server hostname or address .+?: ')
        n.send(ntp_server)
        n.expect(r'Apply these settings .+?\? ')
        n.send('yes')

        # helpers.log("Waiting for system to process info")
        # helpers.sleep(10)

        # Additional output and questions
        #   Enter the IP address of master controller OR
        #   To start a new cluster, just enter <cr>.
        #   Existing controller IP:
        #   clustername = 6771f3f3-b18e-4bcd-b01b-5969706bd195.0
        #   Enter NEW recovery password:
        #   Repeat NEW recovery password:
        #   Initializing the database. Please do not hit CTRL-C from here onwards. This may take a while...
        #   updating cassandra config with seed =  10.192.5.191
        #   Setting static IP address
        #   Setting gateway
        #   Setting DNS1
        #   Setting domain
        #   Setting NTP
        #   Time zone [UTC]: America/Los_Angeles
        #
        #   First-time setup complete!
        #
        #   localhost login: [11910.956374] Restarting system.

        n.expect('Existing controller IP: ')
        n.send('')  # press <Enter>
        n.expect('Enter NEW admin password: ')
        n.send('adminadmin')

        # Hmmm... It doesn't always ask for recovery password...

        n.expect('Enter NEW recovery password:')
        n.send('bsn')
        n.expect('Repeat NEW recovery password:')
        n.send('bsn')

        helpers.log("Waiting for system to process info")
        helpers.sleep(10)
        n.expect('Time zone .+?: ')
        n.send(timezone)
        n.expect('First-time setup complete!')

        loss = helpers.ping(ip_address)
        if loss < 50:
            helpers.log("Node '%s' has survived first-boot!" % node)
            return True
        else:
            return False

    def cli_add_first_boot2(self,
                            node,
                            ip_address,
                            hostname='',
                            netmask='',
                            gateway='',
                            dns_server='',
                            dns_server2='',
                            dns_search='',
                            controller_ip='',
                            ntp_server='',
                            timezone='America/Los_Angeles'):
        """
        First boot setup - connect to the console to complete the first-boot configuration steps.
        It calls keyword 'cli add first boot'.
        """
        t = test.Test()

        n = t.host('h1')
        helpers.log("Getting the console telnet session for '%s'" % node)

        # n = t.node(node).console()
        # n = t.node(node)
        n.bash('uptime')
        n.send('telnet %s %s' % ("blade-1-a.bigswitch.com", 15902))
        n.send('')  # press <Enter> and expect to see the login prompt
        n.send('')
        # helpers.sleep(3)
        n.expect('Big Tap Controller')
        n.expect('Log in as .+? to configure')
        n.expect('localhost login: ')

        # For some unknown reason, Exscript will receive '%admin' as the input
        # (extra '%' character somehow got added) which will cause authen to
        # fail. The steps below is to get past the authen failure and retry
        # the login/password. It should pass the 2nd time around.

        n.send('admin')  # first attempt - expect failure
        n.expect('Password: ')
        n.send('')
        n.expect('Password: ')
        n.send('')
        n.expect('Login incorrect')
        n.expect('localhost login: ')

        n.send('admin')  # second attempt - expect success
        n.expect('Password: ')
        n.send('adminadmin')

        # First boot questionaire
        #   Configuration IPv4 Address: 10.192.5.191
        #   IPv4 subnet mask [255.255.255.0]: 255.255.252.0
        #   Default gateway IPv4 address [10.192.4.1]: 10.192.4.1
        #   Hostname (optional):
        #   DNS server 1 IPv4 address (optional): 192.168.15.2
        #   DNS server 2 IPv4 address (optional):
        #   DNS search domain (optional): bigswitch.com
        #   NTP server hostname or address [0.bigswitch.pool.ntp.org]: 0.bigswitch.pool.ntp.org
        #   ...
        #   Apply these settings [yes]? yes

        n.expect('Configuration IPv4 Address: ')
        n.send(ip_address)
        n.expect(r'IPv4 subnet mask .+?: ')
        n.send(netmask)
        n.expect(r'Default gateway IPv4 address .+?: ')
        n.send(gateway)
        n.expect(r'Hostname \(optional\): ')
        n.send(hostname)  # can press <Enter> for default
        n.expect(r'DNS server 1 IPv4 address .+?: ')
        n.send(dns_server)
        n.expect(r'DNS server 2 IPv4 address .+?: ')
        n.send(dns_server2)  # don't configure a 2nd DNS server
        n.expect(r'DNS search domain .+?: ')
        n.send(dns_search)
        n.expect(r'NTP server hostname or address .+?: ')
        n.send(ntp_server)
        n.expect(r'Apply these settings .+?\? ')
        n.send('yes')
        helpers.log("Waiting for system to process info")
        helpers.sleep(10)

        # Additional output and questions
        #   Enter the IP address of master controller OR
        #   To start a new cluster, just enter <cr>.
        #   Existing controller IP:
        #   clustername = 6771f3f3-b18e-4bcd-b01b-5969706bd195.0
        #   Enter NEW recovery password:
        #   Repeat NEW recovery password:
        #   Initializing the database. Please do not hit CTRL-C from here onwards. This may take a while...
        #   updating cassandra config with seed =  10.192.5.191
        #   Setting static IP address
        #   Setting gateway
        #   Setting DNS1
        #   Setting domain
        #   Setting NTP
        #   Time zone [UTC]: America/Los_Angeles
        #
        #   First-time setup complete!
        #
        #   localhost login: [11910.956374] Restarting system.

        n.expect('Existing controller IP: ')
        n.send(controller_ip)
        # n.send('')  # press <Enter>

        # Hmmm... sometimes it won't ask for admin password...

        prompt_pw = ['Enter NEW admin password: ',
                     'Enter NEW recovery password:']
        n.expect(prompt_pw)

        n.send('')

        idx, _ = n.expect(prompt_pw)

        if idx == 0:
            helpers.log("Matched '%s" % prompt_pw[idx])
            n.send('adminadmin')

            # Hmmm... sometimes it seems the password is not getting sent. When
            # that happens, you see:
            #   prompt_for_password: *** empty password
            #   Enter NEW admin password:

            n.expect('Repeat NEW admin password: ')
            n.send('adminadmin')

            # Hmmm ... It doesn't always see the entered password
            # n.expect(['Repeat NEW admin password: ',
            #           'prompt_for_password: .+? empty password'])
            #
            # if re.search(r'empty password', n.cli_content()):
            #     n.expect('Enter NEW admin password: ')
            #     n.send('adminadmin')
            #
            # n.send('adminadmin')
            #
            # n.expect('Enter NEW recovery password:')

        elif idx == 1:
            helpers.log("Matched '%s" % prompt_pw[idx])

        # Hmmm... It doesn't always ask for recovery password...

        n.send('bsn')
        n.expect('Repeat NEW recovery password:')
        n.send('bsn')

        helpers.log("Waiting for system to process info")
        helpers.sleep(10)
        n.expect('Time zone .+?: ')
        n.send(timezone)
        n.expect('First-time setup complete!')

        loss = helpers.ping(ip_address)
        if loss < 50:
            helpers.log("Node '%s' has survived first-boot!" % node)
            return True
        else:
            return False

    def cli_boot_factory_default_and_first_boot(self, node, *args, **kwargs):
        """
        Call 'cli boot factory default' to put device in first-boot mode. Then call 'cli_add_first_boot' to configure the device.
        """
        do_factory_boot = True
        do_first_boot = True

        if not helpers.is_controller(node):
            helpers.test_error("Node must be a controller ('c1', 'c2').")

        if do_factory_boot:
            self.cli_boot_factory_default(node)
            sec = 30
            helpers.log("Sleeping for %s seconds" % sec)
            helpers.sleep(sec)

        if do_first_boot:
            self.cli_add_first_boot(node, *args, **kwargs)
