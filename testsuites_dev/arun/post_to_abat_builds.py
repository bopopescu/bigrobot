import sys
import pexpect
import optparse
import os
import datetime
import subprocess
import getpass
# Adding Gobot Path to sys path for Exscript APIs
# bigrobot_path = os.path.dirname(__file__) + '/..'
# exscript_path = bigrobot_path + '/vendors/exscript/src'
# sys.path.insert(0, bigrobot_path)
# sys.path.insert(1, exscript_path)
# print bigrobot_path
# print __file__
# print os.path.dirname(__file__)
sys.path.append('/home/amallina/workspace/bigrobot/modules')
sys.path.append('/home/amallina/workspace/bigrobot/vendors/exscript/src')
sys.path.append('/home/amallina/workspace/bigrobot/')
from Exscript import Account
from Exscript.protocols import SSH2, Telnet
from autobot.devconf import HostDevConf
import autobot.helpers as helpers
import re

helpers.set_env('IS_GOBOT', 'False')
helpers.set_env('AUTOBOT_LOG', '/tmp/myrobot.log')



def print_chksums(server, file_locations, cmd):
	user = "bsn"
	pwd = "bsn"
	build_server = HostDevConf(host=server, user=user, password=pwd, name=server, timeout=190)

	build_server.bash(file_locations)
	out = build_server.bash(cmd)
	files = out['content'].split('\n')
	print '-' * 60
	for file_name in files:
		if re.match(r'controller-.*', file_name):
			chksums = build_server.bash("md5sum %s" % file_name)['content']
			print chksums.split('\n')[1]
	print '-' * 60
	return build_server

def scp_to_server(server, location):
	scp_cmd = ('scp -o "UserKnownHostsFile=/dev/null" -o StrictHostKeyChecking=no "%s@%s:%s" %s' % ("bsn", "10.2.3.100", "/var/lib/jenkins/jobs/bcf-2.5.0/lastSuccessful/archive/controller-*", location))
	print scp_cmd
	scp_cmd_out = server.bash(scp_cmd, prompt=[r'.*password:', r'.*#', r'.*$ '])['content']
	if "password" in scp_cmd_out:
		print "sending bsn password.."
		print server.bash('bsn')['content']
	else:
		print ("SCP should be done:\n%s" % scp_cmd_out)
	print ("Success SCP'ing latest Jenkins build !!")
	pass

if __name__ == '__main__':
	build_server_ip = "10.2.3.11"
	jenkins_server_ip = "10.2.3.100"

	file_locations = "cd /home/bsn/abat/builds/T5/ironhorse/bcf_2_5_0/controller-builds"
	print "Build Server file chksums:"
	build_server = print_chksums(build_server_ip, file_locations, cmd="ls -ltr | awk '{print $8}'")

# 	location = "/home/bsn/abat/builds/T5/ironhorse/bcf_2_5_0/controller-builds/."
# 	scp_to_server(build_server, location)

	print "Jenkins Server file chksums:"
	file_locations = "cd /var/lib/jenkins/jobs/bcf-2.5.0/lastSuccessful/archive"

	print_chksums(jenkins_server_ip, file_locations, cmd="ls -ltr | awk '{print $9}'")
	print 'Success!!!'
