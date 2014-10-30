from __future__ import print_function
import os
import sys
import re
import platform
import subprocess
import autobot.helpers as helpers
from nose.exc import SkipTest


# Reserved for critical errors, such as suite setup failures.
EXIT_ON_FAILURE = False


def sleep(s):
    helpers.log("Sleeping for %s seconds" % s)
    helpers.sleep(s)


def log_to_console(msg):
    print(msg)
    helpers.log(msg)


def func_name():
    return sys._getframe(2).f_code.co_name  # pylint: disable=W0212


def run(func, exit_on_failure=False):
    """Nose fixture: run test"""
    global EXIT_ON_FAILURE
    helpers.log("===========================================================")
    helpers.log("Test case: %s" % func_name())
    helpers.log("===========================================================")

    if EXIT_ON_FAILURE:
        helpers.error_exit("Detected critical error. Aborting.", 1)

    try:
        result = func()
    except SkipTest:
        raise
    except:
        if exit_on_failure:
            EXIT_ON_FAILURE = True
        helpers.log(" \n" + helpers.exception_info())
        raise
    else:
        return result


def test_and_install_package():
    """
    Test importing 3rd party modules required by BigRbot. If import fails,
    then attempt to install the package.

    Important: This step is performed before autobot modules can be loaded.
    So we can't depend on aubobot.helpers and similar facilities.
    """
    def _test_and_install(package, module):
        try:
            return __import__(module)
        except ImportError:
            print("Failed to import module '%s'. Will try to install it."
                   % module)
            if os.stat(os.__file__).st_uid == os.getuid():
                # Current user has permission to install module...
                cmd = "pip install %s" % package
            else:
                cmd = "sudo pip install %s" % package
            print("Executing '%s'" % cmd)
            subprocess.call(cmd, shell=True)

    packages = {
                'nose': 'nose',
                'pylint': 'pylint',
                'httplib2': 'httplib2',
                'pyyaml': 'yaml',
                'pytz': 'pytz',
                'ipcalc': 'ipcalc',
                'netaddr': 'netaddr',
                'pymongo': 'pymongo',
                'pycrypto': 'Crypto',
                'paramiko': 'paramiko',
                'scp': 'scp',
                'pexpect': 'pexpect',
                'robotframework': 'robot',
                'celery': 'celery',
                'xmltodict': 'xmltodict',
                'robotframework-seleniumlibrary': "SeleniumLibrary"
                # 'robotframework-ride': 'robotide',
                # 'pep8': '???',  # not possible to test import pep8 package
                }

    for k, v in packages.iteritems():
        _test_and_install(k, v)


def set_environment():
    """
    Look for user-defined environments such as BIGROBOT_PATH. If they
    don't exist then assume some defaults. Add them to Python path.
    """

    system = platform.system()
    if system == 'Darwin':
        p = '%s/Documents/workspace' % os.path.expanduser('~')
    elif system == 'Linux':
        p = '%s/workspace' % os.path.expanduser('~')
    else:
        sys.stderr.write("BigRobot is only supported on OSX and Linux.")
        sys.exit(1)

    if 'BIGROBOT_PATH' not in os.environ:
        os.environ['BIGROBOT_PATH'] = ''.join((p, '/bigrobot'))

    # if 'BIGTEST_PATH' not in os.environ:
    #    os.environ['BIGTEST_PATH'] = ''.join((p, '/bigtest'))

    # Add paths to PYTHONPATH
    bigrobot_path = os.environ['BIGROBOT_PATH']
    sys.path.insert(0, bigrobot_path + '/vendors/exscript/src')
    sys.path.insert(0, bigrobot_path + '/esb')
    sys.path.insert(0, bigrobot_path)

    # (Re-)export PYTHONPATH environment
    os.environ['PYTHONPATH'] = os.pathsep.join(sys.path)


def test_autobot_import():
    """
    Test importing the Autobot package. This must work else we fail hard.
    """
    try:
        import autobot.version
        autobot.version.get_version()  # just to silence the "unused" warning
    except ImportError:
        sys.stderr.write(
            "Error: Cannot find Autobot package. Please check PYTHONPATH"
            " and BIGROBOT_PATH environment variables.\n")
        sys.stderr.write("  PYTHONPATH=%s" % os.environ['PYTHONPATH'])
        sys.stderr.write("  BIGROBOT_PATH=%s\n" % os.environ['BIGROBOT_PATH'])
        sys.exit(1)


