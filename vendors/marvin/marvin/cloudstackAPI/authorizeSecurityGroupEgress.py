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


"""Authorizes a particular egress rule for this security group"""
from baseCmd import *
from baseResponse import *
class authorizeSecurityGroupEgressCmd (baseCmd):
    typeInfo = {}
    def __init__(self):
        self.isAsync = "true"
        """an optional account for the security group. Must be used with domainId."""
        self.account = None
        self.typeInfo['account'] = 'string'
        """the cidr list associated"""
        self.cidrlist = []
        self.typeInfo['cidrlist'] = 'list'
        """an optional domainId for the security group. If the account parameter is used, domainId must also be used."""
        self.domainid = None
        self.typeInfo['domainid'] = 'uuid'
        """end port for this egress rule"""
        self.endport = None
        self.typeInfo['endport'] = 'integer'
        """error code for this icmp message"""
        self.icmpcode = None
        self.typeInfo['icmpcode'] = 'integer'
        """type of the icmp message being sent"""
        self.icmptype = None
        self.typeInfo['icmptype'] = 'integer'
        """an optional project of the security group"""
        self.projectid = None
        self.typeInfo['projectid'] = 'uuid'
        """TCP is default. UDP is the other supported protocol"""
        self.protocol = None
        self.typeInfo['protocol'] = 'string'
        """The ID of the security group. Mutually exclusive with securityGroupName parameter"""
        self.securitygroupid = None
        self.typeInfo['securitygroupid'] = 'uuid'
        """The name of the security group. Mutually exclusive with securityGroupName parameter"""
        self.securitygroupname = None
        self.typeInfo['securitygroupname'] = 'string'
        """start port for this egress rule"""
        self.startport = None
        self.typeInfo['startport'] = 'integer'
        """user to security group mapping"""
        self.usersecuritygrouplist = []
        self.typeInfo['usersecuritygrouplist'] = 'map'
        self.required = []

class authorizeSecurityGroupEgressResponse (baseResponse):
    typeInfo = {}
    def __init__(self):
        """account owning the security group rule"""
        self.account = None
        self.typeInfo['account'] = 'string'
        """the CIDR notation for the base IP address of the security group rule"""
        self.cidr = None
        self.typeInfo['cidr'] = 'string'
        """the ending IP of the security group rule"""
        self.endport = None
        self.typeInfo['endport'] = 'integer'
        """the code for the ICMP message response"""
        self.icmpcode = None
        self.typeInfo['icmpcode'] = 'integer'
        """the type of the ICMP message response"""
        self.icmptype = None
        self.typeInfo['icmptype'] = 'integer'
        """the protocol of the security group rule"""
        self.protocol = None
        self.typeInfo['protocol'] = 'string'
        """the id of the security group rule"""
        self.ruleid = None
        self.typeInfo['ruleid'] = 'string'
        """security group name"""
        self.securitygroupname = None
        self.typeInfo['securitygroupname'] = 'string'
        """the starting IP of the security group rule"""
        self.startport = None
        self.typeInfo['startport'] = 'integer'
        """the list of resource tags associated with the rule"""
        self.tags = []

class tags:
    def __init__(self):
        """"the account associated with the tag"""
        self.account = None
        """"customer associated with the tag"""
        self.customer = None
        """"the domain associated with the tag"""
        self.domain = None
        """"the ID of the domain associated with the tag"""
        self.domainid = None
        """"tag key name"""
        self.key = None
        """"the project name where tag belongs to"""
        self.project = None
        """"the project id the tag belongs to"""
        self.projectid = None
        """"id of the resource"""
        self.resourceid = None
        """"resource type"""
        self.resourcetype = None
        """"tag value"""
        self.value = None

