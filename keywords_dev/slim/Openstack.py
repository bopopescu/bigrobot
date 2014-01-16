import autobot.helpers as helpers
import autobot.test as test


class Openstack(object):

    def __init__(self):
        pass
    
    
    # def openstack_get_nw_id(self, osUserName, osTenantName, osPassWord, osAuthUrl, netName):
        # t = test.Test()
        # h1 = t.host('h1')
         
        # result = h1.bash("neutron --os-username %s --os-tenant-name %s --os-password %s --os-auth-url %s net-show %s" % (osUserName, osTenantName, osPassWord, osAuthUrl, netName)) 
                
        # return
    
    # def openstack_get_flavor_id(self, osUserName, osTenantName, osPassWord, osAuthUrl, flavorName):
        # t = test.Test()
        # h1 = t.host('h1')
        
        # result = h1.bash("nova --os-username %s --os-tenant-name %s --os-password %s --os-auth-url %s flavor-show %s" % (osUserName, osTenantName, osPassWord, osAuthUrl, flavorName))         
        
        # return
    
    # def openstack_get_user_id(self, osUserName, osTenantName, osPassWord, osAuthUrl, userName):
        # t = test.Test()
        # h1 = t.host('h1')
      
        # result = h1.bash("keystone --os-username %s --os-tenant-name %s --os-password %s --os-auth-url %s user-get %s" % (osUserName, osTenantName, osPassWord, osAuthUrl, userName))              
        # return
    
    # def openstack_get_role_id(self, osUserName, osTenantName, osPassWord, osAuthUrl, roleName):
        # t = test.Test()
        # h1 = t.host('h1')
      
        # result = h1.bash("keystone --os-username %s --os-tenant-name %s --os-password %s --os-auth-url %s role-get %s" % (osUserName, osTenantName, osPassWord, osAuthUrl, roleName))              
        # return
    
    # def openstack_set_user_role(self, osUserName, osTenantName, osPassWord, osAuthUrl, userName, roleName, tenantName):
        # t = test.Test()
        # h1 = t.host('h1')
      
        # result = h1.bash("keystone --os-username %s --os-tenant-name %s --os-password %s --os-auth-url %s user-role-add --user %s --role --tenant %s" % (osUserName, osTenantName, osPassWord, osAuthUrl, userName, roleName, tenantName))              
        # return
        
    
    # def openstack_get_tenant_id(self, osUserName, osTenantName, osPassWord, osAuthUrl,):
        # t = test.Test()
        # h1 = t.host('h1')
                
        # return
    
    # def openstack_get_vm_id(self, osUserName, osTenantName, osPassWord, osAuthUrl,):
        # t = test.Test()
        # h1 = t.host('h1')
                
        # return
    
    # def openstack_get_router_id(self, osUserName, osTenantName, osPassWord, osAuthUrl,):
        # t = test.Test()
        # h1 = t.host('h1')
                
        # return
    
    # def openstack_get_net_id(self, osUserName, osTenantName, osPassWord, osAuthUrl,):
        # t = test.Test()
        # h1 = t.host('h1')
                
        # return
    
    # def openstack_get_subnet_id(self, osUserName, osTenantName, osPassWord, osAuthUrl,):
        # t = test.Test()
        # h1 = t.host('h1')
                
        # return
    
    def openstack_get_image_id(self, osUserName, osTenantName, osPassWord, osAuthUrl, imageName):
        t = test.Test()
        h1 = t.host('h1')
    
#        result = h1.bash("nova --os-username %s --os-tenant-name %s  --os-password %s --os-auth-url %s image-show %s | grep -i id" % (osUserName, osTenantName, osPassWord, osAuthUrl, imageName))
#        a = result.split("|")
#        return a[1]
        result = h1.bash("nova --os-username %s --os-tenant-name %s --os-password %s --os-auth-url %s image-show %s" % (osUserName, osTenantName, osPassWord, osAuthUrl, imageName))
        output = result["content"]
        out_dict = helpers.openstack_convert_table_to_dict(output)
        id = out_dict["id"]
        return id
        

    
    # def openstack_create_tenant(self, osUserName, osTenantName, osPassWord, osAuthUrl):
        # t = test.Test()
        # h1 = t.host('h1')
        
        # return
    
    # def openstack_create_user(self, osUserName, osTenantName, osPassWord, osAuthUrl):
        # t = test.Test()
        # h1 = t.host('h1')
        
        # return        
    
    # def openstack_create_role(self, osUserName, osTenantName, osPassWord, osAuthUrl, roleName):
        # t = test.Test()
        # h1 = t.host('h1')
      
        # result = h1.bash("keystone --os-username %s --os-tenant-name %s --os-password %s --os-auth-url %s role-create --name %s" % (osUserName, osTenantName, osPassWord, osAuthUrl, roleName))              
        # return
    
    # def openstack_create_flavor(self, osUserName, osTenantName, osPassWord, osAuthUrl):
        # t = test.Test()
        # h1 = t.host('h1')
        
        # return
    
    # def openstack_create_image(self, osUserName, osTenantName, osPassWord, osAuthUrl):
        # t = test.Test()
        # h1 = t.host('h1')
        
        # return
    
    # def openstack_create_router(self, osUserName, osTenantName, osPassWord, osAuthUrl):
        # t = test.Test()
        # h1 = t.host('h1')
        
        # return
        
    # def openstack_create_net(self, osUserName, osTenantName, osPassWord, osAuthUrl):
        # t = test.Test()
        # h1 = t.host('h1')
        
        # return    
        
    # def openstack_create_subnet(self, osUserName, osTenantName, osPassWord, osAuthUrl, gateway=None, networkName=None, poolStart=None, poolEnd=None, netIP, netMask):
        # t = test.Test()
        # h1 = t.host('h1')
        
        # return
    
    # def openstack_gen_keypair(self, osUserName, osTenantName, osPassWord, osAuthUrl):
        # t = test.Test()
        # h1 = t.host('h1')
        
        # return
    
    # def openstack_set_router_gw(self, osUserName, osTenantName, osPassWord, osAuthUrl):
        # t = test.Test()
        # h1 = t.host('h1')
        
        # return
    
    # def openstack_attach_subnet_to_router(self, osUserName, osTenantName, osPassWord, osAuthUrl, routerip=None):
        # t = test.Test()
        # h1 = t.host('h1')
        
        # return
    
    # def openstack_edit_secgroup(self, osUserName, osTenantName, osPassWord, osAuthUrl):
        # t = test.Test()
        # h1 = t.host('h1')
        
        # return
    
    # def openstack_create_instance(self, osUserName, osTenantName, osPassWord, osAuthUrl):
        # t = test.Test()
        # h1 = t.host('h1')
        
        # return
    