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


"""Removes detail for the Resource."""
from baseCmd import *
from baseResponse import *
class removeResourceDetailCmd (baseCmd):
    typeInfo = {}
    def __init__(self):
        self.isAsync = "true"
        """Delete details for resource id"""
        """Required"""
        self.resourceid = None
        self.typeInfo['resourceid'] = 'string'
        """Delete detail by resource type"""
        """Required"""
        self.resourcetype = None
        self.typeInfo['resourcetype'] = 'string'
        """Delete details matching key/value pairs"""
        self.key = None
        self.typeInfo['key'] = 'string'
        self.required = ["resourceid","resourcetype",]

class removeResourceDetailResponse (baseResponse):
    typeInfo = {}
    def __init__(self):
        """any text associated with the success or failure"""
        self.displaytext = None
        self.typeInfo['displaytext'] = 'string'
        """true if operation is executed successfully"""
        self.success = None
        self.typeInfo['success'] = 'boolean'

