import autobot.helpers as helpers
import autobot.test as test
import re

class Openstack(object):

	def __init__(self):
		pass

	def openstack_show_nw_id(self, osUserName, osTenantName, osPassWord, osAuthUrl, networkName):
		'''Get network id
			Input:
				`osXXX`        		tenant name, password, username etc credentials
				`networkName`       network name for that particular tenant
			Return: id of network
			
			matchObj = re.match( r'(.*) are (.*?) .*', line, re.M|re.I)

if matchObj:
   print "matchObj.group() : ", matchObj.group()
   print "matchObj.group(1) : ", matchObj.group(1)
   print "matchObj.group(2) : ", matchObj.group(2)
else:
   print "No match!!"
			
		'''
		t = test.Test()
		os1 = t.openstack_server('os1')
		
		result = os1.bash("neutron --os-username %s --os-tenant-name %s --os-password %s --os-auth-url %s net-show %s" % (osUserName, osTenantName, osPassWord, osAuthUrl, networkName))
		output = result["content"]
		helpers.log("output: %s" % output)
		
		match = re.search(r'Unable to find network with', output, re.S | re.I)
		if match:
			return False
		else:
			out_dict = helpers.openstack_convert_table_to_dict(output)
			result1 = out_dict["id"]
			netId = result1["value"]
			helpers.log("network %s id is: %s" % (networkName, str(netId)))   
			return netId		

	def openstack_show_flavor_id(self, osUserName, osTenantName, osPassWord, osAuthUrl, flavorName):
		'''Get flavor id
			Input:
				`osXXX`        		tenant name, password, username etc credentials
				`flavorName`       	flavor's name
			Return: id of flavor
		'''
		t = test.Test()
		os1 = t.openstack_server('os1')
		
		result = os1.bash("nova --os-username %s --os-tenant-name %s --os-password %s --os-auth-url %s flavor-show %s" % (osUserName, osTenantName, osPassWord, osAuthUrl, flavorName))         
		output = result["content"]
		
		helpers.log("output: %s" % output)
		match = re.search(r'ERROR: No flavor with', output, re.S | re.I)
		if match:
			return False
		else:
			out_dict = helpers.openstack_convert_table_to_dict(output)
			result1 = out_dict["id"]
			flavorId = result1["value"]
			helpers.log("flavor %s id is: %s" % (flavorName, str(flavorId)))   
			return flavorId		

	def openstack_show_user_id(self, osUserName, osTenantName, osPassWord, osAuthUrl, userName):
		'''Get user id
			Input:
				`osXXX`        		tenant name, password, username etc credentials
				`networkName`       user's name
			Return: id of user
		'''
		t = test.Test()
		os1 = t.openstack_server('os1')
		
		result = os1.bash("keystone --os-username %s --os-tenant-name %s --os-password %s --os-auth-url %s user-get %s" % (osUserName, osTenantName, osPassWord, osAuthUrl, userName))              
		output = result["content"]
		helpers.log("output: %s" % output)
		match = re.search(r'No user with a name or ID', output, re.S | re.I)
		if match:
			return False
		else:
			out_dict = helpers.openstack_convert_table_to_dict(output)
			result1 = out_dict["id"]
			userId = result1["value"]
			helpers.log("user %s id is: %s" % (userName, str(userId)))   
			return userId		

	def openstack_show_role_id(self, osUserName, osTenantName, osPassWord, osAuthUrl, roleName):
		'''Get role id
			Input:
				`osXXX`        		tenant name, password, username etc credentials
				`roleName`       	role's name
			Return: id of role
		'''
		
		t = test.Test()
		os1 = t.openstack_server('os1')
		
		result = os1.bash("keystone --os-username %s --os-tenant-name %s --os-password %s --os-auth-url %s role-get %s" % (osUserName, osTenantName, osPassWord, osAuthUrl, roleName))              
		output = result["content"]
		helpers.log("output: %s" % output)
		out_dict = helpers.openstack_convert_table_to_dict(output)
		result1 = out_dict["id"]
		roleId = result1["value"]
		helpers.log("role %s id is: %s" % (roleName, str(roleId))) 
		return roleId		


	def openstack_show_tenant(self, tenantName):
		'''Get tenant id
			Input:
				`osXXX`        		tenant name, password, username etc credentials
				`tenantName`       	tenant's name
			Return: id of tenant
		'''
		t = test.Test()
		os1 = t.openstack_server('os1')

		result = os1.bash("keystone tenant-get %s" % (tenantName))             
		output = result["content"]
		out_dict = helpers.openstack_convert_table_to_dict(output)
		tenantId = out_dict["id"]["value"]
		return tenantId		

	def openstack_show_vm(self, osUserName, osTenantName, osPassWord, osAuthUrl, instanceName):
		'''Get vm id
			Input:
				`osXXX`        		tenant name, password, username etc credentials
				`instanceName`      vm's name
			Return: id of vm
		'''	
		t = test.Test()
		os1 = t.openstack_server('os1')

		result = os1.bash("nova --os-username %s --os-tenant-name %s --os-password %s --os-auth-url %s show %s" % (osUserName, osTenantName, osPassWord, osAuthUrl, instanceName))              
		output = result["content"]
		helpers.log("output: %s" % output)
		out_dict = helpers.openstack_convert_table_to_dict(output)
		result1 = out_dict["id"]
		vmId = result1["value"]
		helpers.log("VM %s id is: %s" % (instanceName, str(vmId)))   
		return vmId		

	def openstack_show_vm_status(self, osUserName, osTenantName, osPassWord, osAuthUrl, instanceName):
		'''Get vm status
			Input:
				`osXXX`        		tenant name, password, username etc credentials
				`instanceName`       vm's name
			Return: vm status
		'''
		t = test.Test()
		os1 = t.openstack_server('os1')

		result = os1.bash("nova --os-username %s --os-tenant-name %s --os-password %s --os-auth-url %s show %s" % (osUserName, osTenantName, osPassWord, osAuthUrl, instanceName))              
		output = result["content"]
		helpers.log("output: %s" % output)
		out_dict = helpers.openstack_convert_table_to_dict(output)
		result1 = out_dict["status"]
		vmStatus = result1["value"]
		helpers.log("VM %s status is: %s" % (instanceName, str(vmStatus)))   
		return vmStatus		

	def openstack_show_router_id(self, osUserName, osTenantName, osPassWord, osAuthUrl, routerName):
		'''Get router id
			Input:
				`osXXX`        		tenant name, password, username etc credentials
				`routerName`       	router's name
			Return: id of router
		'''
		t = test.Test()
		os1 = t.openstack_server('os1')

		result = os1.bash("neutron --os-username %s --os-tenant-name %s --os-password %s --os-auth-url %s router-show %s" % (osUserName, osTenantName, osPassWord, osAuthUrl, routerName))              
		output = result["content"]
		helpers.log("output: %s" % output)
		out_dict = helpers.openstack_convert_table_to_dict(output)
		result1 = out_dict["id"]
		routerId = result1["value"]
		helpers.log("router %s id is: %s" % (routerName, str(routerId)))   
		return routerId		

	def openstack_show_router_status(self, osUserName, osTenantName, osPassWord, osAuthUrl, routerName):
		'''Get router status
			Input:
				`osXXX`        		tenant name, password, username etc credentials
				`routerName`       	router's name
			Return: router status
		'''	
		t = test.Test()
		os1 = t.openstack_server('os1')

		result = os1.bash("neutron --os-username %s --os-tenant-name %s --os-password %s --os-auth-url %s router-show %s" % (osUserName, osTenantName, osPassWord, osAuthUrl, routerName))              
		output = result["content"]
		helpers.log("output: %s" % output)
		out_dict = helpers.openstack_convert_table_to_dict(output)
		result1 = out_dict["status"]
		routerStatus = result1["value"]
		helpers.log("router %s status is: %s" % (routerName, str(routerStatus)))   
		return routerStatus		

	def openstack_show_subnet(self, subnetName):
		'''Get subnet id
			Input:
				`osXXX`        		tenant name, password, username etc credentials
				`subnetName`       	subnet's name
			Return: id of subnet for that tenant
			NB: when creating subnet, name is optional. Must pass name during subnet creation to use this function
		'''
		t = test.Test()
		os1 = t.openstack_server('os1')

		result = os1.bash("neutron subnet-show %s" % (subnetName))              
		output = result["content"]		
		match = re.search(r'Unable to find subnet with name', output)
		if match:
			helpers.log("subnet Not found")
			return ''
		else:
			out_dict = helpers.openstack_convert_table_to_dict(output)
			subnetId = out_dict["network_id"]["value"]
			return subnetId		

	def openstack_show_image_id(self, imageName):
		'''Get image id
			Input:
				`osXXX`        		tenant name, password, username etc credentials
				`imageName`       	image's name
			Return: id of image
		'''
		t = test.Test()
		os1 = t.openstack_server('os1')
		result = os1.bash("nova image-list")
		output = result["content"]
		match = re.search(r'ERROR: No image with a name or ID', output, re.S | re.I)
		if match:
			return False
		else:
			#output = helpers.strip_cli_output(output)
			out_dict = helpers.openstack_convert_table_to_dict(output)
			image_id = None
			for key in out_dict:
				name = out_dict[key]['name']
				match = re.search(imageName, name)
				if match:
					image_id = key
					break
		return image_id

	def openstack_source(self, source_name):
		'''Get image id
			Input:
				`rc file name (e.g keystone_rc file which contains all the login account details)
		'''
		t = test.Test()
		os1 = t.openstack_server('os1')
		os1.bash("source /home/stack/devstack/%s" % source_name)
		
	def openstack_add_user_role(self, osUserName, osTenantName, osPassWord, osAuthUrl, userName, roleName, tenantName):
		''' set user role
			Input:
				`username`:		username of the tenant's user
				`rolename`:		rolename
				`tenantname`:	name of tenant
		'''
		t = test.Test()
		os1 = t.openstack_server('os1')
		
		os1.bash("keystone --os-username %s --os-tenant-name %s --os-password %s --os-auth-url %s user-role-add --user %s --role --tenant %s" % (osUserName, osTenantName, osPassWord, osAuthUrl, userName, roleName, tenantName))   
		
	def openstack_add_tenant(self, tenantName):
		'''create tenant
			Input:
				       		tenant name to be created , Will use admin login to create tenant(project)
				`tenantName`       	tenant's name
			Return: id of tenant
		'''		
		t = test.Test()
		os1 = t.openstack_server('os1')
		os1.bash("keystone tenant-create --name %s" % (tenantName))
		return True

	def openstack_delete_tenant(self, tenantName):
		'''delete tenant
			Input:
				       		tenant name to be deleted , Will use admin login to create tenant(project)
				`tenantName`       	tenant's name
			Return: True
		'''		
		t = test.Test()
		os1 = t.openstack_server('os1')
		os1.bash("keystone tenant-delete %s" % (tenantName))
		return True
	
	def openstack_add_user(self, tenantName, userName, userPassword, userEmail):
		'''create user
			Input:
				`userName`       	user's name
				`userPassword`		user's password
				`userEmail`			user's email address
			Return: id of user
		'''		
		t = test.Test()
		os1 = t.openstack_server('os1')
		tenantId = self.openstack_show_tenant(tenantName)
		os1.bash("keystone user-create --name=%s --pass=%s --tenant-id %s --email %s" % (userName, userPassword, tenantId, userEmail))
		return True
		
	def openstack_delete_user(self, userName):
		'''delete user
			Input:
				`userName`       	user's name
				
			Return: True
		'''		
		t = test.Test()
		os1 = t.openstack_server('os1')
		os1.bash("keystone user-delete %s" % userName)
		return True
	
	def openstack_add_role(self, osUserName, osTenantName, osPassWord, osAuthUrl, roleName):
		'''create user role
			Input:
				`osXXX`        		tenant name, password, username etc credentials
				`roleName`			role name
			Return: id of role
		'''		
		t = test.Test()
		os1 = t.openstack_server('os1')

		result = os1.bash("keystone --os-username %s --os-tenant-name %s --os-password %s --os-auth-url %s role-create --name %s" % (osUserName, osTenantName, osPassWord, osAuthUrl, roleName))              
		output = result["content"]
		helpers.log("output: %s" % output)
		out_dict = helpers.openstack_convert_table_to_dict(output)
		result1 = out_dict["id"]
		roleId = result1["value"]
		helpers.log("role %s id is: %s" % (roleName, str(roleId)))   
		return roleId

	def openstack_add_flavor(self, osUserName, osTenantName, osPassWord, osAuthUrl, flavorName, flavorId, flavorMemSize, flavorDisk, flavorVCpu):
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
		os1 = t.openstack_server('os1')

		result = os1.bash("nova --os-username %s --os-tenant-name %s --os-password %s --os-auth-url %s flavor-create %s %s %s %s %s" % (osUserName, osTenantName, osPassWord, osAuthUrl, flavorName, flavorId, flavorMemSize, flavorDisk,flavorVCpu))              
		#output = result["content"]
		#helpers.log("output: %s" % output)
		#out_dict = helpers.openstack_convert_table_to_dict(output)
		#result1 = out_dict["id"]
		#roleId = result1["value"]
		#helpers.log("role %s id is: %s" % (roleName, str(roleId)))   
		#return roleId
		return result
	
	def openstack_add_image(self, osUserName, osTenantName, osPassWord, osAuthUrl, imageName, diskFormat, location):
		'''create image
			Input:
				`osXXX`        		tenant name, password, username etc credentials
				`imageName`			name of Image
				`diskFormat`		Image format, should be set to qcow2
				`location`			Location to copy image from, usually http://xxxxxx
			Return: id of image
		'''				
		t = test.Test()
		os1 = t.openstack_server('os1')

		result = os1.bash("glance --os-username %s --os-tenant-name %s --os-password %s --os-auth-url %s image-create --name %s --is-public True --container-format bare --disk-format %s --copy-from %s " % (osUserName, osTenantName, osPassWord, osAuthUrl, imageName, diskFormat, location ))              
		output = result["content"]
		helpers.log("output: %s" % output)
		out_dict = helpers.openstack_convert_table_to_dict(output)
		result1 = out_dict["id"]
		imageId = result1["value"]
		helpers.log("image %s id is: %s" % (imageName, str(imageId)))   
		return imageId

	def openstack_add_router(self, osUserName, osTenantName, osPassWord, osAuthUrl, tenantId, tenantName):
		'''create router
			Input:
				`osXXX`        		tenant name, password, username etc credentials
				`tenantId`			ID of the tenant for the router creation. 
				`tenantName`		Name of Tenant
			Return: id of created Router
		'''				
		t = test.Test()
		os1 = t.openstack_server('os1')

		result = os1.bash("neutron --os-username %s --os-tenant-name %s --os-password %s --os-auth-url %s router-create --tenant-id %s %s-Router " % (osUserName, osTenantName, osPassWord, osAuthUrl, tenantId, tenantName))              
		output = result["content"]
		helpers.log("output: %s" % output)
		out_dict = helpers.openstack_convert_table_to_dict(output)
		result1 = out_dict["id"]
		routerId = result1["value"]
		helpers.log("tenant %s router id is: %s" % (tenantName, str(routerId)))   
		return routerId


	def openstack_add_net(self, tenantName, netName, external=False):
		'''create network
			Input:
				'networkNum`		Network name 
				neutron net-create --tenant-id $adminid External-Network --router:external=True
			Return: id of created Router
		'''				
		t = test.Test()
		os1 = t.openstack_server('os1')
		tenantId = self.openstack_show_tenant(tenantName)
		if external is False:
			os1.bash("neutron net-create --tenant-id %s %s " % (tenantId, netName))             
		else:
			os1.bash("neutron net-create --tenant-id %s %s --router:external=True" % (tenantId, netName))  
		return True

	def openstack_delete_net(self, netName):
		'''delete network
			Input:
				'networkNum`		Network name 
			Return: True
		'''				
		t = test.Test()
		os1 = t.openstack_server('os1')		
		os1.bash("neutron net-delete %s " % (netName))               
		return True
	
	def openstack_add_subnet(self, tenantName, netName, subnetName, subnet_ip, dnsNameServers=None):
		'''create subnet
			Input:
				network name , Subnet name , Subnet (e.g app-net , app-net1, 50.0.0.0/24)
			Return: id for created subnet
		'''				
		t = test.Test()
		os1 = t.openstack_server('os1')
		tenantId = self.openstack_show_tenant(tenantName)
		if dnsNameServers is None:
			os1.bash("neutron subnet-create --tenant-id %s --name %s %s %s" % (tenantId, netName, subnetName, subnet_ip))   
		else:	
			os1.bash("neutron subnet-create --tenant-id %s --name %s %s %s --dns_nameservers list=true %s" % (tenantId, netName, subnetName, subnet_ip, dnsNameServers))   
		return True

	def openstack_add_keypair(self, osUserName, osTenantName, osPassWord, keypairName, pathToSave):
		'''Generate openstack tenant keypair
			Input:
				`osXXX`        		tenant name, password, username etc credentials
				`keypairName`			Keypair name 
				`pathToSave`		Path to save public key on nova controller
			Return: no data is returned
		'''				
		t = test.Test()
		os1 = t.openstack_server('os1')
		os1.bash("nova --os-username %s --os-tenant-name %s --os-password %s keypair-add %s > %s" % (osUserName, osTenantName, osPassWord, keypairName, pathToSave)) 
		return True  
		

	def openstack_add_router_gw(self, osUserName, osTenantName, osPassWord, osAuthUrl, routerId, extNetId):
		'''set tenant router gateway
			Input:
				`osXXX`        		tenant name, password, username etc credentials
				`routerId`			tenant router id
				`extNetId`		external network id
				root@nova-controller:~# neutron --os-username user1 --os-tenant-name Tenant1 --os-auth-url http://10.193.0.120:5000/v2.0/ --os-password bsn router-gateway-set ff25378d-8b0d-4192-8c33-78ea0eba8d0e 02f4a4d1-0930-43bf-94db-2d39b11c343d
S	
				Set gateway for router ff25378d-8b0d-4192-8c33-78ea0eba8d0e
			Return: output of command results
		'''				
		t = test.Test()
		os1 = t.openstack_server('os1')
		
		os1.bash("neutron --os-username %s --os-tenant-name %s --os-password %s --os-auth-url %s router-gateway-set %s %s" % (osUserName, osTenantName, osPassWord, osAuthUrl, routerId, extNetId))   
		data = os1.bash_content()
		return data

	def openstack_delete_router_gw(self, osUserName, osTenantName, osPassWord, osAuthUrl, routerId):
		'''set tenant router gateway
			Input:
				`osXXX`        		tenant name, password, username etc credentials
				`routerId`			tenant router id
				`extNetId`		external network id
				neutron --os-username user1 --os-tenant-name Tenant1 --os-auth-url http://10.193.0.120:5000/v2.0/ --os-password bsn router-gateway-clear ff25378d-8b0d-4192-8c33-78ea0eba8d0e
				Removed gateway from router ff25378d-8b0d-4192-8c33-78ea0eba8d0e
			Return: output of command results
		'''				
		t = test.Test()
		os1 = t.openstack_server('os1')
		
		os1.bash("neutron --os-username %s --os-tenant-name %s --os-password %s --os-auth-url %s router-gateway-delete %s" % (osUserName, osTenantName, osPassWord, osAuthUrl, routerId))   
		data = os1.bash_content()
		return data
		
		
	def openstack_add_subnet_to_router(self, osUserName, osTenantName, osPassWord, osAuthUrl, routerId, subNetId):
		'''attach subnet to tenant router
			Input:
				`osXXX`        		tenant name, password, username etc credentials
				`routerId`			tenant router id
				`subNetId`			sub network id
		neutron --os-username user1 --os-tenant-name Tenant1 --os-auth-url http://10.193.0.120:5000/v2.0/ --os-password bsn router-interface-add ff25378d-8b0d-4192-8c33-78ea0eba8d0e 470fbbce-26e0-464b-9e21-f888a852db04   
		Added interface b0a05a66-db7f-4282-95b5-648ab6dbd8fe to router ff25378d-8b0d-4192-8c33-78ea0eba8d0e.
		
		Return: output of command results
		'''
		t = test.Test()
		os1 = t.openstack_server('os1')
		
		os1.bash("neutron --os-username %s --os-tenant-name %s --os-password %s --os-auth-url %s router-interface-add %s %s" % (osUserName, osTenantName, osPassWord, osAuthUrl, routerId, subNetId))   
		data = os1.bash_content()
		return data
		
	def openstack_delete_subnet_to_router(self, osUserName, osTenantName, osPassWord, osAuthUrl, routerId, subNetId):
		'''detach subnet from tenant router
			Input:
				`osXXX`        		tenant name, password, username etc credentials
				`routerId`			tenant router id
				`subNetId`			sub network id

		neutron --os-username user1 --os-tenant-name Tenant1 --os-auth-url http://10.193.0.120:5000/v2.0/ --os-password bsn router-interface-delete ff25378d-8b0d-4192-8c33-78ea0eba8d0e 470fbbce-26e0-464b-9e21-f888a852db04
		Removed interface from router ff25378d-8b0d-4192-8c33-78ea0eba8d0e.
		Return: output of command results
		'''
		t = test.Test()
		os1 = t.openstack_server('os1')
		
		os1.bash("neutron --os-username %s --os-tenant-name %s --os-password %s --os-auth-url %s router-interface-delete %s %s" % (osUserName, osTenantName, osPassWord, osAuthUrl, routerId, subNetId))   
		data = os1.bash_content()
		return data

	def openstack_add_secgroup_permit_all(self, osUserName, osTenantName, osPassWord, osAuthUrl, secgroupName):
		'''set tenant secgroup policy to allow all traffic
			Input:
				`osXXX`        		tenant name, password, username etc credentials
				`secgroupName`		secgroup name, default is default
		Return: no results to return
		'''
		t = test.Test()
		os1 = t.openstack_server('os1')

		os1.bash("nova --os-username %s --os-tenant-name %s --os-password %s --os-auth-url %s secgroup %s tcp 1 65535 0.0.0.0/0" % (osUserName, osTenantName, osPassWord, osAuthUrl, secgroupName))   
		os1.bash("nova --os-username %s --os-tenant-name %s --os-password %s --os-auth-url %s secgroup %s udp 1 65535 0.0.0.0/0" % (osUserName, osTenantName, osPassWord, osAuthUrl, secgroupName))   
		os1.bash("nova --os-username %s --os-tenant-name %s --os-password %s --os-auth-url %s secgroup %s icmp -1 -1 0.0.0.0/0" % (osUserName, osTenantName, osPassWord, osAuthUrl, secgroupName))   
