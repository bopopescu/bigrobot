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


"""Creates a port forwarding rule"""
from baseCmd import *
from baseResponse import *
class createPortForwardingRuleCmd (baseCmd):
    typeInfo = {}
    def __init__(self):
        self.isAsync = "true"
        """the IP address id of the port forwarding rule"""
        """Required"""
        self.ipaddressid = None
        self.typeInfo['ipaddressid'] = 'uuid'
        """the starting port of port forwarding rule's private port range"""
        """Required"""
        self.privateport = None
        self.typeInfo['privateport'] = 'integer'
        """the protocol for the port fowarding rule. Valid values are TCP or UDP."""
        """Required"""
        self.protocol = None
        self.typeInfo['protocol'] = 'string'
        """the starting port of port forwarding rule's public port range"""
        """Required"""
        self.publicport = None
        self.typeInfo['publicport'] = 'integer'
        """the ID of the virtual machine for the port forwarding rule"""
        """Required"""
        self.virtualmachineid = None
        self.typeInfo['virtualmachineid'] = 'uuid'
        """the cidr list to forward traffic from"""
        self.cidrlist = []
        self.typeInfo['cidrlist'] = 'list'
        """an optional field, whether to the display the rule to the end user or not"""
        self.fordisplay = None
        self.typeInfo['fordisplay'] = 'boolean'
        """The network of the vm the Port Forwarding rule will be created for. Required when public Ip address is not associated with any Guest network yet (VPC case)"""
        self.networkid = None
        self.typeInfo['networkid'] = 'uuid'
        """if true, firewall rule for source/end pubic port is automatically created; if false - firewall rule has to be created explicitely. If not specified 1) defaulted to false when PF rule is being created for VPC guest network 2) in all other cases defaulted to true"""
        self.openfirewall = None
        self.typeInfo['openfirewall'] = 'boolean'
        """the ending port of port forwarding rule's private port range"""
        self.privateendport = None
        self.typeInfo['privateendport'] = 'integer'
        """the ending port of port forwarding rule's private port range"""
        self.publicendport = None
        self.typeInfo['publicendport'] = 'integer'
        """VM guest nic Secondary ip address for the port forwarding rule"""
        self.vmguestip = None
        self.typeInfo['vmguestip'] = 'string'
        self.required = ["ipaddressid","privateport","protocol","publicport","virtualmachineid",]

class createPortForwardingRuleResponse (baseResponse):
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

