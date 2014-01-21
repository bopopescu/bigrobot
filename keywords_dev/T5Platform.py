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
    
    
    def rest_verify_ha_cluster(self):
        '''Using the 'show cluster' command verify the cluster formation across both nodes
	   Also check for the formation integrity
	'''
        try:
            t = test.Test()
            master = t.controller("master")
            slave = t.controller("slave")
            url = '/api/v1/data/controller/cluster'
            
            result = master.rest.get(url)['content']
            reported_active_byMaster = result[0]['status']['domain-leader']['leader-id']
            
            result = slave.rest.get(url)['content']
            reported_active_bySlave = result[0]['status']['domain-leader']['leader-id']
            
            if(reported_active_byMaster != reported_active_bySlave):
                helpers.log("Both controllers %s & %s are declaring themselves as active" \
                        % (reported_active_byMaster, reported_active_bySlave))
                helpers.test_failure("Error: Inconsistent active/stand-By cluster formation detected")
                return False
            else:
                helpers.log("Active controller id is: %s " % reported_active_byMaster)
                helpers.log("Pass: Consistent active/stand-By cluster formation verified")
                return True
            
        except Exception, err:
            helpers.test_failure("Exception in: rest_verify_ha_cluster %s : %s " % (Exception, err))
            return False


