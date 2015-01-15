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


"""List virtual machine snapshot by conditions"""
from baseCmd import *
from baseResponse import *
class listVMSnapshotCmd (baseCmd):
    typeInfo = {}
    def __init__(self):
        self.isAsync = "false"
        """list resources by account. Must be used with the domainId parameter."""
        self.account = None
        self.typeInfo['account'] = 'string'
        """list only resources belonging to the domain specified"""
        self.domainid = None
        self.typeInfo['domainid'] = 'uuid'
        """defaults to false, but if true, lists all resources from the parent specified by the domainId till leaves."""
        self.isrecursive = None
        self.typeInfo['isrecursive'] = 'boolean'
        """List by keyword"""
        self.keyword = None
        self.typeInfo['keyword'] = 'string'
        """If set to false, list only resources belonging to the command's caller; if set to true - list resources that the caller is authorized to see. Default value is false"""
        self.listall = None
        self.typeInfo['listall'] = 'boolean'
        """lists snapshot by snapshot name or display name"""
        self.name = None
        self.typeInfo['name'] = 'string'
        """"""
        self.page = None
        self.typeInfo['page'] = 'integer'
        """"""
        self.pagesize = None
        self.typeInfo['pagesize'] = 'integer'
        """list objects by project"""
        self.projectid = None
        self.typeInfo['projectid'] = 'uuid'
        """state of the virtual machine snapshot"""
        self.state = None
        self.typeInfo['state'] = 'string'
        """List resources by tags (key/value pairs)"""
        self.tags = []
        self.typeInfo['tags'] = 'map'
        """the ID of the vm"""
        self.virtualmachineid = None
        self.typeInfo['virtualmachineid'] = 'uuid'
        """The ID of the VM snapshot"""
        self.vmsnapshotid = None
        self.typeInfo['vmsnapshotid'] = 'uuid'
        self.required = []

class listVMSnapshotResponse (baseResponse):
    typeInfo = {}
    def __init__(self):
        """the ID of the vm snapshot"""
        self.id = None
        self.typeInfo['id'] = 'string'
        """the account associated with the disk volume"""
        self.account = None
        self.typeInfo['account'] = 'string'
        """the create date of the vm snapshot"""
        self.created = None
        self.typeInfo['created'] = 'date'
        """indiates if this is current snapshot"""
        self.current = None
        self.typeInfo['current'] = 'boolean'
        """the description of the vm snapshot"""
        self.description = None
        self.typeInfo['description'] = 'string'
        """the display name of the vm snapshot"""
        self.displayname = None
        self.typeInfo['displayname'] = 'string'
        """the domain associated with the disk volume"""
        self.domain = None
        self.typeInfo['domain'] = 'string'
        """the ID of the domain associated with the disk volume"""
        self.domainid = None
        self.typeInfo['domainid'] = 'string'
        """the name of the vm snapshot"""
        self.name = None
        self.typeInfo['name'] = 'string'
        """the parent ID of the vm snapshot"""
        self.parent = None
        self.typeInfo['parent'] = 'string'
        """the parent displayName of the vm snapshot"""
        self.parentName = None
        self.typeInfo['parentName'] = 'string'
        """the project name of the vpn"""
        self.project = None
        self.typeInfo['project'] = 'string'
        """the project id of the vpn"""
        self.projectid = None
        self.typeInfo['projectid'] = 'string'
        """the state of the vm snapshot"""
        self.state = None
        self.typeInfo['state'] = 'state'
        """VM Snapshot type"""
        self.type = None
        self.typeInfo['type'] = 'string'
        """the vm ID of the vm snapshot"""
        self.virtualmachineid = None
        self.typeInfo['virtualmachineid'] = 'string'
        """the Zone ID of the vm snapshot"""
        self.zoneid = None
        self.typeInfo['zoneid'] = 'string'

