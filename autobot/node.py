import autobot.devconf as devconf
import autobot.helpers as helpers
from autobot.bsn_restclient import BsnRestClient


class Node(object):
    def __init__(self, name, ip, user=None, password=None, params=None,
                 protocol=None):
        if not name:
            helpers.environment_failure("Node name is not defined")

        self._name = name
        self._user = user
        self._password = password
        self._ip = None
        self._console_info = None
        self.http_port = None
        self.base_url = None
        self.params = params
        self.is_pingable = False
        self.rest = None  # REST handle
        self.dev = None  # DevConf handle (SSH)
        self.dev_console = None  # Console handle
        self.dev_debug_level = 0

        # If name are in the form 'node-<ip_addr>', e.g., 'node-10.193.0.43'
        # then they are nodes spawned directly by the user. Don't try to
        # look up their attributes in params since they are not defined.
        if params and not name.startswith('node-'):
            self.node_params = self.params[name]
            val = helpers.params_val('set_devconf_debug_level',
                                     self.node_params)
            if val is not None:
                self.dev_debug_level = val
                helpers.log("Devconf for '%s' set to debug level %s"
                            % (name, self.dev_debug_level))
        else:
            self.node_params = {}

        self._port = self.node_params.get('port', None)
        self._protocol = protocol if protocol else self.node_params.get('protocol', 'ssh')
        self._privatekey = self.node_params.get('privatekey', None)
        self._privatekey_password = self.node_params.get(
                                            'privatekey_password', None)
        self._privatekey_type = self.node_params.get('privatekey_type', None)
        self._hostname = self.node_params.get('hostname', None)

        if not ip:
            if helpers.params_is_false('set_session_ssh', self.node_params):
                # set_session_ssh is False, so IP address doesn't have to be
                # defined
                pass
            else:
                helpers.environment_failure(
                            "Node IP address is not defined for '%s'"
                            % name)
        else:
            self._ip = ip.lower()  # IP might be 'dummy'

        if self.ip() == 'dummy':
            helpers.environment_failure("IP address for '%s' is 'dummy'."
                                        " Needs to be populated."
                                        % self.name())
        if helpers.is_esb():
            helpers.summary_log("ESB environment - bypassing initial ping")

        elif helpers.params_is_false('set_init_ping', self.node_params):
            helpers.log("'set_init_ping' is disabled for '%s', bypassing"
                        " initial ping"
                        % name)
        else:
            self.pingable_or_die()

    def name(self):
        return self._name

    def hostname(self):
        return self._hostname

    def ip(self):
        return self._ip

    def alias(self):
        return self.node_params.get('alias', None)

    def node_id(self):
        """
        Node-id is mainly supported for BVS platform but that may change over
        time. For now, all derived nodes should simply return None.
        """
        return None

    def user(self):
        return self._user

    def password(self):
        return self._password

    def platform(self):
        if self.dev:
            return self.dev.platform()
        return 'undef'

    def pingable_or_die(self):
        if self.is_pingable:
            return True
        if self.ip() is None:
            helpers.environment_failure("Ping failure - Node '%s' does not"
                                        " have an IP address defined"
                                        % self.name())
        helpers.log("Ping %s ('%s')" % (self.ip(), self.name()))
        loss = helpers.ping(self.ip(), count=6, loss=50)
        if  loss > 50:
            # We can tolerate 50% loss.
            # Consider init to be completed, so as not to be invoked again.
            helpers.environment_failure("Ping failure - Node '%s' with IP"
                                        " address %s is unreachable."
                                        % (self.name(), self.ip()))
        self.is_pingable = True
        return True

    def _match_console_banner(self):
        try:
            self.dev_console.expect(r'Escape character is.*', timeout=10)
        except:
            helpers.log("Could not find console signature"
                        " 'Escape character is ^]' - matching everything"
                        " as last resort")
            self.dev_console.expect(r'.*', timeout=10)

    def console(self, driver=None, force_reconnect=False):
        """
        Inheriting class needs to further extend this method.
        """
        if self.dev_console and not force_reconnect:
            return self.dev_console
        else:
            helpers.log("Reconnecting to console for node '%s'" % self.name())

        if 'console' in self.node_params:
            self._console_info = self.node_params['console']
        else:
            helpers.environment_failure(
                            "Console info is not defined for node '%s'"
                            % self.name())

        if 'ip' in self._console_info:
            if self._console_info.get('libvirt_vm_name', None):
                self._console_info['type'] = 'libvirt'
                self._console_info['protocol'] = 'ssh'
                self._console_info['port'] = None
            elif self._console_info.get('port', None):
                self._console_info['type'] = 'telnet'
                self._console_info['protocol'] = 'telnet'
            else:
                helpers.environment_failure("Supported console types are"
                                            " telnet (IP and port) and libvirt"
                                            " (IP and VM name)")
        else:
            helpers.environment_failure("Console needs an IP and a port or"
                                        " VM name (for libvirt)")

        if 'user' not in self._console_info:
            self._console_info['user'] = self.user()
        if 'password' not in self._console_info:
            self._console_info['password'] = self.password()

        if driver:
            self._console_info['driver'] = driver
        elif self.dev:
            # helpers.log("driver: %s" % self.dev.driver().name())
            # self._console_info['driver'] = self.dev.driver().name()
            helpers.log("driver: %s" % self.dev.driver())
            self._console_info['driver'] = self.dev.driver()
        else:
            self._console_info['driver'] = None

        helpers.log("Using devconf driver '%s' for console to '%s'"
                    % (self._console_info['driver'], self.name()))

        # This is where we need to instantiate a devconf object,
        # if applicable.

        return self.dev_console

    def console_reconnect(self, driver=None):
        raise NotImplementedError()

    def console_close(self):
        """
        Exit out the current console session.
        For libvirt, it's simply:
            ^]
        For telnet, it's:
            ^]
            telnet> quit
        """
        h = self.console()
        if self._console_info['type'] == 'libvirt':
            h.send(helpers.ctrl(']'))
        elif self._console_info['type'] == 'telnet':
            h.send(helpers.ctrl(']'))
            # h.expect(r'telnet> ')
            # h.send('quit')
        h.close()
        self.dev_console = None

    def connect(self, user, password, port=None, protocol='ssh', host=None,
                name=None):
        """
        Connect to the node using either ssh or telnet.
        Returns the session handle.
        """
        raise NotImplementedError()

    def devconf(self):
        """
        Returns the devconf handle.
        """
        # raise NotImplementedError()
        return None

    def close(self):
        if self.devconf() == None:
            helpers.log("Devconf is undefined for '%s' - no disconnect"
                        % self.name())
        else:
            self.devconf().close()


