import autobot.helpers as helpers
import autobot.test as test
import keywords.T5 as T5
import keywords.T6 as T6
import string
import telnetlib
import re


class  T6Sflow(object):
    
    
    def __init__(self):
        pass
     
    def rest_add_sflow_counterint(self, counterint):
        '''
        To configure sflow counter interval in seconds 
        '''
        t = test.Test()
        c = t.controller('master')
        url = '/api/v1/data/controller/applications/bcf/sflow'
        try:
            c.rest.patch(url, {"counter-interval": counterint})
        except:
            return False
        else:
            return True
     
    def rest_add_sflow_headersize(self, headersize):
        '''
        To configure sflow header size in Bytes 
        '''
        t = test.Test()
        c = t.controller('master')
        url = '/api/v1/data/controller/applications/bcf/sflow'
        try:
            c.rest.patch(url, {"max-header-size": headersize})
        except:
            return False
        else:
            return True
                
                
                  
                