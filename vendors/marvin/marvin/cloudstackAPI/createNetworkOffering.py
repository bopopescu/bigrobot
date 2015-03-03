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


"""Creates a network offering."""
from baseCmd import *
from baseResponse import *
class createNetworkOfferingCmd (baseCmd):
    typeInfo = {}
    def __init__(self):
        self.isAsync = "false"
        """the display text of the network offering"""
        """Required"""
        self.displaytext = None
        self.typeInfo['displaytext'] = 'string'
        """guest type of the network offering: Shared or Isolated"""
        """Required"""
        self.guestiptype = None
        self.typeInfo['guestiptype'] = 'string'
        """the name of the network offering"""
        """Required"""
        self.name = None
        self.typeInfo['name'] = 'string'
        """services supported by the network offering"""
        """Required"""
        self.supportedservices = []
        self.typeInfo['supportedservices'] = 'list'
        """the traffic type for the network offering. Supported type in current release is GUEST only"""
        """Required"""
        self.traffictype = None
        self.typeInfo['traffictype'] = 'string'
        """the availability of network offering. Default value is Optional"""
        self.availability = None
        self.typeInfo['availability'] = 'string'
        """true if the network offering is IP conserve mode enabled"""
        self.conservemode = None
        self.typeInfo['conservemode'] = 'boolean'
        """Network offering details in key/value pairs. Supported keys are internallbprovider/publiclbprovider with service provider as a value"""
        self.details = []
        self.typeInfo['details'] = 'map'
        """true if guest network default egress policy is allow; false if default egress policy is deny"""
        self.egressdefaultpolicy = None
        self.typeInfo['egressdefaultpolicy'] = 'boolean'
        """true if network offering supports persistent networks; defaulted to false if not specified"""
        self.ispersistent = None
        self.typeInfo['ispersistent'] = 'boolean'
        """if true keepalive will be turned on in the loadbalancer. At the time of writing this has only an effect on haproxy; the mode http and httpclose options are unset in the haproxy conf file."""
        self.keepaliveenabled = None
        self.typeInfo['keepaliveenabled'] = 'boolean'
        """maximum number of concurrent connections supported by the network offering"""
        self.maxconnections = None
        self.typeInfo['maxconnections'] = 'integer'
        """data transfer rate in megabits per second allowed"""
        self.networkrate = None
        self.typeInfo['networkrate'] = 'integer'
        """desired service capabilities as part of network offering"""
        self.servicecapabilitylist = []
        self.typeInfo['servicecapabilitylist'] = 'map'
        """the service offering ID used by virtual router provider"""
        self.serviceofferingid = None
        self.typeInfo['serviceofferingid'] = 'uuid'
        """provider to service mapping. If not specified, the provider for the service will be mapped to the default provider on the physical network"""
        self.serviceproviderlist = []
        self.typeInfo['serviceproviderlist'] = 'map'
        """true if network offering supports specifying ip ranges; defaulted to false if not specified"""
        self.specifyipranges = None
        self.typeInfo['specifyipranges'] = 'boolean'
        """true if network offering supports vlans"""
        self.specifyvlan = None
        self.typeInfo['specifyvlan'] = 'boolean'
        """the tags for the network offering."""
        self.tags = None
        self.typeInfo['tags'] = 'string'
        self.required = ["displaytext","guestiptype","name","supportedservices","traffictype",]

