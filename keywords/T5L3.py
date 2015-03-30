import autobot.helpers as helpers
import autobot.restclient as restclient
import autobot.test as test
import re


class T5L3(object):

    def __init__(self):
        pass

    def rest_add_vns_ip(self, tenant, vns, ipaddr, netmask, private=False):
        '''Create vns router interface via command "logical-router vns interface"

            Input:
                `tenant`        tenant name
                `vns`           vns interface name which must be similar to VNS
                `ipaddr`        interface ip address
                `netmask`       vns subnet mask
                `private`        true or false
            POST http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/tenant%5Bname%3D%22X%22%5D/logical-router/segment-interface%5Bsegment%3D%22X1%22%5D/ip-subnet {"ip-cidr": "10.10.0.1/24", "private": false}
        REST-POST: POST http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/tenant%5Bname%3D%22X%22%5D/logical-router/segment-interface%5Bsegment%3D%22X2%22%5D/ip-subnet {"ip-cidr": "10.10.111.1/24", "private": false}

            Return: true if configuration is successful, false otherwise
        '''

        t = test.Test()
        c = t.controller('master')

        helpers.test_log("Input arguments: tenant = %s vns = %s ipaddr = %s netmask = %s private = %s " % (tenant, vns, ipaddr, netmask, private))
        url = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]/logical-router/segment-interface[segment="%s"]/ip-subnet' % (tenant, vns)
        ip_addr = ipaddr + "/" + netmask
        try:
            # c.rest.patch(url, {"ip-cidr": str(ip_addr)})
            # c.rest.post(url, {"segment": vns, "ip-cidr": str(ip_addr), "active": True})
