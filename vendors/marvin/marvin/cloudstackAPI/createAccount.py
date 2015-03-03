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


"""Creates an account"""
from baseCmd import *
from baseResponse import *
class createAccountCmd (baseCmd):
    typeInfo = {}
    def __init__(self):
        self.isAsync = "false"
        """Type of the account.  Specify 0 for user, 1 for root admin, and 2 for domain admin"""
        """Required"""
        self.accounttype = None
        self.typeInfo['accounttype'] = 'short'
        """email"""
        """Required"""
        self.email = None
        self.typeInfo['email'] = 'string'
        """firstname"""
        """Required"""
        self.firstname = None
        self.typeInfo['firstname'] = 'string'
        """lastname"""
        """Required"""
        self.lastname = None
        self.typeInfo['lastname'] = 'string'
        """Clear text password (Default hashed to SHA256SALT). If you wish to use any other hashing algorithm, you would need to write a custom authentication adapter See Docs section."""
        """Required"""
        self.password = None
        self.typeInfo['password'] = 'string'
        """Unique username."""
        """Required"""
        self.username = None
        self.typeInfo['username'] = 'string'
        """Creates the user under the specified account. If no account is specified, the username will be used as the account name."""
        self.account = None
        self.typeInfo['account'] = 'string'
        """details for account used to store specific parameters"""
        self.accountdetails = []
        self.typeInfo['accountdetails'] = 'map'
        """Account UUID, required for adding account from external provisioning system"""
        self.accountid = None
        self.typeInfo['accountid'] = 'string'
        """Creates the user under the specified domain."""
        self.domainid = None
        self.typeInfo['domainid'] = 'uuid'
        """Network domain for the account's networks"""
        self.networkdomain = None
        self.typeInfo['networkdomain'] = 'string'
        """Specifies a timezone for this command. For more information on the timezone parameter, see Time Zone Format."""
        self.timezone = None
        self.typeInfo['timezone'] = 'string'
        """User UUID, required for adding account from external provisioning system"""
        self.userid = None
        self.typeInfo['userid'] = 'string'
        self.required = ["accounttype","email","firstname","lastname","password","username",]

