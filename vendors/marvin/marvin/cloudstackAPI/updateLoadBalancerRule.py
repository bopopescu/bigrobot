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


"""Updates load balancer"""
from baseCmd import *
from baseResponse import *
class updateLoadBalancerRuleCmd (baseCmd):
    typeInfo = {}
    def __init__(self):
        self.isAsync = "true"
        """the id of the load balancer rule to update"""
        """Required"""
        self.id = None
        self.typeInfo['id'] = 'uuid'
        """load balancer algorithm (source, roundrobin, leastconn)"""
        self.algorithm = None
        self.typeInfo['algorithm'] = 'string'
        """an optional field, in case you want to set a custom id to the resource. Allowed to Root Admins only"""
        self.customid = None
        self.typeInfo['customid'] = 'string'
        """the description of the load balancer rule"""
        self.description = None
        self.typeInfo['description'] = 'string'
        """an optional field, whether to the display the rule to the end user or not"""
        self.fordisplay = None
        self.typeInfo['fordisplay'] = 'boolean'
        """the name of the load balancer rule"""
        self.name = None
        self.typeInfo['name'] = 'string'
        self.required = ["id",]

class updateLoadBalancerRuleResponse (baseResponse):
    typeInfo = {}
    def __init__(self):
        """the load balancer rule ID"""
        self.id = None
        self.typeInfo['id'] = 'string'
        """the account of the load balancer rule"""
        self.account = None
        self.typeInfo['account'] = 'string'
        """the load balancer algorithm (source, roundrobin, leastconn)"""
        self.algorithm = None
        self.typeInfo['algorithm'] = 'string'
        """the cidr list to forward traffic from"""
        self.cidrlist = None
        self.typeInfo['cidrlist'] = 'string'
        """the description of the load balancer"""
        self.description = None
        self.typeInfo['description'] = 'string'
        """the domain of the load balancer rule"""
        self.domain = None
        self.typeInfo['domain'] = 'string'
        """the domain ID of the load balancer rule"""
        self.domainid = None
        self.typeInfo['domainid'] = 'string'
        """is rule for display to the regular user"""
        self.fordisplay = None
        self.typeInfo['fordisplay'] = 'boolean'
        """the name of the load balancer"""
        self.name = None
        self.typeInfo['name'] = 'string'
        """the id of the guest network the lb rule belongs to"""
        self.networkid = None
        self.typeInfo['networkid'] = 'string'
        """the private port"""
        self.privateport = None
        self.typeInfo['privateport'] = 'string'
        """the project name of the load balancer"""
        self.project = None
        self.typeInfo['project'] = 'string'
        """the project id of the load balancer"""
        self.projectid = None
        self.typeInfo['projectid'] = 'string'
        """the protocol of the loadbalanacer rule"""
        self.protocol = None
        self.typeInfo['protocol'] = 'string'
        """the public ip address"""
        self.publicip = None
        self.typeInfo['publicip'] = 'string'
        """the public ip address id"""
        self.publicipid = None
        self.typeInfo['publicipid'] = 'string'
        """the public port"""
        self.publicport = None
        self.typeInfo['publicport'] = 'string'
        """the state of the rule"""
        self.state = None
        self.typeInfo['state'] = 'string'
        """the id of the zone the rule belongs to"""
        self.zoneid = None
        self.typeInfo['zoneid'] = 'string'
        """the list of resource tags associated with load balancer"""
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

