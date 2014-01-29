import autobot.helpers as helpers
import autobot.test as test
import os
import sys
import time
import vendors.Ixia.IxNetwork

class IxLibrary(object):
    def __init__(self):
        self.handle = IxNetwork.IxNet()
        pass

    def IxConnect(self,ixClientIP,ixClientIxNetTclServPortNo,ixClientIxNetVer):
        self.handle.connect(ixClientIP, '-port',ixClientIxNetTclServPortNo, '-version',ixClientIxNetVer)
        ### clear the configuration"
        asyncHandle = self.handle.setAsync().execute('newConfig')
        self.handle.wait(asyncHandle)
        return True

    def IxCreateVport(self):
        helpers.log("### create vports")
        vport1 = self.handle.add(self.handle.getRoot(), 'vport', '-name', 'vport1')
        vport2 = self.handle.add(self.handle.getRoot(), 'vport', '-name', 'vport2')
        vport1 = self.handle.remapIds(vport1)[0]
        vport2 = self.handle.remapIds(vport2)[0]
        self.handle.commit();
        helpers.log("### Done creating vPorts")
        return (vport1,vport2)

    def IxCreateTopo(self,vport1,vport2):
        helpers.log("### Adding two topologies")
        self.handle.add(self.handle.getRoot(),'topology','-vports',vport1)
        self.handle.add(self.handle.getRoot(),'topology','-vports',vport2)
        handle.commit()
        topology = self.handle.getList(self.handle.getRoot(),'topology')
        helpers.log("### Done adding two topologies")
        return topology
    
    def IxCreateDeviceEthernet(self,topology,Mac1Mult,Mac2Mult,Mac1,Mac2,Mac1Step,Mac2Step) :
        helpers.log("### Adding two device groups")
        topo1 = topology[0]    
        topo2 = topology[1]    
        self.handle.add(topo1,'deviceGroup')
        self.handle.add(topo2,'deviceGroup')
        self.handle.commit()
        t1devices = self.handle.getList(topo1,'deviceGroup')
        t2devices = self.handle.getList(topo2,'deviceGroup')
        t1dev1 = self.handle.remapIds(t1devices)[0]
        t2dev1 = self.handle.remapIds(t2devices)[0]
        self.handle.setAttribute(t1dev1, '-multiplier', Mac1Mult)
        self.handle.setAttribute(t2dev1, '-multiplier', Mac2Mult)
        self.handle.commit()
        t1d = self.handle.add(t1dev1,'ethernet')
        t2d = self.handle.add(t2dev1,'ethernet')
        self.handle.commit()
        macd1  = self.handle.getList(t1dev1,'ethernet')
        macd2  = self.handle.getList(t2dev1,'ethernet')
        mac1 = self.handle.remapIds(macd1)[0]
        mac2 = self.handle.remapIds(macd2)[0]
        if Mac1Mult <= 1 :
            m1 = self.handle.setAttribute(self.handle.getAttribute(mac1,'-mac')+'/singleValue','-value',Mac1)
        else :        
            m1 = self.handle.setMultiAttribute(self.handle.getAttribute(mac1,'-mac')+'/counter','-direction','increment','-start',Mac1,'-step',Mac1Step)
        if Mac2Mult <= 1 :
            m2 = self.handle.setAttribute(self.handle.getAttribute(mac2,'-mac')+'/singleValue','-value',Mac2)
        else :        
            m2 = self.handle.setMultiAttribute(self.handle.getAttribute(mac2,'-mac')+'/counter','-direction','increment','-start',Mac2,'-step',Mac2Step)
        self.handle.setAttribute(topo1,'-name','Send Topology')
        self.handle.setAttribute(topo2,'-name','Receive Topology')
        self.handle.setAttribute(t1dev1,'-name','Send Device')
        self.handle.setAttribute(t2dev1,'-name','Receive Device')
        self.handle.commit()
        helpers.log("### Done adding two device groups")
        return (mac1,mac2)

    def IxSetupTrafficStreamsEthernet(self,mac1,mac2,frameType,frameSize,frameRate,frameMode):
        trafficStream1 = self.handle.add(self.handle.getRoot()+'traffic','trafficItem','-name','Ethernet L2','-allowSelfDestined',False,'-trafficItemType','l2L3','-enabled',True,'-transmitMode','interleaved','-biDirectional',False,'-trafficType','ethernetVlan','-hostsPerNetwork','1')
        self.handle.commit()
        endpointSet1 = self.handle.add(trafficStream1, 'endpointSet','-name','l2u','-sources', mac1,'-destinations', mac2)
        endpointSet2 = self.handle.add(trafficStream1, 'endpointSet','-name','l2u','-sources', mac2,'-destinations', mac1)
        self.handle.setAttribute(trafficStream1,'-enabled',True)
        self.handle.setAttribute(trafficStream1+'/highLevelStream:1/'+'frameSize','-type',frameType)
        self.handle.setAttribute(trafficStream1+'/highLevelStream:1/'+'frameSize','-fixedSize',frameSize)
        self.handle.setAttribute(trafficStream1+'/highLevelStream:1/'+'frameRate','-type',frameMode)
        self.handle.setAttribute(trafficStream1+'/highLevelStream:1/'+'frameRate','-rate',frameRate)
        self.handle.setAttribute(trafficStream1+'/highLevelStream:2/'+'frameSize','-type',frameType)
        self.handle.setAttribute(trafficStream1+'/highLevelStream:2/'+'frameSize','-fixedSize',frameSize)
        self.handle.setAttribute(trafficStream1+'/highLevelStream:2/'+'frameRate','-type',frameMode)
        self.handle.setAttribute(trafficStream1+'/highLevelStream:2/'+'frameRate','-rate',frameRate)
        self.handle.setAttribute(handle.getList(trafficStream1,'tracking')[0],'-trackBy','trackingenabled0')
        self.handle.commit()
        return trafficStream1
    
    
    def IxCreateDeviceIP(self,mac1,mac2,Mac1Mult,Mac2Mult,addr1,addr1Step,addr2Step,addr2,prefix1,prefix2) :
        helpers.log("### Add ipv4")
        self.handle.add(mac1,'ipv4')
        self.handle.commit()
        ipA1 = self.handle.getList(mac1,'ipv4')
        ip1 = self.handle.remapIds(ipA1)[0]
        mvAdd1 = self.handle.getAttribute(ip1,'-address')
        mvGw1 = self.handle.getAttribute(ip1,'-gatewayIp')
        if Mac1Mult <= 1 :
            i1 = self.handle.setAttribute(mvAdd1+'/singleValue','-value',addr1)
        else :        
            i1 = self.handle.setMultiAttribute(mvAdd1+'/counter','-start',addr1,'-step',addr1Step)
        self.handle.setAttribute(mvGw1+'/singleValue','-value',addr2)
        self.handle.setAttribute(self.handle.getAttribute(ip1,'-prefix')+'/singleValue','-value',prefix1)
        self.handle.commit()
        self.handle.add(mac2,'ipv4')
        self.handle.commit()
        ipA2 = self.handle.getList(mac2,'ipv4')
        ip2 = self.handle.remapIds(ipA2)[0]
        mvAdd2 = self.handle.getAttribute(ip2,'-address')
        mvGw2 = self.handle.getAttribute(ip2,'-gatewayIp')
        if Mac2Mult <= 1 :
            i2 = self.handle.setAttribute(mvAdd2+'/singleValue','-value',addr2)
        else :        
            i2 = self.handle.setMultiAttribute(mvAdd2+'/counter','-start',addr2,'-step',addr2Step)
        self.handle.setAttribute(mvGw2+'/singleValue','-value',addr1)
        self.handle.setAttribute(self.handle.getAttribute(ip2,'-prefix')+'/singleValue','-value',prefix2)
        self.handle.commit()
        self.handle.setMultiAttribute(self.handle.getAttribute(ip1,'-resolveGateway')+'/singleValue','-value',True)
        self.handle.setMultiAttribute(self.handle.getAttribute(ip2,'-resolveGateway')+'/singleValue','-value',True)
        helpers.log("### Done adding ipv4 Addresses")
        return (ip1,ip2)
    
    def IxSetupTrafficStreamsIP(self,ip1,ip2,frameType,frameSize,frameRate,frameMode):
        self.handle.add(self.handle.getRoot()+'/traffic','trafficItem','-name','IPv4 traffic','-allowSelfDestined',False,'-trafficItemType','l2L3','-mergeDestinations',False,'-egressEnabled',False,'-srcDestMesh','oneToOne','-enabled',True,'-routeMesh','oneToOne','-transmitMode','interleaved','-biDirectional',False,'-trafficType','ipv4','-hostsPerNetwork',1)
        self.handle.commit()
        trItem = self.handle.getList(self.handle.getRoot()+'/traffic','trafficItem')
        trafficItem1=self.handle.remapIds(trItem)[0]
        end1 = self.handle.add(trafficItem1,'endpointSet','-sources',ip1,'-destinations',ip2,'-name','end1','-sourceFilter',' ','-destinationFilter',' ')
        end2 = self.handle.add(trafficItem1,'endpointSet','-sources',ip2,'-destinations',ip1,'-name','end2','-sourceFilter',' ','-destinationFilter',' ')
        self.handle.commit()
        self.handle.setMultiAttribute(trafficItem1+'/configElement:1'+'/frameSize','-type',frameType,'-fixedSize',frameSize)
        self.handle.setMultiAttribute(trafficItem1+'/configElement:2'+'/frameSize','-type',frameType,'-fixedSize',frameSize)
        self.handle.setMultiAttribute(trafficItem1+'/configElement:1'+'/frameRate','-type',frameMode,'-rate',frameRate)
        self.handle.setMultiAttribute(trafficItem1+'/configElement:2'+'/frameRate','-type',frameMode,'-rate',frameRate)
        self.handle.setMultiAttribute(trafficItem1+'/tracking','-trackBy','sourceDestValuePair0')
        self.handle.commit()
        return trafficItem1

    def IxConnectChassis(self,vport1,vport2,ixChassis,ixPorts) :
        chassis = self.handle.add(self.handle.getRoot()+'availableHardware', 'chassis', '-hostname', ixChassis)
        self.handle.commit()
        chassis = self.handle.remapIds(chassis)[0]
        card1 = str(ixPorts[0][1])
        port1 = str(ixPorts[0][2])
        card2 = str(ixPorts[1][1])
        port2 = str(ixPorts[1][2])
        self.handle.setAttribute(vport1, '-connectedTo', chassis+'/card:'+card1+'/port:'+port1)
        self.handle.setAttribute(vport2, '-connectedTo', chassis+'/card:'+card2+'/port:'+port2)
        self.handle.commit()
        while (self.handle.getAttribute(vport1, '-state') != 'up' and self.handle.getAttribute(vport2, '-state') != 'up') :
            time.sleep(2)
        return True
    
    def IxStartTrafficEthernet(self,trafficHandle) :
        helpers.log("### Starting Traffic")
        self.handle.execute('startAllProtocols')
        time.sleep(2)
        self.handle.execute('apply', self.handle.getRoot()+'traffic')
        time.sleep(2)
        portStatistics = self.handle.getFilteredList(self.handle.getRoot()+'statistics', 'view', '-caption', 'Port Statistics')[0]
        time.sleep(2)
        self.handle.execute('startStatelessTraffic',trafficHandle)
        helpers.log("### Traffic Started")
        return portStatistics
    
    def IxStartTrafficIP(self,trafficHandle) :
        helpers.log("### Starting Traffic")
        self.handle.setAttribute(self.handle.getRoot()+'/traffic','-refreshLearnedInfoBeforeApply',True)
        self.handle.commit()
        self.handle.execute('startAllProtocols')
        time.sleep(20)
        self.handle.execute('apply', self.handle.getRoot()+'traffic')
        time.sleep(2)
        portStatistics = self.handle.getFilteredList(self.handle.getRoot()+'statistics', 'view', '-caption', 'Port Statistics')[0]
        self.handle.execute('start', self.handle.getRoot()+'traffic')
        helpers.log("### Traffic Started")
        return portStatistics
    
    def IxStopTraffic(self,trafficHandle,portStatistics) :
        helpers.log("### Stopping Traffic")
        self.handle.execute('stopStatelessTraffic',trafficHandle)
        helpers.log("### Printing Statistics")
        #print handle.getAttribute(portStatistics+'/page', '-columnCaptions')
        #print handle.getAttribute(portStatistics+'/page', '-rowValues')
        #['Stat Name', 'Port Name', 'Line Speed', 'Link State', 'Frames Tx.', 'Valid Frames Rx.', 'Frames Tx. Rate', 'Valid Frames Rx. Rate', 'Data Integrity Frames Rx.', 'Data Integrity Errors', 'Bytes Tx.', 'Bytes Rx.', 'Bits Sent', 'Bits Received', 'Bytes Tx. Rate', 'Tx. Rate (bps)', 'Tx. Rate (Kbps)', 'Tx. Rate (Mbps)', 'Bytes Rx. Rate', 'Rx. Rate (bps)', 'Rx. Rate (Kbps)', 'Rx. Rate (Mbps)', 'Scheduled Frames Tx.', 'Scheduled Frames Tx. Rate', 'Control Frames Tx', 'Control Frames Rx', 'Ethernet OAM Information PDUs Sent', 'Ethernet OAM Information PDUs Received', 'Ethernet OAM Event Notification PDUs Received', 'Ethernet OAM Loopback Control PDUs Received', 'Ethernet OAM Organisation PDUs Received', 'Ethernet OAM Variable Request PDUs Received', 'Ethernet OAM Variable Response Received', 'Ethernet OAM Unsupported PDUs Received', 'Rx Pause Priority Group 0 Frames', 'Rx Pause Priority Group 1 Frames', 'Rx Pause Priority Group 2 Frames', 'Rx Pause Priority Group 3 Frames', 'Rx Pause Priority Group 4 Frames', 'Rx Pause Priority Group 5 Frames', 'Rx Pause Priority Group 6 Frames', 'Rx Pause Priority Group 7 Frames', 'Misdirected Packet Count', 'CRC Errors']
        port1stats = self.handle.getAttribute(portStatistics+'/page', '-rowValues')[0]
        port2stats = self.handle.getAttribute(portStatistics+'/page', '-rowValues')[1]
        return (port1stats, port2stats)