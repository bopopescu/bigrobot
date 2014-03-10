import autobot.devconf as devconf
import autobot.helpers as helpers
from autobot.bsn_restclient import BsnRestClient
import modules.IxLib as IxLib

class Node(object):
    def __init__(self, name, ip, user=None, password=None, params=None):
        if not name:
            helpers.environment_failure("Node name is not defined")
        if not ip:
            helpers.environment_failure("Node IP address is not defined for '%s'"
                                        % name)

        self._name = name
        self._ip = ip.lower()  # IP might be 'dummy'
        self._user = user
        self._password = password
        self.http_port = None
        self.base_url = None
        self.params = params
        self.is_pingable = False
        self.rest = None  # REST handle
        self.dev = None  # DevConf handle (SSH)
        self.dev_console = None
        self.dev_debug_level = 0
        self.console_ip = None
        self.console_port = None

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

        if self.ip() == 'dummy':
            helpers.environment_failure("IP address for '%s' is 'dummy'."
                                        " Needs to be populated."
                                        % self.name())
        if helpers.params_is_false('set_init_ping', self.node_params):
            helpers.log("'set_init_ping' is disabled for '%s', bypassing"
                        " initial ping"
                        % name)
        else:
            self.pingable_or_die()

    def name(self):
        return self._name

    def ip(self):
        return self._ip

    def user(self):
        return self._user

    def password(self):
        return self._password

    def platform(self):
        return self.dev.platform()

    def pingable_or_die(self):
        if self.is_pingable:
            return True
        helpers.log("Ping %s ('%s')" % (self.ip(), self.name()))
        loss = helpers.ping(self.ip(), count=3, waittime=1000)
        if  loss > 20:
            # We can tolerate 20% loss.
            # Consider init to be completed, so as not to be invoked again.
            helpers.environment_failure("Node with IP address %s is unreachable."
                                        % self.ip())
        self.is_pingable = True
        return True

    def console(self):
        """
        Inheriting class needs to define this method.
        """
        raise NotImplementedError()

    def connect(self, user, password, port=None, protocol='ssh', host=None,
                name=None):
        """
        Connect to the node using either ssh or telnet.
        Returns the session handle.
        """
        raise NotImplementedError()


class ControllerNode(Node):
    def __init__(self, name, ip, user, password, t):
        super(ControllerNode, self).__init__(name, ip, user, password,
                                             t.topology_params())

        # Note: Must be initialized before BsnRestClient since we need the
        # CLI for platform info and also to configure the firewall for REST
        # access

        # Note: SSH is required for both DevConf and RestClient to be
        # instantiated. These sessions go together.
        if helpers.params_is_false('set_session_ssh', self.node_params):
            helpers.log("'set_session_ssh' is disabled for '%s', bypassing"
                        " node SSH and RestClient session setup"
                        % name)
            return

        helpers.log("name=%s host=%s user=%s password=%s"
                    % (name, ip, user, password))
        self.dev = self.connect(name=name,
                                host=ip,
                                user=user,
                                password=password)

        if 'http_port' in self.node_params:
            self.http_port = self.node_params['http_port']
        else:
            self.http_port = 8080

        if 'base_url' in self.node_params:
            self.base_url = self.node_params['base_url'] % (ip, self.http_port)
        else:
            self.base_url = 'http://%s:%s' % (ip, self.http_port)

        self.rest = BsnRestClient(base_url=self.base_url,
                                  platform=self.platform(),
                                  host=self.ip(),
                                  user=self._user,
                                  password=self._password)
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

    def connect(self, user, password, port=None, protocol='ssh', host=None,
                name=None):
        if not host:
            host = self.ip()
        if not name:
            name = self.name()
        return devconf.ControllerDevConf(name=name,
                                         host=host,
                                         user=user,
                                         password=password,
                                         port=port,
                                         protocol=protocol,
                                         debug=self.dev_debug_level)

    def is_master(self):
        """
        Am I the master controller? This functionality is already implemented
        in Test class so simply refer to it.
        """
        node = self.name()
        return self.t.is_master_controller(node)

    def console(self):
        if self.dev_console:
            return self.dev_console

        if 'console_ip' in self.node_params:
            self.console_ip = self.node_params['console_ip']
        else:
            helpers.environment_failure("Console IP address is not defined for node '%s'"
                                        % self.name())
        if 'console_port' in self.node_params:
            self.console_port = self.node_params['console_port']
        else:
            helpers.environment_failure("Console port is not defined for node '%s'"
                                        % self.name())

        if self.dev:
            driver = self.dev.driver().name()
        else:
            driver = None

        helpers.log("Using devconf driver '%s' for console to '%s'"
                    % (driver, self.name()))
        self.dev_console = devconf.ControllerDevConf(name=self.name(),
                                                     host=self.console_ip,
                                                     port=self.console_port,
                                                     user=self._user,
                                                     password=self._password,
                                                     is_console=True,
                                                     console_driver=driver,
                                                     debug=self.dev_debug_level)
        return self.dev_console


