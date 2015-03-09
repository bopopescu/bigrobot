#!/usr/bin/env python
'''
    This module is used to maintain Ixia Related Libraries for traffic generation
'''
import autobot.helpers as helpers
import time, re
import sys
from vendors.Ixia import IxNetwork
import modules.IxBigtapLib as IxBigtapLib

class Ixia(object):
    def __init__(self, tcl_server_ip, tcl_server_port=8009, ix_version='7.10', chassis_ip=None,
                 port_map_list=None, clear_ownership=True):
        self._tcl_server_ip = tcl_server_ip
        self._tcl_server_port = tcl_server_port
        self._ix_version = ix_version
        self._chassis_ip = chassis_ip
        self._handle = None
        self._port_map_list = None
        self._vports = []
        self._port_map_list = self.port_map_list(port_map_list)
        self._traffic_stream = {}
        self._topology = {}
        self._traffi_apply = False
        self._frame_size = 68
        self._is_device_created = False
        self._started_hosts = False
        self._ip_devices = {}
        self._arp_check = True
        self._raw_stream = None
        self._raw_stream_id = 1
        # Connect to IXIA Chassis and IXIA TCL Server
        self._handle = self.ix_connect()
        if clear_ownership:
            for key, port in self._port_map_list.iteritems():
                root = self._handle.getRoot()
                hardware = self._handle.getList(root, 'availableHardware')
                chassis = self._handle.getList(hardware[0], 'chassis')
                helpers.log ('Initializing Chassis: %s' % str(chassis))
                helpers.log ('Initializing Port: %s' % str(port))
                ix_card_list = self._handle.getList(chassis[0], 'card')
                helpers.log('ix_card_list available on chassis: %s' % str(ix_card_list))
                ix_card = ''
                for card in ix_card_list:
                    temp_breaks = card.split(':')
                    if temp_breaks[-1] == port[1]:
                        print 'success!!'
                        ix_card = card
                        break
                helpers.log('CARD FOUND: %s' % str(ix_card))
                if ix_card == '':
                    raise IxNetwork.IxNetError('IX_CARD NOT FOUND in chassis!!!!')
                helpers.log('ix_card_port_list: %s' % str(self._handle.getList(ix_card, 'port')))
                ix_port = self._handle.getList(ix_card, 'port')[int(port[2]) - 1]
                self._handle.execute('clearOwnership', ix_port)
                helpers.log('Success CLearing OwnerShip of Port %s !!' % key)

    def port_map_list(self, ports):
        # something happens here
        # self._port_map_list = <something>
        port_map_list = {}
        for port in ports.iteritems():
            match = re.match(r'(\d+)/(\d+)', port[1]['name'].lower())
            port_map_list[port[0].lower()] = (self._chassis_ip, match.group(1), match.group(2))
        return port_map_list

    def ix_connect(self):
        handle = IxNetwork.IxNet()
        # Connect to TCL Server
        handle.connect(self._tcl_server_ip, '-port', self._tcl_server_port,
                        '-version', self._ix_version)
        # ## clear the configuration
        asyncHandle = handle.setAsync().execute('newConfig')
        handle.wait(asyncHandle)
        # Connect to IXIA Chassis
        chassis = handle.add(handle.getRoot() + 'availableHardware', 'chassis', '-hostname', self._chassis_ip)
        handle.commit()
        chassis = handle.remapIds(chassis)[0]
        return handle

    def ix_create_vports(self):
        '''
            Returns created vports with the vports names provided
        '''
        created_vports = []
        vport_names = [vport for vport in self._port_map_list.keys()]
        helpers.log("### creating vports with names : %s " % str(vport_names))
        for vport_name in vport_names:
            created_vports.append(self._handle.add(self._handle.getRoot(), 'vport', '-name', vport_name))
        # Running remapIds As per
        # IXIA config pushing to Ixia chassis
        for vport in created_vports:
            self._vports.append(self._handle.remapIds(vport)[0])
        self._handle.commit()
        helpers.log("### Done creating vPorts")
        return self._vports

    def ix_map_vports_pyhsical_ports(self):
        '''
            Returns True or False after adding vports to given Physical IXIA ports
        '''
        root = self._handle.getRoot()
        hardware = self._handle.getList(root, 'availableHardware')
        chassis = self._handle.getList(hardware[0], 'chassis')[0]

        for (ixport, vport) in zip(self._port_map_list.values(), self._vports):
            card = str(ixport[1])
            port = str(ixport[2])
            self._handle.setAttribute(vport, '-connectedTo', chassis + '/card:' + card + '/port:' + port)
        self._handle.commit()
        for vport in self._vports:
            no_of_tries = 0
            while self._handle.getAttribute(vport, '-state') != 'up' and no_of_tries != 10:
                time.sleep(2)
                no_of_tries = no_of_tries + 1
                helpers.log("Vports didn't come up, will wait 2 secs and check again %s times" % str(10 - no_of_tries))
            if no_of_tries == 10:
                helpers.log("IXIA ports are all not UP , may see traffic issues on ports that are down")
                helpers.log("vport that is down: %s" % str(self._vports))
        return True

    def ix_create_topo(self):
        '''
            RETURNS IXIA topology list object adding a topo for each vport in vports
        '''
        helpers.log("### Adding %s topologies" % len(self._vports))
        topology = {}
        for vport in self._vports:
            vport_name = self._handle.getAttribute(vport, '-name')
            topo = self._handle.add(self._handle.getRoot(), 'topology', '-vports', vport, '-name', vport_name)
            self._handle.commit()
            topology[vport_name] = self._handle.remapIds(topo)[0]

        # topology = self._handle.getList(self._handle.getRoot(), 'topology')
        helpers.log("### Done adding %s topologies" % len(self._vports))
        self._topology = topology

    def ix_create_device_ethernet(self, topology, s_cnt, d_cnt, s_mac, d_mac, s_step, d_step):
        '''
            RETURN IXIA MAC DEVICES mapped with Topologies created with vports and added increment values accordingly
            Ex Usage:
            IxLib.IxCreateDeviceEthernet(ixNet,topology, mac_mults =  mac_mults, macs = macs, mac_steps = mac_steps)
        '''
        helpers.log("### Adding %s device groups" % len(topology))
        mac_mults = [d_cnt, s_cnt]
        mac_steps = [d_step, s_step]
        macs = [d_mac, s_mac]
        for topo in topology:
            self._handle.add(topo, 'deviceGroup')
        self._handle.commit()
        topo_devices = []
        eth_devices = []
        for topo in topology:
            dev_grp = self._handle.getList(topo, 'deviceGroup')
            topo_device = self._handle.remapIds(dev_grp)[0]
            topo_devices.append(topo_device)
        for (topo_device, multi, topo) in zip(topo_devices, mac_mults, topology):
            helpers.log('### topo device : %s' % str(topo_device))
            topo_name = self._handle.getAttribute(topo, '-name')
            self._handle.setAttribute(topo_device, '-multiplier', multi)
            eth_devices.append(self._handle.add(topo_device, 'ethernet', '-name', topo_name))
        self._handle.commit()
        mac_devices = []  # as this are added to ixia need to remap as per ixia API's
        for eth_device in eth_devices:
            mac_devices.append(self._handle.remapIds(eth_device)[0])
        for (mac_device, mult, mac_step, mac) in zip(mac_devices, mac_mults, mac_steps, macs):
            if mult <= 1:
                m1 = self._handle.setAttribute(self._handle.getAttribute(mac_device, '-mac') + '/singleValue', '-value', mac)
            else:
                helpers.log('###Adding Multipier ...')
                m1 = self._handle.setMultiAttribute(self._handle.getAttribute(mac_device, '-mac') + '/counter', '-direction',
                                              'increment', '-start', mac, '-step', mac_step)
        self._handle.commit()
#         helpers.log(" ## adding Name ", topology[0], topology[1])
#         helpers.log(" ## adding Name ", mac_devices[0], mac_devices[1])
        i = 1
        for mac_device in mac_devices:
            self._handle.setAttribute(mac_device, '-name', 'SND_RCV Device' + str(i))
            i = i + 1
        self._handle.commit()
        helpers.log("### Done adding two device groups")
        return mac_devices

    def get_eth_device_and_ip_device(self, mac, topo_name):
        handle = self._handle
        topos = handle.getList(handle.getRoot(), 'topology')
        print("Topos found: %s" % topos)
        for topo in topos:
            ixia_topo_name = handle.getAttribute(topo, '-name')
            helpers.debug("ixia_topo name found: %s" % ixia_topo_name)
            if topo_name == ixia_topo_name:
                dev_group = handle.getList(topo, 'deviceGroup')
                helpers.debug("ixia_device group found: %s" % dev_group)
                for device in dev_group:
                    eth_devices = handle.getList(device, 'ethernet')
                    helpers.debug("ixia eth_Devices found: %s" % eth_devices)
                    for eth_device in eth_devices:
                        ixia_mac = handle.getAttribute(eth_device, '-mac')
                        ixia_mac_value = handle.getAttribute(ixia_mac + '/singleValue' , '-value')
                        helpers.debug("ixia_mac_value found : %s" % ixia_mac_value)
                        ixia_ip_devices = handle.getList(eth_device, 'ipv4')
                        helpers.debug("ixia_ip_devices: %s" % ixia_ip_devices)
                        if ixia_mac_value == mac and len(ixia_ip_devices) > 0:
                            return eth_device, ixia_ip_devices[0]
        return None, None
    def ix_create_device_ethernet_ip(self, topology, s_cnt, d_cnt, s_mac, d_mac, s_mac_step, d_mac_step,
                                     src_ip, dst_ip, src_gw_ip, dst_gw_ip, s_ip_step, d_ip_step,
                                     s_gw_step, d_gw_step, src_gw_mac=None,
                                     dst_gw_mac=None, ip_type='ipv4', vlan_id=None, vlan_step=0, src_gw_prefix=None, dst_gw_prefix=None, vlan_p=None, vlan_p_step=0):
        '''
            RETURN IXIA MAC DEVICES with Ips mapped with Topologies created with vports and added increment values accordingly
            Ex Usage:
            IxLib.IxCreateDeviceEthernet(ixNet,topology, mac_mults =  mac_mults, macs = macs, mac_steps = mac_steps)
        '''
        helpers.log("IP TYPE ------->: %s" % ip_type)
        helpers.log("### Adding %s device groups" % len(topology))
        handle = self._handle
        mac_mults = [s_cnt, d_cnt]
        mac_steps = [s_mac_step, d_mac_step]
        macs = [s_mac, d_mac]
        ips = [src_ip, dst_ip]
        ip_steps = [s_ip_step, d_ip_step]
        gw_ips = [src_gw_ip, dst_gw_ip]
        gw_steps = [s_gw_step, d_gw_step]
        gw_macs = [src_gw_mac, dst_gw_mac]
        prefixs = [src_gw_prefix, dst_gw_prefix]

        topo_names = []
        mac_devices = []  # as this are added to ixia need to remap as per ixia API's
        ip_devices = []
        ixia_refs = {}  # Dictionary to hold the Ixia References
        topo_devices = []
        eth_devices = []

        for topo in topology:
            if len(self._handle.getList(topo, 'deviceGroup')) > 0:
                helpers.log('Ixia Device Group already created for this Topology so no need to created again')
            else:
                helpers.log("First Stop Protocols on all topos before adding new Topo for Ixia port")
                self._handle.execute('stop', topo)
                helpers.log('Successfuly Stopped Hosts on Topology : %s ' % topo)
                helpers.log('Sleeps 3 sec for Hosts to be Stopped')
                self._handle.add(topo, 'deviceGroup')

        self._handle.commit()

        for topo in topology:
            dev_grp = self._handle.getList(topo, 'deviceGroup')
            topo_device = self._handle.remapIds(dev_grp)[0]
            enabled_ref = self._handle.getAttribute(topo_device, '-enabled')
            self._handle.setMultiAttribute(enabled_ref, '-clearOverlays', False, '-pattern', 'singleValue')
            topo_devices.append(topo_device)
            self._is_device_created = True

        for (topo_device, multi, topo, mac) in zip(topo_devices, mac_mults, topology, macs):
            helpers.log('### topo device : %s' % str(topo_device))
            topo_name = self._handle.getAttribute(topo, '-name')
            topo_names.append(topo_name)
            self._handle.setAttribute(topo_device, '-multiplier', multi)
            (ixia_eth_device, ixia_ip_device) = self.get_eth_device_and_ip_device(mac, topo_name)
            if ixia_eth_device is not None:
                helpers.log("Using ALREADY CREATED IXIA ETH DEVICE AND IP DEVICE SKIPPING CREATING AGAIN FROM SAME MAC...")
                eth_devices.append(ixia_eth_device)
                continue
            helpers.log("Adding NEW ETHERNET DEVICE for MAC: %s" % mac)
            eth_devices.append(self._handle.add(topo_device, 'ethernet', '-name', topo_name))
        if vlan_id is not None:
            for eth_device in eth_devices:
                helpers.log("Setting VLAN TRUE in Ixia Ethernet Device")
                self._handle.setMultiAttribute(eth_device, '-useVlans', True)
                self._handle.setMultiAttribute(eth_device + '/vlan:1', '-name')  # Vlan name removed
                self._handle.commit()
                tpid = self._handle.getAttribute(eth_device + '/vlan:1', '-tpid')  # get tpid
                self._handle.setMultiAttribute(tpid, 'clearOverlays', False, '-pattern', 'singleValue')  #
                eth_type = self._handle.add(tpid, 'singleValue')  #
                self._handle.setMultiAttribute(eth_type, '-value', 'ethertype8100')  #
                ixia_vlan_id_refs = self._handle.getAttribute(eth_device + '/vlan:1', '-vlanId')
                self._handle.setMultiAttribute(ixia_vlan_id_refs, 'clearOverlays', False, '-pattern', 'counter')
                self._handle.commit()
                ixia_vlan_counter_refs = self._handle.add(ixia_vlan_id_refs, "counter")
                self._handle.setMultiAttribute(ixia_vlan_counter_refs, '-direction', 'increment', '-start', vlan_id, '-step', vlan_step)
                self._handle.commit()
                if vlan_p is not None:
                    helpers.log("Adding VLAN PRIORITY...")
                    prio = self._handle.getAttribute(eth_device + '/vlan:1', '-priority')  #
                    self._handle.setMultiAttribute(prio, 'clearOverlays', False, '-pattern', 'counter')  #
                    self._handle.commit()
                    vlan_1p = self._handle.add(prio, 'counter')  #
                    self._handle.setMultiAttribute(vlan_1p, '-direction', 'increment', '-start', vlan_p, '-step', vlan_p_step)  # need to add 1p_priority as an argument
                    self._handle.commit()


        self._handle.commit()

        for eth_device in eth_devices:
            mac_devices.append(self._handle.remapIds(eth_device)[0])
        for (mac_device, mult, mac_step, mac, ip_step, ip, gw_step, gw_ip, gw_mac, prefix, topo_name) in zip(mac_devices, mac_mults, mac_steps, macs, ip_steps, ips, gw_steps, gw_ips, gw_macs, prefixs, topo_names):
            ip_name = handle.getAttribute(mac_device, '-name')
#             ip_name = ip_name + 'IPv4\ 1'
            helpers.log('Values:')
            helpers.log('\nMac Device:%s\nMac_Multi:%s\nMac_Step:%s\nMac:%s\nIP_Steps:%s\nIP:%s\nGW_STEP:%s\nGW_IP:%s\nGW_MAC:%s\nVLAN:%s' %
                        (mac_device, mult, mac_step, mac, ip_step, ip, gw_step, gw_ip, gw_mac, vlan_id))
            helpers.log ('Device: NAME : ' + str(ip_name))
            (ixia_eth_device, ixia_ip_device) = self.get_eth_device_and_ip_device(mac, topo_name)
            if ixia_eth_device is not None:
                helpers.log("USING ALREADY CREATED IXIA ETH DEVICE AND IP DEVICE SKIPPING CREATING AGAIN FROM SAME MAC...")
                ip_device = ixia_ip_device
                ip_device_ixia = handle.remapIds(ip_device)[0]
                ip_devices.append(ip_device_ixia)
                continue
            else:
                helpers.log("ADDING NEW IP_DEVICE  for MAC: %s" % mac)
                ip_device = self._handle.add(mac_device, ip_type, '-name', ip_name)

            ip_device_ixia = handle.remapIds(ip_device)[0]
            handle.commit()
            ip_devices.append(ip_device_ixia)
            helpers.log('Using Address: ' + str(ip))
            ixia_refs['address'] = handle.getAttribute(ip_device_ixia, '-address')

            if mult <= 1:
                m1 = self._handle.setAttribute(self._handle.getAttribute(mac_device, '-mac') + '/singleValue', '-value', mac)
                if ip_type == 'ipv6':
                    handle.setMultiAttribute(ixia_refs['address'] + '/counter', 'direction', 'increment', '-start', ip, '-step', '0:0:0:0:0:0:0:0')
                elif ip_type == 'ipv4':
                    handle.setMultiAttribute(ixia_refs['address'] + '/counter', 'direction', 'increment', '-start', ip, '-step', '0.0.0.0')
                ixia_refs['gatewayIp'] = handle.getAttribute(ip_device_ixia, '-gatewayIp')
                ixia_refs['gatewayIp_singleValue'] = handle.add(ixia_refs['gatewayIp'], 'singleValue')
                handle.setMultiAttribute(ixia_refs['gatewayIp_singleValue'], '-value', gw_ip)
            else:
                helpers.log('Adding Multipier ...for mac and Ip')
                helpers.log('Adding Mac: %s with mac_step : %s' % (mac, mac_step))

                m1 = self._handle.setMultiAttribute(self._handle.getAttribute(mac_device, '-mac') + '/counter', '-direction',
                                              'increment', '-start', mac, '-step', mac_step)
                helpers.log('Adding IP : %s with ip_step : %s' % (ip, ip_step))
                handle.setMultiAttribute(ixia_refs['address'] + '/counter', 'direction', 'increment', '-start', ip, '-step', ip_step)
                ixia_refs['gatewayIp'] = handle.getAttribute(ip_device_ixia, '-gatewayIp')
                handle.setMultiAttribute(ixia_refs['gatewayIp'], '-clearOverlays ', False, '-pattern', 'counter')
                ixia_refs['gatewayIp_counter'] = handle.add(ixia_refs['gatewayIp'], 'counter')
                helpers.log('Adding GW_IP : %s with gw_ip_step : %s' % (gw_ip, gw_step))
                handle.setMultiAttribute(ixia_refs['gatewayIp'] + '/counter', 'direction', 'increment', '-start', gw_ip, '-step', gw_step)
            handle.commit()
            # handle.remapIds(ixia_refs['address_counter'])[0]
            if prefix is None:
                prefix = '24'
            ixia_refs['prefix'] = handle.getAttribute(ip_device_ixia, '-prefix')
            ixia_refs['prefix_singleValue'] = handle.add(ixia_refs['prefix'], 'singleValue')
            handle.setMultiAttribute(ixia_refs['prefix_singleValue'], '-value', prefix)
            handle.commit()
            handle.remapIds(ixia_refs['prefix'])[0]

            ixia_refs['resolveGateway'] = handle.getAttribute(ip_device_ixia, '-resolveGateway')
            ixia_refs['resolveGateway_singleValue'] = handle.add(ixia_refs['resolveGateway'], 'singleValue')
            if gw_mac is None:
                helpers.log ('Gateway Address: ' + str(gw_ip))
                handle.setMultiAttribute(ixia_refs['resolveGateway_singleValue'], '-value', 'true')
                handle.commit()
                ixia_refs['resolveGateway_singleValue_remap'] = handle.remapIds(ixia_refs['resolveGateway_singleValue'])[0]
                handle.commit()
