import autobot.devconf as devconf
import helpers
from autobot.bsn_restclient import BsnRestClient


class Node(object):
    def __init__(self, name, ip, user=None, password=None):
        self.node_name = name
        self.ip = ip
        self.user = user
        self.password = password
        self.http_port = None
        self.base_url = None
        self.rest = None  # REST handle
        self.is_pingable = False
        
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


class ControllerNode(Node):
    def __init__(self, name, ip, user, password, t):

        # If user/password info is specified in the topology params then use it
        authen = t.topology_params_authen(name)
        if authen[0]:
            user = authen[0]
        if authen[1]:
            password = authen[1]
        
        super(ControllerNode, self).__init__(name, ip, user, password) 
        self.pingable_or_die()
        params = t.topology_params()

        self.dev = devconf.ControllerDevConf(name=name,
                                             host=ip,
                                             user=user,
                                             password=password)
        
        if 'http_port' in params[name]:
            self.http_port = params[name]['http_port']
        else:
            self.http_port = 8080
            
        if 'base_url' in params[name]:
            self.base_url = params[name]['base_url'] % (ip, self.http_port)
        else:
            self.base_url =  'http://%s:%s' % (ip, self.http_port) 
        
        self.rest = BsnRestClient(base_url=self.base_url,
                                  platform=self.platform(),
                                  host=self.ip)
        
        # !!! FIXME: Can remove this if no one complains
        # Shortcuts
        #self.post = self.rest.post
        #self.get = self.rest.get
        #self.put = self.rest.put
        #self.patch = self.rest.patch
        #self.delete = self.rest.delete
        #self.rest_content = self.rest.content
        #self.rest_content_json = self.rest.content_json
        #self.rest_result = self.rest.result
        #self.rest_result_json = self.rest.result_json
        
        # Shortcuts
        self.cli = self.dev.cli           # CLI mode
        self.enable = self.dev.enable     # Enable mode
        self.config = self.dev.config     # Configuration mode
        self.bash   = self.dev.bash       # Bash mode
        self.sudo   = self.dev.sudo       # Sudo (part of Bash mode)
        self.cli_content = self.dev.content
        self.cli_result = self.dev.result


class MininetNode(Node):
    def __init__(self, name, ip, controller_ip, user, password, t):
        super(MininetNode, self).__init__(name, ip, user, password)
        self.pingable_or_die()
        params = t.topology_params()
        if 'topology' in params[name]:
            self.topology = params[name]['topology']
        else:
            helpers.environment_failure("Mininet topology is missing.")

        if 'type' not in params[name]:
            helpers.environment_failure("Must specify a Mininet type in topology file ('t6' or 'basic').")

        mn_type = params[name]['type'].lower()
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
                                                topology=self.topology)
        elif mn_type == 'basic':
            self.dev = devconf.MininetDevConf(name=name,
                                              host=ip,
                                              user=user,
                                              password=password,
                                              controller=controller_ip,
                                              topology=self.topology)

        # Shortcuts
        self.cli = self.dev.cli
        self.cli_content = self.dev.content
        self.cli_result = self.dev.result


class HostNode(Node):
    def __init__(self, name, ip, user, password, t):

        # If user/password info is specified in the topology params then use it
        authen = t.topology_params_authen(name)
        if authen[0]:
            user = authen[0]
        if authen[1]:
            password = authen[1]
        
        super(HostNode, self).__init__(name, ip, user, password)
        self.pingable_or_die()
        #params = t.topology_params()

        self.dev = devconf.HostDevConf(name=name,
                                       host=ip,
                                       user=user,
                                       password=password)

        # Shortcuts
        self.bash = self.dev.bash
        self.sudo = self.dev.sudo
        self.bash_content = self.dev.content
        self.bash_result = self.dev.result


class SwitchNode(Node):
    def __init__(self, name, ip, user, password, t):

        # If user/password info is specified in the topology params then use it
        authen = t.topology_params_authen(name)
        if authen[0]:
            user = authen[0]
        if authen[1]:
            password = authen[1]
        
        super(SwitchNode, self).__init__(name, ip, user, password)
        self.pingable_or_die()
        #params = t.topology_params()

        self.dev = devconf.SwitchDevConf(name=name,
                                         host=ip,
                                         user=user,
                                         password=password)

        # Shortcuts
        self.cli = self.dev.cli
        #self.bash = self.dev.bash
        self.cli_content = self.dev.content
        self.cli_result = self.dev.result
