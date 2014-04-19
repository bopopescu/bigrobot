import autobot.helpers as helpers
import autobot.node as a_node
import autobot.ha_wrappers as ha_wrappers
import autobot.utils as br_utils
import re


class Test(object):
    """
    Test class is a singleton which contains important test states for the
    current robot execution. E.g., topology information including device
    IP addresses, aliases (controller, switch, spine, leaf), interfaces, and
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
            self._current_controller_master = None
            self._current_controller_slave = None

            # A node in BigRobot may have a alias associated with it. One way
            # you can refer to a node using it's defined name, e.g., 'c1',
            # 'c2', 's1', 'mn', etc. Another way is to refer to its alias.
            # For HA,  'master' and 'slave' are considered as dynamic aliases,
            # since the alias will change when mastership changes. You can also
            # define static aliases such as:
            #    s1:
            #        alias: leaf1
            #    s2:
            #        alias: spine1
            # Test class maintains a lookup table with self._node_static_aliases.
            #
            self._node_static_aliases = {}

            self._bsn_config_file = ''.join((helpers.get_path_autobot_config(),
                                             '/bsn.yaml'))
            helpers.log("Loading config file %s" % self._bsn_config_file)
            self._bsn_config = helpers.load_config(self._bsn_config_file)

            # self._is_ci = helpers.bigrobot_continuous_integration()
            # if self._is_ci.lower() == "true":
            #    helpers.info("BigRobot Continuous Integration environment")
            #    ...do something...

            controller_id = 1
            mininet_id = 1
            params_dict = {}

            self._testbed_type = helpers.bigrobot_testbed()
            if self._testbed_type:
                helpers.info("BIGROBOT_TESTBED: %s" % self._testbed_type)
                if self._testbed_type.lower() == "bigtest":
                    self._bigtest_node_info = helpers.bigtest_node_info()
                    helpers.info("BigTest node info:\n%s"
                                 % helpers.prettify(self._bigtest_node_info))

                    # BigTest node format:
                    #   'controller-c02n01-047,mininet-c02n01-047'
                    # BigTest's "bt startremotevm" is able to bring up multiple
                    # clusters. We need to make sure to use only the VMs in the
                    # clusters assigned, else there will be conflicts.
                    bigtest_nodes = helpers.bigrobot_params_input()
                    node_names = self._bigtest_node_info.keys()
                    if bigtest_nodes:
                        node_names = ['node-' + n for n in bigtest_nodes.split(',')]
                        helpers.info("Found env BIGROBOT_PARAMS_INPUT. Limiting nodes to %s."
                                     % node_names)

                    for key in node_names:
                        if re.match(r'^node-controller', key):
                            c = "c" + str(controller_id)
                            controller_id += 1
                            ip = self._bigtest_node_info[key]['ipaddr']
                            params_dict[c] = {}
                            params_dict[c]['ip'] = ip
                            helpers.debug("'%s' IP address is '%s' (bigtest node '%s')"
                                          % (c, ip, key))
                        if re.match(r'^node-mininet', key):
                            m = "mn" + str(mininet_id)
                            mininet_id += 1
                            ip = self._bigtest_node_info[key]['ipaddr']
                            params_dict[m] = {}
                            params_dict[m]['ip'] = ip
                            helpers.debug("'%s' IP address is '%s' (bigtest node '%s')"
                                          % (m, ip, key))

                elif (self._testbed_type.lower() == "static" or
                      self._testbed_type.lower() == "libvirt"):

                    # Static nodes and libvirt nodes are similarly defined.
                    static_nodes = helpers.bigrobot_params_input()
                    helpers.info("Static (or libvirt) node info: %s"
                                 % static_nodes)

                    # Expecting a YAML config.
                    if static_nodes:
                        match = re.match(r'^file:(.+)$', static_nodes)
                        if match:
                            file = match.group(1)
                            if helpers.file_not_exists(file):
                                helpers.test_error("BIGROBOT_PARAMS_INPUT file '%s' does not exist." % file)
                            else:
                                params_dict = helpers.load_config(file)
                        else:
                            helpers.test_error("For static testbed, env BIGROBOT_PARAMS_INPUT has format 'file:<path_and_filename>'.")
                    else:
                        helpers.test_error("For static testbed, must define env BIGROBOT_PARAMS_INPUT. Format is:\n"
                                           "\texport BIGROBOT_PARAMS_INPUT=file:<path_and_filename>")
                else:
                    helpers.test_error("Supported testbed type is 'bigtest', 'libvirt', or 'static'.")

                yaml_str = helpers.to_yaml(params_dict)

                # This file contain a list of nodes:
                #   c1: {ip: 10.192.5.221}
                #   c2: {ip: 10.192.5.222}
                #   mn1: {ip: 10.192.7.175}
                #   ...and so on...
                self._params_file = helpers.bigrobot_log_path_exec_instance() + '/params.topo'

                helpers.info("Writing params to file '%s'" % self._params_file)
                helpers.file_write_once(self._params_file, yaml_str)
                helpers.bigrobot_params(new_val=self._params_file)

            self._topology_params = self.load_topology()
            if self._topology_params:
                self._has_a_topo_file = True

            self.init_alias_lookup_table()

            if 'mn' in self._topology_params:
                helpers.debug("Changing node name 'mn' to 'mn1'")
                self._topology_params['mn1'] = self._topology_params['mn']
                del self._topology_params['mn']

            self.merge_params_attributes()

            self._topology = {}

        def merge_params_attributes(self):
            """
            Reading from params file and merge attributes with topo file
            """
            params_file = helpers.bigrobot_params()
            if params_file.lower() != 'none':
                if helpers.file_not_exists(params_file):
                    helpers.environment_failure("Params file '%s' does not exist"
                                                % params_file)
                self._params = helpers.load_config(params_file)
                for n in self._topology_params:
                    if n not in self._params:
                        helpers.environment_failure("Node '%s' is not"
                                                    " specified in params file"
                                                    % n)
                    for key in self._params[n]:
                        if key not in self._topology_params[n]:
                            helpers.warn("Node '%s' does not have attribute"
                                         " '%s' defined. Populating it from"
                                         " params file."
                                         % (n, key))
                        elif key in self._topology_params[n] and self._topology_params[n][key].lower() != 'dummy':
                            helpers.warn("Node '%s' has attribute '%s' defined"
                                         " with value '%s'. Overriding it with"
                                         " value from params file."
                                         % (n, key, self._topology_params[n][key]))
                        helpers.info("Node '%s' attribute '%s' gets value '%s'"
                                     % (n, key, self._params[n][key]))
                        self._topology_params[n][key] = self._params[n][key]

        def load_topology(self):
            topo = helpers.bigrobot_topology()
            if helpers.file_not_exists(topo):
                helpers.warn("Topology file not specified (%s)" % topo)
                topo = {}
            else:
                helpers.log("Loading topology file %s" % topo)
                topo = helpers.load_config(topo)
            return topo

        def init_alias_lookup_table(self):
            for node in self._topology_params:
                self._node_static_aliases[node] = node
                if 'alias' in self._topology_params[node]:
                    alias = self._topology_params[node]['alias']
                    self._node_static_aliases[alias] = node

                    # BSN QA convention is to name the aliases as:
                    #   spine0, spine1, etc.
                    #   leaf1-a, leaf1-b, leaf2-a, leaf2-b, etc.
                    #   s021, etc.
                    if not re.match(r'^(leaf\d+-[ab]|spine\d+|s\d+)', alias):
                        helpers.warn("Supported aliases are leaf{n}-{a|b}, spine{n}, s{nnn}")
                        helpers.environment_failure("'%s' has alias '%s' which does not match the allowable alias names"
                                                    % (node, alias))
            self._node_static_aliases['master'] = 'master'
            self._node_static_aliases['slave'] = 'slave'
            self._node_static_aliases['mn'] = 'mn1'
            self._node_static_aliases['mn1'] = 'mn1'
            helpers.log("Node aliases:\n%s"
                        % helpers.prettify(self._node_static_aliases))

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

    def alias(self, name, ignore_error=False):
        """
        :param ignore_error: (Bool) If true, don't trigger exception when
                             name is not found.
        """
        if not name in self._node_static_aliases:
            if ignore_error:
                return name
            helpers.environment_failure("Alias '%s' is not defined" % name)
        return self._node_static_aliases[name]

    def topology_params(self, node=None, key=None, default=None):
        """
        Usage:
        - t.params('c1')  # return attributes for c1
          t.params(node='c1', key='ip')
          t.params(node='tg1', key='type', default='ixia')
                            # if type is not defined, return 'ixia' for type
        - If no argument is specified, return the entire topology dictionary.
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
            node = self.alias(node)
            if node not in self._topology_params:
                helpers.environment_failure("Node '%s' is not defined in topology file"
                                            % node)
            else:
                if key:
                    if key not in self._topology_params[node]:
                        if default:
                            self._topology_params[node][key] = default
                            return default
                        helpers.environment_failure("Node '%s' does not have attribute '%s' defined"
                                           % (node, key))
                    else:
                        return self._topology_params[node][key]
                else:
                    return self._topology_params[node]
        elif key:
            helpers.environment_failure("Key '%s' is defined but not associated with a node"
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
        name = self.alias(name)
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
            name = self.alias(name, ignore_error=ignore_error)
            self._topology[name] = node
            return node
        elif name:
            name = self.alias(name, ignore_error=ignore_error)
            if name not in self._topology:
                if ignore_error:
                    return None
                else:
                    helpers.environment_failure("Device '%s' is not found in topology" % name)
            return self._topology[name]
        else:
            return self._topology

    def is_master_controller(self, name):
        name = self.alias(name)
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

            if 'domain-leader' not in content[0]['status']:
                helpers.environment_failure("HA issue - 'domain-leader' is not found.")
            if 'leader-id' not in content[0]['status']['domain-leader']:
                helpers.environment_failure("HA issue - 'leader-id' is not found.")

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
        return [self.controller(n) for n in self.topology_params() if re.match(r'^c\d+', n)]

    def controller(self, name='c1', resolve_mastership=False):
        """
        :param resolve_mastership: (Bool)
                - If False, it returns the faux controller node (HaControllerNode)
                - If True, it resolves 'master' (or 'slave') to a controller
                  name (e.g., 'c1', 'c2', etc).
        """
        t = self
        name = self.alias(name)

        if not resolve_mastership and name in ('master', 'slave'):
            return ha_wrappers.HaControllerNode(name, t)

        if name == 'master':
            if self.is_master_controller('c1'):
                node = 'c1'
            elif self.is_master_controller('c2'):
                node = 'c2'
            else:
                helpers.environment_failure("Neither 'c1' nor 'c2' is the"
                                            " master. This is an impossible"
                                            " state!")
            helpers.log("Device '%s' is the master" % node)
            self._current_controller_master = node
        elif name == 'slave':
            if not self.is_master_controller('c1'):
                node = 'c1'
            elif not self.is_master_controller('c2'):
                node = 'c2'
            else:
                helpers.environment_failure("Neither 'c1' nor 'c2' is the"
                                            " slave. This is an impossible"
                                            " state!")
            helpers.log("Device '%s' is the slave" % node)
            self._current_controller_slave = node
        else:
            node = name

        return self.topology(node)

    def mininet(self, name='mn1', *args, **kwargs):
        name = self.alias(name)
        if name == 'mn':
            name = 'mn1'
        return self.topology(name, *args, **kwargs)

    def traffic_generators(self):
        """
        Get the handles of all the traffic generators.
        """
        return [self.traffic_generator(n) for n in self.topology_params() if re.match(r'^tg\d+', n)]

    def traffic_generator(self, name='tg1', *args, **kwargs):
        name = self.alias(name)
        return self.topology(name, *args, **kwargs)

    def switches(self):
        """
        Get the handles of all the switches.
        """
        return [self.switch(n) for n in self.topology_params() if re.match(r'^s\d+', n)]

    def switch(self, name='s1', *args, **kwargs):
        name = self.alias(name)
        return self.topology(name, *args, **kwargs)

    def openstack_servers(self):
        """
        Get the handles of all the OpenStack servers.
        """
        return [self.openstack_server(n) for n in self.topology_params() if re.match(r'^os\d+', n)]

    def openstack_server(self, name='os1', *args, **kwargs):
        name = self.alias(name)
        return self.topology(name, *args, **kwargs)

    def hosts(self):
        """
        Get the handles of all the hosts.
        """
        return [self.host(n) for n in self.topology_params() if re.match(r'^h\d+', n)]

    def host(self, name='h1', *args, **kwargs):
        name = self.alias(name)
        return self.topology(name, *args, **kwargs)

    def node(self, *args, **kwargs):
        """
        Returns the handle for a node.
        """
        if len(args) >= 1:
            node = self.alias(args[0])
        elif 'name' in kwargs:
            node = self.alias(kwargs['name'])
        else:
            helpers.environment_failure("Impossible state.")

        if node == 'mn':
            node = 'mn1'

        if re.match(r'^(master|slave)$', node):
            return self.controller(*args, **kwargs)
        else:
            return self.topology(*args, **kwargs)

    def node_spawn(self, ip, node=None, user=None, password=None,
                   device_type='controller'):
        t = self
        if not node:
            node = 'node-%s' % ip

        if device_type == 'controller':
            helpers.log("Initializing controller '%s'" % node)
            user = self.controller_user() if not user else user
            if not password:
                password = self.controller_password()
            n = a_node.ControllerNode(node, ip, user, password, t)
        elif device_type == 'switch':
            helpers.log("Initializing switch '%s'" % node)
            if not user:
                user = self.switch_user()
            if not password:
                password = self.switch_password()
            n = a_node.SwitchNode(node, ip, user, password, t)
        else:
            helpers.environment_failure("You can only spawn nodes for device"
                                        " types: 'controller', 'switch'")
        return n

    def node_connect(self, node, user=None, password=None,
                     controller_ip=None, controller_ip2=None):
        # Matches the following device types:
        #  Controllers: c1, c2, controller, controller1, controller2, master, slave
        #  Mininet: mn, mn1, mn2
        #  Switches: s1, s2, spine1, leaf1, filter1, delivery1
        #  Hosts: h1, h2, h3
        #  OpenStack servers: os1, os2
        #  Traffic generators: tg1, tg2
        #
        match = re.match(r'^(c\d|controller\d?|master|slave|mn\d?|mininet\d?|s\d+|spine\d+|leaf\d+|s\d+|h\d+|tg\d+|os\d+)$', node)
        if not match:
            helpers.environment_failure("Unknown/unsupported device '%s'"
                                        % node)

        host = None
        params = self.topology_params()
        if 'ip' in params[node]:
            host = params[node]['ip']

        t = self  # Test handle


        # Check for user name and password. Here is the order of preference:
        # 1) prefer user/password provided in method arguments
        # 2) else prefer user/password provided in topo file
        # 3) else prefer user/password provided in config/bsn.yaml

        authen = t.topology_params_authen(node)

        if user:
            pass
        elif authen[0]:
            user = authen[0]

        if password:
            pass
        elif authen[1]:
            password = authen[1]

        if helpers.is_controller(node):
            n = self.node_spawn(ip=host, node=node, user=user,
                                password=password, device_type='controller')
        elif helpers.is_switch(node):
            n = self.node_spawn(ip=host, node=node, user=user,
                                password=password, device_type='switch')
        elif helpers.is_mininet(node):
            helpers.log("Initializing Mininet '%s'" % node)
            if not self._has_a_controller:
                helpers.environment_failure("Cannot bring up Mininet without"
                                            " a controller")

            # Use the OpenFlow port defined in the controller ('c1')
            # if it's defined.
            if 'openflow_port' in self.topology_params()['c1']:
                openflow_port = self.topology_params()['c1']['openflow_port']
            else:
                openflow_port = None

            if not user:
                user = self.mininet_user()
            if not password:
                password = self.mininet_password()

            n = a_node.MininetNode(name=node,
                                   ip=host,
                                   controller_ip=controller_ip,
                                   controller_ip2=controller_ip2,
                                   user=user,
                                   password=password,
                                   t=t,
                                   openflow_port=openflow_port)

        elif helpers.is_host(node):
            helpers.log("Initializing host '%s'" % node)

            if not user:
                user = self.host_user()
            if not password:
                password = self.host_password()

            n = a_node.HostNode(node,
                                host,
                                user=user,
                                password=password,
                                t=t)

        elif helpers.is_openstack_server(node):
            helpers.log("Initializing OpenStack server '%s'" % node)

            if not user:
                user = self.host_user()
            if not password:
                password = self.host_password()

            n = a_node.OpenStackNode(node,
                                      host,
                                      user=user,
                                      password=password,
                                      t=t)

        elif helpers.is_traffic_generator(node):
            helpers.log("Initializing traffic generator '%s'" % node)
            if 'platform' not in self.topology_params()[node]:
                helpers.environment_failure("Traffic generator '%s' does not"
                                            " have platform (e.g., platform:"
                                            " 'ixia', 'bigtap-ixia')"
                                            % node)
            platform = self.topology_params()[node]['platform']
            if platform.lower() == 'ixia':
                n = a_node.IxiaNode(node, t)
            elif platform.lower() == 'bigtap-ixia':
                n = a_node.BigTapIxiaNode(node, t)
            else:
                helpers.environment_failure("Unsupported traffic generator '%s'"
                                            % platform)

        else:
            helpers.environment_failure("Not able to initialize device '%s'"
                                        % node)

        self.topology(node, n)

        if n.devconf():
            helpers.log("Exscript driver for '%s': %s"
                        % (node, n.devconf().conn.get_driver()))
            helpers.log("Node '%s' is platform '%s'%s"
                        % (node, n.platform(),
                           br_utils.end_of_output_marker()))
        return n

    def node_reconnect(self, node, **kwargs):
        helpers.log("Node reconnect for '%s'" % node)

        # Resolve 'master' or 'slave' to actual name (e.g., 'c1', 'c2'). But
        # don't do it using REST since we've probably lost the connection.
        if helpers.is_controller(node):
            if node == 'master':
                if self._current_controller_master:
                    node_name = self._current_controller_master
                else:
                    helpers.environment_failure("Unable to resolve actual name"
                                                " of master controller.")
            elif node == 'slave':
                if self._current_controller_slave:
                    node_name = self._current_controller_slave
                else:
                    helpers.environment_failure("Unable to resolve actual name"
                                                " of slave controller.")
            else:
                node_name = node

            # node_name = self.controller(node, resolve_mastership=True).name()
        else:
            node_name = self.node(node).name()
        helpers.log("Actual node name is '%s'" % node_name)
        c = self.node_connect(node_name, **kwargs)
        c.rest.request_session_cookie()
        return self.node(node)

    def initialize(self):
        """
        Initializes the test topology. This should be called prior to test case
        execution (e.g., called by Test Suite or Test Case setup).
        """

        # This check ensures we  don't try to initialize multiple times.
        if self._init_completed:
            # helpers.log("Test object initialization skipped.")
            return

        helpers.debug("Test object initialization begins.")
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

        # Node initialization sequence:
        #   It is required that we initialize the controllers first since they
        #   may be required by the other nodes, Mininet for example.
        all_nodes = params.keys()
        controller_nodes = sorted(filter(lambda x: 'c' in x, all_nodes))
        non_controller_nodes = [x for x in all_nodes if x not in controller_nodes]
        list_of_nodes = controller_nodes + non_controller_nodes

        helpers.debug("List of nodes (controllers must appear first): %s"
                      % list_of_nodes)
        for key in list_of_nodes:
            self.node_connect(key,
                              controller_ip=controller_ip,
                              controller_ip2=controller_ip2)

        helpers.prettify_log("self._topology: ", self._topology)
        self._init_completed = True
        helpers.debug("Test object initialization ends.%s"
                      % br_utils.end_of_output_marker())

    def init_completed(self):
        """
        We may need to do something only during the initialization phase of
        the test object. This flag tells us if we've completed the init phase.
        """
        return self._init_completed

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

    def _controller_cli_firewall_allow_rest_access(self, name, node_id):
        n = self.topology(name)
        n.config('controller-node %s' % node_id)
        n.config('interface Ethernet 0')
        n.config('firewall allow tcp 8000')
        n.config('firewall allow tcp 8082')
        n.config('exit')
        n.config('exit')

    def setup_controller_firewall_allow_rest_access(self, name):
        n = self.topology(name)

        helpers.log("Enabling REST access via firewall filters")
        platform = n.platform()

        if helpers.is_bvs(platform):
            helpers.log("REST is enabled by default for BVS platform")
        elif helpers.is_bigtap(platform) or helpers.is_bigwire(platform):
            config = self.controller_cli_show_running_config(name)
            node_ids = self.controller_get_node_ids(config)
            helpers.log("node_ids: %s" % node_ids)
            for node_id in node_ids:
                self._controller_cli_firewall_allow_rest_access(name, node_id)
        else:
            helpers.environment_failure("'%s' is not a known controller"
                                        " (platform=%s)"
                                        % (name, platform))

    def setup_controller_http_session_cookie(self, name):
        n = self.topology(name)
        return n.rest.request_session_cookie()


    def setup_controller_pre_clean_config(self, name):
        """
        Perform setup on BSN controllers before calling clean configuration.
        """
        n = self.topology(name)

        if not n.devconf():
            helpers.log("DevConf session is not available for node '%s'"
                        % name)
            return

        helpers.log("Setting up controllers - before clean config")

        self.controller_cli_show_version(name)
        self.setup_controller_firewall_allow_rest_access(name)
        self.setup_controller_http_session_cookie(name)

    def setup_controller_post_clean_config(self, name):
        """
        Perform setup on BSN controllers after calling clean configuration.
        """
        n = self.topology(name)

        if not n.devconf():
            # helpers.log("DevConf session is not available for node '%s'"
            #            % name)
            return

        helpers.log("Setting up controllers - after clean config")
        # For now it's just a placeholder...

    def setup_switch_pre_clean_config(self, name):
        """
        Perform setup on SwitchLight after calling clean configuration.
        - configure the controller IP address and (optional) port
        """
        n = self.topology(name)

        if not n.devconf():
            # helpers.log("DevConf session is not available for node '%s'"
            #            % name)
            return

        if helpers.is_switchlight(n.platform()):
            helpers.log("Setting up switches (SwitchLight) - before clean config")
            # For now it's just a placeholder...

    def setup_switch_post_clean_config(self, name):
        """
        Perform setup on SwitchLight after calling clean configuration.
        - configure the controller IP address and (optional) port
        """
        n = self.topology(name)

        if not n.devconf():
            helpers.log("DevConf session is not available for node '%s'"
                        % name)
            return

        if helpers.is_switchlight(n.platform()):
            helpers.log("Setting up switches (SwitchLight) - after clean config")
            for controller in ('c1', 'c2'):
                c = self.topology(controller, ignore_error=True)
                if c:
                    if 'openflow_port' in self.topology_params()[controller]:
                        openflow_port = self.topology_params()[controller]['openflow_port']
                        n.config("controller %s port %s"
                                 % (c.ip(), openflow_port))
                    else:
                        n.config("controller %s" % c.ip())
            n.config("copy running-config startup-config")

    def teardown_switch(self, name):
        """
        Perform teardown on SwitchLight
        - delete the controller IP address
        """
        n = self.topology(name)

        if not n.devconf():
            helpers.log("DevConf session is not available for node '%s'"
                        % name)
            return

        if helpers.is_switchlight(n.platform()):
            helpers.log("Tearing down switches (SwitchLight)")
            content = n.config("show running-config")['content']
            lines = content.splitlines()

            # Find lines with the following config statements:
            #   controller 10.192.5.51
            #   controller 10.192.104.1 port 6633
            lines = filter(lambda x: 'controller' in x, lines)

            for line in lines:
                # Form commands:
                #   no controller 10.192.5.51
                #   no controller 10.192.104.1 port 6633
                cmd = 'no ' + line
                n.config(cmd)

    def setup(self):
        # This check ensures we  don't try to setup multiple times.
        if self._setup_completed:
            # helpers.log("Test object setup skipped.")
            return

        if self._setup_in_progress:
            return

        helpers.debug("Test object setup begins.")
        self._setup_in_progress = True

        params = self.topology_params()
        helpers.debug("Topology info:\n%s" % helpers.prettify(params))

        if helpers.bigrobot_test_setup().lower() != 'false':
            for key in params:
                if helpers.is_controller(key):
                    self.setup_controller_pre_clean_config(key)
                elif helpers.is_switch(key):
                    self.setup_switch_pre_clean_config(key)

            for key in params:
                n = self.node(key)
                if (helpers.is_controller(key) and helpers.is_t5(n.platform())
                    and self.is_master_controller(key)):
                    helpers.log("Running clean config on T5 controller '%s'"
                                " (establishing baseline config setup)" % key)
                    self.t5_clean_configuration(key)

            for key in params:
                if helpers.is_controller(key):
                    self.setup_controller_post_clean_config(key)
                elif helpers.is_switch(key):
                    self.setup_switch_post_clean_config(key)
        else:
            helpers.debug("Env BIGROBOT_TEST_SETUP is False. Skip device setup.")

        self._setup_completed = True
        helpers.debug("Test object setup ends.%s"
                      % br_utils.end_of_output_marker())

    def teardown(self):
        helpers.debug("Test object teardown begins.")
        params = self.topology_params()
        for key in params:
            if helpers.is_controller(key):
                pass
            elif helpers.is_switch(key):
                self.teardown_switch(key)
        helpers.debug("Test object teardown ends.%s"
                      % br_utils.end_of_output_marker())

    def t5_clean_configuration(self, name):
        '''
            Objective: Delete all user configuration
        '''
        t = self
        c = t.controller(name)

        helpers.log("Attempting to delete all tenants")
        url_get_tenant = '/api/v1/data/controller/applications/bvs/info/endpoint-manager/tenant'
        try:
            c.rest.get(url_get_tenant)
            content = c.rest.content()
        except:
            pass
        else:
            if (content):
                for i in range (0, len(content)):
                    url_tenant_delete = '/api/v1/data/controller/applications/bvs/tenant[name="%s"]' % content[i]['name']
                    c.rest.delete(url_tenant_delete, {})

        helpers.log("Attempting to delete all switches")
        url_get_switches = '/api/v1/data/controller/core/switch'
        try:
            c.rest.get(url_get_switches)
            content = c.rest.content()
        except:
            pass
        else:
            if (content):
                for i in range (0, len(content)):
                    if 'name' in content[i]:
                        url_switch_delete = '/api/v1/data/controller/core/switch-config[name="%s"]' % content[i]['name']
                        c.rest.delete(url_switch_delete, {})

        helpers.log("Attempting to delete all port-groups")
        url_get_portgrp = '/api/v1/data/controller/applications/bvs/port-group?config=true'
        try:
            c.rest.get(url_get_portgrp)
            content = c.rest.content()
        except:
            pass
        else:
            if (content):
                for i in range (0, len(content)):
                    url_portgrp_delete = '/api/v1/data/controller/applications/bvs/port-group[name="%s"]' % content[i]['name']
                    c.rest.delete(url_portgrp_delete, {})

        helpers.log("Attempting to delete NTP configurations")
        url_get_ntpservers = '/api/v1/data/controller/os/config/global/time-config?config=true'
        try:
            c.rest.get(url_get_ntpservers)
            content = c.rest.content()
        except:
            pass
        else:
            try:
                if (content[0]['ntp-server']):
                    ntp_list = content[0]['ntp-server']
                    for i in range (0, len(ntp_list)):
                        ntp_list.pop(0)
                        url_ntp_delete = '/api/v1/data/controller/os/config/global/time-config/ntp-server'
                        try:
                            c.rest.put(url_ntp_delete, ntp_list)
                        except:
                            pass
                        else:
                            helpers.log("NTP configuration successfully deleted")
            except:
                pass

        helpers.log("Attempting to delete SNMP Configurations")
        # Delete SNMP location
        url_delete_snmp_location = '/api/v1/data/controller/os/config/global/snmp-config/location'
        try:
            c.rest.delete(url_delete_snmp_location, {})
        except:
            pass
        else:
            helpers.log("SNMP Location configuration successfully deleted")
        # Delete SNMP Contact
        url_delete_snmp_contact = '/api/v1/data/controller/os/config/global/snmp-config/contact'
        try:
            c.rest.delete(url_delete_snmp_contact, {})
        except:
            pass
        else:
            helpers.log("SNMP Contact configuration successfully deleted")
        # Disable SNMP Trap
        url_delete_snmp_trap = '/api/v1/data/controller/os/config/global/snmp-config/trap-enabled'
        try:
            c.rest.delete(url_delete_snmp_trap, {})
        except:
            pass
        else:
            helpers.log("SNMP Trap configuration successfully deleted")
        # Delete SNMP community
        url_delete_snmp_community = '/api/v1/data/controller/os/config/global/snmp-config/community'
        try:
            c.rest.delete(url_delete_snmp_community, {})
        except:
            pass
        else:
            helpers.log("SNMP Community configuration successfully deleted")
        # Delete SNMP Trap Hosts
        url_get_snmphost = '/api/v1/data/controller/os/config/global/snmp-config?config=true'
        try:
            c.rest.get(url_get_snmphost)
        except:
            pass
        else:
            helpers.log("SNMP GET configuration successful")
            content = c.rest.content()
            if(content):
                if ('trap-host' in content[0]):
                    for i in range (0, len(content[0]['trap-host'])):
                        url_delete_trap = '/api/v1/data/controller/os/config/global/snmp-config/trap-host[ipaddr="%s"]/udp-port' % str(content[0]['trap-host'][i]['ipaddr'])
                        try:
                            c.rest.delete(url_delete_trap, {})
                        except:
                            pass
                        else:
                            url_delete_trap = '/api/v1/data/controller/os/config/global/snmp-config/trap-host[ipaddr="%s"]' % str(content[0]['trap-host'][i]['ipaddr'])
                            try:
                                c.rest.delete(url_delete_trap, {})
                            except:
                                pass
                            else:
                                helpers.log("SNMP Trap configuration successfully deleted")

        helpers.log("Attempting to delete logging server configurations")
        url_get_logging = '/api/v1/data/controller/os/config/global/logging-config?config=true'
        c.rest.get(url_get_logging)
        content = c.rest.content()
        if(content):
            if ('logging-server' in content[0]):
                for i in range (0, len(content[0]['logging-server'])):
                    url_delete_logserver = '/api/v1/data/controller/os/config/global/logging-config/logging-server[server="%s"]' % str(content[0]['logging-server'][i]['server'])
                    try:
                        c.rest.delete(url_delete_logserver, {})
                    except:
                        pass
                    else:
                        helpers.log("Logging server configuration successfully deleted")

        helpers.log("Attempting to disable remote logging")
        url_disable_remotelog = '/api/v1/data/controller/os/config/global/logging-config/logging-enabled'
        try:
            c.rest.delete(url_disable_remotelog, {})
        except:
            pass
        else:
            helpers.log("Remote logging successfully deleted")

        return True