#                 handle.remapIds(ixia_refs['gatewayIp_singleValue'])[0]
            else:
                helpers.log('Setting Gw mac manually ..')
                self._arp_check = False
                handle.setMultiAttribute(ixia_refs['resolveGateway_singleValue'], '-value', 'false')
                handle.commit()
                ixia_refs['resolveGateway_singleValue_remap'] = handle.remapIds(ixia_refs['resolveGateway_singleValue'])[0]
                ixia_refs['manualGatewayMac'] = handle.getAttribute(ip_device_ixia, '-manualGatewayMac')
                ixia_refs['manualGatewayMac_singleValue'] = handle.add(ixia_refs['manualGatewayMac'], 'singleValue')
                handle.setMultiAttribute(ixia_refs['manualGatewayMac_singleValue'], '-value', gw_mac)
                handle.commit()
                handle.remapIds(ixia_refs['manualGatewayMac_singleValue'])[0]

        i = 1
        for mac_device in mac_devices:
            name = "Device_" + str(i)
            self._handle.setAttribute(mac_device, '-name', name)
            i = i + 1
        self._handle.commit()
        helpers.log("### Done adding two device groups")
        return ip_devices, mac_devices  # return created Ip_devices and mac_devices

    def ix_setup_traffic_streams_ip(self, ip1, ip2, frameType, frameSize, frameRate, frameMode):
        handle = self._handle
        handle.add(handle.getRoot() + '/traffic', 'trafficItem', '-name', 'IPv4 traffic', '-allowSelfDestined', False,
                   '-trafficItemType', 'l2L3', '-mergeDestinations', False, '-egressEnabled', False, '-srcDestMesh', 'oneToOne',
                   '-enabled', True, '-routeMesh', 'oneToOne', '-transmitMode', 'interleaved', '-biDirectional', False,
                   '-trafficType', 'ipv4', '-hostsPerNetwork', 1)
        handle.commit()
        trItem = handle.getList(handle.getRoot() + '/traffic', 'trafficItem')
        trafficStream1 = handle.remapIds(trItem)[0]
        end1 = handle.add(trafficStream1, 'endpointSet', '-sources', ip1, '-destinations', ip2, '-name', 'end1', '-sourceFilter', ' ', '-destinationFilter', ' ')
        end2 = handle.add(trafficStream1, 'endpointSet', '-sources', ip2, '-destinations', ip1, '-name', 'end2', '-sourceFilter', ' ', '-destinationFilter', ' ')
        handle.commit()
        self._handle.setAttribute(trafficStream1, '-enabled', True)
        self._handle.setAttribute(trafficStream1 + '/highLevelStream:1/' + 'frameSize', '-type', frameType)
        self._handle.setAttribute(trafficStream1 + '/highLevelStream:1/' + 'frameSize', '-fixedSize', frameSize)
        self._handle.setAttribute(trafficStream1 + '/highLevelStream:1/' + 'frameRate', '-type', frameMode)
        self._handle.setAttribute(trafficStream1 + '/highLevelStream:1/' + 'frameRate', '-rate', frameRate)
        self._handle.setAttribute(self._handle.getList(trafficStream1, 'tracking')[0], '-trackBy', 'trackingenabled0')
        handle.commit()
        return trafficStream1

    def ix_setup_traffic_streams_raw(self, frameType, frameSize, frameRate, frameMode, frameCount, flow, name,
                                     mpls_label=None,
                                     lacp_src_mac=None, lld_tlv_chassis_id=None, src_mac=None, dst_mac=None, ethertype=None, vlan_id=None, vlan_cnt=1, vlan_step=None,
                                      burst_cnt=None, burst_gap=None, dst_cnt=None, src_cnt=None, src_mac_step=None, dst_mac_step=None,
                                      line_rate=None, crc=None, src_ip=None, dst_ip=None, src_ip_step=None, dst_ip_step=None, src_ip_cnt=None, dst_ip_cnt=None,
                                      protocol=None, src_port=None, dst_port=None,
                                      icmp_type=None, icmp_code=None, ip_type='ipv4', payload=None, src_vport=None, dst_vport=None,
                                      hex_src_mac=None, hex_dst_mac=None,
                                      synBit=False, urgBit=False, ackBit=False, pshBit=False, rstBit=False, finBit=False, vlan_priority=None):
        '''
           Return Traffic stream with quick flow creation similar to IxNetwork
        '''
        helpers.log("Adding Raw Type Stream with given Raw stream Parameters..")
        current_header_id = 0  # used to add the layer id in Ixia
        tcp_layer_id = 3
        ip_layer_id = str(tcp_layer_id - 1)
        if self._raw_stream is None:
            helpers.log("Creating a New RAW_STREAM ITEM..")
            trafficStream1 = self._handle.add(self._handle.getRoot() + '/traffic', 'trafficItem', '-name',
                                            name, '-trafficItemType', 'quick', '-enabled', True, '-trafficType', 'raw')
            trafficStream1 = self._handle.remapIds(trafficStream1)[0]
            self._raw_stream = trafficStream1
            self._handle.commit()
        else:
            trafficStream1 = self._raw_stream
            self._raw_stream_id = self._raw_stream_id + 1

        stream_name_id = '/highLevelStream:%s' % str(self._raw_stream_id)
        helpers.log("Stream_name_id : %s" % stream_name_id)
        helpers.log("Stream_Name : %s " % trafficStream1)
        helpers.log("src_vport: %s dst_vport: %s" % (src_vport, dst_vport))
        helpers.log("Setting src and dst vports for Raw Streams ...%s  %s " % (src_vport, dst_vport))

        endpointSet1 = self._handle.add(trafficStream1, 'endpointSet', '-sources', src_vport + '/protocols',
                                        '-destinations', dst_vport + '/protocols')
        self._handle.commit()
        endpointSet1 = self._handle.remapIds(endpointSet1)[0]
        self._handle.setMultiAttribute(trafficStream1 + stream_name_id, '-name', name,
                                           '-txPortId', src_vport)
        self._handle.commit()
        self._handle.setAttribute(trafficStream1, '-enabled', True)
        self._handle.commit()
        self._handle.setAttribute(trafficStream1 + stream_name_id + '/frameSize', '-type', frameType)
        self._handle.setAttribute(trafficStream1 + stream_name_id + '/frameSize', '-fixedSize', frameSize)
        self._handle.commit()

        if src_mac is not None and dst_mac is not None:
            helpers.log("Adding HEX Src and Dst MAC's for Raw Stream ..")
            current_header_id += 1
            if dst_cnt is not None:
                helpers.log("Adding DST_MAC COUNT VALUES..")
                self._handle.setMultiAttribute(trafficStream1 + stream_name_id + '/stack:"ethernet-%s"/field:"ethernet.header.destinationAddress-1"' % str(current_header_id),
                                          '-stepValue', dst_mac_step, '-valueType', 'increment', '-optionalEnabled', True, '-countValue', dst_cnt,
                                          '-startValue', dst_mac)
            else:
                helpers.log("Adding Single DST_MAC ..")
                self._handle.setMultiAttribute(trafficStream1 + stream_name_id + '/stack:"ethernet-%s"/field:"ethernet.header.destinationAddress-1"' % str(current_header_id),
                                          '-auto', False, '-fieldValue', dst_mac, '-singleValue', dst_mac,
                                          '-optionalEnabled', True, '-countValue', '1')
            if src_cnt is not None:
                helpers.log("Adding SRC_CNT COUNT VALUES..")
                self._handle.setMultiAttribute(trafficStream1 + stream_name_id + '/stack:"ethernet-%s"/field:"ethernet.header.sourceAddress-2"' % str(current_header_id),
                                          '-stepValue', src_mac_step, '-valueType', 'increment', '-optionalEnabled', True, '-countValue', src_cnt,
                                          '-startValue', src_mac)
            else:
                helpers.log("Adding Single SRC_MAC..")
                self._handle.setMultiAttribute(trafficStream1 + stream_name_id + '/stack:"ethernet-%s"/field:"ethernet.header.sourceAddress-2"' % str(current_header_id),
                                          '-auto', False, '-fieldValue', src_mac, '-singleValue', src_mac,
                                          '-optionalEnabled', True, '-countValue', '1')

        if line_rate is not None:
            helpers.log('Adding Line Rate Value !')
            self._handle.setAttribute(trafficStream1 + stream_name_id + 'frameRate', '-rate', line_rate)

        if burst_cnt is not None:
            helpers.log('Adding BURST COUNT and BURST GAP !!!!')
            self._handle.setMultiAttribute(trafficStream1 + stream_name_id + '/transmissionControl', '-interStreamGap', 0,
                                           '-burstPacketCount', burst_cnt, '-type', 'custom',
                                 '-interBurstGap', burst_gap, '-enableInterBurstGap', True)
            self._handle.setMultiAttribute(trafficStream1 + stream_name_id + '/frameRate', '-rate', frameRate,
                                           '-enforceMinimumInterPacketGap', 0)
        if line_rate is None:
            helpers.log('Adding Frame Rate !!!!')
            self._handle.setAttribute(trafficStream1 + stream_name_id + '/frameRate', '-type', frameMode)
            self._handle.setAttribute(trafficStream1 + stream_name_id + '/frameRate', '-rate', frameRate)
        if frameCount is not None:
            self._handle.setAttribute(trafficStream1 + stream_name_id + '/transmissionControl', '-type',
                                'fixedFrameCount')
            self._handle.setAttribute(trafficStream1 + stream_name_id + '/transmissionControl',
                                '-frameCount', frameCount)
        if crc is not None:
            self._handle.setAttribute(trafficStream1 + stream_name_id, '-crc', 'badCrc')
        if ethertype is not None:
            if current_header_id == 0:
                current_header_id += 1
            helpers.log('Adding Ethertype %s !!!' % ethertype)
            self._handle.setAttribute(trafficStream1 + stream_name_id + '/stack:"ethernet-%s"/field:"ethernet.header.etherType-3"' % str(current_header_id),
                                      '-auto', False)
            self._handle.setAttribute(trafficStream1 + stream_name_id + '/stack:"ethernet-%s"/field:"ethernet.header.etherType-3"' % str(current_header_id),
                                      '-fieldValue', ethertype)
            self._handle.setAttribute(trafficStream1 + stream_name_id + '/stack:"ethernet-%s"/field:"ethernet.header.etherType-3"' % str(current_header_id),
                                      '-singleValue', ethertype)
            self._handle.setAttribute(trafficStream1 + stream_name_id + '/stack:"ethernet-%s"/field:"ethernet.header.etherType-3"' % str(current_header_id),
                                      '-countValue', 1)
            self._handle.setAttribute(trafficStream1 + stream_name_id + '/stack:"ethernet-%s"/field:"ethernet.header.etherType-3"' % str(current_header_id),
                                      '-fixedBits', ethertype)
            self._handle.setAttribute(trafficStream1 + stream_name_id + '/stack:"ethernet-%s"/field:"ethernet.header.etherType-3"' % str(current_header_id),
                                      '-optionalEnabled ', True)
        if lacp_src_mac is not None:
            if current_header_id == 0:
                current_header_id += 1
            helpers.log("Adding LACP DST MAC for Raw Stream ..")
            self._handle.setMultiAttribute(trafficStream1 + stream_name_id + '/stack:"lacp-%s"/field:"lacp.header.header.dstAddress-1"' % str(current_header_id),
                                      '-auto', False, '-fieldValue', '01:80:c2:00:00:02', '-singleValue', '01:80:c2:00:00:02',
                                      '-optionalEnabled', True, '-countValue', '1')
            if src_cnt is not None:
                helpers.log("Adding LACP SRC MAC COUNT with LACP SRC MAC...src_cnt: %s" % src_cnt)
                self._handle.setMultiAttribute(trafficStream1 + stream_name_id + '/stack:"lacp-%s"/field:"lacp.header.header.srcAddress-2"' % str(current_header_id),
                                          '-stepValue', src_mac_step, '-valueType', 'increment', '-optionalEnabled', True, '-countValue', src_cnt,
                                          '-startValue', lacp_src_mac)
            else:
                helpers.log("Adding LACP SRC MAC..")
                self._handle.setMultiAttribute(trafficStream1 + stream_name_id + '/stack:"lacp-%s"/field:"lacp.header.header.srcAddress-2"' % str(current_header_id),
                                          '-auto', False, '-fieldValue', lacp_src_mac, '-singleValue', lacp_src_mac,
                                          '-optionalEnabled', True, '-countValue', '1')
        if lld_tlv_chassis_id is not None:
            current_header_id += 1
            helpers.log("Adding LLDP ttlv chassis id in RAW STREAM..")
            self._handle.setMultiAttribute(trafficStream1 + stream_name_id + '/stack:"lldp-%s"/field:"lldp.header.mandatoryTlv.chassisIdTlv.type-1"' % str(current_header_id),
                                      '-auto', False, '-fieldValue', lld_tlv_chassis_id, '-singleValue', lld_tlv_chassis_id,
                                      '-optionalEnabled', True, '-countValue', '1')
        if mpls_label is not None:
            helpers.log("Adding MPLS Label : %s" % mpls_label)
            current_header_id += 1
            helpers.log("Current Header ID: %s" % str(current_header_id))
            self._handle.setMultiAttribute(trafficStream1 + stream_name_id + '/stack:"mpls-%s"/field:"mpls.label.value-1"' % str(current_header_id),
                                      '-auto', False, '-fieldValue', mpls_label, '-singleValue', mpls_label,
                                      '-optionalEnabled', True, '-countValue', '1')
        if vlan_id is not None:
            current_header_id += 1
            helpers.log('Current Header ID: %s' % str(current_header_id))
            if vlan_priority is None:
                helpers.log('Adding Vlan ID: %s !!!' % vlan_id)
                helpers.log("Changing layer4 id ..")
                tcp_layer_id = tcp_layer_id + 1
                ip_layer_id = str(tcp_layer_id - 1)
                helpers.log("layer4 id : %s" % str(tcp_layer_id))
                if vlan_cnt == 1:
                    self._handle.setMultiAttribute(trafficStream1 + stream_name_id + '/stack:"vlan-%s"/field:"vlan.header.vlanTag.vlanID-3"' % str(current_header_id),
                                              '-countValue', vlan_cnt, '-fieldValue', vlan_id, '-optionalEnabled', True)
                else:
                    self._handle.setAttribute(trafficStream1 + stream_name_id + '/stack:"vlan-%s"/field:"vlan.header.vlanTag.vlanID-3"' % str(current_header_id),
                                              '-countValue', vlan_cnt)
                    self._handle.setAttribute(trafficStream1 + stream_name_id + '/stack:"vlan-%s"/field:"vlan.header.vlanTag.vlanID-3"' % str(current_header_id),
                                              '-startValue', vlan_id)
                    self._handle.setMultiAttribute(trafficStream1 + stream_name_id + '/stack:"vlan-%s"/field:"vlan.header.vlanTag.vlanID-3"' % str(current_header_id),
                                              '-stepValue', vlan_step, '-valueType', 'increment', '-optionalEnabled', True)
            else:
                helpers.log('Adding Vlan ID:%s With Priority: %s !!!' % (vlan_id, vlan_priority))
