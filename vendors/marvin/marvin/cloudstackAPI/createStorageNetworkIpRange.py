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


"""Creates a Storage network IP range."""
from baseCmd import *
from baseResponse import *
class createStorageNetworkIpRangeCmd (baseCmd):
    typeInfo = {}
    def __init__(self):
        self.isAsync = "true"
        """the gateway for storage network"""
        """Required"""
        self.gateway = None
        self.typeInfo['gateway'] = 'string'
        """the netmask for storage network"""
        """Required"""
        self.netmask = None
        self.typeInfo['netmask'] = 'string'
        """UUID of pod where the ip range belongs to"""
        """Required"""
        self.podid = None
        self.typeInfo['podid'] = 'uuid'
        """the beginning IP address"""
        """Required"""
        self.startip = None
        self.typeInfo['startip'] = 'string'
        """the ending IP address"""
        self.endip = None
        self.typeInfo['endip'] = 'string'
        """Optional. The vlan the ip range sits on, default to Null when it is not specificed which means you network is not on any Vlan. This is mainly for Vmware as other hypervisors can directly reterive bridge from pyhsical network traffic type table"""
        self.vlan = None
        self.typeInfo['vlan'] = 'integer'
        self.required = ["gateway","netmask","podid","startip",]

class createStorageNetworkIpRangeResponse (baseResponse):
    typeInfo = {}
    def __init__(self):
        """the uuid of storage network IP range."""
        self.id = None
        self.typeInfo['id'] = 'string'
        """the end ip of the storage network IP range"""
        self.endip = None
        self.typeInfo['endip'] = 'string'
        """the gateway of the storage network IP range"""
        self.gateway = None
        self.typeInfo['gateway'] = 'string'
        """the netmask of the storage network IP range"""
        self.netmask = None
        self.typeInfo['netmask'] = 'string'
        """the network uuid of storage network IP range"""
        self.networkid = None
        self.typeInfo['networkid'] = 'string'
        """the Pod uuid for the storage network IP range"""
        self.podid = None
        self.typeInfo['podid'] = 'string'
        """the start ip of the storage network IP range"""
        self.startip = None
        self.typeInfo['startip'] = 'string'
        """the ID or VID of the VLAN."""
        self.vlan = None
        self.typeInfo['vlan'] = 'integer'
        """the Zone uuid of the storage network IP range"""
        self.zoneid = None
        self.typeInfo['zoneid'] = 'string'

