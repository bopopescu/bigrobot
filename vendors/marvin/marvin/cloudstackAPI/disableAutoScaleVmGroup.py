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


"""Disables an AutoScale Vm Group"""
from baseCmd import *
from baseResponse import *
class disableAutoScaleVmGroupCmd (baseCmd):
    typeInfo = {}
    def __init__(self):
        self.isAsync = "true"
        """the ID of the autoscale group"""
        """Required"""
        self.id = None
        self.typeInfo['id'] = 'uuid'
        self.required = ["id",]

class disableAutoScaleVmGroupResponse (baseResponse):
    typeInfo = {}
    def __init__(self):
        """the autoscale vm group ID"""
        self.id = None
        self.typeInfo['id'] = 'string'
        """the account owning the instance group"""
        self.account = None
        self.typeInfo['account'] = 'string'
        """the domain name of the vm profile"""
        self.domain = None
        self.typeInfo['domain'] = 'string'
        """the domain ID of the vm profile"""
        self.domainid = None
        self.typeInfo['domainid'] = 'string'
        """is group for display to the regular user"""
        self.fordisplay = None
        self.typeInfo['fordisplay'] = 'boolean'
        """the frequency at which the conditions have to be evaluated"""
        self.interval = None
        self.typeInfo['interval'] = 'int'
        """the load balancer rule ID"""
        self.lbruleid = None
        self.typeInfo['lbruleid'] = 'string'
        """the maximum number of members in the vmgroup, The number of instances in the vm group will be equal to or less than this number."""
        self.maxmembers = None
        self.typeInfo['maxmembers'] = 'int'
        """the minimum number of members in the vmgroup, the number of instances in the vm group will be equal to or more than this number."""
        self.minmembers = None
        self.typeInfo['minmembers'] = 'int'
        """the project name of the vm profile"""
        self.project = None
        self.typeInfo['project'] = 'string'
        """the project id vm profile"""
        self.projectid = None
        self.typeInfo['projectid'] = 'string'
        """list of scaledown autoscale policies"""
        self.scaledownpolicies = None
        self.typeInfo['scaledownpolicies'] = 'list'
        """list of scaleup autoscale policies"""
        self.scaleuppolicies = None
        self.typeInfo['scaleuppolicies'] = 'list'
        """the current state of the AutoScale Vm Group"""
        self.state = None
        self.typeInfo['state'] = 'string'
        """the autoscale profile that contains information about the vms in the vm group."""
        self.vmprofileid = None
        self.typeInfo['vmprofileid'] = 'string'

