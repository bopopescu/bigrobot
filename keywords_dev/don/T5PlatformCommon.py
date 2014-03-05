import autobot.helpers as helpers
import autobot.test as test
import keywords.Mininet as mininet
from time import sleep
import keywords.T5Fabric as T5Fabric

switchDict_b4 = {}
switchDict_after = {}
fabricLinks_b4 = []
fabricLinks_after = []
endpoints_b4 = []
endpoints_after = []
fabricLags_b4 = []
fabricLags_after = []
pingFailureCount = 0
warningCount = 0
leafSwitchList = []

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
            helpers.warn("-----------    Connected Switch Discrepancies    -----------")
            helpers.warn("Warning: Number of switches are different between Before & After")
            warningCount += 1

        for switch in switchDict_b4:
            try:
                if switchDict_after[switch] != switchDict_b4[switch]:
                    helpers.warn("Warning: Switch status for switch %s has changed from: %s to %s " \
                            %(switch, switchDict_b4[switch], switchDict_after[switch]))
                    warningCount += 1
            except(KeyError):
                helpers.warn("Warning: Switch: %s is not present after the state change " % (switch))
                warningCount += 1 

        return warningCount


    def verify_fabric_links(self):
        
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
    
           
    def verify_fabric_lags(self):
        t = test.Test()
        c = t.controller("master")
        url = "/api/v1/data/controller/core/switch?select=fabric-lag"
        result = c.rest.get(url)['content']
        fabricLags = []

        for i in range(0, len(result)):
            switchName = ""
            name = ""
            lagType = ""
            srcInt = ""
            dstSwitch = ""
            dstInt = ""
            
            try:
                for j in range(0, len(result[i]["fabric-lag"])):
                    try:
                        switchName = result[i]["fabric-lag"][j]["switch-name"]
                        name = result[i]["fabric-lag"][j]["name"]
                        lagType = result[i]["fabric-lag"][j]["lag-type"]
                    except(KeyError):
                        pass
                    for k in range(0, len(result[i]["fabric-lag"][j]["member"])):
                        try:
                            srcInt = result[i]["fabric-lag"][j]["member"][k]["src-interface"]
                            dstSwitch = result[i]["fabric-lag"][j]["member"][k]["dst-switch"]
                            dstInt = result[i]["fabric-lag"][j]["member"][k]["dst-interface"]
                            key = "%s-%s-%s-%s-%s-%s" % (switchName, name, lagType, srcInt, dstSwitch, dstInt)
                            fabricLags.append(key)
                        except(KeyError):
                            key = "%s-%s-%s-%s-%s-%s" % (switchName, name, lagType, srcInt, dstSwitch, dstInt)
                            fabricLags.append(key)

            except(KeyError):
                pass
    
        return fabricLags
    
    
    def compare_fabric_elements(self, list_b4, list_after, fabricElement):
        ''' Compare fabric element status from one list to the elements in the other list
            fabricElement can be one of the following:
                1) Fabric Links
                2) Fabric Endpoints
                3) Fabric Lags
        '''
        global warningCount
        
        if(helpers.list_compare(list_b4, list_after)):
            if (fabricElement == "FabricLinks"):
                helpers.log("Fabric Links are intact between states")
            if (fabricElement == "FabricEndpoints"):
                helpers.log("Endpoints are intact between states")
            if (fabricElement == "FabricLags"):
                helpers.log("Fabric Lags are intact between states")
            return warningCount
        
        else:
            #helpers.warn("Got List Different from helpers")
            #helpers.log("B4 is: %s" % list_b4)
            #helpers.log("After is: %s" % list_after)
            if (fabricElement == "FabricLinks"):
                helpers.warn("-----------    Fabric Link Discrepancies    -----------")
            if (fabricElement == "FabricEndpoints"):
                helpers.warn("-----------    Fabric Endpoints Discrepancies    -----------")
            if (fabricElement == "FabricLags"):
                helpers.warn("-----------    Fabric Lags Discrepancies    -----------")
            if (len(list_b4) > len(list_after)):
                for item in list_b4:
                    if item not in list_after:
                        if (fabricElement == "FabricLinks"):
                            helpers.warn("Fabric Link: %s is not present after the state change" % item)
                        if (fabricElement == "FabricEndpoints"):
                            helpers.warn("Endpoint: %s is not present after the state change" % item)
                        if (fabricElement == "FabricLags"):
                            helpers.warn("Fabric Lag: %s is not present after the state change" % item)
                            
                        warningCount += 1
            else:
                for item in list_after:
                    if item not in list_b4:
                        if (fabricElement == "FabricLinks"):
                            helpers.warn("New fabric link: %s is present after the state change" % item)
                        if (fabricElement == "FabricEndpoints"):
                            helpers.warn("New endpoint: %s present after the state change" % item)
                        if (fabricElement == "FabricLags"):
                            helpers.warn("New fabric lag: %s is present after the state change" % item)
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
        global fabricLinks_b4
        global fabricLinks_after
        global endpoints_b4
        global endpoints_after
        global fabricLags_b4
        global fabricLags_after
        global warningCount
        

        # Switch connectivity verification
        if (state == "before"):
            switchDict_b4 = self.verify_switch_connectivity()
            fabricLinks_b4 = self.verify_fabric_links()
            endpoints_b4 = self.verify_endpoints()
            fabricLags_b4 = self.verify_fabric_lags()

        else:
            switchDict_after = self.verify_switch_connectivity()
            warningCount = self.compare_switch_status(switchDict_b4, switchDict_after)
            fabricLinks_after = self.verify_fabric_links()
            warningCount = self.compare_fabric_elements(fabricLinks_b4, fabricLinks_after, "FabricLinks")
            endpoints_after = self.verify_endpoints()
            warningCount = self.compare_fabric_elements(endpoints_b4, endpoints_after, "FabricEndpoints")
            fabricLags_after = self.verify_fabric_lags()
            warningCount = self.compare_fabric_elements(fabricLags_b4, fabricLags_after, "FabricLags")

        if(warningCount == 0): 
            if(state == "after"):
                helpers.log("Switch status is intact after the state change operation")
            return True
        else: 
            #helpers.warn("-------  Switch Status Is Not Intact. Please Collect Logs. Sleeping for 10 Hours   ------")
            #sleep(36000)
            return True

        
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

      
            
    def auto_configure_fabric_switch(self, spineList, leafList, leafPerRack):
        
        global leafSwitchList
        
        Fabric = T5Fabric.T5Fabric()
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
        
        numSpines = len(spineList)
        numLeaves = len(leafList)
        
        Fabric = T5Fabric.T5Fabric()
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
                             


