#!/usr/bin/env python
# Wrapper script to execute a BigRobot test suite. You will need to modify the
# following environment variables:
#   bigrobot_path  - full path to BigRobot framework
#   bigtest_path   - full path to BigTest framework
#   bigrobot_suite - full path to the test suite file (tests in this suite will be executed)

bigrobot_path = '/home-local/vui/work/bigrobot'
bigtest_path = '/home-local/vui/work/bigtest'
bigrobot_suite = bigrobot_path + '/testsuites/T5/T5-sanity/t5_singleleaf_dualrack_ping_test_suite'


import os
import sys
import subprocess
import datetime
from pytz import timezone

bigrobot_log_path = bigtest_path + '/testlogs'
bigrobot_bin = bigrobot_path + '/bin'
os.environ['BIGROBOT_PATH'] = bigrobot_path
os.environ['BIGTEST_PATH'] = bigtest_path
os.environ['BIGROBOT_SUITE'] = bigrobot_suite
os.environ['BIGROBOT_LOG_PATH'] = bigrobot_log_path

_TZ = timezone("America/Los_Angeles")


def error_exit(msg):
    error_msg(msg)
    sys.exit(1)


def ts_local():
    """
    Return the current timestamp in local time (string format),
    e.g., 20130926_155749
    """
    local_datetime = datetime.datetime.now(_TZ)
    return local_datetime.strftime("%Y%m%d_%H%M%S")


def run_cmd(cmd):
    print("Executing '%s'" % cmd)
    p = subprocess.call(cmd, shell=True)


suite = os.path.basename(bigrobot_suite)
ts = ts_local()

# BigRobot log directory
os.environ['BIGROBOT_LOG_PATH_EXEC_INSTANCE'] = bigrobot_log_path + "/" + suite + "_" + ts

# Let BigRobot know that it's running in the CI environment (Jenkins/ABAT)
os.environ['BIGROBOT_CI'] = 'True'

os.environ['PATH'] = bigrobot_path + "/bin:/bin:/usr/bin"

if not os.path.exists(bigrobot_path):
    error_exit("ERROR: BIGROBOT_PATH %s is not found!" % bigrobot_path)

if not os.path.exists(bigrobot_suite):
    error_exit("ERROR: BIGROBOT_SUITE %s is not found!" % bigrobot_suite)

print("BIGROBOT_PATH: %s" % os.environ['BIGROBOT_PATH'])
print("BIGTEST_PATH: %s" % os.environ['BIGTEST_PATH'])
print("BIGROBOT_SUITE: %s" % os.environ['BIGROBOT_SUITE'])
print("BIGROBOT_LOG_PATH: %s" % os.environ['BIGROBOT_LOG_PATH'])
print("BIGROBOT_LOG_PATH_EXEC_INSTANCE: %s" % os.environ['BIGROBOT_LOG_PATH_EXEC_INSTANCE'])

# Run the sanity tests
run_cmd(bigrobot_bin + "/gobot version")
run_cmd(bigrobot_bin + "/gobot env")
run_cmd(bigrobot_bin + "/gobot test --include=smoke")

