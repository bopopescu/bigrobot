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
        if os not in ('bsn_controller', 't6mininet'):
            helpers.environment_failure("OS type must be 'bsn_controller' or 't6mininet'.")
        
        helpers.log("Connecting to host %s" % host)
        #helpers.log("User:%s, password:%s" % (user, password))
        account = Account(user, password)
        self.conn = SSH2()
        self.conn.connect(host)
        self.conn.login(account)
        if os == 'bsn_controller':
            # !!! FIXME: Use ios driver in the interim.
            #self.conn.set_driver('bsn_controller')
            pass
        elif os == 't6mininet':
            #self.conn.set_driver('shell')
            pass
        
        self.host = host
        self.user = user
        self.password = password
        self.os = os
        self.last_result = None
        self.mode = 'cli'

    def cmd(self, cmd, quiet=False):
        if not quiet:
            helpers.log("Execute command: %s" % cmd, level=4)
            
        self.conn.execute(cmd)
        self.last_result = { 'content': self.conn.response }
        
        if not quiet:
            helpers.log("Command output: %s" % self.content(), level=4)
        
        return self.result

    # Alias
    cli = cmd
    
    def platform(self):
        driver = self.conn.get_driver()
        if hasattr(driver, 'platform'):
            # Does the driver class have the method platform() defined?
            # See src/protocols/drivers/bsn_controller.py as an example.
            return driver.platform()
        else:
            return "__undefined__"
        
    def result(self):
        return self.last_result

    def content(self):
        return self.result()['content']

    def close(self):
        helpers.log("Closing device %s (OS=%s)." % (self.host, self.os))


class ControllerDevConf(DevConf):
    def __init__(self, host=None, user=None, password=None):
        super(ControllerDevConf, self).__init__(host, user, password, 
                                                #'bvs')
                                                'bsn_controller')
        self.mode_before_bash = None

    def is_cli(self):
        return self.mode == 'cli'

    def is_enable(self):
        return self.mode == 'enable'

    def is_config(self):
        return self.mode == 'config'

    def is_bash(self):
        return self.mode == 'bash'

    def exit_bash_mode(self, new_mode):
        self.mode = self.mode_before_bash
        helpers.log("Switching from bash to %s mode" % new_mode, level=5)
        super(ControllerDevConf, self).cmd('exit', quiet=True)
        helpers.log("Current mode is %s" % self.mode)

    def cmd(self, cmd, quiet=False, mode='cli'):
        if mode == 'cli':
            if self.is_bash():
                self.exit_bash_mode(mode)

            if self.is_enable():
                helpers.log("Switching from enable to %s mode" % mode, level=5)
                super(ControllerDevConf, self).cmd('exit', quiet=True)
            elif self.is_config():
                helpers.log("Switching from config to %s mode" % mode, level=5)
                super(ControllerDevConf, self).cmd('exit', quiet=True)
                super(ControllerDevConf, self).cmd('exit', quiet=True)
        elif mode == 'enable':
            if self.is_bash():
                self.exit_bash_mode(mode)

            if self.is_cli():
                helpers.log("Switching from cli to %s mode" % mode, level=5)
                super(ControllerDevConf, self).cmd('enable', quiet=True)
            elif self.is_config():
                helpers.log("Switching from config to %s mode" % mode, level=5)
                super(ControllerDevConf, self).cmd('exit', quiet=True)
        elif mode == 'config':
            if self.is_bash():
                self.exit_bash_mode(mode)

            if self.is_cli():
                helpers.log("Switching from cli to %s mode" % mode, level=5)
                super(ControllerDevConf, self).cmd('enable', quiet=True)
                super(ControllerDevConf, self).cmd('configure', quiet=True)
            elif self.is_enable():
                helpers.log("Switching from enable to %s mode" % mode, level=5)
                super(ControllerDevConf, self).cmd('configure', quiet=True)
        elif mode == 'bash':
            if self.is_cli():
                self.mode_before_bash = 'cli'
                helpers.log("Switching from cli to %s mode" % mode, level=5)
            elif self.is_enable():
                self.mode_before_bash = 'enable'
                helpers.log("Switching from enable to %s mode" % mode, level=5)
            elif self.is_config():
                self.mode_before_bash = 'config'
                helpers.log("Switching from config to %s mode" % mode, level=5)
            helpers.log("Mode previous to bash is %s" % self.mode_before_bash)
            super(ControllerDevConf, self).cmd('debug bash', quiet=True)
                
        self.mode = mode
        helpers.log("Current mode is %s" % self.mode)

        super(ControllerDevConf, self).cmd(cmd, quiet=True)
        helpers.log("%s result:\n%s\n\n---" % (mode, self.content()), level=5)
        return self.result

    
    def cli(self, cmd, quiet=False):
        return self.cmd(cmd, quiet=quiet, mode='cli')

    def enable(self, cmd, quiet=False):
        return self.cmd(cmd, quiet=quiet, mode='enable')

    def config(self, cmd, quiet=False):
        return self.cmd(cmd, quiet=quiet, mode='config')

    def bash(self, cmd, quiet=False):
        return self.cmd(cmd, quiet=quiet, mode='bash')

    def close(self):
        super(ControllerDevConf, self).close()
        # !!! FIXME: Need to close the controller connection
        

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
        
        # Possible Mininet prompts:
        #   mininet>                 - if successfully acquired Mininet CLI
        #   mininet@t6-mininet: ~$   - on failure
        self.conn.set_prompt(r'(t6-mininet>|mininet@.*mininet:.*\$)')

        self.cli(cmd, quiet=False)

        # Error handling - placeholder (see MinietDevConf for example)

        # Success. Set Mininet prompt.
        self.conn.set_prompt('t6-mininet>')
    
    def close(self):
        super(T6MininetDevConf, self).close()

        self.conn.set_prompt(r'(t6-mininet>|mininet@.*mininet:.*\$)')
        self.cmd('exit', quiet=False)  # Exit mininet CLI
        self.conn.close(force=True)
        helpers.log("T6MininetDevConf - force closed the device connection.")


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
        
        self.cli(cmd, quiet=False)

        # Error handling        
        out = self.content()
        err = helpers.any_match(out, r'(Cleanup complete|error: no such option)')
        if err:
            helpers.test_failure("Mininet CLI unexpected error - %s." % err)

        # Success. Set Mininet prompt.
        self.conn.set_prompt('mininet>')

    def close(self):
        super(MininetDevConf, self).close()

        self.conn.set_prompt(r'(mininet>|mininet@.*mininet:.*\$)')
        self.cmd('exit', quiet=False)  # Exit mininet CLI
        self.conn.close(force=True)
        helpers.log("MininetDevConf - force closed the device connection.")
