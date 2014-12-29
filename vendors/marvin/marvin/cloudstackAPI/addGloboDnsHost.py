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


"""Adds the GloboDNS external host"""
from baseCmd import *
from baseResponse import *
class addGloboDnsHostCmd (baseCmd):
    typeInfo = {}
    def __init__(self):
        self.isAsync = "true"
        """Password for GloboDNS"""
        """Required"""
        self.password = None
        self.typeInfo['password'] = 'string'
        """the Physical Network ID"""
        """Required"""
        self.physicalnetworkid = None
        self.typeInfo['physicalnetworkid'] = 'uuid'
        """GloboDNS url"""
        """Required"""
        self.url = None
        self.typeInfo['url'] = 'string'
        """Username for GloboDNS"""
        """Required"""
        self.username = None
        self.typeInfo['username'] = 'string'
        self.required = ["password","physicalnetworkid","url","username",]

class addGloboDnsHostResponse (baseResponse):
    typeInfo = {}
    def __init__(self):
        """any text associated with the success or failure"""
        self.displaytext = None
        self.typeInfo['displaytext'] = 'string'
        """true if operation is executed successfully"""
        self.success = None
        self.typeInfo['success'] = 'boolean'

