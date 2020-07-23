'''
###  WARNING !!!!!!!
###
###  This is where common code for all T5 will go in.
###
###  To commit new code, please contact the Library Owner:
###  Prashanth Padubidry (prashanth.padubidry@bigswitch.com)
###
###  DO NOT COMMIT CODE WITHOUT APPROVAL FROM LIBRARY OWNER
###
###  Last Updated: 03/06/2014
###
###  WARNING !!!!!!!
'''

import autobot.helpers as helpers
import autobot.restclient as restclient
import autobot.test as test
import re
from netaddr import *


class T5(object):

    def __init__(self):
#        t = test.Test()
#        c = t.controller('main')
        pass
#        url = '/api/v1/auth/login' %
#        result = c.rest.post(url, {"user":"admin", "password":"adminadmin"})
#        session_cookie = result['content']['session_cookie']
#        c.rest.set_session_cookie(session_cookie)

    def rest_show_version(self, string, user="admin", password="adminadmin"):
        '''
            Objective:
            - Return pertinent version value
            - Executes REST API Call on URL http://127.0.0.1:8080/api/v1/data/controller/core/version/component
        
            Inputs:
            |string | Pertinent version string that is being requested|
            |username| username |
            |password| Password|     
            Return Value:
            | True | On Configuration success|
            | False | On Configuration failure|
            
        '''
        t = test.Test()
        c = t.controller('main')
        try:
            url = '/api/v1/data/controller/core/version/component'
            c.rest.get(url)
            data = c.rest.content()
            output_value = data[0][string]
        except:
                return False
        else:
                return output_value

    def rest_add_user_password(self, username, password):
        '''
            Objective:
            - Set password for given user
            
            Inputs:
            |username| username for which password is being configured|
            |password| Password to be configured|            
            
            Return Value:
            | True | On Configuration success|
            | False | On Configuration failure|
            
        '''
        try:
            t = test.Test()
        except:
            return False
        else:
            c = t.controller('main')
            try:
                # Get the hashed value of password
                helpers.log("Password is %s" % json.dumps(password))
                url1 = '/api/v1/data/controller/core/aaa/hash-password[password=%s]' % json.dumps(password)
                c.rest.get(url1)
                myHash = c.rest.content()
                myHashPass = myHash[0]['hashed-password']
                # Assign password to user
                url2 = '/api/v1/data/controller/core/aaa/local-user[user-name="%s"]' % str(username)
                c.rest.patch(url2, {"password": str(myHashPass)})
            except:
                helpers.test_log(c.rest.error())
                return False
            else:
                return True

    def rest_add_tenant(self, tenant):

        t = test.Test()
        c = t.controller('main')
        url = '/api/v1/data/controller/applications/bvs/tenant[name="%s"]' % (tenant)
        try:
                c.rest.put(url, {"name": tenant})
        except:
                return False
        else:
                return True

    def _rest_show_tenant(self, tenant=None, negative=False):
        t = test.Test()
        c = t.controller('main')

        if tenant:
            # Show a specific tenant
            url = '/api/v1/data/controller/applications/bvs/tenant[name="%s"]' % (tenant)
        else:
            # Show all tenants
            url = '/api/v1/data/controller/applications/bvs/tenant' % ()

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
        helpers.log("Input arguments: tenant = %s" % tenant)
        return self._rest_show_tenant(tenant)

    def rest_show_tenant_gone(self, tenant=None):
        helpers.log("Input arguments: tenant = %s" % tenant)
        return self._rest_show_tenant(tenant, negative=True)

    def rest_delete_tenant(self, tenant=None):
        t = test.Test()
        c = t.controller('main')

        helpers.log("Input arguments: tenant = %s" % tenant)

        url = '/api/v1/data/controller/applications/bvs/tenant[name="%s"]' % (tenant)
        try:
            c.rest.delete(url, {"name": tenant})
        except:
            return False
        else:
            return True

    def test_args(self, arg1, arg2, arg3):
        try:
            helpers.log("Input arguments: arg1 = %s" % arg1)
            helpers.log("Input arguments: arg2 = %s" % arg2)
            helpers.log("Input arguments: arg3 = %s" % arg3)
        except:
            return False
        else:
            return True

    def rest_add_vns(self, tenant, vns):
        t = test.Test()
        c = t.controller('main')

        helpers.test_log("Input arguments: tenant = %s vns = %s" % (tenant, vns))

        url = '/api/v1/data/controller/applications/bvs/tenant[name="%s"]/vns[name="%s"]' % (tenant, vns)
        try:
            c.rest.put(url, {"name": vns})
        except:
            return False
        else:
            return True

    def rest_add_vns_scale(self, tenant, count):
        t = test.Test()
        c = t.controller('main')
        count = int(count)
        i = 1
        while (i <= count):
            vns = "v"
            vns += str(i)
            url = '/api/v1/data/controller/applications/bvs/tenant[name="%s"]/vns[name="%s"]' % (tenant, vns)
            try:
                c.rest.put(url, {"name": vns})
            except:
                return False
            i = i + 1

    def rest_add_interface_to_all_vns(self, tenant, switch, intf):
        t = test.Test()
        c = t.controller('main')
        url = '/api/v1/data/controller/applications/bvs/info/endpoint-manager/vnses[tenant-name="%s"]' % (tenant)
        c.rest.get(url)
        data = c.rest.content()
        list_vlan_id = []
        for i in range(0, len(data)):
            if data[i]["internal-vlan"] not in list_vlan_id:
                list_vlan_id.append(data[i]["internal-vlan"])
        list_vlan_id = sorted(list_vlan_id)
        for j in range(0, len(data)):
            if data[j]["internal-vlan"] in list_vlan_id:
                url = '/api/v1/data/controller/applications/bvs/tenant[name="%s"]/vns[name="%s"]/switch-port-membership-rules[switch-name="%s"][interface-name="%s"]' % (tenant, data[j]["name"], switch, intf)
                c.rest.put(url, {"switch-name": switch, "interface-name": intf, "vlan": data[j]["internal-vlan"]})

    def rest_delete_vns(self, tenant, vns=None):
        t = test.Test()
        c = t.controller('main')

        helpers.test_log("Input arguments: tenant = %s vns = %s" % (tenant, vns))

        url = '/api/v1/data/controller/applications/bvs/tenant[name="%s"]/vns[name="%s"]' % (tenant, vns)
        try:
            c.rest.delete(url, {"name": vns})
        except:
            return False
        else:
            return True

    def rest_show_vns(self):
        t = test.Test()
        c = t.controller('main')

        url = '/api/v1/data/controller/applications/bvs/info/endpoint-manager/vnses' % ()
        try:
            c.rest.get(url)
        except:
            return False
        else:
            return True

    def rest_add_portgroup(self, pg):
        t = test.Test()
        c = t.controller('main')

        helpers.test_log("Input arguments: port-group = %s" % pg)

        url = '/api/v1/data/controller/fabric/port-group[name="%s"]' % (pg)
        try:
            c.rest.put(url, {"name": pg})
        except:
            return False
        else:
            return True

    def rest_delete_portgroup(self, pg=None):
        t = test.Test()
        c = t.controller('main')

        helpers.test_log("Input arguments: port-group = %s" % pg)

        url = '/api/v1/data/controller/fabric/port-group[name="%s"]' % (pg)
        try:
            c.rest.delete(url, {"name": pg})
        except:
            return False
        else:
            return True

    def rest_add_endpoint(self, tenant, vns, endpoint):
        '''Add nexthop to ecmp groups aks gateway pool in tenant"
        
            Input:
                `tenant`          tenant name
                `vns`         vns name
                `endpoint`    endpoint name
            Return: true if configuration is successful, false otherwise
            http://127.0.0.1:8080/api/v1/data/controller/applications/bvs/tenant[name="A"]/vns[name="A1"]/endpoints[name="H1"] {"name": "H1"}

        '''

        t = test.Test()
        c = t.controller('main')

        helpers.test_log("Input arguments: tenant = %s, vns = %s, endpoint = %s" % (tenant, vns, endpoint))

        url = '/api/v1/data/controller/applications/bvs/tenant[name="%s"]/vns[name="%s"]/endpoints' % (tenant, vns)
        try:
            c.rest.post(url, {"name": endpoint})
        except:
            return False
        else:
            return True

    def rest_delete_endpoint(self, tenant, vns, endpoint=None):
        t = test.Test()
        c = t.controller('main')

        helpers.test_log("Input arguments: tenant = %s vns = %s endpoint = %s" % (tenant, vns, endpoint))

        url = '/api/v1/data/controller/applications/bvs/tenant[name="%s"]/vns[name="%s"]/endpoints[name="%s"]' % (tenant, vns, endpoint)
        try:
            c.rest.delete(url, {"name": endpoint})
        except:
            return False
        else:
            return True

    def rest_add_interface_to_portgroup(self, switch, intf, pg):
        t = test.Test()
        c = t.controller('main')

        helpers.test_log("Input arguments: switch-name = %s Interface-name = %s port-group = %s" % (switch, intf, pg))

        url = '/api/v1/data/controller/core/switch-config[name="%s"]/interface[name="%s"]' % (switch, intf)
        try:
            c.rest.put(url, {"name": intf, "port-group-name": pg})
        except:
            return False
        else:
            return True

    def rest_add_portgroup_lacp(self, pg):
        t = test.Test()
        c = t.controller('main')

        helpers.test_log("Input arguments: port-group = %s" % (pg))

        url = '/api/v1/data/controller/fabric/port-group[name="%s"]' % (pg)
        try:
            c.rest.patch(url, {"mode": "lacp"})
        except:
            return False
        else:
            return True

    def rest_delete_portgroup_lacp(self, pg):
        t = test.Test()
        c = t.controller('main')

        helpers.test_log("Input arguments: port-group = %s" % (pg))

        url = '/api/v1/data/controller/fabric/port-group[name="%s"]' % (pg)
        try:
            c.rest.delete(url, {"mode": None})
        except:
            return False
        else:
            return True

    def rest_delete_interface_from_portgroup(self, switch, intf, pg):
        t = test.Test()
        c = t.controller('main')

        helpers.test_log("Input arguments: switch-name = %s Interface-name = %s port-group = %s" % (switch, intf, pg))

        url = '/api/v1/data/controller/core/switch-config[name="%s"]/interface[name="%s"]' % (switch, intf)
        try:
            c.rest.delete(url, {"core/switch-config/interface/port-group-name": pg})
        except:
            return False
        else:
            return True

    def rest_add_portgroup_to_vns(self, tenant, vns, pg, vlan):
        t = test.Test()
        c = t.controller('main')

        helpers.test_log("Input arguments: tenant = %s vns = %s port-group = %s vlan = %s" % (tenant, vns, pg, vlan))

        url = '/api/v1/data/controller/applications/bvs/tenant[name="%s"]/vns[name="%s"]/port-group-membership-rules[port-group-name="%s"]' % (tenant, vns, pg)
        try:
            c.rest.put(url, {"vlan": vlan, "port-group-name": pg})
        except:
            return False
        else:
            return True

    def rest_add_portgroup_to_endpoint(self, tenant, vns, endpoint, pg, vlan):
        t = test.Test()
        c = t.controller('main')

        helpers.test_log("Input arguments: tenant = %s vns = %s endpoint = %s port-group = %s vlan = %s" % (tenant, vns, endpoint, pg, vlan))

        url = '/api/v1/data/controller/applications/bvs/tenant[name="%s"]/vns[name="%s"]/endpoints[name="%s"]/attachment-point' % (tenant, vns, endpoint)
        try:
            c.rest.put(url, {"port-group-name": pg, "vlan": vlan})
        except:
            return False
        else:
            return True

    def rest_delete_portgroup_from_vns(self, tenant, vns, pg, vlan):
        t = test.Test()
        c = t.controller('main')

        helpers.test_log("Input arguments: tenant = %s vns = %s port-group = %s vlan = %s" % (tenant, vns, pg, vlan))

        url = '/api/v1/data/controller/applications/bvs/tenant[name="%s"]/vns[name="%s"]/port-group-membership-rules[port-group-name="%s"]' % (tenant, vns, pg)
        try:
            c.rest.delete(url, {"vlan": vlan})
        except:
            return False
        else:
            return True

    def rest_add_interface_to_vns(self, tenant, vns, switch, intf, vlan):
        t = test.Test()
        c = t.controller('main')

        helpers.test_log("Input arguments: tenant = %s vns = %s switch-name = %s interface-name = %s vlan = %s" % (tenant, vns, switch, intf, vlan))

        url = '/api/v1/data/controller/applications/bvs/tenant[name="%s"]/vns[name="%s"]/switch-port-membership-rules[switch-name="%s"][interface-name="%s"]' % (tenant, vns, switch, intf)
        try:
            c.rest.put(url, {"switch-name": switch, "interface-name": intf, "vlan": vlan})
        except:
            return False
        else:
            return True

    def rest_delete_interface_from_vns(self, tenant, vns, switch, intf, vlan):
        t = test.Test()
        c = t.controller('main')

        helpers.test_log("Input arguments: tenant = %s vns = %s switch-name = %s interface-name = %s vlan = %s" % (tenant, vns, switch, intf, vlan))

        url = '/api/v1/data/controller/applications/bvs/tenant[name="%s"]/vns[name="%s"]/switch-port-membership-rules[switch-name="%s"][interface-name="%s"]' % (tenant, vns, switch, intf)
        try:
            c.rest.delete(url, {"vlan": vlan})
        except:
            return False
        else:
            return True

    def rest_add_interface_to_endpoint(self, tenant, vns, endpoint, switch, intf, vlan):
        t = test.Test()
        c = t.controller('main')

        helpers.test_log("Input arguments: tenant = %s vns = %s endpoint = %s switch-name = %s interface-name = %s vlan = %s" % (tenant, vns, endpoint, switch, intf, vlan))

        url = '/api/v1/data/controller/applications/bvs/tenant[name="%s"]/vns[name="%s"]/endpoints[name="%s"]/attachment-point' % (tenant, vns, endpoint)
        try:
            c.rest.put(url, {"switch-name": switch, "interface-name": intf, "vlan": vlan})
        except:
            return False
        else:
            return True

    def rest_add_ip_endpoint(self, tenant, vns, endpoint, ip):
        t = test.Test()
        c = t.controller('main')
        url = '/api/v1/data/controller/applications/bvs/tenant[name="%s"]/vns[name="%s"]/endpoints[name="%s"]' % (tenant, vns, endpoint)
        try:
            c.rest.patch(url, {"ip-address": ip})
        except:
            return False
        else:
            return True

    def rest_add_mac_endpoint(self, tenant, vns, endpoint, mac):
        t = test.Test()
        c = t.controller('main')
        url = '/api/v1/data/controller/applications/bvs/tenant[name="%s"]/vns[name="%s"]/endpoints[name="%s"]' % (tenant, vns, endpoint)
        try:
            c.rest.patch(url, {"mac": mac})
        except:
            return False
        else:
            return True

    def rest_verify_vns(self):
        '''Verify VNS information
        
            Input:           
            
            Return: true if it matches the added VNS (string starts with "v")
        '''
        t = test.Test()
        c = t.controller('main')
        url = '/api/v1/data/controller/applications/bvs/info/endpoint-manager/vnses' % ()
        c.rest.get(url)
        data = c.rest.content()
        for i in range(0, len(data)):
                if len(data) != 0:
                        if (int(data[i]["internal-vlan"]) != 0):
                            helpers.log("Expected VNS's are present in the config")
                            return True
                        else:
                            helpers.test_failure("Expected VNS's are not present in the config")
                            return False
                else:
                        helpers.log("No VNS are added")
                        return False

    def rest_verify_vns_scale(self, count):
        '''Verify VNS information for scale
        
            Input:  No of vns expected to be created          
            
            Return: true if it matches the added VNS (string starts with "v")
        '''
        t = test.Test()
        c = t.controller('main')
        url = '/api/v1/data/controller/applications/bvs/info/endpoint-manager/vnses' % ()
        c.rest.get(url)
        data = c.rest.content()
        if len(data) == int(count):
            for i in range(0, len(data)):
                if len(data) != 0:
                        if (int(data[i]["internal-vlan"]) != 0):
                            helpers.log("Expected VNS's are present in the config")
                            return True
                        else:
                            helpers.test_failure("Expected VNS's are not present in the config")
                            return False
                else:
                        helpers.log("No VNS are added")
                        return False
        else:
                helpers.test_failure("Fail: expected:%s, Actual:%s" % (int(count), len(data)))
                return False

    def rest_verify_tenant(self):
        '''Verify CLI tenant information
        
            Input:   None        
            
            Return: true if it matches the added tenant (string starts with "t")
        '''
        t = test.Test()
        c = t.controller('main')
        url = '/api/v1/data/controller/applications/bvs/info/endpoint-manager/tenants' % ()
        c.rest.get(url)
        data = c.rest.content()
        for i in range(0, len(data)):
                if len(data) != 0:
                    if data[i]["tenant-name"] == re.search('^t.*', 'data[i]["tenant-name"]'):
                        helpers.log("Expected Tenants are present in the config")
                        return True
                    else:
                        helpers.test_failure("Expected Tenants are not present in the config")
                        return False
                else:
                        helpers.log("No tenants are added")
                        return False


    def rest_verify_endpoint(self, vns, vlan, mac, switch, intf):
        '''Verify Dynamic Endpoint entry
        
            Input: vns name , vlan ID , mac , switch name, expected switch interface          
            
            Return: true if it matches Value specified
        '''
        t = test.Test()
        c = t.controller('main')
        url = '/api/v1/data/controller/applications/bvs/info/endpoint-manager/endpoints' % ()
        c.rest.get(url)
        data = c.rest.content()
        if len(data) != 0:
                for i in range(0, len(data)):
                    if str(data[i]["vns-name"]) == vns:
                        if str(data[i]["attachment-point"]["vlan"]) == str(vlan):
                            if (data[i]["mac"] == str(mac)) :
                                if (data[i]["attachment-point"]["switch-name"] == switch) :
                                    if (data[i]["attachment-point"]["interface-name"] == str(intf)) :
                                        helpers.log("Expected Endpoints are added data matches is %s" % data[i]["mac"])
                                        return True
                                    else:
                                        helpers.test_failure("Expected endpoints %s are not added" % (str(mac)))
                                        return False
        else:
            return False

    def rest_verify_endpoint_static(self, vns, vlan, mac, switch, intf):
        '''Verify Static Endpoint entry
        
            Input: vns name , vlan ID , mac , switch name, expected switch interface          
            
            Return: true if it matches Value specified and added attachment point is true
         '''
        t = test.Test()
        c = t.controller('main')
        url = '/api/v1/data/controller/applications/bvs/info/endpoint-manager/endpoints' % ()
        c.rest.get(url)
        data = c.rest.content()
        if len(data) != 0:
            for i in range(0, len(data)):
                if str(data[i]["vns-name"]) == vns:
                    if str(data[i]["attachment-point"]["vlan"]) == str(vlan):
                        if (data[i]["mac"] == str(mac)) :
                            if (data[i]["attachment-point"]["switch-name"] == switch) :
                                if (data[i]["attachment-point"]["interface-name"] == str(intf)) :
                                    if (data[i]["configured-endpoint"] == True) :
                                        helpers.log("Expected Endpoints are added data matches is %s" % data[i]["mac"])
                                        return True
                                    else:
                                        helpers.test_failure("Expected endpoints %s are not added" % (str(mac)))
                                        return False
        else:
                helpers.test_failure("Expected vns are not added %s" % vns)
                return False


    def rest_verify_endpoint_portgroup(self, vns, vlan, mac, pg):
        '''Verify Dynamic Endpoint entry
        
            Input: vns name , vlan ID , mac , portgroup name          
            
            Return: true if it matches Value specified
        '''
        t = test.Test()
        c = t.controller('main')
        url = '/api/v1/data/controller/applications/bvs/info/endpoint-manager/endpoints' % ()
        c.rest.get(url)
        data = c.rest.content()
        if len(data) != 0:
            for i in range(0, len(data)):
                if str(data[i]["vns-name"]) == vns:
                    if str(data[i]["attachment-point"]["vlan"]) == str(vlan):
                        if (data[i]["mac"] == str(mac)) :
                            if (data[i]["attachment-point"]["port-group-name"] == pg) :
                                helpers.log("Expected Endpoints are added data matches is %s" % data[i]["mac"])
                                return True
                            else:
                                helpers.test_failure("Expected endpoints %s are not added" % (str(mac)))
                                return False
        else:
            helpers.test_failure("Expected vns are not added %s" % vns)
            return False

    def rest_verify_endpoint_static_portgroup(self, vns, vlan, mac, pg):
        '''Verify Static Endpoint entry
        
            Input: vns name , vlan ID , mac, portgroup name          
            
            Return: true if it matches Value specified and added attachment point is true
        '''
        t = test.Test()
        c = t.controller('main')
        url = '/api/v1/data/controller/applications/bvs/info/endpoint-manager/endpoints' % ()
        c.rest.get(url)
        data = c.rest.content()
        if len(data) != 0:
                for i in range(0, len(data)):
                    if str(data[i]["vns-name"]) == vns:
                        if str(data[i]["attachment-point"]["vlan"]) == str(vlan):
                            if (data[i]["mac"] == str(mac)) :
                                if (data[i]["attachment-point"]["port-group-name"] == pg) :
                                    if (data[i]["configured-endpoint"] == True) :
                                        helpers.log("Expected Endpoints are added data matches is %s" % data[i]["mac"])
                                        return True
                                    else:
                                        helpers.test_failure("Expected endpoints %s are not added" % (str(mac)))
                                        return False
        else:
                helpers.test_failure("Expected vns are not added %s" % vns)
                return False

    def rest_verify_vns_interface(self, vns, intf_num):
        '''Verify VNS Membership Interface information
        
            Input:  specific VNS Name  and number of interfaces to be present in the VNS       
            
            Return: Num of ports part of the specific VNS
        '''
        t = test.Test()
        c = t.controller('main')
        url = '/api/v1/data/controller/applications/bvs/info/endpoint-manager/vnses[name="%s"]' % (vns)
        c.rest.get(url)
        data = c.rest.content()
        if data[0]["name"] == vns:
                if (int(data[0]["num-ports"]) == int(intf_num)) :
                    helpers.log("Expected Member port counts in VNS are correct %d = %d" % (int(intf_num), int(data[0]["num-ports"])))
                    return True
                else:
                    helpers.test_failure("Membership count in VNS are not correct %d = %d" % (int(intf_num), int(data[0]["num-ports"])))
                    return False
        else:
                helpers.log("Expected VNS are added")
                return False


    def rest_verify_forwarding_vlan_table(self, switch):
        '''Verify VNS(VLAN) Information in Controller Forwarding Table
        
            Input:  Specific switch name  
            
            Return: vlan table from the forwarding table with membership ports.
        '''
        t = test.Test()
        c = t.controller('main')
        url = '/api/v1/data/controller/applications/bvs/info/forwarding/network/switch[switch-name="%s"]/vlan-table' % (switch)
        c.rest.get(url)
        data = c.rest.content()
        no_of_vlans = len(data)
        url1 = '/api/v1/data/controller/applications/bvs/info/endpoint-manager/vnses' % ()
        c.rest.get(url1)
        data1 = c.rest.content()
        no_of_vns = len(data1)
        if (int(no_of_vns) == int(no_of_vlans)):
                helpers.log("Vlan Entries are present in forwarding table Actual:%d = Expected:%d" % (int(no_of_vns), int(no_of_vlans)))
                return True
        else:
                helpers.test_failure("Vlan Entries are inconsistent in forwarding table %d = %d" % (int(no_of_vns), int(no_of_vlans)))
                return False

    def rest_verify_forwarding_port(self, switch):
        '''Verify Edge port  Information in Controller Forwarding Table
        
            Input:  Specific DPID of the switch      
            
            Return: port table with associated Lag id will be provided
        '''
        t = test.Test()
        c = t.controller('main')
        url = '/api/v1/data/controller/applications/bvs/info/forwarding/network/switch[switch-name="%s"]/port-table' % (switch)
        c.rest.get(url)
        data = c.rest.content()
        for i in range(0, len(data)):
            if ((data[i]["lag-id"]) == 0):
                helpers.test_failure("Lag-Id for the edge interface (switch=%s,interface=%s) is showing 0" % (switch, data[i]["port-num"]))
                return False
            helpers.log("Proper Lag-Id added for All edge Interfaces")
            return True

    def rest_verify_forwarding_vlan_xlate(self, switch, vlan, intf):
        '''Verify VNS(VLAN) Information in Controller Forwarding Table
        
            Input:  Specific switch name and specific vlanID     
            
            Return: vlan xlate matching in forwarding table.
        '''
        t = test.Test()
        c = t.controller('main')
        url = '/api/v1/data/controller/applications/bvs/info/forwarding/network/switch[switch-name="%s"]/port-table' % (switch)
        c.rest.get(url)
        data = c.rest.content()
        interface = re.sub("\D", "", intf)
        lag_id = []
        for i in range(0, len(data)):
            if data[i]["port-num"] == int(interface):
                lag_id.append(data[i]["lag-id"])
        url1 = '/api/v1/data/controller/applications/bvs/info/forwarding/network/switch[switch-name="%s"]/vlan-xlate-table' % (switch)
        c.rest.get(url1)
        data1 = c.rest.content()
        for i in range(0, len(data1)):
            if data1[i]["port-num"] == lag_id[0]:
                if str(data1[i]["vlan-id"]) == str(vlan):
                    helpers.log("Vlan Translation table is creaetd properly for the given interface")
                    return True
        return False

    def rest_verify_forwarding_vlan_fabric_tag_members(self, switch):
        '''Verify Fabric interfaces status in a vlan
        
            Input:  Specific switch name    
            
            Return: Function will verify those fabric interfaces must be tagged for all vlans.
        '''
        t = test.Test()
        c = t.controller('main')
        url = '/api/v1/data/controller/core/switch[name="%s"]/interface' % (switch)
        c.rest.get(url)
        data = c.rest.content()
        list_fabric_interface = []
        for i in range(0, len(data)):
            if data[i]["type"] == "unknown" or data[i]["type"] == "edge":
                continue
            elif data[i]["type"] == "leaf" or data[i]["type"] == "spine":
                list_fabric_interface.append(int(re.sub("\D", "", (data[i]["name"]))))
        url1 = '/api/v1/data/controller/applications/bvs/info/forwarding/network/switch[switch-name="%s"]/vlan-table' % (switch)
        c.rest.get(url1)
        data1 = c.rest.content()
        list_tag_intf = []
        for i in range(0, len(data1)):
            for j in range(0, len(data1[i]["tagged-port"])):
                if data1[i]["tagged-port"][j]["port-num"] not in list_tag_intf:
                    list_tag_intf.append(data1[i]["tagged-port"][j]["port-num"])
        helpers.log("%s,%s" % (list_fabric_interface, list_tag_intf))
        list_common = list(set(list_fabric_interface).intersection(set(list_tag_intf)))
        if len(list_fabric_interface) == len(list_common):
                    helpers.log("Pass:All fabric interfaces are in vlan as Tagged member")
                    return True
        else:
                    helpers.test_failure("Fail:All fabric interfaces are not in vlan as Tagged member")
                    return False

    def comm_elements(self, list1, list2):
        ''' Find the common elements in the 2 lists 
         Input: Provide 2 lists
         Output : give the list which has common elements in those lists
        '''
        result = []
        for element in list1:
            if element in list2:
                result.append(element)
        return result

    def rest_verify_forwarding_vlan_edge_untag_members(self, switch, intf):
        '''Verify Fabric edge interfaces status in a vlan
        
            Input:  Specific switch name and specific edge interfaces    
            
            Return: True or False depends on the edge interface present as untagged in a vlan
        '''
        t = test.Test()
        c = t.controller('main')
        url = '/api/v1/data/controller/applications/bvs/info/forwarding/network/switch[switch-name="%s"]/vlan-table' % (switch)
        c.rest.get(url)
        data = c.rest.content()
        interface = re.sub("\D", "", intf)
        for i in range(0, len(data)):
            try:
                value = data[i]["untagged-port"]
            except KeyError:
                continue
            for j in range(0, len(data[i]["untagged-port"])):
                    if data[i]["untagged-port"][j]["port-num"] == int(interface):
                        helpers.log("Pass:Given interface is present in untag memberlist of vlan-table")
                        return True
        return False

    def rest_verify_forwarding_vlan_edge_tag_members(self, switch, intf):
        '''Verify Fabric edge interfaces status in a vlan
        
            Input:  Specific switch name and specific edge interfaces    
            
            Return: return True or False depends on the edge port present as Tagged in a vlan
        '''
        t = test.Test()
        c = t.controller('main')
        url = '/api/v1/data/controller/applications/bvs/info/forwarding/network/switch[switch-name="%s"]/vlan-table' % (switch)
        c.rest.get(url)
        data = c.rest.content()
        interface = re.sub("\D", "", intf)
        for i in range(0, len(data)):
            try:
                value = data[i]["tagged-port"]
            except KeyError:
                continue
            for j in range(0, len(data[i]["tagged-port"])):
                if data[i]["tagged-port"][j]["port-num"] == int(interface):
                    helpers.log("Pass:Given interface is present in untag memberlist of vlan-table")
                    return True
        return False

    def rest_verify_forwarding_layer2_table_untag(self, switch, intf, mac):
        '''Verify Layer 2 MAC information in forwarding table
        
            Input:  Specific switch name , interface , mac     
            
            Return: True or false based on the entry present in the forwarding table.
        '''
        t = test.Test()
        c = t.controller('main')
        # Get the Lag id for the Given interface
        url = '/api/v1/data/controller/applications/bvs/info/forwarding/network/switch[switch-name="%s"]/port-table' % (switch)
        c.rest.get(url)
        data = c.rest.content()
        interface = re.sub("\D", "", intf)
        lag_id = []
        for i in range(0, len(data)):
            if data[i]["port-num"] == int(interface):
                lag_id.append(data[i]["lag-id"])
                # Get the vlan-id for the given interface
        url1 = '/api/v1/data/controller/applications/bvs/info/forwarding/network/switch[switch-name="%s"]/vlan-table' % (switch)
        c.rest.get(url1)
        data1 = c.rest.content()
        vlan_id = []
        for i in range(0, len(data1)):
            try:
                for j in range(0, len(data1[i]["untagged-port"])):
                    if ((data1[i]["untagged-port"][j]["port-num"]) == int(interface)):
                        vlan_id.append(data1[i]["vlan-id"])
            except (KeyError):
                continue
                    # Match the mac in forwarding table with specific lag_id and vlan_id
        url3 = '/api/v1/data/controller/applications/bvs/info/forwarding/network/switch[switch-name="%s"]/l2-table' % (switch)
        c.rest.get(url3)
        data2 = c.rest.content()
        for i in range(0, len(data2)):
            if str(data2[i]["mac"]) == str(mac):
                if data2[i]["port-num"] in lag_id and data2[i]["vlan-id"] in vlan_id:
                    helpers.log("Pass: Expected mac is present in the forwarding table with correct vlan and interface")
                    return True

        return False

    def rest_verify_forwarding_layer2_table_tag(self, switch, intf, mac):
        '''Verify Layer 2 MAC information in forwarding table
        
            Input:  Specific switch name , interface , mac     
            
            Return: True or false based on the entry present in the forwarding table.
        '''
        t = test.Test()
        c = t.controller('main')
        # Get the Lag id for the Given interface
        url = '/api/v1/data/controller/applications/bvs/info/forwarding/network/switch[switch-name="%s"]/port-table' % (switch)
        c.rest.get(url)
        data = c.rest.content()
        interface = re.sub("\D", "", intf)
        lag_id = []
        for i in range(0, len(data)):
            if data[i]["port-num"] == int(interface):
                lag_id.append(data[i]["lag-id"])
                # Get the vlan-id for the given interface
        url1 = '/api/v1/data/controller/applications/bvs/info/forwarding/network/switch[switch-name="%s"]/vlan-table' % (switch)
        c.rest.get(url1)
        data1 = c.rest.content()
        vlan_id = []
        for i in range(0, len(data1)):
            try:
                value = data1[i]["tagged-port"]
            except KeyError:
                continue
            for j in range(0, len(data1[i]["tagged-port"])):
                if (data1[i]["tagged-port"][j]["port-num"] == int(interface)):
                    vlan_id.append(data1[i]["vlan-id"])
                    # Match the mac in forwarding table with specific lag_id and vlan_id
        helpers.log("%s" % vlan_id)
        url3 = '/api/v1/data/controller/applications/bvs/info/forwarding/network/switch[switch-name="%s"]/l2-table' % (switch)
        c.rest.get(url3)
        data2 = c.rest.content()
        for i in range(0, len(data2)):
            if str(data2[i]["mac"]) == str(mac):
                if data2[i]["port-num"] == lag_id[0] and data2[i]["vlan-id"] == vlan_id[0]:
                    helpers.log("Pass: Expected mac is present in the forwarding table with correct vlan and interface")
                    return True

        return False

    def rest_add_endpoint_scale(self, tenant, vns, mac, endpoint, switch, intf, vlan, count):
        ''' Adding static endpoints in a scale 
            Input: tenant , vns , switch , interface , vlan , count (how many static endpoints), starting letter for the endpoint name
            Output: Static creation of endpoints in a given tenant and vns with switch/interface
        '''
        t = test.Test()
        c = t.controller('main')
        i = 1
        while (i <= int(count)):
            endpoint += str(i)
            mac = EUI(mac).value
            mac = "{0}".format(str(EUI(mac + i)).replace('-', ':'))
            url = '/api/v1/data/controller/applications/bvs/tenant[name="%s"]/vns[name="%s"]/endpoints' % (tenant, vns)
            c.rest.post(url, {"name": endpoint})
            url1 = '/api/v1/data/controller/applications/bvs/tenant[name="%s"]/vns[name="%s"]/endpoints[name="%s"]/attachment-point' % (tenant, vns, endpoint)
            c.rest.put(url1, {"switch-name": switch, "interface-name": intf, "vlan": vlan})
            url2 = '/api/v1/data/controller/applications/bvs/tenant[name="%s"]/vns[name="%s"]/endpoints[name="%s"]' % (tenant, vns, endpoint)
            c.rest.patch(url2, {"mac": mac})
            i = i + 1

    def rest_verify_endpoints_in_vns(self, vns, count):
        ''' Function to count no of endoint in the given VNS 
         Input : Expected Count and vns 
         Output: No of endoints match aginst the specifed count in vns table
        '''
        t = test.Test()
        c = t.controller('main')
        url = '/api/v1/data/controller/applications/bvs/info/endpoint-manager/vnses[name="%s"]' % (vns)
        c.rest.get(url)
        data = c.rest.content()
        if data[0]["num-active-endpoints"] == int(count):
            helpers.log("Pass:Expected:%s, Actual:%s" % (int(count), data[0]["num-active-endpoints"]))
            return True
        else:
            helpers.test_failure("Fail: Expected:%s is not equal to Actual:%s" % (int(count), data[0]["num-active-endpoints"]))
            return False

    def rest_verify_endpoint_in_system(self, count):
        ''' Function to count no of endoint in the system 
         Input : Expected Count
         Output: No of endoints match aginst the specifed count in endpoint table
        '''
        t = test.Test()
        c = t.controller('main')
        url = '/api/v1/data/controller/applications/bvs/info/endpoint-manager/endpoints' % ()
        c.rest.get(url)
        data = c.rest.content()
        if int(len(data)) == int(count):
            helpers.log("Pass:Expected:%s, Actual:%s" % (int(count), len(data)))
            return True
        else:
            helpers.test_failure("Fail: Expected:%s is not equal to Actual:%s" % (int(count), len(data)))
            return False



    def rest_clear_vns_stats(self, vns):
        ''' Function to clear the VNS stats
        Input: vns name
        Output: given vns counters will be cleared
        '''
        t = test.Test()
        c = t.controller('main')
        url = 'api/v1/data/controller/applications/bvs/info/stats/reset-stats/clear-vns-counters'
        try:
            c.rest.get(url)
        except:
            return False
        else:
            return True

    def rest_verify_vns_stats(self, vns, frame_cnt):
        ''' Function to verify the VNS stats
        Input: vns name
        Output: given vns counters will be showed
        '''
        t = test.Test()
        c = t.controller('main')
        frame_cnt = int(frame_cnt)
        url = '/api/v1/data/controller/applications/bvs/info/stats/vns-stats/tenants/vnses[vns-name="%s"]' % (vns)
        try:
            c.rest.get(url)
        except:
            return False
        else:
            return True
        data = c.rest.content()
        if data["counters"]["counters-rx-packets"] == frame_cnt:
            helpers.log("Pass: Counters value Expected:%d, Actual:%d" % (frame_cnt, data["counters"]["counters-rx-packets"]))
            return True
        else:
            return False

    def rest_verify_vns_rates(self, vns, frame_rate, vrange=5):
        ''' Function to verify the VNS incoming rates
        Input: vns name
        Output: given vns rates will be displayed and match against the expected rate
        '''
        t = test.Test()
        c = t.controller('main')
        url = '/api/v1/data/controller/applications/bvs/info/stats/vns-stats/tenants/vnses[vns-name="%s"]' % (vns)
        frame_rate = int(frame_rate)
        vrange = int(vrange)
        try:
            c.rest.get(url)
        except:
            return False
        else:
            return True
        data = c.rest.content()
        if (data["rates"]["rates-rx-packets"] >= (frame_rate - vrange)) and (data["rates"]["rates-rx-packets"] <= (frame_rate + vrange)):
            helpers.log("Pass: Rate value Expected:%d, Actual:%d" % (int(frame_rate), data["rates"]["rates-rx-packets"]))
            return True
        else:
            return False



