import autobot.helpers as helpers
import autobot.test as test
from T5Utilities import T5Utilities as utilities
from T5Utilities import T5PlatformThreads
from BsnCommon import BsnCommon as bsnCommon
from time import sleep
import re
import keywords.Mininet as mininet
import keywords.T5 as T5
import keywords.T5L3 as T5L3
import keywords.Host as Host
import keywords.Ixia as Ixia

mininetPingFails = 0
hostPingFails = 0
leafSwitchList = []

class T5Platform(object):

    def __init__(self):
        pass    
    
    def rest_verify_show_cluster(self, **kwargs):
        
        '''Using the 'show cluster' command verify the cluster formation across both nodes
	       Also check for the formation integrity
	       Additional inputs: IP Addresses of the Controllers can be specified as: 'c1=a.b.c.d  c2=a.b.e.f'
	    '''
         
        try:
            t = test.Test()
            if 'c1' in kwargs:
                c1 = t.node_spawn(ip=kwargs.get('c1'))
            else:
                c1 = t.controller("c1")
            if 'c2' in kwargs:
                c2 = t.node_spawn(ip=kwargs.get('c2'))
            else:
                c2 = t.controller("c2")
            
            url = '/api/v1/data/controller/cluster'
            
            result = c1.rest.get(url)['content']
            reported_active_by_c1 = result[0]['status']['domain-leader']['leader-id']
            
            result = c2.rest.get(url)['content']
            reported_active_by_c2 = result[0]['status']['domain-leader']['leader-id']
            
            if(reported_active_by_c1 != reported_active_by_c2):
                helpers.log("Both controllers %s & %s are declaring themselves as active" \
                        % (reported_active_by_c1, reported_active_by_c2))
                helpers.test_failure("Error: Inconsistent active/stand-By cluster formation detected")
                return False
            else:
                helpers.log("Active controller id is: %s " % reported_active_by_c1)
                helpers.log("Pass: Consistent active/standby cluster formation verified")
                return True
            
        except Exception, err:
            helpers.test_failure("Exception in: rest_verify_ha_cluster %s : %s " % (Exception, err))
            return False


    def _cluster_election(self, rigged):
        ''' Invoke "cluster election" commands: re-run or take-leader
            If: "rigged" is true then verify the active controller change.
            Else: execute the election rerun
        '''
        t = test.Test()
        subordinate = t.controller("subordinate")
        main = t.controller("main")

        mainID,subordinateID = self.getNodeID()
        if(mainID == -1 and subordinateID == -1):
            return False

        helpers.log("Current subordinate ID is : %s / Current main ID is: %s" % (subordinateID, mainID))

        url = '/api/v1/data/controller/cluster/config/new-election'

        if(rigged):
            subordinate.rest.post(url, {"rigged": True})
        else:
            subordinate.rest.post(url, {"rigged": False})
        
        sleep(30)

        newMainID = self.getNodeID(False)
        if(newMainID == -1):
            return False

        if(mainID == newMainID):
            if(rigged):
                helpers.test_failure("Fail: Main didn't change after executing take-leader")
                return False
            else:
                helpers.log("Pass: Leader election re-run successful - Leader %s  is intact " % (mainID))
                return True
        else:
            helpers.log("Pass: Take-Leader successful - Leader changed from %s to %s" % (mainID, newMainID))
            return True


    def rest_verify_cluster_election_take_leader(self):
        ''' Invoke "cluster election take-leader" command and verify the controller state
            This function will invoke the take_leader functionality and verify the fabric integrity between 
            before and after states
        '''
        obj = utilities()
        utilities.fabric_integrity_checker(obj,"before")
        returnVal = self._cluster_election(True)
        if(not returnVal):
            return False
        sleep(30)
        return utilities.fabric_integrity_checker(obj, "after")
    
    
    def cli_cluster_take_leader(self):
        ''' Function to trigger failover to subordinate controller via CLI. This function will verify the 
            fabric integrity between states
            
            Input: None
            Output: True if successful, False otherwise
        '''
        t = test.Test()
        c = t.controller('subordinate')
        obj = utilities()
        utilities.fabric_integrity_checker(obj,"before")

        helpers.log("Failover")
        try:
            c.config("config")
            c.send("reauth")
            c.expect(r"Password:")
            c.config("adminadmin")
            c.send("system failover")
            c.expect(r"Election may cause role transition: enter \"yes\" \(or \"y\"\) to continue:")
            c.config("yes")
            sleep(30)
        except:
            helpers.test_log(c.cli_content())
            return False
        else:
            return utilities.fabric_integrity_checker(obj, "after")


    def rest_verify_cluster_election_rerun(self):
        ''' Invoke "cluster election re-run" command and verify the controller state
        '''
        obj = utilities()
        utilities.fabric_integrity_checker(obj, "after")
        returnVal = self._cluster_election(False)
        if(not returnVal):
            return False
        sleep(30)
        return utilities.fabric_integrity_checker(obj, "before")
        

    def cluster_node_reboot(self, mainNode=True):

        ''' Reboot a node and verify the cluster leadership.
            Reboot Main in dual node setup: mainNode == True
        '''
        t = test.Test()
        main = t.controller("main")
        obj = utilities()
        
        if (utilities.cli_get_num_nodes(obj) == 1):
            singleNode = True
        else:
            singleNode = False
            

        if(singleNode):
            mainID = self.getNodeID(False)
        else:
            mainID,subordinateID = self.getNodeID()
        
        if(singleNode):
            if (mainID == -1):
                return False
        else:
            if(mainID == -1 and subordinateID == -1):
                return False
        
        try:
            if(mainNode):
                ipAddr = main.ip()
                main.enable("system reboot", prompt="Confirm \(yes to continue\)")
                main.enable("yes")
                helpers.log("Main is rebooting")
                sleep(90)
            else:
                subordinate = t.controller("subordinate")
                ipAddr = subordinate.ip()
                subordinate.enable("system reboot", prompt="Confirm \(yes to continue\)")
                subordinate.enable("yes")
                helpers.log("Subordinate is rebooting")
                sleep(90)
        except:
            helpers.log("Node is rebooting")
            sleep(90)
            count = 0
            while (True):
                loss = helpers.ping(ipAddr)
                helpers.log("loss is: %s" % loss)
                if(loss != 0):
                    if (count > 5): 
                        helpers.warn("Cannot connect to the IP Address: %s - Tried for 5 Minutes" % ipAddr)
                        return False
                    sleep(60)
                    count += 1
                    helpers.log("Trying to connect to the IP Address: %s - Try %s" % (ipAddr, count))
                else:
                    break
       
        if(singleNode):
            newMainID = self.getNodeID(False)
        else:
            newMainID, newSubordinateID = self.getNodeID()
            
        if(singleNode):
            if (newMainID == -1):
                return False
        else:
            if(newMainID == -1 and newSubordinateID == -1):
                return False


        if(singleNode):
            if(mainID == newMainID):
                obj.restart_floodlight_monitor("main")
                helpers.log("Pass: After the reboot cluster is stable - Main is still : %s " % (newMainID))
                return True
            else:
                helpers.log("Fail: Reboot Failed. Cluster is not stable.  Before the reboot Main is: %s  \n \
                    After the reboot Main is: %s " %(mainID, newMainID))
        else:
            if(mainNode):
                obj.restart_floodlight_monitor("subordinate")
            else:
                obj.restart_floodlight_monitor("main")
            
            if(mainNode):      
                if(mainID == newSubordinateID and subordinateID == newMainID):
                    helpers.log("Pass: After the reboot cluster is stable - Main is : %s / Subordinate is: %s" % (newMainID, newSubordinateID))
                    return True
                else:
                    helpers.log("Fail: Reboot Failed. Cluster is not stable. Before the main reboot Main is: %s / Subordinate is : %s \n \
                            After the reboot Main is: %s / Subordinate is : %s " %(mainID, subordinateID, newMainID, newSubordinateID))
                    obj.stop_floodlight_monitor()
                    return False
            else:
                if(mainID == newMainID and subordinateID == newSubordinateID):
                    helpers.log("Pass: After the reboot cluster is stable - Main is : %s / Subordinate is: %s" % (newMainID, newSubordinateID))
                    return True
                else:
                    helpers.log("Fail: Reboot Failed. Cluster is not stable. Before the subordinate reboot Main is: %s / Subordinate is : %s \n \
                            After the reboot Main is: %s / Subordinate is : %s " %(mainID, subordinateID, newMainID, newSubordinateID))
                    obj.stop_floodlight_monitor()
                    return False


    def _cluster_node_shutdown(self, mainNode=True):
        ''' Shutdown the node
        '''
        t = test.Test()
        main = t.controller("main")
        obj = utilities()

        mainID,subordinateID = self.getNodeID()
        if(mainID == -1 and subordinateID == -1):
            return False

        if(mainNode):
            main.enable("shutdown", prompt="Confirm Shutdown \(yes to continue\)")
            main.enable("yes")
            helpers.log("Main is shutting down")
            sleep(10)
        else:
            subordinate = t.controller("subordinate")
            subordinate.enable("shutdown", prompt="Confirm Shutdown \(yes to continue\)")
            subordinate.enable("yes")
            helpers.log("Subordinate is shutting down")
            sleep(10)

        newMainID = self.getNodeID(False)
        if(newMainID == -1):
            return False

        if(mainNode):
            if(subordinateID == newMainID):
                helpers.log("Pass: After the shutdown cluster is stable - New main is : %s " % (newMainID))
                return True
            else:
                helpers.log("Fail: Shutdown Failed. Cluster is not stable. Before the main node shutdown Main is: %s / Subordinate is : %s \n \
                        After the shutdown Main is: %s " %(mainID, subordinateID, newMainID))
                return False
        else:
            if(mainID == newMainID):
                helpers.log("Pass: After the subordinate shutdown cluster is stable - Main is still: %s " % (newMainID))
                return True
            else:
                helpers.log("Fail: Shutdown failed. Cluster is not stable. Before the subordinate shutdown Main is: %s / Subordinate is : %s \n \
                        After the shutdown Main is: %s " %(mainID, subordinateID, newMainID))
                return False


    def cli_verify_cluster_main_reboot(self):
        obj = utilities()
        utilities.fabric_integrity_checker(obj,"before")
        returnVal = self.cluster_node_reboot()
        if(not returnVal):
            return False
        return utilities.fabric_integrity_checker(obj,"after")

    def cli_verify_cluster_subordinate_reboot(self):
        obj = utilities()
        utilities.fabric_integrity_checker(obj,"before")
        returnVal = self.cluster_node_reboot(False)
        if(not returnVal):
            return False
        return utilities.fabric_integrity_checker(obj,"after")

    def cli_verify_cluster_main_shutdown(self):
        obj = utilities()
        utilities.fabric_integrity_checker(obj,"before")
        returnVal = self._cluster_node_shutdown()
        if(not returnVal):
            return False
        return utilities.fabric_integrity_checker(obj,"after")

    def cli_verify_cluster_subordinate_shutdown(self):
        obj = utilities()
        utilities.fabric_integrity_checker(obj,"before")
        returnVal = self._cluster_node_shutdown(False)
        if(not returnVal):
            return False
        return utilities.fabric_integrity_checker(obj,"after")


    def verify_HA_with_disruption(self, disruptMode="switchReboot", disruptTime="during", failoverMode="failover", **kwargs ):
        '''
            This function will carry out different disruptions during failovers & verify fabric 
            integrity. Disruptions will carry out in distributed manner. For eg. if disruptMode is "switchReboot", this
            functions will schedule a dedicated thread to each switch reboot while carrying out failover function as defined by 
            'disruptTime' argument.
            
            Inputs:
                disruptMode  : "switchReboot"    - Reboot leaf or spine switch eg: "switch=spine0"  / "switch=spine0 leaf0-a"
                
                disruptTime : Disruptions happens 'during' or 'before" the HA event
                
                failoverMode : "failover"     - Failover by issuing failover command (default)
                               "mainReboot" - Failover by rebooting active controller  
                               
                kwargs: "switch=spien0 leaf0-a"                
                                
        '''
        
        obj = utilities()
        utilities.fabric_integrity_checker(obj,"before")
        
        threadCounter = 0
        threadList = []

        if (disruptMode == "switchReboot"):
            switchList = kwargs.get('switch').split(' ')
            for i,switchName in enumerate(switchList):
                threadList.append("thread" + '%s' % threadCounter)
                threadList[i] = T5PlatformThreads(threadCounter, "switchReboot",  switch=switchName)
                threadCounter += 1
            
        disruptThreadCounter = threadCounter
        if(len(threadList)== 0):
            helpers.warn("No disruptMode arguments were detected. Exiting")
            return False
        
        if(failoverMode == "failover"):
            threadList.append("thread" + '%s' % threadCounter)
            threadList[len(threadList)-1] = T5PlatformThreads(threadCounter, "failover")
            threadCounter += 1
        elif(failoverMode == "activeReboot"):
            threadList.append("thread" + '%s' % threadCounter)
            threadList[len(threadList)-1] = T5PlatformThreads(threadCounter, "activeReboot", "")
            threadCounter += 1
        elif(failoverMode == "standbyReboot"):
            threadList.append("thread" + '%s' % threadCounter)
            threadList[len(threadList)-1] = T5PlatformThreads(threadCounter, "standbyReboot", "")
            threadCounter += 1


        if(disruptTime == "during"):
            for thread in threadList:
                helpers.log("Starting thread: %s" % thread)
                thread.start()
        elif(disruptTime == "before"):    
            for i,thread in enumerate(threadList):
                helpers.log("Starting thread: %s" % thread)
                thread.start()
                if (i == disruptThreadCounter-1):
                    sleep(45)

        for thread in threadList:
            helpers.log("Joining thread: %s" % thread)
            thread.join()
            
        sleep(30)
        return utilities.fabric_integrity_checker(obj,"after")
        
        # Create new threads
        #thread1 = Thread(target= self._verify_HA_duringReboot(kwargs.get("switch")))
        #thread2 = Thread(target= self.cli_cluster_take_leader())
 




    def rest_add_user(self, numUsers=1):
        numWarn = 0
        t = test.Test()
        main = t.controller("main")
        url = "/api/v1/data/controller/core/aaa/local-user"
        usersString = []
        numErrors = 0
        for i in range (0, int(numUsers)):
            user = "user" + str(i+1)
            usersString.append(user)
            main.rest.post(url, {"user-name": user})
            sleep(1)
            
            if not main.rest.status_code_ok():
                helpers.test_failure(main.rest.error())
                numErrors += 1
            else:
                helpers.log("Successfully added user: %s " % user)

        if(numErrors > 0):
            return False
        else:
            url = "/api/v1/data/controller/core/aaa/local-user"
            result = main.rest.get(url)
            showUsers = []
            for i in range (0, len(result["content"])):
                showUsers.append(result["content"][i]['user-name'])
            sleep(5)
            for user in usersString:
                if user not in showUsers:
                    numWarn += 1
                    helpers.warn("User: %s not present in the show users" % user)
            if (numWarn > 0):
                return False
            else:
                return True

    def rest_delete_user(self, numUsers=1):
        numWarn = 0
        t = test.Test()
        main = t.controller("main")
        usersString = []
        numErrors = 0
        for i in range (0, int(numUsers)):
            url = "/api/v1/data/controller/core/aaa/local-user[user-name=\""
            user = "user" + str(i+1)
            usersString.append(user)
            url = url + user + "\"]"
            main.rest.delete(url, {})
            sleep(1)
            
            if not main.rest.status_code_ok():
                helpers.test_failure(main.rest.error())
                numErrors += 1
            else:
                helpers.log("Successfully deleted user: %s " % user)

        if(numErrors > 0):
            return False
        else:
            url = "/api/v1/data/controller/core/aaa/local-user"
            result = main.rest.get(url)
            showUsers = []
            for i in range (0, len(result["content"])):
                showUsers.append(result["content"][i]['user-name'])
            sleep(5)
            for user in usersString:
                if user in showUsers:
                    numWarn += 1
                    helpers.warn("User: %s present in the show users" % user)
            if (numWarn > 0):
                return False
            else:
                return True

    
    def auto_configure_tenants(self, numTenants, numVnsPerTenant, vnsIntIPList,  *args):
        
        ''' Add tenant & vns  to the running-config. 
            Usage: 
                * Variables
                @{vnsIntIPDict}  v1  10.10.10.100  v2  20.20.20.100  v3  30.30.30.100
                @{v1MemberPGList}   v1  PG   p1  10  p3  10  
                @{v1MemberIntList}  v1  INT  leaf0-a  ethernet33  -1  leaf1-a  ethernet33  -1
                @{v2MemberPGList}   v2  PG   p2  20  p4  20
                @{v2MemberIntList}  v2  INT  leaf0-a  ethernet34  -1  leaf1-a  ethernet34  -1
                
                Test T5Setup
                    [Tags]  Setup
                    auto configure tenants     1  2  ${vnsIntIPDict}  ${v1MemberPGList}  ${v1MemberIntList}  ${v2MemberPGList}  ${v2MemberIntList}
        '''
        
        
        helpers.log("vnsIntIPList is: %s" % vnsIntIPList)
        vnsIPDict = {}
        
        try:
            vnsIPDict = dict(vnsIntIPList[i:i+2] for i in range(0, len(vnsIntIPList), 2))
        except:
            helpers.test_failure("Error during converting vnsIntIPList to a Dictionary. Check the input parameters for vnsIntIPList")
            return False
        
        vnsMemberPGDict = {}
        vnsMemberIntDict = {}
        
        try:
            
            for arg in args:
                #helpers.log("arg is: %s" % arg)
                currentVNS = arg[0]
                helpers.log("CurrentVNS is : %s" % currentVNS)
                
                if (arg[1] == "PG"):
                    vnsMemberPGDict[currentVNS] = arg[2:]
                    helpers.log("Adding %s PG Dict: %s" % (currentVNS,vnsMemberPGDict[currentVNS]))
                elif (arg[1] == "INT"):
                    vnsMemberIntDict[currentVNS] = arg[2:]
                    helpers.log("Adding %s Int Dict: %s" % (currentVNS,vnsMemberIntDict[currentVNS]))
                    
            i=0        
            while(i< int(numTenants) * int(numVnsPerTenant)):
                    i += 1
                    vnsName = 'v'+ str(i)
                    #helpers.log("VNS Name is: %s / PG List is: %s" % (vnsName, vnsMemberPGDict[vnsName]))
                    #helpers.log("VNS Name is: %s / Int list is: %s" % (vnsName, vnsMemberIntDict[vnsName]))
            
            
        except:
            helpers.test_failure("Error during converting vns member Lists. Check the input parameters for vnsMemberPGList & vnsMemberIntList")
            return False
        
        
        autoTenantList = []
        autoVNSList = []
        i=0
        while (i< int(numTenants)):
            i += 1
            autoTenantList.append('autoT'+ str(i))
        
        helpers.log("Tenant List is: %s" % autoTenantList)
        
        Fabric = T5.T5()
        FabricL3 = T5L3.T5L3()
        
        # ==> Add System Router
        Fabric.rest_add_tenant("system")
        
        i = 0
        for tenant in autoTenantList:
            # ==> Add a Tenant
            Fabric.rest_add_tenant(tenant)
            
            j = 0
            while (j < int(numVnsPerTenant)):
                i += 1
                j += 1
                vnsName = 'v' + str(i)
                autoVNSList.append(vnsName)
                # ==> Add VNS with vnsName
                Fabric.rest_add_vns(tenant, vnsName)
                try:
                    k = 0 
                    helpers.log("VNSName is: %s" % vnsName)
                    while (k < len(vnsMemberPGDict[vnsName])):
                        currentPG = vnsMemberPGDict[vnsName][k]
                        currentVLAN = vnsMemberPGDict[vnsName][k+1]
                        k += 2
                        #helpers.log("currentPG is: %s" % currentPG)
                        #helpers.log("currentVLAN is: %s" % currentVLAN)
                        
                        # ==> Add member port-group (currentPG, curentVLAN, vnsName)
                        Fabric.rest_add_portgroup_to_vns(tenant, vnsName, currentPG, currentVLAN)
                        
                except(KeyError):
                    pass
                
                try:
                    k = 0 
                    while (k < len(vnsMemberIntDict[vnsName])):
                        currentSwitch = vnsMemberIntDict[vnsName][k]
                        currentInt = vnsMemberIntDict[vnsName][k+1]
                        currentVLAN = vnsMemberIntDict[vnsName][k+2]
                        k += 3
                        #helpers.log("currentSwitch is: %s" % currentSwitch)
                        #helpers.log("currentInt is: %s" % currentInt)
                        #helpers.log("currentVLAN is: %s" % currentVLAN)
                        
                        # ==> Add member interface to vns
                        Fabric.rest_add_interface_to_vns(tenant, vnsName, currentSwitch, currentInt, currentVLAN)
                
                        
                except(KeyError):
                    pass
                
                # ==> Add the router interface IPs
                FabricL3.rest_add_router_intf(tenant, vnsName)
                FabricL3.rest_add_vns_ip(tenant, vnsName, vnsIPDict[vnsName], '24' )
                
                # ==> Add system interface to tenant
                FabricL3.rest_add_system_intf_to_tenant_routers(tenant)        
                    
            # ==> Add tenant router interface to system
            FabricL3.rest_add_tenant_routers_intf_to_system(tenant)  
            
            # ==> Add static routes pointing to system
            FabricL3.rest_add_static_routes(tenant, '0.0.0.0/0', "{\"tenant-name\": \"system\"}")
            
        return True
    

    def auto_configure_fabric_switch(self, spineList, leafList, leafPerRack):
        ''' Add leaf & spine switches to the running-config. 
            Usage: 
                * Variables
                @{spineList}  00:00:00:00:00:01:00:01  00:00:00:00:00:01:00:02
                @{leafList}  00:00:00:00:00:02:00:01  00:00:00:00:00:02:00:02  00:00:00:00:00:02:00:03  00:00:00:00:00:02:00:04
                
                Test T5Setup
                    [Tags]  Setup
                    auto configure fabric switch  ${spineList}  ${leafList}  2
        '''
        
        global leafSwitchList
        
        Fabric = T5.T5()
        for i,dpid in enumerate(spineList):
            spineName = "spine"+ str(i)
            Fabric.rest_add_switch(spineName)
            Fabric.rest_add_dpid(spineName, dpid)
            Fabric.rest_add_fabric_role(spineName, 'spine')

        if (int(leafPerRack) == 1):
            for i,dpid in enumerate(leafList):
                leafName = "leaf"+str(i)+'-a'
                leafSwitchList.append(leafName)
                rackName = "rack"+str(i)
                Fabric.rest_add_switch(leafName)
                Fabric.rest_add_dpid(leafName, dpid)
                Fabric.rest_add_fabric_role(leafName, 'leaf')
        else:

            if (int(leafPerRack) == 2):
                if (len(leafList) % 2 == 0):
                    numRacks = len(leafList) / 2
                    for i in range(0,numRacks):
                        leafName = "leaf"+str(i)+'-a'
                        leafSwitchList.append(leafName)
                        rackName = "rack"+str(i)
                        dpid = leafList[i*2]
                        Fabric.rest_add_switch(leafName)
                        Fabric.rest_add_dpid(leafName, dpid)
                        Fabric.rest_add_fabric_role(leafName, 'leaf')
                        Fabric.rest_add_leaf_group(leafName, rackName)
                        leafName = "leaf"+str(i)+'-b'
                        leafSwitchList.append(leafName)
                        rackName = "rack"+str(i)
                        dpid = leafList[i*2 + 1]
                        Fabric.rest_add_switch(leafName)
                        Fabric.rest_add_dpid(leafName, dpid)
                        Fabric.rest_add_fabric_role(leafName, 'leaf')
                        Fabric.rest_add_leaf_group(leafName, rackName)
                else:
                    numRacks = (len(leafList) / 2) + 1
                    for i in range(0,numRacks):
                        leafName = "leaf"+str(i)+'-a'
                        leafSwitchList.append(leafName)
                        rackName = "rack"+str(i)
                        dpid = leafList[i*2]
                        try:
                            testdpid = leafList[i*2 + 1]
                            Fabric.rest_add_switch(leafName)
                            Fabric.rest_add_dpid(leafName, dpid)
                            Fabric.rest_add_fabric_role(leafName, 'leaf')
                            Fabric.rest_add_leaf_group(leafName, rackName)
                            
                            leafName = "leaf"+str(i)+'-b'
                            leafSwitchList.append(leafName)
                            rackName = "rack"+str(i)
                            dpid = leafList[i*2 + 1]
                            Fabric.rest_add_switch(leafName)
                            Fabric.rest_add_dpid(leafName, dpid)
                            Fabric.rest_add_fabric_role(leafName, 'leaf')
                            Fabric.rest_add_leaf_group(leafName, rackName)
                            
                        except:
                            Fabric.rest_add_switch(leafName)
                            Fabric.rest_add_dpid(leafName, dpid)
                            Fabric.rest_add_fabric_role(leafName, 'leaf')
                            Fabric.rest_add_leaf_group(leafName, rackName)
    

     
    def auto_delete_fabric_switch(self, spineList, leafList, leafPerRack):
        ''' Delete all the switches in the running-config. Use as running config cleanup function. (teardown)
            Usage: 
                * Variables
                @{spineList}  00:00:00:00:00:01:00:01  00:00:00:00:00:01:00:02
                @{leafList}  00:00:00:00:00:02:00:01  00:00:00:00:00:02:00:02  00:00:00:00:00:02:00:03  00:00:00:00:00:02:00:04
                
                Test T5TearDown
                    [Tags]  Teardown
                    auto delete fabric switch  ${spineList}  ${leafList}  2
        '''
        
        numSpines = len(spineList)
        numLeaves = len(leafList)
        
        Fabric = T5.T5()
        for i in range(0,numSpines):
            spineName = 'spine' + str(i)
            Fabric.rest_delete_fabric_switch(spineName) 
            
        if (int(leafPerRack) == 1):
            for i in range(0, int(numLeaves)):
                leafName = "leaf"+str(i)+'-a'
                Fabric.rest_delete_fabric_switch(leafName)
                     
        else:
            if (int(leafPerRack) == 2):
                if (numLeaves % 2 == 0):
                    numRacks = numLeaves / 2
                    for i in range(0,numRacks):
                        leafName = "leaf"+str(i)+'-a'
                        Fabric.rest_delete_fabric_switch(leafName)
                        leafName = "leaf"+str(i)+'-b'
                        Fabric.rest_delete_fabric_switch(leafName)
                else:
                    numRacks = (numLeaves / 2) + 1
                    for i in range(0,numRacks):
                        leafName = "leaf"+str(i)+'-a'
                        Fabric.rest_delete_fabric_switch(leafName)
                        try:
                            leafName = "leaf"+str(i)+'-b'
                            Fabric.rest_delete_fabric_switch(leafName)
                        except:
                            pass
                             
    
    def auto_delete_fabric_portgroups(self):
        ''' Delete all the port groups in the running-config. Use as running config cleanup function. (teardown)
        '''
        
        url = "/api/v1/data/controller/applications/bvs/port-group?config=true"
        t = test.Test()
        main = t.controller("main")
        
        result = main.rest.get(url)['content']

        for pg in result:
            url = '/api/v1/data/controller/applications/bvs/port-group[name="%s"]' %  pg['name']
            main.rest.delete(url, {})

             
                             
    def platform_ping(self, src, dst ):
        '''
            Extended mininet_ping function to handle ping failures gracefully for platform HA test cases
            Retry ping 5 times and report failures / Issue Bug reports / Sleeps accordingly
        '''
        global mininetPingFails
        mynet = mininet.Mininet()     
        loss = mynet.mininet_ping(src, dst)
        if (loss != '0'):
            #sleep(5)
            loss = mynet.mininet_ping(src, dst)
            if (loss != '0'):
                if(mininetPingFails == 5):
                    helpers.warn("5 Consecutive Ping Failures: Issuing Mininet-BugReport")
                    #mynet.mininet_bugreport()
                    return False
                helpers.warn("Ping failed between: %s & %s" % (src,dst))
                mininetPingFails += 1
                return True
            else:
                mininetPingFails = 0
                return True
        else:
            mininetPingFails = 0
        return True
    
    def platform_bash_ping(self, src, dst):
        '''
            Extended bash_ping function to handle ping failures gracefully for platform HA test cases
            Retry ping 5 times and report failures / Issue Bug reports / Sleeps accordingly
        '''
        global hostPingFails
        myhost = Host.Host()
        loss = myhost.bash_ping(src, dst)
        if (loss == '100'):
            sleep(30)
            loss = myhost.bash_ping(src, dst)
            if (loss == '100'):
                if(hostPingFails == 5):
                    helpers.warn("5 Consecutive Ping Failures: Please collect logs from the physical host")
                    #mynet.mininet_bugreport()
                    return False
                helpers.warn("Ping failed between: %s & %s" % (src,dst))
                hostPingFails += 1
                return True
            else:
                hostPingFails = 0
                return True
        else:
            hostPingFails = 0
        return True
        
    
    
    def do_show_run_vns_verify(self, vnsName, numMembers):
        t = test.Test()
        main = t.controller("main")
        url = "/api/v1/data/controller/applications/bvs/tenant?config=true"
        result = main.rest.get(url)
        helpers.log("Show run output is: %s " % result["content"][0]['vns'][0]['port-group-membership-rules'])
        vnsList = result["content"][0]['vns'][0]['port-group-membership-rules']
        if (len(vnsList) != int(numMembers)):
            helpers.warn("Show run output is not correct for VNS members. Collecting support logs from the mininet")
            mynet = mininet.Mininet()  
            out = mynet.mininet_bugreport()
            helpers.log("Bug Report Location is: %s " %  out)
            for i in range(0, 2):
                helpers.warn("Show run output is not correct for VNS members. Please collect switch support logs")
                sleep(30)
        else:
            helpers.log("Show run output is correct for VNS members")




    def getNodeID(self, subordinateNode=True):
        
        '''         
        Description:
        -    This function will handout the NodeID's for main & subordinate nodes 
        
        Objective:
        -    This is designed to be resilient to node failures in HA environments. Eg: If the node is not
            reachable or it's powered down this function will handle the logic
            
        Inputs:
        |    boolean: subordinateNode  |  Whether secondary node is available in the system. Default is True
        
        Outputs:
        |    If subordinateNode: return (mainID, subordinateID)
        |    else:    return (mainID)

        
        ''' 
        numTries = 0
        t = test.Test()
        main = t.controller("main")
    
         
        while(True):
            try:
                showUrl = '/api/v1/data/controller/cluster'
                helpers.log("Main is : %s " % main.name)
                result = main.rest.get(showUrl)['content']
                mainID = result[0]['status']['local-node-id']
                break 
            except(KeyError):
                if(numTries < 5):
                    helpers.log("Warning: KeyError detected during main ID retrieval. Sleeping for 10 seconds")
                    sleep(10)
                    numTries += 1
                else:
                    helpers.log("Error: KeyError detected during main ID retrieval")
                    if subordinateNode:
                        return (-1, -1)
                    else:
                        return -1

        if(subordinateNode):
            subordinate = t.controller("subordinate")
            while(True):
                try:
                    showUrl = '/api/v1/data/controller/cluster'
                    result = subordinate.rest.get(showUrl)['content']
                    subordinateID = result[0]['status']['local-node-id']
                    break 
                except(KeyError):
                    if(numTries < 5):
                        helpers.log("Warning: KeyError detected during subordinate ID retrieval. Sleeping for 10 seconds")
                        sleep(10)
                        numTries += 1
                    else:
                        helpers.log("Error: KeyError detected during subordinate ID retrieval")
                        return (-1,-1)


        if(subordinateNode):
            return (mainID, subordinateID)
        else:
            return mainID
        
        
        
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
 
        
        
    def cli_configure_virtual_ip(self, vip):
        ''' Function to show Virtual IP of a controller via CLI
        Input: None
        Output: VIP address if configured, None otherwise
        '''
        t = test.Test()
        c = t.controller('main')

        helpers.test_log("Input arguments: virtual IP = %s" % vip)
        try:
            c.config("controller")
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
        c = None
        try:
            if 'main' in vip:
                c = t.controller('main')
            else:
                helpers.log("Spawning VIP %s" % vip)
                c = t.node_spawn(ip=vip)
                helpers.log("Successfully spawned VIP %s" % vip)

            content = c.cli('show local node interfaces ethernet0')['content']
            output = helpers.strip_cli_output(content)
            lines = helpers.str_to_list(output)
            assert "IP Address" in lines[0]
            rows = lines[2].split(' ')
        except:
            helpers.test_failure("Exception info: %s" % helpers.exception_info())
            if c:
                helpers.test_log(c.rest.error())
            return ''
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
            content = c.cli('show controller virtual-ip')['content']
            output = helpers.strip_cli_output(content)
            lines = helpers.str_to_list(output)
            assert(len(lines) == 3)
            assert "ipv4 address" in lines[0]
        except:
            helpers.test_log(c.cli_content())
            return None
        else:
            return lines[2].strip()


    def bash_verify_virtual_ip(self, vip, node='main'):
        ''' Function to show Virtual IP of a controller via CLI/Bash
        Input: None
        Output: VIP address if configured, None otherwise
        '''
        t = test.Test()
        c = t.controller(node)
        try:
            content = c.bash('ip addr')['content']
            output = helpers.strip_cli_output(content)
            if vip not in output:
                helpers.test_log("VIP: %s not configured on %s" % (vip, node))
                return False
        except:
            helpers.test_log(c.cli_content())
            return False
        else:
            helpers.log("VIP: %s is configired on %s" % (vip, node))
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
            c.config("controller")
            c.config("no virtual-ip")
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
        c = None
        try:
            if 'main' in vip:
                c = t.controller('main')
            else:
                helpers.log("Spawning VIP %s" % vip)
                c = t.node_spawn(ip=vip)
                helpers.log("Successfully spawned VIP %s" % vip)

            helpers.log("Getting MAC address of the controller")
            url = '/api/v1/data/controller/os/action/network-interface'
            c.rest.get(url)
            content = c.rest.content()
        except:
            helpers.test_failure("Exception info: %s" % helpers.exception_info())
            if c:
                helpers.test_log(c.rest.error())
            return ''
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
        
        
    def rest_add_monitor_session(self, sessionID, srcSwitch, srcInt, dstSwitch, dstInt, **kwargs):
        '''
            Add a monitor session (SPAN) to the switch
            Inputs: sessionID - Session ID for the monitor session
                    srcSwitch/Int - Source switch & interface
                    dstSwitch/Int - Destination switch & interface
            Returns:
                True - If the configuration went through without any errors
                False - If the configuration action fails
        '''

        t = test.Test()
        main = t.controller("main")
        
        url = '/api/v1/data/controller/applications/bvs/monitor-session[id=%s]' % (sessionID)
        
        main.rest.put(url, {"id": sessionID})
        
        matchSpec = {}
        if ("src-mac" in kwargs):
            matchSpec["src-mac"] = kwargs.get('src-mac')
        if("src-ip-cidr" in kwargs):
            matchSpec['src-ip-cidr'] =  kwargs.get('src-ip-cidr')
        if("src-tp-port" in kwargs):
            matchSpec["src-tp-port"] = kwargs.get('src-tp-port')
        if("dst-mac" in kwargs):
            matchSpec["dst-mac"] = kwargs.get('dst-mac')
        if("dst-ip-cidr" in kwargs):
            matchSpec['dst-ip-cidr'] = kwargs.get('dst-ip-cidr')
        if("dst-tp-port" in kwargs):
            matchSpec["dst-tp-port"] = kwargs.get('dst-tp-port')
        if("ip-dscp" in kwargs):
            matchSpec["ip-dscp"] = kwargs.get('ip-dscp')
        if("ip-ecn" in kwargs):
            matchSpec["ip-ecn"] = kwargs.get('ip-ecn')
        if("ip-proto" in kwargs):
            matchSpec["ip-proto"] = kwargs.get('ip-proto')
        if("ether-type" in kwargs):
            matchSpec["ether-type"] = kwargs.get('ether-type')
        
        helpers.log("matchSpec is: %s" % matchSpec)
        
        url = '/api/v1/data/controller/applications/bvs/monitor-session[id=%s]/source[switch-name="%s"][interface-name="%s"]' % (sessionID, srcSwitch, srcInt)

        if (matchSpec):
            result = main.rest.put(url, {"match-specification": matchSpec, "direction": "ingress", "switch-name": "leaf0-a", "interface-name": "ethernet15"})
        else:
            result = main.rest.put(url, {"direction": kwargs.get("direction"), "switch-name": srcSwitch , "interface-name": srcInt})
            
        
        url = '/api/v1/data/controller/applications/bvs/monitor-session[id=%s]/destination[switch-name="%s"][interface-name="%s"]' % (sessionID, dstSwitch, dstInt)
        result = main.rest.put(url, {"switch-name": srcSwitch , "interface-name": dstInt})

        
        if main.rest.status_code_ok():
            return True
        else:
            return False

    
    def rest_activate_monitor_session(self, sessionID):
        
        t = test.Test()
        main = t.controller("main")
        url = '/api/v1/data/controller/applications/bvs/monitor-session[id=%s]' % (sessionID)
        
        main.rest.patch(url, {"active": 'true'})
        
        if main.rest.status_code_ok():
                return True
        else:
                return False
            
    
    def rest_deactivate_monitor_session(self, sessionID):
        t = test.Test()
        main = t.controller("main")
        
        url = '/api/v1/data/controller/applications/bvs/monitor-session[id=%s]/active' % (sessionID)
        
        main.rest.delete(url)
        
        if main.rest.status_code_ok():
                return True
        else:
                return False
            
    
    def rest_delete_monitor_session(self, sessionID):
        
        t = test.Test()
        main = t.controller("main") 
        url = '/api/v1/data/controller/applications/bvs/monitor-session[id=%s]' % (sessionID)
        
        main.rest.delete(url, {"id": sessionID})
        
        if main.rest.status_code_ok():
            return True
        else:
            return False
        
        
    def rest_verify_monitor_session(self, sessionID, srcSwitch, srcInt, dstSwitch, dstInt, **kwargs):
        '''
            Verify a monitor session (SPAN) in the switch. This uses "show run monitor-session" command
            for the verification 
            Inputs: sessionID - Session ID for the monitor session
                    srcSwitch/Int - Source switch & interface
                    dstSwitch/Int - Destination switch & interface
            Returns:
                True - If the session exits
                False - If the session doesn't exists
        '''
        
        t = test.Test()
        main = t.controller("main")
        
        foundSession = False
        url = "/api/v1/data/controller/applications/bvs/monitor-session?config=true"
        result = main.rest.get(url)['content']
        
        try:
            for session in result:
                if (str(session['id']) == sessionID):
                    foundSession = True
                    if(session['source'][0]['switch-name'] != srcSwitch):
                        helpers.log("Wrong source switch in the monitor session %s : %s" % (sessionID, srcSwitch))
                        return False
                    if(session['source'][0]['interface-name'] != srcInt):
                        helpers.log("Wrong source interface in the monitor session %s : %s" % (sessionID, srcInt))
                        return False
                    if(session['source'][0]['direction'] != kwargs.get('direction')):
                        helpers.log("Wrong source interface direction in the monitor session %s : %s: %s" % (sessionID, srcInt, kwargs.get('direction')))
                        return False
                    if(session['destination'][0]['switch-name'] != dstSwitch):
                        helpers.log("Wrong destination switch in the monitor session %s : %s" % (sessionID, dstSwitch))
                        return False
                    if(session['destination'][0]['interface-name'] != dstInt):
                        helpers.log("Wrong destination interface in the monitor session %s : %s" % (sessionID, dstInt))
                        return False
                    if ('src-mac') in kwargs:
                        if((session['source'][0]['match-specification'])['src-mac'] != kwargs.get('src-mac')):
                            helpers.log("Wrong src-mac in the monitor session %s : %s: %s" % (sessionID, srcInt, kwargs.get('src-mac')))
                            return False
                    if ('src-ip-cidr') in kwargs:
                        if((session['source'][0]['match-specification'])['src-ip-cidr'] != kwargs.get('src-ip-cidr')):
                            helpers.log("Wrong src-ip-cidr in the monitor session %s : %s: %s" % (sessionID, srcInt, kwargs.get('src-ip-cidr')))
                            return False
                    if ('src-tp-port') in kwargs:
                        if(str((session['source'][0]['match-specification'])['src-tp-port']) != kwargs.get('src-tp-port')):
                            helpers.log("Wrong src-tp-port in the monitor session %s : %s: %s" % (sessionID, srcInt, kwargs.get('src-tp-port')))
                            return False
                    if ('dst-mac') in kwargs:
                        if((session['source'][0]['match-specification'])['dst-mac'] != kwargs.get('dst-mac')):
                            helpers.log("Wrong dst-mac in the monitor session %s : %s: %s" % (sessionID, srcInt, kwargs.get('dst-mac')))
                            return False
                    if ('dst-ip-cidr') in kwargs:
                        if((session['source'][0]['match-specification'])['dst-ip-cidr'] != kwargs.get('dst-ip-cidr')):
                            helpers.log("Wrong dst-ip-cidr in the monitor session %s : %s: %s" % (sessionID, srcInt, kwargs.get('dst-ip-cidr')))
                            return False
                    if ('dst-tp-port') in kwargs:
                        if(str((session['source'][0]['match-specification'])['dst-tp-port']) != kwargs.get('dst-tp-port')):
                            helpers.log("Wrong dst-tp-port in the monitor session %s : %s: %s" % (sessionID, srcInt, kwargs.get('dst-tp-port')))
                            return False
                    if ('ip-dscp') in kwargs:
                        if((session['source'][0]['match-specification'])['ip-dscp'] != kwargs.get('ip-dscp')):
                            helpers.log("Wrong ip-dscp in the monitor session %s : %s: %s" % (sessionID, srcInt, kwargs.get('ip-dscp')))
                            return False
                    if ('ip-ecn') in kwargs:
                        if((session['source'][0]['match-specification'])['ip-ecn'] != kwargs.get('ip-ecn')):
                            helpers.log("Wrong ip-ecn in the monitor session %s : %s: %s" % (sessionID, srcInt, kwargs.get('ip-ecn')))
                            return False
                    if ('ip-proto') in kwargs:
                        if((session['source'][0]['match-specification'])['ip-proto'] != kwargs.get('ip-proto')):
                            helpers.log("Wrong ip-proto in the monitor session %s : %s: %s" % (sessionID, srcInt, kwargs.get('ip-proto')))
                            return False
                    if ('ether-type') in kwargs:
                        if((session['source'][0]['match-specification'])['ether-type'] != kwargs.get('ether-type')):
                            helpers.log("Wrong ether-type in the monitor session %s : %s: %s" % (sessionID, srcInt, kwargs.get('ether-type')))
                            return False      
                    pass
                    
        except(KeyError):
            helpers.warn("KeyError detected: One of the fields are missing from the monitor session")
            helpers.log(session)
            return False

        if(foundSession):
            return True
        else:
            helpers.log("Monitor session is not found in the running config")
            return False



    def verify_ping_with_tcpdump(self, host, ipAddr, verifyHost, verifyInt, *args):
        
        ''' This function will issue a ping request and verify it through the TCP dump.
        
        Input:  host -> hostname from the topo file
                ipAddr -> Destination IP address of that ping request should go
                verifyHost -> Host where tcpdump is being executed
                verifyInt -> interfaces of the host that tcpdump would get excuted
                verifyString -> String to search in the tcpdump output
        '''
        
        t = test.Test()
        n = t.node(verifyHost)
        
        verifyString = ""
        for arg in args:
            verifyString += '.*' + arg
        verifyString += '.*'
        # Issue a tcpdump & make sure there's no traffic already matching "verifyString" is receiving
        output = n.bash("timeout 5 tcpdump -i %s" % verifyInt )
        match = re.search(r"%s" % verifyString, output['content'], re.S | re.I)
        
        if match:
            helpers.log("verifyString is: %s" % verifyString)
            helpers.log("Found it on the tcpdump output before issueing a ping: %s" % output['content'])
            return False
        
        else:
            # Schedule a different thread to execute the ping. Ping will be executed for 10 packets
            pingThread = T5PlatformThreads(1, "hostPing",  host=host, IP=ipAddr)
            helpers.log("Starting ping thread to ping from %s to destIP: %s" % (host, ipAddr))
            pingThread.start()
            
    
            output = n.bash("timeout 5 tcpdump -i %s" % verifyInt )
            verifyStringFound = re.search(r"%s" % verifyString, output['content'], re.S | re.I)
            
            pingThread.join()
            
            if verifyStringFound:
                return True
            else:
                helpers.log("TCPDump match not found for string: %s" % verifyString)
                return False
            
            
    def verify_traffic_with_tcpdump(self, verifyHost, verifyInt, verifyOptions, *args):
        
        ''' This function will verify the traffic through TCP dump.
        
        Input:  
                verifyHost -> Host where tcpdump is being executed
                verifyInt -> interfaces of the host that tcpdump would get excuted
                verifyOptions -> Other TCP Dump options (eg: src port 8000 and tcp)
                verifyString -> String to search in the tcpdump output
        '''
        
        t = test.Test()
        n = t.node(verifyHost)
        
        verifyString = ""
        for arg in args:
            verifyString += '.*' + arg
        verifyString += '.*'
        # Issue tcpdump & look for the intended traffic that matches verifyString
        output = n.bash("timeout 5 tcpdump -i %s %s" % (verifyInt, verifyOptions) )
        match = re.search(r"%s" % verifyString, output['content'], re.S | re.I)
        
        if match:
            return True
        
        else:
            helpers.log("TCPDump match not found for string: %s" % verifyString)
            return False


    def cli_compare(self, node, left=None, right=None,
                    scp_passwd='bsn', soft_error=False):
        """
        Generic function to compare via CLI, also using using SCP
        Input <left> and <right> arguments exactly the same way as you
        would do it in CLI's 'compare' command.

        Inputs:
        | left | Left object for comparison
        | right | Right object for comparison
        | node | Reference to switch/controller as defined in .topo file |
        | scp_passwd | Password for scp connection |
        | soft_error | Soft Error flag |

        Examples:
        | Cli Compare | subordinate | test-file | scp://bsn@regress:path-to-file/file
        | Cli Compare | main | test-file | config://test-config
        | Cli Compare | main | running-config |  test-file

        Return Value:
        - List of lines, in which <left> and <right> are different
        """
        if not right or not left:
            return helpers.test_error("You need to specify values for 'right'"
                                      " and 'left' arguments.")
        helpers.test_log("Running command:\ncompare %s %s" % (left, right))
        t = test.Test()
        c = t.controller(node)
        c.config("config")
        c.send("compare %s %s" % (left, right))
        options = c.expect([r'[Pp]assword: ', r'\(yes/no\)\?', c.get_prompt()])
        content = c.cli_content()
        helpers.log("*****Output is :\n%s" % content)
        try:
            if (('Could not resolve' in content) or ('Error' in content)
                or ('No such file or directory' in content)):
                return helpers.test_failure(content, soft_error)
            elif options[0] == 0 :
                helpers.log("need to provide passwd")
                output = c.config(scp_passwd)['content']
            elif options[0] == 1:
                helpers.log("need to send yes, then provide passwd")
                c.send('yes')
                c.expect(r'[Pp]assword:')
                output = c.config(scp_passwd)['content']
        except:
            return helpers.test_failure(c.cli_content(), soft_error)

        output = c.cli_content()
        helpers.log("Output *** %s " % output)
        if ("Error" in output) or ('No such file or directory' in output):
            return helpers.test_failure(c.cli_content(), soft_error)

        output = helpers.strip_cli_output(output)
        output = helpers.str_to_list(output)
        if options[0] < 2:
            for index, line in enumerate(output):
                if '100%' in line:
                    output = output[(index+1):]
                    break

        helpers.log("Cropped output *** %s " % output)

        differences = []
        if len(output) == 0:
            helpers.log("Files are identical")
            return differences

        for line in output:
            if re.match(r'[0-9].*|< \!|---|> \!|< \Z|> \Z|\Z', line):
                helpers.log("OK: %s" % line)
            elif (re.match(r'[<>]   hostname|[<>]     ip', line)
                  and node=='subordinate'):
                helpers.log("OK: %s" % line)
            else:
                helpers.log("files different at line:\n%s" % line)
                differences.append(line)

        if helpers.any_match(c.cli_content(), r'Error'):
            return helpers.test_failure(c.cli_content(), soft_error)

        return differences


    def cli_copy(self, src, dst, node='main', scp_passwd='bsn'):
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
        options = c.expect([r'[Pp]assword: ', r'\(yes/no\)\?', c.get_prompt()])
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
                c.expect(r'[Pp]assword:')
                c.send(scp_passwd)
            try:
                c.expect(c.get_prompt(), timeout=180)
                if not (helpers.any_match(c.cli_content(), r'100%') or helpers.any_match(c.cli_content(), r'applied \d+ updates') or helpers.any_match(c.cli_content(), r'Lines Applied')):
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
                helpers.log("Comparing '%s' and '%s'" % (line, config_file[index]))
                if 'Current Time' in line:
                    assert 'Current Time' in config_file[index]
                    continue
                if not line == config_file[index]:
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
            #Cropping headers of the outputs
            rc = rc[4:]
            config_file = config_file[8:]

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
        if re.match(r'config://.*', filename) or re.match(r'image://.*', filename) :
            helpers.test_log("Deleting config:// or image://, expecting confirmation prompt")
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

    def copy_pkg_from_jenkins(self,node='main', check=True):
        ''' 
          copy the latest upgrade package from Jenkin
          Author: Mingtao
          input:  node  - controller to copy the image, 
                          main, subordinate, c1 c2
          usage:  
              check: True, if there is a image, will not copy
          output: image build
                     
        '''
        t = test.Test()
        c = t.controller(node)
        if check is True:
            (num,image) = self.cli_check_image(node)
            helpers.log('INFO: *******system image is: %s ' % image)            
        else:
            num = -1
       
        if str(num) == '-1':
            helpers.log("INFO: system NOT have image, or ignore check,   will copy image")
            c.config('')
