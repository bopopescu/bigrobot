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


"""Updates the information about Guest OS"""
from baseCmd import *
from baseResponse import *
class updateGuestOsCmd (baseCmd):
    typeInfo = {}
    def __init__(self):
        self.isAsync = "true"
        """UUID of the Guest OS"""
        """Required"""
        self.id = None
        self.typeInfo['id'] = 'uuid'
        """Unique display name for Guest OS"""
        """Required"""
        self.osdisplayname = None
        self.typeInfo['osdisplayname'] = 'string'
        self.required = ["id","osdisplayname",]

class updateGuestOsResponse (baseResponse):
    typeInfo = {}
    def __init__(self):
        """the ID of the OS type"""
        self.id = None
        self.typeInfo['id'] = 'string'
        """the name/description of the OS type"""
        self.description = None
        self.typeInfo['description'] = 'string'
        """is the guest OS user defined"""
        self.isuserdefined = None
        self.typeInfo['isuserdefined'] = 'string'
        """the ID of the OS category"""
        self.oscategoryid = None
        self.typeInfo['oscategoryid'] = 'string'