#===========================================================
#To be updated
#===========================================================

    def rest_configure_virtual_ip(self, vip):
        ''' Function to configure Virtual IP of the cluster via REST
        Input: VIP address
        Output: True if successful, False otherwise
        '''
        t = test.Test()
        c = t.controller('main')

        helpers.log("Input arguments: virtual IP = %s" % vip)
        try:
            url = '/api/v1/data/controller/os/config/global/virtual-ip-config'
            c.rest.post(url, {"ipv4-address": vip})
        except:
            return False
        else:
            return True


    def rest_delete_virtual_ip(self):
        ''' Function to delete Virtual IP from a controller via REST
        Input: None
        Output: True if successful, False otherwise
        '''
        t = test.Test()
        c = t.controller('main')

        helpers.log("Deleting virtual IP address")
        try:
            url = '/api/v1/data/controller/os/config/global/virtual-ip-config'
            c.rest.delete(url)
        except:
            return False
        else:
            return True


#===========================================================
#To be added
#===========================================================

    def cli_configure_virtual_ip(self, vip):
        ''' Function to show Virtual IP of a controller via CLI
        Input: None
        Output: VIP address if configured, None otherwise
        '''
        t = test.Test()
        c = t.controller('main')

        helpers.test_log("Input arguments: virtual IP = %s" % vip)
        try:
            c.config("cluster")
            c.config("virtual-ip %s" % vip)
            assert "Error" not in c.cli_content()
        except:
            helpers.test_log(c.cli_content())
            return False
        else:
            return True


    def cli_get_eth0_ip_using_virtual_ip(self, vip):
        ''' Function to verify that Virtual IP address
        points to some controller via CLI
        Input: VIP address
        Output: Eth0 IP address of the controller that Virtual IP points to
        '''
        t = test.Test()
        try:
            if 'main' in vip:
                c = t.controller('main')
            else:
                c = t.node_spawn(ip=vip)
            content = c.cli('show local node interfaces ethernet0')['content']
            output = helpers.strip_cli_output(content)
            lines = helpers.str_to_list(output)
            assert "Network-interfaces" in lines[0]
            rows = lines[3].split(' ')
        except:
            helpers.test_log(c.cli_content())
            return None
        else:
            return rows[3]


    def cli_show_virtual_ip(self):
        ''' Function to show Virtual IP of a controller via CLI
        Input: None
        Output: VIP address if configured, None otherwise
        '''
        t = test.Test()
        c = t.controller('main')
        try:
            content = c.cli('show virtual-ip')['content']
            output = helpers.strip_cli_output(content)
            lines = helpers.str_to_list(output)
            assert(len(lines) == 3)
            assert "ipv4 address" in lines[0]
        except:
            helpers.test_log(c.cli_content())
            return None
        else:
            return lines[2].strip()


    def bash_verify_virtual_ip(self, vip):
        ''' Function to show Virtual IP of a controller via CLI/Bash
        Input: None
        Output: VIP address if configured, None otherwise
        '''
        t = test.Test()
        c = t.controller('main')
        try:
            content = c.bash('ip addr')['content']
            output = helpers.strip_cli_output(content)
            if vip not in output:
                helpers.test_log("VIP: %s not in the main" % vip)
                return False
        except:
            helpers.test_log(c.cli_content())
            return False
        else:
            helpers.log("VIP: %s is present in the main" % vip)
            return True


    def cli_delete_virtual_ip(self):
        ''' Function to delete Virtual IP from a controller via CLI
        Input: None
        Output: True if successful, False otherwise
        '''
        t = test.Test()
        c = t.controller('main')

        helpers.test_log("Deleting virtual IP address")
        try:
            c.config("cluster")
            c.config("no virtual-ip")
        except:
            helpers.test_log(c.cli_content())
            return False
        else:
            return True


    def cli_cluster_take_leader(self):
        ''' Function to trigger failover to subordinate controller via CLI
        Input: None
        Output: True if successful, False otherwise
        '''
        t = test.Test()
        c = t.controller('subordinate')

        helpers.log("Failover")
        try:
            c.config("config")
            c.send("reauth")
            c.expect(r"Password:")
            c.config("adminadmin")
            c.send("failover")
            if "Error" in c.cli_content():
                helpers.log("Error in CLI content")
                return False
            c.expect(r"Election may cause role transition: enter \"yes\" \(or \"y\"\) to continue:")
            c.config("yes")
        except:
            helpers.test_log(c.cli_content())
            return False
        else:
            return True


    def rest_get_mac_using_virtual_ip(self, vip):
        ''' Function to verify that Virtual IP address
        points to some controller via REST
        Input: VIP address
        Output: Mac address of the controller that Virtual IP points to
        '''
        t = test.Test()
        try:
            if 'main' in vip:
                c = t.controller('main')
            else:
                c = t.node_spawn(ip=vip)

            helpers.log("Getting MAC address of the controller")
            url = '/api/v1/data/controller/os/action/network-interface'
            c.rest.get(url)
            content = c.rest.content()
        except:
            helpers.test_log(c.rest.error())
            return False
        else:
            return content[0]['hardware-address']


    def rest_show_virtual_ip(self):
        ''' Function to show Virtual IP of a controller via REST
        Input: None
        Output: VIP address if configured, None otherwise
        '''
        t = test.Test()
        c = t.controller('main')

        helpers.log("Getting virtual IP address")
        try:
            url = '/api/v1/data/controller/os/config/global/virtual-ip-config'
            c.rest.get(url)
            content = c.rest.content()
        except:
            helpers.test_failure(c.rest.error())
            return False
        else:
            if len(content[0]) > 0:
                return content[0]['ipv4-address']
            else:
                return None


    def rest_cluster_take_leader(self):
        ''' Function to trigger failover to subordinate controller via REST
        Input: None
        Output: True if successful, False otherwise
        '''
        t = test.Test()
        c = t.controller('subordinate')

        helpers.log("Failover")
        try:
            url = '/api/v1/data/controller/cluster/config/new-election'
            c.rest.post(url, {"rigged": str('true')})
        except:
            helpers.test_failure(c.rest.error())
            return False
        else:
            return True

