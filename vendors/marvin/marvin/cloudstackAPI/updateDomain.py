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


"""Updates a domain with a new name"""
from baseCmd import *
from baseResponse import *
class updateDomainCmd (baseCmd):
    typeInfo = {}
    def __init__(self):
        self.isAsync = "false"
        """ID of domain to update"""
        """Required"""
        self.id = None
        self.typeInfo['id'] = 'uuid'
        """updates domain with this name"""
        self.name = None
        self.typeInfo['name'] = 'string'
        """Network domain for the domain's networks; empty string will update domainName with NULL value"""
        self.networkdomain = None
        self.typeInfo['networkdomain'] = 'string'
        self.required = ["id",]

class updateDomainResponse (baseResponse):
    typeInfo = {}
    def __init__(self):
        """the ID of the domain"""
        self.id = None
        self.typeInfo['id'] = 'string'
        """whether the domain has one or more sub-domains"""
        self.haschild = None
        self.typeInfo['haschild'] = 'boolean'
        """the level of the domain"""
        self.level = None
        self.typeInfo['level'] = 'integer'
        """the name of the domain"""
        self.name = None
        self.typeInfo['name'] = 'string'
        """the network domain"""
        self.networkdomain = None
        self.typeInfo['networkdomain'] = 'string'
        """the domain ID of the parent domain"""
        self.parentdomainid = None
        self.typeInfo['parentdomainid'] = 'string'
        """the domain name of the parent domain"""
        self.parentdomainname = None
        self.typeInfo['parentdomainname'] = 'string'
        """the path of the domain"""
        self.path = None
        self.typeInfo['path'] = 'string'

