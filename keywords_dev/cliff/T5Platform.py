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
    
    def rest_add_ntp_server(self, ntp_server):
        '''Configure the ntp server
        
            Input:
                    ntp_server        NTP server IP address
                                       
            Returns: True if policy configuration is successful, false otherwise  
        '''
        t = test.Test()
        c = t.controller()
                        
        url = '/api/v1/data/controller/os/config/global/time-config'  
        c.rest.put(url, {"ntp-servers": [ntp_server]})
        
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
            return False

        return True
    
    def rest_add_ntp_timezone(self, ntp_timezone):
        '''Configure the ntp timezone
        
            Input:
                    ntp_server        NTP server IP address
                                       
            Returns: True if policy configuration is successful, false otherwise  
        '''
        t = test.Test()
        c = t.controller()
                        
        url = '/api/v1/data/controller/os/config/global/time-config'  
        c.rest.put(url, {"time-zone": ntp_timezone})
        
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
            return False

        return True
    
    def rest_delete_ntp_server(self, ntp_server):
        '''Delete the ntp server
        
            Input:
                    ntp_server        NTP server IP address
                                       
            Returns: True if policy configuration is successful, false otherwise  
        '''
        t = test.Test()
        c = t.controller()
                        
        url = '/api/v1/data/controller/os/config/global/time-config'  
        c.rest.delete(url, {"ntp-servers": [ntp_server]})
        
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
            return False

        return True
    
    def rest_delete_ntp_timezone(self, ntp_timezone):
        '''Delete the ntp timezone
        
            Input:
                    ntp_server        NTP server IP address
                                       
            Returns: True if policy configuration is successful, false otherwise  
        '''
        t = test.Test()
        c = t.controller()
                        
        url = '/api/v1/data/controller/os/config/global/time-config'  
        c.rest.delete(url, {"time-zone": ntp_timezone})
        
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
        
        url = '%s/api/v1/data/controller/os/action/time/ntp ' % (c.base_url)     
        c.rest.get(url)
        
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
            return False
        
        return c.rest.content()
    
    