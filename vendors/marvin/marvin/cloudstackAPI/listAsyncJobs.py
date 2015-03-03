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


"""Lists all pending asynchronous jobs for the account."""
from baseCmd import *
from baseResponse import *
class listAsyncJobsCmd (baseCmd):
    typeInfo = {}
    def __init__(self):
        self.isAsync = "false"
        """list resources by account. Must be used with the domainId parameter."""
        self.account = None
        self.typeInfo['account'] = 'string'
        """list only resources belonging to the domain specified"""
        self.domainid = None
        self.typeInfo['domainid'] = 'uuid'
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
        """the start date of the async job"""
        self.startdate = None
        self.typeInfo['startdate'] = 'tzdate'
        self.required = []

class listAsyncJobsResponse (baseResponse):
    typeInfo = {}
    def __init__(self):
        """the account that executed the async command"""
        self.accountid = None
        self.typeInfo['accountid'] = 'string'
        """the async command executed"""
        self.cmd = None
        self.typeInfo['cmd'] = 'string'
        """the created date of the job"""
        self.created = None
        self.typeInfo['created'] = 'date'
        """the unique ID of the instance/entity object related to the job"""
        self.jobinstanceid = None
        self.typeInfo['jobinstanceid'] = 'string'
        """the instance/entity object related to the job"""
        self.jobinstancetype = None
        self.typeInfo['jobinstancetype'] = 'string'
        """the progress information of the PENDING job"""
        self.jobprocstatus = None
        self.typeInfo['jobprocstatus'] = 'integer'
        """the result reason"""
        self.jobresult = None
        self.typeInfo['jobresult'] = 'responseobject'
        """the result code for the job"""
        self.jobresultcode = None
        self.typeInfo['jobresultcode'] = 'integer'
        """the result type"""
        self.jobresulttype = None
        self.typeInfo['jobresulttype'] = 'string'
        """the current job status-should be 0 for PENDING"""
        self.jobstatus = None
        self.typeInfo['jobstatus'] = 'integer'
        """the user that executed the async command"""
        self.userid = None
        self.typeInfo['userid'] = 'string'
        """the ID of the async job"""
        self.jobid = None
        self.typeInfo['jobid'] = ''

