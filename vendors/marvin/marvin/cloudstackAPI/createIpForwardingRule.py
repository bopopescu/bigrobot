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


"""Creates an ip forwarding rule"""
from baseCmd import *
from baseResponse import *
class createIpForwardingRuleCmd (baseCmd):
    typeInfo = {}
    def __init__(self):
        self.isAsync = "true"
        """the public IP address id of the forwarding rule, already associated via associateIp"""
        """Required"""
        self.ipaddressid = None
        self.typeInfo['ipaddressid'] = 'uuid'
        """the protocol for the rule. Valid values are TCP or UDP."""
        """Required"""
        self.protocol = None
        self.typeInfo['protocol'] = 'string'
        """the start port for the rule"""
        """Required"""
        self.startport = None
        self.typeInfo['startport'] = 'integer'
        """the cidr list to forward traffic from"""
        self.cidrlist = []
        self.typeInfo['cidrlist'] = 'list'
        """the end port for the rule"""
        self.endport = None
        self.typeInfo['endport'] = 'integer'
        """if true, firewall rule for source/end pubic port is automatically created; if false - firewall rule has to be created explicitely. Has value true by default"""
        self.openfirewall = None
        self.typeInfo['openfirewall'] = 'boolean'
        self.required = ["ipaddressid","protocol","startport",]

class createIpForwardingRuleResponse (baseResponse):
    typeInfo = {}
    def __init__(self):
        """the ID of the port forwarding rule"""
        self.id = None
        self.typeInfo['id'] = 'string'
        """the cidr list to forward traffic from"""
        self.cidrlist = None
        self.typeInfo['cidrlist'] = 'string'
        """is firewall for display to the regular user"""
        self.fordisplay = None
        self.typeInfo['fordisplay'] = 'boolean'
        """the public ip address for the port forwarding rule"""
        self.ipaddress = None
        self.typeInfo['ipaddress'] = 'string'
        """the public ip address id for the port forwarding rule"""
        self.ipaddressid = None
        self.typeInfo['ipaddressid'] = 'string'
        """the id of the guest network the port forwarding rule belongs to"""
        self.networkid = None
        self.typeInfo['networkid'] = 'string'
        """the ending port of port forwarding rule's private port range"""
        self.privateendport = None
        self.typeInfo['privateendport'] = 'string'
        """the starting port of port forwarding rule's private port range"""
        self.privateport = None
        self.typeInfo['privateport'] = 'string'
        """the protocol of the port forwarding rule"""
        self.protocol = None
        self.typeInfo['protocol'] = 'string'
        """the ending port of port forwarding rule's private port range"""
        self.publicendport = None
        self.typeInfo['publicendport'] = 'string'
        """the starting port of port forwarding rule's public port range"""
        self.publicport = None
        self.typeInfo['publicport'] = 'string'
        """the state of the rule"""
        self.state = None
        self.typeInfo['state'] = 'string'
        """the VM display name for the port forwarding rule"""
        self.virtualmachinedisplayname = None
        self.typeInfo['virtualmachinedisplayname'] = 'string'
        """the VM ID for the port forwarding rule"""
        self.virtualmachineid = None
        self.typeInfo['virtualmachineid'] = 'string'
        """the VM name for the port forwarding rule"""
        self.virtualmachinename = None
        self.typeInfo['virtualmachinename'] = 'string'
        """the vm ip address for the port forwarding rule"""
        self.vmguestip = None
        self.typeInfo['vmguestip'] = 'string'
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

