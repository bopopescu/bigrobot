#!/usr/bin/env python
'''
    This module is used to maintain Ixia Related Libraries for traffic generation
'''
import autobot.helpers as helpers
import time, re
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
            while self._handle.getAttribute(vport, '-state') != 'up':
                time.sleep(2)
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

    def ix_create_device_ethernet_ip(self, topology, s_cnt, d_cnt, s_mac, d_mac, s_mac_step, d_mac_step,
                                     src_ip, dst_ip, src_gw_ip, dst_gw_ip, s_ip_step, d_ip_step,
                                     s_gw_step, d_gw_step, src_gw_mac=None,
                                     dst_gw_mac=None, ip_type='ipv4'):
        '''
            RETURN IXIA MAC DEVICES with Ips mapped with Topologies created with vports and added increment values accordingly
            Ex Usage:
            IxLib.IxCreateDeviceEthernet(ixNet,topology, mac_mults =  mac_mults, macs = macs, mac_steps = mac_steps)
        '''
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

        topo_names = []

        for topo in topology:
            if len(self._handle.getList(topo, 'deviceGroup')) > 0:
                helpers.log('Ixia Device Group already created for this Topology so no need to created again')
            else:
                self._handle.add(topo, 'deviceGroup')

        self._handle.commit()
        topo_devices = []
        eth_devices = []

        for topo in topology:
            dev_grp = self._handle.getList(topo, 'deviceGroup')
            topo_device = self._handle.remapIds(dev_grp)[0]
            enabled_ref = self._handle.getAttribute(topo_device, '-enabled')
            self._handle.setMultiAttribute(enabled_ref, '-clearOverlays', False, '-pattern', 'singleValue')
            topo_devices.append(topo_device)
            self._is_device_created = True
        for (topo_device, multi, topo) in zip(topo_devices, mac_mults, topology):
            helpers.log('### topo device : %s' % str(topo_device))
            topo_name = self._handle.getAttribute(topo, '-name')
            topo_names.append(topo_name)
            self._handle.setAttribute(topo_device, '-multiplier', multi)
            eth_devices.append(self._handle.add(topo_device, 'ethernet', '-name', topo_name))
        self._handle.commit()
        mac_devices = []  # as this are added to ixia need to remap as per ixia API's
        ip_devices = []
        ixia_refs = {}  # Dictionary to hold the Ixia References
        for eth_device in eth_devices:
            mac_devices.append(self._handle.remapIds(eth_device)[0])
        for (mac_device, mult, mac_step, mac, ip_step, ip, gw_step, gw_ip, gw_mac) in zip(mac_devices, mac_mults, mac_steps, macs, ip_steps, ips, gw_steps, gw_ips, gw_macs):
            ip_name = handle.getAttribute(mac_device, '-name')
#             ip_name = ip_name + 'IPv4\ 1'
            helpers.log('Values:')
            helpers.log('Mac Device:%s\nMac_Multi:%s\nMac_Step:%s\nMac:%s\nIP_Steps:%s\nIP:%s\nGW_STEP:%s\nGW_IP:%s\nGW_MAC:%s' % (mac_device, mult, mac_step, mac, ip_step, ip, gw_step, gw_ip, gw_mac))
            helpers.log ('Ip: NAME : ' + str(ip_name))
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

            ixia_refs['prefix'] = handle.getAttribute(ip_device_ixia, '-prefix')
            ixia_refs['prefix_singleValue'] = handle.add(ixia_refs['prefix'], 'singleValue')
            handle.setMultiAttribute(ixia_refs['prefix_singleValue'], '-value', '24')
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

#                 ixia_refs['manualGatewayMac_counter_remap'] = handle.remapIds(ixia_refs['manualGatewayMac_counter'])[0]
#                 ixia_refs['resolveGateway_counter'] = handle.add(ixia_refs['resolveGateway'], 'counter')
#                 handle.setMultiAttribute(ixia_refs['resolveGateway_counter'], '-direction', 'increment',
#                                          '-start', 'false', '-step', 'false')
#                 handle.remapIds(ixia_refs['manualGatewayMac_counter'])[0]
        # self._handle.commit()
