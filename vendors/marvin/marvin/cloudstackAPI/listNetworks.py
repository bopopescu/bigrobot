# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.


"""Lists all available networks."""
from baseCmd import *
from baseResponse import *
class listNetworksCmd (baseCmd):
    typeInfo = {}
    def __init__(self):
        self.isAsync = "false"
        """list resources by account. Must be used with the domainId parameter."""
        self.account = None
        self.typeInfo['account'] = 'string'
        """list networks by ACL (access control list) type. Supported values are Account and Domain"""
        self.acltype = None
        self.typeInfo['acltype'] = 'string'
        """list networks available for vm deployment"""
        self.canusefordeploy = None
        self.typeInfo['canusefordeploy'] = 'boolean'
        """list resources by display flag; only ROOT admin is eligible to pass this parameter"""
        self.displaynetwork = None
        self.typeInfo['displaynetwork'] = 'boolean'
        """list only resources belonging to the domain specified"""
        self.domainid = None
        self.typeInfo['domainid'] = 'uuid'
        """the network belongs to vpc"""
        self.forvpc = None
        self.typeInfo['forvpc'] = 'boolean'
        """list networks by id"""
        self.id = None
        self.typeInfo['id'] = 'uuid'
        """defaults to false, but if true, lists all resources from the parent specified by the domainId till leaves."""
        self.isrecursive = None
        self.typeInfo['isrecursive'] = 'boolean'
        """true if network is system, false otherwise"""
        self.issystem = None
        self.typeInfo['issystem'] = 'boolean'
        """List by keyword"""
        self.keyword = None
        self.typeInfo['keyword'] = 'string'
        """If set to false, list only resources belonging to the command's caller; if set to true - list resources that the caller is authorized to see. Default value is false"""
        self.listall = None
        self.typeInfo['listall'] = 'boolean'
        """"""
        self.page = None
        self.typeInfo['page'] = 'integer'
        """"""
        self.pagesize = None
        self.typeInfo['pagesize'] = 'integer'
        """list networks by physical network id"""
        self.physicalnetworkid = None
        self.typeInfo['physicalnetworkid'] = 'uuid'
        """list objects by project"""
        self.projectid = None
        self.typeInfo['projectid'] = 'uuid'
        """list networks by restartRequired"""
        self.restartrequired = None
        self.typeInfo['restartrequired'] = 'boolean'
        """true if need to list only networks which support specifying ip ranges"""
        self.specifyipranges = None
        self.typeInfo['specifyipranges'] = 'boolean'
        """list networks supporting certain services"""
        self.supportedservices = []
        self.typeInfo['supportedservices'] = 'list'
        """List resources by tags (key/value pairs)"""
        self.tags = []
        self.typeInfo['tags'] = 'map'
        """type of the traffic"""
        self.traffictype = None
        self.typeInfo['traffictype'] = 'string'
        """the type of the network. Supported values are: Isolated and Shared"""
        self.type = None
        self.typeInfo['type'] = 'string'
        """List networks by VPC"""
        self.vpcid = None
        self.typeInfo['vpcid'] = 'uuid'
        """the Zone ID of the network"""
        self.zoneid = None
        self.typeInfo['zoneid'] = 'uuid'
        self.required = []

