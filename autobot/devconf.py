from Exscript import Account
from Exscript.protocols import SSH2, Telnet
from Exscript.protocols.Exception import LoginFailure, TimeoutException
import autobot.helpers as helpers
import autobot.utils as br_utils
import sys


class DevConf(object):
    def __init__(self, host=None, user=None, password=None, port=None,
                 is_console=False,
                 console_driver=None,
                 name=None,
                 debug=0):
        if host is None:
            helpers.environment_failure("Must specify a host.")
        if user is None:
            helpers.environment_failure("Must specify a user name.")
        if password is None:
            helpers.environment_failure("Must specify a password.")

        # helpers.log("User:%s, password:%s" % (user, password))
        account = Account(user, password)

        try:
            if is_console:
                helpers.log("Connecting to console %s, port %s" % (host, port))
                self.conn = Telnet(debug=debug)
                self.conn.connect(host, port)

                if not console_driver:
                    helpers.log("A devconf driver is not specified for console connection")
                else:
                    helpers.log("Setting devconf driver for console to '%s'"
                                % console_driver)
                    self.conn.set_driver(console_driver)

                # Note: User needs to figure out what state the console is in
                #       and manage it themself.

            else:
                auth_info = "(login:%s, password:%s)" % (user, password)
                if port:
                    helpers.log("SSH connect to host %s, port %s %s"
                                % (host, port, auth_info))
                else:
                    helpers.log("Connecting to host %s %s"
                                % (host, auth_info))

                self.conn = SSH2(debug=debug)
                self.conn.connect(host, port)
                self.conn.login(account)
        except LoginFailure:
            helpers.test_error("Login failure: Check the user name and password"
                               " for device %s. Also try to log in manually to"
                               " see what the error is." % host)
            # helpers.log("Exception in %s" % sys.exc_info()[0])
            # raise
        except TimeoutException:
            helpers.test_error("Login failure: Timed out during SSH connnect"
                               " to device %s. Try to log in manually to see"
                               " what the error is." % host)
            # helpers.log("Exception in %s" % sys.exc_info()[0])
            # raise
        except:
            helpers.log("Unexpected SSH login exception in %s\n"
                        "Expect buffer:\n%s%s"
                        % (sys.exc_info()[0],
                           self.conn.buffer.__str__(),
                           br_utils.end_of_output_marker()))
            raise

        driver = self.conn.get_driver()
        helpers.log("Using devconf driver '%s' (name: '%s')"
                    % (driver, driver.name))

        self._name = name
        self.host = host
        self.user = user
        self.password = password
        self.port = port
        self.last_result = None
        self.mode = 'cli'
        self.is_prompt_changed = False

        # Aliases
        self.set_prompt = self.conn.set_prompt

    def name(self):
        return self._name

    def send(self, cmd, quiet=False, level=4):
        """
        Invoking low-level send/expect commands to the device. This is a
        wrapper for Exscript's send(). Use with caution!!!

        This will simply send the command to the device and immediately
        returns. It is intended to be used with expect(). Note that a
        carriage returned is appended to the command.

        See http://knipknap.github.io/exscript/api/Exscript.protocols.Protocol-class.html#send
        """
        if not quiet:
            helpers.log("Send command: '%s'" % cmd, level=level)
        cmd = ''.join((cmd, '\r'))
        self.conn.send(cmd)

    def expect(self, prompt, quiet=False, level=4):
        """
        Invoking low-level send/expect commands to the device. This is a
        wrapper for Exscript's expect(). Use with caution!!!

        This function will wait until there a prompt match or times out in
        the process. It is intended to be used with send().

        See http://knipknap.github.io/exscript/api/Exscript.protocols.Protocol-class.html#expect
        """
        if not quiet:
            helpers.log("Expecting prompt '%s'" % prompt, level=level)

        try:
            ret_val = self.conn.expect(prompt)
            self.last_result = {'content': self.conn.response}
            if not quiet:
                helpers.log("Expect content:\n%s%s"
                            % (self.content(), br_utils.end_of_output_marker()),
                            level=level)
        except TimeoutException:
            helpers.test_error("Expect failure: Timed out during expect prompt '%s'\n"
                               "Expect buffer:\n%s%s"
                               % (prompt,
                                  self.conn.buffer.__str__(),
                                  br_utils.end_of_output_marker()))
            # raise
            # helpers.log("Exception in %s" % sys.exc_info()[0])
            # raise
        except:
            helpers.log("Unexpected expect exception in %s\n"
                        "Expect buffer:\n%s%s"
                        % (sys.exc_info()[0],
                           self.conn.buffer.__str__(),
                           br_utils.end_of_output_marker()))
            raise

        return ret_val

    def waitfor(self, prompt, quiet=False, level=4):
        """
        Invoking low-level send/expect commands to the device. This is a
        wrapper for Exscript's waitfor(). Use with caution!!!

        This function will wait until there a prompt match or times out in
        the process. It is intended to be used with send().

        See http://knipknap.github.io/exscript/api/Exscript.protocols.Protocol-class.html#waitfor
        """
        if not quiet:
            helpers.log("Expecting waitfor prompt '%s'" % prompt, level=level)

        try:
            self.conn.waitfor(prompt)
            self.last_result = { 'content': self.conn.response }
            if not quiet:
                helpers.log("Waitfor (expect) content:\n%s%s"
                            % (self.content(), br_utils.end_of_output_marker()),
                            level=level)
        except TimeoutException:
            helpers.log("Waitfor failure: Timed out during waitfor prompt '%s'"
                        % prompt)
            helpers.log("Waitfor buffer <%s>" % self.conn.buffer.__str__())
            raise
            # helpers.log("Exception in %s" % sys.exc_info()[0])
            # raise
        except:
            helpers.log("Unexpected waitfor exception in %s"
                        % sys.exc_info()[0])
            raise

    def cmd(self, cmd, quiet=False, mode=None, prompt=None, level=5):
        if prompt:
            helpers.log("Expected prompt is '%s'" % prompt)
            self.conn.set_prompt(prompt)
            self.is_prompt_changed = True
        else:
            if self.is_prompt_changed:
                helpers.log("Resetting default prompt")
                self.conn.set_prompt()

        if not quiet:
            helpers.log("Execute command: '%s'" % cmd, level=level)

        self.conn.execute(cmd)
        self.last_result = { 'content': self.conn.response }

        if not quiet:
            helpers.log("Command content:\n%s" % self.content(), level=level)

        return self.result()

    # Alias
    cli = cmd

    def driver(self):
        return self.conn.get_driver()

    def platform(self):
        driver = self.driver()
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
        helpers.log("Closing device %s" % self.host)


