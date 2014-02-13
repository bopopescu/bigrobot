import autobot.helpers as helpers
import autobot.node as a_node
import autobot.ha_wrappers as ha_wrappers
import re
# import bigtest
# import bigtest.controller
# from bigtest.util import *


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
            self._has_a_controller = False
            self._has_a_single_controller = False
            self._has_a_topo_file = False
            self._params = {}
            self._bigtest_node_info = {}

            # A node in BigRobot may have a role associated with it. One way
            # you can refer to a node using it's defined name, e.g., 'c1',
            # 'c2', 's1', 'mn', etc. Another way is to refer to its role.
            # For HA,  'master' and 'slave' are considered as dynamic roles,
            # since the role will change when mastership changes. You can also
            # define static roles such as:
            #    s1:
            #        role: leaf1
            #    s2:
            #        role: spine1
            # Test class maintains a lookup table with self._node_static_roles.
            #
            self._node_static_roles = {}

            self._bsn_config_file = ''.join((helpers.get_path_autobot_config(),
                                             '/bsn.yaml'))
            helpers.log("Loading config file %s" % self._bsn_config_file)
            self._bsn_config = helpers.load_config(self._bsn_config_file)

            self._is_ci = helpers.bigrobot_continuous_integration()

            controller_id = 1
            mininet_id = 1
            params_dict = {}

            if self._is_ci.lower() == "true":
                helpers.info("BigRobot Continuous Integration environment")
                self._bigtest_node_info = helpers.bigtest_node_info()
                helpers.info("BigTest node info:\n%s"
                             % helpers.prettify(self._bigtest_node_info))
                for key in self._bigtest_node_info:
                    if re.match(r'^node-controller', key):
                        c = "c" + str(controller_id)
                        controller_id += 1
                        ip = self._bigtest_node_info[key]['ipaddr']
                        params_dict[c] = {}
                        params_dict[c]['ip'] = ip
                        helpers.debug("'%s' IP address is '%s'"
                                      % (c, ip))
                    if re.match(r'^node-mininet', key):
                        m = "mn" + str(mininet_id)
                        mininet_id += 1
                        ip = self._bigtest_node_info[key]['ipaddr']
                        params_dict[m] = {}
                        params_dict[m]['ip'] = ip
                        helpers.debug("'%s' IP address is '%s'"
                                      % (m, ip))
                yaml_str = helpers.to_yaml(params_dict)
                self._params_file = '/var/run/bigtest/params.topo'

                helpers.info("Writing params to file '%s'" % self._params_file)
                helpers.file_write_once(self._params_file, yaml_str)

                helpers.bigrobot_params(new_val=self._params_file)

            self.load_topology()
            self.init_role_lookup_table()

            if 'mn' in self._topology_params:
                helpers.debug("Changing node name 'mn' to 'mn1'")
                self._topology_params['mn1'] = self._topology_params['mn']
                del self._topology_params['mn']

            # Reading from params file and overriding attributes in
            # topo file with values from params.
            params_file = helpers.bigrobot_params()
            if params_file.lower() != 'none':
                if helpers.file_not_exists(params_file):
                    helpers.environment_failure("Params file '%s' does not exist"
                                                % params_file)
                self._params = helpers.load_config(params_file)
                for n in self._params:
                    if n not in self._topology_params:
                        helpers.environment_failure("Node '%s' is not specified in topo file"
                                                    % n)
                    for key in self._params[n]:
                        if key not in self._topology_params[n]:
                            helpers.warn("Node '%s' does not have attribute '%s' defined. Populating it from params file."
                                         % (n, key))
                        elif key in self._topology_params[n] and self._topology_params[n][key].lower() != 'dummy':
                            helpers.warn("Node '%s' has attribute '%s' defined with value '%s'. Overriding it with value from params file."
                                         % (n, key, self._topology_params[n][key]))
                        helpers.info("Node '%s' attribute '%s' gets value '%s'"
                                     % (n, key, self._params[n][key]))
                        self._topology_params[n][key] = self._params[n][key]

            self._topology = {}

        def load_topology(self):
            topo = helpers.bigrobot_topology()
            if helpers.file_not_exists(topo):
                helpers.warn("Topology file not specified (%s)" % topo)
                self._topology_params = {}
            else:
                helpers.log("Loading topology file %s" % topo)
                self._topology_params = helpers.load_config(topo)
                self._has_a_topo_file = True

        def init_role_lookup_table(self):
            pass

    def __init__(self):
        if Test._instance is None:
            Test._instance = Test.Singleton()
        self._EventHandler_instance = Test._instance

    def __getattr__(self, attr):
        return getattr(self._instance, attr)

    def __setattr__(self, attr, val):
        return setattr(self._instance, attr, val)

    def bsn_config(self, key):
        if key in self._bsn_config:
            return self._bsn_config[key]
        else:
            helpers.test_error("Attribute '%s' is not defined in %s" %
                               (key, self._bsn_config_file))

    def controller_user(self):
        return self.bsn_config('controller_user')

    def controller_password(self):
        return self.bsn_config('controller_password')

    def mininet_user(self):
        return self.bsn_config('mininet_user')

    def mininet_password(self):
        return self.bsn_config('mininet_password')

    def host_user(self):
        return self.bsn_config('host_user')

    def host_password(self):
        return self.bsn_config('host_password')

    def switch_user(self):
        return self.bsn_config('switch_user')

    def switch_password(self):
        return self.bsn_config('switch_password')

    def topology_params(self, node=None, key=None, default=None):
        """
        Returns the topology dictionary.
        {   'c1': {
                'ip': '10.192.5.116'
            },
            'mn': {
                'ip': '10.192.7.205'
            },
            's1': {
                'ip': '10.195.0.31',
                'user': 'admin',
                'password': 'bsn'
            },
            'h1': {
                'ip': '10.193.0.120'
            }
            ...
        }
        """
        if node:
            if node not in self._topology_params:
                helpers.test_error("Node '%s' is not defined in topology file"
                                   % node)
            else:
                if key:
                    if key not in self._topology_params[node]:
                        if default:
                            self._topology_params[node][key] = default
                            return default
                        helpers.test_error("Node '%s' does not have attribute '%s' defined"
                                           % (node, key))
                    else:
                        return self._topology_params[node][key]
                else:
                    return self._topology_params[node]
        elif key:
            helpers.test_error("Key '%s' is defined but not associated with a node"
                               % key)
        return self._topology_params

    # Alias
    params = topology_params

    def topology_params_authen(self, name):
        """
        Given a node name, check the params info to see whether the
        user/password is specified for the node.
        """
        authen = []
        params = self.topology_params()
        if name in params:
            node = params[name]
            if 'user' in node:
                authen.append(node['user'])
            else:
                authen.append(None)
            if 'password' in node:
                authen.append(node['password'])
            else:
                authen.append(None)
        return authen

    def topology(self, name=None, node=None, ignore_error=False):
        """
        :param ignore_error: (Bool) If true, don't trigger exception when
                             name is not found.
        """
        if not self._init_in_progress:
            self.initialize()

            # Proceed with setup, but only after init completes
            if not self._setup_in_progress:
                self.setup()

        # helpers.prettify_log("_topology:", self._topology)
        if name and node:
            self._topology[name] = node
            return node
        elif name:
            if name not in self._topology:
                if ignore_error:
                    return None
                else:
                    helpers.environment_failure("Device '%s' is not found in topology" % name)
            return self._topology[name]
        else:
            return self._topology

    def is_master_controller(self, name):
        n = self.topology(name)
        platform = n.platform()

        if self._has_a_single_controller:
            # helpers.debug("Topology has a single controller. Assume it's the master.")
            return True

        if helpers.is_bigtap(platform) or helpers.is_bigwire(platform):
            # We don't want REST object to save the result from the REST
            # command to detect mastership.
            result = n.rest.get("/rest/v1/system/ha/role",
                                save_last_result=False)
            content = result['content']
            if content['role'] == "MASTER":
                return True
            else:
                return False
        elif helpers.is_bvs(platform):
            result = n.rest.get("/api/v1/data/controller/cluster",
                                save_last_result=False)
            content = result['content']
            leader_id = content[0]['status']['domain-leader']['leader-id']
            local_node_id = content[0]['status']['local-node-id']

            if leader_id == local_node_id:
                return True
            else:
                return False

    def controllers(self):
        """
        Get the handles of all the controllers.
        """
        return [n for n in self.topology_params() if re.match(r'^c\d+', n)]

    def controller(self, name='c1', resolve_mastership=False):
        """
        :param resolve_mastership: (Bool) 
                - If False, it returns the faux controller node (HaControllerNode)
                - If True, it resolves 'master' (or 'slave') to a controller
                  name (e.g., 'c1', 'c2', etc). 
        """
        t = self

        if not resolve_mastership and name in ('master', 'slave'):
            return ha_wrappers.HaControllerNode(name, t)

        if name == 'master':
            if self.is_master_controller('c1'):
                node = 'c1'
            elif self.is_master_controller('c2'):
                node = 'c2'
            else:
                helpers.environment_failure("Neither 'c1' nor 'c2' is the master. This is an impossible state!")
            helpers.log("Device '%s' is the master" % node)
        elif name == 'slave':
            if not self.is_master_controller('c1'):
                node = 'c1'
            elif not self.is_master_controller('c2'):
                node = 'c2'
            else:
                helpers.environment_failure("Neither 'c1' nor 'c2' is the slave. This is an impossible state!")
            helpers.log("Device '%s' is the slave" % node)
        else:
            node = name

        return self.topology(node)

    def mininet(self, name='mn1', *args, **kwargs):
        if name == 'mn':
            name = 'mn1'
        return self.topology(name, *args, **kwargs)

    def switches(self):
        """
        Get the handles of all the switches.
        """
        return [n for n in self.topology_params() if re.match(r'^s\d+', n)]

    def traffic_generator(self, name='tg1', *args, **kwargs):
        return self.topology(name, *args, **kwargs)

    def traffic_generators(self):
        """
        Get the handles of all the traffic generators.
        """
        return [n for n in self.topology_params() if re.match(r'^tg\d+', n)]

    def switch(self, name='s1', *args, **kwargs):
        return self.topology(name, *args, **kwargs)

    def hosts(self):
        """
        Get the handles of all the hosts.
        """
        return [n for n in self.topology_params() if re.match(r'^h\d+', n)]

    def host(self, name='h1', *args, **kwargs):
        return self.topology(name, *args, **kwargs)

    def node(self, *args, **kwargs):
        """
        Returns the handle for a node. 
        """
        if len(args) >= 1:
            node = args[0]
        elif 'name' in kwargs:
            node = kwargs['name']
        else:
            helpers.test_error("Impossible state.")

        if node == 'mn':
            node = 'mn1'

        if re.match(r'^(master|slave)$', node):
            return self.controller(*args, **kwargs)
        else:
            return self.topology(*args, **kwargs)

    def initialize(self):
        """
        Initializes the test topology. This should be called prior to test case
        execution (e.g., called by Test Suite or Test Case setup).
        """

        # This check ensures we  don't try to initialize multiple times.
        if self._init_completed:
            # helpers.log("Test object initialization skipped.")
            return
        if self._init_in_progress:
            return

        self._init_in_progress = True

        params = self.topology_params()

        if 'c1' not in params:
            helpers.warn("A controller (c1) is not defined")
            controller_ip = None
        else:
            controller_ip = params['c1']['ip']  # Mininet needs this bit of info
            self._has_a_controller = True
            # helpers.log("Controller IP address is %s" % controller_ip)

        if 'c2' not in params:
            helpers.debug("A controller (c2) is not defined")
            controller_ip2 = None
            self._has_a_single_controller = True
        else:
            controller_ip2 = params['c2']['ip']  # Mininet needs this bit of info

        for key in params:
            # Matches the following device types:
            #  Controllers: c1, c2, controller, controller1, controller2, master, slave
            #  Mininet: mn, mn1, mn2
            #  Switches: s1, s2, spine1, leaf1, filter1, delivery1
            #
            match = re.match(r'^(c\d|controller\d?|master|slave|mn\d?|mininet\d?|s\d+|spine\d+|leaf\d+|s\d+|h\d+|tg\d+)$', key)
            if not match:
                helpers.environment_failure("Unknown/unsupported device '%s'" % key)

            host = None
            if 'ip' in params[key]:
                host = params[key]['ip']

            t = self  # Test handle

            if helpers.is_controller(key):
                helpers.log("Initializing controller '%s'" % key)
                n = a_node.ControllerNode(key,
                                          host,
                                          self.controller_user(),
                                          self.controller_password(),
                                          t)
            elif helpers.is_mininet(key):
                helpers.log("Initializing Mininet '%s'" % key)
                if not self._has_a_controller:
                    helpers.environment_failure("Cannot bring up Mininet without a controller")

                # Use the OpenFlow port defined in the controller ('c1')
                # if it's defined.
                if 'openflow_port' in self.topology_params()['c1']:
                    openflow_port = self.topology_params()['c1']['openflow_port']
                else:
                    openflow_port = None

                n = a_node.MininetNode(name=key,
                                       ip=host,
                                       controller_ip=controller_ip,
                                       controller_ip2=controller_ip2,
                                       user=self.mininet_user(),
                                       password=self.mininet_password(),
                                       t=t,
                                       openflow_port=openflow_port)
            elif helpers.is_host(key):
                helpers.log("Initializing host '%s'" % key)
                n = a_node.HostNode(key,
                                    host,
                                    self.host_user(),
                                    self.host_password(),
                                    t)
            elif helpers.is_switch(key):
                helpers.log("Initializing switch '%s'" % key)
                n = a_node.SwitchNode(key,
                                      host,
                                      self.switch_user(),
                                      self.switch_password(),
                                      t)
            elif helpers.is_traffic_generator(key):
                helpers.log("Initializing traffic generator '%s'" % key)
                if 'platform' not in self.topology_params()[key]:
                    helpers.environment_failure("Traffic generator '%s' does not have platform (e.g., platform: 'ixia')"
                                                % key)
                platform = self.topology_params()[key]['platform']
                if platform.lower() == 'ixia':
                    n = a_node.IxiaNode(key, t)
                else:
                    helpers.environment_failure("Unsupported traffic generator '%s'" % platform)
            else:
                helpers.environment_failure("Not able to initialize device '%s'" % key)
            self.topology(key, n)

            if n.dev:
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
            if re.match(r'^!', line):  # remove comments
                i += 1
                continue
            if line.strip() == '':  # remove empty lines
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

        if not n.dev:
            helpers.log("DevConf session is not available for node '%s'" % name)
            return

        n.config('controller-node %s' % node_id)
        n.config('interface Ethernet 0')
        n.config('firewall allow tcp 8000')
        n.config('firewall allow tcp 8082')
        n.config('exit')
        n.config('exit')

    def setup_controller_firewall_allow_rest_access(self, name):
        n = self.topology(name)

        if not n.dev:
            helpers.log("DevConf session is not available for node '%s'" % name)
            return

        helpers.log("Enabling REST access via firewall filters")
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
            helpers.environment_failure("'%s' is not a known controller (platform=%s)" % (name, platform))

    def setup_controller_http_session_cookie(self, name):
        n = self.topology(name)

        if not n.dev:
            helpers.log("DevConf session is not available for node '%s'" % name)
            return

        platform = n.platform()

        helpers.log("Setting up HTTP session cookies for REST access on '%s' (platform=%s)"
                    % (n.name(), platform))

        if helpers.is_bvs(platform):
            url = "/api/v1/auth/login"
        elif helpers.is_bigtap(platform) or helpers.is_bigwire(platform):
            url = "/auth/login"

        return n.rest.request_session_cookie(url)

    def setup_switch(self, name):
        """
        Perform setup on SwitchLight
        - configure the controller IP address and (optional) port
        """
        n = self.topology(name)

        if not n.dev:
            helpers.log("DevConf session is not available for node '%s'" % name)
            return

        for controller in ('c1', 'c2'):
            c = self.topology(controller, ignore_error=True)
            if c:
                if 'openflow_port' in self.topology_params()[controller]:
                    openflow_port = self.topology_params()[controller]['openflow_port']
                    n.config("controller %s port %s" % (c.ip(), openflow_port))
                else:
                    n.config("controller %s" % c.ip())

    def setup(self):
        # This check ensures we  don't try to setup multiple times.
        if self._setup_completed:
            # helpers.log("Test object setup skipped.")
            return
        if self._setup_in_progress:
            return

        self._setup_in_progress = True

        params = self.topology_params()
        for key in params:
            if helpers.is_controller(key):
                self.setup_controller_firewall_allow_rest_access(key)
                self.setup_controller_http_session_cookie(key)
            elif helpers.is_switch(key):
                self.setup_switch(key)

        self._setup_completed = True
