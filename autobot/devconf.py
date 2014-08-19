from Exscript import Account
from Exscript.protocols import SSH2, Telnet
from Exscript.protocols.Exception import LoginFailure, TimeoutException
import autobot.helpers as helpers
import autobot.utils as br_utils
import autobot.monitor as monitor
import sys
import socket
import re


class DevConf(object):
    """
    Quiet levels:
      0 - display everything (default)
      1 - suppress command output
      2 - suppress command
      3 - reserved
      4 - reserved
      5 - suppress all output
    """
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
        self._lock = False

        self._logpath = helpers.bigrobot_log_path_exec_instance()
        if not self._logpath:
            self._logpath = '/tmp'
        self._logfile = ('%s/devconf_conversation.%s.log'
                         % (self._logpath, self._name))
        helpers.file_write_append_once(self._logfile,
                                       "\n\n--------- %s Devconf '%s'\n\n"
                                       % (helpers.ts_long_local(), self._name))

        self._timeout = timeout if timeout else 30  # default timeout

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
                    conn = Telnet(debug=self._debug, logfile=self._logfile)
                elif self._protocol == 'ssh':
                    helpers.log("SSH connect to host %s, port %s %s"
                                    % (self._host, self._port, auth_info))
                    conn = SSH2(debug=self._debug, logfile=self._logfile)

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
                helpers.log("Devconf conversation for '%s' logged to %s"
                            % (self._name, self._logfile))

            else:
                helpers.environment_failure("Supported protocols are 'telnet' and 'ssh'")
        except LoginFailure:
            helpers.warn("Login failure: Check the user name and password"
                         " for device %s (user:%s, password:%s). Try to log"
                         " to log in manually to see what the error is."
                         % (self._host, self._user, self._password))
            self.expect_exception(None, "Login failure", soft_error=True)
            raise
        except TimeoutException:
            helpers.warn("Login failure: Timed out during '%s' connect"
                         " to device %s (user:%s, password:%s). Try to log"
                         " in manually to see what the error is."
                         % (self._protocol, self._host,
                            self._user, self._password))
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

    def default_timeout(self):
        return self._timeout

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
        return seconds

    def name(self):
        return self._name

    def is_locked(self):
        """
        DevConf _simple_ lock mechanism - in the multithreading case, it
        checks if there's a command execution in progress.
        """
        if self._lock:
            print("!!!!!!! DEVCONF_LOCK: %s is locked" % self.name())
        return self._lock

    def set_lock(self):
        self._lock = True
        # print("!!!!!!! DEVCONF_LOCK: %s set lock" % self.name())
        return self._lock

    def clear_lock(self):
        self._lock = False
        # print("!!!!!!! DEVCONF_LOCK: %s clear lock" % self.name())
        return self._lock

    def send(self, cmd, no_cr=False, quiet=0, level=4):
        """
        Invoking low-level send/expect commands to the device. This is a
        wrapper for Exscript's send(). Use with caution!!!

        This will simply send the command to the device and immediately
        returns. It is intended to be used with expect(). Note that a
        carriage returned is appended to the command.

        See http://knipknap.github.io/exscript/api/Exscript.protocols.Protocol-class.html#send
        """
        if self.is_locked():
            helpers.sleep(3)
        self.set_lock()
        if helpers.not_matched(quiet, [2, 5]):
            helpers.log("Send command: '%s'" % cmd, level=level)
        if no_cr is False:
            cmd = ''.join((cmd, '\r'))

        prefix_str = '%s %s' % (self.name(), 'send')
        helpers.bigrobot_devcmd_write("%-9s: %s\n" % (prefix_str, cmd))

        self.conn.send(cmd)
        self.clear_lock()

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
               "Exception type     : %s\n"
               "Exception value    : %s\n"
               "Exception traceback:\n%s\n"
               "Error descr        : %s\n"
               "Expect prompt      : %s\n"
               "Expect buffer      : %s\n"
               "==== Expect error (End) ===="
               % (helpers.exception_info_type(),
                  helpers.exception_info_value(),
                  helpers.indent_str(helpers.exception_info_traceback()),
                  descr, self.prompt_str(prompt), _buffer))
        helpers.log(msg)
        self.clear_lock()
        helpers.test_error("Devconf expect exception", soft_error)

    def expect(self, prompt=None, timeout=None, quiet=0, level=4):
        """
        Invoking low-level send/expect commands to the device. This is a
        wrapper for Exscript's expect(). Use with caution!!!

        This function will wait until there a prompt match or times out in
        the process. It is intended to be used with send().

        See http://knipknap.github.io/exscript/api/Exscript.protocols.Protocol-class.html#expect
        """
        if self.is_locked():
            helpers.sleep(3)
        self.set_lock()

        if prompt is None:
            helpers.debug("Reset prompt to default")
            self.conn.set_prompt()
            prompt = self.conn.get_prompt()
        else:
            prompt = helpers.list_flatten(prompt)

        if timeout: self.timeout(timeout)
        if helpers.not_matched(quiet, [2, 5]):
            helpers.log("Expecting prompt: %s" % self.prompt_str(prompt),
                        level=level)

        try:
            ret_val = self.conn.expect(prompt)
            self.last_result = {'content': self.conn.response}
            if helpers.not_matched(quiet, [1, 5]):
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

        if helpers.not_matched(quiet, [1, 5]):
            helpers.log("Expect prompt matched (%s, '%s')"
                        % (ret_val[0], helpers.re_match_str(ret_val[1])))

        self.clear_lock()
        return ret_val

    def waitfor(self, prompt, timeout=None, quiet=0, level=4):
        """
        Invoking low-level send/expect commands to the device. This is a
        wrapper for Exscript's waitfor(). Use with caution!!!

        This function will wait until there a prompt match or times out in
        the process. It is intended to be used with send().

        See http://knipknap.github.io/exscript/api/Exscript.protocols.Protocol-class.html#waitfor
        """
        if self.is_locked():
            helpers.sleep(3)
        self.set_lock()

        if prompt is None:
            # User might have changed the prompt. So be sure to set it back
            # to default prompt first.
            self.conn.set_prompt()

            # Now get default prompt.
            prompt = self.conn.get_prompt()
        else:
            prompt = helpers.list_flatten(prompt)

        if timeout: self.timeout(timeout)
        if helpers.not_matched(quiet, [2, 5]):
            helpers.log("Expecting waitfor prompt: %s"
                        % self.prompt_str(prompt), level=level)

        try:
            ret_val = self.conn.waitfor(prompt)

            self.last_result = { 'content': self.conn.response }
            if helpers.not_matched(quiet, [2, 5]):
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

        if helpers.not_matched(quiet, [1, 5]):
            helpers.log("Expect prompt matched (%s, '%s')"
                        % (ret_val[0], helpers.re_match_str(ret_val[1])))

        self.clear_lock()
        return ret_val


    def cmd(self, cmd, quiet=0, mode=None, prompt=None,
            timeout=None, level=5):
        if self.is_locked():
            helpers.sleep(3)
        self.set_lock()

        if timeout:
            self.timeout(timeout)
        else:
            timeout = self.timeout()

        if prompt:
            prompt = helpers.list_flatten(prompt)
            helpers.log("Expected prompt: %s" % self.prompt_str(prompt))
            self.conn.set_prompt(prompt)
            self.is_prompt_changed = True
        else:
            if self.is_prompt_changed:
                helpers.log("Resetting expect prompt to default")
                self.conn.set_prompt()

        if helpers.not_matched(quiet, [2, 5]):
            helpers.log("Execute command: '%s' (timeout: %s)"
                        % (cmd, timeout), level=level)

        prefix_str = '%s %s' % (self.name(), mode)
        helpers.bigrobot_devcmd_write("%-9s: %s\n" % (prefix_str, cmd))

        self.conn.execute(cmd)
        self.last_result = { 'content': self.conn.response }

        if helpers.not_matched(quiet, [1, 5]):
            helpers.log("Command content:\n%s" % self.content(), level=level)

        if timeout: self.timeout()

        self.clear_lock()
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
        # helpers.log("Closing DevConf '%s' (%s)" % (self.name(), self._host))
        self.conn.close(force=True)


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
        super(BsnDevConf, self).cmd('exit', mode='bash', quiet=5)
        helpers.log("Current mode is %s" % self.mode())

    def _cmd(self, cmd, quiet=0, mode='cmd', prompt=None,
             timeout=None, level=5):

        if helpers.is_extreme(self.platform()):
            if mode != 'config':
                helpers.test_error("For Extreme Networks switch, only"
                                   " config mode is supported")
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
                super(BsnDevConf, self).cmd('exit', mode='enable',
                                            quiet=5, level=level)
            elif self.is_config():
                if helpers.is_arista(self.platform()):
                    helpers.test_error("For Arista, you cannot switch from"
                                       " enable back to %s mode" % mode)
                helpers.log("Switching from config to %s mode" % mode,
                            level=level)
                super(BsnDevConf, self).cmd('end', mode='config', quiet=5)
                super(BsnDevConf, self).cmd('exit', mode='enable', quiet=5)
        elif mode == 'enable':
            if self.is_bash():
                self.exit_bash_mode(mode)

            if self.is_cli():
                helpers.log("Switching from cli to %s mode" % mode,
                            level=level)
                super(BsnDevConf, self).cmd('enable', mode='cli',
                                            quiet=5, level=level)
            elif self.is_config():
                helpers.log("Switching from config to %s mode" % mode,
                            level=level)
                super(BsnDevConf, self).cmd('end', mode='config',
                                            quiet=5, level=level)
        elif mode == 'config':
            if self.is_bash():
                self.exit_bash_mode(mode)

            if self.is_cli():
                helpers.log("Switching from cli to %s mode" % mode,
                            level=level)
                super(BsnDevConf, self).cmd('enable', mode='cli',
                                            quiet=5, level=level)
                super(BsnDevConf, self).cmd('configure', mode='enable',
                                            quiet=5, level=level)
            elif self.is_enable():
                helpers.log("Switching from enable to %s mode" % mode,
                            level=level)
                super(BsnDevConf, self).cmd('configure', mode=mode,
                                            quiet=5, level=level)
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
                                            quiet=5, level=level)

        self.mode(mode)
        # helpers.log("Current mode is %s" % self.mode(), level=level)

        if helpers.not_matched(quiet, [2, 5]):
            helpers.log("Execute command on '%s': '%s' (timeout: %s)"
                        % (self.name(), cmd,
                           timeout or self.default_timeout()),
                        level=level)

        super(BsnDevConf, self).cmd(cmd, prompt=prompt, mode=mode,
                                    timeout=timeout, quiet=5)

        if helpers.not_matched(quiet, [1, 5]):
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

    def send(self, *args, **kwargs):
        try:
            super(BsnDevConf, self).send(*args, **kwargs)
        except socket.error, e:
            error_str = str(e)
            helpers.log("socket.error: e: %s" % error_str)
            if re.match(r'Socket is closed', error_str):
                helpers.log("Socket is closed. Reconnecting...")
                self.connect()
                super(BsnDevConf, self).send(*args, **kwargs)
            else:
                self.expect_exception(None, "Unexpected socket error",
                                      soft_error=True)
                raise
        except:
            self.expect_exception(None, "Unexpected error", soft_error=True)
            raise

    def cli(self, cmd, quiet=0, prompt=False, timeout=None, level=5):
        return self.cmd(cmd, quiet=quiet, mode='cli', prompt=prompt,
                        timeout=timeout, level=level)

    def enable(self, cmd, quiet=0, prompt=False, timeout=None, level=5):
        return self.cmd(cmd, quiet=quiet, mode='enable', prompt=prompt,
                        timeout=timeout, level=level)

    def config(self, cmd, quiet=0, prompt=False, timeout=None, level=5):
        return self.cmd(cmd, quiet=quiet, mode='config', prompt=prompt,
                        timeout=timeout, level=level)

    def bash(self, cmd, quiet=0, prompt=False, timeout=None, level=5):
        return self.cmd(cmd, quiet=quiet, mode='bash', prompt=prompt,
                        timeout=timeout, level=level)

    def sudo(self, cmd, quiet=0, prompt=False, timeout=None, level=5):
        return self.cmd(' '.join(('sudo', cmd)), quiet=quiet, mode='bash',
                        prompt=prompt, timeout=timeout, level=level)

    def close(self):
        # helpers.log("Closing BsnDevConf '%s' (%s)"
        #            % (self.name(), self._host))
        super(BsnDevConf, self).close()


