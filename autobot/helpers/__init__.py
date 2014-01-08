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
import re
from scp import SCPClient
from pytz import timezone
from log import *
from gobot import *
from autobot.version import *
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
    if new_val:
        os.environ[name] = int_to_str(new_val)
    elif name in os.environ:
        pass
    elif default:
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
    return os.path.exists(filename)    


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


class TestError(AssertionError):
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
    #client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(server, port, user, password)
    return client


def scp_put(server, local_file, remote_path):
    # !!! FIXME: Remove hardcoded user/pw
    user = 'admin'
    password = 'adminadmin'
    ssh = _createSSHClient(server, user, password)
    s = SCPClient(ssh.get_transport())

    # !!! FIXME: Catch conditions where file/path are not found
    #log("scp put local_file=%s remote_path=%s" % (local_file, remote_path))
    s.put(local_file, remote_path) 


def scp_get(server, remote_file, local_path):
    # !!! FIXME: Remove hardcoded user/pw
    user = 'admin'
    password = 'adminadmin'
    ssh = _createSSHClient(server, user, password)
    s = SCPClient(ssh.get_transport())

    # !!! FIXME: Catch conditions where file/path are not found
    #log("scp put remote_file=%s local_path=%s" % (remote_file, local_path))
    s.get(remote_file, local_path)


def get_args(func):
    """
    Provide a mechanism to translate a JSON string into function arguments.
    This allows us to specify "named arguments" (instead of positional
    arguments) as a Robot keyword.
    
    Example keyword:
    
      Test1    kwarg { 'xyz':1, 'arg2':false, 'arg3':null }

    Test1 keyword will invoke the following library function:

      def test1(xyz, arg2=True, arg3=0, arg4=None):
          get_args(self.test1)
          ...

    It returns an argument dictionary.

          args = get_args()
            --  args['xyz'] => 1
            --  args['arg2'] => False
            --  args['arg3'] => None
            --  args['arg4'] => None
    """

    # Get the default list of arguments
    default_args, _, _, default_vals = inspect.getargspec(func)
    default_args = default_args[1:]    # remove 'self' from list
    default_vals = list(default_vals)  # convert tuple to list
    
    first_arg = default_args[0]
    
    if len(default_args) == len(default_vals):
        # all args have default values, so extract default value for 1st arg
        first_arg_val = default_vals[0]
    else:
        # 1st arg doesn't have a default value, so assign None to it
        first_arg_val = None    
    
    stack = inspect.stack()
    
    # get_arg's caller
    #   (<frame object at 0x7f93b3c08450>,
    #   '/Users/vui/Documents/workspace/bigrobot/keywords_dev/vui/MyTest.py',
    #   30,
    #   'test_args2',
    #   ['        args = helpers.get_args()\n'],
    #   0)
    caller_stack = stack[1]
    
    # Robot caller (keyword invocation)
    #   (<frame object at 0x7f93b2514900>,
    #   '/usr/local/lib/python2.7/site-packages/robot/running/handlers.py',
    #   127,
    #   '<lambda>',
    #   ['        return lambda: handler(*positional, **named)\n'],
    #   0),
    robot_caller_stack = stack[2]
  
    #log("stack: %s" % prettify(stack))
    
    args, _, varkw, args_dict = inspect.getargvalues(caller_stack[0])

    args_dict.update(args_dict.pop(varkw, []))
    args_dict.pop('self', None)    # remove 'self' argument

    # Robot Framework's keyword invocation
    # Stackframe output:
    #   robot_kw_args_dict: {
    #       'handler': <bound method MyTest.test_args2 of <MyTest.MyTest object at 0x1038b89d0>>,
    #       'named': {},
    #       'positional': [u'{"arg8":1111, "arg12":2222 }']}
    #
    _, _, _, robot_kw_args_dict = inspect.getargvalues(robot_caller_stack[0])
    #log("robot_kw_args_dict: %s" % prettify(robot_kw_args_dict))
    robot_kw_arg_len = len(robot_kw_args_dict['positional'])
    robot_kw_arg = robot_kw_args_dict['positional'][0]
    
    # Multiple arguments or none were passed, no special handling
    if robot_kw_arg_len != 1:
        return args_dict
    
    # If match 'kwarg {' then we should assume with high confidence that the
    # keyword argument is being passed as a JSON string.
    match = re.match(r'^kwarg ({.*)$', robot_kw_arg, re.I)
    if match:
        kw_arg = match.group(1) 
        #log("Found keyword argument: %s" % kw_arg)
    else:
        return args_dict
    
    if not is_json(kw_arg):
        test_error("Robot keyword argument is not a valid JSON string: %s"
                   % kw_arg)
    
    kw_args_dict = from_json(kw_arg)
    log("Converted keyword argument to dictionary: %s" % kw_args_dict)
    
    # preserve the first argument's default value
    args_dict[first_arg] = first_arg_val
    
    for key in kw_args_dict:
        if key in args_dict:
            if args_dict[key] != kw_args_dict[key]:
                #log("Updating value for '%s' from '%s' to '%s'"
                #    % (key, args_dict[key], kw_args_dict[key]))
                args_dict[key] = kw_args_dict[key]
        else:
            test_error("Invalid Robot keyword argument: '%s'. Allowable arguments are %s."
                       % (key, args[1:]))            
    
    return args_dict

