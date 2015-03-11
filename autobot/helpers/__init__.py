import os
import sys
import errno
import json
import yaml
import datetime
import time
import uuid
import pprint
import paramiko
import inspect
import subprocess
import signal
import traceback
import re
import ipcalc
import platform
import unicodedata
import tempfile
import shutil
import curses.ascii as ascii
import xml.dom.minidom
import smtplib
from email.mime.text import MIMEText
from scp import SCPClient
from pytz import timezone
from autobot.version import get_version
import autobot.utils as br_utils

# All below are modules in the helpers package. So we can control and manage
# name conflicts. Therefore it's assumed safe to do 'import *'.
from log import *  # pylint: disable=W0401, W0403
from gobot import *  # pylint: disable=W0401, W0403
from exec_timer import *  # pylint: disable=W0401, W0403

# Convenience helper function any_match() and first_match() imported from
# Exscript. More info at
# http://knipknap.github.io/exscript/api/Exscript.util.match-module.html
from Exscript.util.match import any_match, first_match

_TZ = timezone("America/Los_Angeles")
_BIGROBOT_ENV_LIST = []
SMTP_SERVER = 'smtp.eng.bigswitch.com'
DEFAULT_EMAIL = 'email_service@bigswitch.com'


def ctrl(char):
    """
    Returns the control character. E.g., helpers.ctrl('c') returns the value
    for Ctrl-c which is \x03'.
    See http://stackoverflow.com/questions/6248766/how-to-enter-the-escape-characters-for-telnet-programmatically
    """
    return ascii.ctrl(char)


def bigrobot_env_variables():
    env_str = ''
    for key in os.environ.keys():
        if re.match(r'^BIGROBOT_', key):
            env_str += "%s=%s\n" % (key, get_env(key))
    return env_str


def bigrobot_module_dependencies():
    import Exscript
    import Crypto
    # import pexpect
    import httplib2

    s = "BigRobot version        %s\n" % get_version()

    try:
        import robot
        s += "Robot Framework version %s\n" % robot.version.VERSION
    except:
        pass

    s += "Exscript version        %s\n" % Exscript.version.__version__
    s += "Paramiko version        %s\n" % paramiko.__version__
    s += "Crypto version          %s\n" % Crypto.__version__
    # s += "Pexpect version         %s\n" % pexpect.__version__
    s += "Httplib2 version        %s\n" % httplib2.__version__
    pversion = sys.version_info
    s += "Python version          %s.%s.%s" % (pversion.major,
                                               pversion.minor,
                                               pversion.micro)
    return s


# is_bool() needs to be defined before test_error() which uses it.
def is_bool(data):
    """Verify if the input is a valid Python boolean."""
    return isinstance(data, bool)


def warn(s, level=2, all_levels=False):
    """
    Warn log.
    """
    Log().warn(s, level, all_levels=all_levels)


def debug(s, level=2, all_levels=False):
    """
    Debug log.
    """
    Log().debug(s, level, all_levels=all_levels)


def trace(s, level=2, all_levels=False):
    """
    Trace log.
    """
    Log().trace(s, level, all_levels=all_levels)


def info(s, level=2, log_level="info", all_levels=False):
    """
    Info log.
    """
    Log().log(s, level=level, log_level=log_level, all_levels=all_levels)


# Alias
test_log = info
log = info


def summary_log(s, level=2, all_levels=False):
    """
    Similar to Info log, but also write the message to stderr as well.
    """
    Log().info(s, level, also_console=True, all_levels=all_levels)


def log_task_output(task_id):
    info("Task output - http://%s/bigrobot_esb/%s/"
         % (bigrobot_log_archiver(), task_id))


def autobot_logger():
    """
    The autobot logging handle may need to be passed to another API so API
    messages can be written to the same logging handle (if they use the same
    logging API).
    """
    return Log().autobot_logger


def autobot_log_level(level):
    """
    Default autobot log level is logging.DEBUG from Python 'logging' module.
    """
    Log().set_autobot_log_level(level)


def autobot_log_send_to_file(filename, close=False):
    """
    In addition to writing log messages to autobot logger, also write to
    the specified file. If close=True, stop writing and close file.
    """
    Log().autobot_log_send_to_file(filename, close)


def analyze(s, level=3):
    info(s, level)


def prettify(data, format_newline=False):
    """
    Return the Python object as a prettified string (formatted).
    """
    pretty_str = pprint.pformat(data)
    if format_newline:
        pretty_str = pretty_str.replace('\\n', '\n')
    return pretty_str


def prettify_xml(xml_str):
    """
    Given an XML string, return a prettified XML string (formatted).
    """
    with tempfile.NamedTemporaryFile() as f:
        filename = f.name
        f.write(xml_str)
        f.flush()
        x = xml.dom.minidom.parse(filename)

    text = x.toprettyxml()
    text = os.linesep.join([s for s in text.splitlines() if not re.match(r'^\s*$', s)])
    return text


def pretty_log(s, format_newline=True, level=3):
    log(prettify(s, format_newline), level)


def exception_info_type():
    return sys.exc_info()[0]


def exception_info_value():
    return str(sys.exc_info()[1])


def exception_info_traceback():
    """
    Returns a string containing the stack trace.
    """
    # return sys.exc_info()[2]
    return traceback.format_exc()


def exception_info():
    """
    Returns printable string of tuple (type, value, traceback).
    See http://docs.python.org/2/library/sys.html#sys.exc_info
    """
    (_type, _val, _) = sys.exc_info()
    return ("Exception type: %s\nException value: %s\nException traceback:\n%s%s"
            % (_type, _val, indent_str(exception_info_traceback()),
               br_utils.end_of_output_marker()))


def error_msg(msg):
    print("Error: %s" % msg)


def error_exit(msg, exit_code=None):
    """
    exit_code follows the Robot Framework convention. Default is 255 which
    matches "Unexpected internal error."
    See https://twiki.cern.ch/twiki/bin/view/EMI/RobotFrameworkAdvancedGuide#Return_Codes
    """
    error_msg(msg)

    # For continuous integration (e.g., Jenkins with Robot-plugin), can only
    # exit with 0 and let robot-plugin do the failure analysis. This is as per
    # https://wiki.jenkins-ci.org/display/JENKINS/Robot+Framework+Plugin
    # "Force your Robot script to return successfully from shell with 'exit 0'
    # to empower the plugin in deciding if the build is success/failure
    # (by default Robot exits with error code when there's any failed tests)"
    if bigrobot_continuous_integration() == 'True':
        exit_code = 0

    if not exit_code:
        exit_code = 255
    sys.exit(exit_code)


def error_exit_if_file_not_exists(msg, f, exit_code=None):
    if f is None:
        error_exit(''.join((msg, ': <file_not_specified>')))
    if not os.path.exists(f):
        error_exit(''.join((msg, ': ', f)), exit_code)


def exit_robot_immediately(msg=None):
    """
    See https://groups.google.com/forum/#!topic/robotframework-users/Mbt_8Pe3t7c
    Send same signal that Ctrl-C sends to stop execution gracefully.
    Currently, this is the sure way to exit out of Robot Framework.
    """
    if msg:
        log(msg, level=4)
    log("Exiting BigRobot now...", level=4)
    os.kill(os.getpid(), signal.SIGINT)  # "Second signal will force exit"
    os.kill(os.getpid(), signal.SIGINT)  # "Execution forcefully stopped"


class TestFailure(AssertionError):
    """
    This can be triggered when there is a test case failure.
    """


class TestError(AssertionError):
    """
    This can be triggered when there is a test error. It is designed for
    flagging uncaught error conditions in the test libraries, such as the
    'Unknown ping error' in helpers.ping().
    """
    # ROBOT_EXIT_ON_FAILURE = True


class EnvironmentFailure(RuntimeError):
    """
    This can be triggered when there is a test environment failure. It is a
    critical condition which should prevent further test executions.
    """
    ROBOT_EXIT_ON_FAILURE = True


def test_success(msg):
    """
    Call this on test success.
    """
    log(msg)


def environment_failure(msg):
    """
    Call this on environmental failure.
    """
    raise EnvironmentFailure(msg)


def test_failure(msg, soft_error=False):
    """
    Call this on test failure.
    """
    if not is_bool(soft_error):
        environment_failure("helpers.test_failure() argument 'soft_error' must"
                            " be a boolean.")
    if soft_error:
        log("Soft test failure: %s" % msg)
        return False
    else:
        raise TestFailure(msg)


def test_error(msg, soft_error=False, dump_error_stack=True):
    """
    Call this on test error.
    """
    if not is_bool(soft_error):
        environment_failure("helpers.test_error() argument 'soft_error' must"
                            " be a boolean.")
    if dump_error_stack:
        log("Dumping the error stack:\n" + exception_info())
    if soft_error:
        log("Soft test error: %s" % msg)
        return False
    else:
        raise TestError(msg)