#		return pass

	def openstack_show_instance_status(self, osUserName, osTenantName, osPassWord, osAuthUrl, vmId):
		'''get instance status
			Input:
				`osXXX`        		tenant name, password, username etc credentials
				`vmId`				Instance ID or instance name. 
			Return: status of instance
		'''

		t = test.Test()
		os1 = t.openstack_server('os1')

		result = os1.bash("nova --os-username %s --os-tenant-name %s --os-password %s --os-auth-url %s show %s" % (osUserName, osTenantName, osPassWord, osAuthUrl, vmId))              
		output = result["content"]
		helpers.log("output: %s" % output)
		out_dict = helpers.openstack_convert_table_to_dict(output)
		result1 = out_dict["status"]
		vmStatus = result1["value"]
		helpers.log("instance %s status is: %s" % (vmId, str(vmStatus)))   
		return vmStatus
		
	
	def openstack_delete_instance(self, osUserName, osTenantName, osPassWord, osAuthUrl, vmId):
		'''delete instance
			Input:
				`osXXX`        		tenant name, password, username etc credentials
				`vmId`				Instance ID or instance name to be deleted. 
			Return: empty string
		'''

		t = test.Test()
		os1 = t.openstack_server('os1')

		os1.bash("nova --os-username %s --os-tenant-name %s --os-password %s --os-auth-url %s delete %s" % (osUserName, osTenantName, osPassWord, osAuthUrl, vmId))              
