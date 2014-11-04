from __future__ import print_function
import sys
import time
import autobot.helpers as helpers
from nose.exc import SkipTest


# Reserved for critical errors, such as suite setup failures.
CRITICAL_FAILURE = False


def sleep(s):
    helpers.log("Sleeping for %s seconds" % s)
    helpers.sleep(s)


def log_to_console(msg):
    print(msg)
    helpers.log(msg)


def func_name(level=2):
    return sys._getframe(level).f_code.co_name  # pylint: disable=W0212


def run(test, setup=None, teardown=None, critical_failure=False):
    """
    Execute a test case. It also accepts test setup/teardown fixtures for an
    all-in-one invocation.

    Arguments:
      - test: test function
      - setup: test setup function
      - teardown: test teardown function
      - critical_failure: set to True if test is considered as critical and
        execution shouldn't continue if test fails

    Return value:
      - On success (pass), return the value from test function. Not sure what
        Nose does with it though... For the most part, it can simply be ignored.
      - On failure, raise exception.
    """
    global CRITICAL_FAILURE  # pylint: disable=W0603
    helpers.log("===========================================================")
    helpers.log("Test case: %s" % func_name())
    helpers.log("===========================================================")
    print("")

    is_tc_failed = False

    if setup:
        try:
            setup()
        except:
            raise

    if CRITICAL_FAILURE:
        helpers.error_exit("Detected critical error. Aborting.", 1)

    try:
        return test()
    except SkipTest:
        raise
    except:
        is_tc_failed = True

        if critical_failure:
            CRITICAL_FAILURE = True
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


def wait_until_keyword_succeeds(timeout, retry_interval, kw, *args):
    """
    Keep running a keyword again and again until it succeeds (success is
    defined as not triggering an exception).

    Arguments:
      - timeout: Continue to run for this duration (in seconds)
      - retry_interval: sleep for n seconds before re-run
      - kw: keyword function
      - args: keyword function arguments

    Return value:
      - On success, return value from keyword function.
      - On failure, raise exception.
    """
    maxtime = time.time() + timeout
    error = None
    while not error:
        try:
            return kw(*args)
        except:
            if time.time() > maxtime:
                error = helpers.exception_info()
            else:
                sleep(retry_interval)
    raise AssertionError("wait_until_keyword_succeeds: Timeout %s seconds exceeded. The last error was:\n%s"
                         % (timeout, error))

