import os
import errno
import time
import autobot.helpers as helpers
import autobot.test as test
import time
import re
from autobot.devconf import HostDevConf, ControllerDevConf
from keywords.T5Platform import T5Platform


KVM_SERVER = helpers.bigrobot_kvm_server()
KVM_USER = 'root'
KVM_PASSWORD = 'bsn'
JENKINS_SERVER = helpers.bigrobot_jenkins_server()
JENKINS_USER = 'bsn'
JENKINS_PASSWORD = 'bsn'
DEFAULT_GATEWAY = '10.8.0.1'
LOG_BASE_PATH = '/var/log/vm_operations'


class KVMOperations(object):

    def __init__(self):
        global LOG_BASE_PATH
        # Note: You might need to manually create the directory for
        # LOG_BASE_PATH since the execution process may not have root
        # permission. E.g.,
        #   # mkdir /var/log/kvm_operations
        #   # chown bsn:bsn /var/log/kvm_operations
        #   # chmod 775 /var/log/kvm_operations
        try:
            if os.path.exists(LOG_BASE_PATH) or os.path.islink(LOG_BASE_PATH):
                pass
            else:
                os.makedirs(LOG_BASE_PATH)
        except OSError as exc:  # Python >2.5
            if exc.errno == errno.EEXIST and os.path.isdir(LOG_BASE_PATH):
                pass
            else:
                # Last resort - put logs in /tmp
                LOG_BASE_PATH = '/tmp'

        self.log_path = None

    def _virt_install_vm(self, **kwargs):
        kvm_handle = kwargs.get("kvm_handle", None)
        disk_path = kwargs.get("disk_path", None)
        vm_name = kwargs.get("vm_name", None)
        ram = kwargs.get("ram", "1024")
        vcpus = kwargs.get("cpus", "1")
        network_interface = kwargs.get("network_interface", "br0")
        virt_install_cmd = ("sudo virt-install"
                            " --connect qemu:///system"
                            " -r %s"
                            " -n %s"
                            " --vcpus=%s"
                            " --disk path=%s,device=disk,format=qcow2"
                            " --import --noautoconsole"
                            " --network=bridge:%s,model=virtio"
                            " --graphics vnc"
                            % (ram, vm_name, vcpus, disk_path, network_interface))
        helpers.log("Creating VM on KVM host:\n%s" % virt_install_cmd)
        content = kvm_handle.bash(virt_install_cmd)['content']
        if "Domain creation completed." in content:
            return True
        else:
            return False

    def _destroy_vm(self, **kwargs):
        kvm_handle = kwargs.get("kvm_handle", None)
        vm_name = kwargs.get("vm_name", None)

        if "destroyed" in kvm_handle.bash("sudo virsh destroy %s" % vm_name)['content']:
            helpers.log ("Successfully powered down VM (destroyed)")
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
        # JENKINS sets the default TERM to dumb changing to xterm
        helpers.log("ENV after connecting to KVM HOST:\n%s" % kvm_handle.bash('env')['content'])
        kvm_handle.bash('export TERM=xterm')
        helpers.log("ENV after setting  TERM KVM HOST:\n%s" % kvm_handle.bash('env')['content'])
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
        qcow_path = qcow_path.replace(" ", "\ ")
        kvm_handle.bash("sudo cp %s /var/lib/libvirt/images/%s.qcow2" % (qcow_path, vm_name))
        kvm_qcow_path = "/var/lib/libvirt/images/%s.qcow2" % vm_name
        helpers.log("Success copying image !!")
        return kvm_qcow_path

    def _get_latest_jenkins_build_number(self, vm_type='bcf',
                                         jenkins_server=JENKINS_SERVER,
                                         jenkins_user=JENKINS_USER,
                                         jenkins_password=JENKINS_PASSWORD, jenkins_project_name=None):
        jenkins_handle = HostDevConf(host=jenkins_server, user=jenkins_user, password=jenkins_password,
                    protocol='ssh', timeout=100, name="jenkins_host")
        output = None
        if vm_type == 'bcf':
            if jenkins_project_name is not None:
                output = jenkins_handle.bash('ls -ltr /var/lib/jenkins/jobs/%s/builds | grep lastSuccessfulBuild' % jenkins_project_name)['content']
            else:
                output = jenkins_handle.bash('ls -ltr /var/lib/jenkins/jobs/bcf_master/builds | grep lastSuccessfulBuild')['content']
        elif vm_type == 'mininet':
            output = jenkins_handle.bash('ls -ltr /var/lib/jenkins/jobs/t6-mininet-vm/builds | grep lastSuccessfulBuild')['content']

        output_lines = output.split('\n')
        latest_build_number = output_lines[1].split('->')[-1]
        return latest_build_number.strip()

    def _get_latest_kvm_build_number(self, vm_type='bcf', kvm_handle=None, jenkins_project_name="bcf_master"):
        output = None
        if vm_type == 'bcf':
            output = kvm_handle.bash('ls -ltr /var/lib/libvirt/bvs_images/ | grep %s | awk \'{print $9}\'' % jenkins_project_name)['content']
            output_lines = output.split('\n')
            latest_image = output_lines[-2]
            match = re.match(r'.*%s-(\d+).*' % jenkins_project_name, latest_image)
            if match:
                return match.group(1)
            else:
                return 0
        elif vm_type == 'mininet':
            output = kvm_handle.bash('ls -ltr /var/lib/libvirt/bvs_images/ | grep mininet| awk \'{print $9}\'')['content']
            output_lines = output.split('\n')
            latest_image = output_lines[-2]
            match = re.match(r'.*mininet-(\d+).*', latest_image)
            if match:
                return match.group(1)
            else:
                return 0


    def _scp_file_to_kvm_host(self, vm_name=None, remote_qcow_path=None, kvm_handle=None, vm_type="bcf", build_number=None, scp=True):
        # for getting the latest jenkins build from jenkins server kvm_host ssh key should be copied to jenkins server
        output = kvm_handle.bash('uname -a')
        helpers.log("KVM Host Details : \n %s" % output['content'])
        kvm_handle.bash('cd /var/lib/libvirt/')
        helpers.log (" GOT VM_TYPE : %s" % vm_type)

        if "No such file or directory" in kvm_handle.bash('cd bvs_images/')['content']:
            helpers.log("No BVS_IMAGES dir in KVM Host @ /var/lib/libvirt creating one to store bvs vmdks")
            kvm_handle.bash('sudo mkdir bvs_images')
            kvm_handle.bash('sudo chmod -R 777 bvs_images/')
        else:
            helpers.log('BVS_IMAGES dir exists in KVM Host @ /var/lib/libvirt/bvs_images/ copying latest vmdkd from jenkins server')

        kvm_handle.bash('sudo chmod -R 777 ../bvs_images/')
        kvm_handle.bash('cd bvs_images')
        helpers.log("Latest VMDK will be copied to location : %s at KVM Host" % kvm_handle.bash('pwd')['content'])
        helpers.log("Executing Scp cmd to copy latest bvs vmdk to KVM Server")
        jenkins_project_name = None
        if remote_qcow_path is not None:
            match = re.match(r'/var/lib/jenkins/jobs/(.*)/lastSuccessful/', remote_qcow_path)
            if match:
                jenkins_project_name = match.group(1)
        helpers.summary_log("Using Jenkins Project Name: %s" % jenkins_project_name)
        latest_build_number = self._get_latest_jenkins_build_number(vm_type, jenkins_project_name=jenkins_project_name)
        latest_kvm_build_number = self._get_latest_kvm_build_number(vm_type, kvm_handle, jenkins_project_name=jenkins_project_name)
        if build_number is not None:
            helpers.log("Build Number is provided resetting latest builds to %s" % build_number)
            latest_build_number = build_number
            latest_kvm_build_number = build_number
        file_name = None
        if vm_type == 'bcf':
            if jenkins_project_name == "bcf_master":
                file_name = "controller-jf_bcf_virtual-%s.qcow2" % (latest_build_number)
            else:
                file_name = "controller-%s_virtual-%s.qcow2" % (jenkins_project_name, latest_build_number)
            helpers.log("Adding virtual tag to build file Name : %s" % file_name)
        elif vm_type == 'mininet':
            file_name = "mininet-%s.qcow2" % latest_build_number
        helpers.log("Latest Build Number on KVM Host: %s" % latest_kvm_build_number)
        helpers.log("Latest Build Number on Jenkins: %s" % latest_build_number)

        if str(latest_kvm_build_number) == str(latest_build_number) and scp:
            helpers.log("Skipping SCP as the latest build on jenkins server did not change from the latest on KVM Host")

        else:
            scp_cmd = ('scp -o "UserKnownHostsFile=/dev/null" -o StrictHostKeyChecking=no "%s@%s:%s" %s'
                       % (JENKINS_USER, JENKINS_SERVER, remote_qcow_path, file_name))
            helpers.log("SCP command arguments:\n%s" % scp_cmd)
            scp_cmd_out = kvm_handle.bash(scp_cmd, prompt=[r'.*password:', r'.*#', r'.*$ '])['content']
            if "password" in scp_cmd_out:
                helpers.log("sending bsn password..")
                helpers.log(kvm_handle.bash('bsn')['content'])
            else:
                helpers.log("SCP should be done:\n%s" % scp_cmd_out)
            helpers.summary_log("Success SCP'ing latest Jenkins build !!")
        helpers.summary_log("Using Jenkins Build #%s (image name: '%s')" % (latest_build_number, file_name))
        helpers.log("Setting BUILD_NUM Env...")
        helpers.set_env("BUILD_NUM", str(latest_build_number))
        helpers.log("env BUILD_NUM: %s" % helpers.get_env("BUILD_NUM"))
        kvm_handle.bash('sudo cp %s ../images/%s.qcow2' % (file_name, vm_name))

        local_qcow_path = "/var/lib/libvirt/images/%s.qcow2" % vm_name
        # vm_name = "%s_BVS" % current_user
        return local_qcow_path

    def _create_temp_topo(self, vm_name, kvm_host=KVM_SERVER):
        # Creating a temp topo file for using first boot keywords
        topo_file = "%s/%s.topo" % (self.log_path, vm_name)
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

    def _configure_vm_first_boot(self, cluster_ip=None, ip_address=None,
                                 netmask='18', vm_host_name=None,
                                 gateway=DEFAULT_GATEWAY):
        # Using Mingtao's First Boot Function to configure spawned VM in KVM
        helpers.log("Sleeping 60 sec while waiting for VM to boot up")
        time.sleep(120)
        helpers.log("Success setting up gobot Env!")

        t5_platform = T5Platform()
        # configure firstboot till IP address
        if ip_address is not None:
            helpers.summary_log("Static IP is given using ip: %s netmask: %s, gateway: %s for VM" %
                                (ip_address, netmask, gateway))
            t5_platform.first_boot_controller_initial_node_setup("c1", ip_address=ip_address,
                                                                 netmask=netmask, hostname=vm_host_name,
                                                                 gateway=gateway)
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
            vm_name = kwargs.get("vm_name", None)
            kvm_host = kwargs.get("kvm_host", KVM_SERVER)
            kvm_user = kwargs.get("kvm_user", KVM_USER)
            kvm_password = kwargs.get("kvm_password", KVM_PASSWORD)
            vm_host_name = kwargs.get("vm_host_name", None)
            vm_type = kwargs.get("vm_type", "bcf")
            qcow_path = kwargs.get("qcow_path", None)
            qcow_vm_path = None
            ip = kwargs.get("ip", None)
            vm_ram = kwargs.get("vm_ram", "2048")
            build_number = kwargs.get("build_number", None)
            if ip == 'None':
                ip = None
            cluster_ip = kwargs.get("cluster_ip", None)
            netmask = kwargs.get("netmask", "18")
            gateway = kwargs.get("gateway", "10.8.0.1")
            network_interface = kwargs.get("network_interface", "br0")
            self.log_path = LOG_BASE_PATH + '/' + vm_name
            try:
                if os.path.exists(self.log_path) or os.path.islink(self.log_path):
                    pass
                else:
                    os.makedirs(self.log_path)
            except OSError as exc:  # Python >2.5
                if exc.errno == errno.EEXIST and os.path.isdir(LOG_BASE_PATH):
                    pass
                else:
                    # Last resort - put logs in /tmp
                    self.log_path = '/tmp' + '/' + vm_name
                    os.makedirs(self.log_path)

            # export IS_GOBOT="False"
            helpers.set_env("AUTOBOT_LOG", "%s/%s.log"
                            % (self.log_path, vm_name))
            helpers.bigrobot_log_path_exec_instance(self.log_path)

            # Note: helpers.summary_log() and helpers.log() are not called
            #       until after we've initialized the BigRobot log path
            #       (above). Don't attempt to write to logs before that
            #       or it will write logs to /tmp directory instead of the
            #       /tmp/<vm_name>/.
            helpers.summary_log("Creating VM with Name: %s " % vm_name)
            helpers.summary_log("Created log_path %s" % self.log_path)
            # remote_qcow_bvs_path = kwargs.get("remote_qcow_bvs_path", "/var/lib/jenkins/jobs/bvs\ master/lastSuccessful/archive/target/appliance/images/bcf/controller-bcf-2.0.8-SNAPSHOT.qcow2")
            remote_qcow_bvs_path = kwargs.get("remote_qcow_bvs_path", "/var/lib/jenkins/jobs/bcf_master/lastSuccessful/archive/controller-bcf-*.qcow2")
            remote_qcow_mininet_path = kwargs.get("remote_qcow_mininet_path", "/var/lib/jenkins/jobs/t6-mininet-vm/builds/lastSuccessfulBuild/archive/t6-mininet-vm/ubuntu-kvm/t6-mininet.qcow2")

            topo_file = self._create_temp_topo(kvm_host=kvm_host, vm_name=vm_name)
            # set the BIG ROBOT Topo file for console connections
            helpers.bigrobot_topology(topo_file)
            helpers.bigrobot_params("none")

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
                                                              remote_qcow_path=remote_qcow_mininet_path, vm_type='mininet',
                                                              vm_name=vm_name, build_number=build_number)
                else:
                    helpers.log("Scp'ing Latest BVS qcow file %s from jenkins to kvm Host.." % remote_qcow_bvs_path)
                    qcow_vm_path = self._scp_file_to_kvm_host(kvm_handle=kvm_handle,
                                                              remote_qcow_path=remote_qcow_bvs_path,
                                                              vm_name=vm_name, build_number=build_number)

            helpers.log("Creating VM on KVM Host with Name : %s " % vm_name)
            self.create_vm_on_kvm_host(vm_type=vm_type,
                                       qcow_path=qcow_vm_path,
                                       vm_name=vm_name,
                                       kvm_handle=kvm_handle,
                                       kvm_host=kvm_host,
                                       network_interface=network_interface, vm_ram=vm_ram)
            result['vm_name'] = vm_name
            result['kvm_host'] = kvm_host
            result['image_path'] = qcow_vm_path
            result['vm_ip'] = ip
