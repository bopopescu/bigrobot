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


"""Enable a Cisco Nexus VSM device"""
from baseCmd import *
from baseResponse import *
class enableCiscoNexusVSMCmd (baseCmd):
    typeInfo = {}
    def __init__(self):
        self.isAsync = "true"
        """Id of the Cisco Nexus 1000v VSM device to be enabled"""
        """Required"""
        self.id = None
        self.typeInfo['id'] = 'uuid'
        self.required = ["id",]

class enableCiscoNexusVSMResponse (baseResponse):
    typeInfo = {}
    def __init__(self):
        """the management IP address of the external Cisco Nexus 1000v Virtual Supervisor Module"""
        self.ipaddress = None
        self.typeInfo['ipaddress'] = 'string'
        """The mode of the VSM (standalone/HA)"""
        self.vsmconfigmode = None
        self.typeInfo['vsmconfigmode'] = 'string'
        """The Config State (Primary/Standby) of the VSM"""
        self.vsmconfigstate = None
        self.typeInfo['vsmconfigstate'] = 'string'
        """control vlan id of the VSM"""
        self.vsmctrlvlanid = None
        self.typeInfo['vsmctrlvlanid'] = 'int'
        """device id of the Cisco N1KV VSM device"""
        self.vsmdeviceid = None
        self.typeInfo['vsmdeviceid'] = 'string'
        """device name"""
        self.vsmdevicename = None
        self.typeInfo['vsmdevicename'] = 'string'
        """device state"""
        self.vsmdevicestate = None
        self.typeInfo['vsmdevicestate'] = 'string'
        """The Device State (Enabled/Disabled) of the VSM"""
        self.vsmdevicestate = None
        self.typeInfo['vsmdevicestate'] = 'string'
        """The VSM is a switch supervisor. This is the VSM's switch domain id"""
        self.vsmdomainid = None
        self.typeInfo['vsmdomainid'] = 'string'
        """management vlan id of the VSM"""
        self.vsmmgmtvlanid = None
        self.typeInfo['vsmmgmtvlanid'] = 'string'
        """packet vlan id of the VSM"""
        self.vsmpktvlanid = None
        self.typeInfo['vsmpktvlanid'] = 'int'
        """storage vlan id of the VSM"""
        self.vsmstoragevlanid = None
        self.typeInfo['vsmstoragevlanid'] = 'int'

