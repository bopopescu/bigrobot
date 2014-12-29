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


"""Lists all Pods."""
from baseCmd import *
from baseResponse import *
class listPodsCmd (baseCmd):
    typeInfo = {}
    def __init__(self):
        self.isAsync = "false"
        """list pods by allocation state"""
        self.allocationstate = None
        self.typeInfo['allocationstate'] = 'string'
        """list Pods by ID"""
        self.id = None
        self.typeInfo['id'] = 'uuid'
        """List by keyword"""
        self.keyword = None
        self.typeInfo['keyword'] = 'string'
        """list Pods by name"""
        self.name = None
        self.typeInfo['name'] = 'string'
        """"""
        self.page = None
        self.typeInfo['page'] = 'integer'
        """"""
        self.pagesize = None
        self.typeInfo['pagesize'] = 'integer'
        """flag to display the capacity of the pods"""
        self.showcapacities = None
        self.typeInfo['showcapacities'] = 'boolean'
        """list Pods by Zone ID"""
        self.zoneid = None
        self.typeInfo['zoneid'] = 'uuid'
        self.required = []

class listPodsResponse (baseResponse):
    typeInfo = {}
    def __init__(self):
        """the ID of the Pod"""
        self.id = None
        self.typeInfo['id'] = 'string'
        """the allocation state of the Pod"""
        self.allocationstate = None
        self.typeInfo['allocationstate'] = 'string'
        """the ending IP for the Pod"""
        self.endip = None
        self.typeInfo['endip'] = 'string'
        """the gateway of the Pod"""
        self.gateway = None
        self.typeInfo['gateway'] = 'string'
        """the name of the Pod"""
        self.name = None
        self.typeInfo['name'] = 'string'
        """the netmask of the Pod"""
        self.netmask = None
        self.typeInfo['netmask'] = 'string'
        """the starting IP for the Pod"""
        self.startip = None
        self.typeInfo['startip'] = 'string'
        """the Zone ID of the Pod"""
        self.zoneid = None
        self.typeInfo['zoneid'] = 'string'
        """the Zone name of the Pod"""
        self.zonename = None
        self.typeInfo['zonename'] = 'string'
        """the capacity of the Pod"""
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

