'''
Created on Jan 28, 2014

@author: mallinaarun
'''
import vendors.Ixia.IxNetwork

if __name__ == '__main__':
    import sys, time
    sys.path.append('/Users/mallinaarun/Documents/workspace/bigrobot/keywords_dev/arun')
    sys.path.append('/Users/mallinaarun/Documents/workspace/bigrobot/vendors/exscript/src')
    import IxLib
    from datetime import datetime
    
    
    startTime  =  datetime.now()
    ixClientIP = '10.194.64.183'
    ixClientIxNetTclServPortNo = 8009
    ixClientIxNetVer = '7.10'
    ixChassis = '10.192.85.151'
    ixPorts = [('10.192.85.151',2, 7), ('10.192.85.151', 2, 8)]
    mac_mults = [20,20]
    macs = ["00:11:23:00:00:01", "00:11:23:00:00:02"]
    mac_steps = ["00:00:00:00:01:00", "00:00:00:00:01:00"]
    
    mRate="100000"
    mSize="64"
    frameType = 'fixed'
    frameSize = '64'
    frameRate = '10000'
    frameMode = 'framesPerSecond'
    #frameMode = 'percentLineRate'
    addr1 = '132.0.0.1'
    addr2 = '132.0.0.100'
    addr1Step = '0.0.0.1'
    addr2Step = '0.0.0.1'
    prefix1 = '24'
    prefix2 = '24'
    vport_names = ['vport1_eclipse', 'vport2_eclipse']
    frameCount = 70000
    
    # Connec to IXIA TCL Server Running on Windows
    ixNet = IxLib.IxConnect(ixClientIP,ixClientIxNetTclServPortNo,ixClientIxNetVer)
    ixNet.setDebug(False)    # Set Debug True to print Ixia Server Interactions
    
    ##ixNet.getVersion()
    getVersion = ixNet.getVersion()
    print 'Verifying ixNet.getVersion():',getVersion
    
    # Create vports:
    vports = IxLib.IxCreateVports(ixNet, vport_names)
    print '### vports Created : ', vports
    
    # Map to Chassis Physhical Ports:
    if IxLib.IxConnectChassis(ixNet, vports, ixChassis, ixPorts):
        print '### Successfully mapped vport to physical ixia ports..'
    # Create Topo:
    topology = IxLib.IxCreateTopo(ixNet, vports)
    print '### Topology Created: ', topology
    # Create IP Devices:
#     ips = IxLib.IxCreateDeviceIP(ixNet, macs, mac_mults, addrs, addrsteps, prefixs)
     
    
    #Create Ether Device:
    mac_devices = IxLib.IxCreateDeviceEthernet(ixNet,topology, mac_mults =  mac_mults, macs = macs, mac_steps = mac_steps)
    print '### Created Mac Devices with corrsponding Topos ...'    
     
    #Create Traffic Stream:
    trafficStream = IxLib.IxSetupTrafficStreamsEthernet(ixNet, mac_devices[0], mac_devices[1], frameType, frameSize, frameRate, frameMode, frameCount)
    print 'Created Traffic Stream : ' , trafficStream
    print 'Starting Traffic...'
     
    portStatistics = IxLib.IxStartTrafficEthernet(ixNet,trafficStream)
     
    print 'Sleeping 45 secs..'    
    time.sleep(45)
    print "Press Enter to stop Traffic "
     
    traffic_results = IxLib.IxStopTraffic(ixNet,trafficStream,portStatistics)
     
    print "Port Stats : ", traffic_results
    
    