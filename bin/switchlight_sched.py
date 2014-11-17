#!/usr/bin/python
'''
    Schedule a Build Jenkins
'''
import pexpect
import optparse
import os
import os.path
import datetime
import subprocess
import getpass
import sys, time, re, os
from subprocess import call

return_code = subprocess.call("rm -rf /var/lib/jenkins/jobs/Regress-BigTap-Summary/workspace/robot_logs/*", shell=True)

jobs_to_build = ['http://10.8.0.52:8080/view/SwitchLight/job/bigtap_switchlight_lag_hashing/build?delay=0sec',
                 'http://10.8.0.52:8080/view/BigTap/job/Bigtap_Clean_config/build?delay=0sec',
                 'http://10.8.0.52:8080/view/SwitchLight/job/bigtap_switchlight_platform_sanity/build?delay=0sec',
                 'http://10.8.0.52:8080/view/BigTap/job/Bigtap_Clean_config/build?delay=0sec',
                 'http://10.8.0.52:8080/view/SwitchLight/job/switchlight_as4600_environment_snmp/build?delay=0sec',
                 'http://10.8.0.52:8080/view/BigTap/job/Bigtap_Clean_config/build?delay=0sec',
                 'http://10.8.0.52:8080/view/SwitchLight/job/switchlight_as4600_snmp/build?delay=0sec',
                 'http://10.8.0.52:8080/view/BigTap/job/Bigtap_Clean_config/build?delay=0sec',
                 'http://10.8.0.52:8080/view/SwitchLight/job/switchlight_as5610_environment_snmp/build?delay=0sec',
                 'http://10.8.0.52:8080/view/BigTap/job/Bigtap_Clean_config/build?delay=0sec',
                 'http://10.8.0.52:8080/view/SwitchLight/job/switchlight_as5610_snmp/build?delay=0sec',
                 'http://10.8.0.52:8080/view/BigTap/job/Bigtap_Clean_config/build?delay=0sec',
                 'http://10.8.0.52:8080/view/SwitchLight/job/switchlight_as5710_environment_snmp/build?delay=0sec',
                 'http://10.8.0.52:8080/view/BigTap/job/Bigtap_Clean_config/build?delay=0sec',
                 'http://10.8.0.52:8080/view/SwitchLight/job/switchlight_as5710_snmp/build?delay=0sec',
                 'http://10.8.0.52:8080/view/BigTap/job/Bigtap_Clean_config/build?delay=0sec',
                 'http://10.8.0.52:8080/view/SwitchLight/job/switchlight_as6700_environment_snmp/build?delay=0sec',
                 'http://10.8.0.52:8080/view/BigTap/job/Bigtap_Clean_config/build?delay=0sec',
                 'http://10.8.0.52:8080/view/SwitchLight/job/switchlight_as6700_snmp/build?delay=0sec',
                 'http://10.8.0.52:8080/view/BigTap/job/Bigtap_Clean_config/build?delay=0sec',
                 'http://10.8.0.52:8080/view/SwitchLight/job/switchlight_lb9_environment_snmp/build?delay=0sec',
                 'http://10.8.0.52:8080/view/BigTap/job/Bigtap_Clean_config/build?delay=0sec',
                 'http://10.8.0.52:8080/view/SwitchLight/job/switchlight_lb9_snmp/build?delay=0sec',
                 'http://10.8.0.52:8080/view/BigTap/job/Bigtap_Clean_config/build?delay=0sec',
                 'http://10.8.0.52:8080/view/SwitchLight/job/switchlight_ly2_environment_snmp/build?delay=0sec',
                 'http://10.8.0.52:8080/view/BigTap/job/Bigtap_Clean_config/build?delay=0sec',
                 'http://10.8.0.52:8080/view/SwitchLight/job/switchlight_ly2_snmp/build?delay=0sec',
                 'http://10.8.0.52:8080/view/BigTap/job/Bigtap_Clean_config/build?delay=0sec',
                 'http://10.8.0.52:8080/view/SwitchLight/job/switchlight_s4810_environment_snmp/build?delay=0sec',
                 'http://10.8.0.52:8080/view/BigTap/job/Bigtap_Clean_config/build?delay=0sec',
                 'http://10.8.0.52:8080/view/SwitchLight/job/switchlight_s4810_snmp/build?delay=0sec',
                 'http://10.8.0.52:8080/view/BigTap/job/Bigtap_Clean_config/build?delay=0sec',
                 'http://10.8.0.52:8080/view/SwitchLight/job/switchlight_s6000_environment_snmp/build?delay=0sec',
                 'http://10.8.0.52:8080/view/BigTap/job/Bigtap_Clean_config/build?delay=0sec',
                 'http://10.8.0.52:8080/view/SwitchLight/job/switchlight_s6000_snmp/build?delay=0sec',
                 'http://10.8.0.52:8080/view/BigTap/job/Bigtap_Clean_config/build?delay=0sec',
                 'http://10.8.0.52:8080/view/SwitchLight/job/switchlight_user_management/build?delay=0sec',
                 'http://10.8.0.52:8080/view/BigTap/job/Bigtap_Clean_config/build?delay=0sec']

for job in jobs_to_build:
    print "Running the job {}".format(job)
    call (["curl", "-X", "POST", job, "--data-urlencode", "json={}"], shell=False)
    time.sleep(20)
    while os.path.isfile('/tmp/bigtap_testbed_lock'):
        print "Inside while and running the job {}".format(job)
        time.sleep(5)


print 'Success'


