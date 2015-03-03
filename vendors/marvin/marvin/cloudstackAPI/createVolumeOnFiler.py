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


"""Create a volume"""
from baseCmd import *
from baseResponse import *
class createVolumeOnFilerCmd (baseCmd):
    typeInfo = {}
    def __init__(self):
        self.isAsync = "false"
        """aggregate name."""
        """Required"""
        self.aggregatename = None
        self.typeInfo['aggregatename'] = 'string'
        """ip address."""
        """Required"""
        self.ipaddress = None
        self.typeInfo['ipaddress'] = 'string'
        """password."""
        """Required"""
        self.password = None
        self.typeInfo['password'] = 'string'
        """pool name."""
        """Required"""
        self.poolname = None
        self.typeInfo['poolname'] = 'string'
        """volume size."""
        """Required"""
        self.size = None
        self.typeInfo['size'] = 'integer'
        """user name."""
        """Required"""
        self.username = None
        self.typeInfo['username'] = 'string'
        """volume name."""
        """Required"""
        self.volumename = None
        self.typeInfo['volumename'] = 'string'
        """snapshot policy."""
        self.snapshotpolicy = None
        self.typeInfo['snapshotpolicy'] = 'string'
        """snapshot reservation."""
        self.snapshotreservation = None
        self.typeInfo['snapshotreservation'] = 'integer'
        self.required = ["aggregatename","ipaddress","password","poolname","size","username","volumename",]

class createVolumeOnFilerResponse (baseResponse):
    typeInfo = {}
    def __init__(self):
        pass
