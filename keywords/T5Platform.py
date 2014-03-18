import autobot.helpers as helpers
import autobot.test as test
from T5Utilities import T5Utilities as utilities
from time import sleep
import keywords.Mininet as mininet
import keywords.T5 as T5

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
                master.enable("reboot", prompt="Confirm Reboot \(yes to continue\)")
                master.enable("yes")
                helpers.log("Master is rebooting")
                sleep(90)
            else:
                slave = t.controller("slave")
                slave.enable("reboot", prompt="Confirm Reboot \(yes to continue\)")
                slave.enable("yes")
                helpers.log("Slave is rebooting")
                sleep(90)
        except:
            helpers.log("Node is rebooting")
            sleep(90)
       
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
        |    If slaveNode: return (masterID, slaveID
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
                    return (-1, -1)

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
        try:
            if 'master' in vip:
                c = t.controller('master')
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


    def bash_verify_virtual_ip(self, vip):
        ''' Function to show Virtual IP of a controller via CLI/Bash
        Input: None
        Output: VIP address if configured, None otherwise
        '''
        t = test.Test()
        c = t.controller('master')
        try:
            content = c.bash('ip addr')['content']
            output = helpers.strip_cli_output(content)
            if vip not in output:
                helpers.test_log("VIP: %s not in the master" % vip)
                return False
        except:
            helpers.test_log(c.cli_content())
            return False
        else:
            helpers.log("VIP: %s is present in the master" % vip)
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
        try:
            if 'master' in vip:
                c = t.controller('master')
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
        c = t.controller('master')
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
