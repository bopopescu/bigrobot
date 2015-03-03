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


"""Issues a Nuage VSP REST API resource request"""
from baseCmd import *
from baseResponse import *
class issueNuageVspResourceRequestCmd (baseCmd):
    typeInfo = {}
    def __init__(self):
        self.isAsync = "false"
        """the Nuage VSP REST API method type"""
        """Required"""
        self.method = None
        self.typeInfo['method'] = 'string'
        """the network offering id"""
        """Required"""
        self.networkofferingid = None
        self.typeInfo['networkofferingid'] = 'uuid'
        """the resource in Nuage VSP"""
        """Required"""
        self.resource = None
        self.typeInfo['resource'] = 'string'
        """the Zone ID for the network"""
        """Required"""
        self.zoneid = None
        self.typeInfo['zoneid'] = 'uuid'
        """the child resource in Nuage VSP"""
        self.childresource = None
        self.typeInfo['childresource'] = 'string'
        """the ID of the physical network in to which Nuage VSP Controller is added"""
        self.physicalnetworkid = None
        self.typeInfo['physicalnetworkid'] = 'uuid'
        """the resource filter in Nuage VSP"""
        self.resourcefilter = None
        self.typeInfo['resourcefilter'] = 'string'
        """the ID of the resource in Nuage VSP"""
        self.resourceid = None
        self.typeInfo['resourceid'] = 'string'
        self.required = ["method","networkofferingid","resource","zoneid",]

class issueNuageVspResourceRequestResponse (baseResponse):
    typeInfo = {}
    def __init__(self):
        """the details of the Nuage VSP resource"""
        self.resourceinfo = None
        self.typeInfo['resourceinfo'] = 'string'

