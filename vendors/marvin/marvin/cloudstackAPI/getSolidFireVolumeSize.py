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


"""Get the SF volume size including Hypervisor Snapshot Reserve"""
from baseCmd import *
from baseResponse import *
class getSolidFireVolumeSizeCmd (baseCmd):
    typeInfo = {}
    def __init__(self):
        self.isAsync = "false"
        """Storage Pool UUID"""
        """Required"""
        self.storageid = None
        self.typeInfo['storageid'] = 'string'
        """Volume UUID"""
        """Required"""
        self.volumeid = None
        self.typeInfo['volumeid'] = 'string'
        self.required = ["storageid","volumeid",]

class getSolidFireVolumeSizeResponse (baseResponse):
    typeInfo = {}
    def __init__(self):
        """SolidFire Volume Size Including Hypervisor Snapshot Reserve"""
        self.solidFireVolumeSize = None
        self.typeInfo['solidFireVolumeSize'] = 'long'

