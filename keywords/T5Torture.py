'''
###  WARNING !!!!!!!
###
###  This is where common code for all T5 will go in.
###
###  To commit new code, please contact the Library Owner:
###  Mingtao Yang (mingtao.yang@bigswitch.com)
###
###  DO NOT COMMIT CODE WITHOUT APPROVAL FROM LIBRARY OWNER
###
###  Last Updated: 2014-11-04
###
###  WARNING !!!!!!!
'''
import re
import autobot.helpers as helpers
import autobot.test as test


# Global variables to save the state
# Used by: fabric_integrity_checker

switchList_b4 = []
switchList_after = []
slave_switchList_b4 = []
slave_switchList_after = []
fabricLinks_b4 = []
fabricLinks_after = []
endpoints_b4 = []
endpoints_after = []
fabricLags_b4 = []
fabricLags_after = []
portgroups_b4 = []
portgroups_after = []

fwdARPTable_b4 = []
fwdARPTable_after = []
fwdEPTable_b4 = []
fwdEPTable_after = []
fwdL3CIDRTable_b4 = []
fwdL3CIDRTable_after = []
fwdL3HostTable_b4 = []
fwdL3HostTable_after = []
fwdMyStationTable_b4 = []
fwdMyStationTable_after = []
fwdRouterIPTable_b4 = []
fwdRouterIPTable_after = []
fwdEcmpTable_b4 = []
fwdEcmpTable_after = []
fwdDhcpTable_b4 = []
fwdDhcpTable_after = []

warningCount = 0
fabricErrorEncounteredFlag = False

floodlightMonitorFlag = False


