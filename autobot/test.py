import autobot.helpers as helpers
import autobot.restclient as restclient
import autobot.node as node
import re
#import bigtest
#import bigtest.controller
#from bigtest.util import *


class Test(object):
    """
    Test class is a singleton which contains important test states for the current
    robot execution. E.g., topology information including device IP addresses,
    roles (controller, switch, spine, leaf), interfaces, and so on...
    """

    _instance = None

    # Singleton pattern. Code borrowed from
    # http://developer.nokia.com/Community/Wiki/How_to_make_a_singleton_in_Python    
    class Singleton:
        def __init__(self):
            # This flag ensures that we only do setup once
            self._init_completed = False
            
            config = ''.join((helpers.bigrobot_config_path(), '/bsn.yaml'))
            self._bsn_config = helpers.load_config(config)

            topo = helpers.bigrobot_topology()
            helpers.error_exit_if_file_not_exist("Topology file not found", topo)
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

    def topology(self, node=None):
        if node:
            return self._topology[node]
        else:
            return self._topology
    
    def controller(self):
        return self.topology('c1')
    
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

    def initialize(self, force_init=False):
        """
        Initializes the test object. This should be called prior to test case
        execution (e.g., called by Test Suite or Test Case setup).
        """

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
            n = node.Node(params[key]['ip'])
            
            if self.is_controller(key):
                if 'http_port' in params[key]:
                    n.http_port = params[key]['http_port']
                else:
                    n.http_port = 8080
                    
                if 'base_url' in params[key]:
                    n.base_url = params[key]['base_url'] % (n.ip, n.http_port)
                else:
                    n.base_url =  'http://%s:%s' % (n.ip, n.http_port) 
                
                n.rest = restclient.RestClient(base_url=n.base_url)
                self._topology[key] = n
                helpers.log("Configure the controller ('%s')" % key)

            # !!! FIXME: This is a hack to get things going for now...
            if self.is_mininet(key):
                #env = bigtest.controller.TwoNodeTest()
                #mininetNode = env.node2()
                #mininetCli = mininetNode.cli()
                #self._topology[key] = mininetCli
                helpers.log("Configure the mininet ('%s')" % key)

            
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
