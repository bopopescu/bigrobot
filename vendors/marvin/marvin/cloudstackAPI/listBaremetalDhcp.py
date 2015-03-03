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


"""list baremetal dhcp servers"""
from baseCmd import *
from baseResponse import *
class listBaremetalDhcpCmd (baseCmd):
    typeInfo = {}
    def __init__(self):
        self.isAsync = "false"
        """the Physical Network ID"""
        """Required"""
        self.physicalnetworkid = None
        self.typeInfo['physicalnetworkid'] = 'uuid'
        """Type of DHCP device"""
        self.dhcpservertype = None
        self.typeInfo['dhcpservertype'] = 'string'
        """DHCP server device ID"""
        self.id = None
        self.typeInfo['id'] = 'long'
        """List by keyword"""
        self.keyword = None
        self.typeInfo['keyword'] = 'string'
        """"""
        self.page = None
        self.typeInfo['page'] = 'integer'
        """"""
        self.pagesize = None
        self.typeInfo['pagesize'] = 'integer'
        self.required = ["physicalnetworkid",]

class listBaremetalDhcpResponse (baseResponse):
    typeInfo = {}
    def __init__(self):
        """device id of"""
        self.id = None
        self.typeInfo['id'] = 'string'
        """name of the provider"""
        self.dhcpservertype = None
        self.typeInfo['dhcpservertype'] = 'string'
        """the physical network to which this external dhcp device belongs to"""
        self.physicalnetworkid = None
        self.typeInfo['physicalnetworkid'] = 'string'
        """name of the provider"""
        self.provider = None
        self.typeInfo['provider'] = 'string'
        """url"""
        self.url = None
        self.typeInfo['url'] = 'string'

