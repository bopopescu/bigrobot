import autobot.helpers as helpers
import autobot.restclient as restclient
import autobot.test as test


class T5L3(object):

    def __init__(self):
        pass
        
    def rest_add_vns_ip(self, tenant, vns, ipaddr, netmask):
        '''Create vns router interface via command "virtual-router vns interface"
        
            Input:
                `tenant`        tenant name
                `vns`           vns interface name which must be similar to VNS
                `ipaddr`        interface ip address
                `netmask`       vns subnet mask
            PATCH http://127.0.0.1:8080/api/v1/data/controller/applications/bvs/tenant[name="A"]/virtual-router/vns-interfaces[vns-name="A2"] {"ip-cidr": "10.10.12.1/24"}
        
            Return: true if configuration is successful, false otherwise
        '''
        
        t = test.Test()
        c = t.controller('main')
        
        helpers.test_log("Input arguments: tenant = %s vns = %s ipaddr = %s netmask = %s " % (tenant, vns, ipaddr, netmask ))
        
        #url = '/api/v1/data/controller/applications/bvs/tenant[name="%s"]/virtual-router/vns-interfaces' % (tenant)
        url = '/api/v1/data/controller/applications/bvs/tenant[name="%s"]/virtual-router/vns-interfaces[vns-name="%s"]' % (tenant, vns)
        ip_addr = ipaddr + "/" + netmask
        try:
            #c.rest.patch(url, {"ip-cidr": str(ip_addr)})
            #c.rest.post(url, {"vns-name": vns, "ip-cidr": str(ip_addr), "active": True})
            c.rest.put(url, {"vns-name": vns, "ip-cidr": str(ip_addr)})
        except:
            #helpers.test_failure(c.rest.error())
            return False
        else: 
            #helpers.test_log("Output: %s" % c.rest.result_json())
            #return c.rest.content()
            return True

    def rest_delete_vns_ip(self, tenant, vnsname, ipaddr, netmask):
        '''Create vns router interface via command "virtual-router vns interface"
        
            Input:
                `tenant`        tenant name
                `vnsname`       vns interface name which must be similar to VNS
                `ipaddr`        interface ip address
                `netmask`       vns subnet mask
REST-POST: DELETE http://127.0.0.1:8080/api/v1/data/controller/applications/bvs/tenant[name="B"]/virtual-router/vns-interfaces[vns-name="B1"]/ip-cidr {}            
            Return: true if configuration is successful, false otherwise
        '''
        
        t = test.Test()
        c = t.controller('main')
        
        helpers.test_log("Input arguments: tenant = %s vns = %s ipaddr = %s netmask = %s " % (tenant, vnsname, ipaddr, netmask ))
        
        url = '/api/v1/data/controller/applications/bvs/tenant[name="%s"]/virtual-router/vns-interfaces[vns-name="%s"]/ip-cidr' % (tenant, vnsname)
        ip_addr = ipaddr + "/" + netmask
        try:
            c.rest.delete(url, {})
        except:
            return False
            #helpers.test_failure(c.rest.error())
        else: 
            #helpers.test_log("Output: %s" % c.rest.result_json())
            #return c.rest.content()
            return True
        
   
    def rest_add_tenant_routers_to_system(self, tenant):        
        '''Attach tenant router to system tenant"
        
            Input:
                `tenant`        tenant name
            
            Return: true if configuration is successful, false otherwise
            
REST-POST: PUT http://127.0.0.1:8080/api/v1/data/controller/applications/bvs/tenant[name="system"]/virtual-router/tenant-interfaces[tenant-name="A"] {"tenant-name": "A"}
REST-POST: http://127.0.0.1:8080/api/v1/data/controller/applications/bvs/tenant[name="system"]/virtual-router/tenant-interfaces[tenant-name="A"] reply: ""

        '''
        
        t = test.Test()
        c = t.controller('main')
        
        helpers.test_log("Input arguments: tenant = %s " % (tenant))
        
        url = '/api/v1/data/controller/applications/bvs/tenant[name="system"]/virtual-router/tenant-interfaces[tenant-name="%s"]' % (tenant)
        try:
            c.rest.post(url, {"tenant-name": tenant, "active": True})
        except:
            helpers.test_failure(c.rest.error())
        else: 
            helpers.test_log("Output: %s" % c.rest.result_json())
            return c.rest.content() 
        
    def rest_delete_tenant_routers_to_system(self, tenant):        
        '''detach tenant router to system tenant"
        
            Input:
                `tenant`        tenant name
            
            Return: true if configuration is successful, false otherwise
            
REST-POST: DELETE http://127.0.0.1:8080/api/v1/data/controller/applications/bvs/tenant[name="system"]/virtual-router/tenant-interfaces[tenant-name="A"] {}
       '''
        
        t = test.Test()
        c = t.controller('main')
        
        helpers.test_log("Input arguments: tenant = %s " % (tenant))
        
        url = '/api/v1/data/controller/applications/bvs/tenant[name="system"]/virtual-router/tenant-interfaces[tenant-name="%s"]' % (tenant)
        try:
            c.rest.delete(url, {})
        except:
            helpers.test_failure(c.rest.error())
        else: 
            helpers.test_log("Output: %s" % c.rest.result_json())
            return c.rest.content() 
        
        
    def rest_add_system_to_tenant_routers(self, tenant):        
        '''Attach system router to tenant router"
        
            Input:
                `tenant`        tenant name
            
            Return: true if configuration is successful, false otherwise
            
        '''
        
        t = test.Test()
        c = t.controller('main')
        
        helpers.test_log("Input arguments: tenant = %s " % (tenant))
        
        url = '/api/v1/data/controller/applications/bvs/tenant[name="%s"]/virtual-router/tenant-interfaces[tenant-name="system"]' % (tenant)
        try:
            c.rest.post(url, {"tenant-name": "system", "active": True})
        except:
            helpers.test_failure(c.rest.error())
        else: 
            helpers.test_log("Output: %s" % c.rest.result_json())
            return c.rest.content()         


    def rest_delete_system_to_tenant_routers(self, tenant):        
        '''detach system router from tenant router"
        
            Input:
                `tenant`        tenant name
REST-POST: DELETE http://127.0.0.1:8080/api/v1/data/controller/applications/bvs/tenant[name="B"]/virtual-router/tenant-interfaces[tenant-name="system"] {}
            Return: true if configuration is successful, false otherwise
            
        '''
        
        t = test.Test()
        c = t.controller('main')
        
        helpers.test_log("Input arguments: tenant = %s " % (tenant))
        
        url = '/api/v1/data/controller/applications/bvs/tenant[name="%s"]/virtual-router/tenant-interfaces[tenant-name="system"]' % (tenant)
        try:
            c.rest.delete(url, {})
        except:
            helpers.test_failure(c.rest.error())
        else: 
            helpers.test_log("Output: %s" % c.rest.result_json())
            return c.rest.content()                    
    
    def rest_add_static_routes(self, tenant, dstroute, nexthop):
        '''Add static routes to tenant router"
        
            Input:
                `tenant`          tenant name
                `dstroute`        destination subnet
                `nexthop`         nexthop IP address or nexthop tenant name or nexthop ecmp group name. e.g. of nexthop input is {"ip-address": "10.10.10.1"} or {"tenant-name": "B"} or {"ecmp-group-name": "e3"}
                more specific example REST add static routes(A, 10.10.11.0/24, {"ecmp-group-name": "e2"})
            Return: true if configuration is successful, false otherwise
        '''
        
        t = test.Test()
        c = t.controller('main')
        
        nexthop_dict = helpers.from_json(nexthop)
        
        helpers.test_log("Input arguments: tenant = %s dstroute = %s nexthop = %s " % (tenant, dstroute, nexthop))
        
        url = '/api/v1/data/controller/applications/bvs/tenant[name="%s"]/virtual-router/routes' % (tenant)
        try:
            c.rest.post(url, {"dest-ip-subnet": dstroute, "next-hop": nexthop_dict})
        except:
            helpers.test_failure(c.rest.error())
        else: 
            helpers.test_log("Output: %s" % c.rest.result_json())
            return c.rest.content()    
                   
    def rest_delete_static_routes(self, tenant, dstroute):
        '''Add static routes to tenant router"
        
            Input:
                `tenant`          tenant name
                `dstroute`        destination subnet
 
REST-POST: DELETE http://127.0.0.1:8080/api/v1/data/controller/applications/bvs/tenant[name="C"]/virtual-router/routes[dest-ip-subnet="10.40.10.0/24"] {}              
                Return: true if configuration is successful, false otherwise
        '''
        
        t = test.Test()
        c = t.controller('main')
        
        helpers.test_log("Input arguments: tenant = %s dstroute = %s " % (tenant, dstroute))
        
        url = '/api/v1/data/controller/applications/bvs/tenant[name="%s"]/virtual-router/routes' % (tenant)
        try:
            c.rest.delete(url, {"dest-ip-subnet": dstroute})
        except:
            helpers.test_failure(c.rest.error())
        else: 
            helpers.test_log("Output: %s" % c.rest.result_json())
            return c.rest.content()    
 
        
    def rest_show_endpoints(self):
        t = test.Test()
        c = t.controller('main')
        
        url = '/api/v1/data/controller/applications/bvs/info/endpoint-manager/endpoints'
        c.rest.get(url)
        helpers.log("Output: %s" % c.rest.result_json())
        data = c.rest.content()
        return data
    
    def rest_show_endpoints_name(self, endpointname):
        t = test.Test()
        c = t.controller('main')
        
        endptname = "%5Bname%3D%22" + endpointname + "%22%5D" 
        url = '/api/v1/data/controller/applications/bvs/info/endpoint-manager/endpoints%s' % (endptname)
        c.rest.get(url)
        helpers.log("Output: %s" % c.rest.result_json())
        data = c.rest.content()
        return data
    
    def rest_show_endpoints_mac(self, mac):
        '''
        %5Bmac%3D%2200%3A00%3A00%3A00%3A00%3A01%22%5D
        '''
        t = test.Test()
        c = t.controller('main')
        
        str1 = mac.replace(":", "%3A")
        mac_addr = "%5Bmac%3D%22" + str1 + "%22%5D" 
        url = '/api/v1/data/controller/applications/bvs/info/endpoint-manager/endpoints%s' % (mac_addr)
        c.rest.get(url)
        helpers.log("Output: %s" % c.rest.result_json())
        data = c.rest.content()
        return data
    
    
    def rest_count_endpoints_mac(self):
        data = self.rest_show_endpoints()
        return len(data)
     
    def rest_add_ecmp_group(self, tenant, ecmpgroup):
        '''Add ecmp groups aks gateway pool to tenant"
        
            Input:
                `tenant`          tenant name
                `ecmpgroup`        pool or ecmp groups name
            Return: true if configuration is successful, false otherwise
        '''
        
        t = test.Test()
        c = t.controller('main')
        
        helpers.test_log("Input arguments: tenant = %s ecmpgroup = %s" % (tenant, ecmpgroup))
        
        url = '/api/v1/data/controller/applications/bvs/tenant[name="%s"]/virtual-router/ecmp-groups' % (tenant)
        try:
            c.rest.post(url, {"name": ecmpgroup})
        except:
            helpers.test_failure(c.rest.error())
        else: 
            helpers.test_log("Output: %s" % c.rest.result_json())
            return c.rest.content()                
     
     
    def rest_add_gw_pool_nexthop(self, tenant, ecmpgroup, nexthop):
        '''Add nexthop to ecmp groups aks gateway pool in tenant"
        
            Input:
                `tenant`         tenant name
                `ecmpgroup`      pool or ecmp groups name
                `nexthop`        nexthop IP address
            Return: true if configuration is successful, false otherwise
        '''
        
        t = test.Test()
        c = t.controller('main')
        
        helpers.test_log("Input arguments: tenant = %s ecmpgroup = %s nexthop = %s" % (tenant, ecmpgroup, nexthop))
        
        url = '/api/v1/data/controller/applications/bvs/tenant[name="%s"]/virtual-router/ecmp-groups[name="%s"]/ip-addresses' % (tenant, ecmpgroup)
        try:
            c.rest.put(url, {"ip-address": nexthop})
        except:
            helpers.test_failure(c.rest.error())
        else: 
            helpers.test_log("Output: %s" % c.rest.result_json())
            return c.rest.content()                         

     

    def rest_add_endpoint_ip(self, tenant, vnsname, endpointname, ipaddr):
        '''Add nexthop to ecmp groups aks gateway pool in tenant"
        
            Input:
                `tenant`          tenant name
                `vnsname`         vns name
                `endpointname`    endpoint name
                `ipaddr`          host IP address
            Return: true if configuration is successful, false otherwise
            http://127.0.0.1:8080/api/v1/data/controller/applications/bvs/tenant[name="A"]/vns[name="A1"]/endpoints[name="H1"] {"name": "H1"}

        '''
        
        t = test.Test()
        c = t.controller('main')
        
        helpers.test_log("Input arguments: tenant = %s vnsname = %s endpointname = %s ipaddress = %s" % (tenant, vnsname, endpointname, ipaddr))
        
        url = '/api/v1/data/controller/applications/bvs/tenant[name="%s"]/vns[name="%s"]/endpoints[name="%s"]' % (tenant, vnsname, endpointname)
        try:
            c.rest.patch(url, {"ip-address": ipaddr})
        except:
            helpers.test_failure(c.rest.error())
        else: 
            helpers.test_log("Output: %s" % c.rest.result_json())
            return c.rest.content()                         

    def rest_delete_endpoint_ip(self, tenant, vnsname, endpointname, ipaddr):
        return True

 
    def rest_add_endpoint_mac(self, tenant, vnsname, endpointname, mac):
        '''Add nexthop to ecmp groups aks gateway pool in tenant"
        
            Input:
                `tenant`          tenant name
                `vnsname`         vns name
                `endpointname`    endpoint name
                `mac`          host mac address
            Return: true if configuration is successful, false otherwise
            http://127.0.0.1:8080/api/v1/data/controller/applications/bvs/tenant[name="A"]/vns[name="A1"]/endpoints[name="H1"] {"name": "H1"}

        '''
        
        t = test.Test()
        c = t.controller('main')
        
        helpers.test_log("Input arguments: tenant = %s vnsname = %s endpointname = %s mac address = %s" % (tenant, vnsname, endpointname, mac))
        
        url = '/api/v1/data/controller/applications/bvs/tenant[name="%s"]/vns[name="%s"]/endpoints[name="%s"]' % (tenant, vnsname, endpointname)
        try:
            c.rest.patch(url, {"mac": mac})
        except:
            helpers.test_failure(c.rest.error())
        else: 
            helpers.test_log("Output: %s" % c.rest.result_json())
            return c.rest.content()                         


    def rest_delete_endpoint_mac(self, tenant, vnsname, endpointname, mac):
        '''Add nexthop to ecmp groups aks gateway pool in tenant"
        
            Input:
                `tenant`          tenant name
                `vnsname`         vns name
                `endpointname`    endpoint name
                `mac`          host mac address
            Return: true if configuration is successful, false otherwise
            http://127.0.0.1:8080/api/v1/data/controller/applications/bvs/tenant[name="A"]/vns[name="A1"]/endpoints[name="H1"] {"name": "H1"}
            DELETE http://127.0.0.1:8080/api/v1/data/controller/applications/bvs/tenant[name="A"]/vns[name="A1"]/endpoints[name="bm0"]/mac {}

        '''
        
        t = test.Test()
        c = t.controller('main')
        
        helpers.test_log("Input arguments: tenant = %s vnsname = %s endpointname = %s mac address = %s" % (tenant, vnsname, endpointname, mac))
        
        url = '/api/v1/data/controller/applications/bvs/tenant[name="%s"]/vns[name="%s"]/endpoints[name="%s"]/mac' % (tenant, vnsname, endpointname)
        try:
            c.rest.delete(url, {})
        except:
            helpers.test_failure(c.rest.error())
        else: 
            helpers.test_log("Output: %s" % c.rest.result_json())
            return c.rest.content()                         

    def rest_add_endpoint_portgroup_attachment(self, tenant, vnsname, endpointname, portgroupname, vlan):
        '''Add nexthop to ecmp groups aks gateway pool in tenant"
        
            Input:
                `tenant`          tenant name
                `vnsname`         vns name
                `endpointname`    endpoint name
                `portgroupname`   port-group name
                `vlan`            vlan id or -1 for untagged
            Return: true if configuration is successful, false otherwise
            curl -gX PATCH -H 'Cookie: session_cookie=RKIUFOl07Dqiz10nXJcbquvUcWVJ3xYM' -d '{"port-group-name": "leaf4", "vlan": -1}' 'localhost:8080/api/v1/data/controller/applications/bvs/tenant[name="B"]/vns[name="B1"]/endpoints[name="B1-H1"]/attachment-point'
        '''
        
        t = test.Test()
        c = t.controller('main')
        
        helpers.test_log("Input arguments: tenant = %s vnsname = %s endpointname = %s portgroup = %s vlan = %s" % (tenant, vnsname, endpointname, portgroupname, vlan))
        
        url = '/api/v1/data/controller/applications/bvs/tenant[name="%s"]/vns[name="%s"]/endpoints[name="%s"]/attachment-point' % (tenant, vnsname, endpointname)
        try:
            c.rest.post(url, {"port-group-name": portgroupname, "vlan": vlan})
        except:
            helpers.test_failure(c.rest.error())
        else: 
            helpers.test_log("Output: %s" % c.rest.result_json())
            return c.rest.content()            


    def rest_add_endpoint_switch_attachment(self, tenant, vnsname, endpointname, switchname, switchinterface, vlan):
        '''Add nexthop to ecmp groups aks gateway pool in tenant"
        
            Input:
                `tenant`          tenant name
                `vnsname`         vns name
                `endpointname`    endpoint name
                `switchname`       name of switch
                `switchinterface`    switch port
                `vlan`            vlan id or -1 for untagged
            Return: true if configuration is successful, false otherwise
            
            curl -gX PATCH -H 'Cookie: session_cookie=RKIUFOl07Dqiz10nXJcbquvUcWVJ3xYM' -d '{"switch-name": "leaf1", "interface-name": "leaf1-eth2", "vlan": -1}' 'localhost:8080/api/v1/data/controller/applications/bvs/tenant[name="B"]/vns[name="B1"]/endpoints[name="B1-H1"]/attachment-point'
        '''        
        t = test.Test()
        c = t.controller('main')
        
        helpers.test_log("Input arguments: tenant = %s vnsname = %s endpointname = %s switchname = %s switch interface = %s vlan = %s" % (tenant, vnsname, endpointname, switchname, switchinterface, vlan))
        
        url = '/api/v1/data/controller/applications/bvs/tenant[name="%s"]/vns[name="%s"]/endpoints[name="%s"]/attachment-point' % (tenant, vnsname, endpointname)
        try:
            c.rest.post(url, {"switch-name": switchname, "interface-name": switchinterface, "vlan": vlan})
        except:
            helpers.test_failure(c.rest.error())
        else: 
            helpers.test_log("Output: %s" % c.rest.result_json())
            return c.rest.content()            

    def rest_add_dhcp_relay(self, tenant, vnsname, dhcpserverip):
        '''Create dhcp server on tenant VNS"
        
            Input:
                `tenant`          tenant name
                `vnsname`         name of vns interface
                `dhcpserverip`    IP address of dhcp server
            Return: true if configuration is successful, false otherwise
REST-POST: PATCH http://127.0.0.1:8080/api/v1/data/controller/applications/bvs/tenant[name="C"]/virtual-router/vns-interfaces[vns-name="C1"] {"dhcp-server-ip": "10.2.1.1"}
REST-POST: http://127.0.0.1:8080/api/v1/data/controller/applications/bvs/tenant[name="C"]/virtual-router/vns-interfaces[vns-name="C1"] reply:             
        '''        
        t = test.Test()
        c = t.controller('main')
        
        helpers.test_log("Input arguments: tenant = %s vns name = %s relay-ip = %s" % (tenant, vnsname, dhcpserverip))
        
        url = '/api/v1/data/controller/applications/bvs/tenant[name="%s"]/virtual-router/vns-interfaces[vns-name="%s"]/dhcp-relay' % (tenant, vnsname)
        try:
            c.rest.patch(url, {"dhcp-server-ip": dhcpserverip})
        except:
            helpers.test_failure(c.rest.error())
        else: 
            helpers.test_log("Output: %s" % c.rest.result_json())
            return c.rest.content()            

    def rest_enable_dhcp_relay(self, tenant, vnsname):
        '''Enable dhcp relay on tenant VNS"
        
            Input:
                `tenant`          tenant name
                `vnsname`         name of vns interface
            Return: true if configuration is successful, false otherwise
REST-POST: PATCH http://127.0.0.1:8080/api/v1/data/controller/applications/bvs/tenant[name="C"]/virtual-router/vns-interfaces[vns-name="C1"]/dhcp-relay {"dhcp-relay-enable": true}
REST-POST: http://127.0.0.1:8080/api/v1/data/controller/applications/bvs/tenant[name="C"]/virtual-router/vns-interfaces[vns-name="C1"] reply: ""           
        '''        
        t = test.Test()
        c = t.controller('main')
        
        helpers.test_log("Input arguments: tenant = %s vns name = %s " % (tenant, vnsname))
        
        url = '/api/v1/data/controller/applications/bvs/tenant[name="%s"]/virtual-router/vns-interfaces[vns-name="%s"]/dhcp-relay' % (tenant, vnsname)
        try:
            c.rest.patch(url, {"dhcp-relay-enable": True})
        except:
            helpers.test_failure(c.rest.error())
        else: 
            helpers.test_log("Output: %s" % c.rest.result_json())
            return c.rest.content()            


    def rest_disable_dhcp_relay(self, tenant, vnsname):
        '''Enable dhcp relay on tenant VNS"
        
            Input:
                `tenant`          tenant name
                `vnsname`         name of vns interface
            Return: true if configuration is successful, false otherwise
REST-POST: PATCH http://127.0.0.1:8080/api/v1/data/controller/applications/bvs/tenant[name="C"]/virtual-router/vns-interfaces[vns-name="C1"] {"dhcp-relay-enable": true}
REST-POST: http://127.0.0.1:8080/api/v1/data/controller/applications/bvs/tenant[name="C"]/virtual-router/vns-interfaces[vns-name="C1"] reply: ""           
        '''        
        t = test.Test()
        c = t.controller('main')
        
        helpers.test_log("Input arguments: tenant = %s vns name = %s " % (tenant, vnsname))
        
        url = '/api/v1/data/controller/applications/bvs/tenant[name="%s"]/virtual-router/vns-interfaces[vns-name="%s"]/dhcp-relay' % (tenant, vnsname)
        try:
            c.rest.patch(url, {"dhcp-relay-enable": False})
        except:
            helpers.test_failure(c.rest.error())
        else: 
            helpers.test_log("Output: %s" % c.rest.result_json())
            return c.rest.content() 			

    def rest_add_dhcprelay_circuitid(self, tenant, vnsname, circuitid):
        '''Set dhcp relay circuit id"
        
            Input:
                `tenant`          tenant name
                `vnsname`         name of vns interface
                `circuitid`      Circuit id, can be a string upto 15 characters
            Return: true if configuration is successful, false otherwise
REST-POST: PATCH http://127.0.0.1:8080/api/v1/data/controller/applications/bvs/tenant[name="C"]/virtual-router/vns-interfaces[vns-name="C1"] {"dhcp-circuit-id": "this is a test"}
REST-POST: http://127.0.0.1:8080/api/v1/data/controller/applications/bvs/tenant[name="C"]/virtual-router/vns-interfaces[vns-name="C1"] reply: ""          
        '''        
        t = test.Test()
        c = t.controller('main')
        
        helpers.test_log("Input arguments: tenant = %s vns name = %s circuit id = %s" % (tenant, vnsname, circuitid))
        
        url = '/api/v1/data/controller/applications/bvs/tenant[name="%s"]/virtual-router/vns-interfaces[vns-name="%s"]/dhcp-relay' % (tenant, vnsname)
        try:
            c.rest.patch(url, {"dhcp-circuit-id": circuitid})
        except:
            helpers.test_failure(c.rest.error())
        else: 
            helpers.test_log("Output: %s" % c.rest.result_json())
            return c.rest.content()            


    def rest_delete_dhcp_relay(self, tenant, vnsname, dhcpserverip):
        '''Delete dhcp server "
        
            Input:
                `tenant`          tenant name
                `vnsname`         name of vns interface
                `dhcpserverip`       DHCP server IP, can be anything since it will delete everything under the vns
            Return: true if configuration is successful, false otherwise

REST-POST: DELETE http://127.0.0.1:8080/api/v1/data/controller/applications/bvs/tenant[name="B"]/virtual-router/vns-interfaces[vns-name="B1"]/dhcp-server-ip {}
     
        '''        
        t = test.Test()
        c = t.controller('main')
        
        helpers.test_log("Input arguments: tenant = %s vns name = %s dhcp server ip = %s" % (tenant, vnsname, dhcpserverip))
        
        url = '/api/v1/data/controller/applications/bvs/tenant[name="%s"]/virtual-router/vns-interfaces[vns-name="%s"]/dhcp-relay/dhcp-server-ip' % (tenant, vnsname)
        try:
            c.rest.delete(url, {})
        except:
            helpers.test_failure(c.rest.error())
        else: 
            helpers.test_log("Output: %s" % c.rest.result_json())
            return c.rest.content()            

    def rest_show_forwarding_switch_l3_host_route(self,switch):
        '''
    GET http://127.0.0.1:8080/api/v1/data/controller/applications/bvs/info/forwarding/network/switch%5Bswitch-name%3D%22leaf0a%22%5D/l3-host-route-table
        '''
        t = test.Test()
        c = t.controller('main')
        
        helpers.test_log("Input arguments: switch = %s " % (switch))
        
        url = '/api/v1/data/controller/applications/bvs/info/forwarding/network/switch[switch-name="%s"]/l3-host-route-table' % (switch)
        try:
            c.rest.get(url)
        except:
            helpers.test_failure(c.rest.error())
        else: 
            return c.rest.content()            

    def rest_show_forwarding_switch_l3_cidr_route(self,switch):
        '''
    GET http://127.0.0.1:8080/api/v1/data/controller/applications/bvs/info/forwarding/network/switch%5Bswitch-name%3D%22leaf0a%22%5D/l3-cidr-route-table
        '''
        t = test.Test()
        c = t.controller('main')
        
        helpers.test_log("Input arguments: switch = %s " % (switch))
        
        #url = '/api/v1/data/controller/applications/bvs/info/forwarding/network/switch\%5Bswitch-name\%3D\%22%s\%22\%5D/l3-cidr-route-table' % (switch)
        url = '/api/v1/data/controller/applications/bvs/info/forwarding/network/switch[switch-name="%s"]/l3-cidr-route-table' % (switch)
        try:
            c.rest.get(url)
        except:
            helpers.test_failure(c.rest.error())
        else: 
            return c.rest.content()            
      
    def rest_show_l3_cidr_table(self):
        '''
        GET http://127.0.0.1:8080/api/v1/data/controller/applications/bvs/info/forwarding/network/l3-cidr-table
        '''
        t = test.Test()
        c = t.controller('main')
        
        url = '/api/v1/data/controller/applications/bvs/info/forwarding/network/l3-cidr-table' 
        try:
            c.rest.get(url)
        except:
            helpers.test_failure(c.rest.error())
        else: 
            return c.rest.content()                    

    def rest_show_l3_host_table(self):
        '''
        GET http://127.0.0.1:8080/api/v1/data/controller/applications/bvs/info/forwarding/network/l3-host-table
        '''
        t = test.Test()
        c = t.controller('main')
        
        url = '/api/v1/data/controller/applications/bvs/info/forwarding/network/l3-host-table' 
        try:
            c.rest.get(url)
        except:
            helpers.test_failure(c.rest.error())
        else: 
            return c.rest.content()                    

