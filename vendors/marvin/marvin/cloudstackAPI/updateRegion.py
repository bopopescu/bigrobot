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


"""Updates a region"""
from baseCmd import *
from baseResponse import *
class updateRegionCmd (baseCmd):
    typeInfo = {}
    def __init__(self):
        self.isAsync = "false"
        """Id of region to update"""
        """Required"""
        self.id = None
        self.typeInfo['id'] = 'integer'
        """updates region with this end point"""
        self.endpoint = None
        self.typeInfo['endpoint'] = 'string'
        """updates region with this name"""
        self.name = None
        self.typeInfo['name'] = 'string'
        self.required = ["id",]

class updateRegionResponse (baseResponse):
    typeInfo = {}
    def __init__(self):
        """the ID of the region"""
        self.id = None
        self.typeInfo['id'] = 'integer'
        """the end point of the region"""
        self.endpoint = None
        self.typeInfo['endpoint'] = 'string'
        """true if GSLB service is enabled in the region, false otherwise"""
        self.gslbserviceenabled = None
        self.typeInfo['gslbserviceenabled'] = 'boolean'
        """the name of the region"""
        self.name = None
        self.typeInfo['name'] = 'string'
        """true if security groups support is enabled, false otherwise"""
        self.portableipserviceenabled = None
        self.typeInfo['portableipserviceenabled'] = 'boolean'

