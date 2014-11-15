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

jobs_to_build = ['http://10.8.0.52:8080/view/BigTap_Summary_View/job/app_tacacs_user_management/build?delay=0sec',
                 'http://10.8.0.52:8080/view/BigTap/job/bigtap_address_list/build?delay=0sec',
                 'http://10.8.0.52:8080/view/BigTap/job/bigtap_inport_masking/build?delay=0sec',
                 'http://10.8.0.52:8080/view/BigTap/job/bigtap_intf_rewrite_vlan/build?delay=0sec',
                 'http://10.8.0.52:8080/view/BigTap/job/bigtap_l3l4_mode/build?delay=0sec',
                 'http://10.8.0.52:8080/view/BigTap/job/bigtap_policy_iptos_match/build?delay=0sec',
                 'http://10.8.0.52:8080/view/BigTap/job/bigtap_policy_rewrite_vlan//build?delay=0sec',
                 'http://10.8.0.52:8080/view/BigTap/job/bigtap_portchannel/build?delay=0sec',
                 'http://10.8.0.52:8080/view/BigTap/job/bigtap_prefix_optimization/build?delay=0sec',
                 'http://10.8.0.52:8080/view/BigTap/job/bigtap_process_restart/build?delay=0sec',
                 'http://10.8.0.52:8080/view/BigTap/job/bigtap_rbac/build?delay=0sec',
                 'http://10.8.0.52:8080/view/BigTap/job/bigtap_snmp/build?delay=0sec',
                 'http://10.8.0.52:8080/view/BigTap/job/bigtap_statistics/build?delay=0sec',
                 'http://10.8.0.52:8080/view/BigTap/job/bigtap_switchlight_accton_as4600_traffic/build?delay=0sec',
                 'http://10.8.0.52:8080/view/BigTap/job/bigtap_switchlight_accton_as5610_traffic/build?delay=0sec',
                 'http://10.8.0.52:8080/view/BigTap/job/bigtap_switchlight_accton_as5710_traffic/build?delay=0sec',
                 'http://10.8.0.52:8080/view/BigTap/job/bigtap_switchlight_dell_s4810_traffic/build?delay=0sec',
                 'http://10.8.0.52:8080/view/BigTap/job/bigtap_switchlight_quanta_lb9_traffic/build?delay=0sec',
                 'http://10.8.0.52:8080/view/BigTap/job/bigtap_switchlight_quanta_ly2_traffic/build?delay=0sec',
                 'http://10.8.0.52:8080/view/BigTap/job/bigtap_user_management/build?delay=0sec',
                 'http://10.8.0.52:8080/view/BigTap/job/bigtap_verify_show_commands/build?delay=0sec',
                 'http://10.8.0.52:8080/view/BigTap/job/bigtap_vft/build?delay=0sec',
                 'http://10.8.0.52:8080/view/BigTap/job/CORSAIR-bigtap_corsair_dpm/build?delay=0sec',
                 'http://10.8.0.52:8080/view/BigTap/job/CORSAIR-bigtap_corsair_overlapping_policies/build?delay=0sec',
                 'http://10.8.0.52:8080/view/BigTap/job/CORSAIR-bigtap_corsair_tunnel_ha/build?delay=0sec',
                 'http://10.8.0.52:8080/view/BigTap/job/CORSAIR-bigtap_corsair_tunnel_sanity/build?delay=0sec',
                 'http://10.8.0.52:8080/view/BigTap/job/CORSAIR-bigtap_corsair_tunnel_traffic/build?delay=0sec',
                 'http://10.8.0.52:8080/view/BigTap/job/CORSAIR-bigtap_dpm_replay/build?delay=0sec',
                 'http://10.8.0.52:8080/view/BigTap/job/CORSAIR-bigtap_interface_groups/build?delay=0sec',
                 'http://10.8.0.52:8080/view/BigTap/job/CORSAIR-bigtap_tcp_flags/build?delay=0sec',
                 'http://10.8.0.52:8080/view/BigTap/job/bigtap_ha/build?delay=0sec']

for job in jobs_to_build:
    print "Running the job {}".format(job)
    call (["curl", "-X", "POST", job, "--data-urlencode", "json={}"], shell=False)
    time.sleep(20)
    while os.path.isfile('/tmp/bigtap_testbed_lock'):
        print "Inside while and running the job {}".format(job)
        time.sleep(5)


print 'Success'


