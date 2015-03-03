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


"""lists Palo Alto firewall devices in a physical network"""
from baseCmd import *
from baseResponse import *
class listPaloAltoFirewallsCmd (baseCmd):
    typeInfo = {}
    def __init__(self):
        self.isAsync = "false"
        """Palo Alto firewall device ID"""
        self.fwdeviceid = None
        self.typeInfo['fwdeviceid'] = 'uuid'
        """List by keyword"""
        self.keyword = None
        self.typeInfo['keyword'] = 'string'
        """"""
        self.page = None
        self.typeInfo['page'] = 'integer'
        """"""
        self.pagesize = None
        self.typeInfo['pagesize'] = 'integer'
        """the Physical Network ID"""
        self.physicalnetworkid = None
        self.typeInfo['physicalnetworkid'] = 'uuid'
        self.required = []

class listPaloAltoFirewallsResponse (baseResponse):
    typeInfo = {}
    def __init__(self):
        """device capacity"""
        self.fwdevicecapacity = None
        self.typeInfo['fwdevicecapacity'] = 'long'
        """device id of the Palo Alto firewall"""
        self.fwdeviceid = None
        self.typeInfo['fwdeviceid'] = 'string'
        """device name"""
        self.fwdevicename = None
        self.typeInfo['fwdevicename'] = 'string'
        """device state"""
        self.fwdevicestate = None
        self.typeInfo['fwdevicestate'] = 'string'
        """the management IP address of the external firewall"""
        self.ipaddress = None
        self.typeInfo['ipaddress'] = 'string'
        """the number of times to retry requests to the external firewall"""
        self.numretries = None
        self.typeInfo['numretries'] = 'string'
        """the physical network to which this Palo Alto firewall belongs to"""
        self.physicalnetworkid = None
        self.typeInfo['physicalnetworkid'] = 'string'
        """the private interface of the external firewall"""
        self.privateinterface = None
        self.typeInfo['privateinterface'] = 'string'
        """the private security zone of the external firewall"""
        self.privatezone = None
        self.typeInfo['privatezone'] = 'string'
        """name of the provider"""
        self.provider = None
        self.typeInfo['provider'] = 'string'
        """the public interface of the external firewall"""
        self.publicinterface = None
        self.typeInfo['publicinterface'] = 'string'
        """the public security zone of the external firewall"""
        self.publiczone = None
        self.typeInfo['publiczone'] = 'string'
        """the timeout (in seconds) for requests to the external firewall"""
        self.timeout = None
        self.typeInfo['timeout'] = 'string'
        """the usage interface of the external firewall"""
        self.usageinterface = None
        self.typeInfo['usageinterface'] = 'string'
        """the username that's used to log in to the external firewall"""
        self.username = None
        self.typeInfo['username'] = 'string'
        """the zone ID of the external firewall"""
        self.zoneid = None
        self.typeInfo['zoneid'] = 'string'

