import os
import sys
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
import re
import ipcalc
import curses.ascii as ascii
from scp import SCPClient
from pytz import timezone
from autobot.version import get_version
import autobot.utils as br_utils

# All below are modules in the helpers package. So we can control and manage
# name conflicts. Therefore it's assumed safe to do 'import *'.
from log import *
from gobot import *
from exec_timer import *

# Convenience helper function any_match() and first_match() imported from
# Exscript. More info at
# http://knipknap.github.io/exscript/api/Exscript.util.match-module.html
from Exscript.util.match import any_match, first_match

_TZ = timezone("America/Los_Angeles")
_BIGROBOT_ENV_LIST = []


def ctrl(char):
    """
    Returns the control character. E.g., helpers.ctrl('c') returns the value
    for Ctrl-c which is \x03'.
    See http://stackoverflow.com/questions/6248766/how-to-enter-the-escape-characters-for-telnet-programmatically
    """
    return ascii.ctrl(char)


# is_bool() needs to be defined before test_error() which uses it.
def is_bool(data):
    """Verify if the input is a valid Python boolean."""
    return isinstance(data, bool)


def warn(s, level=2):
    """
    Warn log.
    """
    Log().warn(s, level)


def debug(s, level=2):
    """
    Debug log.
    """
    Log().debug(s, level)


def trace(s, level=2):
    """
    Trace log.
    """
    Log().trace(s, level)


def info(s, level=2):
    """
    Info log.
    """
    Log().info(s, level)


# Alias
test_log = info
log = info


def analyze(s, level=3):
    info(s, level)


def prettify(data):
    """
    Return the Python object as a pretty-print formatted string.
    """
    return pprint.pformat(data)


def prettify_log(s, data, level=3):
    analyze(''.join((s, '\n', prettify(data))), level)


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


def test_error(msg, soft_error=False):
    """
    Call this on test error.
    """
    if not is_bool(soft_error):
        environment_failure("helpers.test_error() argument 'soft_error' must"
                            " be a boolean.")
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


def set_env(name, value):
    """
    Set the environment variable 'name' to 'value'.
    Note: In Robot text file, you can call the keyword 'Set Environment Variable'
          from the OperatingSystem library instead.
    """
    # Python's os module requires that env value be a string, not integer.
    value = str(value)

    if name in os.environ:
        debug("Environment variable '%s' current value is: '%s'"
              % (name, os.environ[name]))
    os.environ[name] = value
    debug("Environment variable '%s' new value is: '%s'"
          % (name, os.environ[name]))
    return os.environ[name]


def get_env(name):
    """
    Get the environment variable 'name'.
    Note: In Robot text file, you can call the keyword 'Get Environment Variable'
          from the OperatingSystem library instead.
    """
    if not name in os.environ:
        debug("Environment variable '%s' doesn't exist." % name)
        return None
    else:
        debug("Environment variable '%s': '%s'"
              % (name, os.environ[name]))
        return os.environ[name]


def remove_env(name):
    """
    Remove the environment variable 'name'.
    Note: In Robot text file, you can call the keyword 'Remove Environment Variable'
          from the OperatingSystem library instead.
    """
    if not name in os.environ:
        debug("Environment variable '%s' doesn't exist. Removal is not required."
              % name)
        return False
    else:
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
    """
    return _env_get_and_set('BIGROBOT_LOG_PATH_EXEC_INSTANCE',
                            new_val,
                            default)


def bigrobot_suite(new_val=None, default=None):
    """
    Category: Get/set environment variables for BigRobot.
    """
    return _env_get_and_set('BIGROBOT_SUITE', new_val, default)


def bigrobot_suite_format(new_val=None, default=None):
    """
    Category: Get/set environment variables for BigRobot.

    Specify the test suite file format. The possible values include:
    mw  - MediaWiki format (obsolete)
    txt - Robot Framework plain text format
    """
    return _env_get_and_set('BIGROBOT_SUITE_FORMAT', new_val, default)


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
    """
    return _env_get_and_set('BIGROBOT_TOPOLOGY', new_val, default)


