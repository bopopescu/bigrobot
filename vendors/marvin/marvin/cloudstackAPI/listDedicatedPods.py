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


"""Lists dedicated pods."""
from baseCmd import *
from baseResponse import *
class listDedicatedPodsCmd (baseCmd):
    typeInfo = {}
    def __init__(self):
        self.isAsync = "false"
        """the name of the account associated with the pod. Must be used with domainId."""
        self.account = None
        self.typeInfo['account'] = 'string'
        """list dedicated pods by affinity group"""
        self.affinitygroupid = None
        self.typeInfo['affinitygroupid'] = 'uuid'
        """the ID of the domain associated with the pod"""
        self.domainid = None
        self.typeInfo['domainid'] = 'uuid'
        """List by keyword"""
        self.keyword = None
        self.typeInfo['keyword'] = 'string'
        """"""
        self.page = None
        self.typeInfo['page'] = 'integer'
        """"""
        self.pagesize = None
        self.typeInfo['pagesize'] = 'integer'
        """the ID of the pod"""
        self.podid = None
        self.typeInfo['podid'] = 'uuid'
        self.required = []

class listDedicatedPodsResponse (baseResponse):
    typeInfo = {}
    def __init__(self):
        """the ID of the dedicated resource"""
        self.id = None
        self.typeInfo['id'] = 'string'
        """the Account Id to which the Pod is dedicated"""
        self.accountid = None
        self.typeInfo['accountid'] = 'string'
        """the Dedication Affinity Group ID of the pod"""
        self.affinitygroupid = None
        self.typeInfo['affinitygroupid'] = 'string'
        """the domain ID to which the Pod is dedicated"""
        self.domainid = None
        self.typeInfo['domainid'] = 'string'
        """the ID of the Pod"""
        self.podid = None
        self.typeInfo['podid'] = 'string'
        """the Name of the Pod"""
        self.podname = None
        self.typeInfo['podname'] = 'string'