#                 helpers.log("Changing layer4 id ..")
#                 tcp_layer_id = 4
#                 ip_layer_id = str(tcp_layer_id - 1)
#                 helpers.log("layer4 id : %s" % str(tcp_layer_id))
                if vlan_cnt == 1:
                    self._handle.setMultiAttribute(trafficStream1 + stream_name_id + '/stack:"vlan-%s"/field:"vlan.header.vlanTag.vlanUserPriority-1"' % str(current_header_id),
                                              '-countValue', vlan_cnt, '-fieldValue', vlan_priority, '-optionalEnabled', True)

                    self._handle.setMultiAttribute(trafficStream1 + stream_name_id + '/stack:"vlan-%s"/field:"vlan.header.vlanTag.vlanID-3"' % str(current_header_id),
                                              '-countValue', vlan_cnt, '-fieldValue', vlan_id, '-optionalEnabled', True)
                else:
                    self._handle.setAttribute(trafficStream1 + stream_name_id + '/stack:"vlan-%s"/field:"vlan.header.vlanTag.vlanID-3"' % str(current_header_id),
                                              '-countValue', vlan_cnt)
                    self._handle.setAttribute(trafficStream1 + stream_name_id + '/stack:"vlan-%s"/field:"vlan.header.vlanTag.vlanID-3"' % str(current_header_id),
                                              '-startValue', vlan_id)
                    self._handle.setMultiAttribute(trafficStream1 + stream_name_id + '/stack:"vlan-%s"/field:"vlan.header.vlanTag.vlanID-3"' % str(current_header_id),
                                              '-stepValue', vlan_step, '-valueType', 'increment', '-optionalEnabled', True)

        helpers.log("Commiting vlan config in IXIA...")
        helpers.log("ip_type : %s, src_ip: %s" % (ip_type, src_ip))
        self._handle.commit()
        if ip_type == "ipv4":
            current_header_id += 1
            helpers.log('Current Header ID: %s' % str(current_header_id))
            helpers.log("Adding IPV4 Address...")
            if src_ip is not None:
                helpers.log('Adding src_ip..')
                if src_ip_cnt <= 1:
                    helpers.log("Ipv4 id : ipv4-%s" % ip_layer_id)
                    helpers.log("Adding src_ip to raw_stream with single Value")
                    self._handle.setMultiAttribute(trafficStream1 + stream_name_id + '/stack:"ipv4-%s"/field:"ipv4.header.srcIp-27"' % str(current_header_id),
                                              '-countValue', 1, '-fieldValue', src_ip, '-singleValue', src_ip,
                                             '-optionalEnabled', 'true', '-auto', 'false')
                else:
                    helpers.log("Adding src_ip to raw_stream with multiple Values..")
                    self._handle.setMultiAttribute(trafficStream1 + stream_name_id + '/stack:"ipv4-%s"/field:"ipv4.header.srcIp-27"' % str(current_header_id),
                                              '-stepValue', src_ip_step, '-valueType', 'increment', '-optionalEnabled', True, '-countValue', src_ip_cnt,
                                      '-startValue', src_ip)
            if dst_ip is not None:
                helpers.log("Adding Dst ip Got Dst_Cnt: %s..." % dst_ip_cnt)
                if dst_ip_cnt <= 1:
                    helpers.log("Adding dst_ip to raw_stream with single value ...")
                    self._handle.setMultiAttribute(trafficStream1 + stream_name_id + '/stack:"ipv4-%s"/field:"ipv4.header.dstIp-28"' % str(current_header_id),
                                              '-countValue', 1, '-fieldValue', dst_ip, '-singleValue', dst_ip,
                                             '-optionalEnabled', 'true', '-auto', 'false')
                else:
                    helpers.log("Adding dst_ip to raw_stream with multiple Values...")
                    self._handle.setMultiAttribute(trafficStream1 + stream_name_id + '/stack:"ipv4-%s"/field:"ipv4.header.dstIp-28"' % str(current_header_id),
                                              '-stepValue', dst_ip_step, '-valueType', 'increment', '-optionalEnabled', True, '-countValue', dst_ip_cnt,
                                      '-startValue', dst_ip)

        elif ip_type == "ipv6":
            helpers.log('Adding src_ip and dst_ip ..')
            helpers.log("Ipv6id : ipv6-%s" % ip_layer_id)
            current_header_id += 1
            helpers.log('Current Header ID: %s' % str(current_header_id))
            self._handle.setMultiAttribute(trafficStream1 + stream_name_id + '/stack:"ipv6-%s"/field:"ipv6.header.srcIP-7"' % str(current_header_id),
                                      '-countValue', 1, '-fieldValue', src_ip, '-singleValue', src_ip,
                                     '-optionalEnabled', 'true', '-auto', 'false')
            self._handle.setMultiAttribute(trafficStream1 + stream_name_id + '/stack:"ipv6-%s"/field:"ipv6.header.dstIP-8"' % str(current_header_id),
                                      '-countValue', 1, '-fieldValue', dst_ip, '-singleValue', dst_ip,
                                     '-optionalEnabled', 'true', '-auto', 'false')
        if protocol == 'ICMP':
                helpers.log('Current Header ID: %s' % str(current_header_id))
                helpers.log('Adding Message Type: %s and Code Value: %s for Protocl UDP..!!!' % (icmp_type, icmp_code))
                self._handle.setMultiAttribute(trafficStream1 + stream_name_id + '/stack:"icmpv2-%s"/field:"icmpv2.message.messageType-1"' % str(current_header_id),
                                              '-countValue', 1, '-singleValue', icmp_type,
                                             '-optionalEnabled', 'true', '-auto', 'false')
                self._handle.setMultiAttribute(trafficStream1 + stream_name_id + '/stack:"icmpv2-%s"/field:"icmpv2.message.codeValue-2"' % str(current_header_id),
                                              '-countValue', 1, '-singleValue', icmp_code,
                                             '-optionalEnabled', 'true', '-auto', 'false')
        helpers.log("Committing IP Config in IXIA...")
        self._handle.commit()
        if protocol is not None:
            helpers.log('Adding Protocol Field in IP Header ..')
            if ethertype == '0800':
                self._handle.setMultiAttribute(trafficStream1 + stream_name_id + '/stack:"ipv4-%s"/field:"ipv4.header.protocol-25"' % str(current_header_id),
                                              '-countValue', 1, '-fieldValue', protocol,
                                             '-optionalEnabled', 'true', '-auto', 'false')
            elif ethertype == '86dd':
                self._handle.setMultiAttribute(trafficStream1 + stream_name_id + '/stack:"ipv6-%s"/field:"ipv6.header.nextHeader-5"' % str(current_header_id),
                                              '-countValue', 1, '-fieldValue', protocol,
                                             '-optionalEnabled', 'true', '-auto', 'false')
            if protocol == 'TCP':
                current_header_id += 1
                helpers.log('Current Header ID: %s' % str(current_header_id))
                helpers.log('Adding Src_port: %s and Dst_Port: %s for Protocl TCP..!!!' % (src_port, dst_port))
