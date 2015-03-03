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


"""Lists clusters."""
from baseCmd import *
from baseResponse import *
class listClustersCmd (baseCmd):
    typeInfo = {}
    def __init__(self):
        self.isAsync = "false"
        """lists clusters by allocation state"""
        self.allocationstate = None
        self.typeInfo['allocationstate'] = 'string'
        """lists clusters by cluster type"""
        self.clustertype = None
        self.typeInfo['clustertype'] = 'string'
        """lists clusters by hypervisor type"""
        self.hypervisor = None
        self.typeInfo['hypervisor'] = 'string'
        """lists clusters by the cluster ID"""
        self.id = None
        self.typeInfo['id'] = 'uuid'
        """List by keyword"""
        self.keyword = None
        self.typeInfo['keyword'] = 'string'
        """whether this cluster is managed by cloudstack"""
        self.managedstate = None
        self.typeInfo['managedstate'] = 'string'
        """lists clusters by the cluster name"""
        self.name = None
        self.typeInfo['name'] = 'string'
        """"""
        self.page = None
        self.typeInfo['page'] = 'integer'
        """"""
        self.pagesize = None
        self.typeInfo['pagesize'] = 'integer'
        """lists clusters by Pod ID"""
        self.podid = None
        self.typeInfo['podid'] = 'uuid'
        """flag to display the capacity of the clusters"""
        self.showcapacities = None
        self.typeInfo['showcapacities'] = 'boolean'
        """lists clusters by Zone ID"""
        self.zoneid = None
        self.typeInfo['zoneid'] = 'uuid'
        self.required = []

class listClustersResponse (baseResponse):
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

