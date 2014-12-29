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


"""Creates a load balancer rule"""
from baseCmd import *
from baseResponse import *
class createLoadBalancerRuleCmd (baseCmd):
    typeInfo = {}
    def __init__(self):
        self.isAsync = "true"
        """load balancer algorithm (source, roundrobin, leastconn)"""
        """Required"""
        self.algorithm = None
        self.typeInfo['algorithm'] = 'string'
        """name of the load balancer rule"""
        """Required"""
        self.name = None
        self.typeInfo['name'] = 'string'
        """the private port of the private ip address/virtual machine where the network traffic will be load balanced to"""
        """Required"""
        self.privateport = None
        self.typeInfo['privateport'] = 'integer'
        """the public port from where the network traffic will be load balanced from"""
        """Required"""
        self.publicport = None
        self.typeInfo['publicport'] = 'integer'
        """the account associated with the load balancer. Must be used with the domainId parameter."""
        self.account = None
        self.typeInfo['account'] = 'string'
        """the cidr list to forward traffic from"""
        self.cidrlist = []
        self.typeInfo['cidrlist'] = 'list'
        """the description of the load balancer rule"""
        self.description = None
        self.typeInfo['description'] = 'string'
        """the domain ID associated with the load balancer"""
        self.domainid = None
        self.typeInfo['domainid'] = 'uuid'
        """an optional field, whether to the display the rule to the end user or not"""
        self.fordisplay = None
        self.typeInfo['fordisplay'] = 'boolean'
        """The guest network this rule will be created for. Required when public Ip address is not associated with any Guest network yet (VPC case)"""
        self.networkid = None
        self.typeInfo['networkid'] = 'uuid'
        """if true, firewall rule for source/end pubic port is automatically created; if false - firewall rule has to be created explicitely. If not specified 1) defaulted to false when LB rule is being created for VPC guest network 2) in all other cases defaulted to true"""
        self.openfirewall = None
        self.typeInfo['openfirewall'] = 'boolean'
        """The protocol for the LB"""
        self.protocol = None
        self.typeInfo['protocol'] = 'string'
        """public ip address id from where the network traffic will be load balanced from"""
        self.publicipid = None
        self.typeInfo['publicipid'] = 'uuid'
        """zone where the load balancer is going to be created. This parameter is required when LB service provider is ElasticLoadBalancerVm"""
        self.zoneid = None
        self.typeInfo['zoneid'] = 'uuid'
        self.required = ["algorithm","name","privateport","publicport",]

class createLoadBalancerRuleResponse (baseResponse):
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

