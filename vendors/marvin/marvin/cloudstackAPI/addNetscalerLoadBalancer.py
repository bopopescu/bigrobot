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


"""Adds a netscaler load balancer device"""
from baseCmd import *
from baseResponse import *
class addNetscalerLoadBalancerCmd (baseCmd):
    typeInfo = {}
    def __init__(self):
        self.isAsync = "true"
        """Netscaler device type supports NetscalerMPXLoadBalancer, NetscalerVPXLoadBalancer, NetscalerSDXLoadBalancer"""
        """Required"""
        self.networkdevicetype = None
        self.typeInfo['networkdevicetype'] = 'string'
        """Credentials to reach netscaler load balancer device"""
        """Required"""
        self.password = None
        self.typeInfo['password'] = 'string'
        """the Physical Network ID"""
        """Required"""
        self.physicalnetworkid = None
        self.typeInfo['physicalnetworkid'] = 'uuid'
        """URL of the netscaler load balancer appliance."""
        """Required"""
        self.url = None
        self.typeInfo['url'] = 'string'
        """Credentials to reach netscaler load balancer device"""
        """Required"""
        self.username = None
        self.typeInfo['username'] = 'string'
        """true if NetScaler device being added is for providing GSLB service"""
        self.gslbprovider = None
        self.typeInfo['gslbprovider'] = 'boolean'
        """public IP of the site"""
        self.gslbproviderprivateip = None
        self.typeInfo['gslbproviderprivateip'] = 'string'
        """public IP of the site"""
        self.gslbproviderpublicip = None
        self.typeInfo['gslbproviderpublicip'] = 'string'
        """true if NetScaler device being added is for providing GSLB service exclusively and can not be used for LB"""
        self.isexclusivegslbprovider = None
        self.typeInfo['isexclusivegslbprovider'] = 'boolean'
        self.required = ["networkdevicetype","password","physicalnetworkid","url","username",]

class addNetscalerLoadBalancerResponse (baseResponse):
    typeInfo = {}
    def __init__(self):
        """true if NetScaler device is provisioned to be a GSLB service provider"""
        self.gslbprovider = None
        self.typeInfo['gslbprovider'] = 'boolean'
        """private IP of the NetScaler representing GSLB site"""
        self.gslbproviderprivateip = None
        self.typeInfo['gslbproviderprivateip'] = 'string'
        """public IP of the NetScaler representing GSLB site"""
        self.gslbproviderpublicip = None
        self.typeInfo['gslbproviderpublicip'] = 'string'
        """the management IP address of the external load balancer"""
        self.ipaddress = None
        self.typeInfo['ipaddress'] = 'string'
        """true if NetScaler device is provisioned exclusively to be a GSLB service provider"""
        self.isexclusivegslbprovider = None
        self.typeInfo['isexclusivegslbprovider'] = 'boolean'
        """device capacity"""
        self.lbdevicecapacity = None
        self.typeInfo['lbdevicecapacity'] = 'long'
        """true if device is dedicated for an account"""
        self.lbdevicededicated = None
        self.typeInfo['lbdevicededicated'] = 'boolean'
        """device id of the netscaler load balancer"""
        self.lbdeviceid = None
        self.typeInfo['lbdeviceid'] = 'string'
        """device name"""
        self.lbdevicename = None
        self.typeInfo['lbdevicename'] = 'string'
        """device state"""
        self.lbdevicestate = None
        self.typeInfo['lbdevicestate'] = 'string'
        """the physical network to which this netscaler device belongs to"""
        self.physicalnetworkid = None
        self.typeInfo['physicalnetworkid'] = 'string'
        """Used when NetScaler device is provider of EIP service. This parameter represents the list of pod's, for which there exists a policy based route on datacenter L3 router to route pod's subnet IP to a NetScaler device."""
        self.podids = None
        self.typeInfo['podids'] = 'list'
        """the private interface of the load balancer"""
        self.privateinterface = None
        self.typeInfo['privateinterface'] = 'string'
        """name of the provider"""
        self.provider = None
        self.typeInfo['provider'] = 'string'
        """the public interface of the load balancer"""
        self.publicinterface = None
        self.typeInfo['publicinterface'] = 'string'

