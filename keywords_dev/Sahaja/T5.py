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
###  Last Updated: 04/06/2014
###
###  WARNING !!!!!!!
'''

import autobot.helpers as helpers
import autobot.restclient as restclient
import autobot.test as test
import re
# import keywords.BsnCommon as BsnCommon
import SwitchLight as SwitchLight
from netaddr import *

# import sys
# sys.path.append('keywords_dev/Sahaja')
# from SwitchLight import parse_switch_op


class T5(object):

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
        url = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]' % (tenant)
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
            url = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]' % (tenant)
        else:
            # Show all tenant
            url = '/api/v1/data/controller/applications/bcf/tenant' % ()

        c.rest.get(url)
        helpers.log("Output: %s" % c.rest.result_json())

        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())

        data = c.rest.content()

        # If showing all tenant, then we don't need to check further
        if tenant is None:
            return data

        # Search list of tenant to find a match
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

        url = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]' % (tenant)
        try:
            c.rest.delete(url, {"name": tenant})
        except:
            return False
        else:
            return True

    def rest_delete_tenant_all(self):
        ''' delete all tenant in the system
        '''
        t = test.Test()
        c = t.controller('main')

        helpers.log("Entering ===> to delete all tenants")
        url_get_tenant = '/api/v1/data/controller/applications/bcf/info/endpoint-manager/tenant'
        try:
            c.rest.get(url_get_tenant)
            content = c.rest.content()
        except:
            pass
        else:
            if (content):
                for i in range (0, len(content)):
                    url_tenant_delete = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]' % content[i]['name']
                    c.rest.delete(url_tenant_delete, {})

        helpers.log("Exiting ===>   delete all tenants")
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

        url = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]/segment[name="%s"]' % (tenant, vns)
        try:
            c.rest.put(url, {"name": vns})
        except:
            return False
        else:
            return True

    def rest_add_vns_scale(self, tenant, count, name='v'):
        '''
        Functiont to add vns in scale
        Input: tenant , no of vns to be created,  the start leter of the name
        Output: system will created specified no of vns
        '''
        t = test.Test()
        c = t.controller('main')
        count = int(count)
        i = 1
        while (i <= count):
            vns = name
            vns += str(i)
            url = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]/segment[name="%s"]' % (tenant, vns)
            try:
                c.rest.put(url, {"name": vns})
            except:
                return False
            i = i + 1
        return True


    def rest_add_interface_to_all_vns(self, tenant, switch, intf, vlan=1):
        '''
        Function to add interface to all created vns
        Input: tennat , switch , interface
        output : will add specified interfaces into all vns in a tenant as tagged starting with 1
        '''
        t = test.Test()
        c = t.controller('main')
        url = '/api/v1/data/controller/applications/bcf/info/endpoint-manager/segment[tenant="%s"]' % (tenant)
        c.rest.get(url)
        data = c.rest.content()
        data.sort(key=lambda x: x['name'])
        helpers.log("USR INFO: data after sort is %s" % (data))
        i = 0
        while (i < len(data)):
            j = int(vlan) + i
            url = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]/segment[name="%s"]/switch-port-membership-rule[switch="%s"][interface="%s"]' % (tenant, data[i]["name"], switch, intf)
            c.rest.put(url, {"switch": switch, "interface": intf, "vlan": j})
            i = i + 1
        return True

    def rest_add_interface_any_to_all_vns(self, tenant, vlan='1'):
        '''
        Function to add interface any switch any to all created vns
        Input: tennat ,
        output : will add all interface to all created vns
        '''
        t = test.Test()
        c = t.controller('main')
        url = '/api/v1/data/controller/applications/bcf/info/endpoint-manager/segment[tenant="%s"]' % (tenant)
        c.rest.get(url)
        data = c.rest.content()

        for j in range(0, len(data)):
                i = int(vlan) + j
                helpers.log("vlan=%d, %d" % (i, j))
                url = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]/segment[name="%s"]/switch-port-membership-rule[switch="any"][interface="any"]' % (tenant, data[j]["name"])
                c.rest.put(url, {"interface": "any", "switch": "any", "vlan": i})
        return True

    def rest_delete_vns(self, tenant, vns=None):
        t = test.Test()
        c = t.controller('main')

        helpers.test_log("Input arguments: tenant = %s vns = %s" % (tenant, vns))

        url = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]/segment[name="%s"]' % (tenant, vns)
        try:
            c.rest.delete(url, {"name": vns})
        except:
            return False
        else:
            return True

    def rest_show_vns(self):
        t = test.Test()
        c = t.controller('main')

        url = '/api/v1/data/controller/applications/bcf/info/endpoint-manager/segment' % ()
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

        url = '/api/v1/data/controller/applications/bcf/port-group[name="%s"]' % (pg)

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

        url = '/api/v1/data/controller/applications/bcf/port-group[name="%s"]' % (pg)
        try:
            c.rest.delete(url, {"name": pg})
        except:
            return False
        else:
            return True

    def rest_delete_portgroup_all(self):
        ''' delete all port group config in the system
        '''
        t = test.Test()
        c = t.controller('main')

        helpers.log("Entering ===> to delete all port group")

        url = '/api/v1/data/controller/applications/bcf/info/fabric/port-group'
        try:
            c.rest.get(url)
            content = c.rest.content()
        except:
            pass
        else:
            if (content):
                for i in range (0, len(content)):
                    url_delete = '/api/v1/data/controller/applications/bcf/port-group[name="%s"]' % content[i]['name']
                    c.rest.delete(url_delete, {})

        helpers.log("Exiting ===>   delete all port group")
        return True



    def rest_add_endpoint(self, tenant, vns, endpoint):
        '''Add nexthop to ecmp groups aks gateway pool in tenant"

            Input:
                `tenant`          tenant name
                `vns`         vns name
                `endpoint`    endpoint name
            Return: true if configuration is successful, false otherwise
            http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/tenant[name="A"]/segment[name="A1"]/endpoint[name="H1"] {"name": "H1"}

        '''

        t = test.Test()
        c = t.controller('main')

        helpers.test_log("Input arguments: tenant = %s, vns = %s, endpoint = %s" % (tenant, vns, endpoint))

        url = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]/segment[name="%s"]/endpoint' % (tenant, vns)
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

        url = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]/segment[name="%s"]/endpoint[name="%s"]' % (tenant, vns, endpoint)
        try:
            c.rest.delete(url, {"name": endpoint})
        except:
            return False
        else:
            return True

    def rest_add_interface_to_portgroup(self, switch, intf, pg):
        t = test.Test()
        c = t.controller('main')

        helpers.test_log("Input arguments: switch = %s interface = %s port-group = %s" % (switch, intf, pg))

        url = '/api/v1/data/controller/applications/bcf/port-group[name="%s"]/member-interface[switch-name="%s"][interface-name="%s"]' % (pg, switch, intf)
        try:
            c.rest.put(url, {"switch-name": switch, "interface-name": intf})
        except:
            return False
        else:
            return True

    def rest_add_portgroup_lacp(self, pg):
        t = test.Test()
        c = t.controller('main')

        helpers.test_log("Input arguments: port-group = %s" % (pg))

        # url = '/api/v1/data/controller/fabric/port-group[name="%s"]' % (pg)
        url = '/api/v1/data/controller/applications/bcf/port-group[name="%s"]' % (pg)

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

        helpers.test_log("Input arguments: switch = %s interface = %s port-group = %s" % (switch, intf, pg))

        url = '/api/v1/data/controller/core/switch-config[name="%s"]/interface[name="%s"]' % (switch, intf)
        try:
            c.rest.delete(url, {"core/switch-config/interface/port-group": pg})
        except:
            return False
        else:
            return True

    def rest_add_portgroup_to_vns(self, tenant, vns, pg, vlan):
        t = test.Test()
        c = t.controller('main')

        helpers.test_log("Input arguments: tenant = %s vns = %s port-group = %s vlan = %s" % (tenant, vns, pg, vlan))

        url = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]/segment[name="%s"]/port-group-membership-rule[port-group="%s"]' % (tenant, vns, pg)

        try:
            c.rest.put(url, {"vlan": vlan, "port-group": pg})
        except:
            return False
        else:
            return True

    def rest_add_switch_endpoint_to_vns(self, tenant, vns, endpoint, vlan, switch, switch_if):
        t = test.Test()
        c = t.controller('main')

        helpers.test_log("Input arguments: tenant = %s vns = %s endpoint = %s vlan = %s switch = %s switch_if = %s" % (tenant, vns, endpoint, vlan, switch, switch_if))

        # url = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]/segment[name="%s"]/port-group-membership-rule[port-group="%s"]' % (tenant, vns, pg)
        url = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]/segment[name="%s"]/endpoint[name="%s"]/attachment-point' % (tenant, vns, endpoint)

        try:
            c.rest.patch(url, {"interface": switch_if, "switch": switch, "vlan": vlan})
        except:
            return False
        else:
            return True


    def rest_add_portgroup_to_endpoint(self, tenant, vns, endpoint, pg, vlan):
        t = test.Test()
        c = t.controller('main')

        helpers.test_log("Input arguments: tenant = %s vns = %s endpoint = %s port-group = %s vlan = %s" % (tenant, vns, endpoint, pg, vlan))

        url = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]/segment[name="%s"]/endpoint[name="%s"]/attachment-point' % (tenant, vns, endpoint)
        try:
            c.rest.put(url, {"port-group": pg, "vlan": vlan})
        except:
            return False
        else:
            return True

    def rest_delete_portgroup_from_vns(self, tenant, vns, pg, vlan):
        t = test.Test()
        c = t.controller('main')

        helpers.test_log("Input arguments: tenant = %s vns = %s port-group = %s vlan = %s" % (tenant, vns, pg, vlan))

        url = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]/segment[name="%s"]/port-group-membership-rule[port-group="%s"]' % (tenant, vns, pg)
        try:
            c.rest.delete(url, {"vlan": vlan})
        except:
            return False
        else:
            return True

    def rest_add_interface_to_vns(self, tenant, vns, switch, intf, vlan, rest_type="put"):
        t = test.Test()
        c = t.controller('main')

        helpers.test_log("Input arguments: tenant = %s vns = %s switch = %s interface = %s vlan = %s" % (tenant, vns, switch, intf, vlan))

        url = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]/segment[name="%s"]/switch-port-membership-rule[switch="%s"][interface="%s"]' % (tenant, vns, switch, intf)
        try:
            if rest_type == "patch":
                c.rest.patch(url, {"switch": switch, "interface": intf, "vlan": vlan})
            else:
                c.rest.put(url, {"switch": switch, "interface": intf, "vlan": vlan})
        except:
            return False
        else:
            return True

    def rest_delete_interface_from_vns(self, tenant, vns, switch, intf, vlan):
        t = test.Test()
        c = t.controller('main')

        helpers.test_log("Input arguments: tenant = %s vns = %s switch = %s interface = %s vlan = %s" % (tenant, vns, switch, intf, vlan))

        url = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]/segment[name="%s"]/switch-port-membership-rule[switch="%s"][interface="%s"]' % (tenant, vns, switch, intf)
        try:
            c.rest.delete(url, {"vlan": vlan})
        except:
            return False
        else:
            return True

    def rest_add_interface_to_endpoint(self, tenant, vns, endpoint, switch, intf, vlan):
        t = test.Test()
        c = t.controller('main')

        helpers.test_log("Input arguments: tenant = %s vns = %s endpoint = %s switch = %s interface = %s vlan = %s" % (tenant, vns, endpoint, switch, intf, vlan))

        url = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]/segment[name="%s"]/endpoint[name="%s"]/attachment-point' % (tenant, vns, endpoint)
        try:
            c.rest.put(url, {"switch": switch, "interface": intf, "vlan": vlan})
        except:
            return False
        else:
            return True

    def rest_add_ip_endpoint(self, tenant, vns, endpoint, ip):
        t = test.Test()
        c = t.controller('main')
        url = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]/segment[name="%s"]/endpoint[name="%s"]' % (tenant, vns, endpoint)
        try:
            c.rest.patch(url, {"ip-address": ip})
        except:
            return False
        else:
            return True

    def rest_add_mac_endpoint(self, tenant, vns, endpoint, mac):
        t = test.Test()
        c = t.controller('main')
        url = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]/segment[name="%s"]/endpoint[name="%s"]' % (tenant, vns, endpoint)
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
        url = '/api/v1/data/controller/applications/bcf/info/endpoint-manager/segment' % ()
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
                        helpers.log("No VNS are present")
                        return True

    def rest_verify_vns_scale(self, tenant, count):
        '''Verify VNS information for scale

            Input:  No of vns expected to be created

            Return: true if it matches the added VNS (string starts with "v")
        '''
        t = test.Test()
        c = t.controller('main')
        url = '/api/v1/data/controller/applications/bcf/info/endpoint-manager/segment[tenant="%s"]' % tenant
        c.rest.get(url)
        data = c.rest.content()
        if len(data) == int(count):
            for i in range(0, len(data)):
                if (int(data[i]["internal-vlan"]) == 0):
                    helpers.test_failure("Expected VNS's are not present in the config")
                    return False
        else:
                helpers.test_failure("Fail: expected:%s, Actual:%s" % (int(count), len(data)))
                return False
        return True

    def rest_verify_tenant(self):
        '''Verify CLI tenant information

            Input:   None

            Return: true if it matches the added tenant (string starts with "t")
        '''
        t = test.Test()
        c = t.controller('main')
        url = '/api/v1/data/controller/applications/bcf/info/endpoint-manager/tenant' % ()
        c.rest.get(url)
        data = c.rest.content()
        for i in range(0, len(data)):
                if len(data) != 0:
                    match = re.search('^t.*', data[i]["name"])
                    tenant = match.group(0)
                    helpers.log("tenant=%s" % tenant)
                    if str(data[i]["name"]) == tenant:
                        helpers.log("Expected tenant are present in the config")
                        return True
                    else:
                        helpers.test_log("Expected tenant are not present in the config")
                        return False
                else:
                        helpers.log("No tenant are added")
                        return False

    def rest_verify_specific_tenant(self, tenant):
        '''Verify Speicifc tenant in BCF controller

            Input:   Name of tenant to be expected

            Return: true if it matches the added tenant
        '''
        t = test.Test()
        c = t.controller('main')
        url = '/api/v1/data/controller/applications/bcf/info/endpoint-manager/tenant[name="%s"]' % tenant
        c.rest.get(url)
        data = c.rest.content()
        if str(data[0]["name"]) == tenant:
            helpers.log("Expected tenant are present in the config")
            return True
        else:
            helpers.test_log("Expected tenant are not present in the config")
            return False

    def rest_verify_endpoint(self, vns, vlan, mac, switch, intf):
        '''Verify Dynamic Endpoint entry

            Input: vns name , vlan ID , mac , switch name, expected switch interface

            Return: true if it matches Value specified
        '''
        t = test.Test()
        c = t.controller('main')
        url = '/api/v1/data/controller/applications/bcf/info/endpoint-manager/endpoint' % ()
        c.rest.get(url)
        data = c.rest.content()
        attach_point = switch + "|" + intf
        if len(data) != 0:
                for i in range(0, len(data)):
                    if str(data[i]["segment"]) == vns:
                        if str(data[i]["vlan"]) == str(vlan):
                            if (data[i]["mac"] == str(mac)) :
                                if (data[i]["attachment-point"] == attach_point) :
                                        helpers.log("Expected endpoint are added data matches is %s" % data[i]["mac"])
                                        return True
                                else:
                                        helpers.test_failure("Expected endpoint %s are not added" % (str(mac)))
                                        return False
        else:
            return False





    def rest_verify_endpoint_state(self, mac, state):
        '''Verify Dynamic Endpoint entry

            Input: mac, vlan , states (Valid states are: learned , unknown)

            Return: true if it matches Value specified
        '''
        t = test.Test()
        c = t.controller('main')
        url = '/api/v1/data/controller/applications/bcf/info/endpoint-manager/endpoint[mac="%s"]' % (mac)
        c.rest.get(url)
        data = c.rest.content()
        if data[0]["mac"] == mac:
            if str(data[0]["attachment-point-state"]) == "learned":
                helpers.log("Expected endpoint states are showing learned")
                return True
            elif str(data[0]["attachment-point-state"]) == "unknown":
                helpers.log("Expected endpoint states are unknown")
                return True
            else:
                helpers.test_failure("Expected endpoint state is not known to the system")
                return False
        else:
            helpers.log("Given mac address not known to the system MAC=%s" % mac)
            return False

    def rest_verify_endpoint_ip_state(self, tenant, segment, ip, mac, vlan, state):
        '''Verify Dynamic Endpoint entry ip state

            Input: ip, vlan , states (Valid states are: learned , unknown)

            Return: true if it matches Value specified
        '''
        t = test.Test()
        c = t.controller('main')
        url = '/api/v1/data/controller/applications/bcf/info/endpoint-manager/endpoint[mac="%s"]' % (mac)
        c.rest.get(url)
        data = c.rest.content()
        if data[0]["segment"] == segment and data[0]["tenant"] == tenant:
            if data[0]["mac"] == mac and data[0]["vlan"] == vlan:
                for i in range(0, len(data[0]["ip-address"])):
                    if str(data[0]["ip-address"][i]["ip-address"]) == str(ip) and str(data[0]["ip-address"][i]["ip-state"]) == "learned":
                        helpers.log("Expected endpoint states are showing learned")
                        return True
                    else:
                        continue
            else:
                helpers.log("Given mac address not known to the system MAC=%s" % mac)
                return False
        else:
            helpers.log("Given segment does not match in the controller")
            return False

    def rest_verify_endpoint_static(self, tenant, vns, vlan, mac):
        '''Verify Static Endpoint entry

            Input: vns name , vlan ID , mac , switch name, expected switch interface

            Return: true if it matches Value specified and added attachment point is true
         '''
        t = test.Test()
        c = t.controller('main')
        url = '/api/v1/data/controller/applications/bcf/info/endpoint-manager/endpoint[mac="%s"]' % (mac)
        c.rest.get(url)
        data = c.rest.content()
        if str(data[0]["segment"]) == str(vns) and data[0]["mac"] == mac and int(data[0]["vlan"]) == int(vlan) and data[0]["tenant"] == tenant:
            if str(data[0]["attachment-point-state"]) == "static":
                if str(data[0]["state"]) == "L2 Only":
                    helpers.log("static endpoint state is proper")
                    return True
                else:
                    helpers.log("static endpoint state is down")
                    return False

        helpers.test_log("Given static endpoints are not present in the config")
        return False

    def rest_verify_endpoint_static_exists_down(self, tenant, vns, vlan, mac):
        '''Verify Static Endpoint entry

            example show command: show endpoint mac 00:00:00:00:00:01

            Input: vns name , vlan ID , mac , switch name, expected switch interface

            Return: true if it matches Value specified and added attachment point is true
         '''
        t = test.Test()
        c = t.controller('main')
        url = '/api/v1/data/controller/applications/bcf/info/endpoint-manager/endpoint[mac="%s"]' % (mac)
        c.rest.get(url)
        data = c.rest.content()
        if len(data) == 1:
            if str(data[0]["segment"]) == str(vns) and data[0]["mac"] == mac and int(data[0]["vlan"]) == int(vlan) and data[0]["tenant"] == tenant:
                if str(data[0]["attachment-point-state"]) == "static":
                    if str(data[0]["state"]) == "Attach Point Down":
                        helpers.log("static endpoint state is down which is expected")
                        return True
                    else:
                        helpers.log("static endpoint state is %s which is not what we expected" % (data[0]["state"]))
                        return False

            helpers.test_log("Given static endpoints are not present in the config")
            return False
        else:
            helpers.test_log("There are more entries for a given mac")
            return False


    def rest_verify_switch_l2_table(self, switch, mac, Val_exists=True):
        ''' Verify that the mac exists/does not exist as per test

        example show command: show forwarding switch leaf0a l2-table | grep 00:00:00:00:00:01

        Input: switch name, mac, exists

        Return: true if mac exists or not according to the test
        '''
        t = test.Test()
        c = t.controller('main')
        url = '/api/v1/data/controller/applications/bcf/info/forwarding/network/switch[switch-name="%s"]/l2-table' % (switch)
        c.rest.get(url)
        data = c.rest.content()
        helpers.log("exists value got is %s" % (Val_exists))
        if Val_exists is False:
            helpers.log("Entered the first if loop as exists value is as before")
            if len(data) == 0:
                helpers.log("There are no mac entries for given switch which is expected")
                return True
            else:
                helpers.log("There are some entries for given switch")
                return False
        else:
            helpers.log("Entered the first else loop as exists value is %s" % (Val_exists))
            if mac in data:
                 helpers.log("Expected mac exists in the l2 forwarding table")
                 return True
            else:
                helpers.test_log("Expected does not exist in the l2 table")
                return False




    def rest_verify_endpoint_portgroup(self, vns, vlan, mac, pg):
        '''Verify Dynamic Endpoint entry

            Input: vns name , vlan ID , mac , portgroup name

            Return: true if it matches Value specified
        '''
        t = test.Test()
        c = t.controller('main')
        url = '/api/v1/data/controller/applications/bcf/info/endpoint-manager/endpoint' % ()
        c.rest.get(url)
        data = c.rest.content()
        if len(data) != 0:
            for i in range(0, len(data)):
                if str(data[i]["segment"]) == vns:
                    if str(data[i]["attachment-point"]["vlan"]) == str(vlan):
                        if (data[i]["mac"] == str(mac)) :
                            if (data[i]["attachment-point"]["port-group"] == pg) :
                                helpers.log("Expected endpoint are added data matches is %s" % data[i]["mac"])
                                return True
                            else:
                                helpers.test_failure("Expected endpoint %s are not added" % (str(mac)))
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
        url = '/api/v1/data/controller/applications/bcf/info/endpoint-manager/endpoint' % ()
        c.rest.get(url)
        data = c.rest.content()
        if len(data) != 0:
                for i in range(0, len(data)):
                    if str(data[i]["segment"]) == vns:
                        if str(data[i]["attachment-point"]["vlan"]) == str(vlan):
                            if (data[i]["mac"] == str(mac)) :
                                if (data[i]["attachment-point"]["port-group"] == pg) :
                                    if (data[i]["configured-endpoint"] == True) :
                                        helpers.log("Expected endpoint are added data matches is %s" % data[i]["mac"])
                                        return True
                                    else:
                                        helpers.test_failure("Expected endpoint %s are not added" % (str(mac)))
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
        url = '/api/v1/data/controller/applications/bcf/info/endpoint-manager/segment[name="%s"]' % (vns)
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
        url = '/api/v1/data/controller/applications/bcf/info/forwarding/network/switch[switch-name="%s"]/vlan-table' % (switch)
        c.rest.get(url)
        data = c.rest.content()
        no_of_vlans = len(data)
        no_of_user_vlan = int(no_of_vlans) - 1
        url1 = '/api/v1/data/controller/applications/bcf/info/endpoint-manager/segment' % ()
        c.rest.get(url1)
        data1 = c.rest.content()
        no_of_vns = len(data1)
        if (int(no_of_vns) == int(no_of_user_vlan)):
                helpers.log("Vlan Entries are present in forwarding table Actual:%d = Expected:%d" % (int(no_of_vns), int(no_of_user_vlan)))
                return True
        else:
                helpers.test_log("Vlan Entries are inconsistent in forwarding table %d = %d" % (int(no_of_vns), int(no_of_user_vlan)))
                return False

    def rest_verify_forwarding_port(self, switch):
        '''Verify Edge port  Information in Controller Forwarding Table

            Input:  switch name

            Return: port table with associated Lag id will be provided
        '''
        t = test.Test()
        c = t.controller('main')
        url = '/api/v1/data/controller/applications/bcf/info/forwarding/network/switch[switch-name="%s"]/port-table' % (switch)
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
        url = '/api/v1/data/controller/applications/bcf/info/forwarding/network/switch[switch-name="%s"]/port-table' % (switch)
        c.rest.get(url)
        data = c.rest.content()
        interface = re.sub("\D", "", intf)
        lag_id = []
        for i in range(0, len(data)):
            if str(data[i]["port-num"]) == str(interface):
                lag_id.append(data[i]["lag-id"])
            else:
                continue
        url1 = '/api/v1/data/controller/applications/bcf/info/forwarding/network/switch[switch-name="%s"]/vlan-xlate-table' % (switch)
        c.rest.get(url1)
        data1 = c.rest.content()
        for i in range(0, len(data1)):
            if str(data1[i]["in-port-group"]) == str(interface):
                if str(data1[i]["vlan-id"]) == str(vlan):
                    helpers.log("Vlan Translation table is creaetd properly for the given interface")
                    return True
            else:
                continue
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
        url1 = '/api/v1/data/controller/applications/bcf/info/forwarding/network/switch[switch-name="%s"]/vlan-member-table' % (switch)
        c.rest.get(url1)
        data1 = c.rest.content()
        for i in range(0, len(data1)):
                list_common = list(set(list_fabric_interface).intersection(set(data1[i]["tagged-port"])))
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
        url = '/api/v1/data/controller/applications/bcf/info/forwarding/network/switch[switch-name="%s"]/vlan-member-table' % (switch)
        c.rest.get(url)
        data = c.rest.content()
        interface = re.sub("\D", "", intf)
        for i in range(0, len(data)):
            try:
                value = data[i]["untagged-port"]
            except KeyError:
                continue
            if str(interface) in data[i]["untagged-port"]:
                        helpers.log("Pass:Given interface is present in untag memberlist of vlan-member-table")
                        return True
            else:
                continue
        return False

    def rest_verify_forwarding_vlan_edge_tag_members(self, switch, intf):
        '''Verify Fabric edge interfaces status in a vlan

            Input:  Specific switch name and specific edge interfaces

            Return: return True or False depends on the edge port present as Tagged in a vlan
        '''
        t = test.Test()
        c = t.controller('main')
        url = '/api/v1/data/controller/applications/bcf/info/forwarding/network/switch[switch-name="%s"]/vlan-member-table' % (switch)
        c.rest.get(url)
        data = c.rest.content()
        interface = re.sub("\D", "", intf)
        for i in range(0, len(data)):
            try:
                value = data[i]["tagged-port"]
            except KeyError:
                continue
            if interface in data[i]["tagged-port"]:
                    helpers.log("Pass:Given interface is present in tag memberlist of vlan-table")
                    return True
            else:
                continue
        return False

    def rest_verify_forwarding_layer2_table_untag(self, switch, intf, mac):
        '''Verify Layer 2 MAC information in forwarding table

            Input:  Specific switch name , interface , mac

            Return: True or false based on the entry present in the forwarding table.
        '''
        t = test.Test()
        c = t.controller('main')
        # Get the Lag id for the Given interface
        url = '/api/v1/data/controller/applications/bcf/info/forwarding/network/switch[switch-name="%s"]/port-table' % (switch)
        c.rest.get(url)
        data = c.rest.content()
        interface = re.sub("\D", "", intf)
        lag_id = []
        for i in range(0, len(data)):
            if str(data[i]["port-num"]) == str(interface):
                lag_id.append(data[i]["lag-id"])
                # Get the vlan-id for the given interface
            else:
                continue
        url1 = '/api/v1/data/controller/applications/bcf/info/forwarding/network/switch[switch-name="%s"]/vlan-member-table' % (switch)
        c.rest.get(url1)
        data1 = c.rest.content()
        vlan_id = []
        for i in range(0, len(data1)):
            try:
                    if str(interface) in (data1[i]["untagged-port"]):
                        vlan_id.append(data1[i]["vlan-id"])
            except (KeyError):
                continue
                    # Match the mac in forwarding table with specific lag_id and vlan_id
        url3 = '/api/v1/data/controller/applications/bcf/info/forwarding/network/switch[switch-name="%s"]/l2-table' % (switch)
        c.rest.get(url3)
        data2 = c.rest.content()
        for i in range(0, len(data2)):
            if str(data2[i]["mac"]) == str(mac):
                if data2[i]["port-num"] in lag_id and data2[i]["vlan-id"] in vlan_id:
                    helpers.log("Pass: Expected mac is present in the forwarding table with correct vlan and interface")
                    return True
                else:
                    helpers.log("Fail: Expected mac is not present in forwarding table with correct vlan and interface")
            else:
                continue

        return False

    def rest_verify_forwarding_layer2_table_tag(self, switch, intf, mac):
        '''Verify Layer 2 MAC information in forwarding table

            Input:  Specific switch name , interface , mac

            Return: True or false based on the entry present in the forwarding table.
        '''
        t = test.Test()
        c = t.controller('main')
        # Get the Lag id for the Given interface
        url = '/api/v1/data/controller/applications/bcf/info/forwarding/network/switch[switch-name="%s"]/port-table' % (switch)
        c.rest.get(url)
        data = c.rest.content()
        interface = re.sub("\D", "", intf)
        lag_id = []
        for i in range(0, len(data)):
            if str(data[i]["port-num"]) == str(interface):
                lag_id.append(data[i]["lag-id"])
                # Get the vlan-id for the given interface
            else:
                continue
        url1 = '/api/v1/data/controller/applications/bcf/info/forwarding/network/switch[switch-name="%s"]/vlan-member-table' % (switch)
        c.rest.get(url1)
        data1 = c.rest.content()
        vlan_id = []
        for i in range(0, len(data1)):
            try:
                value = data1[i]["tagged-port"]
            except KeyError:
                continue
                if str(interface) in data1[i]["tagged-port"]:
                    vlan_id.append(data1[i]["vlan-id"])
                    # Match the mac in forwarding table with specific lag_id and vlan_id
                else:
                    continue
        url3 = '/api/v1/data/controller/applications/bcf/info/forwarding/network/switch[switch-name="%s"]/l2-table' % (switch)
        c.rest.get(url3)
        data2 = c.rest.content()
        for i in range(0, len(data2)):
            if str(data2[i]["mac"]) == str(mac):
                if data2[i]["port-num"] in lag_id and data2[i]["vlan-id"] in vlan_id:
                    helpers.log("Pass: Expected mac is present in the forwarding table with correct vlan and interface")
                    return True
                else:
                    helpers.log("Fail:Expected mac is not present in the forwarding table with correct vlan and interface")
                    return False
            else:
                continue

        return False

    def rest_add_endpoint_scale(self, tenant, vns, mac, endpoint, switch, intf, vlan, count, quiet=1):
        ''' Adding static endpoint in a scale
            Input: tenant , vns , switch , interface , vlan , count (how many static endpoint), starting letter for the endpoint name
            Output: Static creation of endpoint in a given tenant and vns with switch/interface
        '''
        t = test.Test()
        c = t.controller('main')
        i = 1
        while (i <= int(count)):
            endpoint_new = "%s_%d" % (endpoint, i)
            mac = EUI(mac).value
            mac = "{0}".format(str(EUI(mac + i)).replace('-', ':'))
            url = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]/segment[name="%s"]/endpoint' % (tenant, vns)
            c.rest.post(url, {"name": endpoint_new}, quiet=quiet)
            url1 = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]/segment[name="%s"]/endpoint[name="%s"]/attachment-point' % (tenant, vns, endpoint_new)
            c.rest.put(url1, {"switch": switch, "interface": intf, "vlan": vlan}, quiet=quiet)
            url2 = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]/segment[name="%s"]/endpoint[name="%s"]' % (tenant, vns, endpoint_new)
            c.rest.patch(url2, {"mac": mac}, quiet=quiet)
            i = i + 1
        return True

    def rest_verify_endpoints_in_vns(self, vns, count, quiet=0):
        ''' Function to count no of endoint in the given VNS
         Input : Expected Count and vns
         Output: No of endoints match aginst the specifed count in vns table
        '''
        t = test.Test()
        c = t.controller('main')
        url = '/api/v1/data/controller/applications/bcf/info/endpoint-manager/segment[name="%s"]' % (vns)
        c.rest.get(url, quiet=quiet)
        data = c.rest.content()
        if data[0]["endpoint-count"] == int(count):
            helpers.log("Pass:Expected:%s, Actual:%s" % (int(count), data[0]["endpoint-count"]))
            return True
        else:
            helpers.test_failure("Fail: Expected:%s is not equal to Actual:%s" % (int(count), data[0]["endpoint-count"]))
            return False

    def rest_verify_endpoint_in_system(self, count):
        ''' Function to count no of endoint in the system
         Input : Expected Count
         Output: No of endoints match aginst the specifed count in endpoint table
        '''
        t = test.Test()
        c = t.controller('main')
        url = '/api/v1/data/controller/applications/bcf/info/endpoint-manager/endpoint' % ()
        c.rest.get(url)
        data = c.rest.content()
        if int(len(data)) == int(count):
            helpers.log("Pass:Expected:%s, Actual:%s" % (int(count), len(data)))
            return True
        else:
            helpers.test_failure("Fail: Expected:%s is not equal to Actual:%s" % (int(count), len(data)))
            return False


    def rest_clear_vns_stats(self, vns=None):
        ''' Function to clear the VNS stats
        Input: vns name
        Output: given vns counters will be cleared
        '''
        t = test.Test()
        c = t.controller('main')
        if vns is None or vns is "all":
            url = '/api/v1/data/controller/applications/bcf/info/statistic/segment-counter'
        else:
            url = '/api/v1/data/controller/applications/bcf/info/statistic/segment-counter[name="%s"]' % vns
        c.rest.delete(url, {})
        return True

    def rest_verify_vns_rx_stats(self, tenant, vns, frame_cnt, vrange=5):
        ''' Function to verify the VNS stats
        Input: vns name
        Output: given vns counters will be showed
        '''
        t = test.Test()
        c = t.controller('main')
        frame_cnt = int(frame_cnt)
        vrange = int(vrange)
        url = '/api/v1/data/controller/applications/bcf/info/statistic/segment-counter[name="%s"][tenant-name="%s"]' % (vns, tenant)
        c.rest.get(url)
        data = c.rest.content()
        if data[0]["tenant-name"] == tenant and data[0]["name"] == vns:
                    if (int(data[0]["counter"]["rx-packet"]) >= (frame_cnt - vrange)) and (int(data[0]["counter"]["rx-packet"]) <= (frame_cnt + vrange)):
                        helpers.log("Pass: Counters value Expected:%d, Actual:%d" % (frame_cnt, int(data[0]["counter"]["rx-packet"])))
                        return True
                    else:
                        helpers.test_failure("Vns counter value does not match,Expected:%d,Actual:%d" % (frame_cnt, int(data[0]["counter"]["rx-packet"])))
                        return False
        else:
            helpers.log("Given tenant name and VNS name does not match the config")

    def rest_verify_vns_rx_rates(self, tenant, vns, frame_rate, vrange=100):
        ''' Function to verify the VNS incoming rates
        Input: vns name
        Output: given vns rates will be displayed and match against the expected rate
        '''
        t = test.Test()
        c = t.controller('main')
        url = '/api/v1/data/controller/applications/bcf/info/statistic/segment-rate[name="%s"][tenant-name="%s"]' % (vns, tenant)
        frame_rate = int(frame_rate)
        vrange = int(vrange)
        try:
            c.rest.get(url)
        except:
            return False
        data = c.rest.content()
        if data[0]["tenant-name"] == tenant and data[0]["name"] == vns:
            if (int(data[0]["rate"][0]["rx-packet-rate"]) >= (frame_rate - vrange)) and (int(data[0]["rate"][0]["rx-packet-rate"]) <= (frame_rate + vrange)):
                helpers.log("Pass: Rate value Expected:%d, Actual:%d" % (frame_rate, int(data[0]["rate"][0]["rx-packet-rate"])))
                return True
            else:
                helpers.test_failure("Vns rate value does not match,Expected:%d,Actual:%d" % (frame_rate, int(data[0]["rate"][0]["rx-packet-rate"])))
                return False
        else:
            helpers.log("Given tenant name and vns name does not match in the config")

    def rest_verify_vns_tx_stats(self, tenant, vns, frame_cnt, vrange=5):
        ''' Function to verify the VNS stats
        Input: vns name
        Output: given vns counters will be showed
        '''
        t = test.Test()
        c = t.controller('main')
        frame_cnt = int(frame_cnt)
        vrange = int(vrange)
        url = '/api/v1/data/controller/applications/bcf/info/statistic/segment-counter[name="%s"][tenant-name="%s"]' % (vns, tenant)
        c.rest.get(url)
        data = c.rest.content()
        if data[0]["tenant-name"] == tenant and data[0]["name"] == vns:
                    if (int(data[0]["counter"]["tx-packet"]) >= (frame_cnt - vrange)) and (int(data[0]["counter"]["tx-packet"]) <= (frame_cnt + vrange)):
                        helpers.log("Pass: Counters value Expected:%d, Actual:%d" % (frame_cnt, int(data[0]["counter"]["tx-packet"])))
                        return True
                    else:
                        helpers.test_failure("vns counters does not match, Expected:%d,Actual:%d" % (frame_cnt, int(data[0]["counter"]["tx-packet"])))
                        return False
        else:
            helpers.log("Given tenant name and VNS name does not match the config")

    def rest_verify_vns_tx_rates(self, tenant, vns, frame_rate, vrange=100):
        ''' Function to verify the VNS incoming rates
        Input: vns name
        Output: given vns rates will be displayed and match against the expected rate
        '''
        t = test.Test()
        c = t.controller('main')
        url = '/api/v1/data/controller/applications/bcf/info/statistic/segment-rate[name="%s"][tenant-name="%s"]' % (vns, tenant)
        frame_rate = int(frame_rate)
        vrange = int(vrange)
        c.rest.get(url)
        data = c.rest.content()
        if data[0]["tenant-name"] == tenant and data[0]["name"] == vns:
            if (int(data[0]["rate"][0]["tx-packet-rate"]) >= (frame_rate - vrange)) and (int(data[0]["rate"][0]["tx-packet-rate"]) <= (frame_rate + vrange)):
                helpers.log("Pass: Rate value Expected:%d, Actual:%d" % (frame_rate, int(data[0]["rate"][0]["tx-packet-rate"])))
                return True
            else:
                helpers.test_failure("vns rates does not match, Expected:%d,Actual:%d" % (frame_rate, int(data[0]["rate"][0]["tx-packet-rate"])))
                return False
        else:
            helpers.log("Given tenant name and vns name does not match in the config")

    def rest_clear_fabric_interface_stats(self):
        ''' Function to clear all the fabric interefaces
        Input: None
        Output: All connected switch interfaces will be cleared
        DELETE http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/info/statistic/interface-counter/interface {}  --- Aug 20

        '''
        t = test.Test()
        c = t.controller('main')

        # url = '/api/v1/data/controller/applications/bcf/info/stats/interface/stats/interface'
        url = '/api/v1/data/controller/applications/bcf/info/statistic/interface-counter/interface'
        c.rest.delete(url, {})

    def rest_show_fabric_switch(self):
        '''Return the list of connected switches

            Returns: gives list of connected switches
        '''
        t = test.Test()
        c = t.controller('main')
        url = '/api/v1/data/controller/applications/bcf/info/fabric/switch' % ()
        c.rest.get(url)

        return True

    def rest_show_fabric_link(self):
        '''Return the list of fabric links

            Returns: Print the Total fabric links
        '''
        t = test.Test()
        c = t.controller('main')

        url = '/api/v1/data/controller/applications/bcf/info/fabric?select=link' % ()
        c.rest.get(url)

        return True

    def rest_add_switch(self, switch):
        '''add the fabric switch

            Input:
                    switch        Name of the switch

            Returns: add the fabric switch
        '''
        if helpers.bigrobot_test_ztn().lower() == 'true':
            helpers.log("ZTN is enabled , should not be adding switch again..")
            return True
        t = test.Test()
        c = t.controller('main')

        url = '/api/v1/data/controller/core/switch-config[name="%s"]' % (switch)
        try:
            c.rest.put(url, {"name": switch})
        except:
            helpers.log("Error: Invalid argument: syntax: expected [a-zA-Z][-.0-9a-zA-Z_]*$ for: %s" % (switch))
            return False
        else:
            return True

    def rest_add_dpid(self, switch, dpid):
        if helpers.bigrobot_test_ztn().lower() == 'true':
            helpers.log("ZTN is enabled , should not be adding switch again..")
            return True
        t = test.Test()
        c = t.controller('main')

        url = '/api/v1/data/controller/core/switch-config[name="%s"]' % (switch)
        try:
            c.rest.patch(url, {"dpid": dpid})
        except:
            helpers.log("Error: Invalid argument: Invalid switch id (8-hex bytes): %s; switch %s doesn't exist" % (dpid, switch))
            return False
        else:
            return True

    def rest_add_fabric_role(self, switch, role):
        if helpers.bigrobot_test_ztn().lower() == 'true':
            helpers.log("ZTN is enabled , should not be adding switch again..")
            return True

        t = test.Test()
        c = t.controller('main')

        url = '/api/v1/data/controller/core/switch-config[name="%s"]' % (switch)
        try:
            c.rest.patch(url, {"fabric-role": role})
        except:
            return False
        else:
            return True

    def rest_add_leaf_group(self, switch, group):
        if helpers.bigrobot_test_ztn().lower() == 'true':
            helpers.log("ZTN is enabled , should not be adding switch again..")
            return True
        t = test.Test()
        c = t.controller('main')

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
        if helpers.bigrobot_test_ztn().lower() == 'true':
            helpers.log("ZTN is enabled , should not be adding switch again..")
            return True
        t = test.Test()
        c = t.controller('main')
        url = '/api/v1/data/controller/core/switch-config[name="%s"]/leaf-group' % (switch)
        try:
            c.rest.delete(url, {"leaf-group": None})
        except:
            return False
        else:
            return True

    def rest_delete_fabric_switch(self, switch=None):
        if helpers.bigrobot_test_ztn().lower() == 'true':
            helpers.log("ZTN is enabled , should not be deleting switch again..")
            return True
        t = test.Test()
        c = t.controller('main')

        url = '/api/v1/data/controller/core/switch-config[name="%s"]' % (switch)
        try:
            c.rest.delete(url, {"name": switch})
        except:
            return False
        else:
            return True

    def rest_verify_fabric_switch_all(self):
        t = test.Test()
        c = t.controller('main')
        url1 = '/api/v1/data/controller/applications/bcf/info/fabric/switch' % ()
        c.rest.get(url1)
        data = c.rest.content()
        for i in range (0, len(data)):
            if (data[i]["fabric-connection-state"] == "suspended") and (data[i]["fabric-role"] == "leaf" or data[i]["fabric-role"] == "spine"):
                helpers.test_failure("Fabric manager status is incorrect")
        helpers.log("Fabric manager status is correct")
        return True

    def rest_verify_fabric_link_after_switch_removal(self, switch):
        t = test.Test()
        c = t.controller('main')
        url = '/api/v1/data/controller/applications/bcf/info/fabric?select=link' % ()
        c.rest.get(url)
        data = c.rest.content()
        for i in range (0, len(data)):
            if data[i]["link"]["dst"]["switch-info"]["switch"] == switch and data[i]["link"]["link-direction"] == "bidirectional":
                helpers.test_failure("%s Fabric Links not deleted" % str(data[i]["link"]["dst"]["switch-info"]["switch"]))
                break

        return True

    def rest_verify_fabric_link_common(self, count=16):
        '''
        Function to count the no of bi-directional links present in dual leaf three rack topology
        input: No of links expected (default is 16 in dual leaf , three rack regression topology)
        Output: True or False
        '''
        t = test.Test()
        c = t.controller('main')
        url = '/api/v1/data/controller/applications/bcf/info/fabric?select=link' % ()
        c.rest.get(url)
        data = c.rest.content()
        link = 0
        for i in range (0, len(data[0]["link"])):
            if data[0]["link"][i]["link-direction"] == "bidirectional":
                link = link + 1
        if int(link) == int(count):
            helpers.test_log("Expected links are present,expected:%d,Actual:%d" % (int(count), int(link)))
            return True
        else:
            helpers.test_failure("Expected links are not present, expected:%d,Actual:%d" % (int(count), int(link)))
            return False

    def rest_verify_fabric_switch_role(self, dpid, role):
        t = test.Test()
        c = t.controller('main')
        url = '/api/v1/data/controller/applications/bcf/info/fabric/switch'
        c.rest.get(url)
        data = c.rest.content()
        status = False
        for i in range (0, len(data)):
            helpers.log("Checking switch dpid in controller...")
            try:
                if data[i]["dpid"] == dpid.lower() and data[i]["fabric-role"] == role.lower():
                    helpers.test_log("Fabric switch Role of %s is %s" % (str(data[i]["dpid"]), str(data[i]["fabric-role"])))
                    status = True
                    return True
            except KeyError:
                if data[i]["fabric-connection-state"] == "suspended":
                    if role.lower() == "undefined":
                        if data[i]["suspended-reason"] == "No fabric role configured":
                            status = True
                            return True
        if status == False:
            helpers.test_failure("Fabric switch role Check Test Failed")
        return False

    def rest_delete_fabric_role(self, switch, role=None):
        if helpers.bigrobot_test_ztn().lower() == 'true':
            helpers.log("ZTN is enabled , should not be adding switch again..")
            return True
        t = test.Test()
        c = t.controller('main')

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
        c = t.controller('main')
        url = '/api/v1/data/controller/core/switch[name="%s"]/interface' % (switch)
        c.rest.get(url)
        data = c.rest.content()
        url1 = '/api/v1/data/controller/applications/bcf/info/fabric/switch[name="%s"]' % (switch)
        c.rest.get(url1)
        data1 = c.rest.content()
        dpid = data1[0]["dpid"]
        url2 = '/api/v1/data/controller/core/switch[dpid="%s"]?select=fabric-lag' % (dpid)
        c.rest.get(url2)
        data3 = c.rest.content()
        if str(data1[0]["name"]) == str(switch):
            if data1[0]["fabric-role"] == "spine":
                fabric_interface = 0
                rack_lag = 0
                for i in range(0, len(data)):
                    if data[i]["type"] == "leaf":
                        fabric_interface = fabric_interface + 1
                for i in range(0, len(data3[0]["fabric-lag"])):
                        if (data3[0]["fabric-lag"][i]["lag-type"]) == "rack":
                            rack_lag = rack_lag + int(len(data3[0]["fabric-lag"][i]["member"]))
                if (int(rack_lag) == int(fabric_interface)):
                                helpers.log("No of Rack lag from  %s is correct,Expected = %d, Actual = %d " % (switch, fabric_interface, rack_lag))
                                return True
                else:
                                helpers.test_failure("No of Rack lag from %s is incorrect,Expected = %d, Actual = %d " % (switch, fabric_interface, rack_lag))
                                return False
            elif data1[0]["fabric-role"] == "leaf":
                    fabric_spine_interface = 0
                    fabric_peer_interface = 0
                    for i in range(0, len(data)):
                                if data[i]["type"] == "spine":
                                    fabric_spine_interface = fabric_spine_interface + 1

                                elif data[i]["type"] == "leaf":
                                    fabric_peer_interface = fabric_peer_interface + 1

                    for i in range(0, len(data3[0]["fabric-lag"])):
                                        if data3[0]["fabric-lag"][i]["lag-type"] == "spine":
                                            if (int(len(data3[0]["fabric-lag"][i]["member"])) == int(fabric_spine_interface)):
                                                helpers.log("Spine lag formation from leaf switch %s is correct,Expected = %d, Actual = %d, " % (switch, fabric_spine_interface, len(data3[0]["fabric-lag"][i]["member"])))
                                                return True
                                            else:
                                                helpers.test_failure(" Spine lag formation from leaf %s switch is not correct,Expected = %d, Actual = %d" % (switch, fabric_spine_interface, len(data3[0]["fabric-lag"][i]["member"])))
                                                return False
                                        elif data3[0]["fabric-lag"][i]["lag-type"] == "spine-broadcast":
                                                if len(data3[0]["fabric-lag"][i]["member"]) == (int(self.rest_verify_no_of_rack()) * fabric_spine_interface):
                                                    helpers.log("Spine Broadcast lag from leaf switch %s is correct , Actual = %d , Expected = %d" % (switch, int(self.rest_get_no_of_rack()), fabric_spine_interface))
                                                    return True
                                                else:
                                                        helpers.test_failure("Spine Broadcast lag from leaf switch %s is not correct,expected = %d,actual = %d" % (switch, (int(self.rest_get_no_of_rack()) * fabric_spine_interface), len(data3[0]["fabric-lag"][i]["member"])))
                                                        return False
                                        elif data3[0]["fabric-lag"][i]["lag-type"] == "leaf":
                                            if len(data3[0]["fabric-lag"][i]["member"]) == fabric_peer_interface:
                                                helpers.log("Peer lag formation from leaf switch %s is correct,Expected = %d, Actual = %d" % (switch, fabric_peer_interface, len(data3[0]["fabric-lag"][i]["member"])))
                                                return True
                                            else:
                                                helpers.test_failure(" Spine lag formation from leaf %s switch is not correct,expected= %d,Actual= %d" % (switch, fabric_peer_interface, len(data3[0]["fabric-lag"][i]["member"])))
                                                return False
        else :
            return False


    def rest_verify_fabric_switch(self, switch):
        # Function verify fabric switch status with role configured
        t = test.Test()
        c = t.controller('main')
        url = '/api/v1/data/controller/applications/bcf/info/fabric/switch[name="%s"]' % (switch)
        c.rest.get(url)
        data = c.rest.content()
        if data[0]["name"] == switch and data[0]["fabric-role"] != '':
            if data[0]["fabric-role"] == "spine" and data[0]["connected"] == True:
                        helpers.log("Pass: Fabric switch connection status for spine is correct")
                        return True
            elif data[0]["fabric-role"] == "leaf" and data[0]["connected"] == True:
                        helpers.log("Pass: Fabric switch connection status for leaf is correct")
                        return True
            else:
                helpers.test_failure("Fail:Switch status is not correct:%s=%s" % (switch, data[0]["connected"]))
                return False
        else:
            helpers.log("fabric role is not configured")
            return True

    def rest_verify_fabric_link(self):
        t = test.Test()
        c = t.controller('main')
        url = '/api/v1/data/controller/core/switch/interface' % ()
        c.rest.get(url)
        data = c.rest.content()
        fabric_interface = 0
        for i in range(0, len(data)):
            if data[i]["type"] == "leaf" or data[i]["type"] == "spine":
                fabric_interface = fabric_interface + 1
        url1 = '/api/v1/data/controller/applications/bcf/info/fabric?select=link' % ()
        c.rest.get(url1)
        data1 = c.rest.content()
        bidir_link = 0
        if not((data1 and True) or False):
            for i in range(0, len(data1[0]["link"])):
                if data1[0]["link"][i]["link-direction"] == "bidirectional":
                    bidir_link = bidir_link + 1
                    if bidir_link == fabric_interface / 2:
                        helpers.log("Pass: All Fabric links states are bidirectional")
                        return True
                    else:
                        helpers.test_failure("Fail: Inconsistent state of fabric links. Fabric_Interface = %d , bidir_link = %d" % (fabric_interface, bidir_link))
                        return False
        else:
            helpers.log("Fabric switches are misconfigued")

    def rest_verify_no_of_rack(self):
        t = test.Test()
        c = t.controller('main')
        url = '/api/v1/data/controller/applications/bcf/info/fabric/switch' % ()
        c.rest.get(url)
        data = c.rest.content()
        rack = []
        rack_count = 0
        for i in range(0, len(data)):
            if data[i]["fabric-role"] == "leaf":
                if data[i]["leaf-group"] == None:
                    rack_count = rack_count + 1
                elif not data[i]["leaf-group"] in rack:
                    rack.append(data[i]["leaf-group"])

        total_rack = rack_count + len(rack)
        helpers.log("Total Rack in the Topology: %d" % total_rack)
        return total_rack

    def rest_verify_no_of_spine(self):
        t = test.Test()
        c = t.controller('main')
        url = '/api/v1/data/controller/applications/bcf/info/fabric/switch' % ()
        c.rest.get(url)
        data = c.rest.content()
        list_spine = []
        for i in range(0, len(data)):
            if data[i]["fabric-role"] == "spine":
                list_spine.append(data[i]["name"])

        helpers.log("Total Spine in the topology: %d" % len(list_spine))
        return list_spine

    def rest_verify_rack_lag_from_leaf(self, switcha, switchb):
        '''Verify Rack lag formation for the leaf switch mentioned in the variables to all the racks
            Input: Leaf switch name  , any down event you are expecting to verify on
            Output: Will check the total no of spine switches and compare against the rack connection spine switches.
        '''
        t = test.Test()
        c = t.controller('main')
        url = '/api/v1/data/controller/core/switch[name="%s"]?select=fabric-lag' % (switcha)
        c.rest.get(url)
        data = c.rest.content()
        for i in range(0, len(data[0]["fabric-lag"])):
            if data[0]["fabric-lag"][i]["lag-type"] == "rack-lag":
                actual_spine = []
                for j in range(0, len(data[0]["fabric-lag"][i]["member"])):
                    if data[0]["fabric-lag"][i]["member"][j]["dst-switch"] not in actual_spine:
                        actual_spine.append(data[0]["fabric-lag"][i]["member"][j]["dst-switch"])
                for j in range(0, len(actual_spine)):
                    if (str(actual_spine[j]) == str(switchb)):
                        helpers.log("Rack connectivity from leaf switch %s using all the spine switches are up" % switcha)
                        return True

    def rest_verify_forwarding_lag(self, dpid, switch):
        '''Verify Edge port  Information in Controller Forwarding Table

            Input:  Specific DPID of the switch and also the switch name of the specific device

            Return: Match forwarding table lag/Port for peer switch edge ports
        '''
        t = test.Test()
        c = t.controller('main')
        url = '/api/v1/data/controller/applications/bcf/info/forwarding/network/switch[switch-name="%s"]/lag-table' % (switch)
        c.rest.get(url)
        data = c.rest.content()
        url1 = '/api/v1/data/controller/core/switch[dpid="%s"]' % (dpid)
        c.rest.get(url1)
        data1 = c.rest.content()
        url2 = '/api/v1/data/controller/core/switch[name="%s"]?select=fabric-lag' % (switch)
        c.rest.get(url2)
        data2 = c.rest.content()
        peer_intf = []
        for i in range(0, len(data2[0]["fabric-lag"])):
            if data2[0]["fabric-lag"][i]["lag-type"] == "leaf-lag":
                interface = re.sub("\D", "", data2[0]["fabric-lag"][i]["member"][0]["src-interface"])
                peer_intf.append(int(interface))
            else:
                continue
        if len(peer_intf) != 0:
            if data1[0]["leaf-group"] == None:
                for i in range(0, len(data)):
                        if peer_intf[0] in data[i]["port"]:
                            helpers.test_failure("Peer switch edge ports are not deleted from lag table")
                            return False

            else:
                for i in range(0, len(data)):
                        if peer_intf[0] in data[i]["port"]:
                            helpers.log("Peer switch edge ports are properly added in forwarding table")
                            return True
            return False

    def rest_verify_fabric_interface_lacp(self, switch, intf):
        t = test.Test()
        c = t.controller('main')
        url1 = '/api/v1/data/controller/applications/bcf/info/fabric/switch[name="%s"]' % (switch)
        c.rest.get(url1)
        data1 = c.rest.content()
        dpid = data1[0]["dpid"]
        url = '/api/v1/data/controller/core/switch[interface/name="%s"][dpid="%s"]?select=interface[name="%s"]' % (intf, dpid, intf)
        c.rest.get(url)
        data = c.rest.content()
        try:
            if data[0]["interface"][0]["lacp-state"] == "active" and data[0]["interface"][0]["state"] == "up":
                        helpers.log("LACP Neibhour Is Up and active")
                        return True
            else:
                        helpers.test_log("LACP is enabled , LACP Partner is not seen , check the floodlight logs")
                        return False
        except KeyError:
            return False

    def rest_verify_fabric_error_invalid_link(self, rack1, rack2):
        t = test.Test()
        c = t.controller('main')
        url = '/api/v1/data/controller/applications/bcf/info/errors/fabric/invalid-link' % ()
        c.rest.get(url)
        data = c.rest.content()
        match_string = "Link between Leaf Groups [%s, %s ]" % (rack1, rack2)
        if not((data and True) or False):
            if len(data) != 0:
                if data["reason"] == str(match_string):
                    helpers.log("Fabric error reported for invalid links")
                    return True
                else:
                    helpers.test_failure("No Fabric error Reported for invalid links")
                    return False
            else:
                helpers.log("Fabric error will be none")

    def rest_verify_fabric_error_missing_link(self, switcha, switchb, rack1):
        t = test.Test()
        c = t.controller('main')
        url = '/api/v1/data/controller/applications/bcf/info/errors/fabric/missing-link' % ()
        c.rest.get(url)
        data = c.rest.content()
        match_string = "Link between leaf switches missing in %s" % (rack1)
        if not((data and True) or False):
            if data[0]["dst-switch-name"] == switcha or data[0]["src-switch-name"] == switcha:
                if data["description"] == str(match_string):
                    helpers.log("Pass:Fabric error reported for missing links")
                    return True
                else:
                    helpers.test_failure("No Fabric error Reported for missing links")
                    return False
            else:
                helpers.log("No Fabric error with switch name reported")

    def rest_verify_forwarding_port_table(self, switch):
        t = test.Test()
        c = t.controller('main')
        url = '/api/v1/data/controller/applications/bcf/info/forwarding/network/switch[switch-name="%s"]?select=port-table' % (switch)
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
        c = t.controller('main')
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
        c = t.controller('main')
        url1 = '/api/v1/data/controller/applications/bcf/info/fabric/switch[name="%s"]' % (switch)
        c.rest.get(url1)
        data1 = c.rest.content()
        dpid = data1[0]["dpid"]
        url = '/api/v1/data/controller/core/switch[interface/name="%s"][dpid="%s"]?select=interface[name="%s"]' % (intf, dpid, intf)
        c.rest.get(url)
        data = c.rest.content()
        if len(data) != 0:
            if data[0]["interface"][0]["state"] == "down" and data[0]["interface"][0]["type"] == "unknown":
                helpers.log("Interface is connected to spine or Physical Interface status is down for the leaf switch")
            elif data[0]["interface"][0]["state"] == "up" and data[0]["interface"][0]["type"] == "edge":
                    helpers.log("Inteface is connected to leaf and it is a edge port")
            elif data[0]["interface"][0]["state"] == "up" and data[0]["interface"][0]["type"] == "leaf" or data[0]["interface"][0]["state"] == "up" and data[0]["interface"][0]["type"] == "spine":
                    helpers.log("Interface is fabric interface")
                    return True
            elif data[0]["interface"][0]["state"] == "quarantined" and data[0]["interface"][0]["type"] == "unknown":
                    helpers.log("Edge ports will not come up for the spine switches")
            else:
                    helpers.test_failure("Interface status is not known to the fabric system , Please check the logs")
                    return False
        else:
            helpers.test_failure("Given fabric interface is not valid")
            return False


    def rest_verify_forwarding_port_edge(self, switcha, intf0, switchb, intf1):
        '''
         Function to verify Lag id for the portgroup
         Input:  Dual leaf switch names
         Output" True/false based on the lag-id creation for the same edge port-groups on both the leaf switches
        '''
        t = test.Test()
        c = t.controller('main')
        intf0 = (re.sub("\D", "", intf0))
        intf1 = (re.sub("\D", "", intf1))
        url_a = '/api/v1/data/controller/applications/bcf/info/forwarding/network/switch[switch-name="%s"]/port-table' % (switcha)
        c.rest.get(url_a)
        data = c.rest.content()
        url_b = '/api/v1/data/controller/applications/bcf/info/forwarding/network/switch[switch-name="%s"]/port-table' % (switchb)
        c.rest.get(url_b)
        data1 = c.rest.content()
        lag_id_a = []
        lag_id_b = []
        for i in range(0, len(data)):
            if str(data[i]["port-num"]) == str(intf0):
                    helpers.log("adding the lag id=%s" % data[i]["lag-id"])
                    lag_id_a.append(data[i]["lag-id"])
            else:
                continue
        for i in range(0, len(data1)):
            if str(data1[i]["port-num"]) == str(intf1):
                lag_id_b.append(data1[i]["lag-id"])
            else:
                continue
        if lag_id_a[0] == lag_id_b[0]:
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
        c = t.controller('main')
        url = '/api/v1/data/controller/core/switch[name="%s"]/interface' % (switch)
        c.rest.get(url)
        data = c.rest.content()
        list_fabric_interface = []
        list_fabric_edge_interface = []
        for i in range(0, len(data)):
            if data[i]["type"] == "unknown":
                continue
            elif data[i]["type"] == "edge":
                list_fabric_edge_interface.append(int(re.sub("\D", "", (data[i]["name"]))))
            elif data[i]["type"] == "leaf" or data[i]["type"] == "spine":
                list_fabric_interface.append(int(re.sub("\D", "", (data[i]["name"]))))
        url1 = '/api/v1/data/controller/applications/bcf/info/forwarding/network/switch[switch-name="%s"]/port-table' % (switch)
        c.rest.get(url1)
        data1 = c.rest.content()
        if len(list_fabric_interface) != 0 or len(list_fabric_edge_interface) != 0:
            for i in range(0, len(data1)):
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
        c = t.controller('main')
        url0 = '/api/v1/data/controller/core/switch-config[name="%s"]/interface[name="%s"]' % (switch, intf)
        c.rest.put(url0, {"name": str(intf)})
        url = '/api/v1/data/controller/core/switch-config[name="%s"]/interface[name="%s"]' % (switch, intf)
        c.rest.patch(url, {"shutdown": True})
        helpers.sleep(5)
        url1 = '/api/v1/data/controller/applications/bcf/info/fabric/switch[name="%s"]' % (switch)
        c.rest.get(url1)
        data1 = c.rest.content()
        dpid = data1[0]["dpid"]
        url2 = '/api/v1/data/controller/core/switch[interface/name="%s"][dpid="%s"]?select=interface[name="%s"]' % (intf, dpid, intf)
        c.rest.get(url2)
        cli_string = 'show debug event module FabricManager event-name fabric-interface-physical-status-change-event | grep -B 2 "swName:' + switch + ', ifName:' + intf + ', "'
        c.enable(cli_string)

        data = c.rest.content()
        if data[0]["interface"][0]["state"] == "down":
            helpers.log("Interface state is down")
            return True
        else:
            helpers.test_failure("Interface did not go down:state is still Up, open the bug for inteface disable status")
            return False

    def rest_enable_fabric_interface(self, switch, intf, timeout=30):
        t = test.Test()
        c = t.controller('main')

        url = '/api/v1/data/controller/core/switch-config[name="%s"]/interface[name="%s"]' % (switch, intf)
        c.rest.delete(url, {"shutdown": None})
        helpers.sleep(3)
        url1 = '/api/v1/data/controller/applications/bcf/info/fabric/switch[name="%s"]' % (switch)
        c.rest.get(url1)
        data1 = c.rest.content()
        dpid = data1[0]["dpid"]
        max = int(timeout) / 3
        for loop in range (0, int(max)):
            url2 = '/api/v1/data/controller/core/switch[interface/name="%s"][dpid="%s"]?select=interface[name="%s"]' % (intf, dpid, intf)
            c.rest.get(url2)
            data = c.rest.content()
            cli_string = 'show debug event module FabricManager event-name fabric-interface-physical-status-change-event | grep -B 2 "swName:' + switch + ', ifName:' + intf + ', "'
            c.enable(cli_string)

            if data[0]["interface"][0]["state"] == "up":
                helpers.log("Interface state is up")
                return True

            helpers.log("USR INFO: time since unshut:  switch - %s interface - %s  time - %d sec " % (switch, intf, int(loop + 1) * 3))
            helpers.sleep(3)
        helpers.test_failure("Interface did not come up:state is still down, open the bug for inteface enable status")
        return False

    def rest_verify_fabric_interface_rx_stats(self, switch, intf, frame_cnt, vrange=5):
        ''' Function to verify the fabric interface stats
        Input: switch and interface
        Output: reusult will be compared against the frame_cnt given in the arguments
        '''
        t = test.Test()
        c = t.controller('main')
        dpid = self.rest_get_dpid(switch)
        url = '/api/v1/data/controller/applications/bcf/info/statistic/interface-counter[interface/name="%s"][switch-dpid="%s"]?select=interface[name="%s"]' % (intf, dpid, intf)
        frame_cnt = int(frame_cnt)
        vrange = int(vrange)
        c.rest.get(url)
        data = c.rest.content()
        if data[0]["interface"][0]["name"] == intf:
            if (data[0]["interface"][0]["counter"]["rx-unicast-packet"] >= (frame_cnt - vrange)) and (data[0]["interface"][0]["counter"]["rx-unicast-packet"] <= (frame_cnt + vrange)):
                helpers.log("Pass: Rate value Expected:%d, Actual:%d" % (frame_cnt, data[0]["interface"][0]["counter"]["rx-unicast-packet"]))
                return True
            elif (data[0]["interface"][0]["counter"]["rx-broadcast-packet"] >= (frame_cnt - vrange)) and (data[0]["interface"][0]["counter"]["rx-broadcast-packet"] <= (frame_cnt + vrange)):
                helpers.log("Pass: Rate value Expected:%d, Actual:%d" % (frame_cnt, data[0]["interface"][0]["counter"]["rx-broadcast-packet"]))
                return True
            elif (data[0]["interface"][0]["counter"]["rx-multicast-packet"] >= (frame_cnt - vrange)) and (data[0]["interface"][0]["counter"]["rx-multicast-packet"] <= (frame_cnt + vrange)):
                helpers.log("Pass: Rate value Expected:%d, Actual:%d" % (frame_cnt, data[0]["interface"][0]["counter"]["rx-multicast-packet"]))
                return True
            else:
                helpers.test_failure("Interface counters does not match Expected:%d,Actual:%d,%d,%d" % (frame_cnt, data[0]["interface"][0]["counter"]["rx-unicast-packet"], data[0]["interface"][0]["counter"]["rx-broadcast-packet"], data[0]["interface"][0]["counter"]["rx-multicast-packet"]))
                return False
        else:
            helpers.log("Given switch name and interface name are not present in the controller")

    def rest_verify_fabric_interface_tx_stats(self, switch, intf, frame_cnt, vrange=5):
        ''' Function to verify the fabric interface tx stats
        Input: switch and interface
        Output: Results will be compared against frame_cnt given
        '''
        t = test.Test()
        c = t.controller('main')
        dpid = self.rest_get_dpid(switch)
        url = '/api/v1/data/controller/applications/bcf/info/statistic/interface-counter[interface/name="%s"][switch-dpid="%s"]?select=interface[name="%s"]' % (intf, dpid, intf)
        frame_cnt = int(frame_cnt)
        vrange = int(vrange)
        c.rest.get(url)
        data = c.rest.content()
        if data[0]["interface"][0]["name"] == intf:
            if (data[0]["interface"][0]["counter"]["tx-unicast-packet"] >= (frame_cnt - vrange)) and (data[0]["interface"][0]["counter"]["tx-unicast-packet"] <= (frame_cnt + vrange)):
                helpers.log("Pass: Rate value Expected:%d, Actual:%d" % (frame_cnt, data[0]["interface"][0]["counter"]["tx-unicast-packet"]))
                return True
            elif (data[0]["interface"][0]["counter"]["tx-broadcast-packet"] >= (frame_cnt - vrange)) and (data[0]["interface"][0]["counter"]["tx-broadcast-packet"] <= (frame_cnt + vrange)):
                helpers.log("Pass: Rate value Expected:%d, Actual:%d" % (frame_cnt, data[0]["interface"][0]["counter"]["tx-broadcast-packet"]))
                return True
            elif (data[0]["interface"][0]["counter"]["tx-multicast-packet"] >= (frame_cnt - vrange)) and (data[0]["interface"][0]["counter"]["tx-multicast-packet"] <= (frame_cnt + vrange)):
                helpers.log("Pass: Rate value Expected:%d, Actual:%d" % (frame_cnt, data[0]["interface"][0]["counter"]["tx-multicast-packet"]))
                return True
            else:
                helpers.test_failure("Interface counters does not match Expected:%d,Actual:%d,%d,%d" % (frame_cnt, data[0]["interface"][0]["counter"]["tx-unicast-packet"], data[0]["interface"][0]["counter"]["tx-broadcast-packet"], data[0]["interface"][0]["counter"]["tx-multicast-packet"]))
                return False
        else:
            helpers.log("Given switch name and interface name are not present in the controller")

    def rest_verify_fabric_interface_rx_rates(self, switch, intf, frame_rate, vrange=100):
        ''' Function to verify the fabric interface rates
        Input: switch and interface
        Output: reusult will be compared against the frame_rate given in the arguments
        '''
        t = test.Test()
        c = t.controller('main')
        dpid = self.rest_get_dpid(switch)
        url = '/api/v1/data/controller/applications/bcf/info/statistic/interface-rate[interface/name="%s"][switch-dpid="%s"]?select=interface[name="%s"]' % (intf, dpid, intf)
        frame_rate = int(frame_rate)
        vrange = int(vrange)
        c.rest.get(url)
        data = c.rest.content()
        if data[0]["interface"][0]["name"] == intf:
            if (data[0]["interface"][0]["rate"][0]["rx-unicast-packet-rate"] >= (frame_rate - vrange)) and (data[0]["interface"][0]["rate"][0]["rx-unicast-packet-rate"] <= (frame_rate + vrange)):
                helpers.log("Pass: Rate value Expected:%d, Actual:%d" % (frame_rate, data[0]["interface"][0]["rate"][0]["rx-unicast-packet-rate"]))
                return True
            else:
                helpers.test_failure("Interface Rx rates does not match, Expected:%d, Actual:%d" % (frame_rate, data[0]["interface"][0]["rate"][0]["rx-unicast-packet-rate"]))
                return False
        else:
            helpers.log("Given switch name and interface name are not present in the controller")

    def rest_verify_fabric_interface_tx_rates(self, switch, intf, frame_rate, vrange=100):
        ''' Function to verify the fabric interface tx rates
        Input: switch and interface
        Output: Results will be compared against frame_rate given
        '''
        t = test.Test()
        c = t.controller('main')
        dpid = self.rest_get_dpid(switch)
        url = '/api/v1/data/controller/applications/bcf/info/statistic/interface-rate[interface/name="%s"][switch-dpid="%s"]?select=interface[name="%s"]' % (intf, dpid, intf)
        frame_rate = int(frame_rate)
        vrange = int(vrange)
        c.rest.get(url)
        data = c.rest.content()
        if data[0]["interface"][0]["name"] == intf:
            if (data[0]["interface"][0]["rate"][0]["tx-unicast-packet-rate"] >= (frame_rate - vrange)) and (data[0]["interface"][0]["rate"][0]["tx-unicast-packet-rate"] <= (frame_rate + vrange)):
                helpers.log("Pass: Rate value Expected:%d, Actual:%d" % (frame_rate, data[0]["interface"][0]["rate"][0]["tx-unicast-packet-rate"]))
                return True
            else:
                helpers.test_failure("Interface Tx rates does not match, Expected:%d, Actual:%d" % (frame_rate, data[0]["interface"][0]["rate"][0]["tx-unicast-packet-rate"]))
                return False
        else:
            helpers.log("Given switch name and interface name are not present in the controller")

    def rest_verify_tenant_rx_stats(self, tenant, frame_cnt, vrange=5):
        ''' Function to verify the Tenant stats
        Input: Tenant name , matching frame count , if required user can provide range as well for the frame count match
        Output: given Tenant counters will be showed and matched aginst the value
        '''
        t = test.Test()
        c = t.controller('main')
        frame_cnt = int(frame_cnt)
        vrange = int(vrange)
        url = '/api/v1/data/controller/applications/bcf/info/statistic/tenant-counter[name="%s"]' % (tenant)
        c.rest.get(url)
        data = c.rest.content()
        if data[0]["name"] == tenant:
                    if (int(data[0]["counter"]["rx-packet"]) >= (frame_cnt - vrange)) and (int(data[0]["counter"]["rx-packet"]) <= (frame_cnt + vrange)):
                        helpers.log("Pass: Tenant Counters value Expected:%d, Actual:%d" % (frame_cnt, int(data[0]["counter"]["rx-packet"])))
                        return True
                    else:
                        helpers.test_failure("Tenant counter value does not match,Expected:%d,Actual:%d" % (frame_cnt, int(data[0]["counter"]["rx-packet"])))
                        return False
        else:
            helpers.log("Given tenant name does not match the config")

    def rest_verify_tenant_tx_stats(self, tenant, frame_cnt, vrange=5):
        ''' Function to verify the Tenant Tx stats
        Input: Tenant name , matching frame count , if required user can provide range as well for the frame count match
        Output: given Tenant counters will be showed and matched aginst the value
        '''
        t = test.Test()
        c = t.controller('main')
        frame_cnt = int(frame_cnt)
        vrange = int(vrange)
        url = '/api/v1/data/controller/applications/bcf/info/statistic/tenant-counter[name="%s"]' % (tenant)
        c.rest.get(url)
        data = c.rest.content()
        if data[0]["name"] == tenant:
                    if (int(data[0]["counter"]["tx-packet"]) >= (frame_cnt - vrange)) and (int(data[0]["counter"]["tx-packet"]) <= (frame_cnt + vrange)):
                        helpers.log("Pass: Tenant Counters value Expected:%d, Actual:%d" % (frame_cnt, int(data[0]["counter"]["tx-packet"])))
                        return True
                    else:
                        helpers.test_failure("Tenant counter value does not match,Expected:%d,Actual:%d" % (frame_cnt, int(data[0]["counter"]["tx-packet"])))
                        return False
        else:
            helpers.log("Given tenant name does not match the config")

    def rest_verify_tenant_rx_rates(self, tenant, frame_rate, vrange=100):
        ''' Function to verify the Tenant Tx stats
        Input: Tenant name , matching frame count , if required user can provide range as well for the frame count match
        Output: given Tenant counters will be showed and matched aginst the value
        '''
        t = test.Test()
        c = t.controller('main')
        frame_rate = int(frame_rate)
        vrange = int(vrange)
        url = '/api/v1/data/controller/applications/bcf/info/statistic/tenant-rate[name="%s"]' % (tenant)
        c.rest.get(url)
        data = c.rest.content()
        if data[0]["name"] == tenant:
                    if (int(data[0]["rate"][0]["rx-packet-rate"]) >= (frame_rate - vrange)) and (int(data[0]["rate"][0]["rx-packet-rate"]) <= (frame_rate + vrange)):
                        helpers.log("Pass: Tenant Counters value Expected:%d, Actual:%d" % (frame_rate, int(data[0]["rate"][0]["rx-packet-rate"])))
                        return True
                    else:
                        helpers.test_failure("Tenant counter value does not match,Expected:%d,Actual:%d" % (frame_rate, int(data[0]["rate"][0]["rx-packet-rate"])))
                        return False
        else:
            helpers.log("Given tenant name does not match the config")

    def rest_verify_tenant_tx_rates(self, tenant, frame_rate, vrange=100):
        ''' Function to verify the Tenant Tx stats
        Input: Tenant name , matching frame count , if required user can provide range as well for the frame count match
        Output: given Tenant counters will be showed and matched aginst the value
        '''
        t = test.Test()
        c = t.controller('main')
        frame_rate = int(frame_rate)
        vrange = int(vrange)
        url = '/api/v1/data/controller/applications/bcf/info/statistic/tenant-rate[name="%s"]' % (tenant)
        c.rest.get(url)
        data = c.rest.content()
        if data[0]["name"] == tenant:
                    if (int(data[0]["rate"][0]["tx-packet-rate"]) >= (frame_rate - vrange)) and (int(data[0]["rate"][0]["tx-packet-rate"]) <= (frame_rate + vrange)):
                        helpers.log("Pass: Tenant Counters value Expected:%d, Actual:%d" % (frame_rate, int(data[0]["rate"][0]["tx-packet-rate"])))
                        return True
                    else:
                        helpers.test_failure("Tenant counter value does not match,Expected:%d,Actual:%d" % (frame_rate, int(data[0]["rate"][0]["tx-packet-rate"])))
                        return False
        else:
            helpers.log("Given tenant name does not match the config")

    def rest_verify_membership_port_count(self, tenant, count):
        ''' Function to verify the membership port count for tenant
        Input:  provide how many port counts user expect in a tenant (specifically useful for scale)
        Output: Function will go through the specific tenant and match the provided count (e.g , 1000 vns , 2 ports each , will be 2000 count)
        '''
        t = test.Test()
        c = t.controller('main')
        count = int(count)
        url = '/api/v1/data/controller/applications/bcf/info/endpoint-manager/tenant[name="%s"]' % tenant
        c.rest.get(url)
        data = c.rest.content()
        if int(data[0]["port-count"]) == count:
            helpers.log("Expected membership port count for the tenant is correct")
            return True
        else:
            helpers.test_failure("Expected membership port count for tenant is not correct: Expected:%d,Actual:%d" % (count, data[0]["port-count"]))
            return False

    def cli_show_interface(self, switch=None, intf=None):
        ''' Function to show interface using controller CLI
        Input: interface name , if not given default = None
        Output: Execute show inteface from CLI and verify the output is not empty.
        '''
        t = test.Test()
        c = t.controller('main')
        c.cli("show interface %s %s" % switch, intf)
        result = c.cli_content()
        return result

    def cli_show_switch(self, switch=None):
        ''' Function to show switch using controller CLI
        Input: switch name , if not given it will be none
        Output: Execute show switch from CLI and verify the output is not empty
        '''
        t = test.Test()
        c = t.controller('main')
        c.cli("show switch %s" % switch)
        result = c.cli_content()
        return result

    def cli_show_lag(self, switch=None, lag_name=None):
        ''' Function to show lag using controller CLI
        Input: switch and type of lag , Default= none
        Output: Execute show lag from CLI and verify the output is not empty
        '''
        t = test.Test()
        c = t.controller('main')
        c.cli("show lag %s %s" % switch, lag_name)
        result = c.cli_content()
        return result

    def cli_show_lacp(self, switch=None):
        ''' Function to show lacp using controller CLI
        Input: Switch , Default=None
        Output: Execute show lacp from CLI and verify the output is not empty
        '''
        t = test.Test()
        c = t.controller('main')
        c.cli("show lacp %s" % switch)
        result = c.cli_content()
        return result

    def cli_show_link(self):
        ''' Function to show link using controller CLI
        Input: None
        Output: Execute show link from CLI and verify the output is not empty
        '''
        t = test.Test()
        c = t.controller('main')
        c.cli("show link")
        result = c.cli_content()
        return result

    def cli_controller_reboot_switch(self, switch=None):
        '''Function to reboot switch from main controllers CLI
            if switch argument is not passed reboot all switchs
        '''
        t = test.Test()
        c = t.controller('main')
        params = t.topology_params()
        if switch is None:
            helpers.log("Executing switch reboot for all switchs from main controller")
            c.enable('system reboot switch all', prompt=':')
            c.enable('yes', timeout=300)
            helpers.sleep(120)
            helpers.log('Successfully rebooted switches from controller')
            if helpers.bigrobot_test_ztn().lower() == 'true':
                helpers.debug("Env BIGROBOT_TEST_ZTN is True. Setting up ZTN.")
                helpers.log("Reconnecting switch consoles and updating switch IP's....")
                for key in params:
                    t.setup_ztn_phase2(key)
                helpers.debug("Updated topology info:\n%s"
                              % helpers.prettify(params))
                main = t.controller("main")
                main.enable("show switch")
                helpers.log("Successfully rebooted switchs from controller and re-connected switch IP's with ssh admin account..")
                return True
            else:
                helpers.log("Not ZTN ..not reconfiguring switch consoles for ssh connections..")
        else:
            helpers.log("Rebooting switch: %s from controller" % switch)
            c.enable('show switch %s version | grep Uptime' % switch)
            c.enable('system reboot switch %s' % switch, prompt=':')
            c.enable('yes', timeout=300)
            helpers.sleep(120)
            c.enable('show switch %s version | grep Uptime' % switch)
            helpers.log("Success rebooting switch: %s from controller" % switch)
            if helpers.bigrobot_test_ztn().lower() == 'true':
                helpers.debug("Env BIGROBOT_TEST_ZTN is True. Setting up ZTN.")
                helpers.log("Reconnecting switch consoles and updating switch IP's....")
                for key in params:
                    helpers.debug("params: \n%s" % helpers.prettify(params[key]))
                    if re.match(r's\d+', key):
                        if params[key]['alias'] == switch:
                            helpers.log("Found switch: %s in params reconnecting it using console and SSH" % switch)
                            t.setup_ztn_phase2(key)
                helpers.debug("Updated topology info:\n%s"
                              % helpers.prettify(params))
                main = t.controller("main")
                main.enable("show switch")
                helpers.log("Successfully rebooted switchs from controller and re-connected switch IP's with ssh admin account..")
                return True
            else:
                helpers.log("Not ZTN ..not reconfiguring switch consoles for ssh connections..")
        return True
    def rest_verify_stats_interval(self, intf_value=60, vns_value=600):
        ''' Function to configure stats interval value for interface and vns
        Input: interface interval value and vns interval value , Default = None
        Output: Set the configured number and verify the interval setting
        '''
        t = test.Test()
        c = t.controller('main')
        intf_value = int(intf_value)
        vns_value = int(vns_value)
        url = '/api/v1/data/controller/applications/bcf/stats-config'
        c.rest.patch(url, {"interface-stat-interval": intf_value})
        url1 = '/api/v1/data/controller/applications/bcf/stats-config'
        c.rest.patch(url1, {"segment-stat-interval": vns_value})
        c.rest.get(url)
        data = c.rest.content()
        if int(data[0]["interface-stat-interval"]) == intf_value and int(data[0]["segment-stat-interval"]) == vns_value:
            helpers.log("Interval value provided is correct")
            return True
        else:
            helpers.test_failure("Interval value does not match Actual:%d , Expected:%d" % intf_value, int(data["interface-stat-interval"]))
            return False

    def rest_verify_host_lag(self, switcha, intf0, switchb, intf1):
        ''' Function to verify host lag formation
        Input: dual rack switch name and specific interface which host is connected
        Output: verify the lag id for the given interface from both switch
        '''
        t = test.Test()
        c = t.controller('main')
        intf0 = re.sub("\D", "", intf0)
        intf1 = re.sub("\D", "", intf1)
        lag_id_a = []
        lag_id_b = []
        url_a = '/api/v1/data/controller/applications/bcf/info/forwarding/network/switch[switch="%s"]/port-table' % (switcha)
        c.rest.get(url_a)
        data = c.rest.content()
        url_b = '/api/v1/data/controller/applications/bcf/info/forwarding/network/switch[switch="%s"]/port-table' % (switchb)
        c.rest.get(url_b)
        data1 = c.rest.content()
        for i in range(0, len(data)):
            if data[i]["port-num"] == int(intf0):
                lag_id_a.append(data[i]["lag-id"])
        for i in range(0, len(data1)):
            if data1[i]["port-num"] == int(intf1):
                lag_id_b.append(data1[i]["lag-id"])
        if lag_id_a[0] == lag_id_b[0]:
            helpers.log("BM Downlink lag are properly created for dual rack")
            return True
        else:
            helpers.test_failure("BM Downlink lag are not properly created for dual rack %d:%d" % lag_id_a[0], lag_id_b[0])
            return True

    def rest_verify_fabric_interface_stats_brief(self, switch, intf, frame_cnt, vrange=5):
        ''' Function to verify the Interface stats brief
        Input: switch name and interface
        Output: verify stats brief with both rx and tx on the same CLI output for a given switch and interface
        '''
        t = test.Test()
        c = t.controller('main')
        frame_cnt = int(frame_cnt)
        vrange = int(vrange)
        url = '/api/v1/data/controller/applications/bcf/info/stats/interface-stats/interface[switch-name="%s"][interface-name="%s"]?select=brief' % (switch, intf)
        c.rest.get(url)
        data = c.rest.content()
        if data[0]["switch-name"] == switch and data[0]["interface-name"] == intf:
                    if (int(data[0]["brief"]["rx-unicast-packet"]) >= (frame_cnt - vrange)) and (int(data[0]["brief"]["rx-unicast-packet"]) <= (frame_cnt + vrange)):
                        if (int(data[0]["brief"]["tx-unicast-packet"]) >= (frame_cnt - vrange)) and (int(data[0]["brief"]["tx-unicast-packet"]) <= (frame_cnt + vrange)):
                            helpers.log("Pass: Stats-brief counter for interface rx:%d, tx:%d" % (int(data[0]["brief"]["rx-unicast-packet"]), int(data[0]["brief"]["tx-unicast-packet"])))
                            return True
                        else:
                            helpers.test_failure("rx, tx counter for a interface does not match,rx:%d,tx:%d" % (int(data[0]["brief"]["rx-unicast-packet"]), int(data[0]["brief"]["tx-unicast-packet"])))
                            return False
        else:
            helpers.log("Given interface name is not valid")

    def rest_delete_all_tenants(self):
        '''
        delete all the tenant in the system
        output:  True
                 False
        '''
        t = test.Test()
        c = t.controller('main')
        helpers.log("********* rest_delete_all_tenant ")
        url = '/api/v1/data/controller/applications/bcf/info/endpoint-manager/tenant'
        c.rest.get(url)
        content = c.rest.content()
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
            return False
        helpers.log("Output: %s" % c.rest.result_json())
        length = len(content)
        helpers.log("USER INFO: Number of tenant to be deleted: %s" % str(length))
        for index in range(length):
            name = content[index]['name']
            helpers.log("Tenant being deleted is %s " % name)
            url = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]' % name
            c.rest.delete(url, {"name": name})
            if not c.rest.status_code_ok():
                helpers.test_failure(c.rest.error())
                return False
        return True

    def rest_add_shutdown_fabric_switch(self, switch):
        '''
        add shutdown command to switch
        input: switch name
        output:  True
                 False
        '''
        t = test.Test()
        c = t.controller('main')
        url = '/api/v1/data/controller/core/switch-config[name="%s"]' % (switch)
        try:
            c.rest.patch(url, {"shutdown": True})
        except:
            return False
        else:
            return True
    def rest_delete_shutdown_fabric_switch(self, switch):
        '''
        delete shutdown command to switch
        input: switch name
        output:  True
                 False
        '''
        t = test.Test()
        c = t.controller('main')
        url = '/api/v1/data/controller/core/switch-config[name="%s"]/shutdown' % (switch)
        try:
            c.rest.delete(url, {})
        except:
            return False
        else:
            return True

    def clean_configuration(self, node='main'):
        '''
            Objective: Delete all user configuration
        '''
        t = test.Test()
        return t.t5_clean_configuration(node)

    def rest_clean_switch_interface(self):
        '''
        Function to remove shutdown command from the interface for all switches
        Input: None
        Output : remove shutdown command
        '''
        t = test.Test()
        c = t.controller('main')
        url = '/api/v1/data/controller/core/switch-config?config=true'
        c.rest.get(url)
        data = c.rest.content()
        for i in range(0, len(data)):
            try:
                value = data[i]["interface"]
            except KeyError:
                continue
            for j in range(0, len(data[i]["interface"])):
                    url = '/api/v1/data/controller/core/switch-config[name="%s"]/interface[name="%s"]' % (data[i]["name"], data[i]["interface"][j]["name"])
                    c.rest.delete(url, {"shutdown": None})
                    helpers.sleep(5)
                    return True

    def rest_verify_forwarding_rack_lag(self, switch, rack, intf):
        '''Verify rack lag and interfaces part of the rack lag three rack setup
        Input: switch , leaf group name, fabric interfaces
        Output : True or false based on the entry present in the forwarding lag.
        '''
        t = test.Test()
        c = t.controller('main')
        url = '/api/v1/data/controller/applications/bcf/info/forwarding/network/switch[switch-name="%s"]/lag-table' % (switch)
        c.rest.get(url)
        data = c.rest.content()
        interface = int(re.sub("\D", "", intf))
        rack_name = "rack-" + rack
        helpers.log("%s,%s" % (rack_name, interface))
        for i in range(0, len(data)):
            if str(data[i]["lag-name"]) == str(rack_name):
                try:
                    value = data[i]["port"]
                except KeyError:
                    return False
                if interface in data[i]["port"]:
                        helpers.log("interface present in rack lag")
                        return True
                else:
                        helpers.test_log("given interface not present in rack lag rack=%s,interface=%s" % (rack, intf))
                        return False

    def rest_get_fabric_interface_info(self, switch, intf):
        '''
        Function to get the specific fabric interface status
        Input:   switch   -  leaf1-a ..
                 interface  - ethernet33
        Output: interface info in dict format
        '''
        helpers.test_log("Entering ==> rest_get_fabric_interface_info  for switch: %s  interface: %s" % (switch, intf))
        t = test.Test()
        c = t.controller('main')

        url1 = '/api/v1/data/controller/core/switch?select=name'
        c.rest.get(url1)
        data1 = c.rest.content()
        helpers.test_log("data1 is:  %s, %d" % (data1, len(data1)))

        for i in range (0, len(data1)):
            if 'name' in data1[i].keys() and data1[i]['name'] == switch:
                dpid = data1[i]["dpid"]
                helpers.test_log("get the dpid for switch:  %s" % switch)
                break

        url = '/api/v1/data/controller/core/switch[interface/name="%s"][dpid="%s"]?select=interface[name="%s"]' % (intf, dpid, intf)
        c.rest.get(url)
        intfinfo = {}
        data = c.rest.content()
        if len(data) != 0:
            intfinfo['state'] = data[0]["interface"][0]["state"]
            intfinfo['name'] = data[0]["interface"][0]["name"]
            intfinfo['type'] = data[0]["interface"][0]["type"]
            intfinfo['lacp'] = data[0]["interface"][0]["lacp-state"]
            try:
                intfinfo['downreason'] = data[0]["interface"][0]["interface-down-reason"]
            except:
                helpers.test_log("interface-down-reason does not exist for:  %s" % intf)
            helpers.test_log("interface info is: %s" % intfinfo)
            return intfinfo
        else:
            helpers.test_failure("Given fabric interface is not valid")
            return False


    def rest_verify_fabric_interface_BPDU_Down(self, switch, intf):
        """ check the interface is down by BPDU Guard
        """

        info = self.rest_get_fabric_interface_info(switch, intf)
        if info['state'] == "down" and info['downreason'] == "BPDU Guard Error Disabled":
            return True
        else:
            return False


    def rest_delete_fabric_interface(self, switch, intf):
        t = test.Test()
        c = t.controller('main')
        url = '/api/v1/data/controller/core/switch-config[name="%s"]/interface[name="%s"]' % (switch, intf)
        c.rest.delete(url, {})
        helpers.sleep(2)

        url1 = '/api/v1/data/controller/core/switch-config[name="%s"]?config=true' % switch
        c.rest.get(url1)
        data = c.rest.content()[0]
        if 'interface' in data.keys():
            helpers.test_log("interface exist for:  %s" % data['interface'])
            for i in range (0, len(data['interface'])):
                if data['interface'][i]["name"] == intf:
                    helpers.test_failure("Interface did not deleted: %s" % intf)
                    return False
        return True

    def cli_show_running_tenant(self, tenant=None):
        ''' Function to show switch using controller CLI
        Input: switch name , if not given it will be none
        Output: Execute show switch from CLI and verify the output is not empty
        '''
        t = test.Test()
        c = t.controller('main')
        if tenant:
            c.cli("show running-config tenant %s" % tenant)
        else:
            c.cli("show running-config tenant")

        return True

    def rest_verify_forwarding_cidr_route_spine(self, switch, no_of_ip_subnet):
        '''
        Function to verify the forwarding cidr table entry in all the switches
        Input: switch name , and no of ip subnet expected in the switch
        Output: True or false based on the no of routes to be present and system VRF table no (1023 Fixed)
        '''
        t = test.Test()
        c = t.controller('main')
        url = '/api/v1/data/controller/applications/bcf/info/forwarding/network/switch[switch-name="%s"]/l3-cidr-route-table' % (switch)
        c.rest.get(url)
        data = c.rest.content()
        url1 = '/api/v1/data/controller/applications/bcf/info/fabric/switch[name="%s"]' % (switch)
        c.rest.get(url1)
        data1 = c.rest.content()
        if data1[0]["name"] == switch and data1[0]["fabric-role"] == "spine":
                if len(data) == int(no_of_ip_subnet):
                    for i in range(0, len(data)):
                        if str(data[i]["vrf"]) != str(1023):
                            helpers.test_failure("All CIDR routes not created with vrf 1023")
                else:
                    helpers.test_failure("All CIDR routes are not present at spine switches")
                    return False
        else:
            helpers.log("Given switch name and role is not valid")

    def rest_verify_forwarding_cidr_route_leaf(self, switch, no_of_ip_subnet):
        '''
        Function to verify the forwarding cidr table entry in all the switches
        Input: switch name , and no of ip subnet expected in the switch
        Output: True or false based on the no of routes to be present
        '''
        t = test.Test()
        c = t.controller('main')
        url = '/api/v1/data/controller/applications/bcf/info/forwarding/network/switch[switch-name="%s"]/l3-cidr-route-table' % (switch)
        c.rest.get(url)
        data = c.rest.content()
        url1 = '/api/v1/data/controller/applications/bcf/info/fabric/switch[name="%s"]' % (switch)
        c.rest.get(url1)
        data1 = c.rest.content()
        if data1[0]["name"] == switch and data1[0]["fabric-role"] == "leaf":
                if len(data) == int(no_of_ip_subnet):
                    helpers.log("All CIDR routes are present at leaf switches")
                else:
                    helpers.test_failure("All CIDR routes are not present at leaf switches")
                    return False
        else:
            helpers.log("Given switch name and role is not valid")

    def cli_get_qos_weight(self, node, port):
        t = test.Test()
        s = t.switch(node)
        string = 'debug ofad "qos_weight_info ' + port + '"'
        content = s.enable(string)['content']
        info = []
        temp = helpers.strip_cli_output(content, to_list=True)
        helpers.log("***temp is: %s  \n" % temp)

        for line in temp:
            helpers.log("***line is: %s  \n" % line)
            line = line.lstrip()
            match = re.match(r'queue=(\d+) ->.* weight=(\d+)', line)
            if match:
                helpers.log("INFO: queue is: %s,  weight is: %s" % (match.group(1), match.group(2)))
                info.append(match.group(2))

        helpers.log("***Exiting with info: %s  \n" % info)

        return info

    def cli_get_qos_port_stat(self, node, port):
        t = test.Test()
        s = t.switch(node)
        string = 'debug ofad "qos_port_stat ' + port + '"'
        content = s.enable(string)['content']
        info = []
        temp = helpers.strip_cli_output(content, to_list=True)
        helpers.log("***temp is: %s  \n" % temp)

        for line in temp:
            helpers.log("***line is: %s  \n" % line)
            line = line.lstrip()
            match = re.match(r'.*queue=(\d+).* out_pkt.*=(\d+)', line)
            if match:
                helpers.log("INFO: queue is: %s,  weight is: %s" % (match.group(1), match.group(2)))
                info.append(match.group(2))

        helpers.log("***Exiting with info: %s  \n" % info)

        return info

    def cli_qos_clear_stat(self, node, port):
        t = test.Test()
        s = t.switch(node)
        string = 'debug ofad "qos_clear_stat ' + port + '"'
        s.enable(string)

        return True



    def cli_get_links_nodes_list(self, node1, node2):
        '''
        '''
        helpers.test_log("Entering ==> cli_get_links_nodes_list: %s  - %s" % (node1, node2))
        t = test.Test()
        c = t.controller('main')
        cli = 'show link | grep ' + node1 + ' | grep ' + node2
        content = c.cli(cli)['content']
        temp = helpers.strip_cli_output(content, to_list=True)
        helpers.log("INFO: *** output  *** \n  %s" % temp)
        list = []
        for line in temp:
            line = line.lstrip()
            fields = line.split()
            helpers.log("fields: %s" % fields)
            if fields[1] == node1 :
                list.append(fields[2])
            elif fields[3] == node1 :
                list.append(fields[4])


        helpers.log("INFO: *** link info *** \n for %s: %s \n " % (node1, list))
        return list

    def rest_clear_blocked_endpoint(self, tenant, segment, mac):
        ''' Function to clear blocked endpoint
        Input: tenant, segment, mac address to be cleared
        Output: return true
        http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/info/endpoint-manager/clear[mac="90:e2:ba:6f:00:20"][segment="X1"][tenant="X"]
        '''
        t = test.Test()
        c = t.controller('main')
        helpers.test_log("Input arguments: tenant = %s segment name = %s mac address = %s " % (tenant, segment, mac))

        url = '/api/v1/data/controller/applications/bcf/info/endpoint-manager/clear[mac="%s"][segment="%s"][tenant="%s"]' % (mac, segment, tenant)
        try:
            c.rest.get(url)
        except:
            helpers.test_failure(c.rest.error())
        else:
            helpers.test_log("Output: %s" % c.rest.result_json())
            return c.rest.content()


    def rest_add_l2_endpoint_to_all_vns(self, tenant, switch, intf, mac="00:00:00:00:00:01", vlan=1):
        '''
        Function to add l2 endpoint to all created vns
        Input: tennat , switch , interface
        output : will add end into all vns in a tenant
        '''
        t = test.Test()
        c = t.controller('main')

        url = '/api/v1/data/controller/applications/bcf/info/endpoint-manager/segment[tenant="%s"]' % (tenant)
        c.rest.get(url)
        data = c.rest.content()
        data.sort(key=lambda x: x['name'])
        helpers.log("USR INFO: data after sort is %s" % (data))
        i = 0
        while (i < len(data)):
            j = int(vlan) + i
            endpoint = 'E' + str(j)
            url = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]/segment[name="%s"]/endpoint[name="%s"]' % (tenant, data[i]["name"], endpoint)
            c.rest.put(url, {"name": endpoint})
            c.rest.patch(url, {"mac": mac})
            url1 = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]/segment[name="%s"]/endpoint[name="%s"]/attachment-point' % (tenant, data[i]["name"], endpoint)
            c.rest.patch(url1, {"interface": intf, "switch": switch, "vlan": j})
            mac = helpers.get_next_mac(mac, "00:00:00:00:00:01")
            i = i + 1
        return True


    def rest_add_l3_endpoint_to_all_vns(self, tenant, switch, intf, mac="00:00:00:00:00:01", vlan=1):
        '''
        Function to add l3 endpoint to all created vns
        Input: tennat , switch , interface
        The ip address is taken from the logical interface, the last byte is modified to 253
        output : will add end into all vns in a tenant
        '''
        t = test.Test()
        c = t.controller('main')

        url = '/api/v1/data/controller/applications/bcf/info/logical-router-manager/interface/segment-interface[logical-router="%s"]' % (tenant)
        c.rest.get(url)
        data = c.rest.content()
        data.sort(key=lambda x: x['segment'])
        helpers.log("USR INFO: data after sort is %s" % (data))

        i = 0
        while (i < len(data)):
            j = int(vlan) + i
            endpoint = 'E' + str(j)
            url = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]/segment[name="%s"]/endpoint[name="%s"]' % (tenant, data[i]["segment"], endpoint)
            c.rest.put(url, {"name": endpoint})
            c.rest.patch(url, {"mac": mac})

            ip = data[i]["ip-cidr"].split('.')
            ip[3] = 253
            ipaddr = '.'.join(map(str, ip))
            c.rest.patch(url, {"ip-address": ipaddr})
            url1 = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]/segment[name="%s"]/endpoint[name="%s"]/attachment-point' % (tenant, data[i]["segment"], endpoint)
            c.rest.patch(url1, {"interface": intf, "switch": switch, "vlan": j})
            mac = helpers.get_next_mac(mac, "00:00:00:00:00:01")
            i = i + 1
        return True

    def rest_fabric_setting_global(self):
        '''
        Function to set the orchestration setting to global
        '''
        t = test.Test()
        c = t.controller('main')

        url = '/api/v1/data/controller/applications/bcf/global-setting?single=true'
        c.rest.get(url)
        url1 = '/api/v1/data/controller/applications/bcf/global-setting'
        c.rest.patch(url1, {"orchestration-mapping": "global"})
        return True

    def rest_fabric_setting_default(self):
        '''
        Function to set the orchestration setting to default
        '''
        t = test.Test()
        c = t.controller('main')

        url = '/api/v1/data/controller/applications/bcf/global-setting?single=true'
        c.rest.get(url)
        url1 = '/api/v1/data/controller/applications/bcf/global-setting'
        c.rest.patch(url1, {"orchestration-mapping": "default"})
        return True

    def rest_verify_segment_internal_vlan(self, tenant, vns, vlan_id):
        '''
        Function to verify the internal vlan ID
        '''
        t = test.Test()
        c = t.controller('main')

        url = '/api/v1/data/controller/applications/bcf/info/endpoint-manager/segment[name="%s"][tenant="%s"]' % (vns, tenant)
        c.rest.get(url)
        data = c.rest.content()
        if int(data[0]["internal-vlan"]) == int(vlan_id):
            helpers.log("Pass:Internal vlan is matching given external vlan")
            return True
        else:
            helpers.log("Fail:Internal vlan ID does not match given Vlan ID")
            return False

    def rest_get_dpid(self, switch):
        '''
        Function to get DPID from switch name
        '''
        t = test.Test()
        c = t.controller('main')

        url = '/api/v1/data/controller/applications/bcf/info/fabric/switch[name="%s"]' % (switch)
        c.rest.get(url)
        data = c.rest.content()
        dpid = data[0]["dpid"]
        return dpid

    def rest_get_fabric_interface_stats(self, switch, intf):
        ''' Function to return a switch fabric interface stats
        Input: switch and interface
        Output: contents from the switch interface or error
        GET http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/info/stats/interface/stats[interface/name="ethernet33"][switch-dpid="00:00:70:72:cf:b5:f0:e4"]?select=interface[name="ethernet33"]


