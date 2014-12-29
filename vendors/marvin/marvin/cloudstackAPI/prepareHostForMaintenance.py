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


"""Prepares a host for maintenance."""
from baseCmd import *
from baseResponse import *
class prepareHostForMaintenanceCmd (baseCmd):
    typeInfo = {}
    def __init__(self):
        self.isAsync = "true"
        """the host ID"""
        """Required"""
        self.id = None
        self.typeInfo['id'] = 'uuid'
        self.required = ["id",]

class prepareHostForMaintenanceResponse (baseResponse):
    typeInfo = {}
    def __init__(self):
        """the ID of the host"""
        self.id = None
        self.typeInfo['id'] = 'string'
        """the cpu average load on the host"""
        self.averageload = None
        self.typeInfo['averageload'] = 'long'
        """capabilities of the host"""
        self.capabilities = None
        self.typeInfo['capabilities'] = 'string'
        """the cluster ID of the host"""
        self.clusterid = None
        self.typeInfo['clusterid'] = 'string'
        """the cluster name of the host"""
        self.clustername = None
        self.typeInfo['clustername'] = 'string'
        """the cluster type of the cluster that host belongs to"""
        self.clustertype = None
        self.typeInfo['clustertype'] = 'string'
        """the amount of the host's CPU currently allocated"""
        self.cpuallocated = None
        self.typeInfo['cpuallocated'] = 'string'
        """the CPU number of the host"""
        self.cpunumber = None
        self.typeInfo['cpunumber'] = 'integer'
        """the number of CPU sockets on the host"""
        self.cpusockets = None
        self.typeInfo['cpusockets'] = 'integer'
        """the CPU speed of the host"""
        self.cpuspeed = None
        self.typeInfo['cpuspeed'] = 'long'
        """the amount of the host's CPU currently used"""
        self.cpuused = None
        self.typeInfo['cpuused'] = 'string'
        """the amount of the host's CPU after applying the cpu.overprovisioning.factor"""
        self.cpuwithoverprovisioning = None
        self.typeInfo['cpuwithoverprovisioning'] = 'string'
        """the date and time the host was created"""
        self.created = None
        self.typeInfo['created'] = 'date'
        """Host details in key/value pairs."""
        self.details = None
        self.typeInfo['details'] = 'map'
        """true if the host is disconnected. False otherwise."""
        self.disconnected = None
        self.typeInfo['disconnected'] = 'date'
        """the host's currently allocated disk size"""
        self.disksizeallocated = None
        self.typeInfo['disksizeallocated'] = 'long'
        """the total disk size of the host"""
        self.disksizetotal = None
        self.typeInfo['disksizetotal'] = 'long'
        """events available for the host"""
        self.events = None
        self.typeInfo['events'] = 'string'
        """true if the host is Ha host (dedicated to vms started by HA process; false otherwise"""
        self.hahost = None
        self.typeInfo['hahost'] = 'boolean'
        """true if this host has enough CPU and RAM capacity to migrate a VM to it, false otherwise"""
        self.hasenoughcapacity = None
        self.typeInfo['hasenoughcapacity'] = 'boolean'
        """comma-separated list of tags for the host"""
        self.hosttags = None
        self.typeInfo['hosttags'] = 'string'
        """the host hypervisor"""
        self.hypervisor = None
        self.typeInfo['hypervisor'] = 'hypervisortype'
        """the hypervisor version"""
        self.hypervisorversion = None
        self.typeInfo['hypervisorversion'] = 'string'
        """the IP address of the host"""
        self.ipaddress = None
        self.typeInfo['ipaddress'] = 'string'
        """true if local storage is active, false otherwise"""
        self.islocalstorageactive = None
        self.typeInfo['islocalstorageactive'] = 'boolean'
        """the date and time the host was last pinged"""
        self.lastpinged = None
        self.typeInfo['lastpinged'] = 'date'
        """the management server ID of the host"""
        self.managementserverid = None
        self.typeInfo['managementserverid'] = 'long'
        """the amount of the host's memory currently allocated"""
        self.memoryallocated = None
        self.typeInfo['memoryallocated'] = 'long'
        """the memory total of the host"""
        self.memorytotal = None
        self.typeInfo['memorytotal'] = 'long'
        """the amount of the host's memory currently used"""
        self.memoryused = None
        self.typeInfo['memoryused'] = 'long'
        """the name of the host"""
        self.name = None
        self.typeInfo['name'] = 'string'
        """the incoming network traffic on the host"""
        self.networkkbsread = None
        self.typeInfo['networkkbsread'] = 'long'
        """the outgoing network traffic on the host"""
        self.networkkbswrite = None
        self.typeInfo['networkkbswrite'] = 'long'
        """the OS category ID of the host"""
        self.oscategoryid = None
        self.typeInfo['oscategoryid'] = 'string'
        """the OS category name of the host"""
        self.oscategoryname = None
        self.typeInfo['oscategoryname'] = 'string'
        """the Pod ID of the host"""
        self.podid = None
        self.typeInfo['podid'] = 'string'
        """the Pod name of the host"""
        self.podname = None
        self.typeInfo['podname'] = 'string'
        """the date and time the host was removed"""
        self.removed = None
        self.typeInfo['removed'] = 'date'
        """the resource state of the host"""
        self.resourcestate = None
        self.typeInfo['resourcestate'] = 'string'
        """the state of the host"""
        self.state = None
        self.typeInfo['state'] = 'status'
        """true if this host is suitable(has enough capacity and satisfies all conditions like hosttags, max guests vm limit etc) to migrate a VM to it , false otherwise"""
        self.suitableformigration = None
        self.typeInfo['suitableformigration'] = 'boolean'
        """the host type"""
        self.type = None
        self.typeInfo['type'] = 'type'
        """the host version"""
        self.version = None
        self.typeInfo['version'] = 'string'
        """the Zone ID of the host"""
        self.zoneid = None
        self.typeInfo['zoneid'] = 'string'
        """the Zone name of the host"""
        self.zonename = None
        self.typeInfo['zonename'] = 'string'
        """GPU cards present in the host"""
        self.gpugroup = []
        """the ID of the latest async job acting on this object"""
        self.jobid = None
        self.typeInfo['jobid'] = ''
        """the current status of the latest async job acting on this object"""
        self.jobstatus = None
        self.typeInfo['jobstatus'] = ''

