import autobot.helpers as helpers
import autobot.restclient as restclient
import autobot.devconf as devconf
import autobot.node as node
import re
#import bigtest
#import bigtest.controller
#from bigtest.util import *


class Test(object):
    """
    Test class is a singleton which contains important test states for the
    current robot execution. E.g., topology information including device
    IP addresses, roles (controller, switch, spine, leaf), interfaces, and
    so on...
    """

    _instance = None

    # Singleton pattern borrowed from
    # http://developer.nokia.com/Community/Wiki/How_to_make_a_singleton_in_Python    
    class Singleton:
        def __init__(self):
            # This flag ensures that we only do setup once
            self._init_completed = False
            self._fatal_error = False
            
            config = ''.join((helpers.get_path_autobot_config(), '/bsn.yaml'))
            helpers.log("Loading config file %s" % config)
            self._bsn_config = helpers.load_config(config)

            topo = helpers.bigrobot_topology()
            helpers.error_exit_if_file_not_exist("Topology file not found", topo)
            helpers.log("Loading topology file %s" % topo)
            self._topology_params = helpers.load_config(topo)
            self._topology = {}
    
    def __init__(self):
        if Test._instance is None:
            Test._instance = Test.Singleton()
        self._EventHandler_instance = Test._instance
        self.initialize()
        
    def __getattr__(self, attr):
        return getattr(self._instance, attr)
    
    def __setattr__(self, attr, val):
        return setattr(self._instance, attr, val)
    
    def controller_user(self):
        return self._bsn_config['controller_user']
    
    def controller_password(self):
        return self._bsn_config['controller_password']

    def mininet_user(self):
        return self._bsn_config['mininet_user']
    
    def mininet_password(self):
        return self._bsn_config['mininet_password']

    def topology_params(self):
        """
        Returns the topology dictionary.
        {   'c1': {
                'ip': '10.192.5.116'
            },
            'mn': {
                'ip': '10.192.7.205'
            }
            ...
        }
        """
        return self._topology_params

    def topology(self, name=None):
        #self.initialize()
        if name:
            return self._topology[name]
        else:
            return self._topology
    
    def controller(self, name='c1'):
        return self.topology(name)
    
    def mininet(self):
        return self.topology('mn')
    
    def node(self, name):
        return self.topology(name)
    
    def is_controller(self, name):
        match = re.match(r'^(c\d|controller\d?|master|slave)$', name)
        if match:
            return True
        else:
            return False

    def is_switch(self, name):
        match = re.match(r'^(s\d+|spine\d+|leaf\d+)$', name)
        if match:
            return True
        else:
            return False

    def is_mininet(self, name):
        match = re.match(r'^(mn\d?|mininet\d?)$', name)
        if match:
            return True
        else:
            return False

    def pingable_or_die(self, node):
        if not helpers.ping(node, count=3, waittime=1000):
            # Consider init to be completed, so as not to be invoked again.
            self._init_completed = True
            helpers.environment_failure("Node with IP address %s is unreachable."
                                        % node)

    def initialize(self, force_init=False):
        """
        Initializes the test object. This should be called prior to test case
        execution (e.g., called by Test Suite or Test Case setup).
        """

        if self._fatal_error:
            helpers.exit_robot_immediately()

        # This check ensures we  don't try to initialize multiple times.
        if self._init_completed and not force_init:
            #helpers.log("Test object initialization skipped.")
            return
        
        params = self._topology_params
        for key in params:
            # Matches the following device types:
            #  Controllers: c1, c2, controller, controller1, controller2, master, slave
            #  Mininet: mn, mn1, mn2, mininet
            #  Switches: s1, s2, spine1, leaf1
            #
            match = re.match(r'^(c\d|controller\d?|master|slave|mn\d?|mininet\d?|s\d+|spine\d+|leaf\d+)$', key)
            if not match:
                helpers.environment_failure("Unknown/unsupported device type in topology file: %s" % key)
        
            #
            # !!! FIXME: Need to convert section to a factory design pattern.
            #
            host = params[key]['ip']            
            self.pingable_or_die(host)
            
            if self.is_controller(key):
                helpers.log("Setting up controller ('%s')" % key)
                n = node.ControllerNode(host)

                if 'http_port' in params[key]:
                    n.http_port = params[key]['http_port']
                else:
                    n.http_port = 8080
                    
                if 'base_url' in params[key]:
                    n.base_url = params[key]['base_url'] % (n.ip, n.http_port)
                else:
                    n.base_url =  'http://%s:%s' % (n.ip, n.http_port) 
                
                n.rest = restclient.RestClient(base_url=n.base_url)
                
                # Shortcuts
                n.post = n.rest.post
                n.get = n.rest.get
                n.put = n.rest.put
                n.patch = n.rest.patch
                n.delete = n.rest.delete
                n.rest_content = n.rest.content
                n.rest_content_json = n.rest.content_json
                n.rest_result = n.rest.result
                n.rest_result_json = n.rest.result_json
                
                n.dev = devconf.ControllerDevConf(host=n.ip,
                                                  user=self.controller_user(),
                                                  password=self.controller_password())
                
                # Shortcuts
                n.cli = n.dev.cli           # CLI mode
                n.enable = n.dev.enable     # Enable mode
                n.config = n.dev.config     # Configuration mode
                n.bash   = n.dev.bash       # Bash mode
                n.cli_content = n.dev.content
                n.cli_result = n.dev.result
                
                self._topology[key] = n

            # !!! FIXME: This is a hack to get things going for now...
            if self.is_mininet(key):
                helpers.log("Setting up Mininet ('%s')" % key)
                n = node.MininetNode(host)
                
                if 'topology' in params[key]:
                    n.topology = params[key]['topology']
                else:
                    helpers.environment_failure("Mininet topology is missing.")

                if 'type' not in params[key]:
                    helpers.environment_failure("Must specify a Mininet type in topology file ('t6' or 'basic').")

                mn_type = params[key]['type'].lower()
                if mn_type not in ('t6', 'basic'):
                    helpers.environment_failure("Mininet type must be 't6' or 'basic'.") 
                    
                helpers.log("Mininet type: %s" % mn_type)
                helpers.log("Setting up mininet ('%s')" % key)

                if mn_type == 't6':
                    n.dev = devconf.T6MininetDevConf(host=n.ip,
                                                     user=self.mininet_user(),
                                                     password=self.mininet_password(),
                                                     controller=self.controller().ip,
                                                     topology=n.topology)
                elif mn_type == 'basic':
                    n.dev = devconf.MininetDevConf(host=n.ip,
                                                   user=self.mininet_user(),
                                                   password=self.mininet_password(),
                                                   controller=self.controller().ip,
                                                   topology=n.topology)

                # Shortcuts
                n.cli = n.dev.cli
                n.cli_content = n.dev.content
                n.cli_result = n.dev.result
                
                self._topology[key] = n

        helpers.log("Exscript driver for '%s': %s"
                    % (key, n.dev.conn.get_driver()))
        helpers.log("Platform is %s" % n.platform())

        helpers.prettify_log("self._topology", self._topology)
        helpers.log("Test object initialization completed.") 
        self._init_completed = True


def test_singleton():
    t = Test()
    x = Test()
    x._bsn_config = "XYZ"
    
    assert t._bsn_config == x._bsn_config, \
        ("t._bsn_config('%s') should equal x._bsn_config('%s')"
         % (t._bsn_config, x._bsn_config))

    
if __name__ == '__main__':
    import os
    import sys
    
    os.environ['IS_GOBOT'] = 'True'
    
    if os.environ.has_key("BIGROBOT_PATH") is False:
        print("Error: Please set the environment variable BIGROBOT_PATH.")
        sys.exit(1)
    autobot_path = os.environ["BIGROBOT_PATH"]
    sys.path.append(autobot_path)
    
    #test_singleton()

    t = Test()