REST-SIMPLE: http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/info/stats/interface/stats%5Binterface/name%3D%22ethernet33%22%5D%5Bswitch-dpid%3D%2200%3A00%3A70%3A72%3Acf%3Ab5%3Af0%3Ae4%22%5D?select=interface[name="ethernet33"] 0:00:00.019679 reply "[ {
  "interface" : [ {
    "counter" : {
      "rx-broadcast-packet" : 0,
      "rx-byte" : 0,
      "rx-drop" : 0,
      "rx-error" : 0,
      "rx-multicast-packet" : 0,
      "rx-unicast-packet" : 0,
      "tx-broadcast-packet" : 0,
      "tx-byte" : 4914,
      "tx-drop" : 0,
      "tx-error" : 0,
      "tx-multicast-packet" : 42,
      "tx-unicast-packet" : 0
    },
    "name" : "ethernet33",
    "number" : 33
  } ],
  "switch-dpid" : "00:00:70:72:cf:b5:f0:e4"
} ]"
GET http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/info/statistic/interface-counter[interface/name="ethernet30"][switch-dpid="00:00:70:72:cf:ab:3a:98"]?select=interface[name="ethernet30"] -- Aug 20

        '''
        t = test.Test()
        c = t.controller('main')
        dpid = self.rest_get_dpid(switch)
        helpers.test_log("Input arguments: switch = %s dpid = %s interface = %s" % (switch, dpid, intf))
        # url = '/api/v1/data/controller/applications/bcf/info/stats/interface/stats[interface/name="%s"][switch-dpid="%s"]?select=interface[name="%s"]' % (intf, dpid, intf)
        url = '/api/v1/data/controller/applications/bcf/info/statistic/interface-counter[interface/name="%s"][switch-dpid="%s"]?select=interface[name="%s"]' % (intf, dpid, intf)
        try:
            c.rest.get(url)
        except:
            helpers.test_failure(c.rest.error())
        else:
            return c.rest.content()

    def rest_get_fabric_interface_rate(self, switch, intf):
        ''' Function to return a switch fabric interface rate stats
        Input: switch and interface
        Output: contents from the switch interface or error
        GET http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/info/stats/interface/stats[interface/name="ethernet33"][switch-dpid="00:00:70:72:cf:b5:f0:e4"]?select=interface[name="ethernet33"]



        '''
        t = test.Test()
        c = t.controller('main')
        dpid = self.rest_get_dpid(switch)
        helpers.test_log("Input arguments: switch = %s dpid = %s interface = %s" % (switch, dpid, intf))
        # url = '/api/v1/data/controller/applications/bcf/info/stats/interface/stats[interface/name="%s"][switch-dpid="%s"]?select=interface[name="%s"]' % (intf, dpid, intf)
        url = '/api/v1/data/controller/applications/bcf/info/statistic/interface-rate[interface/name="%s"][switch-dpid="%s"]?select=interface[name="%s"]' % (intf, dpid, intf)
        try:
            c.rest.get(url)
        except:
            helpers.test_failure(c.rest.error())
        else:
            return c.rest.content()


    def rest_get_list_of_switch_connections(self):
        '''
        Function which returns all the connections between switches from controller perspective
        Input : None
        Output : List of connections
        '''
        t = test.Test()
        c = t.controller('main')
        url = '/api/v1/data/controller/applications/bcf/info/fabric?select=link'
        try:
            helpers.log("Trying to issue the command %s" % (url))
            c.rest.get(url)
            helpers.log("Could issue the command")
        except:
            helpers.test_failure(c.rest.error())
        data = c.rest.content()
        helpers.log("Data received from cmd is %s" % (data))
        # List of all switches will be stored in dpids
        # dpids = []
        # for i in data:
        #    dpids.append(i["dpid"])
        # Create a tuple of dpids
        # temp_dpid = [(a,b) for a in dpids for b in dpids if b !=a] # this will create a tuple but has [(a,b),(b,a)]
        # dpid_pair = list(set(map(lambda x: tuple(sorted(x)),temp_dpid))) # Removes repeated tuples
        con_l = []
        for link in data[0].values()[0]:
            dic = {}
            src_mac = re.sub(r'^(.+?):(.+?):', '', str(link[u'src'][u'switch-info'][u'switch-dpid']))
            dst_mac = re.sub(r'^(.+?):(.+?):', '', str(link[u'dst'][u'switch-info'][u'switch-dpid']))
            dic[str(link[u'src'][u'switch-info'][u'switch-name'])] = [src_mac, str(link[u'src'][u'interface'][u'number'])]
            dic[str(link[u'dst'][u'switch-info'][u'switch-name'])] = [dst_mac, str(link[u'dst'][u'interface'][u'number'])]
            con_l.append(dic)
        helpers.log("Final list of dictionary is %s" % con_l)
        return con_l

    def rest_check_sfp(self, lis):
        '''
        Function which returns list of links which has same sfp
        '''
        t = test.Test()
        c = t.controller('main')
        sl = SwitchLight.SwitchLight()
        for pair in lis:
            sw1_url = '/api/v1/data/controller/core/zerotouch/device[mac-address="%s"]/action/status/inventory' % (pair.values()[0][0])
            sw2_url = '/api/v1/data/controller/core/zerotouch/device[mac-address="%s"]/action/status/inventory' % (pair.values()[1][0])
            try:
                c.rest.get(sw1_url)
            except:
                helpers.test_failure(c.rest.error())
            sw1_data = c.rest.content()
            try:
                c.rest.get(sw2_url)
            except:
                helpers.test_failure(c.rest.error())
            sw2_data = c.rest.content()

            # print "sw1 data received is {}".format(sw1_data)
            # print "sw2 data received is {}".format(sw2_data)
            # Create a dictionary for both the data's
            sw1_dic = sl.parse_switch_op(str(sw1_data[0].values()[0]).split('\n'))
            sw2_dic = sl.parse_switch_op(str(sw2_data[0].values()[0]).split('\n'))

            helpers.log("*********Dictionary got for sw1 %s *****************" % (sw1_dic))
            helpers.log("*********Dictionary got for sw2 %s *****************" % (sw2_dic))

            # pair.values()[1][1] and pair.values()[0][1] has port # for a switch
            for sw1_link in sw1_dic:
                if sw1_link['Port'] == pair.values()[0][1]:
                    for sw2_link in sw2_dic:
                        if sw2_link['Port'] == pair.values()[1][1]:
                            if sw1_link['Vendor'] == sw2_link['Vendor'] and sw1_link['Model'] == sw2_link['Model']:
                                helpers.log("Port {} on sw1 {} and Port {} on sw2 {} have same model {} and vendor {}".format(sw1_link['Port'], pair.keys()[0], sw2_link['Port'], pair.keys()[1], sw1_link['Model'], sw1_link['Vendor']))





    def rest_set_vlan_mapping_mode(self, mode):
        '''
        Function to set vlan mapping to global mode
        PATCH http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/global-setting {"vlan-mapping": "global"}
        PATCH http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/global-setting {"vlan-mapping": "default"}
        '''
        t = test.Test()
        c = t.controller('main')
        url = '/api/v1/data/controller/applications/bcf/global-setting'
        try:
            c.rest.patch(url, {"vlan-mapping": mode})
        except:
            return False
        else:
            return True

    def rest_delete_vlan_mapping_mode(self, mode=None):
        '''
           Function to delete vlan mapping
            DELETE http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/global-setting {"vlan-mapping": "global"}
            DELETE http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/global-setting {"vlan-mapping": "default"}
        '''
        t = test.Test()
        c = t.controller('main')
        url = '/api/v1/data/controller/applications/bcf/global-setting'
        if mode is None:
            try:
                c.rest.delete(url, {"vlan-mapping": "default"})
            except:
                return False
            else:
                return True
        else:
            try:
                c.rest.delete(url, {"vlan-mapping": mode})
            except:
                return False
            else:
                return True

    def rest_add_vlan_membership(self, tenant, segment, vlanid):
        '''
            Function to add vlan membership rule to segment under global vlan-mapping mode
            PATCH http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/tenant[name="T-1"]/segment[name="T-1-1"] {"member-vlan": 5}
        '''
        t = test.Test()
        c = t.controller('main')
        helpers.test_log("Input arguments: tenant = %s segment = %s vlanid = %s" % (tenant, segment, vlanid))
        url = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]/segment[name="%s"]' % (tenant, segment)
        try:
            c.rest.patch(url, {"member-vlan": vlanid})
        except:
            return False
        else:
            return True


    def rest_delete_vlan_membership(self, tenant, segment):
        '''
            Function to delete vlan membership rule to segment under global vlan-mapping mode
            DELETE http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/tenant[name="T-1"]/segment[name="T-1-1"]/member-vlan {}
        '''
        t = test.Test()
        c = t.controller('main')
        helpers.test_log("Input arguments: tenant = %s segment = %s" % (tenant, segment))
        url = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]/segment[name="%s"]/member-vlan' % (tenant, segment)
        try:
            c.rest.delete(url, {})
        except:
            return False
        else:
            return True

    def rest_verify_tenant_segment_scale(self, tcount, ncount):
        '''Function to verify tenant and segemtn in each tenant
        Input: no of tenant expected , no of segment expected
        Output , Rest show tenant to verify each and number of segment in each tenant
        '''
        t = test.Test()
        c = t.controller('main')
        url = '/api/v1/data/controller/applications/bcf/info/endpoint-manager/tenant'
        c.rest.get(url)
        data = c.rest.content()
        if int(len(data)) == int(tcount):
            for i in range(0, len(data)):
                if int(data[i]["segment-count"]) != int(ncount):
                    helpers.test_failure("Expected segement count not correct in the tenant=%s" % (data[i]["name"]))
                    return False
        else:
            helpers.test_failure("Expected tenant count not correct Expected=%d , Actual=%d" % (int(tcount), int(len(data))))
            return False

