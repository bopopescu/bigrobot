import autobot.helpers as helpers
import autobot.test as test

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
        helpers.log("B4 is : %s " % switchDict_b4)
        helpers.log("After is: %s " % switchDict_after)
        for switch in switchDict_b4:
            if switchDict_after[switch] != switchDict_b4[switch]:
                helpers.log("Warning: Switch status for switch %s has changed from: %s to %s " \
                        %(switch, switchDict_b4[switch], switchDict_after[switch]))
                warningCount += 1

        return warningCount

    def integrity_checker(self, state):
        ''' Wrapper function to go through different integrity checks of the fabric. 
        '''
        global switchDict_b4
        global switchDict_after
        global warningCount

        # Switch connectivity verification
        if (state == "beforeHA"):
            switchDict_b4 = self.verify_switch_connectivity()

        else:
            switchDict_after = self.verify_switch_connectivity()
            warningCount = self.compare_switch_status(switchDict_b4, switchDict_after)

        if(warningCount == 0): 
            helpers.log("Switch status are intact after the take-leader")
            return True
        else: 
            return False








