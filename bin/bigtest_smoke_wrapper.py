#!/usr/bin/env python
"""
Wrapper script to execute the smoke test cases in a BigRobot test suite.
This happens inside the BigTest environment (via 'bt runtests'). We derive
the various BIGROBOT environment variables from the BigTest path. The
assumption is that BigRobot and BigTest source codes share the same base path.

This script is called by the BigTest wrapper to execute the smoke tests in
a BigRobot test suite. As an example, see:
bigtest/bigtest/smoketest/T5,T5-sanity,t5_singleleaf_dualrack_ping_test_suite.py

This script exports the environment variable BIGTEST_NODES and executes
'gobot test ...'
"""

import os
import re
import sys
import subprocess
import datetime
from pytz import timezone


def usage():
    s = """\nUsage: bigtest_smoke_wrapper.py <suite> --node <nodes> [gobot_options]

Example:
$ bigtest_smoke_wrapper.py \\
    bigtest/smoketest/T5,T5-sanity,t5_singleleaf_dualrack_ping_test_suite.py \\
    --nodes 'controller-c01n01-065,mininet-c01n01-065'
    """
    print(s)
    sys.exit(1)


if len(sys.argv) < 3:
    usage()

SUITE_FILE = sys.argv[1]

if sys.argv[2] == '--nodes':
    NODES = sys.argv[3]
else:
    usage()

ARGS = ''

if len(sys.argv) > 4:
    ARGS = sys.argv[4:]


def error_exit(msg):
    print(msg)
    sys.exit(1)


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


def get_suite_name():
    return os.path.basename(SUITE_FILE)[:-3]


def get_suite_category():
    """
    Return the category that this test suite belongs to. E.g., 'smoketest'
    """
    return SUITE_FILE.split('/')[-2]


def get_base_path():
    """
    The base path is defined as the directory where bigtest resides. This is
    calculated by looking at the current script path and stripping
    '/bigtest/bigtest/.*' to get the base path.
    If script path is /home/bsn/workspace/Test_Robot/bigtest/bigtest/smoketest
    Then base path is /home/bsn/workspace/Test_Robot
    """
    script_path = get_file_path()
    pattern = r'/bigtest/bigtest/.*'
    if re.search(pattern, script_path):
        base_path = re.sub(pattern, '', script_path)
    else:
        error_exit("Cannot derive the base path from '%s'!" % script_path)
    return base_path


ts = ts_local()

print("\n============== BigRobot smoke: Init ==============")
print("SUITE_FILE: %s" % SUITE_FILE)
set_and_print_env('BIGROBOT_CI', 'True')
set_and_print_env('BIGTEST_PATH', get_base_path() + '/bigtest')
set_and_print_env('BIGTEST_NODES', NODES)
set_and_print_env('BIGROBOT_PATH', get_base_path() + '/bigrobot')
set_and_print_env('BIGROBOT_BIN', get_env('BIGROBOT_PATH') + '/bin')
set_and_print_env('BIGROBOT_LOG_PATH', get_env('BIGTEST_PATH') + '/testlogs')
set_and_print_env('BIGROBOT_LOG_PATH_EXEC_INSTANCE',
                  get_env('BIGROBOT_LOG_PATH') +
                      '/' + get_suite_category() +
                      '.' + get_suite_name() +
                      '/' + get_suite_name() + '_' + ts)
set_and_print_env('BIGROBOT_SUITE_RELATIVE',
                  os.path.basename(SUITE_FILE).replace(',', '/')[:-3])
set_and_print_env('BIGROBOT_SUITE',
                  get_env('BIGROBOT_PATH') + '/testsuites/' +
                      get_env('BIGROBOT_SUITE_RELATIVE'))
set_and_print_env('PATH', 
                  get_env('BIGROBOT_BIN') +
                      ":/usr/local/bin:/sbin:/bin:/usr/bin")

if not os.path.exists(get_env('BIGROBOT_PATH')):
    error_exit("ERROR: BIGROBOT_PATH %s is not found!"
               % get_env('BIGROBOT_PATH'))
if not os.path.exists(get_env('BIGROBOT_SUITE') + '.txt'):
    error_exit("ERROR: BIGROBOT_SUITE %s.txt is not found!"
               % get_env('BIGROBOT_SUITE'))

print('suite category: %s' % get_suite_category())

run_cmd(get_env('BIGROBOT_BIN') + "/gobot version")
run_cmd(get_env('BIGROBOT_BIN') + "/gobot env")

print("\n============== BigRobot smoke: Start test  ==============")
status = run_cmd(get_env('BIGROBOT_BIN') +
                 "/gobot test --include=smoke %s" % ' '.join(ARGS))

print("\n============== BigRobot smoke: End test (exit status=%s) =============="
      % status)
sys.exit(status)

