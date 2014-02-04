import autobot.helpers as helpers
import autobot.test as test
from time import sleep

switchDict_b4 = {}
switchDict_after = {}
warningCount = 0

class T5PlatformCommon(object):

    def __init__(self):
        pass
    
    def verify_switch_connectivity(self):

        ''' Using the "show switch" command verify switches are connected to the 
            fabric.

            Returns: dictionary of switches:is_connected , eg: {switch1:true, switch2:true}
        '''
        t = test.Test()
        c = t.controller("master")
        url = "/api/v1/data/controller/core/switch"
        result =  c.rest.get(url)['content']
        switchDict = {}
        i = 0
        while i<len(result):
            dpid = result[i]['dpid']
            switchDict[dpid] = result[i]['connected']
            i += 1

        return switchDict
    

    def compare_switch_status(self, switchDict_b4, switchDict_after):
        ''' Compare switch status from one dict to the status on the other dict
            
            Returns: If the status is differnt increase WarningCount and return
        '''
        global warningCount
        helpers.log("Before is : %s " % switchDict_b4)
        helpers.log("After is: %s " % switchDict_after)
        
        if(len(switchDict_b4) != len(switchDict_after)):
            helpers.log("Warning: Number of switches are different between Before & After")
            warningCount += 1

        for switch in switchDict_b4:
            if switchDict_after[switch] != switchDict_b4[switch]:
                helpers.log("Warning: Switch status for switch %s has changed from: %s to %s " \
                        %(switch, switchDict_b4[switch], switchDict_after[switch]))
                warningCount += 1

        return warningCount

    
    def getNodeID(self, slaveNode=True):
        ''' This function will handout the NodeID's for master & slave nodes '''
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


    def fabric_integrity_checker(self, state):
        ''' Wrapper function to go through different integrity checks of the fabric. 
        '''
        global switchDict_b4
        global switchDict_after
        global warningCount

        # Switch connectivity verification
        if (state == "before"):
            switchDict_b4 = self.verify_switch_connectivity()

        else:
            switchDict_after = self.verify_switch_connectivity()
            warningCount = self.compare_switch_status(switchDict_b4, switchDict_after)

        if(warningCount == 0): 
            if(state == "after"):
                helpers.log("Switch status are intact after the operation")
            return True
        else: 
            return False








