'''
Created on Jan 28, 2014

@author: mallinaarun
'''
if __name__ == '__main__':
    import sys, time, re, os
    sys.path.append('/Users/mallinaarun/Documents/workspace/bigrobot/keywords_dev/arun')
    sys.path.append('/Users/mallinaarun/Documents/workspace/bigrobot/vendors/exscript/src')
    import IxLib
    import pprint
    pp = pprint.PrettyPrinter(indent = 4)
    params = {'tg1': {'chassis_ip': '10.192.85.151',
         'platform': 'ixia',
         'ports': {'a': {'name': '2/7'}, 'b': {'name': '2/8'}, 'c': {'name': '2/9'}, 'd': {'name': '2/10'}},
         'set_init_ping': False,
         'tcl_server_ip': '10.194.64.183'}}
    ixia = IxLib.Ixia(tcl_server_ip = params['tg1']['tcl_server_ip'], chassis_ip = params['tg1']['chassis_ip'], 
                  port_map_list = params['tg1']['ports'])
    L2_stream_args = {'src_mac' :  '00:11:23:00:00:01', 'dst_mac' : '00:11:23:00:00:02', 'd_cnt' : 10, 's_cnt' : 50, \
                    'frame_rate' : 10000, 'frame_size' : 64, 'flow' : 'a->b', 'name': 'a_b'}
    ixia.ix_connect()
    traffic_stream_a_b = ixia.ixia_l2_add(**L2_stream_args)
    print 'Successfully Created Traffic Stream:', traffic_stream_a_b
    L2_stream_args = {'src_mac' :  '00:11:23:00:00:01', 'dst_mac' : '00:11:23:00:00:02', 'd_cnt' : 1, 's_cnt' : 1, \
                'frame_rate' : 10000, 'frame_size' : 64, 'flow' : 'c->d', 'name' : 'c_d'}
    traffic_stream_c_d = ixia.ixia_l2_add(**L2_stream_args)
    print 'Successfully Created Traffic Stream:', traffic_stream_c_d
    print 'Starting IXIA traffic on configured Streams'
    for traffic_stream in ixia._traffic_stream.iteritems():
        ixia.ix_start_traffic_ethernet(traffic_stream[1])
        print 'success Starting Traffic!!! Sleep 10 sec...'
        time.sleep(10)
        i = 0 
        while i <= 5:
            print 'Fetch Results..'
            pp.pprint(ixia.ix_fetch_port_stats())
            i = i + 1
            time.sleep(1)
        print 'Starting Next Stream ....'
    print 'Stopping the traffic ..'
    for traffic_stream in ixia._traffic_stream.iteritems():
        ixia.ix_stop_traffic(traffic_stream[1])
        print 'success Stopping Traffic!!! Sleep 10 sec...'
        time.sleep(10)
        time.sleep(10)
        i = 0 
        while i <= 5:
            print 'Fetch Results...'
            pp.pprint(ixia.ix_fetch_port_stats())
            i = i + 1
            time.sleep(1)
        print 'Stopping Next stream ...'
    
    print 'SUCCESSSSS!!!!!'
    
    