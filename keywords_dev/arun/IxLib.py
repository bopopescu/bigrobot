#!/usr/bin/env python
import autobot.helpers as helpers
import autobot.test as test
import os
import sys
import time
from vendors.Ixia import IxNetwork

def IxConnect(ixClientIP,ixClientIxNetTclServPortNo,ixClientIxNetVer):
    handle = IxNetwork.IxNet()
    handle.connect(ixClientIP, '-port',ixClientIxNetTclServPortNo, '-version',ixClientIxNetVer)
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
    # Running remapIds As per IXIA config pushing to Ixia chassis    
    for vport in created_vports:
        return_vports.append(handle.remapIds(vport)[0])
    handle.commit();
    helpers.log("### Done creating vPorts")

    return return_vports

def IxConnectChassis(handle,vports,ixChassis,ixPorts) :
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
        for (ixport,vport) in zip(ixPorts, vports):
            card = str(ixport[1])
            port = str(ixport[2])
            handle.setAttribute(vport, '-connectedTo', chassis+'/card:'+card+'/port:'+port)
        handle.commit()
        
        for vport in vports:
            while(handle.getAttribute(vport, '-state') != 'up' ):
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
        handle.add(handle.getRoot(),'topology','-vports',vport)
    handle.commit()
    topology = handle.getList(handle.getRoot(),'topology')
    helpers.log("### Done adding %s topologies" % len(vports))
    return topology

def IxCreateDeviceEthernet(handle, topology, mac_mults, macs, mac_steps) :
    '''
        RETURN IXIA MAC DEVICES mapped with Topologies created with vports and added increment values accordingly
        Ex Usage:
        IxLib.IxCreateDeviceEthernet(ixNet,topology, mac_mults =  mac_mults, macs = macs, mac_steps = mac_steps)
    '''
    helpers.log("### Adding %s device groups" % len(topology))
    
    for topo in topology:
        handle.add(topo,'deviceGroup')
    handle.commit()
    topo_devices = []
    eth_devices = []
    for topo in topology:
        dev_grp = handle.getList(topo,'deviceGroup')
        topo_device = handle.remapIds(dev_grp)[0]
        topo_devices.append(topo_device)
        
    for (topo_device, multi) in zip(topo_devices, mac_mults):
        print '### topo device : ', topo_device
        handle.setAttribute(topo_device, '-multiplier', multi)
        eth_devices.append(handle.add(topo_device,'ethernet'))
    handle.commit()
    mac_devices = [] # as this are added to ixia need to remap as per ixia API's
    
    for eth_device in eth_devices:
        mac_devices.append(handle.remapIds(eth_device)[0])
        
    for (mac_device, mult, mac_step, mac) in zip(mac_devices, mac_mults, mac_steps, macs):
        if mult <= 1 :
            m1 = handle.setAttribute(handle.getAttribute(mac_device, '-mac')+'/singleValue', '-value', mac)
        else :     
            helpers.log('###Adding Multipier ...')   
            m1 = handle.setMultiAttribute(handle.getAttribute(mac_device,'-mac')+'/counter','-direction','increment','-start', mac,'-step', mac_step)
    
    handle.commit()
    
    print " ## adding Name ", topology[0], topology[1]
    print " ## adding Name ", mac_devices[0], mac_devices[1]
    
    for topo in topology:
        handle.setAttribute(topo,'-name','SND_RCV Topology')
    for mac_device in mac_devices:
        handle.setAttribute(mac_device,'-name','SND_RCV Device')
    handle.commit()
    helpers.log("### Done adding two device groups")
    return (mac_devices)