#            c.rest.put(url, {"segment": vns, "ip-cidr": str(ip_addr)})
            c.rest.post(url, {"ip-cidr": str(ip_addr), "private": private})
        except:
            # helpers.test_failure(c.rest.error())
            return False
        else:
            # helpers.test_log("Output: %s" % c.rest.result_json())
            # return c.rest.content()
            return True

    def rest_delete_vns_ip(self, tenant, vnsname, ipaddr, netmask):
        '''Create vns router interface via command "logical-router vns interface"

            Input:
                `tenant`        tenant name
                `vnsname`       vns interface name which must be similar to VNS
                `ipaddr`        interface ip address
                `netmask`       vns subnet mask
REST-POST: DELETE http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/tenant%5Bname%3D%22X%22%5D/logical-router/segment-interface%5Bsegment%3D%22X1%22%5D/ip-subnet/ip-cidr {}
REST-POST: http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/tenant%5Bname%3D%22X%22%5D/logical-router/segment-interface%5Bsegment%3D%22X1%22%5D/ip-subnet/ip-cidr done 0:00:00.002873
REST-POST: DELETE http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/tenant%5Bname%3D%22X%22%5D/logical-router/segment-interface%5Bsegment%3D%22X1%22%5D/ip-subnet/private {}
REST-POST: http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/tenant%5Bname%3D%22X%22%5D/logical-router/segment-interface%5Bsegment%3D%22X1%22%5D/ip-subnet/private done 0:00:00.002920
            Return: true if configuration is successful, false otherwise
        '''

        t = test.Test()
        c = t.controller('master')
        helpers.test_log("Input arguments: tenant = %s vns = %s ipaddr = %s netmask = %s " % (tenant, vnsname, ipaddr, netmask))
        url = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]/logical-router/segment-interface[segment="%s"]/ip-subnet/ip-cidr' % (tenant, vnsname)
        ip_addr = ipaddr + "/" + netmask
        try:
            c.rest.delete(url, {})
        except:
            return False
            # helpers.test_failure(c.rest.error())
        else:
            # helpers.test_log("Output: %s" % c.rest.result_json())
            # return c.rest.content()
            return True


    def rest_enable_router_intf(self, tenant, tenantIntf):
        '''Create vns router interface via command "logical-router vns interface"

            Input:
                `tenant`        tenant name
                `vnsname`       vns interface name which must be similar to VNS
                `ipaddr`        interface ip address
                `netmask`       vns subnet mask
                DELETE http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/tenant[name="X"]/logical-router/tenant-interfaces[tenant-name="system"]/shutdown {}
                DELETE http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/tenant[name="system"]/logical-router/tenant-interfaces[tenant-name="X"]/shutdown {}
                DELETE http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/tenant[name="X"]/logical-router/tenant-interface[remote-tenant="system"]/shutdown {}
                Return: true if configuration is successful, false otherwise
        '''
        t = test.Test()
        c = t.controller('master')

        helpers.test_log("Input arguments: tenant = %s vnsname = %s  " % (tenant, tenantIntf))
        url = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]/logical-router/tenant-interface[remote-tenant="%s"]/shutdown' % (tenant, tenantIntf)
        try:
            c.rest.delete(url, {})
        except:
            return False
            # helpers.test_failure(c.rest.error())
        else:
            # helpers.test_log("Output: %s" % c.rest.result_json())
            # return c.rest.content()
            return True

    def rest_disable_router_intf(self, tenant, tenantIntf):
        '''Disable logical router tenant interface"

            Input:
                `tenant`        tenant name
                `vnsname`       vns interface name which must be similar to VNS
                `ipaddr`        interface ip address
                `netmask`       vns subnet mask
                PATCH http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/tenant[name="system"]/logical-router/tenant-interfaces[tenant-name="X"] {"shutdown": true}
                PATCH http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/tenant[name="X"]/logical-router/tenant-interfaces[tenant-name="system"] {"shutdown": true}
                PATCH http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/tenant[name="X"]/logical-router/tenant-interface[remote-tenant="system"] {"shutdown": true}
                Return: true if configuration is successful, false otherwise
        '''
        t = test.Test()
        c = t.controller('master')

        helpers.test_log("Input arguments: tenant = %s vnsname = %s  " % (tenant, tenantIntf))
        url = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]/logical-router/tenant-interface[remote-tenant="%s"]' % (tenant, tenantIntf)
        try:
            c.rest.patch(url, {"shutdown": True})
        except:
            return False
            # helpers.test_failure(c.rest.error())
        else:
            # helpers.test_log("Output: %s" % c.rest.result_json())
            # return c.rest.content()
            return True


    def rest_enable_router_segment_intf(self, tenant, vnsname):
        '''Create vns router interface via command "logical-router vns interface"

            Input:
                `tenant`        tenant name
                `vnsname`       vns interface name which must be similar to VNS
                `ipaddr`        interface ip address
                `netmask`       vns subnet mask
                DELETE http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/tenant[name="X"]/logical-router/segment-interface[segment="X2"]/shutdown {}
                Return: true if configuration is successful, false otherwise
        '''
        t = test.Test()
        c = t.controller('master')

        helpers.test_log("Input arguments: tenant = %s vnsname = %s  " % (tenant, vnsname))
        url = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]/logical-router/segment-interface[segment="%s"]/shutdown' % (tenant, vnsname)
        try:
            c.rest.delete(url, {})
        except:
            return False
            # helpers.test_failure(c.rest.error())
        else:
            # helpers.test_log("Output: %s" % c.rest.result_json())
            # return c.rest.content()
            return True

    def rest_disable_router_segment_intf(self, tenant, vnsname):
        '''Disable logical router segment interface
            http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/tenant[name="X"]/logical-router/segment-interface[segment="X2"] {"shutdown": true}
            PATCH http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/tenant[name="X"]/logical-router/segment-interface[segment="X1"] {"shutdown": true}
         '''
        t = test.Test()
        c = t.controller('master')

        helpers.test_log("Input arguments: tenant = %s vnsname = %s  " % (tenant, vnsname))
        url = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]/logical-router/segment-interface[segment="%s"]' % (tenant, vnsname)
        try:
            c.rest.patch(url, {"shutdown": True})
        except:
            return False
            # helpers.test_failure(c.rest.error())
        else:
            # helpers.test_log("Output: %s" % c.rest.result_json())
            # return c.rest.content()
            return True


    def rest_add_tenant_routers_intf_to_system(self, tenant):
        '''Attach tenant router to system tenant"

            Input:
                `tenant`        tenant name

            Return: true if configuration is successful, false otherwise
REST-POST: PUT http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/tenant[name="system"]/logical-router/tenant-interfaces[tenant-name="A"] {"tenant-name": "A"}
REST-POST: http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/tenant[name="system"]/logical-router/tenant-interfaces[tenant-name="A"] reply: ""

        '''

        t = test.Test()
        c = t.controller('master')

        helpers.test_log("Input arguments: tenant = %s " % (tenant))
        url = '/api/v1/data/controller/applications/bcf/tenant[name="system"]/logical-router/tenant-interface[remote-tenant="%s"]' % (tenant)
        try:
            # c.rest.post(url, {"tenant-name": tenant, "active": True})
            c.rest.put(url, {"remote-tenant": tenant})

        except:
            helpers.test_failure(c.rest.error())
        else:
            helpers.test_log("Output: %s" % c.rest.result_json())
            return c.rest.content()

    def rest_delete_tenant_routers_intf_to_system(self, tenant):
        '''detach tenant router to system tenant"

            Input:
                `tenant`        tenant name

            Return: true if configuration is successful, false otherwise
REST-POST: DELETE http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/tenant[name="system"]/logical-router/tenant-interface[tenant-name="A"] {}
       '''

        t = test.Test()
        c = t.controller('master')

        helpers.test_log("Input arguments: tenant = %s " % (tenant))
        url = '/api/v1/data/controller/applications/bcf/tenant[name="system"]/logical-router/tenant-interface[remote-tenant="%s"]' % (tenant)
        try:
            c.rest.delete(url, {})
        except:
            helpers.test_failure(c.rest.error())
        else:
            helpers.test_log("Output: %s" % c.rest.result_json())
            return c.rest.content()


    def rest_add_system_intf_to_tenant_routers(self, tenant):
        '''Attach system router to tenant router"

            Input:
                `tenant`        tenant name

            Return: true if configuration is successful, false otherwise

        '''

        t = test.Test()
        c = t.controller('master')

        helpers.test_log("Input arguments: tenant = %s " % (tenant))
        url = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]/logical-router/tenant-interface[remote-tenant="system"]' % (tenant)
        try:
            # c.rest.post(url, {"tenant-name": "system", "active": True})
            c.rest.put(url, {"remote-tenant": "system"})
        except:
            helpers.test_failure(c.rest.error())
        else:
            helpers.test_log("Output: %s" % c.rest.result_json())
            return c.rest.content()


    def rest_delete_system_intf_to_tenant_routers(self, tenant):
        '''detach system router from tenant router"

            Input:
                `tenant`        tenant name
 DELETE http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/tenant[name="T-1"]/logical-router/tenant-interface[remote-tenant="system"] {}
            Return: true if configuration is successful, false otherwise

        '''

        t = test.Test()
        c = t.controller('master')

        helpers.test_log("Input arguments: tenant = %s " % (tenant))
        url = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]/logical-router/tenant-interface[remote-tenant="system"]' % (tenant)
        try:
            c.rest.delete(url, {})
        except:
            helpers.test_failure(c.rest.error())
        else:
            helpers.test_log("Output: %s" % c.rest.result_json())
            return c.rest.content()

    def rest_add_static_routes(self, tenant, dstroute, nexthop=None):
        '''Add static routes to tenant router"

            Input:
                `tenant`          tenant name
                `dstroute`        destination subnet
                `nexthop`         nexthop IP address or nexthop tenant name or nexthop ecmp group name. e.g. of nexthop input is {"ip-address": "10.10.10.1"} or {"tenant-name": "B"} or {"ecmp-group-name": "e3"}
                more specific example REST add static routes(A, 10.10.11.0/24, {"ecmp-group-name": "e2"})

            Return: true if configuration is successful, false otherwise
            http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/tenant[name="X"]/logical-router/routes[dest-ip-subnet="10.10.0.0/16"] {"next-hop": {"tenant-name": "system"}, "dest-ip-subnet": "10.10.0.0/16"}
            http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/tenant[name="X"]/logical-router/routes[dest-ip-subnet="10.192.0.0/16"] {"dest-ip-subnet": "10.192.0.0/16"}
            REST-POST: PUT http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/tenant[name="Z"]/logical-router/routes[dest-ip-subnet="10.99.0.0/24"] {"next-hop": {"next-hop-group": "AA2"}, "dest-ip-subnet": "10.99.0.0/24"}
            {"next-hop": {"tenant-name": "system"}, "dest-ip-subnet": "0.0.0.0/0"}
            routes pointing to tenant system:
            PUT http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/tenant[name="X"]/logical-router/static-route[dst-ip-subnet="10.10.10.0/24"] {"next-hop": {"tenant": "system"}, "dst-ip-subnet": "10.10.10.0/24"}
            routes pointing to nexthop group:
            PUT http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/tenant[name="X"]/logical-router/static-route[dst-ip-subnet="10.255.11.0/24"] {"next-hop": {"next-hop-group": "ecmp-aa"}, "dst-ip-subnet": "10.255.11.0/24"}
            routes pointing to null:
            PUT http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/tenant[name="X"]/logical-router/static-route[dst-ip-subnet="10.255.11.0/24"] {"dst-ip-subnet": "10.255.11.0/24"}
            http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/tenant[name="system"]/logical-router/static-route[dst-ip-subnet="10.99.255.0/24"]
            {"next-hop": {"next-hop-group": "ecmp-A1", "tenant": "External"}, "dst-ip-subnet": "10.99.255.0/24"}
        '''

        t = test.Test()
        c = t.controller('master')
        helpers.test_log("Input arguments: tenant = %s dstroute = %s nexthop = %s " % (tenant, dstroute, nexthop))
        url = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]/logical-router/static-route[dst-ip-subnet="%s"]' % (tenant, dstroute)

        helpers.log("nexthop: %s" % nexthop)
        if nexthop is not None:
            try:

                nexthop_dict = helpers.from_json(nexthop)
                # nexthop_dict["dest-ip-subnet"] = dstroute
                # c.rest.post(url, {"dest-ip-subnet": dstroute, "next-hop": nexthop_dict})
                c.rest.put(url, {"next-hop": nexthop_dict, "dst-ip-subnet": dstroute})
            except:
                helpers.test_failure(c.rest.error())
            else:
                helpers.test_log("Output: %s" % c.rest.result_json())
                return c.rest.content()
        else:
            try:
                # c.rest.post(url, {"dst-ip-subnet": dstroute})
                c.rest.put(url, {"dst-ip-subnet": dstroute})
            except:
                helpers.test_failure(c.rest.error())
            else:
                helpers.test_log("Output: %s" % c.rest.result_json())
                return c.rest.content()


    def rest_delete_static_routes(self, tenant, dstroute, nexthop=None):
        '''Add static routes to tenant router"

            Input:
                `tenant`          tenant name
                `dstroute`        destination subnet
                Return: true if configuration is successful, false otherwise
            cli delete route with nexthop:
            DELETE http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/tenant[name="X"]/logical-router/static-route[dst-ip-subnet="10.252.0.0/16"][next-hop/tenant="system"] {}
            cli delete route only:
            DELETE http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/tenant[name="X"]/logical-router/static-route[dst-ip-subnet="10.252.0.0/16"] {}
            DELETE http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/tenant[name="X"]/logical-router/static-route[dst-ip-subnet="0.0.0.0/0"][next-hop/tenant="system"] {}
        '''

        t = test.Test()
        c = t.controller('master')

        helpers.test_log("Input arguments: tenant = %s dstroute = %s " % (tenant, dstroute))
        if nexthop is None:
            url = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]/logical-router/static-route[dst-ip-subnet="%s"]' % (tenant, dstroute)
            try:
                # c.rest.delete(url, {"dest-ip-subnet": dstroute})
                c.rest.delete(url, {})
            except:
                helpers.test_failure(c.rest.error())
            else:
                helpers.test_log("Output: %s" % c.rest.result_json())
                return c.rest.content()
        else:
            url = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]/logical-router/static-route[dst-ip-subnet="%s"][next-hop/tenant="%s"]' % (tenant, dstroute, nexthop)
            try:
                # c.rest.delete(url, {"dest-ip-subnet": dstroute})
                c.rest.delete(url, {})
            except:
                helpers.test_failure(c.rest.error())
            else:
                helpers.test_log("Output: %s" % c.rest.result_json())
                return c.rest.content()

    def rest_show_endpoints(self):
        t = test.Test()
        c = t.controller('master')
        url = '/api/v1/data/controller/applications/bcf/info/endpoint-manager/endpoint'
        c.rest.get(url)
        helpers.log("Output: %s" % c.rest.result_json())
        data = c.rest.content()
        return data

    def rest_show_endpoints_name(self, endpointname):
        t = test.Test()
        c = t.controller('master')
        endptname = "%5Bname%3D%22" + endpointname + "%22%5D"
        url = '/api/v1/data/controller/applications/bcf/info/endpoint-manager/endpoint%s' % (endptname)
        c.rest.get(url)
        helpers.log("Output: %s" % c.rest.result_json())
        data = c.rest.content()
        return data

    def rest_show_endpoints_mac(self, mac):
        '''
        REST-SIMPLE: GET http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/info/endpoint-manager/endpoint%5Bmac%3D%2290%3Ae2%3Aba%3A4e%3Abb%3A90%22%5D

        %5Bmac%3D%2200%3A00%3A00%3A00%3A00%3A01%22%5D
        '''
        t = test.Test()
        c = t.controller('master')

#        str1 = mac.replace(":", "%3A")
#        str3 = str2.replace("\n", "")
#        str4 = str3.replace("\r", "")
#        str1 = str4.replace(" ", "")
#        mac_addr = "%5Bmac%3D%22" + str1 + "%22%5D"
#        url = '/api/v1/data/controller/applications/bcf/info/endpoint-manager/endpoints%s' % (mac_addr)
        url = '/api/v1/data/controller/applications/bcf/info/endpoint-manager/endpoint[mac="%s"]' % (mac)

        c.rest.get(url)
        helpers.log("Output: %s" % c.rest.result_json())
        data = c.rest.content()
#        match = re.search(r'None', data, re.S)
#       if match:
#          return ""
#        else:
#            return data
        helpers.log("data: %s" % data)
        return data

    def rest_show_endpoints_ip_state(self, mac):
        '''
            GET http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/info/endpoint-manager/endpoint[mac="00:00:99:00:00:32"]
            Input: mac address of endpoint
            Return: state of endpoints IP address if found
        '''
        t = test.Test()
        c = t.controller('master')