class BsnDevConf(DevConf):
    def __init__(self, name=None, host=None, user=None, password=None,
                 port=None, is_console=False, console_driver=None, debug=0):
        super(BsnDevConf, self).__init__(host, user, password,
                                                port=port,
                                                is_console=is_console,
                                                console_driver=console_driver,
                                                name=name,
                                                debug=debug)
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
        super(BsnDevConf, self).cmd('exit', quiet=True)
        helpers.log("Current mode is %s" % self.mode)

    def cmd(self, cmd, quiet=False, mode='cmd', prompt=None, level=5):

        # Check to make sure we're in the right mode prior to executing command
        if mode == 'cli':
            if self.is_bash():
                self.exit_bash_mode(mode)

            if self.is_enable():
                helpers.log("Switching from enable to %s mode" % mode, level=level)
                super(BsnDevConf, self).cmd('exit', quiet=True, level=level)
            elif self.is_config():
                helpers.log("Switching from config to %s mode" % mode, level=level)
                super(BsnDevConf, self).cmd('exit', quiet=True)
                super(BsnDevConf, self).cmd('exit', quiet=True)
        elif mode == 'enable':
            if self.is_bash():
                self.exit_bash_mode(mode)

            if self.is_cli():
                helpers.log("Switching from cli to %s mode" % mode, level=level)
                super(BsnDevConf, self).cmd('enable', quiet=True, level=level)
            elif self.is_config():
                helpers.log("Switching from config to %s mode" % mode, level=level)
                super(BsnDevConf, self).cmd('exit', quiet=True, level=level)
        elif mode == 'config':
            if self.is_bash():
                self.exit_bash_mode(mode)

            if self.is_cli():
                helpers.log("Switching from cli to %s mode" % mode, level=level)
                super(BsnDevConf, self).cmd('enable', quiet=True, level=level)
                super(BsnDevConf, self).cmd('configure', quiet=True, level=level)
            elif self.is_enable():
                helpers.log("Switching from enable to %s mode" % mode, level=level)
                super(BsnDevConf, self).cmd('configure', quiet=True, level=level)
        elif mode == 'bash':
            if self.is_cli():
                self.mode_before_bash = 'cli'
                helpers.log("Switching from cli to %s mode" % mode, level=level)
            elif self.is_enable():
                self.mode_before_bash = 'enable'
                helpers.log("Switching from enable to %s mode" % mode, level=level)
            elif self.is_config():
                self.mode_before_bash = 'config'
                helpers.log("Switching from config to %s mode" % mode, level=level)
            helpers.log("Mode previous to bash is %s" % self.mode_before_bash, level=level)
            super(BsnDevConf, self).cmd('debug bash', quiet=True, level=level)

        self.mode = mode
        # helpers.log("Current mode is %s" % self.mode, level=level)

        if not quiet:
            helpers.log("Execute command on '%s': '%s'" % (self.name(), cmd), level=level)

        super(BsnDevConf, self).cmd(cmd, prompt=prompt, quiet=True)
        if not quiet:
            helpers.log("%s content on '%s':\n%s%s"
                        % (mode, self.name(), self.content(),
                           br_utils.end_of_output_marker()),
                           level=level)
        return self.result()


    def cli(self, cmd, quiet=False, prompt=False, level=5):
        return self.cmd(cmd, quiet=quiet, mode='cli', prompt=prompt, level=level)

    def enable(self, cmd, quiet=False, prompt=False, level=5):
        return self.cmd(cmd, quiet=quiet, mode='enable', prompt=prompt, level=level)

    def config(self, cmd, quiet=False, prompt=False, level=5):
        return self.cmd(cmd, quiet=quiet, mode='config', prompt=prompt, level=level)

    def bash(self, cmd, quiet=False, prompt=False, level=5):
        return self.cmd(cmd, quiet=quiet, mode='bash', prompt=prompt, level=level)

    def sudo(self, cmd, quiet=False, prompt=False, level=5):
        return self.cmd(' '.join(('sudo', cmd)), quiet=quiet, mode='bash',
                        prompt=prompt, level=level)

    def close(self):
        super(BsnDevConf, self).close()
        # !!! FIXME: Need to close the controller connection


