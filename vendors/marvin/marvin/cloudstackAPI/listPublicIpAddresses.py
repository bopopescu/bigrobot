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


"""Lists all public ip addresses"""
from baseCmd import *
from baseResponse import *
class listPublicIpAddressesCmd (baseCmd):
    typeInfo = {}
    def __init__(self):
        self.isAsync = "false"
        """list resources by account. Must be used with the domainId parameter."""
        self.account = None
        self.typeInfo['account'] = 'string'
        """limits search results to allocated public IP addresses"""
        self.allocatedonly = None
        self.typeInfo['allocatedonly'] = 'boolean'
        """lists all public IP addresses associated to the network specified"""
        self.associatednetworkid = None
        self.typeInfo['associatednetworkid'] = 'uuid'
        """list only resources belonging to the domain specified"""
        self.domainid = None
        self.typeInfo['domainid'] = 'uuid'
        """list resources by display flag; only ROOT admin is eligible to pass this parameter"""
        self.fordisplay = None
        self.typeInfo['fordisplay'] = 'boolean'
        """list only ips used for load balancing"""
        self.forloadbalancing = None
        self.typeInfo['forloadbalancing'] = 'boolean'
        """the virtual network for the IP address"""
        self.forvirtualnetwork = None
        self.typeInfo['forvirtualnetwork'] = 'boolean'
        """lists ip address by id"""
        self.id = None
        self.typeInfo['id'] = 'uuid'
        """lists the specified IP address"""
        self.ipaddress = None
        self.typeInfo['ipaddress'] = 'string'
        """defaults to false, but if true, lists all resources from the parent specified by the domainId till leaves."""
        self.isrecursive = None
        self.typeInfo['isrecursive'] = 'boolean'
        """list only source nat ip addresses"""
        self.issourcenat = None
        self.typeInfo['issourcenat'] = 'boolean'
        """list only static nat ip addresses"""
        self.isstaticnat = None
        self.typeInfo['isstaticnat'] = 'boolean'
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
        """lists all public IP addresses by physical network id"""
        self.physicalnetworkid = None
        self.typeInfo['physicalnetworkid'] = 'uuid'
        """list objects by project"""
        self.projectid = None
        self.typeInfo['projectid'] = 'uuid'
        """lists all public IP addresses by state"""
        self.state = None
        self.typeInfo['state'] = 'string'
        """List resources by tags (key/value pairs)"""
        self.tags = []
        self.typeInfo['tags'] = 'map'
        """lists all public IP addresses by VLAN ID"""
        self.vlanid = None
        self.typeInfo['vlanid'] = 'uuid'
        """List ips belonging to the VPC"""
        self.vpcid = None
        self.typeInfo['vpcid'] = 'uuid'
        """lists all public IP addresses by Zone ID"""
        self.zoneid = None
        self.typeInfo['zoneid'] = 'uuid'
        self.required = []

class listPublicIpAddressesResponse (baseResponse):
    typeInfo = {}
    def __init__(self):
        """public IP address id"""
        self.id = None
        self.typeInfo['id'] = 'string'
        """the account the public IP address is associated with"""
        self.account = None
        self.typeInfo['account'] = 'string'
        """date the public IP address was acquired"""
        self.allocated = None
        self.typeInfo['allocated'] = 'date'
        """the ID of the Network associated with the IP address"""
        self.associatednetworkid = None
        self.typeInfo['associatednetworkid'] = 'string'
        """the name of the Network associated with the IP address"""
        self.associatednetworkname = None
        self.typeInfo['associatednetworkname'] = 'string'
        """the domain the public IP address is associated with"""
        self.domain = None
        self.typeInfo['domain'] = 'string'
        """the domain ID the public IP address is associated with"""
        self.domainid = None
        self.typeInfo['domainid'] = 'string'
        """is public ip for display to the regular user"""
        self.fordisplay = None
        self.typeInfo['fordisplay'] = 'boolean'
        """the virtual network for the IP address"""
        self.forvirtualnetwork = None
        self.typeInfo['forvirtualnetwork'] = 'boolean'
        """public IP address"""
        self.ipaddress = None
        self.typeInfo['ipaddress'] = 'string'
        """is public IP portable across the zones"""
        self.isportable = None
        self.typeInfo['isportable'] = 'boolean'
        """true if the IP address is a source nat address, false otherwise"""
        self.issourcenat = None
        self.typeInfo['issourcenat'] = 'boolean'
        """true if this ip is for static nat, false otherwise"""
        self.isstaticnat = None
        self.typeInfo['isstaticnat'] = 'boolean'
        """true if this ip is system ip (was allocated as a part of deployVm or createLbRule)"""
        self.issystem = None
        self.typeInfo['issystem'] = 'boolean'
        """the ID of the Network where ip belongs to"""
        self.networkid = None
        self.typeInfo['networkid'] = 'string'
        """the physical network this belongs to"""
        self.physicalnetworkid = None
        self.typeInfo['physicalnetworkid'] = 'string'
        """the project name of the address"""
        self.project = None
        self.typeInfo['project'] = 'string'
        """the project id of the ipaddress"""
        self.projectid = None
        self.typeInfo['projectid'] = 'string'
        """purpose of the IP address. In Acton this value is not null for Ips with isSystem=true, and can have either StaticNat or LB value"""
        self.purpose = None
        self.typeInfo['purpose'] = 'string'
        """State of the ip address. Can be: Allocatin, Allocated and Releasing"""
        self.state = None
        self.typeInfo['state'] = 'string'
        """virutal machine display name the ip address is assigned to (not null only for static nat Ip)"""
        self.virtualmachinedisplayname = None
        self.typeInfo['virtualmachinedisplayname'] = 'string'
        """virutal machine id the ip address is assigned to (not null only for static nat Ip)"""
        self.virtualmachineid = None
        self.typeInfo['virtualmachineid'] = 'string'
        """virutal machine name the ip address is assigned to (not null only for static nat Ip)"""
        self.virtualmachinename = None
        self.typeInfo['virtualmachinename'] = 'string'
        """the ID of the VLAN associated with the IP address. This parameter is visible to ROOT admins only"""
        self.vlanid = None
        self.typeInfo['vlanid'] = 'string'
        """the VLAN associated with the IP address"""
        self.vlanname = None
        self.typeInfo['vlanname'] = 'string'
        """virutal machine (dnat) ip address (not null only for static nat Ip)"""
        self.vmipaddress = None
        self.typeInfo['vmipaddress'] = 'string'
        """VPC the ip belongs to"""
        self.vpcid = None
        self.typeInfo['vpcid'] = 'string'
        """the ID of the zone the public IP address belongs to"""
        self.zoneid = None
        self.typeInfo['zoneid'] = 'string'
        """the name of the zone the public IP address belongs to"""
        self.zonename = None
        self.typeInfo['zonename'] = 'string'
        """the list of resource tags associated with ip address"""
        self.tags = []
        """the ID of the latest async job acting on this object"""
        self.jobid = None
        self.typeInfo['jobid'] = ''
        """the current status of the latest async job acting on this object"""
        self.jobstatus = None
        self.typeInfo['jobstatus'] = ''

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

