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


"""Lists dedicated guest vlan ranges"""
from baseCmd import *
from baseResponse import *
class listDedicatedGuestVlanRangesCmd (baseCmd):
    typeInfo = {}
    def __init__(self):
        self.isAsync = "false"
        """the account with which the guest VLAN range is associated. Must be used with the domainId parameter."""
        self.account = None
        self.typeInfo['account'] = 'string'
        """the domain ID with which the guest VLAN range is associated.  If used with the account parameter, returns all guest VLAN ranges for that account in the specified domain."""
        self.domainid = None
        self.typeInfo['domainid'] = 'uuid'
        """the dedicated guest vlan range"""
        self.guestvlanrange = None
        self.typeInfo['guestvlanrange'] = 'string'
        """list dedicated guest vlan ranges by id"""
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
        """physical network id of the guest VLAN range"""
        self.physicalnetworkid = None
        self.typeInfo['physicalnetworkid'] = 'uuid'
        """project who will own the guest VLAN range"""
        self.projectid = None
        self.typeInfo['projectid'] = 'uuid'
        """zone of the guest VLAN range"""
        self.zoneid = None
        self.typeInfo['zoneid'] = 'uuid'
        self.required = []

class listDedicatedGuestVlanRangesResponse (baseResponse):
    typeInfo = {}
    def __init__(self):
        """the ID of the guest VLAN range"""
        self.id = None
        self.typeInfo['id'] = 'string'
        """the account of the guest VLAN range"""
        self.account = None
        self.typeInfo['account'] = 'string'
        """the domain name of the guest VLAN range"""
        self.domain = None
        self.typeInfo['domain'] = 'string'
        """the domain ID of the guest VLAN range"""
        self.domainid = None
        self.typeInfo['domainid'] = 'string'
        """the guest VLAN range"""
        self.guestvlanrange = None
        self.typeInfo['guestvlanrange'] = 'string'
        """the physical network of the guest vlan range"""
        self.physicalnetworkid = None
        self.typeInfo['physicalnetworkid'] = 'long'
        """the project name of the guest vlan range"""
        self.project = None
        self.typeInfo['project'] = 'string'
        """the project id of the guest vlan range"""
        self.projectid = None
        self.typeInfo['projectid'] = 'string'
        """the zone of the guest vlan range"""
        self.zoneid = None
        self.typeInfo['zoneid'] = 'long'

