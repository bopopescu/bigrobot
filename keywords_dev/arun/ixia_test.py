'''
Created on Jan 28, 2014

@author: mallinaarun
'''
import vendors.Ixia.IxNetwork

if __name__ == '__main__':
    import vendors.Ixia.IxNetwork
    import sys, time
    sys.path.append('/Users/mallinaarun/Documents/workspace/bigrobot/keywords_dev/arun')
    sys.path.append('/Users/mallinaarun/Documents/workspace/bigrobot/vendors/exscript/src')
    import IxLib
    from datetime import datetime
    
    
    startTime  =  datetime.now()
    ix_tcl_server = '10.194.64.183'
    ix_server_port = 8009
    ix_version = '7.10'
    ix_ports = [('10.192.85.151',2, 7), ('10.192.85.151', 2, 8)]
    
    ix_handle = IxLib.IxConnect(ix_tcl_server,  ix_server_port, ix_version)
    L2_stream_args = {'ix_handle' : ix_handle, 'ports' : ix_ports, 'src_mac' :  '00:11:23:00:00:01',\
                       'dst_mac' : '00:11:23:00:00:02', 'd_cnt' : 10, 's_cnt' : 10, \
                       'frame_rate' : 10000, 'frame_size' : 64, \
                       'ix_tcl_server' : '10.194.64.183', 'flow' : 'bi-directional'}
    
    traffic_stream = IxLib.IXIA_L2_ADD(**L2_stream_args)
    
    print 'Successfully created L2 Traffic Flows'
    IxLib.IxStartTrafficEthernet(ix_handle, traffic_stream)
    print "Successfully Started Traffic"
    # below code snippet is sample to fetch results and stop the traffic 
    i = 0
    while i != 5:
        portstats =  IxLib.ix_fetch_port_stats(ix_handle)
        for stat in portstats:
            print 'Port:', stat['port']
            print 'Tx:', stat['Tx']
            print 'TxRate:', stat['TxRate']
            print 'Rx:', stat['Rx']
            print 'RxRate:', stat['RxRate']
            print '#'*50
            
        print 'Sleeping for 5 sec for next poll'
        time.sleep(5)
        i = i + 1
    
    print 'Stopping the traffic...'
    print 'Enter to stop the traffic'
    raw_input()
    port_stats = IxLib.IxStopTraffic(ix_handle, traffic_stream)
    
    print 'Successfully stopped traffic'
    print 'Final Stats Result..'
    print port_stats