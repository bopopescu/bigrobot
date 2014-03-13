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
#        c = t.controller('master')
        pass
#        url = '/api/v1/auth/login' %
#        result = c.rest.post(url, {"user":"admin", "password":"adminadmin"})
#        session_cookie = result['content']['session_cookie']
#        c.rest.set_session_cookie(session_cookie)

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
            c = t.controller('master')
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
        c = t.controller('master')
        url = '/api/v1/data/controller/applications/bvs/tenant[name="%s"]' % (tenant)
        try:
                c.rest.put(url, {"name": tenant})
        except:
                return False
        else:
                return True

    def _rest_show_tenant(self, tenant=None, negative=False):
        t = test.Test()
        c = t.controller('master')

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
        c = t.controller('master')

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
        c = t.controller('master')

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
        c = t.controller('master')
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
        c = t.controller('master')
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
        c = t.controller('master')

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
        c = t.controller('master')

        url = '/api/v1/data/controller/applications/bvs/info/endpoint-manager/vnses' % ()
        try:
            c.rest.get(url)
        except:
            return False
        else:
            return True

    def rest_add_portgroup(self, pg):
        t = test.Test()
        c = t.controller('master')

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
        c = t.controller('master')

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
        c = t.controller('master')

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
        c = t.controller('master')

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
        c = t.controller('master')

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
        c = t.controller('master')

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
        c = t.controller('master')

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
        c = t.controller('master')

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
        c = t.controller('master')

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
        c = t.controller('master')

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
        c = t.controller('master')

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
        c = t.controller('master')

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
        c = t.controller('master')

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
        c = t.controller('master')

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
        c = t.controller('master')
        url = '/api/v1/data/controller/applications/bvs/tenant[name="%s"]/vns[name="%s"]/endpoints[name="%s"]' % (tenant, vns, endpoint)
        try:
            c.rest.patch(url, {"ip-address": ip})
        except:
            return False
        else:
            return True

    def rest_add_mac_endpoint(self, tenant, vns, endpoint, mac):
        t = test.Test()
        c = t.controller('master')
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
        c = t.controller('master')
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
        c = t.controller('master')
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
        c = t.controller('master')
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
        c = t.controller('master')
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
        c = t.controller('master')
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
        c = t.controller('master')
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
        c = t.controller('master')
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
        c = t.controller('master')
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
        c = t.controller('master')
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
        c = t.controller('master')
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
        c = t.controller('master')
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
        c = t.controller('master')
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
        c = t.controller('master')
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
        c = t.controller('master')
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
        c = t.controller('master')
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
        c = t.controller('master')
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
        c = t.controller('master')
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
        c = t.controller('master')
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
        c = t.controller('master')
        url = '/api/v1/data/controller/applications/bvs/info/endpoint-manager/endpoints' % ()
        c.rest.get(url)
        data = c.rest.content()
        if int(len(data)) == int(count):
            helpers.log("Pass:Expected:%s, Actual:%s" % (int(count), len(data)))
            return True
        else:
            helpers.test_failure("Fail: Expected:%s is not equal to Actual:%s" % (int(count), len(data)))
            return False

    def rest_configure_virtual_ip(self, vip):
        ''' Function to configure Virtual IP for a controller
        Input: vip address
        Output: Configured the given VIP address on a master controller
        '''
        t = test.Test()
        c = t.controller('master')

        helpers.log("Input arguments: virtual IP = %s" % vip)
        try:
            url = '/api/v1/data/controller/os/config/global/virtual-ip-config'
            c.rest.post(url, {"ipv4-address": vip})
        except:
            return False
        else:
            return True


    def rest_delete_virtual_ip(self):
        ''' Function to delete  Virtual IP from a controller
        Input: None
        Output: Delete the VIP address
        '''

        t = test.Test()
        c = t.controller('master')

        helpers.log("Deleting virtual IP address")
        try:
            url = '/api/v1/data/controller/os/config/global/virtual-ip-config'
            c.rest.delete(url)
        except:
            return False
        else:
            return True

    def rest_clear_vns_stats(self, vns):
        ''' Function to clear the VNS stats
        Input: vns name
        Output: given vns counters will be cleared
        '''
        t = test.Test()
        c = t.controller('master')
        url = '/api/v1/data/controller/applications/bvs/info/stats/reset-stats/clear-vns-counters'
        c.rest.get(url)

    def rest_verify_vns_rx_stats(self, tenant, vns, frame_cnt, vrange=5):
        ''' Function to verify the VNS stats
        Input: vns name
        Output: given vns counters will be showed
        '''
        t = test.Test()
        c = t.controller('master')
        frame_cnt = int(frame_cnt)
        vrange = int(vrange)
        url = '/api/v1/data/controller/applications/bvs/info/stats/vns-stats/tenants[tenant-name="%s"]/vnses[vns-name="%s"]' % (tenant, vns)
        c.rest.get(url)
        data = c.rest.content()
        if data[0]["tenant-name"] == tenant and data[0]["vns-name"] == vns:
                    if (int(data[0]["counters"]["counters-rx-packets"]) >= (frame_cnt - vrange)) and (int(data[0]["counters"]["counters-rx-packets"]) <= (frame_cnt + vrange)):
                        helpers.log("Pass: Counters value Expected:%d, Actual:%d" % (frame_cnt, int(data[0]["counters"]["counters-rx-packets"])))
                        return True
                    else:
                        helpers.test_failure("Vns counter value does not match,Expected:%d,Actual:%d" % (frame_cnt, int(data[0]["counters"]["counters-rx-packets"])))
                        return False
        else:
            helpers.log("Given tenant name and VNS name does not match the config")

    def rest_verify_vns_rx_rates(self, tenant, vns, frame_rate, vrange=5):
        ''' Function to verify the VNS incoming rates
        Input: vns name
        Output: given vns rates will be displayed and match against the expected rate
        '''
        t = test.Test()
        c = t.controller('master')
        url = '/api/v1/data/controller/applications/bvs/info/stats/vns-stats/tenants[tenant-name="%s"]/vnses[vns-name="%s"]' % (tenant, vns)
        frame_rate = int(frame_rate)
        vrange = int(vrange)
        try:
            c.rest.get(url)
        except:
            return False
        data = c.rest.content()
        if data[0]["tenant-name"] == tenant and data[0]["vns-name"] == vns:
            if (int(data[0]["rates"]["rates-rx-packets"]) >= (frame_rate - vrange)) and (int(data[0]["rates"]["rates-rx-packets"]) <= (frame_rate + vrange)):
                helpers.log("Pass: Rate value Expected:%d, Actual:%d" % (frame_rate, int(data[0]["rates"]["rates-rx-packets"])))
                return True
            else:
                helpers.test_failure("Vns rate value does not match,Expected:%d,Actual:%d" % (frame_rate, int(data[0]["rates"]["rates-rx-packets"])))
                return False
        else:
            helpers.log("Given tenant name and vns name does not match in the config")

    def rest_verify_vns_tx_stats(self, tenant, vns, frame_cnt, vrange=5):
        ''' Function to verify the VNS stats
        Input: vns name
        Output: given vns counters will be showed
        '''
        t = test.Test()
        c = t.controller('master')
        frame_cnt = int(frame_cnt)
        vrange = int(vrange)
        url = '/api/v1/data/controller/applications/bvs/info/stats/vns-stats/tenants[tenant-name="%s"]/vnses[vns-name="%s"]' % (tenant, vns)
        c.rest.get(url)
        data = c.rest.content()
        if data[0]["tenant-name"] == tenant and data[0]["vns-name"] == vns:
                    if (int(data[0]["counters"]["counters-tx-packets"]) >= (frame_cnt - vrange)) and (int(data[0]["counters"]["counters-tx-packets"]) <= (frame_cnt + vrange)):
                        helpers.log("Pass: Counters value Expected:%d, Actual:%d" % (frame_cnt, int(data[0]["counters"]["counters-tx-packets"])))
                        return True
                    else:
                        helpers.test_failure("vns counters does not match, Expected:%d,Actual:%d" % (frame_cnt, int(data[0]["counters"]["counters-tx-packets"])))
                        return False
        else:
            helpers.log("Given tenant name and VNS name does not match the config")

    def rest_verify_vns_tx_rates(self, tenant, vns, frame_rate, vrange=5):
        ''' Function to verify the VNS incoming rates
        Input: vns name
        Output: given vns rates will be displayed and match against the expected rate
        '''
        t = test.Test()
        c = t.controller('master')
        url = '/api/v1/data/controller/applications/bvs/info/stats/vns-stats/tenants[tenant-name="%s"]/vnses[vns-name="%s"]' % (tenant, vns)
        frame_rate = int(frame_rate)
        vrange = int(vrange)
        c.rest.get(url)
        data = c.rest.content()
        if data[0]["tenant-name"] == tenant and data[0]["vns-name"] == vns:
            if (int(data[0]["rates"]["rates-tx-packets"]) >= (frame_rate - vrange)) and (int(data[0]["rates"]["rates-tx-packets"]) <= (frame_rate + vrange)):
                helpers.log("Pass: Rate value Expected:%d, Actual:%d" % (frame_rate, int(data[0]["rates"]["rates-tx-packets"])))
                return True
            else:
                helpers.test_failure("vns rates does not match, Expected:%d,Actual:%d" % (frame_rate, int(data[0]["rates"]["rates-rx-packets"])))
                return False
        else:
            helpers.log("Given tenant name and vns name does not match in the config")

    def rest_clear_fabric_interface_stats(self):
        ''' Function to clear all the fabric interefaces
        Input: None
        Output: All connected switch interfaces will be cleared
        '''
        t = test.Test()
        c = t.controller('master')
        url = '/api/v1/data/controller/applications/bvs/info/stats/reset-stats/clear-interface-counters'
        c.rest.get(url)

    def rest_show_fabric_switch(self):
        '''Return the list of connected switches

            Returns: gives list of connected switches
        '''
        t = test.Test()
        c = t.controller('master')
        url = '/api/v1/data/controller/core/switch' % ()
        c.rest.get(url)

        return True

    def rest_show_fabric_link(self):
        '''Return the list of fabric links

            Returns: Print the Total fabric links
        '''
        t = test.Test()
        c = t.controller('master')

        url = '/api/v1/data/controller/applications/bvs/info/fabric?select=link' % ()
        c.rest.get(url)

        return True

    def rest_add_switch(self, switch):
        '''add the fabric switch

            Input:
                    switch        Name of the switch

            Returns: add the fabric switch
        '''
        t = test.Test()
        c = t.controller('master')

        url = '/api/v1/data/controller/core/switch-config[name="%s"]' % (switch)
        try:
            c.rest.put(url, {"name": switch})
        except:
            helpers.log("Error: Invalid argument: syntax: expected [a-zA-Z][-.0-9a-zA-Z_]*$ for: %s" % (switch))
            return False
        else:
            return True

    def rest_add_dpid(self, switch, dpid):
        t = test.Test()
        c = t.controller('master')

        url = '/api/v1/data/controller/core/switch-config[name="%s"]' % (switch)
        try:
            c.rest.patch(url, {"dpid": dpid})
        except:
            helpers.log("Error: Invalid argument: Invalid switch id (8-hex bytes): %s; switch %s doesn't exist" % (dpid,switch))
            return False
        else:
            return True

    def rest_add_fabric_role(self, switch, role):
        t = test.Test()
        c = t.controller('master')

        url = '/api/v1/data/controller/core/switch-config[name="%s"]' % (switch)
        try:
            c.rest.patch(url, {"fabric-role": role})
        except:
            return False
        else:
            return True

    def rest_add_leaf_group(self, switch, group):
        t = test.Test()
        c = t.controller('master')

        url = '/api/v1/data/controller/core/switch-config[name="%s"]' % (switch)
        try:
            c.rest.patch(url, {"leaf-group": group})
        except:
            helpers.log("Error: Invalid argument: syntax: expected [a-zA-Z][-.0-9a-zA-Z_]*$ for: %s" % (group))
            return False
        else:
            return True

    def rest_delete_leaf_group(self, switch, group=None):
        '''
           Function to delete the specific leaf group
           Input:  Switch name
        '''
        t = test.Test()
        c = t.controller('master')
        url = '/api/v1/data/controller/core/switch-config[name="%s"]/leaf-group' % (switch)
        try:
            c.rest.delete(url, {"leaf-group": None})
        except:
            return False
        else:
            return True

    def rest_delete_fabric_switch(self, switch=None):
        t = test.Test()
        c = t.controller('master')

        url = '/api/v1/data/controller/core/switch-config[name="%s"]' % (switch)
        try:
            c.rest.delete(url, {"name": switch})
        except:
            return False
        else:
            return True

    def rest_verify_fabric_switch_all(self):
        t = test.Test()
        c = t.controller('master')
        url = '/api/v1/data/controller/core/switch' % ()
        c.rest.get(url)
        data = c.rest.content()
        for i in range (0,len(data)):
            if data[i]["fabric-switch-info"]["suspended"] is True and (data[i]["fabric-switch-info"]["fabric-role"] == "leaf" or data[i]["fabric-switch-info"]["fabric-role"] == "spine"):
                helpers.test_failure("Fabric manager status is incorrect")
            elif data[i]["fabric-switch-info"]["suspended"] is False and (data[i]["fabric-switch-info"]["fabric-role"] == "virtual"):
                helpers.test_failure("Fabric manager status is incorrect")
        helpers.log("Fabric manager status is correct")

        return True

    def rest_verify_fabric_link_after_switch_removal(self, switch):
        t = test.Test()
        c = t.controller('master')
        url = '/api/v1/data/controller/applications/bvs/info/fabric?select=link' % ()
        c.rest.get(url)
        data = c.rest.content()
        for i in range (0,len(data)):
            if data[i]["link"]["dst"]["switch-info"]["switch-name"] == switch and data[i]["link"]["link-direction"] == "bidirectional":
                helpers.test_failure("%s Fabric Links not deleted" % str(data[i]["link"]["dst"]["switch-info"]["switch-name"]))
                break

        return True

    def rest_verify_fabric_link_common(self, switch):
        t = test.Test()
        c = t.controller('master')
        url = '/api/v1/data/controller/applications/bvs/info/fabric?select=link' % ()
        c.rest.get(url)
        data = c.rest.content()
        for i in range (0,len(data)):
            if data[i]["link"]["dst"]["switch-info"]["switch-name"] == switch and data[i]["link"]["link-direction"] == "bidirectional":
                helpers.test_log("%s Fabric Links not deleted" % str(data[i]["link"]["dst"]["switch-info"]["switch-name"]))

        return True

    def rest_verify_fabric_switch_role(self, dpid, role):
        t = test.Test()
        c = t.controller('master')
        url = '/api/v1/data/controller/core/switch' % ()
        c.rest.get(url)
        data = c.rest.content()
        status = False
        for i in range (0,len(data)):
            if data[i]["dpid"] == dpid and data[i]["fabric-switch-info"]["fabric-role"] == role:
                helpers.test_log("Fabric switch Role of %s is %s" % (str(data[i]["dpid"]), str(data[i]["fabric-switch-info"]["fabric-role"])))
                status = True
                return True
                break
        if status == False:
            helpers.test_failure("Fabric switch role removal Test Failed")

        return False

    def rest_delete_fabric_role(self, switch, role=None):
        t = test.Test()
        c = t.controller('master')

        url = '/api/v1/data/controller/core/switch-config[name="%s"]/fabric-role' % (switch)
        c.rest.delete(url, {"fabric-role": role})
        helpers.test_log("Output: %s" % c.rest.content_json())
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())

        return c.rest.content()

    def rest_verify_fabric_lag(self, switch):
        '''
          Function to verify Lag formation from the fabric switches
          Input : specific switch name
          output : Will provide the No of lag it is suppose to form between Spine and Leaf in Dual Rack or single rack setup
        '''
        t = test.Test()
        c = t.controller('master')
        url = '/api/v1/data/controller/core/switch[name="%s"]/interface' % (switch)
        c.rest.get(url)
        data = c.rest.content()
        url1 = '/api/v1/data/controller/core/switch[name="%s"]' % (switch)
        c.rest.get(url1)
        data1 = c.rest.content()
        url2 = '/api/v1/data/controller/core/switch[name="%s"]?select=fabric-lag' % (switch)
        c.rest.get(url2)
        data3 = c.rest.content()
        if str(data1[0]["fabric-switch-info"]["switch-name"]) == str(switch):
            if data1[0]["fabric-switch-info"]["fabric-role"] == "spine":
                fabric_interface = 0
                rack_lag = 0
                for i in range(0,len(data)):
                    if data[i]["type"] == "leaf":
                        fabric_interface = fabric_interface + 1
                for i in range(0,len(data3[0]["fabric-lag"])):
                        if (data3[0]["fabric-lag"][i]["lag-type"]) == "rack-lag":
                            rack_lag = rack_lag + int(len(data3[0]["fabric-lag"][i]["member"]))
                if (int(rack_lag) == int(fabric_interface)):
                                helpers.log("No of Rack lag from  %s is correct,Expected = %d, Actual = %d " % (switch, fabric_interface, rack_lag))
                                return True
                else:
                                helpers.test_failure("No of Rack lag from %s is incorrect,Expected = %d, Actual = %d " % (switch, fabric_interface, rack_lag))
                                return False
            elif data1[0]["fabric-switch-info"]["fabric-role"] == "leaf":
                    fabric_spine_interface = 0
                    fabric_peer_interface = 0
                    for i in range(0,len(data)):
                                if data[i]["type"] == "spine":
                                    fabric_spine_interface = fabric_spine_interface + 1

                                elif data[i]["type"] == "leaf":
                                    fabric_peer_interface = fabric_peer_interface + 1

                    for i in range(0,len(data3[0]["fabric-lag"])):
                                        if data3[0]["fabric-lag"][i]["lag-type"] == "spine-lag":
                                            if (int(len(data3[0]["fabric-lag"][i]["member"])) == int(fabric_spine_interface)):
                                                helpers.log("Spine lag formation from leaf switch %s is correct,Expected = %d, Actual = %d, " % (switch, fabric_spine_interface, len(data3[0]["fabric-lag"][i]["member"])))
                                                return True
                                            else:
                                                helpers.test_failure(" Spine lag formation from leaf %s switch is not correct,Expected = %d, Actual = %d" % (switch, fabric_spine_interface, len(data3[0]["fabric-lag"][i]["member"])))
                                                return False
                                        elif data3[0]["fabric-lag"][i]["lag-type"] == "spine-broadcast-lag":
                                                if len(data3[0]["fabric-lag"][i]["member"]) == (int(self.rest_verify_no_of_rack()) * fabric_spine_interface):
                                                    helpers.log("Spine Broadcast lag from leaf switch %s is correct , Actual = %d , Expected = %d" % (switch, int(self.rest_get_no_of_rack()), fabric_spine_interface))
                                                    return True
                                                else:
                                                        helpers.test_failure("Spine Broadcast lag from leaf switch %s is not correct,expected = %d,actual = %d" % (switch, (int(self.rest_get_no_of_rack()) * fabric_spine_interface), len(data3[0]["fabric-lag"][i]["member"])))
                                                        return False
                                        elif data3[0]["fabric-lag"][i]["lag-type"] == "leaf-lag":
                                            if len(data3[0]["fabric-lag"][i]["member"]) == fabric_peer_interface:
                                                helpers.log("Peer lag formation from leaf switch %s is correct,Expected = %d, Actual = %d" % (switch, fabric_peer_interface, len(data3[0]["fabric-lag"][i]["member"])))
                                                return True
                                            else:
                                                helpers.test_failure(" Spine lag formation from leaf %s switch is not correct,expected= %d,Actual= %d" % (switch, fabric_peer_interface, len(data3[0]["fabric-lag"][i]["member"])))
                                                return False
        else :
            return False


    def rest_verify_fabric_switch(self, dpid):
        # Function verify fabric switch status for default as well after fabric role configuration
        t = test.Test()
        c = t.controller('master')
        url = '/api/v1/data/controller/core/switch[dpid="%s"]' % (dpid)
        c.rest.get(url)
        data = c.rest.content()
        if data[0]["dpid"] == dpid:
            if data[0]["connected"]:
                if data[0]["fabric-switch-info"]["fabric-role"] != "virtual":
                    if data[0]["fabric-switch-info"]["fabric-role"] == "spine" and data[0]["fabric-switch-info"]["suspended"] == False:
                        helpers.log("Pass: Fabric switch connection status for spine is correct")
                        return True
                    elif data[0]["fabric-switch-info"]["fabric-role"] == "leaf" and data[0]["fabric-switch-info"]["suspended"] == False and data[0]["fabric-switch-info"]["leaf-group"] != '':
                        if data[0]["dpid"] == dpid and data[0]["fabric-switch-info"]["lacp-port-offset"] == 0:
                            helpers.log("Pass: Fabric switch connection status for %s dual leaf is correct" % str(data[0]["fabric-switch-info"]["switch-name"]))
                            return True
                        elif data[0]["dpid"] == dpid and data[0]["fabric-switch-info"]["lacp-port-offset"] == 100:
                            helpers.log("Pass: Fabric switch connection status for %s dual leaf is correct" % str(data[0]["fabric-switch-info"]["switch-name"]))
                            return True
                elif data[0]["fabric-switch-info"]["suspended"] == True:
                        helpers.log("Default fabric role is virtual for not added fabric switches")
                        return True
                else:
                        helpers.test_failure("Fabric role is virual but suspended = False ")
                        return False
            elif data[0]["fabric-switch-info"]["suspended"] == False or data[0]["fabric-switch-info"]["suspended"] == True:
                helpers.test_failure("Fail: Switch is not connected , Fabric switch status still exists")
                return False
        else :
            return False

    def rest_verify_fabric_link(self):
        t = test.Test()
        c = t.controller('master')
        url = '/api/v1/data/controller/core/switch/interface' % ()
        c.rest.get(url)
        data = c.rest.content()
        fabric_interface = 0
        for i in range(0,len(data)):
            if data[i]["type"] == "leaf" or data[i]["type"] == "spine":
                fabric_interface = fabric_interface + 1
        url1 = '/api/v1/data/controller/applications/bvs/info/fabric?select=link' % ()
        c.rest.get(url1)
        data1 = c.rest.content()
        bidir_link = 0
        if not((data1 and True) or False):
            for i in range(0,len(data1[0]["link"])):
                if data1[0]["link"][i]["link-direction"] == "bidirectional":
                    bidir_link = bidir_link + 1
                    if bidir_link == fabric_interface/2:
                        helpers.log("Pass: All Fabric links states are bidirectional")
                        return True
                    else:
                        helpers.test_failure("Fail: Inconsistent state of fabric links. Fabric_Interface = %d , bidir_link = %d" % (fabric_interface, bidir_link))
                        return False
        else:
            helpers.log("Fabric switches are misconfigued")

    def rest_verify_no_of_rack(self):
        t = test.Test()
        c = t.controller('master')
        url = '/api/v1/data/controller/core/switch' % ()
        c.rest.get(url)
        data = c.rest.content()
        rack = []
        rack_count = 0
        for i in range(0,len(data)):
            if data[i]["fabric-switch-info"]["fabric-role"] == "leaf":
                if data[i]["fabric-switch-info"]["leaf-group"] == None:
                    rack_count = rack_count + 1
                elif not data[i]["fabric-switch-info"]["leaf-group"] in rack:
                    rack.append(data[i]["fabric-switch-info"]["leaf-group"])

        total_rack = rack_count + len(rack)
        helpers.log("Total Rack in the Topology: %d" % total_rack)
        return total_rack

    def rest_verify_no_of_spine(self):
        t = test.Test()
        c = t.controller('master')
        url = '/api/v1/data/controller/core/switch' % ()
        c.rest.get(url)
        data = c.rest.content()
        list_spine = []
        for i in range(0,len(data)):
            if data[i]["fabric-switch-info"]["fabric-role"] == "spine":
                list_spine.append(data[i]["fabric-switch-info"]["switch-name"])

        helpers.log("Total Spine in the topology: %d" % len(list_spine))
        return list_spine

    def rest_verify_rack_lag_from_leaf(self, switcha, switchb):
        '''Verify Rack lag formation for the leaf switch mentioned in the variables to all the racks
            Input: Leaf switch name  , any down event you are expecting to verify on
            Output: Will check the total no of spine switches and compare against the rack connection spine switches.
        '''
        t = test.Test()
        c = t.controller('master')
        url = '/api/v1/data/controller/core/switch[name="%s"]?select=fabric-lag' % (switcha)
        c.rest.get(url)
        data = c.rest.content()
        for i in range(0,len(data[0]["fabric-lag"])):
            if data[0]["fabric-lag"][i]["lag-type"] == "rack-lag":
                actual_spine = []
                for j in range(0,len(data[0]["fabric-lag"][i]["member"])):
                    if data[0]["fabric-lag"][i]["member"][j]["dst-switch"] not in actual_spine:
                        actual_spine.append(data[0]["fabric-lag"][i]["member"][j]["dst-switch"])
                for j in range(0,len(actual_spine)):
                    if (str(actual_spine[j]) == str(switchb)):
                        helpers.log("Rack connectivity from leaf switch %s using all the spine switches are up" % switcha)
                        return True

    def rest_verify_forwarding_lag(self, dpid, switch):
        '''Verify Edge port  Information in Controller Forwarding Table

            Input:  Specific DPID of the switch and also the switch name of the specific device

            Return: Match forwarding table lag/Port for peer switch edge ports
        '''
        t = test.Test()
        c = t.controller('master')
        url = '/api/v1/data/controller/applications/bvs/info/forwarding/network/switch[switch-name="%s"]/lag-table' % (switch)
        c.rest.get(url)
        data = c.rest.content()
        url1 = '/api/v1/data/controller/core/switch[dpid="%s"]' % (dpid)
        c.rest.get(url1)
        data1 = c.rest.content()
        url2 = '/api/v1/data/controller/core/switch[name="%s"]?select=fabric-lag' % (switch)
        c.rest.get(url2)
        data2 = c.rest.content()
        peer_intf = []
        for i in range(0,len(data2[0]["fabric-lag"])):
            if data2[0]["fabric-lag"][i]["lag-type"] == "leaf-lag":
                interface = re.sub("\D", "", data2[0]["fabric-lag"][i]["member"][0]["src-interface"])
                peer_intf.append(int(interface))
        if len(peer_intf) != 0:
            if data1[0]["fabric-switch-info"]["leaf-group"] == None:
                for i in range(0,len(data)):
                    for j in range(0,len(data[i]["port"])):
                        if (data[i]["port"][j]["port-num"] == peer_intf[0]):
                            helpers.test_failure("Peer switch edge ports are not deleted from lag table")
                            return False

            else:
                for i in range(0,len(data)):
                    for j in range(0,len(data[i]["port"])):
                        if (data[i]["port"][j]["port-num"]) == (peer_intf[0]):
                            helpers.log("Peer switch edge ports are properly added in forwarding table")
                            return True
            return False

    def rest_verify_fabric_interface_lacp(self, switch, intf):
        t = test.Test()
        c = t.controller('master')
        url = '/api/v1/data/controller/core/switch[name="%s"]/interface[name="%s"]' % (switch, intf)
        c.rest.get(url)
        data = c.rest.content()
        try:
                if data[0]["lacp-active"] == True:
                    if data[0]["lacp-partner-info"]["system-mac"] != None:
                        helpers.log("LACP Neibhour Is Up and active")
                        return True
                    else:
                        helpers.test_failure("LACP is enabled , LACP Partner is not seen , check the floodlight logs")
                        return False
        except KeyError:
            return False

    def rest_verify_fabric_error_dual_tor_peer_link(self, rack):
        t = test.Test()
        c = t.controller('master')
        url = '/api/v1/data/controller/applications/bvs/info/fabric/errors/dual-tor/peer-link-absent' % ()
        c.rest.get(url)
        data = c.rest.content()
        if not((data and True) or False):
            if len(data) != 0:
                if data["name"] == rack:
                    helpers.log("Fabric error reported for %s" % data["name"])
                    return True
                else:
                    helpers.test_failure("No Fabric error Reported for dual tor no peer link for rack %s" % data["name"])
                    return False
            else:
                helpers.log("Fabric error will be none")

    def rest_verify_forwarding_port_table(self, switch):
        t = test.Test()
        c = t.controller('master')
        url = '/api/v1/data/controller/applications/bvs/info/forwarding/network/switch[switch-name="%s"]/port-table' % (switch)
        c.rest.get(url)
        if not c.rest.status_code_ok():
            helpers.log("Error: forwarding output table is not returning any value")
            helpers.test_failure(c.rest.error())

    def rest_show_fabric_interface(self, switch, intf):
        '''
        Function to get the fabric interface status for validation
        Input: switch name and interface
        Output" Rest output of the fabric interface for various validation
        '''
        t = test.Test()
        c = t.controller('master')
        url = '/api/v1/data/controller/core/switch[name="%s"]/interface[name="%s"]' % (switch, intf)
        c.rest.get(url)
        return c.rest.content()

    def rest_verify_fabric_interface(self, switch, intf):
        '''
        Function to verify the specific fabric interface status
        Input:  Rest Output from the function (show_fabric_interface())
        Output" validation of the fabric interface status
        '''
        t = test.Test()
        c = t.controller('master')
        url = '/api/v1/data/controller/core/switch[name="%s"]/interface[name="%s"]' % (switch, intf)
        c.rest.get(url)
        data = c.rest.content()
        if len(data) != 0:
            if data[0]["state"] == "down" and data[0]["type"] == "unknown":
                helpers.log("Interface is connected to spine or Physical Interface status is down for the leaf switch")
            elif data[0]["state"] == "up" and data[0]["type"] == "edge":
                    helpers.log("Inteface is connected to leaf and it is a edge port")
            elif data[0]["state"] == "up" and data[0]["type"] == "leaf" or data[0]["state"] == "up" and data[0]["type"] == "spine":
                    helpers.log("Interface is fabric interface")
                    return True
            elif data[0]["state"] == "quarantined" and data[0]["type"] == "unknown":
                    helpers.log("Edge ports will not come up for the spine switches")
            else:
                    helpers.test_failure("Interface status is not known to the fabric system , Please check the logs")
                    return False
        else:
            helpers.test_failure("Given fabric interface is not valid")
            return False


    def rest_verify_forwarding_port_edge(self, switcha, switchb):
        '''
         Function to verify Lag id for the portgroup
         Input:  Dual leaf switch names
         Output" True/false based on the lag-id creation for the same edge port-groups on both the leaf switches
        '''
        t = test.Test()
        c = t.controller('master')
        url_a = '/api/v1/data/controller/applications/bvs/info/forwarding/network/switch[switch-name="%s"]/port-table' % (switcha)
        c.rest.get(url_a)
        data = c.rest.content()
        url_b = '/api/v1/data/controller/applications/bvs/info/forwarding/network/switch[switch-name="%s"]/port-table' % (switchb)
        c.rest.get(url_b)
        data1 = c.rest.content()
        if data[0]["lag-id"] == data1[0]["lag-id"]:
            helpers.log("Portgroup Lag id creation in forwarding table is correct for dual rack")
            return True
        else:
            helpers.test_failure("Portgroup Lag id creation in forwarding table does not match for dual rack , check the logs")
            return False

    def rest_verify_forwarding_port_source_mac_check(self, switch):
        '''
        Function to verify the Source mac check status for the fabric interfaces
        Input:  switch name
        Output" Find the fabric interface for the switch and check the source mac check setting
        '''
        t = test.Test()
        c = t.controller('master')
        url = '/api/v1/data/controller/core/switch[name="%s"]/interface' % (switch)
        c.rest.get(url)
        data = c.rest.content()
        list_fabric_interface = []
        list_fabric_edge_interface = []
        for i in range(0,len(data)):
            if data[i]["type"] == "unknown":
                continue
            elif data[i]["type"] == "edge":
                list_fabric_edge_interface.append(int(re.sub("\D", "", (data[i]["name"]))))
            elif data[i]["type"] == "leaf" or data[i]["type"] == "spine":
                list_fabric_interface.append(int(re.sub("\D", "", (data[i]["name"]))))
        url1 = '/api/v1/data/controller/applications/bvs/info/forwarding/network/switch[switch-name="%s"]/port-table' % (switch)
        c.rest.get(url1)
        data1 = c.rest.content()
        if len(list_fabric_interface) != 0 or len(list_fabric_edge_interface) != 0:
            for i in range(0,len(data1)):
                if data1[i]["port-num"] in list_fabric_interface:
                    if data1[i]["is-src-mac-check-disabled"] == True:
                        helpers.log("Source Mac check is disabled on Fabric interfaces")
                        return True
                    else:
                        helpers.test_failure("Source MAC check is enabled on Fabric Interface:%s" % data1[i]["port-num"])
                        return False
                elif data1[i]["port-num"] in list_fabric_edge_interface:
                    if data1[i]["is-src-mac-check-disabled"] == False:
                        helpers.log("Source MAC check is enabled on fabric edge interfaces")
                        return True
                    else:
                        helpers.log("Source MAC check is disabled on fabric edge interface:%s" % data1[i]["port-num"])
                        return False
        return False

    def rest_disable_fabric_interface(self, switch, intf):
        t = test.Test()
        c = t.controller('master')

        url = '/api/v1/data/controller/core/switch-config[name="%s"]/interface[name="%s"]' % (switch, intf)
        try:
            c.rest.patch(url, {"shutdown": True})
        except:
            return False
        else:
            return True

    def rest_enable_fabric_interface(self, switch, intf):
        t = test.Test()
        c = t.controller('master')

        url = '/api/v1/data/controller/core/switch-config[name="%s"]/interface[name="%s"]' % (switch, intf)
        try:
            c.rest.patch(url, {"shutdown": None})
        except:
            return False
        else:
            return True

    def rest_verify_fabric_interface_rx_stats(self, switch, intf, frame_cnt, vrange=5):
        ''' Function to verify the fabric interface stats
        Input: switch and interface
        Output: reusult will be compared against the frame_cnt given in the arguments
        '''
        t = test.Test()
        c = t.controller('master')
        url = '/api/v1/data/controller/core/switch[name="%s"]/interface[name="%s"]?select=interface-stats/interface-rx-counters' % (switch, intf)
        frame_cnt = int(frame_cnt)
        vrange = int(vrange)
        c.rest.get(url)
        data = c.rest.content()
        if data[0]["interface-stats"]["interface-rx-counters"]["rxcounters-interface-name"] == intf and data[0]["interface-stats"]["interface-rx-counters"]["rxcounters-switch-name"] == switch:
            if (data[0]["interface-stats"]["interface-rx-counters"]["rxcounters-packets-unicast"] >= (frame_cnt - vrange)) and (data[0]["interface-stats"]["interface-rx-counters"]["rxcounters-packets-unicast"] <= (frame_cnt + vrange)):
                helpers.log("Pass: Rate value Expected:%d, Actual:%d" % (frame_cnt, data[0]["interface-stats"]["interface-rx-counters"]["rxcounters-packets-unicast"]))
                return True
            elif (data[0]["interface-stats"]["interface-rx-counters"]["rxcounters-packets-broadcast"] >= (frame_cnt - vrange)) and (data[0]["interface-stats"]["interface-rx-counters"]["rxcounters-packets-broadcast"] <= (frame_cnt + vrange)):
                helpers.log("Pass: Rate value Expected:%d, Actual:%d" % (frame_cnt, data[0]["interface-stats"]["interface-rx-counters"]["rxcounters-packets-broadcast"]))
                return True
            elif (data[0]["interface-stats"]["interface-rx-counters"]["rxcounters-packets-multicast"] >= (frame_cnt - vrange)) and (data[0]["interface-stats"]["interface-rx-counters"]["rxcounters-packets-multicast"] <= (frame_cnt + vrange)):
                helpers.log("Pass: Rate value Expected:%d, Actual:%d" % (frame_cnt, data[0]["interface-stats"]["interface-rx-counters"]["rxcounters-packets-multicast"]))
                return True
            else:
                helpers.test_failure("Interface counters does not match Expected:%d,Actual:%d,%d,%d" % (frame_cnt, data[0]["interface-stats"]["interface-rx-counters"]["rxcounters-packets-unicast"], data[0]["interface-stats"]["interface-rx-counters"]["rxcounters-packets-broadcast"], data[0]["interface-stats"]["interface-rx-counters"]["rxcounters-packets-multicast"]))
                return False
        else:
            helpers.log("Given switch name and interface name are not present in the controller")

    def rest_verify_fabric_interface_tx_stats(self, switch, intf, frame_cnt, vrange=5):
        ''' Function to verify the fabric interface tx stats
        Input: switch and interface
        Output: Results will be compared against frame_cnt given
        '''
        t = test.Test()
        c = t.controller('master')
        url = '/api/v1/data/controller/core/switch[name="%s"]/interface[name="%s"]?select=interface-stats/interface-tx-counters' % (switch, intf)
        frame_cnt = int(frame_cnt)
        vrange = int(vrange)
        c.rest.get(url)
        data = c.rest.content()
        if data[0]["interface-stats"]["interface-tx-counters"]["txcounters-interface-name"] == intf and data[0]["interface-stats"]["interface-tx-counters"]["txcounters-switch-name"] == switch:
            if (data[0]["interface-stats"]["interface-tx-counters"]["txcounters-packets-unicast"] >= (frame_cnt - vrange)) and (data[0]["interface-stats"]["interface-tx-counters"]["txcounters-packets-unicast"] <= (frame_cnt + vrange)):
                helpers.log("Pass: Rate value Expected:%d, Actual:%d" % (frame_cnt, data["interface-stats"]["interface-tx-counters"]["txcounters-packets-unicast"]))
                return True
            elif (data[0]["interface-stats"]["interface-tx-counters"]["txcounters-packets-broadcast"] >= (frame_cnt - vrange)) and (data[0]["interface-stats"]["interface-tx-counters"]["txcounters-packets-broadcast"] <= (frame_cnt + vrange)):
                helpers.log("Pass: Rate value Expected:%d, Actual:%d" % (frame_cnt, data["interface-stats"]["interface-tx-counters"]["txcounters-packets-broadcast"]))
                return True
            elif (data[0]["interface-stats"]["interface-tx-counters"]["txcounters-packets-multicast"] >= (frame_cnt - vrange)) and (data[0]["interface-stats"]["interface-tx-counters"]["txcounters-packets-multicast"] <= (frame_cnt + vrange)):
                helpers.log("Pass: Rate value Expected:%d, Actual:%d" % (frame_cnt, data["interface-stats"]["interface-tx-counters"]["txcounters-packets-multicast"]))
                return True
            else:
                helpers.test_failure("Interface counters does not match Expected:%d,Actual:%d,%d,%d" % (frame_cnt, data[0]["interface-stats"]["interface-tx-counters"]["txcounters-packets-unicast"], data[0]["interface-stats"]["interface-tx-counters"]["txcounters-packets-broadcast"], data[0]["interface-stats"]["interface-tx-counters"]["txcounters-packets-multicast"]))
                return False
        else:
            helpers.log("Given switch name and interface name are not present in the controller")

    def rest_verify_fabric_interface_rx_rates(self, switch, intf, frame_rate, vrange=5):
        ''' Function to verify the fabric interface rates
        Input: switch and interface
        Output: reusult will be compared against the frame_rate given in the arguments
        '''
        t = test.Test()
        c = t.controller('master')
        url = '/api/v1/data/controller/core/switch[name="%s"]/interface[name="%s"]?select=interface-stats/interface-rx-rates' % (switch, intf)
        frame_rate = int(frame_rate)
        vrange = int(vrange)
        c.rest.get(url)
        data = c.rest.content()
        if data[0]["interface-stats"]["interface-rx-rates"]["rxrates-interface-name"] == intf and data[0]["interface-stats"]["interface-rx-rates"]["rxrates-switch-name"] == switch:
            if (data[0]["interface-stats"]["interface-rx-rates"]["rxrates-packets-unicast"] >= (frame_rate - vrange)) and (data[0]["interface-stats"]["interface-rx-rates"]["rxrates-packets-unicast"] <= (frame_rate + vrange)):
                helpers.log("Pass: Rate value Expected:%d, Actual:%d" % (frame_rate, data[0]["interface-stats"]["interface-rx-rates"]["rxrates-packets-unicast"]))
                return True
            else:
                helpers.test_failure("Interface Rx rates does not match, Expected:%d, Actual:%d" % (frame_rate, data[0]["interface-stats"]["interface-rx-rates"]["rxrates-packets-unicast"]))
                return False
        else:
            helpers.log("Given switch name and interface name are not present in the controller")

    def rest_verify_fabric_interface_tx_rates(self, switch, intf, frame_rate, vrange=5):
        ''' Function to verify the fabric interface tx rates
        Input: switch and interface
        Output: Results will be compared against frame_rate given
        '''
        t = test.Test()
        c = t.controller('master')
        url = '/api/v1/data/controller/core/switch[name="%s"]/interface[name="%s"]?select=interface-stats/interface-tx-rates' % (switch, intf)
        frame_rate = int(frame_rate)
        vrange = int(vrange)
        c.rest.get(url)
        data = c.rest.content()
        if data[0]["interface-stats"]["interface-tx-rates"]["txrates-interface-name"] == intf and data[0]["interface-stats"]["interface-tx-rates"]["txrates-switch-name"] == switch:
            if (data[0]["interface-stats"]["interface-tx-rates"]["txrates-packets-unicast"] >= (frame_rate - vrange)) and (data[0]["interface-stats"]["interface-tx-rates"]["txrates-packets-unicast"] <= (frame_rate + vrange)):
                helpers.log("Pass: Rate value Expected:%d, Actual:%d" % (frame_rate, data[0]["interface-stats"]["interface-tx-rates"]["txrates-packets-unicast"]))
                return True
            else:
                helpers.test_failure("Interface Rx rates does not match, Expected:%d, Actual:%d" % (frame_rate, data[0]["interface-stats"]["interface-tx-rates"]["txrates-packets-unicast"]))
                return False
        else:
            helpers.log("Given switch name and interface name are not present in the controller")

    def rest_verify_tenant_rx_stats(self, tenant, frame_cnt, vrange=5):
        ''' Function to verify the Tenant stats
        Input: Tenant name , matching frame count , if required user can provide range as well for the frame count match
        Output: given Tenant counters will be showed and matched aginst the value
        '''
        t = test.Test()
        c = t.controller('master')
        frame_cnt = int(frame_cnt)
        vrange = int(vrange)
        url = '/api/v1/data/controller/applications/bvs/info/stats/tenant-stats/tenants[tenant-name="%s"]' % (tenant)
        c.rest.get(url)
        data = c.rest.content()
        if data[0]["tenant-name"] == tenant:
                    if (int(data[0]["counters"]["counters-rx-packets"]) >= (frame_cnt - vrange)) and (int(data[0]["counters"]["counters-rx-packets"]) <= (frame_cnt + vrange)):
                        helpers.log("Pass: Tenant Counters value Expected:%d, Actual:%d" % (frame_cnt, int(data[0]["counters"]["counters-rx-packets"])))
                        return True
                    else:
                        helpers.test_failure("Tenant counter value does not match,Expected:%d,Actual:%d" % (frame_cnt, int(data[0]["counters"]["counters-rx-packets"])))
                        return False
        else:
            helpers.log("Given tenant name does not match the config")
            
    def rest_verify_tenant_tx_stats(self, tenant, frame_cnt, vrange=5):
        ''' Function to verify the Tenant Tx stats
        Input: Tenant name , matching frame count , if required user can provide range as well for the frame count match
        Output: given Tenant counters will be showed and matched aginst the value
        '''
        t = test.Test()
        c = t.controller('master')
        frame_cnt = int(frame_cnt)
        vrange = int(vrange)
        url = '/api/v1/data/controller/applications/bvs/info/stats/tenant-stats/tenants[tenant-name="%s"]' % (tenant)
        c.rest.get(url)
        data = c.rest.content()
        if data[0]["tenant-name"] == tenant:
                    if (int(data[0]["counters"]["counters-tx-packets"]) >= (frame_cnt - vrange)) and (int(data[0]["counters"]["counters-tx-packets"]) <= (frame_cnt + vrange)):
                        helpers.log("Pass: Tenant Counters value Expected:%d, Actual:%d" % (frame_cnt, int(data[0]["counters"]["counters-tx-packets"])))
                        return True
                    else:
                        helpers.test_failure("Tenant counter value does not match,Expected:%d,Actual:%d" % (frame_cnt, int(data[0]["counters"]["counters-tx-packets"])))
                        return False
        else:
            helpers.log("Given tenant name does not match the config")
            
    def rest_verify_tenant_rx_rates(self, tenant, frame_rate, vrange=5):
        ''' Function to verify the Tenant Tx stats
        Input: Tenant name , matching frame count , if required user can provide range as well for the frame count match
        Output: given Tenant counters will be showed and matched aginst the value
        '''
        t = test.Test()
        c = t.controller('master')
        frame_rate = int(frame_rate)
        vrange = int(vrange)
        url = '/api/v1/data/controller/applications/bvs/info/stats/tenant-stats/tenants[tenant-name="%s"]' % (tenant)
        c.rest.get(url)
        data = c.rest.content()
        if data[0]["tenant-name"] == tenant:
                    if (int(data[0]["rates"]["rates-rx-packets"]) >= (frame_rate - vrange)) and (int(data[0]["rates"]["rates-rx-packets"]) <= (frame_rate + vrange)):
                        helpers.log("Pass: Tenant Counters value Expected:%d, Actual:%d" % (frame_rate, int(data[0]["rates"]["rates-rx-packets"])))
                        return True
                    else:
                        helpers.test_failure("Tenant counter value does not match,Expected:%d,Actual:%d" % (frame_rate, int(data[0]["rates"]["rates-rx-packets"])))
                        return False
        else:
            helpers.log("Given tenant name does not match the config")
            
    def rest_verify_tenant_tx_rates(self, tenant, frame_rate, vrange=5):
        ''' Function to verify the Tenant Tx stats
        Input: Tenant name , matching frame count , if required user can provide range as well for the frame count match
        Output: given Tenant counters will be showed and matched aginst the value
        '''
        t = test.Test()
        c = t.controller('master')
        frame_rate = int(frame_rate)
        vrange = int(vrange)
        url = '/api/v1/data/controller/applications/bvs/info/stats/tenant-stats/tenants[tenant-name="%s"]' % (tenant)
        c.rest.get(url)
        data = c.rest.content()
        if data[0]["tenant-name"] == tenant:
                    if (int(data[0]["rates"]["rates-tx-packets"]) >= (frame_rate - vrange)) and (int(data[0]["rates"]["rates-tx-packets"]) <= (frame_rate + vrange)):
                        helpers.log("Pass: Tenant Counters value Expected:%d, Actual:%d" % (frame_rate, int(data[0]["rates"]["rates-tx-packets"])))
                        return True
                    else:
                        helpers.test_failure("Tenant counter value does not match,Expected:%d,Actual:%d" % (frame_rate, int(data[0]["rates"]["rates-tx-packets"])))
                        return False
        else:
            helpers.log("Given tenant name does not match the config")
            
    def rest_verify_membership_port_count(self, count):
        ''' Function to verify the membership port count for each vns
        Input:  provide how many port counts user is expecting in each VNS
        Output: Function will go through each VNS and match the provided count (e.g , 1000 vns , 2 ports each)
        '''
        t = test.Test()
        c = t.controller('master')
        count = int(count)
        url = '/api/v1/data/controller/applications/bvs/info/endpoint-manager/vnses'
        c.rest.get(url)
        data = c.rest.content()
        for i in range(0,len(data)):
            if int(data[i]["num-ports"]) == count:
                helpers.log("Expected membership ports:%d are present in the each VNS" % count)
                return True
            else:
                helpers.test_failure("Expected membership ports are not present in VNS :%s" % data[i]["name"])
                return False

    def cli_show_interface(self, switch=None, intf=None):
        ''' Function to show interface using controller CLI
        Input: interface name , if not given default = None
        Output: Execute show inteface from CLI and verify the output is not empty.
        '''
        t = test.Test()
        c = t.controller('master')
        c.cli("show interface %s %s" % switch, intf)
        result = c.cli_content()
        return result
    
    def cli_show_switch(self, switch=None):
        ''' Function to show switch using controller CLI
        Input: switch name , if not given it will be none
        Output: Execute show switch from CLI and verify the output is not empty
        '''
        t = test.Test()
        c = t.controller('master')
        c.cli("show switch %s" % switch)
        result = c.cli_content()
        return result
    
    def cli_show_lag(self, switch=None, lag_name=None):
        ''' Function to show lag using controller CLI
        Input: switch and type of lag , Default= none
        Output: Execute show lag from CLI and verify the output is not empty
        '''
        t = test.Test()
        c = t.controller('master')
        c.cli("show lag %s %s" % switch, lag_name)
        result = c.cli_content()
        return result
    
    def cli_show_lacp(self, switch=None):
        ''' Function to show lacp using controller CLI
        Input: Switch , Default=None
        Output: Execute show lacp from CLI and verify the output is not empty
        '''
        t = test.Test()
        c = t.controller('master')
        c.cli("show lacp %s" % switch)
        result = c.cli_content()
        return result
    
    def cli_show_link(self):
        ''' Function to show link using controller CLI
        Input: None
        Output: Execute show link from CLI and verify the output is not empty
        '''
        t = test.Test()
        c = t.controller('master')
        c.cli("show link")
        result = c.cli_content()
        return result
   
