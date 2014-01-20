import autobot.helpers as helpers
import autobot.test as test


class Openstack(object):

	def __init__(self):
		pass


	def openstack_get_nw_id(self, osUserName, osTenantName, osPassWord, osAuthUrl, networkName):
		'''Get network id
			Input:
				`osXXX`        		tenant name, password, username etc credentials
				`networkName`       network name for that particular tenant
			Return: id of network
		'''
		t = test.Test()
		h1 = t.host('h1')
		
		result = h1.bash("neutron --os-username %s --os-tenant-name %s --os-password %s --os-auth-url %s net-show %s" % (osUserName, osTenantName, osPassWord, osAuthUrl, networkName))
		output = result["content"]
		helpers.log("output: %s" % output)
		out_dict = helpers.openstack_convert_table_to_dict(output)
		result1 = out_dict["id"]
		netId = result1["value"]
		helpers.log("network %s id is: %s" % (networkName, str(netId)))   
		return netId		

	def openstack_get_flavor_id(self, osUserName, osTenantName, osPassWord, osAuthUrl, flavorName):
		'''Get flavor id
			Input:
				`osXXX`        		tenant name, password, username etc credentials
				`flavorName`       	flavor's name
			Return: id of flavor
		'''
		t = test.Test()
		h1 = t.host('h1')
		
		result = h1.bash("nova --os-username %s --os-tenant-name %s --os-password %s --os-auth-url %s flavor-show %s" % (osUserName, osTenantName, osPassWord, osAuthUrl, flavorName))         
		output = result["content"]
		helpers.log("output: %s" % output)
		out_dict = helpers.openstack_convert_table_to_dict(output)
		result1 = out_dict["id"]
		flavorId = result1["value"]
		helpers.log("flavor %s id is: %s" % (flavorName, str(flavorId)))   
		return flavorId		

	def openstack_get_user_id(self, osUserName, osTenantName, osPassWord, osAuthUrl, userName):
		'''Get user id
			Input:
				`osXXX`        		tenant name, password, username etc credentials
				`networkName`       user's name
			Return: id of user
		'''
		t = test.Test()
		h1 = t.host('h1')
		
		result = h1.bash("keystone --os-username %s --os-tenant-name %s --os-password %s --os-auth-url %s user-get %s" % (osUserName, osTenantName, osPassWord, osAuthUrl, userName))              
		output = result["content"]
		helpers.log("output: %s" % output)
		out_dict = helpers.openstack_convert_table_to_dict(output)
		result1 = out_dict["id"]
		userId = result1["value"]
		helpers.log("user %s id is: %s" % (userName, str(userId)))   
		return userId		

	def openstack_get_role_id(self, osUserName, osTenantName, osPassWord, osAuthUrl, roleName):
		'''Get role id
			Input:
				`osXXX`        		tenant name, password, username etc credentials
				`roleName`       	role's name
			Return: id of role
		'''
		
		t = test.Test()
		h1 = t.host('h1')
		
		result = h1.bash("keystone --os-username %s --os-tenant-name %s --os-password %s --os-auth-url %s role-get %s" % (osUserName, osTenantName, osPassWord, osAuthUrl, roleName))              
		output = result["content"]
		helpers.log("output: %s" % output)
		out_dict = helpers.openstack_convert_table_to_dict(output)
		result1 = out_dict["id"]
		roleId = result1["value"]
		helpers.log("role %s id is: %s" % (roleName, str(roleId))) 
		return roleId		


	def openstack_get_tenant_id(self, osUserName, osTenantName, osPassWord, osAuthUrl, tenantName):
		'''Get tenant id
			Input:
				`osXXX`        		tenant name, password, username etc credentials
				`tenantName`       	tenant's name
			Return: id of tenant
		'''
		t = test.Test()
		h1 = t.host('h1')

		result = h1.bash("keystone --os-username %s --os-tenant-name %s --os-password %s --os-auth-url %s tenant-get %s" % (osUserName, osTenantName, osPassWord, osAuthUrl, tenantName))              
		output = result["content"]
		helpers.log("output: %s" % output)
		out_dict = helpers.openstack_convert_table_to_dict(output)
		result1 = out_dict["id"]
		tenantId = result1["value"]
		helpers.log("tenant %s id is: %s" % (tenantName, str(tenantId)))   
		return tenantId		

	def openstack_get_vm_id(self, osUserName, osTenantName, osPassWord, osAuthUrl, instanceName):
		'''Get vm id
			Input:
				`osXXX`        		tenant name, password, username etc credentials
				`instanceName`      vm's name
			Return: id of vm
		'''	
		t = test.Test()
		h1 = t.host('h1')

		result = h1.bash("nova --os-username %s --os-tenant-name %s --os-password %s --os-auth-url %s show %s" % (osUserName, osTenantName, osPassWord, osAuthUrl, instanceName))              
		output = result["content"]
		helpers.log("output: %s" % output)
		out_dict = helpers.openstack_convert_table_to_dict(output)
		result1 = out_dict["id"]
		vmId = result1["value"]
		helpers.log("VM %s id is: %s" % (instanceName, str(vmId)))   
		return vmId		

	def openstack_get_vm_status(self, osUserName, osTenantName, osPassWord, osAuthUrl, instanceName):
		'''Get vm status
			Input:
				`osXXX`        		tenant name, password, username etc credentials
				`instanceName`       vm's name
			Return: vm status
		'''
		t = test.Test()
		h1 = t.host('h1')

		result = h1.bash("nova --os-username %s --os-tenant-name %s --os-password %s --os-auth-url %s show %s" % (osUserName, osTenantName, osPassWord, osAuthUrl, instanceName))              
		output = result["content"]
		helpers.log("output: %s" % output)
		out_dict = helpers.openstack_convert_table_to_dict(output)
		result1 = out_dict["status"]
		vmStatus = result1["value"]
		helpers.log("VM %s status is: %s" % (instanceName, str(vmStatus)))   
		return vmStatus		

	def openstack_get_router_id(self, osUserName, osTenantName, osPassWord, osAuthUrl, routerName):
		'''Get router id
			Input:
				`osXXX`        		tenant name, password, username etc credentials
				`routerName`       	router's name
			Return: id of router
		'''
		t = test.Test()
		h1 = t.host('h1')

		result = h1.bash("neutron --os-username %s --os-tenant-name %s --os-password %s --os-auth-url %s router-show %s" % (osUserName, osTenantName, osPassWord, osAuthUrl, routerName))              
		output = result["content"]
		helpers.log("output: %s" % output)
		out_dict = helpers.openstack_convert_table_to_dict(output)
		result1 = out_dict["id"]
		routerId = result1["value"]
		helpers.log("router %s id is: %s" % (routerName, str(routerId)))   
		return routerId		

	def openstack_get_router_status(self, osUserName, osTenantName, osPassWord, osAuthUrl, routerName):
		'''Get router status
			Input:
				`osXXX`        		tenant name, password, username etc credentials
				`routerName`       	router's name
			Return: router status
		'''	
		t = test.Test()
		h1 = t.host('h1')

		result = h1.bash("neutron --os-username %s --os-tenant-name %s --os-password %s --os-auth-url %s router-show %s" % (osUserName, osTenantName, osPassWord, osAuthUrl, routerName))              
		output = result["content"]
		helpers.log("output: %s" % output)
		out_dict = helpers.openstack_convert_table_to_dict(output)
		result1 = out_dict["status"]
		routerStatus = result1["value"]
		helpers.log("router %s status is: %s" % (routerName, str(routerStatus)))   
		return routerStatus		


	def openstack_get_subnet_id(self, osUserName, osTenantName, osPassWord, osAuthUrl, subnetName):
		'''Get subnet id
			Input:
				`osXXX`        		tenant name, password, username etc credentials
				`subnetName`       	subnet's name
			Return: id of subnet for that tenant
			NB: when creating subnet, name is optional. Must pass name during subnet creation to use this function
		'''
		t = test.Test()
		h1 = t.host('h1')

		result = h1.bash("neutron --os-username %s --os-tenant-name %s --os-password %s --os-auth-url %s router-show %s" % (osUserName, osTenantName, osPassWord, osAuthUrl, subnetName))              
		output = result["content"]
		helpers.log("output: %s" % output)
		out_dict = helpers.openstack_convert_table_to_dict(output)
		result1 = out_dict["id"]
		subnetId = result1["value"]
		helpers.log("subnet %s id is: %s" % (subnetName, str(subnetId)))   
		return subnetId		


	def openstack_get_image_id(self, osUserName, osTenantName, osPassWord, osAuthUrl, imageName):
		'''Get image id
			Input:
				`osXXX`        		tenant name, password, username etc credentials
				`imageName`       	image's name
			Return: id of image
		'''
		t = test.Test()
		h1 = t.host('h1')

		result = h1.bash("nova --os-username %s --os-tenant-name %s --os-password %s --os-auth-url %s image-show %s" % (osUserName, osTenantName, osPassWord, osAuthUrl, imageName))
		output = result["content"]
		helpers.log("output: %s" % output)
		out_dict = helpers.openstack_convert_table_to_dict(output)
		result1 = out_dict["id"]
		imageId = result1["value"]
		helpers.log("image %s id is: %s" % (imageName, str(imageId)))   
		return imageId


	def openstack_set_user_role(self, osUserName, osTenantName, osPassWord, osAuthUrl, userName, roleName, tenantName):
		t = test.Test()
		h1 = t.host('h1')
		
		h1.bash("keystone --os-username %s --os-tenant-name %s --os-password %s --os-auth-url %s user-role-add --user %s --role --tenant %s" % (osUserName, osTenantName, osPassWord, osAuthUrl, userName, roleName, tenantName))   
		
	def openstack_create_tenant(self, osUserName, osTenantName, osPassWord, osAuthUrl, tenantName):
		'''create tenant
			Input:
				`osXXX`        		tenant name, password, username etc credentials
				`tenantName`       	tenant's name
			Return: id of tenant
		'''		
		t = test.Test()
		h1 = t.host('h1')

		result = h1.bash("keystone --os-username %s --os-tenant-name %s --os-password %s --os-auth-url %s --name %s" % (osUserName, osTenantName, osPassWord, osAuthUrl, tenantName))
		output = result["content"]
		helpers.log("output: %s" % output)
		out_dict = helpers.openstack_convert_table_to_dict(output)
		result1 = out_dict["id"]
		tenantId = result1["value"]
		helpers.log("image %s id is: %s" % (tenantName, str(tenantId)))   
		return tenantId


	def openstack_create_user(self, osUserName, osTenantName, osPassWord, osAuthUrl, userName, userPassword, tenantName, userEmail):
		'''create user
			Input:
				`osXXX`        		tenant name, password, username etc credentials
				`userName`       	user's name
				`userPassword`		user's password
				`tenantName`		name of tenant that the user is a member of
				`userEmail`			user's email address
			Return: id of user
		'''		
		t = test.Test()
		h1 = t.host('h1')

		result = h1.bash("keystone --os-username %s --os-tenant-name %s --os-password %s --os-auth-url %s user-create --name=%s --pass=%s --tenant-id %s --email %s" % (osUserName, osTenantName, osPassWord, osAuthUrl, userName, userPassword, tenantName, userEmail))
		output = result["content"]
		helpers.log("output: %s" % output)
		out_dict = helpers.openstack_convert_table_to_dict(output)
		result1 = out_dict["id"]
		userId = result1["value"]
		helpers.log("user %s id is: %s" % (userName, str(userId)))   
		return userId
		
	def openstack_create_role(self, osUserName, osTenantName, osPassWord, osAuthUrl, roleName):
		'''create user role
			Input:
				`osXXX`        		tenant name, password, username etc credentials
				`roleName`			role name
			Return: id of role
		'''		
		t = test.Test()
		h1 = t.host('h1')

		result = h1.bash("keystone --os-username %s --os-tenant-name %s --os-password %s --os-auth-url %s role-create --name %s" % (osUserName, osTenantName, osPassWord, osAuthUrl, roleName))              
		output = result["content"]
		helpers.log("output: %s" % output)
		out_dict = helpers.openstack_convert_table_to_dict(output)
		result1 = out_dict["id"]
		roleId = result1["value"]
		helpers.log("role %s id is: %s" % (roleName, str(roleId)))   
		return roleId

	def openstack_create_flavor(self, osUserName, osTenantName, osPassWord, osAuthUrl, flavorName, flavorId, flavorMemSize, flavorDisk, flavorVCpu):
		'''create flavor
			Input:
				`osXXX`        		tenant name, password, username etc credentials
				`flavorName`			name of flavor
				`flavorId`				flavor ID, need to pass a flavor ID to the cli as it is required in the creation.
				`flavorMemSize`			Memory size of the flavor
				`flavorDisk`			Disk size of the flavor, can be 0
				`flavorVCpu`			Number of vcpu for the flavor
				
			Return: result of creation table output is different from other openstack cli
			root@nova-controller:~# nova --os-username admin --os-tenant-name admin  --os-auth-url http://10.193.0.120:5000/v2.0/ --os-password bsn flavor-create xlarge 10 9000 10 1
			+----+--------+-----------+------+-----------+------+-------+-------------+-----------+
			| ID | Name   | Memory_MB | Disk | Ephemeral | Swap | VCPUs | RXTX_Factor | Is_Public |
			+----+--------+-----------+------+-----------+------+-------+-------------+-----------+
			| 10 | xlarge | 9000      | 10   | 0         |      | 1     | 1.0         | True      |
			+----+--------+-----------+------+-----------+------+-------+-------------+-----------+

		'''					
		t = test.Test()
		h1 = t.host('h1')

		result = h1.bash("nova --os-username %s --os-tenant-name %s --os-password %s --os-auth-url %s flavor-create %s %s %d %d %d" % (osUserName, osTenantName, osPassWord, osAuthUrl, flavorName, flavorId, flavorMemSize, flavorDisk,flavorVCpu))              
		#output = result["content"]
		#helpers.log("output: %s" % output)
		#out_dict = helpers.openstack_convert_table_to_dict(output)
		#result1 = out_dict["id"]
		#roleId = result1["value"]
		#helpers.log("role %s id is: %s" % (roleName, str(roleId)))   
		#return roleId
		return result
	
	def openstack_create_image(self, osUserName, osTenantName, osPassWord, osAuthUrl, imageName, diskFormat, location):
		'''create image
			Input:
				`osXXX`        		tenant name, password, username etc credentials
				`imageName`			name of Image
				`diskFormat`		Image format, should be set to qcow2
				`location`			Location to copy image from, usually http://xxxxxx
			Return: id of image
		'''				
		t = test.Test()
		h1 = t.host('h1')

		result = h1.bash("glance --os-username %s --os-tenant-name %s --os-password %s --os-auth-url %s image-create --name %s --is-public True --container-format bare --disk-format %s --copy-from %s " % (osUserName, osTenantName, osPassWord, osAuthUrl, imageName, diskFormat, location ))              
		output = result["content"]
		helpers.log("output: %s" % output)
		out_dict = helpers.openstack_convert_table_to_dict(output)
		result1 = out_dict["id"]
		imageId = result1["value"]
		helpers.log("image %s id is: %s" % (imageName, str(imageId)))   
		return imageId

	def openstack_create_router(self, osUserName, osTenantName, osPassWord, osAuthUrl, tenantId, tenantName):
		'''create router
			Input:
				`osXXX`        		tenant name, password, username etc credentials
				`tenantId`			ID of the tenant for the router creation. 
				`tenantName`		Name of Tenant
			Return: id of created Router
		'''				
		t = test.Test()
		h1 = t.host('h1')

		result = h1.bash("neutron --os-username %s --os-tenant-name %s --os-password %s --os-auth-url %s router-create --tenant-id %s %s-Router " % (osUserName, osTenantName, osPassWord, osAuthUrl, tenantId, tenantName))              
		output = result["content"]
		helpers.log("output: %s" % output)
		out_dict = helpers.openstack_convert_table_to_dict(output)
		result1 = out_dict["id"]
		routerId = result1["value"]
		helpers.log("tenant %s router id is: %s" % (tenantName, str(routerId)))   
		return routerId


	def openstack_create_net(self, osUserName, osTenantName, osPassWord, osAuthUrl, tenantId, tenantName, networkNum):
		'''create network
			Input:
				`osXXX`        		tenant name, password, username etc credentials
				`tenantId`			ID of the tenant for the router creation. 
				`tenantName`		Name of Tenant
				`networkNum`		Metwork Num or identifier for this tenant network
			Return: id of created Router
		'''				
		t = test.Test()
		h1 = t.host('h1')

		result = h1.bash("neutron --os-username %s --os-tenant-name %s --os-password %s --os-auth-url %s net-create --tenant-id %s %s-Network-%s " % (osUserName, osTenantName, osPassWord, osAuthUrl, tenantId, tenantName, networkNum))              
		output = result["content"]
		helpers.log("output: %s" % output)
		out_dict = helpers.openstack_convert_table_to_dict(output)
		result1 = out_dict["id"]
		netId = result1["value"]
		helpers.log("network %s id is: %s" % (tenantName, str(netId)))   
		return netId

	def openstack_create_subnet(self, osUserName, osTenantName, osPassWord, osAuthUrl, gateway=None, networkName, poolStart=None, poolEnd=None, netIP, netMask):
		'''create image
			Input:
				`osXXX`        		tenant name, password, username etc credentials
				`tenantId`			ID of the tenant for the router creation. 
				`tenantName`		Name of Tenant
				`networkNum`		Metwork Num or identifier for this tenant network
			Return: id of created Router
		'''				
		t = test.Test()
		h1 = t.host('h1')

		result = h1.bash("neutron --os-username %s --os-tenant-name %s --os-password %s --os-auth-url %s net-create --tenant-id %s %s-Network-%s " % (osUserName, osTenantName, osPassWord, osAuthUrl, tenantId, tenantName, networkNum))              
		output = result["content"]
		helpers.log("output: %s" % output)
		out_dict = helpers.openstack_convert_table_to_dict(output)
		result1 = out_dict["id"]
		netId = result1["value"]
		helpers.log("network %s id is: %s" % (tenantName, str(netId)))   
		return netId
	
neutron subnet-create --tenant-id $tenantid Tenant$startTenantid-Network-$startExtNetwork $ipExtsubnet --dns_nameservers list=true $dns1 $dns2 
    
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
    