#                 helpers.log("Adding tcp id : tcp-%s" % str(tcp_layer_id))
                helpers.log('SynBit : %s' % str(synBit))
                self._handle.setMultiAttribute(trafficStream1 + stream_name_id + '/stack:"tcp-%s"/field:"tcp.header.srcPort-1"' % str(current_header_id),
                                              '-countValue', 1, '-fieldValue', src_port, '-singleValue', src_port,
                                             '-optionalEnabled', 'true', '-auto', 'false')
                self._handle.setMultiAttribute(trafficStream1 + stream_name_id + '/stack:"tcp-%s"/field:"tcp.header.dstPort-2"' % str(current_header_id),
                                              '-countValue', 1, '-fieldValue', dst_port, '-singleValue', dst_port,
                                             '-optionalEnabled', 'true', '-auto', 'false')
                if synBit:
                    helpers.log("Adding Sync Bit with TCP header...")
                    self._handle.setMultiAttribute(trafficStream1 + stream_name_id + '/stack:"tcp-%s"/field:"tcp.header.controlBits.synBit-14"' % str(current_header_id),
                                              '-countValue', 1, '-fieldValue', synBit, '-singleValue', synBit,
                                             '-optionalEnabled', 'true', '-auto', 'false')
                if urgBit:
                    helpers.log("Adding Urgent Bit with TCP header...")
                    self._handle.setMultiAttribute(trafficStream1 + stream_name_id + '/stack:"tcp-%s"/field:"tcp.header.controlBits.urgBit-10"' % str(current_header_id),
                                              '-countValue', 1, '-fieldValue', urgBit, '-singleValue', urgBit,
                                             '-optionalEnabled', 'true', '-auto', 'false')
                if ackBit:
                    helpers.log("Adding ACK Bit with TCP header...")
                    self._handle.setMultiAttribute(trafficStream1 + stream_name_id + '/stack:"tcp-%s"/field:"tcp.header.controlBits.ackBit-11"' % str(current_header_id),
                                              '-countValue', 1, '-fieldValue', ackBit, '-singleValue', ackBit,
                                             '-optionalEnabled', 'true', '-auto', 'false')
                if pshBit:
                    helpers.log("Adding PSH Bit with TCP header...")
                    self._handle.setMultiAttribute(trafficStream1 + stream_name_id + '/stack:"tcp-%s"/field:"tcp.header.controlBits.pshBit-12"' % str(current_header_id),
                                              '-countValue', 1, '-fieldValue', pshBit, '-singleValue', pshBit,
                                             '-optionalEnabled', 'true', '-auto', 'false')
                if rstBit:
                    helpers.log("Adding RST Bit with TCP header...")
                    self._handle.setMultiAttribute(trafficStream1 + stream_name_id + '/stack:"tcp-%s"/field:"tcp.header.controlBits.rstBit-13"' % str(current_header_id),
                                              '-countValue', 1, '-fieldValue', rstBit, '-singleValue', rstBit,
                                             '-optionalEnabled', 'true', '-auto', 'false')
                if finBit:
                    helpers.log("Adding FIN Bit with TCP header...")
                    self._handle.setMultiAttribute(trafficStream1 + stream_name_id + '/stack:"tcp-%s"/field:"tcp.header.controlBits.finBit-15"' % str(current_header_id) ,
                                              '-countValue', 1, '-fieldValue', finBit, '-singleValue', finBit,
                                             '-optionalEnabled', 'true', '-auto', 'false')

            if protocol == 'UDP':
                current_header_id += 1
                helpers.log('Current Header ID: %s' % str(current_header_id))
                helpers.log('Adding Src_port: %s and Dst_Port: %s for Protocl UDP..!!!' % (src_port, dst_port))
                self._handle.setMultiAttribute(trafficStream1 + '/highLevelStream:1/stack:"udp-%s"/field:"udp.header.srcPort-1"' % str(current_header_id),
                                              '-countValue', 1, '-fieldValue', src_port, '-singleValue', src_port,
                                             '-optionalEnabled', 'true', '-auto', 'false')
                self._handle.setMultiAttribute(trafficStream1 + stream_name_id + '/stack:"udp-%s"/field:"udp.header.dstPort-2"' % str(current_header_id),
                                              '-countValue', 1, '-fieldValue', dst_port, '-singleValue', dst_port,
                                             '-optionalEnabled', 'true', '-auto', 'false')
            if payload:
                helpers.log('Setting Payload information provided to Raw Traffic Stream...')
                self._handle.setMultiAttribute(trafficStream1 + stream_name_id + '/framePayload',
                                              '-type', 'custom', '-customPattern', payload,
                                             '-customRepeat', False, '-auto', 'false')
        self._handle.commit()
        return trafficStream1 + stream_name_id

    def ix_setup_traffic_streams_ethernet(self, mac1, mac2, frameType, frameSize, frameRate,
                                      frameMode, frameCount, flow, name, ethertype=None, ethertype_cnt=1, ethertype_step=None,
                                      vlan_id=None, vlan_cnt=1, vlan_step=None,
                                      burst_count=None, burst_gap=None,
                                      line_rate=None, crc=None, src_ip=None, src_ip_cnt=1, src_ip_step=None,
                                      dst_ip=None, dst_ip_cnt=1, dst_ip_step=None, no_arp=False,
                                      protocol=None, src_port=None, dst_port=None,
                                      icmp_type=None, icmp_code=None, ip_type='ipv4', payload=None, src_vport=None, dst_vport=None,
                                      hex_src_mac=None, hex_dst_mac=None,
                                      synBit=False, urgBit=False, ackBit=False, pshBit=False, rstBit=False, finBit=False):
        '''
            Returns traffic stream with 2 flows with provided mac sources
            Ex Usage:
                IxLib.IxSetupTrafficStreamsEthernet(ixNet, mac_devices[0], mac_devices[1], frameType, frameSize, frameRate, frameMode)
        '''
        handle = self._handle
        tcp_layer_id = 3
        ip_layer_id = str(tcp_layer_id - 1)
        if no_arp:
            helpers.log('Adding Basic ethernet type Stream for sending without Arp Resolution')
            trafficStream1 = self._handle.add(self._handle.getRoot() + 'traffic', 'trafficItem', '-name',
                                        name, '-allowSelfDestined', False, '-trafficItemType',
                                        'l2L3', '-enabled', True, '-transmitMode', 'interleaved',
                                        '-biDirectional', False, '-trafficType', 'ethernetVlan', '-hostsPerNetwork', '1')
            endpointSet1 = self._handle.add(trafficStream1, 'endpointSet', '-name', 'l2u', '-sources', mac1,
                                  '-destinations', mac2)
        elif payload:
            helpers.log("Adding Raw Type Stream with given Payload and L2 , L3 information..")
            trafficStream1 = self._handle.add(self._handle.getRoot() + 'traffic', 'trafficItem', '-name',
                                        name, '-trafficItemType', 'quick', '-enabled', True, '-trafficType', 'raw')
        else:
            helpers.log('Adding %s type Stream for sending with Arp Resolution' % ip_type)
            trafficStream1 = handle.add(handle.getRoot() + '/traffic', 'trafficItem', '-name', name, '-allowSelfDestined', False,
                       '-trafficItemType', 'l2L3', '-mergeDestinations', False, '-egressEnabled', False, '-srcDestMesh', 'oneToOne',
                       '-enabled', True, '-routeMesh', 'oneToOne', '-transmitMode', 'interleaved', '-biDirectional', False,
                       '-trafficType', ip_type, '-hostsPerNetwork', 1)
            endpointSet1 = self._handle.add(trafficStream1, 'endpointSet', '-name', 'l2u', '-sources', mac1,
                                  '-destinations', mac2)
        self._handle.commit()
        trafficStream1 = self._handle.remapIds(trafficStream1)[0]

        if payload:
            helpers.log("src_vport: %s dst_vport: %s" % (src_vport, dst_vport))
            endpointSet1 = self._handle.add(trafficStream1, 'endpointSet', '-sources', src_vport + '/protocols',
                                            '-destinations', dst_vport + '/protocols')
            self._handle.commit()
            endpointSet1 = self._handle.remapIds(endpointSet1)[0]
            helpers.log("Setting src and dst vports for Raw Streams ...%s  %s " % (src_vport, dst_vport))
            self._handle.setMultiAttribute(trafficStream1 + '/highLevelStream:1', '-name', name,
                                               '-txPortId', src_vport)

        self._handle.setAttribute(trafficStream1, '-enabled', True)
        self._handle.commit()
        self._handle.setAttribute(trafficStream1 + '/highLevelStream:1/' + 'frameSize', '-type', frameType)
        self._handle.setAttribute(trafficStream1 + '/highLevelStream:1/' + 'frameSize', '-fixedSize', frameSize)

        if hex_src_mac:
            helpers.log("Adding HEX Src and Dst MAC's for Raw Stream ..")
            self._handle.setMultiAttribute(trafficStream1 + '/highLevelStream:1/stack:"ethernet-1"/field:"ethernet.header.destinationAddress-1"',
                                      '-auto', False, '-fieldValue', hex_dst_mac, '-singleValue', hex_dst_mac,
                                      '-optionalEnabled', True, '-countValue', '1')
            self._handle.setMultiAttribute(trafficStream1 + '/highLevelStream:1/stack:"ethernet-1"/field:"ethernet.header.sourceAddress-2"',
                                      '-auto', False, '-fieldValue', hex_src_mac, '-singleValue', hex_src_mac,
                                      '-optionalEnabled', True, '-countValue', '1')

        if line_rate is not None:
            helpers.log('Adding Line Rate Value !')
            self._handle.setAttribute(trafficStream1 + '/highLevelStream:1/' + 'frameRate', '-rate', line_rate)

        if burst_count is not None:
            helpers.log('Adding BURST COUNT and BURST GAP !!!!')
            self._handle.setMultiAttribute(trafficStream1 + '/highLevelStream:1/' + 'transmissionControl', '-interStreamGap', 0,
                                           '-burstPacketCount', burst_count, '-type', 'custom',
                                 '-interBurstGap', burst_gap, '-enableInterBurstGap', True)
            self._handle.setMultiAttribute(trafficStream1 + '/highLevelStream:1/' + 'frameRate', '-rate', frameRate,
                                           '-enforceMinimumInterPacketGap', 0)

        if line_rate is None:
            helpers.log('Adding Frame Rate !!!!')
            self._handle.setAttribute(trafficStream1 + '/highLevelStream:1/' + 'frameRate', '-type', frameMode)
            self._handle.setAttribute(trafficStream1 + '/highLevelStream:1/' + 'frameRate', '-rate', frameRate)

        if frameCount is not None:
            self._handle.setAttribute(trafficStream1 + '/highLevelStream:1/' + 'transmissionControl', '-type',
                                'fixedFrameCount')
            self._handle.setAttribute(trafficStream1 + '/highLevelStream:1/' + 'transmissionControl',
                                '-frameCount', frameCount)


        if crc is not None:
            self._handle.setAttribute(trafficStream1 + '/highLevelStream:1', '-crc', 'badCrc')
        if ethertype is not None:
            helpers.log('Adding Ethertype %s !!!' % ethertype)
            if ethertype_cnt == 1:
                helpers.log("Adding Ethertype with cnt: 1..")
                self._handle.setMultiAttribute(trafficStream1 + '/highLevelStream:1/stack:"ethernet-1"/field:"ethernet.header.etherType-3"',
                                          '-auto', False, '-fieldValue', ethertype, '-singleValue', ethertype, '-countValue', 1,
                                          '-fixedBits', ethertype, '-optionalEnabled ', 'true')
            else:
                helpers.log("Adding Ethertype with cnt: %s" % str(ethertype_cnt))
                self._handle.setMultiAttribute(trafficStream1 + '/highLevelStream:1/stack:"ethernet-1"/field:"ethernet.header.etherType-3"',
                                        '-countValue', ethertype_cnt, '-startValue', ethertype, '-stepValue', ethertype_step, '-valueType', 'increment',
                                          '-optionalEnabled ', 'true', '-auto', False)

        if vlan_id is not None:
            helpers.log('Adding Vlan ID: %s !!!' % vlan_id)
            helpers.log("Changing layer4 id ..")
            tcp_layer_id = 4
            ip_layer_id = str(tcp_layer_id - 1)
            helpers.log("layer4 id : %s" % str(tcp_layer_id))
            if vlan_cnt == 1:
                self._handle.setAttribute(trafficStream1 + '/highLevelStream:1/stack:"vlan-2"/field:"vlan.header.vlanTag.vlanID-3"',
                                          '-countValue', vlan_cnt)
                self._handle.setAttribute(trafficStream1 + '/highLevelStream:1/stack:"vlan-2"/field:"vlan.header.vlanTag.vlanID-3"',
                                          '-fieldValue', vlan_id)
                self._handle.setAttribute(trafficStream1 + '/highLevelStream:1/stack:"vlan-2"/field:"vlan.header.vlanTag.vlanID-3"',
                                          '-optionalEnabled', True)
            else:
                self._handle.setAttribute(trafficStream1 + '/highLevelStream:1/stack:"vlan-2"/field:"vlan.header.vlanTag.vlanID-3"',
                                          '-countValue', vlan_cnt)
                self._handle.setAttribute(trafficStream1 + '/highLevelStream:1/stack:"vlan-2"/field:"vlan.header.vlanTag.vlanID-3"',
                                          '-startValue', vlan_id)
                self._handle.setMultiAttribute(trafficStream1 + '/highLevelStream:1/stack:"vlan-2"/field:"vlan.header.vlanTag.vlanID-3"',
                                          '-stepValue', vlan_step, '-valueType', 'increment', '-optionalEnabled', True)
        helpers.log("Commiting vlan config in IXIA...")
        helpers.log("ip_type : %s, src_ip: %s" % (ip_type, src_ip))
        self._handle.commit()
        if src_ip is not None:
                if ip_type == "ipv4":
                    helpers.log('Adding src_ip and dst_ip ..')
                    helpers.log("Ipv4 id : ipv4-%s" % ip_layer_id)
                    if src_ip_cnt == 1:
                        helpers.log("Adding SRC_IP: %s WITH Count: 1.." % src_ip)
                        self._handle.setMultiAttribute(trafficStream1 + '/highLevelStream:1/stack:"ipv4-%s"/field:"ipv4.header.srcIp-27"' % ip_layer_id,
                                                  '-countValue', 1, '-fieldValue', src_ip, '-singleValue', src_ip,
                                                 '-optionalEnabled', 'true', '-auto', 'false')
                    else:
                        helpers.log("Adding SRC_IP:%s  WITH Count: %s and step: %s" % (src_ip, str(src_ip_cnt), str(src_ip_step)))
                        if src_ip_step is None:
                            helpers.log("PLEASE PROVIDE SRC_IP_STEP WITH START, SRC_IP FOR MULTIPLE IPs..")
                            return False
                        self._handle.setMultiAttribute(trafficStream1 + '/highLevelStream:1/stack:"ipv4-%s"/field:"ipv4.header.srcIp-27"' % ip_layer_id,
                                                  '-countValue', src_ip_cnt, '-startValue', src_ip, '-stepValue', src_ip_step, '-valueType', 'increment',
                                                 '-optionalEnabled', True)

                    if dst_ip_cnt == 1:
                        helpers.log("Adding DST_IP %s WITH Count: 1.." % dst_ip)
                        self._handle.setMultiAttribute(trafficStream1 + '/highLevelStream:1/stack:"ipv4-%s"/field:"ipv4.header.dstIp-28"' % ip_layer_id,
                                                  '-countValue', 1, '-fieldValue', dst_ip, '-singleValue', dst_ip,
                                                 '-optionalEnabled', 'true', '-auto', 'false')
                    else:
                        helpers.log("Adding DST_IP:%s  WITH Count: %s and step: %s" % (dst_ip, str(dst_ip_cnt), str(dst_ip_step)))
                        if dst_ip_step is None:
                            helpers.log("PLEASE PROVIDE DST_IP_STEP WITH START DST_IP FOR MULTIPLE IPs..")
                            return False
                        self._handle.setMultiAttribute(trafficStream1 + '/highLevelStream:1/stack:"ipv4-%s"/field:"ipv4.header.dstIp-28"' % ip_layer_id,
                                                  '-countValue', dst_ip_cnt, '-startValue', dst_ip, '-stepValue', dst_ip_step, '-valueType', 'increment',
                                                 '-optionalEnabled', True)

                elif ip_type == "ipv6":
                    helpers.log('Adding src_ip and dst_ip ..')
                    helpers.log("Ipv4 id : ipv6-%s" % ip_layer_id)
                    if src_ip_cnt == 1:
                        helpers.log("Adding SRC_IP: %s WITH Count: 1.." % src_ip)
                        self._handle.setMultiAttribute(trafficStream1 + '/highLevelStream:1/stack:"ipv6-%s"/field:"ipv6.header.srcIP-7"' % ip_layer_id,
                                                  '-countValue', 1, '-fieldValue', src_ip, '-singleValue', src_ip,
                                                 '-optionalEnabled', 'true', '-auto', 'false')
                    else:
                        helpers.log("Adding SRC_IP:%s  WITH Count: %s and step: %s" % (src_ip, str(src_ip_cnt), str(src_ip_step)))
                        self._handle.setMultiAttribute(trafficStream1 + '/highLevelStream:1/stack:"ipv6-%s"/field:"ipv6.header.srcIP-7"' % ip_layer_id,
                                                  '-countValue', src_ip_cnt, '-startValue', src_ip, '-stepValue', src_ip_step, '-valueType', 'increment',
                                                 '-optionalEnabled', True)
                    if dst_ip_cnt == 1:
                        helpers.log("Adding DST_IP %s WITH Count: 1.." % dst_ip)
                        self._handle.setMultiAttribute(trafficStream1 + '/highLevelStream:1/stack:"ipv6-%s"/field:"ipv6.header.dstIP-8"' % ip_layer_id,
                                                  '-countValue', 1, '-fieldValue', dst_ip, '-singleValue', dst_ip,
                                             '-optionalEnabled', 'true', '-auto', 'false')
                    else:
                        helpers.log("Adding DST_IP:%s  WITH Count: %s and step: %s" % (dst_ip, str(dst_ip_cnt), str(dst_ip_step)))
                        self._handle.setMultiAttribute(trafficStream1 + '/highLevelStream:1/stack:"ipv6-%s"/field:"ipv6.header.dstIP-8"' % ip_layer_id,
                                                  '-countValue', dst_ip_cnt, '-fieldValue', dst_ip, '-stepValue', dst_ip_step, '-valueType', 'increment',
                                             '-optionalEnabled', True)
        helpers.log("Committing IP Config in IXIA...")
        self._handle.commit()
        if protocol is not None:
            helpers.log('Adding Protocol Field in IP Header ..')
            if ethertype == '0800':
                self._handle.setMultiAttribute(trafficStream1 + '/highLevelStream:1/stack:"ipv4-%s"/field:"ipv4.header.protocol-25"' % ip_layer_id,
                                              '-countValue', 1, '-fieldValue', protocol,
                                             '-optionalEnabled', 'true', '-auto', 'false')
            elif ethertype == '86dd':
                self._handle.setMultiAttribute(trafficStream1 + '/highLevelStream:1/stack:"ipv6-%s"/field:"ipv6.header.nextHeader-5"' % ip_layer_id,
                                              '-countValue', 1, '-fieldValue', protocol,
                                             '-optionalEnabled', 'true', '-auto', 'false')
            if protocol == 'TCP':
                helpers.log('Adding Src_port: %s and Dst_Port: %s for Protocl TCP..!!!' % (src_port, dst_port))
                helpers.log("Adding tcp id : tcp-%s" % str(tcp_layer_id))
                helpers.log('SynBit : %s' % str(synBit))
                self._handle.setMultiAttribute(trafficStream1 + '/highLevelStream:1/stack:"tcp-%s"/field:"tcp.header.srcPort-1"' % str(tcp_layer_id),
                                              '-countValue', 1, '-fieldValue', src_port, '-singleValue', src_port,
                                             '-optionalEnabled', 'true', '-auto', 'false')
                self._handle.setMultiAttribute(trafficStream1 + '/highLevelStream:1/stack:"tcp-%s"/field:"tcp.header.dstPort-2"' % str(tcp_layer_id),
                                              '-countValue', 1, '-fieldValue', dst_port, '-singleValue', dst_port,
                                             '-optionalEnabled', 'true', '-auto', 'false')
                if synBit:
                    helpers.log("Adding Sync Bit with TCP header...")
                    self._handle.setMultiAttribute(trafficStream1 + '/highLevelStream:1/stack:"tcp-%s"/field:"tcp.header.controlBits.synBit-14"' % str(tcp_layer_id),
                                              '-countValue', 1, '-fieldValue', synBit, '-singleValue', synBit,
                                             '-optionalEnabled', 'true', '-auto', 'false')
                if urgBit:
                    helpers.log("Adding Urgent Bit with TCP header...")
                    self._handle.setMultiAttribute(trafficStream1 + '/highLevelStream:1/stack:"tcp-%s"/field:"tcp.header.controlBits.urgBit-10"' % str(tcp_layer_id),
                                              '-countValue', 1, '-fieldValue', urgBit, '-singleValue', urgBit,
                                             '-optionalEnabled', 'true', '-auto', 'false')
                if ackBit:
                    helpers.log("Adding ACK Bit with TCP header...")
                    self._handle.setMultiAttribute(trafficStream1 + '/highLevelStream:1/stack:"tcp-%s"/field:"tcp.header.controlBits.ackBit-11"' % str(tcp_layer_id),
                                              '-countValue', 1, '-fieldValue', ackBit, '-singleValue', ackBit,
                                             '-optionalEnabled', 'true', '-auto', 'false')
                if pshBit:
                    helpers.log("Adding PSH Bit with TCP header...")
                    self._handle.setMultiAttribute(trafficStream1 + '/highLevelStream:1/stack:"tcp-%s"/field:"tcp.header.controlBits.pshBit-12"' % str(tcp_layer_id),
                                              '-countValue', 1, '-fieldValue', pshBit, '-singleValue', pshBit,
                                             '-optionalEnabled', 'true', '-auto', 'false')
                if rstBit:
                    helpers.log("Adding RST Bit with TCP header...")
                    self._handle.setMultiAttribute(trafficStream1 + '/highLevelStream:1/stack:"tcp-%s"/field:"tcp.header.controlBits.rstBit-13"' % str(tcp_layer_id),
                                              '-countValue', 1, '-fieldValue', rstBit, '-singleValue', rstBit,
                                             '-optionalEnabled', 'true', '-auto', 'false')
                if finBit:
                    helpers.log("Adding FIN Bit with TCP header...")
                    self._handle.setMultiAttribute(trafficStream1 + '/highLevelStream:1/stack:"tcp-%s"/field:"tcp.header.controlBits.finBit-15"' % str(tcp_layer_id) ,
                                              '-countValue', 1, '-fieldValue', finBit, '-singleValue', finBit,
                                             '-optionalEnabled', 'true', '-auto', 'false')

            if protocol == 'UDP':
                helpers.log('Adding Src_port: %s and Dst_Port: %s for Protocl UDP..!!!' % (src_port, dst_port))
                self._handle.setMultiAttribute(trafficStream1 + '/highLevelStream:1/stack:"udp-%s"/field:"udp.header.srcPort-1"' % str(tcp_layer_id),
                                              '-countValue', 1, '-fieldValue', src_port, '-singleValue', src_port,
                                             '-optionalEnabled', 'true', '-auto', 'false')
                self._handle.setMultiAttribute(trafficStream1 + '/highLevelStream:1/stack:"udp-%s"/field:"udp.header.dstPort-2"' % str(tcp_layer_id),
                                              '-countValue', 1, '-fieldValue', dst_port, '-singleValue', dst_port,
                                             '-optionalEnabled', 'true', '-auto', 'false')
            if protocol == 'ICMP':
                helpers.log('Adding Message Type: %s and Code Value: %s for Protocl UDP..!!!' % (icmp_type, icmp_code))
                self._handle.setMultiAttribute(trafficStream1 + '/highLevelStream:1/stack:"icmpv2-3"/field:"icmpv2.message.messageType-1"',
                                              '-countValue', 1, '-singleValue', icmp_type,
                                             '-optionalEnabled', 'true', '-auto', 'false')
                self._handle.setMultiAttribute(trafficStream1 + '/highLevelStream:1/stack:"icmpv2-3"/field:"icmpv2.message.codeValue-2"',
                                              '-countValue', 1, '-singleValue', icmp_code,
                                             '-optionalEnabled', 'true', '-auto', 'false')
            if payload:
                helpers.log('Setting Payload information provided to Raw Traffic Stream...')
                self._handle.setMultiAttribute(trafficStream1 + '/highLevelStream:1/framePayload',
                                              '-type', 'custom', '-customPattern', payload,
                                             '-customRepeat', False, '-auto', 'false')
        helpers.log("Committing L4 portocol Config in IXIA...")
        self._handle.commit()
        if flow == 'bi-directional':
            helpers.log('Adding Another  ixia end point set for Bi Directional Traffic..')

            if payload:
                helpers.log("Setting src and dst vports for Raw Streams BiDirectional ...")
                helpers.log("src_vport: %s dst_vport: %s" % (dst_vport, src_port))
                endpointSet2 = self._handle.add(trafficStream1, 'endpointSet', '-sources', dst_vport + '/protocols',
                                                '-destinations', src_vport + '/protocols')
                self._handle.commit()
                endpointSet2 = self._handle.remapIds(endpointSet2)[0]
                helpers.log("Setting src and dst vports for Raw Streams ...%s  %s " % (src_vport, dst_vport))
                self._handle.setMultiAttribute(trafficStream1 + '/highLevelStream:2', '-name', name,
                                                   '-txPortId', dst_vport)
            else:
                endpointSet2 = self._handle.add(trafficStream1, 'endpointSet', '-name', 'l2u', '-sources', mac2,
                                          '-destinations', mac1)
            if crc is not None:
                self._handle.setAttribute(trafficStream1 + '/highLevelStream:2', '-crc', 'badCrc')

            self._handle.setAttribute(trafficStream1 + '/highLevelStream:2/' + 'frameSize', '-type', frameType)
            self._handle.setAttribute(trafficStream1 + '/highLevelStream:2/' + 'frameSize', '-fixedSize', frameSize)

            if line_rate is not None:
                helpers.log('Adding Line Rate Value !')
                self._handle.setAttribute(trafficStream1 + '/highLevelStream:2/' + 'frameRate', '-rate', line_rate)

            if burst_count is not None:
                helpers.log('Adding BURST COUNT and BURST GAP !!!!')
                self._handle.setMultiAttribute(trafficStream1 + '/highLevelStream:2/' + 'transmissionControl', '-interStreamGap', 0,
                                               '-burstPacketCount', burst_count, '-type', 'custom',
                                     '-interBurstGap', burst_gap, '-enableInterBurstGap', True)
                self._handle.setMultiAttribute(trafficStream1 + '/highLevelStream:2/' + 'frameRate', '-rate', frameRate,
                                               '-enforceMinimumInterPacketGap', 0)
            if line_rate is None:
                helpers.log('Adding Frame Rate !!!!')
                self._handle.setAttribute(trafficStream1 + '/highLevelStream:2/' + 'frameRate', '-type', frameMode)
                self._handle.setAttribute(trafficStream1 + '/highLevelStream:2/' + 'frameRate', '-rate', frameRate)

            if frameCount is not None:
                self._handle.setAttribute(trafficStream1 + '/highLevelStream:2/' + 'transmissionControl', '-type',
                                    'fixedFrameCount')
                self._handle.setAttribute(trafficStream1 + '/highLevelStream:2/' + 'transmissionControl', '-frameCount',
                                    frameCount)
            elif burst_count is not None:
                helpers.log('Adding BURST COUNT and BURST GAP !!!!')
                self._handle.setMultiAttribute(trafficStream1 + '/highLevelStream:2/' + 'transmissionControl', '-interStreamGap ', 0,
                                               '-burstPacketCount ', burst_count, '-type', 'custom ', '-minGapBytes', 12,
                                     '-interBurstGap ', burst_gap, '-enableInterBurstGap ', True)
            if ethertype is not None:
                self._handle.setMultiAttribute(trafficStream1 + '/highLevelStream:2/stack:"ethernet-1"/field:"ethernet.header.etherType-3"',
                                          '-auto', False, '-fieldValue', ethertype, '-singleValue', ethertype,
                                          '-countValue', 1, '-fixedBits', ethertype, '-optionalEnabled ', True)
            if vlan_id is not None:
                helpers.log('Adding Vlan ID: %s !!!' % vlan_id)
                if vlan_cnt == 1:
                    self._handle.setAttribute(trafficStream1 + '/highLevelStream:2/stack:"vlan-2"/field:"vlan.header.vlanTag.vlanID-3"',
                                              '-countValue', vlan_cnt)
                    self._handle.setAttribute(trafficStream1 + '/highLevelStream:2/stack:"vlan-2"/field:"vlan.header.vlanTag.vlanID-3"',
                                              '-fieldValue', vlan_id)
                    self._handle.setAttribute(trafficStream1 + '/highLevelStream:2/stack:"vlan-2"/field:"vlan.header.vlanTag.vlanID-3"',
                                              '-optionalEnabled', True)
                else:
                    self._handle.setAttribute(trafficStream1 + '/highLevelStream:2/stack:"vlan-2"/field:"vlan.header.vlanTag.vlanID-3"',
                                              '-countValue', vlan_cnt)
                    self._handle.setAttribute(trafficStream1 + '/highLevelStream:2/stack:"vlan-2"/field:"vlan.header.vlanTag.vlanID-3"',
                                              '-startValue', vlan_id)
                    self._handle.setMultiAttribute(trafficStream1 + '/highLevelStream:2/stack:"vlan-2"/field:"vlan.header.vlanTag.vlanID-3"',
                                              '-stepValue', vlan_step, '-valueType', 'increment', '-optionalEnabled', True)

            if src_ip is not None:
                if ip_type == "ipv4":
                    helpers.log('Adding src_ip and dst_ip ..')
                    helpers.log("Ipv4 id : ipv4-%s" % ip_layer_id)
                    if dst_ip_cnt == 1:
                        helpers.log("Adding SRC_IP: %s WITH Count: 1.." % dst_ip)
                        self._handle.setMultiAttribute(trafficStream1 + '/highLevelStream:2/stack:"ipv4-%s"/field:"ipv4.header.srcIp-27"' % ip_layer_id,
                                                  '-countValue', 1, '-fieldValue', dst_ip, '-singleValue', dst_ip,
                                                 '-optionalEnabled', 'true', '-auto', 'false')
                    else:
                        helpers.log("Adding SRC_IP:%s  WITH Count: %s and step: %s" % (dst_ip, str(dst_ip_cnt), str(dst_ip_step)))
                        if dst_ip_step is None:
                            helpers.log("PLEASE PROVIDE SRC_IP_STEP WITH START, SRC_IP FOR MULTIPLE IPs..")
                            return False
                        self._handle.setMultiAttribute(trafficStream1 + '/highLevelStream:2/stack:"ipv4-%s"/field:"ipv4.header.srcIp-27"' % ip_layer_id,
                                                  '-countValue', dst_ip_cnt, '-startValue', dst_ip, '-stepValue', dst_ip_step, '-valueType', 'increment',
                                                 '-optionalEnabled', True)

                    if src_ip_cnt == 1:
                        helpers.log("Adding DST_IP %s WITH Count: 1.." % src_ip)
                        self._handle.setMultiAttribute(trafficStream1 + '/highLevelStream:2/stack:"ipv4-%s"/field:"ipv4.header.dstIp-28"' % ip_layer_id,
                                                  '-countValue', 1, '-fieldValue', src_ip, '-singleValue', src_ip,
                                                 '-optionalEnabled', 'true', '-auto', 'false')
                    else:
                        helpers.log("Adding DST_IP:%s  WITH Count: %s and step: %s" % (src_ip, str(src_ip_cnt), str(src_ip_step)))
                        if src_ip_step is None:
                            helpers.log("PLEASE PROVIDE DST_IP_STEP WITH START DST_IP FOR MULTIPLE IPs..")
                            return False
                        self._handle.setMultiAttribute(trafficStream1 + '/highLevelStream:2/stack:"ipv4-%s"/field:"ipv4.header.dstIp-28"' % ip_layer_id,
                                                  '-countValue', src_ip_cnt, '-startValue', src_ip, '-stepValue', src_ip_step, '-valueType', 'increment',
                                                 '-optionalEnabled', True)

                elif ip_type == "ipv6":
                    helpers.log('Adding src_ip and dst_ip ..')
                    helpers.log("Ipv4 id : ipv6-%s" % ip_layer_id)
                    if dst_ip_cnt == 1:
                        helpers.log("Adding SRC_IP: %s WITH Count: 1.." % src_ip)
                        self._handle.setMultiAttribute(trafficStream1 + '/highLevelStream:2/stack:"ipv6-%s"/field:"ipv6.header.srcIP-7"' % ip_layer_id,
                                                  '-countValue', 1, '-fieldValue', dst_ip, '-singleValue', dst_ip,
                                                 '-optionalEnabled', 'true', '-auto', 'false')
                    else:
                        helpers.log("Adding SRC_IP:%s  WITH Count: %s and step: %s" % (dst_ip, str(dst_ip_cnt), str(dst_ip_step)))
                        self._handle.setMultiAttribute(trafficStream1 + '/highLevelStream:2/stack:"ipv6-%s"/field:"ipv6.header.srcIP-7"' % ip_layer_id,
                                                  '-countValue', dst_ip_cnt, '-startValue', dst_ip, '-stepValue', dst_ip_step, '-valueType', 'increment',
                                                 '-optionalEnabled', True)
                    if src_ip_cnt == 1:
                        helpers.log("Adding DST_IP %s WITH Count: 1.." % src_ip)
                        self._handle.setMultiAttribute(trafficStream1 + '/highLevelStream:2/stack:"ipv6-%s"/field:"ipv6.header.dstIP-8"' % ip_layer_id,
                                                  '-countValue', 1, '-fieldValue', src_ip, '-singleValue', src_ip,
                                             '-optionalEnabled', 'true', '-auto', 'false')
                    else:
                        helpers.log("Adding DST_IP:%s  WITH Count: %s and step: %s" % (src_ip, str(src_ip_cnt), str(src_ip_step)))
                        self._handle.setMultiAttribute(trafficStream1 + '/highLevelStream:2/stack:"ipv6-%s"/field:"ipv6.header.dstIP-8"' % ip_layer_id,
                                                  '-countValue', src_ip_cnt, '-fieldValue', src_ip, '-stepValue', src_ip_step, '-valueType', 'increment',
                                             '-optionalEnabled', True)
            helpers.log("Commiting IP config in IXIA...")
            self._handle.commit()
            if protocol is not None:
                helpers.log('Adding Protocol Field in IP Header ..')
                if ethertype == '0800':
                    self._handle.setMultiAttribute(trafficStream1 + '/highLevelStream:2/stack:"ipv4-%s"/field:"ipv4.header.protocol-25"' % ip_layer_id,
                                                  '-countValue', 1, '-fieldValue', protocol,
                                                 '-optionalEnabled', 'true', '-auto', 'false')
                elif ethertype == '86dd':
                    self._handle.setMultiAttribute(trafficStream1 + '/highLevelStream:2/stack:"ipv6-%s"/field:"ipv6.header.nextHeader-5"' % ip_layer_id,
                                                  '-countValue', 1, '-fieldValue', protocol,
                                                 '-optionalEnabled', 'true', '-auto', 'false')
                if protocol == 'TCP':
                    helpers.log('Adding Src_port: %s and Dst_Port: %s for Protocl TCP..!!!' % (src_port, dst_port))
                    helpers.log("Adding tcp id : tcp-%s" % str(tcp_layer_id))
                    self._handle.setMultiAttribute(trafficStream1 + '/highLevelStream:2/stack:"tcp-%s"/field:"tcp.header.srcPort-1"' % str(tcp_layer_id),
                                                  '-countValue', 1, '-fieldValue', dst_port, '-singleValue', dst_port,
                                                 '-optionalEnabled', 'true', '-auto', 'false')
                    self._handle.setMultiAttribute(trafficStream1 + '/highLevelStream:2/stack:"tcp-%s"/field:"tcp.header.dstPort-2"' % str(tcp_layer_id),
                                                  '-countValue', 1, '-fieldValue', src_port, '-singleValue', src_port,
                                                 '-optionalEnabled', 'true', '-auto', 'false')
                    if synBit:
                        helpers.log("Adding Sync Bit with TCP header...")
                        self._handle.setMultiAttribute(trafficStream1 + '/highLevelStream:2/stack:"tcp-%s"/field:"tcp.header.controlBits.synBit-14"' % str(tcp_layer_id),
                                                  '-countValue', 1, '-fieldValue', synBit, '-singleValue', synBit,
                                                 '-optionalEnabled', 'true', '-auto', 'false')
                    if urgBit:
                        helpers.log("Adding Urgent Bit with TCP header...")
                        self._handle.setMultiAttribute(trafficStream1 + '/highLevelStream:2/stack:"tcp-%s"/field:"tcp.header.controlBits.urgBit-10"' % str(tcp_layer_id),
                                                  '-countValue', 1, '-fieldValue', urgBit, '-singleValue', urgBit,
                                                 '-optionalEnabled', 'true', '-auto', 'false')
                    if ackBit:
                        helpers.log("Adding ACK Bit with TCP header...")
                        self._handle.setMultiAttribute(trafficStream1 + '/highLevelStream:2/stack:"tcp-%s"/field:"tcp.header.controlBits.ackBit-11"' % str(tcp_layer_id),
                                                  '-countValue', 1, '-fieldValue', ackBit, '-singleValue', ackBit,
                                                 '-optionalEnabled', 'true', '-auto', 'false')
                    if pshBit:
                        helpers.log("Adding PSH Bit with TCP header...")
                        self._handle.setMultiAttribute(trafficStream1 + '/highLevelStream:2/stack:"tcp-%s"/field:"tcp.header.controlBits.pshBit-12"' % str(tcp_layer_id),
                                                  '-countValue', 1, '-fieldValue', pshBit, '-singleValue', pshBit,
                                                 '-optionalEnabled', 'true', '-auto', 'false')
                    if rstBit:
                        helpers.log("Adding RST Bit with TCP header...")
                        self._handle.setMultiAttribute(trafficStream1 + '/highLevelStream:2/stack:"tcp-%s"/field:"tcp.header.controlBits.rstBit-13"' % str(tcp_layer_id),
                                                  '-countValue', 1, '-fieldValue', rstBit, '-singleValue', rstBit,
                                                 '-optionalEnabled', 'true', '-auto', 'false')
                    if finBit:
                        helpers.log("Adding FIN Bit with TCP header...")
                        self._handle.setMultiAttribute(trafficStream1 + '/highLevelStream:2/stack:"tcp-%s"/field:"tcp.header.controlBits.finBit-15"' % str(tcp_layer_id),
                                                  '-countValue', 1, '-fieldValue', finBit, '-singleValue', finBit,
                                                 '-optionalEnabled', 'true', '-auto', 'false')
                if protocol == 'UDP':
                    helpers.log('Adding Src_port: %s and Dst_Port: %s for Protocl UDP..!!!' % (src_port, dst_port))
                    self._handle.setMultiAttribute(trafficStream1 + '/highLevelStream:2/stack:"udp-%s"/field:"udp.header.srcPort-1"' % str(tcp_layer_id),
                                                  '-countValue', 1, '-fieldValue', dst_port, '-singleValue', dst_port,
                                                 '-optionalEnabled', 'true', '-auto', 'false')
                    self._handle.setMultiAttribute(trafficStream1 + '/highLevelStream:2/stack:"udp-%s"/field:"udp.header.dstPort-2"' % str(tcp_layer_id),
                                                  '-countValue', 1, '-fieldValue', src_port, '-singleValue', src_port,
                                                 '-optionalEnabled', 'true', '-auto', 'false')
                if protocol == 'ICMP':
                    helpers.log('Adding Message Type: %s and Code Value: %s for Protocl UDP..!!!' % (icmp_type, icmp_code))
                    self._handle.setMultiAttribute(trafficStream1 + '/highLevelStream:2/stack:"icmpv2-3"/field:"icmpv2.message.messageType-1"',
                                                  '-countValue', 1, '-singleValue', icmp_type,
                                                 '-optionalEnabled', 'true', '-auto', 'false')
                    self._handle.setMultiAttribute(trafficStream1 + '/highLevelStream:2/stack:"icmpv2-3"/field:"icmpv2.message.codeValue-2"',
                                                  '-countValue', 1, '-singleValue', icmp_code,
                                                 '-optionalEnabled', 'true', '-auto', 'false')
                if payload:
                    helpers.log('Setting Payload information provided to Raw Traffic Stream...')
                    self._handle.setMultiAttribute(trafficStream1 + '/highLevelStream:2/framePayload',
                                                  '-type', 'custom', '-customPattern', payload,
                                                 '-customRepeat', False, '-auto', 'false')
        if payload:
            helpers.log('Skiping to enable Flow Tracking....')
        else:
            helpers.log('Setting Flow Tracking ....')
            self._handle.setAttribute(self._handle.getList(trafficStream1, 'tracking')[0], '-trackBy', 'trackingenabled0')

        self._handle.commit()
        return trafficStream1

    def ix_l2_add(self, **kwargs):
        '''
            This Helper Method created L2 related Config on IXIA to start Traffic with given arguments
        '''
        helpers.log("###Starting L2 IXIA ADD Config ...")
        ix_handle = self._handle
        ix_ports = [port for port in self._port_map_list.values()]
        dst_mac = kwargs.get('src_mac', '00:11:23:00:00:01')
        src_mac = kwargs.get('dst_mac', '00:11:23:00:00:02')
        src_cnt = kwargs.get('dst_cnt', 1)
        dst_cnt = kwargs.get('src_cnt', 1)
        src_step = kwargs.get('dst_mac_step', '00:00:00:00:00:01')
        dst_step = kwargs.get('src_mac_step', '00:00:00:00:00:01')
        frame_rate = kwargs.get('frame_rate', 100)
        frame_cnt = kwargs.get('frame_cnt', None)
        self._frame_size = kwargs.get('frame_size', 70)
        frame_type = kwargs.get('frame_type', 'fixed')
        frame_mode = kwargs.get('frame_mode', 'framesPerSecond')
        name = kwargs.get('name', 'gobot_default')
        ethertype = kwargs.get('ethertype', None)
        ethertype_cnt = kwargs.get('ethertype_cnt', 1)
        ethertype_step = kwargs.get('ethertype_step', None)
        vlan_id = kwargs.get('vlan_id', None)
        line_rate = kwargs.get('line_rate', None)
        burst_count = kwargs.get('burst_count', None)
        burst_gap = kwargs.get('burst_gap', None)
        if vlan_id is not None:
            ethertype = '8100'
        crc = kwargs.get('crc', None)
        no_arp = kwargs.get('no_arp', True)
        vlan_cnt = kwargs.get('vlan_cnt', 1)
        vlan_step = kwargs.get('vlan_step', 1)

        ix_tcl_server = self._tcl_server_ip
        flow = kwargs.get('flow', 'None')
        if ix_tcl_server is None or ix_ports is None or src_mac is None or dst_mac is None:
            helpers.warn('Please Provide Required Args for IXIA_L2_ADD helper method !!')
            raise IxNetwork.IxNetError('Please provide Required Args for IXIA_L2_ADD helper method !!')
        get_version = ix_handle.getVersion()
        helpers.log("###Current Version of Ixia Chassis : %s " % get_version)
        ix_handle.setDebug(False)  # Set Debug True to print Ixia Server Interactions
        # Create vports:
        if len(self._vports) == 0:
            vports = self.ix_create_vports()
            helpers.log('### vports Created : %s' % vports)
            # Map to Chassis Physhical Ports:
            if self.ix_map_vports_pyhsical_ports():
                helpers.log('### Successfully mapped vport to physical ixia ports..')
            else:
                helpers.warn('Unable to connect to Ixia Chassis')
                return False
        else:
            helpers.log('### vports already Created : %s' % self._vports)

        if len(self._topology) == 0:
            # Create Topo:
            self.ix_create_topo()
            helpers.log('### Topology Created: %s' % self._topology)
        else:
            helpers.log('###Topology already created: %s' % self._topology)
        create_topo = []
        match_uni1 = re.match(r'(\w+)->(\w+)', flow)
        match_uni2 = re.match(r'(\w+)<-(\w+)', flow)
        match_bi = re.match(r'(\w+)<->(\w+)', flow)
        stream_flow = ''
        is_bigtap = kwargs.get('bigtap', False)
        if match_uni1:
            source = match_uni1.group(1).lower()
            destination = match_uni1.group(2).lower()
            stream_flow = 'uni-directional'
            if is_bigtap:
                create_topo.append(self._topology['a'])  # # FIX Need to dynamical get from TOPO file
                create_topo.append(self._topology['b'])
                bigtap_ports = kwargs['bigtap_ports']
                helpers.log('Changing src and dst macs as BigTap is True for bigtap Ports:...')
                helpers.log(str(bigtap_ports))
                ixia_macs = IxBigtapLib.create_mac_list(bigtap_ports[source]['name'], 5, False)
                dst_mac = ixia_macs['start_mac']
                dst_cnt = ixia_macs['count']
                dst_step = ixia_macs['mac_step']
                ixia_macs = IxBigtapLib.create_mac_list(bigtap_ports[destination]['name'], 5, False)
                src_mac = ixia_macs['start_mac']
                src_cnt = ixia_macs['count']
                src_step = ixia_macs['mac_step']
            else:
                create_topo.append(self._topology[source])
                create_topo.append(self._topology[destination])

        elif match_uni2:
            source = match_uni2.group(2).lower()
            destination = match_uni2.group(1).lower()
            stream_flow = 'uni-directional'
            if is_bigtap:
                create_topo.append(self._topology['a'])
                create_topo.append(self._topology['b'])
                helpers.log('Changing src and dst macs as BigTap is True for bigtap Ports:...')
                helpers.log(str(bigtap_ports))
                bigtap_ports = kwargs['bigtap_ports']
                ixia_macs = IxBigtapLib.create_mac_list(bigtap_ports[source]['name'], 5, False)
                src_mac = ixia_macs['start_mac']
                src_cnt = ixia_macs['count']
                src_step = ixia_macs['mac_step']
                ixia_macs = IxBigtapLib.create_mac_list(bigtap_ports[destination]['name'], 5, False)
                dst_mac = ixia_macs['start_mac']
                dst_cnt = ixia_macs['count']
                dst_step = ixia_macs['mac_step']
            else:
                create_topo.append(self._topology[source])
                create_topo.append(self._topology[destination])
        elif match_bi:
            source = match_bi.group(1).lower()
            destination = match_bi.group(2).lower()
            stream_flow = 'bi-directional'
            if is_bigtap:
                create_topo.append(self._topology['a'])
                create_topo.append(self._topology['b'])
                bigtap_ports = kwargs['bigtap_ports']
                helpers.log('Changing src and dst macs as BigTap is True for bigtap Ports:...')
                helpers.log(str(bigtap_ports))
                ixia_macs = IxBigtapLib.create_mac_list(bigtap_ports[source]['name'], 5, False)
                src_mac = ixia_macs['start_mac']
                src_cnt = ixia_macs['count']
                src_step = ixia_macs['mac_step']
                ixia_macs = IxBigtapLib.create_mac_list(bigtap_ports[destination]['name'], 5, False)
                dst_mac = ixia_macs['start_mac']
                dst_cnt = ixia_macs['count']
                dst_step = ixia_macs['mac_step']
            else:
                create_topo.append(self._topology[source])
                create_topo.append(self._topology[destination])
        # Create Ether Device:
        mac_devices = self.ix_create_device_ethernet(create_topo, src_cnt, dst_cnt, src_mac, dst_mac, src_step, dst_step)
        helpers.log('### Created Mac Devices with corrsponding Topos ...')
        # Create Traffic Stream:
        traffic_stream = self.ix_setup_traffic_streams_ethernet(mac_devices[0], mac_devices[1],
                                                       frame_type, self._frame_size, frame_rate, frame_mode,
                                                       frame_cnt, stream_flow, name,
                                                       ethertype=ethertype, ethertype_cnt=ethertype_cnt, ethertype_step=ethertype_step,
                                                       vlan_id=vlan_id, vlan_cnt=vlan_cnt, vlan_step=vlan_step,
                                                       burst_count=burst_count, burst_gap=burst_gap,
                                                       crc=crc, no_arp=no_arp, line_rate=line_rate)
        helpers.log('Created Traffic Stream : %s' % traffic_stream)
        self._traffic_stream[name] = traffic_stream
        helpers.log('Applying Traffic config..')
        self._handle.execute('apply', self._handle.getRoot() + 'traffic')
        helpers.log('Succesfully Applied traffic Config ..')
        self._traffi_apply = True  # Setting it False to Apply Changes while starting traffic
        return traffic_stream

    def ix_l3_add_hosts(self, **kwargs):
        '''
            This methods adds ixia_l3 hosts and returns ip_Devices
        '''
        ix_handle = self._handle
        ix_ports = [port for port in self._port_map_list.values()]
        src_mac = kwargs.get('src_mac', '00:11:23:00:00:01')
        dst_mac = kwargs.get('dst_mac', '00:11:23:00:00:02')
        dst_mac_step = kwargs.get('dst_mac_step', '00:00:00:00:00:01')
        src_mac_step = kwargs.get('src_mac_step', '00:00:00:00:00:01')
        d_cnt = kwargs.get('d_cnt', 1)
        s_cnt = kwargs.get('s_cnt', 1)
        ip_type = 'ipv4'

        src_ip = kwargs.get('src_ip', '20.0.0.1')
        src_ip_step = kwargs.get('src_ip_step', '0.0.0.1')
        src_gw_ip = kwargs.get('gw_ip', '20.0.0.2')
        src_gw_step = kwargs.get('src_gw_step', '0.0.1.0')

        dst_ip = kwargs.get('dst_ip', '20.0.0.2')
        dst_gw_ip = kwargs.get('dst_gw', '20.0.0.1')
        dst_gw_step = kwargs.get('src_gw_step', '0.0.1.0')
        dst_ip_step = kwargs.get('dst_ip_step', '0.0.0.1')
        vlan_id = kwargs.get("vlan_id", None)
        vlan_step = kwargs.get("vlan_step", None)
        vlan_p = kwargs.get("vlan_priority", 0)
        vlan_p_step = kwargs.get("vlan_priority_step", 0)

        port_name = kwargs.get('port_name', None)
        ix_tcl_server = self._tcl_server_ip

        if ix_tcl_server is None or ix_ports is None:
            helpers.warn('Please Provide Required Args for IXIA_L2_ADD helper method !!')
            raise IxNetwork.IxNetError('Please provide Required Args for IXIA_L2_ADD helper method !!')
        get_version = ix_handle.getVersion()

        helpers.log("Current Version of Ixia Chassis : %s " % get_version)
        ix_handle.setDebug(False)  # Set Debug True to print Ixia Server Interactions

        # Create vports:
        if len(self._vports) == 0:
            vports = self.ix_create_vports()
            helpers.log('vports Created : %s' % vports)
            # Map to Chassis Physhical Ports:
            if self.ix_map_vports_pyhsical_ports():
                helpers.log('Successfully mapped vport to physical ixia ports..')
            else:
                helpers.log('Unable to connect to Ixia Chassis')
                return False
        else:
            helpers.log('vports already Created : %s' % self._vports)

        if len(self._topology) == 0:
            # Create Topo:
            self.ix_create_topo()
            helpers.log('Topology Created: %s' % self._topology)
        else:
            helpers.log('Topology already created: %s' % self._topology)
        if port_name is None:
            helpers.warn('Please Provide Ixia Port on which to create IP Host !!')
            raise IxNetwork.IxNetError('Please Provide Ixia Port on which to create IP Host !!')
        else:
            # Create Ether Device with IpDevices:
            create_topo = [self._topology[port_name]]

            (ip_devices, mac_devices) = self.ix_create_device_ethernet_ip(create_topo, s_cnt, d_cnt, src_mac, dst_mac, src_mac_step,
                                                                      dst_mac_step, src_ip, dst_ip, src_gw_ip, dst_gw_ip, src_ip_step,
                                                                      dst_ip_step, src_gw_step, dst_gw_step, ip_type=ip_type,
                                                                      vlan_p=vlan_p, vlan_p_step=vlan_p_step, vlan_id=vlan_id, vlan_step=vlan_step)
            helpers.log('Created Mac Devices with corrsponding Topos ...')
            helpers.log ("Success Creating Ip Devices !!!")
            return ip_devices

    def ix_raw_add(self, **kwargs):
        '''
            Helper function to create similar to IxNetwork Quick Streams
            As per user requests this method needs to be enchanced with Options Available in IxNetwork
        '''
        ix_handle = self._handle
        ix_ports = [port for port in self._port_map_list.values()]
        ix_tcl_server = self._tcl_server_ip
        flow = kwargs.get('flow', None)
        frame_rate = kwargs.get('frame_rate', 100)
        frame_cnt = kwargs.get('frame_cnt', None)
        frame_type = kwargs.get('frame_type', 'fixed')
        frame_mode = kwargs.get('frame_mode', 'framesPerSecond')
        self._frame_size = kwargs.get('frame_size', 128)
        name = kwargs.get('name', 'gobot_default')

        lacp = kwargs.get('lacp', False)
        lldp = kwargs.get('lldp', False)
        src_mac = kwargs.get('src_mac', None)
        dst_mac = kwargs.get('dst_mac', None)
        d_cnt = kwargs.get('dst_mac_cnt', None)
        s_cnt = kwargs.get('src_mac_cnt', None)
        dst_mac_step = kwargs.get('dst_mac_step', '00:00:00:00:00:01')
        src_mac_step = kwargs.get('src_mac_step', '00:00:00:00:00:01')
        lld_tlv_chassis_id = kwargs.get("lld_tlv_chassisid", None)
        lacp_src_mac = None
        ethertype = kwargs.get('ethertype', None)
        vlan_id = kwargs.get('vlan_id', None)
        vlan_cnt = kwargs.get('vlan_cnt', 1)
        vlan_step = kwargs.get('vlan_step', 1)
        vlan_priority = kwargs.get('vlan_priority', None)
        line_rate = kwargs.get('line_rate', None)
        protocol = kwargs.get('protocol', None)
        burst_cnt = kwargs.get('burst_count', None)
        burst_gap = kwargs.get('burst_gap', None)
        payload = kwargs.get('payload', None)
        urgBit = kwargs.get('urgBit', False)
        ackBit = kwargs.get('ackBit', False)
        pshBit = kwargs.get('pshBit', False)
        rstBit = kwargs.get('rstBit', False)
        finBit = kwargs.get('finBit', False)
        synBit = kwargs.get('synBit', False)
        crc = kwargs.get('crc', None)
        src_port = kwargs.get('src_port', '6001')
        dst_port = kwargs.get('dst_port', '7001')
        icmp_type = kwargs.get('icmp_type', '0')
        icmp_code = kwargs.get('icmp_code', '0')
        mpls_label = kwargs.get("mpls_label", None)

        ip_type = 'ipv4'
        if str(ethertype).lower() == '86dd':
            src_ip = kwargs.get('src_ip', None)
            dst_ip = kwargs.get('dst_ip', None)
            src_ip_step = kwargs.get('src_ip_step', '0:0:0:0:0:0:1:0')
            dst_ip_step = kwargs.get('dst_ip_step', '0:0:0:0:0:0:1:0')
            ip_type = 'ipv6'
            self._frame_size = kwargs.get('frame_size', 140)
            protocol = kwargs.get('protocol', None)
        else:
            src_ip = kwargs.get('src_ip', None)
            dst_ip = kwargs.get('dst_ip', None)
            src_ip_step = kwargs.get('src_ip_step', '0.0.0.1')
            dst_ip_step = kwargs.get('dst_ip_step', '0.0.0.1')
            self._frame_size = kwargs.get('frame_size', 130)
            protocol = kwargs.get('protocol', None)
            src_ip_cnt = kwargs.get("src_ip_cnt", 1)
            dst_ip_cnt = kwargs.get("dst_ip_cnt", 1)


        if lacp:
            helpers.log("Getting LCAP Parameters..")
            lacp_src_mac = kwargs.get('lacp_src_mac', '00:00:99:99:88:77')
            s_cnt = kwargs.get('src_cnt', 1)
            src_mac_step = kwargs.get('src_mac_step', '00:00:00:00:00:01')

        if lldp:
            helpers.log("Getting LLDP Parameters..")
            src_mac = kwargs.get('src_mac', '00:11:23:00:00:01')
            dst_mac = kwargs.get('dst_mac', '00:11:23:00:00:02')
            lld_tlv_chassis_id = kwargs.get("lld_tlv_chassisid", 1)

        if ix_tcl_server is None or ix_ports is None :
            helpers.warn('Please Provide Required Args for IXIA_L3_ADD helper method !!')
            raise IxNetwork.IxNetError('Please provide Required Args for IXIA_L3_ADD helper method !!')
        get_version = ix_handle.getVersion()

        self._traffi_apply = False
        traffic_stream1 = []

        helpers.log("###Current Version of Ixia Chassis : %s " % get_version)
        ix_handle.setDebug(False)  # Set Debug True to print Ixia Server Interactions
        # Create vports:
        if len(self._vports) == 0:
            vports = self.ix_create_vports()
            helpers.log('### vports Created : %s' % vports)
            if self.ix_map_vports_pyhsical_ports():
                helpers.log('### Successfully mapped vport to physical ixia ports..')
            else:
                helpers.log('Unable to connect to Ixia Chassis')
                return False
        else:
            helpers.log('### vports already Created : %s' % self._vports)


        helpers.log("Need to create Ixia Quick Flows similar to Raw Streams..")
        helpers.log("No Hosts are created and No gw arps are resolved, Hence correct dst_mac should be provided for L3 traffic to work..")

        helpers.log("Skipping Creating Topologies ...")
        match_uni1 = re.match(r'(\w+)->(\w+)', flow)
        match_uni2 = re.match(r'(\w+)<-(\w+)', flow)
        match_bi = re.match(r'(\w+)<->(\w+)', flow)

        stream_flow = ''
        src_ix_port = ''
        dst_ix_port = ''

        if match_uni1:
            stream_flow = 'uni-directional'
            src_ix_port = match_uni1.group(1).lower()
            dst_ix_port = match_uni1.group(2).lower()
        elif match_uni2:
            stream_flow = 'uni-directional'
            src_ix_port = match_uni2.group(2).lower()
            dst_ix_port = match_uni2.group(1).lower()
        elif match_bi:
            stream_flow = 'bi-directional'
            src_ix_port = match_bi.group(1).lower()
            dst_ix_port = match_bi.group(2).lower()

        helpers.log("src ixia port used :%s dst ixia port used :%s" % (src_ix_port, dst_ix_port))
        src_vport = self._handle.getFilteredList(self._handle.getRoot(), 'vport', '-name', src_ix_port)[0]
        dst_vport = self._handle.getFilteredList(self._handle.getRoot(), 'vport', '-name', dst_ix_port)[0]
        if vlan_priority is None:
            traffic_item = self.ix_setup_traffic_streams_raw(frame_type, self._frame_size, frame_rate, frame_mode, frame_cnt, stream_flow, name,
                                                             mpls_label=mpls_label,
                                                        lacp_src_mac=lacp_src_mac, src_mac=src_mac, lld_tlv_chassis_id=lld_tlv_chassis_id, burst_cnt=burst_cnt, burst_gap=burst_gap, crc=crc,
                                                        dst_mac=dst_mac, dst_cnt=d_cnt, src_cnt=s_cnt, src_mac_step=src_mac_step, dst_mac_step=dst_mac_step,
                                                        src_vport=src_vport, dst_vport=dst_vport, protocol=protocol, src_ip=src_ip, dst_ip=dst_ip, src_ip_cnt=src_ip_cnt, dst_ip_cnt=dst_ip_cnt,
                                                        icmp_type=icmp_type, icmp_code=icmp_code, src_ip_step=src_ip_step, dst_ip_step=dst_ip_step,
                                                        ethertype=ethertype, ip_type=ip_type, line_rate=line_rate, payload=payload,
                                                        vlan_id=vlan_id, vlan_cnt=vlan_cnt, vlan_step=vlan_step,
                                                        hex_src_mac=src_mac, hex_dst_mac=dst_mac, src_port=src_port, dst_port=dst_port,
                                                        synBit=synBit, urgBit=urgBit, ackBit=ackBit, pshBit=pshBit, rstBit=rstBit, finBit=finBit)
        else:
            traffic_item = self.ix_setup_traffic_streams_raw(frame_type, self._frame_size, frame_rate, frame_mode, frame_cnt, stream_flow, name,
                                                             mpls_label=mpls_label,
                                                        lacp_src_mac=lacp_src_mac, src_mac=src_mac, lld_tlv_chassis_id=lld_tlv_chassis_id, burst_cnt=burst_cnt, burst_gap=burst_gap, crc=crc,
                                                        dst_mac=dst_mac, dst_cnt=d_cnt, src_cnt=s_cnt, src_mac_step=src_mac_step, dst_mac_step=dst_mac_step,
                                                        src_vport=src_vport, dst_vport=dst_vport, protocol=protocol, src_ip=src_ip, dst_ip=dst_ip, src_ip_cnt=src_ip_cnt, dst_ip_cnt=dst_ip_cnt,
                                                        icmp_type=icmp_type, icmp_code=icmp_code, src_ip_step=src_ip_step, dst_ip_step=dst_ip_step,
                                                        ethertype=ethertype, ip_type=ip_type, line_rate=line_rate, payload=payload,
                                                        vlan_id=vlan_id, vlan_cnt=vlan_cnt, vlan_step=vlan_step, vlan_priority=vlan_priority,
                                                        hex_src_mac=src_mac, hex_dst_mac=dst_mac, src_port=src_port, dst_port=dst_port,
                                                        synBit=synBit, urgBit=urgBit, ackBit=ackBit, pshBit=pshBit, rstBit=rstBit, finBit=finBit)

        traffic_stream1.append(traffic_item)
        self.ix_apply_traffic()
        return traffic_stream1[0]

    def ix_l3_add(self, **kwargs):
        ix_handle = self._handle
        ix_ports = [port for port in self._port_map_list.values()]
        src_mac = kwargs.get('src_mac', '00:11:23:00:00:01')
        dst_mac = kwargs.get('dst_mac', '00:11:23:00:00:02')
        d_cnt = kwargs.get('dst_cnt', 1)
        s_cnt = kwargs.get('src_cnt', 1)
        dst_mac_step = kwargs.get('dst_mac_step', '00:00:00:00:00:01')
        src_mac_step = kwargs.get('src_mac_step', '00:00:00:00:00:01')
        frame_rate = kwargs.get('frame_rate', 100)
        frame_cnt = kwargs.get('frame_cnt', None)
        frame_type = kwargs.get('frame_type', 'fixed')
        frame_mode = kwargs.get('frame_mode', 'framesPerSecond')
        self._frame_size = kwargs.get('frame_size', 128)
        name = kwargs.get('name', 'gobot_default')
        ethertype = kwargs.get('ethertype', '0800')
        ethertype_cnt = kwargs.get('ethertype_cnt', 1)
        ethertype_step = kwargs.get('ethertype_step', None)
        vlan_id = kwargs.get('vlan_id', None)
        vlan_cnt = kwargs.get('vlan_cnt', 1)
        vlan_step = kwargs.get('vlan_step', 1)
        vlan_priority = kwargs.get('vlan_priority', None)
        line_rate = kwargs.get('line_rate', None)
        protocol = kwargs.get('protocol', None)
        burst_count = kwargs.get('burst_count', None)
        burst_gap = kwargs.get('burst_gap', None)
        payload = kwargs.get('payload', None)
        urgBit = kwargs.get('urgBit', False)
        ackBit = kwargs.get('ackBit', False)
        pshBit = kwargs.get('pshBit', False)
        rstBit = kwargs.get('rstBit', False)
        finBit = kwargs.get('finBit', False)
        synBit = kwargs.get('synBit', False)
        src_gw_prefix = kwargs.get('src_gw_prefix', None)
        dst_gw_prefix = kwargs.get('dst_gw_prefix', None)
        crc = kwargs.get('crc', None)
        ip_type = 'ipv4'