def _env_get_and_set(name, new_val=None, default=None):
    """
    Category: Get/set environment variables for BigRobot.

    :param name:    str, The name of the environment variable
    :param new_val: str, If specified, force set env with new_value
    :param default: str, Default fallback value
    :return: str or None, Value of the environment variable

    Attempt to update `name` environment variable with a value.
    - If `new_val` is specified, then assign it to env (force option)
    - Else if env exists, then use it
    - Else, if default is specified, then assign it to env (fallback option)
    - Else return None as last resort
    """
    if new_val is not None:
        os.environ[name] = int_to_str(new_val)
    elif name in os.environ:
        pass
    elif default is not None:
        os.environ[name] = int_to_str(default)
    else:
        return None

    if name not in _BIGROBOT_ENV_LIST:
        _BIGROBOT_ENV_LIST.append(name)

    return os.environ[name]


def set_env(name, value, quiet=True):
    """
    Set the environment variable 'name' to 'value'.
    Note: In Robot text file, you can call the keyword 'Set Environment Variable'
          from the OperatingSystem library instead.
    """
    # Python's os module requires that env value be a string, not integer.
    value = str(value)

    if name in os.environ:
        if not quiet:
            debug("Environment variable '%s' current value is: '%s'"
                  % (name, os.environ[name]))
    os.environ[name] = value
    if not quiet:
        debug("Environment variable '%s' new value is: '%s'"
              % (name, os.environ[name]))
    return os.environ[name]


def get_env(name, default=None, quiet=True):
    """
    Get the environment variable 'name'.
    Note: In Robot text file, you can call the keyword 'Get Environment Variable'
          from the OperatingSystem library instead.
    """
    if not name in os.environ:
        if not quiet:
            debug("Environment variable '%s' doesn't exist." % name)
        if default:
            return set_env(name, default, quiet)
        else:
            return None
    else:
        if not quiet:
            debug("Environment variable '%s': '%s'"
                  % (name, os.environ[name]))
        return os.environ[name]


def remove_env(name, quiet=True):
    """
    Remove the environment variable 'name'.
    Note: In Robot text file, you can call the keyword 'Remove Environment Variable'
          from the OperatingSystem library instead.
    """
    if not name in os.environ:
        if not quiet:
            debug("Environment variable '%s' doesn't exist. Removal is not required."
                  % name)
        return False
    else:
        if not quiet:
            debug("Environment variable '%s' is removed" % name)
        del os.environ[name]
        return True


def bigrobot_env_list():
    return _BIGROBOT_ENV_LIST


def bigrobot_path(new_val=None, default=None):
    """
    Category: Get/set environment variables for BigRobot.
    """
    return _env_get_and_set('BIGROBOT_PATH', new_val, default)


def bigrobot_log_path(new_val=None, default=None):
    """
    Category: Get/set environment variables for BigRobot.
    """
    return _env_get_and_set('BIGROBOT_LOG_PATH', new_val, default)


def bigrobot_log_path_exec_instance(new_val=None, default=None):
    """
    Category: Get/set environment variables for BigRobot.
    This is the actual log path (i.e., outputdir) for an instance of
    test suite execution.
    """
    return _env_get_and_set('BIGROBOT_LOG_PATH_EXEC_INSTANCE',
                            new_val,
                            default)


def bigrobot_log_path_exec_instance_relative(new_val=None, default=None):
    """
    Category: Get/set environment variables for BigRobot.
    This is the relative log path (i.e., outputdir) for an instance of
    test suite execution.
    """
    return _env_get_and_set('BIGROBOT_LOG_PATH_EXEC_INSTANCE_REL',
                            new_val,
                            default)


def bigrobot_devconf_debug_level(new_val=None, default=None):
    """
    Category: Get/set environment variables for BigRobot.
    Set the global devconf debug level. This value overrides the
    set_devconf_debug_level property in the topo file as well as the
    devconf_debug_level parameter in Test.node_connect() and Test.node_spawn().
      0:  disable
      1-5:  where 5 is very verbose
    """
    return _env_get_and_set('BIGROBOT_DEVCONF_DEBUG_LEVEL',
                            new_val,
                            default)


def bigrobot_devcmd_log(new_val=None, default=None):
    """
    Category: Get/set environment variables for BigRobot.
    This log file captures all the device CLI/REST commands.
    """
    return _env_get_and_set('BIGROBOT_DEVICE_COMMAND_LOG', new_val, default)


def bigrobot_listener_log(new_val=None, default=None):
    """
    Category: Get/set environment variables for BigRobot.
    This log file captures all the device CLI/REST commands.
    """
    return _env_get_and_set('BIGROBOT_LISTENER_LOG', new_val, default)


def bigrobot_global_params(new_val=None, default=None):
    """
    Category: Get/set environment variables for BigRobot.
    """
    return _env_get_and_set('BIGROBOT_GLOBAL_PARAMS', new_val, default)


def bigrobot_additional_params(new_val=None, default=None):
    """
    Category: Get/set environment variables for BigRobot.
    """
    return _env_get_and_set('BIGROBOT_ADDITIONAL_PARAMS', new_val, default)


def bigrobot_suite(new_val=None, default=None):
    """
    Category: Get/set environment variables for BigRobot.
    """
    return _env_get_and_set('BIGROBOT_SUITE', new_val, default)


def bigrobot_exec_hint_format(new_val=None, default='export'):
    """
    Category: Get/set environment variables for BigRobot.
    Options:
        - 'export'
        - 'run_gobot'
    """
    opt = _env_get_and_set('BIGROBOT_EXEC_HINT_FORMAT', new_val, default)
    if opt == 'export':
        return 'export BIGROBOT_SUITE=%s'
    elif opt == 'run_gobot':
        return 'BIGROBOT_SUITE=%s gobot test'
    else:
        environment_failure("Invalid option '%s'. Supported options are"
                            " 'export', 'run_gobot'."
                            % opt)


def bigrobot_topology(new_val=None, default=None):
    """
    Category: Get/set environment variables for BigRobot.
    This env points to the topology file. In BigRobot, this is typically
    the name of the script appended with '.virtual.topo' or '.physical.topo'.
    """
    return _env_get_and_set('BIGROBOT_TOPOLOGY', new_val, default)


def bigrobot_topology_for_esb(new_val=None, default='None'):
    """
    Category: Get/set environment variables for BigRobot.
    This env is a YAML topology string which is passed to the ESB
    (Enterprise Service Bus).

    Check whether value is a Python dictionary and convert it to YAML if so.
    """
    if is_dict(new_val): new_val = to_yaml(new_val)
    if is_dict(default): default = to_yaml(default)
    return _env_get_and_set('BIGROBOT_TOPOLOGY_FOR_ESB', new_val, default)


def bigrobot_esb(new_val=None, default='False'):
    """
    Category: Get/set environment variables for BigRobot.
    Set to 'True' when running inside the Enterprise Service Bus (ESB)
    environment.
    """
    return _env_get_and_set('BIGROBOT_ESB', new_val, default)


def bigrobot_esb_broker(new_val=None,
                        default='amqp://guest@qa-esb1.qa.bigswitch.com//'):
    """
    Category: Get/set environment variables for BigRobot.
    Defines the URI of the ESB broker.
    """
    return _env_get_and_set('BIGROBOT_ESB_BROKER', new_val, default)

def bigrobot_continuous_integration(new_val=None, default='False'):
    """
    Category: Get/set environment variables for BigRobot.
    Set to 'True' if test is run under smoketest/regression environment
    (i.e., Jenkins).
    """
    return _env_get_and_set('BIGROBOT_CI', new_val, default)


def bigrobot_params_input(new_val=None, default=None):
    """
    Category: Get/set environment variables for BigRobot.
    Dynamic topology support. This env points to a file containing the
    "reference" topology information. Format is:
        BIGROBOT_PARAMS_INPUT=file:<path_and_file>
    e.g.,
        BIGROBOT_PARAMS_INPUT=file:/tmp/static.topo
    """
    return _env_get_and_set('BIGROBOT_PARAMS_INPUT', new_val, default)


def bigrobot_params(new_val=None, default=None):
    """
    Category: Get/set environment variables for BigRobot.
    """
    return _env_get_and_set('BIGROBOT_PARAMS', new_val, default)


def bigrobot_nose_setup(new_val=None, default='False'):
    """
    Category: Get/set environment variables for BigRobot.
    Set to 'True' to enable testing using the Nose test framework.
    """
    return _env_get_and_set('BIGROBOT_NOSE_SETUP', new_val, default)


def bigrobot_test_setup(new_val=None, default='True'):
    """
    Category: Get/set environment variables for BigRobot.
    Set to 'False' to bypass Test setup.
    """
    return _env_get_and_set('BIGROBOT_TEST_SETUP', new_val, default)


def bigrobot_test_teardown(new_val=None, default='True'):
    """
    Category: Get/set environment variables for BigRobot.
    Set to 'False' to bypass Test teardown.
    """
    return _env_get_and_set('BIGROBOT_TEST_TEARDOWN', new_val, default)


def bigrobot_test_postmortem(new_val=None, default='False'):
    """
    Category: Get/set environment variables for BigRobot.
    Set to 'False' to bypass Test case postmortem.
    """
    return _env_get_and_set('BIGROBOT_TEST_POSTMORTEM', new_val, default)


def bigrobot_test_clean_config(new_val=None, default='True'):
    """
    Category: Get/set environment variables for BigRobot.
    Set to 'False' to bypass Test clean configuration. Clean_config is run
    during Test initialization.
    """
    return _env_get_and_set('BIGROBOT_TEST_CLEAN_CONFIG', new_val, default)