#             result['content'] = helpers.file_read_once("%s/%s.log"
#                                                        % (self.log_path,
#                                                           vm_name))

            if vm_type == 'mininet':
                # FIX ME configure mininet with user specified ip / return the DHCP ip of mininet VM
                helpers.log("Success Creating Mininet vm!!")
                helpers.log("Configuring IP for mininet if provided")
                result['vm_ip'] = self.set_mininet_ip(node="c1", ip=ip, get_ip=True)
                return result

            # For controller, attempt First Boot
            helpers.log("SLeep another 60 sec for controller to boot up..")
            time.sleep(30)
            result['vm_ip'] = self._configure_vm_first_boot(cluster_ip=cluster_ip,
                                                            ip_address=ip,
                                                            netmask=netmask,
                                                            vm_host_name=vm_host_name,
                                                            gateway=gateway)
            helpers.summary_log("Copying firstboot-config on New Controller: %s" % result['vm_ip'])
            helpers.sleep(10)
            bvs = ControllerDevConf(host=result['vm_ip'], user="admin", password="adminadmin", name="test-bvs")
            bvs.config("copy running-config snapshot://firstboot-config")
            helpers.summary_log("Success saving firstboot-config")

            helpers.summary_log("Done! Logs are written to %s" % self.log_path)
            return result
        except:
            inst = helpers.exception_info_traceback()
            helpers.log("Exception Details:\n%s" % inst)
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
            helpers.summary_log("vm_State: %s\n" % str(vm_state))
            if re.match(r'.*running.*', vm_state) or re.match(r'.*paused.*', vm_state):
                helpers.summary_log("Tearing down VM with Name:%s on kvm host: %s"
                                    % (vm_name, kvm_host))
                self._destroy_vm(kvm_handle=kvm_handle, vm_name=vm_name)
                self._undefine_vm(kvm_handle=kvm_handle, vm_name=vm_name)
                helpers.log("Checking The State of Vm : %s" % vm_name)
                new_vm_state = self._get_vm_running_state(kvm_handle=kvm_handle, vm_name=vm_name)
                helpers.log(" new vm_state : %s" % new_vm_state)
                if new_vm_state != '':
                    helpers.log("Vm still alive trying to destroy again..")
                    self.vm_teardown(vm_name, kvm_host, kvm_user, kvm_password)
                else:
                    helpers.log("Vm Is Dead!")
            elif re.match(r'.*shut.*', vm_state):
                helpers.summary_log("Deleting down the VM : %s on KVM_HOST: %s" % (vm_name, kvm_host))
                self._undefine_vm(kvm_handle=kvm_handle, vm_name=vm_name)
            else:
                helpers.summary_log("VM with given name %s doesn't exists on KVM host! %s"
                                    % (vm_name, kvm_host))
                result['status_code'] = False
                result['status_descr'] = "VM name doesn't exist on KVM host"
                return result
            self._delete_vm_storage_file(kvm_handle=kvm_handle, vm_name=vm_name)
            return result
        except:
            inst = helpers.exception_info_traceback()
            helpers.log("Exception Details:\n%s" % inst)
            result['status_code'] = False
            result['status_descr'] = inst
            return result

    def set_mininet_ip(self, **kwargs):
        t = test.Test()
        node = kwargs.get("node", "c1")
        ip = kwargs.get("ip", None)
        get_ip = kwargs.get("get_ip", True)
        n = t.node(node)

        helpers.log("Sleeping 30 sec from mininet to come up..")
        time.sleep(45)
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
        options = n_console.expect([r't6-mininet login: ', n_console.get_prompt()])
        if options[0] == 1:
            helpers.log("Autotomatci Mininet Log is enabled no need to log into mininet..")
        else:
            helpers.log("Sending mininet password..")
            n_console.send('mininet')
            n_console.expect(r'Password: ')
            n_console.send('mininet')
        time.sleep(1)
