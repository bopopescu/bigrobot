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


"""Removes vpn user"""
from baseCmd import *
from baseResponse import *
class removeVpnUserCmd (baseCmd):
    typeInfo = {}
    def __init__(self):
        self.isAsync = "true"
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
        """remove vpn user from the project"""
        self.projectid = None
        self.typeInfo['projectid'] = 'uuid'
        self.required = ["username",]

class removeVpnUserResponse (baseResponse):
    typeInfo = {}
    def __init__(self):
        """any text associated with the success or failure"""
        self.displaytext = None
        self.typeInfo['displaytext'] = 'string'
        """true if operation is executed successfully"""
        self.success = None
        self.typeInfo['success'] = 'boolean'

