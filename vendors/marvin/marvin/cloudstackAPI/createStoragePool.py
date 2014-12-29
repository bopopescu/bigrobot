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


"""Creates a storage pool."""
from baseCmd import *
from baseResponse import *
class createStoragePoolCmd (baseCmd):
    typeInfo = {}
    def __init__(self):
        self.isAsync = "false"
        """the name for the storage pool"""
        """Required"""
        self.name = None
        self.typeInfo['name'] = 'string'
        """the URL of the storage pool"""
        """Required"""
        self.url = None
        self.typeInfo['url'] = 'string'
        """the Zone ID for the storage pool"""
        """Required"""
        self.zoneid = None
        self.typeInfo['zoneid'] = 'uuid'
        """bytes CloudStack can provision from this storage pool"""
        self.capacitybytes = None
        self.typeInfo['capacitybytes'] = 'long'
        """IOPS CloudStack can provision from this storage pool"""
        self.capacityiops = None
        self.typeInfo['capacityiops'] = 'long'
        """the cluster ID for the storage pool"""
        self.clusterid = None
        self.typeInfo['clusterid'] = 'uuid'
        """the details for the storage pool"""
        self.details = []
        self.typeInfo['details'] = 'map'
        """hypervisor type of the hosts in zone that will be attached to this storage pool. KVM, VMware supported as of now."""
        self.hypervisor = None
        self.typeInfo['hypervisor'] = 'string'
        """whether the storage should be managed by CloudStack"""
        self.managed = None
        self.typeInfo['managed'] = 'boolean'
        """the Pod ID for the storage pool"""
        self.podid = None
        self.typeInfo['podid'] = 'uuid'
        """the storage provider name"""
        self.provider = None
        self.typeInfo['provider'] = 'string'
        """the scope of the storage: cluster or zone"""
        self.scope = None
        self.typeInfo['scope'] = 'string'
        """the tags for the storage pool"""
        self.tags = None
        self.typeInfo['tags'] = 'string'
        self.required = ["name","url","zoneid",]

class createStoragePoolResponse (baseResponse):
    typeInfo = {}
    def __init__(self):
        """the ID of the storage pool"""
        self.id = None
        self.typeInfo['id'] = 'string'
        """IOPS CloudStack can provision from this storage pool"""
        self.capacityiops = None
        self.typeInfo['capacityiops'] = 'long'
        """the ID of the cluster for the storage pool"""
        self.clusterid = None
        self.typeInfo['clusterid'] = 'string'
        """the name of the cluster for the storage pool"""
        self.clustername = None
        self.typeInfo['clustername'] = 'string'
        """the date and time the storage pool was created"""
        self.created = None
        self.typeInfo['created'] = 'date'
        """the host's currently allocated disk size"""
        self.disksizeallocated = None
        self.typeInfo['disksizeallocated'] = 'long'
        """the total disk size of the storage pool"""
        self.disksizetotal = None
        self.typeInfo['disksizetotal'] = 'long'
        """the host's currently used disk size"""
        self.disksizeused = None
        self.typeInfo['disksizeused'] = 'long'
        """the hypervisor type of the storage pool"""
        self.hypervisor = None
        self.typeInfo['hypervisor'] = 'string'
        """the IP address of the storage pool"""
        self.ipaddress = None
        self.typeInfo['ipaddress'] = 'string'
        """the name of the storage pool"""
        self.name = None
        self.typeInfo['name'] = 'string'
        """the overprovisionfactor for the storage pool"""
        self.overprovisionfactor = None
        self.typeInfo['overprovisionfactor'] = 'string'
        """the storage pool path"""
        self.path = None
        self.typeInfo['path'] = 'string'
        """the Pod ID of the storage pool"""
        self.podid = None
        self.typeInfo['podid'] = 'string'
        """the Pod name of the storage pool"""
        self.podname = None
        self.typeInfo['podname'] = 'string'
        """the scope of the storage pool"""
        self.scope = None
        self.typeInfo['scope'] = 'string'
        """the state of the storage pool"""
        self.state = None
        self.typeInfo['state'] = 'storagepoolstatus'
        """the storage pool capabilities"""
        self.storagecapabilities = None
        self.typeInfo['storagecapabilities'] = 'map'
        """true if this pool is suitable to migrate a volume, false otherwise"""
        self.suitableformigration = None
        self.typeInfo['suitableformigration'] = 'boolean'
        """the tags for the storage pool"""
        self.tags = None
        self.typeInfo['tags'] = 'string'
        """the storage pool type"""
        self.type = None
        self.typeInfo['type'] = 'string'
        """the Zone ID of the storage pool"""
        self.zoneid = None
        self.typeInfo['zoneid'] = 'string'
        """the Zone name of the storage pool"""
        self.zonename = None
        self.typeInfo['zonename'] = 'string'
        """the ID of the latest async job acting on this object"""
        self.jobid = None
        self.typeInfo['jobid'] = ''
        """the current status of the latest async job acting on this object"""
        self.jobstatus = None
        self.typeInfo['jobstatus'] = ''

