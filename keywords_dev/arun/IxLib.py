#!/usr/bin/env python
import autobot.helpers as helpers
import time
from vendors.Ixia import IxNetwork
def IxConnect(ixClientIP, ixClientIxNetTclServPortNo, ixClientIxNetVer):
    handle = IxNetwork.IxNet()
    handle.connect(ixClientIP, '-port', ixClientIxNetTclServPortNo,
                    '-version', ixClientIxNetVer)
    ### clear the configuration"
    asyncHandle = handle.setAsync().execute('newConfig')
    handle.wait(asyncHandle)
    return handle

def IxCreateVports(handle, vport_names):
    '''
        Returns created vports with the vports names provided
        Ex Usages:
            vport_names = ['vport1_eclipse', 'vport2_eclipse']
            IxCreateVports(handle = handle, vport_names)
            IxCreateVports(handle = handle, vport_names = vport_names)
    '''
    created_vports = []
    return_vports = []
    helpers.log("### creating vports with names : %s " % str(vport_names))
    for vport in vport_names:
        created_vports.append(handle.add(handle.getRoot(), 'vport', '-name', vport))
    #Running remapIds As per
    # IXIA config pushing to Ixia chassis
    for vport in created_vports:
        return_vports.append(handle.remapIds(vport)[0])
    handle.commit()
    helpers.log("### Done creating vPorts")
    return return_vports

def IxConnectChassis(handle, vports, ixChassis, ixPorts):
    '''
        Returns True or False after apping vports to given Physical IXIA ports
        Ex Usages:
            IxConnectChassis(ixNet, vports, ixChassis, ixPorts)
            IxConnectChassis(vports = vports, ixChassis = '10.193.28.20', ixNet = ixia_handle, ixPorts = ixia_ports)
    '''
    if len(ixPorts) != len(vports):
        raise IxNetwork.IxNetError('Please provide same No of vports as Physical Ixia_ports')
    else:
        chassis = handle.add(handle.getRoot()+'availableHardware', 'chassis', '-hostname', ixChassis)
        handle.commit()
        chassis = handle.remapIds(chassis)[0]
        for (ixport, vport) in zip(ixPorts, vports):
            card = str(ixport[1])
            port = str(ixport[2])
            handle.setAttribute(vport, '-connectedTo', chassis+'/card:'+card+'/port:'+port)
        handle.commit()
        for vport in vports:
            while handle.getAttribute(vport, '-state') != 'up':
                time.sleep(2)
        return True

def IxCreateTopo(handle, vports):
    '''
        RETURNS IXIA topology list object adding a topo for each vport in vports
        Ex Usage:
        IxCreateTopo(handle, vports) # vports should created using IxCreateVports method by passing vport_names
    '''
    helpers.log("### Adding %s topologies" % len(vports))
    for vport in vports:
        handle.add(handle.getRoot(), 'topology', '-vports', vport)
    handle.commit()
    topology = handle.getList(handle.getRoot(), 'topology')
    helpers.log("### Done adding %s topologies" % len(vports))
    return topology

def IxCreateDeviceEthernet(handle, topology, s_cnt, d_cnt, s_mac, d_mac, s_step, d_step):
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
        handle.add(topo, 'deviceGroup')
    handle.commit()
    topo_devices = []
    eth_devices = []
    for topo in topology:
        dev_grp = handle.getList(topo, 'deviceGroup')
        topo_device = handle.remapIds(dev_grp)[0]
        topo_devices.append(topo_device)
    for (topo_device, multi) in zip(topo_devices, mac_mults):
        print '### topo device : ', topo_device
        handle.setAttribute(topo_device, '-multiplier', multi)
        eth_devices.append(handle.add(topo_device, 'ethernet'))
    handle.commit()
    mac_devices = [] # as this are added to ixia need to remap as per ixia API's
    for eth_device in eth_devices:
        mac_devices.append(handle.remapIds(eth_device)[0])
    for (mac_device, mult, mac_step, mac) in zip(mac_devices, mac_mults, mac_steps, macs):
        if mult <= 1:
            m1 = handle.setAttribute(handle.getAttribute(mac_device, '-mac')+'/singleValue', '-value', mac)
        else:
            helpers.log('###Adding Multipier ...')
            m1 = handle.setMultiAttribute(handle.getAttribute(mac_device, '-mac')+'/counter', '-direction',
                                          'increment', '-start', mac, '-step', mac_step)
    handle.commit()
    print " ## adding Name ", topology[0], topology[1]
    print " ## adding Name ", mac_devices[0], mac_devices[1]
    for topo in topology:
        handle.setAttribute(topo, '-name', 'SND_RCV Topology')
    for mac_device in mac_devices:
        handle.setAttribute(mac_device, '-name', 'SND_RCV Device')
    handle.commit()
    helpers.log("### Done adding two device groups")
    return mac_devices