#            string = 'copy "scp://bsn@jenkins:/var/lib/jenkins/jobs/bvs main/lastSuccessful/archive/target/appliance/images/bvs/controller-upgrade-bvs-*-SNAPSHOT.pkg"'
            string = 'copy "scp://bsn@jenkins:/var/lib/jenkins/jobs/bvs main/lastSuccessful/archive/controller-upgrade-bvs-*-SNAPSHOT.pkg"'

            c.send(string + ' image://')
#            c.expect(r'[\r\n].+password: ') 
            c.expect(r'[\r\n].+password: |[\r\n].+(yes/no)?')
            content = c.cli_content()
            helpers.log("*****Output is :\n%s" % content)
            if re.match(r'.*password:.*', content):
                helpers.log("INFO:  need to provide passwd " )
                c.send('bsn')
            elif re.match(r'.+(yes/no)?', content):
                helpers.log("INFO:  need to send yes, then provide passwd " )
                c.send('yes')
                c.expect(r'[\r\n].+password: ')
                c.send('bsn')
            
            try:
                c.expect(timeout=300)
            except:
                helpers.log('scp failed')
                return False
            else:
                helpers.log('scp completed successfully')
                (num,image) = self.cli_check_image(node)    
                if num == -1:
                    helpers.log('there is still no image') 
                    return False                               

        else:
            helpers.log("INFO: system has image: %s, will not copy image again" % image)

        return image
    
    def copy_pkg_from_server(self,src,node='main',passwd='bsn',soft_error=False):
        ''' 
          copy the a upgrade package from server
          Author: Mingtao
          input:  node  - controller to copy the image, 
                          main, subordinate, c1 c2
          usage: 
              copy_pkg_from_server  bsn@qa-kvm-32:/home/mingtao/bigtap-3.0.0-upgrade-2014.02.27.1852.pkg 
              soft_error:  True, handle negative case
          output: image build
                     
        '''
        t = test.Test()
        c = t.controller(node)
      
        c.config('')
        string = 'copy scp://' + src
        c.send(string + ' image://')
 
        c.expect(r'[\r\n].+password: |[\r\n].+(yes/no)?')
        content = c.cli_content()
        helpers.log("*****Output is :\n%s" % content)
        if re.match(r'.*password:.* ', content):
            helpers.log("INFO:  need to provide passwd " )
            c.send(passwd)
        elif re.match(r'.+(yes/no)?', content):
            helpers.log("INFO:  need to send yes, then provide passwd " )
            c.send('yes')
            c.expect(r'[\r\n].+password: ')
            c.send(passwd)
        
        try:
            c.expect(timeout=180)                    
        except:
            helpers.log('scp failed')
            return False
        else:
            helpers.log('scp completed successfully')
            content = c.cli_content()            
            temp = helpers.strip_cli_output(content)
            temp = helpers.str_to_list(temp)
            helpers.log("*****Output list   is :\n%s" % temp)
            line = temp[-1]
            if re.match(r'Error:.*', line) and not re.match(r'.*already exists.*', line):   
                helpers.log("Error: %s" % line)    
                if soft_error:           
                    return False
                else:
                    helpers.test_failure("Error: %s" % line)   
            else:
                image = self.cli_check_image(node)

        return image
 

    def cli_check_image(self,node='main',soft_error=False):
        ''' 
          check image available in the system "show image"
          Author: Mingtao
          input:  node  - controller  
                          main, subordinate, c1 c2
          usage:  ${num}  ${image}=      cli_check_image
          output: ${num - the number of images
                ${image}   - the image build in a list
        '''
        
        t = test.Test()
        c = t.controller(node)
        helpers.log('INFO: Entering ==> check_image with soft_error: %s' %str(soft_error))        
        c.enable('')
        c.enable("show image")
        content = c.cli_content()
        helpers.log("*****Output is :\n%s" % content)
        temp = helpers.strip_cli_output(content)
        temp = helpers.str_to_list(temp)
        helpers.log("*****Output list   is :\n%s" % temp)
        if re.match(r'Error:.*', temp[0]):   
            helpers.log("Error: %s" % temp[0])            
            if soft_error:           
                return False
            else:
                helpers.test_failure("Error: %s" %temp)   
        
        if len(temp) == 1 and 'None.' in temp:
            helpers.log("INFO:  ***image is not in controller******")
            num = -1
            images =[]
          
        else:
            temp.pop(0);temp.pop(0)
            helpers.log("INFO:  ***image is available: %s" % temp)
        
            num = len(temp) 
            images =[]
            for line in temp:
                line = line.split()
                image = line[3]
                helpers.log("INFO: ***image is available: %s" % image)
                images.append(image)
            helpers.log("INFO:  ***image is available: %s" % images)
  
        return num, images


    def cli_delete_image(self,node='main',image=None):
        ''' 
          delete image  in system             
          Author: Mingtao
          input:  node  - controller  
                          main, subordinate, c1 c2
                  image - build number to be deleted
                          None - delete all the images
          usage:   
          output: ${num - the number of images
                  ${image}   - the image build in a list
        '''       
        
        t = test.Test()
        c = t.controller(node)
        helpers.log('INFO: Entering ==> cli_delete_image  '  )    
        (_,images) = self.cli_check_image(node)        
        if image is None:
            for image in images:
                c.config('')
                c.send('delete image %s' %image) 
                c.expect(r".*: " )
                c.send('yes') 
                c.expect()
            (newnum,newimages) = self.cli_check_image(node)  
            if newnum != -1:
                helpers.log('Error:  not all the images are deleted  '  )     
                return False                   
        else:
            if image in images:
                c.config('')
                c.send('delete image %s' %image) 
                c.expect(r".*: " )
                c.send('yes') 
                c.expect()                
                (_,newimages) = self.cli_check_image(node)  
                if image in newimages:
                    helpers.log('Error: images: %s is NOT  deleted' %image )     
                    return False                                       
            else:
                helpers.log("INFO: image: %s not in controller" % image)          
                
        return True


    def cli_upgrade_stage(self, node='main', image=None):
        ''' 
          upgrade stage  -  1 step of upgrade         
          Author: Mingtao
          input:  node  - controller 
                          main, subordinate, c1 c2
                  image - build number to be staged
                          None - pick the biggest build number  
          usage:   
          output: True  - upgrade staged successfully
                  False  -upgrade staged Not successfully
        '''              
        t = test.Test()
        c = t.controller(node)
        helpers.log('INFO: Entering ==> cli_upgrade_stage'   )
        
        c.config('')
        if image is None:
            (num,images) = self.cli_check_image(node)
            if num == 1:
                c.send('upgrade stage')
            else:
                image = max(images)
                c.send('upgrade stage ' + image) 
        else:
            c.send('upgrade stage ' + image)
        c.expect(r'[\r\n].*to continue.*')      
        c.send("yes")
        try:
            c.expect(timeout=900)
        except:
            helpers.log('stage did not finish within 180 second ')
            return False
        else:
            content = c.cli_content()
            helpers.log("INFO:*****Content Output is :\n%s" % content)
            temp = helpers.str_to_list(content)
            helpers.log("INFO:*****temp Output is :\n%s" % temp)
            for line in temp:
                helpers.log("line is : %s" % line)
                if re.match(r'Upgrade stage: Upgrade Staged', line):
                    helpers.log('stage completed successfully')
                    return True
        return False



    def cli_upgrade_launch(self,node='main'):
        ''' 
          upgrade launch  -  2 step of upgrade         
          Author: Mingtao
          input:  node  - controller  
                          main, subordinate, c1 c2
                  
          usage:   
          output: True  - upgrade launched successfully
                  False  -upgrade launched Not successfully
        '''              
                
        t = test.Test()
        c = t.controller(node)
        helpers.log('INFO: Entering ==> cli_upgrade_launch ')
        c.config('')
        c.send('upgrade launch')
        c.expect(r'[\r\n].+: ')
        content = c.cli_content()
        helpers.log("*****Output is :\n%s" % content)
        c.send("yes")
         
        try:
            c.expect(r'[\r\n].+Rebooting.*')
        except:
            helpers.log('ERROR: upgrade launch NOT successfully')
            return False
        else:
            helpers.log('INFO: upgrade launch  successfully')
            return True
        return False
    
    
    
    def cli_take_snapshot(self,node='main', run_config=None, local_node=None, fabric_switch=None,filepath=None):
        ''' 
          take snapshot of the system, can only take snapshot one by one  
          Author: Mingtao
          input:  node  - controller  
                          main, subordinate, c1 c2
                  run_config   - runnning config
                  fabric_switch  -  show fabric switch
                  filepath -  file infos in the filepath
          usage:   
          output: "show running-config" or "show fabric_switch" or "ls "
                   
        '''              
        t = test.Test()
        c = t.controller(node)
        helpers.log('INFO: Entering ==> cli_take_sanpshot')
        host = Host.Host()    
        
        if run_config: 
            c.enable('show running-config')     
            content = c.cli_content()       
            helpers.log("********content in string:************\n%s" % content)       
            temp = helpers.strip_cli_output(content)
            temp = helpers.str_to_list(temp)
            helpers.log("********content is list************\n%s" % helpers.prettify(temp))
            config = temp[6:]
            content = '\n'.join(config)
            helpers.log("********config :************\n%s" % content)  
            new_content = re.sub(r'\s+hashed-password.*$','\n  remove-passwd',content,flags=re.M)  
            if local_node is None:
                new_content = re.sub(r'local node.*! user','\n  remove-local-node',new_content,flags=re.DOTALL)               
            helpers.log("********config after remove passwd :************\n%s" % new_content)                          
            return  new_content
        if fabric_switch: 
            c.enable('show fabric switch')     
            content = c.cli_content()       
            helpers.log("********content in string:************\n%s" % content)       
            temp = helpers.strip_cli_output(content)
            helpers.log("********string :************\n%s" % temp)                   
            return  temp
        if filepath:
            fileinfo = host.bash_ls(node, filepath)
            helpers.log("********file info is************\n%s" % fileinfo)    
            return fileinfo         
        return False    

 

    def rest_get_node_role(self,node='c1'):
        '''  
           return the local node role:
          Author: Mingtao
          input:  node  - controller  
                           c1 c2                
          usage:   
          output: active or stand-by
          fails if there is no domain-leader for the cluster
        '''
        t = test.Test()
        c = t.controller(node)
        helpers.log('INFO: Entering ==> rest_get_node_role ')
 
        
        url = '/api/v1/data/controller/cluster'  
        c.rest.get(url)
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())

        if(c.rest.content()):
            local_id = c.rest.content()[0]['status']['local-node-id']
            helpers.log("INFO: local node ID: %s" %  local_id)
            if c.rest.content()[0]['status']['domain-leader']:
                leader_id = c.rest.content()[0]['status']['domain-leader']['leader-id']
                helpers.log("INFO: domain-leader: %s" % c.rest.content()[0]['status']['domain-leader']['leader-id'])
                if local_id == leader_id:
                    return 'active'
                else:
                    return 'stand-by'
                
            else:
                helpers.log("ERROR: there is no domain-leader" ) 
                helpers.test_failure('ERROR: There is no domain-leader')
        return False     


    def cli_get_node_role(self,node='c1'):
        '''  
           return the local node role:
          Author: Mingtao
          input:  node  - controller  
                           c1 c2                
          usage:   
          output: active or stand-by
          fails if there is no domain-leader for the cluster
        ''' 
        t = test.Test()
        c = t.controller(node)
        helpers.log('INFO: Entering ==> cli_get_node_role ')       
        c.cli('show cluster' )
        content = c.cli_content()
        temp = helpers.strip_cli_output(content)
        temp = helpers.str_to_list(temp)
        for line in temp:          
            helpers.log("INFO: line is - %s" % line)
            match= re.match(r'.*(active|stand-by).* Current', line)
            if match:
                helpers.log("INFO: role is: %s" % match.group(1))                          
                return  match.group(1)
            else:
                helpers.log("INFO: not current node  %s" % line)   
        return False     



    def rest_get_ver(self,node='c1'):
        '''  
          return the local node version 
          Author: Mingtao
          input:  node  - controller  
                           c1 c2                
          usage:   
          output:  build 
          
        '''
        t = test.Test()
        c = t.controller(node)
        helpers.log('INFO: Entering ==> rest_get_node_role ')
         
        url = '/api/v1/data/controller/core/version/appliance'  
        c.rest.get(url)
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())

        if(c.rest.content()):             
            return c.rest.content()[0]['build-id']
        return False     
      
 

    def rest_get_num_nodes(self):
        ''' 
          return the number of nodes in the system  
          Author: Mingtao
          input:                                        
          usage:   
          output:   1  or 2 
        '''
        t = test.Test()
        c = t.controller('main')
        helpers.log('INFO: Entering ==> rest_get_node_role ')
   
        
        url = '/api/v1/data/controller/cluster'  
        c.rest.get(url)
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())

        if(c.rest.content()):
            num = len(c.rest.content()[0]['status']['nodes'])
            helpers.log("INFO: There are %d of controller in cluster" %  num)
            for index in range(0,num):
                
                hostname = c.rest.content()[0]['status']['nodes'][index]['hostname']
                helpers.log("INFO: hostname is: %s" % hostname )
                  
            return num
        else:
            helpers.test_failure(c.rest.error())      
 

    def cli_whoami(self):
        '''  
          run cli whoami  
          Author: Mingtao
          input:                                        
          usage:   
          output:   username and group        
        '''
        t = test.Test()
        c = t.controller('main')
        helpers.log('INFO: Entering ==> cli_whoami ')
                
        c.cli('whoami' )
        content = c.cli_content()
        temp = helpers.strip_cli_output(content)
        temp = helpers.str_to_list(temp)
        helpers.log("INFO: temp is - %s" % temp) 
    
        for line in temp:
            line = line.lstrip()          
            helpers.log("INFO: line is - %s,  " % line)
            match= re.match(r'.*Id\s+:\s*(.*)', line)      
            if match:
                name=match.group(1)
                helpers.log("INFO: ID: %s" % match.group(1))        
            match= re.match(r'.*Groups\s+:\s*(.*)', line)      
            if match:
                group=match.group(1)
                helpers.log("INFO: Group: %s" % match.group(1))        
           
        return [name,group]   
    
  
    def cli_reauth(self,user='admin',passwd='adminadmin'):
        '''  
          run cli reauth, and run cli_whoami verify 
          Author: Mingtao
          input:                                        
          usage:  cli_reauth  user 
          output:   True  or False      
                       
        '''
        t = test.Test()
        c = t.controller('main')
        helpers.log('INFO: Entering ==> cli_reauth ')
        
        c.enable('end')
        c.send('reauth '+user)
        c.expect("Password: " )
        c.send(passwd) 
        c.expect()  
        userinfo = self.cli_whoami()[0]
        if user == userinfo:
            helpers.log('INFO: current session with user:  %s ' %  user)
            return True
        else:
            helpers.log('INFO: current session with user:  %s ' % user) 
            return False

    def cli_kill_ssh_sessions(self,node):
        '''
        Kill SSH sessions by running 'pkill -TERM sshd' from bash mode.

        Inputs:
        | node | reference to controller as defined in .topo file |

        Return Value:
        - True if killing sessions successful, False otherwise
        '''
        t = test.Test()
        bsn_common = bsnCommon()
        ip_addr = bsn_common.get_node_ip(node)
        c = t.node_spawn(ip=ip_addr)
        helpers.log('INFO: Entering bash mode to kill all sshd processes')
        c.cli("debug bash")
        try:
            c.send("sudo pkill -TERM sshd")
            helpers.log("Kill command sent")
            return True
        except:
            helpers.test_failure('ERROR: failure killing ssh sessions')
            return False
 

    def bash_top(self, node):
        """
        Execute 'top - n 1' on a device.
        Author:    Mingtao
        Inputs:
        | node | reference to switch/controller/host as defined in .topo file |
        
        Example:    bash_top   c1
       
        Return Value:
        - Dictionary
            {'Swap': {'cached': '904268k',
              'free': '1943548k',
              'total': '1943548k',
              'used': '0k'},
                 'cpu': {'hi': '0.0',
                         'id': '97.8',
                         'ni': '0.0',
                         'si': '0.0',
                         'st': '0.1',
                         'sy': '0.4',
                         'us': '0.7',
                         'wa': '0.9'},
                 'init': {'cpu': '0',
                          'mem': '0.1',
                          'pid': '1',
                          'res': '2180',
                          'shr': '1268',
                          'virt': '24340'},
                 'java': {'cpu': '4',
                          'mem': '15.0',
                          'pid': '683',
                          'res': '299m',
                          'shr': '9844',
                          'virt': '3036m'},
                 'load': '0.00, 0.01, 0.05',
                 'mem': {'buffers': '106336k',
                         'free': '499892k',
                         'total': '2051616k',
                         'used': '1551724k'}
         }           
        """
        t = test.Test()
        n = t.node(node)
        content = n.bash('top -n 1')['content']
        lines = helpers.strip_cli_output(content, to_list=True)
        helpers.log("lines: %s" %  lines )
        topinfo = {}      
        linenum = 0
        for line in lines:
            line = line.lstrip()
            helpers.log(" line is - %s" % line)    
            linenum = linenum+1     
            if (re.match(r'.*load average: (.*)', line)):
                
                match = re.match(r'.*load average: (.*)', line)
                topinfo['load'] = match.group(1)
                helpers.log("INFO: *** get the load info *** topinfo is \n  %s" % topinfo)     
          
            elif (re.match(r'Cpu.* (.*)%us,.*', line)):    
                topinfo['cpu'] = {} 
                match = re.match(r'Cpu.* (.*)%us,\s+(.*)%sy,\s+(.*)%ni,\s+(.*)%id,\s+(.*)%wa,\s+(.*)%hi,\s+(.*)%si,\s+(.*)%st.*', line)
                topinfo['cpu']['us'] = match.group(1)
                topinfo['cpu']['sy'] = match.group(2)
                topinfo['cpu']['ni'] = match.group(3)   
                topinfo['cpu']['id'] = match.group(4)
                topinfo['cpu']['wa'] = match.group(5)
                topinfo['cpu']['hi'] = match.group(6)   
                topinfo['cpu']['si'] = match.group(7)
                topinfo['cpu']['st'] = match.group(8)                                               
                helpers.log("INFO: *** get the cpu info **** topinfo is \n  %s" % topinfo)     
            elif (re.match(r'Mem:.*', line)):    
                topinfo['mem'] = {} 
                match = re.match(r'Mem:.* (.*) total,\s+(.*) used,\s+(.*) free,\s+(.*) buffers.*', line)
                topinfo['mem']['total'] = match.group(1)
                topinfo['mem']['used'] = match.group(2)      
                topinfo['mem']['free'] = match.group(3)
                topinfo['mem']['buffers'] = match.group(4)      
                                                        
                helpers.log("INFO: *** get the Mem info **** topinfo is \n  %s" % topinfo)     
                            
            elif (re.match(r'Swap:\s+(.*) total,\s+(.*) used,\s+(.*) free,\s+(.*) cached.*', line)):    
                topinfo['Swap'] = {} 
                match = re.match(r'Swap:\s+(.*) total,\s+(.*) used,\s+(.*) free,\s+(.*) cached.*', line)
                topinfo['Swap']['total'] = match.group(1)
                topinfo['Swap']['used'] = match.group(2)      
                topinfo['Swap']['free'] = match.group(3)
                topinfo['Swap']['cached'] = match.group(4)      
                                                        
                helpers.log("INFO: *** get the Swap info **** topinfo is \n  %s" % topinfo)     
            elif (re.match(r'PID USER.*', line)):  
                helpers.log("INFO: *** below are stats for process ****   \n ")          
                break
            
        helpers.log("INFO: *** line number is  ****  %d   " % linenum)        
        process = lines[linenum:]
        helpers.log("INFO: *** remain lines are  ****   \n  %s" % process)   
        for line in process:
            fields = line.split()  
            helpers.log("INFO: fields   \n  %s" % fields)               
            pname= fields[11]
            if pname == 'init' or  pname == 'java':
                topinfo[pname] = {}
                topinfo[pname]['pid'] = fields[0]
                topinfo[pname]['virt'] = fields[4]
                topinfo[pname]['res'] = fields[5]  
                topinfo[pname]['shr'] = fields[6] 
                topinfo[pname]['cpu'] = fields[8] 
                topinfo[pname]['mem'] = fields[9]    
            else:
                continue
        helpers.log("INFO:  topinfo is \n  %s" % helpers.prettify(topinfo))                                          
        return topinfo 
 
    def cli_add_user(self,user='user1',passwd='adminadmin'):
        '''
          cli add user to the system, can only run at main
          Author: Mingtao
          input:   user = username,  passwd  = password                                       
          usage:   
          output:   True                            
        '''
  
        t = test.Test()
        c = t.controller('main')
        helpers.log('INFO: Entering ==> cli_add_user ')
        t = test.Test()   
        c.config('user '+user) 
        c.send('password' )
        c.expect('Password: ')        
        c.send(passwd)
        c.expect('Re-enter:')
        c.send(passwd)                
        c.expect()        
        return True     



    def cli_group_add_users(self,group=None,user=None):
        '''  
          cli add user to group, can only run at main
          Author: Mingtao
          input:   group  - if group not give, will user admin
                  user    - if user not given, will add all uers                             
          usage:   
          output:   True                            
        '''  
        t = test.Test()
        c = t.controller('main')
        helpers.log('INFO: Entering ==> cli_add_user ')    
        if group is None:
            group = 'admin'         
        c.config('group '+ group) 
        if user:
            c.config('associate user '+user)
        else: 
            c.config('show running-config user | grep user')   
            content = c.cli_content()
            temp = helpers.strip_cli_output(content)
            temp = helpers.str_to_list(temp)
            helpers.log("********new_content:************\n%s" % helpers.prettify(temp))
            temp.pop(0)
            helpers.log("********new_content:************\n%s" % helpers.prettify(temp))            
            for line in temp:
                line = line.lstrip()
                user = line.split(' ')[1]
                helpers.log('INFO: user is: %s ' % user)  
                if user == 'admin':
                    continue   
                else:                        
                    c.config('associate user '+user)
            
            return True    


    def rest_get_user_group(self,user):
        '''  
          get the group for a user, can only run at main
          Author: Mingtao
          input:   
                  user    - if user not given, will add all uers                             
          usage:   
          output:   group                          
        '''
        t = test.Test()
        c = t.controller('main')
        helpers.log('INFO: Entering ==> rest_get_user_group ')
   
        
        url = '/api/v1/data/controller/core/aaa/group[user="%s"]'  % user
        c.rest.get(url)
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())

        if(c.rest.content()):
            helpers.log('INFO: content is: %s ' %c.rest.content())        

            if user in c.rest.content()[0]['user']:    
                helpers.log('INFO: inside  ')        
                return  c.rest.content()[0]['name']          
        else:
            helpers.test_failure(c.rest.error())      


    def cli_delete_user(self,user):
        '''  
          delete users can only run at main
          Author: Mingtao
          input:  user                        
          usage:   
          output:   True                            
           
        '''
  
        t = test.Test()
        c = t.controller('main')
        helpers.log('INFO: Entering ==> cli_delete_user ')
        c.config('no user '+ user)    
        return True
  

    def T5_cli_clean_all_users(self,user=None ):
        ''' 
        delete all users except admin
          Author: Mingtao
          input:  user                        
          usage:   
          output:   True                                                
        '''
  
        t = test.Test()
        c = t.controller('main')
        helpers.log('INFO: Entering ==> cli_delete_user ')
      
        if user: 
            c.config('no user '+ user)     
            return True
        else:
            c.config('show running-config user | grep user')   
            content = c.cli_content()
            temp = helpers.strip_cli_output(content)
            temp = helpers.str_to_list(temp)
            helpers.log("********new_content:************\n%s" % helpers.prettify(temp))
            temp.pop(0)
            helpers.log("********new_content:************\n%s" % helpers.prettify(temp))            
            for line in temp:
                line = line.lstrip()
                user = line.split(' ')[1]
                helpers.log('INFO: user is: %s ' % user)  
                if user == 'admin':
                    continue   
                else:                        
                    c.config('no user '+ user)
                            
            return True    



    def first_boot_controller(self, node,
                           join_cluster = 'no',
                           dhcp='no',
                           ip_address=None,
                           netmask='18',
                           gateway='10.192.64.1',
                           dns_server='10.92.3.1',
                           dns_search='bigswitch.com',                          
                           hostname='MY-T5-C',                           
                           cluster_ip ='',
                           cluster_passwd='adminadmin',
                           cluster_name='T5cluster',
                           cluster_descr='T5cluster',
                           admin_password='adminadmin',
                           platform='bvs',
                           ntp_server='',
                        ):
        
        """
        First boot setup: connect to the console  and complete the first boot.  
        input: dhcp = no   - static ip assign
               dhcp = yes,  dhcp
               join_cluster = no  - start a new cluster 
               join_cluster = yes  - jion existing cluster

        Author: Mingtao       

        """ 
        helpers.log("Entering ====>  first_boot_controller node:'%s' " % node)
        self.first_boot_controller_initial_node_setup(node,dhcp,ip_address,netmask,gateway,dns_server,dns_search,hostname)
        self.first_boot_controller_initial_cluster_setup(node,join_cluster,cluster_ip )        
        new_ip_address = self.first_boot_controller_menu_apply(node)
        helpers.sleep(3)  # Sleep for a few seconds just in case...
        helpers.log("new_ip_address = '%s'" % new_ip_address)
        loss = helpers.ping(new_ip_address)
        if loss < 50:
            helpers.log("Node '%s' has survived first-boot!" % node)
            return new_ip_address
        else:
            helpers.test_failure('ERROR: the controller is not reachable')
            return False


    def console_boot_factory_default(self, node, timeout=360):
        """
        Runs boot factory-default from console, the can be used when controller is setup using dhcp      
        Author: Mingtao        
        """
        
        t = test.Test()
        n = t.node(node)
        helpers.log("Entering ===> console_boot_factory_default: '%s'" % node)
        helpers.log("Getting the console session for '%s'" % node)
        n_console = n.console()
        helpers.summary_log('BVS boot factory may take a bit of time. Setting timeout to %s seconds.' % timeout)
        n_console.send(helpers.ctrl('c'))
        helpers.sleep(2)
        n_console.send('')
        helpers.sleep(2)        
        n_console.send('')       
        options = n_console.expect([r'Big Virtual Switch Appliance.*[\r\n]', r'.*> '])   
        if options[0] =='0':
            n_console.expect(r'.*login: ')
            n_console.send('admin')
            n_console.expect(r'[Pp]assword: ')
            n_console.send('adminadmin')
            n_console.expect(r'[#>] ')
        
        n_console.send('enable')
        n_console.expect('#')
        n_console.send('boot factory-default')
        n_console.expect(r'proceed \("yes" or "y" to continue\)')
        n_console.send('y')
        n_console.expect(r'loading image into stage partition', timeout=timeout)
        n_console.expect(r'checking integrity of new partition', timeout=timeout)
        n_console.expect(r'New Partition Ready', timeout=timeout)
        n_console.expect(r'ready for reboot', timeout=timeout)
        n_console.expect(r'"yes" or "y" to continue\): ', timeout=timeout)
        n_console.send('y')
        
        helpers.summary_log("'%s' has been rebooted." % node)
        helpers.log("Boot factory-default completed on '%s'. System should be rebooting." % node)
        return True
  
  
    def first_boot_controller_initial_node_setup(self,
                           node,
                           dhcp = 'no',
                           ip_address=None,
                           netmask='18',
                           gateway='10.192.64.1',
                           dns_server='10.192.3.1',
                           dns_search='bigswitch.com',                          
                           hostname='MY-T5-C',                           
                            ):
        """
        First boot setup I: connect to the console to complete the first-boot node setup part 
        input: dhcp = no   - static ip assign
               dhcp = yes,  dhcp
        Author: Mingtao       
        """
        t = test.Test()
        n = t.node(node)

        if not ip_address:
            ip_address = n.ip()
        helpers.log("Entering ===> first_boot_controller_initial_node_setup: '%s', %s, %s, %s, %s, %s, %s, %s " \
                    % (node, dhcp, ip_address, netmask, gateway, dns_server, dns_search, hostname))
        helpers.log("Getting the console session for '%s'" % node)
        n_console = n.console()

        options = n_console.expect([r'Escape character.*[\r\n]', r'login:',r'Local Node Configuration'])
    
        content = n_console.content()
        helpers.log("*****Output is :*******\n%s" % content)
        if options[0]<2:
            if options[0] == 0 :
                helpers.log("USER INFO:  need to Enter " )
                n_console.send('')   
                n_console.send(helpers.ctrl('c'))
                helpers.sleep(2)
                n_console.send('')
                n_console.expect(r'Big Virtual Switch Appliance.*[\r\n]')
                n_console.expect(r'login:')            
            elif options[0] == 1:
                helpers.log("INFO:  need to login as  admin" )        
            n_console.send('admin')
            n_console.expect(r'Do you accept the EULA.* > ')
            n_console.send('Yes')
            n_console.expect(r'Local Node Configuration')
        
        n_console.expect(r'Password for emergency recovery user > ')
        n_console.send('bsn')
        n_console.expect(r'Retype Password for emergency recovery user > ')
        n_console.send('bsn')
        n_console.expect(r'Please choose an IP mode:.*[\r\n]')
        n_console.expect(r'> ')
        if dhcp == 'no':
            n_console.send('1')  # Manual
            n_console.expect(r'IP address .* > ')
            n_console.send(ip_address)
    
            if not re.match(r'.*/\d+', ip_address):
                # Send netmask if IP address doesn't contain prefix length
                n_console.expect(r'CIDR prefix length .* > ')
                n_console.send(netmask)
    
            n_console.expect(r'Default gateway address .* > ')
            n_console.send(gateway)
            n_console.expect(r'DNS server address .* > ')
            n_console.send(dns_server)
            n_console.expect(r'DNS search domain .* > ')
            n_console.send(dns_search)
            n_console.expect(r'Hostname > ')
            n_console.send(hostname)
        else:
            # dhcp 
            n_console.send('2')  #DHCP
        helpers.sleep(3)  # Sleep for a few seconds just in case...        
        return True
    
    def first_boot_controller_initial_cluster_setup(self,
                           node,
                           join_cluster = 'no',
                           cluster_ip ='',
                           cluster_passwd='adminadmin',
                           cluster_name='T5cluster',
                           cluster_descr='T5cluster',
                           admin_password='adminadmin',
                           ntp_server='',
                           ):
        """
        First boot setup II: connect to the console to complete the first-boot cluster setup part 
        input: join_cluster = no  - start a new cluster 
               join_cluster = yes  - jion existing cluster
        Author: Mingtao       
        """
  
        t = test.Test()
        n = t.node(node)
        helpers.log("Entering ===> first_boot_controller_initial_cluster_setup: '%s', %s, %s, %s, %s, %s, %s" \
                    % (node, join_cluster, cluster_ip, cluster_passwd, cluster_descr, admin_password, ntp_server)) 
        helpers.log("Getting the console session for '%s'" % node)
        n_console = n.console()        
