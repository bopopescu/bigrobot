import autobot.helpers as helpers
import autobot.test as test
import time

class KVMOperations(object):

    def __init__(self):
        pass 
    
    def set_mininet_ip(self, **kwargs):
        t = test.Test()
        node = kwargs.get("node", "c1")
        ip = kwargs.get("ip", None)
        prompt = kwargs.get("prompt", "~$ ")
        n = t.node(node)
        
        
        if not ip:
            ip = n.ip()
        
        helpers.log("Setting IP : %s for Linux Node : %s using ifconfig" % (ip, node))
        n_console = n.console()
        n_console.send('')
#         helpers.log("Sleeping 20 secs...")
#         time.sleep(20)
        n_console.expect(r'Escape character.*[\r\n]')
        n_console.send('')
        n_console.send('')
        n_console.expect(r't6-mininet login: ')
        n_console.send('mininet')
        n_console.expect(r'Password: ')
        n_console.send('mininet')
        time.sleep(1)
        n_console.expect()
#         n_console.bash('pwd')
#         n_console.expect()
        n_console.send('sudo ifconfig eth0 %s netmask 255.255.192.0' % ip)
        n_console.expect()
        helpers.log("Success configuring Static IP !!")
        """
        n_console.expect(r'%s' % prompt)
        n_console.send('ifconfig')
        n_console.expect(r'%s'% prompt)
        n_console.send('sudo ifconfig eth0 %s netmask 255.255.192.0' % ip)
        n_console.expect(r'%s'% prompt)
        n_console.send('ifconfig')
        n_console.send('')
        n_console.expect(r'%s'% prompt)
        content = n_console.content()
        helpers.log("*****Output is :*******\n%s" % content)
        """
    def create_vm_on_kvm_host(self, **kwargs):
        vm_type = kwargs.get("vm_type", "bvs")
        kvm_vmdk_path = kwargs.get("vmdk_path", None)
        vm_name = kwargs.get("vm_name", None)
        kvm_handle = kwargs.get("kvm_handle", None)
        kvm_host = kwargs.get("kvm_host", None)
        kvm_vmdk_path1 = kwargs.get("vmdk_path1", None)
        vm_backup_name = kwargs.get("vm_backup_name", None)
        
        
        if vm_type == "mininet":
            virt_install_cmd = "sudo virt-install     \
                            --connect qemu:///system     \
                            -r 1024     \
                            -n %s     \
                            --disk path=%s,device=disk,format=vmdk     \
                            --import     --noautoconsole    \
                            --network=bridge:br0,model=virtio    \
                            --graphics vnc" % (vm_name, kvm_vmdk_path)
            
        else:
            virt_install_cmd = "sudo virt-install     \
                            --connect qemu:///system     \
                            -r 2048     \
                            --vcpus 2     \
                            -n %s     \
                            --disk path=%s,device=disk,format=vmdk     \
                            --import     --noautoconsole    \
                            --network=bridge:br0,model=virtio" % (vm_name, kvm_vmdk_path)
        helpers.log("Creating VM on KVM Host with virt-install cmd: \n%s..." % virt_install_cmd)
        if "Domain creation completed." in kvm_handle.bash(virt_install_cmd)['content']:
            helpers.log("2. Success Creating VM with Name: %s on KVM_Host: %s" % (vm_name, kvm_host))
            print "2. Success Creating VM with Name: %s on KVM_Host: %s" % (vm_name, kvm_host)
            helpers.log("Waiting for VM to boot up..")
            time.sleep(30)
            helpers.log("Current Running VMs on KVM_HOST : \n %s" % kvm_handle.bash('sudo virsh list --all')['content'])
        else:
            print "FAILURE CREATING VM  :( Need to debug ..."
        
        if kvm_vmdk_path1 is not None:
            virt_install_cmd = "sudo virt-install     \
                            --connect qemu:///system     \
                            -r 2048     \
                            --vcpus 2     \
                            -n %s     \
                            --disk path=%s,device=disk,format=vmdk     \
                            --import     --noautoconsole    \
                            --network=bridge:br0,model=virtio" % (vm_backup_name, kvm_vmdk_path1)
            helpers.log("Creating VM on KVM Host with virt-install cmd: \n%s..." % virt_install_cmd)
            if "Domain creation completed." in kvm_handle.bash(virt_install_cmd)['content']:
                helpers.log("2-a. Success Creating VM with Name: %s on KVM_Host: %s" % (vm_backup_name, kvm_host))
                print "2-a. Success Creating VM with Name: %s on KVM_Host: %s" % (vm_backup_name, kvm_host)
                helpers.log("Waiting for VM to boot up..")
                time.sleep(20)
                helpers.log("Current Running VMs on KVM_HOST : \n %s" % kvm_handle.bash('sudo virsh list --all')['content'])
            else:
                print "FAILURE CREATING VM  :( Need to debug ..."