#         n_console.bash('pwd')
#         n_console.expect()
        if get_ip:
            helpers.log("Just getting DHCP IP from Mininet VM ..")
            n_console.send('sudo ifconfig | grep inet | awk \'{print $2}\'')
            time.sleep(1)
            output = n_console.content()
            output_lines = output.split('\n')
            helpers.log("Mininet IP Content:")
            ips = output_lines[1].split(':')
            helpers.log("Mininet IP is : %s" % ips[1])
            return ips[1]
        else:
            helpers.log("Setting IP on Mininet VM ...")
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
        vm_name = kwargs.get("vm_name", None)
        vm_type = kwargs.get("vm_type", "bcf")
        kvm_vmdk_path = kwargs.get("qcow_path", None)
        kvm_handle = kwargs.get("kvm_handle", None)
        kvm_host = kwargs.get("kvm_host", None)
        network_interface = kwargs.get("network_interface", None)
        vm_ram = kwargs.get("vm_ram", "2048")

        vm_creation = False

        if vm_type == "mininet":
            vm_creation = self._virt_install_vm(kvm_handle=kvm_handle, disk_path=kvm_vmdk_path,
                                                vm_name=vm_name, network_interface=network_interface)
        else:
            vm_creation = self._virt_install_vm(kvm_handle=kvm_handle, disk_path=kvm_vmdk_path,
                                                vm_name=vm_name, ram=vm_ram, cpus="8", network_interface=network_interface)

        if vm_creation:
            helpers.summary_log("2. Success Creating VM with Name: %s on KVM_Host: %s" % (vm_name, kvm_host))
            helpers.log("Current Running VMs on KVM_HOST : \n %s" % kvm_handle.bash('sudo virsh list --all')['content'])
        else:
            helpers.summary_log("FAILURE CREATING VM  :( Need to debug ...")

    def virsh_cmd(self, node=None, virsh_cmd=None):
        '''

        '''
        t = test.Test()
        if node is None:
            helpers.log("Please provide Host name of the Kvm Host to perform Virsh cmds...")
            return True
        kvm_host = t.host(node)
        kvm_host.bash(virsh_cmd)
        helpers.log("Success executing virsh cmd..")
