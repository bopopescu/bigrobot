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
                 console_info=None,
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
        self._console_info = console_info
        self._debug = debug
        self._platform = None
        self.conn = None
        self.last_result = None
        self._mode = 'cli'
        self.is_prompt_changed = False

        self._timeout = timeout if timeout else 30

        self.connect()

        helpers.debug("Setting expect timeout to %s seconds" % self._timeout)
        self.conn.set_timeout(self._timeout)

        driver = self.conn.get_driver()
        helpers.log("Using devconf driver '%s' (name: '%s')"
                    % (driver, driver.name))

        # Devconf autoinit which will invoke driver's init_terminal()
        self.conn.autoinit()

        # Aliases
        self.set_prompt = self.conn.set_prompt
        self.get_prompt = self.conn.get_prompt

    def mode(self, new_mode=None):
        if new_mode:
            self._mode = new_mode
        return self._mode

    def connect(self):
        try:
            if self._protocol == 'telnet' or self._protocol == 'ssh':
                auth_info = "(login:%s, password:%s)" % (self._user,
                                                         self._password)
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

                if self._console_info:
                    if self._console_info['type'] == 'telnet':
                        helpers.log("Connecting to console via telnet")
                    elif self._console_info['type'] == 'libvirt':
                        helpers.log("Connecting to console via ssh (libvirt console)")
                        conn.login(account)
                    else:
                        helpers.environment_failure("Unsupported console type")

                    # Note: User needs to figure out what state the console is in
                    #       and manage it themself.
                else:
                    conn.login(account)

            else:
                helpers.environment_failure("Supported protocols are 'telnet' and 'ssh'")
        except LoginFailure:
            helpers.warn("Login failure: Check the user name and password"
                         " for device %s (user:%s, password:%s). Also try"
                         " to log in manually to see what the error is."
                         % (self._host, self._user, self._password))
            self.expect_exception(None, "Login failure", soft_error=True)
            raise
        except TimeoutException:
            helpers.warn("Login failure: Timed out during '%s' connect"
                         " to device %s. Try to log in manually to see"
                         " what the error is." % (self._protocol, self._host))
            self.expect_exception(None, "Login timed out")
        except:
            if hasattr(self.conn, 'buffer'):
                self.expect_exception(None, "Unexpected '%s' login exception"
                                      % self._protocol, soft_error=True)
            else:
                helpers.warn("Unexpected SSH login exception in %s"
                             % (sys.exc_info()[0]))
            raise

        # Reset mode to 'cli' as default
        self._mode = 'cli'
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

    def send(self, cmd, no_cr=False, quiet=False, level=4):
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
        if no_cr is False:
            cmd = ''.join((cmd, '\r'))
        self.conn.send(cmd)

    def prompt_str(self, prompt):
        prompt_str_list = []
        if helpers.is_list(prompt):
            for p in prompt:
                if hasattr(p, 'match'):
                    prompt_str_list.append(p.pattern)
                else:
                    prompt_str_list.append(p)
        else:
            p = prompt
            if hasattr(p, 'match'):
                prompt_str_list.append(p.pattern)
            else:
                prompt_str_list.append(p)
        return prompt_str_list

    def expect_exception(self, prompt=None, descr="No description",
                         soft_error=False):
        _buffer = None
        if self.conn:
            _buffer = '\n' + self.conn.buffer.__str__()
        msg = ("\n"
               "==== Expect error (Start) ====\n"
               "Error descr  : %s\n"
               "Expect prompt: %s\n"
               "Expect buffer: %s\n"
               "==== Expect error (End) ===="
               % (descr, self.prompt_str(prompt), _buffer))
        helpers.log(msg)
        helpers.test_error("Devconf expect exception", soft_error)

    def expect(self, prompt=None, timeout=None, quiet=False, level=4):
        """
        Invoking low-level send/expect commands to the device. This is a
        wrapper for Exscript's expect(). Use with caution!!!

        This function will wait until there a prompt match or times out in
        the process. It is intended to be used with send().

        See http://knipknap.github.io/exscript/api/Exscript.protocols.Protocol-class.html#expect
        """
        if prompt is None:
            helpers.debug("Reset prompt to default")
            self.conn.set_prompt()
            prompt = self.conn.get_prompt()
        else:
            prompt = helpers.list_flatten(prompt)

        if timeout: self.timeout(timeout)
        if not quiet:
            helpers.log("Expecting prompt: %s" % self.prompt_str(prompt),
                        level=level)

        try:
            ret_val = self.conn.expect(prompt)
            self.last_result = {'content': self.conn.response}
            if not quiet:
                helpers.log("Expect content:\n%s%s"
                            % (self.content(), br_utils.end_of_output_marker()),
                            level=level)
        except TimeoutException:
            self.expect_exception(prompt,
                                  "Timed out while expecting the prompt")
        except:
            self.expect_exception(prompt, "Unexpected except exception",
                                  soft_error=True)
            raise
        if timeout: self.timeout()

        helpers.log("Expect prompt matched (%s, '%s')"
                    % (ret_val[0], helpers.re_match_str(ret_val[1])))
        return ret_val

    def waitfor(self, prompt, timeout=None, quiet=False, level=4):
        """
        Invoking low-level send/expect commands to the device. This is a
        wrapper for Exscript's waitfor(). Use with caution!!!

        This function will wait until there a prompt match or times out in
        the process. It is intended to be used with send().

        See http://knipknap.github.io/exscript/api/Exscript.protocols.Protocol-class.html#waitfor
        """
        if prompt is None:
            # User might have changed the prompt. So be sure to set it back
            # to default prompt first.
            self.conn.set_prompt()

            # Now get default prompt.
            prompt = self.conn.get_prompt()
        else:
            prompt = helpers.list_flatten(prompt)

        if timeout: self.timeout(timeout)
        if not quiet:
            helpers.log("Expecting waitfor prompt: %s"
                        % self.prompt_str(prompt), level=level)

        try:
            ret_val = self.conn.waitfor(prompt)

            self.last_result = { 'content': self.conn.response }
            if not quiet:
                helpers.log("Waitfor (expect) content:\n%s%s"
                            % (self.content(), br_utils.end_of_output_marker()),
                            level=level)
        except TimeoutException:
            self.expect_exception(prompt, "Timed out during waitfor",
                                  soft_error=True)
            raise
        except:
            self.expect_exception(prompt, "Unexpected waitfor exception",
                                  soft_error=True)
            raise
        if timeout: self.timeout()

        helpers.log("Expect prompt matched (%s, '%s')"
                    % (ret_val[0], helpers.re_match_str(ret_val[1])))
        return ret_val


    def cmd(self, cmd, quiet=False, mode=None, prompt=None,
            timeout=None, level=5):
        if timeout: self.timeout(timeout)
        if prompt:
            prompt = helpers.list_flatten(prompt)
            helpers.log("Expected prompt: %s" % self.prompt_str(prompt))
            self.conn.set_prompt(prompt)
            self.is_prompt_changed = True
        else:
            if self.is_prompt_changed:
                helpers.log("Resetting expect prompt to default")
                self.conn.set_prompt()

        if not quiet:
            helpers.log("Execute command: '%s' (timeout: %s)"
                        % (cmd, timeout), level=level)

        prefix_str = '%s %s' % (self.name(), mode)
        helpers.bigrobot_devcmd_write("%-9s: %s\n" % (prefix_str, cmd))

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
                 port=None, console_info=None,
                 timeout=None, protocol='ssh', debug=0):
        super(BsnDevConf, self).__init__(host, user, password,
                                         port=port,
                                         console_info=console_info,
                                         name=name,
                                         timeout=timeout,
                                         protocol=protocol,
                                         debug=debug)
        self._mode_before_bash = None

    def is_cli(self):
        return self.mode() == 'cli'

    def is_enable(self):
        return self.mode() == 'enable'

    def is_config(self):
        return self.mode() == 'config'

    def is_bash(self):
        return self.mode() == 'bash'

    def exit_bash_mode(self, new_mode):
        self.mode(self._mode_before_bash)
        helpers.log("Switching from bash to %s mode" % new_mode, level=5)
        super(BsnDevConf, self).cmd('exit', mode='bash', quiet=True)
        helpers.log("Current mode is %s" % self.mode())

    def _cmd(self, cmd, quiet=False, mode='cmd', prompt=None,
             timeout=None, level=5):

        if helpers.is_extreme(self.platform()):
            if mode != 'config':
                helpers.test_error("For Extreme Networks switch, only config mode is supported")
        # Check to make sure we're in the right mode prior to executing command
        elif mode == 'cli':
            if self.is_bash():
                self.exit_bash_mode(mode)

            if self.is_enable():
                # In Arista, you cannot go back to CLI mode once you enter
                # enable/config mode. Exiting from enable mode will put you
                # in bash mode or log you out.
                if helpers.is_arista(self.platform()):
                    helpers.test_error("For Arista, you cannot switch from"
                                       " enable back to %s mode" % mode)
                helpers.log("Switching from enable to %s mode" % mode,
                            level=level)
                super(BsnDevConf, self).cmd('exit', mode=mode,
                                            quiet=True, level=level)
            elif self.is_config():
                if helpers.is_arista(self.platform()):
                    helpers.test_error("For Arista, you cannot switch from"
                                       " enable back to %s mode" % mode)
                helpers.log("Switching from config to %s mode" % mode,
                            level=level)
                super(BsnDevConf, self).cmd('end', mode=mode, quiet=True)
                super(BsnDevConf, self).cmd('exit', mode=mode, quiet=True)
        elif mode == 'enable':
            if self.is_bash():
                self.exit_bash_mode(mode)

            if self.is_cli():
                helpers.log("Switching from cli to %s mode" % mode,
                            level=level)
                super(BsnDevConf, self).cmd('enable', mode=mode,
                                            quiet=True, level=level)
            elif self.is_config():
                helpers.log("Switching from config to %s mode" % mode,
                            level=level)
                super(BsnDevConf, self).cmd('end', mode=mode,
                                            quiet=True, level=level)
        elif mode == 'config':
            if self.is_bash():
                self.exit_bash_mode(mode)

            if self.is_cli():
                helpers.log("Switching from cli to %s mode" % mode,
                            level=level)
                super(BsnDevConf, self).cmd('enable', mode=mode,
                                            quiet=True, level=level)
                super(BsnDevConf, self).cmd('configure', mode=mode,
                                            quiet=True, level=level)
            elif self.is_enable():
                helpers.log("Switching from enable to %s mode" % mode,
                            level=level)
                super(BsnDevConf, self).cmd('configure', mode=mode,
                                            quiet=True, level=level)
        elif mode == 'bash':
            if self.is_cli() or self.is_enable() or self.is_config():
                if self.is_cli():
                    self._mode_before_bash = 'cli'
                    helpers.log("Switching from cli to %s mode" % mode,
                                level=level)
                elif self.is_enable():
                    self._mode_before_bash = 'enable'
                    helpers.log("Switching from enable to %s mode" % mode,
                                level=level)
                elif self.is_config():
                    self._mode_before_bash = 'config'
                    helpers.log("Switching from config to %s mode" % mode,
                                level=level)

                if helpers.is_arista(self.platform()):
                    bash_cmd = "bash"
                else:
                    # Supports BSN controllers, BSN SwitchLight
                    bash_cmd = "debug bash"
                super(BsnDevConf, self).cmd(bash_cmd,
                                            mode=self._mode_before_bash,
                                            quiet=True, level=level)

        self.mode(mode)
        # helpers.log("Current mode is %s" % self.mode(), level=level)

        if not quiet:
            helpers.log("Execute command on '%s': '%s' (timeout: %s)"
                        % (self.name(), cmd, timeout), level=level)

        super(BsnDevConf, self).cmd(cmd, prompt=prompt, mode=mode,
                                    timeout=timeout, quiet=True)

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
                self.expect_exception(None, "Unexpected socket error",
                                      soft_error=True)
                raise
        except:
            self.expect_exception(None, "Unexpected error", soft_error=True)
            raise
        return result

    def cli(self, cmd, quiet=False, prompt=False, timeout=None, level=5):
        return self.cmd(cmd, quiet=quiet, mode='cli', prompt=prompt,
                        timeout=timeout, level=level)

    def enable(self, cmd, quiet=False, prompt=False, timeout=None, level=5):
        return self.cmd(cmd, quiet=quiet, mode='enable', prompt=prompt,
                        timeout=timeout, level=level)

    def config(self, cmd, quiet=False, prompt=False, timeout=None, level=5):
        return self.cmd(cmd, quiet=quiet, mode='config', prompt=prompt,
                        timeout=timeout, level=level)

    def bash(self, cmd, quiet=False, prompt=False, timeout=None, level=5):
        return self.cmd(cmd, quiet=quiet, mode='bash', prompt=prompt,
                        timeout=timeout, level=level)

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
                helpers.test_error("Attribute '%s' is not found in switch info"
                                   % key)
            return self._info[key]
        return self._info

    def bash(self, *args, **kwargs):
        if helpers.is_switchlight(self.platform()):
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
                 controller=None, controller2=None, port=None, topology=None,
                 openflow_port=None, timeout=None, protocol='ssh',
                 debug=0, is_start_mininet=True):

        if controller is None:
            helpers.environment_failure("Must specify a controller for Mininet.")
        if topology is None:
            helpers.environment_failure("Must specify a topology for Mininet.")

        self._mode_before_bash = None
        self.topology = topology
        self.controller = controller
        self.controller2 = controller2
        self.openflow_port = openflow_port
        self.state = 'stopped'  # or 'started'
        super(MininetDevConf, self).__init__(host, user, password, name=name,
                                             timeout=timeout,
                                             port=port,
                                             protocol=protocol,
                                             debug=debug)
        if not is_start_mininet:
            helpers.log("Not starting Mininet session (is_start_mininet=%s)"
                        % is_start_mininet)
        else:
            self.start_mininet()

    def is_cli(self):
        return self.mode() == 'cli'

    def is_bash(self):
        return self.mode() == 'bash'

    def exit_bash_mode(self, new_mode):
        self.mode(self._mode_before_bash)
        helpers.log("Switching from bash to %s mode" % new_mode, level=5)
        super(MininetDevConf, self).cmd('exit', mode='bash', quiet=True)
        helpers.log("Current mode is %s" % self.mode())

    def _cmd(self, cmd, quiet=False, mode='cli', prompt=False, timeout=None,
             level=4):

        if mode == 'cli':
            if self.is_bash():
                self.exit_bash_mode(mode)
        elif mode == 'bash':
            if self.is_cli():
                self._mode_before_bash = 'cli'
                helpers.log("Switching from cli to %s mode" % mode,
                            level=level)
                super(MininetDevConf, self).cmd("sh bash",
                                                mode=self._mode_before_bash,
                                                quiet=True, level=level)
        else:
            helpers.environment_failure("Mode '%s' is not supported for Mininet"
                                        % mode)

        self.mode(mode)

        if not quiet:
            helpers.log("Execute command on '%s': %s (timeout: %s)"
                        % (self.name(), cmd, timeout), level=level)

        super(MininetDevConf, self).cmd(cmd, prompt=prompt, mode=mode,
                                        timeout=timeout, quiet=True)
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
                self.expect_exception(None, "Unexpected socket error",
                                      soft_error=True)
                raise
        except:
            self.expect_exception(None, "Unexpected error", soft_error=True)
            raise
        return result

    def cli(self, cmd, quiet=False, prompt=False, timeout=None, level=5):
        return self.cmd(cmd, quiet=quiet, mode='cli', prompt=prompt,
                        timeout=timeout, level=level)

    def bash(self, cmd, quiet=False, prompt=False, timeout=None, level=5):
        return self.cmd(cmd, quiet=quiet, mode='bash', prompt=prompt,
                        timeout=timeout, level=level)

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

    def restart_mininet(self, new_topology=None, sleep=5):
        helpers.log("Restarting Mininet topology on '%s'" % self.name())
        self.stop_mininet()
        helpers.sleep(sleep)
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
    def __init__(self, *args, **kwargs):
        super(HostDevConf, self).__init__(*args, **kwargs)
        self.bash('uname -a')

    def _cmd(self, cmd, quiet=False, prompt=False, timeout=None, level=4):
        if not quiet:
            helpers.log("Execute command on '%s': '%s' (timeout: %s)"
                        % (self.name(), cmd, timeout), level=level)

        super(HostDevConf, self).cmd(cmd, prompt=prompt, mode='bash',
                                     timeout=timeout, quiet=True)
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
                self.expect_exception(None, "Unexpected socket error",
                                      soft_error=True)
                raise
        except:
            self.expect_exception(None, "Unexpected error", soft_error=True)
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