#        n_console.expect(r'Controller Clustering')
        n_console.expect(r'Please choose a cluster option:.*')
        n_console.expect(r'> ')
        
        if join_cluster == 'yes':
            n_console.send('2')  # join existing cluster     
            n_console.expect(r'Existing node IP.*> ')
            n_console.send(cluster_ip)     
            n_console.expect(r'Administrator password for cluster.*> ')
            n_console.send(cluster_passwd)     
            n_console.expect(r'Retype Administrator password for cluster.*> ')
            n_console.send(cluster_passwd)     
        else:      
            n_console.send('1')  # Start a new cluster
            n_console.expect(r'Cluster name > ')
            n_console.send(cluster_name)
            n_console.expect(r'Cluster description .* > ')
            n_console.send(cluster_descr)
            n_console.expect(r'Administrator password for cluster > ')
            n_console.send(admin_password)
            n_console.expect(r'Retype .* > ')
            n_console.send(admin_password)    
            n_console.expect(r'System Time')
            n_console.expect(r'Enter NTP server .* > ')
            n_console.send(ntp_server)
            
        helpers.sleep(3)  # Sleep for a few seconds just in case...
        helpers.log("USER INFO:  Please choose an option"  )
                
        return True

    def first_boot_controller_menu_apply(self,node):
        """
        First boot setup III: connect to the console to apply the setting.
        First boot setup Menu :  Apply settings
        Author: Mingtao       
        """
        t = test.Test()
        n = t.node(node)
        helpers.log("Entering ====>  first_boot_controller_menu_1 for node: '%s'" % node)
        helpers.log("Getting the console session for '%s'" % node)
        n_console = n.console() 
        n_console.expect(r'\[1\] > ')
        helpers.log("[1] Apply settings " )      
        content = n_console.content()
        helpers.log("USER INFO: the content is '%s'" % content) 
        match = re.search(r'\[\s*(\d+)\] Apply settings.*[\r\n$]', content)
        if match:
            option = match.group(1)
            helpers.log("USER INFO: the option is %s" % option) 
        else:
            helpers.log("USER ERROR: there is no match" )             
            return False                 
                  
        n_console.send(option)  # Apply settings
        n_console.expect(r'Initializing system.*[\r\n]')
        n_console.expect(r'Configuring controller.*[\r\n]')
          
        n_console.expect(r'IP address on eth0 is (.*)[\r\n]')
        content = n_console.content()
     
        helpers.log("content is:  %s" % content)              
        match = re.search(r'IP address on eth0 is (\d+\.\d+\.\d+\.\d+).*[\r\n]', content)
        new_ip_address = match.group(1)
        helpers.log("new_ip_address: '%s'" % new_ip_address)  
                     
        n_console.expect(r'Configuring cluster.*[\r\n]')
        n_console.expect(r'First-time setup is complete.*[\r\n]')
        n_console.expect(r'Press enter to continue > ')
        n_console.send('')
        #helpers.log("Closing console connection for '%s'" % node)
        #n.console_close()

        helpers.sleep(3)  # Sleep for a few seconds just in case...
        return new_ip_address

       
        
    def first_boot_controller_menu_recovery(self,node,passwd='bsn'):
        """  
        First boot setup Menu :  Update Emergency Recovery Password
        Author: Mingtao       
        """
        t = test.Test()
        n = t.node(node)
        helpers.log("Entering ====>  Update Emergency Recovery Password for node: '%s'" % node)
        helpers.log("Getting the console session for '%s'" % node)
        n_console = n.console()
        n_console.expect(r'\[1\] > ')            
        content = n_console.content()
        helpers.log("USER INFO: the content is '%s'" % content) 
        match = re.search(r'\[\s*(\d+)\] Update Emergency Recovery Password.*[\r\n$]', content)
        if match:
            option = match.group(1)
            helpers.log("USER INFO: the optin is %s" % option) 
        else:
            helpers.log("USER ERROR: there is no match" )             
            return False       
        if option != '3':
            helpers.summary_log("choice %s not 2" % option)                        
        n_console.send(option)  # Apply settings            
        n_console.expect(r'Password for emergency recovery user > ')
        n_console.send(passwd)
        n_console.expect(r'Retype Password for emergency recovery user > ')
        n_console.send(passwd)
 #       n_console.expect(r'Please choose an option:.*[\r\n$]')   
       
        helpers.sleep(3)  # Sleep for a few seconds just in case...
        return True
    
    def first_boot_controller_menu_IP(self,node,ip_addr,netmask='24',invalid_input=False):
        """
       First boot setup Menu :  Update Local IP Address
        Author: Mingtao       
        """
        t = test.Test()
        n = t.node(node)
        helpers.log("Entering ====> Update Local IP Address for node: '%s'" % node)
        helpers.log("Getting the console session for '%s'" % node)
        n_console = n.console()
        options = n_console.expect([r'\[1\] > ', r'IP address .* >'])                                     
        content = n_console.content()
        helpers.log("USER INFO: the content is '%s'" % content) 
        if options[0] == 0:   
            match = re.search(r'\[\s*(\d+)\] Update Local IP Address.*[\r\n$]', content)
            if match:
                option = match.group(1)
                helpers.log("USER INFO: the optin is %s" % option) 
            else:
                helpers.log("USER ERROR: there is no match" )             
                return False                 
            if option != '5':
                helpers.summary_log("choice %s not 5" % option)      
            n_console.send(option)  # Apply settings            
            n_console.expect(r'IP address .* > ')
        n_console.send(ip_addr)
        if invalid_input:
            helpers.log("USER INFO: in invalid input,  this is negative case" ) 
            n_console.expect(r'Error:.*')  
            return True                                  
