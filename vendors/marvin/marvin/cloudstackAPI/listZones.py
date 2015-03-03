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


"""Lists zones"""
from baseCmd import *
from baseResponse import *
class listZonesCmd (baseCmd):
    typeInfo = {}
    def __init__(self):
        self.isAsync = "false"
        """true if you want to retrieve all available Zones. False if you only want to return the Zones from which you have at least one VM. Default is false."""
        self.available = None
        self.typeInfo['available'] = 'boolean'
        """the ID of the domain associated with the zone"""
        self.domainid = None
        self.typeInfo['domainid'] = 'uuid'
        """the ID of the zone"""
        self.id = None
        self.typeInfo['id'] = 'uuid'
        """List by keyword"""
        self.keyword = None
        self.typeInfo['keyword'] = 'string'
        """the name of the zone"""
        self.name = None
        self.typeInfo['name'] = 'string'
        """the network type of the zone that the virtual machine belongs to"""
        self.networktype = None
        self.typeInfo['networktype'] = 'string'
        """"""
        self.page = None
        self.typeInfo['page'] = 'integer'
        """"""
        self.pagesize = None
        self.typeInfo['pagesize'] = 'integer'
        """flag to display the capacity of the zones"""
        self.showcapacities = None
        self.typeInfo['showcapacities'] = 'boolean'
        """List zones by resource tags (key/value pairs)"""
        self.tags = []
        self.typeInfo['tags'] = 'map'
        self.required = []

class listZonesResponse (baseResponse):
    typeInfo = {}
    def __init__(self):
        """Zone id"""
        self.id = None
        self.typeInfo['id'] = 'string'
        """the allocation state of the cluster"""
        self.allocationstate = None
        self.typeInfo['allocationstate'] = 'string'
        """Zone description"""
        self.description = None
        self.typeInfo['description'] = 'string'
        """the dhcp Provider for the Zone"""
        self.dhcpprovider = None
        self.typeInfo['dhcpprovider'] = 'string'
        """the display text of the zone"""
        self.displaytext = None
        self.typeInfo['displaytext'] = 'string'
        """the first DNS for the Zone"""
        self.dns1 = None
        self.typeInfo['dns1'] = 'string'
        """the second DNS for the Zone"""
        self.dns2 = None
        self.typeInfo['dns2'] = 'string'
        """Network domain name for the networks in the zone"""
        self.domain = None
        self.typeInfo['domain'] = 'string'
        """the UUID of the containing domain, null for public zones"""
        self.domainid = None
        self.typeInfo['domainid'] = 'string'
        """the name of the containing domain, null for public zones"""
        self.domainname = None
        self.typeInfo['domainname'] = 'string'
        """the guest CIDR address for the Zone"""
        self.guestcidraddress = None
        self.typeInfo['guestcidraddress'] = 'string'
        """the first internal DNS for the Zone"""
        self.internaldns1 = None
        self.typeInfo['internaldns1'] = 'string'
        """the second internal DNS for the Zone"""
        self.internaldns2 = None
        self.typeInfo['internaldns2'] = 'string'
        """the first IPv6 DNS for the Zone"""
        self.ip6dns1 = None
        self.typeInfo['ip6dns1'] = 'string'
        """the second IPv6 DNS for the Zone"""
        self.ip6dns2 = None
        self.typeInfo['ip6dns2'] = 'string'
        """true if local storage offering enabled, false otherwise"""
        self.localstorageenabled = None
        self.typeInfo['localstorageenabled'] = 'boolean'
        """Zone name"""
        self.name = None
        self.typeInfo['name'] = 'string'
        """the network type of the zone; can be Basic or Advanced"""
        self.networktype = None
        self.typeInfo['networktype'] = 'string'
        """Meta data associated with the zone (key/value pairs)"""
        self.resourcedetails = None
        self.typeInfo['resourcedetails'] = 'map'
        """true if security groups support is enabled, false otherwise"""
        self.securitygroupsenabled = None
        self.typeInfo['securitygroupsenabled'] = 'boolean'
        """Zone Token"""
        self.zonetoken = None
        self.typeInfo['zonetoken'] = 'string'
        """the capacity of the Zone"""
        self.capacity = []
        """the list of resource tags associated with zone."""
        self.tags = []

class capacity:
    def __init__(self):
        """"the total capacity available"""
        self.capacitytotal = None
        """"the capacity currently in use"""
        self.capacityused = None
        """"the Cluster ID"""
        self.clusterid = None
        """"the Cluster name"""
        self.clustername = None
        """"the percentage of capacity currently in use"""
        self.percentused = None
        """"the Pod ID"""
        self.podid = None
        """"the Pod name"""
        self.podname = None
        """"the capacity type"""
        self.type = None
        """"the Zone ID"""
        self.zoneid = None
        """"the Zone name"""
        self.zonename = None

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

