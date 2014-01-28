import autobot.helpers as helpers
import autobot.restclient as restclient
import autobot.test as test


class T5_L3(object):

    def __init__(self):
        pass
        
    def rest_create_vns_ip(self, tenant, vns, ipaddr, netmask):
        '''Create vns router interface via command "virtual-router vns interface"
        
            Input:
                `tenant`        tenant name
                `vns`           vns interface name which must be similar to VNS
                `ipaddr`        interface ip address
                `netmask`       vns subnet mask
            
            Return: true if configuration is successful, false otherwise
        '''
        
        t = test.Test()
        c = t.controller()
        
        helpers.test_log("Input arguments: tenant = %s vns = %s ipaddr = %s netmask = %s " % (tenant, vns, ipaddr, netmask ))
        
        url = '%s/api/v1/data/controller/applications/bvs/tenant[name="%s"]/virtual-router/vns-interfaces' % (c.base_url, tenant)
        ip_addr = ipaddr + "/" + netmask
        try:
            c.rest.post(url, {"vns-name": vns, "ip-cidr": str(ip_addr), "active": True})
        except:
            helpers.test_failure(c.rest.error())
        else: 
            helpers.test_log("Output: %s" % c.rest.result_json())
            return c.rest.content()
        
   
    def rest_attach_tenant_routers_to_system(self, tenant):        
        '''Attach tenant router to system router"
        
            Input:
                `tenant`        tenant name
            
            Return: true if configuration is successful, false otherwise
            
REST-POST: PUT http://127.0.0.1:8080/api/v1/data/controller/applications/bvs/tenant[name="system"]/virtual-router/tenant-interfaces[tenant-name="A"] {"tenant-name": "A"}
REST-POST: http://127.0.0.1:8080/api/v1/data/controller/applications/bvs/tenant[name="system"]/virtual-router/tenant-interfaces[tenant-name="A"] reply: ""

        '''
        
        t = test.Test()
        c = t.controller()
        
        helpers.test_log("Input arguments: tenant = %s " % (tenant))
        
        url = '%s/api/v1/data/controller/applications/bvs/tenant[name="system"]/virtual-router/tenant-interfaces[tenant-name="%s"]' % (c.base_url, tenant)
        try:
            c.rest.post(url, {"tenant-name": tenant, "active": True})
        except:
            helpers.test_failure(c.rest.error())
        else: 
            helpers.test_log("Output: %s" % c.rest.result_json())
            return c.rest.content() 
        
        
    def rest_attach_system_to_tenant_routers(self, tenant):        
        '''Attach tenant router to system router"
        
            Input:
                `tenant`        tenant name
            
            Return: true if configuration is successful, false otherwise
            
        '''
        
        t = test.Test()
        c = t.controller()
        
        helpers.test_log("Input arguments: tenant = %s " % (tenant))
        
        url = '%s/api/v1/data/controller/applications/bvs/tenant[name="%s"]/virtual-router/tenant-interfaces[tenant-name="system"]' % (c.base_url, tenant)
        try:
            c.rest.post(url, {"tenant-name": "system", "active": True})
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
        c = t.controller()
        
        nexthop_dict = helpers.from_json(nexthop)
        
        helpers.test_log("Input arguments: tenant = %s dstroute = %s nexthop = %s " % (tenant, dstroute, nexthop))
        
        url = '%s/api/v1/data/controller/applications/bvs/tenant[name="%s"]/virtual-router/routes' % (c.base_url, tenant)
        try:
            c.rest.post(url, {"dest-ip-subnet": dstroute, "next-hop": nexthop_dict})
        except:
            helpers.test_failure(c.rest.error())
        else: 
            helpers.test_log("Output: %s" % c.rest.result_json())
            return c.rest.content()    
                   
        
    def rest_show_endpoints(self):
        t = test.Test()
        c = t.controller()
        url = '%s/api/v1/data/controller/applications/bvs/info/endpoint-manager/endpoints' % (c.base_url)
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
        c = t.controller()
        
        helpers.test_log("Input arguments: tenant = %s ecmpgroup = %s" % (tenant, ecmpgroup))
        
        url = '%s/api/v1/data/controller/applications/bvs/tenant[name="%s"]/virtual-router/ecmp-groups' % (c.base_url, tenant)
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
        c = t.controller()
        
        helpers.test_log("Input arguments: tenant = %s ecmpgroup = %s nexthop = %s" % (tenant, ecmpgroup, nexthop))
        
        url = '%s/api/v1/data/controller/applications/bvs/tenant[name="%s"]/virtual-router/ecmp-groups[name="%s"]/ip-addresses' % (c.base_url, tenant, ecmpgroup)
        try:
            c.rest.put(url, {"ip-address": nexthop})
        except:
            helpers.test_failure(c.rest.error())
        else: 
            helpers.test_log("Output: %s" % c.rest.result_json())
            return c.rest.content()                         

     

    def rest_create_endpoint_ip(self, tenant, vnsname, endpointname, ipaddr):
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
        c = t.controller()
        
        helpers.test_log("Input arguments: tenant = %s vnsname = %s endpointname = %s ipaddress = %s" % (tenant, vnsname, endpointname, ipaddr))
        
        url = '%s/api/v1/data/controller/applications/bvs/tenant[name="%s"]/vns[name="%s"]/endpoints[name="%s"]' % (c.base_url, tenant, vnsname, endpointname)
        try:
            c.rest.patch(url, {"ip-address": ipaddr})
        except:
            helpers.test_failure(c.rest.error())
        else: 
            helpers.test_log("Output: %s" % c.rest.result_json())
            return c.rest.content()                         

    def rest_create_endpoint_mac(self, tenant, vnsname, endpointname, mac):
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
        c = t.controller()
        
        helpers.test_log("Input arguments: tenant = %s vnsname = %s endpointname = %s mac address = %s" % (tenant, vnsname, endpointname, mac))
        
        url = '%s/api/v1/data/controller/applications/bvs/tenant[name="%s"]/vns[name="%s"]/endpoints[name="%s"]' % (c.base_url, tenant, vnsname, endpointname)
        try:
            c.rest.patch(url, {"mac": mac})
        except:
            helpers.test_failure(c.rest.error())
        else: 
            helpers.test_log("Output: %s" % c.rest.result_json())
            return c.rest.content()                         


    def rest_create_endpoint_portgroup_attachment(self, tenant, vnsname, endpointname, portgroupname, vlan):
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
        c = t.controller()
        
        helpers.test_log("Input arguments: tenant = %s vnsname = %s endpointname = %s portgroup = %s vlan = %s" % (tenant, vnsname, endpointname, portgroupname, vlan))
        
        url = '%s/api/v1/data/controller/applications/bvs/tenant[name="%s"]/vns[name="%s"]/endpoints[name="%s"]/attachment-point' % (c.base_url, tenant, vnsname, endpointname)
        try:
            c.rest.post(url, {"port-group-name": portgroupname, "vlan": vlan})
        except:
            helpers.test_failure(c.rest.error())
        else: 
            helpers.test_log("Output: %s" % c.rest.result_json())
            return c.rest.content()            


    def rest_create_endpoint_switch_attachment(self, tenant, vnsname, endpointname, switchname, switchinterface, vlan):
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
        c = t.controller()
        
        helpers.test_log("Input arguments: tenant = %s vnsname = %s endpointname = %s switchname = %s switch interface = %s vlan = %s" % (tenant, vnsname, endpointname, switchname, switchinterface, vlan))
        
        url = '%s/api/v1/data/controller/applications/bvs/tenant[name="%s"]/vns[name="%s"]/endpoints[name="%s"]/attachment-point' % (c.base_url, tenant, vnsname, endpointname)
        try:
            c.rest.post(url, {"switch-name": switchname, "interface-name": switchinterface, "vlan": vlan})
        except:
            helpers.test_failure(c.rest.error())
        else: 
            helpers.test_log("Output: %s" % c.rest.result_json())
            return c.rest.content()            

    def rest_create_dhcp_relay(self, tenant, vnsname, dhcpserverip):
        '''Add nexthop to ecmp groups aks gateway pool in tenant"
        
            Input:
                `tenant`          tenant name
                `vnsname`         name of vns interface
                `dhcpserverip`    IP address of dhcp server
            Return: true if configuration is successful, false otherwise
REST-POST: PATCH http://127.0.0.1:8080/api/v1/data/controller/applications/bvs/tenant[name="C"]/virtual-router/vns-interfaces[vns-name="C1"] {"dhcp-server-ip": "10.2.1.1"}
REST-POST: http://127.0.0.1:8080/api/v1/data/controller/applications/bvs/tenant[name="C"]/virtual-router/vns-interfaces[vns-name="C1"] reply:             
        '''        
        t = test.Test()
        c = t.controller()
        
        helpers.test_log("Input arguments: tenant = %s vns name = %s relay-ip = %s" % (tenant, vnsname, dhcpserverip))
        
        url = '%s/api/v1/data/controller/applications/bvs/tenant[name="%s"]/virtual-router/vns-interfaces[vns-name="%s"]' % (c.base_url, tenant, vnsname)
        try:
            c.rest.post(url, {"dhcp-server-ip": dhcpserverip})
        except:
            helpers.test_failure(c.rest.error())
        else: 
            helpers.test_log("Output: %s" % c.rest.result_json())
            return c.rest.content()            

    def rest_toggle_dhcp_relay(self, tenant, vnsname, togglevalue):
        '''Add nexthop to ecmp groups aks gateway pool in tenant"
        
            Input:
                `tenant`          tenant name
                `vnsname`         name of vns interface
                `togglevalue`     True or False to enable or disable dhcp relay
            Return: true if configuration is successful, false otherwise
REST-POST: PATCH http://127.0.0.1:8080/api/v1/data/controller/applications/bvs/tenant[name="C"]/virtual-router/vns-interfaces[vns-name="C1"] {"dhcp-relay-enable": true}
REST-POST: http://127.0.0.1:8080/api/v1/data/controller/applications/bvs/tenant[name="C"]/virtual-router/vns-interfaces[vns-name="C1"] reply: ""           
        '''        
        t = test.Test()
        c = t.controller()
        
        helpers.test_log("Input arguments: tenant = %s vns name = %s toggle values = %s" % (tenant, vnsname, togglevalue))
        
        url = '%s/api/v1/data/controller/applications/bvs/tenant[name="%s"]/virtual-router/vns-interfaces[vns-name="%s"]' % (c.base_url, tenant, vnsname, togglevalue)
        try:
            c.rest.post(url, {"dhcp-relay-enable": togglevalue})
        except:
            helpers.test_failure(c.rest.error())
        else: 
            helpers.test_log("Output: %s" % c.rest.result_json())
            return c.rest.content()            

    def rest_set_dhcprelay_circuitid(self, tenant, vnsname, circuitid):
        '''Add nexthop to ecmp groups aks gateway pool in tenant"
        
            Input:
                `tenant`          tenant name
                `vnsname`         name of vns interface
                `circuitid`      Circuit id, can be a string
            Return: true if configuration is successful, false otherwise
REST-POST: PATCH http://127.0.0.1:8080/api/v1/data/controller/applications/bvs/tenant[name="C"]/virtual-router/vns-interfaces[vns-name="C1"] {"dhcp-circuit-id": "this is a test"}
REST-POST: http://127.0.0.1:8080/api/v1/data/controller/applications/bvs/tenant[name="C"]/virtual-router/vns-interfaces[vns-name="C1"] reply: ""          
        '''        
        t = test.Test()
        c = t.controller()
        
        helpers.test_log("Input arguments: tenant = %s vns name = %s circuit id = %s" % (tenant, vnsname, circuitid))
        
        url = '%s/api/v1/data/controller/applications/bvs/tenant[name="%s"]/virtual-router/vns-interfaces[vns-name="%s"]' % (c.base_url, tenant, vnsname, circuitid)
        try:
            c.rest.post(url, {"dhcp-circuit-id": circuitid})
        except:
            helpers.test_failure(c.rest.error())
        else: 
            helpers.test_log("Output: %s" % c.rest.result_json())
            return c.rest.content()            


    def rest_delete_dhcprelay(self, tenant, vnsname, dhcpserverip):
        '''Add nexthop to ecmp groups aks gateway pool in tenant"
        
            Input:
                `tenant`          tenant name
                `vnsname`         name of vns interface
                `dhcpserverip`       DHCP server IP, can be anything since it will delete everything under the vns
            Return: true if configuration is successful, false otherwise

REST-POST: DELETE http://127.0.0.1:8080/api/v1/data/controller/applications/bvs/tenant[name="B"]/virtual-router/vns-interfaces[vns-name="B1"]/dhcp-server-ip {}
     
        '''        
        t = test.Test()
        c = t.controller()
        
        helpers.test_log("Input arguments: tenant = %s vns name = %s dhcp server ip = %s" % (tenant, vnsname, dhcpserverip))
        
        url = '%s/api/v1/data/controller/applications/bvs/tenant[name="%s"]/virtual-router/vns-interfaces[vns-name="%s"]/dhcp-server-ip' % (c.base_url, tenant, vnsname)
        try:
            c.rest.delete(url, {})
        except:
            helpers.test_failure(c.rest.error())
        else: 
            helpers.test_log("Output: %s" % c.rest.result_json())
            return c.rest.content()            