#===========================================================
#End here
#===========================================================



    def cli_compare(self, src, dst, node='main', scp_passwd='adminadmin'):
        ''' Generic function to compare via CLI, using SCP
        Input:
        Src, Dst - source and destination of compare command
        Scp_Password - password for scp connection
        Node - pointing to Main or Subordinate controller
        Output: True if successful, False otherwise
         '''
        helpers.test_log("Running command:\ncompare %s %s" % (src, dst))
        t = test.Test()
        c = t.controller(node)
        c.config("config")
        c.send("compare %s %s" % (src, dst))
        options = c.expect([r'Password: ', r'\(yes/no\)\?', c.get_prompt()])
        content = c.cli_content()
        helpers.log("*****Output is :\n%s" % content)
        try:
            if  ('Could not resolve' in content) or ('Error' in content) or ('No such file or directory' in content):
                helpers.test_failure(content)
                return False
            elif options[0] == 0 :
                helpers.log("INFO:  need to provide passwd " )
                output = c.config(scp_passwd)['content']
            elif options[0] == 1:
                helpers.log("INFO:  need to send yes, then provide passwd " )
                c.send('yes')
                c.expect(r'Password:')
                output = c.config(scp_passwd)['content']
        except:
            helpers.test_failure(c.cli_content())
            return False

        output = c.cli_content()
        helpers.log("Output *** %s " % output)
        if ("Error" in output) or ('No such file or directory' in output):
            helpers.test_failure(c.cli_content())
            return False

        output = helpers.strip_cli_output(output)
        output = helpers.str_to_list(output)
        if options[0] < 2:
            for index, line in enumerate(output):
                if '100%' in line:
                    output = output[(index+1):]
                    break
        
        helpers.log("Cropped output *** %s " % output)
        if len(output) == 0:
            helpers.log("Files are identical")
            return True

        for line in output:
            if re.match(r'[0-9].*|< \!|---|> \!|< \Z|> \Z|\Z', line):
                helpers.log("OK: %s" % line)
                continue
            else:
                helpers.log("files different at line:\n%s" % line)
                return False
        
        if helpers.any_match(c.cli_content(), r'Error'):
            helpers.test_failure(c.cli_content())
            return False
        return True


    def cli_copy(self, src, dst, node='main', scp_passwd='adminadmin'):
        ''' Generic function to copy via CLI, using SCP
        Input:
        Src, Dst - source and destination of copy command
        Scp_Password - password for scp connection
        Node - pointing to Main or Subordinate controller
        Output: True if successful, False otherwise
        '''
        helpers.test_log("Running command:\ncopy %s %s" % (src, dst))
        t = test.Test()
        c = t.controller(node)
        c.config("config")
        c.send("copy %s %s" % (src, dst))
        options = c.expect([r'Password: ', r'\(yes/no\)\?', c.get_prompt()])
        content = c.cli_content()
        helpers.log("*****Output is :\n%s" % content)
        if  ('Could not resolve' in content) or ('Error' in content) or ('No such file or directory' in content):
            helpers.test_failure(content)
            return False

        if options[0] < 2:
            if options[0] == 0 :
                helpers.log("INFO:  need to provide passwd " )
                c.send(scp_passwd)
            elif options[0] == 1:
                helpers.log("INFO:  need to send yes, then provide passwd " )
                c.send('yes')
                c.expect(r'Password:')
                c.send(scp_passwd)
            try:
                c.expect(c.get_prompt(), timeout=180)
                if not (helpers.any_match(c.cli_content(), r'100%') or helpers.any_match(c.cli_content(), r'Lines Applied')):
                    helpers.test_failure(c.cli_content())
                    return False
            except:
                helpers.log('scp failed')
                helpers.test_failure(c.cli_content())
                return False
            else:
                helpers.log('scp completed successfully')
        else:
            c.config("config")

        content = c.cli_content()
        if helpers.any_match(content, r'Error') or  helpers.any_match(content, r'input stream empty') or \
        helpers.any_match(content, r'Lines Applied\: None') or helpers.any_match(content, r'Preserving Session'):
            helpers.test_failure(c.cli_content())
            return False
        return True


    def cli_compare_running_config_with_file_line_by_line(self, filename):
        ''' Function to compare current running config with
        config saved in a file, via CLI line by line
        Input: Filename
        Output: True if successful, False otherwise
        '''
        helpers.test_log("Comparing output of 'show running-config' with 'show file %s'" % filename)
        t = test.Test()
        c = t.controller('main')
        try:
            rc = c.config("show running-config")['content']
            if "Error" in c.cli_content():
                helpers.log("Error in CLI content")
                return False
            rc = helpers.strip_cli_output(rc)
            rc = helpers.str_to_list(rc)
            config_file = c.config("show file %s" % filename)['content']
            if "Error" in c.cli_content():
                helpers.log("Error in CLI content")
                return False
            config_file = helpers.strip_cli_output(config_file)
            config_file = helpers.str_to_list(config_file)

            if not len(rc) == len(config_file):
                helpers.log("Length of RC is different than lenght of RC in file")
                return False
            for index,line in enumerate(rc):
                line_temp = "%s: %s" % (filename, line)
                helpers.log("Comparing '%s' and '%s'" % (line_temp, config_file[index]))
                if 'Current Time' in line_temp:
                    assert 'Current Time' in config_file[index]
                    continue
                if not line_temp == config_file[index]:
                    helpers.log("difference")
                    return False
        except:
            helpers.test_log(c.cli_content())
            return False
        else:
            return True


    def cli_compare_running_config_with_config_line_by_line(self, filename):
        ''' Function to compare current running config with
        config saved in config://, via CLI line by line
        Input: Filename
        Output: True if successful, False otherwise
        '''
        helpers.test_log("Comparing output of 'show running-config' with 'show config %s'" % filename)
        t = test.Test()
        c = t.controller('main')
        try:
            rc = c.config("show running-config")['content']
            if "Error" in c.cli_content():
                helpers.log("Error in CLI content")
                return False
            rc = helpers.strip_cli_output(rc)
            rc = helpers.str_to_list(rc)
            config_file = c.config("show config %s" % filename)['content']
            if "Error" in c.cli_content():
                helpers.log("Error in CLI content")
                return False
            config_file = helpers.strip_cli_output(config_file)
            config_file = helpers.str_to_list(config_file)

            helpers.log("length is %s" % len(rc))
            helpers.log("length is %s" % len(config_file))

            rc = rc[3:]
            config_file = config_file[7:]

            if not len(rc) == len(config_file):
                helpers.log("Length of RC is different than lenght of RC in config")
                return False
            for index,line in enumerate(rc):
                helpers.log("Comparing '%s' and '%s'" % (line, config_file[index]))
                if not line == config_file[index]:
                    helpers.log("difference")
                    return False
        except:
            helpers.test_log(c.cli_content())
            return False
        else:
            return True

    def cli_delete(self, filename):
        ''' Function to delete file
        via CLI
        Input: Filename
        Output: True if successful, False otherwise
        '''
        
        if re.match(r'image://.*', filename):
            name = re.split(r'image://', filename)
            cmd = "delete image %s" % name[1]
        elif re.match(r'config://.*', filename):
            name = re.split(r'config://', filename)
            cmd = "delete config %s" % name[1]
        else:
            cmd = "delete file %s" % filename
            
        helpers.test_log("Running command:\n%s" % cmd)
        t = test.Test()
        c = t.controller('main')
        if re.match(r'config://.*', filename):
            helpers.test_log("Deleting config://, expecting confirmation prompt")
            c.config("config")
            c.send(cmd)
            c.expect(r'[\r\n].+continue+.*|Error.*')
            if 'Error' in c.cli_content():
                helpers.test_failure(c.cli_content())
                return False
            c.config("yes")
        else:
            helpers.test_log("Deleting file")
            c.config(cmd)
        if helpers.any_match(c.cli_content(), r'Error'):
            helpers.test_failure(c.cli_content())
            return False
        return True


    def bash_clear_known_hosts(self):
        ''' Function to delete known SSH RSA keys
        via CLI/BASH
        Output: True if successful, False otherwise
        '''
        helpers.test_log("Running command:\ndebug bash; > .ssh/known_hosts")
        t = test.Test()
        c = t.controller('main')
        try:
            c.config("config")
            c.bash("> .ssh/known_hosts")
            if "Error" in c.cli_content():
                helpers.log("Error in CLI content")
                return False
        except:
            helpers.test_log(c.cli_content())
            return False
        else:
            return True
