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


"""Creates a Load Balancer"""
from baseCmd import *
from baseResponse import *
class createLoadBalancerCmd (baseCmd):
    typeInfo = {}
    def __init__(self):
        self.isAsync = "true"
        """load balancer algorithm (source, roundrobin, leastconn)"""
        """Required"""
        self.algorithm = None
        self.typeInfo['algorithm'] = 'string'
        """the TCP port of the virtual machine where the network traffic will be load balanced to"""
        """Required"""
        self.instanceport = None
        self.typeInfo['instanceport'] = 'integer'
        """name of the Load Balancer"""
        """Required"""
        self.name = None
        self.typeInfo['name'] = 'string'
        """The guest network the Load Balancer will be created for"""
        """Required"""
        self.networkid = None
        self.typeInfo['networkid'] = 'uuid'
        """the load balancer scheme. Supported value in this release is Internal"""
        """Required"""
        self.scheme = None
        self.typeInfo['scheme'] = 'string'
        """the network id of the source ip address"""
        """Required"""
        self.sourceipaddressnetworkid = None
        self.typeInfo['sourceipaddressnetworkid'] = 'uuid'
        """the source port the network traffic will be load balanced from"""
        """Required"""
        self.sourceport = None
        self.typeInfo['sourceport'] = 'integer'
        """the description of the Load Balancer"""
        self.description = None
        self.typeInfo['description'] = 'string'
        """an optional field, whether to the display the rule to the end user or not"""
        self.fordisplay = None
        self.typeInfo['fordisplay'] = 'boolean'
        """the source ip address the network traffic will be load balanced from"""
        self.sourceipaddress = None
        self.typeInfo['sourceipaddress'] = 'string'
        self.required = ["algorithm","instanceport","name","networkid","scheme","sourceipaddressnetworkid","sourceport",]

class createLoadBalancerResponse (baseResponse):
    typeInfo = {}
    def __init__(self):
        """the Load Balancer ID"""
        self.id = None
        self.typeInfo['id'] = 'string'
        """the account of the Load Balancer"""
        self.account = None
        self.typeInfo['account'] = 'string'
        """the load balancer algorithm (source, roundrobin, leastconn)"""
        self.algorithm = None
        self.typeInfo['algorithm'] = 'string'
        """the description of the Load Balancer"""
        self.description = None
        self.typeInfo['description'] = 'string'
        """the domain of the Load Balancer"""
        self.domain = None
        self.typeInfo['domain'] = 'string'
        """the domain ID of the Load Balancer"""
        self.domainid = None
        self.typeInfo['domainid'] = 'string'
        """is rule for display to the regular user"""
        self.fordisplay = None
        self.typeInfo['fordisplay'] = 'boolean'
        """the name of the Load Balancer"""
        self.name = None
        self.typeInfo['name'] = 'string'
        """Load Balancer network id"""
        self.networkid = None
        self.typeInfo['networkid'] = 'string'
        """the project name of the Load Balancer"""
        self.project = None
        self.typeInfo['project'] = 'string'
        """the project id of the Load Balancer"""
        self.projectid = None
        self.typeInfo['projectid'] = 'string'
        """Load Balancer source ip"""
        self.sourceipaddress = None
        self.typeInfo['sourceipaddress'] = 'string'
        """Load Balancer source ip network id"""
        self.sourceipaddressnetworkid = None
        self.typeInfo['sourceipaddressnetworkid'] = 'string'
        """the list of instances associated with the Load Balancer"""
        self.loadbalancerinstance = []
        """the list of rules associated with the Load Balancer"""
        self.loadbalancerrule = []
        """the list of resource tags associated with the Load Balancer"""
        self.tags = []

class loadbalancerinstance:
    def __init__(self):
        """"the instance ID"""
        self.id = None
        """"the ip address of the instance"""
        self.ipaddress = None
        """"the name of the instance"""
        self.name = None
        """"the state of the instance"""
        self.state = None

class loadbalancerrule:
    def __init__(self):
        """"instance port of the load balancer rule"""
        self.instanceport = None
        """"source port of the load balancer rule"""
        self.sourceport = None
        """"the state of the load balancer rule"""
        self.state = None

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