def IxSetupTrafficStreamsEthernet(handle,mac1,mac2,frameType,frameSize,frameRate,frameMode):
    '''
        Returns traffic stream with 2 flows with provided mac sources 
        Ex Usage:
            IxLib.IxSetupTrafficStreamsEthernet(ixNet, mac_devices[0], mac_devices[1], frameType, frameSize, frameRate, frameMode)
    '''
    trafficStream1 = handle.add(handle.getRoot()+'traffic','trafficItem','-name','Ethernet L2','-allowSelfDestined',False,'-trafficItemType','l2L3','-enabled',True,'-transmitMode','interleaved','-biDirectional',False,'-trafficType','ethernetVlan','-hostsPerNetwork','1')
    handle.commit()
    endpointSet1 = handle.add(trafficStream1, 'endpointSet','-name','l2u','-sources', mac1,'-destinations', mac2)
    endpointSet2 = handle.add(trafficStream1, 'endpointSet','-name','l2u','-sources', mac2,'-destinations', mac1)
    handle.commit()
    handle.setAttribute(trafficStream1,'-enabled',True)
    handle.setAttribute(trafficStream1+'/highLevelStream:1/'+'frameSize','-type',frameType)
    handle.setAttribute(trafficStream1+'/highLevelStream:1/'+'frameSize','-fixedSize',frameSize)
    handle.setAttribute(trafficStream1+'/highLevelStream:1/'+'frameRate','-type',frameMode)
    handle.setAttribute(trafficStream1+'/highLevelStream:1/'+'frameRate','-rate',frameRate)
    handle.setAttribute(trafficStream1+'/highLevelStream:2/'+'frameSize','-type',frameType)
    handle.setAttribute(trafficStream1+'/highLevelStream:2/'+'frameSize','-fixedSize',frameSize)
    handle.setAttribute(trafficStream1+'/highLevelStream:2/'+'frameRate','-type',frameMode)
    handle.setAttribute(trafficStream1+'/highLevelStream:2/'+'frameRate','-rate',frameRate)
    handle.setAttribute(handle.getList(trafficStream1,'tracking')[0],'-trackBy','trackingenabled0')
    handle.commit()
    return trafficStream1

def IxStartTrafficEthernet(handle,trafficHandle) :
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
    handle.execute('startStatelessTraffic',trafficHandle)
    helpers.log("### Traffic Started")
    return portStatistics

def IxStopTraffic(handle,trafficHandle,portStatistics) :
    '''
        Stops the traffis and returns port stats
    '''
    helpers.log("### Stopping Traffic")
    handle.execute('stopStatelessTraffic',trafficHandle)
    helpers.log("### Printing Statistics")
    #print handle.getAttribute(portStatistics+'/page', '-columnCaptions')
    #print handle.getAttribute(portStatistics+'/page', '-rowValues')
#['Stat Name', 'Port Name', 'Line Speed', 'Link State', 'Frames Tx.', 'Valid Frames Rx.', 'Frames Tx. Rate', 'Valid Frames Rx. Rate', 'Data Integrity Frames Rx.', 'Data Integrity Errors', 'Bytes Tx.', 'Bytes Rx.', 'Bits Sent', 'Bits Received', 'Bytes Tx. Rate', 'Tx. Rate (bps)', 'Tx. Rate (Kbps)', 'Tx. Rate (Mbps)', 'Bytes Rx. Rate', 'Rx. Rate (bps)', 'Rx. Rate (Kbps)', 'Rx. Rate (Mbps)', 'Scheduled Frames Tx.', 'Scheduled Frames Tx. Rate', 'Control Frames Tx', 'Control Frames Rx', 'Ethernet OAM Information PDUs Sent', 'Ethernet OAM Information PDUs Received', 'Ethernet OAM Event Notification PDUs Received', 'Ethernet OAM Loopback Control PDUs Received', 'Ethernet OAM Organisation PDUs Received', 'Ethernet OAM Variable Request PDUs Received', 'Ethernet OAM Variable Response Received', 'Ethernet OAM Unsupported PDUs Received', 'Rx Pause Priority Group 0 Frames', 'Rx Pause Priority Group 1 Frames', 'Rx Pause Priority Group 2 Frames', 'Rx Pause Priority Group 3 Frames', 'Rx Pause Priority Group 4 Frames', 'Rx Pause Priority Group 5 Frames', 'Rx Pause Priority Group 6 Frames', 'Rx Pause Priority Group 7 Frames', 'Misdirected Packet Count', 'CRC Errors']
    port1stats = handle.getAttribute(portStatistics+'/page', '-rowValues')[0]
    port2stats = handle.getAttribute(portStatistics+'/page', '-rowValues')[1]
    return (port1stats, port2stats)

