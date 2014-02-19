#!/usr/bin/env python
"""
Wrapper script to execute a BigRobot test suite. You will need to modify the
following environment variables:
  BIGROBOT_PATH           - full path to BigRobot framework
  BIGROBOT_SUITE_RELATIVE - relative path to the test suite file (tests in
                            this suite will be executed)

In Jenkins, set the following env in the 'Execute shell' window:
  export BIGROBOT_PATH=${WORKSPACE}
                          # WORKSPACE=/Users/vui/.jenkins/workspace/Regression
  export BIGROBOT_LOG_PATH=${JENKINS_HOME}/job/${JOB_NAME}/${BUILD_NUMBER}/robot/report
  export BIGROBOT_SUITE_RELATIVE=/testsuites/T5/T5-sanity/t5_singleleaf_dualrack_ping_test_suite

"""    

import os
import sys
import subprocess
import datetime
from pytz import timezone

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
    p = subprocess.call(cmd, shell=True)


def set_env(name, value):
    os.environ[name] = value
    return os.environ[name]


def get_env(name):
    if not name in os.environ:
        error_exit("Environment variable '%s' does not exist!" % name)
    return os.environ[name]


def print_env(name):
    print("%s: %s" % (name, get_env(name)))
    

bigrobot_path = get_env('BIGROBOT_PATH')
bigrobot_suite_relative = get_env('BIGROBOT_SUITE_RELATIVE')
bigrobot_suite = bigrobot_path + bigrobot_suite_relative
bigrobot_log_path = bigrobot_path + '/testlogs'
bigrobot_bin = bigrobot_path + '/bin'

set_env('BIGROBOT_SUITE', bigrobot_suite)
#set_env('BIGROBOT_LOG_PATH', bigrobot_log_path)
set_env('BIGROBOT_LOG_PATH_EXEC_INSTANCE', get_env('BIGROBOT_LOG_PATH'))


#suite = os.path.basename(bigrobot_suite)
#ts = ts_local()

# BigRobot log directory
#set_env('BIGROBOT_LOG_PATH_EXEC_INSTANCE',
#        bigrobot_log_path + "/" + suite + "_" + ts)

# Let BigRobot know that it's running in the CI environment (Jenkins/ABAT)
set_env('BIGROBOT_CI', 'True')
set_env('PATH', bigrobot_path + ":/usr/local/bin:/sbin:/bin:/usr/bin")

if not os.path.exists(bigrobot_path):
    error_exit("ERROR: BIGROBOT_PATH %s is not found!" % bigrobot_path)

if not os.path.exists(bigrobot_suite + '.txt'):
    error_exit("ERROR: BIGROBOT_SUITE %s.txt is not found!" % bigrobot_suite)

print_env('BIGROBOT_PATH')
print_env('BIGROBOT_SUITE')
print_env('BIGROBOT_LOG_PATH')
print_env('BIGROBOT_LOG_PATH_EXEC_INSTANCE')

run_cmd(bigrobot_bin + "/gobot version")
run_cmd(bigrobot_bin + "/gobot env")
run_cmd(bigrobot_bin + "/gobot test --include=smoke")

