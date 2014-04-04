import autobot.helpers as helpers
import autobot.test as test
from T5Utilities import T5Utilities as utilities
from time import sleep
import re
import keywords.Mininet as mininet
import keywords.T5 as T5
import keywords.Host as Host
import keywords.BsnCommon as BsnCommon


pingFailureCount = 0
leafSwitchList = []

class T5Platform(object):

    def __init__(self):
        pass    
    
    def rest_verify_show_cluster(self):
        '''Using the 'show cluster' command verify the cluster formation across both nodes
	   Also check for the formation integrity
	'''
        try:
            t = test.Test()
            c1 = t.controller("c1")
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
        slave = t.controller("slave")
        master = t.controller("master")

        masterID,slaveID = self.getNodeID()
        if(masterID == -1 and slaveID == -1):
            return False

        helpers.log("Current slave ID is : %s / Current master ID is: %s" % (slaveID, masterID))

        url = '/api/v1/data/controller/cluster/config/new-election'

        if(rigged):
            slave.rest.post(url, {"rigged": True})
        else:
            slave.rest.post(url, {"rigged": False})
        
        sleep(30)

        newMasterID = self.getNodeID(False)
        if(newMasterID == -1):
            return False

        if(masterID == newMasterID):
            if(rigged):
                helpers.test_failure("Fail: Master didn't change after executing take-leader")
                return False
            else:
                helpers.log("Pass: Leader election re-run successful - Leader %s  is intact " % (masterID))
                return True
        else:
            helpers.log("Pass: Take-Leader successful - Leader changed from %s to %s" % (masterID, newMasterID))
            return True


    def rest_verify_cluster_election_take_leader(self):
        ''' Invoke "cluster election take-leader" command and verify the controller state
        '''
        obj = utilities()
        utilities.fabric_integrity_checker(obj,"before")
        returnVal = self._cluster_election(True)
        if(not returnVal):
            return False
        sleep(30)
        return utilities.fabric_integrity_checker(obj, "after")
    
    
    def cli_cluster_take_leader(self):
        ''' Function to trigger failover to slave controller via CLI
        Input: None
        Output: True if successful, False otherwise
        '''
        t = test.Test()
        c = t.controller('slave')

        helpers.log("Failover")
        try:
            c.config("config")
            c.send("reauth")
            c.expect(r"Password:")
            c.config("adminadmin")
            c.send("failover")
            c.expect(r"Election may cause role transition: enter \"yes\" \(or \"y\"\) to continue:")
            c.config("yes")
        except:
            helpers.test_log(c.cli_content())
            return False
        else:
            return True


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
        

    def cluster_node_reboot(self, masterNode=True):

        ''' Reboot a node and verify the cluster leadership.
            Reboot Master in dual node setup: masterNode == True
        '''
        t = test.Test()
        master = t.controller("master")
        obj = utilities()
        if (utilities.cli_get_num_nodes(obj) == 1):
            singleNode = True
        else:
            singleNode = False
            

        if(singleNode):
            masterID = self.getNodeID(False)
        else:
            masterID,slaveID = self.getNodeID()
        
        if(singleNode):
            if (masterID == -1):
                return False
        else:
            if(masterID == -1 and slaveID == -1):
                return False
        
        try:
            if(masterNode):
                ipAddr = master.ip()
                master.enable("system reboot", prompt="Confirm \(yes to continue\)")
                master.enable("yes")
                helpers.log("Master is rebooting")
                sleep(90)
            else:
                slave = t.controller("slave")
                ipAddr = slave.ip()
                slave.enable("system reboot", prompt="Confirm \(yes to continue\)")
                slave.enable("yes")
                helpers.log("Slave is rebooting")
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
            newMasterID = self.getNodeID(False)
        else:
            newMasterID, newSlaveID = self.getNodeID()
            
        if(singleNode):
            if (newMasterID == -1):
                return False
        else:
            if(newMasterID == -1 and newSlaveID == -1):
                return False


        if(singleNode):
            if(masterID == newMasterID):
                helpers.log("Pass: After the reboot cluster is stable - Master is still : %s " % (newMasterID))
                return True
            else:
                helpers.log("Fail: Reboot Failed. Cluster is not stable.  Before the reboot Master is: %s  \n \
                    After the reboot Master is: %s " %(masterID, newMasterID))
        else:
            if(masterNode):
                if(masterID == newSlaveID and slaveID == newMasterID):
                    helpers.log("Pass: After the reboot cluster is stable - Master is : %s / Slave is: %s" % (newMasterID, newSlaveID))
                    return True
                else:
                    helpers.log("Fail: Reboot Failed. Cluster is not stable. Before the master reboot Master is: %s / Slave is : %s \n \
                            After the reboot Master is: %s / Slave is : %s " %(masterID, slaveID, newMasterID, newSlaveID))
                    return False
            else:
                if(masterID == newMasterID and slaveID == newSlaveID):
                    helpers.log("Pass: After the reboot cluster is stable - Master is : %s / Slave is: %s" % (newMasterID, newSlaveID))
                    return True
                else:
                    helpers.log("Fail: Reboot Failed. Cluster is not stable. Before the slave reboot Master is: %s / Slave is : %s \n \
                            After the reboot Master is: %s / Slave is : %s " %(masterID, slaveID, newMasterID, newSlaveID))
                    return False


    def _cluster_node_shutdown(self, masterNode=True):
        ''' Shutdown the node
        '''
        t = test.Test()
        master = t.controller("master")
        obj = utilities()

        masterID,slaveID = self.getNodeID()
        if(masterID == -1 and slaveID == -1):
            return False

        if(masterNode):
            master.enable("shutdown", prompt="Confirm Shutdown \(yes to continue\)")
            master.enable("yes")
            helpers.log("Master is shutting down")
            sleep(10)
        else:
            slave = t.controller("slave")
            slave.enable("shutdown", prompt="Confirm Shutdown \(yes to continue\)")
            slave.enable("yes")
            helpers.log("Slave is shutting down")
            sleep(10)

        newMasterID = self.getNodeID(False)
        if(newMasterID == -1):
            return False

        if(masterNode):
            if(slaveID == newMasterID):
                helpers.log("Pass: After the shutdown cluster is stable - New master is : %s " % (newMasterID))
                return True
            else:
                helpers.log("Fail: Shutdown Failed. Cluster is not stable. Before the master node shutdown Master is: %s / Slave is : %s \n \
                        After the shutdown Master is: %s " %(masterID, slaveID, newMasterID))
                return False
        else:
            if(masterID == newMasterID):
                helpers.log("Pass: After the slave shutdown cluster is stable - Master is still: %s " % (newMasterID))
                return True
            else:
                helpers.log("Fail: Shutdown failed. Cluster is not stable. Before the slave shutdown Master is: %s / Slave is : %s \n \
                        After the shutdown Master is: %s " %(masterID, slaveID, newMasterID))
                return False


    def cli_verify_cluster_master_reboot(self):
        obj = utilities()
        utilities.fabric_integrity_checker(obj,"before")
        returnVal = self.cluster_node_reboot()
        if(not returnVal):
            return False
        return utilities.fabric_integrity_checker(obj,"after")

    def cli_verify_cluster_slave_reboot(self):
        obj = utilities()
        utilities.fabric_integrity_checker(obj,"before")
        returnVal = self.cluster_node_reboot(False)
        if(not returnVal):
            return False
        return utilities.fabric_integrity_checker(obj,"after")

    def cli_verify_cluster_master_shutdown(self):
        obj = utilities()
        utilities.fabric_integrity_checker(obj,"before")
        returnVal = self._cluster_node_shutdown()
        if(not returnVal):
            return False
        return utilities.fabric_integrity_checker(obj,"after")

    def cli_verify_cluster_slave_shutdown(self):
        obj = utilities()
        utilities.fabric_integrity_checker(obj,"before")
        returnVal = self._cluster_node_shutdown(False)
        if(not returnVal):
            return False
        return utilities.fabric_integrity_checker(obj,"after")

    def rest_add_user(self, numUsers=1):
        numWarn = 0
        t = test.Test()
        master = t.controller("master")
        url = "/api/v1/data/controller/core/aaa/local-user"
        usersString = []
        numErrors = 0
        for i in range (0, int(numUsers)):
            user = "user" + str(i+1)
            usersString.append(user)
            master.rest.post(url, {"user-name": user})
            sleep(1)
            
            if not master.rest.status_code_ok():
                helpers.test_failure(master.rest.error())
                numErrors += 1
            else:
                helpers.log("Successfully added user: %s " % user)

        if(numErrors > 0):
            return False
        else:
            url = "/api/v1/data/controller/core/aaa/local-user"
            result = master.rest.get(url)
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
        master = t.controller("master")
        usersString = []
        numErrors = 0
        for i in range (0, int(numUsers)):
            url = "/api/v1/data/controller/core/aaa/local-user[user-name=\""
            user = "user" + str(i+1)
            usersString.append(user)
            url = url + user + "\"]"
            master.rest.delete(url, {})
            sleep(1)
            
            if not master.rest.status_code_ok():
                helpers.test_failure(master.rest.error())
                numErrors += 1
            else:
                helpers.log("Successfully deleted user: %s " % user)

        if(numErrors > 0):
            return False
        else:
            url = "/api/v1/data/controller/core/aaa/local-user"
            result = master.rest.get(url)
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
        
        url = "/api/v1/data/controller/fabric/port-group?config=true"
        t = test.Test()
        master = t.controller("master")
        
        result = master.rest.get(url)['content']
        
        for pg in result:
            url = "/api/v1/data/controller/fabric/port-group[name=\""+ pg['name'] + "\"]"
            master.rest.delete(url, {})

             
                             
    def platform_ping(self, src, dst ):
        global pingFailureCount
        mynet = mininet.Mininet()     
        loss = mynet.mininet_ping(src, dst)
        if (loss != '0'):
            #sleep(5)
            loss = mynet.mininet_ping(src, dst)
            if (loss != '0'):
                if(pingFailureCount == 5):
                    helpers.warn("5 Consecutive Ping Failures: Issuing Mininet-BugReport")
                    #mynet.mininet_bugreport()
                    return False
                helpers.warn("Ping failed between: %s & %s" % (src,dst))
                pingFailureCount += 1
                return True
            else:
                pingFailureCount = 0
                return True
        else:
            pingFailureCount = 0
        return True
    
    
    
    def do_show_run_vns_verify(self, vnsName, numMembers):
        t = test.Test()
        master = t.controller("master")
        url = "/api/v1/data/controller/applications/bvs/tenant?config=true"
        result = master.rest.get(url)
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




    def getNodeID(self, slaveNode=True):
        
        '''         
        Description:
        -    This function will handout the NodeID's for master & slave nodes 
        
        Objective:
        -    This is designed to be resilient to node failures in HA environments. Eg: If the node is not
            reachable or it's powered down this function will handle the logic
            
        Inputs:
        |    boolean: slaveNode  |  Whether secondary node is available in the system. Default is True
        
        Outputs:
        |    If slaveNode: return (masterID, slaveID)
        |    else:    return (masterID)

        
        ''' 
        numTries = 0
        t = test.Test()
        master = t.controller("master")
    
         
        while(True):
            try:
                showUrl = '/api/v1/data/controller/cluster'
                helpers.log("Master is : %s " % master.name)
                result = master.rest.get(showUrl)['content']
                masterID = result[0]['status']['local-node-id']
                break 
            except(KeyError):
                if(numTries < 5):
                    helpers.log("Warning: KeyError detected during master ID retrieval. Sleeping for 10 seconds")
                    sleep(10)
                    numTries += 1
                else:
                    helpers.log("Error: KeyError detected during master ID retrieval")
                    if slaveNode:
                        return (-1, -1)
                    else:
                        return -1

        if(slaveNode):
            slave = t.controller("slave")
            while(True):
                try:
                    showUrl = '/api/v1/data/controller/cluster'
                    result = slave.rest.get(showUrl)['content']
                    slaveID = result[0]['status']['local-node-id']
                    break 
                except(KeyError):
                    if(numTries < 5):
                        helpers.log("Warning: KeyError detected during slave ID retrieval. Sleeping for 10 seconds")
                        sleep(10)
                        numTries += 1
                    else:
                        helpers.log("Error: KeyError detected during slave ID retrieval")
                        return (-1,-1)


        if(slaveNode):
            return (masterID, slaveID)
        else:
            return masterID
        
        
        
    def rest_configure_virtual_ip(self, vip):
        ''' Function to configure Virtual IP of the cluster via REST
        Input: VIP address
        Output: True if successful, False otherwise
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
        ''' Function to delete Virtual IP from a controller via REST
        Input: None
        Output: True if successful, False otherwise
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
 
        
        
    def cli_configure_virtual_ip(self, vip):
        ''' Function to show Virtual IP of a controller via CLI
        Input: None
        Output: VIP address if configured, None otherwise
        '''
        t = test.Test()
        c = t.controller('master')

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
        c = None
        try:
            if 'master' in vip:
                c = t.controller('master')
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
        c = t.controller('master')
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


    def bash_verify_virtual_ip(self, vip, node='master'):
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
        c = t.controller('master')

        helpers.test_log("Deleting virtual IP address")
        try:
            c.config("cluster")
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
            if 'master' in vip:
                c = t.controller('master')
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
        c = t.controller('master')

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
        master = t.controller("master")
        url = "/api/v1/data/controller/fabric/monitor-session[id=" + sessionID+"]"
        
        master.rest.put(url, {"id": sessionID})
                
        url = "/api/v1/data/controller/fabric/monitor-session[id=" + sessionID + "]/source[switch-name=\"" +srcSwitch +"\"][interface-name=\"" + srcInt+ "\"]"
        result = master.rest.put(url, {"direction": kwargs.get("direction"), "switch-name": srcSwitch , "interface-name": srcInt})

        url = "/api/v1/data/controller/fabric/monitor-session[id=" + sessionID + "]/destination[switch-name=\"" +dstSwitch +"\"][interface-name=\"" + dstInt+ "\"]"
        result = master.rest.put(url, {"switch-name": srcSwitch , "interface-name": dstInt})
        
        if master.rest.status_code_ok():
            return True
        else:
            return False
        
    
    def rest_delete_monitor_session(self, sessionID):
        
        t = test.Test()
        master = t.controller("master") 
        url = "/api/v1/data/controller/fabric/monitor-session[id=" + sessionID+"]"
        
        master.rest.delete(url, {"id": sessionID})
        
        if master.rest.status_code_ok():
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
        master = t.controller("master")
        
        foundSession = False
        url = "/api/v1/data/controller/fabric/monitor-session?config=true"
        result = master.rest.get(url)['content']
        
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




    def cli_compare(self, src, dst, node='master', scp_passwd='adminadmin'):
        ''' Generic function to compare via CLI, using SCP
        Input:
        Src, Dst - source and destination of compare command
        Scp_Password - password for scp connection
        Node - pointing to Master or Slave controller
        Output: True if successful, False otherwise
         '''
        helpers.test_log("Running command:\ncompare %s %s" % (src, dst))
        t = test.Test()
        c = t.controller(node)
        c.config("config")
        c.send("compare %s %s" % (src, dst))
        options = c.expect([r'[Pp]assword: ', r'\(yes/no\)\?', c.get_prompt()])
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
                c.expect(r'[Pp]assword:')
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


    def cli_copy(self, src, dst, node='master', scp_passwd='adminadmin'):
        ''' Generic function to copy via CLI, using SCP
        Input:
        Src, Dst - source and destination of copy command
        Scp_Password - password for scp connection
        Node - pointing to Master or Slave controller
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
                if not (helpers.any_match(c.cli_content(), r'100%') or helpers.any_match(c.cli_content(), r'applied \d. updates') or helpers.any_match(c.cli_content(), r'Lines Applied')):
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
        c = t.controller('master')
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
        c = t.controller('master')
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
            rc = rc[5:]
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
        c = t.controller('master')
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
        c = t.controller('master')
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

    def copy_pkg_from_jenkins(self,node='master', check=True):
        ''' 
          copy the latest upgrade package from Jenkin
          Author: Mingtao
          input:  node  - controller to copy the image, 
                          master, slave, c1 c2
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
            string = 'copy "scp://bsn@jenkins:/var/lib/jenkins/jobs/bvs master/lastSuccessful/archive/target/appliance/images/bvs/controller-upgrade-bvs-2.0.5-SNAPSHOT.pkg"'
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
    
    def copy_pkg_from_server(self,src,node='master',passwd='bsn',soft_error=False):
        ''' 
          copy the a upgrade package from server
          Author: Mingtao
          input:  node  - controller to copy the image, 
                          master, slave, c1 c2
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
 

    def cli_check_image(self,node='master',soft_error=False):
        ''' 
          check image available in the system "show image"
          Author: Mingtao
          input:  node  - controller  
                          master, slave, c1 c2
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


    def cli_delete_image(self,node='master',image=None):
        ''' 
          delete image  in system             
          Author: Mingtao
          input:  node  - controller  
                          master, slave, c1 c2
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


    def cli_upgrade_stage(self, node='master', image=None):
        ''' 
          upgrade stage  -  1 step of upgrade         
          Author: Mingtao
          input:  node  - controller 
                          master, slave, c1 c2
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



    def cli_upgrade_launch(self,node='master'):
        ''' 
          upgrade launch  -  2 step of upgrade         
          Author: Mingtao
          input:  node  - controller  
                          master, slave, c1 c2
                  
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
    
    
    
    def cli_take_snapshot(self,node='master', run_config=None,fabric_switch=None,filepath=None):
        ''' 
          take snapshot of the system, can only take snapshot one by one  
          Author: Mingtao
          input:  node  - controller  
                          master, slave, c1 c2
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
            config = temp[5:]
            content = '\n'.join(config)
            helpers.log("********config :************\n%s" % content)                 
            return  content
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
        c = t.controller('master')
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
 

    def cli_get_num_nodes(self):
        '''  
          return the number of nodes in the system  
          Author: Mingtao
          input:                                        
          usage:   
          output:   1  or 2 
        '''
        t = test.Test()
        c = t.controller('master')
        helpers.log('INFO: Entering ==> rest_get_node_role ')
        
        c.cli('show cluster' )
        content = c.cli_content()
        temp = helpers.strip_cli_output(content)
        temp = helpers.str_to_list(temp)
        num = 0
        for line in temp:          
            helpers.log("INFO: line is - %s" % line)
            match= re.match(r'.*(active|stand-by).*', line)
            if match:
                helpers.log("INFO: role is: %s" % match.group(1))  
                num = num+1                                      
            else:
                helpers.log("INFO: not for controller  %s" % line)  
        helpers.log("INFO: there are %d of controllers in the cluster" % num)   
        return num    

    def cli_whoami(self):
        '''  
          run cli whoami  
          Author: Mingtao
          input:                                        
          usage:   
          output:   username and group        
        '''
        t = test.Test()
        c = t.controller('master')
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
        c = t.controller('master')
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
          cli add user to the system, can only run at master
          Author: Mingtao
          input:   user = username,  passwd  = password                                       
          usage:   
          output:   True                            
        '''
  
        t = test.Test()
        c = t.controller('master')
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
          cli add user to group, can only run at master
          Author: Mingtao
          input:   group  - if group not give, will user admin
                  user    - if user not given, will add all uers                             
          usage:   
          output:   True                            
        '''  
        t = test.Test()
        c = t.controller('master')
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
          get the group for a user, can only run at master
          Author: Mingtao
          input:   
                  user    - if user not given, will add all uers                             
          usage:   
          output:   group                          
        '''
        t = test.Test()
        c = t.controller('master')
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
          delete users can only run at master
          Author: Mingtao
          input:  user                        
          usage:   
          output:   True                            
           
        '''
  
        t = test.Test()
        c = t.controller('master')
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
        c = t.controller('master')
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



    