class vgpu:
    def __init__(self):
        """"Maximum vgpu can be created with this vgpu type on the given gpu group"""
        self.maxcapacity = None
        """"Maximum displays per user"""
        self.maxheads = None
        """"Maximum X resolution per display"""
        self.maxresolutionx = None
        """"Maximum Y resolution per display"""
        self.maxresolutiony = None
        """"Maximum no. of vgpu per gpu card (pgpu)"""
        self.maxvgpuperpgpu = None
        """"Remaining capacity in terms of no. of more VMs that can be deployped with this vGPU type"""
        self.remainingcapacity = None
        """"Model Name of vGPU"""
        self.vgputype = None
        """"Video RAM for this vGPU type"""
        self.videoram = None

class gpugroup:
    def __init__(self):
        """"GPU cards present in the host"""
        self.gpugroupname = None
        """"the list of enabled vGPUs"""
        self.vgpu = []
        """"Maximum vgpu can be created with this vgpu type on the given gpu group"""
        self.maxcapacity = None
        """"Maximum displays per user"""
        self.maxheads = None
        """"Maximum X resolution per display"""
        self.maxresolutionx = None
        """"Maximum Y resolution per display"""
        self.maxresolutiony = None
        """"Maximum no. of vgpu per gpu card (pgpu)"""
        self.maxvgpuperpgpu = None
        """"Remaining capacity in terms of no. of more VMs that can be deployped with this vGPU type"""
        self.remainingcapacity = None
        """"Model Name of vGPU"""
        self.vgputype = None
        """"Video RAM for this vGPU type"""
        self.videoram = None

