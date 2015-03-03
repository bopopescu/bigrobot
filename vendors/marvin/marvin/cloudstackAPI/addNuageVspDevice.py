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


"""Adds a Nuage VSP device"""
from baseCmd import *
from baseResponse import *
class addNuageVspDeviceCmd (baseCmd):
    typeInfo = {}
    def __init__(self):
        self.isAsync = "true"
        """the version of the API to use to communicate to Nuage VSD"""
        """Required"""
        self.apiversion = None
        self.typeInfo['apiversion'] = 'string'
        """the hostname of the Nuage VSD"""
        """Required"""
        self.hostname = None
        self.typeInfo['hostname'] = 'string'
        """the password of CMS user in Nuage VSD"""
        """Required"""
        self.password = None
        self.typeInfo['password'] = 'string'
        """the ID of the physical network in to which Nuage VSP is added"""
        """Required"""
        self.physicalnetworkid = None
        self.typeInfo['physicalnetworkid'] = 'uuid'
        """the port to communicate to Nuage VSD"""
        """Required"""
        self.port = None
        self.typeInfo['port'] = 'integer'
        """the number of retries on failure to communicate to Nuage VSD"""
        """Required"""
        self.retrycount = None
        self.typeInfo['retrycount'] = 'integer'
        """the time to wait after failure before retrying to communicate to Nuage VSD"""
        """Required"""
        self.retryinterval = None
        self.typeInfo['retryinterval'] = 'long'
        """the user name of the CMS user in Nuage VSD"""
        """Required"""
        self.username = None
        self.typeInfo['username'] = 'string'
        self.required = ["apiversion","hostname","password","physicalnetworkid","port","retrycount","retryinterval","username",]

class addNuageVspDeviceResponse (baseResponse):
    typeInfo = {}
    def __init__(self):
        """the version of the API to use to communicate to Nuage VSD"""
        self.apiversion = None
        self.typeInfo['apiversion'] = 'string'
        """the hostname of the Nuage VSD"""
        self.hostname = None
        self.typeInfo['hostname'] = 'string'
        """the name of the Nuage VSP device"""
        self.nuagedevicename = None
        self.typeInfo['nuagedevicename'] = 'string'
        """the ID of the physical network to which this Nuage VSP belongs to"""
        self.physicalnetworkid = None
        self.typeInfo['physicalnetworkid'] = 'string'
        """the port to communicate to Nuage VSD"""
        self.port = None
        self.typeInfo['port'] = 'int'
        """the service provider name corresponding to this Nuage VSP device"""
        self.provider = None
        self.typeInfo['provider'] = 'string'
        """the number of retries on failure to communicate to Nuage VSD"""
        self.retrycount = None
        self.typeInfo['retrycount'] = 'int'
        """the time to wait after failure before retrying to communicate to Nuage VSD"""
        self.retryinterval = None
        self.typeInfo['retryinterval'] = 'long'
        """the device id of the Nuage VSD"""
        self.vspdeviceid = None
        self.typeInfo['vspdeviceid'] = 'string'

