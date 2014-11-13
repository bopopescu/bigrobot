import autobot.helpers as helpers
import autobot.test as test
import re

'''
    ::::::::::    README    ::::::::::::::

    This BigTaptilities file is used to abstract the BigTap utility
    functions. Please include any utility functions that are not
    specific to your test suites here.

'''

syslogMonitorFlag = False

class BigTapUtilities(object):
    def __init__(self):
        pass

    def start_syslog_monitor(self):
        '''
        Start monitoring the log.
        Kill the existing tail process if any and start new tail
        '''
        global syslogMonitorFlag

        try:
            t = test.Test()
            c1 = t.controller('c1')
            c2 = t.controller('c2')
            c1_pidList = self.get_syslog_monitor_pid('c1')
            c2_pidList = self.get_syslog_monitor_pid('c2')
            for c1_pid in c1_pidList:
                # if (re.match("^d", c1_pid)):
                    c1.sudo('kill -9 %s' % (c1_pid))
            for c2_pid in c2_pidList:
                # if (re.match("^d", c2_pid)):
                    c2.sudo('kill -9 %s' % (c2_pid))

            # Add rm of the file if file already exist in case of a new test
            c1.sudo("tail -f /var/log/syslog | grep --line-buffered '#011' > %s &" % "c1_syslog_dump.txt")
            c2.sudo("tail -f /var/log/syslog | grep --line-buffered '#011' > %s &" % "c2_syslog_dump.txt")

            syslogMonitorFlag = True
            return True

        except:
            helpers.log("Exception occured while starting the syslog monitor")
            return False

    def restart_syslog_monitor(self, node):

        global syslogMonitorFlag

        if(syslogMonitorFlag):
            t = test.Test()
            c = t.controller(node)
            result = c.sudo('ls *_dump.txt')
            filename = re.split('\n', result['content'])[1:-1]
            c.sudo("tail -f /var/log/syslog/syslog.log | grep --line-buffered '#011' >> %s &" % filename[0].strip('\r'))
            return True
        else:
            return True



    def stop_syslog_monitor(self):

        global syslogMonitorFlag

        if(syslogMonitorFlag):
            c1_pidList = self.get_syslog_monitor_pid('c1')
            c2_pidList = self.get_syslog_monitor_pid('c2')
            t = test.Test()
            c1 = t.controller('c1')
            c2 = t.controller('c2')
            helpers.log("Stopping syslog Monitor on C1")
            for c1_pid in c1_pidList:
                c1.sudo('kill -9 %s' % (c1_pid))
            helpers.log("Stopping syslog Monitor on C2")
            for c2_pid in c2_pidList:
                c2.sudo('kill -9 %s' % (c2_pid))
            syslogMonitorFlag = False

            try:
                helpers.log("****************    syslog Log From C1    ****************")
                result = c1.sudo('cat c1_syslog_dump.txt')
                split = re.split('\n', result['content'])[1:-1]
                if split:
                    helpers.warn("syslog Errors Were Detected At: %s " % helpers.ts_long_local())

            except(AttributeError):
                helpers.log("No Errors From syslog Monitor on C1")

            try:
                helpers.log("****************    syslog Log From C2    ****************")
                result = c2.sudo('cat c2_syslog_dump.txt')
                split = re.split('\n', result['content'])[1:-1]
                if split:
                    helpers.warn("syslog Errors Were Detected At: %s " % helpers.ts_long_local())
            except(AttributeError):
                helpers.log("No Errors From syslog Monitor on C2")

            return True

        else:
            helpers.log("syslogMonitorFlag is not set: Returning")



    def get_syslog_monitor_pid(self, role):
        t = test.Test()
        c = t.controller(role)
        helpers.log("Verifing for monitor job")
        c_result = c.sudo('ps ax | grep tail | grep sudo | awk \'{print $1}\'')
        split = re.split('\n', c_result['content'])
        pidList = split[1:-1]
        return pidList