class MininetNode(Node):
    def __init__(self, name, ip, user, password, t,
                 controller_ip, controller_ip2=None,
                 openflow_port=None):
        super(MininetNode, self).__init__(name, ip, user, password,
                                          t.topology_params())

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
                helpers.environment_failure("%s: 'start_mininet' must be a boolean value"
                                            % name)

        self.mn_type = self.node_params['type'].lower()
        if self.mn_type not in ('t6', 'basic'):
            helpers.environment_failure("%s: Mininet type must be 't6' or 'basic'."
                                        % name)

        if helpers.params_is_false('set_session_ssh', self.node_params):
            helpers.log("'set_session_ssh' is disabled for '%s', bypassing"
                        " node SSH and RestClient session setup"
                        % name)
            return

        helpers.log("Mininet type: %s" % self.mn_type)
        helpers.log("Setting up mininet ('%s')" % name)

        self.dev = self.connect(name=name,
                                host=ip,
                                user=user,
                                password=password)

        # Shortcuts
        self.cli = self.dev.cli
        self.cli_content = self.dev.content
        self.cli_result = self.dev.result
        self.start_mininet = self.dev.start_mininet
        self.restart_mininet = self.dev.restart_mininet
        self.stop_mininet = self.dev.stop_mininet
        self.set_prompt = self.dev.set_prompt
        self.send = self.dev.send
        self.expect = self.dev.expect

    def connect(self, user, password, port=None, protocol='ssh', host=None,
                name=None):
        if not host:
            host = self.ip()
        if not name:
            name = self.name()

        if self.mn_type == 't6':
            return devconf.T6MininetDevConf(name=name,
                                            host=host,
                                            user=user,
                                            password=password,
                                            controller=self.controller_ip,
                                            controller2=self.controller_ip2,
                                            topology=self.topology,
                                            openflow_port=self.openflow_port,
                                            debug=self.dev_debug_level,
                                            is_start_mininet=self._start_mininet)
        elif self.mn_type == 'basic':
            return devconf.MininetDevConf(name=name,
                                          host=host,
                                          user=user,
                                          password=password,
                                          controller=self.controller_ip,
                                          controller2=self.controller_ip2,
                                          topology=self.topology,
                                          openflow_port=self.openflow_port,
                                          debug=self.dev_debug_level,
                                          is_start_mininet=self._start_mininet)


class HostNode(Node):
    def __init__(self, name, ip, user, password, t):
        super(HostNode, self).__init__(name, ip, user, password,
                                       t.topology_params())

        if helpers.params_is_false('set_session_ssh', self.node_params):
            helpers.log("'set_session_ssh' is disabled for '%s', bypassing"
                        " node SSH and RestClient session setup"
                        % name)
            return

        self.dev = self.connect(name=name,
                                host=ip,
                                user=user,
                                password=password)

        # Shortcuts
        self.bash = self.dev.bash
        self.sudo = self.dev.sudo
        self.bash_content = self.dev.content
        self.bash_result = self.dev.result
        self.bash_content = self.dev.content
        self.bash_result = self.dev.result
        self.set_prompt = self.dev.set_prompt
        self.send = self.dev.send
        self.expect = self.dev.expect

    def connect(self, user, password, port=None, protocol='ssh', host=None,
                name=None):
        if not host:
            host = self.ip()
        if not name:
            name = self.name()
        return devconf.HostDevConf(name=name,
                                   host=host,
                                   user=user,
                                   password=password,
                                   port=port,
                                   protocol=protocol)


class SwitchNode(Node):
    def __init__(self, name, ip, user, password, t):
        super(SwitchNode, self).__init__(name, ip, user, password,
                                         t.topology_params())

        if helpers.params_is_false('set_session_ssh', self.node_params):
            helpers.log("'set_session_ssh' is disabled for '%s', bypassing"
                        " node SSH and RestClient session setup"
                        % name)
            return

        self.dev = self.connect(name=name,
                                host=ip,
                                user=user,
                                password=password)

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
        self.send = self.dev.send
        self.expect = self.dev.expect
        self.info = self.dev.info

    def connect(self, user, password, port=None, protocol='ssh', host=None,
                name=None):
        if not host:
            host = self.ip()
        if not name:
            name = self.name()
        return devconf.SwitchDevConf(name=name,
                                     host=host,
                                     user=user,
                                     password=password,
                                     port=port,
                                     protocol=protocol,
                                     debug=self.dev_debug_level)

class IxiaNode(Node):
    def __init__(self, name, t):
        self._chassis_ip = t.params(name, 'chassis_ip')
        self._tcl_server_ip = t.params(name, 'tcl_server_ip')
        self._tcl_server_port = t.params(name, 'tcl_server_port', 8009)
        self._ix_version = t.params(name, 'ix_version', '7.10')
        self._ports = t.params(name, 'ports')

        super(IxiaNode, self).__init__(name, self._chassis_ip,
                                       params=t.topology_params())
        self.ixia_init()

    def ixia_init(self):
        helpers.log("tcl_server_ip: %s" % self.tcl_server_ip())
        helpers.log("chassis_ip: %s" % self.chassis_ip())
        helpers.log("ports: %s" % self.ports())

        self._ixia = IxLib.Ixia(tcl_server_ip=self.tcl_server_ip(),
                                chassis_ip=self.chassis_ip(),
                                port_map_list=self.ports())
        return self._ixia

    def handle(self):
        return self._ixia
    def chassis_ip(self):
        return self._chassis_ip

    def tcl_server_ip(self):
        return self._tcl_server_ip

    def tcl_server_port(self):
        return self._tcl_server_port

    def ix_version(self):
        return self._ix_version

    def ports(self):
        return self._ports

    def platform(self):
        return 'ixia'
