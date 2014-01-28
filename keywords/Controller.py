import autobot.helpers as helpers
import autobot.test as test


class Controller(object):

    def __init__(self):
        pass
        
    def cli_show_user(self, user=None):
        t = test.Test()
        c = t.controller()
        cmd = 'show user'
        if user:
            cmd = ''.join((cmd, ' ', user)) 
        c.cli(cmd)
        helpers.log("CLI mode result: %s" % c.cli_content())

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
        
        
        
        
        
        
        
        
        
        
        
        
        
        