class createAccountResponse (baseResponse):
    typeInfo = {}
    def __init__(self):
        """the id of the account"""
        self.id = None
        self.typeInfo['id'] = 'string'
        """details for the account"""
        self.accountdetails = None
        self.typeInfo['accountdetails'] = 'map'
        """account type (admin, domain-admin, user)"""
        self.accounttype = None
        self.typeInfo['accounttype'] = 'short'
        """the total number of cpu cores available to be created for this account"""
        self.cpuavailable = None
        self.typeInfo['cpuavailable'] = 'string'
        """the total number of cpu cores the account can own"""
        self.cpulimit = None
        self.typeInfo['cpulimit'] = 'string'
        """the total number of cpu cores owned by account"""
        self.cputotal = None
        self.typeInfo['cputotal'] = 'long'
        """the default zone of the account"""
        self.defaultzoneid = None
        self.typeInfo['defaultzoneid'] = 'string'
        """name of the Domain the account belongs too"""
        self.domain = None
        self.typeInfo['domain'] = 'string'
        """id of the Domain the account belongs too"""
        self.domainid = None
        self.typeInfo['domainid'] = 'string'
        """the list of acl groups that account belongs to"""
        self.groups = None
        self.typeInfo['groups'] = 'list'
        """the total number of public ip addresses available for this account to acquire"""
        self.ipavailable = None
        self.typeInfo['ipavailable'] = 'string'
        """the total number of public ip addresses this account can acquire"""
        self.iplimit = None
        self.typeInfo['iplimit'] = 'string'
        """the total number of public ip addresses allocated for this account"""
        self.iptotal = None
        self.typeInfo['iptotal'] = 'long'
        """true if the account requires cleanup"""
        self.iscleanuprequired = None
        self.typeInfo['iscleanuprequired'] = 'boolean'
        """true if account is default, false otherwise"""
        self.isdefault = None
        self.typeInfo['isdefault'] = 'boolean'
        """the total memory (in MB) available to be created for this account"""
        self.memoryavailable = None
        self.typeInfo['memoryavailable'] = 'string'
        """the total memory (in MB) the account can own"""
        self.memorylimit = None
        self.typeInfo['memorylimit'] = 'string'
        """the total memory (in MB) owned by account"""
        self.memorytotal = None
        self.typeInfo['memorytotal'] = 'long'
        """the name of the account"""
        self.name = None
        self.typeInfo['name'] = 'string'
        """the total number of networks available to be created for this account"""
        self.networkavailable = None
        self.typeInfo['networkavailable'] = 'string'
        """the network domain"""
        self.networkdomain = None
        self.typeInfo['networkdomain'] = 'string'
        """the total number of networks the account can own"""
        self.networklimit = None
        self.typeInfo['networklimit'] = 'string'
        """the total number of networks owned by account"""
        self.networktotal = None
        self.typeInfo['networktotal'] = 'long'
        """the total primary storage space (in GiB) available to be used for this account"""
        self.primarystorageavailable = None
        self.typeInfo['primarystorageavailable'] = 'string'
        """the total primary storage space (in GiB) the account can own"""
        self.primarystoragelimit = None
        self.typeInfo['primarystoragelimit'] = 'string'
        """the total primary storage space (in GiB) owned by account"""
        self.primarystoragetotal = None
        self.typeInfo['primarystoragetotal'] = 'long'
        """the total number of projects available for administration by this account"""
        self.projectavailable = None
        self.typeInfo['projectavailable'] = 'string'
        """the total number of projects the account can own"""
        self.projectlimit = None
        self.typeInfo['projectlimit'] = 'string'
        """the total number of projects being administrated by this account"""
        self.projecttotal = None
        self.typeInfo['projecttotal'] = 'long'
        """the total number of network traffic bytes received"""
        self.receivedbytes = None
        self.typeInfo['receivedbytes'] = 'long'
        """the total secondary storage space (in GiB) available to be used for this account"""
        self.secondarystorageavailable = None
        self.typeInfo['secondarystorageavailable'] = 'string'
        """the total secondary storage space (in GiB) the account can own"""
        self.secondarystoragelimit = None
        self.typeInfo['secondarystoragelimit'] = 'string'
        """the total secondary storage space (in GiB) owned by account"""
        self.secondarystoragetotal = None
        self.typeInfo['secondarystoragetotal'] = 'long'
        """the total number of network traffic bytes sent"""
        self.sentbytes = None
        self.typeInfo['sentbytes'] = 'long'
        """the total number of snapshots available for this account"""
        self.snapshotavailable = None
        self.typeInfo['snapshotavailable'] = 'string'
        """the total number of snapshots which can be stored by this account"""
        self.snapshotlimit = None
        self.typeInfo['snapshotlimit'] = 'string'
        """the total number of snapshots stored by this account"""
        self.snapshottotal = None
        self.typeInfo['snapshottotal'] = 'long'
        """the state of the account"""
        self.state = None
        self.typeInfo['state'] = 'string'
        """the total number of templates available to be created by this account"""
        self.templateavailable = None
        self.typeInfo['templateavailable'] = 'string'
        """the total number of templates which can be created by this account"""
        self.templatelimit = None
        self.typeInfo['templatelimit'] = 'string'
        """the total number of templates which have been created by this account"""
        self.templatetotal = None
        self.typeInfo['templatetotal'] = 'long'
        """the total number of virtual machines available for this account to acquire"""
        self.vmavailable = None
        self.typeInfo['vmavailable'] = 'string'
        """the total number of virtual machines that can be deployed by this account"""
        self.vmlimit = None
        self.typeInfo['vmlimit'] = 'string'
        """the total number of virtual machines running for this account"""
        self.vmrunning = None
        self.typeInfo['vmrunning'] = 'integer'
        """the total number of virtual machines stopped for this account"""
        self.vmstopped = None
        self.typeInfo['vmstopped'] = 'integer'
        """the total number of virtual machines deployed by this account"""
        self.vmtotal = None
        self.typeInfo['vmtotal'] = 'long'
        """the total volume available for this account"""
        self.volumeavailable = None
        self.typeInfo['volumeavailable'] = 'string'
        """the total volume which can be used by this account"""
        self.volumelimit = None
        self.typeInfo['volumelimit'] = 'string'
        """the total volume being used by this account"""
        self.volumetotal = None
        self.typeInfo['volumetotal'] = 'long'
        """the total number of vpcs available to be created for this account"""
        self.vpcavailable = None
        self.typeInfo['vpcavailable'] = 'string'
        """the total number of vpcs the account can own"""
        self.vpclimit = None
        self.typeInfo['vpclimit'] = 'string'
        """the total number of vpcs owned by account"""
        self.vpctotal = None
        self.typeInfo['vpctotal'] = 'long'
        """the list of users associated with account"""
        self.user = []

class user:
    def __init__(self):
        """"the user ID"""
        self.id = None
        """"the account name of the user"""
        self.account = None
        """"the account ID of the user"""
        self.accountid = None
        """"the account type of the user"""
        self.accounttype = None
        """"the api key of the user"""
        self.apikey = None
        """"the date and time the user account was created"""
        self.created = None
        """"the domain name of the user"""
        self.domain = None
        """"the domain ID of the user"""
        self.domainid = None
        """"the user email address"""
        self.email = None
        """"the user firstname"""
        self.firstname = None
        """"the boolean value representing if the updating target is in caller's child domain"""
        self.iscallerchilddomain = None
        """"true if user is default, false otherwise"""
        self.isdefault = None
        """"the user lastname"""
        self.lastname = None
        """"the secret key of the user"""
        self.secretkey = None
        """"the user state"""
        self.state = None
        """"the timezone user was created in"""
        self.timezone = None
        """"the user name"""
        self.username = None

