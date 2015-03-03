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


"""Updates an existing autoscale vm profile."""
from baseCmd import *
from baseResponse import *
class updateAutoScaleVmProfileCmd (baseCmd):
    typeInfo = {}
    def __init__(self):
        self.isAsync = "true"
        """the ID of the autoscale vm profile"""
        """Required"""
        self.id = None
        self.typeInfo['id'] = 'uuid'
        """the ID of the user used to launch and destroy the VMs"""
        self.autoscaleuserid = None
        self.typeInfo['autoscaleuserid'] = 'uuid'
        """counterparam list. Example: counterparam[0].name=snmpcommunity&counterparam[0].value=public&counterparam[1].name=snmpport&counterparam[1].value=161"""
        self.counterparam = []
        self.typeInfo['counterparam'] = 'map'
        """an optional field, in case you want to set a custom id to the resource. Allowed to Root Admins only"""
        self.customid = None
        self.typeInfo['customid'] = 'string'
        """the time allowed for existing connections to get closed before a vm is destroyed"""
        self.destroyvmgraceperiod = None
        self.typeInfo['destroyvmgraceperiod'] = 'integer'
        """an optional field, whether to the display the profile to the end user or not"""
        self.fordisplay = None
        self.typeInfo['fordisplay'] = 'boolean'
        """the template of the auto deployed virtual machine"""
        self.templateid = None
        self.typeInfo['templateid'] = 'uuid'
        self.required = ["id",]

class updateAutoScaleVmProfileResponse (baseResponse):
    typeInfo = {}
    def __init__(self):
        """the autoscale vm profile ID"""
        self.id = None
        self.typeInfo['id'] = 'string'
        """the account owning the instance group"""
        self.account = None
        self.typeInfo['account'] = 'string'
        """the ID of the user used to launch and destroy the VMs"""
        self.autoscaleuserid = None
        self.typeInfo['autoscaleuserid'] = 'string'
        """the time allowed for existing connections to get closed before a vm is destroyed"""
        self.destroyvmgraceperiod = None
        self.typeInfo['destroyvmgraceperiod'] = 'integer'
        """the domain name of the vm profile"""
        self.domain = None
        self.typeInfo['domain'] = 'string'
        """the domain ID of the vm profile"""
        self.domainid = None
        self.typeInfo['domainid'] = 'string'
        """is profile for display to the regular user"""
        self.fordisplay = None
        self.typeInfo['fordisplay'] = 'boolean'
        """parameters other than zoneId/serviceOfferringId/templateId to be used while deploying a virtual machine"""
        self.otherdeployparams = None
        self.typeInfo['otherdeployparams'] = 'string'
        """the project name of the vm profile"""
        self.project = None
        self.typeInfo['project'] = 'string'
        """the project id vm profile"""
        self.projectid = None
        self.typeInfo['projectid'] = 'string'
        """the service offering to be used while deploying a virtual machine"""
        self.serviceofferingid = None
        self.typeInfo['serviceofferingid'] = 'string'
        """the template to be used while deploying a virtual machine"""
        self.templateid = None
        self.typeInfo['templateid'] = 'string'
        """the availability zone to be used while deploying a virtual machine"""
        self.zoneid = None
        self.typeInfo['zoneid'] = 'string'

