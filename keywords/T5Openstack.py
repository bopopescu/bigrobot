import autobot.helpers as helpers
import autobot.test as test
import re
import netaddr

class T5Openstack(object):

	def __init__(self):
		pass

	def openstack_show_flavor(self, osUserName, osTenantName, osPassWord, osAuthUrl, flavorName):
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

	def openstack_show_user(self, osUserName, osTenantName, osPassWord, osAuthUrl, userName):
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

	def openstack_show_role(self, osUserName, osTenantName, osPassWord, osAuthUrl, roleName):
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

	def openstack_show_instance_all(self):
		'''Get vm status
			Input:
				make sure to source the specific tenant rc file which contains , tenant name , user , password
				show all instance
			Return: vm status
		'''
		t = test.Test()
		os1 = t.openstack_server('os1')
		os1.bash("nova list")
		return True

	def openstack_show_instance_ip(self, instanceName, netName):
		'''Get instance id
			Input:
				instance name to be provided
				net name for the IP address
			Return: instance IP.
		'''
		t = test.Test()
		os1 = t.openstack_server('os1')
		result = os1.bash("nova show %s" % instanceName)
		output = result["content"]
		instanceIp = []
		out_dict = helpers.openstack_convert_table_to_dict(output)
		if out_dict["status"]["value"] == "ACTIVE":
			network = netName + " " + "network"
			ip = out_dict[network]["value"]
			if re.match(r'.+,.+', ip):
				instanceIp = ip.split(',')  # should have 2 entries
			else:
				instanceIp = [ip]
			return instanceIp[0]
		else:
			helpers.log("Instance is not active in nova controller")
	
	def openstack_show_instance_floating_ip(self, instanceName, netName):
		'''Get instance id
			Input:
				instance name to be provided
				net name for the IP address
			Return: instance IP.
		'''
		t = test.Test()
		os1 = t.openstack_server('os1')
		result = os1.bash("nova show %s" % instanceName)
		output = result["content"]
		instanceIp = []
		out_dict = helpers.openstack_convert_table_to_dict(output)
		if out_dict["status"]["value"] == "ACTIVE":
			network = netName + " " + "network"
			ip = out_dict[network]["value"]
			if re.match(r'.+,.+', ip):
				instanceIp = ip.split(',')  # should have 2 entries
				helpers.log("instanceip=%s" % instanceIp)
			else:
				instanceIp = [ip]
			return instanceIp[1]
		else:
			helpers.log("Instance is not active in nova controller")	
	
	def openstack_show_router(self, routerName):
		'''Get router id
			Input:
				`osXXX`        		tenant name, password, username etc credentials
				`routerName`       	router's name
			Return: id of router
		'''
		t = test.Test()
		os1 = t.openstack_server('os1')

		result = os1.bash("neutron router-show %s" % (routerName))
		output = result["content"]
		match = re.search(r'Unable to find router with name', output)
		if match:
			helpers.log("router Not found")
			return ''
		else:
			out_dict = helpers.openstack_convert_table_to_dict(output)
			routerId = out_dict["id"]["value"]
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
			subnetId = out_dict["id"]["value"]
			return subnetId

	def openstack_show_subnet_ip(self, subnetName):
		'''Get subnet gateway IP address
			Input: subnet Name
			Output: gateway IP
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
			subnetIp = out_dict["gateway_ip"]["value"]
			return subnetIp

	def openstack_show_subnet_cidr(self, subnetName):
		'''Get subnet CIDR value
			Input: subnet Name
			Output: CIDR for the network
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
			subnet_cidr = out_dict["cidr"]["value"]
			return subnet_cidr
	
	def openstack_show_net(self, netName):
		'''Get Nova net Id
			Input:
				net Name : created during the test using openstack add net
			Return: id of of the net to be used for instance creation.
		'''
		t = test.Test()
		os1 = t.openstack_server('os1')
		result = os1.bash("nova network-show %s" % (netName))
		output = result["content"]
		match = re.search(r'ERROR: No network with a name', output)
		if match:
			helpers.log("Network Not found")
			return ''
		else:
			out_dict = helpers.openstack_convert_table_to_dict(output)
			netId = out_dict["id"]["value"]
			return netId

	def openstack_show_image(self, imageName):
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
			# output = helpers.strip_cli_output(output)
			out_dict = helpers.openstack_convert_table_to_dict(output)
			imageId = None
			for key in out_dict:
				name = out_dict[key]['name']
				match = re.search(imageName, name)
				if match:
					imageId = key
					break
		return imageId

	def openstack_show_external_network(self, extName):
		'''Get subnet id
			Input:
				`osXXX`        		tenant name, password, username etc credentials
				`subnetName`       	subnet's name
			Return: id of subnet for that tenant
			NB: when creating subnet, name is optional. Must pass name during subnet creation to use this function
		'''
		t = test.Test()
		os1 = t.openstack_server('os1')

		result = os1.bash("neutron subnet-show %s" % (extName))
		output = result["content"]
		match = re.search(r'Unable to find subnet with name', output)
		if match:
			helpers.log("subnet Not found")
			return ''
		else:
			out_dict = helpers.openstack_convert_table_to_dict(output)
			
			helpers.log(helpers.prettify(out_dict))
			
			extId = out_dict["network_id"]["value"]
			return extId
	
	def openstack_nova_floating_ip_pool_list(self):
		'''
		get floating ip pool list
		'''
		t = test.Test()
		os1 = t.openstack_server('os1')
		result = os1.bash("nova floating-ip-pool-list")
		output = result["content"]
		out_dict = helpers.openstack_convert_table_to_dict(output)
		return out_dict
	
	def openstack_nova_floating_ip_create(self, external_network_name ):
		'''function to create a floating ip from given pool for the tenant
		'''
		t = test.Test()
		os1 = t.openstack_server("os1")
		result = os1.bash("nova floating-ip-create %s" % (external_network_name))
		output = result["content"]
		match = re.search(r'ERROR (NotFound): Floating ip pool not found', output)
		if match:
			helpers.log("Floating ip pool not found")
			return ''
		return True
	
	def openstack_nova_floating_ip_list(self):
		'''Function to list the floating ip created for the tenant
		'''
		t = test.Test()
		os1 = t.openstack_server("os1")
		result = os1.bash("nova floating-ip-list")
		output = result["content"]
		out_dict =  helpers.openstack_convert_table_to_dict(output)
		helpers.log(helpers.prettify(out_dict))
		return out_dict
	
	def openstack_get_floating_ip(self):
		'''function to provide floating IP for assignment
		'''
		t = test.Test()
		os1 = t.openstack_server("os1")
		result = os1.bash("nova floating-ip-list")
		output = result["content"]
		out_dict = helpers.openstack_convert_table_to_dict(output)
		for record in out_dict.values():	
			if re.match(r'^\d+\.\d+\.\d+\.\d+', record['fixed ip']):
				continue
			else:
				floating_ip = record['ip']
		return floating_ip
		
	def openstack_nova_floating_ip_associate(self, instanceName):
		''' function to associate floating ip to a given instance
		'''
		t = test.Test()
		os1 = t.openstack_server("os1")
		floating_ip = self.openstack_get_floating_ip()
		os1.bash("nova floating-ip-associate %s %s" % (instanceName, floating_ip))
		return True
	
	def openstack_nova_floating_ip_disassociate(self, instanceName, netName):
		''' function to associate floating ip to a given instance
		'''
		t = test.Test()
		os1 = t.openstack_server("os1")
		floating_ip = self.openstack_show_instance_floating_ip(instanceName, netName)
		result = os1.bash("nova floating-ip-disassociate %s %s" % (instanceName, floating_ip))
		output = result["content"]
		match = re.search(r'ERROR', output)
		if match:
			helpers.log("floating ip not found")
			return ''
		else:
			return True
	
	def openstack_nova_floating_ip_delete(self):
		'''function to delete floating ip assigned for a tenant
		'''
		t = test.Test()
		os1 = t.openstack_server("os1")
		result = os1.bash("nova floating-ip-list")
		output = result["content"]
		out_dict = helpers.openstack_convert_table_to_dict(output)
		for record in out_dict.values():	
			if re.match(r'^\d+\.\d+\.\d+\.\d+', record['fixed ip']):
				continue
			else:
				floating_ip = record['ip']
		os1.bash("nova floating-ip-delete %s" % floating_ip)
		return True
	
	def openstack_source(self, source_name):
		'''Get image id
			Input:
				`rc file name (e.g keystone_rc file which contains all the login account details)
		'''
		t = test.Test()
		os1 = t.openstack_server('os1')
		os1.bash("source /root/%s" % source_name)

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

		result = os1.bash("nova --os-username %s --os-tenant-name %s --os-password %s --os-auth-url %s flavor-create %s %s %s %s %s" % (osUserName, osTenantName, osPassWord, osAuthUrl, flavorName, flavorId, flavorMemSize, flavorDisk, flavorVCpu))
		# output = result["content"]
		# helpers.log("output: %s" % output)
		# out_dict = helpers.openstack_convert_table_to_dict(output)
		# result1 = out_dict["id"]
		# roleId = result1["value"]
		# helpers.log("role %s id is: %s" % (roleName, str(roleId)))
		# return roleId
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

		os1.bash("glance --os-username %s --os-tenant-name %s --os-password %s --os-auth-url %s image-create --name %s --is-public True --container-format bare --disk-format %s --copy-from %s " % (osUserName, osTenantName, osPassWord, osAuthUrl, imageName, diskFormat, location))
		return True

	def openstack_add_router(self, tenantName, routerName):
		'''create router
			Input:
				tenantName`		Name of Tenant
				router name
			Return: id of created Router
		'''
		t = test.Test()
		os1 = t.openstack_server('os1')
		tenantId = self.openstack_show_tenant(tenantName)
		try:
			os1.bash("neutron router-create --tenant-id %s %s" % (tenantId, routerName))
		except:
			output = helpers.exception_info_value()
			helpers.log("Output: %s" % output)
			return False
		return True

	def openstack_delete_router(self, routerName):
		'''Delete router
			Input:
				tenantName`		Name of Tenant
				router name
			Return: id of created Router
		'''
		t = test.Test()
		os1 = t.openstack_server('os1')
		try:
			os1.bash("neutron router-delete %s" % (routerName))
		except:
			output = helpers.exception_info_value()
			helpers.log("Output: %s" % output)
			return False
		return True

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
			try:
				os1.bash("neutron net-create --tenant-id %s %s " % (tenantId, netName))
			except:
				output = helpers.exception_info_value()
				helpers.log("Output: %s" % output)
				return False
		else:
			try:
				os1.bash("neutron net-create --tenant-id %s %s --router:external=True" % (tenantId, netName))
			except:
				output = helpers.exception_info_value()
				helpers.log("Output: %s" % output)
				return False
		return True

	def openstack_delete_net(self, netName):
		'''delete network
			Input:
				'networkNum`		Network name
			Return: True
		'''
		t = test.Test()
		os1 = t.openstack_server('os1')
		try:
			os1.bash("neutron net-delete %s " % (netName))
		except:
			output = helpers.exception_info_value()
			helpers.log("Output: %s" % output)
			return True
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
			try:
				os1.bash("neutron subnet-create --tenant-id %s --name %s %s %s" % (tenantId, netName, subnetName, subnet_ip))
			except:
				output = helpers.exception_info_value()
				helpers.log("Output: %s" % output)
				return False
		else:
			try:
				os1.bash("neutron subnet-create --tenant-id %s --name %s %s %s --dns_nameservers list=true %s" % (tenantId, netName, subnetName, subnet_ip, dnsNameServers))
			except:
				output = helpers.exception_info_value()
				helpers.log("Output: %s" % output)
				return False
		return True

	def openstack_add_net_external(self, netName):
		'''create a external network
			Input:
				network name
			Return: id for created subnet
		'''
		t = test.Test()
		os1 = t.openstack_server('os1')
		try:
				os1.bash("neutron net-create %s --router:external=True" % (netName))
		except:
				output = helpers.exception_info_value()
				helpers.log("Output: %s" % output)
				return False
		return True
	
	def openstack_add_net_external_juno(self, netName, phy_network_name, vlan_id):
		'''create a external network
			Input:
				network name
				physical bridge name : typically physnet1 or physnet2
				vlan ID to be used for external network segment
			Return: id for created subnet
		'''
		t = test.Test()
		os1 = t.openstack_server('os1')
		try:
				os1.bash("neutron net-create %s --router:external --provider:network_type vlan --provider:physical_network %s --provider:segmentation_id %s" % (netName, phy_network_name, vlan_id))
		except:
				output = helpers.exception_info_value()
				helpers.log("Output: %s" % output)
				return False
		return True
	
	def openstack_add_subnet_external(self,  netName, subnetName, external_gateway_ip, subnet_ip):
		'''create subnet
			Input:
				network name , Subnet name , Subnet (e.g app-net , app-net1, 50.0.0.0/24)
			Return: id for created subnet
		'''
		t = test.Test()
		os1 = t.openstack_server('os1')
		try:
				os1.bash("neutron subnet-create %s --name %s --gateway %s %s" % (netName, subnetName, external_gateway_ip, subnet_ip))
		except:
				output = helpers.exception_info_value()
				helpers.log("Output: %s" % output)
				return False
		return True

	def openstack_add_subnet_external_pool(self,  netName, subnetName, start_ip, end_ip, external_gateway_ip, subnet_ip):
		'''create subnet
			Input:
				network name , Subnet name , Subnet (e.g app-net , app-net1, 50.0.0.0/24) , start IP = DHCP start IP address , end IP : DHCP end ip address)
			Return: id for created subnet
		'''
		t = test.Test()
		os1 = t.openstack_server('os1')
		try:
				os1.bash("neutron subnet-create %s --name %s --allocation-pool start=%s,end=%s --gateway %s %s" % (netName, subnetName, start_ip, end_ip, external_gateway_ip, subnet_ip))
		except:
				output = helpers.exception_info_value()
				helpers.log("Output: %s" % output)
				return False
		return True
	
	def openstack_delete_subnet(self, subnetName):
		'''create subnet
			Input:
				network name , Subnet name , Subnet (e.g app-net , app-net1, 50.0.0.0/24)
			Return: id for created subnet
		'''
		t = test.Test()
		os1 = t.openstack_server('os1')
		try:
				os1.bash("neutron subnet-delete %s" % (subnetName))
		except:
				output = helpers.exception_info_value()
				helpers.log("Output: %s" % output)
				return False
		return True
	
	
	def openstack_add_keypair(self, keypairName, pathToSave):
		'''Generate openstack tenant keypair
			Input:
				For this function make sure to call source "open_rc or any rc file" to get the user name /password for that tenant
				`keypairName`			Keypair name
				`pathToSave`		Path to save public key on nova controller
			Return: no data is returned
		'''
		t = test.Test()
		os1 = t.openstack_server('os1')
		os1.bash("nova keypair-add %s > %s" % (keypairName, pathToSave))
		os1.bash("chmod 600 %s" % pathToSave)
		return True

	def openstack_delete_keypair(self, keypairName):
		'''delete a keypair
			Input:
				For this function make sure to call source "open_rc or any rc file" to get the user name /password for that tenant
				`keypairName`			Keypair name

			Return: no data is returned
		'''
		t = test.Test()
		os1 = t.openstack_server('os1')
		os1.bash("nova keypair-delete %s" % (keypairName))
		return True

	def openstack_add_secrule_icmp(self, secName):
		'''Adding security rule to exsisting security group name
			Input:
				exsisting security name
			Return: None
		'''
		t = test.Test()
		os1 = t.openstack_server('os1')
		os1.bash("nova secgroup-add-rule %s icmp -1 -1 0.0.0.0/0" % (secName))
		return True
	
	def openstack_add_router_gw(self, routerName, extName):
		'''set tenant router gateway
			Input:
				`routerId`			tenant router id
				`extNetId`		external network id
				root@nova-controller:~# neutron router-gateway-set ff25378d-8b0d-4192-8c33-78ea0eba8d0e 02f4a4d1-0930-43bf-94db-2d39b11c343d
S
				Set gateway for router ff25378d-8b0d-4192-8c33-78ea0eba8d0e
			Return: output of command results
		'''
		t = test.Test()
		os1 = t.openstack_server('os1')
		routerId = self.openstack_show_router(routerName)
		extId = self.openstack_show_net(extName)
		os1.bash("neutron router-gateway-set %s %s" % (routerId, extId))
		data = os1.bash_content()
		return data

	def openstack_delete_router_gw(self, routerName):
		'''set tenant router gateway
			Input:
				`routerId`			tenant router id
				`extNetId`		external network id
				neutron router-gateway-clear ff25378d-8b0d-4192-8c33-78ea0eba8d0e
				Removed gateway from router ff25378d-8b0d-4192-8c33-78ea0eba8d0e
			Return: output of command results
			All of these commands will assume you have the openrc file sourced , make sure to source that file in the script test suite setup or test setup
		'''
		t = test.Test()
		os1 = t.openstack_server('os1')
		routerId = self.openstack_show_router(routerName)
		os1.bash("neutron router-gateway-clear %s" % (routerId))
		data = os1.bash_content()
		return data


	def openstack_add_subnet_to_router(self, routerName, subnetName):
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
		routerId = self.openstack_show_router(routerName)
		subnetId = self.openstack_show_subnet(subnetName)
		try:
			os1.bash("neutron router-interface-add %s %s" % (routerId, subnetId))
			return True
		except:
			output = helpers.exception_info_value()
			helpers.log("Output: %s" % output)
			return False

	def openstack_delete_subnet_to_router(self, routerName, subnetName):
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
		routerId = self.openstack_show_router(routerName)
		subnetId = self.openstack_show_subnet(subnetName)
		try:
			os1.bash("neutron  router-interface-delete %s %s" % (routerId, subnetId))
		except:
			output = helpers.exception_info_value()
			helpers.log("Output: %s" % output)
			return False
		return True

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
		return True

	def openstack_add_instance(self, imageName, netName, instanceName):
		'''delete instance
			Input:
				imageName : e.g cirros , ubuntu etc
				keypairName: keypair created in the testcase
				subnetName : subnet name created during the test
				instanceName: any name to identigy the instance
				flavor selection : 1:tiny , 2:small, 3:medium , 4: large
			Return: True
		'''
		t = test.Test()
		os1 = t.openstack_server('os1')
		imageId = self.openstack_show_image(imageName)
		netId = self.openstack_show_net(netName)
		os1.bash("nova boot --flavor 2 --image %s --nic net-id=%s %s" % (imageId, netId, instanceName))
		return True

	def openstack_delete_instance(self, instanceName):
		'''delete instance
			Input:
				source the tenant rc file which which includes , tenant name , user, passowrd
				`instanceName`			instance name to be deleted.
			Return: empty string
		'''
		t = test.Test()
		os1 = t.openstack_server('os1')
		try:
			os1.bash("nova delete %s" % (instanceName))
		except:
			output = helpers.exception_info_value()
			helpers.log("Output: %s" % output)
			return True
		return True

	def openstack_verify_tenant(self, tenantName):
		'''function to verify tenant in BSN controller
			Input:
				tenant Name
			Return: verify the tenant created in BSN controller
		'''
		t = test.Test()
		c = t.controller('master')
		url = '/api/v1/data/controller/applications/bcf/info/endpoint-manager/tenant'
		c.rest.get(url)
		data = c.rest.content()
		tenantId = self.openstack_show_tenant(tenantName)
		for i in range(0, len(data)):
			if str(data[i]["name"]) == str(tenantId):
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
			url = '/api/v1/data/controller/applications/bcf/info/endpoint-manager/segment[tenant="%s"]' % (tenantId)
			c.rest.get(url)
			data = c.rest.content()
			for i in range(0,len(data)):
				if  str(data[i]["name"]) == str(netId):
					helpers.log("Pass: Openstack networks are present in the BSN controller")
					return True
				else:
					continue
		else:
			url = '/api/v1/data/controller/applications/bcf/info/endpoint-manager/tenant'
			c.rest.get(url)
			data = c.rest.content()
			for i in range(0,len(data)):
				if data[i]["name"] != tenantId:
					helpers.log("Expected vns is deleted from the controller")
					return True
				else:
					helpers.log("Expected vns is not deleted from the controller")
					return False

	def openstack_verify_endpoint(self, instanceName, netName):
		'''function to verify endpoint in BSN controller
			Input:
				instance Name
			Return: verify the endpoint is created and active
		'''
		t = test.Test()
		c = t.controller('master')
		instanceIp = self.openstack_show_instance_ip(instanceName, netName)
		url = '/api/v1/data/controller/applications/bcf/info/endpoint-manager/endpoint[ip="%s"]' % (instanceIp)
		c.rest.get(url)
		data = c.rest.content()
		if len(data) != 0:
			if str(data[0]["ip-address"][0]["ip-address"]) == str(instanceIp):
