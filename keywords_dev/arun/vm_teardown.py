#!/usr/bin/env python
'''
Wrapper Script to spwan cotroller VMs on KVM Machine
'''
import os, re, sys, subprocess, datetime, getpass
from pytz import timezone


vmdk_name = "controller-bvs-2.0.7-SNAPSHOT.vmdk"
vmdk_path = "/var/lib/jenkins/jobs/bvs\ main/lastSuccessful/archive/target/appliance/images/bvs/"
kvm_host = "10.192.104.13"
kvm_user = "bsn"
kvm_pwd = "bsn"
current_user = getpass.getuser()
kvm_handle = None
kvm_vmdk_path = None
vm_name = None

# Adding Gobot Path to sys path for Exscript APIs
bigrobot_path = os.path.dirname(__file__) + '/..'
exscript_path = bigrobot_path + '/vendors/exscript/src'
sys.path.insert(0, bigrobot_path)
sys.path.insert(1, exscript_path)
print "Detailed log can be tailed at /tmp/robot.log  or /tmp/autobot_%s.log" % current_user
import autobot.helpers as helpers
from autobot.devconf import HostDevConf

def usage():
    s = """\nUsage: vm_teardown <name>
Example:
$ vm_teardown \\
    <name>
    """
    print(s)
    sys.exit(1)

def connect_to_kvm_host(**kwargs):
    global kvm_handle
    hostname = kwargs.get('hostname', None)
    user = kwargs.get('user', None)
    password = kwargs.get('password', None)
    name = kwargs.get('name', None)
    kvm_handle = HostDevConf(host = hostname, user = user, password = password,
            protocol = 'ssh', timeout=100, name = name)

def get_vm_running_state():
    return kvm_handle.bash('sudo virsh list --all | grep %s | awk \'{print $3}\'' % vm_name)['content']
    pass

def tear_down_vm():
    if "destroyed" in kvm_handle.bash("sudo virsh destroy %s" % vm_name)['content']:
        print "1. Successfully Powered Down"
    else:
        print "Issue with Shutting down VM using virsh \nPlease debug on KVM Host %s \n Exiting.." % kvm_host
        sys.exit(1)
    if "undefined" in kvm_handle.bash("sudo virsh undefine %s" % vm_name)['content']:
        print "2. Successfully Deleted !"
    else:
        print "Issue with Deleting VM using virsh \nPlease debug on KVM Host %s \n Exiting.." % kvm_host
        sys.exit(1)
          
def main(*args):
    global vm_name
    if not args or args[0][0] in ['help', '-h', '--help']:
        usage()
        sys.exit(1)
    vm_name = args[0][0]
    connect_to_kvm_host(hostname = kvm_host, user = kvm_user,
                                     password = kvm_pwd, name = 'kvm_host')
    
    if vm_name in kvm_handle.bash('sudo virsh list --all')['content']:
        print "Tearing down VM with Name : %s" % vm_name
        helpers.log("Tearing down VM with Name on kvm host: %s " % vm_name)
        tear_down_vm()
    else:
        helpers.log("VM with given name %s doesn't exits in KVM Host! %s\nExisting.." % (vm_name, kvm_host))
        print "VM with given name %s doens't exists in KVM Host %s\nWe are good!\nExisting.." % (vm_name, kvm_host)
        sys.exit(1)
        
if __name__ == '__main__':
    global vm_name
    vm_name = sys.argv[1]
    print get_vm_running_state()
#     if len(sys.argv) < 2:
#         usage()
#     main(sys.argv[1:])

print "Success !!!"