class ControllerNode(Node):
    def __init__(self, name, ip, user, password, t, protocol=None):
        super(ControllerNode, self).__init__(name, ip, user, password,
                                             t.topology_params(),
                                             protocol=protocol)

        self._monitor_reauth = False  # default

        # Note: Must be initialized before BsnRestClient since we need the
        # CLI for platform info and also to configure the firewall for REST
        # access

        # Note: SSH is required for both DevConf and RestClient to be
        # instantiated. These sessions go together.
        if (not t.init_completed()
            and helpers.params_is_false('set_session_ssh',
                                        self.node_params)):
            helpers.log("'set_session_ssh' is disabled for '%s', bypassing"
                        " node SSH and RestClient session setup"
                        % name)
            return

        if 'monitor_reauth' in self.node_params:
            self._monitor_reauth = self.node_params['monitor_reauth']

        helpers.log("name=%s host=%s user=%s password=%s"
                    % (name, ip, user, password))
        self.dev = self.connect(name=name,
                                host=ip,
                                user=user,
                                password=password,
                                protocol=protocol)

        if 'http_port' in self.node_params:
            self.http_port = self.node_params['http_port']
        else:
            if helpers.is_bvs(self.platform()):
                self.http_port = 8443
            elif helpers.is_bigtap(self.platform()):
                self.http_port = 8000

        if 'base_url' in self.node_params:
            self.base_url = self.node_params['base_url'] % (ip, self.http_port)
        else:
            self.base_url = 'http://%s:%s' % (ip, self.http_port)

        self.rest = BsnRestClient(name=name,
                                  base_url=self.base_url,
                                  platform=self.platform(),
                                  host=ip,
                                  user=user,
                                  password=password,
                                  http_port=self.http_port)
        self.t = t

        # CLI Shortcuts
        self.cli = self.dev.cli  # CLI mode
        self.enable = self.dev.enable  # Enable mode
        self.config = self.dev.config  # Configuration mode
        self.bash = self.dev.bash  # Bash mode
        self.sudo = self.dev.sudo  # Sudo (part of Bash mode)
        self.cli_content = self.dev.content
        self.cli_result = self.dev.result
        self.bash_content = self.dev.content
        self.bash_result = self.dev.result
        self.set_prompt = self.dev.set_prompt
        self.get_prompt = self.dev.get_prompt
        self.send = self.dev.send
        self.expect = self.dev.expect

        # REST Shortcuts
        self.post = self.rest.post
        self.get = self.rest.get
        self.put = self.rest.put
        self.patch = self.rest.patch
        self.delete = self.rest.delete
        self.rest_content = self.rest.content
        self.rest_result = self.rest.result
        self.rest_content_json = self.rest.content_json
        self.rest_result_json = self.rest.result_json

    def connect(self, user, password, port=None, protocol=None, host=None,
                name=None):
        if not host:
            host = self.ip()
        if not name:
            name = self.name()
        if not port:
            port = self._port
        if not protocol:
            protocol = self._protocol
        return devconf.ControllerDevConf(
                            name=name,
                            host=host,
                            user=user,
                            password=password,
                            port=port,
                            protocol=protocol,
                            is_monitor_reauth=self._monitor_reauth,
                            debug=self.dev_debug_level,
                            privatekey=self._privatekey,
                            privatekey_password=self._privatekey_password,
                            privatekey_type=self._privatekey_type)

    def devconf(self):
        return self.dev

    def is_master(self):
        """
        Am I the master controller? This functionality is already implemented
        in Test class so simply refer to it.
        """
        node = self.name()
        return self.t.is_master_controller(node)

    def node_id(self):
        """
        Node-id is mainly supported for BVS platform but that may change over
        time. For now, all derived nodes should simply return None.

        For BVS, get the node-id for the specified node. The REST
        'show cluster' API has 'local-node-id' which is the node-id for the
        node we want.

        Input: Node name (e.g., 'master', 'c1', 'c2', etc.)
        Output: Integer value for the node-id
        """
        node = self.name()
        n = self.t.controller(node)
        if not helpers.is_bvs(n.platform()):
            return None

        count = 0
        while(True):
            try:
                url = '/api/v1/data/controller/cluster'
                content = n.rest.get(url)['content']
                nodeid = content[0]['status']['local-node-id']
                helpers.log("'%s' has local-node-id %s" % (node, nodeid))
                break
            except(KeyError):
                if(count < 5):
                    helpers.warn("'%s' KeyError while retrieving"
                                 " local-node-id. Sleeping for 10 seconds."
                                 % node)
                    helpers.sleep(10)
                    count += 1
                else:
                    helpers.test_error("'%s' KeyError while retrieving"
                                       " local-node-id."
                                       % node)
        return nodeid

    def console(self, driver=None, force_reconnect=False, expect_console_banner=False):
        if self.dev_console and not force_reconnect:
            return self.dev_console
        else:
            helpers.log("Reconnecting to console for node '%s'" % self.name())

        super(ControllerNode, self).console(driver)

        helpers.log("'%s' console type: %s" % (self.name(),
                                               self._console_info['type']))
        if self._console_info['type'] == 'telnet':
            # For telnet console, requirements are an IP address and a port
            # number.
            self.dev_console = devconf.ControllerDevConf(
                                    name=self.name() + "_console",
                                    host=self._console_info['ip'],
                                    port=self._console_info['port'],
                                    user=self._console_info['user'],
                                    password=self._console_info['password'],
                                    protocol=self._console_info['protocol'],
                                    console_info=self._console_info,
                                    debug=self.dev_debug_level)
        elif self._console_info['type'] == 'libvirt':
            # For libvirt console, requirements are an IP address (of the
            # KVM server) and the libvirt VM name (libvirt_vm_name). We will
            # first SSH to the KVM server, then execute 'virsh console <name>'.
            #
            # Note: We're using ControllerDevConf even though the libvirt
            # server is Ubuntu. This is because once we get on the controller
            # console, we want to be able to issue commands in different
            # modes: cli, enable, config, bash, etc.
            self.dev_console = devconf.ControllerDevConf(
                                    name=self.name() + "_console",
                                    host=self._console_info['ip'],
                                    port=self._console_info['port'],
                                    user=self._console_info['user'],
                                    password=self._console_info['password'],
                                    protocol=self._console_info['protocol'],
                                    console_info=self._console_info,
                                    debug=self.dev_debug_level)
        else:
            helpers.test_error("Unsupported console type '%s'"
                               % self._console_info['type'])

        if self._console_info['type'] == 'libvirt':
            self.dev_console.send("virsh console %s" %
                                  self._console_info['libvirt_vm_name'])
            if expect_console_banner:
                self._match_console_banner()

        # FIXME!!! The code below is not working. Figure out why...

        # if self._console_info['driver']:
        #    helpers.log("Setting devconf driver for console to '%s'"
        #                % self._console_info['driver'])
        #    self.dev_console.conn.set_driver(self._console_info['driver'])

        return self.dev_console

    def console_reconnect(self, driver=None, expect_console_banner=False):
        # Delay for 1 second to allow the output to settle.
        helpers.sleep(1)
        if self._console_info['type'] == 'libvirt':
            self.dev_console.send("virsh console %s"
                                  % self._console_info['libvirt_vm_name'])
            if expect_console_banner:
                self._match_console_banner()

            return self.dev_console

    def monitor_reauth(self, state):
        return self.dev.monitor_reauth(state)

    def close(self, delete_session_cookie=True):
        super(ControllerNode, self).close()
        if delete_session_cookie:
            try:
                self.rest.delete_session_cookie()
            except:
                helpers.log("Failed to delete REST session cookie for node '%s'. Ignore error."
                            % self.name())
        else:
            helpers.log("Argument delete_session_cookie=%s. Don't delete session cookie."
                        % delete_session_cookie)


