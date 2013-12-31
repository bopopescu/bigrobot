import autobot.helpers as helpers
from Exscript import Account
from Exscript.protocols import SSH2

class DevConf(object):
    def __init__(self, host=None, user=None, password=None, os=None):
        """
        :param os: str, supported OS are bvs, t6mininet, shell (host)
        """
        
        if host is None:
            helpers.environment_failure("Must specify a host.")
        if user is None:
            helpers.environment_failure("Must specify a user name.")
        if password is None:
            helpers.environment_failure("Must specify a password.")
        if os not in ('bvs', 't6mininet'):
            helpers.environment_failure("OS type must be 'bvs' or 't6mininet'.")
        
        helpers.log("Connecting to host %s" % host)
        #helpers.log("User:%s, password:%s" % (user, password))
        account = Account(user, password)
        self.conn = SSH2()
        self.conn.connect(host)
        self.conn.login(account)
        if os == 'bvs':
            # !!! FIXME: Use ios driver in the interim.
            self.conn.set_driver('ios')
        elif os == 't6mininet':
            self.conn.set_driver('shell')

    def cmd(self, cmd):
        self.conn.execute(cmd)

    # Alias
    cli = cmd
    
    def response(self):
        return self.conn.response
    

class ControllerDevConf(DevConf):
    def __init__(self, host=None, user=None, password=None):
        super(ControllerDevConf, self).__init__(host, user, password, 'bvs')
    

class T6MininetDevConf(DevConf):
    """
    :param topology: str, in the form
        '--num-spine 0 --num-rack 1 --num-bare-metal 2 --num-hypervisor 0'
    """
    def __init__(self, host=None, user=None, password=None, controller=None,
                 port=6653,
                 topology=None):
        if controller is None:
            helpers.environment_failure("Must specify a controller for T6Mininet.")
        if topology is None:
            helpers.environment_failure("Must specify a topology for T6Mininet.")

        super(T6MininetDevConf, self).__init__(host, user, password, 't6mininet')
        
        # Enter CLI mode
        cmd = ("sudo /opt/t6-mininet/run.sh -c %s:%s %s"
               % (controller, port, topology))
        helpers.log("Execute T6Mininet cmd: %s" % cmd)
        
        # T6Mininet prompt
        self.conn.set_prompt('t6-mininet>')
        self.cli(cmd)
        helpers.log("Response: %s" % self.response())


class MininetDevConf(DevConf):
    """
    :param topology: str, in the form 'tree,4,2'
    """
    def __init__(self, host=None, user=None, password=None, controller=None,
                 topology=None):
        if controller is None:
            helpers.environment_failure("Must specify a controller for Mininet.")
        if topology is None:
            helpers.environment_failure("Must specify a topology for Mininet.")

        super(MininetDevConf, self).__init__(host, user, password, 't6mininet')
        
        # Enter CLI mode
        cmd = ("sudo mn --controller=remote --ip=%s --topo=%s --mac"
               % (controller, topology))
        helpers.log("Execute Mininet cmd: %s" % cmd)

        # Possible Mininet prompts:
        #   mininet>                 - if successfully acquired Mininet CLI
        #   mininet@t6-mininet: ~$   - on failure
        self.conn.set_prompt(r'(mininet>|mininet@.*mininet:.*\$)')
        
        self.cli(cmd)
        out = self.response()
        helpers.log("Response: %s" % out)

        err = helpers.any_match(out, r'(Cleanup complete|error: no such option)')
        if err:
            helpers.test_failure("Mininet CLI unexpected error - %s." % err)

        # Success. Set Mininet prompt.
        self.conn.set_prompt('mininet>')
