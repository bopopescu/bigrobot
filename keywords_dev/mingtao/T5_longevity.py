import autobot.helpers as helpers
import autobot.test as test
import re
import keywords.T5 as T5
import keywords.T5Platform as T5Platform 
 
class T5_longevity(object):
# This is for all the common function   - Mingtao
    def __init__(self):
        pass


################  start of commit #############
 
    def rest_add_tenant_vns_scale(self, tenantcount, vnscount):
 
        t5 = T5.T5()   
        
        for count in range(0,int(tenantcount)):
            tenant = 'T'+str(count)
            if not t5.rest_add_tenant(tenant):      
                helpers.test_failure("USER Error: tenant is NOT configed successfully")               
            if not t5.rest_add_vns_scale(tenant, vnscount):
                helpers.test_failure("USER Error: VNS is NOT configed successfully for tenant %s" % tenant)  
  
        return True
                   
          