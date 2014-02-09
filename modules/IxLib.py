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
        mac_mults = [s_cnt, d_cnt]
        mac_steps = [s_step, d_step]
        macs = [s_mac, d_mac]
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

    def ix_setup_traffic_streams_ethernet(self, mac1, mac2, frameType, frameSize, frameRate,
                                      frameMode, frameCount, flow, name, ethertype=None, vlan_id=None, crc=None):
        '''
            Returns traffic stream with 2 flows with provided mac sources
            Ex Usage:
                IxLib.IxSetupTrafficStreamsEthernet(ixNet, mac_devices[0], mac_devices[1], frameType, frameSize, frameRate, frameMode)
        '''
        trafficStream1 = self._handle.add(self._handle.getRoot() + 'traffic', 'trafficItem', '-name',
                                    name, '-allowSelfDestined', False, '-trafficItemType',
                                    'l2L3', '-enabled', True, '-transmitMode', 'interleaved',
                                    '-biDirectional', False, '-trafficType', 'ethernetVlan', '-hostsPerNetwork', '1')
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
            print('Adding Vlan ID: %s !!!' % vlan_id)
            self._handle.setAttribute(trafficStream1 + '/highLevelStream:1/stack:"vlan-2"/field:"vlan.header.vlanTag.vlanID-3"',
                                      '-countValue', 1)
            self._handle.setAttribute(trafficStream1 + '/highLevelStream:1/stack:"vlan-2"/field:"vlan.header.vlanTag.vlanID-3"',
                                      '-fieldValue', vlan_id)
            self._handle.setAttribute(trafficStream1 + '/highLevelStream:1/stack:"vlan-2"/field:"vlan.header.vlanTag.vlanID-3"',
                                      '-optionalEnabled', True)
            
            
            
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
                print('Adding Vlan ID: %s !!!' % vlan_id)
                self._handle.setAttribute(trafficStream1 + '/highLevelStream:2/stack:"vlan-2"/field:"vlan.header.vlanTag.vlanID-3"',
                                          '-countValue', 1)
                self._handle.setAttribute(trafficStream1 + '/highLevelStream:2/stack:"vlan-2"/field:"vlan.header.vlanTag.vlanID-3"',
                                          '-fieldValue', vlan_id)
                self._handle.setAttribute(trafficStream1 + '/highLevelStream:2/stack:"vlan-2"/field:"vlan.header.vlanTag.vlanID-3"',
                                          '-optionalEnabled', True)
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
                                                       frame_cnt, stream_flow, name, ethertype, vlan_id, crc)
        helpers.log('Created Traffic Stream : %s' % traffic_stream)
        self._traffic_stream[name] = traffic_stream
        return traffic_stream

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
                    frames = int(value) / self._frame_size
                    port_stat['received_frames'] = frames                    
            port_stats[port_stat['port']] = port_stat
        return port_stats

    def ix_stop_traffic(self, traffic_stream):
        '''
            Stops the traffis and returns port stats
            Ex Usage : IxStopTraffic(ix_handle, traffic_stream)
        '''
        handle = self._handle
        helpers.log("### Stopping Traffic")
        handle.execute('stopStatelessTraffic', traffic_stream)
        helpers.log("### Printing Statistics")
        port_stats = self.ix_fetch_port_stats()
        helpers.log("### Port Stats : \n %s" % port_stats)
        return True