def bigrobot_test_ztn(new_val=None, default='False'):
    """
    Category: Get/set environment variables for BigRobot.
    Set to 'True' if using ZTN setup and tests.
    """
    return _env_get_and_set('BIGROBOT_TEST_ZTN', new_val, default)

def bigrobot_no_auto_reload(new_val=None, default='False'):
    """
    Category: Get/set environment variables for BigRobot.
    Set to 'True' if using ssh Switch handles.
    """
    return _env_get_and_set('BIGROBOT_NO_AUTO_RELOAD', new_val, default)

def bigrobot_ztn_reload(new_val=None, default='False'):
    """
    Category: Get/set environment variables for BigRobot.
    Set to 'True' if using needed reboot of all the switchs with new ZTN controllers.
    """
    return _env_get_and_set('BIGROBOT_ZTN_RELOAD', new_val, default)

def bigrobot_ztn_installer(new_val=None, default='False'):
    """
    Category: Get/set environment variables for BigRobot.
    Set to 'True' if using needed reboot of all the switchs with new ZTN controllers and install Loader.
    """
    return _env_get_and_set('BIGROBOT_ZTN_INSTALLER', new_val, default)

def bigrobot_ha_logging(new_val=None, default='False'):
    """
    Category: Get/set environment variables for BigRobot.
    Set to 'True' if needed extra HA logging to debug HA relates issues during script Runs.
    """
    return _env_get_and_set('BIGROBOT_HA_LOGGING', new_val, default)


def bigrobot_log_archiver(new_val=None, default='qa-tools1.qa.bigswitch.com'):
    """
    Category: Get/set environment variables for BigRobot.
    This is used to archive the postmortem logs.
    """
    return _env_get_and_set('BIGROBOT_LOG_ARCHIVER', new_val, default)


def bigrobot_kvm_server(new_val=None, default='qa-tools3.qa.bigswitch.com'):
    """
    Category: Get/set environment variables for BigRobot.
    This is the default KVM server used by vm_setup and vm_teardown tools.
    """
    return _env_get_and_set('BIGROBOT_KVM_SERVER', new_val, default)


def bigrobot_jenkins_server(new_val=None, default='jenkins.eng.bigswitch.com'):
    """
    Category: Get/set environment variables for BigRobot.
    This is the Jenkins server for Smoketest (Continuous Integration).
    http://qa-tools1.qa.bigswitch.com/regression_logs/
    """
    return _env_get_and_set('BIGROBOT_JENKINS_SERVER', new_val, default)


def bigrobot_test_pause_on_fail(new_val=None, default='False'):
    """
    Category: Get/set environment variables for BigRobot.
    Set to 'True' to pause test case after it had failed.
    """
    return _env_get_and_set('BIGROBOT_TEST_PAUSE_ON_FAIL', new_val, default)


def bigrobot_ignore_mininet_exception_on_close(new_val=None, default='False'):
    """
    Category: Get/set environment variables for BigRobot.
    Set to 'True' to ignore devconf exception when closing Mininet session.
    This knob is added primarily for Smoke Test where we've seen Mininet
    session hanged when session is trying to close (TimeoutException on
    'exit').
    """
    return _env_get_and_set('BIGROBOT_IGNORE_MININET_EXCEPTION_ON_CLOSE',
                            new_val, default)


def bigrobot_preserve_mininet_screen_session_on_fail(new_val=None, default='False'):
    """
    Category: Get/set environment variables for BigRobot.
    Set to 'True' to preserve the Mininet "screen" session. This feature is
    useful for debugging. A user can attach to the screen session at a later
    time.
    """
    return _env_get_and_set('BIGROBOT_PRESERVE_MININET_SCREEN_SESSION_ON_FAIL',
                            new_val, default)


def bigrobot_delete_session_cookies(new_val=None, default='True'):
    """
    Category: Get/set environment variables for BigRobot.
    Set to 'True' to pause test case after it had failed.
    """
    return _env_get_and_set('BIGROBOT_DELETE_SESSION_COOKIES', new_val, default)


def bigrobot_test_suite_status(new_val=None, default=None):
    """
    Category: Get/set environment variables for BigRobot.
    Set to 'PASS' or 'FAIL' by 'Base suite teardown' keyword (defined in
    BsnCommon.py).
    """
    return _env_get_and_set('BIGROBOT_TEST_SUITE_STATUS', new_val, default)


def bigrobot_selenium_browser(new_val=None, default='chrome'):
    """
    Category: Get/set environment variables for BigRobot.
    Specify the browser to use when running Selenium tests. Currently
    supported browsers are:
      chrome
      firefox
    """
    return _env_get_and_set('BIGROBOT_SELENIUM_BROWSER', new_val, default)


def bigtest_path(new_val=None, default=None):
    """
    Category: Get/set environment variables for BigTest.
    """
    return _env_get_and_set('BIGTEST_PATH', new_val, default)


def bigrobot_testbed(new_val=None, default=None):
    """
    Category: Get/set environment variables for BigRobot.
    Set the testbed type. Possible values are:
        'bigtest'
        'libvirt'
        'static'
    - Default is None which assumes attributes are hard coded in .topo file.
    - Dynamic topology support:
      - 'libvirt' and 'static' are nearly identical. 'libvirt' is primarily
        used for virtual testbed whereas 'static' is used for physical testbed.
      - BigRobot no longer requires BigTest testbeds. This is legacy support.
    """
    return _env_get_and_set('BIGROBOT_TESTBED', new_val, default)


def bigrobot_syslog_file(new_val=None, default=None):
    """
    Category: Get/set environment variables for BigRobot.
    """
    return _env_get_and_set('BIGROBOT_SYSLOG_FILE', new_val, default)


def bigrobot_syslog_level(new_val=None, default=None):
    """
    Category: Get/set environment variables for BigRobot.
    """
    return _env_get_and_set('BIGROBOT_SYSLOG_LEVEL', new_val, default)


def bigrobot_reconfig_reauth(new_val=None, default='True'):
    """
    Category: Get/set environment variables for BigRobot.
    Reconfiguration of reauth timeout. If True then reconfigure reauth timeout
    to be longer than the 2 hour default, but in the process it has to restart
    floodlight. In some test scenarios, user may want to disable that by
    setting this value to 'False'.
    """
    return _env_get_and_set('BIGROBOT_RECONFIG_REAUTH',
                            new_val, default)


def bigrobot_reconfig_reauth_sleep_timer(new_val=None, default=30):  # 30 seconds
    """
    Category: Get/set environment variables for BigRobot.
    After reconfiguring reauth timeout which requires re-starting floodlight,
    sleep for a few seconds while floodlight settles down.
    """
    return _env_get_and_set('BIGROBOT_RECONFIG_REAUTH_SLEEP_TIMER',
                            new_val, default)


def bigrobot_monitor_reauth_timer(new_val=None, default=300):  # 5 minutes
    """
    Category: Get/set environment variables for BigRobot.
    Monitor for timer-based tasks to work around BSN reauth timeout. The
    values in seconds.
    """
    return _env_get_and_set('BIGROBOT_MONITOR_REAUTH_TIMER',
                            new_val, default)


def bigrobot_monitor_reauth_init_timer(new_val=None, default=480):  # 8 minutes
    """
    Category: Get/set environment variables for BigRobot.
    Monitor for timer-based tasks to work around BSN reauth timeout. The
    values in seconds.
    The initial time (in seconds) to wait before executing a task for the
    first time.
    """
    return _env_get_and_set('BIGROBOT_MONITOR_REAUTH_INIT_TIMER',
                            new_val, default)


def bigrobot_quiet_output(new_val=None, default=-1):  # disabled
    """
    Category: Get/set environment variables for BigRobot.

    Quiet levels:
      0 - display everything (default)
      1 - suppress command output
      2 - suppress command
      3 - reserved
      4 - reserved
      5 - suppress all output. This is typically used by DevConf library to
          suppresss output when switching modes. Users should avoid this level.

    By default, quiet=0 means that for every command issued, the command and
    its output are captured to the log file. The user can change the quiet
    level when they issue a RestClient or DevConf command. To change the quiet
    level globally, the user can set this environment variable to the value
    0-5. By default, -1 means this env var is disabled.
    """
    return _env_get_and_set('BIGROBOT_QUIET_OUTPUT', new_val, default)


def bigrobot_debug(new_val=None, default=None):
    """
    Category: Get/set environment variables for BigRobot.

    If env BIGROBOT_DEBUG is 1, then enable Robot Framework syslog debugging.
    The syslog settings are:
        Syslog file => <log_path>/syslog.txt
        Syslog level => DEBUG
    """
    _debug = _env_get_and_set('BIGROBOT_DEBUG', new_val, default)
    if int(_debug) == 1:
        bigrobot_syslog_file(default=''.join((bigrobot_log_path_exec_instance(),
                                              '/syslog.txt')))
        bigrobot_syslog_level(default='DEBUG')

    return _debug


def bigrobot_devcmd_write(s, no_timestamp=False):
    """
    Write the device command (CLI or REST command) into a log file.
    """
    if is_gobot():
        if no_timestamp:
            file_write_append_once(bigrobot_devcmd_log(), s)
        else:
            file_write_append_once(bigrobot_devcmd_log(),
                                   ts_logger() + ' ' + s)


