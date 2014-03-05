import autobot.helpers as helpers
import autobot.test as test
from T5PlatformCommon import T5PlatformCommon as common
from time import sleep

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

        obj = common()
        masterID,slaveID = common.getNodeID(obj)
        if(masterID == -1 and slaveID == -1):
            return False

        helpers.log("Current slave ID is : %s / Current master ID is: %s" % (slaveID, masterID))

        url = '/api/v1/data/controller/cluster/config/new-election'

        if(rigged):
            slave.rest.post(url, {"rigged": True})
        else:
            slave.rest.post(url, {"rigged": False})
        
        sleep(30)

        obj = common()
        newMasterID = common.getNodeID(obj, False)
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
        obj = common()
        common.fabric_integrity_checker(obj,"before")
        returnVal = self._cluster_election(True)
        if(not returnVal):
            return False
        sleep(30)
        return common.fabric_integrity_checker(obj, "after")

    def rest_verify_cluster_election_rerun(self):
        ''' Invoke "cluster election re-run" command and verify the controller state
        '''
        obj = common()
        common.fabric_integrity_checker(obj, "after")
        returnVal = self._cluster_election(False)
        if(not returnVal):
            return False
        sleep(30)
        return common.fabric_integrity_checker(obj, "before")
        

    def _cluster_node_reboot(self, masterNode=True):

        ''' Reboot the node
        '''
        t = test.Test()
        master = t.controller("master")
        obj = common()

        masterID,slaveID = common.getNodeID(obj)
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
       
        newMasterID, newSlaveID = common.getNodeID(obj)
        if(newMasterID == -1 and newSlaveID == -1):
            return False

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
        obj = common()

        masterID,slaveID = common.getNodeID(obj)
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

        newMasterID = common.getNodeID(obj, False)
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
        obj = common()
        common.fabric_integrity_checker(obj,"before")
        returnVal = self._cluster_node_reboot()
        if(not returnVal):
            return False
        return common.fabric_integrity_checker(obj,"after")

    def cli_verify_cluster_slave_reboot(self):
        obj = common()
        common.fabric_integrity_checker(obj,"before")
        returnVal = self._cluster_node_reboot(False)
        if(not returnVal):
            return False
        return common.fabric_integrity_checker(obj,"after")

    def cli_verify_cluster_master_shutdown(self):
        obj = common()
        common.fabric_integrity_checker(obj,"before")
        returnVal = self._cluster_node_shutdown()
        if(not returnVal):
            return False
        return common.fabric_integrity_checker(obj,"after")

    def cli_verify_cluster_slave_shutdown(self):
        obj = common()
        common.fabric_integrity_checker(obj,"before")
        returnVal = self._cluster_node_shutdown(False)
        if(not returnVal):
            return False
        return common.fabric_integrity_checker(obj,"after")

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


    def rest_add_vip(self, vip):
        
        t = test.Test()
        master = t.controller("master")
        url = "/api/v1/data/controller/os/config/global/virtual-ip-config"
        master.rest.post(url, {"ipv4-address": vip})
        
        url = "/api/v1/data/controller/os/config/global/virtual-ip-config"
        result = master.rest.get(url)['content']
        if (result[0]['ipv4-address'] == vip):
            return True
        else:
            return False
    
    def cli_verify_cluster_vip(self, vip):
        t = test.Test()
        master = t.controller("master")
        
        content = master.bash("ip addr")['content']
        helpers.log("CLI Content is: %s " % content)
        splitContent = str(content).split(' ')
        helpers.log("splitContent is: %s" % splitContent)
        if vip not in splitContent:
            helpers.log("VIP: %s not in the master" % vip)
            return False
        else:
            helpers.log("VIP: %s is present in the master" % vip)
            return True
        
        
    def rest_delete_vip(self):
        
        t = test.Test()
        master = t.controller("master")
        url = "/api/v1/data/controller/os/config/global/virtual-ip-config"
        content = master.rest.delete(url)['content']
        
        if (content):
            helpers.log("result is: %s" % content)
            return False
        else:
            
            return True



 




