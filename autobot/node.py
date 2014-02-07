import autobot.devconf as devconf
import helpers
from autobot.bsn_restclient import BsnRestClient


class Node(object):
    def __init__(self, name, ip, user=None, password=None, params=None):
        if not name:
            helpers.test_error("Controller node name is not defined")
        if not ip:
            helpers.test_error("Controller IP address is not defined for '%s'"
                               % name)

        self._name = name
        self._ip = ip
        self.user = user
        self.password = password
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
        if params:
            self.node_params = self.params[name]
            val = helpers.params_val('set_devconf_debug_level', self.node_params)
            if val is not None:
                self.dev_debug_level = val
                helpers.log("Devconf for '%s' set to debug level %s"
                            % (name, self.dev_debug_level))
        else:
            self.node_params = None

        if helpers.params_is_false('set_init_ping', self.node_params):
            helpers.log("'set_init_ping' is disabled for '%s', bypassing initial ping" % name)
        else:
            self.pingable_or_die()

    def name(self):
        return self._name

    def ip(self):
        return self._ip

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
            self._init_completed = True
            helpers.environment_failure("Node with IP address %s is unreachable."
                                        % self.ip())
        self.is_pingable = True
        return True

    def console(self):
        """
        Inheriting class needs to define this method.
        """
        raise NotImplementedError()


class ControllerNode(Node):
    def __init__(self, name, ip, user, password, t):
        # If user/password info is specified in the topology params then use it
        authen = t.topology_params_authen(name)
        if authen[0]:
            user = authen[0]
        if authen[1]:
            password = authen[1]

        super(ControllerNode, self).__init__(name, ip, user, password,
                                             t.topology_params())

        # Note: Must be initialized before BsnRestClient since we need the
        # CLI for platform info and also to configure the firewall for REST
        # access

        # Note: SSH is required for both DevConf and RestClient to be
        # instantiated. These sessions go together.
        if helpers.params_is_false('set_session_ssh', self.node_params):
            helpers.log("'set_session_ssh' is disabled for '%s', bypassing node SSH and RestClient session setup" % name)
            return

        helpers.log("name=%s host=%s user=%s password=%s" % (name, ip, user, password))
        self.dev = devconf.ControllerDevConf(name=name,
                                             host=ip,
                                             user=user,
                                             password=password,
                                             debug=self.dev_debug_level)

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
                                  host=self.ip())
        self.t = t

        # Shortcuts
        self.cli = self.dev.cli  # CLI mode
        self.enable = self.dev.enable  # Enable mode
        self.config = self.dev.config  # Configuration mode
        self.bash = self.dev.bash  # Bash mode
        self.sudo = self.dev.sudo  # Sudo (part of Bash mode)
        self.cli_content = self.dev.content
        self.cli_result = self.dev.result
        self.set_prompt = self.dev.set_prompt
        self.send = self.dev.send
        self.expect = self.dev.expect

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
            helpers.test_error("Console IP address is not defined for node '%s'"
                               % self.name())
        if 'console_port' in self.node_params:
            self.console_port = self.node_params['console_port']
        else:
            helpers.test_error("Console port is not defined for node '%s'"
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
                                                     user=self.user,
                                                     password=self.password,
                                                     is_console=True,
                                                     console_driver=driver,
                                                     debug=self.dev_debug_level)
        return self.dev_console