def python_path(new_val=None, default=None):
    """
    Category: Get/set environment variables for BigRobot.
    """
    return _env_get_and_set('PYTHONPATH', new_val, default)


def bigrobot_configs_path(config_path='/../configs'):
    return ''.join((get_path_autobot(), config_path))


def _bigrobot_config_load(config_file):
    config_file = bigrobot_configs_path() + config_file
    if file_not_exists(config_file):
        error_exit("Config file '%s' does not exist" % config_file, 1)
    config_dict = load_config(config_file)
    config_dict['this_file'] = config_file
    return config_dict


def bigrobot_config_common():
    return _bigrobot_config_load('/common.yaml')


def bigrobot_config_test_catalog():
    return _bigrobot_config_load('/catalog.yaml')


def bigrobot_config_qa_authors():
    return _bigrobot_config_load('/qa_authors.yaml')


def bigrobot_config_rest_services():
    return _bigrobot_config_load('/rest_services.yaml')


def print_bigrobot_env(minimum=False):
    for env in sorted(bigrobot_env_list()):
        if minimum and env not in ['BIGROBOT_PATH', 'BIGROBOT_LOG_PATH',
                                   'BIGROBOT_SUITE', 'BIGROBOT_TOPOLOGY',
                                   'BIGROBOT_LOG_PATH_EXEC_INSTANCE']:
            continue
        print("%s=%s" % (env, os.environ[env]))
    print("")


def load_config(yaml_file):
    """
    Load a configuration file which is in YAML format. Result is Python dict.
    """
    if file_not_exists(yaml_file):
        environment_failure("File %s does not exist" % yaml_file)
    stream = open(yaml_file, 'r')
    return yaml.load(stream)


def sleep(s):
    """
    Sleep for <s> seconds.
    """
    time.sleep(float(s))


def is_esb():
    return bigrobot_esb().lower() == 'true'


def is_controller(name):
    """
    Controller is defined as c1, c2, master, slave, ...
    """
    match = re.match(r'^(c\d|controller\d?|master|slave)$', name)
    return True if match else False


def is_controller_or_error(name):
    """
    Controller is defined as c1, c2, master, slave, ...
    """
    if not is_controller(name):
        environment_failure("Node must be a controller ('c1', 'c2').")
    else:
        return True


def is_switch(name):
    """
    Switch is defined as s1, s2, s3, spine1, spine2, leaf1, leaf2, ...
    """
    match = re.match(r'^(s\d+|spine\d+|leaf\d+)$', name)
    return True if match else False


def is_host(name):
    """
    Host is defined as h1, h2, h3, ...
    """
    match = re.match(r'^(h\d+)$', name)
    return True if match else False


def is_openstack_server(name):
    """
    OpenStack server is defined as os1, os2, os3, ...
    """
    match = re.match(r'^(os\d+)$', name)
    return True if match else False


def is_mininet(name):
    """
    Mininet is defined as mn, mn1, or mininet
    """
    match = re.match(r'^(mn\d?|mininet\d?)$', name)
    return True if match else False


def is_traffic_generator(name):
    """
    Traffic generator is defined as tg1, tg2, tg3, ...
    """
    match = re.match(r'^(tg\d+)$', name)
    return True if match else False


def is_bvs(name):
    """
    Inspect the platform type for the node. Usage:

    if helpers.is_bvs(n.platform()):
        ...this is a BVS (aka T5) controller...
    """
    return name == 'bvs' or name == 'bcf'


# Alias
is_t5 = is_bvs
is_bcf = is_bvs


def is_bigtap(name):
    """
    Inspect the platform type for the node. Usage:

    if helpers.is_bigtap(n.platform()):
        ...this is a BigTap controller...
    """
    return name == 'bigtap'


def is_bigwire(name):
    """
    Inspect the platform type for the node. Usage:

    if helpers.is_bigwire(n.platform()):
        ...this is a BigWire controller...
    """
    return name == 'bigwire'


def is_switchlight(name):
    """
    Inspect the platform type for the node. Usage:

    if helpers.is_switchlight(n.platform()):
        ...this is a SwitchLight switch...
    """
    return name == 'switchlight'


def is_bsn_controller(name):
    return is_bvs(name) or is_bigtap(name) or is_bigwire(name)


def is_arista(name):
    """
    Inspect the platform type for the node. Usage:

    if helpers.is_arista(n.platform()):
        ...this is an Arista switch...
    """
    return name == 'arista'


def is_extreme(name):
    """
    Inspect the platform type for the node. Usage:

    if helpers.is_extreme(n.platform()):
        ...this is an Extreme switch...
    """
    return name == 'extreme_switch'


def is_ixia(name):
    """
    Inspect the platform type for the node. Usage:

    if helpers.is_traffic_generator(n.platform()):
        ...this is an IXIA box...
    """
    return name == 'ixia'


def is_scalar(data):
    """Verify if the input is a valid Python scalar."""
    return isinstance(data, (type(None), str, int, float, bool))


def is_int(data):
    """Verify if the input is a valid Python integer."""
    return isinstance(data, int)


def is_list(data):
    """Verify if the input is a valid Python list (array)."""
    return isinstance(data, list)


def is_dict(data):
    """Verify if the input is a valid Python dictionary (hash)."""
    return isinstance(data, dict)


def is_str(data):
    """Verify if the input is a valid Python string."""
    return isinstance(data, str)


def is_re_pattern(data):
    """Verify if the input is a valid Python regular expression pattern.
       Matches <type '_sre.SRE_Pattern'>
    """
    SRE_PATTERN_TYPE = type(re.compile(''))
    return type(data) is SRE_PATTERN_TYPE


def is_re_match(data):
    """Verify if the input is a valid Python regular expression match.
       Matches <type '_sre.SRE_Match'>
    """
    SRE_MATCH_TYPE = type(re.match('', ''))
    return type(data) is SRE_MATCH_TYPE


def is_json(data):
    """
    Verify if the input is a valid JSON string.
    """
    try:
        _ = json.loads(data)
    except ValueError:
        return False
    else:
        return True


def from_json(json_str):
    """
    Return Python datatype (dict or array) from JSON string.
    """
    return json.loads(json_str)


def to_json(python_data, is_raw=False):
    """
    Return JSON (pretty) formatted string from Python datatype (dict or array).
    """
    if is_raw:
        return json.dumps(python_data, sort_keys=True)
    else:
        return json.dumps(python_data, indent=4, sort_keys=True)


def in_list(_list, element, case_sensitive=False):
    """
    Return True if element is in the list and False it it isn't.
    By default, ignore case when comparing values.
    """
    if case_sensitive:
        if element in _list:
            return True
    else:
        if element.lower() in [x.lower() for x in _list]:
            return True
    return False


def unicode_to_ascii(u):
    """
    Convert a Unicode string to an ASCII string.
    """
    return unicodedata.normalize('NFKD', u).encode('ascii', 'ignore')


def from_yaml(yaml_str):
    """
    Convert a YAML-formatted string to Python dict.
    """
    return yaml.load(yaml_str)


def to_yaml(data):
    """
    Convert a Python dict to YAML-formatted string.
    """
    return yaml.dump(data)


def re_pattern_str(data):
    """
    Convert a regular expression pattern to readable value (string).
    Matches <type '_sre.SRE_Pattern'>
    """
    if is_re_pattern(data):
        return data.pattern
    else:
        environment_failure("'%s' is not a regex pattern" % data)


def re_match_str(data):
    """
    Convert a regular expression match to readable value (string).
    Matches <type '_sre.SRE_Match'>
    """
    if is_re_match(data):
        s = data.group()
        s = s.replace('\n', "\\n")
        s = s.replace('\r', "\\r")
        return s
    else:
        environment_failure("'%s' is not a regex match" % data)


def get(var, default):
    """
    Return var if is True/non-zero/non-empty. Else return default.
    This is similar to dictionary's get() method.
    """
    return var if var else default


def get_path(filename):
    """
    Extract the path from the filename.
    """
    return os.path.dirname(filename)


def get_path_autobot():
    """
    Extract the path of the Autobot module.
    """
    import autobot
    return get_path(autobot.__file__)


def create_uuid():
    """
    Create a UUID based on the host ID and current time.
    """
    return str(uuid.uuid1())


def set_unique(a):
    """
    Return list with duplicate elements removed.
    """
    return list(set(a))


def set_intersection(a, b):
    """
    Return list which is the intersection of two lists.
    """
    return list(set(a) & set(b))


def set_union(a, b):
    """
    Return list which is the union of two lists.
    """
    return list(set(a) | set(b))


def ds():
    """
    Return the current datestamp, e.g., 20130926.
    """
    t = datetime.datetime.now(_TZ)

    # UTC time would return '2013-10-30T07:40:53z' whereas the following
    # returns '2013-10-30T00:40:53z' (PST)
    return t.strftime("%Y%m%d")


def ts():
    """
    Return the current timestamp in UTC time (string format),
    e.g., 20130926_155749
    """
    utc_datetime = datetime.datetime.utcnow()
    return utc_datetime.strftime("%Y%m%d_%H%M%S")


def ts_local():
    """
    Return the current timestamp in local time (string format),
    e.g., 20130926_155749
    """
    local_datetime = datetime.datetime.now(_TZ)
    return local_datetime.strftime("%Y%m%d_%H%M%S")


