import autobot.helpers as helpers
import autobot.test as test

class T5Platform(object):

    def __init__(self):
        t = test.Test()
        c = t.controller()
        
        url = '%s/api/v1/auth/login' % c.base_url
        result = c.rest.post(url, {"user":"admin", "password":"adminadmin"})
        session_cookie = result['content']['session_cookie']
        c.rest.set_session_cookie(session_cookie)
    
    def rest_configure_ntp(self, ntp_server):
        '''Configure the ntp server
        
            Input:
                    ntp_server        NTP server IP address
                                       
            Returns: True if policy configuration is successful, false otherwise  
        '''
        t = test.Test()
        c = t.controller()
                        
        url = '%s/api/v1/data/controller//action/time/ntp'      
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
        
        url = '%s/api/v1/data/controller//action/time/ntp/status ' % (c.base_url)       
        c.rest.get(url)
        
        return True