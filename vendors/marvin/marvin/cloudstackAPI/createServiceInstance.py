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


"""Creates a system virtual-machine that implements network services"""
from baseCmd import *
from baseResponse import *
class createServiceInstanceCmd (baseCmd):
    typeInfo = {}
    def __init__(self):
        self.isAsync = "true"
        """The left (inside) network for service instance"""
        """Required"""
        self.leftnetworkid = None
        self.typeInfo['leftnetworkid'] = 'uuid'
        """The name of the service instance"""
        """Required"""
        self.name = None
        self.typeInfo['name'] = 'string'
        """The right (outside) network ID for the service instance"""
        """Required"""
        self.rightnetworkid = None
        self.typeInfo['rightnetworkid'] = 'uuid'
        """The service offering ID that defines the resources consumed by the service appliance"""
        """Required"""
        self.serviceofferingid = None
        self.typeInfo['serviceofferingid'] = 'uuid'
        """The template ID that specifies the image for the service appliance"""
        """Required"""
        self.templateid = None
        self.typeInfo['templateid'] = 'uuid'
        """Availability zone for the service instance"""
        """Required"""
        self.zoneid = None
        self.typeInfo['zoneid'] = 'uuid'
        """An optional account for the virtual machine. Must be used with domainId."""
        self.account = None
        self.typeInfo['account'] = 'string'
        """An optional domainId for the virtual machine. If the account parameter is used, domainId must also be used."""
        self.domainid = None
        self.typeInfo['domainid'] = 'uuid'
        """Project ID for the service instance"""
        self.projectid = None
        self.typeInfo['projectid'] = 'uuid'
        self.required = ["leftnetworkid","name","rightnetworkid","serviceofferingid","templateid","zoneid",]

class createServiceInstanceResponse (baseResponse):
    typeInfo = {}
    def __init__(self):
        """the ID of the virtual machine"""
        self.id = None
        self.typeInfo['id'] = 'string'
        """the account associated with the virtual machine"""
        self.account = None
        self.typeInfo['account'] = 'string'
        """user generated name. The name of the virtual machine is returned if no displayname exists."""
        self.displayname = None
        self.typeInfo['displayname'] = 'string'
        """the name of the domain in which the virtual machine exists"""
        self.domain = None
        self.typeInfo['domain'] = 'string'
        """the ID of the domain in which the virtual machine exists"""
        self.domainid = None
        self.typeInfo['domainid'] = 'string'
        """the name of the virtual machine"""
        self.name = None
        self.typeInfo['name'] = 'string'
        """the project name of the vm"""
        self.project = None
        self.typeInfo['project'] = 'string'
        """the project id of the vm"""
        self.projectid = None
        self.typeInfo['projectid'] = 'string'

