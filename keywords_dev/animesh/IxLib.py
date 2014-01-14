#!/usr/bin/env python
import autobot.helpers as helpers
import autobot.test as test
import os
import sys
import time
import IxNetwork

class IxLib(object):
	def IxConnect(ixClientIP,ixClientIxNetTclServPortNo,ixClientIxNetVer):
		handle = IxNetwork.IxNet()
		handle.connect(ixClientIP, '-port',ixClientIxNetTclServPortNo, '-version',ixClientIxNetVer)
		### clear the configuration"
		asyncHandle = handle.setAsync().execute('newConfig')
		handle.wait(asyncHandle)
		return handle
	
	def IxCreateVport(handle):
		helpers.log("### create vports")
		vport1 = handle.add(handle.getRoot(), 'vport', '-name', 'vport1')
		vport2 = handle.add(handle.getRoot(), 'vport', '-name', 'vport2')
		vport1 = handle.remapIds(vport1)[0]
		vport2 = handle.remapIds(vport2)[0]
		handle.commit();
		helpers.log("### Done creating vPorts")
		return (vport1,vport2)
	
	def IxCreateTopo(handle,vport1,vport2):
		helpers.log("### Adding two topologies")
		handle.add(handle.getRoot(),'topology','-vports',vport1)
		handle.add(handle.getRoot(),'topology','-vports',vport2)
		handle.commit()
		topology = handle.getList(handle.getRoot(),'topology')
		helpers.log("### Done adding two topologies")
		return topology
	
	def IxCreateDeviceEthernet(handle,topology,Mac1Mult,Mac2Mult,Mac1,Mac2,Mac1Step,Mac2Step) :
		helpers.log("### Adding two device groups")
		topo1 = topology[0]	
		topo2 = topology[1]	
		handle.add(topo1,'deviceGroup')
		handle.add(topo2,'deviceGroup')
		handle.commit()
		t1devices = handle.getList(topo1,'deviceGroup')
		t2devices = handle.getList(topo2,'deviceGroup')
		t1dev1 = handle.remapIds(t1devices)[0]
		t2dev1 = handle.remapIds(t2devices)[0]
		handle.setAttribute(t1dev1, '-multiplier', Mac1Mult)
		handle.setAttribute(t2dev1, '-multiplier', Mac2Mult)
		handle.commit()
		t1d = handle.add(t1dev1,'ethernet')
		t2d = handle.add(t2dev1,'ethernet')
		handle.commit()
		macd1  = handle.getList(t1dev1,'ethernet')
		macd2  = handle.getList(t2dev1,'ethernet')
		mac1 = handle.remapIds(macd1)[0]
		mac2 = handle.remapIds(macd2)[0]
		if Mac1Mult <= 1 :
			m1 = handle.setAttribute(handle.getAttribute(mac1,'-mac')+'/singleValue','-value',Mac1)
		else :		
			m1 = handle.setMultiAttribute(handle.getAttribute(mac1,'-mac')+'/counter','-direction','increment','-start',Mac1,'-step',Mac1Step)
		if Mac2Mult <= 1 :
			m2 = handle.setAttribute(handle.getAttribute(mac2,'-mac')+'/singleValue','-value',Mac2)
		else :		
			m2 = handle.setMultiAttribute(handle.getAttribute(mac2,'-mac')+'/counter','-direction','increment','-start',Mac2,'-step',Mac2Step)
		handle.setAttribute(topo1,'-name','Send Topology')
		handle.setAttribute(topo2,'-name','Receive Topology')
		handle.setAttribute(t1dev1,'-name','Send Device')
		handle.setAttribute(t2dev1,'-name','Receive Device')
		handle.commit()
		helpers.log("### Done adding two device groups")
		return (mac1,mac2)
	
	def IxSetupTrafficStreamsEthernet(handle,mac1,mac2,frameType,frameSize,frameRate,frameMode):
		trafficStream1 = handle.add(handle.getRoot()+'traffic','trafficItem','-name','Ethernet L2','-allowSelfDestined',False,'-trafficItemType','l2L3','-enabled',True,'-transmitMode','interleaved','-biDirectional',False,'-trafficType','ethernetVlan','-hostsPerNetwork','1')
		handle.commit()
		endpointSet1 = handle.add(trafficStream1, 'endpointSet','-name','l2u','-sources', mac1,'-destinations', mac2)
		endpointSet2 = handle.add(trafficStream1, 'endpointSet','-name','l2u','-sources', mac2,'-destinations', mac1)
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
		handle.add(handle.getRoot()+'/traffic','trafficItem','-name','IPv4 traffic','-allowSelfDestined',False,'-trafficItemType','l2L3','-mergeDestinations',False,'-egressEnabled',False,'-srcDestMesh','oneToOne','-enabled',True,'-routeMesh','oneToOne','-transmitMode','interleaved','-biDirectional',False,'-trafficType','ipv4','-hostsPerNetwork',1)
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
		handle.commit()
		return trafficItem1
	
	def IxConnectChassis(handle,vport1,vport2,ixChassis,ixPorts) :
		chassis = handle.add(handle.getRoot()+'availableHardware', 'chassis', '-hostname', ixChassis)
		handle.commit()
		chassis = handle.remapIds(chassis)[0]
		card1 = str(ixPorts[0][1])
		port1 = str(ixPorts[0][2])
		card2 = str(ixPorts[1][1])
		port2 = str(ixPorts[1][2])
		handle.setAttribute(vport1, '-connectedTo', chassis+'/card:'+card1+'/port:'+port1)
		handle.setAttribute(vport2, '-connectedTo', chassis+'/card:'+card2+'/port:'+port2)
		handle.commit()
		while (handle.getAttribute(vport1, '-state') != 'up' and handle.getAttribute(vport2, '-state') != 'up') :
			time.sleep(2)
		return True
	
	def IxStartTrafficEthernet(handle,trafficHandle) :
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
	
	def IxStopTraffic(handle,trafficHandle,portStatistics) :
		helpers.log("### Stopping Traffic")
		handle.execute('stopStatelessTraffic',trafficHandle)
		helpers.log("### Printing Statistics")
		#print handle.getAttribute(portStatistics+'/page', '-columnCaptions')
		#print handle.getAttribute(portStatistics+'/page', '-rowValues')
	#['Stat Name', 'Port Name', 'Line Speed', 'Link State', 'Frames Tx.', 'Valid Frames Rx.', 'Frames Tx. Rate', 'Valid Frames Rx. Rate', 'Data Integrity Frames Rx.', 'Data Integrity Errors', 'Bytes Tx.', 'Bytes Rx.', 'Bits Sent', 'Bits Received', 'Bytes Tx. Rate', 'Tx. Rate (bps)', 'Tx. Rate (Kbps)', 'Tx. Rate (Mbps)', 'Bytes Rx. Rate', 'Rx. Rate (bps)', 'Rx. Rate (Kbps)', 'Rx. Rate (Mbps)', 'Scheduled Frames Tx.', 'Scheduled Frames Tx. Rate', 'Control Frames Tx', 'Control Frames Rx', 'Ethernet OAM Information PDUs Sent', 'Ethernet OAM Information PDUs Received', 'Ethernet OAM Event Notification PDUs Received', 'Ethernet OAM Loopback Control PDUs Received', 'Ethernet OAM Organisation PDUs Received', 'Ethernet OAM Variable Request PDUs Received', 'Ethernet OAM Variable Response Received', 'Ethernet OAM Unsupported PDUs Received', 'Rx Pause Priority Group 0 Frames', 'Rx Pause Priority Group 1 Frames', 'Rx Pause Priority Group 2 Frames', 'Rx Pause Priority Group 3 Frames', 'Rx Pause Priority Group 4 Frames', 'Rx Pause Priority Group 5 Frames', 'Rx Pause Priority Group 6 Frames', 'Rx Pause Priority Group 7 Frames', 'Misdirected Packet Count', 'CRC Errors']
		port1stats = handle.getAttribute(portStatistics+'/page', '-rowValues')[0]
		port2stats = handle.getAttribute(portStatistics+'/page', '-rowValues')[1]
		return (port1stats, port2stats)

