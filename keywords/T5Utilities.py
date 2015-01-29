import autobot.helpers as helpers
import autobot.test as test
import re
from BsnCommon import BsnCommon as bsnCommon

'''
    ::::::::::    README    ::::::::::::::

    This T5Utilities file is used to abstract the T5 utility
    functions. Please include any utility functions that are not
    specific to your test suites here.

'''


''' Global variables to save the state
    Used by: fabric_integrity_checker
'''
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


class T5Utilities(object):

    def __init__(self):
        pass


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



    def cli_get_num_nodes(self):
        '''
            Utility functions to return the number of nodes in a cluster.
            Returns:
                1 : single node cluster
                2 : HA cluster
        '''
        t = test.Test()
        c = t.controller('master')

        c.cli('show controller')
        content = c.cli_content()
        temp = helpers.strip_cli_output(content)
        temp = helpers.str_to_list(temp)
        num = 0
        for line in temp:
            match = re.match(r'.*(active|standby).*', line)
            if match:
                num = num + 1
            else:
                helpers.log("INFO: not for controller  %s" % line)
        helpers.log("INFO: There are %d of controller(s) in the cluster" % num)
        return num


    def start_floodlight_monitor(self):
        global floodlightMonitorFlag

        try:
            t = test.Test()
            c1 = t.controller('c1')
            c2 = t.controller('c2')
            c1_pidList = self.get_floodlight_monitor_pid('c1')
            c2_pidList = self.get_floodlight_monitor_pid('c2')
            for c1_pid in c1_pidList:
                # if (re.match("^d", c1_pid)):
                    c1.sudo('kill -9 %s' % (c1_pid))
            for c2_pid in c2_pidList:
                # if (re.match("^d", c2_pid)):
                    c2.sudo('kill -9 %s' % (c2_pid))

            # Add rm of the file if file already exist in case of a new test
            c1.sudo("tail -f /var/log/floodlight/floodlight.log | grep --line-buffered ERROR > %s &" % "c1_floodlight_dump.txt")
            c2.sudo("tail -f /var/log/floodlight/floodlight.log | grep --line-buffered ERROR > %s &" % "c2_floodlight_dump.txt")

            floodlightMonitorFlag = True
            return True

        except:
            helpers.log("Exception occured while starting the floodlight monitor")
            return False

    def restart_floodlight_monitor(self, node):

        global floodlightMonitorFlag

        if(floodlightMonitorFlag):
            t = test.Test()
            c = t.controller(node)
            result = c.sudo('ls *_dump.txt')
            filename = re.split('\n', result['content'])[1:-1]
            c.sudo("tail -f /var/log/floodlight/floodlight.log | grep --line-buffered ERROR >> %s &" % filename[0].strip('\r'))
            return True
        else:
            return True



    def stop_floodlight_monitor(self):

        global floodlightMonitorFlag

        if(floodlightMonitorFlag):
            c1_pidList = self.get_floodlight_monitor_pid('c1')
            c2_pidList = self.get_floodlight_monitor_pid('c2')
            t = test.Test()
            c1 = t.controller('c1')
            c2 = t.controller('c2')
            helpers.log("Stopping Floodlight Monitor on C1")
            for c1_pid in c1_pidList:
                c1.sudo('kill -9 %s' % (c1_pid))
            helpers.log("Stopping Floodlight Monitor on C2")
            for c2_pid in c2_pidList:
                c2.sudo('kill -9 %s' % (c2_pid))
            floodlightMonitorFlag = False

            try:
                helpers.log("****************    Floodlight Log From C1    ****************")
                result = c1.sudo('cat c1_floodlight_dump.txt')
                split = re.split('\n', result['content'])[1:-1]
                if split:
                    helpers.warn("Floodlight Errors Were Detected At: %s " % helpers.ts_long_local())

            except(AttributeError):
                helpers.log("No Errors From Floodlight Monitor on C1")

            try:
                helpers.log("****************    Floodlight Log From C2    ****************")
                result = c2.sudo('cat c2_floodlight_dump.txt')
                split = re.split('\n', result['content'])[1:-1]
                if split:
                    helpers.warn("Floodlight Errors Were Detected At: %s " % helpers.ts_long_local())
            except(AttributeError):
                helpers.log("No Errors From Floodlight Monitor on C2")

            return True

        else:
            helpers.log("FloodlightMonitorFlag is not set: Returning")



    def get_floodlight_monitor_pid(self, role):
        t = test.Test()
        c = t.controller(role)
        helpers.log("Verifing for monitor job")
        c_result = c.sudo('ps ax | grep tail | grep sudo | awk \'{print $1}\'')
        split = re.split('\n', c_result['content'])
        pidList = split[1:-1]
        return pidList


    def cli_run(self, node, command, cmd_timeout=45, user='admin', password='adminadmin', soft_error=False):
        """
        Run given CLI command

        Inputs:
        | node | Reference to switch/controller as defined in .topo file |
        | command | CLI command to run |
        | cmd_timeout | Timeout for given command to be executed and controller prompt to be returned |
        | user | Username to use when logging into the node |
        | password | Password for the user |
        | soft_error | Soft Error flag |

        Return Value:
        - True if command executed with no errors, False otherwise
        """

        helpers.test_log("Running command: %s on node %s" % (command, node))
        t = test.Test()
        if user == 'admin':
            c = t.controller(node)
        else:
            bsn_common = bsnCommon()
            ip_addr = bsn_common.get_node_ip(node)
            c = t.node_spawn(ip=ip_addr, user=user, password=password)
        try:
            c.config(command, timeout=cmd_timeout)
            if "Error" in c.cli_content():
                helpers.test_failure(c.cli_content(), soft_error)
                return False
        except:
            helpers.test_failure(c.cli_content(), soft_error)
            return False
        else:
            return True



    def cli_run_and_verify_output(self, node, command, expected, flag='True', cmd_timeout=5, user='admin', password='adminadmin', node_type='controller', soft_error=False):
        """
        Run given CLI command and verify that expected content is in the command output

        Inputs:
        | node | Reference to switch/controller as defined in .topo file |
        | command | CLI command to run |
        | expected | String expected in the output of the command |
        | flag | Toggle to switch whether expected string should be in the output (default) or should not be there |
        | cmd_timeout | Timeout for given command to be executed and controller prompt to be returned |
        | user | Username to use when logging into the node |
        | password | Password for the user |
        | node_type | Type of the node - controller/switch |
        | soft_error | Soft Error flag |

        Return Value:
        - True if command executed with no errors, False otherwise
        """
        helpers.test_log("Running command: %s on node %s" % (command, node))
        t = test.Test()
        if node_type == 'controller':
            if user == 'admin':
                c = t.controller(node)
            else:
                bsn_common = bsnCommon()
                ip_addr = bsn_common.get_node_ip(node)
                c = t.node_spawn(ip=ip_addr, user=user, password=password)
        if node_type == 'switch':
            c = t.switch(node)
        try:
            c.send(command)
            c.expect([c.get_prompt()], timeout=cmd_timeout)
            if "Error" in c.cli_content():
                if (re.match(r'.*[\?\t]$', command)
                    and "Error: Unexpected end of command" in c.cli_content()):
                    helpers.log("Analyzing available completions")
                else:
                    helpers.test_failure(c.cli_content(), soft_error)
                    return False
            content = c.cli_content()
            content = helpers.strip_cli_output(content)
            helpers.log("Length of contents is %s" % str(len(content)))
            if not content:
                if flag == 'True':
                    helpers.log("Failure: expecting \n%s but the output is empty" % (expected, content))
                    helpers.test_failure(c.cli_content(), soft_error)
                    return False
                else:
                    helpers.log("Not expecting \n%s and the output is empty" % expected)
                    return True

            helpers.log("Expected result is %s" % str(helpers.any_match(content, expected)))

            if expected in content and flag == 'True':
                helpers.log("Expecting %s in \n%s \nand got it" % (expected, content))
                return True
            elif (expected not in content) and flag == 'False':
                helpers.log("Not expecting %s in \n%s \nand did not get it" % (expected, content))
                return True
            else:
                helpers.log("Failure: expecting %s in \n%s \nto be %s" % (expected, content, flag))
                helpers.test_failure(c.cli_content(), soft_error)
                return False
        except:
            helpers.test_failure(c.cli_content(), soft_error)
            return False
        else:
            return True


    def cli_run_and_verify_output_length(self, node, command, length, cmd_timeout=5, user='admin', password='adminadmin', node_type='controller', soft_error=False):
        """
        Run given CLI command and verify that expected content is in the command output

        Inputs:
        | node | Reference to switch/controller as defined in .topo file |
        | command | CLI command to run |
        | length | Expected length of the output |
        | cmd_timeout | Timeout for given command to be executed and controller prompt to be returned |
        | user | Username to use when logging into the node |
        | password | Password for the user |
        | node_type | Type of the node - controller/switch |
        | soft_error | Soft Error flag |

        Return Value:
        - True if command executed with no errors, False otherwise
        """
        helpers.test_log("Running command: %s on node %s" % (command, node))
        t = test.Test()
        if node_type == 'controller':
            if user == 'admin':
                c = t.controller(node)
            else:
                bsn_common = bsnCommon()
                ip_addr = bsn_common.get_node_ip(node)
                c = t.node_spawn(ip=ip_addr, user=user, password=password)
        if node_type == 'switch':
            c = t.switch(node)

        length = int(length)
        c.send(command)
        options = c.expect([c.get_prompt(),
          r'hit q to quit'],
          timeout=cmd_timeout)
        if options[0] == 0:
            helpers.log(c.cli_content())
        if options[0] == 1:
            while options[0] == 1:
                helpers.log(c.cli_content())
                content = c.cli_content()
                content = helpers.str_to_list(content)
                helpers.log("Length of contents is %s" % str(len(content)))
                if (len(content) != (length + 2)
                    and len(content) != (length + 1)):
                    helpers.log("Expected length %s not matched"
                                % str(length))
                    return helpers.test_failure(c.cli_content(), soft_error)

                c.send(' ')
                options = c.expect([c.get_prompt(),
                   r'.*hit q to quit, any character to continue'],
                   timeout=cmd_timeout)
                if options[0] == 0:
                    if len(content) > (length + 2):
                        helpers.log("Expected length %s not matched"
                                    % str(length))
                        return helpers.test_failure(c.cli_content(), soft_error)

        if "Error" in c.cli_content():
            if (re.match(r'.*[\?\t]$', command)
                and "Error: Unexpected end of command" in c.cli_content()):
                helpers.log("We were analyzing CLI suggestions")
            else:
                helpers.test_failure(c.cli_content(), soft_error)
                return False

    def cli_get_number_of_logs_in_last(self, node, period):
        """
        Run "show logging syslog last <>" and returns number of entries

        Inputs:
        | node | Reference to switch/controller as defined in .topo file |
        | period | Time period |

        Return Value:
        - Number of logs, or -1 in case of error
        """
        helpers.test_log("Running command: show logging syslog last"
                         "%s on node %s" % (period, node))
        t = test.Test()
        c = t.controller(node)
        content = c.config("show logging syslog last %s | wc -l"
                           % period)["content"]
        helpers.log(c.cli_content())
        if "Error" in c.cli_content():
            helpers.log("Error in command")
            return -1
        else:
            output = helpers.strip_cli_output(content)
            return int(output)


    def cli_get_session_hash(self):
	''' Function that returns hash value of session id'''
        helpers.test_log("Getting hash of sesison id")
        t = test.Test()
        c = t.controller('master')
        content = c.config("show session")['content']
        output = helpers.strip_cli_output(content)
        lines = helpers.str_to_list(output)
        for i, line in enumerate(lines):
            if '*' in line:
                line = line.split()
                helpers.test_log("Session hash is %s" % line[2])
                return line[2]
        return None



    def rest_switch_int_shut(self, switch, interface):
        ''' This function will shut down the switch interface
        '''
        t = test.Test()
        c = t.controller("master")
        # url = '/api/v1/data/controller/core/switch-config[name="%s"]/interface[name="%s"]' % (switch, interface)
        # result = c.rest.patch(url,{"shutdown": True})

        # if c.rest.status_code_ok():
        #    return True
        # else:
        #    return False
        try:
            c.config("switch %s" % switch)
            c.config("interface %s" % interface)
            c.config("shutdown")
            assert "Error" not in c.cli_content()
        except:
            helpers.test_log(c.cli_content())
            return False
        else:
            return True



    def rest_switch_int_noshut(self, switch, interface):
        ''' This function will no-shut the switch interface
        '''
        t = test.Test()
        c = t.controller("master")
        # url = '/api/v1/data/controller/core/switch-config[name="%s"]/interface[name="%s"]/shutdown' % (switch, interface)
        # result = c.rest.delete(url,{})

        # if c.rest.status_code_ok():
        #    return True
        # else:
        #    return False
        try:
            c.config("switch %s" % switch)
            c.config("interface %s" % interface)
            c.config("no shutdown")
            assert "Error" not in c.cli_content()
        except:
            helpers.test_log(c.cli_content())
            return False
        else:
            return True


    def cli_diff_running_configs(self, node, file1, file2):
        ''' This function will compare 2 controller running configs. (Ideall between
            active and a standby node.
            It'll do a diff for the two files, and returns true if there are only
            12 lines of diff
        '''

        t = test.Test()
        n = t.node(node)
        output = n.sudo("diff %s %s | wc -l" % (file1, file2), timeout=120)['content']
        if '12' in output:
            helpers.log("Running Configs match between file1 & file2")
            return True
        else:
            helpers.log("Running Configs didn't match between file1 & file2 ")
            return False