#        str1 = mac.replace(":", "%3A")
#        str3 = str2.replace("\n", "")
#        str4 = str3.replace("\r", "")
#        str1 = str4.replace(" ", "")
#        mac_addr = "%5Bmac%3D%22" + str1 + "%22%5D"
#        url = '/api/v1/data/controller/applications/bcf/info/endpoint-manager/endpoints%s' % (mac_addr)
        url = '/api/v1/data/controller/applications/bcf/info/endpoint-manager/endpoint[mac="%s"]' % (mac)

        c.rest.get(url)
        helpers.log("Output: %s" % c.rest.result_json())
        data = c.rest.content()
        if "ip-address" in data[0]:
            state = data[0]["ip-address"][0]["ip-state"]
            return state
        else:
            return False



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
        c = t.controller('master')

        helpers.test_log("Input arguments: tenant = %s ecmpgroup = %s" % (tenant, ecmpgroup))
        url = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]/logical-router/ecmp-groups' % (tenant)
        try:
            c.rest.post(url, {"name": ecmpgroup})
        except:
            helpers.test_failure(c.rest.error())
        else:
            helpers.test_log("Output: %s" % c.rest.result_json())
            return c.rest.content()

    def rest_add_nexthop_group(self, tenant, groupName):
        '''Add nexthop group in tenant"

            Input:
                `tenant`          tenant name
                `groupName`        next hop group name
            Return: true if configuration is successful, false otherwise
            PUT http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/tenant[name="Z"]/logical-router/next-hop-group[name="AA1"] {"name": "AA1"}

        '''

        t = test.Test()
        c = t.controller('master')

        helpers.test_log("Input arguments: tenant = %s groupName = %s" % (tenant, groupName))
        url = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]/logical-router/next-hop-group[name="%s"]' % (tenant, groupName)
        try:
            c.rest.put(url, {"name": groupName})
        except:
            helpers.test_failure(c.rest.error())
        else:
            helpers.test_log("Output: %s" % c.rest.result_json())
            return c.rest.content()

    def rest_delete_nexthop_group(self, tenant, groupName):
        '''Delete nexthop group in tenant"

            Input:
                `tenant`          tenant name
                `groupName`        next hop group name
            Return: true if configuration is successful, false otherwise
            REST-POST: DELETE http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/tenant[name="Z"]/logical-router/next-hop-group[name="AA1"] {}
        '''

        t = test.Test()
        c = t.controller('master')

        helpers.test_log("Input arguments: tenant = %s groupName = %s" % (tenant, groupName))
        url = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]/logical-router/next-hop-group[name="%s"]' % (tenant, groupName)
        try:
            c.rest.delete(url, {})
        except:
            helpers.test_failure(c.rest.error())
        else:
            helpers.test_log("Output: %s" % c.rest.result_json())
            return c.rest.content()


    def rest_add_gw_pool_nexthop(self, tenant, ecmpgroup, nexthop):
        '''Add nexthop groups aks gateway pool in tenant"

            Input:
                `tenant`         tenant name
                `ecmpgroup`      pool or ecmp groups name
                `nexthop`        nexthop IP address
            Return: true if configuration is successful, false otherwise
        '''

        t = test.Test()
        c = t.controller('master')

        helpers.test_log("Input arguments: tenant = %s ecmpgroup = %s nexthop = %s" % (tenant, ecmpgroup, nexthop))
        url = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]/logical-router/ecmp-groups[name="%s"]/ip-addresses' % (tenant, ecmpgroup)
        try:
#            c.rest.put(url, {"ip-address": nexthop})
            c.rest.post(url, {"ip-address": nexthop})
        except:
            helpers.test_failure(c.rest.error())
        else:
            helpers.test_log("Output: %s" % c.rest.result_json())
            return c.rest.content()

    def rest_add_nexthopGroup_ip(self, tenant, groupName, nexthop):
        '''Add nexthop IP to nexthop groups"

            Input:
                `tenant`         tenant name
                `groupName`      nexthop group name
                `nexthop`        nexthop IP address
            Return: true if configuration is successful, false otherwise
            PUT http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/tenant[name="Z"]/logical-router/next-hop-group[name="AA1"]/ip-addresses[ip-address="10.99.0.1"] {"ip-address": "10.99.0.1"}
            PUT http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/tenant[name="E"]/logical-router/next-hop-group[name="AA1"]/ip-address[ip-address="10.99.99.1"] {"ip-address": "10.99.99.1"}
        '''

        t = test.Test()
        c = t.controller('master')

        helpers.test_log("Input arguments: tenant = %s groupName = %s nexthop = %s" % (tenant, groupName, nexthop))
        url = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]/logical-router/next-hop-group[name="%s"]/ip-address[ip-address="%s"] ' % (tenant, groupName, nexthop)
        try:
#            c.rest.put(url, {"ip-address": nexthop})
            c.rest.post(url, {"ip-address": nexthop})
        except:
            # helpers.test_failure(c.rest.error())
            return False
        else:
            helpers.test_log("Output: %s" % c.rest.result_json())
            # return c.rest.content()
            return True

    def rest_delete_nexthopGroup_ip(self, tenant, groupName, nexthop):
        '''Delete nexthop IP in nexthop group"
            Input:
                `tenant`         tenant name
                `groupName`      nexthop group name
                `nexthop`        nexthop IP address
            Return: true if configuration is successful, false otherwise
          REST-POST: DELETE http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/tenant[name="Z"]/logical-router/next-hop-group[name="AA1"]/ip-addresses[ip-address="10.99.0.1"] {}
                     DELETE http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/tenant[name="E"]/logical-router/next-hop-group[name="AA1"]/ip-address[ip-address="10.99.99.1"] {}


      '''
        t = test.Test()
        c = t.controller('master')

        helpers.test_log("Input arguments: tenant = %s groupName = %s nexthop = %s" % (tenant, groupName, nexthop))
        url = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]/logical-router/next-hop-group[name="%s"]/ip-address[ip-address="%s"] ' % (tenant, groupName, nexthop)
        try:
