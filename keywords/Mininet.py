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
    
    def mininet_bugreport(self):
        t = test.Test()
        mn = t.mininet()
        mn.cli('bugreport')
        out = mn.cli_content()
        location = helpers.any_match(out, r'Bugreport left at')
        helpers.log("Bugreport Location is: %s" % location)
        return location
    
    def mininet_ping(self, src, dst, count=5):        
        t = test.Test()
        mn = t.mininet()
        mn.cli('%s ping %s -c %s' % (src, dst, count))
        
        out = mn.cli_content()
        loss = helpers.any_match(out, r', (\d+)% packet loss')
        helpers.log("packet loss: %s" % loss)
        return loss[0]
    
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
 
    def mininet_l3_ping(self, src, dst, count=5, options="None"):        
        t = test.Test()
        mn = t.mininet()
        
        if options == "None":           
            mn.cli('%s ping %s -c %s -W 2' % (src, dst, count))
        else:
            mn.cli('%s ping %s -c %s -W 2 %s' % (src, dst, count, options))
        out = mn.cli_content()
        loss = helpers.any_match(out, r', (\d+)% packet loss')
        helpers.log("packet loss: %s" % loss)
        return loss[0]             
 
     
    def mininet_l3_link_tag(self, host, intf_name, vlan, ip, mask):        
        t = test.Test()
        mn = t.mininet()
        ipaddr = ip + "/" + mask
        mn.cli('%s ifconfig %s 0.0.0.0' % (host, intf_name))
        mn.cli('%s ip link add link %s vlan%s type vlan id %s' % (host, intf_name, vlan, vlan))
        mn.cli('%s ifconfig vlan%s %s' % (host, vlan, ipaddr))
        
        
    def mininet_l3_link_untag(self, host, intf_name, vlan, ip, mask):        
        t = test.Test()
        mn = t.mininet()
        ipaddr = ip + "/" + mask
        mn.cli('%s ip link delete link %s vlan%s' % (host, intf_name, vlan))
        mn.cli('%s ifconfig %s %s' % (host, intf_name, ipaddr))   
    
    def mininet_host_tagged_gw(self, host, gw, intf):        
        t = test.Test()
        mn = t.mininet()
        mn.cli('%s route add default gw %s vlan%s' % (host, gw, intf))
    
    def mininet_link_up (self, host, intf):        
        t = test.Test()
        mn = t.mininet()
        mn.cli('%s ifconfig %s up' % (host, intf))         
    
    def mininet_link_down (self, host, intf):        
        t = test.Test()
        mn = t.mininet()
        mn.cli('%s ifconfig %s down' % (host, intf))      
    
    def mininet_host_mac_config (self, host, intf, mac):        
        t = test.Test()
        mn = t.mininet()
        mn.cli('%s ifconfig %s hw ether %s' % (host, intf, mac))     
        
    def mininet_dump_switch(self, switch):
        t = test.Test()
        mn = t.mininet()
        mn.cli('dumpt6 %s' % (switch))
        helpers.log(mn.cli_content())
        
    def mininet_start(self):
        t = test.Test()
        mn = t.mininet()
        mn.start_mininet()
        
    def mininet_stop(self):
        t = test.Test()
        mn = t.mininet()
        mn.stop_mininet()
        
    def mininet_restart(self):
        t = test.Test()
        mn = t.mininet()
        mn.restart_mininet()