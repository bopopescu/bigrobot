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


"""Adds a Brocade VCS Switch"""
from baseCmd import *
from baseResponse import *
class addBrocadeVcsDeviceCmd (baseCmd):
    typeInfo = {}
    def __init__(self):
        self.isAsync = "true"
        """Hostname of ip address of the Brocade VCS Switch."""
        """Required"""
        self.hostname = None
        self.typeInfo['hostname'] = 'string'
        """Credentials to access the Brocade VCS Switch API"""
        """Required"""
        self.password = None
        self.typeInfo['password'] = 'string'
        """the Physical Network ID"""
        """Required"""
        self.physicalnetworkid = None
        self.typeInfo['physicalnetworkid'] = 'uuid'
        """Credentials to access the Brocade VCS Switch API"""
        """Required"""
        self.username = None
        self.typeInfo['username'] = 'string'
        self.required = ["hostname","password","physicalnetworkid","username",]

class addBrocadeVcsDeviceResponse (baseResponse):
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