def ts_long():
    """
    Return the current timestamp in UTC time (string format),
    e.g., 2013-09-26T15:57:49.123Z
    """
    utc_datetime = datetime.datetime.utcnow()
    return utc_datetime.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + 'Z'


def ts_long_local():
    """
    Return the current timestamp in local time (string format),
    e.g., 2013-09-26T15:57:49.123
    """
    local_datetime = datetime.datetime.now(_TZ)
    return local_datetime.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]


def ts_logger():
    """
    Return the current timestamp in local time (string format which is
    compatible with the Robot Framework logger format)
    e.g., 20140429 15:01:51.039
    """
    local_datetime = datetime.datetime.now(_TZ)
    return local_datetime.strftime("%Y%m%d %H:%M:%S.%f")[:-3]


def time_now():
    """
    Return the current time.
    """
    return time.time()


def week_num():
    """
    Return the week number.
    """
    return datetime.datetime.now().isocalendar()[1]


def year():
    """
    Return the year.
    """
    return datetime.date.today().year


def month():
    """
    Return the month.
    """
    return datetime.date.today().month


def day():
    """
    Return the day's number.
    """
    return datetime.date.today().day


def format_robot_timestamp(timestamp, is_datestamp=False):
    """
    Robot Framework records the local time uses the following timestamp format:
        20140523 16:49:38.051
    Convert it to local ISO time format:
        2014-05-23T16:49:38.051
    """
    match = re.match(r'(\d{4})(\d{2})(\d{2})\s+(\d+):(\d+):(\d+)\.(\d+)$',
                     timestamp)
    if not match:
        environment_failure("Incorrect time format: '%s'" % timestamp)
    (year, month, date, hour, minute, sec, msec) = match.groups()
    # hour = int(hour) + 7  # change PST to UTC
    if is_datestamp:
        s = '%s-%s-%s' % (year, month, date)
    else:
        s = '%s-%s-%sT%s:%s:%s.%s' % (year, month, date,
                                      hour, minute, sec, msec)
    return s


def format_robot_datestamp(timestamp):
    return format_robot_timestamp(timestamp, is_datestamp=True)


#
# String processing helpers
#


def file_exists(filename):
    """
    Does the file exist?
    """

    # os.path.exists doesn't detect stale symlinks (link to non-existent
    # file), so also need to check if file is a symlink
    return os.path.exists(filename) or os.path.islink(filename)


def file_not_exists(f):
    if f is None:
        return True
    if not file_exists(f):
        return True
    return False


def file_not_empty(f):
    if os.path.isfile(f) and os.path.getsize(f) > 0:
        return True
    else:
        return False


def file_rename(old_name, new_name):
    """
    Rename a file from old_name to new_name.
    """
    os.rename(old_name, new_name)


def file_remove(filename):
    """
    Remove/delete a file.
    """
    if file_exists(filename):
        os.remove(filename)


def file_cat(filename):
    """
    Behaves like the Unix 'cat' - concatenate and print file.
    Reads a file and prints it to stdout.
    """
    s = file_read_once(filename)
    print(s)


def file_read_once(filename, to_list=False):
    """
    Read file in a single shot. Immediately close file.
    Returns a string.
    """
    f = open(filename, 'r')
    lines = f.readlines()
    f.close()
    if to_list:
        return lines
    else:
        s = ''.join(lines)
        return s


def file_write_once(filename, s):
    """
    Write string to file in a single shot. Immediately close file.
    """
    f = open(filename, 'w')
    f.write(s)
    f.close()


def file_write_append_once(filename, s):
    """
    Write (append) string to file in a single shot. Immediately close file.
    """
    f = open(filename, 'a')
    f.write(s)
    f.close()


def file_touch(fname, times=None):
    """
    Like Unix 'touch' command.
    Borrowed from
    http://stackoverflow.com/questions/1158076/implement-touch-using-python
    times=None will set access and modified times to the current time
    """
    with file(fname, 'a'):
        os.utime(fname, times)


def file_copy(src, dst):
    """
    Copy source file to destination file.
    """
    shutil.copyfile(src, dst)


def is_same_file(file1, file2):
    """
    Check if file1 is the same file as file2 by comparing their inodes. This
    gets us around the issue of 'debug.txt' != './debug.txt"
    """
    if not file_exists(file1) or not file_exists(file2):
        return False
    inode1 = os.stat(file1)[1]
    inode2 = os.stat(file2)[1]

    return True if inode1 == inode2 else False


def mkdir_p(path):
    """
    Works like 'mkdir -p' (create intermediate directories as required.
    Borrowed from
    http://stackoverflow.com/questions/600268/mkdir-p-functionality-in-python
    """
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise


def dict_merge(dict1, dict2):
    """
    Merge dict1 and dict2. If there are common keys, dict2 will overwrite
    dict1. Return the merged dict.
    """
    return dict(dict1.items() + dict2.items())


def matched(val, match_list):
    if not is_list(match_list):
        match_list = [match_list]
    return int(val) in match_list


def not_matched(val, match_list):
    return not matched(val, match_list)


def not_quiet(val, quiet_levels):
    """
    Return True if val matches one of the quiet levels (list).
    """
    if val == 5:
        # 5 - Suppress all output, is typically specified by DevConf
        # to hide the details when mode switching, which can be quiet verbose.
        # So if 5 is specified, we should not override it.
        pass
    elif int(bigrobot_quiet_output()) != -1:
        val = int(bigrobot_quiet_output())
    return not_matched(val, quiet_levels)


def dict_compare(dict1, dict2, ignore_keys=None):
    """
    Compare to see whether dict1 is the same as dict2. You can provide a list
    of keys to ignore in the comparison.

    Usage:
    status = helpers.dict_compare(mydict1, mydict2, ignore_keys=['abc', 'xyz'])

    Return
       - True  if dictionaries are same
       - False if dictionaries are different
    """

    keys1 = sorted(dict1.keys())
    keys2 = sorted(dict2.keys())
    combined_keys = keys1 + list(set(keys2) - set(keys1))

    ignore = []
    if ignore_keys:
        if is_scalar(ignore_keys):
            ignore.append(ignore_keys)
        else:
            ignore = ignore_keys

    for k in combined_keys:
        if k in ignore:
            print "Ignoring key '%s'" % k
            continue

        if k in dict1 and k in dict2:
            if dict1[k] == dict2[k]:
                pass
            else:
                print "Dictionaries differ at key '%s'" % k
                return False
        elif k in dict1:
            print "First dictionary contains key '%s'" % k
            return False
        else:
            print "Second dictionary contains key '%s'" % k
            return False
    return True


def list_compare(list1, list2):
    """
    Compare to see whether list1 is the same as list2.
    Return
       - True  if lists are same
       - False if lists are different
    """
    list1 = sorted(list1)
    list2 = sorted(list2)

    if len(list1) != len(list2):
        debug("Lists are not the same - lengths are different")
        return False

    for i, _ in enumerate(list1):
        if list1[i] != list2[i]:
            debug("Lists are not the same - list1[%s]('%s') != list2[%s]('%s')"
                  % (i, list1[i], i, list2[i]))
            return False

    return True


def list_flatten(alist):
    """
    Given a list, such as [0, 1, 2, [3, 4, 5], 6, [7, 8]], flatten it.
    Caveat: It only flattens one level... for now...

    Return
       - New list (flattened)
    """
    if not is_list(alist):
        return alist

    # Else we're dealing with a list...
    result = []
    for entry in alist:
        if is_list(entry):
            _ = [result.append(i) for i in entry]
        else:
            result.append(entry)
    return result


def bigtest_node_info():
    """
    Traverse the directory /var/run/bigtest and gather all the node attributes
    which were created by BigTest.
    """

    my_root = '/var/run/bigtest'

    if not os.path.exists(my_root):
        error_exit('Directory %s does not exist.' % my_root)

    nodes = {}
    for root, _, files in os.walk(my_root):
        if root == my_root:
            # Ignore top-level root
            continue

        node = os.path.basename(root)
        nodes[node] = {}

        for filename in files:
            full_path_filename = "%s/%s/%s" % (my_root, node, filename)
            val = open(full_path_filename, "r").read().rstrip()
            nodes[node][filename] = val

    if not nodes:
        error_exit('Directory %s appears to be empty.' % my_root)

    return nodes


def int_to_str(val):
    """
    Check value - if type is integer then convert to string and return string.
    """
    if isinstance(val, int):
        val = str(val)
    return val


def str_to_int(val):
    """
    Check value - if type is string then convert to integer and return integer.
    """
    if isinstance(val, basestring):
        val = int(val)
    return val


def utf8(unicode_val):
    """
    Input can be a single or a list of Unicode strings. Return the converted
    values.
    """
    if is_list(unicode_val):
        new_list = []
        for x in unicode_val:
            new_list.append(x.encode('utf-8'))
        return new_list
    else:
        return unicode_val.encode('utf-8')


def _createSSHClient(server, user, password, port=22):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(server, port, user, password)
    return client