#            c.rest.put(url, {"ip-address": nexthop})
            c.rest.delete(url, {})
        except:
            # helpers.test_failure(c.rest.error())
            return False
        else:
            helpers.test_log("Output: %s" % c.rest.result_json())
            # return c.rest.content()
            return True


    def rest_add_endpoint_ip(self, tenant, vnsname, endpointname, ipaddr):
        '''Add ip address to static endpoint"

            Input:
                `tenant`          tenant name
                `vnsname`         vns name
                `endpointname`    endpoint name
                `ipaddr`          host IP address
            Return: true if configuration is successful, false otherwise
            http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/tenant[name="A"]/segment[name="A1"]/endpoint[name="H1"] {"name": "H1"}
        PUT http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/tenant[name="X"]/segment[name="X1"]/endpoint[name="H1"]/ip-address[ip-address="10.251.1.88"] {"ip-address": "10.251.1.88"}
        '''

        t = test.Test()
        c = t.controller('master')

        helpers.test_log("Input arguments: tenant = %s vnsname = %s endpointname = %s ipaddress = %s" % (tenant, vnsname, endpointname, ipaddr))
        url = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]/segment[name="%s"]/endpoint[name="%s"]/ip-address[ip-address="%s"]' % (tenant, vnsname, endpointname, ipaddr)
        try:
            # c.rest.patch(url, {"ip-address": ipaddr})
            c.rest.put(url, {"ip-address": ipaddr})
        except:
            helpers.test_failure(c.rest.error())
        else:
            helpers.test_log("Output: %s" % c.rest.result_json())
            return c.rest.content()

    def rest_delete_endpoint_ip(self, tenant, vnsname, endpointname, ipaddr):
        t = test.Test()
        c = t.controller('master')

        helpers.test_log("Input arguments: tenant = %s vnsname = %s endpointname = %s ip address = %s" % (tenant, vnsname, endpointname, ipaddr))
        url = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]/segment[name="%s"]/endpoint[name="%s"]/ip-address' % (tenant, vnsname, endpointname)
        try:
            c.rest.delete(url, {})
        except:
            helpers.test_failure(c.rest.error())
        else:
            helpers.test_log("Output: %s" % c.rest.result_json())
            return c.rest.content()


    def rest_add_endpoint_mac(self, tenant, vnsname, endpointname, mac):
        '''Add mac address to static endpoint"

            Input:
                `tenant`          tenant name
                `vnsname`         vns name
                `endpointname`    endpoint name
                `mac`          host mac address
            Return: true if configuration is successful, false otherwise
            http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/tenant[name="A"]/segment[name="A1"]/endpoint[name="H1"] {"name": "H1"}

        '''

        t = test.Test()
        c = t.controller('master')

        helpers.test_log("Input arguments: tenant = %s vnsname = %s endpointname = %s mac address = %s" % (tenant, vnsname, endpointname, mac))
        url = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]/segment[name="%s"]/endpoint[name="%s"]' % (tenant, vnsname, endpointname)
        try:
            c.rest.patch(url, {"mac": mac})
        except:
            helpers.test_failure(c.rest.error())
        else:
            helpers.test_log("Output: %s" % c.rest.result_json())
            return c.rest.content()


    def rest_delete_endpoint_mac(self, tenant, vnsname, endpointname, mac):
        '''Delete static endpoint mac address"

            Input:
                `tenant`          tenant name
                `vnsname`         vns name
                `endpointname`    endpoint name
                `mac`          host mac address
            Return: true if configuration is successful, false otherwise
            http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/tenant[name="A"]/segment[name="A1"]/endpoint[name="H1"] {"name": "H1"}
            DELETE http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/tenant[name="A"]/segment[name="A1"]/endpoint[name="bm0"]/mac {}

        '''

        t = test.Test()
        c = t.controller('master')

        helpers.test_log("Input arguments: tenant = %s vnsname = %s endpointname = %s mac address = %s" % (tenant, vnsname, endpointname, mac))
        url = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]/segment[name="%s"]/endpoint[name="%s"]/mac' % (tenant, vnsname, endpointname)
        try:
            c.rest.delete(url, {})
        except:
            helpers.test_failure(c.rest.error())
        else:
            helpers.test_log("Output: %s" % c.rest.result_json())
            return c.rest.content()

    def rest_add_endpoint_portgroup_attachment(self, tenant, vnsname, endpointname, portgroupname, vlan):
        '''Add static endpoint port-group"

            Input:
                `tenant`          tenant name
                `vnsname`         vns name
                `endpointname`    endpoint name
                `portgroupname`   port-group name
                `vlan`            vlan id or -1 for untagged
            Return: true if configuration is successful, false otherwise
            curl -gX PATCH -H 'Cookie: session_cookie=RKIUFOl07Dqiz10nXJcbquvUcWVJ3xYM' -d '{"port-group-name": "leaf4", "vlan": -1}' 'localhost:8080/api/v1/data/controller/applications/bcf/tenant[name="B"]/segment[name="B1"]/endpoints[name="B1-H1"]/attachment-point'
            REST-POST: PATCH http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/tenant%5Bname%3D%22X%22%5D/segment%5Bname%3D%22X1%22%5D/endpoint%5Bname%3D%22H1%22%5D/attachment-point {"vlan": 200, "port-group": "leaf0-pc1"}
            REST-POST: http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/tenant%5Bname%3D%22X%22%5D/segment%5Bname%3D%22X1%22%5D/endpoint%5Bname%3D%22H1%22%5D/attachment-point done 0:00:00.005086

        '''

        t = test.Test()
        c = t.controller('master')

        helpers.test_log("Input arguments: tenant = %s vnsname = %s endpointname = %s portgroup = %s vlan = %s" % (tenant, vnsname, endpointname, portgroupname, vlan))
        url = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]/segment[name="%s"]/endpoint[name="%s"]/attachment-point' % (tenant, vnsname, endpointname)
        try:
            c.rest.post(url, {"vlan": vlan, "port-group": portgroupname})
        except:
            helpers.test_failure(c.rest.error())
        else:
            helpers.test_log("Output: %s" % c.rest.result_json())
            return c.rest.content()




    def rest_delete_endpoint_portgroup_attachment(self, tenant, vnsname, endpointname, portgroupname, vlan):
        '''Delete static endpoint portgroup"

            Input:
                `tenant`          tenant name
                `vnsname`         vns name
                `endpointname`    endpoint name
                `portgroupname`   port-group name
                `vlan`            vlan id or -1 for untagged
            Return: true if configuration is successful, false otherwise
REST-POST: DELETE http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/tenant%5Bname%3D%22X%22%5D/segment%5Bname%3D%22X1%22%5D/endpoint%5Bname%3D%22H1%22%5D/attachment-point {"vlan": 200, "port-group": "leaf0-pc1"}
REST-POST: http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/tenant%5Bname%3D%22X%22%5D/segment%5Bname%3D%22X1%22%5D/endpoint%5Bname%3D%22H1%22%5D/attachment-point done 0:00:00.004887
REST-POST: DELETE http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/tenant%5Bname%3D%22X%22%5D/segment%5Bname%3D%22X1%22%5D/endpoint%5Bname%3D%22H1%22%5D/attachment-point {"vlan": 200, "port-group": "leaf0-pc1"}
REST-POST: http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/tenant%5Bname%3D%22X%22%5D/segment%5Bname%3D%22X1%22%5D/endpoint%5Bname%3D%22H1%22%5D/attachment-point done 0:00:00.002376
      '''

        t = test.Test()
        c = t.controller('master')

        helpers.test_log("Input arguments: tenant = %s vnsname = %s endpointname = %s portgroup = %s vlan = %s" % (tenant, vnsname, endpointname, portgroupname, vlan))
        url = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]/segment[name="%s"]/endpoint[name="%s"]/attachment-point' % (tenant, vnsname, endpointname)
        try:
            c.rest.delete(url, {"vlan": vlan, "port-group": portgroupname})
        except:
            helpers.test_failure(c.rest.error())
        else:
            helpers.test_log("Output: %s" % c.rest.result_json())
            return c.rest.content()



    def rest_add_endpoint_switch_attachment(self, tenant, vnsname, endpointname, switchname, switchinterface, vlan):
        '''add static endpoint switch port"
            Input:
                `tenant`          tenant name
                `vnsname`         vns name
                `endpointname`    endpoint name
                `switchname`       name of switch
                `switchinterface`    switch port
                `vlan`            vlan id or -1 for untagged
            Return: true if configuration is successful, false otherwise
     REST-POST: PATCH http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/tenant%5Bname%3D%22X%22%5D/segment%5Bname%3D%22X1%22%5D/endpoint%5Bname%3D%22H1%22%5D/attachment-point {"interface": "ethernet22", "switch": "leaf0-a", "vlan": 10}
    REST-POST: http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/tenant%5Bname%3D%22X%22%5D/segment%5Bname%3D%22X1%22%5D/endpoint%5Bname%3D%22H1%22%5D/attachment-point done 0:00:00.004528
        '''
        t = test.Test()
        c = t.controller('master')

        helpers.test_log("Input arguments: tenant = %s vnsname = %s endpointname = %s switchname = %s switch interface = %s vlan = %s" % (tenant, vnsname, endpointname, switchname, switchinterface, vlan))
        url = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]/segment[name="%s"]/endpoint[name="%s"]/attachment-point' % (tenant, vnsname, endpointname)
        try:
            c.rest.post(url, {"interface": switchinterface, "switch": switchname, "vlan": vlan})
        except:
            helpers.test_failure(c.rest.error())
        else:
            helpers.test_log("Output: %s" % c.rest.result_json())
            return c.rest.content()

    def rest_delete_endpoint_switch_attachment(self, tenant, vnsname, endpointname, switchname, switchinterface, vlan):
        '''Delete static endpoint switch port"

            Input:
                `tenant`          tenant name
                `vnsname`         vns name
                `endpointname`    endpoint name
                `switchname`       name of switch
                `switchinterface`    switch port
                `vlan`            vlan id or -1 for untagged
            Return: true if configuration is successful, false otherwise
REST-POST: DELETE http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/tenant%5Bname%3D%22X%22%5D/segment%5Bname%3D%22X1%22%5D/endpoint%5Bname%3D%22H1%22%5D/attachment-point {"interface": "ethernet22", "switch": "leaf0-a", "vlan": 10}
REST-POST: http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/tenant%5Bname%3D%22X%22%5D/segment%5Bname%3D%22X1%22%5D/endpoint%5Bname%3D%22H1%22%5D/attachment-point done 0:00:00.010011
REST-POST: DELETE http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/tenant%5Bname%3D%22X%22%5D/segment%5Bname%3D%22X1%22%5D/endpoint%5Bname%3D%22H1%22%5D/attachment-point {"interface": "ethernet22", "switch": "leaf0-a", "vlan": 10}
REST-POST: http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/tenant%5Bname%3D%22X%22%5D/segment%5Bname%3D%22X1%22%5D/endpoint%5Bname%3D%22H1%22%5D/attachment-point done 0:00:00.003425
REST-POST: DELETE http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/tenant%5Bname%3D%22X%22%5D/segment%5Bname%3D%22X1%22%5D/endpoint%5Bname%3D%22H1%22%5D/attachment-point {"interface": "ethernet22", "switch": "leaf0-a", "vlan": 10}

       '''
        t = test.Test()
        c = t.controller('master')

        helpers.test_log("Input arguments: tenant = %s vnsname = %s endpointname = %s switchname = %s switch interface = %s vlan = %s" % (tenant, vnsname, endpointname, switchname, switchinterface, vlan))
        url = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]/segment[name="%s"]/endpoint[name="%s"]/attachment-point' % (tenant, vnsname, endpointname)
        try:
            c.rest.delete(url, {"interface": switchinterface, "switch": switchname, "vlan": vlan})
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
REST-POST: PATCH http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/tenant[name="C"]/logical-router/segment-interface[segment="C1"] {"dhcp-server-ip": "10.2.1.1"}
REST-POST: http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/tenant[name="C"]/logical-router/segment-interface[segment="C1"] reply:
        '''
        t = test.Test()
        c = t.controller('master')

        helpers.test_log("Input arguments: tenant = %s vns name = %s relay-ip = %s" % (tenant, vnsname, dhcpserverip))
        url = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]/logical-router/segment-interface[segment="%s"]/dhcp-relay' % (tenant, vnsname)
        try:
            c.rest.patch(url, {"server-ip": dhcpserverip})
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
REST-POST: PATCH http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/tenant[name="C"]/logical-router/segment-interface[segment="C1"]/dhcp-relay {"dhcp-relay-enable": true}
<<<<<<< HEAD
REST-POST: http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/tenant[name="C"]/logical-router/segment-interface[segment="C1"] reply: ""
REST-POST: http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/tenant[name="C"]/logical-router/segment-interface[segment="C1"] reply: ""
        '''
        t = test.Test()
        c = t.controller('master')

        helpers.test_log("Input arguments: tenant = %s vns name = %s " % (tenant, vnsname))
        url = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]/logical-router/segment-interface[segment="%s"]/dhcp-relay' % (tenant, vnsname)
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
REST-POST: PATCH http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/tenant[name="C"]/logical-router/segment-interface[segment="C1"] {"dhcp-relay-enable": true}
REST-POST: http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/tenant[name="C"]/logical-router/segment-interface[segment="C1"] reply: ""
        '''
        t = test.Test()
        c = t.controller('master')

        helpers.test_log("Input arguments: tenant = %s vns name = %s " % (tenant, vnsname))
        url = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]/logical-router/segment-interface[segment="%s"]/dhcp-relay' % (tenant, vnsname)
        try:
            c.rest.patch(url, {"dhcp-relay-enable": False})
        except:
            helpers.test_failure(c.rest.error())
        else:
            helpers.test_log("Output: %s" % c.rest.result_json())
            return c.rest.content()

    def rest_add_dhcprelay_circuitid(self, tenant, vnsname, dhcpserverip, circuitid):
        '''Set dhcp relay circuit id"

            Input:
                `tenant`          tenant name
                `vnsname`         name of vns interface
                `circuitid`      Circuit id, can be a string upto 15 characters
            Return: true if configuration is successful, false otherwise
