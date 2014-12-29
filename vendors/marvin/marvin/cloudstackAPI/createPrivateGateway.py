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


"""Creates a private gateway"""
from baseCmd import *
from baseResponse import *
class createPrivateGatewayCmd (baseCmd):
    typeInfo = {}
    def __init__(self):
        self.isAsync = "true"
        """the gateway of the Private gateway"""
        """Required"""
        self.gateway = None
        self.typeInfo['gateway'] = 'string'
        """the IP address of the Private gateaway"""
        """Required"""
        self.ipaddress = None
        self.typeInfo['ipaddress'] = 'string'
        """the netmask of the Private gateway"""
        """Required"""
        self.netmask = None
        self.typeInfo['netmask'] = 'string'
        """the network implementation uri for the private gateway"""
        """Required"""
        self.vlan = None
        self.typeInfo['vlan'] = 'string'
        """the VPC network belongs to"""
        """Required"""
        self.vpcid = None
        self.typeInfo['vpcid'] = 'uuid'
        """the ID of the network ACL"""
        self.aclid = None
        self.typeInfo['aclid'] = 'uuid'
        """the uuid of the network offering to use for the private gateways network connection"""
        self.networkofferingid = None
        self.typeInfo['networkofferingid'] = 'uuid'
        """the Physical Network ID the network belongs to"""
        self.physicalnetworkid = None
        self.typeInfo['physicalnetworkid'] = 'uuid'
        """source NAT supported value. Default value false. If 'true' source NAT is enabled on the private gateway 'false': sourcenat is not supported"""
        self.sourcenatsupported = None
        self.typeInfo['sourcenatsupported'] = 'boolean'
        self.required = ["gateway","ipaddress","netmask","vlan","vpcid",]

class createPrivateGatewayResponse (baseResponse):
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

