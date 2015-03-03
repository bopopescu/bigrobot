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


"""Lists Nuage VSP devices"""
from baseCmd import *
from baseResponse import *
class listNuageVspDevicesCmd (baseCmd):
    typeInfo = {}
    def __init__(self):
        self.isAsync = "false"
        """List by keyword"""
        self.keyword = None
        self.typeInfo['keyword'] = 'string'
        """"""
        self.page = None
        self.typeInfo['page'] = 'integer'
        """"""
        self.pagesize = None
        self.typeInfo['pagesize'] = 'integer'
        """the Physical Network ID"""
        self.physicalnetworkid = None
        self.typeInfo['physicalnetworkid'] = 'uuid'
        """the Nuage VSP device ID"""
        self.vspdeviceid = None
        self.typeInfo['vspdeviceid'] = 'uuid'
        self.required = []

class listNuageVspDevicesResponse (baseResponse):
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

