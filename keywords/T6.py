'''
###  WARNING !!!!!!!
###
###  This is where common code for all T6 will go in.
###  If existing T5 keywords can be enhanced to support T6 features
###  (e.g., IVS), then you can enhance the T5 library. This T6 library
###  is intended for new T6 keywords.
###
###  To commit new code, please contact the Library Owner:
###  Prashanth Padubidry (prashanth.padubidry@bigswitch.com)
###
###  DO NOT COMMIT CODE WITHOUT APPROVAL FROM LIBRARY OWNER
###
###  Last Updated: 01/28/2015
###
###  WARNING !!!!!!!
'''

import autobot.helpers as helpers
import autobot.test as test
from keywords.BsnCommon import BsnCommon
from keywords.T5 import T5
import re
import sys
import json
from netaddr import *


class T6(object):

    def rest_show_t6_dummy(self, node):
        """
        This is a dummy keyword...
        """
        t = test.Test()
        c = t.controller(node)
        helpers.log("Dummy T6 keyword...")
        return True
    
    def rest_verify_vswitch_portgroup(self, pg_count):
        ''' function to verify the vswitch portgroup
        Input: no of vswitch auto portgroup count expected , each vswitch will be one portgroup
        '''
        t = test.Test()
        c = t.controller('master')
        url = '/api/v1/data/controller/applications/bcf/info/fabric/port-group' % ()
        c.rest.get(url)
        data = c.rest.content()
        count = 0
        for i in range(0, len(data)):
            if data[i]["mode"] == "static-auto-vswitch-inband":
                count = count + 1
            else:
                continue
        if int(count) == int(pg_count):
            helpers.log("Expected vswitch portgroups are present No of link %s" % int(pg_count))
            return True
        else:
            helpers.log("Fail: Expected vswitch portgroups are not present in the controller expected = %d, Actual = %d" % (int(pg_count), int(count)))
            return False
        
    def rest_verify_fabric_vswitch_all(self):
        ''' Function to verify vswitch connection state for all the vswitches
        '''
        t = test.Test()
        c = t.controller('master')
        url1 = '/api/v1/data/controller/applications/bcf/info/fabric/switch' % ()
        c.rest.get(url1)
        data = c.rest.content()
        for i in range (0, len(data)):
            if (data[i]["fabric-connection-state"] == "not_connected") and (data[i]["fabric-role"] == "virtual"):
                helpers.test_failure("Fabric manager status for vswitch is incorrect")
        helpers.log("Fabric manager status is correct")
        return True
    
    def rest_add_nat_switch(self, nat_switch):
        '''function to add nat-switch to nat-pool
        Input: vswitch name
        '''
        t = test.Test()
        c = t.controller('master')
        url = '/api/v1/data/controller/applications/bcf/nat-pool/switch[name="%s"]' % nat_switch
        try:
            c.rest.put(url, {"name": nat_switch})
        except:
            return False
        else:
            return True
        
    def rest_verify_nat_switch(self, nat_switch):
        ''' Function to verify the nat-pool switch state
        Input: vswitch name to be verified as nat switch
        '''
        t = test.Test()
        c = t.controller('master')
        url = '/api/v1/data/controller/applications/bcf/info/endpoint-manager/nat-pool'
        c.rest.get(url)
        data = c.rest.content()
        for i in range (0, len(data)):
            if data[i]["switch"] == nat_switch:
                if data[i]["state"] == "active":
                    helpers.log("Given switch is configured under nat-pool and state is active")
                    return True
                else:
                    helpers.log("Given switch is not active in nat-pool")
                    return False
            else:
                helpers.log("Given switch is not configured under nat-pool")
                return False
    
    def rest_delete_nat_switch(self, nat_switch):
        '''Function to delete nat switch from pool
        Input: vswitch name
        '''
        t = test.Test()
        c = t.controller('master')
        url = '/api/v1/data/controller/applications/bcf/nat-pool/switch[name="%s"]' % nat_switch
        try:
            c.rest.delete(url, {})
        except:
            return False
        else:
            return True
        
    def rest_add_nat_profile(self, tenant, nat_profile):
        '''Function to add nat profile in logical router
        Input: tenant name, nat profile name to be created
        '''
        t = test.Test()
        c = t.controller('master')
        url = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]/logical-router/nat-profile[name="%s"]' % (tenant, nat_profile)
        try:
            c.rest.put(url, {"name": nat_profile})
        except:
            return False
        else:
            return True
        
    def rest_delete_nat_profile(self, tenant, nat_profile):
        '''Function to delete nat-profile from logical router
        Input: tenant name, nat profile name
        '''
        t = test.Test()
        c = t.controller('master')
        url = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]/logical-router/nat-profile[name="%s"]' % (tenant, nat_profile)
        try:
            c.rest.delete(url, {})
        except:
            return False
        else:
            return True
        
    def rest_add_pat(self, tenant, nat_profile):
        ''' Function to enable pat(port-address-translation) for a nat-profile
        Input: tenant name, nat profile name
        '''
        t = test.Test()
        c = t.controller('master')
        url = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]/logical-router/nat-profile[name="%s"]/pat' % (tenant, nat_profile)
        try:
            c.rest.put(url, {})
        except:
            return False
        else:
            return True
    
    def rest_add_pat_public_ip(self, tenant, nat_profile, public_ip):
        ''' Function to enable pat for a nat-profile
        Input: tenant name, nat profile name, public IP to be configured in NAT
        '''
        t = test.Test()
        c = t.controller('master')
        url = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]/logical-router/nat-profile[name="%s"]/pat' % (tenant, nat_profile)
        try:
            c.rest.patch(url, {"ip-address": public_ip})
        except:
            return False
        else:
            return True
    def rest_add_nat_remote_tenant(self, tenant, nat_profile, remote_tenant, remote_segment):
        ''' Function to add remote tennat and segment for nat-profile
        Input: tenant name, nat profile name, remote external tenant name, remote external segment name which to be created as public
        '''
        t = test.Test()
        c = t.controller('master')
        url = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]/logical-router/nat-profile[name="%s"]' % (tenant, nat_profile)
        try:
            c.rest.patch(url, {"remote-segment": remote_segment, "remote-tenant": remote_tenant})
        except:
            return False
        else:
            return True
        
    def rest_verify_nat_profile(self, tenant, nat_profile):
        '''Function to verify nat-profile status for tenant logical router
        Input: tenant name, nat profile name
        '''
        t = test.Test()
        c = t.controller('master')
        url = '/api/v1/data/controller/applications/bcf/info/logical-router-manager/logical-router[name="%s"]/nat-profile' % tenant
        c.rest.get(url)
        data = c.rest.content()
        for i in range(0, len(data)):
            if data[i]["logical-router"] == tenant and data[i]["name"] == nat_profile:
                if data[i]["state"] == "active":
                        helpers.log("given nat-profile is applied to tenant logical router and status is active")
                        return True
                else:
                        helpers.log("given nat-profile is not active")
                        return False
            else:
                continue
    
    def rest_verify_pat_profile(self, tenant, nat_profile):
        '''Function to verify nat-profile status for tenant logical router
        Input: tenant name, nat profile name
        '''
        t = test.Test()
        c = t.controller('master')
        url = '/api/v1/data/controller/applications/bcf/info/logical-router-manager/logical-router[name="%s"]/pat-profile' % tenant
        c.rest.get(url)
        data = c.rest.content()
        for i in range(0, len(data)):
            if data[i]["logical-router"] == tenant and data[i]["nat-profile"] == nat_profile:
                if data[i]["state"] == "active" and data[i]["attachment-point"] != "":
                        helpers.log("given nat-profile is applied to tenant logical router and status is active")
                        return True
                else:
                        helpers.log("given nat-profile is not active")
                        return False
            else:
                continue
    
    def rest_verify_nat_attachment_point(self, tenant, nat_profile, nat_switch):
        '''Function to verify nat ivs switch attachment point for fixed nat switch
        Input: tenant name, nat profile name, configured vswitch name for NAT
        '''
        t = test.Test()
        c = t.controller('master')
        url = '/api/v1/data/controller/applications/bcf/info/logical-router-manager/logical-router[name="%s"]/nat-profile' % tenant
        c.rest.get(url)
        data = c.rest.content()
        for i in range(0, len(data)):
            if data[i]["name"] == nat_profile and data[i]["state"] == "active":
                attachment_point = data[i]["attachment-point"]
                ivs_switch = attachment_point.split('|')
                if ivs_switch[0] == nat_switch:
                        helpers.log("tenant logical router has correct nat attachment point")
                        return True
                else:
                        helpers.log("logical router nat attachment point is not correct")
                        return False
            else:
                    continue
        return False
                
    def rest_verify_tenant_route_nat(self, tenant, nat_profile):
        '''Function to verify routes in tenant showing nat next-hop
        Input: tenant name, nat profile
        '''
        t = test.Test()
        c = t.controller('master')
        url = '/api/v1/data/controller/applications/bcf/info/logical-router-manager/logical-router[name="%s"]/route' % tenant
        c.rest.get(url)
        data = c.rest.content()
        for i in range(0, len(data)):
            if data[i]["logical-router"] == tenant:
                next_hop = data[i]["next-hop-group"].split(' ')
                if next_hop[2] == nat_profile:
                    if data[i]["status"] == "Active":
                        helpers.log("Tenant Logical router route nexthop is nat profile and status is active")
                        return True
                    else:
                        helpers.log("Tenant logical router nat next hop is not active")
                        return False
                else:
                    continue
            else:
                helpers.log("Given tenant is not present in the config")
                return False
        return False
        
    def rest_show_tenant_logical_router_default_route_state(self, tenant, nat_profile):
        '''function to verify tenant logical router next-hop
        Input: tenant name, nat profile
        '''
        t = test.Test()
        c = t.controller('master')
        url = '/api/v1/data/controller/applications/bcf/info/logical-router-manager/logical-router[name="%s"]?select=state' % tenant
        c.rest.get(url)
        data = c.rest.content()
        if data[0]["name"] == tenant:
            default_state = data[0]["state"][0]["default-route-state"].split(' ')
            if default_state[3] == nat_profile:
                    helpers.log("tenant default route showing proper nat next-hop")
                    return True
            else:
                    helpers.log("tenant default route is not showing nat profile")
                    return False
       
    def rest_verify_nat_endpoint(self, tenant, nat_profile, remote_tenant, remote_segment):
        '''Function to verify nat endpoint
        Input: tenant name, nat profile, external tenant name, external segment name
        '''
        t = test.Test()
        c = t.controller('master')
        url = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]?select=logical-router&config=true' % tenant
        c.rest.get(url)
        data = c.rest.content()
        for i in range(0, len(data[0]["logical-router"]["nat-profile"])):
            if data[0]["logical-router"]["nat-profile"][i]["name"] == nat_profile:
                public_ip = data[0]["logical-router"]["nat-profile"][i]["pat"]["ip-address"]
            else:
                continue
        url1 = '/api/v1/data/controller/applications/bcf/info/endpoint-manager/endpoint[ip="%s"]' % public_ip
        c.rest.get(url1)
        data1 = c.rest.content()
        helpers.log("content %s" % data1)
        if data1[0]["ip-address"][0]["ip-address"] == public_ip and data1[0]["ip-address"][0]["ip-state"] == "static" and data1[0]["state"] == "Active":
            helpers.log("nat container endpoint is present")
            return True
        else:
            helpers.test_failure("nat container endpoint is not present")
            return False
            
    def rest_return_nat_attachment_switch(self, tenant, nat_profile):
        '''Function to verify nat ivs switch attachment point for fixed nat switch
        Input: tenant name, nat profile name
        '''
        t = test.Test()
        c = t.controller('master')
        url = '/api/v1/data/controller/applications/bcf/info/logical-router-manager/logical-router[name="%s"]/nat-profile' % tenant
        c.rest.get(url)
        data = c.rest.content()
        for i in range(0, len(data)):
            if data[i]["name"] == nat_profile and data[i]["state"] == "active":
                attachment_point = data[i]["attachment-point"]
                ivs_switch = attachment_point.split('|')
                return ivs_switch[0]
            else:
                continue   
            
    def rest_vswitch_portgroup(self, nat_switch):
        '''Function to extract the port group and its members which VM instance belongs
        Input: openstack network name and Instance name
        Output: list of port group members in dictionary format
        '''
        t = test.Test()
        c = t.controller('master')
        portgroup_members = {}
        url1 = '/api/v1/data/controller/applications/bcf/info/fabric/port-group[name="%s"]' % (nat_switch)
        c.rest.get(url1)
        data1 = c.rest.content()
        helpers.log("length=%d" % len(data1[0]["interface"]))
        for i in range(0, len(data1[0]["interface"])):
            k, v = data1[0]["interface"][i]["switch-name"], data1[0]["interface"][i]["interface-name"]
            portgroup_members[k] = v 
        return portgroup_members
    
    def rest_disable_nat_switch_interfaces(self, nat_switch):
        '''Function to disable leaf interfaces for the nat ivs switch connected
        Input: vswitch name
        '''
        t = test.Test()
        c = t.controller('master')
        url = '/api/v1/data/controller/applications/bcf/info/fabric/port-group[name="%s"]' % nat_switch
        c.rest.get(url)
        data = c.rest.content()
        for i in range(0, len(data[0]["interface"])):
            switch = data[0]["interface"][i]["switch-name"]
            interface = data[0]["interface"][i]["interface-name"]
            url0 = '/api/v1/data/controller/core/switch-config[name="%s"]/interface[name="%s"]' % (switch, interface)
            c.rest.put(url0, {"name": str(interface)})
            url = '/api/v1/data/controller/core/switch-config[name="%s"]/interface[name="%s"]' % (switch, interface)
            c.rest.patch(url, {"shutdown": True})
            helpers.sleep(5)
           
    def rest_enable_nat_switch_interfaces(self, nat_switch):
        '''Function to disable leaf interfaces for the nat ivs switch connected
        Input: vswitch name
        '''
        t = test.Test()
        c = t.controller('master')
        url = '/api/v1/data/controller/applications/bcf/info/fabric/port-group[name="%s"]' % nat_switch
        c.rest.get(url)
        data = c.rest.content()
        for i in range(0, len(data[0]["interface"])):
            switch = data[0]["interface"][i]["switch-name"]
            interface = data[0]["interface"][i]["interface-name"]   
            url = '/api/v1/data/controller/core/switch-config[name="%s"]/interface[name="%s"]' % (switch, interface)
            c.rest.delete(url, {"shutdown": None})
            helpers.sleep(3)
            
    def rest_add_floating_ip(self, tenant, nat_profile, public_ip):
        '''Function to configure floating IP
        Input: tenant name, nat profile name, public IP which needs to be part of floating IP 
        '''
        t = test.Test()
        c = t.controller('master')
        url = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]/logical-router/nat-profile[name="%s"]/floating-ip[ip-address="%s"]' % (tenant, nat_profile, public_ip) 
        try:
            c.rest.put(url, {"ip-address": public_ip})
        except:
            return False
        else:
            return True
        
    def rest_add_private_ip(self, tenant, nat_profile, public_ip, private_ip):
        '''Function to configure Private IP association to Public floating IP
        Input: tenant name, nat profile name , public ip confgured for floating IP , private IP of the VM which needs to be added for floating IP
        '''
        t = test.Test()
        c = t.controller('master')
        url = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]/logical-router/nat-profile[name="%s"]/floating-ip[ip-address="%s"]' % (tenant, nat_profile, public_ip)
        try:
            c.rest.patch(url, {"private-ip-address": private_ip})
        except:
            return False
        else:
            return True
        
    def rest_add_public_mac(self, tenant, nat_profile, public_ip, public_mac):
        '''Function to configure Private IP association to Public floating IP
        Input: tenant name , nat profile name , public IP configured for floating IP , public MAC (you can give any unicast mac)
        '''
        t = test.Test()
        c = t.controller('master')
        url = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]/logical-router/nat-profile[name="%s"]/floating-ip[ip-address="%s"]' % (tenant, nat_profile, public_ip)
        try:
            c.rest.patch(url, {"public-mac": public_mac})
        except:
            return False
        else:
            return True  
        
    def rest_verify_floating_ip(self, tenant, nat_profile, public_ip, private_ip):
        '''Function to verify nat-profile status for tenant logical router
        Input: tenant name , nat profile name , public ip cofigured under floating IP section , private IP of the VM
        '''
        t = test.Test()
        c = t.controller('master')
        url = '/api/v1/data/controller/applications/bcf/info/logical-router-manager/logical-router[name="%s"]/floating-ip' % tenant
        c.rest.get(url)
        data = c.rest.content()
        for i in range(0, len(data)):
            if data[i]["logical-router"] == tenant and data[i]["nat-profile"] == nat_profile:
                if data[i]["floating-ip"] == public_ip and data[i]["private-ip"] == private_ip and data[i]["state"] == "active":
                        helpers.log("given floating ip is applied to tenant logical router and status is active")
                        return True
                else:
                        helpers.log("given floating ip is not active")
                        return False
            else:
                continue
            
    def rest_delete_floating_ip(self, tenant, nat_profile, public_ip):
        '''Function to delete floating IP from nat-profile
        Input: tenant name , nat profile name , public IP configured in floating IP section
        '''
        t = test.Test()
        c = t.controller('master')
        url = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]/logical-router/nat-profile[name="%s"]/floating-ip[ip-address="%s"]' % (tenant, nat_profile, public_ip)
        try:
            c.rest.delete(url, {})
        except:
            return False
        else:
            return True
        
    def rest_verify_vswitch_l3_cidr_nat(self, tenant, ivs_switch, route):
        '''
        Function to verify route pointing to nat next-hop
        Input : tenant name , vswitch name , route to match
        '''
        t = test.Test()
        c = t.controller('master')
        url = '/api/v1/data/controller/applications/bcf/info/forwarding/network/switch[switch-name="%s"]/l3-cidr-route-table' % ivs_switch
        c.rest.get(url)
        data = c.rest.content()
        vrf_id = self.rest_get_vrf_id(tenant)
        for i in range(0, len(data)):
            if data[i]["vrf"] == vrf_id and data[i]["ip"] == route and data[i]["new-vlan-id"] == 4090:
                    helpers.log("cidr route next-hop point to nat container")
                    return True
            else:
                continue
        helpers.log("given route does not point to nat net-hop")
        return False
    
    def rest_get_vrf_id(self, tenant):
        '''Function to get VRF ID for a tenant
        Input: tenant name
        '''
        t = test.Test()
        c = t.controller('master')
        url = '/api/v1/data/controller/applications/bcf/info/forwarding/network/internal/tenant-to-vrf-mapping'
        c.rest.get(url)
        data = c.rest.content()
        for i in range(0, len(data)):
            if data[i]["name"] == tenant:
                vrf_id = data[i]["id"]
                return vrf_id
            else:
                continue     
    
    def rest_create_nat_scale(self, tenant, subnet, remote_tenant, remote_segment, count, name="n"):
        '''Function to add nat profile in a tenant in a loop
        Input: tenant name, subnet for the external network (e.g , 40.0.0) , external tenant , externl segment , count , always starts with name = n 
        '''
        t = test.Test()
        c = t.controller('master')
        i = 2
        count = int(count)
        count = count + 1
        while (i <= count):
            nat_profile = name
            nat_profile += str(i)
            public_ip = subnet + "." + "%s" % i
            self.rest_add_nat_profile(tenant, nat_profile)
            self.rest_add_nat_remote_tenant(tenant, nat_profile, remote_tenant, remote_segment)
            helpers.sleep(5)
            self.rest_add_pat(tenant, nat_profile)
            self.rest_add_pat_public_ip(tenant, nat_profile, public_ip)
            i = i + 1
            
    def rest_delete_nat_scale(self, tenant, count, name="n"):
        '''function to delete nat-profile in a loop
        Input: tenant name , how many nat profiles needs to be delete , nat-profile name starts with "n" and while loop integers
        '''
        t = test.Test()
        c = t.controller('master')
        i = 2
        count = int(count)
        count = count + 1
        while (i <= count):
            nat_profile = name
            nat_profile += str(i)
            self.rest_delete_nat_profile(tenant, nat_profile)
            i = i + 1
            
    def rest_verify_nat_endpoint_scale(self, tenant, remote_tenant, remote_segment, count, name="n"):
        ''' Function to verify nat endpoint created for each nat profile in a loop
        Input: tenant , count for loop , name starts with "n"
        '''
        t = test.Test()
        c = t.controller('master')
        i = 2
        count = int(count)
        count = count + 1
        status = True
        while (i <= count):
            nat_profile = name
            nat_profile += str(i)
            if self.rest_verify_nat_endpoint(tenant, nat_profile, remote_tenant, remote_segment) == False:
                status = False
            i = i + 1
        return status
            
        
        