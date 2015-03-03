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


"""Lists Brocade VCS Switches"""
from baseCmd import *
from baseResponse import *
class listBrocadeVcsDevicesCmd (baseCmd):
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
        """Brocade VCS switch ID"""
        self.vcsdeviceid = None
        self.typeInfo['vcsdeviceid'] = 'uuid'
        self.required = []

class listBrocadeVcsDevicesResponse (baseResponse):
    typeInfo = {}
    def __init__(self):
        """device name"""
        self.brocadedevicename = None
        self.typeInfo['brocadedevicename'] = 'string'
        """the principal switch Ip address"""
        self.hostname = None
        self.typeInfo['hostname'] = 'string'
        """the physical Network to which this Brocade VCS belongs to"""
        self.physicalnetworkid = None
        self.typeInfo['physicalnetworkid'] = 'string'
        """name of the provider"""
        self.provider = None
        self.typeInfo['provider'] = 'string'
        """device id of the Brocade Vcs"""
        self.vcsdeviceid = None
        self.typeInfo['vcsdeviceid'] = 'string'