#        else:
#            n_console.expect(r'Please choose an option:.*[\r\n$]')   
       
        if not re.match(r'.*/\d+', ip_addr):
            # to make sure the next table has CIDR entry
            n_console.expect(r'\[1\] > ') 
            content = n_console.content()
            helpers.log("USER INFO: the content is '%s'" % content) 
            match = re.search(r'\[\s*(\d+)\] Update CIDR Prefix Length.*[\r\n$]', content)
            if match:
                option = match.group(1)
                helpers.log("USER INFO: the option is %s" % option)
            else:
                helpers.log("USER ERROR: there is no match" )             
                return False                 
            n_console.send(option)  # Apply settings            
            n_console.expect(r'CIDR prefix length \[24\].* > ')
            n_console.send(netmask)
        helpers.sleep(3)  # Sleep for a few seconds just in case...          
        return True


    def first_boot_controller_menu_prefix(self,node,netmask,invalid_input=False):
        """
       First boot setup Menu :  Update CIDR Prefix Length
        Author: Mingtao              
        """
        t = test.Test()
        n = t.node(node)
        helpers.log("Entering ====> Update CIDR Prefix Length for node: '%s'" % node)
        helpers.log("Getting the console session for '%s'" % node)
        n_console = n.console()
         
        options = n_console.expect([r'\[1\] > ', r'CIDR prefix length.* >'])    
        content = n_console.content()      
        helpers.log("USER INFO: the content:  %s" % content)        
        if options[0] == 0:   
            match = re.search(r'\[\s*(\d+)\] Update CIDR Prefix Length.*[\r\n$]', content)
            if match:
                option = match.group(1)
                helpers.log("USER INFO: the option is %s" % option) 
            else:
                helpers.log("USER ERROR: there is no match" )             
                return False                 
            n_console.send(option)  # Apply settings            
            n_console.expect(r'CIDR prefix length \[24\].* > ')
        n_console.send(netmask)
        if invalid_input:
            helpers.log("USER INFO: in invalid input,  this is negative case" ) 
            n_console.expect(r'Error:.*')                                    
