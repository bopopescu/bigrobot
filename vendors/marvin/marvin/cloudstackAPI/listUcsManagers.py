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


"""List ucs manager"""
from baseCmd import *
from baseResponse import *
class listUcsManagersCmd (baseCmd):
    typeInfo = {}
    def __init__(self):
        self.isAsync = "false"
        """the ID of the ucs manager"""
        self.id = None
        self.typeInfo['id'] = 'uuid'
        """List by keyword"""
        self.keyword = None
        self.typeInfo['keyword'] = 'string'
        """"""
        self.page = None
        self.typeInfo['page'] = 'integer'
        """"""
        self.pagesize = None
        self.typeInfo['pagesize'] = 'integer'
        """the zone id"""
        self.zoneid = None
        self.typeInfo['zoneid'] = 'uuid'
        self.required = []

class listUcsManagersResponse (baseResponse):
    typeInfo = {}
    def __init__(self):
        """the ID of the ucs manager"""
        self.id = None
        self.typeInfo['id'] = 'string'
        """the name of ucs manager"""
        self.name = None
        self.typeInfo['name'] = 'string'
        """the url of ucs manager"""
        self.url = None
        self.typeInfo['url'] = 'string'
        """the zone ID of ucs manager"""
        self.zoneid = None
        self.typeInfo['zoneid'] = 'string'