#				if str(data[0]["state"]) == "Active":
					helpers.log("Pass:VM Instance endpoints are present")
					return True
#				else:
#					helpers.test_failure("VM Instance Endpoint state is Attachement Down")
			else:
				helpers.test_failure("VM Instance endpoint IP does not match")
				return False
		else:
			helpers.test_failure("Expected VM endpoints are not present in BCF controller")
			return False

	def openstack_verify_router(self, routerName):
		'''verify router creation status through horizon
			Input:router name
			Output : Check the status to "Active"
		'''
		t = test.Test()
		os1 = t.openstack_server('os1')
		result = os1.bash("neutron router-show %s" % (routerName))
		output = result["content"]
		match = re.search(r'Unable to find router with name', output)
		if match:
			helpers.log("router Not found")
			return ''
		else:
			out_dict = helpers.openstack_convert_table_to_dict(output)
			if out_dict["status"]["value"] == "ACTIVE":
				helpers.log("Pass: Router is active in the tenant")
				return True
			else:
				helpers.test_failure("Fail: router status is not active")
				return False

	def openstack_verify_router_interface(self, subnetName):
		'''verify router gateway IP creaetd in endpoint
			Input:subnetName
			Output : Verify the subnet gateway IP created in endpoint
		'''
		t = test.Test()
		c = t.controller('master')
		subnetIp = self.openstack_show_subnet_ip(subnetName)
		url = '/api/v1/data/controller/applications/bcf/info/endpoint-manager/endpoint[ip="%s"]' % (subnetIp)
		c.rest.get(url)
		data = c.rest.content()
		if len(data) != 0:		
			if str(data[0]["ip-address"][0]["ip-address"]) == str(subnetIp) and str(data[0]["ip-address"][0]["ip-state"]) == "static":
