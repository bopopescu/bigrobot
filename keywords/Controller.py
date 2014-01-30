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
        n.expect('Confirm Reload \(yes to continue\)')
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
        helpers.log("Reloading '%s' (platform=%s)" % (n.name, n.platform()))

        if helpers.is_bigwire(platform) or helpers.is_bigtap(platform):
            self._boot_bigtap_bigwire(node)
        elif helpers.is_bvs(platform):
            self._boot_bvs(node)
        elif helpers.is_switchlight(platform):
            self._boot_switchlight(node)
        else:
            helpers.test_error("Reload does not recognize platform '%s'" % platform)
        
        helpers.log("Device '%s' has rebooted" % n.name)
    
    # alias
    cli_reboot = cli_reload

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
        Run 'boot factory default' command. This will cause the SSH connection
        to disappear and it would need to be restarted.
        """

        dns_server = '192.168.15.2'
        dns_search = 'bigswitch.com'
        ntp_server = '0.bigswitch.pool.ntp.org'
        
        t = test.Test()
        n = t.node(node)
        if not helpers.is_controller(node):
            helpers.test_error("Node must be a controller ('c1', 'c2').")
        
        #n.enable("boot factory-default", prompt="Do you want to continue \[no\]\? ")
        #n.enable("yes",                  prompt='Enter NEW admin password: ')
        #n.enable("adminadmin",           prompt='Repeat NEW admin password: ')
        #n.enable("adminadmin",           prompt='UNAVAILABLE localhost')
        
        # At this point, device is rebooted and we lose the session handle.
        # Connect to device console to complete first-boot.

        #helpers.test_error("***** I am here!!!")
        
        #n.console().set_prompt(r'localhost login: ?$')
        n.console().cmd('',           prompt=r'localhost login: ?$')
        out = n.console().conn
        helpers.log("out: %s" % out)
        helpers.marker()

        n.console().cmd('admin',      prompt=r'Password: ')
        helpers.marker()

        n.console().cmd('adminadmin', prompt=r'Configuration IPv4 Address: ')
        helpers.marker()

        n.console().cmd(n.ip,         prompt=r'IPv4 subnet mask .+: ')
        helpers.marker()

        n.console().cmd(n.netmask,    prompt=r'Default gateway IPv4 address .+: ')
        helpers.marker()

        """        
        # Let's accept the default value for gateway
        n.console().cmd('',           prompt=r'Hostname (optional): ')
        
        # Ignore hostname
        n.console().cmd('',           prompt='DNS server 1 IPv4 address .+: ')
        n.console().cmd(dns_server,   prompt='DNS server 2 IPv4 address .+: ')
        
        # Ignore DNS2
        n.console().cmd('',           prompt='DNS search domain (optional): ')
        n.console().cmd(dns_search,   prompt='NTP server hostname or address .+: ')
        n.console().cmd(ntp_server,   prompt='Apply these settings .+\? ')
        
        # Press <enter> to accept
        n.console().cmd('',           prompt='Existing controller IP: ')
        
        n.console().cmd('adminadmin', prompt='Enter NEW admin password: ')
        n.console().cmd('adminadmin', prompt='Repeat NEW admin password: ')
        n.console().cmd('adminadmin', prompt='Enter NEW recovery password: ')
        n.console().cmd('adminadmin', prompt='Repeat NEW recovery password: ')
        
        n.console().set_prompt('localhost login: ')
        """
        helpers.log("****** Here I am...")
        
        
        
        
        
        
        
        
        
        
        
        
        
        