def scp_put(server, local_file, remote_path,
            user=None, password=None, recursive=True):
    """
    Example:
        helpers.scp_put(c.ip(),
                        local_file='/etc/hosts',
                        remote_path='/tmp/12345/1234')
    Limitations: Does not support wildcards.
    """

    if not user:
        error_exit("Need to specify user name")
    if not password:
        error_exit("Need to specify user password")

    ssh = _createSSHClient(server, user, password)
    s = SCPClient(ssh.get_transport())

    # !!! FIXME: Catch conditions where file/path are not found
    # log("scp put local_file=%s remote_path=%s" % (local_file, remote_path))
    log("SSH copy source (%s) to destination (%s) " % (local_file, remote_path))
    s.put(local_file, remote_path, recursive=recursive)


def scp_get(server, remote_file, local_path,
            user='admin', password='adminadmin', recursive=True):
    """
    Example:
        helpers.scp_get(c.ip(),
                        remote_file='/var/log',
                        local_path='/tmp',
                        user='recovery',
                        password='bsn')

    Limitations: Does not support wildcards.
    """
    if not user:
        error_exit("Need to specify user name")
    if not password:
        error_exit("Need to specify user password")

    ssh = _createSSHClient(server, user, password)
    s = SCPClient(ssh.get_transport())

    # !!! FIXME: Catch conditions where file/path are not found
    # log("scp put remote_file=%s local_path=%s" % (remote_file, local_path))
    log("SSH copy source (%s) to destination (%s) " % (remote_file, local_path))
    s.get(remote_file, local_path, recursive=recursive)


def run_cmd(cmd, cwd=None, ignore_stderr=False, shell=True, quiet=False):
    """
    NOTE: Consider using run_cmd2() instead.

    shell - Just pass the command string for execution in a subshell. This is
            ideal when command should run in the background (string can include
            '&') and/or command contains shell variables/wildcards.

    Returns tuple (Boolean, String)
        success: (True,  "...success message...")
        failure: (False, "...error message...")
    """
    if not quiet:
        log("Executing '%s'" % cmd)

    if shell:
        # In general, should avoid shell mode. The command output will go
        # straight to stdout/stderr and are not redirected.
        p = subprocess.call(cmd, shell=True)
        return (True, None)
    else:
        cmd_list = cmd.split(' ')
        p = subprocess.Popen(cmd_list,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, cwd=cwd)
        out, err = p.communicate()
        if err and not ignore_stderr:
            return (False, err)

        return (True, out)


def run_cmd2(cmd, ignore_stderr=False, cwd=None, shell=True, quiet=False):
    """
    shell - Just pass the command string for execution in a subshell. This is
            ideal when command should run in the background (string can include
            '&') and/or command contains shell variables/wildcards.

    In this version of run_cmd, the shell and non-shell modes are near
    identical, resulting in more consistent behavior. Need to gradually phase
    out the old run_cmd usage.

    Returns tuple (Boolean, String, String, Integer)
        success: (True,  "command_output", "error_msg", <errorcode>)
        failure: (False, "command_output', "error_msg", <errorcode>)
    """
    if not quiet:
        log("Executing '%s'" % cmd)
    if shell:
        # In general, should avoid shell mode due to security reasons.
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, shell=True)
    else:
        cmd_list = cmd.split(' ')
        p = subprocess.Popen(cmd_list,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, cwd=cwd)
    out, err = p.communicate()
    error_code = p.returncode
    status = True
    if error_code and not ignore_stderr:
        status = False
    return (status, out, err, error_code)


def user_id():
    """
    Dump output from 'id'.
    """
    _, output, _, _ = run_cmd2('id', shell=False, quiet=True)
    return output.strip()


def uname():
    """
    Dump output from 'uname -a'.
    """
    _, output, _, _ = run_cmd2('uname -a', shell=False, quiet=True)
    return output.strip()


def ulimit():
    """
    Dump output from 'ulimit -a'.
    Note: On Mac OS X, ulimit is in /usr/bin. On Linux (Ubuntu), it's a
    built-in shell command. So let's execute it using shell mode.
    """
    _, output, _, _ = run_cmd2('ulimit -a', shell=True, quiet=True)
    return output.strip()


def uptime():
    """
    Dump output from 'uptime'.
    """
    _, output, _, _ = run_cmd2('uptime', shell=False, quiet=True)
    return output.strip()


def _run_ping_cmd(host, count=10, timeout=None, quiet=False, source_if=None,
          record_route=False, node_handle=None, mode=None, ttl=None,
          interval=0.4, ping_output=None, background=False, label=None):
    if background:
        if node_handle == None or mode != 'bash':
            test_error("Background ping is only support for bash mode")
        if label == None:
            test_error("You must provide a unique label (string) for background ping")
        count = None

    if count == None or int(count) == -1:  # disable count
        cmd = "ping"
    else:
        cmd = "ping -c %s" % count
    if source_if:
        cmd = "%s -I %s" % (cmd, source_if)
    if record_route:
        cmd = "%s -R" % (cmd)
    if interval:
        # Mac OS X < 13 (Maverick) requires minimum interval of 1 second.
        if (platform.system() == 'Darwin' and
            int(platform.release().split('.')[0]) < 13):
            interval = 1
        if float(interval) < 0.2:
            test_error("Ping interval cannot be less than 0.2 seconds.")
        cmd = "%s -i %s" % (cmd, interval)

    # Ping initiated from the staging machine (likely is your MacBook)
    if not node_handle and platform.system() == 'Darwin':
        # MacOS X platform
        if ttl:
            cmd = "%s -T %s" % (cmd, ttl)
        if timeout:
            cmd = "%s -t %s" % (cmd, timeout)
    else:
        # Linux platform
        if ttl:
            cmd = "%s -t %s" % (cmd, ttl)
        if timeout:
            cmd = "%s -w %s" % (cmd, timeout)

    cmd = "%s %s" % (cmd, host)

    prefix_str = 'bigrobot'
    bigrobot_devcmd_write("%-9s: %s\n" % (prefix_str, cmd))

    if not node_handle:
        if not quiet:
            log("Ping command: %s" % cmd, level=4)
        _, ping_output = run_cmd(cmd, shell=False, quiet=True,
                                 ignore_stderr=True)
    else:
        if mode == 'bash':
            if not quiet:
                log("Ping command: %s" % cmd, level=4)
            if background:
                output_file = '/tmp/ping_background_output.%s.log' % label
                node_handle.bash("rm -f %s" % output_file)
                result = node_handle.bash(cmd + " > " + output_file + " &")
                pid = str_to_list(node_handle.bash("echo $!")['content'])[1]
                log("Ping is running in the background. PID=%s" % pid)
                node_handle.bash("echo %s > %s" % (pid, output_file + ".pid"))

                return pid
            else:
                result = node_handle.bash(cmd)
                ping_output = result["content"]

        elif mode == 'cli':
            # Ping command on Controller is very basic. It doesn't support
            # any option besides count.

            cmd = "ping"
            if is_bcf(node_handle.platform()) or is_bigtap(node_handle.platform()):
                if source_if:
                    test_error("source_if option not supported for controller CLI ping.")
                if count == None or int(count) == -1:  # disable count
                    pass
                else:
                    cmd = "%s count %s" % (cmd, count)

            cmd = "%s %s" % (cmd, host)
            if not quiet:
                log("Ping command: %s" % cmd, level=4)
            result = node_handle.cli(cmd)
            ping_output = result["content"]
        else:
            test_error("Unknown mode '%s'. Only 'bash' or 'cli' supported."
                       % mode)
    return ping_output


