'''
###  WARNING !!!!!!!
###
###  This is where common code for Controller will go in.
###
###  To commit new code, please contact the Library Owner:
###  Vui Le (vui.le@bigswitch.com)
###
###  DO NOT COMMIT CODE WITHOUT APPROVAL FROM LIBRARY OWNER
###
###  Last Updated: 03/11/2014
###
###  WARNING !!!!!!!
'''

import autobot.helpers as helpers
import autobot.test as test
import re


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
        n.cli('')
        n.send("show ?")
        n.set_prompt()
        helpers.log("***** I am here")

    def _boot_switchlight(self, node):
        t = test.Test()
        n = t.node(node)
        n.enable('')
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
        n.enable('')
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

        helpers.log("Device '%s' has rebooted" % n.name())

    def cli_reboot(self, *args, **kwargs):
        """
        Alias for 'cli reload'.
        """
        return self.cli_reload(*args, **kwargs)

    def cli_save_running_config(self, node=None,
                                dest_file='running-config-bigrobot'):
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
            node_handles = [t.controller(node)]
        else:
            node_handles = t.controllers()

        for n in node_handles:
            helpers.log("Copying running-config to file on node '%s'"
                        % n.name())
            if helpers.is_t5(n.platform()):
                n.enable('copy running-config config://%s' % dest_file)
            else:
                n.enable('copy running-config file://%s' % dest_file)

    def cli_boot_factory_default(self, node, timeout=360):
        """
        Runs boot factory-default. This will cause the SSH connection to disappear and the session would need to be restarted.
        """
        t = test.Test()
        n = t.node(node)
        if helpers.is_bigtap(n.platform()):
            helpers.log("Boot factory-default on '%s' (Big Tap Controller)" % node)
            n.enable("boot factory-default", prompt=r'Do you want to continue \[no\]\? ')
            n.enable("yes", prompt='Enter NEW admin password: ')
            n.enable("adminadmin", prompt='Repeat NEW admin password: ')
            n.enable("adminadmin", prompt='UNAVAILABLE localhost')
        elif helpers.is_bvs(n.platform()):
            helpers.log("Boot factory-default on '%s' (BVS)" % node)
            helpers.summary_log('BVS boot factory may take a bit of time. Setting timeout to %s seconds.' % timeout)

            # vui-bvs> enable
            # vui-bvs# boot factory-default
            # boot factory default: will over-write the alternate partition
            # proceed ("yes" or "y" to continue): y
            # boot factory default: loading image into stage partition
            # boot factory default: checking integrity of new partition
            # boot factory default: New Partition Ready
            # factory default: ready for reboot
            # boot factory default: reboot? ("yes" or "y" to continue): y
            #
            # Broadcast message from root@blah
            #    (unknown) at 20:32 ...
            #
            # The system is going down for reboot NOW!
            # Connection to 10.192.104.2 closed by remote host.
            # Connection to 10.192.104.2 closed.

            n.enable('')
            n.send('boot factory-default')
            n.expect(r'proceed \("y" or "yes" to continue\)')
            n.send('y')
            n.expect(r'copying image into alternate partition', timeout=timeout)
            n.expect(r'checking integrity of new partition', timeout=timeout)
            n.expect(r'New Partition Ready', timeout=timeout)
            n.expect(r'ready for reboot', timeout=timeout)
            n.expect(r'"y" or "yes" to continue\): ', timeout=timeout)
            n.send('y')
            # n.expect(r'system is going down for reboot')
            helpers.summary_log("'%s' has been rebooted." % node)
        else:
            helpers.test_error("Boot factory-default is only supported on 'bvs' and 'bigtap'")

        # At this point, device is rebooted and we lose the session handle.
        # Connect to device console to complete first-boot.
        helpers.log("Boot factory-default completed on '%s'. System should be rebooting." % node)
        return True

    def cli_add_first_boot(self,
                           node,
                           ip_address=None,
                           netmask='',
                           gateway='',
                           dns_server='',
                           dns_search='',
                           ntp_server='',
                           hostname='mycontroller',
                           cluster_name='mycluster',
                           cluster_descr='',
                           admin_password='adminadmin',
                           platform='bvs',
                           ):
        """
        First boot setup fpr BVS - It will then connect to the console to
        complete the first-boot configuration steps (call
        'cli add first boot').
        """

        if platform != 'bvs':
            helpers.test_error("Only 'bvs' platform is supported")

        t = test.Test()
        n = t.node(node)

        if not ip_address:
            ip_address = n.ip()

        helpers.log("Getting the console session for '%s'" % node)
        n_console = n.console()

        _ = """ Note: Below is the basic first boot question/answer output.

        root@qa-kvm-32:~# virsh console vui-bvs
        Connected to domain vui-bvs
        Escape character is ^]

        Big Virtual Switch Appliance 2.0.5-SNAPSHOT (bvs main #1223)
        Log in as 'admin' to configure

        controller login: admin                                            <===
        Last login: Mon Mar 17 20:28:31 UTC 2014 from 10.192.123.117 on pts/0

        The programs included with the Ubuntu system are free software;
        the exact distribution terms for each program are described in the
        individual files in /usr/share/doc/*/copyright.

        Ubuntu comes with ABSOLUTELY NO WARRANTY, to the extent permitted by
        applicable law.
        <clear screen>

        This product is governed by an End User License Agreement (EULA).
        You must accept this EULA to continue using this product.

        You can view this EULA by typing 'View', or from our website at:
        http://www.bigswitch.com/eula

        Do you accept the EULA for this product? (Yes/No/View) [Yes] > Yes <===

        Running system pre-check

        Found eth0
        Found 2 CPU cores
        Found 2.00 GB of memory

        Finished system pre-check


        Starting first-time setup


        Local Node Configuration
        ------------------------

        Password for emergency recovery user > bsn                         <===
        Retype Password for emergency recovery user > bsn                  <===
        Please choose an IP mode:

        [1] Manual
        [2] Automatic via DHCP

        > 1                                                                <===
        IP address [0.0.0.0/0] > 10.192.104.2                              <===
        CIDR prefix length [24] > 18                                       <===
        Default gateway address (Optional) > 10.192.64.1                   <===
        DNS server address (Optional) > 10.192.3.1                         <===
        DNS search domain (Optional) > bigswitch.com                       <===
        Hostname > blah                                                    <===

        Controller Clustering
        ---------------------

        Please choose a cluster option:

        [1] Start a new cluster
        [2] Join an existing cluster

        > 1                                                                <===
        Cluster name > bleh                                                <===
        Cluster description (Optional) > [enter]                           <===
        Administrator password for cluster > adminadmin                    <===
        Retype Administrator password for cluster > adminadmin             <===

        System Time
        -----------

        Enter NTP server [0.bigswitch.pool.ntp.org] > [enter]              <===

        Menu
        ----

        Please choose an option:

        [ 1] Apply settings
        [ 2] Reset and start over
        [ 3] Update Emergency Recovery Password   (***)
        [ 4] Update IP Auto/Manual                (Manual)
        [ 5] Update Local IP Address              (10.192.104.2)
        [ 6] Update CIDR Prefix Length            (18)
        [ 7] Update Gateway                       (10.192.64.1)
        [ 8] Update DNS Server                    (10.192.3.1)
        [ 9] Update DNS Search Domain             (bigswitch.com)
        [10] Update Hostname                      (blah)
        [11] Update Cluster Option                (Start a new cluster)
        [12] Update Cluster Name                  (bleh)
        [13] Update Cluster Description           (<none>)
        [14] Update Cluster Admin Password        (***)
        [15] Update NTP Server                    (0.bigswitch.pool.ntp.org)

        [1] > 1                                                            <===
        [Stage 0] Initializing system
        [Stage 1] Configuring controller
          Waiting for network configuration
          IP address on eth0 is 10.192.104.2
          Generating cryptographic keys
          Retrieving time from NTP server 0.bigswitch.pool.ntp.org
        [Stage 2] Configuring cluster
          Cluster configured successfully.
          Current node ID is 3146
          All cluster nodes:
            Node 3146: 10.192.104.2:6642

        First-time setup is complete!

        Press enter to continue > [enter]                                  <===

        Big Virtual Switch Appliance 2.0.5-SNAPSHOT (bvs main #1223)
        Log in as 'admin' to configure

        blah login: admin                                                  <===
        Password: *****                                                    <===

        Last login: Mon Mar 17 19:01:17 UTC 2014 on ttyS0
        Big Virtual Switch Appliance 2.0.5-SNAPSHOT (bvs main #1223)
        Logged in as admin, 2014-03-17 20:24:20.843000 UTC, auth from blah
        blah>
        """

        n_console.expect(r'Escape character.*[\r\n]')
        n_console.send('')  # press <Enter> and expect to see the login prompt

        # We might be in midst of a previously failed first boot setup.
        # Interrupt it (Control-C) and press <Enter> to log out...
        n_console.send(helpers.ctrl('c'))
        helpers.sleep(2)
        n_console.send('')

        n_console.expect(helpers.regex_bvs())
        n_console.expect(r'login:')
        n_console.send('admin')

        # Need to enable developer mode to use DHCP option. Magic string
        # to enable it is 'dhcp'.
        n_console.expect(r'Do you accept the EULA.* > ')
        n_console.send('dhcp')
        n_console.expect(r'Developer.* mode enabled.*')
        # The "real" EULA
        n_console.expect(r'Do you accept the EULA.* > ')
        n_console.send('Yes')

        n_console.expect(r'Local Node Configuration')
        n_console.expect(r'Password for emergency recovery user > ')
        n_console.send('bsn')
        n_console.expect(r'Retype Password for emergency recovery user > ')
        n_console.send('bsn')
        n_console.expect(r'Please choose an IP mode:.*[\r\n]')
        n_console.expect(r'> ')
        n_console.send('1')  # Manual
        n_console.expect(r'IP address .* > ')
        n_console.send(ip_address)

        if not re.match(r'.*/\d+', ip_address):
            # Send netmask if IP address doesn't contain prefix length
            n_console.expect(r'CIDR prefix length .* > ')
            n_console.send(netmask)

        n_console.expect(r'Default gateway address .* > ')
        n_console.send(gateway)
        n_console.expect(r'DNS server address .* > ')
        n_console.send(dns_server)
        n_console.expect(r'DNS search domain .* > ')
        n_console.send(dns_search)
        n_console.expect(r'Hostname > ')
        n_console.send(hostname)

        n_console.expect(r'Controller Clustering')
        n_console.expect(r'> ')
        n_console.send('1')  # Start a new cluster
        n_console.expect(r'Cluster name > ')
        n_console.send(cluster_name)
        n_console.expect(r'Cluster description .* > ')
        n_console.send(cluster_descr)
        n_console.expect(r'Administrator password for cluster > ')
        n_console.send(admin_password)
        n_console.expect(r'Retype .* > ')
        n_console.send(admin_password)

        n_console.expect(r'System Time')
        n_console.expect(r'Enter NTP server .* > ')
        n_console.send(ntp_server)

        n_console.expect(r'Please choose an option:.*[\r\n]')
        n_console.expect(r'\[1\] > ')
        n_console.send('1')  # Apply settings

        n_console.expect(r'Initializing system.*[\r\n]')
        n_console.expect(r'Configuring controller.*[\r\n]')
        n_console.expect(r'Configuring cluster.*[\r\n]')
        n_console.expect(r'First-time setup is complete.*[\r\n]')

        n_console.expect(r'Press enter to continue > ')
        n_console.send('')

        helpers.log("Closing console connection for '%s'" % node)
        n.console_close()

        helpers.sleep(3)  # Sleep for a few seconds just in case...

        # Check that controller is now pingable.
        # First remove the prefix from the IP address.
        new_ip_address = re.sub(r'/\d+$', '', ip_address)
        loss = helpers.ping(new_ip_address)
        if loss < 50:
            helpers.log("Node '%s' has survived first-boot!" % node)
            return True
        else:
            return False

    def cli_boot_factory_default_and_first_boot(self, node, reboot_sleep=60,
                                                **kwargs):
        """
        Call 'cli boot factory default' to put device in first-boot mode. Then call 'cli_add_first_boot' to configure the device.
        """
        do_factory_boot = True
        do_first_boot = True

        if not helpers.is_controller(node):
            helpers.test_error("Node must be a controller ('c1', 'c2').")

        if do_factory_boot:
            self.cli_boot_factory_default(node)
            helpers.log("Sleeping for %s seconds before first boot setup"
                        % reboot_sleep)
            helpers.sleep(reboot_sleep)

        if do_first_boot:
            return self.cli_add_first_boot(node, **kwargs)

    def cli_ping(self, node, dest_ip=None, dest_node=None, return_stats=False,
                 *args, **kwargs):
        """
        Perform a ping from the CLI. Returns the loss percentage
        - 0   - 0% loss (default)
        - 100 - 100% loss (default)
        - Stats dict if return_stats is ${true}

        Inputs:
        - node:      The device name as defined in the topology file, e.g., 'c1', 's1', etc.
        - dest_ip:   Ping this destination IP address
        - dest_node  Ping this destination node ('c1', 's1', etc)

        Example:
        | ${lossA} = | Cli Ping | h1          | 10.192.104.1 |
        | ${lossB} = | Cli Ping | node=main | dest_node=s1 |
        =>
        - ${lossA} = 0
        - ${lossB} = 100

        See also Host.bash ping.
        """
        t = test.Test()
        n = t.node(node)

        if not dest_ip and not dest_node:
            helpers.test_error("Must specify 'dest_ip' or 'dest_node'")
        if dest_ip and dest_node:
            helpers.test_error("Specify 'dest_ip' or 'dest_node' but not both")
        if dest_ip:
            dest = dest_ip
        if dest_node:
            dest = t.node(dest_node).ip()
        stats = helpers._ping(dest, node_handle=n, mode='cli', *args, **kwargs)
        if return_stats:
            return stats
        else:
            return stats["packets_loss_pct"]

_ = ''' These methods are candidates for removal...

    def cli_add_first_boot_bigtap(self,
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
        #   Enter the IP address of main controller OR
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

    def cli_add_first_boot_bigtap2(self,
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
        #   Enter the IP address of main controller OR
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
'''
