import time
import autobot.helpers as helpers
import autobot.test as test

class T5Platform(object):

    def __init__(self):
	pass
   
    def rest_configure_ntp(self, ntp_server):
        '''Configure the ntp server
        
            Input:
                    ntp_server        NTP server IP address
                                       
            Returns: True if policy configuration is successful, false otherwise  
        '''
        t = test.Test()
        c = t.controller()
                        
        url = '/api/v1/data/controller/action/time/ntp'      
        c.rest.put(url, {"ntp-server": ntp_server})
        
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
            return False

        return True

    def rest_show_ntp_servers(self):
        '''Return the list of NTP servers      
                    
            Returns: Output of 'ntpq -pn' which lists configured NTP servers and their status
        '''
        t = test.Test()
        c = t.controller()
        
        url = '/api/v1/data/controller/action/time/ntp/status '
        c.rest.get(url)
        
        return True
    
    
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



    def rest_cluster_election(self, rigged):
        ''' Invoke "cluster election" commands: re-run or take-leader
            If: "rigged" is true then verify the active controller change.
            Else: execute the election rerun
        '''
        t = test.Test()
        slave = t.controller("slave")
        master = t.controller("master")

        showUrl = '/api/v1/data/controller/cluster'
        result = master.rest.get(showUrl)['content']
        masterID = result[0]['status']['local-node-id']
        result = slave.rest.get(showUrl)['content']
        slaveID = result[0]['status']['local-node-id']

        helpers.log("Current slave ID is : %s / Current master ID is: %s" % (slaveID, masterID))

        url = '/api/v1/data/controller/cluster/config/new-election'

        if(rigged):
            slave.rest.post(url, {"rigged": True})
        else:
            slave.rest.post(url, {"rigged": False})
        
        time.sleep(10)
        newMaster = t.controller("master")
        result = newMaster.rest.get(showUrl)['content'] 
        newMasterID = result[0]['status']['domain-leader']['leader-id']

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

    def rest_cluster_election_take_leader(self):
        ''' Invoke "cluster election take-leader" command and verify the controller state
        '''
        self.rest_cluster_election(True)

    def rest_cluster_election_rerun(self):
        ''' Invoke "cluster election re-run" command and verify the controller state
        '''
        self.rest_cluster_election(False)


    def rest_cluster_master_reboot(self):
        ''' Reboot the cluster master
        '''
        t = test.Test()
        master = t.controller("master")
        slave = t.controller("slave")
       
        showUrl = '/api/v1/data/controller/cluster'
        result = master.rest.get(showUrl)['content']
        masterID = result[0]['status']['local-node-id']
        result = slave.rest.get(showUrl)['content']
        slaveID = result[0]['status']['local-node-id']
        
        url = "/api/v1/data/controller/os/action/power"
        master.rest.post(url, {"action": "reboot"})
 
        time.sleep(15)
 
        master = t.controller("master")
        showUrl = '/api/v1/data/controller/cluster'
        result = master.rest.get(showUrl)['content']
        newMasterID = result[0]['status']['local-node-id']
 
        slave = t.controller("slave")
        showUrl = '/api/v1/data/controller/cluster'
        result = slave.rest.get(showUrl)['content']
        newSlaveID = result[0]['status']['local-node-id']
 
        if(masterID == newSlaveID and slaveID == newMasterID):
            helpers.log("Pass: After the reboot cluster is stable - Master is : %s / Slave is: %s" % (newMasterID, newSlaveID))
            return True
        else:
            helper.log("Fail: Reboot Failed. Cluster is not stable. Before the reboot Master is: %s / Slave is : %s \n \
                    After the reboot Master is: %s / Slave is : %s " %(masterID, slaveID, newMasterID, newSlaveID))
            return False
 
 





 