#        else:
#            n_console.expect(r'Please choose an option:.*[\r\n$]')   
                
        helpers.sleep(3)  # Sleep for a few seconds just in case...          
        return True




    def first_boot_controller_menu_gateway(self,node,gateway):
        """
       First boot setup Menu :  Update Gateway
        Author: Mingtao       
       
        """
        t = test.Test()
        n = t.node(node)
        helpers.log("Entering ====> Update Gateway for node: '%s'" % node)
        helpers.log("Getting the console session for '%s'" % node)
        n_console = n.console()
        n_console.expect(r'\[1\] > ')                
        content = n_console.content()
        helpers.log("USER INFO: the content is '%s'" % content) 
        match = re.search(r'\[\s*(\d+)\] Update Gateway.*[\r\n$]', content)
        if match:
            option = match.group(1)
            helpers.log("USER INFO: the option is %s" % option) 
        else:
            helpers.log("USER ERROR: there is no match" )             
            return False                 
        n_console.send(option)  # Apply settings     
        n_console.expect(r'Gateway.*')               
        n_console.expect(r'Default gateway address.*> ')
        n_console.send(gateway)
#        n_console.expect(r'Please choose an option:.*[\r\n$]')    
          
        helpers.sleep(3)  # Sleep for a few seconds just in case...
        return True
    
    def first_boot_controller_menu_dnsserver(self,node,dnsserver,invalid_input=False):
        """
       First boot setup Menu :  Update DNS Server
        Author: Mingtao              
        """
        t = test.Test()
        n = t.node(node)
        helpers.log("Entering ====> Update DNS Server for node: '%s'" % node)
        helpers.log("Getting the console session for '%s'" % node)
        n_console = n.console()
        
        options = n_console.expect([r'\[1\] > ', r'DNS server address.* >'])    
        content = n_console.content()      
        helpers.log("USER INFO: the content:  %s" % content)        
        if options[0] == 0:   
            match = re.search(r'\[\s*(\d+)\] Update DNS Server.*[\r\n$]', content)
            if match:
                option = match.group(1)
                helpers.log("USER INFO: the option is %s" % option) 
            else:
                helpers.log("USER ERROR: there is no match" )             
                return False                 
            n_console.send(option)  # Apply settings    
            n_console.expect(r'DNS Server.*')                
            n_console.expect(r'DNS server address.* > ')
            
        n_console.send(dnsserver)
        if invalid_input:
            helpers.log("USER INFO: in invalid input,  this is negative case" ) 
            n_console.expect(r'Error: Invalid.*')                                    