REST-POST: PATCH http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/tenant[name="C"]/logical-router/segment-interface[segment="C1"] {"dhcp-circuit-id": "this is a test"}
<<<<<<< HEAD
REST-POST: http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/tenant[name="C"]/logical-router/segment-interface[segment="C1"] reply: ""
PUT http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/tenant[name="Y"]/logical-router/segment-interface[segment="Y3"]/dhcp-relay {"circuit-id": "11111", "server-ip": "10.251.1.11"}
        '''
        t = test.Test()
        c = t.controller('master')

        helpers.test_log("Input arguments: tenant = %s vns name = %s dhcp server ip = %s circuit id = %s" % (tenant, vnsname, dhcpserverip, circuitid))
        url = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]/logical-router/segment-interface[segment="%s"]/dhcp-relay' % (tenant, vnsname)
        try:
            c.rest.patch(url, {"circuit-id": circuitid, "server-ip": dhcpserverip})
        except:
            helpers.test_failure(c.rest.error())
        else:
            helpers.test_log("Output: %s" % c.rest.result_json())
            return c.rest.content()


    def rest_delete_dhcp_relay(self, tenant, vnsname, dhcpserverip=None, dhcpcircuitid=None):
        '''Delete dhcp server "

            Input:
                `tenant`          tenant name
                `vnsname`         name of vns interface
                `dhcpserverip`       DHCP server IP, can be anything since it will delete everything under the vns
            Return: true if configuration is successful, false otherwise
