#!/usr/bin/env python
'''
    This module is used to maintain Ixia Related Libraries for traffic generation
'''
import autobot.helpers as helpers
import time, re
from vendors.Ixia import IxNetwork

class Ixia(object):
    def __init__(self, tcl_server_ip, tcl_server_port=8009, ix_version='7.10', chassis_ip=None,
                 port_map_list=None):
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

    def port_map_list(self, ports):
        # something happens here
        # self._port_map_list = <something>
        port_map_list = {}
        for port in ports.iteritems():
            match = re.match(r'(\d+)/(\d+)', port[1]['name'].lower())
            port_map_list[port[0].lower()] = (self._chassis_ip, match.group(1), match.group(2))
        return port_map_list

    def ix_connect(self):
        self._handle = IxNetwork.IxNet()
        self._handle.connect(self._tcl_server_ip, '-port', self._tcl_server_port,
                        '-version', self._ix_version)
        # ## clear the configuration
        asyncHandle = self._handle.setAsync().execute('newConfig')
        self._handle.wait(asyncHandle)

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
        chassis = self._handle.add(self._handle.getRoot() + 'availableHardware', 'chassis', '-hostname', self._chassis_ip)
        self._handle.commit()
        chassis = self._handle.remapIds(chassis)[0]
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
        for mac_device in mac_devices:
            self._handle.setAttribute(mac_device, '-name', 'SND_RCV Device')
        self._handle.commit()
        helpers.log("### Done adding two device groups")
        return mac_devices

    def ix_create_device_ethernet_ip(self, topology, s_cnt, d_cnt, s_mac, d_mac, s_mac_step, d_mac_step,
                                     src_ip, dst_ip, src_gw_ip, dst_gw_ip, s_ip_step, d_ip_step, src_gw_mac = None,
                                     dst_gw_mac = None):
        '''
            RETURN IXIA MAC DEVICES with Ips mapped with Topologies created with vports and added increment values accordingly
            Ex Usage:
            IxLib.IxCreateDeviceEthernet(ixNet,topology, mac_mults =  mac_mults, macs = macs, mac_steps = mac_steps)
        '''
        helpers.log("### Adding %s device groups" % len(topology))
        handle = self._handle
        mac_mults = [s_cnt, d_cnt]
        mac_steps = [s_mac_step, d_mac_step]
        ip_steps = [s_ip_step, d_ip_step]
        macs = [s_mac, d_mac]
        ips = [src_ip, dst_ip]
        gw_ips = [src_gw_ip, dst_gw_ip]
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
        ixia_refs = {} # Dictionary to hold the Ixia References
        for eth_device in eth_devices:
            mac_devices.append(self._handle.remapIds(eth_device)[0])
        for (mac_device, mult, mac_step, mac, ip_step, ip, gw_ip, gw_mac) in zip(mac_devices, mac_mults, mac_steps, macs, ip_steps, ips, gw_ips, gw_macs):
            ip_name = handle.getAttribute(mac_device, '-name')
#             ip_name = ip_name + 'IPv4\ 1'
            helpers.log ('Ip: NAME : ' +  str(ip_name))
            ip_device = self._handle.add(mac_device, "ipv4", '-name', ip_name)
            ip_device_ixia = handle.remapIds(ip_device)[0]
            handle.commit()
            ip_devices.append(ip_device_ixia)
            helpers.log( 'Using Address: ' + str(ip))
            ixia_refs['address'] = handle.getAttribute(ip_device_ixia, '-address')
            
            if mult <= 1:
                m1 = self._handle.setAttribute(self._handle.getAttribute(mac_device, '-mac') + '/singleValue', '-value', mac)
                handle.setMultiAttribute(ixia_refs['address']+'/counter', 'direction', 'increment', '-start', ip, '-step', '0.0.0.0')
                ixia_refs['gatewayIp'] = handle.getAttribute(ip_device_ixia, '-gatewayIp')
                ixia_refs['gatewayIp_singleValue'] = handle.add(ixia_refs['gatewayIp'], 'singleValue')
                handle.setMultiAttribute(ixia_refs['gatewayIp_singleValue'], '-value', gw_ip)
                
                
            else:
                helpers.log('###Adding Multipier ...for mac and Ip')
                m1 = self._handle.setMultiAttribute(self._handle.getAttribute(mac_device, '-mac') + '/counter', '-direction',
                                              'increment', '-start', mac, '-step', mac_step)
                handle.setMultiAttribute(ixia_refs['address']+'/counter', 'direction', 'increment', '-start', ip, '-step', ip_step)
                ixia_refs['gatewayIp'] = handle.getAttribute(ip_device_ixia, '-gatewayIp')
                ixia_refs['gatewayIp_counter'] = handle.add(ixia_refs['gatewayIp'], 'counter')
                handle.setMultiAttribute(ixia_refs['gatewayIp_counter'],'direction', 'increment', '-start', gw_ip, '-step', ip_step)
                
            handle.commit()
            #handle.remapIds(ixia_refs['address_counter'])[0]
            
            ixia_refs['prefix'] = handle.getAttribute(ip_device_ixia, '-prefix')
            ixia_refs['prefix_singleValue'] = handle.add(ixia_refs['prefix'], 'singleValue')
            handle.setMultiAttribute(ixia_refs['prefix_singleValue'], '-value', '24')
            handle.commit()
            handle.remapIds(ixia_refs['prefix'])[0]
            
            ixia_refs['resolveGateway'] = handle.getAttribute(ip_device_ixia, '-resolveGateway')
            ixia_refs['resolveGateway_singleValue'] = handle.add(ixia_refs['resolveGateway'], 'singleValue')
            if gw_mac is None:
                helpers.log ('Gateway Address: ' +  str(gw_ip))
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
        #self._handle.commit()