#        else:
#            n_console.expect(r'Please choose an option:.*[\r\n$]')   
          
        helpers.sleep(3)  # Sleep for a few seconds just in case...
        return True

    def first_boot_controller_menu_domain(self,node,domain):
        """
       First boot setup Menu :  Update DNS Search Domain
        Author: Mingtao       
        """
        t = test.Test()
        n = t.node(node)
        helpers.log("Entering ====> Update DNS Search Domain for node: '%s'" % node)
        helpers.log("Getting the console session for '%s'" % node)
        n_console = n.console()
        n_console.expect(r'\[1\] > ')                
        content = n_console.content()
        helpers.log("USER INFO: the content is '%s'" % content) 
        match = re.search(r'\[\s*(\d+)\] Update DNS Search Domain.*[\r\n$]', content)
        if match:
            option = match.group(1)
            helpers.log("USER INFO: the optin is %s" % option) 
        else:
            helpers.log("USER ERROR: there is no match" )             
            return False                 
        n_console.send(option)  # Apply settings    
        n_console.expect(r'DNS Search Domain.*')                
        n_console.expect(r'DNS search domain.* > ')
        n_console.send(domain)
#        n_console.expect(r'Please choose an option:.*[\r\n$]')   
          
        helpers.sleep(3)  # Sleep for a few seconds just in case...
        return True
     
    def first_boot_controller_menu_name(self,node,name):
        """
       First boot setup Menu :  Update Hostname
        Author: Mingtao       
        """
        t = test.Test()
        n = t.node(node)
        helpers.log("Entering ====> Update Hostname for node: '%s'" % node)
        helpers.log("Getting the console session for '%s'" % node)
        n_console = n.console()
        n_console.expect(r'\[1\] > ')                
        content = n_console.content()
        helpers.log("USER INFO: the content is '%s'" % content) 
        match = re.search(r'\[\s*(\d+)\] Update Hostname.*[\r\n$]', content)
        if match:
            option = match.group(1)
            helpers.log("USER INFO: the optin is %s" % option) 
        else:
            helpers.log("USER ERROR: there is no match" )             
            return False                 
      
        n_console.send(option)  # Apply settings    
        n_console.expect(r'Hostname.*')                
        n_console.expect(r'Hostname.* > ')
        n_console.send(name)
#        n_console.expect(r'Please choose an option:.*[\r\n$]')   
          
        helpers.sleep(3)  # Sleep for a few seconds just in case...
        return True
            
    def first_boot_controller_menu_cluster_name(self,node,name='MY-T5-C',invalid_input=False):
        """
       First boot setup Menu :   Update Cluster Name
        """
        t = test.Test()
        n = t.node(node)
        helpers.log("Entering ====> Update Cluster Name for node: '%s'" % node)
        helpers.log("Getting the console session for '%s'" % node)
        n_console = n.console()
          
        options = n_console.expect([r'\[1\] > ',r'Cluster name.* > '])             
        content = n_console.content()
        helpers.log("USER INFO: the content is '%s'" % content) 
        if options[0] == 0:   
            match = re.search(r'\[\s*(\d+)\] Update Cluster Name.*[\r\n$]', content)
            if match:
                option = match.group(1)
                helpers.log("USER INFO: the option is %s" % option) 
            else:
                helpers.log("USER ERROR: there is no match" )             
                return False                 
            n_console.send(option)  # Apply settings                
            n_console.expect(r'Cluster Name.*')                
            n_console.expect(r'Cluster name.* > ')
            
        n_console.send(name)
        if invalid_input:
            helpers.log("USER INFO: in invalid input,  this is negative case" ) 
            n_console.expect(r'Error: Invalid.*')                                    
#        else:
#            n_console.expect(r'Please choose an option:.*[\r\n$]')   
           
        helpers.sleep(3)  # Sleep for a few seconds just in case...
        return True
 
    def first_boot_controller_menu_cluster_desr(self,node,descr='MY-T5-C'):
        """
       First boot setup Menu :   Update Cluster Description
        """
        t = test.Test()
        n = t.node(node)
        helpers.log("Entering ====> Update Cluster Description for node: '%s'" % node)
        helpers.log("Getting the console session for '%s'" % node)
        n_console = n.console()
        n_console.expect(r'\[1\] > ')                
        content = n_console.content()
        helpers.log("USER INFO: the content is '%s'" % content) 
        match = re.search(r'\[\s*(\d+)\] Update Cluster Description.*[\r\n$]', content)
        if match:
            option = match.group(1)
            helpers.log("USER INFO: the optin is %s" % option) 
        else:
            helpers.log("USER ERROR: there is no match" )             
            return False                 
        n_console.send(option)  # Apply settings    
        n_console.expect(r'Cluster Description.*')                
        n_console.expect(r'Cluster description.* > ')
        n_console.send(descr)
#        n_console.expect(r'Please choose an option:.*[\r\n$]')   
          
        helpers.sleep(3)  # Sleep for a few seconds just in case...
        return True
    
    def first_boot_controller_menu_cluster_passwd(self,node,passwd='adminadmin'):
        """
       First boot setup Menu :   Update Cluster Admin Password
        """
        t = test.Test()
        n = t.node(node)
        helpers.log("Entering ====> Update Cluster Admin Password  for node: '%s'" % node)
        helpers.log("Getting the console session for '%s'" % node)
        n_console = n.console()
        n_console.expect(r'\[1\] > ')                
        content = n_console.content()
        helpers.log("USER INFO: the content is '%s'" % content) 
        match = re.search(r'\[\s*(\d+)\] Update Cluster Admin Password.*[\r\n$]', content)
        if match:
            option = match.group(1)
            helpers.log("USER INFO: the optin is %s" % option) 
        else:
            helpers.log("USER ERROR: there is no match" )             
            return False                 
        n_console.send(option)  # Apply settings    
        n_console.expect(r'Cluster Admin Password.*')                
        n_console.expect(r'Administrator password for cluster.* > ')
        n_console.send(passwd)
        n_console.expect(r'Retype Administrator password for cluster.* > ')
        n_console.send(passwd)
