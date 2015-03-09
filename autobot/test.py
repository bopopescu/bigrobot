import os
import autobot.helpers as helpers
import autobot.node as a_node
import autobot.ha_wrappers as ha_wrappers
import autobot.utils as br_utils
import re
import uuid


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
            self._settings = {}
            self._checkpoint = 0
            self._is_bcf_topology = False

            # ESB environment:
            # Per convention, the consumer will pass the params data to the
            # producer (the worker). The params data has all the details about
            # the test topology which the producer can use to instantiate a
            # new test handle (an object of the Test class). The producer has
            # to prepare the test environment using the steps below.
            #
            # - Save the params data, the YAML string contained in env
            #   BIGROBOT_TOPOLOGY_FOR_ESB into a topo file
            # - Point env BIGROBOT_TOPOLOGY to the new topo file
            # - Unset env BIGROBOT_TESTBED (used for dynamic topology)
            #   - Since params data already contains the expanded topo info
            # - Unset env BIGROBOT_PARAMS_INPUT (used for dynamic topology)
            # - Diable test setup
            # - Disable test postmortem
            # - Disable test clean config
            # - Disable test ZTN
            # - Don't ping or connect to devices during initialization
            #   (see initialization())
            #
            if helpers.is_esb():
                helpers.summary_log("Enterprise Service Bus (ESB) environment")

                if helpers.bigrobot_topology_for_esb().lower() == 'none':
                    helpers.environment_failure(
                                    "Env BIGROBOT_TOPOLOGY_FOR_ESB must be"
                                    " defined when running under the"
                                    " ESB environment")
                params_file = helpers.params_to_file(
                                    helpers.bigrobot_topology_for_esb(),
                                    path=helpers.bigrobot_log_path_exec_instance())
                helpers.summary_log("ESB BIGROBOT_TOPOLOGY: %s"
                                    % helpers.bigrobot_topology(params_file))
                helpers.remove_env("BIGROBOT_TESTBED")
                helpers.remove_env("BIGROBOT_PARAMS_INPUT")
                helpers.bigrobot_test_setup("False")
                helpers.bigrobot_test_postmortem("False")
                helpers.bigrobot_test_clean_config("False")
                helpers.bigrobot_test_ztn("False")

            # A node in BigRobot may have a alias associated with it. One way
            # you can refer to a node using it's defined name, e.g., 'c1',
            # 'c2', 's1', 'mn', etc. Another way is to refer to its alias.
            # For HA,  'master' and 'slave' are considered as dynamic aliases,
            # since the alias will change when mastership changes. You can also
            # define static aliases such as:
            #    s1:
            #        alias: leaf1-a
            #    s2:
            #        alias: spine1
            # Test class maintains a lookup table with self._node_static_aliases.
            #
            self._node_static_aliases = {}

            self._bsn_config = helpers.bigrobot_config_common()
            helpers.log("Loaded config file %s" % self._bsn_config['this_file'])

            # self._is_ci = helpers.bigrobot_continuous_integration()
            # if self._is_ci.lower() == "true":
            #    helpers.info("BigRobot Continuous Integration environment")
            #    ...do something...

            controller_id = 1
            mininet_id = 1
            params_dict = {}

            # If env BIGROBOT_TESTBED is defined then we are dealing with a
            # dynamic topology.
            self._testbed_type = helpers.bigrobot_testbed()
            if self._testbed_type:
                helpers.info("BIGROBOT_TESTBED: %s" % self._testbed_type)
                if self._testbed_type.lower() == "bigtest":
                    self._bigtest_node_info = helpers.bigtest_node_info()
                    helpers.info("BigTest node info:\n%s"
                                 % helpers.prettify(self._bigtest_node_info))

                    # !!! FIXME: Remove this section of code at some point
                    #            since BigTest VM resources are not used.

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
                    # !!! FIXME: Static and libvirt have become virtually
                    #            identical. They both rely on the env var
                    #            BIGROBOT_PARAMS_INPUT. Consider removing or
                    #            repurposing BIGROBOT_TESTBED in the future.

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

                # For Mininet, clean up logical name. Change 'mn' to 'mn1'.
                if 'mn' in params_dict:
                    params_dict['mn1'] = params_dict['mn']
                    del params_dict['mn']

                yaml_str = helpers.to_yaml(params_dict)

                # This file contain a list of nodes:
                #   c1: {ip: 10.192.5.221}
                #   c2: {ip: 10.192.5.222}
                #   mn1: {ip: 10.192.7.175}
                #   ...and so on...
                self._params_file = helpers.bigrobot_log_path_exec_instance() \
                                    + '/reference_params.topo'

                helpers.file_write_once(self._params_file, yaml_str)
                helpers.bigrobot_params(new_val=self._params_file)

            self._topology_params = self.load_params()
            if self._topology_params:
                self._has_a_topo_file = True

            if 'mn' in self._topology_params:
                helpers.debug("Changing node name 'mn' to 'mn1'")
                self._topology_params['mn1'] = self._topology_params['mn']
                del self._topology_params['mn']

            if helpers.bigrobot_topology() == None:
                helpers.environment_failure("Environment variable BIGROBOT_TOPOLOGY is not defined.")

            self.merge_params_attributes(helpers.bigrobot_params())
            if helpers.bigrobot_additional_params() is None:
                helpers.log("Skip merging additional params..")
            else:
                if helpers.file_exists(helpers.bigrobot_additional_params()):
                    self.merge_params_attributes(helpers.bigrobot_additional_params())

            # Load merge global parameters if file exists.
            if (helpers.bigrobot_additional_params() and
                helpers.file_exists(helpers.bigrobot_global_params())):
                self.merge_params_attributes(helpers.bigrobot_global_params())

            if 'global' not in self._topology_params:
                # Initialize the global space (equivalent to a node) if one
                # doesn't exist.
                self._topology_params['global'] = {}

            self.init_alias_lookup_table()
            self._topology = {}

        def merge_params_attributes(self, params_file):
            """
            Reading from params file and merge attributes with topo file
            """
            if params_file == None or params_file.lower() == 'none':
                return True

            if helpers.file_not_exists(params_file):
                helpers.environment_failure("Params file '%s' does not exist"
                                            % params_file)
            self._params = self.load_params(params_file=params_file)

            # We only merge in the attributes for a node if that node is
            # defined in the test suite topo file. But we need to give
            # specially treatment to 'global' which is not a node. Merge
            # all global attributes.
            if 'global' in self._params and 'global' not in self._topology_params:
                self._topology_params['global'] = self._params['global']

            for n in self._topology_params:
                # if n not in self._params:
                #    helpers.environment_failure("Node '%s' is not"
                #                                " specified in params file"
                #                                % n)
                if n not in self._params:
                    continue
                for key in self._params[n]:
                    if key not in self._topology_params[n]:
                        helpers.info("Node '%s' does not have attribute"
                                     " '%s' defined. Populating it from"
                                     " params file."
                                     % (n, key))
                    # elif key in self._topology_params[n] and self._topology_params[n][key].lower() != 'dummy':
                    #    helpers.trace("Node '%s' has attribute '%s' defined"
                    #                  " with value '%s'. Overriding it with"
                    #                  " value from params file."
                    #                  % (n, key, self._topology_params[n][key]))
                    helpers.info("Node '%s' attribute '%s' gets value '%s'"
                                 % (n, key, self._params[n][key]))
                    self._topology_params[n][key] = self._params[n][key]
            return True

        def load_params(self, params_file=None):
            if not params_file:
                params_file = helpers.bigrobot_topology()

            if re.match(r'.*\.topo$', params_file):
                _type = 'topology'
            else:
                _type = 'params'

            if helpers.file_not_exists(params_file):
                helpers.debug("%s file not specified (%s)"
                              % (_type.capitalize(), params_file))
                params = {}
            else:
                params = helpers.load_config(params_file)
                helpers.debug("Loaded %s file %s\n%s"
                              % (_type, params_file, helpers.prettify(params)))
            return params

        def init_alias_lookup_table(self):
            for node in self._topology_params:
                self._node_static_aliases[node] = node
                if 'alias' in self._topology_params[node]:
                    alias = self._topology_params[node]['alias']
                    self._node_static_aliases[alias] = node

                    # BSN QA convention is to name the aliases as:
                    #   global - for global parameters which may be used to
                    #            manipulate test conditions (user defined)
                    #   spine0, spine1, etc.
                    #   leaf1-a, leaf1-b, leaf2-a, leaf2-b, etc.
                    #   s021, etc.
                    #   arista-1 - for Arista switches
                    #   h1-rack1 - for hosts
                    #   h1-vm1-rack1 - for virtual hosts
                    #   ixia<n> - for IXIA traffic generator (tg<n> node)
                    r = r'^(global|leaf\d+-[ab]|spine\d+|s\d+|arista-\d+|h\d+(-vm\d+)?-rack\d+|ixia\d*)$'
                    if not re.match(r, alias):
                        helpers.warn("Supported aliases are leaf{n}-{a|b},"
                                     " spine{n}, s{nnn}, arista-{n},"
                                     " h{n}-rack{m}, h{n}-vm{m}-rack{o},"
                                     " ixia{n}")
                        helpers.environment_failure(
                                    "'%s' has alias '%s' which does not match"
                                    " the allowable alias names"
                                    % (node, alias))
            self._node_static_aliases['master'] = 'master'
            self._node_static_aliases['slave'] = 'slave'
            self._node_static_aliases['mn'] = 'mn1'
            self._node_static_aliases['mn1'] = 'mn1'
            helpers.log("Node aliases:\n%s"
                        % helpers.prettify(self._node_static_aliases))

    def __init__(self, reset_instance=False, esb=False, params=None):
        """
        In ESB environment, we want to overwrite the singletone object
        everytime we start a new worker task. This can be done by setting
        reset_instance=True.
        """
        if esb:
            reset_instance = True
            helpers.bigrobot_esb('True')
            helpers.bigrobot_topology_for_esb(params)
        if Test._instance is None or reset_instance:
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
                               (key, self._bsn_config['this_file']))

    def checkpoint(self, msg):
        self._checkpoint += 1
        helpers.log(":::: CHECKPOINT %04d - %s%s"
                    % (self._checkpoint, msg, br_utils.end_of_output_marker()),
                    level=3)

    def is_bcf_topology(self, new_state=None):
        if new_state != None:
            self._is_bcf_topology = new_state
        return self._is_bcf_topology

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

    def pdu_user(self):
        return self.bsn_config('pdu_user')

    def pdu_password(self):
        return self.bsn_config('pdu_password')

    def alias(self, name, ignore_error=False):
        """
        :param ignore_error: (Bool) If true, don't trigger exception when
                             name is not found.
        """
        name = name.lower()
        if not name in self._node_static_aliases:
            if ignore_error:
                return name
            helpers.environment_failure("Device alias '%s' is not defined"
                                        % name)
        return self._node_static_aliases[name]

    def settings(self, name=None, value=None):
        """
        Test settings is a way to store state info during test execution.
        The state info is essentially a bunch of global variables.
        """
        if value:
            self._settings[name] = value
        if name:
            return self._settings.get(name, None)
        return self._settings  # return entire settings dictionary

    def topology_params(self, node=None, key=None, new_val=None, default=None):
        """
        Usage:
        - t.params('c1')  # return attributes for c1
          t.params(node='c1', key='ip')
          t.params(node='tg1', key='type', default='ixia')
                            # if type is not defined, return 'ixia' for type
          t.params('global', 'my_image')
                            # BigRobot convention is to use 'global' to hold
                            # common key/values which are not node-specific.
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
        if node != None:
            node = self.alias(node)
            if node not in self._topology_params:
                helpers.environment_failure("Node '%s' is not defined in topology file"
                                            % node)
            if key != None and new_val != None:
                helpers.log("Updating param[%s][%s] to '%s'" %
                            (node, key, new_val))
                self._topology_params[node][key] = new_val
            if key != None:
                if key not in self._topology_params[node]:
                    if default:
                        self._topology_params[node][key] = default
                        return default
                    helpers.log("Node '%s' does not have attribute '%s' defined" % (node, key))
                    if key == "console_ip":
                        helpers.log("console_ip key is not defined check another sub level")
                        if "console" in self._topology_params[node]:
                            return self._topology_params[node]['console']['ip']
                    if key == "console_port":
                        helpers.log("console_port key is not defined check another sub level")
                        if "console" in self._topology_params[node]:
                            return self._topology_params[node]['console']['port']
                    helpers.environment_failure("Node '%s' does not have attribute '%s' defined"
                                       % (node, key))
                else:
                    return self._topology_params[node][key]
            else:
                return self._topology_params[node]
        elif key != None:
            helpers.environment_failure("Key '%s' is defined but not associated with a node"
                                        % key)
        return self._topology_params

    # Alias
    params = topology_params

    def params_global(self, key=None, new_val=None, default=None):
        """
        Getter/setter for global parameters.
        """
        return self.topology_params(node='global', key=key, new_val=new_val,
                                    default=default)

    def topology_params_nodes(self, **kwargs):
        """
        Returns the list of node params only. Ignore other params which are
        not nodes.
        """
        params = dict(self.topology_params(**kwargs))
        if 'global' in params:
            del params['global']
        return params

    # Alias
    params_nodes = topology_params_nodes

    def topology_params_authen(self, name):
        """
        Given a node name, check the params info to see whether the
        user/password is specified for the node.
        """
        authen = []
        params = self.topology_params_nodes()
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

        if name and node:
            name = self.alias(name, ignore_error=ignore_error)
            self._topology[name] = node
            return node
        elif name:
            name = self.alias(name, ignore_error=ignore_error)

            if name not in self._topology and name in self.params():
                # In certain condition (e.g., ESB environment), we don't
                # connect to the devices during Test initialization. But if
                # the device handle is requested then call node_connect() to
                # retrieve it.
                self.node_connect(name)

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
                                save_last_result=False, log_level='trace')
            content = result['content']
            if content['role'] == "MASTER":
                return True
            else:
                return False
        elif helpers.is_bvs(platform):
            result = n.rest.get("/api/v1/data/controller/cluster",
                                save_last_result=False, log_level='trace')
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
        return [self.controller(n) for n in self.topology_params_nodes() if re.match(r'^c\d+', n)]

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
        return [self.traffic_generator(n) for n in self.topology_params_nodes() if re.match(r'^tg\d+', n)]

    def traffic_generator(self, name='tg1', *args, **kwargs):
        name = self.alias(name)
        return self.topology(name, *args, **kwargs)

    def switches(self):
        """
        Get the handles of all the switches.
        """
        return [self.switch(n) for n in self.topology_params_nodes() if re.match(r'^s\d+', n)]

    def switch(self, name='s1', *args, **kwargs):
        name = self.alias(name)
        return self.topology(name, *args, **kwargs)

    def openstack_servers(self):
        """
        Get the handles of all the OpenStack servers.
        """
        return [self.openstack_server(n) for n in self.topology_params_nodes() if re.match(r'^os\d+', n)]

    def openstack_server(self, name='os1', *args, **kwargs):
        name = self.alias(name)
        return self.topology(name, *args, **kwargs)

    def hosts(self):
        """
        Get the handles of all the hosts.
        """
        return [self.host(n) for n in self.topology_params_nodes() if re.match(r'^h\d+', n)]

    def host(self, name='h1', *args, **kwargs):
        name = self.alias(name)
        return self.topology(name, *args, **kwargs)

    def node(self, *args, **kwargs):
        """
        Returns the handle for a node.
        """
        if len(args) >= 1:
            name = self.alias(args[0])
        elif 'name' in kwargs:
            name = self.alias(kwargs['name'])
        else:
            helpers.environment_failure("Impossible state.")
        name = self.alias(name)

        if name == 'mn':
            name = 'mn1'

        if re.match(r'^(master|slave)$', name):
            return self.controller(*args, **kwargs)
        else:
            return self.topology(*args, **kwargs)

    def node_spawn(self, ip, node=None, user=None, password=None,
                   device_type='controller', protocol='ssh', quiet=0):
        t = self
        if not node:
            node = 'node-%s-%s' % (ip, re.match(r'\w+-\w+-\w+-\w+-(\w+)',
                                                str(uuid.uuid4())).group(1))
        if helpers.not_quiet(quiet, [1]):
            helpers.log("Node spawn for '%s' (node name: '%s')"
                        % (ip, node))

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
        elif device_type == 'host':
            helpers.log("Initializing host '%s'" % node)
            if not user:
                user = self.host_user()
            if not password:
                password = self.host_password()
            n = a_node.HostNode(node, ip, user, password, t, protocol=protocol)
        elif device_type == 'pdu':
            helpers.log("Initializing host '%s'" % node)
            if not user:
                user = self.pdu_user()
            if not password:
                password = self.pdu_password()
            n = a_node.PduNode(node, ip, user, password, t, protocol=protocol)
        else:
            # !!! FIXME: Need to support other device types (see the list of
            #            devices in node_connect().
            helpers.environment_failure("You can only spawn nodes for device"
                                        " types: 'controller', 'switch', 'host'")
        return n

    def node_connect(self, node, user=None, password=None,
                     controller_ip=None, controller_ip2=None, quiet=0):
        # Matches the following device types:
        #  Controllers: c1, c2, controller, controller1, controller2, master, slave
        #  Mininet: mn, mn1, mn2
        #  Switches: s1, s2, spine1, leaf1, filter1, delivery1
        #  Hosts: h1, h2, h3
        #  OpenStack servers: os1, os2
        #  Traffic generators: tg1, tg2, ixia1
        #
        match = re.match(r'^(c\d|controller\d?|master|slave|mn\d?|mininet\d?|s\d+|spine\d+|leaf\d+|s\d+|h\d+|tg\d+|os\d+|ixia\d*)$', node)
        if not match:
            helpers.environment_failure("Unknown/unsupported device '%s'"
                                        % node)

        if helpers.not_quiet(quiet, [1]):
            helpers.log("Node connect for '%s' (user:%s, password:%s)"
                        % (node, user, password))

        host = None
        params = self.topology_params_nodes()
        if 'ip' in params[node]:
            host = params[node]['ip']

        t = self  # Test handle


        # Check for user name and password. Here is the order of preference:
        # 1) prefer user/password provided in method arguments
        # 2) else prefer user/password provided in topo file
        # 3) else prefer user/password provided in config/common.yaml

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
                                password=password, device_type='controller',
                                quiet=1)
            if helpers.is_bcf(n.platform()) and not self.is_bcf_topology():
                helpers.log("Node '%s' is a BCF controller. This is a BCF topology." % node)
                self.is_bcf_topology(True)
        elif helpers.is_switch(node):
            n = self.node_spawn(ip=host, node=node, user=user,
                                password=password, device_type='switch',
                                quiet=1)
        elif helpers.is_mininet(node):
            helpers.log("Initializing Mininet '%s'" % node)
            if not self._has_a_controller:
                helpers.environment_failure("Cannot bring up Mininet without"
                                            " a controller")

            # Use the OpenFlow port defined in the controller ('c1')
            # if it's defined.
            if 'openflow_port' in self.topology_params_nodes()['c1']:
                openflow_port = self.topology_params_nodes()['c1']['openflow_port']
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
            if 'platform' not in self.topology_params_nodes()[node]:
                helpers.environment_failure("Traffic generator '%s' does not"
                                            " have platform (e.g., platform:"
                                            " 'ixia', 'bigtap-ixia')"
                                            % node)
            platform = self.topology_params_nodes()[node]['platform']
            if platform.lower() in ['ixia', 'bigtap-ixia']:
                try:
                    # IXIA support is not available in some packages. So
                    # load it only if it is truly required.
                    import sys
                    import autobot.node_ixia as node_ixia
                except Exception, e:
                    helpers.log("Unexpect IXIA Error: \n %s" % str(e))
                    helpers.environment_failure("Unable to import node_ixia")
            if platform.lower() == 'ixia':
                n = node_ixia.IxiaNode(node, t)
            elif platform.lower() == 'bigtap-ixia':
                n = node_ixia.BigTapIxiaNode(node, t)
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

    def node_disconnect(self, node=None, delete_session_cookie=True):
        """
        Disconnect the node's SSH/Telnet sessions.
        If node name is not specified, disconnect all the nodes. If node name
        is specified (either as 'c1' or as a list ['c1', 'c2', 's1'], only
        disconnect those nodes.
        """
        node_handles = []
        if node:
            if helpers.is_list(node):
                for n in node:
                    node_handles.append(self.topology(n))
            else:
                node_handles.append(self.topology(node))
        else:
            for _, handle in self.topology().items():
                node_handles.append(handle)
        for h in node_handles:
            if helpers.is_controller(h.name()):
                h.close(delete_session_cookie=delete_session_cookie)
            else:
                h.close()
            del self._topology[h.name()]

    def node_reconnect(self, node, delete_session_cookie=True, **kwargs):
        helpers.log("Node reconnect for '%s'" % node)

        if helpers.is_controller(node):
            if node in ['master', 'slave']:
                try:
                    c = self.controller(node, resolve_mastership=True)
                    node_name = c.name()
                except:
                    # Resolve 'master' or 'slave' to actual name (e.g., 'c1', 'c2'). But
                    # don't do it using REST since we've probably lost the connection.
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

        if helpers.is_controller(node_name):
            self.node(node_name).close(delete_session_cookie=delete_session_cookie)
        else:
            self.node(node_name).close()

        c = self.node_connect(node_name, quiet=1, **kwargs)
        if helpers.is_controller(node_name):
            helpers.log("Create HTTP session cookie for '%s'" % node_name)
            self.setup_controller_http_session_cookie(node_name)
        return self.node(node)

    def dev_console(self, node, modeless=False, expect_console_banner=False):
        """
        Telnet to the console of a BSN controller or switch.

        To use this feature, you need to define the console for a node in the
        topo file. E.g.,

            s1:
              console:
                ip: cs-rack10
                port: 6010

        Then:
            t = test.Test()
            con = t.dev_console(node)
            con.bash("w")
            con.sudo("cat /etc/shadow")
            con.enable("show running-config")

        Assumption:
            After authentication, the device puts you directly in the CLI mode.

        How it works:
        - It attempts to exit out of whichever mode the console is currently
           in, then try to put the device into CLI mode, or die trying...
        - If modeless=True, just return the console handle as is and not
          atttempt to log in. The user can decide how to control the console
          session (i.e.,  the user is on his own).

        Returns a generic DevConf object since console is essentially an
        "Expect" session and not a full blown node object.

        Note: User needs to put the console back to CLI mode to avoid future
        console connections getting confused. At the end of the keyword, do:
            con.cli("")
        """
        t = self
        n = t.node(node)
        n_console = n.console(expect_console_banner=expect_console_banner)

        if modeless:
            return n_console

        prompt_login = r'.*login:.*$'
        prompt_password = r'[Pp]assword:.*'

        user = n.user()
        password = n.password()
        helpers.log("Console user:%s password:%s" % (user, password))

        # This regex should match prompts from BSN controllers and switches.
        # See vendors/exscript/src/Exscript/protocols/drivers/bsn_{switch,controller}.py
        prompt_device_cli = r'[\r\n\x07]+\s?(\w+(-?\w+)?\s?@?)?[\-\w+\.:/]+(?:\([^\)]+\))?(:~)?[>#$] ?$'

        helpers.log("Sending carriage return and checking for matching prompt/output")
        n_console.send('')

        def login():
            helpers.log("Found the login prompt. Sending user name ('%s')"
                        % user)
            n_console = n.console(expect_console_banner=expect_console_banner)
            n_console.send(user)
            if helpers.bigrobot_test_ztn().lower() == 'true':
                helpers.debug("Env BIGROBOT_TEST_ZTN is True. DO NOT EXPECT PASSWORD...")
            match = n_console.expect(prompt=[prompt_password,
                                             prompt_device_cli],
                                     timeout=60)
            if match[0] == 0:
                helpers.log("Found the password prompt. Sending password.")
                n_console.send(password)
                match = n_console.expect(prompt=[prompt_device_cli])

        # Match login or CLI prompt.
        match = n_console.expect(prompt=[prompt_login,
                                         prompt_device_cli,
                                         ],
                                 timeout=60)
        if match[0] == 0:
            login()  # Found login prompt. Attempt to authenticate.
        elif match[0] == 1:
            helpers.log("Found the BSN device prompt. Exiting system.")
            n_console.send('logout')
            match = n_console.expect(prompt=[prompt_login])
            login()

        # Assume that the device mode is CLI by default.
        n_console.mode('cli')
        n_console.cli('show version')
        return n_console

    def _pdu_mgt(self, node, action):
        """
        action:  "on" | "off" | "reboot"
        """
        if action == "on":
            action = "olOn"
        elif action == "off":
            action = "olOff"
        elif action == "reboot":
            action = "olReboot"
        else:
            helpers.test_error("Invalid PDU option '%s'" % action)
        t = self
        pdu = t.params(node, key='pdu')
        pdu_port = pdu['port']
        helpers.log("pdu: %s" % pdu)
        p = t.node_spawn(ip=pdu["ip"], user="apc", password="apc", device_type='pdu', protocol='telnet')
        p.cli('about')
        p.cli('olStatus %s' % pdu_port)
        reboot_cmd = '%s %s' % (action, str(pdu_port))
        p.cli(str(reboot_cmd).encode('ascii'))
        p.close()

    def power_cycle(self, node, minutes=0):
        self._pdu_mgt(node, 'reboot')
        helpers.log("Power cycled '%s'. Sleeping for %s minutes while it comes up."
                    % (node, minutes))
        helpers.sleep(int(minutes) * 60)

    def power_down(self, node, minutes=0):
        self._pdu_mgt(node, 'off')
        helpers.log("Powered down '%s'" % node)
        helpers.log("Powered down '%s'. Sleeping for %s minutes while it comes up."
                    % (node, minutes))
        helpers.sleep(int(minutes) * 60)

    def power_up(self, node, minutes=0):
        self._pdu_mgt(node, 'on')
        helpers.log("Powered up '%s'" % node)
        helpers.log("Powered up '%s'. Sleeping for %s minutes while it comes up."
                    % (node, minutes))
        helpers.sleep(int(minutes) * 60)

    def initialize(self):
        """
        Initializes the test topology. This should be called prior to test case
        execution (e.g., called by Test Suite or Test Case setup).
        """

        # This check ensures we  don't try to initialize multiple times.
        if self._init_completed:  # pylint: disable=E0203
            # helpers.log("Test object initialization skipped.")
            return

        self.checkpoint("Test object initialization begins.")
        if self._init_in_progress:  # pylint: disable=E0203
            return

        helpers.log("BigRobot environment variables:\n%s%s"
                    % (helpers.indent_str(helpers.bigrobot_env_variables()),
                       br_utils.end_of_output_marker()))

        if not helpers.is_esb():
            helpers.log("BigRobot dependencies:\n%s%s"
                        % (helpers.bigrobot_module_dependencies(),
                           br_utils.end_of_output_marker()))
            helpers.log("BigRobot repository (Git):\n%s%s"
                        % (helpers.run_cmd2("/usr/bin/git branch -lvv",
                                            shell=True,
                                            quiet=True)[1],
                           br_utils.end_of_output_marker()))
            helpers.log("Staging system uname:\n%s%s"
                        % (helpers.uname(),
                           br_utils.end_of_output_marker()))
            helpers.log("Staging system uptime:\n%s%s"
                        % (helpers.uptime(),
                           br_utils.end_of_output_marker()))
            helpers.log("Staging system ulimit:\n%s%s"
                        % (helpers.ulimit(),
                           br_utils.end_of_output_marker()))
            helpers.log("Staging User ID:\n%s%s"
                        % (helpers.user_id(),
                           br_utils.end_of_output_marker()))
    
            jenkins_env = [x for x in ['BUILD_NAME', 'BUILD_URL'] if os.environ.get(x, None)]
            for i in range(0, len(jenkins_env)):
                if i == 0:
                    helpers.log("Jenkins environment:")
                if i + 1 == len(jenkins_env):
                    helpers.log("\t%s: %s%s" % (jenkins_env[i], os.environ[jenkins_env[i]], br_utils.end_of_output_marker()))
                else:
                    helpers.log("\t%s: %s" % (jenkins_env[i], os.environ[jenkins_env[i]]))

        self._init_in_progress = True  # pylint: disable=W0201

        params = self.topology_params_nodes()

        if 'c1' not in params:
            helpers.warn("A controller (c1) is not defined")
            controller_ip = None
        else:
            controller_ip = params['c1']['ip']  # Mininet needs this bit of info
            self._has_a_controller = True  # pylint: disable=W0201
            # helpers.log("Controller IP address is %s" % controller_ip)

        if 'c2' not in params:
            helpers.debug("A controller (c2) is not defined")
            controller_ip2 = None
            self._has_a_single_controller = True  # pylint: disable=W0201
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

        if helpers.is_esb():
            helpers.summary_log("ESB environment - don't ping/connect to"
                                " nodes during Test initialization")
        else:
            for key in list_of_nodes:
                self.node_connect(key,
                                  controller_ip=controller_ip,
                                  controller_ip2=controller_ip2)

        self._init_completed = True  # pylint: disable=W0201
        helpers.debug("Test object initialization ends.%s"
                      % br_utils.end_of_output_marker())

        helpers.debug("Final topology_params: %s" % self.topology_params())

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
        if n.devconf():
            n.cli('show version')

    def controller_cli_show_running_config(self, name):
        n = self.topology(name)
        if n.devconf():
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

    def _sudo_with_error_code(self, name, cmd):
        n = self.topology(name)
        cmd_output = n.sudo(cmd)['content']
        content = n.bash('echo $?')['content']
        error_code = helpers.strip_cli_output(content, to_list=True)[0]
        return (cmd_output, int(error_code))

    def _file_exists(self, name, filename):
        (_, error_code) = self._sudo_with_error_code(name, 'ls -la %s' % filename)
        return error_code

    def _setup_controller_idle_timeout(self, name):
        self.checkpoint("Checking idle timeout on '%s'" % name)
        n = self.topology(name)
        source_file = "/usr/share/floodlight/cli-package/com.bigswitch.floodlight/floodlight-bcf/desc/version200/application.py"

        if self._file_exists(name, source_file) != 0:
            helpers.environment_failure("'%s' - Source file does not exist: %s"
                                        % (name, source_file))
        (_, error_code) = self._sudo_with_error_code(name,
                                'grep -E "(BigRobot|QA) mod" %s' % source_file)
        if error_code == 0:
            helpers.log("'%s' - QA idle timeout modifications have already been applied."
                        % name)
            return False

        (_, error_code) = self._sudo_with_error_code(
                            name,
                            'grep -E "^command.cli.interactive_read_timeout" %s'
                            % source_file)
        if error_code != 0:
            helpers.environment_failure("Cannot find interactive_read_timeout in %s on '%s'."
                                        % (source_file, name))

        helpers.log("'%s' - Modifying source file: %s" % (name, source_file))
        n.sudo('sed -i.orig "s/^command.cli.interactive_read_timeout.*/command.cli.interactive_read_timeout( 1000 \* 60 ) \# 1000 minutes (QA mod)/" %s'
               % source_file)

        (_, error_code) = self._sudo_with_error_code(
                            name,
                            'grep -E "command.cli.interactive_read_timeout.*(BigRobot|QA) mod" %s'
                            % source_file)
        if error_code != 0:
            helpers.environment_failure("Not able to modify idle time in %s on '%s'."
                                        % (source_file, name))

        n.sudo('grep -E "^command.cli.interactive_read_timeout" %s'
               % source_file)
        return True

    def _setup_controller_reauth_timeout(self, name):
        if helpers.bigrobot_reconfig_reauth().lower() == "false":
            helpers.log("Env BIGROBOT_RECONFIG_REAUTH is False. Bypass reauth reconfig.")
            return False

        self.checkpoint("Checking reauth timeout on '%s'" % name)
        n = self.topology(name)
        source_file = "/etc/default/floodlight"

        if self._file_exists(name, source_file) != 0:
            helpers.environment_failure("'%s' - Source file does not exist: %s"
                                        % (name, source_file))
        (_, error_code) = self._sudo_with_error_code(name,
                                'grep -E "(BigRobot|QA) mod" %s' % source_file)
        if error_code == 0:
            helpers.log("'%s' - QA reauth timeout modifications have already been applied."
                        % name)
            return False

        (_, error_code) = self._sudo_with_error_code(
                            name,
                            'grep -E "^JVM_OPTS.*org.projectfloodlight.db.auth.sessionCacheSpec=" %s'
                            % source_file)
        if error_code == 0:
            helpers.environment_failure("Found sessionCacheSpec in %s on '%s'. Possibly a change was recently made to Floodlight source which conflicts with QA mod."
                                        % (source_file, name))

        helpers.log("'%s' - Modifying source file: %s" % (name, source_file))
        n.sudo('echo \'JVM_OPTS="$JVM_OPTS -Dorg.projectfloodlight.db.auth.sessionCacheSpec=maximumSize=1000000,expireAfterAccess=100d"  # 100 days (QA mod)\' | sudo tee -a %s'
               % source_file)

        (_, error_code) = self._sudo_with_error_code(
                            name,
                            'grep -E "^JVM_OPTS.*org.projectfloodlight.db.auth.sessionCacheSpec=" %s'
                            % source_file)
        if error_code != 0:
            helpers.environment_failure("Not able to modify reauth time in %s on '%s'."
                                        % (source_file, name))

        self.checkpoint("Restarting floodlight to put new reauth timeout into effect.")
        n.sudo("initctl stop floodlight")
        helpers.sleep(0.5)
        n.sudo("initctl start floodlight")
        sleep_time = helpers.bigrobot_reconfig_reauth_sleep_timer()
        helpers.log("Sleeping for %s seconds while floodlight settles." % sleep_time)
        helpers.sleep(sleep_time)
        return True

    def cli_add_controller_idle_and_reauth_timeout(self, name,
                                                   reconfig_idle=True,
                                                   reconfig_reauth=True):
        """
        When logging into the BCF controller for the first time, modify the
        idle timeout setting in Floodlight's application.py. Then reconnect
        so changes can take effect.
        """
        n = self.topology(name)
        if not n.devconf():
            return False

        platform = n.platform()
        if not helpers.is_bcf(platform):
            return True

        status1 = status2 = False

        if reconfig_idle:
            status1 = self._setup_controller_idle_timeout(name)
        else:
            helpers.log("reconfig_idle=%s" % reconfig_idle)
        if reconfig_reauth:
            status2 = self._setup_controller_reauth_timeout(name)
        else:
            helpers.log("reconfig_reauth=%s" % reconfig_reauth)

        if status1 or status2:
            # Reconnect to device if updates were made to idle/reauth
            # properties.

            helpers.log("Reconnecting nodes")
            self.node_reconnect(name)
        return True

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

        helpers.log("Setting up controllers - before clean-config")

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

        helpers.log("Setting up controllers - after clean-config")
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
            helpers.log("Setting up switches (SwitchLight) - before clean-config")
            self.teardown_switch(name)

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
            helpers.log("Setting up switches (SwitchLight) - after clean-config")
            for controller in ('c1', 'c2'):
                c = self.topology(controller, ignore_error=True)
                if c:
                    if 'openflow_port' in self.topology_params_nodes()[controller]:
                        openflow_port = self.topology_params_nodes()[controller]['openflow_port']
                        n.config("controller %s port %s"
                                 % (c.ip(), openflow_port))
                    else:
                        n.config("controller %s" % c.ip())
            n.config("copy running-config startup-config")

    def setup_ztn_phase1(self, name):
        '''
            Configure switch's on Controller for ZTN bring up of switch's and send reboot to all switchs
        '''
        # n = self.topology(name)
        if not helpers.is_switch(name):
            return True
        if re.match(r'.*spine.*', self.params(name, 'alias')):
            fabric_role = 'spine'
        elif re.match(r'.*leaf.*', self.params(name, 'alias')):
            fabric_role = 'leaf'
            leaf_group = self.params(name, 'leaf-group')
        else:
            helpers.log("Not Leaf / Spine Ignore ZTN SETUP")
            return True
        c1_ip = self.params('c1', 'ip')
        c2_ip = self.params('c2', 'ip')
        helpers.log("First Adding Switch in master controller for ZTN Bootup...")
        master = self.controller("master")
        console = self.params(name, 'console')
        cmds = ['switch %s' % self.params(name, 'alias'), 'fabric-role %s' % fabric_role, \
                'mac %s' % self.params(name, 'mac')]
        helpers.log("Executing cmds ..%s" % str(cmds))
        for cmd in cmds:
            helpers.log('Executin cmd: %s' % cmd)
            master.config(cmd)
        if fabric_role == 'leaf':
            helpers.log("Adding leaf group for leaf %s" % name)
            master.config('leaf-group %s' % leaf_group)
        helpers.log("Success adding switch in controller..%s" % str(name))
        helpers.log("Waiting 30 secs for the switche to get connected to Controller..")
        helpers.sleep(155)
        if helpers.bigrobot_ztn_reload().lower() != "true" and helpers.bigrobot_ztn_installer().lower() == "false":
            helpers.log("BIGROBOT_ZTN_RELOAD is False Skipp rebooting switches from Consoles..")
            return True
        if not ('ip' in console and 'port' in console):
            return True
        helpers.log("ZTN setup - found switch '%s' console info" % name)
#         if re.match(r'.*spine.*', self.params(name, 'alias')):
#             helpers.log("Initializing spine with modeless state due to JIRA PAN-845")
#             con = self.dev_console(name, modeless=True)
#             con.send('admin')
#             helpers.sleep(2)
#             con.send('adminadmin')
#             helpers.sleep(2)
#             con.send('enable;conf;no snmp-server enable')
#             con = self.dev_console(name)
#         else:
        helpers.log("Initializaing switches normally..")
        con = self.dev_console(name)
        helpers.log("Reload the switch for ZTN..")
        con.bash("")
        con.send('reboot')
        con.send('')
        if not helpers.is_switchlight(con.platform()):
            helpers.log("ZTN setup - switch '%s' is not SwitchLight. No action..." % name)
            return True
        if helpers.bigrobot_ztn_installer().lower() != "true":
            helpers.log("Finish sending Reboot on switch : %s" % name)
            return
        try:
            con.expect("Hit any key to stop autoboot")
        except:
            return helpers.test_failure("Unable to stop at u-boot shell")
        con.send("")
        con.expect([r'\=\>'], timeout=30)
        con.send("setenv onie_boot_reason install")
        con.expect([r'\=\>'], timeout=30)
        con.send("run onie_bootcmd")
        con.expect("Loading Open Network Install Environment")
        helpers.log("Finish sending Reboot on switch : %s with installer option" % name)
        return True

    def setup_ztn_phase2(self, name):
        '''
            Reload the switch's and update IP's from switchs and reconnect switchs using ssh.
        '''
#         helpers.log(" NO MORE Re-connecting Switches with Console to get IP with recent ZTN work flows")
#         return True
        if not helpers.is_switch(name):
            return True
        if re.match(r'.*spine.*', self.params(name, 'alias')):
            helpers.log("will perform setup_ztn_phase2, updating IP's for consoles for Spines..")
        elif re.match(r'.*leaf.*', self.params(name, 'alias')):
            helpers.log("will perform setup_ztn_phase2, updating IP's for consoles for Leaf..")
        else:
            helpers.log("Not Leaf / Spine Ignore ZTN SETUP PHASE 2")
            return True
        console = self.params(name, 'console')
        if not ('ip' in console and 'port' in console):
            return True
        helpers.log("ZTN setup - found switch '%s' console info" % name)
        helpers.log("Re-Login in console of switch after reboot...")
        helpers.log("Initializaing leafs and Spines normally..")
        con = self.dev_console(name)

        if helpers.bigrobot_no_auto_reload().lower() == 'true':
            helpers.log("Disabling switch config auto-reloads...")
            con.bash('touch /mnt/flash/local.d/no-auto-reload')
        else:
            helpers.log("Skipping to disable auto-reloads , which disallows switch SSH Handles")

        helpers.log("ZTN setup - found SwitchLight '%s'. Creating admin account and starting SSH service." % name)
        con.config("username admin secret adminadmin")
        con.config("ssh enable")
        content = con.bash("ifconfig ma1")["content"]
        match = helpers.any_match(content,
                                  r'inet addr:(\d+\.\d+\.\d+\.\d+).*')
        if match and len(match) == 1:
            mgt_ip = match[0]
            helpers.log("ZTN setup - SwitchLight '%s' management IP is %s. Updating topology params." % (name, mgt_ip))
            self.params(name, 'ip', new_val=mgt_ip)
        else:
            helpers.warn("ZTN setup - SwitchLight '%s' does not have a management IP" % name)
        con.cli("")
        self.node_reconnect(name)
        helpers.log("Closing dev_console session for switch : %s" % name)
        con.close()
        # Need to add switch connect verification.. Added in Setup so we can ignore verifying the switch connections here.
        return True


    def setup(self):
        # This check ensures we  don't try to setup multiple times.
        if self._setup_completed:  # pylint: disable=E0203
            # helpers.log("Test object setup skipped.")
            return

        if self._setup_in_progress:  # pylint: disable=E0203
            return

        self.checkpoint("Test object setup begins.")
        self._setup_in_progress = True  # pylint: disable=W0201

        params = self.topology_params_nodes()
        helpers.debug("Topology info:\n%s" % helpers.prettify(params))
        master = self.controller("master")
        standby = self.controller("slave")

        # CAUTION: The following section may not execute properly if the device
        # is connected via console, or if the device is in firstboot state. So
        # be sure to check if devconf handle exists before running any kind of
        # REST/CLI command.

        if not helpers.is_esb():
            for key in params:
                if helpers.is_controller(key):
                    self.controller_cli_show_version(key)

        for key in params:
            if helpers.is_controller(key):
                self.cli_add_controller_idle_and_reauth_timeout(key)

#         if helpers.bigrobot_no_auto_reload().lower() == 'true':
#             helpers.log("Reconnecting switch consoles and updating switch IP's....")
#             helpers.log("Please make sure switches are not in ZTN MODE ..before using BIGROBOT_NO_AUTO_RELOAD env")
#             for key in params:
#                 self.setup_ztn_phase2(key)
#         else:
#             helpers.log("Skipping Switch ssh handle updates, Cannot execute ssh commands")
        # Don't run the following section if test setup is disabled.
        if helpers.bigrobot_test_setup().lower() != 'false':
            for key in params:
                if helpers.is_controller(key):
                    self.setup_controller_pre_clean_config(key)
                elif helpers.is_switch(key):
                    if helpers.bigrobot_test_ztn().lower() == 'true':
                        helpers.log("Skipping switch CLEAN configs in ZTN MODE")
                    else:
                        self.setup_switch_pre_clean_config(key)
            for key in params:
                self.clean_config(key)
            for key in params:
                if helpers.is_controller(key):
                    self.setup_controller_post_clean_config(key)
                elif helpers.is_switch(key):
                    if helpers.bigrobot_test_ztn().lower() == 'true':
                        helpers.log("Skipping switch CLEAN configs in ZTN MODE")
                    else:
                        self.setup_switch_post_clean_config(key)
            if helpers.bigrobot_test_ztn().lower() == 'true':
                helpers.debug("Env BIGROBOT_TEST_ZTN is True. Setting up ZTN.")
                master = self.controller("master")
                standby = self.controller("slave")
                for key in params:
                    self.setup_ztn_phase1(key)
                if helpers.bigrobot_ztn_installer().lower() != "true":
                    helpers.log("Sleeping 2 mins..")
                    helpers.sleep(120)
                else:
                    helpers.log("Loader install on Switch is trigerred need to wait for more time for switches to come up:")
                    helpers.sleep(400)
                url1 = '/api/v1/data/controller/applications/bcf/info/fabric/switch' % ()
                master.rest.get(url1)
                data = master.rest.content()
                for i in range (0, len(data)):
                    helpers.log("Checking switch Connections state from controller...state: %s" % data[i]["fabric-connection-state"])
                    if (data[i]["fabric-connection-state"] == "suspended") or (data[i]["fabric-connection-state"] == "not_connected"):
                        helpers.test_failure("Fabric manager status is incorrect")
                        helpers.exit_robot_immediately("Switches didn't come please check Controllers...")
                helpers.log("Fabric manager status is correct")
                if helpers.bigrobot_no_auto_reload().lower() == 'true':
                    helpers.log("Reconnecting switch consoles and updating switch IP's....")
                    for key in params:
                        self.setup_ztn_phase2(key)
                helpers.debug("Updated topology info:\n%s"
                              % helpers.prettify(params))
                master.config("show switch")
                master.config("show running-config")
                master.config("show logging level")
                master.config("enable; config; copy running-config snapshot://ztn-base-config")
                helpers.log("########  Stand_by config after ZTN setup: ")
                standby.config("show switch")
                standby.config("show running-config")
                standby.config("enable; config; copy running-config snapshot://ztn-base-config")
        else:
            helpers.debug("Env BIGROBOT_TEST_SETUP is False. Skipping device setup.")
            if helpers.bigrobot_test_ztn().lower() == 'true':
                helpers.log("Env BIGROBOT_TEST_ZTN is True. Loading ZTN-based config as BIGROBOT_TEST SETUP is False, make sure switches are brought up with ZTN on these controllers!")
                master = self.controller("master")
                master.enable("show switch")
#                 master.enable("copy snapshot://ztn-base-config running-config ")
                master.config("show logging level")
                master.enable("show running-config")
                master.enable("show switch")
                helpers.log("Trying to log into switch consoles to update ZTN IP's on topo files")
                for key in params:
                    self.setup_ztn_phase2(key)
                helpers.debug("Updated topology info:\n%s"
                              % helpers.prettify(params))
                master = self.controller("master")
                master.enable("show switch")

        if helpers.bigrobot_ha_logging().lower() == "true":
            helpers.log("Env BIGROBOT_HA_LOGGING is True. Enabling HA Debug logging for Dev to debug HA failures....")
            master.config("logging level org.projectfloodlight.ha debug")
            master.config("logging level org.projectfloodlight.sync.internal.transaction debug")
            master.config("logging level org.projectfloodlight.db.data.PackedFileStateRepository debug")
            master.config("logging level org.projectfloodlight.db.data.SyncServiceStateRepository debug")
            master.config("show logging level")
        self._setup_completed = True  # pylint: disable=W0201
        self.checkpoint("Test object setup ends.")

    def teardown_switch(self, name):
        """
        Perform teardown on SwitchLight
        - delete the controller IP address
        """
        n = self.topology(name)
        if helpers.bigrobot_no_auto_reload().lower() == 'true' and helpers.bigrobot_test_ztn().lower() == 'true':
            con = self.dev_console(name)
            helpers.log("Removing switch config auto-reloads files at the End of Each script Execution...")
            con.bash('rm -rf /mnt/flash/local.d/no-auto-reload')
            con.cli("")

        if helpers.bigrobot_test_ztn().lower() == 'true':
            helpers.log("Skipping switch TEAR_DOWN in ZTN MODE")
            return

        if self.is_bcf_topology():
            helpers.log("Skipping switch TEAR_DOWN for BCF topology")
            return

        if not n.devconf():
            helpers.log("DevConf session is not available for node '%s'"
                        % name)
            return

        if helpers.is_switchlight(n.platform()):
            helpers.log("Tearing down config for SwitchLight")
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

    def teardown(self):
        self.checkpoint("Test object teardown begins.")
        params = self.topology_params_nodes()

        if helpers.bigrobot_test_teardown().lower() != 'false':
            for key in params:
                if helpers.is_controller(key):
                    pass
                elif helpers.is_switch(key):
                    self.teardown_switch(key)
        else:
            helpers.debug("Env BIGROBOT_TEST_TEARDOWN is False. Skipping device teardown.")

        helpers.debug("Test object teardown ends.%s"
                      % br_utils.end_of_output_marker())

    def clean_config(self, name):
        n = self.node(name)
        if helpers.bigrobot_test_clean_config().lower() == 'false':
            helpers.log("Env BIGROBOT_TEST_CLEAN_CONFIG is False - bypassing"
                        " clean-config")
            return True

        self.checkpoint("Running clean-config on devices in topology")
        if (helpers.is_controller(name) and helpers.is_t5(n.platform())
            and self.is_master_controller(name)):

            helpers.log("Running clean-config on T5 controller '%s'"
                        " (establishing baseline config setup)" % name)
            self.t5_clean_configuration(name)
        return True

    def t5_clean_configuration(self, name):
        '''
            Objective: Delete all user configuration
        '''
        t = self
        c = t.controller(name)

        helpers.log("Attempting to delete all tenants")
#         if helpers.bigrobot_test_ztn().lower() == 'true':
#             helpers.log("ZTN knob is True just loding the ztn-base-config")
#             helpers.log("Loading ztn-base-config ...")
#             c.config("copy snapshot://ztn-base-config running-config")
#         else:
        helpers.log("Loading firstboot-config ...")
        c.config("copy snapshot://firstboot-config running-config")
        c.config("show running-config")

        return True
