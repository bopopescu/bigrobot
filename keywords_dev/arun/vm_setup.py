#!/usr/bin/env python
'''
Wrapper Script to spwan cotroller VMs on KVM Machine
'''
import os, re, sys, subprocess, datetime, getpass
from pytz import timezone


vmdk_name = "controller-bvs-2.0.7-SNAPSHOT.vmdk"
vmdk_path = "/var/lib/jenkins/jobs/bvs\ master/lastSuccessful/archive/target/appliance/images/bvs/"
kvm_host = "10.192.104.13"
kvm_user = "bsn"
kvm_pwd = "bsn"
current_user = getpass.getuser()
kvm_handle = None
kvm_vmdk_path = None
vm_name = None

# Adding Gobot Path to sys path for Exscript APIs
sys.path.append("/home/%s/workspace/bigrobot/modules" % current_user)
sys.path.append("/home/%s/workspace/bigrobot/vendors/exscript/src" % current_user)
sys.path.append("/home/%s/workspace/bigrobot/" % current_user)
import autobot.helpers as helpers
from autobot.devconf import HostDevConf

def usage():
    s = """\nUsage: vm_setup <name>

Example:
$ vm_setup \\
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
    
def scp_vmdk_to_kvm(**kwargs):
    global vm_name, kvm_vmdk_path
    
    output = kvm_handle.bash('uname -a')
    helpers.log("KVM Host Details : \n %s" % output['content'])
    kvm_handle.bash('cd /var/lib/libvirt/')
    
    if "No such file or directory" in kvm_handle.bash('cd bvs_images/')['content']:
        helpers.log("No BVS_IMAGES dir in KVM Host @ /var/lib/libvirt creating one to store bvs vmdks") 
        kvm_handle.bash('sudo mkdir bvs_images')
        kvm_handle.bash('sudo chmod -R 777 bvs_images/')
    else:
        helpers.log('BVS_IMAGES dir exists in KVM Host @ /var/lib/libvirt/bvs_images/ copying latest vmdkd from jenkins server')
    kvm_handle.bash('sudo chmod -R 777 ../bvs_images/')
    kvm_handle.bash('cd bvs_images')
    helpers.log("Latest VMDK will be copied to location : %s at KVM Host" % kvm_handle.bash('pwd')['content'])
    
    # For below SCP to work we need to have Kvm Pub Key in jenkins build server..
    helpers.log("Executing Scp cmd to copy latest bvs vmdk to KVM Server")
    kvm_handle.bash('scp "bsn@jenkins:/var/lib/jenkins/jobs/bvs\ master/lastSuccessful/archive/target/appliance/images/bvs/controller-bvs-2.0.7-SNAPSHOT.vmdk" .', timeout=100)['content']
    kvm_handle.bash('sudo cp controller-bvs-2.0.7-SNAPSHOT.vmdk ../images/%s.vmdk' % vm_name)
    kvm_vmdk_path = "/var/lib/libvirt/images/%s.vmdk" % vm_name
    #vm_name = "%s_BVS" % current_user
    helpers.log("1. Success copying latest VMDK to KVM Host to Location: %s" % kvm_vmdk_path)
    print   "1. Success Copying Latest BVS VMDK to %s on KVM Host!!" % kvm_vmdk_path

def create_vm_on_kvm(**kwargs):
    virt_install_cmd = "sudo virt-install     \
                        --connect qemu:///system     \
                        -r 2048     \
                        --vcpus 2     \
                        -n %s     \
                        --disk path=%s,device=disk,format=vmdk     \
                        --import     --noautoconsole" % (vm_name, kvm_vmdk_path)
    helpers.log('Creating VM on KVM Host...')
    if "Domain creation completed." in kvm_handle.bash(virt_install_cmd)['content']:
        helpers.log("2. Success Creating VM with Name: %s on KVM_Host: %s" % (vm_name, kvm_host))
        print "2. Success Creating VM with Name: %s on KVM_Host: %s" % (vm_name, kvm_host)
        helpers.log("Current Running VMs on KVM_HOST : \n %s" % kvm_handle.bash('sudo virsh list --all')['content'])
    else:
        print "FAILURE CREATING VM  :( Need to debug ..."
        
def main(*args):
    global vm_name
    vm_name = current_user + '_' + args[0][0]
    print "Creating VM with Name : %s" % vm_name
    helpers.log("Creating VM with Name: %s " % vm_name)
    connect_to_kvm_host(hostname = kvm_host, user = kvm_user,
                                     password = kvm_pwd, name = 'kvm_host')
    if vm_name in kvm_handle.bash('sudo virsh list --all')['content']:
        helpers.log("VM with given name %s already exists in KVM Host %s\nExisting.." % (vm_name, kvm_host))
        print "VM with given name %s already exists in KVM Host %s\nPlease use different name\nExisting.." % (vm_name, kvm_host)
        sys.exit(1)
        
    scp_vmdk_to_kvm(kvm_handle = kvm_handle)
    create_vm_on_kvm()
    
if __name__ == '__main__':
    if len(sys.argv) < 2:
        usage()
    main(sys.argv[1:])

print "Success !!!"
    