class MininetNode(Node):
    def __init__(self, name, ip, user, password, t,
                 controller_ip, controller_ip2=None,
                 openflow_port=None, protocol=None):
        super(MininetNode, self).__init__(name, ip, user, password,
                                          t.topology_params(),
                                          protocol=protocol)

        self.controller_ip = controller_ip
        self.controller_ip2 = controller_ip2
        self.openflow_port = openflow_port

        if 'topology' in self.node_params:
            self.topology = self.node_params['topology']
        else:
            helpers.environment_failure("%s: Mininet topology is missing."
                                        % name)

        if 'type' not in self.node_params:
            helpers.environment_failure("%s: Must specify a Mininet type in"
                                        " topology file ('t6' or 'basic')."
                                        % name)

        if 'start_mininet' not in self.node_params:
            self._start_mininet = True
        else:
            self._start_mininet = self.node_params['start_mininet']
            if not helpers.is_bool(self._start_mininet):
                helpers.environment_failure("%s: 'start_mininet' must be a"
                                            " boolean value"
                                            % name)

        self.mn_type = self.node_params['type'].lower()
        if self.mn_type not in ('t6', 'basic'):
            helpers.environment_failure("%s: Mininet type must be 't6' or 'basic'."
                                        % name)

        if (not t.init_completed()
            and helpers.params_is_false('set_session_ssh',
                                        self.node_params)):
            helpers.log("'set_session_ssh' is disabled for '%s', bypassing"
                        " node SSH and RestClient session setup"
                        % name)
            return

        helpers.log("Mininet type: %s" % self.mn_type)
        helpers.log("Setting up mininet ('%s')" % name)

        self.dev = self.connect(name=name,
                                host=ip,
                                user=user,
                                password=password,
                                protocol=protocol)

        # Shortcuts
        self.cli = self.dev.cli
        self.bash = self.dev.bash  # Bash mode
        self.cli_content = self.dev.content
        self.cli_result = self.dev.result
        self.bash_content = self.dev.content
        self.bash_result = self.dev.result
        self.start_mininet = self.dev.start_mininet
        self.restart_mininet = self.dev.restart_mininet
        self.stop_mininet = self.dev.stop_mininet
        self.set_prompt = self.dev.set_prompt
        self.get_prompt = self.dev.get_prompt
        self.send = self.dev.send
        self.expect = self.dev.expect

    def connect(self, user, password, port=None, protocol=None, host=None,
                name=None):
        if not host:
            host = self.ip()
        if not name:
            name = self.name()
        if not port:
            port = self._port
        if not protocol:
            protocol = self._protocol

        if self.mn_type == 't6':
            return devconf.T6MininetDevConf(
                            name=name,
                            host=host,
                            user=user,
                            password=password,
                            controller=self.controller_ip,
                            controller2=self.controller_ip2,
                            topology=self.topology,
                            openflow_port=self.openflow_port,
                            debug=self.dev_debug_level,
                            is_start_mininet=self._start_mininet,
                            port=port,
                            protocol=protocol,
                            privatekey=self._privatekey,
                            privatekey_password=self._privatekey_password,
                            privatekey_type=self._privatekey_type)
        elif self.mn_type == 'basic':
            return devconf.MininetDevConf(
                            name=name,
                            host=host,
                            user=user,
                            password=password,
                            controller=self.controller_ip,
                            controller2=self.controller_ip2,
                            topology=self.topology,
                            openflow_port=self.openflow_port,
                            debug=self.dev_debug_level,
                            is_start_mininet=self._start_mininet,
                            port=port,
                            protocol=protocol,
                            privatekey=self._privatekey,
                            privatekey_password=self._privatekey_password,
                            privatekey_type=self._privatekey_type)

    def devconf(self):
        return self.dev

    def console(self, driver=None, force_reconnect=False):
        helpers.environment_failure("Console is currently not supported for Mininet node.")


