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


"""Lists site to site vpn customer gateways"""
from baseCmd import *
from baseResponse import *
class listVpnCustomerGatewaysCmd (baseCmd):
    typeInfo = {}
    def __init__(self):
        self.isAsync = "false"
        """list resources by account. Must be used with the domainId parameter."""
        self.account = None
        self.typeInfo['account'] = 'string'
        """list only resources belonging to the domain specified"""
        self.domainid = None
        self.typeInfo['domainid'] = 'uuid'
        """id of the customer gateway"""
        self.id = None
        self.typeInfo['id'] = 'uuid'
        """defaults to false, but if true, lists all resources from the parent specified by the domainId till leaves."""
        self.isrecursive = None
        self.typeInfo['isrecursive'] = 'boolean'
        """List by keyword"""
        self.keyword = None
        self.typeInfo['keyword'] = 'string'
        """If set to false, list only resources belonging to the command's caller; if set to true - list resources that the caller is authorized to see. Default value is false"""
        self.listall = None
        self.typeInfo['listall'] = 'boolean'
        """"""
        self.page = None
        self.typeInfo['page'] = 'integer'
        """"""
        self.pagesize = None
        self.typeInfo['pagesize'] = 'integer'
        """list objects by project"""
        self.projectid = None
        self.typeInfo['projectid'] = 'uuid'
        self.required = []

class listVpnCustomerGatewaysResponse (baseResponse):
    typeInfo = {}
    def __init__(self):
        """the vpn gateway ID"""
        self.id = None
        self.typeInfo['id'] = 'string'
        """the owner"""
        self.account = None
        self.typeInfo['account'] = 'string'
        """guest cidr list of the customer gateway"""
        self.cidrlist = None
        self.typeInfo['cidrlist'] = 'string'
        """the domain name of the owner"""
        self.domain = None
        self.typeInfo['domain'] = 'string'
        """the domain id of the owner"""
        self.domainid = None
        self.typeInfo['domainid'] = 'string'
        """if DPD is enabled for customer gateway"""
        self.dpd = None
        self.typeInfo['dpd'] = 'boolean'
        """Lifetime of ESP SA of customer gateway"""
        self.esplifetime = None
        self.typeInfo['esplifetime'] = 'long'
        """IPsec policy of customer gateway"""
        self.esppolicy = None
        self.typeInfo['esppolicy'] = 'string'
        """public ip address id of the customer gateway"""
        self.gateway = None
        self.typeInfo['gateway'] = 'string'
        """Lifetime of IKE SA of customer gateway"""
        self.ikelifetime = None
        self.typeInfo['ikelifetime'] = 'long'
        """IKE policy of customer gateway"""
        self.ikepolicy = None
        self.typeInfo['ikepolicy'] = 'string'
        """guest ip of the customer gateway"""
        self.ipaddress = None
        self.typeInfo['ipaddress'] = 'string'
        """IPsec preshared-key of customer gateway"""
        self.ipsecpsk = None
        self.typeInfo['ipsecpsk'] = 'string'
        """name of the customer gateway"""
        self.name = None
        self.typeInfo['name'] = 'string'
        """the project name"""
        self.project = None
        self.typeInfo['project'] = 'string'
        """the project id"""
        self.projectid = None
        self.typeInfo['projectid'] = 'string'
        """the date and time the host was removed"""
        self.removed = None
        self.typeInfo['removed'] = 'date'

