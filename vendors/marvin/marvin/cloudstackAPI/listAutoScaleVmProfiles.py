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


"""Lists autoscale vm profiles."""
from baseCmd import *
from baseResponse import *
class listAutoScaleVmProfilesCmd (baseCmd):
    typeInfo = {}
    def __init__(self):
        self.isAsync = "false"
        """list resources by account. Must be used with the domainId parameter."""
        self.account = None
        self.typeInfo['account'] = 'string'
        """list only resources belonging to the domain specified"""
        self.domainid = None
        self.typeInfo['domainid'] = 'uuid'
        """list resources by display flag; only ROOT admin is eligible to pass this parameter"""
        self.fordisplay = None
        self.typeInfo['fordisplay'] = 'boolean'
        """the ID of the autoscale vm profile"""
        self.id = None
        self.typeInfo['id'] = 'uuid'
        """defaults to false, but if true, lists all resources from the parent specified by the domainId till leaves."""
        self.isrecursive = None
        self.typeInfo['isrecursive'] = 'boolean'
        """List by keyword"""
        self.keyword = None
        self.typeInfo['keyword'] = 'string'
        """If set to false, list only resources belonging to the command's caller; if set to true - list resources that the caller is authorized to see. Default value is false"""
        self.listall = None
        self.typeInfo['listall'] = 'boolean'
        """the otherdeployparameters of the autoscale vm profile"""
        self.otherdeployparams = None
        self.typeInfo['otherdeployparams'] = 'string'
        """"""
        self.page = None
        self.typeInfo['page'] = 'integer'
        """"""
        self.pagesize = None
        self.typeInfo['pagesize'] = 'integer'
        """list objects by project"""
        self.projectid = None
        self.typeInfo['projectid'] = 'uuid'
        """list profiles by service offering id"""
        self.serviceofferingid = None
        self.typeInfo['serviceofferingid'] = 'uuid'
        """the templateid of the autoscale vm profile"""
        self.templateid = None
        self.typeInfo['templateid'] = 'uuid'
        """availability zone for the auto deployed virtual machine"""
        self.zoneid = None
        self.typeInfo['zoneid'] = 'uuid'
        self.required = []

class listAutoScaleVmProfilesResponse (baseResponse):
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