#         helpers.log(" ## adding Name ", topology[0], topology[1])
#         helpers.log(" ## adding Name ", mac_devices[0], mac_devices[1])
        i = 1
        for mac_device in mac_devices:
            name = "Device_" + str(i)
            self._handle.setAttribute(mac_device, '-name', name)
            i = i +1
        self._handle.commit()
        helpers.log("### Done adding two device groups")
        return ip_devices, mac_devices # return created Ip_devices and mac_devices

    def ix_setup_traffic_streams_ip(self,ip1,ip2,frameType,frameSize,frameRate,frameMode):
        handle = self._handle
        handle.add(handle.getRoot()+'/traffic','trafficItem','-name','IPv4 traffic','-allowSelfDestined',False,
                   '-trafficItemType','l2L3','-mergeDestinations',False,'-egressEnabled',False,'-srcDestMesh','oneToOne',
                   '-enabled',True,'-routeMesh','oneToOne','-transmitMode','interleaved','-biDirectional',False,
                   '-trafficType','ipv4','-hostsPerNetwork',1)
        handle.commit()
        trItem = handle.getList(handle.getRoot()+'/traffic','trafficItem')
        trafficStream1=handle.remapIds(trItem)[0]
        end1 = handle.add(trafficStream1,'endpointSet','-sources',ip1,'-destinations',ip2,'-name','end1','-sourceFilter',' ','-destinationFilter',' ')
        end2 = handle.add(trafficStream1,'endpointSet','-sources',ip2,'-destinations',ip1,'-name','end2','-sourceFilter',' ','-destinationFilter',' ')
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
                                      frameMode, frameCount, flow, name, ethertype=None, vlan_id=None,
                                      crc=None, src_ip = None, dst_ip = None, no_arp=False,
                                      protocol= None, src_port= None, dst_port = None):
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
        else:
            helpers.log('Adding Ipv4 type Stream for sending with Arp Resolution')
            trafficStream1 = handle.add(handle.getRoot()+'/traffic','trafficItem','-name','IPv4 traffic','-allowSelfDestined',False,
                       '-trafficItemType','l2L3','-mergeDestinations',False,'-egressEnabled',False,'-srcDestMesh','oneToOne',
                       '-enabled',True,'-routeMesh','oneToOne','-transmitMode','interleaved','-biDirectional',False,
                       '-trafficType','ipv4','-hostsPerNetwork',1)
        self._handle.commit()
        endpointSet1 = self._handle.add(trafficStream1, 'endpointSet', '-name', 'l2u', '-sources', mac1,
                                  '-destinations', mac2)
        self._handle.setAttribute(trafficStream1, '-enabled', True)
        self._handle.setAttribute(trafficStream1 + '/highLevelStream:1/' + 'frameSize', '-type', frameType)
        self._handle.setAttribute(trafficStream1 + '/highLevelStream:1/' + 'frameSize', '-fixedSize', frameSize)
        self._handle.setAttribute(trafficStream1 + '/highLevelStream:1/' + 'frameRate', '-type', frameMode)
        self._handle.setAttribute(trafficStream1 + '/highLevelStream:1/' + 'frameRate', '-rate', frameRate)
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
            self._handle.setAttribute(trafficStream1 + '/highLevelStream:1/stack:"vlan-2"/field:"vlan.header.vlanTag.vlanID-3"',
                                      '-countValue', 1)
            self._handle.setAttribute(trafficStream1 + '/highLevelStream:1/stack:"vlan-2"/field:"vlan.header.vlanTag.vlanID-3"',
                                      '-fieldValue', vlan_id)
            self._handle.setAttribute(trafficStream1 + '/highLevelStream:1/stack:"vlan-2"/field:"vlan.header.vlanTag.vlanID-3"',
                                      '-optionalEnabled', True)
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
                    self._handle.setMultiAttribute(trafficStream1 + '/highLevelStream:1/stack:"ipv6-2"/field:"ipv6.header.srcIp-7"',
                                              '-countValue', 1, '-fieldValue', src_ip, '-singleValue', src_ip,
                                             '-optionalEnabled', 'true', '-auto', 'false')
                    self._handle.setMultiAttribute(trafficStream1 + '/highLevelStream:1/stack:"ipv6-2"/field:"ipv6.header.dstIp-8"',
                                              '-countValue', 1, '-fieldValue', dst_ip, '-singleValue', dst_ip,
                                             '-optionalEnabled', 'true', '-auto', 'false')
        if protocol is not None:
            helpers.log('Adding Protocol Field in IP Header ..')
            if ethertype == '0800':
                self._handle.setMultiAttribute(trafficStream1 + '/highLevelStream:1/stack:"ipv4-2"/field:"ipv4.header.protocol-25"',
                                              '-countValue', 1, '-fieldValue', protocol,
                                             '-optionalEnabled', 'true', '-auto', 'false')
            elif ethertype == '86dd':
                self._handle.setMultiAttribute(trafficStream1 + '/highLevelStream:1/stack:"ipv4-6"/field:"ipv6.header.nextHeader-5"',
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
        
        if frameCount is not None:
            self._handle.setAttribute(trafficStream1 + '/highLevelStream:1/' + 'transmissionControl', '-type',
                                'fixedFrameCount')
            self._handle.setAttribute(trafficStream1 + '/highLevelStream:1/' + 'transmissionControl',
                                '-frameCount', frameCount)

        if flow == 'bi-directional':
            helpers.log('Adding Another  ixia end point set for Bi Directional Traffic..')
            endpointSet2 = self._handle.add(trafficStream1, 'endpointSet', '-name', 'l2u', '-sources', mac2,
                                      '-destinations', mac1)
            if crc is not None:
                self._handle.setAttribute(trafficStream1 + '/highLevelStream:2', '-crc', 'badCrc')
            
            self._handle.setAttribute(trafficStream1 + '/highLevelStream:2/' + 'frameSize', '-type', frameType)
            self._handle.setAttribute(trafficStream1 + '/highLevelStream:2/' + 'frameSize', '-fixedSize', frameSize)
            self._handle.setAttribute(trafficStream1 + '/highLevelStream:2/' + 'frameRate', '-type', frameMode)
            self._handle.setAttribute(trafficStream1 + '/highLevelStream:2/' + 'frameRate', '-rate', frameRate)
            if frameCount is not None:
                self._handle.setAttribute(trafficStream1 + '/highLevelStream:2/' + 'transmissionControl', '-type',
                                    'fixedFrameCount')
                self._handle.setAttribute(trafficStream1 + '/highLevelStream:2/' + 'transmissionControl', '-frameCount',
                                    frameCount)
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
                self._handle.setAttribute(trafficStream1 + '/highLevelStream:2/stack:"vlan-2"/field:"vlan.header.vlanTag.vlanID-3"',
                                          '-countValue', 1)
                self._handle.setAttribute(trafficStream1 + '/highLevelStream:2/stack:"vlan-2"/field:"vlan.header.vlanTag.vlanID-3"',
                                          '-fieldValue', vlan_id)
                self._handle.setAttribute(trafficStream1 + '/highLevelStream:2/stack:"vlan-2"/field:"vlan.header.vlanTag.vlanID-3"',
                                          '-optionalEnabled', True)
            
            if protocol is not None:
                helpers.log('Adding Protocol Field in IP Header ..')
                if ethertype == '0800':
                    self._handle.setMultiAttribute(trafficStream1 + '/highLevelStream:2/stack:"ipv4-2"/field:"ipv4.header.protocol-25"',
                                                  '-countValue', 1, '-fieldValue', protocol,
                                                 '-optionalEnabled', 'true', '-auto', 'false')
                elif ethertype == '86dd':
                    self._handle.setMultiAttribute(trafficStream1 + '/highLevelStream:2/stack:"ipv4-6"/field:"ipv6.header.nextHeader-5"',
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
                
        self._handle.setAttribute(self._handle.getList(trafficStream1, 'tracking')[0], '-trackBy', 'trackingenabled0')
        
        self._handle.commit()
        return trafficStream1

    def ixia_l2_add(self, **kwargs):
        '''
            This Helper Method created L2 related Config on IXIA to start Traffic with given arguments
        '''
        helpers.log("###Starting L2 IXIA ADD Config ...")
        ix_handle = self._handle
        ix_ports = [port for port in self._port_map_list.values()]
        s_mac = kwargs.get('src_mac', '00:11:23:00:00:01')
        d_mac = kwargs.get('dst_mac', '00:11:23:00:00:02')
        d_cnt = kwargs.get('d_cnt', 1)
        s_cnt = kwargs.get('s_cnt', 1)
        d_step = kwargs.get('d_step', '00:00:00:01:00:00')
        s_step = kwargs.get('s_step', '00:00:00:01:00:00')
        frame_rate = kwargs.get('frame_rate', 100)
        frame_cnt = kwargs.get('frame_cnt', None)
        self._frame_size = kwargs.get('frame_size', 70)
        frame_type = kwargs.get('frame_type', 'fixed')
        frame_mode = kwargs.get('frame_mode', 'framesPerSecond')
        name = kwargs.get('name', 'gobot_default')
        ethertype = kwargs.get('ethertype', None)
        vlan_id = kwargs.get('vlan_id', None)
        crc = kwargs.get('crc', None)
        no_arp = kwargs.get('no_arp', True)
        
        ix_tcl_server = self._tcl_server_ip
        flow = kwargs.get('flow', 'None')
        if ix_tcl_server is None or ix_ports is None or s_mac is None or d_mac is None:
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
        if match_uni1:
            create_topo.append(self._topology[match_uni1.group(1).lower()])
            create_topo.append(self._topology[match_uni1.group(2).lower()])
            stream_flow = 'uni-directional'
        elif match_uni2:
            create_topo.append(self._topology[match_uni2.group(2).lower()])
            create_topo.append(self._topology[match_uni2.group(1).lower()])
            stream_flow = 'uni-directional'
        elif match_bi:
            create_topo.append(self._topology[match_bi.group(2).lower()])
            create_topo.append(self._topology[match_bi.group(1).lower()])
            stream_flow = 'bi-directional'
        # Create Ether Device:
        mac_devices = self.ix_create_device_ethernet(create_topo, s_cnt, d_cnt, s_mac, d_mac, s_step, d_step)
        helpers.log('### Created Mac Devices with corrsponding Topos ...')
        # Create Traffic Stream:
        traffic_stream = self.ix_setup_traffic_streams_ethernet(mac_devices[0], mac_devices[1],
                                                       frame_type, self._frame_size, frame_rate, frame_mode,
                                                       frame_cnt, stream_flow, name, ethertype, vlan_id, crc, no_arp = no_arp)
        helpers.log('Created Traffic Stream : %s' % traffic_stream)
        self._traffic_stream[name] = traffic_stream
        return traffic_stream
    
    def ixia_l3_add_hosts(self, **kwargs):
        '''
            This methods adds ixia_l3 hosts and returns ip_Devices
        '''
        ix_handle = self._handle
        ix_ports = [port for port in self._port_map_list.values()]
        s_mac = kwargs.get('src_mac', '00:11:23:00:00:01')
        d_mac = kwargs.get('dst_mac', '00:11:23:00:00:02')
        d_cnt = kwargs.get('d_cnt', 1)
        s_cnt = kwargs.get('s_cnt', 1)
        d_step = kwargs.get('d_step', '00:00:00:01:00:00')
        s_step = kwargs.get('s_step', '00:00:00:01:00:00')
        s_ip = kwargs.get('src_ip', '20.0.0.1')
        d_ip = kwargs.get('dst_ip', '20.0.0.2')
        gw = kwargs.get('gw_ip', None)
        port_name = kwargs.get('ixia_port', None)
        ix_tcl_server = self._tcl_server_ip
        
        if ix_tcl_server is None or ix_ports is None or s_mac is None or d_mac is None:
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
            (ip_devices, mac_devices) = self.ix_create_device_ethernet_ip([self._topology[port_name]], s_mac, s_ip, gw)
            helpers.log('Created Mac Devices with corrsponding Topos ...')
            helpers.log ("Success Creating Ip Devices !!!")
            return ip_devices
    
    def ix_l3_add(self, **kwargs):
        ix_handle = self._handle
        ix_ports = [port for port in self._port_map_list.values()]
        src_mac = kwargs.get('src_mac', '00:11:23:00:00:01')
        dst_mac = kwargs.get('dst_mac', '00:11:23:00:00:02')
        d_cnt = kwargs.get('dnt_cnt', 1)
        s_cnt = kwargs.get('src_cnt', 1)
        dst_mac_step = kwargs.get('dst_mac_step', '00:00:00:01:00:00')
        src_mac_step = kwargs.get('src_mac_step', '00:00:00:01:00:00')
        frame_rate = kwargs.get('frame_rate', 100)
        frame_cnt = kwargs.get('frame_cnt', None)
        self._frame_size = kwargs.get('frame_size', 130)
        frame_type = kwargs.get('frame_type', 'fixed')
        frame_mode = kwargs.get('frame_mode', 'framesPerSecond')
        name = kwargs.get('name', 'gobot_default')
        ethertype = kwargs.get('ethertype', '0800')
        vlan_id = kwargs.get('vlan_id', None)
        crc = kwargs.get('crc', None)
        if ethertype == '0800':
            src_ip = kwargs.get('src_ip', '20.0.0.1')
            dst_ip = kwargs.get('dst_ip', '20.0.0.2')
            src_gw_ip = kwargs.get('src_gw', '20.0.0.2')
            dst_gw_ip = kwargs.get('dst_gw', '20.0.0.1')
            src_ip_step = kwargs.get('src_ip_step','0.0.0.1')
            dst_ip_step = kwargs.get('dst_ip_step', '0.0.0.1')
            no_arp = kwargs.get('no_arp', False)
        elif ethertype == '86dd':
            src_ip = kwargs.get('src_ip', '20.0.0.1')
            dst_ip = kwargs.get('dst_ip', '20.0.0.2')
            src_gw_ip = kwargs.get('src_gw', '20.0.0.2')
            dst_gw_ip = kwargs.get('dst_gw', '20.0.0.1')
            src_ip_step = kwargs.get('src_ip_step','0.0.0.1')
            dst_ip_step = kwargs.get('dst_ip_step', '0.0.0.1')
            no_arp = kwargs.get('no_arp', True)
        
        protocol = kwargs.get('protocol','6')
        src_port = kwargs.get('src_port', '6001')
        dst_port = kwargs.get('dst_port', '7001')
        
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
            # Map to Chassis Physhical Ports:
            if self.ix_map_vports_pyhsical_ports():
                helpers.log('### Successfully mapped vport to physical ixia ports..')
            else:
                helpers.log('Unable to connect to Ixia Chassis')
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
        if match_uni1:
            create_topo.append(self._topology[match_uni1.group(1).lower()])
            create_topo.append(self._topology[match_uni1.group(2).lower()])
            stream_flow = 'uni-directional'
        elif match_uni2:
            create_topo.append(self._topology[match_uni2.group(2).lower()])
            create_topo.append(self._topology[match_uni2.group(1).lower()])
            stream_flow = 'uni-directional'
        elif match_bi:
            create_topo.append(self._topology[match_bi.group(2).lower()])
            create_topo.append(self._topology[match_bi.group(1).lower()])
            stream_flow = 'bi-directional'
        # Create Ether Device with IpDevices:
        
        helpers.log('### Created Mac Devices with corrsponding Topos ...')
        helpers.log ("Success Creating Ip Devices !!!")
        # Start the Hosts to resolve Arps of GW
        
        # Create Traffic item with flows:
        traffic_stream1 = []
        if no_arp == 'True':
            helpers.log('Adding Stream with Ethernet devices as no_arp is True!!!')
            (ip_devices, mac_devices) = self.ix_create_device_ethernet_ip(create_topo, s_cnt, d_cnt, src_mac, dst_mac, src_mac_step, 
                                                                      dst_mac_step, src_ip, dst_ip, src_gw_ip, dst_gw_ip, src_ip_step,
                                                                      dst_ip_step, dst_mac, src_mac)
            helpers.log('Created Mac Devices : %s ' % mac_devices)
            
            traffic_stream = self.ix_setup_traffic_streams_ethernet(mac_devices[0], mac_devices[1],
                                                       frame_type, self._frame_size, frame_rate, frame_mode,
                                                       frame_cnt, stream_flow, name, src_ip = src_ip, dst_ip = dst_ip, protocol = protocol,
                                                       src_port = src_port, dst_port = dst_port, no_arp = no_arp, ethertype = ethertype)
            
            traffic_stream1.append(traffic_stream)
        else:
            helpers.log('Adding L3 Stream with ARP resolution for configured Gateway')
            (ip_devices, mac_devices) = self.ix_create_device_ethernet_ip(create_topo, s_cnt, d_cnt, src_mac, dst_mac, src_mac_step, 
                                                                      dst_mac_step, src_ip, dst_ip, src_gw_ip, dst_gw_ip, src_ip_step,
                                                                      dst_ip_step)
            self.ix_start_hosts()
            self._started_hosts = True
            traffic_item = self.ix_setup_traffic_streams_ethernet(ip_devices[0], ip_devices[1], frame_type, self._frame_size, frame_rate, frame_mode,
                                                         frame_cnt, stream_flow, name, protocol= protocol,
                                                         src_port = src_port, dst_port = dst_port, ethertype = ethertype)
            traffic_stream1.append(traffic_item)
        
        helpers.log('### Created Traffic Stream with Ip Devices ...')
        helpers.log ("Success Creating Ip Traffic Stream!!!")
        return traffic_stream1[0]
    
    def ix_start_traffic_ethernet(self, trafficHandle):
        '''
            Returns portStatistics after starting the traffic that is configured in Traffic Stream using Mac devices and Topologies
        '''
        helpers.log("### Starting Traffic")
        # self._handle.execute('startAllProtocols')
        time.sleep(2)
        if self._traffi_apply:
            helpers.log("#### No Need to Apply Ixia config already applied")
        else:
            self._handle.execute('apply', self._handle.getRoot() + 'traffic')
            helpers.log('###Applied traffic Config ..')
            self._traffi_apply = True
        time.sleep(2)
        # portStatistics = self._handle.getFilteredList(self._handle.getRoot()+'statistics', 'view', '-caption', 'Port Statistics')[0]
        time.sleep(2)
        self._handle.execute('startStatelessTrafficBlocking', trafficHandle)
        helpers.log("### Traffic Started")
        return True
    def ix_start_hosts(self, port_name = None):
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
                        helpers.log ('Sleeping 10 sec ..for Arps to get resolved !')
                        time.sleep(10)   # Sleep for the gw arp to get Resolved
                        device1 = self._handle.getList(self._topology[port], 'deviceGroup')
                        mac_device1 = self._handle.getList(device1[0], 'ethernet')
                        ip_device1 =  self._handle.getList(mac_device1[0], 'ipv4')
                        resolved_mac = self._handle.getAttribute(ip_device1[0], '-resolvedGatewayMac')    
                        helpers.log('Successfully Started L3 Hosts on Ixia Port : %s' % str(topo))
                        helpers.log(' Resolved MAC for Gw : %s' % str(resolved_mac))
                        match = re.match(r'.*Unresolved*.', resolved_mac[0])
                        if match:
                            if i < 3:
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
    
    def ix_fetch_port_stats(self):
        '''
            Returns Dictionary with Port Tx and Rx real time results
        '''
        handle = self._handle
        port_stats = {}
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
                    port_stat['received_frame_rate'] = value
#                 if column == 'Data Integrity Frames Rx.':
#                     port_stat['received_invalid_frames'] = value
                if column == 'CRC Errors':
                    port_stat['received_crc_errored_frames'] = value
                if column == 'Bytes Rx.':
                    frames = int(value) / int(self._frame_size)
                    port_stat['received_frames'] = str(frames)                    
            port_stats[port_stat['port']] = port_stat
        return port_stats

    def ix_stop_traffic(self, traffic_stream = None):
        '''
            Stops the traffis and returns port stats
            Ex Usage : IxStopTraffic(ix_handle, traffic_stream)
        '''
        handle = self._handle
        helpers.log("Stopping Traffic")
        if traffic_stream is None:
            helpers.log('No Traffic Stream is given, so stopping all the traffic running on this ixia Session...')
            self._handle.execute('stop', self._handle.getRoot() + 'traffic')
        else:
            handle.execute('stopStatelessTraffic', traffic_stream)
            helpers.log("Printing Statistics")
            port_stats = self.ix_fetch_port_stats()
            helpers.log("Port Stats : \n %s" % port_stats)
        helpers.log('Successfully Stopped the traffic for Stream %s ' % str(traffic_stream))
        return True
