import os.path
import autobot.helpers as helpers
import autobot.test as test
from robot.api import logger


class Listener:

    ROBOT_LISTENER_API_VERSION = 2

    # !!! FIXME: Calling helpers.log() will not write to the Robot log files
    #            (e.g., debug.log). Not sure why that is so. Looks to be an
    #            issue with Robot's logger API.

    def __init__(self):
        self.logfile = open(helpers.bigrobot_listener_log(), 'w')
        self.testcase_counter = 0
        _ = test.Test()

    def log(self, s):
        self.logfile.write(s + '\n')

    def log_devcmd(self, s, no_timestamp=False):
        helpers.bigrobot_devcmd_write(s + '\n', no_timestamp=no_timestamp)

    def start_suite(self, name, attrs):
        self.log_devcmd("# Test Suite: %s\n#    Source: %s"
                        % (attrs['longname'], attrs['source']),
                        no_timestamp=True)
        self.log("%-12s name: '%s', attrs: '%s'" % ('start_suite', name, helpers.prettify(attrs)))
        self.log('--------')
        # self.log("%12s: %s '%s'" % ('start_suite', name, attrs['doc']))

    def end_suite(self, name, attrs):
        self.log("%-12s name: '%s', attrs: '%s'" % ('end_suite', name, helpers.prettify(attrs)))
        self.log('--------')
        # self.log("%12s: status=%s, message='%s'" % ('end_suite', attrs['status'], attrs['message']))

    def start_test(self, name, attrs):
        self.testcase_counter += 1
        self.log_devcmd("# Test Case start: %s (#%d)"
                        % (attrs['longname'], self.testcase_counter),
                        no_timestamp=True)
        self.log("%-12s name: '%s', attrs: '%s'" % ('start_test', name, helpers.prettify(attrs)))
        self.log('--------')
        # helpers.bigrobot_test_case_status("None")
        # tags = ' '.join(attrs['tags'])
        # self.log("%0.12s: %s '%s' [ %s ]" % ('start_test', name, attrs['doc'], tags))

    def end_test(self, name, attrs):
        self.log_devcmd("# Test Case end: %s (#%d) - %s"
                        % (attrs['longname'], self.testcase_counter, attrs['status']),
                        no_timestamp=True)
        self.log("%-12s name: '%s', attrs: '%s'" % ('end_test', name, helpers.prettify(attrs)))
        self.log('--------')
        # status = 'PASSED' if attrs['status'] == 'PASS' else 'FAILED'
        # helpers.bigrobot_test_case_status(status)
        # self.log("%12s: status=%s, message='%s'" % ('end_test', attrs['status'], attrs['message']))

    def start_keyword(self, name, attrs):
        # self.log_devcmd("# Keyword: %s" % name, no_timestamp=True)
        self.log("%-12s name: '%s', attrs: '%s'" % ('start_keyword', name, helpers.prettify(attrs)))
        self.log('--------')
        # tags = ' '.join(attrs['tags'])
        # self.log("%0.12s: %s '%s' [ %s ]" % ('start_keyword', name, attrs['doc'], tags))

    def end_keyword(self, name, attrs):
        self.log("%-12s name: '%s', attrs: '%s'" % ('end_keyword', name, helpers.prettify(attrs)))
        self.log('--------')
        # self.log("%12s: status=%s, message='%s'" % ('end_keyword', attrs['status'], attrs['message']))

    def close(self):
        self.log('%-12s: <done>' % 'close')
        self.logfile.close()

