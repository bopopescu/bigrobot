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


"""Lists project's accounts"""
from baseCmd import *
from baseResponse import *
class listProjectAccountsCmd (baseCmd):
    typeInfo = {}
    def __init__(self):
        self.isAsync = "false"
        """id of the project"""
        """Required"""
        self.projectid = None
        self.typeInfo['projectid'] = 'uuid'
        """list accounts of the project by account name"""
        self.account = None
        self.typeInfo['account'] = 'string'
        """List by keyword"""
        self.keyword = None
        self.typeInfo['keyword'] = 'string'
        """"""
        self.page = None
        self.typeInfo['page'] = 'integer'
        """"""
        self.pagesize = None
        self.typeInfo['pagesize'] = 'integer'
        """list accounts of the project by role"""
        self.role = None
        self.typeInfo['role'] = 'string'
        self.required = ["projectid",]

class listProjectAccountsResponse (baseResponse):
    typeInfo = {}
    def __init__(self):
        """the id of the project"""
        self.id = None
        self.typeInfo['id'] = 'string'
        """the account name of the project's owner"""
        self.account = None
        self.typeInfo['account'] = 'string'
        """the total number of cpu cores available to be created for this project"""
        self.cpuavailable = None
        self.typeInfo['cpuavailable'] = 'string'
        """the total number of cpu cores the project can own"""
        self.cpulimit = None
        self.typeInfo['cpulimit'] = 'string'
        """the total number of cpu cores owned by project"""
        self.cputotal = None
        self.typeInfo['cputotal'] = 'long'
        """the displaytext of the project"""
        self.displaytext = None
        self.typeInfo['displaytext'] = 'string'
        """the domain name where the project belongs to"""
        self.domain = None
        self.typeInfo['domain'] = 'string'
        """the domain id the project belongs to"""
        self.domainid = None
        self.typeInfo['domainid'] = 'string'
        """the total number of public ip addresses available for this project to acquire"""
        self.ipavailable = None
        self.typeInfo['ipavailable'] = 'string'
        """the total number of public ip addresses this project can acquire"""
        self.iplimit = None
        self.typeInfo['iplimit'] = 'string'
        """the total number of public ip addresses allocated for this project"""
        self.iptotal = None
        self.typeInfo['iptotal'] = 'long'
        """the total memory (in MB) available to be created for this project"""
        self.memoryavailable = None
        self.typeInfo['memoryavailable'] = 'string'
        """the total memory (in MB) the project can own"""
        self.memorylimit = None
        self.typeInfo['memorylimit'] = 'string'
        """the total memory (in MB) owned by project"""
        self.memorytotal = None
        self.typeInfo['memorytotal'] = 'long'
        """the name of the project"""
        self.name = None
        self.typeInfo['name'] = 'string'
        """the total number of networks available to be created for this project"""
        self.networkavailable = None
        self.typeInfo['networkavailable'] = 'string'
        """the total number of networks the project can own"""
        self.networklimit = None
        self.typeInfo['networklimit'] = 'string'
        """the total number of networks owned by project"""
        self.networktotal = None
        self.typeInfo['networktotal'] = 'long'
        """the total primary storage space (in GiB) available to be used for this project"""
        self.primarystorageavailable = None
        self.typeInfo['primarystorageavailable'] = 'string'
        """the total primary storage space (in GiB) the project can own"""
        self.primarystoragelimit = None
        self.typeInfo['primarystoragelimit'] = 'string'
        """the total primary storage space (in GiB) owned by project"""
        self.primarystoragetotal = None
        self.typeInfo['primarystoragetotal'] = 'long'
        """the total secondary storage space (in GiB) available to be used for this project"""
        self.secondarystorageavailable = None
        self.typeInfo['secondarystorageavailable'] = 'string'
        """the total secondary storage space (in GiB) the project can own"""
        self.secondarystoragelimit = None
        self.typeInfo['secondarystoragelimit'] = 'string'
        """the total secondary storage space (in GiB) owned by project"""
        self.secondarystoragetotal = None
        self.typeInfo['secondarystoragetotal'] = 'long'
        """the total number of snapshots available for this project"""
        self.snapshotavailable = None
        self.typeInfo['snapshotavailable'] = 'string'
        """the total number of snapshots which can be stored by this project"""
        self.snapshotlimit = None
        self.typeInfo['snapshotlimit'] = 'string'
        """the total number of snapshots stored by this project"""
        self.snapshottotal = None
        self.typeInfo['snapshottotal'] = 'long'
        """the state of the project"""
        self.state = None
        self.typeInfo['state'] = 'string'
        """the total number of templates available to be created by this project"""
        self.templateavailable = None
        self.typeInfo['templateavailable'] = 'string'
        """the total number of templates which can be created by this project"""
        self.templatelimit = None
        self.typeInfo['templatelimit'] = 'string'
        """the total number of templates which have been created by this project"""
        self.templatetotal = None
        self.typeInfo['templatetotal'] = 'long'
        """the total number of virtual machines available for this project to acquire"""
        self.vmavailable = None
        self.typeInfo['vmavailable'] = 'string'
        """the total number of virtual machines that can be deployed by this project"""
        self.vmlimit = None
        self.typeInfo['vmlimit'] = 'string'
        """the total number of virtual machines running for this project"""
        self.vmrunning = None
        self.typeInfo['vmrunning'] = 'integer'
        """the total number of virtual machines stopped for this project"""
        self.vmstopped = None
        self.typeInfo['vmstopped'] = 'integer'
        """the total number of virtual machines deployed by this project"""
        self.vmtotal = None
        self.typeInfo['vmtotal'] = 'long'
        """the total volume available for this project"""
        self.volumeavailable = None
        self.typeInfo['volumeavailable'] = 'string'
        """the total volume which can be used by this project"""
        self.volumelimit = None
        self.typeInfo['volumelimit'] = 'string'
        """the total volume being used by this project"""
        self.volumetotal = None
        self.typeInfo['volumetotal'] = 'long'
        """the total number of vpcs available to be created for this project"""
        self.vpcavailable = None
        self.typeInfo['vpcavailable'] = 'string'
        """the total number of vpcs the project can own"""
        self.vpclimit = None
        self.typeInfo['vpclimit'] = 'string'
        """the total number of vpcs owned by project"""
        self.vpctotal = None
        self.typeInfo['vpctotal'] = 'long'
        """the list of resource tags associated with vm"""
        self.tags = []

class tags:
    def __init__(self):
        """"the account associated with the tag"""
        self.account = None
        """"customer associated with the tag"""
        self.customer = None
        """"the domain associated with the tag"""
        self.domain = None
        """"the ID of the domain associated with the tag"""
        self.domainid = None
        """"tag key name"""
        self.key = None
        """"the project name where tag belongs to"""
        self.project = None
        """"the project id the tag belongs to"""
        self.projectid = None
        """"id of the resource"""
        self.resourceid = None
        """"resource type"""
        self.resourcetype = None
        """"tag value"""
        self.value = None

