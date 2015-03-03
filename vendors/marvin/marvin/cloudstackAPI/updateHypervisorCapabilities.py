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


"""Updates a hypervisor capabilities."""
from baseCmd import *
from baseResponse import *
class updateHypervisorCapabilitiesCmd (baseCmd):
    typeInfo = {}
    def __init__(self):
        self.isAsync = "false"
        """ID of the hypervisor capability"""
        self.id = None
        self.typeInfo['id'] = 'uuid'
        """the max number of Guest VMs per host for this hypervisor."""
        self.maxguestslimit = None
        self.typeInfo['maxguestslimit'] = 'long'
        """set true to enable security group for this hypervisor."""
        self.securitygroupenabled = None
        self.typeInfo['securitygroupenabled'] = 'boolean'
        self.required = []

class updateHypervisorCapabilitiesResponse (baseResponse):
    typeInfo = {}
    def __init__(self):
        """the ID of the hypervisor capabilities row"""
        self.id = None
        self.typeInfo['id'] = 'string'
        """the hypervisor type"""
        self.hypervisor = None
        self.typeInfo['hypervisor'] = 'hypervisortype'
        """the hypervisor version"""
        self.hypervisorversion = None
        self.typeInfo['hypervisorversion'] = 'string'
        """the maximum number of Data Volumes that can be attached for this hypervisor"""
        self.maxdatavolumeslimit = None
        self.typeInfo['maxdatavolumeslimit'] = 'integer'
        """the maximum number of guest vms recommended for this hypervisor"""
        self.maxguestslimit = None
        self.typeInfo['maxguestslimit'] = 'long'
        """the maximum number of Hosts per cluster for this hypervisor"""
        self.maxhostspercluster = None
        self.typeInfo['maxhostspercluster'] = 'integer'
        """true if security group is supported"""
        self.securitygroupenabled = None
        self.typeInfo['securitygroupenabled'] = 'boolean'
        """true if storage motion is supported"""
        self.storagemotionenabled = None
        self.typeInfo['storagemotionenabled'] = 'boolean'