''' Following class will perform T5 platform related multithreading activities
    Instantiating this class is done by functions reside in T5Platform.

    Extends threading.Thread
'''

from threading import Thread
import keywords.Host as Host

class T5PlatformThreads(Thread):

    def __init__(self, threadID, name, **kwargs):
            Thread.__init__(self)
            self.threadID = threadID
            self.name = name
            self.kwargs = kwargs


    def run(self):
        if(self.name == "switchReboot"):
            self.switch_reboot(self.kwargs.get("switch"))
        if(self.name == "switchPowerCycle"):
            self.switch_power_cycle(self.kwargs.get("switch"))
        if(self.name == "failover"):
            self.controller_failover()
        if(self.name == "activeReboot"):
            self.controller_reboot('master')
        if(self.name == "standbyReboot"):
            self.controller_reboot('slave')
        if(self.name == "hostPing"):
            self.host_ping(self.kwargs.get("host"), self.kwargs.get("IP"))



    def switch_reboot(self, switchName):
        try:
            print ("Starting Thread %s For Rebooting Switch: %s" % (self.threadID, switchName))
            t = test.Test()
            switch = t.switch(switchName)
            cli_input = 'reload now'
            switch.enable('')
            switch.send(cli_input)
            helpers.sleep(60)
            common = bsnCommon()
            if(common.verify_ssh_connection(switchName)):
                print ("Exiting Thread %s After Rebooting Switch: %s" % (self.threadID, switchName))
                return True
            else:
                print ("Connection Failure in Thread %s After Rebooting Switch: %s" % (self.threadID, switchName))
                return False
        except:
            helpers.test_failure("Failure during switch:%s reboot" % (switchName))
            print ("Failure during switch:%s reboot" % (switchName))
            return False

    def switch_power_cycle(self, switchList):
        try:
            t = test.Test()
            newSwitchList = switchList.split(' ')
            for switchName in newSwitchList:
                t.power_cycle(switchName, 0)
            helpers.sleep(120)
            return True
        except:
            helpers.test_failure("Failure during switch:%s power cycle" % (switchName))
            print ("Failure during switch:%s power cycle" % (switchName))
            return False


    def controller_failover(self):
        from T5Platform import T5Platform
        platform = T5Platform()
        print ("Starting Thread %s For Controller Failover" % (self.threadID))
        returnVal = platform._cluster_election(True)
        print ("Exiting Thread %s After Controller Failover" % (self.threadID))
        return returnVal

    def controller_reboot(self, node):
        from T5Platform import T5Platform
        platform = T5Platform()
        print ("Starting Thread %s For Controller Reboot for Node: " % (self.threadID), node)
        if (node == "master"):
            returnVal = platform.cluster_node_reboot()
        else:
            returnVal = platform.cluster_node_reboot(False)
        print ("Exiting Thread %s After Controller Reboot for Node: " % (self.threadID), node)
        return returnVal

    def host_ping(self, host, IP):
        print ("Starting Thread ID.. %s" % str(self.threadID))
        myhost = Host.Host()
        loss = myhost.bash_ping(host, IP, count=10)
        print("Exiting Thread ...%s" % str(self.threadID))







