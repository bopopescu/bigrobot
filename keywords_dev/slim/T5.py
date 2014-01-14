import autobot.helpers as helpers
import autobot.restclient as restclient
import autobot.test as test


class T5(object):

    def __init__(self):
        t = test.Test()
        c = t.controller()
        
        url = '%s/api/v1/auth/login' % c.base_url
        result = c.rest.post(url, {"user":"admin", "password":"adminadmin"})
        session_cookie = result['content']['session_cookie']
        c.rest.set_session_cookie(session_cookie)
        
    def rest_create_tenant(self, tenant):
        t = test.Test()
        c = t.controller()

        helpers.log("Input arguments: tenant = %s" % tenant )
                
        url = '%s/api/v1/data/controller/applications/bvs/tenant[name="%s"]' % (c.base_url, tenant)
        c.rest.put(url, {"name": tenant})
        helpers.log("Output: %s" % c.rest.result_json())

        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())

        return c.rest.content()
        
    def _rest_show_tenant(self, tenant=None, negative=False):
        t = test.Test()
        c = t.controller()

        if tenant:
            # Show a specific tenant
            url = '%s/api/v1/data/controller/applications/bvs/tenant[name="%s"]' % (c.base_url, tenant)
        else:
            # Show all tenants
            url = '%s/api/v1/data/controller/applications/bvs/tenant' % (c.base_url)
            
        c.rest.get(url)
        helpers.log("Output: %s" % c.rest.result_json())
        
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())

        data = c.rest.content()

        # If showing all tenants, then we don't need to check further
        if tenant is None:
            return data
        
        # Search list of tenants to find a match
        for t in data:
            actual_tenant = t['name']
            if actual_tenant == tenant:
                helpers.log("Match: Actual tenant '%s' == expected tenant '%s'" % (actual_tenant, tenant))
                
                if negative:
                    helpers.test_failure("Unexpected match: Actual tenant '%s' == expected tenant '%s'" % (actual_tenant, tenant))
                else:
                    return data
            else:
                helpers.log("No match: Actual tenant '%s' != expected tenant '%s'" % (actual_tenant, tenant))
        
        # If we reach here, then we didn't find a matching tenant.
        if negative:
            helpers.log("Expected No match: For tenant '%s'" % tenant)
            return data
        else:
            helpers.test_failure("No match: For tenant '%s'." % tenant)

    def rest_show_tenant(self, tenant=None):
        helpers.log("Input arguments: tenant = %s" % tenant )
        return self._rest_show_tenant(tenant)
        
    def rest_show_tenant_gone(self, tenant=None):
        helpers.log("Input arguments: tenant = %s" % tenant )
        return self._rest_show_tenant(tenant, negative=True)
        
    def rest_delete_tenant(self, tenant=None):
        t = test.Test()
        c = t.controller()

        helpers.log("Input arguments: tenant = %s" % tenant )
        
        url = '%s/api/v1/data/controller/applications/bvs/tenant[name="%s"]' % (c.base_url, tenant)

        c.rest.delete(url, {"name": tenant})
        helpers.log("Ouput: %s" % c.rest.result_json())

        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())

        return c.rest.content()

    def test_args(self, arg1, arg2, arg3):
        try:
            helpers.log("Input arguments: arg1 = %s" % arg1 )
            helpers.log("Input arguments: arg2 = %s" % arg2 )
            helpers.log("Input arguments: arg3 = %s" % arg3 )
        except:
            return False
        else:
            return True

    def rest_create_vns(self, tenant, vns):
        t = test.Test()
        c = t.controller()
        
        helpers.test_log("Input arguments: tenant = %s vns = %s" % (tenant, vns ))
        
        url = '%s/api/v1/data/controller/applications/bvs/tenant[name="%s"]/vns[name="%s"]' % (c.base_url, tenant, vns)
        try:
            c.rest.put(url, {"name": vns})
        except:
            helpers.test_failure(c.rest.error())
        else:
            if not c.rest.status_code_ok():
                helpers.test_failure(c.rest.error())
    
            return c.rest.content()
    
    def rest_delete_vns(self, tenant, vns=None):
        t = test.Test()
        c = t.controller()
        
        helpers.test_log("Input arguments: tenant = %s vns = %s" % (tenant, vns ))
        
        url = '%s/api/v1/data/controller/applications/bvs/tenant[name="%s"]/vns[name="%s"]' % (c.base_url, tenant, vns)
        c.rest.delete(url, {"name": vns})
        helpers.test_log("Output: %s" % c.rest.result_json())

        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())

        return c.rest.content()
    
    def rest_create_portgroup(self, pg):
        t = test.Test()
        c = t.controller()
        
        helpers.test_log("Input arguments: port-group = %s" % pg )
        
        url = '%s/api/v1/data/controller/fabric/port-group[name="%s"]' % (c.base_url, pg)
        c.rest.put(url, {"name": pg})
        helpers.test_log("Output: %s" % c.rest.result_json())

        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())

        return c.rest.content()
    
    def rest_delete_portgroup(self, pg=None):
        t = test.Test()
        c = t.controller()
        
        helpers.test_log("Input arguments: port-group = %s" % pg )
        
        url = '%s/api/v1/data/controller/fabric/port-group[name="%s"]' % (c.base_url, pg)
        c.rest.delete(url, {"name": pg})
        helpers.test_log("Output: %s" % c.rest.result_json())

        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())

        return c.rest.content()
    
    def rest_create_endpoint(self, tenant, vns, endpoint):
        t = test.Test()
        c = t.controller()
        
        helpers.test_log("Input arguments: tenant = %s, vns = %s, endpoint = %s" % (tenant, vns, endpoint ))
        
        url = '%s/api/v1/data/controller/applications/bvs/tenant[name="%s"]/vns[name="%s"]/endpoints[name="%s"]' % (c.base_url, tenant, vns, endpoint)
        c.rest.put(url, {"name": endpoint})
        helpers.test_log("Output: %s" % c.rest.result_json())

        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())

        return c.rest.content()
    
    def rest_delete_endpoint(self, tenant, vns, endpoint=None):
        t = test.Test()
        c = t.controller()
        
        helpers.test_log("Input arguments: tenant = %s vns = %s endpoint = %s" % (tenant, vns, endpoint ))
        
        url = '%s/api/v1/data/controller/applications/bvs/tenant[name="%s"]/vns[name="%s"]/endpoints[name="%s"]' % (c.base_url, tenant, vns, endpoint)
        c.rest.delete(url, {"name": endpoint})
        helpers.test_log("Output: %s" % c.rest.result_json())

        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())

        return c.rest.content()
   
    def rest_add_interface_to_portgroup(self, switch, intf, pg):
        t = test.Test()
        c = t.controller()
                       
        helpers.test_log("Input arguments: switch-name = %s Interface-name = %s port-group = %s" % (switch, intf, pg))
        
        url = '%s/api/v1/data/controller/core/switch-config[name="%s"]/interface[name="%s"]' % (c.base_url, switch, intf)
        c.rest.put(url, {"name": intf, "port-group-name": pg})
        helpers.test_log("Output: %s" % c.rest.result_json())

        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())

        return c.rest.content()
    
    def rest_delete_interface_from_portgroup(self, switch, intf, pg):
        t = test.Test()
        c = t.controller()
                
        helpers.test_log("Input arguments: switch-name = %s Interface-name = %s port-group = %s" % (switch, intf, pg))
        
        url = '%s/api/v1/data/controller/core/switch-config[name="%s"]/interface[name="%s"]' % (c.base_url, switch, intf)
        c.rest.delete(url, {"core/switch-config/interface/port-group-name": pg})
        helpers.test_log("Output: %s" % c.rest.result_json())

        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())

        return c.rest.content()
    
    def rest_add_portgroup_to_vns(self, tenant, vns, pg, vlan):
        t = test.Test()
        c = t.controller()
        
        helpers.test_log("Input arguments: tenant = %s vns = %s port-group = %s vlan = %s" % (tenant, vns, pg, vlan ))
        
        url = '%s/api/v1/data/controller/applications/bvs/tenant[name="%s"]/vns[name="%s"]/port-group-membership-rules[port-group-name="%s"]' % (c.base_url, tenant, vns, pg)
        c.rest.put(url, {"vlan": vlan, "port-group-name": pg})
        helpers.test_log("Output: %s" % c.rest.result_json())

        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())

        return c.rest.content()
            
    def rest_add_portgroup_to_endpoint(self, tenant, vns, endpoint, pg, vlan):
        t = test.Test()
        c = t.controller()
        
        helpers.test_log("Input arguments: tenant = %s vns = %s endpoint = %s port-group = %s vlan = %s" % (tenant, vns, endpoint, pg, vlan ))
        
        url = '%s/api/v1/data/controller/applications/bvs/tenant[name="%s"]/vns[name="%s"]/endpoints[name="%s"]/attachment-point' % (c.base_url, tenant, vns, endpoint)
        c.rest.put(url, {"port-group-name": pg, "vlan": vlan})
        helpers.test_log("Output: %s" % c.rest.result_json())

        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())

        return c.rest.content()
            
    def rest_ping(self, bm0, bm1):
        pass
            
    def rest_change_to_tenant(self, tenant):
        t = test.Test()
        c = t.controller()
        
        helpers.test_log("Input arguments: tenant = %s" % tenant )
        
        url = '%s/api/v1/data/controller/applications/bvs/tenant[name="%s"]?config=true&select=name&single=true' % (c.base_url, tenant)
        c.rest.get(url, {"name": tenant})
        helpers.test_log("Output: %s" % c.rest.result_json())

        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())

        return c.rest.content()
    
    def rest_change_to_vns(self, tenant, vns): 
        t = test.Test()
        c = t.controller()
        
        helpers.test_log("Input arguments: vns = %s" % vns )
        
        url = '%s/api/v1/data/controller/applications/bvs/tenant[name="%s"]/vns[name="%s"]?config=true&select=name&single=true' % (c.base_url, tenant, vns)
        c.rest.get(url, {"name": vns})
        helpers.test_log("Output: %s" % c.rest.result_json())

        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())

        return c.rest.content()
    
    def rest_change_to_portgroup(self, pg): 
        t = test.Test()
        c = t.controller()
        
        helpers.test_log("Input arguments: port-group = %s" % pg )
        
        url = '%s/api/v1/data/controller/fabric/port-group[name="%s"]?config=true&select=name&single=true' % (c.base_url, pg)
        c.rest.get(url, {"name": pg})
        helpers.test_log("Output: %s" % c.rest.result_json())

        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())

        return c.rest.content()

    def rest_delete_portgroup_from_vns(self, tenant, vns, pg, vlan):
        t = test.Test()
        c = t.controller()
        
        helpers.test_log("Input arguments: tenant = %s vns = %s port-group = %s vlan = %s" % (tenant, vns, pg, vlan ))
        
        url = '%s/api/v1/data/controller/applications/bvs/tenant[name="%s"]/vns[name="%s"]/port-group-membership-rules[port-group-name="%s"]' % (c.base_url, tenant, vns, pg)
        c.rest.delete(url, {"vlan": vlan})
        helpers.test_log("Output: %s" % c.rest.result_json())

        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())

        return c.rest.content()
            
    def rest_show_endpoints(self):
        pass
    def rest_add_interface_to_vns(self, tenant, vns, switch, intf, vlan):
        t = test.Test()
        c = t.controller()
        
        helpers.test_log("Input arguments: tenant = %s vns = %s switch-name = %s interface-name = %s vlan = %s" % (tenant, vns, switch, intf, vlan ))
        
        url = '%s/api/v1/data/controller/applications/bvs/tenant[name="%s"]/vns[name="%s"]/switch-port-membership-rules[switch-name="%s"][interface-name="%s"]' % (c.base_url, tenant, vns, switch, intf)
        c.rest.put(url, {"switch-name": switch, "interface-name": intf, "vlan": vlan})
        helpers.test_log("Output: %s" % c.rest.result_json())

        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())

        return c.rest.content() 
      
    def rest_delete_interface_from_vns(self, tenant, vns, switch, intf, vlan):
        t = test.Test()
        c = t.controller()
        
        helpers.test_log("Input arguments: tenant = %s vns = %s switch-name = %s interface-name = %s vlan = %s" % (tenant, vns, switch, intf, vlan ))
        
        url = '%s/api/v1/data/controller/applications/bvs/tenant[name="%s"]/vns[name="%s"]/switch-port-membership-rules[switch-name="%s"][interface-name="%s"]' % (c.base_url, tenant, vns, switch, intf)
        c.rest.delete(url, {"vlan": vlan})
        helpers.test_log("Output: %s" % c.rest.result_json())

        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())

        return c.rest.content()
            
    def rest_add_interface_to_endpoint(self, tenant, vns, endpoint, switch, intf, vlan):
        t = test.Test()
        c = t.controller()
        
        helpers.test_log("Input arguments: tenant = %s vns = %s endpoint = %s switch-name = %s interface-name = %s vlan = %s" % (tenant, vns, endpoint, switch, intf, vlan ))
        
        url = '%s/api/v1/data/controller/applications/bvs/tenant[name="%s"]/vns[name="%s"]/endpoints[name="%s"]/attachment-point' % (c.base_url, tenant, vns, endpoint)
        c.rest.put(url, {"switch-name": switch, "interface-name": intf, "vlan": vlan})
        helpers.test_log("Output: %s" % c.rest.result_json())

        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
            
        return c.rest.content()

    
    def rest_configure_ip_endpoint(self, tenant, vns, endpoint, ip):
        t = test.Test()
        c = t.controller()
        url = '%s/api/v1/data/controller/applications/bvs/tenant[name="%s"]/vns[name="%s"]/endpoints[name="%s"]' % (c.base_url, tenant, vns, endpoint)
        c.rest.patch(url, {"ip-address": ip})
        helpers.test_log("Output: %s" % c.rest.result_json())
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
        return c.rest.content()
    
    def rest_configure_mac_endpoint(self, tenant, vns, endpoint, mac):
        t = test.Test()
        c = t.controller()
        url = '%s/api/v1/data/controller/applications/bvs/tenant[name="%s"]/vns[name="%s"]/endpoints[name="%s"]' % (c.base_url, tenant, vns, endpoint)
        c.rest.patch(url, {"mac": mac})
        helpers.test_log("Output: %s" % c.rest.result_json())
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
        return c.rest.content()


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
                `nexthop`         nexthop IP address
            Return: true if configuration is successful, false otherwise
        '''
        
        t = test.Test()
        c = t.controller()
        
        helpers.test_log("Input arguments: tenant = %s dstroute = %s nexthop = %s " % (tenant, dstroute, nexthop))
        
        url = '%s/api/v1/data/controller/applications/bvs/tenant[name="%s"]/virtual-router/routes' % (c.base_url, tenant)
        try:
            c.rest.post(url, {"dest-ip-subnet": dstroute, "next-hop": nexthop})
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
     