class ControllerDevConf(BsnDevConf):
    def __init__(self, *args, **kwargs):
        super(ControllerDevConf, self).__init__(*args, **kwargs)


class SwitchDevConf(BsnDevConf):
    def __init__(self, *args, **kwargs):
        super(SwitchDevConf, self).__init__(*args, **kwargs)


class MininetDevConf(DevConf):
    """
    :param topology: str, in the form 'tree,4,2'
    """
    def __init__(self, name=None, host=None, user=None, password=None,
                 controller=None, topology=None, openflow_port=None,
                 debug=0):

        if controller is None:
            helpers.environment_failure("Must specify a controller for Mininet.")
        if topology is None:
            helpers.environment_failure("Must specify a topology for Mininet.")

        self.topology = topology
        self.controller = controller
        self.openflow_port = openflow_port
        self.state = 'stopped'  # or 'started'
<<<<<<< HEAD
        
        super(MininetDevConf, self).__init__(host, user, password, name=name,
                                             debug=debug)
=======

        super(MininetDevConf, self).__init__(host, user, password, debug=debug)
>>>>>>> dev
        self.start_mininet()

    def cmd(self, cmd, quiet=False, prompt=False, level=4):
        if not quiet:
            helpers.log("Execute command on '%s': %s"
                        % (self.name(), cmd), level=level)

        super(MininetDevConf, self).cmd(cmd, prompt=prompt, quiet=True)
        if not quiet:
            helpers.log("Content on '%s':\n%s%s"
                        % (self.name(), self.content(),
                           br_utils.end_of_output_marker()),
                           level=level)
        return self.result()

    # Alias
    cli = cmd

    def mininet_cmd(self):
        return ("sudo /usr/local/bin/mn --controller=remote --ip=%s --topo=%s --mac"
                % (self.controller, self.topology))

    def start_mininet(self, new_topology=None):
        if self.state == 'started':
            helpers.log("Mininet is already running. No need to start it.")
            return True

        helpers.log("Starting Mininet on '%s'" % self.name())

        if new_topology:
            self.topology = new_topology
            helpers.log("Start new Mininet topology for '%s': %s"
                        % (self.name(), new_topology))

        _cmd = self.mininet_cmd()

        self.cli(_cmd, quiet=False)
        self.state = 'started'

    def stop_mininet(self):
        if self.state == 'stopped':
            helpers.log("Mininet is not running. No need to stop it.")
            return True

        helpers.log("Stopping Mininet on '%s'" % self.name())
        self.cli("exit", quiet=False)
        self.state = 'stopped'

    def restart_mininet(self, new_topology=None):
        helpers.log("Restarting Mininet topology on '%s'" % self.name())
        self.stop_mininet()
        self.start_mininet(new_topology)

    def close(self):
        super(MininetDevConf, self).close()

        self.stop_mininet()
        self.conn.close(force=True)
        helpers.log("Mininet - force closed the device connection '%s'."
                    % self.name())


