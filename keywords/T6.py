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
        '''
        t = test.Test()
        c = t.controller('master')
        url = '/api/v1/data/controller/applications/bcf/tenant[name="%s]/logical-router/nat-profile[name="%s"]' % (tenant, nat_profile)
        try:
            c.rest.delete(url, {})
        except:
            return False
        else:
            return True
        
    def rest_enable_pat(self, tenant, nat_profile):
        ''' Function to enable pat for a nat-profile
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
    
    def rest_enable_pat_public_ip(self, tenant, nat_profile, public_ip):
        ''' Function to enable pat for a nat-profile
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
    
    def rest_verify_nat_attachment_point(self, tenant, nat_profile, nat_switch):
        '''Function to verify nat ivs switch attachment point for fixed nat switch
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
                    helpers.log("Given nat-profile is not active")
                    return False
                
    def rest_verify_tenant_route_nat(self, tenant, nat_profile):
        '''Function to verify routes in tenant showing nat next-hop
        '''
        t = test.Test()
        c = t.controller('master')
        url = '/api/v1/data/controller/applications/bcf/info/logical-router-manager/logical-router[name="%s"]/route' % tenant
        c.rest.get(url)
        data = c.rest.content()
        
    def rest_verify_nat_endpoint(self, tenant, nat_profile, remote_tenant, remote_segment):
        '''Function to verify nat endpoint
        '''
        t = test.Test()
        c = t.controller('master')
        url = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]?select=logical-router&config=true' % tenant
        c.rest.get(url)
        data = c.rest.content()
        helpers.log("print content %s" % data[0]["logical-router"]["nat-profile"])
        for i in range(0, len(data[0]["logical-router"]["nat-profile"])):
            if data[0]["logical-router"]["nat-profile"][i]["name"] == nat_profile:
                public_ip = data[0]["logical-router"]["nat-profile"][i]["pat"]["ip-address"]
                return public_ip
            else:
                continue
        url1 = '/api/v1/data/controller/applications/bcf/info/endpoint-manager/endpoint[ip="%s"]' % public_ip
        c.rest.get(url1)
        data1 = c.rest.content()
        if data1["ip-address"]["ip-address"] == public_ip and data1["ip-address"]["ip-state"] == "static" and data1["state"] == "Active":
            helpers.log("nat container endpoint is present")
            return True
        else:
            helpers.test_failure("nat container endpoint is not present")
            return False
            
        
            
        
        

