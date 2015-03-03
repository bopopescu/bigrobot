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


"""Upgrades domain router to a new service offering"""
from baseCmd import *
from baseResponse import *
class changeServiceForRouterCmd (baseCmd):
    typeInfo = {}
    def __init__(self):
        self.isAsync = "false"
        """The ID of the router"""
        """Required"""
        self.id = None
        self.typeInfo['id'] = 'uuid'
        """the service offering ID to apply to the domain router"""
        """Required"""
        self.serviceofferingid = None
        self.typeInfo['serviceofferingid'] = 'uuid'
        self.required = ["id","serviceofferingid",]

class changeServiceForRouterResponse (baseResponse):
    typeInfo = {}
    def __init__(self):
        """the id of the router"""
        self.id = None
        self.typeInfo['id'] = 'string'
        """the account associated with the router"""
        self.account = None
        self.typeInfo['account'] = 'string'
        """the date and time the router was created"""
        self.created = None
        self.typeInfo['created'] = 'date'
        """the first DNS for the router"""
        self.dns1 = None
        self.typeInfo['dns1'] = 'string'
        """the second DNS for the router"""
        self.dns2 = None
        self.typeInfo['dns2'] = 'string'
        """the domain associated with the router"""
        self.domain = None
        self.typeInfo['domain'] = 'string'
        """the domain ID associated with the router"""
        self.domainid = None
        self.typeInfo['domainid'] = 'string'
        """the gateway for the router"""
        self.gateway = None
        self.typeInfo['gateway'] = 'string'
        """the guest IP address for the router"""
        self.guestipaddress = None
        self.typeInfo['guestipaddress'] = 'string'
        """the guest MAC address for the router"""
        self.guestmacaddress = None
        self.typeInfo['guestmacaddress'] = 'string'
        """the guest netmask for the router"""
        self.guestnetmask = None
        self.typeInfo['guestnetmask'] = 'string'
        """the ID of the corresponding guest network"""
        self.guestnetworkid = None
        self.typeInfo['guestnetworkid'] = 'string'
        """the host ID for the router"""
        self.hostid = None
        self.typeInfo['hostid'] = 'string'
        """the hostname for the router"""
        self.hostname = None
        self.typeInfo['hostname'] = 'string'
        """the hypervisor on which the template runs"""
        self.hypervisor = None
        self.typeInfo['hypervisor'] = 'string'
        """the first IPv6 DNS for the router"""
        self.ip6dns1 = None
        self.typeInfo['ip6dns1'] = 'string'
        """the second IPv6 DNS for the router"""
        self.ip6dns2 = None
        self.typeInfo['ip6dns2'] = 'string'
        """if this router is an redundant virtual router"""
        self.isredundantrouter = None
        self.typeInfo['isredundantrouter'] = 'boolean'
        """the link local IP address for the router"""
        self.linklocalip = None
        self.typeInfo['linklocalip'] = 'string'
        """the link local MAC address for the router"""
        self.linklocalmacaddress = None
        self.typeInfo['linklocalmacaddress'] = 'string'
        """the link local netmask for the router"""
        self.linklocalnetmask = None
        self.typeInfo['linklocalnetmask'] = 'string'
        """the ID of the corresponding link local network"""
        self.linklocalnetworkid = None
        self.typeInfo['linklocalnetworkid'] = 'string'
        """the name of the router"""
        self.name = None
        self.typeInfo['name'] = 'string'
        """the network domain for the router"""
        self.networkdomain = None
        self.typeInfo['networkdomain'] = 'string'
        """the Pod ID for the router"""
        self.podid = None
        self.typeInfo['podid'] = 'string'
        """the project name of the address"""
        self.project = None
        self.typeInfo['project'] = 'string'
        """the project id of the ipaddress"""
        self.projectid = None
        self.typeInfo['projectid'] = 'string'
        """the public IP address for the router"""
        self.publicip = None
        self.typeInfo['publicip'] = 'string'
        """the public MAC address for the router"""
        self.publicmacaddress = None
        self.typeInfo['publicmacaddress'] = 'string'
        """the public netmask for the router"""
        self.publicnetmask = None
        self.typeInfo['publicnetmask'] = 'string'
        """the ID of the corresponding public network"""
        self.publicnetworkid = None
        self.typeInfo['publicnetworkid'] = 'string'
        """the state of redundant virtual router"""
        self.redundantstate = None
        self.typeInfo['redundantstate'] = 'string'
        """true if the router template requires upgrader"""
        self.requiresupgrade = None
        self.typeInfo['requiresupgrade'] = 'boolean'
        """role of the domain router"""
        self.role = None
        self.typeInfo['role'] = 'string'
        """the version of scripts"""
        self.scriptsversion = None
        self.typeInfo['scriptsversion'] = 'string'
        """the ID of the service offering of the virtual machine"""
        self.serviceofferingid = None
        self.typeInfo['serviceofferingid'] = 'string'
        """the name of the service offering of the virtual machine"""
        self.serviceofferingname = None
        self.typeInfo['serviceofferingname'] = 'string'
        """the state of the router"""
        self.state = None
        self.typeInfo['state'] = 'state'
        """the template ID for the router"""
        self.templateid = None
        self.typeInfo['templateid'] = 'string'
        """the version of template"""
        self.version = None
        self.typeInfo['version'] = 'string'
        """VPC the router belongs to"""
        self.vpcid = None
        self.typeInfo['vpcid'] = 'string'
        """the Zone ID for the router"""
        self.zoneid = None
        self.typeInfo['zoneid'] = 'string'
        """the Zone name for the router"""
        self.zonename = None
        self.typeInfo['zonename'] = 'string'
        """the list of nics associated with the router"""
        self.nic = []

class nic:
    def __init__(self):
        """"the ID of the nic"""
        self.id = None
        """"the broadcast uri of the nic"""
        self.broadcasturi = None
        """"device id for the network when plugged into the virtual machine"""
        self.deviceid = None
        """"the gateway of the nic"""
        self.gateway = None
        """"the IPv6 address of network"""
        self.ip6address = None
        """"the cidr of IPv6 network"""
        self.ip6cidr = None
        """"the gateway of IPv6 network"""
        self.ip6gateway = None
        """"the ip address of the nic"""
        self.ipaddress = None
        """"true if nic is default, false otherwise"""
        self.isdefault = None
        """"the isolation uri of the nic"""
        self.isolationuri = None
        """"true if nic is default, false otherwise"""
        self.macaddress = None
        """"the netmask of the nic"""
        self.netmask = None
        """"the ID of the corresponding network"""
        self.networkid = None
        """"the name of the corresponding network"""
        self.networkname = None
        """"the Secondary ipv4 addr of nic"""
        self.secondaryip = None
        """"the traffic type of the nic"""
        self.traffictype = None
        """"the type of the nic"""
        self.type = None
        """"Id of the vm to which the nic belongs"""
        self.virtualmachineid = None

