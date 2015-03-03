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


"""Adds vpn users"""
from baseCmd import *
from baseResponse import *
class addVpnUserCmd (baseCmd):
    typeInfo = {}
    def __init__(self):
        self.isAsync = "true"
        """password for the username"""
        """Required"""
        self.password = None
        self.typeInfo['password'] = 'string'
        """username for the vpn user"""
        """Required"""
        self.username = None
        self.typeInfo['username'] = 'string'
        """an optional account for the vpn user. Must be used with domainId."""
        self.account = None
        self.typeInfo['account'] = 'string'
        """an optional domainId for the vpn user. If the account parameter is used, domainId must also be used."""
        self.domainid = None
        self.typeInfo['domainid'] = 'uuid'
        """add vpn user to the specific project"""
        self.projectid = None
        self.typeInfo['projectid'] = 'uuid'
        self.required = ["password","username",]

class addVpnUserResponse (baseResponse):
    typeInfo = {}
    def __init__(self):
        """the vpn userID"""
        self.id = None
        self.typeInfo['id'] = 'string'
        """the account of the remote access vpn"""
        self.account = None
        self.typeInfo['account'] = 'string'
        """the domain name of the account of the remote access vpn"""
        self.domain = None
        self.typeInfo['domain'] = 'string'
        """the domain id of the account of the remote access vpn"""
        self.domainid = None
        self.typeInfo['domainid'] = 'string'
        """the project name of the vpn"""
        self.project = None
        self.typeInfo['project'] = 'string'
        """the project id of the vpn"""
        self.projectid = None
        self.typeInfo['projectid'] = 'string'
        """the state of the Vpn User"""
        self.state = None
        self.typeInfo['state'] = 'string'
        """the username of the vpn user"""
        self.username = None
        self.typeInfo['username'] = 'string'