def bigrobot_env_init(is_gobot='True'):
    os.environ['IS_GOBOT'] = is_gobot

    helpers.bigrobot_log_path(default='.')
    if helpers.bigrobot_suite():
        _suite = helpers.bigrobot_suite()

        # If user specified full path, trim it down to just suite name. E.g.,
        # Change:
        #  /Users/vui/Documents/ws/myforks/bigrobot/testsuites_dev/vui/test_mininet
        # To:
        #  vui_test_mininet_20140513_095428
        _match = re.search(r'.+testsuites(_dev)?/(.+)$', _suite)
        if _match:
            _suite = re.sub(r'[\W\s]', '_', _match.group(2))
        helpers.bigrobot_log_path_exec_instance_relative(
                    default="%s_%s"
                    % (_suite, helpers.ts_local()))
    else:
        helpers.bigrobot_log_path_exec_instance_relative(
                    default="<bigrobot_suite>")
    helpers.bigrobot_log_path_exec_instance(
                default="%s/%s"
                % (helpers.bigrobot_log_path(),
                   helpers.bigrobot_log_path_exec_instance_relative()))

    if helpers.bigrobot_suite():
        _topo_p = helpers.bigrobot_suite() + ".physical.topo"
        _topo_v = helpers.bigrobot_suite() + ".virtual.topo"
        _topo_u = helpers.bigrobot_suite() + ".topo"  # p or v unspecified

        if helpers.file_exists(_topo_p):
            topo_file = _topo_p
        elif helpers.file_exists(_topo_v):
            topo_file = _topo_v
        else:
            topo_file = _topo_u

        helpers.bigrobot_topology(default=topo_file)
        print("BigRobot suite: %s" % helpers.bigrobot_suite())
        print("BigRobot topology: %s" % helpers.bigrobot_topology())

    helpers.bigrobot_params(default='None')
    helpers.bigrobot_continuous_integration()
    helpers.bigrobot_exec_hint_format()
    helpers.bigrobot_log_archiver()
    helpers.bigrobot_debug(default=1)

    # !!! FIXME: 2014-04-10 Exscript's Protocol.py sys.stderr is closed for some
    #     reason, which causes SSH2._dbg() to fail. Still not able to figure out
    #     what is causing this (it used to work fine). The workaround is to write
    #     the Exscript debug log to a file instead. We achieve this by setting
    #     an environment variable BIGROBOT_EXSCRIPT_DEBUG_LOG_PATH which
    #      Exscript's Protocol will pick up.
    #
    #     Note: This env should only be set after bigrobot_log_path_exec_instance()
    #           is set.
    helpers.bigrobot_excript_debug_log_path(
          default=helpers.bigrobot_log_path_exec_instance())

    helpers.bigrobot_listener_log(
          default=(helpers.bigrobot_log_path_exec_instance() +
                   '/bigrobot_listener.log'))
    helpers.bigrobot_devcmd_log(
          default=(helpers.bigrobot_log_path_exec_instance() +
                   '/dev_commands.log'))
    helpers.bigrobot_additional_params(
          default=(helpers.bigrobot_log_path_exec_instance() +
                   '/additional-params.topo'))

    helpers.bigrobot_path()
    # helpers.bigtest_path()
    helpers.python_path()
    helpers.bigrobot_test_setup()  # (default=True)
    helpers.bigrobot_test_postmortem()  # (default=True)
    helpers.bigrobot_test_clean_config()  # (default=True)
    helpers.bigrobot_test_pause_on_fail()  # (default=False)
    helpers.bigrobot_test_ztn()  # (default=False)
    helpers.bigrobot_ignore_mininet_exception_on_close()  # (default=False)
    helpers.bigrobot_preserve_mininet_screen_session_on_fail()  # (default=False)
    helpers.bigrobot_esb()
    helpers.bigrobot_esb_broker()
    helpers.bigrobot_ztn_reload()
    helpers.bigrobot_ztn_installer()
    helpers.bigrobot_no_auto_reload()
    helpers.bigrobot_ha_logging()
    helpers.bigrobot_quiet_output()
    helpers.bigrobot_reconfig_reauth()


def big_setup(is_gobot='True'):
    test_and_install_package()
    set_environment()
    test_autobot_import()
    bigrobot_env_init(is_gobot=is_gobot)


def environment_setup():
    helpers.bigrobot_nose_setup("True")
    big_setup(is_gobot='False')
    os.environ["AUTOBOT_LOG"] = helpers.bigrobot_log_path_exec_instance() + "/debug.log"
    print()
