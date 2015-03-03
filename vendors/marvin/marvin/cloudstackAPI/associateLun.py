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


"""Associate a LUN with a guest IQN"""
from baseCmd import *
from baseResponse import *
class associateLunCmd (baseCmd):
    typeInfo = {}
    def __init__(self):
        self.isAsync = "false"
        """Guest IQN to which the LUN associate."""
        """Required"""
        self.iqn = None
        self.typeInfo['iqn'] = 'string'
        """LUN name."""
        """Required"""
        self.name = None
        self.typeInfo['name'] = 'string'
        self.required = ["iqn","name",]

class associateLunResponse (baseResponse):
    typeInfo = {}
    def __init__(self):
        """the LUN id"""
        self.id = None
        self.typeInfo['id'] = 'string'
        """the IP address of"""
        self.ipaddress = None
        self.typeInfo['ipaddress'] = 'string'
        """the target IQN"""
        self.targetiqn = None
        self.typeInfo['targetiqn'] = 'string'

