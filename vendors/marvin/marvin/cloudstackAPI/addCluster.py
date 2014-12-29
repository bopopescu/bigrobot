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


"""Adds a new cluster"""
from baseCmd import *
from baseResponse import *
class addClusterCmd (baseCmd):
    typeInfo = {}
    def __init__(self):
        self.isAsync = "false"
        """the cluster name"""
        """Required"""
        self.clustername = None
        self.typeInfo['clustername'] = 'string'
        """type of the cluster: CloudManaged, ExternalManaged"""
        """Required"""
        self.clustertype = None
        self.typeInfo['clustertype'] = 'string'
        """hypervisor type of the cluster: XenServer,KVM,VMware,Hyperv,BareMetal,Simulator"""
        """Required"""
        self.hypervisor = None
        self.typeInfo['hypervisor'] = 'string'
        """the Pod ID for the host"""
        """Required"""
        self.podid = None
        self.typeInfo['podid'] = 'uuid'
        """the Zone ID for the cluster"""
        """Required"""
        self.zoneid = None
        self.typeInfo['zoneid'] = 'uuid'
        """Allocation state of this cluster for allocation of new resources"""
        self.allocationstate = None
        self.typeInfo['allocationstate'] = 'string'
        """Name of virtual switch used for guest traffic in the cluster. This would override zone wide traffic label setting."""
        self.guestvswitchname = None
        self.typeInfo['guestvswitchname'] = 'string'
        """Type of virtual switch used for guest traffic in the cluster. Allowed values are, vmwaresvs (for VMware standard vSwitch) and vmwaredvs (for VMware distributed vSwitch)"""
        self.guestvswitchtype = None
        self.typeInfo['guestvswitchtype'] = 'string'
        """the password for the host"""
        self.password = None
        self.typeInfo['password'] = 'string'
        """Name of virtual switch used for public traffic in the cluster.  This would override zone wide traffic label setting."""
        self.publicvswitchname = None
        self.typeInfo['publicvswitchname'] = 'string'
        """Type of virtual switch used for public traffic in the cluster. Allowed values are, vmwaresvs (for VMware standard vSwitch) and vmwaredvs (for VMware distributed vSwitch)"""
        self.publicvswitchtype = None
        self.typeInfo['publicvswitchtype'] = 'string'
        """the URL"""
        self.url = None
        self.typeInfo['url'] = 'string'
        """the username for the cluster"""
        self.username = None
        self.typeInfo['username'] = 'string'
        """the ipaddress of the VSM associated with this cluster"""
        self.vsmipaddress = None
        self.typeInfo['vsmipaddress'] = 'string'
        """the password for the VSM associated with this cluster"""
        self.vsmpassword = None
        self.typeInfo['vsmpassword'] = 'string'
        """the username for the VSM associated with this cluster"""
        self.vsmusername = None
        self.typeInfo['vsmusername'] = 'string'
        self.required = ["clustername","clustertype","hypervisor","podid","zoneid",]

class addClusterResponse (baseResponse):
    typeInfo = {}
    def __init__(self):
        """the cluster ID"""
        self.id = None
        self.typeInfo['id'] = 'string'
        """the allocation state of the cluster"""
        self.allocationstate = None
        self.typeInfo['allocationstate'] = 'string'
        """the type of the cluster"""
        self.clustertype = None
        self.typeInfo['clustertype'] = 'string'
        """The cpu overcommit ratio of the cluster"""
        self.cpuovercommitratio = None
        self.typeInfo['cpuovercommitratio'] = 'string'
        """the hypervisor type of the cluster"""
        self.hypervisortype = None
        self.typeInfo['hypervisortype'] = 'string'
        """whether this cluster is managed by cloudstack"""
        self.managedstate = None
        self.typeInfo['managedstate'] = 'string'
        """The memory overcommit ratio of the cluster"""
        self.memoryovercommitratio = None
        self.typeInfo['memoryovercommitratio'] = 'string'
        """the cluster name"""
        self.name = None
        self.typeInfo['name'] = 'string'
        """the Pod ID of the cluster"""
        self.podid = None
        self.typeInfo['podid'] = 'string'
        """the Pod name of the cluster"""
        self.podname = None
        self.typeInfo['podname'] = 'string'
        """the Zone ID of the cluster"""
        self.zoneid = None
        self.typeInfo['zoneid'] = 'string'
        """the Zone name of the cluster"""
        self.zonename = None
        self.typeInfo['zonename'] = 'string'
        """the capacity of the Cluster"""
        self.capacity = []

class capacity:
    def __init__(self):
        """"the total capacity available"""
        self.capacitytotal = None
        """"the capacity currently in use"""
        self.capacityused = None
        """"the Cluster ID"""
        self.clusterid = None
        """"the Cluster name"""
        self.clustername = None
        """"the percentage of capacity currently in use"""
        self.percentused = None
        """"the Pod ID"""
        self.podid = None
        """"the Pod name"""
        self.podname = None
        """"the capacity type"""
        self.type = None
        """"the Zone ID"""
        self.zoneid = None
        """"the Zone name"""
        self.zonename = None

