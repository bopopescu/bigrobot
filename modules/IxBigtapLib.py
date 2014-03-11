#!/usr/bin/env python
'''
    This module is used to maintain Ixia Related Libraries for traffic generation with Bigtap Controller
'''
import autobot.helpers as helpers
import time, re
from vendors.Ixia import IxNetwork
    
def create_mac_list(bigtap_port_name, count, re_list = True):
    '''
        Creating mac lists from given bigta_port_name
    '''
    return_dic = {}
    a = bigtap_port_name
    d = a.split('/')
    octs = []
    final_macs = []
    for x in d:
        if len(x) == 1:
            octs.append('0'+str(x))
        else:
            octs.append(str(x))
    if len(octs) > 2:
        raise IxNetwork.IxNetError('Failure !! should not be possible if used correct format for ports a, b')
        return
    # Creating start mac from give bigtap_portname
    start_mac = '00:'+octs[0]+':'+octs[1]+':'+'00:00:00'
    return_dic['start_mac'] = start_mac
    return_dic['mac_step'] = '00:00:00:01:00:00'
    return_dic['count'] = count
    helpers.log("Using Start Mac: %s" % start_mac)
    increment = '00'
    for i in xrange(0,count):
        hex_num = int(increment,16) + i
        hex_str = str(hex(hex_num))
        if len(hex_str[2:]) == 1:
            final_macs.append(start_mac[:9]+'0'+hex_str[2:]+start_mac[11:])
        else:
            final_macs.append(start_mac[:9]+hex_str[2:]+start_mac[11:])
    if re_list:
        return final_macs
    else:
        return return_dic
    
def create_bigtap_flow_conf_tx(switch_dpid, bigtap_portname, ix_portname, macs):
    bigtap_config = []
    bigtap_config.append('enable')
    bigtap_config.append('configure')
    
    for mac, i  in zip(macs, xrange(1,len(macs) +1)):
        if bigtap_portname in ix_portname:
            print 'No inline Delivery as both are SAME !!!!'
        else:
            bigtap_config.append('bigtap policy ethernet'+bigtap_portname+' rbac-permission admin-view')
            bigtap_config.append('action forward')
            for ix_port in ix_portname:
                bigtap_config.append('inline-filter-interface '+switch_dpid+' ethernet'+ix_port)
            bigtap_config.append('inline-delivery-interface '+switch_dpid+' ethernet'+bigtap_portname)
            bigtap_config.append(str(i)+' match mac src-mac '+mac)
    return bigtap_config


def create_bigtap_flow_conf_rx(switch_dpid, bigtap_no_of_ports, ix_portname):
    bigtap_config = []
    bigtap_config.append('enable')
    bigtap_config.append('configure')
    bigtap_config.append('switch '+switch_dpid)
    
    for i in xrange(1, bigtap_no_of_ports + 1):
        bigtap_config.append('interface'+' ethernet'+str(i))
    bigtap_config.append('bigtap policy policyall rbac-permission admin-view')
    
    for i in xrange(2, bigtap_no_of_ports + 1):
        if str(i) in ix_portname:
            print 'no INLINE for port : %s as it is DELIVERY Port' % str(i)
        else:
            bigtap_config.append('inline-filter-interface '+switch_dpid+' ethernet'+str(i))
    for ix_port in ix_portname:
        bigtap_config.append('inline-delivery-interface '+switch_dpid+' ethernet'+ix_port)
    bigtap_config.append('1 match any')
    bigtap_config.append('action forward')
    return bigtap_config


    
    
    