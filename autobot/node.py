import autobot.devconf as devconf
import helpers
from autobot.bsn_restclient import BsnRestClient


class Node(object):
    def __init__(self, name, ip, user=None, password=None, params=None):
        self.node_name = name
        self.ip = ip
        self.user = user
        self.password = password
        self.http_port = None
        self.base_url = None
        self.is_pingable = False
        self.rest = None  # REST handle
        self.dev = None   # DevConf handle (SSH)
        self.dev_console = None
        self.dev_debug_level = 0
        self.console_ip = None
        self.console_port = None
        self.params = params
        if params:
            self.node_params = self.params[name]
            val = helpers.params_val('set_devconf_debug_level', self.node_params)
            if val is not None:
                self.dev_debug_level = val
                helpers.log("Devconf for '%s' set to debug level %s"
                            % (name, self.dev_debug_level))
        else:
            self.node_params = None
        
    def platform(self):
        return self.dev.platform()

    def pingable_or_die(self):
        if self.is_pingable:
            return True
        helpers.log("Ping %s ('%s')" % (self.ip, self.node_name))
        if not helpers.ping(self.ip, count=3, waittime=1000):
            # Consider init to be completed, so as not to be invoked again.
            self._init_completed = True
            helpers.environment_failure("Node with IP address %s is unreachable."
                                        % self.ip)
        self.is_pingable = True
        return True

    def console(self):
        """
        Inheriting class needs to define this method.
        """
        pass


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
        
        if helpers.params_is_false('set_session_ssh', self.node_params):
            helpers.log("'set_init_ping' is disabled for '%s', bypassing node ping" % name)
        else:
            self.pingable_or_die()

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
            self.base_url =  'http://%s:%s' % (ip, self.http_port) 
        
        self.rest = BsnRestClient(base_url=self.base_url,
                                  platform=self.platform(),
                                  host=self.ip)
        # Shortcuts
        self.cli = self.dev.cli           # CLI mode
        self.enable = self.dev.enable     # Enable mode
        self.config = self.dev.config     # Configuration mode
        self.bash   = self.dev.bash       # Bash mode
        self.sudo   = self.dev.sudo       # Sudo (part of Bash mode)
        self.cli_content = self.dev.content
        self.cli_result = self.dev.result
        self.set_prompt = self.dev.set_prompt

    def console(self):
        if self.dev_console:
            return self.dev_console

        if 'console_ip' in self.node_params:
            self.console_ip = self.node_params['console_ip']
        else:
            helpers.test_error("Console IP address is not defined for node '%s'"
                               % self.node_name)
        if 'console_port' in self.node_params:
            self.console_port = self.node_params['console_port']
        else:
            helpers.test_error("Console port is not defined for node '%s'"
                               % self.node_name)
            
        self.dev_console = devconf.ControllerDevConf(name=self.node_name,
                                                     host=self.console_ip,
                                                     port=self.console_port,
                                                     user=self.user,
                                                     password=self.password,
                                                     is_console=True,
                                                     debug=self.dev_debug_level)
        return self.dev_console


class MininetNode(Node):
    def __init__(self, name, ip, controller_ip, user, password, t):
        super(MininetNode, self).__init__(name, ip, user, password,
                                          t.topology_params())
        self.pingable_or_die()
        if 'topology' in self.node_params:
            self.topology = self.node_params['topology']
        else:
            helpers.environment_failure("Mininet topology is missing.")

        if 'type' not in self.node_params:
            helpers.environment_failure("Must specify a Mininet type in topology file ('t6' or 'basic').")

        mn_type = self.node_params['type'].lower()
        if mn_type not in ('t6', 'basic'):
            helpers.environment_failure("Mininet type must be 't6' or 'basic'.") 
            
        helpers.log("Mininet type: %s" % mn_type)
        helpers.log("Setting up mininet ('%s')" % name)

        if mn_type == 't6':
            self.dev = devconf.T6MininetDevConf(name=name,
                                                host=ip,
                                                user=user,
                                                password=password,
                                                controller=controller_ip,
                                                topology=self.topology,
                                                debug=self.dev_debug_level)
        elif mn_type == 'basic':
            self.dev = devconf.MininetDevConf(name=name,
                                              host=ip,
                                              user=user,
                                              password=password,
                                              controller=controller_ip,
                                              topology=self.topology,
                                              debug=self.dev_debug_level)

        # Shortcuts
        self.cli = self.dev.cli
        self.cli_content = self.dev.content
        self.cli_result = self.dev.result
        self.start_mininet = self.dev.start_mininet
        self.restart_mininet = self.dev.restart_mininet
        self.stop_mininet = self.dev.stop_mininet
        self.set_prompt = self.dev.set_prompt


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
        self.pingable_or_die()
        #params = t.topology_params()

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
        self.pingable_or_die()
        #params = t.topology_params()

        self.dev = devconf.SwitchDevConf(name=name,
                                         host=ip,
                                         user=user,
                                         password=password,
                                         debug=self.dev_debug_level)

        # Shortcuts
        self.cli = self.dev.cli
        #self.bash = self.dev.bash
        self.cli_content = self.dev.content
        self.cli_result = self.dev.result
        self.set_prompt = self.dev.set_prompt
