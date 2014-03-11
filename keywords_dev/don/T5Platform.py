import autobot.helpers as helpers
import autobot.test as test
from T5Utilities import T5Utilities as utilities
from time import sleep
import keywords.Mininet as mininet
import keywords.T5Fabric as T5Fabric

pingFailureCount = 0
leafSwitchList = []

class T5Platform(object):

    def __init__(self):
        pass    
    


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
        

    def _cluster_node_reboot(self, masterNode=True):

        ''' Reboot the node
        '''
        t = test.Test()
        master = t.controller("master")

        masterID,slaveID = self.getNodeID()
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
       
        newMasterID, newSlaveID = self.getNodeID()
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




    def rest_add_monitor_session(self, sessionID):

        t = test.Test()
        master = t.controller("master")
        url = "/api/v1/data/controller/fabric/monitor-session[id=" + sessionID+"]"
        
        master.rest.put(url, {"id": sessionID})
        
        url = "/api/v1/data/controller/fabric/monitor-session?config=true"
        
        result = master.rest.get(url)['content']
        try:
            for session in result:
                if (str(session['id']) == sessionID):
                    return True
        except(KeyError):
            return False
        
        return False
















   