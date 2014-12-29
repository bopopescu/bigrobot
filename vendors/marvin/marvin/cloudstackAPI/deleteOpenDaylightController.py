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


"""Removes an OpenDyalight controler"""
from baseCmd import *
from baseResponse import *
class deleteOpenDaylightControllerCmd (baseCmd):
    typeInfo = {}
    def __init__(self):
        self.isAsync = "true"
        """OpenDaylight Controller ID"""
        """Required"""
        self.id = None
        self.typeInfo['id'] = 'uuid'
        self.required = ["id",]

class deleteOpenDaylightControllerResponse (baseResponse):
    typeInfo = {}
    def __init__(self):
        """device id of the controller"""
        self.id = None
        self.typeInfo['id'] = 'string'
        """the name assigned to the controller"""
        self.name = None
        self.typeInfo['name'] = 'string'
        """the physical network to which this controller belongs to"""
        self.physicalnetworkid = None
        self.typeInfo['physicalnetworkid'] = 'string'
        """the url of the controller api"""
        self.url = None
        self.typeInfo['url'] = 'string'
        """the username to authenticate to the controller"""
        self.username = None
        self.typeInfo['username'] = 'string'

