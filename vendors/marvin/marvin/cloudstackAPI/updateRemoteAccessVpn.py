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


"""Updates remote access vpn"""
from baseCmd import *
from baseResponse import *
class updateRemoteAccessVpnCmd (baseCmd):
    typeInfo = {}
    def __init__(self):
        self.isAsync = "true"
        """id of the remote access vpn"""
        """Required"""
        self.id = None
        self.typeInfo['id'] = 'uuid'
        """an optional field, in case you want to set a custom id to the resource. Allowed to Root Admins only"""
        self.customid = None
        self.typeInfo['customid'] = 'string'
        """an optional field, whether to the display the vpn to the end user or not"""
        self.fordisplay = None
        self.typeInfo['fordisplay'] = 'boolean'
        self.required = ["id",]

class updateRemoteAccessVpnResponse (baseResponse):
    typeInfo = {}
    def __init__(self):
        """the id of the remote access vpn"""
        self.id = None
        self.typeInfo['id'] = 'string'
        """the account of the remote access vpn"""
        self.account = None
        self.typeInfo['account'] = 'string'
        """the domain name of the account of the remote access vpn"""
        self.domain = None
        self.typeInfo['domain'] = 'string'
        """the domain id of the account of the remote access vpn"""
        self.domainid = None
        self.typeInfo['domainid'] = 'string'
        """is vpn for display to the regular user"""
        self.fordisplay = None
        self.typeInfo['fordisplay'] = 'boolean'
        """the range of ips to allocate to the clients"""
        self.iprange = None
        self.typeInfo['iprange'] = 'string'
        """the ipsec preshared key"""
        self.presharedkey = None
        self.typeInfo['presharedkey'] = 'string'
        """the project name of the vpn"""
        self.project = None
        self.typeInfo['project'] = 'string'
        """the project id of the vpn"""
        self.projectid = None
        self.typeInfo['projectid'] = 'string'
        """the public ip address of the vpn server"""
        self.publicip = None
        self.typeInfo['publicip'] = 'string'
        """the public ip address of the vpn server"""
        self.publicipid = None
        self.typeInfo['publicipid'] = 'string'
        """the state of the rule"""
        self.state = None
        self.typeInfo['state'] = 'string'