class PduNode(Node):
    def __init__(self, name, ip, user, password, t, protocol=None):
        super(PduNode, self).__init__(name, ip, user, password,
                                      t.topology_params(), protocol=protocol)

        self.dev = self.connect(name=name,
                                host=ip,
                                user=user,
                                password=password,
                                protocol=protocol)

        # Shortcuts
        self.cli = self.dev.cli  # CLI mode
        self.cli_content = self.dev.content
        self.cli_result = self.dev.result
        self.set_prompt = self.dev.set_prompt
        self.get_prompt = self.dev.get_prompt
        self.send = self.dev.send
        self.expect = self.dev.expect

    def connect(self, user, password, port=None, protocol=None, host=None,
                name=None):
        if not host:
            host = self.ip()
        if not name:
            name = self.name()
        if not port:
            port = self._port
        if not protocol:
            protocol = self._protocol
        return devconf.PduDevConf(
                            name=name,
                            host=host,
                            user=user,
                            password=password,
                            port=port,
                            protocol=protocol,
                            debug=self.dev_debug_level,
                            privatekey=self._privatekey,
                            privatekey_password=self._privatekey_password,
                            privatekey_type=self._privatekey_type)

    def devconf(self):
        return self.dev


class HostNode(Node):
    def __init__(self, name, ip, user, password, t, protocol=None):
        super(HostNode, self).__init__(name, ip, user, password,
                                       t.topology_params(), protocol=protocol)

        if (not t.init_completed()
            and helpers.params_is_false('set_session_ssh',
                                        self.node_params)):
            helpers.log("'set_session_ssh' is disabled for '%s', bypassing"
                        " node SSH and RestClient session setup"
                        % name)
            return

        self.dev = self.connect(name=name,
                                host=ip,
                                user=user,
                                password=password,
                                protocol=protocol)

        # Shortcuts
        self.bash = self.dev.bash
        self.sudo = self.dev.sudo
        self.bash_content = self.dev.content
        self.bash_result = self.dev.result
        self.bash_content = self.dev.content
        self.bash_result = self.dev.result
        self.set_prompt = self.dev.set_prompt
        self.get_prompt = self.dev.get_prompt
        self.send = self.dev.send
        self.expect = self.dev.expect

    def connect(self, user, password, port=None, protocol=None, host=None,
                name=None):
        if not host:
            host = self.ip()
        if not name:
            name = self.name()
        if not port:
            port = self._port
        if not protocol:
            protocol = self._protocol
        return devconf.HostDevConf(
                            name=name,
                            host=host,
                            user=user,
                            password=password,
                            port=port,
                            protocol=protocol,
                            debug=self.dev_debug_level,
                            privatekey=self._privatekey,
                            privatekey_password=self._privatekey_password,
                            privatekey_type=self._privatekey_type)

    def devconf(self):
        return self.dev

    def console(self, driver=None, force_reconnect=False, expect_console_banner=False):
        if self.dev_console and not force_reconnect:
            return self.dev_console
        else:
            helpers.log("Reconnecting to console for node '%s'" % self.name())

        super(HostNode, self).console(driver)

        if self._console_info['type'] in ['telnet', 'libvirt']:
            # For telnet console, requirements are an IP address and a port
            # number.
            #
            # For libvirt console, requirements are an IP address (of the
            # KVM server) and the libvirt VM name (libvirt_vm_name). We will
            # first SSH to the KVM server, then execute 'virsh console <name>'.
            self.dev_console = devconf.HostDevConf(name=self.name() + "_console",
                                                   host=self._console_info['ip'],
                                                   port=self._console_info['port'],
                                                   user=self._console_info['user'],
                                                   password=self._console_info['password'],
                                                   protocol=self._console_info['protocol'],
                                                   console_info=self._console_info,
                                                   debug=self.dev_debug_level)
        else:
            helpers.test_error("Unsupported console type '%s'"
                               % self._console_info['type'])
            if expect_console_banner:
                self._match_console_banner()

        if self._console_info['type'] == 'libvirt':
            self.dev_console.send("virsh console %s" % self._console_info['libvirt_vm_name'])

        # FIXME!!! The code below is not working. Figure out why...

        # if self._console_info['driver']:
        #    helpers.log("Setting devconf driver for console to '%s'"
        #                % self._console_info['driver'])
        #    self.dev_console.conn.set_driver(self._console_info['driver'])

        return self.dev_console

    def console_reconnect(self, driver=None):
        # Delay for 1 second to allow the output to settle.
        helpers.sleep(1)
        if self._console_info['type'] == 'libvirt':
            self.dev_console.send("virsh console %s" % self._console_info['libvirt_vm_name'])
            return self.dev_console