class listNetworksResponse (baseResponse):
    typeInfo = {}
    def __init__(self):
        """the id of the network"""
        self.id = None
        self.typeInfo['id'] = 'string'
        """the owner of the network"""
        self.account = None
        self.typeInfo['account'] = 'string'
        """ACL Id associated with the VPC network"""
        self.aclid = None
        self.typeInfo['aclid'] = 'string'
        """acl type - access type to the network"""
        self.acltype = None
        self.typeInfo['acltype'] = 'string'
        """Broadcast domain type of the network"""
        self.broadcastdomaintype = None
        self.typeInfo['broadcastdomaintype'] = 'string'
        """broadcast uri of the network. This parameter is visible to ROOT admins only"""
        self.broadcasturi = None
        self.typeInfo['broadcasturi'] = 'string'
        """list networks available for vm deployment"""
        self.canusefordeploy = None
        self.typeInfo['canusefordeploy'] = 'boolean'
        """Cloudstack managed address space, all CloudStack managed VMs get IP address from CIDR"""
        self.cidr = None
        self.typeInfo['cidr'] = 'string'
        """an optional field, whether to the display the network to the end user or not."""
        self.displaynetwork = None
        self.typeInfo['displaynetwork'] = 'boolean'
        """the displaytext of the network"""
        self.displaytext = None
        self.typeInfo['displaytext'] = 'string'
        """the first DNS for the network"""
        self.dns1 = None
        self.typeInfo['dns1'] = 'string'
        """the second DNS for the network"""
        self.dns2 = None
        self.typeInfo['dns2'] = 'string'
        """the domain name of the network owner"""
        self.domain = None
        self.typeInfo['domain'] = 'string'
        """the domain id of the network owner"""
        self.domainid = None
        self.typeInfo['domainid'] = 'string'
        """the network's gateway"""
        self.gateway = None
        self.typeInfo['gateway'] = 'string'
        """the cidr of IPv6 network"""
        self.ip6cidr = None
        self.typeInfo['ip6cidr'] = 'string'
        """the gateway of IPv6 network"""
        self.ip6gateway = None
        self.typeInfo['ip6gateway'] = 'string'
        """true if network is default, false otherwise"""
        self.isdefault = None
        self.typeInfo['isdefault'] = 'boolean'
        """list networks that are persistent"""
        self.ispersistent = None
        self.typeInfo['ispersistent'] = 'boolean'
        """true if network is system, false otherwise"""
        self.issystem = None
        self.typeInfo['issystem'] = 'boolean'
        """the name of the network"""
        self.name = None
        self.typeInfo['name'] = 'string'
        """the network's netmask"""
        self.netmask = None
        self.typeInfo['netmask'] = 'string'
        """the network CIDR of the guest network configured with IP reservation. It is the summation of CIDR and RESERVED_IP_RANGE"""
        self.networkcidr = None
        self.typeInfo['networkcidr'] = 'string'
        """the network domain"""
        self.networkdomain = None
        self.typeInfo['networkdomain'] = 'string'
        """availability of the network offering the network is created from"""
        self.networkofferingavailability = None
        self.typeInfo['networkofferingavailability'] = 'string'
        """true if network offering is ip conserve mode enabled"""
        self.networkofferingconservemode = None
        self.typeInfo['networkofferingconservemode'] = 'boolean'
        """display text of the network offering the network is created from"""
        self.networkofferingdisplaytext = None
        self.typeInfo['networkofferingdisplaytext'] = 'string'
        """network offering id the network is created from"""
        self.networkofferingid = None
        self.typeInfo['networkofferingid'] = 'string'
        """name of the network offering the network is created from"""
        self.networkofferingname = None
        self.typeInfo['networkofferingname'] = 'string'
        """the physical network id"""
        self.physicalnetworkid = None
        self.typeInfo['physicalnetworkid'] = 'string'
        """the project name of the address"""
        self.project = None
        self.typeInfo['project'] = 'string'
        """the project id of the ipaddress"""
        self.projectid = None
        self.typeInfo['projectid'] = 'string'
        """related to what other network configuration"""
        self.related = None
        self.typeInfo['related'] = 'string'
        """the network's IP range not to be used by CloudStack guest VMs and can be used for non CloudStack purposes"""
        self.reservediprange = None
        self.typeInfo['reservediprange'] = 'string'
        """true network requires restart"""
        self.restartrequired = None
        self.typeInfo['restartrequired'] = 'boolean'
        """true if network supports specifying ip ranges, false otherwise"""
        self.specifyipranges = None
        self.typeInfo['specifyipranges'] = 'boolean'
        """state of the network"""
        self.state = None
        self.typeInfo['state'] = 'string'
        """true if network can span multiple zones"""
        self.strechedl2subnet = None
        self.typeInfo['strechedl2subnet'] = 'boolean'
        """true if users from subdomains can access the domain level network"""
        self.subdomainaccess = None
        self.typeInfo['subdomainaccess'] = 'boolean'
        """the traffic type of the network"""
        self.traffictype = None
        self.typeInfo['traffictype'] = 'string'
        """the type of the network"""
        self.type = None
        self.typeInfo['type'] = 'string'
        """The vlan of the network. This parameter is visible to ROOT admins only"""
        self.vlan = None
        self.typeInfo['vlan'] = 'string'
        """VPC the network belongs to"""
        self.vpcid = None
        self.typeInfo['vpcid'] = 'string'
        """zone id of the network"""
        self.zoneid = None
        self.typeInfo['zoneid'] = 'string'
        """the name of the zone the network belongs to"""
        self.zonename = None
        self.typeInfo['zonename'] = 'string'
        """If a network is enabled for 'streched l2 subnet' then represents zones on which network currently spans"""
        self.zonesnetworkspans = None
        self.typeInfo['zonesnetworkspans'] = 'set'
        """the list of services"""
        self.service = []
        """the list of resource tags associated with network"""
        self.tags = []

class capability:
    def __init__(self):
        """"can this service capability value can be choosable while creatine network offerings"""
        self.canchooseservicecapability = None
        """"the capability name"""
        self.name = None
        """"the capability value"""
        self.value = None

class provider:
    def __init__(self):
        """"uuid of the network provider"""
        self.id = None
        """"true if individual services can be enabled/disabled"""
        self.canenableindividualservice = None
        """"the destination physical network"""
        self.destinationphysicalnetworkid = None
        """"the provider name"""
        self.name = None
        """"the physical network this belongs to"""
        self.physicalnetworkid = None
        """"services for this provider"""
        self.servicelist = None
        """"state of the network provider"""
        self.state = None

class service:
    def __init__(self):
        """"the service name"""
        self.name = None
        """"the list of capabilities"""
        self.capability = []
        """"can this service capability value can be choosable while creatine network offerings"""
        self.canchooseservicecapability = None
        """"the capability name"""
        self.name = None
        """"the capability value"""
        self.value = None
        """"the service provider name"""
        self.provider = []
        """"uuid of the network provider"""
        self.id = None
        """"true if individual services can be enabled/disabled"""
        self.canenableindividualservice = None
        """"the destination physical network"""
        self.destinationphysicalnetworkid = None
        """"the provider name"""
        self.name = None
        """"the physical network this belongs to"""
        self.physicalnetworkid = None
        """"services for this provider"""
        self.servicelist = None
        """"state of the network provider"""
        self.state = None

class tags:
    def __init__(self):
        """"the account associated with the tag"""
        self.account = None
        """"customer associated with the tag"""
        self.customer = None
        """"the domain associated with the tag"""
        self.domain = None
        """"the ID of the domain associated with the tag"""
        self.domainid = None
        """"tag key name"""
        self.key = None
        """"the project name where tag belongs to"""
        self.project = None
        """"the project id the tag belongs to"""
        self.projectid = None
        """"id of the resource"""
        self.resourceid = None
        """"resource type"""
        self.resourcetype = None
        """"tag value"""
        self.value = None

