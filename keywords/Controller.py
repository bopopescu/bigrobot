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
        c.cli.cmd(cmd)
        helpers.log(c.cli.response())