class createNetworkOfferingResponse (baseResponse):
    typeInfo = {}
    def __init__(self):
        """the id of the network offering"""
        self.id = None
        self.typeInfo['id'] = 'string'
        """availability of the network offering"""
        self.availability = None
        self.typeInfo['availability'] = 'string'
        """true if network offering is ip conserve mode enabled"""
        self.conservemode = None
        self.typeInfo['conservemode'] = 'boolean'
        """the date this network offering was created"""
        self.created = None
        self.typeInfo['created'] = 'date'
        """additional key/value details tied with network offering"""
        self.details = None
        self.typeInfo['details'] = 'map'
        """an alternate display text of the network offering."""
        self.displaytext = None
        self.typeInfo['displaytext'] = 'string'
        """true if guest network default egress policy is allow; false if default egress policy is deny"""
        self.egressdefaultpolicy = None
        self.typeInfo['egressdefaultpolicy'] = 'boolean'
        """true if network offering can be used by VPC networks only"""
        self.forvpc = None
        self.typeInfo['forvpc'] = 'boolean'
        """guest type of the network offering, can be Shared or Isolated"""
        self.guestiptype = None
        self.typeInfo['guestiptype'] = 'string'
        """true if network offering is default, false otherwise"""
        self.isdefault = None
        self.typeInfo['isdefault'] = 'boolean'
        """true if network offering supports persistent networks, false otherwise"""
        self.ispersistent = None
        self.typeInfo['ispersistent'] = 'boolean'
        """maximum number of concurrents connections to be handled by lb"""
        self.maxconnections = None
        self.typeInfo['maxconnections'] = 'integer'
        """the name of the network offering"""
        self.name = None
        self.typeInfo['name'] = 'string'
        """data transfer rate in megabits per second allowed."""
        self.networkrate = None
        self.typeInfo['networkrate'] = 'integer'
        """the ID of the service offering used by virtual router provider"""
        self.serviceofferingid = None
        self.typeInfo['serviceofferingid'] = 'string'
        """true if network offering supports specifying ip ranges, false otherwise"""
        self.specifyipranges = None
        self.typeInfo['specifyipranges'] = 'boolean'
        """true if network offering supports vlans, false otherwise"""
        self.specifyvlan = None
        self.typeInfo['specifyvlan'] = 'boolean'
        """state of the network offering. Can be Disabled/Enabled/Inactive"""
        self.state = None
        self.typeInfo['state'] = 'string'
        """true if network offering supports network that span multiple zones"""
        self.supportsstrechedl2subnet = None
        self.typeInfo['supportsstrechedl2subnet'] = 'boolean'
        """the tags for the network offering"""
        self.tags = None
        self.typeInfo['tags'] = 'string'
        """the traffic type for the network offering, supported types are Public, Management, Control, Guest, Vlan or Storage."""
        self.traffictype = None
        self.typeInfo['traffictype'] = 'string'
        """the list of supported services"""
        self.service = []

class capability:
    def __init__(self):
        """"can this service capability value can be choosable while creatine network offerings"""
        self.canchooseservicecapability = None
        """"the capability name"""
        self.name = None
        """"the capability value"""
        self.value = None

class provider:
    def __init__(self):
        """"uuid of the network provider"""
        self.id = None
        """"true if individual services can be enabled/disabled"""
        self.canenableindividualservice = None
        """"the destination physical network"""
        self.destinationphysicalnetworkid = None
        """"the provider name"""
        self.name = None
        """"the physical network this belongs to"""
        self.physicalnetworkid = None
        """"services for this provider"""
        self.servicelist = None
        """"state of the network provider"""
        self.state = None

class service:
    def __init__(self):
        """"the service name"""
        self.name = None
        """"the list of capabilities"""
        self.capability = []
        """"can this service capability value can be choosable while creatine network offerings"""
        self.canchooseservicecapability = None
        """"the capability name"""
        self.name = None
        """"the capability value"""
        self.value = None
        """"the service provider name"""
        self.provider = []
        """"uuid of the network provider"""
        self.id = None
        """"true if individual services can be enabled/disabled"""
        self.canenableindividualservice = None
        """"the destination physical network"""
        self.destinationphysicalnetworkid = None
        """"the provider name"""
        self.name = None
        """"the physical network this belongs to"""
        self.physicalnetworkid = None
        """"services for this provider"""
        self.servicelist = None
        """"state of the network provider"""
        self.state = None

