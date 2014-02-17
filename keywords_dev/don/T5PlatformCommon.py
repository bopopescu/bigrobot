import autobot.helpers as helpers
import autobot.test as test
from time import sleep

switchDict_b4 = {}
switchDict_after = {}
fabricLink_b4 = []
fabricLink_after = []
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
            helpers.warn("Warning: Number of switches are different between Before & After")
            warningCount += 1

        for switch in switchDict_b4:
            if switchDict_after[switch] != switchDict_b4[switch]:
                helpers.warn("Warning: Switch status for switch %s has changed from: %s to %s " \
                        %(switch, switchDict_b4[switch], switchDict_after[switch]))
                warningCount += 1

        return warningCount


    def verify_fabric_link(self):
        
        t = test.Test()
        c = t.controller("master")
        url = "/api/v1/data/controller/applications/bvs/info/fabric?select=link"
        result = c.rest.get(url)['content']
        fabricLink = []
        try:
            for i in range(0, len(result[0]['link'])):
                src_switch  = result[0]['link'][i]['src']['interface']['name']
                dst_switch  = result[0]['link'][i]['dst']['interface']['name']
                key = "%s-%s" % (src_switch, dst_switch)
                fabricLink.append(key)
        except(KeyError):
            helpers.warn("Warning: No fabric links are detected in the fabric")
            
        return fabricLink
        
    
    def compare_fabric_link_status(self, fabricLink_b4, fabricLink_after):
        ''' Compare fabric link status from one list to the links on the other list
        
            Returns: If the status is different increase Warningcount & return
        '''
        global warningCount
        
        if(helpers.list_compare(fabricLink_b4, fabricLink_after)):
            helpers.log("Fabric Links are intact between states")
            return warningCount
        else:
            if(len(fabricLink_b4) > len(fabricLink_after)):
                for fabricLink in fabricLink_b4:
                    if fabricLink not in fabricLink_after:
                        helpers.warn("Fabric Link: %s is not present after the state change" % fabricLink)
                        warningCount += 1
            else:
                for fabricLink in fabricLink_after:
                    if fabricLink not in fabricLink_after:
                        helpers.warn("New fabric link: %s is present after the state change" % fabricLink)
                        warningCount += 1
        
        return warningCount
    
    
    def verify_endpoints(self):
        t = test.Test()
        c = t.controller("master")
        url = "/api/v1/data/controller/applications/bvs/info/endpoint-manager/endpoints"
        result = c.rest.get(url)['content']
        endpoints = []
        try:
            for i in range(0, len(result)):
                mac = result[i]['mac']
                tenant = result[i]['tenant-name']
                vns = result[i]['vns-name']
                try:
                    ip = result[i]['ip-address']
                    key = "%s-%s-%s-%s" % (mac,ip,tenant,vns)
                except(KeyError):
                    key = "%s-%s-%s" % (mac,tenant,vns)
                
                endpoints.append(key)
                
        except(KeyError):
            helpers.warn("No endpoints are detected in the fabric", 1)
            
        helpers.log("endpoint list is: %s " % endpoints)
        return endpoints
    
    
    def compare_endpoints(self, endpoints_b4, endpoints_after):
        ''' Compare endpoint status from one list to the endpoints in the other list
        '''
        global warningCount
        
        if(helpers.list_compare(endpoints_b4, endpoints_after)):
            helpers.log("Endpoints are intact between states")
            return warningCount
        else:
            if (len(endpoints_b4) > len(endpoints_after)):
                for endpoint in endpoints_b4:
                    if endpoint not in endpoints_after:
                        helpers.warn("Endpoint: %s is not present after the state change" % endpoint)
                        warningCount += 1
            else:
                for endpoint in endpoints_after:
                    if endpoint not in endpoints_b4:
                        helpers.warn("New endpoint: %s present after the state change" % endpoint)
                        warningCount += 1
           
    
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
        global fabricLink_b4
        global fabricLink_after
        global warningCount
        

        # Switch connectivity verification
        if (state == "before"):
            switchDict_b4 = self.verify_switch_connectivity()
            fabricLink_b4 = self.verify_fabric_link()

        else:
            switchDict_after = self.verify_switch_connectivity()
            warningCount = self.compare_switch_status(switchDict_b4, switchDict_after)
            fabricLink_after = self.verify_fabric_link()
            warningCount = self.compare_fabric_link_status(fabricLink_b4, fabricLink_after)

        if(warningCount == 0): 
            if(state == "after"):
                helpers.log("Switch status are intact after the operation")
            return True
        else: 
            return False