def IxSetupTrafficStreamsEthernet(handle, mac1, mac2, frameType, frameSize, frameRate,
                                  frameMode, frameCount, flow):
    '''
        Returns traffic stream with 2 flows with provided mac sources
        Ex Usage:
            IxLib.IxSetupTrafficStreamsEthernet(ixNet, mac_devices[0], mac_devices[1], frameType, frameSize, frameRate, frameMode)
    '''
    trafficStream1 = handle.add(handle.getRoot()+'traffic', 'trafficItem', '-name',
                                'Ethernet L2', '-allowSelfDestined', False, '-trafficItemType',
                                'l2L3', '-enabled', True, '-transmitMode', 'interleaved',
                                '-biDirectional', False, '-trafficType', 'ethernetVlan', '-hostsPerNetwork', '1')
    handle.commit()
    endpointSet1 = handle.add(trafficStream1, 'endpointSet', '-name', 'l2u', '-sources', mac1,
                              '-destinations', mac2)
    handle.setAttribute(trafficStream1, '-enabled', True)
    handle.setAttribute(trafficStream1+'/highLevelStream:1/'+'frameSize', '-type', frameType)
    handle.setAttribute(trafficStream1+'/highLevelStream:1/'+'frameSize', '-fixedSize', frameSize)
    handle.setAttribute(trafficStream1+'/highLevelStream:1/'+'frameRate', '-type', frameMode)
    handle.setAttribute(trafficStream1+'/highLevelStream:1/'+'frameRate', '-rate', frameRate)
    if frameCount is not None:
        handle.setAttribute(trafficStream1+'/highLevelStream:1/'+'transmissionControl', '-type',
                            'fixedFrameCount')
        handle.setAttribute(trafficStream1+'/highLevelStream:1/'+'transmissionControl',
                            '-frameCount', frameCount + 10000)
    if flow == 'bi-directional':
        helpers.log('Adding Another  ixia end point set for Bi Directional Traffic..')
        endpointSet2 = handle.add(trafficStream1, 'endpointSet', '-name', 'l2u', '-sources', mac2,
                                  '-destinations', mac1)
        handle.setAttribute(trafficStream1+'/highLevelStream:2/'+'frameSize', '-type', frameType)
        handle.setAttribute(trafficStream1+'/highLevelStream:2/'+'frameSize', '-fixedSize', frameSize)
        handle.setAttribute(trafficStream1+'/highLevelStream:2/'+'frameRate', '-type', frameMode)
        handle.setAttribute(trafficStream1+'/highLevelStream:2/'+'frameRate', '-rate', frameRate)
        if frameCount is not None:
            handle.setAttribute(trafficStream1+'/highLevelStream:2/'+'transmissionControl', '-type',
                                'fixedFrameCount')
            handle.setAttribute(trafficStream1+'/highLevelStream:2/'+'transmissionControl', '-frameCount',
                                frameCount)
    handle.setAttribute(handle.getList(trafficStream1, 'tracking')[0], '-trackBy', 'trackingenabled0')
    handle.commit()
    return trafficStream1

def IxStartTrafficEthernet(handle, trafficHandle):
    '''
        Returns portStatistics after starting the traffic that is configured in Traffic Stream using Mac devices and Topologies
        Ex Usage:
            IxLib.IxStartTrafficEthernet(ixNet,trafficStream)
    '''
    helpers.log("### Starting Traffic")
    handle.execute('startAllProtocols')
    time.sleep(2)
    handle.execute('apply', handle.getRoot()+'traffic')
    time.sleep(2)
    portStatistics = handle.getFilteredList(handle.getRoot()+'statistics', 'view', '-caption', 'Port Statistics')[0]
    time.sleep(2)
    handle.execute('startStatelessTraffic', trafficHandle)
    helpers.log("### Traffic Started")
    return portStatistics

def IXIA_L2_ADD(**kwargs):
    '''
        This Helper Method created L2 related Config on IXIA to start Traffic with given arguments
        Ex Usage:
            ix_ports = [('10.192.85.151',2, 7), ('10.192.85.151', 2, 8)]
            L2_stream_args = {ports : ix_ports, src_mac :  '00:11:23:00:00:01', dst_mac : '00:11:23:00:00:02', d_cnt : 10, s_cnt : 50, \
            frame_rate : 10000, frame_cnt : 90000, frame_size : 64, ix_tcl_server : '10.194.64.183'. 'flow' : 'bi-directional'}
            IXIA_L2_ADD(**L2_stream_args)
    '''
    helpers.log("###Starting L2 IXIA ADD Config ...")
    ix_handle = kwargs.get('ix_handle', None)
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

def IxStopTraffic(handle,traffic_stream) :
    '''
        Stops the traffis and returns port stats
        Ex Usage : IxStopTraffic(ix_handle, traffic_stream)
    '''
    helpers.log("### Stopping Traffic")
    handle.execute('stopStatelessTraffic',traffic_stream)
    helpers.log("### Printing Statistics")
    port_stats = ix_fetch_port_stats(handle)
    helpers.log("### Port Stats : \n %s" % port_stats)
    return port_stats