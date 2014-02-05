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
        
    def port_map_list(self, ports):
        # something happens here
        #self._port_map_list = <something>
        port_map_list = {}
        for port in ports.iteritems():
            match = re.match(r'(\d+)/(\d+)', port[1].lower())
            port_map_list[port[0].lower()] = (self._chassis_ip, match.group(1), match.group(2)) 
        return port_map_list
    
    def ix_connect(self):
        self.handle = IxNetwork.IxNet()
        self.handle.connect(self._tcl_server_ip, '-port', self._tcl_server_port,
                        '-version', self._ix_version)
        ### clear the configuration
        asyncHandle = self.handle.setAsync().execute('newConfig')
        self.handle.wait(asyncHandle)
        
    def ix_create_vports(self, vport_names):
        '''
            Returns created vports with the vports names provided
        '''
        created_vports = []
        helpers.log("### creating vports with names : %s " % str(vport_names))
        for port in self._port_map_list.iteritems():
            created_vports.append(self.handle.add(self.handle.getRoot(), 'vport', '-name', port[0]))
        #Running remapIds As per
        # IXIA config pushing to Ixia chassis
        for vport in created_vports:
            self._vports.append(self.handle.remapIds(vport)[0])
        self.handle.commit()
        helpers.log("### Done creating vPorts")

    def ix_connect_chassis(self):
        '''
            Returns True or False after adding vports to given Physical IXIA ports
        '''
        chassis = self.handle.add(self.handle.getRoot()+'availableHardware', 'chassis', '-hostname', self._chassis_ip)
        self.handle.commit()
        chassis = self.handle.remapIds(chassis)[0]
        for (ixport, vport) in zip(self._port_map_list.values(), self._vports):
            card = str(ixport[1])
            port = str(ixport[2])
            self.handle.setAttribute(vport, '-connectedTo', chassis+'/card:'+card+'/port:'+port)
        self.handle.commit()
        for vport in self._vports:
            while self.handle.getAttribute(vport, '-state') != 'up':
                time.sleep(2)
        return True

    def ix_create_topo(self):
        '''
            RETURNS IXIA topology list object adding a topo for each vport in vports
        '''
        helpers.log("### Adding %s topologies" % len(self._vports))
        for vport in self._vports:
            self.handle.add(self.handle.getRoot(), 'topology', '-vports', vport)
        self.handle.commit()
        topology = self.handle.getList(self.handle.getRoot(), 'topology')
        helpers.log("### Done adding %s topologies" % len(self._vports))
        return topology
    
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
            self.handle.add(topo, 'deviceGroup')
        self.handle.commit()
        topo_devices = []
        eth_devices = []
        for topo in topology:
            dev_grp = self.handle.getList(topo, 'deviceGroup')
            topo_device = self.handle.remapIds(dev_grp)[0]
            topo_devices.append(topo_device)
        for (topo_device, multi) in zip(topo_devices, mac_mults):
            print '### topo device : ', topo_device
            self.handle.setAttribute(topo_device, '-multiplier', multi)
            eth_devices.append(self.handle.add(topo_device, 'ethernet'))
        self.handle.commit()
        mac_devices = [] # as this are added to ixia need to remap as per ixia API's
        for eth_device in eth_devices:
            mac_devices.append(self.handle.remapIds(eth_device)[0])
        for (mac_device, mult, mac_step, mac) in zip(mac_devices, mac_mults, mac_steps, macs):
            if mult <= 1:
                m1 = self.handle.setAttribute(self.handle.getAttribute(mac_device, '-mac')+'/singleValue', '-value', mac)
            else:
                helpers.log('###Adding Multipier ...')
                m1 = self.handle.setMultiAttribute(self.handle.getAttribute(mac_device, '-mac')+'/counter', '-direction',
                                              'increment', '-start', mac, '-step', mac_step)
        self.handle.commit()
        print " ## adding Name ", topology[0], topology[1]
        print " ## adding Name ", mac_devices[0], mac_devices[1]
        for topo in topology:
            self.handle.setAttribute(topo, '-name', 'SND_RCV Topology')
        for mac_device in mac_devices:
            self.handle.setAttribute(mac_device, '-name', 'SND_RCV Device')
        self.handle.commit()
        helpers.log("### Done adding two device groups")
        return mac_devices
    
    def ix_setup_traffic_streams_ethernet(self, mac1, mac2, frameType, frameSize, frameRate,
                                      frameMode, frameCount, flow):
        '''
            Returns traffic stream with 2 flows with provided mac sources
            Ex Usage:
                IxLib.IxSetupTrafficStreamsEthernet(ixNet, mac_devices[0], mac_devices[1], frameType, frameSize, frameRate, frameMode)
        '''
        trafficStream1 = self.handle.add(self.handle.getRoot()+'traffic', 'trafficItem', '-name',
                                    'Ethernet L2', '-allowSelfDestined', False, '-trafficItemType',
                                    'l2L3', '-enabled', True, '-transmitMode', 'interleaved',
                                    '-biDirectional', False, '-trafficType', 'ethernetVlan', '-hostsPerNetwork', '1')
        self.handle.commit()
        endpointSet1 = self.handle.add(trafficStream1, 'endpointSet', '-name', 'l2u', '-sources', mac1,
                                  '-destinations', mac2)
        self.handle.setAttribute(trafficStream1, '-enabled', True)
        self.handle.setAttribute(trafficStream1+'/highLevelStream:1/'+'frameSize', '-type', frameType)
        self.handle.setAttribute(trafficStream1+'/highLevelStream:1/'+'frameSize', '-fixedSize', frameSize)
        self.handle.setAttribute(trafficStream1+'/highLevelStream:1/'+'frameRate', '-type', frameMode)
        self.handle.setAttribute(trafficStream1+'/highLevelStream:1/'+'frameRate', '-rate', frameRate)
        if frameCount is not None:
            self.handle.setAttribute(trafficStream1+'/highLevelStream:1/'+'transmissionControl', '-type',
                                'fixedFrameCount')
            self.handle.setAttribute(trafficStream1+'/highLevelStream:1/'+'transmissionControl',
                                '-frameCount', frameCount + 10000)
        if flow == 'bi-directional':
            helpers.log('Adding Another  ixia end point set for Bi Directional Traffic..')
            endpointSet2 = self.handle.add(trafficStream1, 'endpointSet', '-name', 'l2u', '-sources', mac2,
                                      '-destinations', mac1)
            self.handle.setAttribute(trafficStream1+'/highLevelStream:2/'+'frameSize', '-type', frameType)
            self.handle.setAttribute(trafficStream1+'/highLevelStream:2/'+'frameSize', '-fixedSize', frameSize)
            self.handle.setAttribute(trafficStream1+'/highLevelStream:2/'+'frameRate', '-type', frameMode)
            self.handle.setAttribute(trafficStream1+'/highLevelStream:2/'+'frameRate', '-rate', frameRate)
            if frameCount is not None:
                self.handle.setAttribute(trafficStream1+'/highLevelStream:2/'+'transmissionControl', '-type',
                                    'fixedFrameCount')
                self.handle.setAttribute(trafficStream1+'/highLevelStream:2/'+'transmissionControl', '-frameCount',
                                    frameCount)
        self.handle.setAttribute(self.handle.getList(trafficStream1, 'tracking')[0], '-trackBy', 'trackingenabled0')
        self.handle.commit()
        return trafficStream1
    
    def IxStartTrafficEthernet(self, trafficHandle):
        '''
            Returns portStatistics after starting the traffic that is configured in Traffic Stream using Mac devices and Topologies
            Ex Usage:
                IxLib.IxStartTrafficEthernet(ixNet,trafficStream)
        '''
        helpers.log("### Starting Traffic")
        self.handle.execute('startAllProtocols')
        time.sleep(2)
        self.handle.execute('apply', self.handle.getRoot()+'traffic')
        time.sleep(2)
        portStatistics = self.handle.getFilteredList(self.handle.getRoot()+'statistics', 'view', '-caption', 'Port Statistics')[0]
        time.sleep(2)
        self.handle.execute('startStatelessTraffic', trafficHandle)
        helpers.log("### Traffic Started")
        return portStatistics
    
    def IXIA_L2_ADD(self, **kwargs):
        '''
            This Helper Method created L2 related Config on IXIA to start Traffic with given arguments
            Ex Usage:
                ix_ports = [('10.192.85.151',2, 7), ('10.192.85.151', 2, 8)]
                L2_stream_args = {ports : ix_ports, src_mac :  '00:11:23:00:00:01', dst_mac : '00:11:23:00:00:02', d_cnt : 10, s_cnt : 50, \
                frame_rate : 10000, frame_cnt : 90000, frame_size : 64, ix_tcl_server : '10.194.64.183'. 'flow' : 'bi-directional'}
                IXIA_L2_ADD(**L2_stream_args)
        '''
        helpers.log("###Starting L2 IXIA ADD Config ...")
        ix_handle = self.handle
        ix_ports = kwargs.get('ports', None)
        s_mac = kwargs.get('src_mac', None)
        d_mac = kwargs.get('dst_mac', None)
        d_cnt = kwargs.get('d_cnt', 1)
        s_cnt = kwargs.get('s_cnt', 1)
        d_step = kwargs.get('d_step', '00:00:00:01:00:00')
        s_step = kwargs.get('s_step', '00:00:00:01:00:00')
        frame_rate = kwargs.get('frame_rate', 100)
        frame_cnt = kwargs.get('frame_cnt', None)
        frame_size = kwargs.get('frame_size', 70)
        frame_type = kwargs.get('frame_type', 'fixed')
        frame_mode = kwargs.get('frame_mode', 'framesPerSecond')
        ix_tcl_server = kwargs.get('ix_tcl_server', None)
        flow = kwargs.get('flow', 'bi-directional')
        vport_names = ['vport1_sdk', 'vport2_sdk']
        ix_chassis = ix_ports[0][0]
        if ix_tcl_server is None or ix_ports is None or s_mac is None or d_mac is None:
            helpers.warn('Please Provide Required Args for IXIA_L2_ADD helper method !!')
            raise IxNetwork.IxNetError('Please provide Required Args for IXIA_L2_ADD helper method !!')
        get_version = ix_handle.getVersion()
        helpers.log("###Current Version of Ixia Chassis : %s " % get_version)
        ix_handle.setDebug(False)    # Set Debug True to print Ixia Server Interactions
        # Create vports:
        vports = IxCreateVports(ix_handle, vport_names)
        helpers.log('### vports Created : %s' % vports)
        # Map to Chassis Physhical Ports:
        if IxConnectChassis(ix_handle, vports, ix_chassis, ix_ports):
            helpers.log('### Successfully mapped vport to physical ixia ports..')
        else:
            helpers.warn('Unable to connect to Ixia Chassis')
            return False
        # Create Topo:
        topology = IxCreateTopo(ix_handle, vports)
        helpers.log('### Topology Created: %s' % topology)
        #Create Ether Device:
        mac_devices = IxCreateDeviceEthernet(ix_handle, topology, s_cnt, d_cnt, s_mac, d_mac, s_step, d_step)
        helpers.log('### Created Mac Devices with corrsponding Topos ...')
        #Create Traffic Stream:
        traffic_stream = IxSetupTrafficStreamsEthernet(ix_handle, mac_devices[0], mac_devices[1],\
                                                       frame_type, frame_size, frame_rate, frame_mode, frame_cnt, flow)
        helpers.log('Created Traffic Stream : %s' % traffic_stream)
        return traffic_stream
    
    def ix_fetch_port_stats(handle):
        '''
            Returns Dictionary with Port Tx and Rx real time results
        '''
        port_stats = []
        portStatistics = handle.getFilteredList(handle.getRoot()+'statistics', 'view', '-caption', 'Port Statistics')[0]
        col_names = handle.getAttribute(portStatistics+'/page', '-columnCaptions')
        stats = handle.getAttribute(portStatistics+'/page', '-rowValues')
        for stat in stats:
            port_stat = {}
            for column, value in zip(col_names, stat[0]):
                if column == 'Stat Name':
                    port_stat['port'] = value
                if column == 'Frames Tx.':
                    port_stat['Tx'] = value
                if column == 'Valid Frames Rx.':
                    port_stat['Rx'] = value
                if column == 'Frames Tx. Rate':
                    port_stat['TxRate'] = value
                if column == 'Valid Frames Rx. Rate':
                    port_stat['RxRate'] = value
            port_stats.append(port_stat)
        return port_stats
    
    def IxStopTraffic(handle, traffic_stream):
        '''
            Stops the traffis and returns port stats
            Ex Usage : IxStopTraffic(ix_handle, traffic_stream)
        '''
        helpers.log("### Stopping Traffic")
        handle.execute('stopStatelessTraffic', traffic_stream)
        helpers.log("### Printing Statistics")
        port_stats = ix_fetch_port_stats(handle)
        helpers.log("### Port Stats : \n %s" % port_stats)
        return port_stats
