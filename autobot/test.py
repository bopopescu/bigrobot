import autobot.helpers as helpers
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
            self._init_in_progress = False
            self._init_completed = False
            self._setup_in_progress = False
            self._setup_completed = False
            
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

    def topology(self, name=None, node=None):
        if not self._init_in_progress:
            self._init_in_progress = True
            self.initialize()

            # Proceed with setup, but only after init completes        
            if not self._setup_in_progress:
                self._setup_in_progress = True
                self.setup()

        #helpers.prettify_log("_topology:", self._topology)
        if name and node:
            self._topology[name] = node
            return node
        elif name:
            if name not in self._topology:
                helpers.environment_failure("Device '%s' is not found in topology" % name)
            return self._topology[name]
        else:
            return self._topology

    def controller(self, name='c1'):
        if name == 'master':
            if self.controller_rest_is_master('c1'):
                node = 'c1'
            elif self.controller_rest_is_master('c2'):
                node = 'c2'
            else:
                helpers.environment_failure("Neither 'c1' nor 'c2' is the master. This is an impossible state!")
            helpers.log("Device '%s' is the master" % node)
        elif name == 'slave':
            if not self.controller_rest_is_master('c1'):
                return self.topology('c1')
            elif not self.controller_rest_is_master('c2'):
                return self.topology('c2')
            else:
                helpers.environment_failure("Neither 'c1' nor 'c2' is the slave. This is an impossible state!")
            helpers.log("Device '%s' is the slave" % node)
        else:
            node = name

        return self.topology(node)
    
    def mininet(self):
        return self.topology('mn')
    
    def node(self, name):
        return self.topology(name)
    
    def initialize(self):
        """
        Initializes the test topologt. This should be called prior to test case
        execution (e.g., called by Test Suite or Test Case setup).
        """

        # This check ensures we  don't try to initialize multiple times.
        if self._init_completed:
            #helpers.log("Test object initialization skipped.")
            return
        
        params = self._topology_params
        
        if 'c1' not in params:
            helpers.environment_failure("Must have a controller (c1) defined")
        controller_ip = params['c1']['ip']   # Mininet needs this bit of info
        helpers.log("Controller IP address is %s" % controller_ip)
        
        for key in params:
            # Matches the following device types:
            #  Controllers: c1, c2, controller, controller1, controller2, master, slave
            #  Mininet: mn, mn1, mn2, mininet
            #  Switches: s1, s2, spine1, leaf1
            #
            match = re.match(r'^(c\d|controller\d?|master|slave|mn\d?|mininet\d?|s\d+|spine\d+|leaf\d+)$', key)
            if not match:
                helpers.environment_failure("Unknown/unsupported device type in topology file: %s" % key)
        
            host = params[key]['ip']            
            
            t = self   # Test handle
            
            if helpers.is_controller(key):
                helpers.log("Initializing controller '%s'" % key)
                n = node.ControllerNode(key, host,
                                        self.controller_user(),
                                        self.controller_password(),
                                        t)
            if helpers.is_mininet(key):
                helpers.log("Initializing Mininet '%s'" % key)
                n = node.MininetNode(key, host, controller_ip,
                                     self.mininet_user(),
                                     self.mininet_password(),
                                     t)
            self.topology(key, n)

            helpers.log("Exscript driver for '%s': %s"
                        % (key, n.dev.conn.get_driver()))
            helpers.log("Node '%s' is platform '%s'" % (key, n.platform()))

        helpers.prettify_log("self._topology: ", self._topology)
        helpers.log("Test object initialization completed.") 
        self._init_completed = True

    def leading_spaces(self, s):
        return len(s) - len(s.lstrip(' '))
                     
    def parse_running_config(self, config):
        data = {}
        lines = config.split('\n')

        # Ignore 1st line: contains command string
        # Ignore last line: contains device prompt
        i = 1
        while i < len(lines) - 1:
            line = lines[i]
            if re.match(r'^!', line):        # remove comments
                i += 1
                continue
            if line.strip() == '':           # remove empty lines
                i += 1
                continue
            helpers.log("Line %s: %s" % (i, line))
            if re.match(r'^\w+', line):
                key, val = line.split(' ', 1)
                data[key] = val
            i += 1
        return data
             
    def controller_cli_show_version(self, name):
        n = self.topology(name)
        n.cli('show version')

    def controller_cli_show_running_config(self, name):
        n = self.topology(name)
        n.enable('show running-config', quiet=True)
        return n.cli_content()
    
    def controller_get_node_ids(self, config):
        lines = config.split('\n')
        node_ids = []
        for line in lines:
            match = re.match(r'^controller-node (.+)$', line)
            if match:
                node = match.group(1)
                node = node.strip()
                node_ids.append(node)
        return node_ids
    
    def controller_cli_firewall_allow_rest_access(self, name, node_id):
        n = self.topology(name)
        n.config('controller-node %s' % node_id)
        n.config('interface Ethernet 0')
        n.config('firewall allow tcp 8000')
        n.config('firewall allow tcp 8082')
        n.config('exit')
        n.config('exit')
        
    def setup_controller_firewall_allow_rest_access(self, name):
        helpers.log("Enabling REST access via firewall filters")
        n = self.topology(name)
        platform = n.platform()
        
        if helpers.is_bvs(platform):
            # Currently REST is enabled by default
            pass
        elif helpers.is_bigtap(platform) or helpers.is_bigwire(platform):
            self.controller_cli_show_version(name)
            config = self.controller_cli_show_running_config(name)
            node_ids = self.controller_get_node_ids(config)
            helpers.log("node_ids: %s" % node_ids)
            for node_id in node_ids:
                self.controller_cli_firewall_allow_rest_access(name, node_id)
        else:
            helpers.environment_failure("Inconceivable!!!")
    
    def setup_controller_http_session_cookie(self, name):
        n = self.topology(name)
        platform = n.platform()

        helpers.log("Setting up HTTP session cookies for REST access")

        if helpers.is_bvs(platform):
            url = "/api/v1/auth/login"
        elif helpers.is_bigtap(platform) or helpers.is_bigwire(platform):
            url = "/auth/login"

        result = n.rest.post(url, {"user":"admin", "password":"adminadmin"})
        session_cookie = result['content']['session_cookie']
        n.rest.set_session_cookie(session_cookie)

    def controller_rest_is_master(self, name):
        n = self.topology(name)
        platform = n.platform()

        if helpers.is_bigtap(platform) or helpers.is_bigwire(platform):
            http_port = 8000
            url = "http://%s:%s/rest/v1/system/ha/role" % (n.ip, http_port)
            n.rest.get(url)
            content = n.rest.content()
            helpers.log("content: %s" % content)
            if content['role'] == "MASTER":
                return True
            else:
                return False
        elif helpers.is_bvs(platform):
            helpers.log("Device '%s' is platform 'bvs'. HA is not supported."
                        % name)
            return True

    def setup(self):
        # This check ensures we  don't try to setup multiple times.
        if self._setup_completed:
            #helpers.log("Test object setup skipped.")
            return

        params = self._topology_params
        for key in params:
            if helpers.is_controller(key):
                self.setup_controller_firewall_allow_rest_access(key)
                self.setup_controller_http_session_cookie(key)
                
        self._setup_completed = True
    

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
