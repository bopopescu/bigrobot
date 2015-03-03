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


"""List private gateways"""
from baseCmd import *
from baseResponse import *
class listPrivateGatewaysCmd (baseCmd):
    typeInfo = {}
    def __init__(self):
        self.isAsync = "false"
        """list resources by account. Must be used with the domainId parameter."""
        self.account = None
        self.typeInfo['account'] = 'string'
        """list only resources belonging to the domain specified"""
        self.domainid = None
        self.typeInfo['domainid'] = 'uuid'
        """list private gateway by id"""
        self.id = None
        self.typeInfo['id'] = 'uuid'
        """list gateways by ip address"""
        self.ipaddress = None
        self.typeInfo['ipaddress'] = 'string'
        """defaults to false, but if true, lists all resources from the parent specified by the domainId till leaves."""
        self.isrecursive = None
        self.typeInfo['isrecursive'] = 'boolean'
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
        """list objects by project"""
        self.projectid = None
        self.typeInfo['projectid'] = 'uuid'
        """list gateways by state"""
        self.state = None
        self.typeInfo['state'] = 'string'
        """list gateways by vlan"""
        self.vlan = None
        self.typeInfo['vlan'] = 'string'
        """list gateways by vpc"""
        self.vpcid = None
        self.typeInfo['vpcid'] = 'uuid'
        self.required = []

class listPrivateGatewaysResponse (baseResponse):
    typeInfo = {}
    def __init__(self):
        """the id of the private gateway"""
        self.id = None
        self.typeInfo['id'] = 'string'
        """the account associated with the private gateway"""
        self.account = None
        self.typeInfo['account'] = 'string'
        """ACL Id set for private gateway"""
        self.aclid = None
        self.typeInfo['aclid'] = 'string'
        """the domain associated with the private gateway"""
        self.domain = None
        self.typeInfo['domain'] = 'string'
        """the ID of the domain associated with the private gateway"""
        self.domainid = None
        self.typeInfo['domainid'] = 'string'
        """the gateway"""
        self.gateway = None
        self.typeInfo['gateway'] = 'string'
        """the private gateway's ip address"""
        self.ipaddress = None
        self.typeInfo['ipaddress'] = 'string'
        """the private gateway's netmask"""
        self.netmask = None
        self.typeInfo['netmask'] = 'string'
        """the physical network id"""
        self.physicalnetworkid = None
        self.typeInfo['physicalnetworkid'] = 'string'
        """the project name of the private gateway"""
        self.project = None
        self.typeInfo['project'] = 'string'
        """the project id of the private gateway"""
        self.projectid = None
        self.typeInfo['projectid'] = 'string'
        """Souce Nat enable status"""
        self.sourcenatsupported = None
        self.typeInfo['sourcenatsupported'] = 'boolean'
        """State of the gateway, can be Creating, Ready, Deleting"""
        self.state = None
        self.typeInfo['state'] = 'string'
        """the network implementation uri for the private gateway"""
        self.vlan = None
        self.typeInfo['vlan'] = 'string'
        """VPC the private gateaway belongs to"""
        self.vpcid = None
        self.typeInfo['vpcid'] = 'string'
        """zone id of the private gateway"""
        self.zoneid = None
        self.typeInfo['zoneid'] = 'string'
        """the name of the zone the private gateway belongs to"""
        self.zonename = None
        self.typeInfo['zonename'] = 'string'

