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
    return _env_get_and_set('BIGROBOT_LOG_PATH_EXEC_INSTANCE', new_val, default)


def bigrobot_suite(new_val=None, default=None):
    """
    Category: Get/set environment variables for BigRobot.
    """
    return _env_get_and_set('BIGROBOT_SUITE', new_val, default)


def bigrobot_suite_format(new_val=None, default=None):
    """
    Category: Get/set environment variables for BigRobot.

    Specify the test suite file format. The possible values include:
    mw  - MediaWiki format
    txt - Robot Framework plain text format 
    """
    return _env_get_and_set('BIGROBOT_SUITE_FORMAT', new_val, default)


def bigrobot_topology(new_val=None, default=None):
    """
    Category: Get/set environment variables for BigRobot.
    """
    return _env_get_and_set('BIGROBOT_TOPOLOGY', new_val, default)


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
    debug = _env_get_and_set('BIGROBOT_DEBUG', new_val, default)
    if int(debug) == 1:
        robot_syslog_file(default=''.join((bigrobot_log_path_exec_instance(),
                                           '/syslog.txt')))
        robot_syslog_level(default='DEBUG')

    return debug


def bigrobot_pandoc_support(new_val=None, default=None):
    """
    Category: Get/set environment variables for BigRobot.
    """
    return _env_get_and_set('BIGROBOT_PANDOC_SUPPORT', new_val, default)


def analyze(s, level=2):
    """
    Write to the log file. The advantage with this function is convenience
    since the user doesn't need to instantiate from the Log class. They can
    simply call helpers.analyze("blah") to start logging.

    The intended use is for quick code analysis.
    """
    Log().log(s, level)


def log(s, level=3):
    analyze(s, level)


# Alias
test_log = log


def prettify(data):
    """
    Return the Python object as a pretty-print formatted string.
    """
    return pprint.pformat(data)


def prettify_log(s, data, level=3):
    analyze(''.join((s, '\n', prettify(data))), level)


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
        test_error("Node must be a controller ('c1', 'c2').")
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


def is_bvs(name):
    return name == 'bvs'


def is_bigtap(name):
    return name == 'bigtap'


def is_bigwire(name):
    return name == 'bigwire'


def is_scalar(data):
    """Verify if the input is a valid Python scalar."""
    return isinstance(data, (type(None), str, int, float, bool))
    
    
def is_bool(data):
    """Verify if the input is a valid Python boolean."""
    return isinstance(data, bool)
    
    
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


def file_remove(filename):
    """
    Remove/delete a file.
    """
    if file_exists(filename):
        os.remove(filename)


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
    
    
def error_msg(msg):
    print("Error: %s" % msg)


def error_exit(msg):
    error_msg(msg)
    sys.exit(1)


def error_exit_if_file_not_exist(msg, f):
    if f is None:
        error_exit(''.join((msg, ': <topology_file_not_specified>')))
    if not os.path.exists(f):
        error_exit(''.join((msg, ': ', f)))


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
    ROBOT_EXIT_ON_FAILURE = True


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

    
def test_failure(msg):
    """
    Call this on test failure.
    """
    raise TestFailure(msg)


def test_error(msg):
    """
    Call this on test error.
    """
    raise TestError(msg)


def environment_failure(msg):
    """
    Call this on environmental failure.
    """
    raise EnvironmentFailure(msg)


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
    #log("scp put local_file=%s remote_path=%s" % (local_file, remote_path))
    log("SSH copy source (%s) to destination (%s) " % (local_file, remote_path))
    s.put(local_file, remote_path, recursive=True) 


def scp_get(server, remote_file, local_path,
            user='admin', password='adminadmin', recursive=True):
    ssh = _createSSHClient(server, user, password)
    s = SCPClient(ssh.get_transport())

    # !!! FIXME: Catch conditions where file/path are not found
    #log("scp put remote_file=%s local_path=%s" % (remote_file, local_path))
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


def _ping(host, count=3, waittime=100, quiet=False, node=None):

    # !!! FIXME: Mac OS X ping can use -W (waittime) to timeout ping.
    #            On Ubuntu, use -w (deadline) to timeout after n seconds.
    if not node:
        cmd = "ping -c %d -W %d %s" % (count, waittime, host)
        if not quiet:
            log("Ping command: %s" % cmd, level=4)

        _, out = run_cmd(cmd, shell=False, quiet=True)
    else:
        cmd = "ping -w %d %s" % (count, host)
        if not quiet:
            log("Ping command: %s" % cmd, level=4)

        result = node.bash(cmd)
        out = result["content"]

    if not quiet:
        log("Ping output:\n%s" % out, level=4)
        
    # Linux output:
    #   3 packets transmitted, 3 received, 0% packet loss, time 2003ms
    # Mac OS X output:
    #   3 packets transmitted, 3 packets received, 0.0% packet loss

    match = re.search(r'.*transmitted, (\d+)( packets)? received.*',
                      out,
                      re.M|re.I)
    if match:
        packets_received = int(match.group(1))
        s = ("Ping host '%s' - %d transmitted, %d received"
             % (host, count, packets_received))
        if packets_received > 0:
            if not quiet:
                log("Success! %s%s"
                    % (s, br_utils.end_of_output_marker()), level=4)
            return True
        else:
            if not quiet:
                log("Failure! %s%s"
                    % (s, br_utils.end_of_output_marker()), level=4)
            return False
    test_error("Unknown ping error.")


def ping(host, count=3, waittime=100, quiet=False):
    """
    Unix ping.
    :param host: (Str) ping hist host
    :param count: (Int) number of packets to send
    :param waittime: (Int) time in milliseconds to wait for a reply
    """
    if count < 3:
        count = 3   # minimum count
    status = _ping(host, count=1, waittime=100, quiet=quiet)
    if not status:
        status = _ping(host, count=1, waittime=100, quiet=quiet)
    if not status:
        count -= 2
        status = _ping(host, count=count, waittime=waittime, quiet=quiet)
    return status


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

def marker():
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")