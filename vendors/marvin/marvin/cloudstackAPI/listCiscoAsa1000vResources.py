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


"""Lists Cisco ASA 1000v appliances"""
from baseCmd import *
from baseResponse import *
class listCiscoAsa1000vResourcesCmd (baseCmd):
    typeInfo = {}
    def __init__(self):
        self.isAsync = "false"
        """Hostname or ip address of the Cisco ASA 1000v appliance."""
        self.hostname = None
        self.typeInfo['hostname'] = 'string'
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
        """Cisco ASA 1000v resource ID"""
        self.resourceid = None
        self.typeInfo['resourceid'] = 'uuid'
        self.required = []

class listCiscoAsa1000vResourcesResponse (baseResponse):
    typeInfo = {}
    def __init__(self):
        pass