REST-POST: DELETE http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/tenant[name="B"]/logical-router/segment-interface[segment="B1"]/dhcp-server-ip {}
<<<<<<< HEAD

        '''
        t = test.Test()
        c = t.controller('master')

        helpers.test_log("Input arguments: tenant = %s vns name = %s dhcp server ip = %s" % (tenant, vnsname, dhcpserverip))
        url = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]/logical-router/segment-interface[segment="%s"]/dhcp-relay/server-ip' % (tenant, vnsname)
        if dhcpserverip is not None:
            url1 = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]/logical-router/segment-interface[segment="%s"]/dhcp-relay[server-ip="%s"]' % (tenant, vnsname, dhcpserverip)
            c.rest.get(url1)
            data = c.rest.content()
            helpers.log ("result: %s" % helpers.prettify(data))
            if len(data) == 0:
                helpers.log ("dhcp server ip is not configured on this segment")
                return False
        try:

#            self.rest_disable_dhcp_relay(tenant, vnsname)
            c.rest.delete(url, {})
        except:
            helpers.test_failure(c.rest.error())
            return False
        else:
            helpers.test_log("Output: %s" % c.rest.result_json())
            # return c.rest.content()
            return True

    def rest_show_forwarding_switch_l3_host_route(self, switch):
        '''
    GET http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/info/forwarding/network/switch%5Bswitch-name%3D%22leaf0a%22%5D/l3-host-route-table
        '''
        t = test.Test()
        c = t.controller('master')

        helpers.test_log("Input arguments: switch = %s " % (switch))
        url = '/api/v1/data/controller/applications/bcf/info/forwarding/network/switch[switch-name="%s"]/l3-host-route-table' % (switch)
        try:
            c.rest.get(url)
        except:
            helpers.test_failure(c.rest.error())
        else:
            return c.rest.content()

    def rest_show_forwarding_switch_l3_cidr_route(self, switch=None):
        '''
    GET http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/info/forwarding/network/switch%5Bswitch-name%3D%22leaf0a%22%5D/l3-cidr-route-table
    GET http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/info/forwarding/network/global/l3-cidr-table
        '''
        t = test.Test()
        c = t.controller('master')
        if switch is not None:
            helpers.test_log("Input arguments: switch = %s " % (switch))
            url = '/api/v1/data/controller/applications/bcf/info/forwarding/network/switch[switch-name="%s"]/l3-cidr-route-table' % (switch)
            try:
                c.rest.get(url)
            except:
                helpers.test_failure(c.rest.error())
            else:
                return c.rest.content()
        else:
            url = '/api/v1/data/controller/applications/bcf/info/forwarding/network/global/l3-cidr-table'
            try:
                c.rest.get(url)
            except:
                helpers.test_failure(c.rest.error())
            else:
                return c.rest.content()


    def rest_show_l3_cidr_table(self):
        '''
        GET http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/info/forwarding/network/global/l3-cidr-table
        GET http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/info/forwarding/network/l3-cidr-table
        '''
        t = test.Test()
        c = t.controller('master')
        url = '/api/v1/data/controller/applications/bcf/info/forwarding/network/global/l3-cidr-table'
        try:
            c.rest.get(url)
        except:
            helpers.test_failure(c.rest.error())
        else:
            return c.rest.content()

    def rest_show_l3_host_table(self):
        '''
        GET http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/info/forwarding/network/global/l3-host-table

        GET http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/info/forwarding/network/l3-host-table
        '''
        t = test.Test()
        c = t.controller('master')

        url = '/api/v1/data/controller/applications/bcf/info/forwarding/network/global/l3-host-table'
        try:
            c.rest.get(url)
        except:
            helpers.test_failure(c.rest.error())
        else:
            return c.rest.content()


    def rest_add_policy(self, tenant, polname):
        '''Create a tenant policy

            Input:
                `tenant`        tenant name
                `polname`        name of policy

            Return: true if configuration is successful, false otherwise
        '''

        t = test.Test()
        c = t.controller('master')

        helpers.test_log("Input arguments: tenant = %s policy name = %s  " % (tenant, polname))

        # url = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]/logical-router/segment-interface' % (tenant)
        url = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]/logical-router/policy-list[name="%s"]' % (tenant, polname)
        try:
            c.rest.post(url, {"name": polname})
        except:
            # helpers.test_failure(c.rest.error())
            return False
        else:
            # helpers.test_log("Output: %s" % c.rest.result_json())
            # return c.rest.content()
            return True

    def rest_delete_policy(self, tenant, polname):
        ''' Deleting a tenant policy
            Input:
                    'tenant'        tenant name
                    'polname'        policy name to be deleted

            Return: treu if deletetion successful, else false
        '''
        t = test.Test()
        c = t.controller('master')

        helpers.test_log("To be deleted: Input arguments: tenant = %s policy name = %s  " % (tenant, polname))

        # url = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]/logical-router/segment-interface' % (tenant)
        # url_delete = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]/logical-router/policy-lists[name="%s"] {}'
        url_delete_polname = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]/logical-router/policy-lists[name="%s"]' % (tenant, polname)
        try:
            c.rest.delete(url_delete_polname, {})
        except:
            # helpers.test_failure(c.rest.error())
            return False
        else:
            # helpers.test_log("Output: %s" % c.rest.result_json())
            # return c.rest.content()
            return True


    def rest_apply_policy_on_vns(self, tenant, vnsname, polname):
        '''Create a tenant policy

            Input:
                `tenant`        tenant name
                `vnsname`        vns name
                `polname`        name of policy

            Return: true if configuration is successful, false otherwise
        '''

        t = test.Test()
        c = t.controller('master')

        helpers.test_log("Input arguments: tenant = %s vns name = %s policy name = %s  " % (tenant, vnsname, polname))

        # url = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]/logical-router/segment-interface' % (tenant)
        url = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]/logical-router' % (tenant)
        try:
            c.rest.patch(url, {"inbound-policy-name": polname})
        except:
            # helpers.test_failure(c.rest.error())
            return False
        else:
            # helpers.test_log("Output: %s" % c.rest.result_json())
            # return c.rest.content()
            return True

    def rest_remove_policy_on_vns(self, tenant, vnsname, polname):
        '''Remove a tenant policy

            Input:
                `tenant`        tenant name
                `vnsname`        vns name
                `polname`        name of policy

            Return: true if configuration is successful, false otherwise
        '''

        t = test.Test()
        c = t.controller('master')

        helpers.test_log("Input arguments: tenant = %s vns name = %s policy name = %s  " % (tenant, vnsname, polname))

        # url = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]/logical-router/segment-interface' % (tenant)
        url_remove_policy = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]/logical-router/inbound-policy-name' % (tenant)
        try:
            c.rest.delete(url_remove_policy, {})
        except:
            # helpers.test_failure(c.rest.error())
            return False
        else:
            # helpers.test_log("Output: %s" % c.rest.result_json())
            # return c.rest.content()
            return True


    def rest_apply_policy_on_tenant(self, tenant, polname, intf="system"):
        '''Create a tenant policy

            Input:
                `tenant`        tenant name
                `vnsname`        vns name
                `polname`        name of policy

            Return: true if configuration is successful, false otherwise
        '''

        t = test.Test()
        c = t.controller('master')

        helpers.test_log("Input arguments: tenant = %s interface = %s policy name = %s  " % (tenant, intf, polname))

        # url = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]/logical-router/segment-interface' % (tenant)
        url = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]/logical-router' % (tenant)
        try:
            c.rest.patch(url, {"inbound-policy": polname})
        except:
            # helpers.test_failure(c.rest.error())
            return False
        else:
            # helpers.test_log("Output: %s" % c.rest.result_json())
            # return c.rest.content()
            return True

    def rest_remove_policy_on_tenant(self, tenant, polname, intf="system"):
        '''Remove a tenant policy

            Input:
                `tenant`        tenant name
                `vnsname`        vns name
                `polname`        name of policy

            Return: true if configuration is successful, false otherwise
        '''

        t = test.Test()
        c = t.controller('master')
        helpers.test_log("Input arguments: tenant = %s interface = %s policy name = %s  " % (tenant, intf, polname))

        # url = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]/logical-router/segment-interface' % (tenant)
        url_remove_policy = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]/logical-router/inbound-policy' % (tenant)
        try:
            c.rest.delete(url_remove_policy, {})
        except:
            # helpers.test_failure(c.rest.error())
            return False
        else:
            # helpers.test_log("Output: %s" % c.rest.result_json())
            # return c.rest.content()
            return True


    def rest_add_policy_item(self, tenant, polname, seqnum, polaction, srcdata, dstdata):
        '''add a policy item

            Input:
                `tenant`        tenant name
                `polname`       name of policy
                `seqnum`        sequence number
                `src-data`      Source policy data
                `dst-data`      Destination policy data
            http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/tenant[name="A"]/logical-router/policy-lists[name="p2"]/rules[seq=10] {"src": {"segment": "A1", "tenant-name": "A"}, "seq": 10, "dst": {"cidr": "10.1.1.1/24"}, "ip-proto": 6, "action": "next-hop", "next-hop": {"ip-address": "10.1.1.1"}}
            Return: true if configuration is successful, false otherwise
        '''

        t = test.Test()
        c = t.controller('master')

        helpers.test_log("Input arguments: tenant = %s policy name = %s sequence number = %s src-data = %s dst-data = %s action = %s " % (tenant, polname, str(seqnum), str(srcdata), str(dstdata), polaction))
        url = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]/logical-router/policy-list[name="%s"]/rule[seq=%s]' % (tenant, polname, seqnum)
        try:
            c.rest.put(url, {"src":srcdata, "seq": str(seqnum), "dst":dstdata, "action": str(polaction)})

        except:
            # helpers.test_failure(c.rest.error())
            return False
        else:
            # helpers.test_log("Output: %s" % c.rest.result_json())
            # return c.rest.content()
            return True

    def rest_add_router_intf(self, tenant, vns):
        '''Create vns router interface via command "logical-router vns interface"

            Input:
                `tenant`        tenant name
                `vns`           vns interface name which must be similar to VNS
            PUT http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/tenant%5Bname%3D%22X%22%5D/logical-router/segment-interface%5Bsegment%3D%22X1%22%5D {"segment": "X1"}
            Return: true if configuration is successful, false otherwise
        '''

        t = test.Test()
        c = t.controller('master')

        helpers.test_log("Input arguments: tenant = %s vns = %s " % (tenant, vns))
        url = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]/logical-router/segment-interface[segment="%s"]' % (tenant, vns)
        try:
            c.rest.put(url, {"segment": vns})
        except:
            # helpers.test_failure(c.rest.error())
            return False
        else:
            # helpers.test_log("Output: %s" % c.rest.result_json())
            # return c.rest.content()
            return True

    def rest_del_router_intf(self, tenant, vns):
        '''Create vns router interface via command "logical-router vns interface"

            Input:
                `tenant`        tenant name
                `vns`           vns interface name which must be similar to VNS
             DELETE http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/tenant%5Bname%3D%22X%22%5D/logical-router/segment-interface%5Bsegment%3D%22X1%22%5D {}
            Return: true if configuration is successful, false otherwise
        '''

        t = test.Test()
        c = t.controller('master')

        helpers.test_log("Input arguments: tenant = %s vns = %s " % (tenant, vns))
        url = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]/logical-router/segment-interface[segment="%s"]' % (tenant, vns)
        try:
            c.rest.delete(url, {})
        except:
            # helpers.test_failure(c.rest.error())
            return False
        else:
            # helpers.test_log("Output: %s" % c.rest.result_json())
            # return c.rest.content()
            return True




    def rest_add_policy_item_example(self, **kwargs):
        '''add a policy item

            Input:
                `tenant`        tenant name
                `polname`       name of policy
                `seqnum`        sequence number
                `src-data`      Source policy data
                `dst-data`      Destination policy data
            http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/tenant[name="A"]/logical-router/policy-lists[name="p2"]/rules[seq=10] {"src": {"segment": "A1", "tenant-name": "A"}, "seq": 10, "dst": {"cidr": "10.1.1.1/24"}, "ip-proto": 6, "action": "next-hop", "next-hop": {"ip-address": "10.1.1.1"}}
            Return: true if configuration is successful, false otherwise
        '''

        t = test.Test()
        c = t.controller('master')
        # src_mac = kwargs.get('src_mac', '00:11:23:00:00:01')
        seqnum = kwargs.get('seqnum')
        action = kwargs.get('action')
        srcdata = kwargs.get('srcdata', None)
        dstdata = kwargs.get('dstdata', None)
        ip_proto = kwargs.get('proto', None)
        next_hop = kwargs.get('next-hop', None)
        tenant = kwargs.get('tenant', None)
        polname = kwargs.get('polname', None)
        log = kwargs.get('log', None)
        segment = kwargs.get('segment-interface', None)

        if (tenant is None or polname is None or seqnum is None):
            helpers.test_failure("Tenant and Polname are Null")



        helpers.test_log("Input arguments: tenant = %s" \
                         " policy name = %s" \
                         " sequence number = %s " \
                         " src-data = %s " \
                         " dst-data = %s " \
                         " action = %s " \
                         " ip-proto = %s " \
                         " segment-interface = %s" \
                         " next-hop-group = %s " % (tenant, polname, str(seqnum), str(srcdata), str(dstdata), action, ip_proto, segment, next_hop))
        url = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]/logical-router/policy-list[name="%s"]/rule[seq=%s]' % (tenant, polname, seqnum)
        if (next_hop is None and ip_proto is None):
            if (srcdata is not None and dstdata is not None):
                if(segment is None):
                    data = {"src":srcdata, "seq": str(seqnum), "dst":dstdata, "action": str(action)}
                else:
                    data = {"src":srcdata, "seq": str(seqnum), "dst":dstdata, "action": str(action), "segment-interface":segment}
                try:
                    helpers.log("**** url: %s" % url)
                    c.rest.put(url, data)
                except:
                    helpers.log("Error happend Output: %s " % c.rest.result_json())
                    return False
                else:
                    helpers.test_log("Output: %s" % c.rest.result_json())
                    return c.rest.content()
                    return True

            if (srcdata is None):
                data = {"seq": str(seqnum), "dst":dstdata, "action": str(action)}
                try:
                    c.rest.put(url, data)

                except:
                    # helpers.test_failure(c.rest.error())
                    return False
                else:
                    # helpers.test_log("Output: %s" % c.rest.result_json())
                    # return c.rest.content()
                    return True

            if (dstdata is None):
                data = {"src":srcdata, "seq": str(seqnum), "action": str(action)}
                try:
                    c.rest.put(url, data)

                except:
                    # helpers.test_failure(c.rest.error())
                    return False
                else:
                    # helpers.test_log("Output: %s" % c.rest.result_json())
                    # return c.rest.content()
                    return True

            if (dstdata is None and srcdata is None):
                data = { "seq": str(seqnum), "action": str(action)}
                try:
                    c.rest.put(url,)

                except:
                    # helpers.test_failure(c.rest.error())
                    return False
                else:
                    # helpers.test_log("Output: %s" % c.rest.result_json())
                    # return c.rest.content()
                    return True

        if (next_hop is None and ip_proto is not None):
            if (srcdata is not None and dstdata is not None):
                data = {"src":srcdata, "seq": str(seqnum), "dst":dstdata, "action": str(action), "ip-proto":ip_proto}
                try:
                    c.rest.put(url, data)

                except:
                        # helpers.test_failure(c.rest.error())
                        return False
                else:
                    # helpers.test_log("Output: %s" % c.rest.result_json())
                    # return c.rest.content()
                    return True

            if (srcdata is None):
                data = {"seq": str(seqnum), "dst":dstdata, "action": str(action), "ip-proto":ip_proto}
                try:
                    c.rest.put(url, data)

                except:
                    # helpers.test_failure(c.rest.error())
                    return False
                else:
                    # helpers.test_log("Output: %s" % c.rest.result_json())
                    # return c.rest.content()
                    return True

            if (dstdata is None):
                data = {"src":srcdata, "seq": str(seqnum), "action": str(action), "ip-proto":ip_proto}
                try:
                    c.rest.put(url, data)

                except:
                    # helpers.test_failure(c.rest.error())
                    return False
                else:
                    # helpers.test_log("Output: %s" % c.rest.result_json())
                    # return c.rest.content()
                    return True

            if (dstdata is None and srcdata is None):
                data = { "seq": str(seqnum), "action": str(action), "ip-proto":ip_proto}
                try:
                    c.rest.put(url, data)

                except:
                    # helpers.test_failure(c.rest.error())
                    return False
                else:
                    # helpers.test_log("Output: %s" % c.rest.result_json())
                    # return c.rest.content()
                    return True

        if (next_hop is not None and ip_proto is not None and action == "next-hop"):
            if (srcdata is not None and dstdata is not None):
                if (segment is not None):
                    data = {"src":srcdata, "seq": str(seqnum), "dst":dstdata, "action": str(action), "ip-proto":ip_proto, "next-hop":next_hop, "segment-interface":segment}
                else:
                    data = {"src":srcdata, "seq": str(seqnum), "dst":dstdata, "action": str(action), "ip-proto":ip_proto, "next-hop":next_hop}

                try:
                    c.rest.put(url, data)

                except:
                    # helpers.test_failure(c.rest.error())
                    return False
                else:
                    # helpers.test_log("Output: %s" % c.rest.result_json())
                    # return c.rest.content()
                    return True

            if (srcdata is None):
                if (segment is not None):
                    data = {"seq": str(seqnum), "dst":dstdata, "action": str(action), "ip-proto":ip_proto, "next-hop":next_hop, "segment-interface":segment}
                else:
                    data = {"seq": str(seqnum), "dst":dstdata, "action": str(action), "ip-proto":ip_proto, "next-hop":next_hop}

                try:
                    c.rest.put(url, data)

                except:
                    # helpers.test_failure(c.rest.error())
                    return False
                else:
                    # helpers.test_log("Output: %s" % c.rest.result_json())
                    # return c.rest.content()
                    return True

            if (dstdata is None):
                if (segment is not None):
                    data = {"src":srcdata, "seq": str(seqnum), "action": str(action), "ip-proto":ip_proto, "next-hop":next_hop, "segment-interface":segment}
                else:
                    data = {"src":srcdata, "seq": str(seqnum), "action": str(action), "ip-proto":ip_proto, "next-hop":next_hop}

                try:
                    c.rest.put(url, data)

                except:
                    # helpers.test_failure(c.rest.error())
                    return False
                else:
                    # helpers.test_log("Output: %s" % c.rest.result_json())
                    # return c.rest.content()
                    return True

            if (dstdata is None and srcdata is None):
                if (segment is not None):
                    data = { "seq": str(seqnum), "action": str(action), "ip-proto":ip_proto, "next-hop":next_hop, "segment-interface":segment}
                else:
                    data = { "seq": str(seqnum), "action": str(action), "ip-proto":ip_proto, "next-hop":next_hop}

                try:
                    c.rest.put(url,)

                except:
                    # helpers.test_failure(c.rest.error())
                    return False
                else:
                    # helpers.test_log("Output: %s" % c.rest.result_json())
                    # return c.rest.content()
                    return True

        if (next_hop is not None and action == "next-hop"):
            if (ip_proto is None):
                if (srcdata is not None and dstdata is not None):
                    if (segment is not None):
                        if(log is not None):
                            helpers.test_log("next hop is not none, ip proto is none, policy-log enabled and action is next-hop")
                            data = {"src":srcdata, "log":log, "seq": str(seqnum), "dst":dstdata, "action": str(action), "next-hop":next_hop, "segment-interface":segment}
                        else:
                            helpers.test_log("next hop is not none, ip proto is none, policy-log not enabled and action is next-hop")
                            data = {"src":srcdata, "seq": str(seqnum), "dst":dstdata, "action": str(action), "next-hop":next_hop, "segment-interface":segment}

                    else:
                        helpers.test_log("next hop is none, ip proto is none and action is next-hop")
                        data = {"src":srcdata, "seq": str(seqnum), "dst":dstdata, "action": str(action), "next-hop":next_hop}

                    try:
                        c.rest.put(url, data)

                    except:
                    # helpers.test_failure(c.rest.error())
                        return False
                    else:
                    # helpers.test_log("Output: %s" % c.rest.result_json())
                    # return c.rest.content()
                        return True

                if (srcdata is None):
                    if (segment is not None):
                        data = {"seq": str(seqnum), "dst":dstdata, "action": str(action), "next-hop":next_hop, "segment-interface":segment}
                    else:
                        data = {"seq": str(seqnum), "dst":dstdata, "action": str(action), "next-hop":next_hop}

                    try:
                        c.rest.put(url, data)

                    except:
                    # helpers.test_failure(c.rest.error())
                        return False
                    else:
                    # helpers.test_log("Output: %s" % c.rest.result_json())
                    # return c.rest.content()
                        return True

                if (dstdata is None):
                    if (segment is not None):
                        data = {"src":srcdata, "seq": str(seqnum), "action": str(action), "next-hop":next_hop, "segment-interface":segment}
                    else:
                        data = {"src":srcdata, "seq": str(seqnum), "action": str(action), "next-hop":next_hop}

                    try:
                        c.rest.put(url, data)

                    except:
                    # helpers.test_failure(c.rest.error())
                        return False
                    else:
                    # helpers.test_log("Output: %s" % c.rest.result_json())
                    # return c.rest.content()
                        return True

                if (dstdata is None and srcdata is None):
                    if (segment is not None):
                        data = { "seq": str(seqnum), "action": str(action), "next-hop":next_hop, "segment-interface":segment}
                    else:
                        data = { "seq": str(seqnum), "action": str(action), "next-hop":next_hop}

                    try:
                        c.rest.put(url, data)

                    except:
                    # helpers.test_failure(c.rest.error())
                        return False
                    else:
                    # helpers.test_log("Output: %s" % c.rest.result_json())
                    # return c.rest.content()
                        return True

    def rest_show_forwarding_dhcp_table(self, routerip=None):
        '''
       GET http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/info/forwarding/network/global/dhcp-table
     '''
        t = test.Test()
        c = t.controller('master')
        url = '/api/v1/data/controller/applications/bcf/info/forwarding/network/global/dhcp-table'
        c.rest.get(url)
        data = c.rest.content()
        helpers.log ("result: %s" % helpers.prettify(data))
        if routerip is None:
            if len(data) == 0:
                return {}
            else:
                return data
        else:
            for entry in data:
                helpers.log("entry is %s" % entry)
                if entry['router-ip'] == routerip:
                    return entry
        helpers.log("no Match")
        return {}

    def rest_show_forwarding_ecmp_table(self):
        '''
        GET http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/info/forwarding/network/global/ecmp-table

     '''
        t = test.Test()
        c = t.controller('master')
        url = '/api/v1/data/controller/applications/bcf/info/forwarding/network/global/ecmp-table'
        try:
            c.rest.get(url)
        except:
            helpers.test_failure(c.rest.error())
        else:
            return c.rest.content()

    def rest_disable_endpoint_flap_protection(self):
        '''Disable endpoint flap protection
         REST-POST: DELETE http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/global-setting/enable-endpoint-flap-protection {}
                Return: true if configuration is successful, false otherwise
        '''
        t = test.Test()
        c = t.controller('master')

        url = '/api/v1/data/controller/applications/bcf/global-setting/enable-endpoint-flap-protection'
        try:
            c.rest.delete(url, {})
        except:
            return False
            # helpers.test_failure(c.rest.error())
        else:
            # helpers.test_log("Output: %s" % c.rest.result_json())
            # return c.rest.content()
            return True

    def rest_enable_endpoint_flap_protection(self):
        '''Enable endpoint flap protection
         REST-POST: PATCH http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/global-setting {"enable-endpoint-flap-protection": true}
                    PATCH http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/global-setting {"enable-endpoint-flap-protection": true}
                                                api/v1/data/controller/applications/bcf/global-setting
                Return: true if configuration is successful, false otherwise
        '''
        t = test.Test()
        c = t.controller('master')
        helpers.log ("Inside rest enable endpoint flap protection")
        url = '/api/v1/data/controller/applications/bcf/global-setting'
        try:
            # helpers.log("Before patch command")
            result = c.rest.patch(url, {"enable-endpoint-flap-protection": True})
            # helpers.log("After patch command. result:%s" % helpers.prettify(result))
#        try:
        except:
            return False
            # helpers.test_failure(c.rest.error())
        else:
            # helpers.test_log("Output: %s" % c.rest.result_json())
            # return c.rest.content()
            return True


    def rest_get_l3_cidr_route_info(self, ipaddress, netMask, switch=None):
        '''return specific route entry in l3 cidr table
        GET http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/info/forwarding/network/global/l3-cidr-table
        GET http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/info/forwarding/network/switch[switch-name="leaf0-a"]/l3-cidr-route-table

            Input: ip, subnet mask

            Return: content if found
        '''
        t = test.Test()
        c = t.controller('master')
        if switch is None:
            url = '/api/v1/data/controller/applications/bcf/info/forwarding/network/global/l3-cidr-table'
        else:
            url = '/api/v1/data/controller/applications/bcf/info/forwarding/network/switch[switch-name="%s"]/l3-cidr-route-table' % switch
        c.rest.get(url)
        data = c.rest.content()
#        result = helpers.from_json(data)
        helpers.log ("result: %s" % helpers.prettify(data))
        if len(data) == 0:
            return {}
        else:
            for entry in data:
                helpers.log("entry is %s" % entry)
                if entry['ip'] == ipaddress:
                    helpers.log("Match IP address '%s'" % ipaddress)
                    if entry['ip-mask'] == netMask:
                        helpers.log("Match IP address '%s', netmask '%s'" % (ipaddress, netMask))
                        return entry
        helpers.log("no Match")
        return {}

    def rest_ecmp_nexthop_count(self, ecmpIndex):
        ''' return number of next hop in ecmp group
            Input: ecmp index
            Return: count or error
