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


"""Lists all the system wide capacities."""
from baseCmd import *
from baseResponse import *
class listCapacityCmd (baseCmd):
    typeInfo = {}
    def __init__(self):
        self.isAsync = "false"
        """lists capacity by the Cluster ID"""
        self.clusterid = None
        self.typeInfo['clusterid'] = 'uuid'
        """recalculate capacities and fetch the latest"""
        self.fetchlatest = None
        self.typeInfo['fetchlatest'] = 'boolean'
        """List by keyword"""
        self.keyword = None
        self.typeInfo['keyword'] = 'string'
        """"""
        self.page = None
        self.typeInfo['page'] = 'integer'
        """"""
        self.pagesize = None
        self.typeInfo['pagesize'] = 'integer'
        """lists capacity by the Pod ID"""
        self.podid = None
        self.typeInfo['podid'] = 'uuid'
        """Sort the results. Available values: Usage"""
        self.sortby = None
        self.typeInfo['sortby'] = 'string'
        """lists capacity by type* CAPACITY_TYPE_MEMORY = 0* CAPACITY_TYPE_CPU = 1* CAPACITY_TYPE_STORAGE = 2* CAPACITY_TYPE_STORAGE_ALLOCATED = 3* CAPACITY_TYPE_VIRTUAL_NETWORK_PUBLIC_IP = 4* CAPACITY_TYPE_PRIVATE_IP = 5* CAPACITY_TYPE_SECONDARY_STORAGE = 6* CAPACITY_TYPE_VLAN = 7* CAPACITY_TYPE_DIRECT_ATTACHED_PUBLIC_IP = 8* CAPACITY_TYPE_LOCAL_STORAGE = 9."""
        self.type = None
        self.typeInfo['type'] = 'integer'
        """lists capacity by the Zone ID"""
        self.zoneid = None
        self.typeInfo['zoneid'] = 'uuid'
        self.required = []

class listCapacityResponse (baseResponse):
    typeInfo = {}
    def __init__(self):
        """the total capacity available"""
        self.capacitytotal = None
        self.typeInfo['capacitytotal'] = 'long'
        """the capacity currently in use"""
        self.capacityused = None
        self.typeInfo['capacityused'] = 'long'
        """the Cluster ID"""
        self.clusterid = None
        self.typeInfo['clusterid'] = 'string'
        """the Cluster name"""
        self.clustername = None
        self.typeInfo['clustername'] = 'string'
        """the percentage of capacity currently in use"""
        self.percentused = None
        self.typeInfo['percentused'] = 'string'
        """the Pod ID"""
        self.podid = None
        self.typeInfo['podid'] = 'string'
        """the Pod name"""
        self.podname = None
        self.typeInfo['podname'] = 'string'
        """the capacity type"""
        self.type = None
        self.typeInfo['type'] = 'short'
        """the Zone ID"""
        self.zoneid = None
        self.typeInfo['zoneid'] = 'string'
        """the Zone name"""
        self.zonename = None
        self.typeInfo['zonename'] = 'string'

