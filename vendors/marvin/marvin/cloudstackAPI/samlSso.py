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


"""SP initiated SAML Single Sign On"""
from baseCmd import *
from baseResponse import *
class samlSsoCmd (baseCmd):
    typeInfo = {}
    def __init__(self):
        self.isAsync = "false"
        """Identity Provider SSO HTTP-Redirect binding URL"""
        """Required"""
        self.idpurl = None
        self.typeInfo['idpurl'] = 'string'
        self.required = ["idpurl",]

class samlSsoResponse (baseResponse):
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