def _ping(*args, **kwargs):
    """
    Ping options:
      :param host: (Str) ping this host
      :param count : (Int) number of packets to send, equivalent to -c <counter>
                      If count is -1 or None, disable count.
                      If background is specified, disable count.
      :param source_inf : -I <interface>
      :param record_route : -R
      :param ttl : -t <ttl> (on Linux), -T <ttl> (on Mac OS X)
      :param timeout : (Int) time in seconds to wait for a reply, equivalent
             to -w <timeout> (on Linux), -t <timeout> (on Mac OS X)
      :param interval : (Real) time in seconds to wait between sending packets.
             equivalent to -i <wait>. Interval value less than 0.2 will
             trigger an error (not supported).
      :param ping_output : (Str) if specified, assuming ping action happened
             as a separate activity and simply process the ping output.

    Return value:
      { "packets_sent": nnn,
        "packets_received": nnn,
        "packets_loss": nnn,
        "packets_loss_percentage": nnn,
        "background_ping_output" = abc
      }

    See also Host.bash_ping() to see how to use ping as a BigRobot keyword.
    """

    if args:
        host = args[0]
    else:
        host = kwargs.get('host')
    output = kwargs.get('ping_output', None)
    if output == None:
        output = _run_ping_cmd(*args, **kwargs)

    if kwargs.get('background'):
        return {"background_ping_output": output}

    if not kwargs.get('quiet'):
        log("Ping output:\n%s" % output, level=4)

    # Linux output:
    #   3 packets transmitted, 3 received, 0% packet loss, time 2003ms
    #   3 packets transmitted, 0 received, +3 errors, 100% packet loss, time 2014ms
    #       This is when ping failed with 'ping -c 3 -w 4 -I eth0 101.195.0.131'
    #
    # Mac OS X output:
    #   3 packets transmitted, 3 packets received, 0.0% packet loss
    #
    # BigSwitch controller output:
    #   localhost> ping qa-kvm-32
    #   PING qa-kvm-32.bigswitch.com (10.192.88.32) 56(84) bytes of data.
    #   64 bytes from qa-kvm-32.bigswitch.com (10.192.88.32): icmp_req=1 ttl=64 time=16.1 ms
    #   64 bytes from qa-kvm-32.bigswitch.com (10.192.88.32): icmp_req=2 ttl=64 time=0.550 ms
    #   64 bytes from qa-kvm-32.bigswitch.com (10.192.88.32): icmp_req=3 ttl=64 time=0.548 ms
    #   64 bytes from qa-kvm-32.bigswitch.com (10.192.88.32): icmp_req=4 ttl=64 time=0.512 ms
    #   64 bytes from qa-kvm-32.bigswitch.com (10.192.88.32): icmp_req=5 ttl=64 time=0.540 ms
    #
    #   --- qa-kvm-32.bigswitch.com ping statistics ---
    #   5 packets transmitted, 5 received, 0% packet loss, time 4007ms
    #   rtt min/avg/max/mdev = 0.512/3.669/16.196/6.263 ms

    if kwargs.get('source_if'):
        match = re.search(r'ping: unknown iface (\w+)',
                          output,
                          re.M | re.I)
        if match:
            test_error("Ping error - unknown source interface '%s'"
                       % match.group(1))

    match = re.search(r'.*?(\d+) packets transmitted, (\d+)( packets)? received, .*?(\d+\.?(\d+)?)% packet loss.*',
                      output,
                      re.M | re.I)
    if match:
        packets_sent = int(match.group(1))
        packets_received = int(match.group(2))
        loss_pct = int(float(match.group(4)))
        s = ("Ping host '%s' - %d transmitted, %d received, %d%% loss"
             % (host, packets_sent, packets_received,
                loss_pct))

        calculated_loss_pct = int((float(packets_sent) -
                                   float(packets_received))
                                  / float(packets_sent) * 100.0)
        if calculated_loss_pct != loss_pct:
            warn("Reported ping loss%% (%s) does not equal calculated %% (%s)"
                 % (loss_pct, calculated_loss_pct))

        log("Ping result: %s%s"
            % (s, br_utils.end_of_output_marker()), level=4)
        return {
                "packets_sent": packets_sent,
                "packets_received": packets_received,
                "packets_loss": packets_sent - packets_received,
                "packets_loss_pct": calculated_loss_pct
                }

    if re.search(r'no route to host', output, re.M | re.I):
        test_error("Ping error - no route to host")

    test_error("Unknown ping error. Please check the output log.")


def ping(host=None, count=10, timeout=None, loss=0, ping_output=None,
         quiet=False, return_stats=False):
    """
    Unix ping. See _ping() for a complete list of options.
    Additional arguments:

    :param loss: (Int) allowable loss percentage

    Return:
      - (Int) loss percentage, by default
      - Stats dict if return_stats is True
    """
    if ping_output == None and host == None:
        test_error("Must specify a host to ping")
    if count < 4:
        count = 4  # minimum count

    stats = _ping(host=host, count=count, timeout=timeout,
                  ping_output=ping_output, quiet=quiet)
    if stats["packets_loss_pct"] > loss:
        stats = _ping(host=host, count=count, timeout=timeout,
                      ping_output=ping_output, quiet=quiet)
        if stats["packets_loss_pct"] > loss:
            count -= 4
            stats = _ping(host=host, count=count, timeout=timeout,
                          ping_output=ping_output, quiet=quiet)
    if return_stats:
        return stats
    else:
        return stats["packets_loss_pct"]


def params_val(k, params_dict):
    """
    If key is found in Params dictionary then return its value, else return
    None.
    """
    if k in params_dict:
        return params_dict[k]
    else:
        return None


def params_is_true(k, params_dict):
    val = params_val(k, params_dict)
    if val is True:
        return True
    else:
        return False


def params_is_false(k, params_dict):
    val = params_val(k, params_dict)
    if val is False:
        return True
    else:
        return False


def params_to_file(params_dict, path='/tmp', prefix='bigrobot_params_',
                   suffix='.topo'):
    """
    Write the params structure (dict) to a YAML file.
    Return the file name.
    """
    yaml_str = to_yaml(params_dict) if is_dict(params_dict) else params_dict
    _, filename = tempfile.mkstemp(prefix=prefix, suffix=suffix, dir=path)
    os.chmod(filename, 0644)  # Fix default permission from 600 - read/write by user only
    file_write_once(filename, yaml_str)
    return filename


def snake_case_key(in_dict):
    """
    Convert the keys in a dictionary to snake case. It also supports nested
    dictionaries.
    """
    out_dict = {}
    for k, v in in_dict.iteritems():
        new_key = k.lower()
        new_key = new_key.replace (" ", "_")
        if is_dict(v):
            v = snake_case_key(v)
        out_dict[new_key] = v
    return out_dict


def send_mail(m, infile=None):
    """
    m data structure contains:
      from: <sender>
      to: <comma-separated list of receivers>
      subject: <subject>
      message_body: <content>

    Usage:
        helpers.send_mail( {
                'from': 'vui.le@bigswitch.com',
                'to': 'vui.le@bigswitch.com',
                'subject': 'Emergency system test',
                'message_body': 'This is only a test',
                } )
    """
    _to = [utf8(x) for x in split_and_strip(m['to'])]
    s = smtplib.SMTP(SMTP_SERVER)
    s.set_debuglevel(debug)

    if infile:
        input_text = file_read_once(infile)
        if len(input_text) > 100000:
            lines = 200
            input_text = ("... Attention: File is greater than 100K bytes."
                          " Send the last %s lines of file ...\n\n"
                          % lines + '\n'.join(str_to_list(input_text)[-lines:]))
        m['message_body'] += "\n\n<<<File: %s>>>\n" % infile + input_text

    msg = MIMEText(m['message_body'])
    msg['Subject'] = m['subject']
    msg['From'] = m['from']
    msg['To'] = m['to']
    s.sendmail(m['from'], _to, msg.as_string())
    s.quit()


def params_dot_notation_to_dict(params):
    """
    Convert a list of strings representing parameter inputs (in dot
    notation) into a dictionary.

    :param params: List of strings as

    E.g.,
    Input:
      params=['common.user_switch_image=/etc/hosts',
              'common.user_abc.groupA=123',
              'common.user_abc.groupB=999',
              'common.user_abc.groupC=555',
              'common.user_abc.groupD.name=Larry']
    will produce the following output dictionary:
      {'common': {'user_abc': {'groupA': '123',
                               'groupB': '999',
                               'groupC': '555',
                               'groupD': {'name': 'Larry'}},
                  'user_switch_image': '/etc/hosts'}}
    """
    new_dict = {}
    for param in params:
        keys = param.split('.', 1)
        keys[-1], value = keys[-1].split('=', 1)
        ref = new_dict
        key_counter = 1
        for key in keys:
            if key_counter < len(keys):
                if not key in ref:
                    ref[key] = {}
                ref = ref[key]
                key_counter += 1
            else:
                ref[key] = value
    return new_dict


def openstack_convert_table_to_dict(input_str):
    """
    Many commands on OpenStack Nova controller will return a table output,
    e.g.,

    root@nova-controller:~# nova --os-username admin \
                                 --os-tenant-name admin \
                                 --os-auth-url http://10.193.0.120:5000/v2.0/ \
                                 --os-password bsn
                                 image-show  Ubuntu.13.10

        +----------------------+--------------------------------------+
        | Property             | Value                                |
        +----------------------+--------------------------------------+
        | status               | ACTIVE                               |
        | updated              | 2014-01-03T06:51:26Z                 |
        | name                 | Ubuntu.13.10                         |
        | created              | 2014-01-03T06:50:55Z                 |
        | minDisk              | 0                                    |
        | progress             | 100                                  |
        | minRam               | 0                                    |
        | OS-EXT-IMG-SIZE:size | 243662848                            |
        | id                   | 8caae5ae-66dd-4ee1-87f8-08674da401ff |
        +----------------------+--------------------------------------+

    This function converts the table to a Python dictionary-of-dictionaries.
    Each field in the first column is used as a dictionary keys which points
    to a dictionary containing values from the other columns. E.g.,

    { 'OS-EXT-IMG-SIZE:size':
                  {'property': 'OS-EXT-IMG-SIZE:size', 'value': '243662848'},
      'created':  {'property': 'created',  'value': '2014-01-03T06:50:55Z'},
      'id':       {'property': 'id',       'value': '8caae5ae-66dd-4ee1-...'},
      'minDisk':  {'property': 'minDisk',  'value': '0'},
      'minRam':   {'property': 'minRam',   'value': '0'},
      'name':     {'property': 'name',     'value': 'Ubuntu.13.10'},
      'progress': {'property': 'progress', 'value': '100'},
      'status':   {'property': 'status',   'value': 'ACTIVE'},
      'updated':  {'property': 'updated',  'value': '2014-01-03T06:51:26Z'}
    }

    Return dictionary.
    """
    if is_list(input_str):
        out = input_str
    elif is_str(input_str):
        out = input_str.split('\n')
    else:
        test_error("Input must be a string or a list")

    out = br_utils.strip_empty_lines(out)
    out = br_utils.strip_cruds_before_table_begins(out)
    out = br_utils.strip_cruds_after_table_ends(out)
    out = br_utils.strip_table_row_dividers(out)
    out = br_utils.strip_table_ws_between_columns(out)
    out = br_utils.convert_table_to_dict(out)

    return out


