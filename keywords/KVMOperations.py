import autobot.helpers as helpers
import autobot.test as test
import time
from autobot.devconf import HostDevConf
from keywords.T5Platform import T5Platform


KVM_SERVER = '10.192.104.13'
KVM_USER = 'root'
KVM_PASSWORD = 'bsn'


class KVMOperations(object):

    def __init__(self):
        pass
    def _virt_install_vm(self, **kwargs):
        kvm_handle = kwargs.get("kvm_handle", None)
        disk_path = kwargs.get("disk_path", None)
        vm_name = kwargs.get("vm_name", None)
        ram = kwargs.get("ram", "1024")
        vcpus = kwargs.get("cpus", "1")
        virt_install_cmd = "sudo virt-install \
                            --connect qemu:///system \
                            -r %s \
                            -n %s \
                            --vcpus=%s \
                            --disk path=%s,device=disk,format=qcow2 \
                            --import     --noautoconsole \
                            --network=bridge:br0,model=virtio \
                            --graphics vnc" % (ram, vm_name, vcpus, disk_path)
        helpers.log("Creating VM on KVM Host with virt-install cmd: \n%s..." % virt_install_cmd)
        if "Domain creation completed." in kvm_handle.bash(virt_install_cmd)['content']:
            return True
        else:
            return False

    def _destroy_vm(self, **kwargs):
        kvm_handle = kwargs.get("kvm_handle", None)
        vm_name = kwargs.get("vm_name", None)

        if "destroyed" in kvm_handle.bash("sudo virsh destroy %s" % vm_name)['content']:
            helpers.log ("1. Successfully Powered Down")
            return True
        else:
            helpers.log("Issue with Shutting down VM using virsh \nPlease debug on KVM Host \n Exiting..")
            return False

    def _undefine_vm(self, **kwargs):
        kvm_handle = kwargs.get("kvm_handle", None)
        vm_name = kwargs.get("vm_name", None)

        if "undefined" in kvm_handle.bash("sudo virsh undefine %s" % vm_name)['content']:
            helpers.log("2. Successfully Deleted !")
            return True
        else:
            helpers.log("Issue with Deleting VM using virsh \nPlease debug on KVM Host \n Exiting..")
            return False

    def _delete_vm_storage_file(self, **kwargs):
        kvm_handle = kwargs.get("kvm_handle", None)
        vm_name = kwargs.get("vm_name", None)
        kvm_handle.bash("sudo rm -rf /var/lib/libvirt/images/%s.qcow2" % vm_name)
        helpers.log("Success Removing Storage files of VM !!")
        return True

    def _connect_to_kvm_host(self, **kwargs):
        hostname = kwargs.get('hostname', KVM_SERVER)
        user = kwargs.get('user', KVM_USER)
        password = kwargs.get('password', KVM_PASSWORD)
        name = kwargs.get('name', "kvm_host")
        kvm_handle = HostDevConf(host=hostname, user=user, password=password,
                protocol='ssh', timeout=100, name=name)
        return kvm_handle

    def _get_vm_running_state(self, **kwargs):
        kvm_handle = kwargs.get("kvm_handle", None)
        vm_name = kwargs.get("vm_name", None)
        virsh_list_out = kvm_handle.bash('sudo virsh list --all | grep %s | awk \'{print $3}\'' % vm_name)['content']
        temp_list = virsh_list_out.split('\n')
        if len(temp_list) > 2:
            return temp_list[1]
        else:
            return ''
    def _cp_qcow_to_images_folder(self, **kwargs):
        '''
            Copy qcow image to uniquely created vm_name to avoid overrides of qcow images
        '''
        kvm_handle = kwargs.get("kvm_handle", None)
        qcow_path = kwargs.get("qcow_path", None)
        vm_name = kwargs.get("vm_name", None)
        kvm_handle.bash("sudo cp %s /var/lib/libvirt/images/%s.qcow2" % (qcow_path, vm_name))
        kvm_qcow_path = "/var/lib/libvirt/images/%s.qcow2" % vm_name
        helpers.log("Success copying image !!")
        return kvm_qcow_path

    def _scp_file_to_kvm_host(self, **kwargs):
        # for getting the latest jenkins build from jenkins server kvm_host ssh key should be copied to jenkins server
        vm_name = kwargs.get("vm_name", None)
        remote_qcow_path = kwargs.get("remote_qcow_path", None)
        kvm_handle = kwargs.get("kvm_handle", None)
        scp = kwargs.get("scp", True)
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

        # FIX ME For below SCP to work we need to have Kvm Pub Key in jenkins build server..
        if scp:
            helpers.log("Executing scp cmd to copy latest bvs vmdk to KVM Server")
            kvm_handle.bash('scp "bsn@jenkins:%s" .' % remote_qcow_path, timeout=100)['content']
        else:
            helpers.log("Skipping scp - expecting the VMDK already scp'ed to kvm_host..")
        file_name = remote_qcow_path.split('/')[-1]

        kvm_handle.bash('sudo cp %s ../images/%s.qcow2' % (file_name, vm_name))

        local_qcow_path = "/var/lib/libvirt/images/%s.qcow2" % vm_name
        # vm_name = "%s_BVS" % current_user
        return local_qcow_path

    def _create_temp_topo(self, vm_name, kvm_host=KVM_SERVER):
        # Creating a temp topo file for using first boot keywords
        topo_file = "/tmp/%s.topo" % vm_name
        topo = open(topo_file, "wb")
        config = " c1:\n\
          ip: 10.192.105.20\n\
          set_init_ping: false            # default: true\n\
          set_session_ssh: false          # default: true\n\
          console: \n\
            ip: %s\n\
            libvirt_vm_name: %s\n\
            user: %s\n\
            password: %s\n" % (kvm_host, vm_name, KVM_USER, KVM_PASSWORD)
        topo.write(config)
        topo.close()
        helpers.log("Success in creating topo file %s" % topo_file)
        return topo_file

    def _configure_vm_first_boot(self, **kwargs):
        # Using Mingtao's First Boot Function to configure spawned VM in KVM
        helpers.log("SLeeping 60 sec ..for VM to Boot UP....This time should bring down soon..")
        time.sleep(45)
        helpers.log("Success setting up gobot Env!")
        cluster_ip = kwargs.get("cluster_ip", None)
        ip_address = kwargs.get("ip_address", None)
        netmask = kwargs.get("netmask", "18")
        vm_host_name = kwargs.get("vm_host_name", None)

        t5_platform = T5Platform()
        # configure firstboot till IP address
        if ip_address is not None:
            helpers.summary_log("Static IP is given using ip: %s for VM" % ip_address)
            t5_platform.first_boot_controller_initial_node_setup("c1", ip_address=ip_address,
                                                                 netmask=netmask, hostname=vm_host_name)
        else:
            t5_platform.first_boot_controller_initial_node_setup("c1", dhcp="yes", hostname=vm_host_name)
        # Apply setting and add cluster Ip if provided
        if cluster_ip is not None:
            t5_platform.first_boot_controller_initial_cluster_setup("c1", join_cluster="yes",
                                                                    cluster_ip=cluster_ip)
            helpers.summary_log("Success Adding BVS VM to Cluster!")
        else:
            t5_platform.first_boot_controller_initial_cluster_setup("c1")

        new_ip_address = t5_platform.first_boot_controller_menu_apply("c1")
        helpers.summary_log("3. Success configuring first boot Controller IP : %s" % str(new_ip_address))
        return new_ip_address


    def vm_setup(self, **kwargs):
        result = {
                  "status_code": True,
                  "status_descr": "Success",
                  }

        try:
            kvm_host = kwargs.get("kvm_host", KVM_SERVER)
            kvm_user = kwargs.get("kvm_user", KVM_USER)
            kvm_password = kwargs.get("kvm_password", KVM_PASSWORD)
            vm_name = kwargs.get("vm_name", None)
            vm_host_name = kwargs.get("vm_host_name", None)
            vm_type = kwargs.get("vm_type", "bvs")
            qcow_path = kwargs.get("qcow_path", None)
            qcow_vm_path = None
            ip = kwargs.get("ip", None)
            if ip == 'None':
                ip = None
            cluster_ip = kwargs.get("cluster_ip", None)
            netmask = kwargs.get("netmask", "18")
            remote_qcow_bvs_path = kwargs.get("remote_qcow_bvs_path", "/var/lib/jenkins/jobs/bvs\ master/lastSuccessful/archive/target/appliance/images/bvs/controller-bvs-2.0.8-SNAPSHOT.qcow2")
            remote_qcow_mininet_path = kwargs.get("remote_qcow_mininet_path", "/var/lib/jenkins/jobs/t6-mininet-vm/builds/lastSuccessfulBuild/archive/t6-mininet-vm/ubuntu-kvm/t6-mininet.qcow2")
            scp = kwargs.get("scp", True)

            topo_file = self._create_temp_topo(kvm_host=kvm_host, vm_name=vm_name)
            # set the BIG ROBOT Topo file for console connections
            helpers.bigrobot_topology(topo_file)
            helpers.bigrobot_params("none")
            # export IS_GOBOT="False"
            # AUTOBOT_LOG=/tmp/robot.log
            helpers.set_env("AUTOBOT_LOG", "/tmp/%s.log" % vm_name)

            kvm_handle = self._connect_to_kvm_host(hostname=kvm_host, user=kvm_user, password=kvm_password)

            if vm_name in kvm_handle.bash('sudo virsh list --all')['content']:
                helpers.summary_log("VM with given name %s already exists in KVM Host %s" % (vm_name, kvm_host))
                return False

            if qcow_path is not None:
                helpers.log("QCOW path is provided using it locally NO SCP just copy to images..")
                qcow_vm_path = self._cp_qcow_to_images_folder(kvm_handle=kvm_handle, qcow_path=qcow_path,
                                                              vm_name=vm_name)
            else:
                helpers.log("no VMDK path is given copying from latest bvs build from jenkins server")
                if vm_type == 'mininet':
                    helpers.log("Scp'ing Latest Mininet qcow file from jenkins to kvm Host..")
                    qcow_vm_path = self._scp_file_to_kvm_host(kvm_handle=kvm_handle,
                                                              remote_qcow_path=remote_qcow_mininet_path)
                else:
                    if scp:
                        helpers.log("Scp'ing Latest BVS qcow file from jenkins to kvm Host..")
                        qcow_vm_path = self._scp_file_to_kvm_host(kvm_handle=kvm_handle,
                                                                  remote_qcow_path=remote_qcow_bvs_path,
                                                                  vm_name=vm_name)
                    else:
                        helpers.log("Skipping scp expecting latest BVS image already in KVM...")
                        qcow_path = "/var/lib/libvirt/bvs_images/controller-bvs-2.0.8-SNAPSHOT.qcow2"
                        qcow_vm_path = self._cp_qcow_to_images_folder(kvm_handle=kvm_handle, qcow_path=qcow_path,
                                                              vm_name=vm_name)

            helpers.log("Creating VM on KVM Host with Name : %s " % vm_name)
            self.create_vm_on_kvm_host(vm_type=vm_type, qcow_path=qcow_vm_path,
                                  vm_name=vm_name, kvm_handle=kvm_handle, kvm_host=kvm_host)
            result['vm_name'] = vm_name
            result['kvm_host'] = kvm_host
            result['image_path'] = qcow_vm_path
            result['vm_ip'] = ip
            result['content'] = helpers.file_read_once("/tmp/%s.log" % vm_name)

            if vm_type == 'mininet':
                # FIX ME configure mininet with user specified ip / return the DHCP ip of mininet VM
                helpers.log("Success Creating Mininet vm!!")
                helpers.log("Configuring IP for mininet if provided")
                self.set_mininet_ip(node="c1", ip=ip)
                return result

            # For controller, attempt First Boot
            result['vm_ip'] = self._configure_vm_first_boot(cluster_ip=cluster_ip,
                                                            ip_address=ip,
                                                            netmask=netmask,
                                                            vm_host_name=vm_host_name)
            return result
        except Exception as inst:
            helpers.log("Exception Details %s" % inst)
            result['status_code'] = False
            result['status_descr'] = inst
            return result

    def vm_teardown(self, vm_name, kvm_host=KVM_SERVER,
                    kvm_user=KVM_USER, kvm_password=KVM_PASSWORD):
        result = {
                  "vm_name": vm_name,
                  "status_code": True,
                  "status_descr": "Success",
                  }

        try:
            kvm_handle = self._connect_to_kvm_host(hostname=kvm_host,
                                                   user=kvm_user,
                                                   password=kvm_password)
            vm_state = self._get_vm_running_state(kvm_handle=kvm_handle,
                                                  vm_name=vm_name)
            if 'running' in vm_state:
                helpers.summary_log("Tearing down VM with Name on kvm host: %s"
                                    % vm_name)
                self._destroy_vm(kvm_handle=kvm_handle, vm_name=vm_name)
                self._undefine_vm(kvm_handle=kvm_handle, vm_name=vm_name)
            elif 'shut' in vm_state:
                helpers.summary_log("Deleting down the VM : %s" % vm_name)
                self._undefine_vm(kvm_handle=kvm_handle, vm_name=vm_name)
            else:
                helpers.summary_log("VM with given name %s doesn't exists on KVM host! %s"
                                    % (vm_name, kvm_host))
                result['status_code'] = False
                result['status_descr'] = "VM name doesn't exist on KVM host"
                return result
            self._delete_vm_storage_file(kvm_handle=kvm_handle, vm_name=vm_name)
            return result
        except Exception as inst:
            helpers.log("Exception Details %s" % inst)
            result['status_code'] = False
            result['status_descr'] = inst
            return result

    def set_mininet_ip(self, **kwargs):
        t = test.Test()
        node = kwargs.get("node", "c1")
        ip = kwargs.get("ip", None)
        prompt = kwargs.get("prompt", "~$ ")
        n = t.node(node)


        if not ip:
            ip = n.ip()

        helpers.log("Setting IP : %s for Linux Node : %s using ifconfig"
                    % (ip, node))
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
        kvm_vmdk_path = kwargs.get("qcow_path", None)
        vm_name = kwargs.get("vm_name", None)
        kvm_handle = kwargs.get("kvm_handle", None)
        kvm_host = kwargs.get("kvm_host", None)

        vm_creation = False

        if vm_type == "mininet":
            vm_creation = self._virt_install_vm(kvm_handle=kvm_handle, disk_path=kvm_vmdk_path,
                                                vm_name=vm_name)
        else:
            vm_creation = self._virt_install_vm(kvm_handle=kvm_handle, disk_path=kvm_vmdk_path,
                                                vm_name=vm_name, ram="2048", cpus="2")

        if vm_creation:
            helpers.summary_log("2. Success Creating VM with Name: %s on KVM_Host: %s" % (vm_name, kvm_host))
            helpers.log("Current Running VMs on KVM_HOST : \n %s" % kvm_handle.bash('sudo virsh list --all')['content'])
        else:
            helpers.summary_log("FAILURE CREATING VM  :( Need to debug ...")
