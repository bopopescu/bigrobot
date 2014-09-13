'''
Wrapper scripts to find the summary logs on virtual regression jobs in Jenkins
For Summary View to run rebot
'''

import sys
import pexpect
import optparse
import os
import datetime
import subprocess
import getpass
# Adding Gobot Path to sys path for Exscript APIs
bigrobot_path = os.path.dirname(__file__) + '/..'
exscript_path = bigrobot_path + '/vendors/exscript/src'
sys.path.insert(0, bigrobot_path)
sys.path.insert(1, exscript_path)
from Exscript import Account
from Exscript.protocols import SSH2, Telnet
from autobot.devconf import HostDevConf
import autobot.helpers as helpers

helpers.set_env('IS_GOBOT', 'False')
helpers.set_env('AUTOBOT_LOG', '/tmp/myrobot.log')

regress = 'regress'
user = "root"
pwd = "bsn"
jenkins_location = 'cd /var/lib/jenkins/jobs'
phy_regress_jobs = ['Regress-virtual_HA', 'Regress-virtual', 't5_platform_firstboot_HA']

regress_handle = HostDevConf(host=regress, user=user, password=pwd, name="regress-host")
for dir_name in phy_regress_jobs:
    grep_cmd = 'find %s -name output.xml | grep testlogs | grep -v archive' % dir_name
    if dir_name == "Regress-virtual":
        cmd_list = [jenkins_location, 'find $PWD/%s/builds -name output.xml | sort | tail -13' % dir_name]
    else:
        cmd_list = [jenkins_location, 'find $PWD/%s/builds -name output.xml | sort | tail -1' % dir_name]
    for cmd in cmd_list:
      out = regress_handle.bash(cmd)
    print str(dir_name) + ':'
    print out['content']

print 'Success!!!'
