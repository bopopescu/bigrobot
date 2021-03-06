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


"""Create a LUN from a pool"""
from baseCmd import *
from baseResponse import *
class createLunOnFilerCmd (baseCmd):
    typeInfo = {}
    def __init__(self):
        self.isAsync = "false"
        """pool name."""
        """Required"""
        self.name = None
        self.typeInfo['name'] = 'string'
        """LUN size."""
        """Required"""
        self.size = None
        self.typeInfo['size'] = 'long'
        self.required = ["name","size",]

class createLunOnFilerResponse (baseResponse):
    typeInfo = {}
    def __init__(self):
        """ip address"""
        self.ipaddress = None
        self.typeInfo['ipaddress'] = 'string'
        """iqn"""
        self.iqn = None
        self.typeInfo['iqn'] = 'string'
        """pool path"""
        self.path = None
        self.typeInfo['path'] = 'string'

