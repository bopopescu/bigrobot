import autobot.helpers as helpers
import autobot.test as test


class Mininet(object):

    def __init__(self):
        pass
        
    def mininet_dump(self):
        t = test.Test()
        mn = t.mininet()
        mn.cli('dump')
        helpers.log(mn.cli_content())

    def mininet_pingall(self):
        t = test.Test()
        mn = t.mininet()
        mn.cli('pingall')

        out = mn.cli_content()
        drop = helpers.any_match(out, r'Results: (\d+)% dropped')
        helpers.log("drop: %s" % drop)
        if int(drop[0]) > 0:
            helpers.test_failure(drop[0] + "% packet drop")
            
        return out
    
    def mininet_ping(self, src, dst, count=5):        
        t = test.Test()
        mn = t.mininet()
        mn.cli('%s ping %s -c %s' % (src, dst, count))
        
        out = mn.cli_content()
        loss = helpers.any_match(out, r', (\d+)% packet loss')
        helpers.log("packet loss: %s" % loss)
        if int(loss[0]) > 0:
            helpers.test_failure(loss[0] + "% packet loss")
        
        return out
    
    def mininet_link_tag(self, intf, intf_name, vlan, ip):        
        t = test.Test()
        mn = t.mininet()
        mn.cli('%s ip link add link %s vlan1 type vlan id %s' % (intf, intf_name, vlan))
        mn.cli('%s ifconfig %s 0.0.0.0' % (intf, intf_name))
        mn.cli('%s ifconfig vlan1 %s' % (intf, ip))
        
    def mininet_link_untag(self, intf, intf_name, vlan, ip):        
        t = test.Test()
        mn = t.mininet()
        mn.cli('%s ip link delete link %s vlan1' % (intf, intf_name))
        mn.cli('%s ifconfig %s %s' % (intf, intf_name, ip))

    def mininet_host_gw(self, host, gw, intf):        
        t = test.Test()
        mn = t.mininet()
        mn.cli('%s route add default gw %s %s' % (host, gw, intf))

    def mininet_host_ipcfg(self, host, intf, ipaddr, mask):
        t = test.Test()
        mn = t.mininet()
        ip_addr = ipaddr + "/" + mask
        mn.cli('%s ifconfig %s %s up' % (host, intf, ip_addr) )
        
    def mininet_host_arp(self, host, ipaddr, mac):
        t = test.Test()
        mn = t.mininet()
        mn.cli('%s arp -s %s %s' % (host, ipaddr, mac))
 
    def mininet_L3_ping(self, src, dst, count=5):        
        t = test.Test()
        mn = t.mininet()
        mn.cli('%s ping %s -c %s' % (src, dst, count))
        
        out = mn.cli_content()
        loss = helpers.any_match(out, r', (\d+)% packet loss')
        helpers.log("packet loss: %s" % loss)
        value = list element   loss   0
        return value             
       
    def list_element(self, content, index):
        return content[index]
    