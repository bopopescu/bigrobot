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


"""Lists network serviceproviders for a given physical network."""
from baseCmd import *
from baseResponse import *
class listNetworkServiceProvidersCmd (baseCmd):
    typeInfo = {}
    def __init__(self):
        self.isAsync = "false"
        """List by keyword"""
        self.keyword = None
        self.typeInfo['keyword'] = 'string'
        """list providers by name"""
        self.name = None
        self.typeInfo['name'] = 'string'
        """"""
        self.page = None
        self.typeInfo['page'] = 'integer'
        """"""
        self.pagesize = None
        self.typeInfo['pagesize'] = 'integer'
        """the Physical Network ID"""
        self.physicalnetworkid = None
        self.typeInfo['physicalnetworkid'] = 'uuid'
        """list providers by state"""
        self.state = None
        self.typeInfo['state'] = 'string'
        self.required = []

class listNetworkServiceProvidersResponse (baseResponse):
    typeInfo = {}
    def __init__(self):
        """uuid of the network provider"""
        self.id = None
        self.typeInfo['id'] = 'string'
        """true if individual services can be enabled/disabled"""
        self.canenableindividualservice = None
        self.typeInfo['canenableindividualservice'] = 'boolean'
        """the destination physical network"""
        self.destinationphysicalnetworkid = None
        self.typeInfo['destinationphysicalnetworkid'] = 'string'
        """the provider name"""
        self.name = None
        self.typeInfo['name'] = 'string'
        """the physical network this belongs to"""
        self.physicalnetworkid = None
        self.typeInfo['physicalnetworkid'] = 'string'
        """services for this provider"""
        self.servicelist = None
        self.typeInfo['servicelist'] = 'list'
        """state of the network provider"""
        self.state = None
        self.typeInfo['state'] = 'string'

