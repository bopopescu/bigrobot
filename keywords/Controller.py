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
        t = test.Test()
        n = t.node(node)
        if not helpers.is_controller(node):
            helpers.test_error("Node must be a controller ('c1', 'c2').")
        
        n.enable("boot factory-default", prompt="Do you want to continue \[no\]\? ")
        n.enable("yes",                  prompt='Enter NEW admin password:')
        n.enable("adminadmin",           prompt='Repeat NEW admin password:')
        #n.enable("adminadmin",           prompt=r'Connection to .* closed')
        n.enable("adminadmin",           prompt=r'UNAVAILABLE localhost')

        helpers.log("****** I am here")