def bigrobot_continuous_integration(new_val=None, default=None):
    """
    Category: Get/set environment variables for BigRobot.
    """
    return _env_get_and_set('BIGROBOT_CI', new_val, default)


def bigrobot_params(new_val=None, default=None):
    """
    Category: Get/set environment variables for BigRobot.
    """
    return _env_get_and_set('BIGROBOT_PARAMS', new_val, default)


def bigtest_path(new_val=None, default=None):
    """
    Category: Get/set environment variables for BigRobot.
    """
    return _env_get_and_set('BIGTEST_PATH', new_val, default)


def python_path(new_val=None, default=None):
    """
    Category: Get/set environment variables for BigRobot.
    """
    return _env_get_and_set('PYTHONPATH', new_val, default)


def robot_syslog_file(new_val=None, default=None):
    """
    Category: Get/set environment variables for BigRobot.
    """
    return _env_get_and_set('ROBOT_SYSLOG_FILE', new_val, default)


def robot_syslog_level(new_val=None, default=None):
    """
    Category: Get/set environment variables for BigRobot.
    """
    return _env_get_and_set('ROBOT_SYSLOG_LEVEL', new_val, default)


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
        robot_syslog_file(default=''.join((bigrobot_log_path_exec_instance(),
                                           '/syslog.txt')))
        robot_syslog_level(default='DEBUG')

    return _debug


def bigrobot_pandoc_support(new_val=None, default=None):
    """
    Category: Get/set environment variables for BigRobot.
    """
    return _env_get_and_set('BIGROBOT_PANDOC_SUPPORT', new_val, default)