class ControllerDevConf(BsnDevConf):
    def __init__(self, *args, **kwargs):
        if 'is_monitor_reauth' in kwargs:
            is_monitor_reauth = kwargs['is_monitor_reauth']
            del kwargs['is_monitor_reauth']
        else:
            is_monitor_reauth = True

        super(ControllerDevConf, self).__init__(*args, **kwargs)

        self.test_monitor = None
        if is_monitor_reauth:
            self.monitor_reauth_init()
        else:
            helpers.log("Params attribute 'monitor_reauth' is false."
                        " Reauth monitoring is disabled.")

    def monitor_reauth_init(self):
        init_timer = helpers.bigrobot_monitor_reauth_init_timer()
        timer = helpers.bigrobot_monitor_reauth_timer()
        helpers.log("Test Monitor '%s' init_timer: %s, timer:%s"
                    % (self.name(), init_timer, timer))
        self.test_monitor = monitor.Monitor(
                    self.name(),
                    init_timer=init_timer,
                    timer=timer,
                    callback_task=self.monitor_action_reauth)

    def monitor_reauth(self, state):
        if state == True:
            helpers.debug("Enabling reauth monitor")
            if self.test_monitor:
                self.test_monitor.on(user_invoked=True)
            else:
                self.monitor_reauth_init()
        elif state == False:
            helpers.debug("Disabling reauth monitor")
            if self.test_monitor:
                self.test_monitor.off()
        else:
            helpers.test_error("Unknown state '%s' - should be True or False"
                               % state)

    def monitor_action_reauth(self):
        """
        This callback method is a workaround for the infamous 'reauth' issue.
        When in enable/config mode and idled for longer than 10 minutes, the
        system will kick you back to cli mode. E.g.,

        controller> enable
        controller#
        Timeout: exiting 'enable' mode to 'login' mode
        controller>

        standby controller> enable
        standby controller# config
        standby controller(config)#
        Timeout: exiting 'config' mode to 'login' mode
        standby controller>

        controller(config-fabricsetting)#
        Timeout: exiting 'config-fabricsetting' mode to 'login' mode
        controller>

        This method is called by autobot.monitor.Monitor(). A side effect
        is that helpers.log() doesn't work - Robot Framework logger is a
        bit funky. Workaround is to simply print to stdout.
        """
        print("Test Monitor for ControllerDevConf '%s' - triggered session"
              " keepalive to avoid reauth"
              % (self.name()))
        self.send("", quiet=5)
        self.expect(quiet=5)
        content = self.content()
        print("Test Monitor for ControllerDevConf '%s' - output='%s'"
              % (self.name(), repr(content)))

    def close(self):
        if self.test_monitor:
            self.test_monitor.off()
        helpers.log("Closing ControllerDevConf '%s' (%s)"
                    % (self.name(), self._host))
        super(ControllerDevConf, self).close()


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
            out = helpers.text_processing_str_remove_to_end(
                                out, line_marker=r'^Uptime is')
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

    def close(self):
        helpers.log("Closing SwitchDevConf '%s' (%s)"
                    % (self.name(), self._host))
        super(SwitchDevConf, self).close()


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
        self.is_screen_session = False

        super(MininetDevConf, self).__init__(host, user, password, name=name,
                                             timeout=timeout,
                                             port=port,
                                             protocol=protocol,
                                             debug=debug)
        if not is_start_mininet:
            helpers.log("Not starting Mininet session (is_start_mininet=%s)"
                        % is_start_mininet)
        else:
            # Warn user if there's already a screen session.
            self.send("screen -ls")
            self.expect(quiet=5)
            if not helpers.any_match(self.content(), r'No Sockets found'):
                helpers.environment_failure(
                    "There are other Mininet screen sessions running on %s."
                    " Please close them." % host)

            if helpers.bigrobot_preserve_mininet_screen_session_on_fail().lower() == 'true':
                # Must specify a "sensible" term type to avoid the screen error
                # "Clear screen capability required."
                self.send("export TERM=vt100")
                self.expect(quiet=0)
                self.send("screen")
                self.expect(r'.*Press Space or Return to end.*')
                self.send(" ", no_cr=True)
                self.is_screen_session = True

                # Important: Sleep a little big to ensure we get back the shell
                # prompt before issuing the command to start up Mininet.
                helpers.sleep(0.5)

            self.start_mininet()

    def is_cli(self):
        return self.mode() == 'cli'

    def is_bash(self):
        return self.mode() == 'bash'

    def exit_bash_mode(self, new_mode):
        self.mode(self._mode_before_bash)
        helpers.log("Switching from bash to %s mode" % new_mode, level=5)
        super(MininetDevConf, self).cmd('exit', mode='bash', quiet=5)
        helpers.log("Current mode is %s" % self.mode())

    def _cmd(self, cmd, quiet=0, mode='cli', prompt=False, timeout=None,
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
                                                quiet=5, level=level)
        else:
            helpers.environment_failure("Mode '%s' is not supported for Mininet"
                                        % mode)

        self.mode(mode)

        if helpers.not_matched(quiet, [2, 5]):
            helpers.log("Execute command on '%s': %s (timeout: %s)"
                        % (self.name(), cmd,
                           timeout or self.default_timeout()),
                        level=level)

        super(MininetDevConf, self).cmd(cmd, prompt=prompt, mode=mode,
                                        timeout=timeout, quiet=5)
        if helpers.not_matched(quiet, [1, 5]):
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

    def cli(self, cmd, quiet=0, prompt=False, timeout=None, level=5):
        return self.cmd(cmd, quiet=quiet, mode='cli', prompt=prompt,
                        timeout=timeout, level=level)

    def bash(self, cmd, quiet=0, prompt=False, timeout=None, level=5):
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
        content = self.cli(_cmd, quiet=0)['content']
        if not helpers.any_match(content, r'Starting CLI'):
            helpers.environment_failure("Mininet CLI did not start correctly")
        else:
            helpers.log("Mininet CLI started correctly")
        self.state = 'started'

    def stop_mininet(self):
        if self.state == 'stopped':
            helpers.log("Mininet is not running. No need to stop it.")
            return True

        helpers.log("Stopping Mininet on '%s'" % self.name())
        self.cli("exit", quiet=0)
        self.state = 'stopped'

    def restart_mininet(self, new_topology=None, sleep=5):
        helpers.log("Restarting Mininet topology on '%s'" % self.name())
        self.stop_mininet()
        helpers.sleep(sleep)
        self.start_mininet(new_topology)

    def close(self):
        if (helpers.bigrobot_test_suite_status().lower() == 'fail' and
            helpers.bigrobot_preserve_mininet_screen_session_on_fail().lower() == 'true'):
            helpers.log("Env BIGROBOT_PRESERVE_MININET_SCREEN_SESSION_ON_FAIL"
                        " is 'True' and test suite failed. Preserving Mininet"
                        " screen session.")
            return True
        try:
            self.stop_mininet()
        except:
            if helpers.bigrobot_ignore_mininet_exception_on_close().lower() == 'true':
                helpers.log("Env BIGROBOT_IGNORE_MININET_EXCEPTION_ON_CLOSE"
                            " is 'True'. Ignoring Mininet exception.")
            else:
                raise
        else:
            if self.is_screen_session:
                helpers.log("Exiting 'screen' session")
                self.send('exit', quiet=5)  # terminate screen session
            helpers.log("Closing MininetDevConf '%s' (%s)"
                        % (self.name(), self._host))
            super(MininetDevConf, self).close()


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

    def close(self):
        # helpers.log("Closing T6MininetDevConf '%s' (%s)"
        #            % (self.name(), self._host))
        super(T6MininetDevConf, self).close()



class HostDevConf(DevConf):
    def __init__(self, *args, **kwargs):
        super(HostDevConf, self).__init__(*args, **kwargs)
        self.bash('uname -a')

    def _cmd(self, cmd, quiet=0, prompt=False, timeout=None, level=4):
        if helpers.not_matched(quiet, [2, 5]):
            helpers.log("Execute command on '%s': '%s' (timeout: %s)"
                        % (self.name(), cmd,
                           timeout or self.default_timeout()),
                        level=level)

        super(HostDevConf, self).cmd(cmd, prompt=prompt, mode='bash',
                                     timeout=timeout, quiet=5)
        if helpers.not_matched(quiet, [1, 5]):
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

    def sudo(self, cmd, quiet=0, prompt=False, timeout=None, level=5):
        return self.bash(' '.join(('sudo', cmd)), quiet=quiet, prompt=prompt,
                         timeout=timeout, level=level)

    def close(self):
        helpers.log("Closing HostDevConf '%s' (%s)"
                    % (self.name(), self._host))
        super(HostDevConf, self).close()
