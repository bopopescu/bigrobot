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


"""Lists SSL certificates"""
from baseCmd import *
from baseResponse import *
class listSslCertsCmd (baseCmd):
    typeInfo = {}
    def __init__(self):
        self.isAsync = "false"
        """Account Id"""
        self.accountid = None
        self.typeInfo['accountid'] = 'uuid'
        """Id of SSL certificate"""
        self.certid = None
        self.typeInfo['certid'] = 'uuid'
        """Loadbalancer Rule Id"""
        self.lbruleid = None
        self.typeInfo['lbruleid'] = 'uuid'
        """project who owns the ssl cert"""
        self.projectid = None
        self.typeInfo['projectid'] = 'uuid'
        self.required = []

class listSslCertsResponse (baseResponse):
    typeInfo = {}
    def __init__(self):
        """SSL certificate ID"""
        self.id = None
        self.typeInfo['id'] = 'string'
        """account for the certificate"""
        self.account = None
        self.typeInfo['account'] = 'string'
        """certificate chain"""
        self.certchain = None
        self.typeInfo['certchain'] = 'string'
        """certificate"""
        self.certificate = None
        self.typeInfo['certificate'] = 'string'
        """the domain name of the network owner"""
        self.domain = None
        self.typeInfo['domain'] = 'string'
        """the domain id of the network owner"""
        self.domainid = None
        self.typeInfo['domainid'] = 'string'
        """certificate fingerprint"""
        self.fingerprint = None
        self.typeInfo['fingerprint'] = 'string'
        """List of loabalancers this certificate is bound to"""
        self.loadbalancerrulelist = None
        self.typeInfo['loadbalancerrulelist'] = 'list'
        """the project name of the certificate"""
        self.project = None
        self.typeInfo['project'] = 'string'
        """the project id of the certificate"""
        self.projectid = None
        self.typeInfo['projectid'] = 'string'

