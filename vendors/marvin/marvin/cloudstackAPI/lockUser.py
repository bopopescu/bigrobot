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


"""Locks a user account"""
from baseCmd import *
from baseResponse import *
class lockUserCmd (baseCmd):
    typeInfo = {}
    def __init__(self):
        self.isAsync = "false"
        """Locks user by user ID."""
        """Required"""
        self.id = None
        self.typeInfo['id'] = 'uuid'
        self.required = ["id",]

class lockUserResponse (baseResponse):
    typeInfo = {}
    def __init__(self):
        """the user ID"""
        self.id = None
        self.typeInfo['id'] = 'string'
        """the account name of the user"""
        self.account = None
        self.typeInfo['account'] = 'string'
        """the account ID of the user"""
        self.accountid = None
        self.typeInfo['accountid'] = 'string'
        """the account type of the user"""
        self.accounttype = None
        self.typeInfo['accounttype'] = 'short'
        """the api key of the user"""
        self.apikey = None
        self.typeInfo['apikey'] = 'string'
        """the date and time the user account was created"""
        self.created = None
        self.typeInfo['created'] = 'date'
        """the domain name of the user"""
        self.domain = None
        self.typeInfo['domain'] = 'string'
        """the domain ID of the user"""
        self.domainid = None
        self.typeInfo['domainid'] = 'string'
        """the user email address"""
        self.email = None
        self.typeInfo['email'] = 'string'
        """the user firstname"""
        self.firstname = None
        self.typeInfo['firstname'] = 'string'
        """the boolean value representing if the updating target is in caller's child domain"""
        self.iscallerchilddomain = None
        self.typeInfo['iscallerchilddomain'] = 'boolean'
        """true if user is default, false otherwise"""
        self.isdefault = None
        self.typeInfo['isdefault'] = 'boolean'
        """the user lastname"""
        self.lastname = None
        self.typeInfo['lastname'] = 'string'
        """the secret key of the user"""
        self.secretkey = None
        self.typeInfo['secretkey'] = 'string'
        """the user state"""
        self.state = None
        self.typeInfo['state'] = 'string'
        """the timezone user was created in"""
        self.timezone = None
        self.typeInfo['timezone'] = 'string'
        """the user name"""
        self.username = None
        self.typeInfo['username'] = 'string'

