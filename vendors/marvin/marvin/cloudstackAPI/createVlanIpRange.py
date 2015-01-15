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


"""Creates a VLAN IP range."""
from baseCmd import *
from baseResponse import *
class createVlanIpRangeCmd (baseCmd):
    typeInfo = {}
    def __init__(self):
        self.isAsync = "false"
        """account who will own the VLAN. If VLAN is Zone wide, this parameter should be ommited"""
        self.account = None
        self.typeInfo['account'] = 'string'
        """domain ID of the account owning a VLAN"""
        self.domainid = None
        self.typeInfo['domainid'] = 'uuid'
        """the ending IP address in the VLAN IP range"""
        self.endip = None
        self.typeInfo['endip'] = 'string'
        """the ending IPv6 address in the IPv6 network range"""
        self.endipv6 = None
        self.typeInfo['endipv6'] = 'string'
        """true if VLAN is of Virtual type, false if Direct"""
        self.forvirtualnetwork = None
        self.typeInfo['forvirtualnetwork'] = 'boolean'
        """the gateway of the VLAN IP range"""
        self.gateway = None
        self.typeInfo['gateway'] = 'string'
        """the CIDR of IPv6 network, must be at least /64"""
        self.ip6cidr = None
        self.typeInfo['ip6cidr'] = 'string'
        """the gateway of the IPv6 network. Required for Shared networks and Isolated networks when it belongs to VPC"""
        self.ip6gateway = None
        self.typeInfo['ip6gateway'] = 'string'
        """the netmask of the VLAN IP range"""
        self.netmask = None
        self.typeInfo['netmask'] = 'string'
        """the network id"""
        self.networkid = None
        self.typeInfo['networkid'] = 'uuid'
        """the physical network id"""
        self.physicalnetworkid = None
        self.typeInfo['physicalnetworkid'] = 'uuid'
        """optional parameter. Have to be specified for Direct Untagged vlan only."""
        self.podid = None
        self.typeInfo['podid'] = 'uuid'
        """project who will own the VLAN. If VLAN is Zone wide, this parameter should be ommited"""
        self.projectid = None
        self.typeInfo['projectid'] = 'uuid'
        """the beginning IP address in the VLAN IP range"""
        self.startip = None
        self.typeInfo['startip'] = 'string'
        """the beginning IPv6 address in the IPv6 network range"""
        self.startipv6 = None
        self.typeInfo['startipv6'] = 'string'
        """the ID or VID of the VLAN. If not specified, will be defaulted to the vlan of the network or if vlan of the network is null - to Untagged"""
        self.vlan = None
        self.typeInfo['vlan'] = 'string'
        """the Zone ID of the VLAN IP range"""
        self.zoneid = None
        self.typeInfo['zoneid'] = 'uuid'
        self.required = []

class createVlanIpRangeResponse (baseResponse):
    typeInfo = {}
    def __init__(self):
        """the ID of the VLAN IP range"""
        self.id = None
        self.typeInfo['id'] = 'string'
        """the account of the VLAN IP range"""
        self.account = None
        self.typeInfo['account'] = 'string'
        """the description of the VLAN IP range"""
        self.description = None
        self.typeInfo['description'] = 'string'
        """the domain name of the VLAN IP range"""
        self.domain = None
        self.typeInfo['domain'] = 'string'
        """the domain ID of the VLAN IP range"""
        self.domainid = None
        self.typeInfo['domainid'] = 'string'
        """the end ip of the VLAN IP range"""
        self.endip = None
        self.typeInfo['endip'] = 'string'
        """the end ipv6 of the VLAN IP range"""
        self.endipv6 = None
        self.typeInfo['endipv6'] = 'string'
        """the virtual network for the VLAN IP range"""
        self.forvirtualnetwork = None
        self.typeInfo['forvirtualnetwork'] = 'boolean'
        """the gateway of the VLAN IP range"""
        self.gateway = None
        self.typeInfo['gateway'] = 'string'
        """the cidr of IPv6 network"""
        self.ip6cidr = None
        self.typeInfo['ip6cidr'] = 'string'
        """the gateway of IPv6 network"""
        self.ip6gateway = None
        self.typeInfo['ip6gateway'] = 'string'
        """the netmask of the VLAN IP range"""
        self.netmask = None
        self.typeInfo['netmask'] = 'string'
        """the network id of vlan range"""
        self.networkid = None
        self.typeInfo['networkid'] = 'string'
        """the physical network this belongs to"""
        self.physicalnetworkid = None
        self.typeInfo['physicalnetworkid'] = 'string'
        """the Pod ID for the VLAN IP range"""
        self.podid = None
        self.typeInfo['podid'] = 'string'
        """the Pod name for the VLAN IP range"""
        self.podname = None
        self.typeInfo['podname'] = 'string'
        """the project name of the vlan range"""
        self.project = None
        self.typeInfo['project'] = 'string'
        """the project id of the vlan range"""
        self.projectid = None
        self.typeInfo['projectid'] = 'string'
        """the start ip of the VLAN IP range"""
        self.startip = None
        self.typeInfo['startip'] = 'string'
        """the start ipv6 of the VLAN IP range"""
        self.startipv6 = None
        self.typeInfo['startipv6'] = 'string'
        """the ID or VID of the VLAN."""
        self.vlan = None
        self.typeInfo['vlan'] = 'string'
        """the Zone ID of the VLAN IP range"""
        self.zoneid = None
        self.typeInfo['zoneid'] = 'string'