class OpenStackNode(HostNode):
    def __init__(self, name, ip, user, password, t, protocol=None):
        super(OpenStackNode, self).__init__(name, ip, user, password, t,
                                            protocol=protocol)


class SwitchNode(Node):
    def __init__(self, name, ip, user, password, t, protocol=None):
        super(SwitchNode, self).__init__(name, ip, user, password,
                                         t.topology_params(),
                                         protocol=protocol)

        if (not t.init_completed()
            and helpers.params_is_false('set_session_ssh',
                                        self.node_params)):
            helpers.log("'set_session_ssh' is disabled for '%s', bypassing"
                        " node SSH and RestClient session setup"
                        % name)
            return

        self.dev = self.connect(name=name,
                                host=ip,
                                user=user,
                                password=password,
                                protocol=protocol)

        # Shortcuts
        self.cli = self.dev.cli  # CLI mode
        self.enable = self.dev.enable  # Enable mode
        self.config = self.dev.config  # Configuration mode
        self.bash = self.dev.bash  # Bash mode
        self.sudo = self.dev.sudo  # Sudo (part of Bash mode)
        self.cli_content = self.dev.content
        self.cli_result = self.dev.result
        self.bash_content = self.dev.content
        self.bash_result = self.dev.result
        self.set_prompt = self.dev.set_prompt
        self.get_prompt = self.dev.get_prompt
        self.send = self.dev.send
        self.expect = self.dev.expect
        self.info = self.dev.info

    def connect(self, user, password, port=None, protocol=None, host=None,
                name=None):
        if not host:
            host = self.ip()
        if not name:
            name = self.name()
        if not port:
            port = self._port
        if not protocol:
            protocol = self._protocol
        return devconf.SwitchDevConf(
                            name=name,
                            host=host,
                            user=user,
                            password=password,
                            port=port,
                            protocol=protocol,
                            debug=self.dev_debug_level,
                            privatekey=self._privatekey,
                            privatekey_password=self._privatekey_password,
                            privatekey_type=self._privatekey_type)

    def devconf(self):
        return self.dev

    def console(self, driver=None, force_reconnect=False, expect_console_banner=False):
        if self.dev_console and not force_reconnect:
            return self.dev_console
        else:
            helpers.log("Reconnecting to console for node '%s'" % self.name())

        super(SwitchNode, self).console(driver)

        if self._console_info['type'] == 'telnet':
            # For telnet console, requirements are an IP address and a port
            # number.
            self.dev_console = devconf.SwitchDevConf(
                                    name=self.name() + "_console",
                                    host=self._console_info['ip'],
                                    port=self._console_info['port'],
                                    user=self._console_info['user'],
                                    password=self._console_info['password'],
                                    protocol=self._console_info['protocol'],
                                    console_info=self._console_info,
                                    debug=self.dev_debug_level)
        else:
            helpers.test_error("Unsupported console type '%s'"
                               % self._console_info['type'])
            if expect_console_banner:
                self._match_console_banner()

        # FIXME!!! The code below is not working. Figure out why...

        # if self._console_info['driver']:
        #    helpers.log("Setting devconf driver for console to '%s'"
        #                % self._console_info['driver'])
        #    self.dev_console.conn.set_driver(self._console_info['driver'])

        return self.dev_console