#        n_console.expect(r'Please choose an option:.*[\r\n$]')   
        helpers.sleep(3)  # Sleep for a few seconds just in case...
        return True
    
    def first_boot_controller_ctl_c(self,node):
        """
       First boot:   send ctl_c,  then resume
        Author: Mingtao
        """
        t = test.Test()
        n = t.node(node)
        helpers.log("Entering ====> first_boot_controller_ctl_c  for node: '%s'" % node)
        helpers.log("Getting the console session for '%s'" % node)
        n_console = n.console()
        
        n_console.send(helpers.ctrl('c'))
        helpers.summary_log('CTRL  C is hited' )
         
        n_console.expect(r'Option Menu.*')  
        n_console.expect(r'\[1\] > ')                               
        content = n_console.content()
        helpers.log("USER INFO: the content is '%s'" % content) 
        match = re.search(r'\[\s*(\d+)\] Resume setup.*[\r\n$]', content)
        if match:
            option = match.group(1)
            helpers.log("USER INFO: the option is %s" % option) 
        else:
            helpers.log("USER ERROR: there is no match for resume setup" )             
            return False                 
        n_console.send(option)  # Apply settings    
        n_console.expect(r'Resuming setup.*')   
        return True
      
    def rest_controller_add_ip(self, node, ipaddr,netmask,spawn=None):
        """
          config a new local ip address and make sure it is reachable.
          Author: Mingtao
          input:  node  - controller  
                           c1 c2    
                   spawn: if node= 1.1.1.1,  and the address is not in topology, set it to True
          usage:   
          output:   
        """        
        t = test.Test()        
        if spawn:
            #  this is a ip address not in topology,  need to spawn, node is an ip address
            c = t.node_spawn(ip=node)
        else:
            c = t.controller(node)        
        url = '/api/v1/data/controller/os/config/local-node/network-config/network-interface[type="ethernet"][number=0]/ipv4/address[ip-address="%s"]' %ipaddr  
        try:     
            c.rest.put(url,{"prefix":netmask,"ip-address":ipaddr})
        except:
            helpers.test_failure(c.rest.error())           
            return False
        else:
            helpers.sleep(5)  # Sleep for a few seconds just in case...
            loss = helpers.ping(ipaddr)
            if loss < 50:
                helpers.log("Node '%s' ip address:  %s is reachable !" % (node, ipaddr))
                return True
            else:
                return False

    def rest_controller_add_ntp_timezone(self, node, timezone):
        """
          config a ntp time zone.
          Author: Mingtao
          input:  node  - controller  
                           c1 c2    
                 timezone:    America/Los_Angeles     America/New_York
          usage:   
          output:   
        """        
        
        t = test.Test()
        c = t.controller(node)                
        helpers.log('INFO: Entering ==> rest_controller_add_ntp')        
        url = '/api/v1/data/controller/os/config/global/time-config' 
    
        try:      
            c.rest.put(url,{"time-zone":timezone})
        except:
            helpers.test_failure(c.rest.error())           
            return False
        else:
            return True

    def cli_controller_show_clock(self, node):
        """
          cli show clock  
          Author: Mingtao
          input:  node  - controller  
                           c1 c2                  
          usage:   
          output:   {'time':......,'timezone':PDT}
        """        
        t = test.Test()
        c = t.controller(node)                
        helpers.log('INFO: Entering ==> cli_controller_show_clock')          
        c.cli("show clock")
        content = c.cli_content()
 
        temp = helpers.strip_cli_output(content)
        helpers.log("*****Output is :\n%s" % temp)        
        match = re.match(r'System time :\s+(.*) ([A-Z]{3})[\r\n\$]',temp)
        if match:
            time = {}
            helpers.log("INFO: time is: %s" % match.group(1)) 
            time['time'] = match.group(1)
            helpers.log("INFO: time zone is: %s" % match.group(2))
            time['timezone'] = match.group(2)
            return time   
        else:
            helpers.log("ERROR: did not match the time: %s" % temp)       
            return False
    
    def controller_verify_timezone(self, node, timezone):
        """
         verify the timezone configuration
          Author: Mingtao
          input:  node  - controller  
                           c1 c2   
                timezone:    America/Los_Angeles     America/New_York                        
          usage:   
          output:   True:   if expect and show clock matches
                    False:  if expect and show clock Not matche 
        
        """
        helpers.log('INFO: Entering ==> controller_verify_timezone ') 
        temp=self.cli_controller_show_clock(node)   
        helpers.log("INFO: timezone is: %s" % temp['timezone'])   
        ctimezone = temp['timezone']
        if timezone ==  'America/Los_Angeles' and ctimezone == 'PDT':           
            return True          
        elif timezone ==  'America/New_York' and ctimezone == 'EDT':  
            return True 
        return False
            
 
    def first_boot_controller_menu_cluster_option_apply(self,node,
                           join_cluster = 'no',
                           cluster_ip ='',
                           cluster_passwd='adminadmin',
                           cluster_name='T5cluster',
                           cluster_descr='T5cluster',
                           admin_password='adminadmin',
                           ntp_server='',
                            ):
        """
       First boot setup Menu :   Update Cluster Name
        """
        t = test.Test()
        n = t.node(node)
        helpers.log("Entering ====> Update Cluster Option for node: '%s'" % node)
       
        helpers.log("Getting the console session for '%s'" % node)
        n_console = n.console()
        n_console.expect(r'\[1\] > ')                
        content = n_console.content()
        helpers.log("USER INFO: the content is '%s'" % content) 
        match = re.search(r'\[\s*(\d+)\] Update Cluster Option.*[\r\n$]', content)
        if match:
            option = match.group(1)
            helpers.log("USER INFO: the option is %s" % option) 
        else:
            helpers.log("USER ERROR: there is no match" )             
            return False                 
        n_console.send(option)  # Apply settings         
        n_console.expect(r'Please choose a cluster option:.*')
        n_console.expect(r'> ')
        
        if join_cluster == 'yes':
            n_console.send('2')  # join existing cluster     
            n_console.expect(r'Existing node IP.*> ')
            n_console.send(cluster_ip)     
        else:      
            n_console.send('1')  # Start a new cluster
            n_console.expect(r'Cluster name > ')
            n_console.send(cluster_name)
            n_console.expect(r'Cluster description .* > ')
            n_console.send(cluster_descr)
            n_console.expect('')
        try:
            options = n_console.expect([r'\[1\] > ', r'[^\]]> '])
        except:
            content = n_console.content()    
            helpers.log("*****Output is :*******\n%s" % content)           
            helpers.log("USER ERROR: there is no match") 
            helpers.test_failure('There is no match')
             
        else:    
            content = n_console.content()    
            helpers.log("*****Output is :*******\n%s" % content)  
       
            if options[0] == 0 :                 
                helpers.log("*****Matched   [1] > can apply setting now*******  "  )       
            elif options[0] == 1:
                helpers.log("*****Matched >  can NOT apply setting now*******  "  ) 
            
                match = re.search(r'\[\s*(\d+)\].*<NOT SET, UPDATE REQUIRED>.*[\r\n$]', content)
                if match:
                    helpers.log("USER INFO:  need to configure ntp"  )                       
                    option = match.group(1)
                    helpers.log("USER INFO: the option is %s" % option)                      
                    n_console.send(option)
                    n_console.expect(r'Enter NTP server.* > ')
                    n_console.send('')    
                    n_console.expect(r'\[1\] > ')             
                                    
            n_console.send('')  # Apply settings
            n_console.expect(r'Initializing system.*[\r\n]')
            n_console.expect(r'Configuring controller.*[\r\n]')
              
            n_console.expect(r'IP address on eth0 is (.*)[\r\n]')
            content = n_console.content()
         
            helpers.log("content is:  %s" % content)              
            match = re.search(r'IP address on eth0 is (\d+\.\d+\.\d+\.\d+).*[\r\n]', content)
            new_ip_address = match.group(1)
            helpers.log("new_ip_address: '%s'" % new_ip_address)  
                         
            n_console.expect(r'Configuring cluster.*[\r\n]')
            n_console.expect(r'First-time setup is complete.*[\r\n]')
            n_console.expect(r'Press enter to continue > ')
            n_console.send('')
            helpers.sleep(3)  # Sleep for a few seconds just in case...
            return new_ip_address
               
             
    def first_boot_controller_menu_reset(self,node):
        """
       First boot setup Menu :   reset 
        """
        t = test.Test()
        n = t.node(node)
        helpers.log("Entering ====> Reset and start over for node: '%s'" % node)
        helpers.log("Getting the console session for '%s'" % node)
        n_console = n.console()
        n_console.expect(r'\[1\] > ')                
        content = n_console.content()
        helpers.log("USER INFO: the content is '%s'" % content) 
        match = re.search(r'\[\s*(\d+)\] Reset and start over.*[\r\n$]', content)
        if match:
            option = match.group(1)
            helpers.log("USER INFO: the option is %s" % option) 
        else:
            helpers.log("USER ERROR: there is no match" )             
            return False                 
        n_console.send(option) 
  
        return True
    
    
    
    def first_boot_controller_menu_apply_negative(self,node, **kwargs):
        """
        First boot setup III: connect to the console to apply the setting. 
            this is negative, if wrong gw is given. then NTP and DNS can not be reached
        First boot setup Menu :  Apply settings
    
        Author: Mingtao       
        """
        t = test.Test()
        n = t.node(node)
        helpers.log("Entering ====>  first_boot_controller_menu_1 for node: '%s'" % node)
        helpers.log("Getting the console session for '%s'" % node)
        n_console = n.console() 
        n_console.expect(r'\[1\] > ')
        helpers.log("[1] Apply settings " )      
        content = n_console.content()
        helpers.log("USER INFO: the content is '%s'" % content) 
        match = re.search(r'\[\s*(\d+)\] Apply settings.*[\r\n$]', content)
        if match:
            option = match.group(1)
            helpers.log("USER INFO: the option is %s" % option) 
        else:
            helpers.log("USER ERROR: there is no match" )             
            return False                 
                  
        n_console.send(option)  # Apply settings
        n_console.expect(r'Initializing system.*[\r\n]')
        n_console.expect(r'Configuring controller.*[\r\n]')
        n_console.expect(r'Waiting for network configuration.*[\r\n]')        
        options=n_console.expect([r'Unable to resolve domains with DNS.*[\r\n]',r'No route to host.*[\r\n]'],timeout=300)
        if options[0] == 0:
            n_console.expect(r'Retrieving time from NTP server.*[\r\n]',timeout=120)
            n_console.expect(r'unreachable now.*[\r\n]',timeout=120)        
            n_console.expect(r'Configuring cluster.*[\r\n]',timeout=120) 
        if options[0] == 1 : 
            helpers.log("USER INFO: need to correct cluster ip") 
        try:
            options = n_console.expect([r'\[1\] >', r'First-time setup is complete.*[\r\n]'], timeout =120)    
        except:
            content = n_console.content()    
            helpers.log("*****Output is :*******\n%s" % content)           
            helpers.log("USER ERROR: there is no match") 
            helpers.test_failure('There is no match')
        else:
            content = n_console.content()    
            helpers.log("*****Output is :*******\n%s" % content)  
       
            if options[0] == 0 :                 
                helpers.summary_log("*****Need to correct parameter *******  "  )       
                if 'gateway' in kwargs:
                    gateway=kwargs.get('gateway')
                    match = re.search(r'\[\s*(\d+)\] Update Gateway.*[\r\n$]', content)
                    if match:
                        option = match.group(1)
                        helpers.log("USER INFO: the option is %s" % option) 
                    else:
                        helpers.log("USER ERROR: there is no match" )             
                        return False                 
                    n_console.send(option)  # Apply settings     
                    n_console.expect(r'Gateway.*')               
                    n_console.expect(r'Default gateway address.*> ')
                    n_console.send(gateway)
                    n_console.expect(r'\[1\] >')
                    content = n_console.content()  
                if 'dns' in kwargs:
                    dns=kwargs.get('dns')
                    match = re.search(r'\[\s*(\d+)\] Update DNS Server.*[\r\n$]', content)
                    if match:
                        option = match.group(1)
                        helpers.log("USER INFO: the option is %s" % option) 
                    else:
                        helpers.log("USER ERROR: there is no match" )             
                        return False                 
                    n_console.send(option)  # Apply settings     
                    n_console.expect(r'DNS Server.*')               
                    n_console.expect(r'DNS server address.* > ')
                    n_console.send(dns)
                    n_console.expect(r'\[1\] >')
                if 'cluster_ip' in kwargs:
                    clusterip=kwargs.get('cluster_ip')
                    match = re.search(r'\[\s*(\d+)\] Update Existing Node IP Address.*[\r\n$]', content)
                    if match:
                        option = match.group(1)
                        helpers.log("USER INFO: the option is %s" % option) 
                    else:
                        helpers.log("USER ERROR: there is no match" )             
                        return False                 
                    n_console.send(option)  # Apply settings     
                    n_console.expect(r'Existing Node IP Address.*')               
                    n_console.expect(r'Existing node IP.* > ')
                    n_console.send(clusterip)
                    n_console.expect(r'\[1\] >')
                                            
                n_console.send('')  # Apply settings
                n_console.expect(r'Initializing system.*[\r\n]',timeout=120)
                n_console.expect(r'Configuring controller.*[\r\n]',timeout=120)                              
                n_console.expect(r'Configuring cluster.*[\r\n]',timeout=120)
                n_console.expect(r'First-time setup is complete.*[\r\n]',timeout=120)
                n_console.expect(r'Press enter to continue > ')
                n_console.send('')
                helpers.sleep(3)  # Sleep for a few seconds just in case...
                return True             
               
            if options[0] == 1 :                 
                helpers.log("*****first boot complete *******  "  )   
                n_console.expect(r'Press enter to continue > ')
                n_console.send('')    
                helpers.summary_log('First boot complete even the NTP/DNS not reachable' )
        helpers.sleep(3)  # Sleep for a few seconds just in case...
        return True

    def cli_show_local_config(self,node):
        '''
        show the local node config
        '''
      
        t = test.Test()
        c = t.controller(node)
    
        c.enable('')
        c.enable("show running-config local")
        content = c.cli_content()
        helpers.log("*****Output is :\n%s" % content)
        temp = helpers.strip_cli_output(content)
        temp = helpers.str_to_list(temp)
        helpers.log("*****Output list   is :\n%s" % temp)
             
        localinfo = {}    
        for line in temp:          
            line = line.lstrip()
            helpers.log(" line is - %s" % line)            
            if (re.match(r'.*hostname .*', line)): 
                match = re.match(r'.*hostname (.*)', line)        
                localinfo['hostname'] = match.group(1)
            
            elif (re.match(r'.*dns search.*', line)): 
                match = re.match(r'.*dns search (.*)', line)        
                localinfo['domain'] = match.group(1)
             
            elif (re.match(r'.*dns server.*', line)): 
                match = re.match(r'.*dns server (.*)', line)        
                localinfo['dns'] = match.group(1)
            
            elif (re.match(r'.*ip.* gateway.*', line)): 
                match = re.match(r'.*ip (\d+\.\d+\.\d+\.\d+)/(\d+) gateway (\d+\.\d+\.\d+\.\d+)', line)        
                localinfo['ip'] = match.group(1)
                localinfo['mask'] = match.group(2)
                localinfo['gateway'] = match.group(3)
            elif (re.match(r'.*Error: running command.*', line)):  
                helpers.test_failure("Error:  there is a show command error \n %s " % line)                
                   
            helpers.log("INFO: *** local node info *** \n  %s" % localinfo)      
        return localinfo      

        
    def bash_df(self, node):
        ''' do df in debug bash
        ouput: index:  directory  with all the field
        '''
        t = test.Test()
        n = t.node(node)
        content = n.bash('df')['content']
        lines = helpers.strip_cli_output(content, to_list=True)
        lines = lines[1:]
        helpers.log("lines: %s" %  lines )
        dfinfo = {}      
    
        for line in lines:
            line = line.lstrip()
            fields = line.split()
            helpers.log("fields: %s" % fields)   
            dfinfo[fields[5]]={}         
            dfinfo[fields[5]]['filesystem']=fields[0]
            dfinfo[fields[5]]['1k-blocks']=fields[1]            
            dfinfo[fields[5]]['used']=fields[2]    
            dfinfo[fields[5]]['available']=fields[3]               
            dfinfo[fields[5]]['usedpercent']=fields[4]               
        helpers.log("USER INFO: dfinfo is :\n%s" % dfinfo)
        return dfinfo

    def get_disk_used_percentage(self, node, directory):        
        '''
        get the used percentage for given directory
        '''
        dfinfo = self.bash_df(node)
        return dfinfo[directory]['usedpercent']

    
    def rest_configure_testpath_controller_view(self, **kwargs):
        '''
            This function will query the controller for the test packet path controller view
            Returns True if controller view returns without an error message.
            
            kwargs Examples:
                src-tenant=T1    
                src-segment=v1    
                src-ip=10.10.10.51    
                dst-tenant=T1  
                dst-segment=v1    
                dst-ip=10.10.10.52    
                ip-protocol=icmp
        '''
        t = test.Test()
        c = t.controller('main')
        url =  '/api/v1/data/controller/applications/bvs/test/path/controller-view'
        
        if(kwargs.get('dst-segment')):
            url = url + '[dst-segment="%s"]' % (kwargs.get('dst-segment'))
        if(kwargs.get('dst-tenant')):
            url = url + '[dst-tenant="%s"]' % (kwargs.get('dst-tenant'))
        if(kwargs.get('ip-protocol')):
            url = url + '[ip-protocol="%s"]' % (kwargs.get('ip-protocol'))
        if(kwargs.get('src-ip')):
            url = url + '[src-ip="%s"]' % (kwargs.get('src-ip'))
        if(kwargs.get('src-segment')):
            url = url + '[src-segment="%s"]' % (kwargs.get('src-segment'))
        if(kwargs.get('dst-ip')):
            url = url + '[dst-ip="%s"]' % (kwargs.get('dst-ip'))
        if(kwargs.get('src-tenant')):
            url = url + '[src-tenant="%s"]' % (kwargs.get('src-tenant'))
            
        
        result = c.rest.get(url)['content']
        hopCount = 0
        for item in result[0]["logical-hop"]: 
            try:
                errorCode = item["error"]
                helpers.log("Test Path Error In Controller View:  %s" % errorCode)
                return False
            except (KeyError):
                hopCount += 1
                try:
                    if item["policy-action"]:
                        helpers.log("Policy Action- %s ===== At Hop- %s" % ( item["policy-action"], item["hop-name"]))
                except(KeyError):
                    pass
                pass
        
        helpers.log("Test Path Sucees In Controller View. Number Of Logical Hops Detected: %s" % hopCount )
        return True
                    
                    
    def rest_configure_testpath_fabric_view(self, **kwargs):
        '''
            This function will set up the fabric view for the controller.
            Returns True if the fabric view returns without an error message after the setup.
            
            kwargs Examples:
                test-name=Test1
                src-tenant=T1    
                src-segment=v1    
                src-ip=10.10.10.51    
                dst-tenant=T1  
                dst-segment=v1    
                dst-ip=10.10.10.52    
                ip-protocol=tcp
                src-l4-port=8000
                dst-l4-port=8500
        '''
        t = test.Test()
        c = t.controller('main')
            
        url = '/api/v1/data/controller/applications/bvs/test/path/setup-result'

        if(kwargs.get('test-name')):
            url = url + '[test-name="%s"]' % (kwargs.get('test-name'))
        if(kwargs.get('timeout')):
            url = url + '[timeout="%s"]' % (kwargs.get('timeout'))
        if(kwargs.get('dst-segment')):
            url = url + '[dst-segment="%s"]' % (kwargs.get('dst-segment'))
        if(kwargs.get('dst-tenant')):
            url = url + '[dst-tenant="%s"]' % (kwargs.get('dst-tenant'))
        if(kwargs.get('ip-protocol')):
            url = url + '[ip-protocol="%s"]' % (kwargs.get('ip-protocol'))
        if(kwargs.get('src-ip')):
            url = url + '[src-ip="%s"]' % (kwargs.get('src-ip'))
        if(kwargs.get('src-segment')):
            url = url + '[src-segment="%s"]' % (kwargs.get('src-segment'))
        if(kwargs.get('dst-ip')):
            url = url + '[dst-ip="%s"]' % (kwargs.get('dst-ip'))
        if(kwargs.get('src-tenant')):
            url = url + '[src-tenant="%s"]' % (kwargs.get('src-tenant'))
        if(kwargs.get('src-l4-port')):
            url = url + '[src-l4-port=%s]' % (kwargs.get('src-l4-port'))
        if(kwargs.get('dst-l4-port')):
            url = url + '[dst-l4-port=%s]' % (kwargs.get('dst-l4-port'))
        
        result = c.rest.get(url)['content']
        hopCount = 0
        for item in result[0]["logical-hop"]: 
            try:
                errorCode = item["error"]
                helpers.log("Test Path Error In Fabric View:  %s" % errorCode)
                helpers.log("%s" % result[0]["message"][0]["setup-message"])
                return False
            except (KeyError):
                hopCount += 1
                try:
                    if item["policy-action"]:
                        helpers.log("Policy Action- \"%s\" ===== At Hop- \"%s\"" % ( item["policy-action"], item["hop-name"]))
                except(KeyError):
                    pass
                pass
                
        helpers.log("Test Path Sucees In Fabric View. Number Of Logical Hops Detected: %s" % hopCount )
        return True
    
    def rest_verify_testpath_fabric_view(self, testName, trafficMode, *args, **kwargs):
        
        '''
            This function will verify the fabric view test path with the active traffic stream
            
            testName => testName from the rest_configure_testpath_fabric_view
            trafficMode => Ixia / HostPing
            args:
                Expected traffic path through the Leaf or Spine switches
                eg: "leaf  spine  leaf"
            kwargs:
                If trafficMode==Ixia:  stream:StreamName (Ixia streamName) [Optional, only if the user wants
                us to start the ixia stream]
                host:hostName (Hostname of the host which the ping should originate from)
                ip:pingIP (The IP address to ping)
        '''
        t = test.Test()
        c = t.controller("main")
        
        if(trafficMode=='Ixia'):
            if 'stream' in kwargs:
                helpers.log("Test Path: Starting Ixia Stream: %s" % kwargs.get('stream'))
                ixia = Ixia.Ixia()
                ixia.start_traffic(kwargs.get('stream'))
                sleep(10)
            
        elif(trafficMode == 'HostPing'):
            pingThread = T5PlatformThreads(1, "hostPing",  host=kwargs.get('host'), IP=kwargs.get('ip'))
            helpers.log("Starting ping thread to ping from %s to destIP: %s" % (kwargs.get('host'), kwargs.get('ip')))
            pingThread.start()
            sleep(3)
        
        url = '/api/v1/data/controller/applications/bvs/test/path/fabric-view[test-name="%s"]' % testName
        result = c.rest.get(url)['content']

        count = 0
        while(True):
            if(count == 3):
                helpers.log("Test Path Error During Validating Hops List")
                return  False
            count += 1
            currentHops = []
            currentFlowCount = {}
            currentPktInCount = {}
            try:
                for index,hop in enumerate(result[0]['physical-hop']):
                    try:
                        if (index > len(args)-1):
                            helpers.log("Test Path Error: Expected # of Hops: %s / Actual # of Hops: %s" %((len(args), len(result[0]['physical-hop']))))
                            return False
                        
                        if args[index] not in hop["hop-name"]:
                            helpers.log("Test Path Error: Expected - %s / Actual - %s" % (args[index], hop["hop-name"]))
                            return False
                        else: 
                            currentHops.append(hop['hop-name'])
                            currentFlowCount[hop["hop-name"]] = hop["flow-counter"].strip('[]')
                            currentPktInCount[hop["hop-name"]] = hop["pktin-counter"].strip('[]')
                            
                    except Exception as e:
                        helpers.log("Test Path Error During Validating Hops List: %s" % str(e))
                        return  False
                
                if(len(args) != len(currentHops)):
                    helpers.log("Test Path Error: Expected # Hops : %s / Actual # Hops: %s" % (len(args), len(currentHops)))
                    return False
                
                break
            
            except Exception as e:
                helpers.log("Exception occured: %s" % str(e))
                helpers.log("Test Path: No Hops Detected. Retrying ...")

                
        sleep(3)
        url = '/api/v1/data/controller/applications/bvs/test/path/fabric-view[test-name="%s"]' % testName
        result = c.rest.get(url)['content']
        for hop in result[0]['physical-hop']:
            try:
                newFlowCount = int(hop["flow-counter"].strip('[]'))
                newPktInCount = int(hop["pktin-counter"].strip('[]'))
                
                if(newFlowCount > int(currentFlowCount[hop["hop-name"]])):
                    helpers.log("Hop: %s passing @ newFlowCount" % hop["hop-name"])
                    pass 
                elif(newPktInCount > int(currentPktInCount[hop["hop-name"]])):
                    helpers.log("Hop: %s passing @ newPktInCount" % hop["hop-name"])
                    pass
                else:
                    helpers.log("Test Path Error During Flow Path Counting For Hop \"%s\": Previous Count- %s / New Count- %s" % (hop["hop-name"], currentFlowCount[hop["hop-name"]], newFlowCount))
                    return False
                
            except Exception as e:
                helpers.log("Test Path Error During Validating Hops List: %s" % str(e))
                return  False
                  
        
        if(trafficMode=='Ixia'):
            if 'stream' in kwargs:
                ixia.stop_traffic(kwargs.get('stream'))
        if(trafficMode=='HostPing'):
            pingThread.join()
        
        return True
    
        
    def rest_verify_testpath(self, pathName):
        
        t = test.Test()
        c = t.controller("main")
        
        url = '/api/v1/data/controller/applications/bvs/test/path/all-test'
        
        try:
            result = c.rest.get(url)['content']
            for testpath in result:
                if testpath['test-name'] == pathName:
                    helpers.log("Found path: %s in the test-path config" % pathName)
                    return True
        except:
            helpers.test_failure(c.rest.error())           
            return False
        else:
            helpers.log("Didn't find path: %s in the test-path config" % pathName)
            return False
        
    def rest_verify_testpath_timeout(self,pathName):
        
        t = test.Test()
        c = t.controller("main")
        
        url = '/api/v1/data/controller/applications/bvs/test/path/all-test'
        
        try:
            result = c.rest.get(url)['content']
            for testpath in result:
                if testpath['test-name'] == pathName:
                    if testpath['test-state'] == "TIMEDOUT":
                        helpers.log("Test Path: %s in TIMEDOUT state" % pathName)
                        return True
                    else:
                        helpers.log("Test Path: %s not in TIMEDOUT state" % pathName)
                        return False
                        
        except:
            helpers.test_failure(c.rest.error())           
            return False
        else:
            helpers.log("Didn't find path: %s in the test-path config" % pathName)
            return False
        
        
    def cli_walk_exec(self, string='', file_name=None, padding=''):
        ''' cli_exec_walk
           walk through exec/login mode CLI hierarchy
           output:   file cli_exec_walk
        '''
        t = test.Test()
        c = t.controller('main')
        c.cli('')
        helpers.log("********* Entering cli_exec_walk ----> string: %s, file name: %s" % (string, file_name))
        if string == '':
            cli_string = '?'
        else:
            cli_string = string + ' ?'
        c.send(cli_string, no_cr=True)
        c.expect(r'[\r\n\x07][\w-]+[#>] ')
        content = c.cli_content()
        temp = helpers.strip_cli_output(content)
        temp = helpers.str_to_list(temp)
        helpers.log("********new_content:************\n%s" % helpers.prettify(temp))
        c.send(helpers.ctrl('u'))
        c.expect()
        c.cli('')

        string_c = string

        if file_name:
            helpers.log("opening file: %s" % file_name)
            fo = open(file_name, 'a')
            lines = []
            lines.append((padding + string))
            lines.append((padding + '----------'))
            for line in temp:
                lines.append((padding + line))
            lines.append((padding + '=================='))
            content = '\n'.join(lines)
            fo.write(str(content))
            fo.write("\n")

            fo.close()

        num = len(temp)
        padding = "   " + padding
        
        # Loop through commands and sub-commands
        for line in temp:
            string = string_c
            helpers.log(" line is - %s" % line)
            line = line.lstrip()
            keys = line.split(' ')
            key = keys.pop(0)
            helpers.log("*** key is - %s" % key)
            helpers.log("*** string is - %s" % string)
            helpers.log("*** stringc is - %s" % string_c)
        
            # Ignoring lines which do not contain actual commands
            if re.match(r'For', line) or line == "Commands:":
                helpers.log("Ignoring line - %s" % line)
                num = num - 1
                continue
            
            # Ignoring commands which are either disruptive or are only one level commands
            # These commands would have already been displayed with corresponding help in a previous top-level hierarchy
            if key == "reauth" or key == "echo" or key == "help" or key == "logout" or key == "ping" or key == "watch":
                helpers.log("Ignore line %s" % line)
                num = num - 1
                continue
            
            # Ignoring sub-commands under 'clear debug' and 'show debug'
            if key == "ApplicationManager" or key == "Controller" or key == "EndpointManager" or key == "FabricManager" or key == "com.bigswitch.floodlight.bvs.application" or key == "ForwardingDebugCounters" or key == "ISyncService" or key =="StatsCollector" or key == "VirtualRoutingManager" or key == "org.projectfloodlight.core" or key == "StatsCollector":
                helpers.log("Ignore line %s" % line)
                num = num - 1
                continue
            
            # Ignoring sub-commands under 'debug'
            if key == "bash" or key == "cassandra-cli" or key == "cli" or key == "cli-backtrace" or key == "cli-batch" or key == "description" or key == "netconfig" or key == "python" or key == "rest":
                helpers.log("Ignore line %s" % line)
                num = num - 1
                continue
            
            # Ignoring options that require user input or comments in <>
            if re.match(r'^<.+', line) and not re.match(r'^<cr>', line):
                helpers.log("Ignoring line - %s" % line)
                num = num - 1
                continue
            
            # Ignoring some sub-commands that may impact test run
            if ((key =='<cr>' and (re.match(r' set length term', string))) or re.match(r' show debug counters', string) or re.match(r' show debug events details', string)):
                helpers.log("Ignoring line - %s" % string)
                num = num - 1
                continue
            
            # skip 'show session' (PR BSC-5233)    
            if (re.match(r' show session', string)):
                helpers.log("Ignoring line - %s" % string)
                num = num - 1
                continue
            
            # for interface related commands, only iterate through "all" and one specific interface
            if (re.match(r' show(.*)interface(.*)', string)):
                if key != 'leaf0a-eth1' and key != 'all':
                    helpers.log("Ignoring line - %s" % string)
                    num = num - 1
                    continue
            
            # for switch related commands, only iterate through "all" and one specific switch    
            if (re.match(r' show(.*)switch(.*)', string)):
                if key != 'leaf0a' and key != 'all':
                    helpers.log("Ignoring line - %s" % string)
                    num = num - 1
                    continue
                
            # for tenant related commands, only iterate through "all" and one specific tenant
            if (re.match(r' show(.*)tenant(.*)', string)):
                if key != 'A' and key != 'all':
                    helpers.log("Ignoring line - %s" % string)
                    num = num - 1
                    continue
            
            # for vns related commands, only iterate through "all" and one specific vns
            if (re.match(r' show(.*)vns(.*)', string)):
                if key != 'A1' and key != 'all':
                    helpers.log("Ignoring line - %s" % string)
                    num = num - 1
                    continue
            
            # skip 'show logging', 'show lacp interface', 'show stats interface-history interface', 'show stats interface-history switch' and 'show running-config' - no need to iterate through options   
            if (re.match(r' show lacp interface', string)) or (re.match(r' show logging', string)) or (re.match(r' show stats interface-history interface', string)) or (re.match(r' show stats interface-history switch', string)):
                helpers.log("Ignoring line - %s" % string)
                num = num - 1
                continue

            # issue the <cr> to test that the command actually works
            if key == '<cr>':
                
                if re.match(r'.*boot.*', string) or re.match(r'.*compare.*', string) or re.match(r'.*configure.*', string) or re.match(r'.*copy.*', string) or re.match(r'.*delete.*', string) or re.match(r'.*enable.*', string) or re.match(r'.*end.*', string) or re.match(r'.*exit.*', string) or re.match(r'.*failover.*', string) or re.match(r'.*logout.*', string):
                    num = num - 1
                    continue
                                
                if re.match(r'.* show router .*', string) or re.match(r'.* no .*', string) or re.match(r'.*ping.*', string) or re.match(r'.*reauth.*', string) or re.match(r'.*set .*', string) or re.match(r'.*show logging.*', string) or re.match(r'.*system.*', string) or re.match(r'.*test.*', string) or re.match(r'.*upgrade.*', string) or re.match(r'.*watch.*', string):
                    num = num - 1
                    continue
                
                helpers.log(" complete CLI show command: ******%s******" % string)
                c.cli(string)
                
                if num == 1:
                    helpers.log("AT END: ******%s******" % string)
                    return string
            
            # If command has sub-commands, call the function again to walk through sub-command options
            else:
                string = string + ' ' + key
                helpers.log("key - %s" % (key))
                helpers.log("string - %s" % (string))
                
                helpers.log("***** Call the cli walk again with  --- %s" % string)
                self.cli_walk_exec(string, file_name, padding)  
        
    def cli_walk_enable(self, string='', file_name=None, padding=''):
        t = test.Test()
        c = t.controller('main')
        c.enable('')
        helpers.log("********* Entering CLI show  walk with ----> string: %s, file name: %s" % (string, file_name))
        if string == '':
            cli_string = '?'
        else:
            cli_string = string + ' ?'
        c.send(cli_string, no_cr=True)
        c.expect(r'[\r\n\x07][\w-]+[#>] ')
        content = c.cli_content()
        temp = helpers.strip_cli_output(content)
        temp = helpers.str_to_list(temp)
        helpers.log("******new_content:\n%s" % helpers.prettify(temp))
        c.send(helpers.ctrl('u'))
        c.expect()

        string_c = string
        helpers.log("string for this level is: %s" % string_c)
        helpers.log("The length of string: %d" % len(temp))

        if file_name:
            helpers.log("opening file: %s" % file_name)
            fo = open(file_name, 'a')
            lines = []
            lines.append((padding + string))
            lines.append((padding + '----------'))
            for line in temp:
                lines.append((padding + line))
            lines.append((padding + '=================='))
            content = '\n'.join(lines)
            fo.write(str(content))
            fo.write("\n")

            fo.close()

        num = len(temp)
        padding = "   " + padding
        for line in temp:
            string = string_c
            helpers.log(" line is - %s" % line)
            line = line.lstrip()
            keys = line.split(' ')
            key = keys.pop(0)
            helpers.log("*** string is - %s" % string)
            helpers.log("*** key is - %s" % key)
            if re.match(r'All', line):
                helpers.log("Don't need to loop through exec commands- %s" % line)
                continue
            
            if re.match(r'For', line) or line == "Commands:":
                helpers.log("Ignoring line - %s" % line)
                num = num - 1
                continue
            
            if re.match(r'^<.+', line) and not re.match(r'^<cr>', line):
                helpers.log("Ignoring line - %s" % line)
                num = num - 1
                continue
            
            # Ignoring sub-commands under 'clear debug' and 'show debug'
            if key == "ApplicationManager" or key == "ControllerCounters" or key == "EndpointManager" or key == "FabricManager" or key == "com.bigswitch.floodlight.bvs.application" or key == "ForwardingDebugCounters" or key == "ISyncService" or key == "OFSwitchManager" or key == "RoleManager" or key =="StatsCollector" or key == "VirtualRoutingManager" or key == "org.projectfloodlight.core" or key == "StatsCollector":
                helpers.log("Ignore line %s" % line)
                num = num - 1
                continue
           
            # Ignoring sub-commands under 'debug'
            if key == "bash" or key == "cassandra-cli" or key == "cli" or key == "cli-backtrace" or key == "cli-batch" or key == "description" or key == "netconfig" or key == "python" or key == "rest":
                helpers.log("Ignore line %s" % line)
                num = num - 1
                continue            
            
            # Ignoring commands which are either disruptive or are only one level commands
            # These commands would have already been displayed with corresponding help in a previous top-level hierarchy
            if key == "reauth" or key == "echo" or key == "help" or key == "logout" or key == "ping" or key == "watch":
                helpers.log("Ignore line %s" % line)
                num = num - 1
                continue
                        
            # for interface related commands, only iterate through "all" and one specific interface
            if (re.match(r' show(.*)interface(.*)', string)) or (re.match(r' clear(.*)interface-counter(.*)interface', string)):
                if key != 'leaf0a-eth1' and key != 'all':
                    helpers.log("Ignoring line - %s" % string)
                    num = num - 1
                    continue
            
            # for switch related commands, only iterate through "all" and one specific switch    
            if (re.match(r' show(.*)switch(.*)', string)) or (re.match(r' clear(.*)interface-counter(.*)switch', string)):
                if key != 'leaf0a' and key != 'all':
                    helpers.log("Ignoring line - %s" % string)
                    num = num - 1
                    continue
                
            # for tenant related commands, only iterate through "all" and one specific tenant
            if (re.match(r' show(.*)tenant(.*)', string)) or (re.match(r' clear(.*)vns-counter(.*)tenant(.*)', string)):
                if key != 'A' and key != 'all':
                    helpers.log("Ignoring line - %s" % string)
                    num = num - 1
                    continue
            
            # for vns related commands, only iterate through "all" and one specific vns
            if (re.match(r' show(.*)vns(.*)', string)) or (re.match(r' clear(.*)vns-counter(.*)vns(.*)', string)):
                if key != 'A1' and key != 'all':
                    helpers.log("Ignoring line - %s" % string)
                    num = num - 1
                    continue
                
            # Ignoring some sub-commands that may impact test run or require user input
            if ((key =='<cr>' and (re.match(r' set length term', string))) or re.match(r' test path', string) or re.match(r' show debug counters', string) or re.match(r' show debug events details', string)):
                helpers.log("Ignoring line - %s" % string)
                num = num - 1
                continue
            
            # for vns related commands, only iterate through "all" and one specific vns
            if (re.match(r' system reboot', string)) or (re.match(r' system shutdown', string)):
                helpers.log("Ignoring line - %s" % string)
                num = num - 1
                continue            
            
            # skip 'show session' (PR BSC-5233)    
            if (re.match(r' show session', string)):
                helpers.log("Ignoring line - %s" % string)
                num = num - 1
                continue
            
            # for interface related commands, only iterate through "all" and one specific interface
            if (re.match(r' show(.*)interface(.*)', string)):
                if key != 'leaf0a-eth1' and key != 'all':
                    helpers.log("Ignoring line - %s" % string)
                    num = num - 1
                    continue
            
            # for switch related commands, only iterate through "all" and one specific switch    
            if (re.match(r' show(.*)switch(.*)', string)):
                if key != 'leaf0a' and key != 'all':
                    helpers.log("Ignoring line - %s" % string)
                    num = num - 1
                    continue
                
            # for tenant related commands, only iterate through "all" and one specific tenant
            if (re.match(r' show(.*)tenant(.*)', string)):
                if key != 'A' and key != 'all':
                    helpers.log("Ignoring line - %s" % string)
                    num = num - 1
                    continue
            
            # for vns related commands, only iterate through "all" and one specific vns
            if (re.match(r' show(.*)vns(.*)', string)):
                if key != 'A1' and key != 'all':
                    helpers.log("Ignoring line - %s" % string)
                    num = num - 1
                    continue
            
            # skip 'show logging', 'show lacp interface', 'show stats interface-history interface', 'show stats interface-history switch' - no need to iterate through options   
            if (re.match(r' show lacp interface', string)) or (re.match(r' show logging', string)) or (re.match(r' show stats interface-history interface', string)) or (re.match(r' show stats interface-history switch', string)):
                helpers.log("Ignoring line - %s" % string)
                num = num - 1
                continue                                          

            if key == '<cr>':

                if re.match(r'.*boot.*', string) or re.match(r'.*compare.*', string) or re.match(r'.*configure.*', string) or re.match(r'.*copy.*', string) or re.match(r'.*delete.*', string) or re.match(r'.*enable.*', string) or re.match(r'.*end.*', string) or re.match(r'.*exit.*', string) or re.match(r'.*failover.*', string) or re.match(r'.*logout.*', string):
                    num = num - 1
                    continue
                                
                if re.match(r'.* show router .*', string) or re.match(r'.* no .*', string) or re.match(r'.*ping.*', string) or re.match(r'.*reauth.*', string) or re.match(r'.*set .*', string) or re.match(r'.*show logging.*', string) or re.match(r'.*system.*', string) or re.match(r'.*test.*', string) or re.match(r'.*upgrade.*', string) or re.match(r'.*watch.*', string):
                    num = num - 1
                    continue
                
                helpers.log(" complete CLI show command: ******%s******" % string)
                c.enable(string)
                
                if num == 1:
                    return string
            else:
                string = string + ' ' + key
                helpers.log("key - %s" % (key))
                helpers.log("***** Call the cli walk again with  --- %s" % string)
                self.cli_walk_enable(string, file_name, padding)
                
    def cli_walk_config(self, string='', file_name=None, padding='', config_submode = False, exec_mode_done = False):
        t = test.Test()
        c = t.controller('main')
        c.config('')
        helpers.log("********* Entering CLI show  walk with ----> string: %s, file name: %s" % (string, file_name))
        if string == '':
            cli_string = '?'
        else:
            cli_string = string + ' ?'
        c.send(cli_string, no_cr=True)

        prompt_re = r'[\r\n\x07]?[\w\x07-]+\(([\w\x07-]+)\)(\x07)?[#>]'
        c.expect(prompt_re)
        content = c.cli_content()
        helpers.log("********** CONTENT ************\n%s" % content)

        # Content is a multiline string. Convert it to a list of strings. Then
        # get the last entry which should be the prompt.
        prompt_str1 = helpers.str_to_list(content)[-1]

        # helpers.log("Prompt1: '%s'" % prompt_str1)

        match = re.match(prompt_re, prompt_str1)
        if match:
            prompt1 = match.group(1)
        else:
            helpers.log("No match")

        temp = helpers.strip_cli_output(content)
        temp = helpers.str_to_list(temp)
        helpers.log("******new_content:\n%s" % helpers.prettify(temp))
        c.send(helpers.ctrl('u'))
        c.expect()
        c.config('')
        string_c = string
        helpers.log("string for this level is: %s" % string_c)
        helpers.log("The length of string: %d" % len(temp))

        if file_name:
            helpers.log("opening file: %s" % file_name)
            fo = open(file_name, 'a')
            lines = []
            lines.append((padding + string))
            lines.append((padding + '----------'))
            for line in temp:
                lines.append((padding + line))
            lines.append((padding + '=================='))
            content = '\n'.join(lines)
            fo.write(str(content))
            fo.write("\n")

            fo.close()

        num = len(temp)
        padding = "   " + padding
        for line in temp:
            string = string_c
            helpers.log(" NUM IS - %s" % num)
            helpers.log(" line is - %s" % line)
            line = line.lstrip()
            helpers.log(" line: %s" % line)
            keys = line.split(' ')
            key = keys.pop(0)
            helpers.log("*** string is - %s" % string)
            helpers.log("*** key is - %s" % key)

            # If done iterating over enable commands, set exec_mode_done = True
            if re.match(r'.*Commands:.*', line):
                    helpers.log("Done with enable mode commands")
                    exec_mode_done = True
                    num = num - 1
                    continue
                
            # Don't iterate over enable commands again if looping through this via a subconfig mode
            if config_submode and not exec_mode_done:
                helpers.log("Ignoring EXEC MODE command - %s" % line)
                continue
            else:
                
                if re.match(r'For', line):
                    helpers.log("Ignoring line - %s" % line)
                    num = num - 1
                    continue              
                            
                if re.match(r'^<.+', line) and not re.match(r'^<cr>', line):
                    helpers.log("Ignoring line - %s" % line)
                    num = num - 1
                    continue
                if key == "no" or key == "debug" or key == "reauth" or key == "echo" or key == "help" or key == "history" or key == "logout" or key == "ping" or key == "watch":
                    helpers.log("Ignore line %s" % line)
                    num = num - 1
                    continue
                if re.match(r'.*session.*', string) and key == "session" :
                    helpers.log("Ignore line - %s" % string)
                    num = num - 1
                    continue
                if re.match(r'.*session.*', string) and key != "<cr>" :
                    helpers.log("Ignore line - string %s, key %s" % (string, key))
                    num = num - 1
                    continue
                if re.match(r'.*password.*', string) and key == "<cr>" :
                    helpers.log("Ignore line - %s" % string)
                    num = num - 1
                    continue
                if re.match(r'.*core-switch.*', string) and key == "<cr>" :
                    helpers.log("Ignore line due to bug BSC-4903 - %s" % string)
                    num = num - 1
                    continue
                
                
                # for interface related commands, only iterate through "all" and one specific interface
                if (re.match(r' (.*)interface(.*)', string)):
                    if key != 'leaf0a-eth1' and key != 'all' and key != '<cr>':
                        helpers.log("Ignoring line - %s" % string)
                        num = num - 1
                        continue
                
                # for switch related commands, only iterate through "all" and one specific switch    
                if (re.match(r' (.*)switch(.*)', string)):
                    if key != 'leaf0a' and key != 'all' and key != '<cr>':
                        helpers.log("Ignoring line - %s" % string)
                        num = num - 1
                        continue
                    
                # for tenant related commands, only iterate through "all" and one specific tenant
                if (re.match(r' (.*)tenant(.*)', string)):
                    if key != 'A' and key != 'all' and key != '<cr>':
                        helpers.log("Ignoring line - %s" % string)
                        num = num - 1
                        continue
                
                # for vns related commands, only iterate through "all" and one specific vns
                if (re.match(r' (.*)vns(.*)', string)):
                    if key != 'A1' and key != 'all' and key != '<cr>':
                        helpers.log("Ignoring line - %s" % string)
                        num = num - 1
                        continue  
                    
                # for lag related commands, only iterate through "any_leaf"
                if (re.match(r' (.*)lag(.*)', string)):
                    if key != 'any_leaf' and key != '<cr>':
                        helpers.log("Ignoring line - %s" % string)
                        num = num - 1
                        continue                            
                
                if re.match(r'.*shutdown.*', string) and re.match(r'.*controller.*', key):
                    helpers.log("Ignore line  - %s %s" % (string, key))
                    num = num - 1
                    continue
    
    
                if re.match(r'.*internal.*', key):
                    helpers.log("Ignore line  - %s" % string)
                    num = num - 1
                    continue
    
                if re.match(r'All', line):
                    helpers.log("Don't need to loop through exec commands- %s" % line)
                    num = num - 1
                    continue                             
    
                if key == '<cr>':
                    
                    if re.match(r'.*boot.*', string) or re.match(r'.*compare.*', string) or re.match(r'.*copy.*', string) or re.match(r'.*delete.*', string) or re.match(r'.*enable.*', string) or re.match(r'.*end.*', string) or re.match(r'.*exit.*', string) or re.match(r'.*failover.*', string) or re.match(r'.*logout.*', string):
                        num = num - 1
                        continue
                                
                    if re.match(r'.* show router .*', string) or re.match(r'.* no .*', string) or re.match(r'.*ping.*', string) or re.match(r'.*reauth.*', string) or re.match(r'.*set .*', string) or re.match(r'.*show logging.*', string) or re.match(r'.*system.*', string) or re.match(r'.*test.*', string) or re.match(r'.*upgrade.*', string) or re.match(r'.*watch.*', string):
                        num = num - 1
                        continue
                                    
                    helpers.log(" complete CLI show command: ******%s******" % string)
                    c.config(string)
    
                    prompt_re = r'[\r\n\x07]?[\w-]+\(([\w-]+)\)[#>]'
                    content = c.cli_content()
    
                    helpers.log("********** CONTENT ************\n%s" % content)
    
                    # Content is a multiline string. Convert it to a list of strings. Then
                    # get the last entry which should be the prompt.
                    prompt_str2 = helpers.str_to_list(content)[-1]
    
                    match = re.match(prompt_re, prompt_str2)
                    if match:
                        prompt2 = match.group(1)
                    else:
                        helpers.log("No match")
    
                    helpers.log("Prompt1: '%s'" % prompt_str1)
                    helpers.log("Prompt2: '%s'" % prompt_str2)
    
    
                    #Compare prompts.  
                    if prompt1 != prompt2:
                        newstring = ''
                        helpers.log("***** Call the cli walk again with  --- %s" % string)
                        
                        #If different, it means that we entered a new config submode.  Call the function again but set config_submode flag to True
                        self.cli_walk_config(newstring, file_name, padding, config_submode = True, exec_mode_done = False)

                    if num == 1:
                        return string
                else:
                    string = string + ' ' + key
                    helpers.log("***** Call the cli walk again with  --- %s" % string)
                    self.cli_walk_config(string, file_name, padding)
    