def IxCreateDeviceIP(handle,mac1,mac2,Mac1Mult,Mac2Mult,addr1,addr1Step,addr2Step,addr2,prefix1,prefix2) :
    helpers.log("### Add ipv4")
    handle.add(mac1,'ipv4')
    handle.commit()
    ipA1 = handle.getList(mac1,'ipv4')
    ip1 = handle.remapIds(ipA1)[0]
    mvAdd1 = handle.getAttribute(ip1,'-address')
    mvGw1 = handle.getAttribute(ip1,'-gatewayIp')
    if Mac1Mult <= 1 :
        i1 = handle.setAttribute(mvAdd1+'/singleValue','-value',addr1)
    else :        
        i1 = handle.setMultiAttribute(mvAdd1+'/counter','-start',addr1,'-step',addr1Step)
    handle.setAttribute(mvGw1+'/singleValue','-value',addr2)
    handle.setAttribute(handle.getAttribute(ip1,'-prefix')+'/singleValue','-value',prefix1)
    handle.commit()
    handle.add(mac2,'ipv4')
    handle.commit()
    ipA2 = handle.getList(mac2,'ipv4')
    ip2 = handle.remapIds(ipA2)[0]
    mvAdd2 = handle.getAttribute(ip2,'-address')
    mvGw2 = handle.getAttribute(ip2,'-gatewayIp')
    if Mac2Mult <= 1 :
        i2 = handle.setAttribute(mvAdd2+'/singleValue','-value',addr2)
    else :        
        i2 = handle.setMultiAttribute(mvAdd2+'/counter','-start',addr2,'-step',addr2Step)
    handle.setAttribute(mvGw2+'/singleValue','-value',addr1)
    handle.setAttribute(handle.getAttribute(ip2,'-prefix')+'/singleValue','-value',prefix2)
    handle.commit()
    handle.setMultiAttribute(handle.getAttribute(ip1,'-resolveGateway')+'/singleValue','-value',True)
    handle.setMultiAttribute(handle.getAttribute(ip2,'-resolveGateway')+'/singleValue','-value',True)
    helpers.log("### Done adding ipv4 Addresses")
    return (ip1,ip2)

def IxSetupTrafficStreamsIP(handle,ip1,ip2,frameType,frameSize,frameRate,frameMode):
    trafficItem = handle.add(handle.getRoot()+'traffic', 'trafficItem', '-trafficItemType', 'raw')
    #handle.add(handle.getRoot()+'/traffic','trafficItem','-name','IPv4 traffic','-allowSelfDestined',False,'-trafficItemType','l2L3','-mergeDestinations',False,'-egressEnabled',False,'-srcDestMesh','oneToOne','-enabled',True,'-routeMesh','oneToOne','-transmitMode','interleaved','-biDirectional',False,'-trafficType','ipv4','-hostsPerNetwork',1)
    endpointSet = ixNet.add(trafficItem, 'endpointSet', '-sources', vport1+'/protocols', '-destinations', vport2+'/protocols')
    handle.commit()
    trItem = handle.getList(handle.getRoot()+'/traffic','trafficItem')
    trafficItem1=handle.remapIds(trItem)[0]
    end1 = handle.add(trafficItem1,'endpointSet','-sources',ip1,'-destinations',ip2,'-name','end1','-sourceFilter',' ','-destinationFilter',' ')
    end2 = handle.add(trafficItem1,'endpointSet','-sources',ip2,'-destinations',ip1,'-name','end2','-sourceFilter',' ','-destinationFilter',' ')
    handle.commit()
    handle.setMultiAttribute(trafficItem1+'/configElement:1'+'/frameSize','-type',frameType,'-fixedSize',frameSize)
    handle.setMultiAttribute(trafficItem1+'/configElement:2'+'/frameSize','-type',frameType,'-fixedSize',frameSize)
    handle.setMultiAttribute(trafficItem1+'/configElement:1'+'/frameRate','-type',frameMode,'-rate',frameRate)
    handle.setMultiAttribute(trafficItem1+'/configElement:2'+'/frameRate','-type',frameMode,'-rate',frameRate)
    handle.setMultiAttribute(trafficItem1+'/tracking','-trackBy','sourceDestValuePair0')
    #handle.setAttribute(handle.getList(end1,'tracking')[0],'-trackBy','trackingenabled0')
    handle.commit()
    return trafficItem1





def IxStartTrafficIP(handle,trafficHandle) :
    helpers.log("### Starting Traffic")
    handle.setAttribute(handle.getRoot()+'/traffic','-refreshLearnedInfoBeforeApply',True)
    handle.commit()
    handle.execute('startAllProtocols')
    time.sleep(20)
    handle.execute('apply', handle.getRoot()+'traffic')
    time.sleep(2)
    portStatistics = handle.getFilteredList(handle.getRoot()+'statistics', 'view', '-caption', 'Port Statistics')[0]
    handle.execute('start', handle.getRoot()+'traffic')
    helpers.log("### Traffic Started")
    return portStatistics




