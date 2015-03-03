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


"""Creates an autoscale policy for a provision or deprovision action, the action is taken when the all the conditions evaluates to true for the specified duration. The policy is in effect once it is attached to a autscale vm group."""
from baseCmd import *
from baseResponse import *
class createAutoScalePolicyCmd (baseCmd):
    typeInfo = {}
    def __init__(self):
        self.isAsync = "true"
        """the action to be executed if all the conditions evaluate to true for the specified duration."""
        """Required"""
        self.action = None
        self.typeInfo['action'] = 'string'
        """the list of IDs of the conditions that are being evaluated on every interval"""
        """Required"""
        self.conditionids = []
        self.typeInfo['conditionids'] = 'list'
        """the duration for which the conditions have to be true before action is taken"""
        """Required"""
        self.duration = None
        self.typeInfo['duration'] = 'integer'
        """the cool down period for which the policy should not be evaluated after the action has been taken"""
        self.quiettime = None
        self.typeInfo['quiettime'] = 'integer'
        self.required = ["action","conditionids","duration",]

class createAutoScalePolicyResponse (baseResponse):
    typeInfo = {}
    def __init__(self):
        """the autoscale policy ID"""
        self.id = None
        self.typeInfo['id'] = 'string'
        """the account owning the autoscale policy"""
        self.account = None
        self.typeInfo['account'] = 'string'
        """the action to be executed if all the conditions evaluate to true for the specified duration."""
        self.action = None
        self.typeInfo['action'] = 'string'
        """the list of IDs of the conditions that are being evaluated on every interval"""
        self.conditions = None
        self.typeInfo['conditions'] = 'list'
        """the domain name of the autoscale policy"""
        self.domain = None
        self.typeInfo['domain'] = 'string'
        """the domain ID of the autoscale policy"""
        self.domainid = None
        self.typeInfo['domainid'] = 'string'
        """the duration for which the conditions have to be true before action is taken"""
        self.duration = None
        self.typeInfo['duration'] = 'integer'
        """the project name of the autoscale policy"""
        self.project = None
        self.typeInfo['project'] = 'string'
        """the project id autoscale policy"""
        self.projectid = None
        self.typeInfo['projectid'] = 'string'
        """the cool down period for which the policy should not be evaluated after the action has been taken"""
        self.quiettime = None
        self.typeInfo['quiettime'] = 'integer'

