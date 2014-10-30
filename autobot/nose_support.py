from __future__ import print_function
import os
import sys
import time
import autobot.helpers as helpers
from autobot.setup_env import big_setup
from nose.exc import SkipTest


# Reserved for critical errors, such as suite setup failures.
EXIT_ON_FAILURE = False


def sleep(s):
    helpers.log("Sleeping for %s seconds" % s)
    helpers.sleep(s)


def log_to_console(msg):
    print(msg)
    helpers.log(msg)


def func_name(level=2):
    return sys._getframe(level).f_code.co_name  # pylint: disable=W0212


def run(test, setup=None, teardown=None, exit_on_failure=False):
    global EXIT_ON_FAILURE  # pylint: disable=W0603
    helpers.log("===========================================================")
    helpers.log("Test case: %s" % func_name())
    helpers.log("===========================================================")
    print("")

    is_tc_failed = False

    if setup:
        try:
            setup(tc_failed=is_tc_failed)
        except:
            raise

    if EXIT_ON_FAILURE:
        helpers.error_exit("Detected critical error. Aborting.", 1)

    try:
        test()
    except SkipTest:
        raise
    except:
        is_tc_failed = True

        if exit_on_failure:
            EXIT_ON_FAILURE = True
        helpers.log(" \n" + helpers.exception_info())

        if teardown:
            log_to_console("Inside exception for %s" % func_name())
            try:
                teardown(tc_failed=is_tc_failed)
            except:
                pass

        raise
    else:
        if teardown:
            try:
                teardown(tc_failed=is_tc_failed)
            except:
                raise


def wait_until_keyword_succeeds(self, timeout, retry_interval, kw):
    maxtime = time.time() + timeout
    error = None
    while not error:
        try:
            kw()
        except:
            if time.time() > maxtime:
                raise
            else:
                time.sleep(retry_interval)
    raise AssertionError("Timeout %s exceeded. The last error was: %s"
                         % (utils.secs_to_timestr(timeout), error))


def environment_setup():
    helpers.bigrobot_nose_setup("True")
    big_setup(is_gobot='False')
    os.environ["AUTOBOT_LOG"] = helpers.bigrobot_log_path_exec_instance() + "/debug.log"
    print()
