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


"""Adds F5 external load balancer appliance."""
from baseCmd import *
from baseResponse import *
class addExternalLoadBalancerCmd (baseCmd):
    typeInfo = {}
    def __init__(self):
        self.isAsync = "false"
        """Password of the external load balancer appliance."""
        """Required"""
        self.password = None
        self.typeInfo['password'] = 'string'
        """URL of the external load balancer appliance."""
        """Required"""
        self.url = None
        self.typeInfo['url'] = 'string'
        """Username of the external load balancer appliance."""
        """Required"""
        self.username = None
        self.typeInfo['username'] = 'string'
        """Zone in which to add the external load balancer appliance."""
        """Required"""
        self.zoneid = None
        self.typeInfo['zoneid'] = 'uuid'
        self.required = ["password","url","username","zoneid",]

class addExternalLoadBalancerResponse (baseResponse):
    typeInfo = {}
    def __init__(self):
        """the ID of the external load balancer"""
        self.id = None
        self.typeInfo['id'] = 'string'
        """the management IP address of the external load balancer"""
        self.ipaddress = None
        self.typeInfo['ipaddress'] = 'string'
        """the number of times to retry requests to the external load balancer"""
        self.numretries = None
        self.typeInfo['numretries'] = 'string'
        """the private interface of the external load balancer"""
        self.privateinterface = None
        self.typeInfo['privateinterface'] = 'string'
        """the public interface of the external load balancer"""
        self.publicinterface = None
        self.typeInfo['publicinterface'] = 'string'
        """the username that's used to log in to the external load balancer"""
        self.username = None
        self.typeInfo['username'] = 'string'
        """the zone ID of the external load balancer"""
        self.zoneid = None
        self.typeInfo['zoneid'] = 'string'

