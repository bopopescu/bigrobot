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


"""Logs a user into the CloudStack. A successful login attempt will generate a JSESSIONID cookie value that can be passed in subsequent Query command calls until the "logout" command has been issued or the session has expired."""
from baseCmd import *
from baseResponse import *
class loginCmd (baseCmd):
    typeInfo = {}
    def __init__(self):
        self.isAsync = "false"
        """Hashed password (Default is MD5). If you wish to use any other hashing algorithm, you would need to write a custom authentication adapter See Docs section."""
        """Required"""
        self.password = None
        self.typeInfo['password'] = 'string'
        """Username"""
        """Required"""
        self.username = None
        self.typeInfo['username'] = 'string'
        """Path of the domain that the user belongs to. Example: domain=/com/cloud/internal. If no domain is passed in, the ROOT (/) domain is assumed."""
        self.domain = None
        self.typeInfo['domain'] = 'string'
        """The id of the domain that the user belongs to. If both domain and domainId are passed in, "domainId" parameter takes precendence"""
        self.domainId = None
        self.typeInfo['domainId'] = 'long'
        self.required = ["password","username",]

class loginResponse (baseResponse):
    typeInfo = {}
    def __init__(self):
        """the account name the user belongs to"""
        self.account = None
        self.typeInfo['account'] = 'string'
        """Domain ID that the user belongs to"""
        self.domainid = None
        self.typeInfo['domainid'] = 'string'
        """first name of the user"""
        self.firstname = None
        self.typeInfo['firstname'] = 'string'
        """last name of the user"""
        self.lastname = None
        self.typeInfo['lastname'] = 'string'
        """Is user registered"""
        self.registered = None
        self.typeInfo['registered'] = 'string'
        """Session key that can be passed in subsequent Query command calls"""
        self.sessionkey = None
        self.typeInfo['sessionkey'] = 'string'
        """the time period before the session has expired"""
        self.timeout = None
        self.typeInfo['timeout'] = 'integer'
        """user time zone"""
        self.timezone = None
        self.typeInfo['timezone'] = 'string'
        """the account type (admin, domain-admin, read-only-admin, user)"""
        self.type = None
        self.typeInfo['type'] = 'string'
        """User ID"""
        self.userid = None
        self.typeInfo['userid'] = 'string'
        """Username"""
        self.username = None
        self.typeInfo['username'] = 'string'