def openstack_replace_text_marker(input_file, output_file, line_marker,
                                  line_marker_end, append_string):
    """
    Takes an input file and search for a marker, such as '[filter:authtoken]',
    then remove the marker and all subsequent lines in the file until
    the line_marker_end is hit. A sample line_marker_end is '[filter:gzip]'.

    Usage:

    append_str = '''
    [filter:authtoken]
    paste.filter_factory = keystoneclient.middleware.auth_token:filter_factory
    delay_auth_decision = true
    auth_host = 10.193.0.120
    auth_port = 35357
    auth_protocol = http
    admin_tenant_name = service
    admin_user = glance
    '''
    helpers.openstack_replace_text_marker(
              input_file='/tmp/glance-api-paste.ini',
              output_file='/tmp/new-glance-api-paste.ini',
              line_marker=r'^\[filter:authtoken\]',
              line_marker_end=r'^\[.+',
              append_string=append_str)
    """
    line_marker = line_marker.strip()
    line_marker_end = line_marker_end.strip()
    s = file_read_once(input_file)
    lines = s.split("\n")
    ignore_line = False
    new_lines = []
    for line in lines:
        line = line.strip()
        if re.search(line_marker, line):
            log("matched line_marker: %s" % line_marker)
            ignore_line = True
        elif ignore_line and re.search(line_marker_end, line):
            log("matched line_marker_end: %s" % line_marker_end)
            ignore_line = False
        if not ignore_line:
            new_lines.append(line)
        else:
            log("Ignoring: %s" % line)
    new_str = '\n'.join(new_lines) + '\n' + append_string
    file_write_once(output_file, new_str)
    return new_str


def text_processing_str_remove_header(input_str, n):
    """
    Given a multi-line string, remove the first <n> lines.
    """
    lines = input_str.split("\n")
    return '\n'.join(lines[n:])


def text_processing_str_remove_trailer(input_str, n):
    """
    Given a multi-line string, remove the trailing <n> lines.
    """
    lines = input_str.split("\n")
    return '\n'.join(lines[:-n])


def str_to_list(input_str):
    """
    Convert a multi-line string into a list of strings.
    """
    return input_str.splitlines()


def indent_str(input_str, spaces='    '):
    """
    Indent a multi-lined string by the amount of spaces specified.
    """
    input_str = str(input_str)  # make sure we're dealing with a string
    lines = str_to_list(input_str)
    new_lines = []
    for line in lines:
        new_lines.append(spaces + line)
    return "\n".join(new_lines)


def split_and_strip(input_str, split_str=','):
    """
    Split a string (default split character is ',') and remove surrounding
    whitespaces.
    """
    return [x.strip() for x in input_str.split(split_str)]


def strip_ctrl_chars(string):
    # Strip control chars, such as
    #   \x07 - ^G - Bell
    return re.sub(r'[\x07]', '', string)


def strip_cli_output(input_str, to_list=False):
    """
    The convention from the expect library (Exscript) is as followed:
      - first line contains the issued command
      - last line contains the device prompt
    This function strips the first and last line, leaving the actual output.

    Returns:
      - a multi-line string by default
      - a list of strings, if to_list=True
    """
    out = text_processing_str_remove_header(input_str, 1)
    out = text_processing_str_remove_trailer(out, 1)
    if to_list:
        return str_to_list(out)
    else:
        return out


def text_processing_str_remove_to_end(input_str, line_marker):
    """
    Given a multi-line string, find the input marker and remove the content
    to end of string.

    Usage:

    input_str = '''
    Manufacturer: Quanta
    Model: LY2
    Uptime is 2:53:22
    Load average:  0.24 0.17 0.15
    '''
    out = helpers.text_processing_str_remove_to_end(input_str,
                                                    line_marker=r'^Uptime is')

    Returns:

    Manufacturer: Quanta
    Model: LY2

    """
    lines = input_str.split("\n")
    for i, line in enumerate(lines):
        if re.search(line_marker, line):
            break
    return '\n'.join(lines[:i])


def regex_bvs():
    # return r'Big Virtual Switch Appliance.*[\r\n]'
    return r'Big (Virtual Switch|Cloud Fabric) Appliance.*[\r\n]'


#
# Network-related helpers
#

def ip_range(subnet, first=None, last=None):
    """
    :param subnet: (str) The IP subnet, e.g., '192.168.1.1/24'
    :param first:  (str) [Optional] The first IP address in range
    :param last:   (str) [Optional] The last IP address in range
    """
    subnet_list = [str(ip) for ip in ipcalc.Network(subnet)]

    first_index, last_index = None, None
    if first:
        first_index = subnet_list.index(first)
    if last:
        last_index = subnet_list.index(last) + 1

    if first_index is None and last_index is None:
        return subnet_list
    if last_index is None:
        return subnet_list[first_index:]

    return subnet_list[first_index:last_index]


def ip_range_byte_mod(self, subnet, first=None, last=None, byte=None):
    """
    :param byte: (str) [Optional] The byte field in the IP address to
            modify in addition to the 4th bite field.

    IP address anatomy:
      <byte1>.<byte2>.<byte3>.<byte4>

    This is intended for testing TCAM optimization (per MingTao). In
    addition to changing the host byte (4th byte) of the IP address, we
    want to change a network byte as well, such as the 2nd or 3rd byte of
    the IP address.
    """
    subnet_list = ip_range(subnet, first, last)

    # Convert byte value to integer
    if byte:
        byte = int(byte)

    if byte in (None, 4):
        return subnet_list

    if byte not in (1, 2, 3):
        test_error("Error: Can only modify 1st, 2nd, or 3rd byte in IP address.")

    new_subnet_list = []
    for ip in subnet_list:
        byte_list = ip.split('.')
        byte_list[byte - 1] = byte_list[3]
        new_subnet_list.append('.'.join(byte_list))

    return new_subnet_list


def get_next_mac(base, incr):
    """
    Contributor: Mingtao Yang
    Objective:
    - Generate the next mac/physical address based on the base and step.

    Inputs:
      | base | starting mac address |
      | incr | Value by which we will increment the mac/physical address |

    Usage:
      | macAddr = self.get_next_mac(base,incr) |
    """

    log("the base address is: %s,  the step is: %s,  "
        % (str(base), str(incr)))

    mac = base.split(":")
    step = incr.split(":")
    log("MAC list is %s" % mac)

    hexmac = []

    for index in range(5, 0, -1):
        mac[index] = int(mac[index], 16) + int(step[index], 16)
        mac[index] = hex(mac[index])
        temp = mac[index]
        if int(temp, 16) >= 256:
            mac[index] = hex(0)
            mac[index - 1] = int(mac[index - 1], 16) + 1
            mac[index - 1] = hex(mac[index - 1])

    mac[0] = int(mac[0], 16) + int(step[0], 16)
    mac[0] = hex(mac[0])

    temp = mac[0]
    if int(temp, 16) >= 256:
        mac[0] = hex(0)

    for i in range(0, 6):
        hexmac.append('{0:02x}'.format(int(mac[i], 16)))
    macAddr = ':'.join(map(str, hexmac))

    return macAddr


def get_next_address(addr_type, base, incr):
    """
    Contributor: Mingtao Yang
    Objective:
    Generate the next address bases on the base and step.

    Input:
    | addr_type | IPv4/IpV6|
    | base | Starting IP address |
    | incr | Value by which we will increment the IP address|

    Usage:    ipAddr = self.get_next_address(
                          ipv4,'10.0.0.0','0.0.0.1')
              ipAddr = self.get_next_address(
                          ipv6,'f001:100:0:0:0:0:0:0','0:0:0:0:0:0:0:1:0')
    """

    log("the base address is: %s,  the step is: %s,  "
        % (str(base), str(incr)))
    if addr_type == 'ipv4' or addr_type == 'ip':
        ip = list(map(int, base.split(".")))
        step = list(map(int, incr.split(".")))
        ip_address = []
        for i in range(3, 0, -1):
            ip[i] += step[i]
            if ip[i] >= 256:
                ip[i] = 0
                ip[i - 1] += 1
        ip[0] += step[0]
        if ip[0] >= 256:
            ip[0] = 0

        ip_address = '.'.join(map(str, ip))

    if addr_type == 'ipv6'  or addr_type == 'ip6':
        ip = base.split(":")
        step = incr.split(":")
        log("IP list is %s" % ip)

        ip_address = []
        hexip = []

        for i in range(0, 7):
            index = 7 - int(i)
            ip[index] = int(ip[index], 16) + int(step[index], 16)
            ip[index] = hex(ip[index])
            temp = ip[index]
            if int(temp, 16) >= 65536:
                ip[index] = hex(0)
                ip[index - 1] = int(ip[index - 1], 16) + 1
                ip[index - 1] = hex(ip[index - 1])


        ip[0] = int(ip[0], 16) + int(step[0], 16)
        ip[0] = hex(ip[0])
        temp = ip[0]
        if int(temp, 16) >= 65536:
            ip[0] = hex(0)

        for i in range(0, 8):
            hexip.append('{0:x}'.format(int(ip[i], 16)))

        ip_address = ':'.join(map(str, hexip))

    return ip_address
