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


"""Adds a BigSwitch BCF Controller device"""
from baseCmd import *
from baseResponse import *
class addBigSwitchBcfDeviceCmd (baseCmd):
    typeInfo = {}
    def __init__(self):
        self.isAsync = "true"
        """Hostname of ip address of the BigSwitch BCF Controller."""
        """Required"""
        self.hostname = None
        self.typeInfo['hostname'] = 'string'
        """Password of the BigSwitch BCF Controller."""
        """Required"""
        self.password = None
        self.typeInfo['password'] = 'string'
        """the Physical Network ID"""
        """Required"""
        self.physicalnetworkid = None
        self.typeInfo['physicalnetworkid'] = 'uuid'
        """Username of the BigSwitch BCF Controller."""
        """Required"""
        self.username = None
        self.typeInfo['username'] = 'string'
        self.required = ["hostname","password","physicalnetworkid","username",]

class addBigSwitchBcfDeviceResponse (baseResponse):
    typeInfo = {}
    def __init__(self):
        """device id of the BigSwitch BCF Controller"""
        self.bcfdeviceid = None
        self.typeInfo['bcfdeviceid'] = 'string'
        """device name"""
        self.bigswitchdevicename = None
        self.typeInfo['bigswitchdevicename'] = 'string'
        """the controller Ip address"""
        self.hostname = None
        self.typeInfo['hostname'] = 'string'
        """the controller password"""
        self.password = None
        self.typeInfo['password'] = 'string'
        """the physical network to which this BigSwitch BCF segment belongs to"""
        self.physicalnetworkid = None
        self.typeInfo['physicalnetworkid'] = 'string'
        """name of the provider"""
        self.provider = None
        self.typeInfo['provider'] = 'string'
        """the controller username"""
        self.username = None
        self.typeInfo['username'] = 'string'

