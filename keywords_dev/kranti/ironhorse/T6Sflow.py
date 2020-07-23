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
         
    def rest_add_sflow_collector(self, ip, tenant, segment):
        '''
        To configure sflow counter interval in seconds 
        '''
        t = test.Test()
        c = t.controller('main')
        url1 = '/api/v1/data/controller/applications/bcf/sflow/collector[ip-address="%s"]' % (ip)
        
        try:
            c.rest.put(url1, {"segment": segment, "ip-address": ip, "tenant": tenant})    
        except:
            return False
        else:
            return True
    
    def rest_delete_sflow_collector(self, ip):
        '''
        To configure sflow counter interval in seconds 
        '''
        t = test.Test()
        c = t.controller('main')
        url1 = '/api/v1/data/controller/applications/bcf/sflow/collector[ip-address="%s"]'  % (ip)
        
        try:
            c.rest.delete(url1, {})
            
        except:
            return False
        else:
            return True
    
    def rest_add_sflow_counterint(self, counterint):
        '''
        To configure sflow counter interval in seconds 
        '''
        t = test.Test()
        c = t.controller('main')
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
        c = t.controller('main')
        url = '/api/v1/data/controller/applications/bcf/sflow'
        try:
            c.rest.patch(url, {"max-header-size": headersize})
        except:
            return False
        else:
            return True
                

    def rest_add_sflow_samplerate(self, samplerate):
        '''
        To configure sflow header size in Bytes 
        '''
        t = test.Test()
        c = t.controller('main')
        url = '/api/v1/data/controller/applications/bcf/sflow'
        try:
            c.rest.patch(url, {"sample-rate": samplerate})
        except:
            return False
        else:
            return True                
                  

    def rest_get_sflow_collectorinfo(self, switch):
        '''
        To get the sflow collector info from controller for a given switch 
        '''
        t = test.Test()
        c = t.controller('main')
        url = '/api/v1/data/controller/applications/bcf/info/forwarding/network/switch[switch-name="%s"]/sflow-collector-table' % (switch)
        try:
            c.rest.get(url)
            data = c.rest.content()
            
        except:
            return False
        else:
            return True
   
    def rest_get_sflow_samplerinfo(self, switch):
        '''
        To get the sflow sampler info from controller for a given switch 
        '''
        t = test.Test()
        c = t.controller('main')
        url = '/api/v1/data/controller/applications/bcf/info/forwarding/network/switch[switch-name="%s"]/sflow-sampler-table' % (switch)
        try:
            c.rest.get(url)
            data = c.rest.content()
            
        except:
            return False
        else:
            return True   
        
   
                    