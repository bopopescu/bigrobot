import os
import sys
import json
import yaml
import datetime
import time
import uuid
import pprint
from pytz import timezone
from log import *
from gobot import *
from autobot.version import *
from exec_timer import *


TZ = timezone("America/Los_Angeles")


def _env_get_and_set(name, new_val=None, default=None):
    """
    Category: Get/set environment variables for BigRobot.
    Attempt to update 'name' environment variable with a value:
    - if new_val is specified, then set env and return it
    - else if env exist, then just return it
    - else if a default value is specified, then set env and return it
    - last resort, return None
    """
    if new_val:
        os.environ[name] = int_to_str(new_val)
        return os.environ[name]
    elif name in os.environ:
        return os.environ[name]
    elif default:
        os.environ[name] = int_to_str(default)
        return os.environ[name]
    else:
        return None


def bigrobot_path(new_val=None, default=None):
    """
    Category: Get/set environment variables for BigRobot.
    """
    return _env_get_and_set('BIGROBOT_PATH', new_val, default)


def bigrobot_config_path():
    """
    Category: Get/set environment variables for BigRobot.
    """
    return ''.join((bigrobot_path(), '/autobot/config'))


def bigrobot_log_path(new_val=None, default=None):
    """
    Category: Get/set environment variables for BigRobot.
    """
    return _env_get_and_set('BIGROBOT_LOG_PATH', new_val, default)


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
    if debug:
        robot_syslog_file(default=''.join((bigrobot_log_path(), '/syslog.txt')))
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


def prettify_log(s, data, level=3):
    analyze(''.join((s, '\n', prettify(data))), level)


def sleep(s):
    """
    Sleep for <s> seconds.
    """
    time.sleep(s)


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


def create_uuid():
    """
    Create a UUID based on the host ID and current time.
    """
    return str(uuid.uuid1())


def ds():
    """
    Return the current datestamp, e.g., 20130926.
    """
    t = datetime.datetime.now(TZ)

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
    local_datetime = datetime.datetime.now(TZ)
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
    local_datetime = datetime.datetime.now(TZ)
    return local_datetime.strftime("%Y-%m-%dT%H:%M:%Sz")


def time_now():
    """
    Return the current time.
    """
    return time.time()


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


def prettify(data):
    """
    Return the Python object as a pretty-print formatted string.
    """
    return pprint.pformat(data)


def bigtest_node_info():
    """
    Traverse the directory /var/run/bigtest and gather all the node attributes
    which were created by BigTest.
    """

    my_root = '/var/run/bigtest'

    if not os.path.exists(my_root):
        error_exit('Directory %s does not exist.' % my_root)
    
    nodes = {}
    for root, dirs, files in os.walk(my_root):
        if root == my_root:
            # Ignore top-level root
            continue
    
        node = os.path.basename(root)
        nodes[node] = {}
    
        for filename in files:
            full_path_filename = "%s/%s/%s" % (my_root, node, filename)
            val = open(full_path_filename, "r").read().rstrip()
            nodes[node][filename] = val
    

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


class TestFailure(AssertionError):
    """
    This can triggered when there is a test failure.
    """


class EnvironmentFailure(AssertionError):
    """
    This is triggered when there is a test environment failure.
    """
    

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


def environment_failure(msg):
    """
    Call this on environmental failure.
    """
    raise EnvironmentFailure(msg)
