import autobot.helpers as helpers
import autobot.test as test


class Openstack(object):

    def __init__(self):
        pass
    
    
    def create_tenant(self, osUserName, osTenantName, osAuthUrl, osPassWord, tenantName):        
        t = test.Test()
        nova = t.nova()
        mn.cli('%s ping %s -c %s' % (src, dst, count))
      