#         helpers.log(" ## adding Name ", topology[0], topology[1])
#         helpers.log(" ## adding Name ", mac_devices[0], mac_devices[1])
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

    def ix_setup_traffic_streams_ethernet(self, mac1, mac2, frameType, frameSize, frameRate,
                                      frameMode, frameCount, flow, name, ethertype=None, vlan_id=None, vlan_cnt=1, vlan_step=None,
                                      burst_count=None, burst_gap=None,
                                      line_rate=None, crc=None, src_ip=None, dst_ip=None, no_arp=False,
                                      protocol=None, src_port=None, dst_port=None,
                                      icmp_type=None, icmp_code=None, ip_type='ipv4', payload=None, src_vport=None, dst_vport=None,
                                      hex_src_mac=None, hex_dst_mac=None):
        '''
            Returns traffic stream with 2 flows with provided mac sources
            Ex Usage:
                IxLib.IxSetupTrafficStreamsEthernet(ixNet, mac_devices[0], mac_devices[1], frameType, frameSize, frameRate, frameMode)
        '''
        handle = self._handle
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
            helpers.log("src_vport: %s dst_vport: %s" % (src_vport, dst_port))
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
            self._handle.setAttribute(trafficStream1 + '/highLevelStream:1/stack:"ethernet-1"/field:"ethernet.header.etherType-3"',
                                      '-auto', False)
            self._handle.setAttribute(trafficStream1 + '/highLevelStream:1/stack:"ethernet-1"/field:"ethernet.header.etherType-3"',
                                      '-fieldValue', ethertype)
            self._handle.setAttribute(trafficStream1 + '/highLevelStream:1/stack:"ethernet-1"/field:"ethernet.header.etherType-3"',
                                      '-singleValue', ethertype)
            self._handle.setAttribute(trafficStream1 + '/highLevelStream:1/stack:"ethernet-1"/field:"ethernet.header.etherType-3"',
                                      '-countValue', 1)
            self._handle.setAttribute(trafficStream1 + '/highLevelStream:1/stack:"ethernet-1"/field:"ethernet.header.etherType-3"',
                                      '-fixedBits', ethertype)
            self._handle.setAttribute(trafficStream1 + '/highLevelStream:1/stack:"ethernet-1"/field:"ethernet.header.etherType-3"',
                                      '-optionalEnabled ', True)

        if vlan_id is not None:
            helpers.log('Adding Vlan ID: %s !!!' % vlan_id)
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
        if src_ip is not None:
                helpers.log('Adding src_ip and dst_ip ..')
                if ethertype == '0800':
                    self._handle.setMultiAttribute(trafficStream1 + '/highLevelStream:1/stack:"ipv4-2"/field:"ipv4.header.srcIp-27"',
                                              '-countValue', 1, '-fieldValue', src_ip, '-singleValue', src_ip,
                                             '-optionalEnabled', 'true', '-auto', 'false')
                    self._handle.setMultiAttribute(trafficStream1 + '/highLevelStream:1/stack:"ipv4-2"/field:"ipv4.header.dstIp-28"',
                                              '-countValue', 1, '-fieldValue', dst_ip, '-singleValue', dst_ip,
                                             '-optionalEnabled', 'true', '-auto', 'false')
                elif ethertype == '86dd':
                    self._handle.setMultiAttribute(trafficStream1 + '/highLevelStream:1/stack:"ipv6-2"/field:"ipv6.header.srcIP-7"',
                                              '-countValue', 1, '-fieldValue', src_ip, '-singleValue', src_ip,
                                             '-optionalEnabled', 'true', '-auto', 'false')
                    self._handle.setMultiAttribute(trafficStream1 + '/highLevelStream:1/stack:"ipv6-2"/field:"ipv6.header.dstIP-8"',
                                              '-countValue', 1, '-fieldValue', dst_ip, '-singleValue', dst_ip,
                                             '-optionalEnabled', 'true', '-auto', 'false')
        if protocol is not None:
            helpers.log('Adding Protocol Field in IP Header ..')
            if ethertype == '0800':
                self._handle.setMultiAttribute(trafficStream1 + '/highLevelStream:1/stack:"ipv4-2"/field:"ipv4.header.protocol-25"',
                                              '-countValue', 1, '-fieldValue', protocol,
                                             '-optionalEnabled', 'true', '-auto', 'false')
            elif ethertype == '86dd':
                self._handle.setMultiAttribute(trafficStream1 + '/highLevelStream:1/stack:"ipv6-2"/field:"ipv6.header.nextHeader-5"',
                                              '-countValue', 1, '-fieldValue', protocol,
                                             '-optionalEnabled', 'true', '-auto', 'false')
            if protocol == 'TCP':
                helpers.log('Adding Src_port: %s and Dst_Port: %s for Protocl TCP..!!!' % (src_port, dst_port))
                self._handle.setMultiAttribute(trafficStream1 + '/highLevelStream:1/stack:"tcp-3"/field:"tcp.header.srcPort-1"',
                                              '-countValue', 1, '-fieldValue', src_port, '-singleValue', src_port,
                                             '-optionalEnabled', 'true', '-auto', 'false')
                self._handle.setMultiAttribute(trafficStream1 + '/highLevelStream:1/stack:"tcp-3"/field:"tcp.header.dstPort-2"',
                                              '-countValue', 1, '-fieldValue', dst_port, '-singleValue', dst_port,
                                             '-optionalEnabled', 'true', '-auto', 'false')
            if protocol == 'UDP':
                helpers.log('Adding Src_port: %s and Dst_Port: %s for Protocl UDP..!!!' % (src_port, dst_port))
                self._handle.setMultiAttribute(trafficStream1 + '/highLevelStream:1/stack:"udp-3"/field:"udp.header.srcPort-1"',
                                              '-countValue', 1, '-fieldValue', src_port, '-singleValue', src_port,
                                             '-optionalEnabled', 'true', '-auto', 'false')
                self._handle.setMultiAttribute(trafficStream1 + '/highLevelStream:1/stack:"udp-3"/field:"udp.header.dstPort-2"',
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
                self._handle.setAttribute(trafficStream1 + '/highLevelStream:2/stack:"ethernet-1"/field:"ethernet.header.etherType-3"',
                                          '-auto', False)
                self._handle.setAttribute(trafficStream1 + '/highLevelStream:2/stack:"ethernet-1"/field:"ethernet.header.etherType-3"',
                                          '-fieldValue', ethertype)
                self._handle.setAttribute(trafficStream1 + '/highLevelStream:2/stack:"ethernet-1"/field:"ethernet.header.etherType-3"',
                                          '-singleValue', ethertype)
                self._handle.setAttribute(trafficStream1 + '/highLevelStream:2/stack:"ethernet-1"/field:"ethernet.header.etherType-3"',
                                          '-countValue', 1)
                self._handle.setAttribute(trafficStream1 + '/highLevelStream:2/stack:"ethernet-1"/field:"ethernet.header.etherType-3"',
                                          '-fixedBits', ethertype)
                self._handle.setAttribute(trafficStream1 + '/highLevelStream:2/stack:"ethernet-1"/field:"ethernet.header.etherType-3"',
                                          '-optionalEnabled ', True)
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
                helpers.log('Adding src_ip and dst_ip ..')
                if ethertype == '0800':
                    self._handle.setMultiAttribute(trafficStream1 + '/highLevelStream:1/stack:"ipv4-2"/field:"ipv4.header.srcIp-27"',
                                              '-countValue', 1, '-fieldValue', dst_ip, '-singleValue', dst_ip,
                                             '-optionalEnabled', 'true', '-auto', 'false')
                    self._handle.setMultiAttribute(trafficStream1 + '/highLevelStream:1/stack:"ipv4-2"/field:"ipv4.header.dstIp-28"',
                                              '-countValue', 1, '-fieldValue', src_ip, '-singleValue', src_ip,
                                             '-optionalEnabled', 'true', '-auto', 'false')
                elif ethertype == '86dd':
                    self._handle.setMultiAttribute(trafficStream1 + '/highLevelStream:1/stack:"ipv6-2"/field:"ipv6.header.srcIP-7"',
                                              '-countValue', 1, '-fieldValue', dst_ip, '-singleValue', dst_ip,
                                             '-optionalEnabled', 'true', '-auto', 'false')
                    self._handle.setMultiAttribute(trafficStream1 + '/highLevelStream:1/stack:"ipv6-2"/field:"ipv6.header.dstIP-8"',
                                              '-countValue', 1, '-fieldValue', src_ip, '-singleValue', src_ip,
                                             '-optionalEnabled', 'true', '-auto', 'false')
            if protocol is not None:
                helpers.log('Adding Protocol Field in IP Header ..')
                if ethertype == '0800':
                    self._handle.setMultiAttribute(trafficStream1 + '/highLevelStream:2/stack:"ipv4-2"/field:"ipv4.header.protocol-25"',
                                                  '-countValue', 1, '-fieldValue', protocol,
                                                 '-optionalEnabled', 'true', '-auto', 'false')
                elif ethertype == '86dd':
                    self._handle.setMultiAttribute(trafficStream1 + '/highLevelStream:2/stack:"ipv6-2"/field:"ipv6.header.nextHeader-5"',
                                                  '-countValue', 1, '-fieldValue', protocol,
                                                 '-optionalEnabled', 'true', '-auto', 'false')
                if protocol == 'TCP':
                    helpers.log('Adding Src_port: %s and Dst_Port: %s for Protocl TCP..!!!' % (src_port, dst_port))
                    self._handle.setMultiAttribute(trafficStream1 + '/highLevelStream:2/stack:"tcp-3"/field:"tcp.header.srcPort-1"',
                                                  '-countValue', 1, '-fieldValue', dst_port, '-singleValue', dst_port,
                                                 '-optionalEnabled', 'true', '-auto', 'false')
                    self._handle.setMultiAttribute(trafficStream1 + '/highLevelStream:2/stack:"tcp-3"/field:"tcp.header.dstPort-2"',
                                                  '-countValue', 1, '-fieldValue', src_port, '-singleValue', src_port,
                                                 '-optionalEnabled', 'true', '-auto', 'false')
                if protocol == 'UDP':
                    helpers.log('Adding Src_port: %s and Dst_Port: %s for Protocl UDP..!!!' % (src_port, dst_port))
                    self._handle.setMultiAttribute(trafficStream1 + '/highLevelStream:2/stack:"udp-3"/field:"udp.header.srcPort-1"',
                                                  '-countValue', 1, '-fieldValue', dst_port, '-singleValue', dst_port,
                                                 '-optionalEnabled', 'true', '-auto', 'false')
                    self._handle.setMultiAttribute(trafficStream1 + '/highLevelStream:2/stack:"udp-3"/field:"udp.header.dstPort-2"',
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
                                                       frame_cnt, stream_flow, name, ethertype, vlan_id, vlan_cnt=vlan_cnt, vlan_step=vlan_step,
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
                                                                      dst_ip_step, src_gw_step, dst_gw_step, ip_type=ip_type)
            helpers.log('Created Mac Devices with corrsponding Topos ...')
            helpers.log ("Success Creating Ip Devices !!!")
            return ip_devices

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
        vlan_id = kwargs.get('vlan_id', None)
        vlan_cnt = kwargs.get('vlan_cnt', 1)
        vlan_step = kwargs.get('vlan_step', 1)
        line_rate = kwargs.get('line_rate', None)
        protocol = kwargs.get('protocol', None)
        burst_count = kwargs.get('burst_count', None)
        burst_gap = kwargs.get('burst_gap', None)
        payload = kwargs.get('payload', None)

        crc = kwargs.get('crc', None)
        ip_type = 'ipv4'
        if vlan_id is not None:
            ethertype = '8100'
            protocol = kwargs.get('protocol', 'UDP')

        if ethertype == '0800':
            src_ip = kwargs.get('src_ip', '20.0.0.1')
            dst_ip = kwargs.get('dst_ip', '20.0.0.2')
            src_gw_ip = kwargs.get('src_gw', '20.0.0.2')
            src_gw_step = kwargs.get('src_gw_step', '0.0.1.0')
            dst_gw_ip = kwargs.get('dst_gw', '20.0.0.1')
            dst_gw_step = kwargs.get('src_gw_step', '0.0.1.0')
            src_ip_step = kwargs.get('src_ip_step', '0.0.0.1')
            dst_ip_step = kwargs.get('dst_ip_step', '0.0.0.1')
            self._frame_size = kwargs.get('frame_size', 130)
            protocol = kwargs.get('protocol', 'UDP')

        elif ethertype == '86dd':
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
            protocol = kwargs.get('protocol', 'UDP')
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

        no_arp = kwargs.get('no_arp', False)

        src_port = kwargs.get('src_port', '6001')
        dst_port = kwargs.get('dst_port', '7001')
        icmp_type = kwargs.get('icmp_type', '0')
        icmp_code = kwargs.get('icmp_code', '0')

        ix_tcl_server = self._tcl_server_ip
        flow = kwargs.get('flow', None)

        if ix_tcl_server is None or ix_ports is None or src_ip is None or dst_ip is None:
            helpers.warn('Please Provide Required Args for IXIA_L2_ADD helper method !!')
            raise IxNetwork.IxNetError('Please provide Required Args for IXIA_L2_ADD helper method !!')
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
                src_ix_port = match_uni1.group(2).lower()
                dst_ix_port = match_uni1.group(1).lower()
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
                                                                          dst_ip_step, src_gw_step, dst_gw_step, dst_mac, src_mac, ip_type=ip_type)
                helpers.log('Created Mac Devices : %s ' % mac_devices)

                traffic_stream = self.ix_setup_traffic_streams_ethernet(mac_devices[0], mac_devices[1],
                                                           frame_type, self._frame_size, frame_rate, frame_mode,
                                                           frame_cnt, stream_flow, name, vlan_id=vlan_id, crc=crc, src_ip=src_ip, dst_ip=dst_ip,
                                                           protocol=protocol, icmp_type=icmp_type, icmp_code=icmp_code, vlan_cnt=vlan_cnt, vlan_step=vlan_step,
                                                           burst_count=burst_count, burst_gap=burst_gap,
                                                           src_port=src_port, dst_port=dst_port, no_arp=no_arp, ethertype=ethertype, line_rate=line_rate)

                traffic_stream1.append(traffic_stream)
            else:
                helpers.log('Adding L3 Stream with ARP resolution for configured Gateway')
                self._arp_check = True
                (ip_devices, mac_devices) = self.ix_create_device_ethernet_ip(create_topo, s_cnt, d_cnt, src_mac, dst_mac, src_mac_step,
                                                                          dst_mac_step, src_ip, dst_ip, src_gw_ip, dst_gw_ip, src_ip_step,
                                                                          dst_ip_step, src_gw_step, dst_gw_step, ip_type=ip_type)
                self.ix_start_hosts(ip_type=ip_type)
                self._started_hosts = True
                traffic_item = self.ix_setup_traffic_streams_ethernet(ip_devices[0], ip_devices[1], frame_type, self._frame_size, frame_rate, frame_mode,
                                                             frame_cnt, stream_flow, name, vlan_id=vlan_id, crc=crc, vlan_cnt=vlan_cnt, vlan_step=vlan_step,
                                                             burst_count=burst_count, burst_gap=burst_gap,
                                                             protocol=protocol, icmp_type=icmp_type, icmp_code=icmp_code,
                                                             src_port=src_port, dst_port=dst_port, ethertype=ethertype, ip_type=ip_type, line_rate=line_rate)
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
                                                             src_port=src_port, dst_port=dst_port, ethertype=ethertype, ip_type=ip_type, line_rate=line_rate,
                                                             payload=payload, src_vport=src_vport, dst_vport=dst_vport,
                                                             hex_src_mac=src_mac, hex_dst_mac=dst_mac)
            traffic_stream1.append(traffic_item)
        return traffic_stream1[0]

    def ix_start_traffic_ethernet(self, trafficHandle=None, exception=False, **kwargs):
        '''
            Returns portStatistics after starting the traffic that is configured in Traffic Stream using Mac devices and Topologies
        '''
        helpers.log("### Starting Traffic")
        # self._handle.execute('startAllProtocols')
        learn = kwargs.get('learn', False)
        time.sleep(2)
        if self._traffi_apply:
            helpers.log("#### No Need to Apply Ixia config already applied")
        else:
            self._handle.execute('apply', self._handle.getRoot() + 'traffic')
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
    def ix_start_hosts(self, port_name=None, ip_type='ipv4'):
        '''
            Starts the Topo's that is create under port_name
        '''
        if port_name is None:
            for topo in self._topology.values():
                self._handle.execute('start', topo)
            if self._arp_check:
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
                                raise IxNetwork.IxNetError('Arp for GW not Resolved on port : %s so cannot send L3 Traffic!!' % port)
                                break
                        else:
                            helpers.log('Arp Successfully resolved for gw on port %s !!' % port)
                            break
                        helpers.log (' Resolved MAC for Gw : %s' % str(resolved_mac))
            else:
                helpers.log('Skipping ARP RESOLUTION CHECK ..AS Manualy Gw Mac is configured')
                helpers.log('Sleeping 20 sec for IP Host to be UP...')
                time.sleep(30)

        else:
            self._handle.execute('start', self._topology[port_name])
            helpers.log('Successfully Started L3 Hosts on Ixia Port : %s' % str(self._port_map_list[port_name]))
        return True

    def ix_chk_arp(self, ip_type="ipv4"):
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
        self._handle.execute('stop', self._topology[port_name])
        helpers.log('Successfully Stopped Hosts on Ixia Port : %s' % str(self._port_map_list[port_name]))
        return True

    def ix_send_arp(self, ip_device):
        '''
            Sends arp for the gw_ip configured on the ip_Device
        '''
        self._handle.execute('sendArp', ip_device)
        helpers.log('Successully sent arp !!')
        return True

    def ix_fetch_port_stats(self, **kwargs):
        '''
            Returns Dictionary with Port Tx and Rx real time results
        '''
        stream = kwargs.get('stream', None)
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

                port_stats[port_stat['port']] = port_stat
            helpers.log('result:\n%s' % helpers.prettify(port_stats))
        else:
            traffic_item_name = handle.getAttribute(stream, '-name')
            helpers.log('Fetching Port Stats for Traffic Item : %s' % traffic_item_name)
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
            port_stats[port_stat['Traffic_item']] = port_stat
        helpers.log('result:\n%s' % helpers.prettify(port_stats))
        return port_stats

    def ix_stop_traffic(self, traffic_stream=None):
        '''
            Stops the traffis and returns port stats
            Ex Usage : IxStopTraffic(ix_handle, traffic_stream)
        '''
        handle = self._handle
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
        if port_name is None:
            helpers.log('Clearing Stats Globally on all ports initialized')
            handle.execute('clearPortsAndTrafficStats')
            helpers.log('Stats Cleared Succesffuly ..')
        helpers.log('Sleep 3 secs for the stats to get cleared in IXIA...')
        time.sleep(3)
        result = self.ix_fetch_port_stats()
        helpers.log('result:\n%s' % helpers.prettify(result))
        return True

    def ix_delete_traffic(self, **kwargs):
        '''
            Method to delete all configured Traffic Items
        '''
        handle = self._handle
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
        time.sleep(3)
        for topo in self._topology.values():
            handle.remove(topo)
            handle.commit()
            helpers.log('Successfully Removed Topology : %s ' % str(topo))
        self._topology = {}
        helpers.log('Succes Removing Topologies Created !!!')
        time.sleep(3)
        return True



