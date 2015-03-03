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


"""Adds a VMware datacenter to specified zone"""
from baseCmd import *
from baseResponse import *
class addVmwareDcCmd (baseCmd):
    typeInfo = {}
    def __init__(self):
        self.isAsync = "false"
        """Name of VMware datacenter to be added to specified zone."""
        """Required"""
        self.name = None
        self.typeInfo['name'] = 'string'
        """The name/ip of vCenter. Make sure it is IP address or full qualified domain name for host running vCenter server."""
        """Required"""
        self.vcenter = None
        self.typeInfo['vcenter'] = 'string'
        """The Zone ID."""
        """Required"""
        self.zoneid = None
        self.typeInfo['zoneid'] = 'uuid'
        """The password for specified username."""
        self.password = None
        self.typeInfo['password'] = 'string'
        """The Username required to connect to resource."""
        self.username = None
        self.typeInfo['username'] = 'string'
        self.required = ["name","vcenter","zoneid",]

class addVmwareDcResponse (baseResponse):
    typeInfo = {}
    def __init__(self):
        """The VMware Datacenter ID"""
        self.id = None
        self.typeInfo['id'] = 'string'
        """The VMware Datacenter name"""
        self.name = None
        self.typeInfo['name'] = 'string'
        """The VMware vCenter name/ip"""
        self.vcenter = None
        self.typeInfo['vcenter'] = 'string'
        """the Zone ID associated with this VMware Datacenter"""
        self.zoneid = None
        self.typeInfo['zoneid'] = 'long'