#				if str(data[0]["state"]) == "Active":
					helpers.log("Pass: Router interface creaetd as endpoint in controller")
					return True
#				else:
#					helpers.test_failure("Router interface state is not L2 only")
			else:
				helpers.log("Fail:router interface not present in controller endpoint table")
				return False
		else:
			helpers.log("Expected endpoint is not present in BCF controller")
			return False
	
	def openstack_tenant_scale(self, count, name='p'):
		'''Function to add multiple tenants based on count
		   Input: count and name
		   Output: project will be added to neutron server
		'''
		t = test.Test()
		os1 = t.openstack_server('os1')
		count = int(count)
		i = 1
		while (i <= count):
			tenant = name
			tenant += str(i)
			os1.bash("keystone tenant-create --name %s" % (tenant))
			i = i + 1
		return True

	def openstack_tenant_scale_delete(self, count, name='p'):
		'''Function to add multiple tenants based on count
		   Input: count and name
		   Output: project will be added to neutron server
		'''
		t = test.Test()
		os1 = t.openstack_server('os1')
		count = int(count)
		i = 1
		while (i <= count):
			tenant = name
			tenant += str(i)
			os1.bash("keystone tenant-delete %s" % (tenant))
			i = i + 1
		return True
	
	def openstack_segment_scale(self, tenantName, subnet, count, name='n'):
		'''Function to create multiple segments in a given tenant
			Input: tenantName , count , name starts with segment
			Output: given number of segments created in neutron server using neutron command
	    '''
		t = test.Test()
		os1 = t.openstack_server('os1')
		tenantId = self.openstack_show_tenant(tenantName)
		count = int(count)
		i = 1
		j = 0
		k = 0
		while (i <= count):
			netName = name
			netName += str(i)
			try:
				os1.bash("neutron net-create --tenant-id %s %s " % (tenantId, netName))
				helpers.sleep(2)
			except:
				output = helpers.exception_info_value()
				helpers.log("Output: %s" % output)
				return False
			ipaddr = "%s.%s.%s.0" % (subnet, j, k)
			subnet_ip = ipaddr + "/" + str(24)
			try:
				os1.bash("neutron subnet-create --tenant-id %s --name %s %s %s" % (tenantId, netName, netName, subnet_ip))
				helpers.sleep(2)
			except:
				output = helpers.exception_info_value()
				helpers.log("Output: %s" % output)
				return False
			k = k + 1
			if k == 254:
				j = j + 1
				k = 0
			#else:
			#	continue
			i = i + 1
		return True
			
	def openstack_verify_external_router_interface(self, routerName):
		'''verify interface creation through horizon and check endpoints created in BCF controller.
			Input:router name
			Output : Verify the specific endpoint created in BCF controller
		'''
		t = test.Test()
		c = t.controller('master')
		os1 = t.openstack_server('os1')
		content = os1.bash("neutron router-port-list %s" % (routerName))['content']
		output = helpers.strip_cli_output(content).strip()
		helpers.log("*** output: '%s'" % output)
		if output != '':
			out_dict = helpers.openstack_convert_table_to_dict(output)
			ip_list = []
			for key, value in out_dict.items():
				fixed_ips_str = value['fixed_ips']
				fixed_ips_dict = helpers.from_json(fixed_ips_str)
				ip_list.append(fixed_ips_dict['ip_address'])
			url = '/api/v1/data/controller/applications/bcf/info/endpoint-manager/endpoint'
			c.rest.get(url)
			data = c.rest.content()
			endpoint_ip_list = []
			for i in range(0,len(data)):
				for j in range(0,len(data[i]["ip-address"])):
					endpoint_ip_list.append(data[i]["ip-address"][j]["ip-address"])						
			ip_common = list(set(ip_list).intersection(set(endpoint_ip_list)))
			if len(ip_common) == len(ip_list):
				helpers.log("Pass:All router interface created as endpoint in BCF controller")
				return True
			else:
				helpers.test_failure("Fail:All router interface not present in BCF endpoint")
				return False
		else:
			url = '/api/v1/data/controller/applications/bcf/info/endpoint-manager/endpoint'
			c.rest.get(url)
			data = c.rest.content()
			endpoint_ip_list = []
			for i in range(0,len(data)):
				for j in range(0,len(data[i]["ip-address"])):
					endpoint_ip_list.append(data[i]["ip-address"][j]["ip-address"])
			if len(endpoint_ip_list) == 0:
				helpers.log("Router gateway endpoints are removed from BCF controller")
				return True
			else:
				helpers.log("Router gateway endpoints are not removed from BCF controller")
				return False
	
	def openstack_segment_scale_delete(self, count, name='n'):
		'''Function to create multiple segments in a given tenant
			Input: tenantName , count , name starts with segment
			Output: given number of segments created in neutron server using neutron command
	    '''
		t = test.Test()
		os1 = t.openstack_server('os1')
		count = int(count)
		i = 1
		while (i <= count):
			netName = name
			netName += str(i)
			try:
				os1.bash("neutron net-delete %s " % (netName))
				helpers.sleep(2)
			except:
				output = helpers.exception_info_value()
				helpers.log("Output: %s" % output)
				return False
			i = i + 1
		return True			
		
	def openstack_verify_segment_scale(self, tenantName, count):
		'''Function to verify multiple segments in the controller
			Input: tenantName , count , 
			Output: show tenant will count the no of segments created in controller
	    '''
		t = test.Test()
		c = t.controller('master')
		count = int(count)
		if str(tenantName) != "global":
			tenantId = self.openstack_show_tenant(tenantName)
			url = '/api/v1/data/controller/applications/bcf/info/endpoint-manager/segment[tenant="%s"]' % (tenantId)
			c.rest.get(url)
			data = c.rest.content()
			if len(data) == count:
				helpers.test_log("All Openstack segments are present in controller")
				return True	
			else:
				helpers.test_failure("All Openstack segments are not present in controller")
				return False
		else:
			url = '/api/v1/data/controller/applications/bcf/info/endpoint-manager/segment[tenant="global"]'
			c.rest.get(url)
			data = c.rest.content()
			if len(data) == count:
				helpers.test_log("All Openstack segments are present in controller")
				return True	
			else:
				helpers.test_failure("All Openstack segments are not present in controller")
				return False
		
	def openstack_router_scale(self, extName, count, tName='p', rname='r'):
		'''Function to add multiple routers to each tenant
		   Input: count and external network
		   Output: routers will be added to each tenants and create a getway to external network for each tenant router
		'''
		t = test.Test()
		os1 = t.openstack_server('os1')
		extId = self.openstack_show_net(extName)
		count = int(count)
		i = 1
		while (i <= count):
			routerName = rname
			tenantName = tName
			tenantName += str(i)
			routerName += str(i)
			tenantId = self.openstack_show_tenant(tenantName)
			os1.bash("neutron router-create --tenant-id %s %s" % (tenantId, routerName))
			helpers.sleep(5)
			routerId = self.openstack_show_router(routerName)
			os1.bash("neutron router-gateway-set %s %s" % (routerId, extId))
			i = i + 1
		return True
	
	def openstack_router_scale_delete(self, count, rname='r'):
		'''Function to delete all routers for each tenant
		   Input: count 
		   Output:routers will be deleted for each tenant
		'''
		t = test.Test()
		os1 = t.openstack_server('os1')
		count = int(count)
		i = 1
		while (i <= count):
			routerName = rname
			routerName += str(i)
			routerId = self.openstack_show_router(routerName)
			os1.bash("neutron router-gateway-clear %s" % (routerId))
			helpers.sleep(5)
			os1.bash("neutron router-delete %s" % (routerName))
			i = i + 1
		return True
	
	def openstack_interface_to_router_scale(self, routerName, count, name='n'):
		'''Function to add multiple router interfaces to single tenant
		   Input: count and name of the tenant router
		   Output: L3 interfaces will be added to tenant router
		'''
		t = test.Test()
		os1 = t.openstack_server('os1')
		routerId = self.openstack_show_router(routerName)
		count = int(count)
		i = 1
		while (i <= count):
			subnetName = name
			subnetName += str(i)
			subnetId = self.openstack_show_subnet(subnetName)
			os1.bash("neutron router-interface-add %s %s" % (routerId, subnetId))
			helpers.sleep(3)
			i = i + 1
		return True
		
	def openstack_interface_to_router_scale_delete(self, routerName, count, name='n'):
		'''Function to delete all router interfaces from tenant router
		   Input: count and router name
		   Output: all interfaces will be deleted from tenant router
		'''
		t = test.Test()
		os1 = t.openstack_server('os1')
		routerId = self.openstack_show_router(routerName)
		count = int(count)
		i = 1
		while (i <= count):
			subnetName = name
			subnetName += str(i)
			subnetId = self.openstack_show_subnet(subnetName)
			os1.bash("neutron  router-interface-delete %s %s" % (routerId, subnetId))
			helpers.sleep(3)
			i = i + 1
		return True
	
	def openstack_multiple_scale(self, subnet, tcount, ncount, tname='p', name='n'):
		'''Function to create multiple segments in a given tenant
			Input: tenantName , count , name starts with segment
			Output: given number of segments created in neutron server using neutron command
	    '''
		t = test.Test()
		os1 = t.openstack_server('os1')
		tcount = int(tcount)
		ncount = int(ncount)
		ncount_increment = ncount
		i = 1
		j = 0
		k = 0
		h = 1
		while (i <= tcount):
			tenant = tname
			tenant += str(i)
			while (h <= ncount):
				tenantId = self.openstack_show_tenant(tenant)
				netName = name
				netName += str(h)
				try:
					os1.bash("neutron net-create --tenant-id %s %s " % (tenantId, netName))
					helpers.sleep(1)
				except:
					output = helpers.exception_info_value()
					helpers.log("Output: %s" % output)
					return False
				ipaddr = "%s.%s.%s.0" % (subnet, j, k)
				subnet_ip = ipaddr + "/" + str(24)
				try:
					os1.bash("neutron subnet-create --tenant-id %s --name %s %s %s" % (tenantId, netName, netName, subnet_ip))
					helpers.sleep(1)
				except:
					output = helpers.exception_info_value()
					helpers.log("Output: %s" % output)
					return False
				k = k + 1
				if k == 254:
					j = j + 1
					k = 0
				h = h + 1
			i = i + 1
			ncount = ncount + ncount_increment 
			
		return True

	def openstack_multiple_scale_delete(self, tcount, ncount, tname='p', name='n'):
		'''Function to create multiple segments in a given tenant
			Input: tenantName , count , name starts with segment
			Output: given number of segments created in neutron server using neutron command
	    '''
		t = test.Test()
		os1 = t.openstack_server('os1')
		tcount = int(tcount)
		ncount = int(ncount)
		i = 1
		h = 1
		while (i <= tcount):
			tenant = tname
			tenant += str(i)
			while (h <= ncount):
				name += str(i)
				netName = name
				netName += str(h)
				try:
					os1.bash("neutron net-delete %s " % (netName))
					helpers.sleep(1)
				except:
					output = helpers.exception_info_value()
					helpers.log("Output: %s" % output)
					return False
				h = h + 1
			i = i + 1
			h = 1
		return True
	
	def openstack_compute_node_portgroup(self, instanceName, netName):
		'''Function to extract the port group and its members which VM instance belongs
		Input: openstack network name and Instance name
		Output: list of port group members in dictionary format
		'''
		t = test.Test()
		c = t.controller('master')
		instanceIp = self.openstack_show_instance_ip(instanceName, netName)
		url = '/api/v1/data/controller/applications/bcf/info/endpoint-manager/endpoint[ip="%s"]' % (instanceIp)
		c.rest.get(url)
		data = c.rest.content()
		portgroup_members = {}
		port_group_name = str(data[0]["port-group"])
		url1 = '/api/v1/data/controller/applications/bcf/info/fabric/port-group[name="%s"]' % (port_group_name)
		c.rest.get(url1)
		data1 = c.rest.content()
		helpers.log("length=%d" % len(data1[0]["interface"]))
		for i in range(0, len(data1[0]["interface"])):
			k, v = data1[0]["interface"][i]["switch-name"], data1[0]["interface"][i]["interface-name"]
			portgroup_members[k] = v 
		return portgroup_members
	
	def openstack_verify_multiple_scale(self, tcount, ncount, tname='p'):
		'''Function to verify total number of segment in each tenant
			Input: tenantName , count , expected network count
			Output: verify each tenant with expected network count in each tenant
	    '''
		t = test.Test()
		c = t.controller('master')
		os1 = t.openstack_server('os1')
		tcount = int(tcount)
		ncount = int(ncount)
		i = 1
		while (i <= tcount):
			tenant = tname
			tenant += str(i)
			tenantId = self.openstack_show_tenant(tenant)
			url = '/api/v1/data/controller/applications/bcf/info/endpoint-manager/tenant[name="%s"]' % (tenantId)
			c.rest.get(url)
			data = c.rest.content()
			if int(data[0]["segment-count"]) != ncount:
				helpers.test_failure("All Openstack segments are not present in a tenant")
				return False
			i = i + 1
		return True
	
	def openstack_t6_verify_router_interface(self, tenantName, subnetName):
		'''verify router gateway IP creaetd as logical router interface
			Input:subnetName
			Output : Verify the subnet gateway IP created in endpoint
		'''
		t = test.Test()
		c = t.controller('master')
		os1 = t.openstack_server('os1')
		tenantId = self.openstack_show_tenant(tenantName)
		subnetIp = self.openstack_show_subnet_ip(subnetName)
		subnet_cidr = self.openstack_show_subnet_cidr(subnetName)
		netId = self.openstack_show_subnet(subnetName)
		subnet_mask = subnet_cidr.split('/')
		interface_ip = subnetIp + "/" + subnet_mask[1]
		url = '/api/v1/data/controller/applications/bcf/info/logical-router-manager/logical-router[name="%s"]/segment-interface' % (tenantId)
		c.rest.get(url)
		data = c.rest.content()
		if len(data) != 0:		
			for i in range(0,len(data)):
				if data[0][i]["segment"] == str(netId) and data[0][i]["ip-cidr"] == interface_ip and data[0][i]["state"] == "Active":
					helpers.log("L3 Interface is present in BCF controller for the network")
					return True
				else:
					continue
			return False
		else:
			helpers.log("No Logical router interface are present")
			return False
		
	def openstack_l3agent_scale_test(self, extName, tcount, rcount, subnet, tName='p', rName='r', nName='n', sName='s'):
		'''Function to add multiple routers to each tenant
		   Input: no of tenant count and external network
		   Output: routers will be added to each tenants and create a getway to external network for each tenant router
		'''
		t = test.Test()
		os1 = t.openstack_server('os1')
		extId = self.openstack_show_net(extName)
		tcount = int(tcount)
		i = 1
		rcount = int(rcount)
		subnet = int(subnet)
		while (i <= tcount):
			tenantName = tName
			tenantName += str(i)
			tenantId = self.openstack_show_tenant(tenantName)
			subnet = subnet + 1
			j = 1
			while (j <= rcount): 
				r_name = rName
				n_name = nName
				s_name = sName
				r_name += str(j)
				n_name += str(j)
				s_name += str(j)
				routerName = r_name + "_" + tenantId
				netName = n_name + "_" + tenantId
				subnetName = s_name + "_" + tenantId 
				ipaddr = "35.%d.%d.0" % (subnet, j)
				subnet_ip = ipaddr + "/" + str(24)
				os1.bash("neutron net-create --tenant-id %s %s" % (tenantId, netName))
				helpers.sleep(5)
				os1.bash("neutron subnet-create --tenant-id %s --name %s %s %s" % (tenantId, subnetName, netName, subnet_ip))
				os1.bash("neutron router-create --tenant-id %s %s" % (tenantId, routerName))
				helpers.sleep(5)
				routerId = self.openstack_show_router(routerName)
				subnetId = self.openstack_show_subnet(subnetName)
				os1.bash("neutron router-interface-add %s %s" % (routerId, subnetId))
				helpers.sleep(5)
				os1.bash("neutron router-gateway-set %s %s" % (routerId, extId))
				j = j + 1
			i = i + 1
		return True
	
	def openstack_l3agent_scale_test_delete(self, tcount, rcount, tName='p', rName='r', nName='n', sName='s'):
		'''Function to add multiple routers to each tenant
		   Input: no of tenant count and external network
		   Output: routers will be added to each tenants and create a getway to external network for each tenant router
		'''
		t = test.Test()
		os1 = t.openstack_server('os1')
		tcount = int(tcount)
		i = 1
		rcount = int(rcount)
		while (i <= tcount):
			tenantName = tName
			tenantName += str(i)
			tenantId = self.openstack_show_tenant(tenantName)
			j = 1
			while (j <= rcount): 
				r_name = rName
				n_name = nName
				s_name = sName
				r_name += str(j)
				n_name += str(j)
				s_name += str(j)
				routerName = r_name + "_" + tenantId
				netName = n_name + "_" + tenantId
				subnetName = s_name + "_" + tenantId 
				routerId = self.openstack_show_router(routerName)
				subnetId = self.openstack_show_subnet(subnetName)
				os1.bash("neutron router-gateway-clear %s" % (routerId))
				os1.bash("neutron  router-interface-delete %s %s" % (routerId, subnetId))
				helpers.sleep(3)
				os1.bash("neutron router-delete %s" % (routerName))
				os1.bash("neutron subnet-delete %s" % (subnetName))
				helpers.sleep(3)
				os1.bash("neutron net-delete %s " % (netName))
				helpers.sleep(3)
				j = j + 1
			i = i + 1
		return True
				
		
		