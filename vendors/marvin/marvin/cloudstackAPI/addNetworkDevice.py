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


"""Adds a network device of one of the following types: ExternalDhcp, ExternalFirewall, ExternalLoadBalancer, PxeServer"""
from baseCmd import *
from baseResponse import *
class addNetworkDeviceCmd (baseCmd):
    typeInfo = {}
    def __init__(self):
        self.isAsync = "false"
        """parameters for network device"""
        self.networkdeviceparameterlist = []
        self.typeInfo['networkdeviceparameterlist'] = 'map'
        """Network device type, now supports ExternalDhcp, PxeServer, NetscalerMPXLoadBalancer, NetscalerVPXLoadBalancer, NetscalerSDXLoadBalancer, F5BigIpLoadBalancer, JuniperSRXFirewall, PaloAltoFirewall"""
        self.networkdevicetype = None
        self.typeInfo['networkdevicetype'] = 'string'
        self.required = []

class addNetworkDeviceResponse (baseResponse):
    typeInfo = {}
    def __init__(self):
        """the ID of the network device"""
        self.id = None
        self.typeInfo['id'] = 'string'

