import autobot.helpers as helpers
import autobot.restclient as restclient
import autobot.test as test


class T5(object):

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

        
        
     