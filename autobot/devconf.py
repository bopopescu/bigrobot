from Exscript import Account, PrivateKey
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
    DevConf for talking to devices via the CLI (SSH, Telnet).
    """
    def __init__(self, host=None, user=None, password=None,
                 port=None,
                 console_info=None,
                 name=None,
                 timeout=None,
                 protocol='ssh',
                 debug=0,
                 privatekey=None,
                 privatekey_password=None,
                 privatekey_type=None):
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
        self._protocol = protocol if protocol else 'ssh'
        self._console_info = console_info
        self._debug = debug
        self._privatekey = privatekey
        self._privatekey_password = helpers.get(privatekey_password, '')
        self._privatekey_type = helpers.get(privatekey_type, 'rsa')
        self._platform = None
        self.conn = None
        self.last_result = None
        self._mode = 'cli'
        self.is_prompt_changed = False
        self._lock = False
        self._last_matched_index = self._last_matched_object = None

        self._logpath = helpers.bigrobot_log_path_exec_instance()
        if not self._logpath:
            self._logpath = '/tmp'
        else:
            # Create directory if it doesn't exist
            if not helpers.file_exists(self._logpath):
                helpers.mkdir_p(self._logpath)
        self._logfile = ('%s/devconf_conversation.%s.log'
                         % (self._logpath, self._name))
        helpers.file_write_append_once(self._logfile,
                "\n\n--------- %s New devconf conversation for '%s'\n\n"
                % (helpers.ts_long_local(), self._name))

        self._timeout = timeout if timeout else 30  # default timeout

        self.connect()

    def _patch_driver(self, d):
        """
        A convention commonly seen in device output is an "Authen banner"
        which appears when connected to the device (but before authentication),
        followed by a "Login banner" after successfully authenticated. E.g.,

          $ ssh admin@10.8.1.225
          Warning: Permanently added '10.8.1.225' (RSA) to the list of known hosts.
          Big Cloud Fabric Appliance 2.0.0-master01-SNAPSHOT (bcf_master #3338)      <=== Authen banner
          Log in as 'admin' to configure

          admin@10.8.1.225's password: *****
          Last login: Tue Feb  3 17:42:28 2015 from 10.1.13.188
          Big Cloud Fabric Appliance 2.0.0-master01-SNAPSHOT (bcf_master #3338)      <=== Login banner
          Logged in as admin, 2015-02-24 19:13:13.431000 UTC, auth from 10.1.10.25
          standby controller>

        Exscript and BigRobot relies the Login banner to guess the platform/OS
        in order to select the appropriate driver.

        2015-02-24 For Switch Light OS, the Login banner has been removed which
        causes the OS detection to fail and to return a 'generic' device. We
        attempt to correct the driver issue by guessing the platform/OS from
        the 'show version' output.
        """

        if not re.match(r'^s\d+', self._name):
            helpers.log("Devconf driver patch for '%s' failed - currently only"
                        " support switches (s1, s2, etc.), using Generic driver"
                        % self._name)
            return d

        helpers.log("Not able to find proper driver for '%s'. Possibly missing Login banner."
                    " Attempting to detect platform using 'show version'."
                    % self._name)
        try:
            result = self.cmd("show blah")
            self.mode('cli')
        except:
            result = None

        if result and re.search(r'Software Image Version: Switch Light', result['content']):
            helpers.log("Devconf driver patch for '%s' detected Switch Light OS"
                        % self._name)
            self.conn.set_driver('bsn_switch')
            self._platform = "switchlight"
            return self.conn.get_driver()
        else:
            helpers.log("Devconf driver patch for '%s' failed - using Generic driver"
                        % self._name)
            return d

    def mode(self, new_mode=None):
        if new_mode:
            self._mode = new_mode
        return self._mode

    def connect(self):
        try:
            if self._protocol == 'telnet' or self._protocol == 'ssh':
                auth_info = "(login:%s, password:%s)" % (self._user,
                                                         self._password)
                if self._protocol == 'ssh' and self._privatekey:
                    # User-specified identity file, e.g., ~/.ssh/id_rsa.
                    # This is equivalent to 'ssh -i' option.
                    helpers.debug("Using SSH identity in '%s' of type '%s'"
                                  % (self._privatekey, self._privatekey_type))
                    key = PrivateKey.from_file(
                                filename=self._privatekey,
                                password=self._privatekey_password,
                                keytype=self._privatekey_type)
                else:
                    key = None

                account = Account(self._user, self._password, key=key)

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

        helpers.debug("Setting expect timeout to %s seconds" % self._timeout)
        self.conn.set_timeout(self._timeout)

        driver = self.conn.get_driver()
        if driver.name == 'generic' and self._console_info == None:
            # Patch the device driver, possibly due to missing Login banner.
            # Don't do this if the devconf session is a console.
            driver = self._patch_driver(driver)

        helpers.log("Node '%s' using devconf driver '%s' (name: '%s')"
                    % (self._name, driver, driver.name))

        # Devconf autoinit which will invoke driver's init_terminal()
        self.conn.autoinit()

        # Aliases
        self.set_prompt = self.conn.set_prompt
        self.get_prompt = self.conn.get_prompt

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
            print("%s - !!!!!!! DEVCONF_LOCK: %s is locked"
                  % (helpers.ts_logger(), self.name()))
        return self._lock

    def set_lock(self):
        self._lock = True
        # print("%s - !!!!!!! DEVCONF_LOCK: %s set lock"
        #      % (helpers.ts_logger(), self.name()))
        return self._lock

    def clear_lock(self):
        self._lock = False
        # print("%s - !!!!!!! DEVCONF_LOCK: %s clear lock"
        #      % (helpers.ts_logger(), self.name()))
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
        if helpers.not_quiet(quiet, [2, 5]):
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
        if helpers.not_quiet(quiet, [2, 5]):
            helpers.log("Expecting prompt: %s" % self.prompt_str(prompt),
                        level=level)

        try:
            self._last_matched_index, self._last_matched_object = self.conn.expect(prompt)
            self.last_result = {'content': self.conn.response}
            if helpers.not_quiet(quiet, [1, 5]):
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

        if helpers.not_quiet(quiet, [1, 5]):
            helpers.log("Expect prompt matched (%s, '%s')"
                        % (self._last_matched_index,
                           helpers.re_match_str(self._last_matched_object)))

        self.clear_lock()
        return (self._last_matched_index, self._last_matched_object)

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
        if helpers.not_quiet(quiet, [2, 5]):
            helpers.log("Expecting waitfor prompt: %s"
                        % self.prompt_str(prompt), level=level)

        try:
            self._last_matched_index, self._last_matched_object = self.conn.waitfor(prompt)

            self.last_result = { 'content': self.conn.response }
            if helpers.not_quiet(quiet, [2, 5]):
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

        if helpers.not_quiet(quiet, [1, 5]):
            helpers.log("Expect prompt matched (%s, '%s')"
                        % (self._last_matched_index,
                           helpers.re_match_str(self._last_matched_object)))

        self.clear_lock()
        return (self._last_matched_index, self._last_matched_object)


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

        if helpers.not_quiet(quiet, [2, 5]):
            helpers.log("Execute command: '%s' (timeout: %s)"
                        % (cmd, timeout), level=level)

        prefix_str = '%s %s' % (self.name(), mode)
        helpers.bigrobot_devcmd_write("%-9s: %s\n" % (prefix_str, cmd))

        self._last_matched_index, self._last_matched_object = self.conn.execute(cmd)

        self.last_result = { 'content': self.conn.response }

        if helpers.not_quiet(quiet, [1, 5]):
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
    def __init__(self, *args, **kwargs):
        # helpers.debug("Creating BsnDevConf '%s'" % kwargs.get('name'))
        super(BsnDevConf, self).__init__(*args, **kwargs)
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

    def _reset_mode(self):
        if self._last_matched_object == None:
            return False
        matched_string = self._last_matched_object.group(self._last_matched_index)
        helpers.log("!!!!! matched_string: '%s'" % matched_string)
        is_matched_prompt = False
        for prompt in self.conn.get_prompt():
            if re.match(prompt, matched_string):
                is_matched_prompt = True
                break
        is_mismatched = False
        if is_matched_prompt:  # We found a prompt
            helpers.log("!!!!! We found a prompt ('%s')" % matched_string.lstrip())
            if self.mode() != 'cli' and re.match(r'[\r\n\x07]+(\w+(-?\w+)?\s?@?)?[\-\w+\.:/]+(?:\([^\)]+\))?(:~)?> ?$', matched_string):
                # Detected mode mismatch, possibly caused by idle timeout.
                # Restore to 'cli' mode.
                helpers.warn("'%s' current mode is '%s' but prompt is '%s' ('cli')."
                             " Possibly triggered by reauth. Resetting mode to 'cli'."
                            % (self.name(), self.mode(), matched_string.lstrip()))
                self.mode(new_mode='cli')
                is_mismatched = True
            else:
                helpers.log("!!!!! Current mode is '%s' and prompt is '%s'. All is well."
                            % (self.mode(), matched_string.lstrip()))
                pass
        return is_mismatched

    def _cmd(self, cmd, quiet=0, mode='cmd', prompt=None,
             timeout=None, level=5):

        """
        if helpers.is_bsn_controller(self.platform()):
            content = super(BsnDevConf, self).cmd('', prompt=prompt,
                                                  timeout=timeout, quiet=5)['content']
            if self._reset_mode():
                helpers.log("'%s' mode reset to 'cli'. Last output was:\n%s."
                            % (self.name(), helpers.indent_str("'" + content + "'")))
        """
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

                # 2014-09-30 It seems this is causing havoc on console
                # sessions. Disable for now.
                # super(BsnDevConf, self).cmd("set +o emacs",
                #                            mode=self._mode_before_bash,
                #                            quiet=5, level=level)

        self.mode(mode)
        # helpers.log("Current mode is %s" % self.mode(), level=level)

        if helpers.not_quiet(quiet, [2, 5]):
            helpers.log("Execute command on '%s': '%s' (timeout: %s)"
                        % (self.name(), cmd,
                           timeout or self.default_timeout()),
                        level=level)

        super(BsnDevConf, self).cmd(cmd, prompt=prompt, mode=mode,
                                    timeout=timeout, quiet=5)

        if helpers.not_quiet(quiet, [1, 5]):
            helpers.log("%s content on '%s':\n%s%s"
                        % (mode, self.name(), self.content(),
                           br_utils.end_of_output_marker()),
                           level=level)

        """
        if helpers.is_bsn_controller(self.platform()):
            if re.search(r"^Timeout: exiting '\w+' mode to '\w+' mode", self.content(), re.M):
                helpers.log("Found mode mismatch on '%s'. Possibly triggered by idle timeout."
                            " Resetting mode to 'cli' and re-running command."
                            % (self.name()))
                self.mode('cli')
                self.cmd(cmd, quiet=quiet, mode=mode, prompt=prompt,
                         timeout=timeout, level=level)
            else:
                # helpers.log("!!!!! No mode mismatch. All is well!")
                pass
        """
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
        helpers.debug("Creating ControllerDevConf '%s'" % kwargs.get('name'))

        # !!! FIXME 2014-08-28 Reauth monitoring is disabled because (for some
        # still unknown reason) it causes Exscript to ignore the expect
        # timeout, so a script may hang indefinitely while waiting for a
        # matching prompt. Need to revisit this problem later. For now we
        # have a workaround.
        #
        # Inside autobot/node.py is where we disabled this functionality.
        #
        is_monitor_reauth = kwargs.pop('is_monitor_reauth', False)
        super(ControllerDevConf, self).__init__(*args, **kwargs)

        self.test_monitor = None
        if is_monitor_reauth:
            self.monitor_reauth_init()
        else:
            # helpers.log("Params attribute 'monitor_reauth' is false."
            #            " Reauth monitoring is disabled.")
            pass

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
        msg = ("%s - Test Monitor '%s' - triggered session"
               " keepalive to avoid reauth"
               % (helpers.ts_logger(), self.name()))
        # print msg
        helpers.log(msg)
        self.send("", quiet=5)
        self.expect(quiet=5)
        content = self.content()
        msg = ("%s - Test Monitor '%s' - output='%s'"
               % (helpers.ts_logger(), self.name(), repr(content)))
        print msg
        helpers.log(msg)

    def close(self):
        if self.test_monitor:
            self.test_monitor.off()
        helpers.debug("Closing ControllerDevConf '%s' (%s)"
                      % (self.name(), self._host), level=4)
        super(ControllerDevConf, self).close()


class SwitchDevConf(BsnDevConf):
    def __init__(self, *args, **kwargs):
        helpers.debug("Creating SwitchDevConf '%s'" % kwargs.get('name'))
        super(SwitchDevConf, self).__init__(*args, **kwargs)
        self._info = None
        # self.mode('cli')

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
        helpers.debug("Closing SwitchDevConf '%s' (%s)"
                      % (self.name(), self._host))
        super(SwitchDevConf, self).close()


class MininetDevConf(DevConf):
    """
    :param topology: str, in the form 'tree,4,2'
    """
    def __init__(self, *args, **kwargs):
        helpers.debug("Creating MininetDevConf '%s'" % kwargs.get('name'))
        self.controller = kwargs.pop('controller', None)
        self.controller2 = kwargs.pop('controller2', None)
        is_start_mininet = kwargs.pop('is_start_mininet', True)
        if self.controller is None:
            helpers.environment_failure("Must specify a controller for Mininet.")

        self.topology = kwargs.pop('topology', None)
        if self.topology is None:
            helpers.environment_failure("Must specify a topology for Mininet.")

        self._mode_before_bash = None
        self.openflow_port = kwargs.pop('openflow_port', None)
        self.state = 'stopped'  # or 'started'
        self.is_screen_session = False

        super(MininetDevConf, self).__init__(*args, **kwargs)
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
                    " Please close them." % self._host)

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

        if helpers.not_quiet(quiet, [2, 5]):
            helpers.log("Execute command on '%s': %s (timeout: %s)"
                        % (self.name(), cmd,
                           timeout or self.default_timeout()),
                        level=level)

        super(MininetDevConf, self).cmd(cmd, prompt=prompt, mode=mode,
                                        timeout=timeout, quiet=5)
        if helpers.not_quiet(quiet, [1, 5]):
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
            helpers.debug("Closing MininetDevConf '%s' (%s)"
                          % (self.name(), self._host))
            super(MininetDevConf, self).close()


class T6MininetDevConf(MininetDevConf):
    """
    :param topology: str, in the form
        '--num-spine 0 --num-rack 1 --num-bare-metal 2 --num-hypervisor 0'
    """
    def __init__(self, **kwargs):
        helpers.debug("Creating T6MininetDevConf '%s'" % kwargs.get('name'))
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
        helpers.debug("Closing T6MininetDevConf '%s' (%s)"
                      % (self.name(), self._host))
        super(T6MininetDevConf, self).close()


class PduDevConf(DevConf):
    def __init__(self, *args, **kwargs):
        helpers.debug("Creating PduDevConf '%s'" % kwargs.get('name'))
        super(PduDevConf, self).__init__(*args, **kwargs)

    def close(self):
        helpers.debug("Closing PduDevConf '%s' (%s)"
                    % (self.name(), self._host))
        super(PduDevConf, self).close()


class HostDevConf(DevConf):
    def __init__(self, *args, **kwargs):
        helpers.debug("Creating HostDevConf '%s'" % kwargs.get('name'))
        super(HostDevConf, self).__init__(*args, **kwargs)
        self.bash('uname -a')

    def _cmd(self, cmd, quiet=0, prompt=False, timeout=None, level=4):
        if helpers.not_quiet(quiet, [2, 5]):
            helpers.log("Execute command on '%s': '%s' (timeout: %s)"
                        % (self.name(), cmd,
                           timeout or self.default_timeout()),
                        level=level)

        super(HostDevConf, self).cmd(cmd, prompt=prompt, mode='bash',
                                     timeout=timeout, quiet=5)
        if helpers.not_quiet(quiet, [1, 5]):
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
        helpers.debugh("Closing HostDevConf '%s' (%s)"
                       % (self.name(), self._host))
        super(HostDevConf, self).close()
