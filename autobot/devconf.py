from Exscript import Account
from Exscript.protocols import SSH2, Telnet
from Exscript.protocols.Exception import LoginFailure, TimeoutException
import autobot.helpers as helpers
import autobot.utils as br_utils
import sys
import socket
import re


class DevConf(object):
    def __init__(self, host=None, user=None, password=None,
                 port=None,
                 is_console=False,
                 console_driver=None,
                 name=None,
                 timeout=None,
                 protocol='ssh',
                 debug=0):
        if host is None:
            helpers.environment_failure("Must specify a host.")
        if user is None:
            helpers.environment_failure("Must specify a user name.")
        if password is None:
            helpers.environment_failure("Must specify a password.")

        self._name = name
        self._host = host
        self._user = user
        self._password = password
        self._port = port
        self._protocol = protocol
        self._is_console = is_console
        self._console_driver = console_driver
        self._debug = debug
        self._platform = None
        self.conn = None
        self.last_result = None
        self.mode = 'cli'
        self.is_prompt_changed = False

        self._timeout = timeout if timeout else 30

        self.connect()

        helpers.debug("Setting timeout to %s seconds" % self._timeout)
        self.conn.set_timeout(self._timeout)

        driver = self.conn.get_driver()
        helpers.log("Using devconf driver '%s' (name: '%s')"
                    % (driver, driver.name))

        # Aliases
        self.set_prompt = self.conn.set_prompt

    def connect(self):
        try:
            if self._is_console:
                # Console connection only supports telnet. So ignore protocol
                # field (if specified).
                helpers.log("Telnet to console on host %s, port %s (user:%s)"
                            % (self._host, self._port, self._user))
                conn = Telnet(debug=self._debug)
                conn.connect(self._host, self._port)

                if self._console_driver:
                    helpers.log("Setting devconf driver for console to '%s'"
                                % self._console_driver)
                    conn.set_driver(self._console_driver)

                # Note: User needs to figure out what state the console is in
                #       and manage it themself.

            elif self._protocol == 'telnet' or self._protocol == 'ssh':
                auth_info = "(login:%s, password:%s)" % (self._user, self._password)
                account = Account(self._user, self._password)

                if self._protocol == 'telnet':
                    helpers.log("Telnet to host %s, port %s (user:%s)"
                                % (self._host, self._port, self._user))
                    conn = Telnet(debug=self._debug)
                elif self._protocol == 'ssh':
                    helpers.log("SSH connect to host %s, port %s %s"
                                    % (self._host, self._port, auth_info))
                    conn = SSH2(debug=self._debug)

                conn.connect(self._host, self._port)
                conn.login(account)

            else:
                helpers.environment_failure("Supported protocols are 'telnet' and 'ssh'")
        except LoginFailure:
            helpers.environment_failure("Login failure: Check the user name and password"
                                        " for device %s (user:%s, password:%s). Also try"
                                        " to log in manually to see what the error is."
                                        % (self._host, self._user, self._password))
            # helpers.log("Exception in %s" % sys.exc_info()[0])
            # raise
        except TimeoutException:
            helpers.environment_failure("Login failure: Timed out during SSH connnect"
                                        " to device %s. Try to log in manually to see"
                                        " what the error is." % self._host)
            # helpers.log("Exception in %s" % sys.exc_info()[0])
            # raise
        except:
            helpers.log("Unexpected SSH login exception in %s\n"
                        "Expect buffer:\n%s%s"
                        % (sys.exc_info()[0],
                           self.conn.buffer.__str__(),
                           br_utils.end_of_output_marker()))
            raise

        # Reset mode to 'cli' as default
        self.mode = 'cli'
        self.conn = conn


    def timeout(self, seconds=None):
        """
        Set the expect timeout to 'seconds'. If not specified, reset to
        default timeout value.
        """
        if seconds:
            helpers.debug("Setting timeout to %s seconds" % seconds, level=3)
        else:
            # helpers.debug("Setting timeout to default (%s seconds)"
            #              % self._timeout, level=3)
            seconds = self._timeout

        self.conn.set_timeout(seconds)

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

    def expect(self, prompt, timeout=None, quiet=False, level=4):
        """
        Invoking low-level send/expect commands to the device. This is a
        wrapper for Exscript's expect(). Use with caution!!!

        This function will wait until there a prompt match or times out in
        the process. It is intended to be used with send().

        See http://knipknap.github.io/exscript/api/Exscript.protocols.Protocol-class.html#expect
        """
        if timeout: self.timeout(timeout)
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
            helpers.environment_failure("Expect failure: Timed out during expect prompt '%s'\n"
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
        if timeout: self.timeout()

        return ret_val

    def waitfor(self, prompt, timeout=None, quiet=False, level=4):
        """
        Invoking low-level send/expect commands to the device. This is a
        wrapper for Exscript's waitfor(). Use with caution!!!

        This function will wait until there a prompt match or times out in
        the process. It is intended to be used with send().

        See http://knipknap.github.io/exscript/api/Exscript.protocols.Protocol-class.html#waitfor
        """
        if timeout: self.timeout(timeout)
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
        if timeout: self.timeout()

    def cmd(self, cmd, quiet=False, mode=None, prompt=None, timeout=None, level=5):
        if timeout: self.timeout(timeout)
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

        if timeout: self.timeout()

        return self.result()

    # Alias
    cli = cmd

    def driver(self):
        return self.conn.get_driver()

    def platform(self):
        if self._platform:
            return self._platform

        driver = self.driver()
        if hasattr(driver, 'platform'):
            # Does the driver class have the method platform() defined?
            # See src/Exscript/protocols/drivers/bsn_controller.py as an
            # example.
            #
            # CAUTION: platform() implementation in the Exscript code is a
            # hack to help BigRobot determine the platform of the node.
            # Exscript maintains only one copy of the object (in a lookup
            # table?) so the _platform in platform() is overwritten everytime
            # a new node is instantiated. So we cache the platform info here
            # in devconf (self._platform).
            self._platform = driver.platform()
        else:
            self._platform = "__undefined__"

        return self._platform

    def result(self):
        return self.last_result

    def content(self):
        return self.result()['content']

    def close(self):
        helpers.log("Closing device %s" % self._host)


class BsnDevConf(DevConf):
    def __init__(self, name=None, host=None, user=None, password=None,
                 port=None, is_console=False, console_driver=None,
                 timeout=None, protocol='ssh', debug=0):
        super(BsnDevConf, self).__init__(host, user, password,
                                         port=port,
                                         is_console=is_console,
                                         console_driver=console_driver,
                                         name=name,
                                         timeout=timeout,
                                         protocol=protocol,
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

    def _cmd(self, cmd, quiet=False, mode='cmd', prompt=None, timeout=None, level=5):

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
                super(BsnDevConf, self).cmd('debug bash', quiet=True, level=level)
            elif self.is_enable():
                self.mode_before_bash = 'enable'
                helpers.log("Switching from enable to %s mode" % mode, level=level)
                super(BsnDevConf, self).cmd('debug bash', quiet=True, level=level)
            elif self.is_config():
                self.mode_before_bash = 'config'
                helpers.log("Switching from config to %s mode" % mode, level=level)
                super(BsnDevConf, self).cmd('debug bash', quiet=True, level=level)

        self.mode = mode
        # helpers.log("Current mode is %s" % self.mode, level=level)

        if not quiet:
            helpers.log("Execute command on '%s': '%s'" % (self.name(), cmd), level=level)

        super(BsnDevConf, self).cmd(cmd, prompt=prompt, timeout=timeout, quiet=True)

        if not quiet:
            helpers.log("%s content on '%s':\n%s%s"
                        % (mode, self.name(), self.content(),
                           br_utils.end_of_output_marker()),
                           level=level)
        return self.result()

    def cmd(self, *args, **kwargs):
        try:
            result = self._cmd(*args, **kwargs)
        except socket.error, e:
            error_str = str(e)
            helpers.log("socket.error: e: %s" % error_str)
            if re.match(r'Socket is closed', error_str):
                helpers.log("Socket is closed. Reconnecting...")
                self.connect()
                result = self._cmd(*args, **kwargs)
            else:
                helpers.log("Unexpected socket error: %s" % sys.exc_info()[0])
                raise
        except:
            helpers.log("Unexpected error: %s" % sys.exc_info()[0])
            raise
        return result

    def cli(self, cmd, quiet=False, prompt=False, timeout=None, level=5):
        return self.cmd(cmd, quiet=quiet, mode='cli', prompt=prompt, timeout=timeout, level=level)

    def enable(self, cmd, quiet=False, prompt=False, timeout=None, level=5):
        return self.cmd(cmd, quiet=quiet, mode='enable', prompt=prompt, timeout=timeout, level=level)

    def config(self, cmd, quiet=False, prompt=False, timeout=None, level=5):
        return self.cmd(cmd, quiet=quiet, mode='config', prompt=prompt, timeout=timeout, level=level)

    def bash(self, cmd, quiet=False, prompt=False, timeout=None, level=5):
        return self.cmd(cmd, quiet=quiet, mode='bash', prompt=prompt, timeout=timeout, level=level)

    def sudo(self, cmd, quiet=False, prompt=False, timeout=None, level=5):
        return self.cmd(' '.join(('sudo', cmd)), quiet=quiet, mode='bash',
                        prompt=prompt, timeout=timeout, level=level)

    def close(self):
        super(BsnDevConf, self).close()
        # !!! FIXME: Need to close the controller connection


class ControllerDevConf(BsnDevConf):
    def __init__(self, *args, **kwargs):
        super(ControllerDevConf, self).__init__(*args, **kwargs)


class SwitchDevConf(BsnDevConf):
    def __init__(self, *args, **kwargs):
        super(SwitchDevConf, self).__init__(*args, **kwargs)
        self._info = None

    def info(self, key=None, refresh=False):
        if refresh or not self._info:
            out = self.cli('show version')['content']
            # Remove first line, which contains 'show version'
            out = helpers.text_processing_str_remove_header(out, 1)
            # Remove line starting with 'Uptime is xxxxxx' to the end of string
            out = helpers.text_processing_str_remove_to_end(out,
                                                            line_marker=r'^Uptime is')
            out_dict = helpers.from_yaml(out)
            self._info = helpers.snake_case_key(out_dict)
            helpers.log("Switch info:\n%s" % helpers.prettify(self._info))
        if key:
            if key not in self._info:
                helpers.test_error("Attribute '%s' is not found in switch info" % key)
            return self._info[key]
        return self._info

    def bash(self, *args, **kwargs):
        # For SwitchLight, you need to enter Enable mode to execute
        # 'debug bash'.
        self.enable('')
        super(SwitchDevConf, self).bash(*args, **kwargs)
        return self.result()


class MininetDevConf(DevConf):
    """
    :param topology: str, in the form 'tree,4,2'
    """
    def __init__(self, name=None, host=None, user=None, password=None,
                 controller=None, controller2=None, topology=None,
                 openflow_port=None, timeout=None, protocol='ssh',
                 debug=0):

        if controller is None:
            helpers.environment_failure("Must specify a controller for Mininet.")
        if topology is None:
            helpers.environment_failure("Must specify a topology for Mininet.")

        self.topology = topology
        self.controller = controller
        self.controller2 = controller2
        self.openflow_port = openflow_port
        self.state = 'stopped'  # or 'started'
        super(MininetDevConf, self).__init__(host, user, password, name=name,
                                             timeout=timeout,
                                             protocol=protocol,
                                             debug=debug)
        self.start_mininet()

    def _cmd(self, cmd, quiet=False, prompt=False, timeout=None, level=4):
        if not quiet:
            helpers.log("Execute command on '%s': %s"
                        % (self.name(), cmd), level=level)

        super(MininetDevConf, self).cmd(cmd, prompt=prompt, timeout=timeout, quiet=True)
        if not quiet:
            helpers.log("Content on '%s':\n%s%s"
                        % (self.name(), self.content(),
                           br_utils.end_of_output_marker()),
                           level=level)
        return self.result()

    def cmd(self, *args, **kwargs):
        try:
            result = self._cmd(*args, **kwargs)
        except socket.error, e:
            error_str = str(e)
            helpers.log("socket.error: e: %s" % error_str)
            if re.match(r'Socket is closed', error_str):
                helpers.log("Socket is closed. Reconnecting...")
                self.connect()
                result = self._cmd(*args, **kwargs)
            else:
                helpers.log("Unexpected socket error: %s" % sys.exc_info()[0])
                raise
        except:
            helpers.log("Unexpected error: %s" % sys.exc_info()[0])
            raise
        return result

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

        if self.controller2:
            # Start Mininet with dual controllers
            return ("sudo /opt/t6-mininet/run.sh -c %s:%s -c %s:%s %s"
                    % (self.controller, self.openflow_port,
                       self.controller2, self.openflow_port,
                       self.topology))
        else:
            return ("sudo /opt/t6-mininet/run.sh -c %s:%s %s"
                    % (self.controller, self.openflow_port, self.topology))


class HostDevConf(DevConf):
    def __init__(self, name=None, host=None, user=None, password=None,
                 port=None, is_console=False, timeout=None, protocol='ssh',
                 debug=0):
        super(HostDevConf, self).__init__(host, user, password,
                                          port=port,
                                          is_console=is_console,
                                          name=name,
                                          timeout=timeout,
                                          protocol=protocol,
                                          debug=debug)
        self.bash('uname -a')

    def _cmd(self, cmd, quiet=False, prompt=False, timeout=None, level=4):
        if not quiet:
            helpers.log("Execute command on '%s': '%s'"
                        % (self.name(), cmd), level=level)

        super(HostDevConf, self).cmd(cmd, prompt=prompt, timeout=None, quiet=True)
        if not quiet:
            helpers.log("Content on '%s':\n%s%s"
                        % (self.name(), self.content(),
                           br_utils.end_of_output_marker()),
                           level=level)
        return self.result()

    def cmd(self, *args, **kwargs):
        try:
            result = self._cmd(*args, **kwargs)
        except socket.error, e:
            error_str = str(e)
            helpers.log("socket.error: e: %s" % error_str)
            if re.match(r'Socket is closed', error_str):
                helpers.log("Socket is closed. Reconnecting...")
                self.connect()
                result = self._cmd(*args, **kwargs)
            else:
                helpers.log("Unexpected socket error: %s" % sys.exc_info()[0])
                raise
        except:
            helpers.log("Unexpected error: %s" % sys.exc_info()[0])
            raise
        return result

    # Alias
    bash = cmd

    def sudo(self, cmd, quiet=False, prompt=False, level=5):
        return self.bash(' '.join(('sudo', cmd)), quiet=quiet, prompt=prompt,
                         level=level)

    def close(self):
        super(HostDevConf, self).close()
        # !!! FIXME: Need to close the controller connection
