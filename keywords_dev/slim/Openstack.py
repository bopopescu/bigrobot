import autobot.helpers as helpers
import autobot.test as test


class Openstack(object):

    def __init__(self):
        pass
    
    def openstack_get_image_id(self, osUserName, osTenantName, osPassWord, osAuthUrl, imageName):
        t = test.Test()
        h1 = t.host('h1')
    
        result = h1.bash("nova --os-username %s --os-tenant-name %s  --os-password %s --os-auth-url %s image-show %s | grep -i id" % (osUserName, osTenantName, osPassWord, osAuthUrl, imageName))
        a = result.split("|")
        return a[1]
    
#    def openstack_create_tenant(self, osUserName, osTenantName, osAuthUrl, osPassWord, tenantName):        
#        t = test.Test()
#        h1 = t.host('h1')
#        h2 = t.host('h2')
        
        
        
      