class MininetNode(Node):
    def __init__(self, name, ip, controller_ip, user, password, t,
                 openflow_port=None):
        super(MininetNode, self).__init__(name, ip, user, password,
                                          t.topology_params())
        if 'topology' in self.node_params:
            self.topology = self.node_params['topology']
        else:
            helpers.environment_failure("Mininet topology is missing.")

        if 'type' not in self.node_params:
            helpers.environment_failure("Must specify a Mininet type in topology file ('t6' or 'basic').")

        mn_type = self.node_params['type'].lower()
        if mn_type not in ('t6', 'basic'):
            helpers.environment_failure("Mininet type must be 't6' or 'basic'.")

        if helpers.params_is_false('set_session_ssh', self.node_params):
            helpers.log("'set_session_ssh' is disabled for '%s', bypassing node SSH and RestClient session setup" % name)
            return

        helpers.log("Mininet type: %s" % mn_type)
        helpers.log("Setting up mininet ('%s')" % name)

        if mn_type == 't6':
            self.dev = devconf.T6MininetDevConf(name=name,
                                                host=ip,
                                                user=user,
                                                password=password,
                                                controller=controller_ip,
                                                topology=self.topology,
                                                openflow_port=openflow_port,
                                                debug=self.dev_debug_level)
        elif mn_type == 'basic':
            self.dev = devconf.MininetDevConf(name=name,
                                              host=ip,
                                              user=user,
                                              password=password,
                                              controller=controller_ip,
                                              topology=self.topology,
                                              openflow_port=openflow_port,
                                              debug=self.dev_debug_level)

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


class HostNode(Node):
    def __init__(self, name, ip, user, password, t):
        # If user/password info is specified in the topology params then use it
        authen = t.topology_params_authen(name)
        if authen[0]:
            user = authen[0]
        if authen[1]:
            password = authen[1]

        super(HostNode, self).__init__(name, ip, user, password,
                                       t.topology_params())

        if helpers.params_is_false('set_session_ssh', self.node_params):
            helpers.log("'set_session_ssh' is disabled for '%s', bypassing node SSH and RestClient session setup" % name)
            return

        self.dev = devconf.HostDevConf(name=name,
                                       host=ip,
                                       user=user,
                                       password=password,
                                       debug=self.dev_debug_level)

        # Shortcuts
        self.bash = self.dev.bash
        self.sudo = self.dev.sudo
        self.bash_content = self.dev.content
        self.bash_result = self.dev.result
        self.set_prompt = self.dev.set_prompt
        self.send = self.dev.send
        self.expect = self.dev.expect


class SwitchNode(Node):
    def __init__(self, name, ip, user, password, t):
        # If user/password info is specified in the topology params then use it
        authen = t.topology_params_authen(name)
        if authen[0]:
            user = authen[0]
        if authen[1]:
            password = authen[1]

        super(SwitchNode, self).__init__(name, ip, user, password,
                                         t.topology_params())

        if helpers.params_is_false('set_session_ssh', self.node_params):
            helpers.log("'set_session_ssh' is disabled for '%s', bypassing node SSH and RestClient session setup" % name)
            return

        self.dev = devconf.SwitchDevConf(name=name,
                                         host=ip,
                                         user=user,
                                         password=password,
                                         debug=self.dev_debug_level)

        # Shortcuts
        self.cli = self.dev.cli  # CLI mode
        self.enable = self.dev.enable  # Enable mode
        self.config = self.dev.config  # Configuration mode
        self.bash = self.dev.bash  # Bash mode
        self.sudo = self.dev.sudo  # Sudo (part of Bash mode)
        self.cli_content = self.dev.content
        self.cli_result = self.dev.result
        self.set_prompt = self.dev.set_prompt
        self.send = self.dev.send
        self.expect = self.dev.expect
        self.info = self.dev.info


class IxiaNode(Node):
    def __init__(self, name, t):
        self._chassis_ip = t.params(name, 'chassis_ip')
        self._tcl_server_ip = t.params(name, 'tcl_server_ip')
        self._tcl_server_port = t.params(name, 'tcl_server_port', 8009)
        self._ix_version = t.params(name, 'ix_version', '7.10')
        self._ports = t.params(name, 'ports')
        helpers.log("***** IXIA ports for '%s': %s" % (name, self._ports))

        super(IxiaNode, self).__init__(name, self._chassis_ip,
                                       params=t.topology_params())

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