#		return pass
	def openstack_verify_tenant(self, tenantName):
		'''function to verify tenant in BSN controller
			Input:
				tenant Name 
			Return: verify the tenant created in BSN controller
		'''
		t = test.Test()
		c = t.controller('master')
		url = '/api/v1/data/controller/applications/bvs/info/endpoint-manager/tenants'
		c.rest.get(url)
		data = c.rest.content()
		tenantId = self.openstack_show_tenant(tenantName)
		for i in range(0,len(data)):
			if str(data[i]["tenant-name"]) == str(tenantId):
				helpers.log("Pass: Openstack tenant are present in the BSN controller")
				return True
		return False
			
	def openstack_verify_vns(self, tenantName, subnetName):
		'''function to verify vns present in BSN controller
			Input:
				tenant Name, netName
			Return: verify the vns created in BSN controller
		'''
		t = test.Test()
		c = t.controller('master')
		tenantId = self.openstack_show_tenant(tenantName)
		netId = self.openstack_show_subnet(subnetName)
		if netId != '':
			url = '/api/v1/data/controller/applications/bvs/info/endpoint-manager/vnses[tenant-name="%s"][name="%s"]' % (tenantId, netId)	      
			c.rest.get(url)
			data = c.rest.content()
			if data[0]["tenant-name"] == tenantId:
				if data[0]["name"] == netId:
					helpers.log("Pass: Openstack networks are present in the BSN controller")
					return True
				else:
					helpers.test_failure("Fail:Openstack networks are not created in the BSN controller, check the network service log")
					return False
			else:
					helpers.log("Openstack tenant not present in the BSN controller")
					return False
		else:
			url = '/api/v1/data/controller/applications/bvs/info/endpoint-manager/tenants'
			c.rest.get(url)	
			data = c.rest.content()
			if len(data) == 0:
				helpers.log("Expected vns is deleted from the controller")
				return True
			else:
				helpers.test_failure("Expected vns is not deleted from the controller")	
				return False
						