#         if vlan_id is not None:
#             ethertype = '8100'
#             protocol = kwargs.get('protocol', 'UDP')
        if vlan_cnt > 1:
            helpers.log("Adding src_cnt and dst_cnt as vln_cnt is given to increment devices..")
            s_cnt = vlan_cnt
            d_cnt = vlan_cnt

        if ethertype.lower() == '86dd':
            src_ip = kwargs.get('src_ip', '2001:0:0:0:0:0:0:c4')
            dst_ip = kwargs.get('dst_ip', '2001:0:0:0:0:0:0:c5')
            src_gw_ip = kwargs.get('src_gw', '2001:0:0:0:0:0:0:c5')
            src_gw_step = kwargs.get('src_gw_step', '2001:0:0:0:0:0:0:1')
            dst_gw_ip = kwargs.get('dst_gw', '2001:0:0:0:0:0:0:c4')
            dst_gw_step = kwargs.get('dst_gw_step', '2001:0:0:0:0:0:0:1')
            src_ip_step = kwargs.get('src_ip_step', '0:0:0:0:0:0:1:0')
            dst_ip_step = kwargs.get('dst_ip_step', '0:0:0:0:0:0:1:0')
            ip_type = 'ipv6'
            self._frame_size = kwargs.get('frame_size', 140)
            protocol = kwargs.get('protocol', None)
        else:
            src_ip = kwargs.get('src_ip', '20.0.0.1')
            dst_ip = kwargs.get('dst_ip', '20.0.0.2')
            src_gw_ip = kwargs.get('src_gw', '20.0.0.2')
            src_gw_step = kwargs.get('src_gw_step', '0.0.1.0')
            dst_gw_ip = kwargs.get('dst_gw', '20.0.0.1')
            dst_gw_step = kwargs.get('src_gw_step', '0.0.1.0')
            src_ip_step = kwargs.get('src_ip_step', '0.0.0.1')
            dst_ip_step = kwargs.get('dst_ip_step', '0.0.0.1')
            self._frame_size = kwargs.get('frame_size', 130)
            protocol = kwargs.get('protocol', None)

        no_arp = kwargs.get('no_arp', False)

        src_port = kwargs.get('src_port', '6001')
        dst_port = kwargs.get('dst_port', '7001')
        icmp_type = kwargs.get('icmp_type', '0')
        icmp_code = kwargs.get('icmp_code', '0')

        ix_tcl_server = self._tcl_server_ip
        flow = kwargs.get('flow', None)

        if ix_tcl_server is None or ix_ports is None or src_ip is None or dst_ip is None:
            helpers.warn('Please Provide Required Args for IXIA_L3_ADD helper method !!')
            raise IxNetwork.IxNetError('Please provide Required Args for IXIA_L3_ADD helper method !!')
        get_version = ix_handle.getVersion()

        helpers.log("###Current Version of Ixia Chassis : %s " % get_version)
        ix_handle.setDebug(False)  # Set Debug True to print Ixia Server Interactions

        # Create vports:
        if len(self._vports) == 0:
            vports = self.ix_create_vports()
            helpers.log('### vports Created : %s' % vports)
            if self.ix_map_vports_pyhsical_ports():
                helpers.log('### Successfully mapped vport to physical ixia ports..')
            else:
                helpers.log('Unable to connect to Ixia Chassis')
                return False
        else:
            helpers.log('### vports already Created : %s' % self._vports)

        if payload:
            helpers.log("Skipping Creating Topologies ...")
            match_uni1 = re.match(r'(\w+)->(\w+)', flow)
            match_uni2 = re.match(r'(\w+)<-(\w+)', flow)
            match_bi = re.match(r'(\w+)<->(\w+)', flow)

            stream_flow = ''
            src_ix_port = ''
            dst_ix_port = ''

            if match_uni1:
                stream_flow = 'uni-directional'
                src_ix_port = match_uni1.group(1).lower()
                dst_ix_port = match_uni1.group(2).lower()
            elif match_uni2:
                stream_flow = 'uni-directional'
                src_ix_port = match_uni2.group(2).lower()
                dst_ix_port = match_uni2.group(1).lower()
            elif match_bi:
                stream_flow = 'bi-directional'
                src_ix_port = match_bi.group(1).lower()
                dst_ix_port = match_bi.group(2).lower()
        else:
            if len(self._topology) == 0:
                # Create Topo:
                self.ix_create_topo()
                helpers.log('### Topology Created: %s' % self._topology)
            else:
                helpers.log('###Topology already created: %s' % self._topology)
            create_topo = []
            match_uni1 = re.match(r'(\w+)->(\w+)', flow)
            match_uni2 = re.match(r'(\w+)<-(\w+)', flow)
            match_bi = re.match(r'(\w+)<->(\w+)', flow)

            stream_flow = ''
            src_ix_port = ''
            dst_ix_port = ''

            if match_uni1:
                create_topo.append(self._topology[match_uni1.group(1).lower()])
                create_topo.append(self._topology[match_uni1.group(2).lower()])
                stream_flow = 'uni-directional'
                src_ix_port = match_uni1.group(1).lower()
                dst_ix_port = match_uni1.group(2).lower()
            elif match_uni2:
                create_topo.append(self._topology[match_uni2.group(2).lower()])
                create_topo.append(self._topology[match_uni2.group(1).lower()])
                stream_flow = 'uni-directional'
                src_ix_port = match_uni2.group(2).lower()
                dst_ix_port = match_uni2.group(1).lower()
            elif match_bi:
                create_topo.append(self._topology[match_bi.group(1).lower()])
                create_topo.append(self._topology[match_bi.group(2).lower()])
                stream_flow = 'bi-directional'
                src_ix_port = match_bi.group(1).lower()
                dst_ix_port = match_bi.group(2).lower()

        # Create Ether Device with IpDevices:
        # Start the Hosts to resolve Arps of GW
        # Create Traffic item with flows:
        self._traffi_apply = False
        traffic_stream1 = []
        if payload is None:
            for topo in self._topology:
                self.ix_stop_hosts(topo)
                helpers.log('Successfuly Stopped Hosts on Topology : %s ' % topo)
            helpers.log('Sleeps 3 sec for Hosts to be Stopped')
            time.sleep(3)
            if no_arp == 'True':
                helpers.log('Adding Stream with Ethernet devices as no_arp is True!!!')
                self._arp_check = False
                (ip_devices, mac_devices) = self.ix_create_device_ethernet_ip(create_topo, s_cnt, d_cnt, src_mac, dst_mac, src_mac_step,
                                                                              dst_mac_step, src_ip, dst_ip, src_gw_ip, dst_gw_ip, src_ip_step,
                                                                              dst_ip_step, src_gw_step, dst_gw_step, dst_mac, src_mac, ip_type=ip_type,
                                                                              vlan_id=vlan_id, vlan_step=vlan_step, src_gw_prefix=src_gw_prefix, dst_gw_prefix=dst_gw_prefix, vlan_p=vlan_priority)
                helpers.log('Created Mac Devices : %s ' % mac_devices)
                if vlan_priority is None:
                    traffic_stream = self.ix_setup_traffic_streams_ethernet(mac_devices[0], mac_devices[1],
                                                               frame_type, self._frame_size, frame_rate, frame_mode,
                                                               frame_cnt, stream_flow, name, crc=crc, vlan_id=vlan_id,
                                                               src_ip=src_ip, src_ip_step=src_ip_step, src_ip_cnt=s_cnt,
                                                               dst_ip=dst_ip, dst_ip_step=dst_ip_step, dst_ip_cnt=d_cnt,
                                                               protocol=protocol, icmp_type=icmp_type, icmp_code=icmp_code, vlan_cnt=vlan_cnt, vlan_step=vlan_step,
                                                               burst_count=burst_count, burst_gap=burst_gap,
                                                               src_port=src_port, dst_port=dst_port, no_arp=no_arp,
                                                               ethertype=ethertype, ethertype_cnt=ethertype_cnt, ethertype_step=ethertype_step,
                                                               ip_type=ip_type, line_rate=line_rate,
                                                               synBit=synBit, urgBit=urgBit, ackBit=ackBit, pshBit=pshBit, rstBit=rstBit, finBit=finBit)
                else:
                    traffic_stream = self.ix_setup_traffic_streams_ethernet(mac_devices[0], mac_devices[1],
                                                               frame_type, self._frame_size, frame_rate, frame_mode,
                                                               frame_cnt, stream_flow, name, crc=crc,
                                                               src_ip=src_ip, src_ip_step=src_ip_step, src_ip_cnt=s_cnt,
                                                               dst_ip=dst_ip, dst_ip_step=dst_ip_step, dst_ip_cnt=d_cnt,
                                                               protocol=protocol, icmp_type=icmp_type, icmp_code=icmp_code, vlan_cnt=vlan_cnt, vlan_step=vlan_step,
                                                               burst_count=burst_count, burst_gap=burst_gap,
                                                               src_port=src_port, dst_port=dst_port, no_arp=no_arp,
                                                               ethertype=ethertype, ethertype_cnt=ethertype_cnt, ethertype_step=ethertype_step,
                                                               ip_type=ip_type, line_rate=line_rate,
                                                               synBit=synBit, urgBit=urgBit, ackBit=ackBit, pshBit=pshBit, rstBit=rstBit, finBit=finBit)

                traffic_stream1.append(traffic_stream)
            else:
                helpers.log('Adding L3 Stream with ARP resolution for configured Gateway')
                self._arp_check = True
                (ip_devices, mac_devices) = self.ix_create_device_ethernet_ip(create_topo, s_cnt, d_cnt, src_mac, dst_mac, src_mac_step,
                                                                              dst_mac_step, src_ip, dst_ip, src_gw_ip, dst_gw_ip, src_ip_step,
                                                                              dst_ip_step, src_gw_step, dst_gw_step, ip_type=ip_type, vlan_id=vlan_id,
                                                                              src_gw_prefix=src_gw_prefix, dst_gw_prefix=dst_gw_prefix, vlan_p=vlan_priority)
                self.ix_start_hosts(ip_type=ip_type)
                self._started_hosts = True
                helpers.log("IP Devices: %s" % ip_devices)
                if vlan_priority is None:
                    traffic_item = self.ix_setup_traffic_streams_ethernet(ip_devices[0], ip_devices[1], frame_type, self._frame_size, frame_rate, frame_mode,
                                                             frame_cnt, stream_flow, name, crc=crc, vlan_id=vlan_id, src_ip=src_ip, dst_ip=dst_ip,
                                                             vlan_cnt=vlan_cnt, vlan_step=vlan_step,
                                                             burst_count=burst_count, burst_gap=burst_gap,
                                                             protocol=protocol, icmp_type=icmp_type, icmp_code=icmp_code,
                                                             src_port=src_port, dst_port=dst_port,
                                                             ethertype=ethertype, ethertype_cnt=ethertype_cnt, ethertype_step=ethertype_step,
                                                             ip_type=ip_type, line_rate=line_rate,
                                                             synBit=synBit, urgBit=urgBit, ackBit=ackBit, pshBit=pshBit, rstBit=rstBit, finBit=finBit)
                else:
                    traffic_item = self.ix_setup_traffic_streams_ethernet(ip_devices[0], ip_devices[1], frame_type, self._frame_size, frame_rate, frame_mode,
                                                             frame_cnt, stream_flow, name, crc=crc, vlan_id=vlan_id, src_ip=src_ip, dst_ip=dst_ip,
                                                             vlan_cnt=vlan_cnt, vlan_step=vlan_step,
                                                             burst_count=burst_count, burst_gap=burst_gap,
                                                             protocol=protocol, icmp_type=icmp_type, icmp_code=icmp_code,
                                                             src_port=src_port, dst_port=dst_port,
                                                             ethertype=ethertype, ethertype_cnt=ethertype_cnt, ethertype_step=ethertype_step,
                                                             ip_type=ip_type, line_rate=line_rate,
                                                             synBit=synBit, urgBit=urgBit, ackBit=ackBit, pshBit=pshBit, rstBit=rstBit, finBit=finBit)

                traffic_stream1.append(traffic_item)

            helpers.log('### Created Traffic Stream with Ip Devices ...')
            helpers.log ("Success Creating Ip Traffic Stream!!!")
            self._handle.execute('apply', self._handle.getRoot() + 'traffic')
            helpers.log('Succesfully Applied traffic Config ..')
            self._traffi_apply = True  # Setting it True to Not Apply Changes while starting traffic
        else:
            helpers.log("Payload is provided Need to create Ixia Quick Flows similar to Raw Streams..")
            helpers.log("No Hosts are created and No gw arps are resolved, Hence correct dst_mac should be provided for L3 traffic to work..")
            helpers.log("src ixia port used :%s dst ixia port used :%s" % (src_ix_port, dst_ix_port))
            src_vport = self._handle.getFilteredList(self._handle.getRoot(), 'vport', '-name', src_ix_port)[0]
            dst_vport = self._handle.getFilteredList(self._handle.getRoot(), 'vport', '-name', dst_ix_port)[0]
            traffic_item = self.ix_setup_traffic_streams_ethernet(None, None, frame_type, self._frame_size, frame_rate, frame_mode,
                                                             frame_cnt, stream_flow, name, vlan_id=vlan_id, crc=crc, vlan_cnt=vlan_cnt, vlan_step=vlan_step,
                                                             burst_count=burst_count, burst_gap=burst_gap,
                                                             protocol=protocol, src_ip=src_ip, dst_ip=dst_ip, icmp_type=icmp_type, icmp_code=icmp_code,
                                                             src_port=src_port, dst_port=dst_port,
                                                             ethertype=ethertype, ethertype_cnt=ethertype_cnt, ethertype_step=ethertype_step,
                                                             ip_type=ip_type, line_rate=line_rate,
                                                             payload=payload, src_vport=src_vport, dst_vport=dst_vport,
                                                             hex_src_mac=src_mac, hex_dst_mac=dst_mac,
                                                             synBit=synBit, urgBit=urgBit, ackBit=ackBit, pshBit=pshBit, rstBit=rstBit, finBit=finBit)
            traffic_stream1.append(traffic_item)
        return traffic_stream1[0]
    def ix_apply_traffic(self, **kwargs):
        helpers.log("First Checking IXIA vPort States whether Released or not..")
        self.ix_check_vport_state()
        ixia_traffic_state = self._handle.getAttribute(self._handle.getRoot() + 'traffic', '-state')
        if str(ixia_traffic_state) == 'started':
            helpers.log("Traffic is Still Running , Stopping the Traffic before applying traffic item..")
            self.ix_stop_traffic()
        helpers.log("Enabling Packet Loss Duration..")
        self._handle.setAttribute(self._handle.getRoot() + '/traffic/statistics/packetLossDuration', '-enabled', True)
        self._handle.commit()
        helpers.log("Applying Traffic as Requested ....")
        helpers.sleep(10)
        self._handle.execute('apply', self._handle.getRoot() + 'traffic')
        helpers.log('###Applied traffic Config ..')
        self._traffi_apply = True
        return True
    def ix_start_traffic_ethernet(self, trafficHandle=None, exception=False, **kwargs):
        '''
            Returns portStatistics after starting the traffic that is configured in Traffic Stream using Mac devices and Topologies
        '''
        helpers.log("First Checking IXIA vPort States whether Released or not..")
        self.ix_check_vport_state()
        helpers.log("### Starting Traffic")
        # self._handle.execute('startAllProtocols')
        learn = kwargs.get('learn', False)
        time.sleep(2)
        if self._traffi_apply:
            helpers.log("#### No Need to Apply Ixia config already applied")
        else:
            self.ix_apply_traffic()
            helpers.log('###Applied traffic Config ..')
            self._traffi_apply = True
        time.sleep(2)
        # portStatistics = self._handle.getFilteredList(self._handle.getRoot()+'statistics', 'view', '-caption', 'Port Statistics')[0]
        # time.sleep(5)
        if trafficHandle is None:
            if learn:
                helpers.log('Starting traffic for 5 secs and stop it for learning')
                self._handle.execute('startStatelessTrafficBlocking', self._handle.getRoot() + 'traffic')
                time.sleep(10)
                self.ix_stop_traffic()
                helpers.log('Success Stopping traffic fetch port stats to make sure traffic is transmitted!!!')
                self.ix_fetch_port_stats()
                self.ix_clear_stats()
                helpers.log('Fetching port stats after clearing stats')
                self.ix_fetch_port_stats()
            helpers.log('No Traffic Stream is given so, starting traffic on all configured Streams !!')
            try:
                helpers.log("Trying to Starting traffic all the streams configured ...")
                self._handle.execute('startStatelessTrafficBlocking', self._handle.getRoot() + 'traffic')
                helpers.log("Succes starting traffic on all ports...")
            except:
                if exception:
                    helpers.log("Already tried one time with Applying traffic on Ix Network Exception ,, need to check traffic config for fix this")
                    helpers.log("Unexpected error: %s" % sys.exc_info()[0])
                    return False
                else:
                    helpers.log("Got IXIA exception while Applying traffic ...")
                    helpers.log("will try applying the traffic and try again...")
                    self._handle.execute('apply', self._handle.getRoot() + 'traffic')
                    helpers.log('###Applied traffic Config ..')
                    self.ix_start_traffic_ethernet(trafficHandle, exception=True)

        else:
            if learn:
                helpers.log('Starting traffic for 5 secs and stop it for learning on give traffic stream')
                self._handle.execute('startStatelessTrafficBlocking', trafficHandle)
                time.sleep(10)
                self.ix_stop_traffic()
                helpers.log('Success Stopping traffic fetch port stats to make sure traffic is transmitted!!!')
                self.ix_fetch_port_stats()
                self.ix_clear_stats()
                helpers.log('Fetching port stats after clearing stats')
                self.ix_fetch_port_stats()
            helpers.log('Traffic Stream is given, starting traffic on given stream')
            try:
                helpers.log("Trying to start traffic on given traffic stream..")
                self._handle.execute('startStatelessTrafficBlocking', trafficHandle)
            except:
                helpers.log("Got Exception while trying to apply traffic..")
                helpers.log("Unexpected error: %s" % sys.exc_info()[0])
                if exception:
                    helpers.log("Already tried one time with Applying traffic on Ix Network Exception ,, need to check traffic config for fix this")
                    return False
                else:
                    helpers.log("Got IXIA exception while Applying traffic ...")
                    helpers.log("will try applying the traffic and try again...")
                    self._handle.execute('apply', self._handle.getRoot() + 'traffic')
                    helpers.log('###Applied traffic Config ..')
                    self.ix_start_traffic_ethernet(trafficHandle, exception=True)


        time.sleep(10)
        helpers.log("### Traffic Started")
        return True
    def ix_start_hosts(self, port_name=None, ip_type='ipv4', arp_check=True, RetransmitInterval='3000', RetransmitCount='4'):
        '''
            Starts the Topo's that is create under port_name
        '''
        helpers.log("arp_chek: %s" % arp_check)
        helpers.log("First Checking IXIA vPort States whether Released or not..")
        self.ix_check_vport_state()
        helpers.log("Adding Arp Re-Trasmit interval: %s and Arp Transmit Count: %s" % (RetransmitInterval, RetransmitCount))
        vports = self._handle.getList(self._handle.getRoot(), 'vport')
        for vport in vports:
            self._handle.setAttribute(vport + '/protocolStack/options', '-ipv4RetransTime' , RetransmitInterval)
            self._handle.setAttribute(vport + '/protocolStack/options', '-ipv4McastSolicit' , RetransmitCount)
        self._handle.commit()
        helpers.log("Disable Suppression of Arp for Duplicate gateway in IxNetwork..")
        arp_dup_ref = self._handle.getAttribute(self._handle.getRoot() + 'globals/topology/ipv4', '-suppressArpForDuplicateGateway')
        self._handle.setMultiAttribute(arp_dup_ref, '-clearOverlays', False, '-pattern', 'singleValue')
        self._handle.commit()
        arp_dup_ref_value = self._handle.add(arp_dup_ref, 'singleValue')
        self._handle.setMultiAttribute(arp_dup_ref_value, '-value', False)
        self._handle.commit()
        if str(arp_check).lower() == 'False'.lower():
            helpers.log("Disable Arp Check in Ixia...")
            self._arp_check = False
        if port_name is None:
            for topo in self._topology.values():
                self._handle.execute('start', topo)
        else:
            self._handle.execute('start', self._topology[port_name])
            helpers.log('Successfully Started L3 Hosts on Ixia Port : %s' % str(self._port_map_list[port_name]))
        if self._arp_check:
            helpers.log("Checking for Gateway Arp Resolution in IxNetwork..")
            self.ix_chk_arp()
        else:
            helpers.log('Skipping ARP RESOLUTION CHECK ..AS Manualy Gw Mac is configured/ arp_check is False')
            helpers.log('Sleeping 20 sec for IP Host to be UP...')
            time.sleep(30)
        return True

    def ix_chk_arp(self, ip_type="ipv4"):
        helpers.log("First Checking IXIA vPort States whether Released or not..")
        self.ix_check_vport_state()
        for port, topo in self._topology.iteritems():
            i = 0
            while True:
                i = i + 1
                device1 = self._handle.getList(self._topology[port], 'deviceGroup')
                if len(device1) == 0:
                    helpers.log(' no devices created for this Port , skipping Arp resolution')
                    break
                time.sleep(1)
                mac_device1 = self._handle.getList(device1[0], 'ethernet')
                ip_device1 = self._handle.getList(mac_device1[0], ip_type)
                resolved_mac = self._handle.getAttribute(ip_device1[0], '-resolvedGatewayMac')
                helpers.log ('Sleeping 5 sec ..for Arps to get resolved !')
                time.sleep(1)  # Sleep for the gw arp to get Resolved
                helpers.log('Successfully Started L3 Hosts on Ixia Port : %s' % str(topo))
                helpers.log(' Resolved MAC for Gw : %s' % str(resolved_mac))
                match = re.match(r'.*Unresolved*.', resolved_mac[0])
                if match:
                    if i < 10:
                        continue
                    else:
                        raise IxNetwork.IxNetError('Arp for GW not Resolved on port : %s after 10 trys so cannot send L3 Traffic!!' % port)
                        return False
                else:
                    helpers.log('Arp Successfully resolved for gw on port %s !!' % port)
                    break
                helpers.log (' Resolved MAC for Gw : %s' % str(resolved_mac))
        return True

    def ix_stop_hosts(self, port_name):
        '''
            Stops the topo with hosts that is created under give port_name
        '''
        helpers.log("First Checking IXIA vPort States whether Released or not..")
        self.ix_check_vport_state()
        self._handle.execute('stop', self._topology[port_name])
        helpers.log('Successfully Stopped Hosts on Ixia Port : %s' % str(self._port_map_list[port_name]))
        return True

    def ix_send_arp(self, ip_device):
        '''
            Sends arp for the gw_ip configured on the ip_Device
        '''
        helpers.log("First Checking IXIA vPort States whether Released or not..")
        self.ix_check_vport_state()
        self._handle.execute('sendArp', ip_device)
        helpers.log('Successully sent arp !!')
        return True

    def ix_fetch_port_stats(self, **kwargs):
        '''
            Returns Dictionary with Port Tx and Rx real time results
        '''
        helpers.log("First Checking IXIA vPort States whether Released or not..")
        self.ix_check_vport_state()
        stream = kwargs.get('stream', None)
        flow_stats = kwargs.get('flow_stats', False)
        helpers.log('Got the Stream Arguments %s' % str(kwargs))
        handle = self._handle
        port_stats = {}
        if stream is None:
            helpers.log('Fetching all Ixia Port Stats defined in Topo File ..')
            portStatistics = handle.getFilteredList(handle.getRoot() + 'statistics', 'view', '-caption', 'Port Statistics')[0]
            col_names = handle.getAttribute(portStatistics + '/page', '-columnCaptions')
            stats = handle.getAttribute(portStatistics + '/page', '-rowValues')
            for stat in stats:
                port_stat = {}
                for column, value in zip(col_names, stat[0]):
                    if column == 'Stat Name':
                        port_stat['physical_port'] = value
                    if column == 'Port Name':
                        port_stat['port'] = value
                    if column == 'Frames Tx.':
                        port_stat['transmitted_frames'] = value
                    if column == 'Valid Frames Rx.':
                        port_stat['received_valid_frames'] = value
                    if column == 'Frames Tx. Rate':
                        port_stat['transmitted_frame_rate'] = value
                    if column == 'Valid Frames Rx. Rate':
                        port_stat['received_valid_frame_rate'] = value
    #                 if column == 'Data Integrity Frames Rx.':
    #                     port_stat['received_invalid_frames'] = value
                    if column == 'Data Integrity Frames Rx.':
                        port_stat['received_data_integrity_frames'] = value
                    if column == 'CRC Errors':
                        port_stat['received_crc_errored_frames'] = value
                    if column == 'Bytes Rx.':
                        frames = int(value) / int(self._frame_size)
                        port_stat['received_frames'] = str(frames)
                    if column == 'Bytes Rx. Rate':
                        frames = int(value) / int(self._frame_size)
                        port_stat['received_frame_rate'] = str(frames)
                    if re.match(r'.*Loss Duration.*', column):
                        port_stat['packet_loss_duration_ms'] = value

                port_stats[port_stat['port']] = port_stat
            helpers.log('result:\n%s' % helpers.prettify(port_stats))
        else:
            traffic_item_name = handle.getAttribute(stream, '-name')
            helpers.log('Fetching Port Stats for Traffic Item : %s' % traffic_item_name)
            if flow_stats:  # Fetching Flow stats from IxNetwork under flow_stats view
                portStatistics = handle.getFilteredList(handle.getRoot() + 'statistics', 'view', '-caption', 'Flow Statistics')[0]
                col_names = handle.getAttribute(portStatistics + '/page', '-columnCaptions')
                stats = handle.getAttribute(portStatistics + '/page', '-rowValues')
                temp_port_stat = {}
                temp_port_stats = {}
                final_stats = {}
                get_stats = False
                for stat in stats:
                    for column, value in zip(col_names, stat[0]):
                        if column == 'Tx Port':
                            print('Adding TRAFFIC ITEM Name ...!!!!')
                            if len(port_stat) == 0:
                                helpers.Log ("skip adding port_stat in port_Stats Dic...")
                            else:
                                helpers.log("Adding port_stat into port_stats Dic...")
                                temp_port_stats[port_stat['Tx Port']] = temp_port_stat
                                final_stats[port_stat["Traffic Item"]] = temp_port_stats
                                temp_port_stat = {}
                            temp_port_stat[column] = value
                            get_stats = True
                        if get_stats:
                            temp_port_stat[column] = value
                helpers.log("Adding port_stat into port_stats Dic...")
                temp_port_stats[port_stat['Tx Port']] = temp_port_stat
                final_stats[port_stat["Traffic Item"]] = temp_port_stats
                temp_port_stat = {}
                port_stats = final_stats
            else:
                portStatistics = handle.getFilteredList(handle.getRoot() + 'statistics', 'view', '-caption', 'Traffic Item Statistics')[0]
                col_names = handle.getAttribute(portStatistics + '/page', '-columnCaptions')
                stats = handle.getAttribute(portStatistics + '/page', '-rowValues')
                get_stats = False
                port_stat = {}
                for stat in stats:
                    get_stats = False
                    for column, value in zip(col_names, stat[0]):
                        if column == 'Traffic Item':
                            if value == traffic_item_name:
                                helpers.log('Adding TRAFFIC ITEM Name ...!!!!')
                                port_stat['Traffic_item'] = value
                                get_stats = True
                        if get_stats:
                            if column == 'Tx Frames':
                                port_stat['transmitted_frames'] = value
                            if column == 'Rx Frames':
                                port_stat['received_frames'] = value
                                port_stat['received_valid_frames'] = value
                            if column == 'Loss %':
                                port_stat['loss_percentage'] = value
                            if column == 'Tx Frame Rate':
                                port_stat['transmitted_frame_rate'] = value
                            if column == 'Rx Frame Rate':
                                port_stat['received_frame_rate'] = value
                            if column == 'Frames Delta':
                                port_stat['frames_delta'] = value
                            if re.match(r'.*Loss Duration.*', column):
                                port_stat['packet_loss_duration_ms'] = value
                port_stats[port_stat['Traffic_item']] = port_stat
            helpers.log('result:\n%s' % helpers.prettify(port_stats))
        return port_stats

    def ix_stop_traffic(self, traffic_stream=None):
        '''
            Stops the traffis and returns port stats
            Ex Usage : IxStopTraffic(ix_handle, traffic_stream)
        '''
        handle = self._handle
        helpers.log("First Checking IXIA vPort States whether Released or not..")
        self.ix_check_vport_state()
        helpers.log("Stopping Traffic")
        ixia_traffic_state = handle.getAttribute(handle.getRoot() + 'traffic', '-state')
        if str(ixia_traffic_state) == 'stopped':
            helpers.log('IXIA TRAFFIC CURRENTLY NOT RUNNING ..NO NEED STOP TRAFFIC AGAIN!')
        elif traffic_stream is None:
            helpers.log('No Traffic Stream is given, so stopping all the traffic running on this ixia Session...')
            self._handle.execute('stop', self._handle.getRoot() + 'traffic')
        else:
            helpers.log('CURRENT TRAFFIC STATE IN IXIA %s' % str(ixia_traffic_state))
            handle.execute('stopStatelessTraffic', traffic_stream)
            helpers.log("Printing Statistics")
            port_stats = self.ix_fetch_port_stats()
            helpers.log('result:\n%s' % helpers.prettify(port_stats))

        time.sleep(5)
        helpers.log('Successfully Stopped the traffic for Stream %s ' % str(traffic_stream))
        return True
    def ix_clear_stats(self, port_name=None):
        '''
            Clears stats of give port_name or globally clears port stats
        '''
        handle = self._handle
        helpers.log("First Checking IXIA vPort States whether Released or not..")
        self.ix_check_vport_state()
        if port_name is None:
            helpers.log('Clearing Stats Globally on all ports initialized')
            handle.execute('clearPortsAndTrafficStats')
            helpers.log('Stats Cleared Succesffuly ..')
        helpers.log('Sleep 3 secs for the stats to get cleared in IXIA...')
        time.sleep(3)
        result = self.ix_fetch_port_stats()
        helpers.log('result:\n%s' % helpers.prettify(result))
        return True

    def ix_check_vport_state(self, vports_not_connected=False, retry_count=0, **kwargs):
        handle = self._handle
        for vport in self._vports:
            helpers.log("Checking Connection State of Vport: %s" % str(vport))
            vport_state = handle.getAttribute(vport, '-isConnected')
            helpers.log("Connection State: %s" % str(vport_state))
            if vport_state != "true":
                vports_not_connected = True
                helpers.log("IXIA BUG / Network issue ports got Disconnected.. Reconnecting:")
                handle.execute('connectPorts', vport)
                helpers.log("Executed vport connected")
            else:
                helpers.log("Ports still connected ..No IXIA connection issues")
                vports_not_connected = False
        if vports_not_connected:
            if retry_count == 10:
                helpers.log("Already tried 10 times to re-connect Release IXIA Ports , Aborting tests please check IXNETWORK on Corresponding Windows RDP...")
                helpers.exit_robot_immediately("Aborting tests Due to IXIA Ports got Released / disconnected even after trying 10 times to re-connect")
                return False
            helpers.log("Waiting for IXIA ports to connecte back ....")
            helpers.sleep(10)
            helpers.log("vports state..after connecting back")
            self.ix_check_vport_state(vports_not_connected, retry_count=retry_count + 1)
        return True

    def ix_simulate_port_state(self, **kwargs):
        '''
            Use to Simulate Link Down / UP Action in IxNetowrk..
        '''
        handle = self._handle
        port_name = kwargs.get("port_name", None)
        action = kwargs.get("action", None)
        if port_name is None or action is None:
            helpers.log("Please Pass the Port Name and link simulate action: up/down")
            helpers.exit_robot_immediately("Got In Complete Ixia Argumnets..")
        vports = handle.getList(handle.getRoot(), 'vport')
        if len(vports) == 0:
            helpers.log("No Vports are created in IxNetwork mapping to Bigrobot Topo file tg ixia ports creating vports..")
            self.ix_create_vports()
            if self.ix_map_vports_pyhsical_ports():
                helpers.log('### Successfully mapped vport to physical ixia ports..')
            else:
                helpers.log('Unable to connect to Ixia Chassis')
                return False
            helpers.log("Successfully Created vports mapping to Bigrobot topo file in IxNetwork..")
        vports = handle.getList(handle.getRoot(), 'vport')
        for vport in vports:
            if handle.getAttribute(vport, "-name") == port_name:
                helpers.log("Simulating Link %s in IxNetwork.. " % str(action))
                handle.execute("linkUpDn", vport, str(action))
        return True
    def ix_get_port_state(self, **kwargs):
        '''
            Use to check the Ixia port state in IxNetwork
        '''
        handle = self._handle
        port_name = kwargs.get("port_name", None)
        state = kwargs.get("state", None)
        if port_name is None or state is None:
            helpers.log("Please Pass the Port Name and stae expected: up/down")
            helpers.exit_robot_immediately("Got In Complete Ixia Argumnets..")
        vports = handle.getList(handle.getRoot(), 'vport')
        if len(vports) == 0:
            helpers.log("No Vports are created in IxNetwork mapping to Bigrobot Topo file tg ixia ports creating vports..")
            self.ix_create_vports()
            if self.ix_map_vports_pyhsical_ports():
                helpers.log('### Successfully mapped vport to physical ixia ports..')
            else:
                helpers.log('Unable to connect to Ixia Chassis')
                return False
            helpers.log("Successfully Created vports mapping to Bigrobot topo file in IxNetwork..")
        vports = handle.getList(handle.getRoot(), 'vport')
        for vport in vports:
            if handle.getAttribute(vport, "-name") == port_name:
                helpers.log("Checking the Link state of ixia port %s in IxNetwork.. " % str(port_name))
                helpers.log("IXIA Port State in IxNetwork is: %s" % str(handle.getAttribute(vport, "-state")).lower())
                return str(handle.getAttribute(vport, "-state")).lower()
        return False
    def ix_delete_traffic(self, **kwargs):
        '''
            Method to delete all configured Traffic Items
        '''
        handle = self._handle
        helpers.log("First Checking IXIA vPort States whether Released or not..")
        self.ix_check_vport_state()

        ixia_traffic_state = handle.getAttribute(handle.getRoot() + 'traffic', '-state')
        if str(ixia_traffic_state) == 'started':
            helpers.log("Traffic is Still Running , Stopping the Traffic before deleting traffic item..")
            self.ix_stop_traffic()
        else:
            helpers.log("Traffic Already Stopped in Testcase No need to Stop the Traffic !!")
        root = handle.getRoot()
        traffic_item = handle.getList(root, 'traffic')
        traffic_streams = handle.getList(traffic_item[0], 'trafficItem')
        if len(traffic_streams) == 0:
            helpers.log("No Traffic Streams Configure we are goot no need to Delete streams !")
        else:
            for stream in traffic_streams:
                handle.remove(stream)
            handle.commit()
            helpers.log("Success Removing configured traffic flow !!!")
        helpers.log("Succes deleting Traffic Strems!!")
        handle.remove(handle.getRoot() + 'traffic' + '/trafficItem')
        handle.commit()
        helpers.log('succes removing traffic Items Configured!!!')
        # if self._started_hosts:
        for topo in self._topology:
            self.ix_stop_hosts(topo)
            helpers.log('Successfuly Stopped Hosts on Topology : %s ' % topo)
        helpers.log('Sleeps 3 sec for Hosts to be Stopped')
        time.sleep(20)  # Increase the time for hosts to be stopped, need FIX by checking from IXnetwork.
        for topo in self._topology.values():
            handle.remove(topo)
            handle.commit()
            helpers.log('Successfully Removed Topology : %s ' % str(topo))
        self._topology = {}
        helpers.log('Succes Removing Topologies Created !!!')
        time.sleep(3)
        self._raw_stream = None
        self._raw_stream_id = 1
        return True



