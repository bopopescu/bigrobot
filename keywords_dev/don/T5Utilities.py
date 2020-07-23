import autobot.helpers as helpers
import autobot.test as test
import keywords.Mininet as mininet
from time import sleep

'''
    ::::::::::    README    ::::::::::::::
    
    This T5Utilities file is used to abstract the T5 utility 
    functions. Please include any utility functions that are not
    specific to your test suites here.
    
'''


''' Global variables to save the state
    Used by: fabric_integrity_checker 
'''
switchDict_b4 = {}
switchDict_after = {}
fabricLinks_b4 = []
fabricLinks_after = []
endpoints_b4 = []
endpoints_after = []
fabricLags_b4 = []
fabricLags_after = []
warningCount = 0


class T5Utilities(object):

    def __init__(self):
        pass


    def fabric_integrity_checker(self, state):
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
            
        Description :
        -    Checks for the fabric state differences on following component: Switch Connectivity / Fabric Links / Fabric Lags / Endpoints

        Inputs:
        |    state= "before" or "after"
        
        Outputs:
        |    Warning Messages along with return True
        
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
            switchDict_b4 = self._gather_switch_connectivity()
            fabricLinks_b4 = self._gather_fabric_links()
            endpoints_b4 = self._gather_endpoints()
            fabricLags_b4 = self._gather_fabric_lags()

        else:
            switchDict_after = self._gather_switch_connectivity()
            warningCount = self._compare_switch_status(switchDict_b4, switchDict_after)
            fabricLinks_after = self._gather_fabric_links()
            warningCount = self._compare_fabric_elements(fabricLinks_b4, fabricLinks_after, "FabricLinks")
            endpoints_after = self._gather_endpoints()
            warningCount = self._compare_fabric_elements(endpoints_b4, endpoints_after, "FabricEndpoints")
            fabricLags_after = self._gather_fabric_lags()
            warningCount = self._compare_fabric_elements(fabricLags_b4, fabricLags_after, "FabricLags")

        if(warningCount == 0): 
            if(state == "after"):
                helpers.log("Switch status is intact after the state change operation")
            return True
        else: 
            #helpers.warn("-------  Switch Status Is Not Intact. Please Collect Logs. Sleeping for 10 Hours   ------")
            #sleep(36000)
            return True

        
        
        
    def _gather_switch_connectivity(self):
        ''' 
        -    This is a helper function. This function is used by "fabric_integrity_checker"
        
        Description:
        -    Using the "show switch" command verify switches are connected to the fabric

        '''
        t = test.Test()
        c = t.controller("main")
        url = "/api/v1/data/controller/core/switch"
        result =  c.rest.get(url)['content']
        switchDict = {}
        i = 0
        while i<len(result):
            dpid = result[i]['dpid']
            switchDict[dpid] = result[i]['connected']
            i += 1

        return switchDict
    

    def _compare_switch_status(self, switchDict_b4, switchDict_after):
        ''' 
        -    This is a helper function. This function is used by "fabric_integrity_checker"
        
        Description:
        -    Using the "show switch" command verify switches are connected to the fabric

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


    def _gather_fabric_links(self):
        ''' 
        -    This is a helper function. This function is used by "fabric_integrity_checker"
        
        Description:
        -    Using the "show fabric link" command verify fabric links in the fabric
        
        '''
        t = test.Test()
        c = t.controller("main")
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
        
    
    def _gather_endpoints(self):
        ''' 
        -    This is a helper function. This function is used by "fabric_integrity_checker"
        
        Description:
        -    Using the "show endpoints" command verify endpoints in the fabric
    
        '''
        t = test.Test()
        c = t.controller("main")
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
    
           
    def _gather_fabric_lags(self):
        ''' 
        -    This is a helper function. This function is used by "fabric_integrity_checker"
        
        Description:
        -    Using the "show fabric lags" command verify fabric lags in the fabric
        
        '''
        t = test.Test()
        c = t.controller("main")
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
    
    
    def _compare_fabric_elements(self, list_b4, list_after, fabricElement):
        ''' 
        -    This is a helper function. This function is used by "fabric_integrity_checker"
    
        Description:
            Compare fabric element status from one list to the elements in the other list
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
           
    


      
            