def sleep(s):
    """
    Sleep for <s> seconds.
    """
    time.sleep(int(s))


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

    if helpers.is_bvs(n.platform():
        ...this is a BVS (aka T5) controller...
    """
    return name == 'bvs'


# Alias
is_t5 = is_bvs


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


def is_arista(name):
    """
    Inspect the platform type for the node. Usage:

    if helpers.is_arista(n.platform()):
        ...this is an Arista switch...
    """
    return name == 'arista'


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


def to_json(python_data):
    """
    Return JSON (pretty) formatted string from Python datatype (dict or array).
    """
    return json.dumps(python_data, indent=4, sort_keys=True)


def load_config(yaml_file):
    """
    Load a configuration file which is in YAML format. Result is Python dict.
    """
    stream = open(yaml_file, 'r')
    return yaml.load(stream)


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


def get_path_autobot_config():
    return ''.join((get_path_autobot(), '/config'))


def create_uuid():
    """
    Create a UUID based on the host ID and current time.
    """
    return str(uuid.uuid1())


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
    e.g., 2013-09-26T15:57:49z
    """
    utc_datetime = datetime.datetime.utcnow()
    return utc_datetime.strftime("%Y-%m-%dT%H:%M:%Sz")


def ts_long_local():
    """
    Return the current timestamp in local time (string format),
    e.g., 2013-09-26T15:57:49z
    """
    local_datetime = datetime.datetime.now(_TZ)
    return local_datetime.strftime("%Y-%m-%dT%H:%M:%Sz")


def time_now():
    """
    Return the current time.
    """
    return time.time()


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


def file_read_once(filename):
    """
    Read file in a single shot. Immediately close file.
    Returns a string.
    """
    f = open(filename, 'r')
    lines = f.readlines()
    f.close()
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
    """
    with file(fname, 'a'):
        os.utime(fname, times)


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


def _createSSHClient(server, user, password, port=22):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(server, port, user, password)
    return client


def scp_put(server, local_file, remote_path,
            user='admin', password='adminadmin'):
    ssh = _createSSHClient(server, user, password)
    s = SCPClient(ssh.get_transport())

    # !!! FIXME: Catch conditions where file/path are not found
    # log("scp put local_file=%s remote_path=%s" % (local_file, remote_path))
    log("SSH copy source (%s) to destination (%s) " % (local_file, remote_path))
    s.put(local_file, remote_path, recursive=True)


def scp_get(server, remote_file, local_path,
            user='admin', password='adminadmin', recursive=True):
    ssh = _createSSHClient(server, user, password)
    s = SCPClient(ssh.get_transport())

    # !!! FIXME: Catch conditions where file/path are not found
    # log("scp put remote_file=%s local_path=%s" % (remote_file, local_path))
    log("SSH copy source (%s) to destination (%s) " % (remote_file, local_path))
    s.get(remote_file, local_path)


def run_cmd(cmd, cwd=None, ignore_stderr=False, shell=True, quiet=False):
    """
    shell - Just pass the command string for execution in a subshell. This is
            ideal when command should run in the background (string can include
            '&') and/or command contains shell variables/wildcards.

    Returns tuple (Boolean, String)
        success: (True,  "...success message...")
        failure: (False, "...error message...")
    """
    if not quiet:
        print("Executing '%s'" % cmd)

    if shell:
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


def _ping(host, count=5, waittime=100, quiet=False, source_if=None, node=None):
    if not node:
        cmd = "ping -c %s -W %s %s" % (count, waittime, host)
        if not quiet:
            log("Ping command: %s" % cmd, level=4)

        _, out = run_cmd(cmd, shell=False, quiet=True, ignore_stderr=True)
    else:
        options = ''
        if source_if:
            options = "-I %s " % source_if

        # On Ubuntu, use -w (deadline) to timeout after n seconds. Set it to
        # be the same as count. On Unbuntu, if the destination is not pingable,
        # it will keep attempting to ping until deadline is reache.
        cmd = "ping -c %s -w %s %s%s" % (count, count, options, host)
        if not quiet:
            log("Ping command: %s" % cmd, level=4)

        result = node.bash(cmd)
        out = result["content"]

    if not quiet:
        log("Ping output:\n%s" % out, level=4)

    # Linux output:
    #   3 packets transmitted, 3 received, 0% packet loss, time 2003ms
    #   3 packets transmitted, 0 received, +3 errors, 100% packet loss, time 2014ms
    #       This is when ping failed with 'ping -c 3 -w 4 -I eth0 101.195.0.131'
    # Mac OS X output:
    #   3 packets transmitted, 3 packets received, 0.0% packet loss

    if source_if:
        match = re.search(r'ping: unknown iface (\w+)', out, re.M | re.I)
        if match:
            test_error("Ping error - unknown source interface '%s'"
                       % match.group(1))

    match = re.search(r'.*?(\d+) packets transmitted, (\d+)( packets)? received, .*?(\d+\.?(\d+)?)% packet loss.*',
                      out,
                      re.M | re.I)
    if match:
        packets_transmitted = int(match.group(1))
        packets_received = int(match.group(2))
        loss_percentage = int(float(match.group(4)))
        s = ("Ping host '%s' - %d transmitted, %d received, %d%% loss"
             % (host, packets_transmitted, packets_received, loss_percentage))

        log("Ping result: %s%s"
            % (s, br_utils.end_of_output_marker()), level=4)
        return loss_percentage

    if re.search(r'no route to host', out, re.M | re.I):
        test_error("Ping error - no route to host")

    test_error("Unknown ping error. Please check the output log.")


def ping(host, count=5, waittime=100, quiet=False):
    """
    Unix ping.
    :param host: (Str) ping hist host
    :param count: (Int) number of packets to send
    :param waittime: (Int) time in milliseconds to wait for a reply

    Return: (Int) loss percentage
    """
    if count < 3:
        count = 3  # minimum count
    loss = _ping(host, count=1, waittime=100, quiet=quiet)
    if loss > 0:
        loss = _ping(host, count=1, waittime=100, quiet=quiet)
    if loss > 0:
        count -= 2
        loss = _ping(host, count=count, waittime=waittime, quiet=quiet)
    return loss


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


#
# String processing helpers
#

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

    This function converts the table to a Python dictionary.

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


def strip_cli_output(input_str):
    """
    The convention from the expect library (Exscript) is as followed:
      - first line contains the issued command
      - last line contains the device prompt
    This function strips the first and last line, leaving the actual output.
    """
    out = text_processing_str_remove_header(input_str, 1)
    out = text_processing_str_remove_trailer(out, 1)
    return out

def str_to_list(input_str):
    """
    Convert a multi-line string into a list of strings.
    """
    return input_str.splitlines()

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
