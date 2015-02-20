#!/usr/bin/env python
"""
Wrapper script to execute the smoke test cases in a BigRobot test suite.
We derive the various BIGROBOT environment variables from the relative path
(assuming bin/ in bigrobot path).

This script exports the environment variables BIGROBOT_TESTBED and
BIGROBOT_PARAMS_INPUT, then executes 'gobot test ...'
"""

import os
import re
import sys
import subprocess
import datetime
from pytz import timezone


def usage():
    s = """\nUsage: bigrobot_smoke_wrapper.py <suite> [gobot_options]

Example:
$ bigrobot_smoke_wrapper.py \\
    testsuites/T5/T5-sanity/t5_singleleaf_dualrack_ping_test_suite
    """
    print(s)
    sys.exit(1)


if len(sys.argv) < 2:
    usage()

SUITE_FILE = sys.argv[1]
TEST_TYPE = sys.argv[2]

ARGS = ''

if len(sys.argv) > 3:
    ARGS = sys.argv[3:]


def error_exit(msg):
    print(msg)
    sys.exit(1)


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


def ts_local():
    """
    Return the current timestamp in local time (string format),
    e.g., 20130926_155749
    """
    local_datetime = datetime.datetime.now(timezone("America/Los_Angeles"))
    return local_datetime.strftime("%Y%m%d_%H%M%S")


def run_cmd(cmd):
    print("Executing '%s'" % cmd)
    return subprocess.call(cmd, shell=True)

def run_cmd_spaces(*args):
    print ("Executing '%s'" % str(args))
    return subprocess.call(args, shell=False)

def set_env(name, value):
    os.environ[name] = value
    return os.environ[name]


def get_env(name, default=None):
    if not name in os.environ:
        if default:
            set_env(name, default)
        else:
            error_exit("Environment variable '%s' does not exist!" % name)
    return os.environ[name]


def print_env(name):
    print("%s: %s" % (name, get_env(name)))


def set_and_print_env(name, value):
    set_env(name, value)
    return print_env(name)


def get_file_path():
    return os.path.dirname(os.path.abspath(SUITE_FILE))


def get_base_path():
    """
    The base path is defined as the directory where bigrobot resides. This is
    calculated by looking at the current script path, which should be
    bigrobot/bin and moving up 2 levels to get to the base path.
    If script path is /home/bsn/workspace/Test_Robot/bigrobot/bin
    Then base path is /home/bsn/workspace/Test_Robot
    """
    script_path = get_file_path()
    pattern = r'/bigrobot/bin/.*'
    if re.search(pattern, script_path):
        base_path = re.sub(pattern, '', script_path)
    else:
        error_exit("Cannot derive the base path from '%s'!" % script_path)
    return base_path


ts = ts_local()

print("\n============== BigRobot smoke: Init ==============")
set_and_print_env('BIGROBOT_CI', 'True')
# set_and_print_env('BIGROBOT_TESTBED', 'bigtest')
# set_and_print_env('BIGROBOT_PARAMS_INPUT', NODES)
set_and_print_env('BIGROBOT_PATH', get_base_path() + '/bigrobot')
set_and_print_env('BIGROBOT_BIN', get_env('BIGROBOT_PATH') + '/bin')
set_and_print_env('BIGROBOT_LOG_PATH', get_env('BIGROBOT_PATH') + '/testlogs')
set_and_print_env('BIGROBOT_LOG_PATH_EXEC_INSTANCE',
                  get_env('BIGROBOT_LOG_PATH') +
                      '/' + SUITE_FILE.replace('/', '-') + '_' + ts)
set_and_print_env('BIGROBOT_SUITE',
                  get_env('BIGROBOT_PATH') + '/' + SUITE_FILE)
set_and_print_env('PATH',
                  get_env('BIGROBOT_BIN') +
                      ":/usr/local/bin:/sbin:/bin:/usr/bin")

if not os.path.exists(get_env('BIGROBOT_PATH')):
    error_exit("ERROR: BIGROBOT_PATH %s is not found!"
               % get_env('BIGROBOT_PATH'))
if not os.path.exists(get_env('BIGROBOT_SUITE') + '.txt'):
    error_exit("ERROR: BIGROBOT_SUITE %s.txt is not found!"
               % get_env('BIGROBOT_SUITE'))

run_cmd_spaces(get_env('BIGROBOT_BIN') + "/gobot", "version")
run_cmd_spaces(get_env('BIGROBOT_BIN') + "/gobot", "env")
# run_cmd(get_env('BIGROBOT_BIN') + "/gobot version")
# run_cmd(get_env('BIGROBOT_BIN') + "/gobot env")

print("\n============== BigRobot smoke: Start test  ==============")
# status = run_cmd(get_env('BIGROBOT_BIN') +
#                  "/gobot test --include=smoke %s" % ' '.join(ARGS))
if TEST_TYPE is not None:
    status = run_cmd(get_env('BIGROBOT_BIN') +
                 "/gobot test --include %s" % TEST_TYPE)
else:
    status = run_cmd(get_env('BIGROBOT_BIN') +
                     "/gobot test")

print "Status: %s" % status

if status == 0:
    file_touch(get_env('BIGROBOT_LOG_PATH_EXEC_INSTANCE') + '/PASSED')
else:
    file_touch(get_env('BIGROBOT_LOG_PATH_EXEC_INSTANCE') + '/FAILED')

print("\n============== BigRobot smoke: End test (exit status=%s) =============="
      % status)
sys.exit(status)
