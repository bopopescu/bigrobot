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


"""A command to list events."""
from baseCmd import *
from baseResponse import *
class listEventsCmd (baseCmd):
    typeInfo = {}
    def __init__(self):
        self.isAsync = "false"
        """list resources by account. Must be used with the domainId parameter."""
        self.account = None
        self.typeInfo['account'] = 'string'
        """list only resources belonging to the domain specified"""
        self.domainid = None
        self.typeInfo['domainid'] = 'uuid'
        """the duration of the event"""
        self.duration = None
        self.typeInfo['duration'] = 'integer'
        """the end date range of the list you want to retrieve (use format "yyyy-MM-dd" or the new format "yyyy-MM-dd HH:mm:ss")"""
        self.enddate = None
        self.typeInfo['enddate'] = 'date'
        """the time the event was entered"""
        self.entrytime = None
        self.typeInfo['entrytime'] = 'integer'
        """the ID of the event"""
        self.id = None
        self.typeInfo['id'] = 'uuid'
        """defaults to false, but if true, lists all resources from the parent specified by the domainId till leaves."""
        self.isrecursive = None
        self.typeInfo['isrecursive'] = 'boolean'
        """List by keyword"""
        self.keyword = None
        self.typeInfo['keyword'] = 'string'
        """the event level (INFO, WARN, ERROR)"""
        self.level = None
        self.typeInfo['level'] = 'string'
        """If set to false, list only resources belonging to the command's caller; if set to true - list resources that the caller is authorized to see. Default value is false"""
        self.listall = None
        self.typeInfo['listall'] = 'boolean'
        """"""
        self.page = None
        self.typeInfo['page'] = 'integer'
        """"""
        self.pagesize = None
        self.typeInfo['pagesize'] = 'integer'
        """list objects by project"""
        self.projectid = None
        self.typeInfo['projectid'] = 'uuid'
        """the start date range of the list you want to retrieve (use format "yyyy-MM-dd" or the new format "yyyy-MM-dd HH:mm:ss")"""
        self.startdate = None
        self.typeInfo['startdate'] = 'date'
        """the event type (see event types)"""
        self.type = None
        self.typeInfo['type'] = 'string'
        self.required = []

class listEventsResponse (baseResponse):
    typeInfo = {}
    def __init__(self):
        """the ID of the event"""
        self.id = None
        self.typeInfo['id'] = 'string'
        """the account name for the account that owns the object being acted on in the event (e.g. the owner of the virtual machine, ip address, or security group)"""
        self.account = None
        self.typeInfo['account'] = 'string'
        """the date the event was created"""
        self.created = None
        self.typeInfo['created'] = 'date'
        """a brief description of the event"""
        self.description = None
        self.typeInfo['description'] = 'string'
        """the name of the account's domain"""
        self.domain = None
        self.typeInfo['domain'] = 'string'
        """the id of the account's domain"""
        self.domainid = None
        self.typeInfo['domainid'] = 'string'
        """the event level (INFO, WARN, ERROR)"""
        self.level = None
        self.typeInfo['level'] = 'string'
        """whether the event is parented"""
        self.parentid = None
        self.typeInfo['parentid'] = 'string'
        """the project name of the address"""
        self.project = None
        self.typeInfo['project'] = 'string'
        """the project id of the ipaddress"""
        self.projectid = None
        self.typeInfo['projectid'] = 'string'
        """the state of the event"""
        self.state = None
        self.typeInfo['state'] = 'state'
        """the type of the event (see event types)"""
        self.type = None
        self.typeInfo['type'] = 'string'
        """the name of the user who performed the action (can be different from the account if an admin is performing an action for a user, e.g. starting/stopping a user's virtual machine)"""
        self.username = None
        self.typeInfo['username'] = 'string'

