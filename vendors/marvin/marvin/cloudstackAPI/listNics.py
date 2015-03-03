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


"""list the vm nics  IP to NIC"""
from baseCmd import *
from baseResponse import *
class listNicsCmd (baseCmd):
    typeInfo = {}
    def __init__(self):
        self.isAsync = "false"
        """the ID of the vm"""
        """Required"""
        self.virtualmachineid = None
        self.typeInfo['virtualmachineid'] = 'uuid'
        """list resources by display flag; only ROOT admin is eligible to pass this parameter"""
        self.fordisplay = None
        self.typeInfo['fordisplay'] = 'boolean'
        """List by keyword"""
        self.keyword = None
        self.typeInfo['keyword'] = 'string'
        """list nic of the specific vm's network"""
        self.networkid = None
        self.typeInfo['networkid'] = 'uuid'
        """the ID of the nic to to list IPs"""
        self.nicid = None
        self.typeInfo['nicid'] = 'uuid'
        """"""
        self.page = None
        self.typeInfo['page'] = 'integer'
        """"""
        self.pagesize = None
        self.typeInfo['pagesize'] = 'integer'
        self.required = ["virtualmachineid",]

class listNicsResponse (baseResponse):
    typeInfo = {}
    def __init__(self):
        """the ID of the nic"""
        self.id = None
        self.typeInfo['id'] = 'string'
        """the broadcast uri of the nic"""
        self.broadcasturi = None
        self.typeInfo['broadcasturi'] = 'string'
        """device id for the network when plugged into the virtual machine"""
        self.deviceid = None
        self.typeInfo['deviceid'] = 'string'
        """the gateway of the nic"""
        self.gateway = None
        self.typeInfo['gateway'] = 'string'
        """the IPv6 address of network"""
        self.ip6address = None
        self.typeInfo['ip6address'] = 'string'
        """the cidr of IPv6 network"""
        self.ip6cidr = None
        self.typeInfo['ip6cidr'] = 'string'
        """the gateway of IPv6 network"""
        self.ip6gateway = None
        self.typeInfo['ip6gateway'] = 'string'
        """the ip address of the nic"""
        self.ipaddress = None
        self.typeInfo['ipaddress'] = 'string'
        """true if nic is default, false otherwise"""
        self.isdefault = None
        self.typeInfo['isdefault'] = 'boolean'
        """the isolation uri of the nic"""
        self.isolationuri = None
        self.typeInfo['isolationuri'] = 'string'
        """true if nic is default, false otherwise"""
        self.macaddress = None
        self.typeInfo['macaddress'] = 'string'
        """the netmask of the nic"""
        self.netmask = None
        self.typeInfo['netmask'] = 'string'
        """the ID of the corresponding network"""
        self.networkid = None
        self.typeInfo['networkid'] = 'string'
        """the name of the corresponding network"""
        self.networkname = None
        self.typeInfo['networkname'] = 'string'
        """the Secondary ipv4 addr of nic"""
        self.secondaryip = None
        self.typeInfo['secondaryip'] = 'list'
        """the traffic type of the nic"""
        self.traffictype = None
        self.typeInfo['traffictype'] = 'string'
        """the type of the nic"""
        self.type = None
        self.typeInfo['type'] = 'string'
        """Id of the vm to which the nic belongs"""
        self.virtualmachineid = None
        self.typeInfo['virtualmachineid'] = 'string'

