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


"""Adds traffic type to a physical network"""
from baseCmd import *
from baseResponse import *
class addTrafficTypeCmd (baseCmd):
    typeInfo = {}
    def __init__(self):
        self.isAsync = "true"
        """the Physical Network ID"""
        """Required"""
        self.physicalnetworkid = None
        self.typeInfo['physicalnetworkid'] = 'uuid'
        """the trafficType to be added to the physical network"""
        """Required"""
        self.traffictype = None
        self.typeInfo['traffictype'] = 'string'
        """The network name label of the physical device dedicated to this traffic on a Hyperv host"""
        self.hypervnetworklabel = None
        self.typeInfo['hypervnetworklabel'] = 'string'
        """Used if physical network has multiple isolation types and traffic type is public. Choose which isolation method. Valid options currently 'vlan' or 'vxlan', defaults to 'vlan'."""
        self.isolationmethod = None
        self.typeInfo['isolationmethod'] = 'string'
        """The network name label of the physical device dedicated to this traffic on a KVM host"""
        self.kvmnetworklabel = None
        self.typeInfo['kvmnetworklabel'] = 'string'
        """The VLAN id to be used for Management traffic by VMware host"""
        self.vlan = None
        self.typeInfo['vlan'] = 'string'
        """The network name label of the physical device dedicated to this traffic on a VMware host"""
        self.vmwarenetworklabel = None
        self.typeInfo['vmwarenetworklabel'] = 'string'
        """The network name label of the physical device dedicated to this traffic on a XenServer host"""
        self.xenservernetworklabel = None
        self.typeInfo['xenservernetworklabel'] = 'string'
        self.required = ["physicalnetworkid","traffictype",]

class addTrafficTypeResponse (baseResponse):
    typeInfo = {}
    def __init__(self):
        """id of the network provider"""
        self.id = None
        self.typeInfo['id'] = 'string'
        """The network name label of the physical device dedicated to this traffic on a HyperV host"""
        self.hypervnetworklabel = None
        self.typeInfo['hypervnetworklabel'] = 'string'
        """The network name label of the physical device dedicated to this traffic on a KVM host"""
        self.kvmnetworklabel = None
        self.typeInfo['kvmnetworklabel'] = 'string'
        """the physical network this belongs to"""
        self.physicalnetworkid = None
        self.typeInfo['physicalnetworkid'] = 'string'
        """the trafficType to be added to the physical network"""
        self.traffictype = None
        self.typeInfo['traffictype'] = 'string'
        """The network name label of the physical device dedicated to this traffic on a VMware host"""
        self.vmwarenetworklabel = None
        self.typeInfo['vmwarenetworklabel'] = 'string'
        """The network name label of the physical device dedicated to this traffic on a XenServer host"""
        self.xenservernetworklabel = None
        self.typeInfo['xenservernetworklabel'] = 'string'

