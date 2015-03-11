import autobot.helpers as helpers
from autobot.node import Node
import modules.IxLib as IxLib
import modules.IxBigtapLib as IxBigtapLib



class IxiaNode(Node):
    def __init__(self, name, t):
        self._chassis_ip = t.params(name, 'chassis_ip')
        self._tcl_server_ip = t.params(name, 'tcl_server_ip')
        self._tcl_server_port = t.params(name, 'tcl_server_port', 8009)
        self._ix_version = t.params(name, 'ix_version', '7.10')
        self._ports = t.params(name, 'ports')

        super(IxiaNode, self).__init__(name=name, ip=self._chassis_ip, t=t)
        self.ixia_init()

    def ixia_init(self):
        helpers.log("tcl_server_ip: %s" % self.tcl_server_ip())
        helpers.log("chassis_ip: %s" % self.chassis_ip())
        helpers.log("ports: %s" % self.ports())

        helpers.log("Platform: %s" % self.platform())
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

    def console(self, driver=None):
        helpers.environment_failure("Console is currently not supported for Ixia node.")

    def close(self): pass
        # There's no SSH/Telnet session for Ixia node, so no need to call
        # close() in base class (Node).


class BigTapIxiaNode(IxiaNode):
    def __init__(self, name, t):
        self._bigtap_controller_ip = t.params(name, 'bigtap_controller')['ip']
        self._bigtap_switches = t.params(name, 'switches')
        self._bigtap_ports = t.params(name, 'bigtap_ports')
        self._bigtap_to_config = t.params(name, 'bigtap_controller')['set_bigtap_config']
        self._switch_dpids = {'s1': '00:00:5c:16:c7:19:e7:4e'}  # FIXME: will be changing to getdynamically
        self._switch_handles = {}
        super(BigTapIxiaNode, self).__init__(name, t)
        self.bigtap_init(t)

    def bigtap_init(self, t):
        helpers.log("Bigtap_ip: %s" % self._bigtap_controller_ip)
        helpers.log("Bigtap_switches: %s" % self._bigtap_switches)
        helpers.log("Bigtap_Ports: %s" % self._bigtap_ports)
        helpers.log("Bigtap IXIA Ports: %s" % self._ports)

        self._bigtap_node = t.node_spawn(self._bigtap_controller_ip,
                                         user='admin', password='adminadmin')
        # string = 'show version'
        bigtap = self._bigtap_node
        # bigtap.cli(string)
        # content = bigtap.cli_content()
        # helpers.log('Printing BIGTAP VERSION:')
        # helpers.log(content)
        # string = 'show running-config'
        # bigtap.cli(string)
        # content = bigtap.cli_content()
        # helpers.log('BIGTAP RUNNING CONFIG Before pushing Statics Policies')
        # helpers.log(content)
        for switch in self._bigtap_switches.iteritems():
            self._switch_handles[switch[0]] = t.node_spawn(switch[1]['ip'],
                                                           user='admin',
                                                           password='adminadmin',
                                                           device_type='switch')
            string = 'show version'
            self._switch_handles[switch[0]].cli(string)
            helpers.log('Displaying Switch : %s version ' % switch[0])
            helpers.log(self._switch_handles[switch[0]].cli_content())

        for port in self._bigtap_ports.values():
            final_macs = IxBigtapLib.create_mac_list(port['name'], 5)
            ixia_macs = IxBigtapLib.create_mac_list(port['name'], 5, False)
            for mac in final_macs:
                helpers.log('Mac : %s' % mac)
            temp_list = port['name'].split('/')
            bigtap_switch_id = temp_list[0]  # to be used for calculating switch DPID
            bigtap_port_id = temp_list[1]

            switch = 's' + str(bigtap_switch_id)
            bigtap_config_rx = IxBigtapLib.create_bigtap_flow_conf_rx(self._bigtap_switches[switch]['dpid'],
                                                                52, ['1', '2'])  # FIXME to be changed for passing ix port from Topo file
            bigtap_config_tx = IxBigtapLib.create_bigtap_flow_conf_tx(self._bigtap_switches[switch]['dpid'],
                                                                bigtap_portname=bigtap_port_id,
                                                               ix_portname=['1', '2'], macs=final_macs)

            if not self._bigtap_to_config:
                helpers.log('Skipping Big tap Config...')
            else:
                helpers.log('Configuring Switches with bigtap Controller IP')
                # FIXE ME need to add configuring switches with bigtap controller and enabling bi-directional flows in Bigtap
                helpers.log('Configuring BigTap')
                for conf in bigtap_config_rx:
                    print 'Executing cmd: ', conf
                    bigtap.cli(conf)
                for conf in bigtap_config_tx:
                    print 'Executing cmd: ', conf
                    bigtap.cli(conf)
            print ixia_macs

    def platform(self):
        return 'bigtap-ixia'