class T6MininetDevConf(MininetDevConf):
    """
    :param topology: str, in the form
        '--num-spine 0 --num-rack 1 --num-bare-metal 2 --num-hypervisor 0'
    """
    def __init__(self, **kwargs):
        super(T6MininetDevConf, self).__init__(**kwargs)

    def mininet_cmd(self):
        if self.openflow_port is None:
            self.openflow_port = 6653
            helpers.log("Setting OpenFlow port to %d" % self.openflow_port)
        return ("sudo /opt/t6-mininet/run.sh -c %s:%s %s"
                % (self.controller, self.openflow_port, self.topology))


class HostDevConf(DevConf):
    def __init__(self, name=None, host=None, user=None, password=None,
                 port=None, is_console=False, debug=0):
        super(HostDevConf, self).__init__(host, user, password,
                                          port=port,
                                          is_console=is_console,
                                          name=name,
                                          debug=debug)
        self.bash('uname -a')

    def cmd(self, cmd, quiet=False, prompt=False, level=4):
        if not quiet:
            helpers.log("Execute command on '%s': '%s'"
                        % (self.name(), cmd), level=level)

        super(HostDevConf, self).cmd(cmd, prompt=prompt, quiet=True)
        if not quiet:
            helpers.log("Content on '%s':\n%s%s"
                        % (self.name(), self.content(),
                           br_utils.end_of_output_marker()),
                           level=level)
        return self.result()

    # Alias
    bash = cmd

    def sudo(self, cmd, quiet=False, prompt=False, level=5):
        return self.bash(' '.join(('sudo', cmd)), quiet=quiet, prompt=prompt,
                         level=level)

    def close(self):
        super(HostDevConf, self).close()
        # !!! FIXME: Need to close the controller connection