class T5Torture(object):

    # T5
    def cli_link_flap_between_nodes(self, node1, node2, interval=60):
        '''
        '''
        helpers.test_log("Entering ==> cli_event_link_flap:  node1 - %s  node2  - %s " % (node1, node2))
        ints = self.cli_get_links_nodes_list(node1, node2)

        for interface in ints:
            helpers.test_log("INFO: flap interface - %s" % interface)
            self.rest_disable_fabric_interface(node1, interface)
            helpers.sleep(interval)
            self.rest_enable_fabric_interface(node1, interface)
            helpers.sleep(interval)
        return True

    # T5
    def cli_event_link_flap(self, list1, list2, interval=60):
        '''
        '''
        helpers.test_log("Entering ==> cli_event_link_flap:  list1 - %s  list22  - %s " % (list1, list2))

        for node1 in list1:
            for node2 in list2:
                if node1 == node2:
                    helpers.test_log("INFO: node pairs are same: %s  - %s. Don't run test." % (node1, node2))
                    continue
                helpers.test_log("INFO: node pair: %s  - %s" % (node1, node2))
                self.cli_link_flap_between_nodes(node1, node2, interval)

        return True

    # T5
    def cli_get_links_nodes_list(self, node1, node2):
        '''
        '''
        helpers.test_log("Entering ==> cli_get_links_nodes_list: %s  - %s" % (node1, node2))
        t = test.Test()
        c = t.controller('master')
        cli = 'show link | grep ' + node1 + ' | grep ' + node2
        content = c.cli(cli)['content']
        temp = helpers.strip_cli_output(content, to_list=True)
        helpers.log("INFO: *** output  *** \n  %s" % temp)
        a_list = []
        for line in temp:
            line = line.lstrip()
            fields = line.split()
            helpers.log("fields: %s" % fields)
            if fields[1] == node1 :
                a_list.append(fields[2])
            elif fields[3] == node1 :
                a_list.append(fields[4])

        helpers.log("INFO: *** link info *** \n for %s: %s \n " % (node1, list))
        return a_list

    # T5
    def rest_show_switch(self, node='master', soft_error=False):
        """
        Return dictionary containing all switches connected to current controller

        Inputs:
        | node | name of the controller, default is 'master' |

        Return value:
        | List | on success, returns list of switches (each entry is a dictionary) |
        | None   | on failure, if soft_error is True |
        | Exception | on failure, if soft_error is False |
        """
        t = test.Test()
        c = t.controller(node)
        url = '/api/v1/data/controller/applications/bcf/info/fabric/switch'

        try:
            c.rest.get(url)
        except:
            helpers.test_error("REST GET error", soft_error=soft_error)
            return None
        else:
            content = c.rest.content()
            return content

    # T5
    def rest_get_switch_names(self, node='master', soft_error=False):
        """
        Return list containing all switch names which are connected to current controller

        Inputs:
        | node | name of the controller, default is 'master' |

        Return value:
        | List | on success, returns list of switch names |
        | None   | on failure, if soft_error is True |
        | Exception | on failure, if soft_error is False |
        """
        result = self.rest_show_switch(node, soft_error)
        if result:
            return [helpers.utf8(s['name']) for s in result]
        else:
            return None

    # T5
    def rest_get_spine_switch_names(self, node='master', soft_error=False):
        """
        Return list containing all spine switch names which are connected to current controller

        Inputs:
        | node | name of the controller, default is 'master' |

        Return value:
        | List | on success, returns list of spine switch names |
        | None   | on failure, if soft_error is True |
        | Exception | on failure, if soft_error is False |
        """
        result = self.rest_get_switch_names(node, soft_error)
        if result:
            return [s for s in result if re.match(r'.*spine.*', s)]
        else:
            return None

    # T5
    def rest_get_leaf_switch_names(self, node='master', soft_error=False):
        """
        Return list containing all leaf switch names which are connected to current controller

        Inputs:
        | node | name of the controller, default is 'master' |

        Return value:
        | List | on success, returns list of leaf switch names |
        | None   | on failure, if soft_error is True |
        | Exception | on failure, if soft_error is False |
        """
        result = self.rest_get_switch_names(node, soft_error)
        if result:
            return [s for s in result if re.match(r'.*leaf.*', s)]
        else:
            return None


    # T5Utilities
    def fabric_integrity_checker(self, state, cluster="HA", consistencyChecker="No"):
        '''
        Objective::
        -    This function will check for fabric integrity between states. For example calling this function before a state
            change (eg:HA Failover) & after a state change would compare fabric elements from both the states and list out
            differences as warnings.
            Usage:
                    obj =  T5Utilities()
                    utilities.fabric_integrity_checker(obj,"before")
                    <do stuff>
                    utilities.fabric_integrity_checker(obj,"after")

            If Single Node Cluster:
                    obj =  T5Utilities()
                    utilities.fabric_integrity_checker(obj,"before", "single")
                    <do stuff>
                    utilities.fabric_integrity_checker(obj,"after", "single")

        Description :
        -    Checks for the fabric state differences on following component: Switch Connectivity / Fabric Links / Fabric Lags / Endpoints

        Inputs:
        |    state= "before" or "after"

        Outputs:
        |    Warning Messages along with return True

        '''
        global switchList_b4
        global switchList_after
        global slave_switchList_b4
        global slave_switchList_after
        global fabricLinks_b4
        global fabricLinks_after
        global endpoints_b4
        global endpoints_after
        global fabricLags_b4
        global fabricLags_after
        global portgroups_b4
        global portgroups_after

        global fwdARPTable_b4
        global fwdEPTable_b4
        global fwdL3CIDRTable_b4
        global fwdL3HostTable_b4
        global fwdMyStationTable_b4
        global fwdRouterIPTable_b4
        global fwdEcmpTable_b4
        global fwdDhcpTable_b4

        global fwdARPTable_after
        global fwdEPTable_after
        global fwdL3CIDRTable_after
        global fwdL3HostTable_after
        global fwdMyStationTable_after
        global fwdRouterIPTable_after
        global fwdEcmpTable_after
        global fwdDhcpTable_after

        global warningCount
        global fabricErrorEncounteredFlag

        # Switch connectivity verification
        if (state == "before"):
            switchList_b4 = self._gather_switch_connectivity()
            if(cluster == "HA"):
                slave_switchList_b4 = self._gather_switch_connectivity("slave")
            fabricLinks_b4 = self._gather_fabric_links()
            endpoints_b4 = self._gather_endpoints()
            fabricLags_b4 = self._gather_fabric_lags()
            portgroups_b4 = self._gather_port_groups()

            fwdARPTable_b4 = self._gather_forwarding('arp-table')
            fwdEPTable_b4 = self._gather_forwarding('ep-table')
            fwdL3CIDRTable_b4 = self._gather_forwarding('l3-cidr-table')
            fwdL3HostTable_b4 = self._gather_forwarding('l3-host-table')
            fwdMyStationTable_b4 = self._gather_forwarding('my-station-table')
            fwdRouterIPTable_b4 = self._gather_forwarding('router-ip-table')
            fwdEcmpTable_b4 = self._gather_forwarding('ecmp-table')
            fwdDhcpTable_b4 = self._gather_forwarding('dhcp-table')


        else:
            if(consistencyChecker == "Yes"):
                switchList_after = self._gather_switch_connectivity("slave", "Yes")
            else:
                switchList_after = self._gather_switch_connectivity()
            warningCount = self._compare_fabric_elements(switchList_b4, switchList_after, "SwitchList")
            if(cluster == "HA"):
                slave_switchList_after = self._gather_switch_connectivity("slave")
                warningCount = self._compare_fabric_elements(slave_switchList_b4, slave_switchList_after, "SwitchList")

            if(consistencyChecker == "Yes"):
                fabricLinks_after = self._gather_fabric_links("slave")
            else:
                fabricLinks_after = self._gather_fabric_links()
            warningCount = self._compare_fabric_elements(fabricLinks_b4, fabricLinks_after, "FabricLinks")

            if(consistencyChecker == "Yes"):
                endpoints_after = self._gather_endpoints("slave")
            else:
                endpoints_after = self._gather_endpoints()
            warningCount = self._compare_fabric_elements(endpoints_b4, endpoints_after, "FabricEndpoints")

            if(consistencyChecker == "Yes"):
                fabricLags_after = self._gather_fabric_lags("slave")
            else:
                fabricLags_after = self._gather_fabric_lags()
            warningCount = self._compare_fabric_elements(fabricLags_b4, fabricLags_after, "FabricLags")

            if(consistencyChecker == "Yes"):
                portgroups_after = self._gather_port_groups("slave")
            else:
                portgroups_after = self._gather_port_groups()
            warningCount = self._compare_fabric_elements(portgroups_b4, portgroups_after, "PortGroups")

            if(consistencyChecker == "Yes"):
                fwdARPTable_after = self._gather_forwarding('arp-table', "slave")
            else:
                fwdARPTable_after = self._gather_forwarding('arp-table')
            warningCount = self._compare_fabric_elements(fwdARPTable_b4, fwdARPTable_after, "fwdARPTable")

            if(consistencyChecker == "Yes"):
                fwdEPTable_after = self._gather_forwarding('ep-table', "slave")
            else:
                fwdEPTable_after = self._gather_forwarding('ep-table')
            warningCount = self._compare_fabric_elements(fwdEPTable_b4, fwdEPTable_after, "fwdEPTable")

            if(consistencyChecker == "Yes"):
                fwdL3CIDRTable_after = self._gather_forwarding('l3-cidr-table', "slave")
            else:
                fwdL3CIDRTable_after = self._gather_forwarding('l3-cidr-table')
            warningCount = self._compare_fabric_elements(fwdL3CIDRTable_b4, fwdL3CIDRTable_after, "fwdL3CIDRTable")

            if(consistencyChecker == "Yes"):
                fwdL3HostTable_after = self._gather_forwarding('l3-host-table', "slave")
            else:
                fwdL3HostTable_after = self._gather_forwarding('l3-host-table')
            warningCount = self._compare_fabric_elements(fwdL3HostTable_b4, fwdL3HostTable_after, "fwdL3HostTable")

            if(consistencyChecker == "Yes"):
                fwdMyStationTable_after = self._gather_forwarding('my-station-table', "slave")
            else:
                fwdMyStationTable_after = self._gather_forwarding('my-station-table')
            warningCount = self._compare_fabric_elements(fwdMyStationTable_b4, fwdMyStationTable_after, "fwdMyStationTable")

            if(consistencyChecker == "Yes"):
                fwdRouterIPTable_after = self._gather_forwarding('router-ip-table', "slave")
            else:
                fwdRouterIPTable_after = self._gather_forwarding('router-ip-table')
            warningCount = self._compare_fabric_elements(fwdRouterIPTable_b4, fwdRouterIPTable_after, "fwdRouterIPTable")

            if(consistencyChecker == "Yes"):
                fwdEcmpTable_after = self._gather_forwarding('ecmp-table', "slave")
            else:
                fwdEcmpTable_after = self._gather_forwarding('ecmp-table')
            warningCount = self._compare_fabric_elements(fwdEcmpTable_b4, fwdEcmpTable_after, "fwdEcmpTable")

            if(consistencyChecker == "Yes"):
                fwdDhcpTable_after = self._gather_forwarding('dhcp-table', "slave")
            else:
                fwdDhcpTable_after = self._gather_forwarding('dhcp-table')
            warningCount = self._compare_fabric_elements(fwdDhcpTable_b4, fwdDhcpTable_after, "fwdDhcpTable")

        if(fabricErrorEncounteredFlag):
            helpers.warn("------- Fabric Error encountered during Fabric Integrity Checks. Returning False -------")
            return False
        if(warningCount == 0):
            if(state == "after"):
                helpers.log("Switch status is intact after the state change operation")
            return True
        else:
            # helpers.warn("-------  Switch Status Is Not Intact. Please Collect Logs. Sleeping for 10 Hours   ------")
            # sleep(36000)
            return True

    # T5Utilities
    def _gather_switch_connectivity(self, node="master", consistencyChecker="No"):
        '''
        -    This is a helper function. This function is used by "fabric_integrity_checker"

        Description:
        -    Using the "show switch" command verify switches are connected to the fabric

        '''
        t = test.Test()
        if(node == "master"):
            c = t.controller("master")
        else:
            c = t.controller("slave")

        url = "/api/v1/data/controller/applications/bcf/info/fabric/switch"
        result = c.rest.get(url)['content']
        switchList = []
        i = 0

        while i < len(result):
            try:
                dpid = result[i]['dpid']
                connected = result[i]['connected']
                fabricConState = result[i]['fabric-connection-state']
                fabricRole = result[i]['fabric-role']
                shutdown = result[i]['shutdown']
                try:
                    handShakeState = result[i]['handshake-state']
                    if(consistencyChecker == "Yes"):
                        if(handShakeState == "slave-state"):
                            # If the function is consistency check between active & standby changing the slave handshake
                            # state to "master-state" to get around with the key mismatching
                            handShakeState = "master-state"
                            key = "%s-%s-%s-%s-%s-%s" % (dpid, connected, fabricConState, fabricRole, shutdown, handShakeState)
                    else:
                        key = "%s-%s-%s-%s-%s-%s" % (dpid, connected, fabricConState, fabricRole, shutdown, handShakeState)
                except(KeyError):
                    key = "%s-%s-%s-%s-%s" % (dpid, connected, fabricConState, fabricRole, shutdown)

                switchList.append(key)
                i += 1
            except(KeyError):
                helpers.warn("Warning: No switches are detected in the fabric")
                break

        return switchList

    # T5Utilities
    def _gather_fabric_links(self, node="master"):
        '''
        -    This is a helper function. This function is used by "fabric_integrity_checker"

        Description:
        -    Using the "show fabric link" command verify fabric links in the fabric

        '''
        t = test.Test()
        if(node == "master"):
            c = t.controller("master")
        else:
            c = t.controller("slave")

        url = "/api/v1/data/controller/applications/bcf/info/fabric?select=link"
        result = c.rest.get(url)['content']
        fabricLink = []
        try:
            for i in range(0, len(result[0]['link'])):
                src_switch = result[0]['link'][i]['src']['interface']['name']
                dst_switch = result[0]['link'][i]['dst']['interface']['name']
                key = "%s-%s" % (src_switch, dst_switch)
                fabricLink.append(key)
        except(KeyError):
            helpers.warn("Warning: No fabric links are detected in the fabric")

        return fabricLink

    # T5Utilities
    def _gather_endpoints(self, node="master"):
        '''
        -    This is a helper function. This function is used by "fabric_integrity_checker"

        Description:
        -    Using the "show endpoints" command verify endpoints in the fabric

        '''
        t = test.Test()
        if(node == "master"):
            c = t.controller("master")
        else:
            c = t.controller("slave")

        url = "/api/v1/data/controller/applications/bcf/info/endpoint-manager/endpoint"
        result = c.rest.get(url)['content']
        endpoints = []
        try:
            for i in range(0, len(result)):
                mac = result[i]['mac']
                tenant = result[i]['tenant']
                segment = result[i]['segment']
                try:
                    ip = result[i]['ip-address']
                    key = "%s-%s-%s-%s" % (mac, ip, tenant, segment)
                except(KeyError):
                    key = "%s-%s-%s" % (mac, tenant, segment)

                endpoints.append(key)

        except(KeyError):
            helpers.warn("No endpoints are detected in the fabric", 1)

        helpers.log("endpoint list is: %s " % endpoints)
        return endpoints

    # T5Utilities
    def _gather_fabric_lags(self, node="master"):
        '''
        -    This is a helper function. This function is used by "fabric_integrity_checker"

        Description:
        -    Using the "show fabric lags" command verify fabric lags in the fabric

        '''
        t = test.Test()
        if(node == "master"):
            c = t.controller("master")
        else:
            c = t.controller("slave")

        url = "/api/v1/data/controller/core/switch?select=fabric-lag"
        result = c.rest.get(url)['content']
        fabricLags = []

        for i in range(0, len(result)):
            name = ""
            lagType = ""
            srcInt = ""
            dstSwitch = ""
            dstInt = ""

            try:
                for j in range(0, len(result[i]["fabric-lag"])):
                    try:
                        name = result[i]["fabric-lag"][j]["name"]
                        lagType = result[i]["fabric-lag"][j]["lag-type"]
                    except(KeyError):
                        pass
                    for k in range(0, len(result[i]["fabric-lag"][j]["member"])):
                        try:
                            srcInt = result[i]["fabric-lag"][j]["member"][k]["src-interface"]
                            dstSwitch = result[i]["fabric-lag"][j]["member"][k]["dst-switch"]
                            dstInt = result[i]["fabric-lag"][j]["member"][k]["dst-interface"]
                            key = "%s-%s-%s-%s-%s" % (name, lagType, srcInt, dstSwitch, dstInt)
                            fabricLags.append(key)
                        except(KeyError):
                            key = "%s-%s-%s-%s-%s" % (name, lagType, srcInt, dstSwitch, dstInt)
                            fabricLags.append(key)

            except(KeyError):
                pass

        return fabricLags

    # T5Utilities
    def _gather_port_groups(self, node="master"):
        '''
        -    This is a helper function. This function is used by "fabric_integrity_checker"

        Description:
        -    Using the "show fabric lags" command verify fabric lags in the fabric

        '''

        t = test.Test()
        if(node == "master"):
            c = t.controller("master")
        else:
            c = t.controller("slave")

        url = "/api/v1/data/controller/applications/bcf/info/fabric/port-group"
        result = c.rest.get(url)['content']
        portgroups = []

        try:
            for i in range(0, len(result)):
                name = mode = switchName = interface = leafGroup = state = ""
                name = result[i]['name']
                mode = result[i]['mode']

                for k in range(0, len(result[i]['interface'])) :
                    switchName = result[i]['interface'][k]['switch-name']
                    interface = result[i]['interface'][k]['interface-name']
                    # leafGroup = result[i]['interface'][k]['leaf-group']
                    state = result[i]['interface'][k]['state']
                    key = "%s-%s-%s-%s-%s-%s" % (name, mode, switchName, interface, leafGroup, state)
                    portgroups.append(key)

        except(KeyError):
            pass

        helpers.log("portgroup list is: %s " % portgroups)
        return portgroups

    # T5Utilities
    def _gather_forwarding(self, fwdTableName, node="master"):

        t = test.Test()
        if(node == "master"):
            c = t.controller("master")
        else:
            c = t.controller("slave")

        # url = "/api/v1/data/controller/applications/bcf/info/forwarding/network?select=%s" % fwdTableName
        url = "/api/v1/data/controller/applications/bcf/info/forwarding/network/global/%s" % fwdTableName
        result = c.rest.get(url)['content']
        fwdTableList = []

        try:
            # fwdTable = result[0][fwdTableName]
            fwdTable = result
            for i in range(0, len(fwdTable)):

                if(fwdTableName == 'arp-table'):
                    ip = fwdTable[i]['ip']
                    mac = fwdTable[i]['mac']
                    vlanID = fwdTable[i]['vlan-id']
                    key = "%s-%s-%s" % (ip, mac, vlanID)
                    fwdTableList.append(key)

                if(fwdTableName == 'ep-table'):
                    mac = fwdTable[i]['mac']
                    pgLagID = fwdTable[i]['port-group-lag-id']
                    rackID = fwdTable[i]['rack-id']
                    rackLagID = fwdTable[i]['rack-lag-id']
                    vlanID = fwdTable[i]['vlan-id']
                    key = "%s-%s-%s-%s-%s" % (mac, pgLagID, rackID, rackLagID, vlanID)
                    fwdTableList.append(key)

                if(fwdTableName == 'l3-cidr-table'):
                    ip = fwdTable[i]['ip']
                    mask = fwdTable[i]['ip-mask']
                    pgLagID = fwdTable[i]['port-group-lag-id']
                    rackLagID = fwdTable[i]['rack-lag-id']
                    vlanID = fwdTable[i]['vlan-id']
                    vrf = fwdTable[i]['vrf']
                    dstVrf = fwdTable[i]['dst-vrf']
                    key = "%s-%s-%s-%s-%s-%s-%s" % (ip, mask, pgLagID, rackLagID, vlanID, vrf, dstVrf)
                    fwdTableList.append(key)

                if(fwdTableName == 'l3-host-table'):
                    ip = fwdTable[i]['ip']
                    mac = fwdTable[i]['mac']
                    pgLagID = fwdTable[i]['port-group-lag-id']
                    rackLagID = fwdTable[i]['rack-lag-id']
                    vlanID = fwdTable[i]['vlan-id']
                    vrf = fwdTable[i]['vrf']
                    key = "%s-%s-%s-%s-%s-%s" % (ip, mac, pgLagID, rackLagID, vlanID, vrf)
                    fwdTableList.append(key)

                if(fwdTableName == 'my-station-table'):
                    vRouterMac = fwdTable[i]['mac']
                    macMask = fwdTable[i]['mac-mask']
                    key = "%s-%s" % (vRouterMac, macMask)
                    fwdTableList.append(key)

                if(fwdTableName == 'router-ip-table'):
                    routerIP = fwdTable[i]['ip']
                    routerMac = fwdTable[i]['mac']
                    vlanID = fwdTable[i]['vlan-id']
                    key = "%s-%s-%s" % (routerIP, routerMac, vlanID)
                    fwdTableList.append(key)

                if(fwdTableName == 'ecmp-table'):
                    ecmpGroupID = fwdTable[i]['ecmp-group-id']
                    vrf = fwdTable[i]['vrf']
                    vlanID = fwdTable[i]['vlan-id']
                    mac = fwdTable[i]['mac']
                    rackLagID = fwdTable[i]['rack-lag-id']
                    portGroupLagID = fwdTable[i]['port-group-lag-id']
                    key = "%s-%s-%s-%s-%s-%s" % (ecmpGroupID, vrf, vlanID, mac, rackLagID, portGroupLagID)
                    fwdTableList.append(key)

                if(fwdTableName == 'dhcp-table'):
                    dhcpIp = fwdTable[i]['dhcp-ip']
                    routerIp = fwdTable[i]['router-ip']
                    routerMac = fwdTable[i]['router-mac']
                    vlanID = fwdTable[i]['vlan-id']
                    key = "%s-%s-%s-%s" % (dhcpIp, routerIp, routerMac, vlanID)
                    fwdTableList.append(key)

        except(KeyError, IndexError):
            pass

        return fwdTableList

    # T5Utilities
    def _compare_fabric_elements(self, list_b4, list_after, fabricElement):
        '''
        -    This is a helper function. This function is used by "fabric_integrity_checker"

        Description:
            Compare fabric element status from one list to the elements in the other list
            fabricElement can be one of the following:
                1) Switch List
                2) Fabric Links
                3) Fabric Endpoints
                4) Fabric Lags
                5) Port Groups
                6) Show Forwarding Table
        '''
        global warningCount
        global fabricErrorEncounteredFlag
        helpers.log("Before State Change Total # of Fabric Elements: %s " % len(list_b4))
        helpers.log("Before State Change : %s " % list_b4)
        helpers.log("After State Change Total # of Fabric Elements: %s " % len(list_after))
        helpers.log("After State Change: %s " % list_after)

        if(helpers.list_compare(list_b4, list_after)):
            if(fabricElement == "SwitchList"):
                helpers.log("Switch List is intact between states")
            if (fabricElement == "FabricLinks"):
                helpers.log("Fabric Links are intact between states")
            if (fabricElement == "FabricEndpoints"):
                helpers.log("Endpoints are intact between states")
            if (fabricElement == "FabricLags"):
                helpers.log("Fabric Lags are intact between states")
            if (fabricElement == "PortGroups"):
                helpers.log("Port Groups are intact between states")

            if (fabricElement == "fwdARPTable"):
                helpers.log("Controller ARP Table Forwarding entries are intact between states")
            if (fabricElement == "fwdEPTable"):
                helpers.log("Controller EndPoint Table Forwarding entries are intact between states")
            if (fabricElement == "fwdL3CIDRTable"):
                helpers.log("Controller L3 CIDR Table Forwarding entries are intact between states")
            if (fabricElement == "fwdL3HostTable"):
                helpers.log("Controller L3 Host Table Forwarding entries are intact between states")
            if (fabricElement == "fwdMyStationTable"):
                helpers.log("Controller My Station Table Forwarding entries are intact between states")
            if (fabricElement == "fwdRouterIPTable"):
                helpers.log("Controller Router IP Table Forwarding entries are intact between states")
            if (fabricElement == "fwdEcmpTable"):
                helpers.log("Controller ECMP Table Forwarding entries are intact between states")
            if (fabricElement == "fwdDhcpTable"):
                helpers.log("Controller DHCP Table Forwarding entries are intact between states")

            return warningCount

        else:
            # helpers.warn("Got List Different from helpers")
            # helpers.log("B4 is: %s" % list_b4)
            # helpers.log("After is: %s" % list_after)
            if (fabricElement == "SwitchList"):
                helpers.warn("-----------    Switch List Discrepancies    -----------")
            if (fabricElement == "FabricLinks"):
                helpers.warn("-----------    Fabric Link Discrepancies    -----------")
            if (fabricElement == "FabricEndpoints"):
                helpers.warn("-----------    Fabric Endpoints Discrepancies    -----------")
            if (fabricElement == "FabricLags"):
                helpers.warn("-----------    Fabric Lags Discrepancies    -----------")
            if (fabricElement == "PortGroups"):
                helpers.warn("-----------    Port Group Discrepancies    -----------")


            if (fabricElement == "fwdARPTable"):
                helpers.warn("-----------    FWD: ARP Table Discrepancies    -----------")
            if (fabricElement == "fwdEPTable"):
                helpers.warn("-----------    FWD: EndPoint Table Discrepancies    -----------")
            if (fabricElement == "fwdL3CIDRTable"):
                helpers.warn("-----------    FWD: L3 CIDR Table Discrepancies    -----------")
            if (fabricElement == "fwdL3HostTable"):
                helpers.warn("-----------    FWD: L3 Host Table Discrepancies    -----------")
            if (fabricElement == "fwdMyStationTable"):
                helpers.warn("-----------    FWD: My Station Table Discrepancies    -----------")
            if (fabricElement == "fwdRouterIPTable"):
                helpers.warn("-----------    FWD: Router IP Table Discrepancies    -----------")
            if (fabricElement == "fwdEcmpTable"):
                helpers.warn("-----------    FWD: ECMP Table Discrepancies    -----------")
            if (fabricElement == "fwdDhcpTable"):
                helpers.warn("-----------    FWD: DHCP Table Discrepancies    -----------")

            if (len(list_b4) > len(list_after)):
                for item in list_b4:
                    if item not in list_after:
                        if (fabricElement == "SwitchList"):
                            helpers.warn("Switch list item: %s is not present after the state change" % item)
                            fabricErrorEncounteredFlag = True
                        if (fabricElement == "FabricLinks"):
                            helpers.warn("Fabric Link: %s is not present after the state change" % item)
                            fabricErrorEncounteredFlag = True
                        if (fabricElement == "FabricEndpoints"):
                            helpers.warn("Endpoint: %s is not present after the state change" % item)
                        if (fabricElement == "FabricLags"):
                            helpers.warn("Fabric Lag: %s is not present after the state change" % item)
                            fabricErrorEncounteredFlag = True
                        if (fabricElement == "PortGroups"):
                            helpers.warn("Port Group: %s is not present after the state change" % item)
                            fabricErrorEncounteredFlag = True

                        if (fabricElement == "fwdARPTable"):
                            helpers.warn("FWD:ARP Table Entry: %s is not present after the state change" % item)
                        if (fabricElement == "fwdEPTable"):
                            helpers.warn("FWD:EndPoint Table Entry: %s is not present after the state change" % item)
                        if (fabricElement == "fwdL3CIDRTable"):
                            helpers.warn("FWD:L3 CIDR Table Entry: %s is not present after the state change" % item)
                        if (fabricElement == "fwdL3HostTable"):
                            helpers.warn("FWD:L3 Host Table Entry: %s is not present after the state change" % item)
                        if (fabricElement == "fwdMyStationTable"):
                            helpers.warn("FWD:My Station Table Entry: %s is not present after the state change" % item)
                        if (fabricElement == "fwdRouterIPTable"):
                            helpers.warn("FWD:Router IP Table Entry: %s is not present after the state change" % item)
                        if (fabricElement == "fwdEcmpTable"):
                            helpers.warn("FWD:ECMP Table Entry: %s is not present after the state change" % item)
                        if (fabricElement == "fwdDhcpTable"):
                            helpers.warn("FWD:DHCP Table Entry: %s is not present after the state change" % item)

                        warningCount += 1
            else:
                for item in list_after:
                    if item not in list_b4:
                        if (fabricElement == "SwitchList"):
                            helpers.warn("New Switch list item: %s is present after the state change" % item)
                            fabricErrorEncounteredFlag = True
                        if (fabricElement == "FabricLinks"):
                            helpers.warn("New fabric link: %s is present after the state change" % item)
                            fabricErrorEncounteredFlag = True
                        if (fabricElement == "FabricEndpoints"):
                            helpers.warn("New endpoint: %s present after the state change" % item)
                        if (fabricElement == "FabricLags"):
                            helpers.warn("New fabric lag: %s is present after the state change" % item)
                            fabricErrorEncounteredFlag = True
                        if (fabricElement == "PortGroups"):
                            helpers.warn("New portgroup: %s is present after the state change" % item)
                            fabricErrorEncounteredFlag = True

                        if (fabricElement == "fwdARPTable"):
                            helpers.warn("New FWD:ARP Table Entry: %s is present after the state change" % item)
                        if (fabricElement == "fwdEPTable"):
                            helpers.warn("New FWD:EndPoint Table Entry: %s is present after the state change" % item)
                        if (fabricElement == "fwdL3CIDRTable"):
                            helpers.warn("New FWD:L3 CIDR Table Entry: %s is present after the state change" % item)
                        if (fabricElement == "fwdL3HostTable"):
                            helpers.warn("New FWD:L3 Host Table Entry: %s is present after the state change" % item)
                        if (fabricElement == "fwdMyStationTable"):
                            helpers.warn("New FWD:My Station Table Entry: %s is present after the state change" % item)
                        if (fabricElement == "fwdRouterIPTable"):
                            helpers.warn("New FWD:Router IP Table Entry: %s is present after the state change" % item)
                        if (fabricElement == "fwdEcmpTable"):
                            helpers.warn("New FWD:Ecmp Table Entry: %s is present after the state change" % item)
                        if (fabricElement == "fwdDhcpTable"):
                            helpers.warn("New FWD:Dchp Table Entry: %s is present after the state change" % item)
                        warningCount += 1

        return warningCount

    # T5Platform
    def cli_cluster_take_leader(self, node='slave'):
        ''' Function to trigger failover to slave controller via CLI. This function will verify the
            fabric integrity between states

            Input: None
            Output: True if successful, False otherwise
        '''
        t = test.Test()
        c = t.controller(node)
        self.fabric_integrity_checker("before")

        helpers.log("Failover")
        try:
            c.config("config")
            c.send("reauth")
            c.expect(r"Password:")
            c.config("adminadmin")
            c.send("system failover")
            c.expect(r"Failover to this controller node \(\"y\" or \"yes\" to continue\)?")
            c.config("yes")
            # sleep(30)
            helpers.sleep(90)
        except:
            helpers.test_log(c.cli_content())
            return False
        else:
            return self.fabric_integrity_checker("after")

    # T5Platform
    def rest_get_disconnect_switch(self, node='master'):
        """
        Get fabric connection state of the switch

        Inputs:
        | node | Alias of the controller node |

        Return Value:
        - the list of switches in suspended state
        """
        t = test.Test()
        c = t.controller(node)
        url = '/api/v1/data/controller/applications/bcf/info/fabric/switch'
        helpers.log("get switch fabric connection state")

        c.rest.get(url)
        data = c.rest.content()
        info = []
        if (data):
            for i in range(0, len(data)):
                if data[i]['connected'] == False :
                    if 'fabric-connection-state' in data[i].keys() and data[i]['fabric-connection-state'] == "not_connected":
                        info.append(data[i]['name'])
        helpers.test_log("USER INFO:  the switches in NOT connected states:  %s" % info)
        return info

    # T5ZTN
    def cli_reboot_switch(self, node, switch):
        """
        Reboot switch, switches from controller's CLI

        Inputs:
        | node | reference to controller as defined in .topo file |
        | switch | Alias, IP, MAC of the switch, or All |

        Return Value:
        - True if successfully executed reboot command, False otherwise
        """
        t = test.Test()
        c = t.controller(node)
        c.config("")
        helpers.log("Executing 'system reboot switch %s' command"
                    " on node %s" % (switch, node))
        try:
            c.send("system reboot switch %s" % switch)
            helpers.log(c.cli_content())
            options = c.expect([r'to continue', c.get_prompt(),
                                r'Waiting for reconnect'], timeout=30)
            if options[0] == 0:
                helpers.log("Switch has fabric role configured. Confirming.")
                c.send("yes")
                c.expect(c.get_prompt(), timeout=120)
            if options[0] == 2:
                helpers.log("Rebooting all switches. Waiting for CLI prompt...")
                c.expect(c.get_prompt(), timeout=120)
            if 'Error' in c.cli_content():
                helpers.log(c.cli_content())
                helpers.log("Error rebooting the switch")
                return False
        except:
            helpers.log(c.cli_content())
            helpers.log("Error rebooting the switch")
            return False

        helpers.log("Reboot command executed successfully")
        return True

    # T5
    def rest_disable_fabric_interface(self, switch, intf):
        t = test.Test()
        c = t.controller('master')
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

    # T5
    def rest_enable_fabric_interface(self, switch, intf, timeout=30):
        t = test.Test()
        c = t.controller('master')

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

    # T5Platform
    def rest_add_tenant_vns_scale(self, tenantcount='1', tname='T', tenant_create=None,
                                        vnscount='1', vname='V', vns_create='yes',
                                        vns_ip=None, base="100.0.0.100", step="0.1.0.0", mask="24"
                                        ):
        '''
        Function to add l3 endpoint to all created vns
        Input: tennat , switch , interface
        The ip address is taken from the logical interface, the last byte is modified to 253
        output : will add end into all vns in a tenant
        '''

        t = test.Test()
        c = t.controller('master')

        helpers.test_log("Entering ==> rest_add_tenant_vns_scale ")

        for count in range(0, int(tenantcount)):
            tenant = tname + str(count)

            if tenant_create == 'yes':
                if not self.rest_add_tenant(tenant):
                    helpers.test_failure("USER Error: tenant is NOT configured successfully")
            elif  tenant_create is None:
                if (re.match(r'None.*', self.cli_show_tenant(tenant))):
                    helpers.test_log("tenant: %s  does not exist,  creating tenant")
                    if not self.rest_add_tenant(tenant):
                        helpers.test_failure("USER Error: tenant is NOT configured successfully")

            if vns_create == 'yes' :
                helpers.test_log("creating tenant L2 vns")
                if not self.rest_add_vns_scale(tenant, vnscount, vname):
                    helpers.test_failure("USER Error: VNS is NOT configured successfully for tenant %s" % tenant)
            if vns_ip is not None:
                i = 1
                while  (i <= int(vnscount)):
                    vns = vname + str(i)
                    self.rest_add_router_intf(tenant, vns)
                    if not self.rest_add_vns_ip(tenant, vns, base, mask):
                        helpers.test_failure("USER Error: VNS is NOT configured successfully for tenant %s" % tenant)
                    ip_addr = helpers.get_next_address('ipv4', base, step)
                    base = ip_addr
                    i = i + 1

        c.cli('show running-config tenant')['content']
        return True

    # T5
    def rest_add_interface_to_all_vns(self, tenant, switch, intf, vlan=1):
        '''
        Function to add interface to all created vns
        Input: tennat , switch , interface
        output : will add specified interfaces into all vns in a tenant as tagged starting with 1
        '''
        t = test.Test()
        c = t.controller('master')
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

    # T5
    def cli_show_tenant(self, tenant):
        '''
        show tenant
        Input: tenant
        Output:
        Author: Mingtao
        '''
        t = test.Test()
        c = t.controller('master')
        cli = 'show tenant ' + tenant
        content = c.cli(cli)['content']
        temp = helpers.strip_cli_output(content)
        return temp

    # T5
    def rest_add_tenant(self, tenant):

        t = test.Test()
        c = t.controller('master')
        url = '/api/v1/data/controller/applications/bcf/tenant[name="%s"]' % (tenant)
        try:
            c.rest.put(url, {"name": tenant})
        except:
            return False
        else:
            return True

    # T5
    def rest_add_vns_scale(self, tenant, count, name='v'):
        '''
        Functiont to add vns in scale
        Input: tenant , no of vns to be created,  the start leter of the name
        Output: system will created specified no of vns
        '''
        t = test.Test()
        c = t.controller('master')
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

    # T5L3
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

    # T5L3
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