GET http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/info/forwarding/network/global/ecmp-table

        '''
        t = test.Test()
        c = t.controller('master')
        count = 0
        url = '/api/v1/data/controller/applications/bcf/info/forwarding/network/global/ecmp-table'
        c.rest.get(url)
        data = c.rest.content()
        helpers.log ("result: %s" % helpers.prettify(data))
        if len(data) != 0:
            for entry in data:
                if entry['ecmp-group-id'] == ecmpIndex:
                    count = count + 1
        return count

    def rest_get_logical_router_segment_interface(self, tenant, vnsName=None):
        '''return segment interface information
        GET http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/info/logical-router-manager/logical-router/segment-interface

            Input:  segment name
                    tenant name
            Return: content if found
        '''
        t = test.Test()
        c = t.controller('master')
        url = '/api/v1/data/controller/applications/bcf/info/logical-router-manager/logical-router/segment-interface'
        c.rest.get(url)
        data = c.rest.content()
#        result = helpers.from_json(data)
        helpers.log ("result: %s" % helpers.prettify(data))
        if len(data) == 0:
            return {}
        else:
            if vnsName is None:
                return data
            else:
                for entry in data:
                    helpers.log("entry is %s" % entry)
                    if entry['logical-router'] == tenant:
                        if entry['segment'] == vnsName:
                            helpers.log("Match segment '%s'" % vnsName)
                            return entry

            helpers.log("no Match")
            return {}

    def rest_get_tracked_endpoint(self, ipaddr=None):
        '''
            get tracked endpoint and return the result
         GET http://127.0.0.1:8080/api/v1/data/controller/applications/bcf/info/endpoint-manager/tracked-endpoint
         '''
        t = test.Test()
        c = t.controller('master')
        url = '/api/v1/data/controller/applications/bcf/info/endpoint-manager/tracked-endpoint'
        c.rest.get(url)
        data = c.rest.content()
        helpers.log ("result: %s" % helpers.prettify(data))
        if ipaddr is None:
            if len(data) == 0:
                return {}
            else:
                return data
        else:
            for entry in data:
                helpers.log("entry is %s" % entry)
                if entry['ip-address'] == ipaddr:
                    return entry
        helpers.log("no Match")
        return {}

    def rest_verify_policy_stats(self, tenant, seq, frame_cnt, flag=False, delta=2):
        ''' Function to verify policy rule counter
        Input: tenant name, policy seq number and packets tx
        Output: policy counter
        '''
        t = test.Test()
        c = t.controller('master')
        frame_cnt = int(frame_cnt)
        url = '/api/v1/data/controller/applications/bcf/info/statistic/policy-counter[policy/seq="%s"][tenant-name="%s"]' % (seq, tenant)
        c.rest.get(url)
        data = c.rest.content()
        helpers.log("Printing len of data: %d and flag:%s" % (len(data), flag))
        if (len(data) != 0 and flag is False):
            helpers.log("In len.data not ZERO and FLAG is FALSE")
            hw_pkt_cnt = int(data[0]['policy'][0]['packet'])
            if data[0]["tenant-name"] == tenant and data[0]['policy'][0]['seq'] == seq:
                if (hw_pkt_cnt >= (frame_cnt - delta) and hw_pkt_cnt <= (frame_cnt + delta)):
                    helpers.log("Pass: Policy Counters value Expected:%d, Actual:%d" % (frame_cnt, int(data[0]['policy'][0]['packet'])))
                    return True
                else:
                    helpers.test_failure("Policy counter value does not match,Expected:%d,Actual:%d" % (frame_cnt, int(data[0]['policy'][0]['packet'])))
                    return False
            else:
                helpers.log("Given tenant name and policy seq number does not match the config")
        else:
            helpers.log("In len.data eq ZERO and FLAG is TRUE")
            return True

    def rest_verify_fwd_icap_table(self, switch, matchip):
        ''' Function to verify given ip exist in fwding icap table
        Input: switch name and ip
        Output: return true if ip exist in the fwding icap table
        '''
        t = test.Test()
        c = t.controller('master')

        url = '/api/v1/data/controller/applications/bcf/info/forwarding/network/switch[switch-name="%s"]/icap-table' % (switch)
        c.rest.get(url)
        data = c.rest.content()
        helpers.log("Printing len of data: %d and switch name:%s" % (len(data), switch))
        if (len(data) != 0):
            for i in range (0, len(data)):
                helpers.log("printing ICAP table from switch:%s and given IP :%s" % (data[i]['dst-ip'], matchip))
                if data[i]["dst-ip"] == matchip:
                    helpers.log("Match found in ICAP table")
                    return True
        else:
            helpers.log("Match not found in ICAP table")
            return False

        return False

    def rest_verify_fwd_ecmp_grp_icap_table(self, switch, matchip, zero=False):
        ''' Function to verify ecmp group id should not be zero in fwding icap table
        Input: switch name, matchip
        Output: return true if ecmp grp id more than zero in the fwding icap table
        '''
        t = test.Test()
        c = t.controller('master')

        url = '/api/v1/data/controller/applications/bcf/info/forwarding/network/switch[switch-name="%s"]/icap-table' % (switch)
        c.rest.get(url)
        data = c.rest.content()
        helpers.log("Printing len of data: %d and switch name:%s and zero :%s" % (len(data), switch, zero))
        if (len(data) != 0 and zero == False):
            for i in range (0, len(data)):
                helpers.log("printing ICAP table from switch:%s and given IP :%s" % (data[i]['dst-ip'], matchip))
                if data[i]["dst-ip"] == matchip and int(data[i]["ecmp-group-id"] and data[i]["src-ip"] != matchip) > 0:
                    helpers.log("Match found in ICAP table and ecmp group id is not Zero")
                    return True

        elif (len(data) != 0 and zero == 'True'):
            for i in range (0, len(data)):
                helpers.log("printing ICAP table from switch:%s and given IP :%s" % (data[i]['dst-ip'], matchip))
                if data[i]["dst-ip"] == matchip and int(data[i]["ecmp-group-id"]) == 0:
                    helpers.log("Match found in ICAP table and ecmp group id is NOT SET, which is correct")
                    return True

        return False


    def rest_clear_policy_stats(self, tenant, seq):
        ''' Function to clear policy counters
        Input: tenant name, policy seq number
        Output: none
        '''
        t = test.Test()
        c = t.controller('master')
        url = '/api/v1/data/controller/applications/bcf/info/statistic/policy-counter[tenant-name="%s"]/policy[seq="%s"]' % (tenant, seq)
        c.rest.delete(url, {})

    def rest_get_policy_log_pkt_cnt(self, tenant):
        ''' Function to verify policy log counter
        Input: tenant name
        Output: policy log counter
        '''
        return_null = 0
        t = test.Test()
        c = t.controller('master')
        url = '/api/v1/data/controller/applications/bcf/info/policy-log/counter[tenant="%s"]' % (tenant)
        c.rest.get(url)
        data = c.rest.content()
        if data[0]["tenant"] == tenant:
            log_cnt = data[0]['value']['packet']
            if (log_cnt):
                helpers.log("Pass: Policy log Counters value %d" % log_cnt)
                return log_cnt
            else:
                return return_null

        else:
            helpers.log("Given tenant name did not match the config")
            
    def rest_get_policy_name(self, tenant):
        ''' Function to get policy name for a tenant
        Input: tenant name
        Output: policy log counter
        '''
        t = test.Test()
        c = t.controller('master')
        url = '/api/v1/data/controller/applications/bcf/info/logical-router-manager/logical-router[name="%s"]/policy-list' % (tenant)
        c.rest.get(url)
        data = c.rest.content()
        for i in range(0, len(data)):
            if data[i]["applied"] == "true":
                policy = data[i]["policy"]
                return policy
            else:
                continue

                

