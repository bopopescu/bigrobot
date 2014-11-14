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
jobs_to_build = ['http://10.8.0.52:8080/view/BigTap_Summary_View/job/monitor_bigtap_verify_show_commands/build?delay=0sec','http://10.8.0.52:8080/view/BigTap/job/Bigtap_Clean_config/build?delay=0sec','http://10.8.0.52:8080/view/BigTap/job/monitor_bigtap_snmp/build?delay=0sec','http://10.8.0.52:8080/view/BigTap/job/Bigtap_Clean_config/build?delay=0sec']
#jobs_to_build = ['http://10.8.0.52:8080/view/SwitchLight/job/switchlight_as4600_snmp/build?delay=0sec']

for job in jobs_to_build:
  print "Running the job {}".format(job)
  call (["curl", "-X", "POST", job, "--data-urlencode", "json={}"], shell=False)
  time.sleep(20)
  while os.path.isfile('/tmp/bigtap_testbed_lock'):
    print "Inside while and running the job {}".format(job)
    time.sleep(5)


print 'Success'


