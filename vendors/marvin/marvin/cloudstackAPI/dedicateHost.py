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


"""Dedicates a host."""
from baseCmd import *
from baseResponse import *
class dedicateHostCmd (baseCmd):
    typeInfo = {}
    def __init__(self):
        self.isAsync = "true"
        """the ID of the containing domain"""
        """Required"""
        self.domainid = None
        self.typeInfo['domainid'] = 'uuid'
        """the ID of the host to update"""
        """Required"""
        self.hostid = None
        self.typeInfo['hostid'] = 'uuid'
        """the name of the account which needs dedication. Must be used with domainId."""
        self.account = None
        self.typeInfo['account'] = 'string'
        self.required = ["domainid","hostid",]

class dedicateHostResponse (baseResponse):
    typeInfo = {}
    def __init__(self):
        """the ID of the dedicated resource"""
        self.id = None
        self.typeInfo['id'] = 'string'
        """the Account ID of the host"""
        self.accountid = None
        self.typeInfo['accountid'] = 'string'
        """the Dedication Affinity Group ID of the host"""
        self.affinitygroupid = None
        self.typeInfo['affinitygroupid'] = 'string'
        """the domain ID of the host"""
        self.domainid = None
        self.typeInfo['domainid'] = 'string'
        """the ID of the host"""
        self.hostid = None
        self.typeInfo['hostid'] = 'string'
        """the name of the host"""
        self.hostname = None
        self.typeInfo['hostname'] = 'string'

