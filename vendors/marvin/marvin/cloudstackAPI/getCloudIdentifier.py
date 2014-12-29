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


"""Retrieves a cloud identifier."""
from baseCmd import *
from baseResponse import *
class getCloudIdentifierCmd (baseCmd):
    typeInfo = {}
    def __init__(self):
        self.isAsync = "false"
        """the user ID for the cloud identifier"""
        """Required"""
        self.userid = None
        self.typeInfo['userid'] = 'uuid'
        self.required = ["userid",]

class getCloudIdentifierResponse (baseResponse):
    typeInfo = {}
    def __init__(self):
        """the cloud identifier"""
        self.cloudidentifier = None
        self.typeInfo['cloudidentifier'] = 'string'
        """the signed response for the cloud identifier"""
        self.signature = None
        self.typeInfo['signature'] = 'string'
        """the user ID for the cloud identifier"""
        self.userid = None
        self.typeInfo['userid'] = 'string'

