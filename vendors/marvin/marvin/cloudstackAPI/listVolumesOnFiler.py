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


"""List Volumes"""
from baseCmd import *
from baseResponse import *
class listVolumesOnFilerCmd (baseCmd):
    typeInfo = {}
    def __init__(self):
        self.isAsync = "false"
        """pool name."""
        """Required"""
        self.poolname = None
        self.typeInfo['poolname'] = 'string'
        self.required = ["poolname",]

class listVolumesOnFilerResponse (baseResponse):
    typeInfo = {}
    def __init__(self):
        """volume id"""
        self.id = None
        self.typeInfo['id'] = 'long'
        """Aggregate name"""
        self.aggregatename = None
        self.typeInfo['aggregatename'] = 'string'
        """ip address"""
        self.ipaddress = None
        self.typeInfo['ipaddress'] = 'string'
        """pool name"""
        self.poolname = None
        self.typeInfo['poolname'] = 'string'
        """volume size"""
        self.size = None
        self.typeInfo['size'] = 'string'
        """snapshot policy"""
        self.snapshotpolicy = None
        self.typeInfo['snapshotpolicy'] = 'string'
        """snapshot reservation"""
        self.snapshotreservation = None
        self.typeInfo['snapshotreservation'] = 'integer'
        """Volume name"""
        self.volumename = None
        self.typeInfo['volumename'] = 'string'

