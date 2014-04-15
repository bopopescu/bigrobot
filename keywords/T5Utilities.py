import autobot.helpers as helpers
import autobot.test as test
import re
from BsnCommon import BsnCommon as bsnCommon

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

floodlightMonitorFlag = False

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
        
    
    def _gather_endpoints(self):
        ''' 
        -    This is a helper function. This function is used by "fabric_integrity_checker"
        
        Description:
        -    Using the "show endpoints" command verify endpoints in the fabric
    
        '''
        t = test.Test()
        c = t.controller("master")
        url = "/api/v1/data/controller/applications/bvs/info/endpoint-manager/endpoint"
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
        helpers.log("Before State Change Total # of Fabric Elements: %s " % len(list_b4))
        helpers.log("Before State Change : %s " % list_b4)
        helpers.log("After State Change Total # of Fabric Elements: %s " % len(list_after))
        helpers.log("After State Change: %s " % list_after)
        
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
    
    
    
    def cli_get_num_nodes(self):
        ''' 
            Utility functions to return the number of nodes in a cluster.
            Returns:
                1 : single node cluster
                2 : HA cluster
        '''
        t = test.Test()
        c = t.controller('master')
        
        c.cli('show cluster' )
        content = c.cli_content()
        temp = helpers.strip_cli_output(content)
        temp = helpers.str_to_list(temp)
        num = 0
        for line in temp:          
            #match= re.match(r'.*(active|stand-by).*', line)
            match= re.match(r'.*(leader|follower).*', line)
            if match:
                num = num+1                                      
            else:
                helpers.log("INFO: not for controller  %s" % line)  
        helpers.log("INFO: There are %d of controller(s) in the cluster" % num)   
        return num    
           
    
    def start_floodlight_monitor(self):
        global floodlightMonitorFlag
        
        try:
            t = test.Test()
            c1 = t.controller('c1')
            c2 = t.controller('c2')
            c1_pidList = self.get_floodlight_monitor_pid('c1')
            c2_pidList = self.get_floodlight_monitor_pid('c2')
            for c1_pid in c1_pidList:
                c1.sudo('kill %s' % (c1_pid))
            for c2_pid in c2_pidList:
                c2.sudo('kill %s' % (c2_pid))
            
            # Add rm of the file if file already exist in case of a new test
            c1.sudo("tail -f /var/log/floodlight/floodlight.log | grep --line-buffered ERROR > %s &" % "c1_floodlight_dump.txt")
            c2.sudo("tail -f /var/log/floodlight/floodlight.log | grep --line-buffered ERROR > %s &" % "c2_floodlight_dump.txt")
            
            floodlightMonitorFlag = True
            return True
        
        except:
            helpers.log("Exception occured while starting the floodlight monitor")
            return False
                        
    def restart_floodlight_monitor(self, node):
        
        global floodlightMonitorFlag
        
        if(floodlightMonitorFlag):
            t = test.Test()
            c = t.controller(node)
            result = c.sudo('ls *_dump.txt')
            filename = re.split('\n', result['content'])[1:-1]
            c.sudo("tail -f /var/log/floodlight/floodlight.log | grep --line-buffered ERROR >> %s &" % filename[0].strip('\r'))
            return True
        else:
            return True
            
    
    
    def stop_floodlight_monitor(self):
        
        global floodlightMonitorFlag
        
        if(floodlightMonitorFlag):
            c1_pidList = self.get_floodlight_monitor_pid('c1')
            c2_pidList = self.get_floodlight_monitor_pid('c2')
            t = test.Test()
            c1 = t.controller('c1')
            c2 = t.controller('c2')
            helpers.log("Stopping Floodlight Monitor on C1")
            for c1_pid in c1_pidList:
                c1.sudo('kill %s' % (c1_pid))
            helpers.log("Stopping Floodlight Monitor on C2")
            for c2_pid in c2_pidList:
                c2.sudo('kill %s' % (c2_pid))
            floodlightMonitorFlag = False
            
            try:
                helpers.log("****************    Floodlight Log From C1    ****************")
                result = c1.sudo('cat c1_floodlight_dump.txt')
                split = re.split('\n', result['content'])[1:-1]
                if split:
                    helpers.warn("Floodlight Errors Were Detected At: %s " % helpers.ts_long_local())
                    
            except(AttributeError):
                helpers.log("No Errors From Floodlight Monitor on C1")
                
            try:
                helpers.log("****************    Floodlight Log From C2    ****************")
                result = c2.sudo('cat c2_floodlight_dump.txt')
                split = re.split('\n', result['content'])[1:-1]
                if split:
                    helpers.warn("Floodlight Errors Were Detected At: %s " % helpers.ts_long_local())
            except(AttributeError):
                helpers.log("No Errors From Floodlight Monitor on C2")
            
            return True
            
        else:
            helpers.log("FloodlightMonitorFlag is not set: Returning")
            
            
        
    def get_floodlight_monitor_pid(self, role):
        t = test.Test()
        c = t.controller(role)
        helpers.log("Verifing for monitor job")
        c_result = c.sudo('ps ax | grep tail | grep sudo | awk \'{print $1}\'')
        split = re.split('\n',c_result['content'])
        pidList = split[1:-1]
        return pidList
    
    

''' Following class will perform T5 platform related multithreading activities
    Instantiating this class is done by functions reside in T5Platform. 
    
    Extends threading.Thread
'''

from threading import Thread

class T5PlatformThreads(Thread):
    
    def __init__(self, threadID, name, arg):
            Thread.__init__(self)
            self.threadID = threadID
            self.name = name
            self.arg = arg
            
    def run(self):
        if(self.name == "switchReboot"):
            self.switch_reboot(self.arg)
        if(self.name == "failover"):
            self.controller_failover()
        if(self.name == "activeReboot"):
            self.controller_reboot('master')
        if(self.name == "standbyReboot"):
            self.controller_reboot('slave')
    
        
    def switch_reboot(self, switchName):
        try:
            #helpers.log("Starting Thread %s For Rebooting Switch: %s" % (self.threadID, self.arg))
            print ("Starting Thread %s For Rebooting Switch: %s" % (self.threadID, self.arg))
            t = test.Test()
            switch = t.switch(switchName)
            cli_input = 'reload now'
            switch.enable('')
            switch.send(cli_input)
            helpers.sleep(60)
            common = bsnCommon()
            if(common.verify_ssh_connection(switchName)):
                print ("Exiting Thread %s After Rebooting Switch: %s" % (self.threadID, self.arg))
                return True
            else:
                print ("Connection Failure in Thread %s After Rebooting Switch: %s" % (self.threadID, self.arg))
                return False
        except:
            helpers.test_failure("Failure during switch:%s reboot" % (switchName))
            print ("Failure during switch:%s reboot" % (switchName))
            return False
        
    def controller_failover(self):  
        from T5Platform import T5Platform
        platform = T5Platform()
        #helpers.log("Exiting Thread %s After Rebooting Switch: %s" % (self.threadID, self.arg))
        print ("Starting Thread %s For Controller Failover" % (self.threadID))    
        returnVal =  platform._cluster_election(True)
        print ("Exiting Thread %s After Controller Failover" % (self.threadID))
        return returnVal
        
    def controller_reboot(self, node):
        from T5Platform import T5Platform
        platform = T5Platform()
        print ("Starting Thread %s For Controller Reboot for Node: " % (self.threadID), node) 
        if (node=="master"):
            returnVal = platform.cluster_node_reboot()
        else:
            returnVal = platform.cluster_node_reboot(False)
        print ("Exiting Thread %s After Controller Reboot for Node: " % (self.threadID), node)
        return returnVal
    
