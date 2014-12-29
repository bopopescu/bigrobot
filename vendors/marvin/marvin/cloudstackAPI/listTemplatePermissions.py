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


"""List template visibility and all accounts that have permissions to view this template."""
from baseCmd import *
from baseResponse import *
class listTemplatePermissionsCmd (baseCmd):
    typeInfo = {}
    def __init__(self):
        self.isAsync = "false"
        """the template ID"""
        """Required"""
        self.id = None
        self.typeInfo['id'] = 'uuid'
        self.required = ["id",]

class listTemplatePermissionsResponse (baseResponse):
    typeInfo = {}
    def __init__(self):
        """the template ID"""
        self.id = None
        self.typeInfo['id'] = 'string'
        """the list of accounts the template is available for"""
        self.account = None
        self.typeInfo['account'] = 'list'
        """the ID of the domain to which the template belongs"""
        self.domainid = None
        self.typeInfo['domainid'] = 'string'
        """true if this template is a public template, false otherwise"""
        self.ispublic = None
        self.typeInfo['ispublic'] = 'boolean'
        """the list of projects the template is available for"""
        self.projectids = None
        self.typeInfo['projectids'] = 'list'

