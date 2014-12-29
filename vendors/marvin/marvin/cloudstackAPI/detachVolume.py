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


"""Detaches a disk volume from a virtual machine."""
from baseCmd import *
from baseResponse import *
class detachVolumeCmd (baseCmd):
    typeInfo = {}
    def __init__(self):
        self.isAsync = "true"
        """the device ID on the virtual machine where volume is detached from"""
        self.deviceid = None
        self.typeInfo['deviceid'] = 'long'
        """the ID of the disk volume"""
        self.id = None
        self.typeInfo['id'] = 'uuid'
        """the ID of the virtual machine where the volume is detached from"""
        self.virtualmachineid = None
        self.typeInfo['virtualmachineid'] = 'uuid'
        self.required = []

class detachVolumeResponse (baseResponse):
    typeInfo = {}
    def __init__(self):
        """ID of the disk volume"""
        self.id = None
        self.typeInfo['id'] = 'string'
        """the account associated with the disk volume"""
        self.account = None
        self.typeInfo['account'] = 'string'
        """the date the volume was attached to a VM instance"""
        self.attached = None
        self.typeInfo['attached'] = 'date'
        """the chain info of the volume"""
        self.chaininfo = None
        self.typeInfo['chaininfo'] = 'string'
        """the date the disk volume was created"""
        self.created = None
        self.typeInfo['created'] = 'date'
        """the boolean state of whether the volume is destroyed or not"""
        self.destroyed = None
        self.typeInfo['destroyed'] = 'boolean'
        """the ID of the device on user vm the volume is attahed to. This tag is not returned when the volume is detached."""
        self.deviceid = None
        self.typeInfo['deviceid'] = 'long'
        """bytes read rate of the disk volume"""
        self.diskBytesReadRate = None
        self.typeInfo['diskBytesReadRate'] = 'long'
        """bytes write rate of the disk volume"""
        self.diskBytesWriteRate = None
        self.typeInfo['diskBytesWriteRate'] = 'long'
        """io requests read rate of the disk volume"""
        self.diskIopsReadRate = None
        self.typeInfo['diskIopsReadRate'] = 'long'
        """io requests write rate of the disk volume"""
        self.diskIopsWriteRate = None
        self.typeInfo['diskIopsWriteRate'] = 'long'
        """the display text of the disk offering"""
        self.diskofferingdisplaytext = None
        self.typeInfo['diskofferingdisplaytext'] = 'string'
        """ID of the disk offering"""
        self.diskofferingid = None
        self.typeInfo['diskofferingid'] = 'string'
        """name of the disk offering"""
        self.diskofferingname = None
        self.typeInfo['diskofferingname'] = 'string'
        """an optional field whether to the display the volume to the end user or not."""
        self.displayvolume = None
        self.typeInfo['displayvolume'] = 'boolean'
        """the domain associated with the disk volume"""
        self.domain = None
        self.typeInfo['domain'] = 'string'
        """the ID of the domain associated with the disk volume"""
        self.domainid = None
        self.typeInfo['domainid'] = 'string'
        """Hypervisor the volume belongs to"""
        self.hypervisor = None
        self.typeInfo['hypervisor'] = 'string'
        """true if the volume is extractable, false otherwise"""
        self.isextractable = None
        self.typeInfo['isextractable'] = 'boolean'
        """an alternate display text of the ISO attached to the virtual machine"""
        self.isodisplaytext = None
        self.typeInfo['isodisplaytext'] = 'string'
        """the ID of the ISO attached to the virtual machine"""
        self.isoid = None
        self.typeInfo['isoid'] = 'string'
        """the name of the ISO attached to the virtual machine"""
        self.isoname = None
        self.typeInfo['isoname'] = 'string'
        """max iops of the disk volume"""
        self.maxiops = None
        self.typeInfo['maxiops'] = 'long'
        """min iops of the disk volume"""
        self.miniops = None
        self.typeInfo['miniops'] = 'long'
        """name of the disk volume"""
        self.name = None
        self.typeInfo['name'] = 'string'
        """the path of the volume"""
        self.path = None
        self.typeInfo['path'] = 'string'
        """the project name of the vpn"""
        self.project = None
        self.typeInfo['project'] = 'string'
        """the project id of the vpn"""
        self.projectid = None
        self.typeInfo['projectid'] = 'string'
        """provisioning type used to create volumes."""
        self.provisioningtype = None
        self.typeInfo['provisioningtype'] = 'string'
        """need quiesce vm or not when taking snapshot"""
        self.quiescevm = None
        self.typeInfo['quiescevm'] = 'boolean'
        """the display text of the service offering for root disk"""
        self.serviceofferingdisplaytext = None
        self.typeInfo['serviceofferingdisplaytext'] = 'string'
        """ID of the service offering for root disk"""
        self.serviceofferingid = None
        self.typeInfo['serviceofferingid'] = 'string'
        """name of the service offering for root disk"""
        self.serviceofferingname = None
        self.typeInfo['serviceofferingname'] = 'string'
        """size of the disk volume"""
        self.size = None
        self.typeInfo['size'] = 'long'
        """ID of the snapshot from which this volume was created"""
        self.snapshotid = None
        self.typeInfo['snapshotid'] = 'string'
        """the state of the disk volume"""
        self.state = None
        self.typeInfo['state'] = 'string'
        """the status of the volume"""
        self.status = None
        self.typeInfo['status'] = 'string'
        """name of the primary storage hosting the disk volume"""
        self.storage = None
        self.typeInfo['storage'] = 'string'
        """id of the primary storage hosting the disk volume; returned to admin user only"""
        self.storageid = None
        self.typeInfo['storageid'] = 'string'
        """shared or local storage"""
        self.storagetype = None
        self.typeInfo['storagetype'] = 'string'
        """an alternate display text of the template for the virtual machine"""
        self.templatedisplaytext = None
        self.typeInfo['templatedisplaytext'] = 'string'
        """the ID of the template for the virtual machine. A -1 is returned if the virtual machine was created from an ISO file."""
        self.templateid = None
        self.typeInfo['templateid'] = 'string'
        """the name of the template for the virtual machine"""
        self.templatename = None
        self.typeInfo['templatename'] = 'string'
        """type of the disk volume (ROOT or DATADISK)"""
        self.type = None
        self.typeInfo['type'] = 'string'
        """id of the virtual machine"""
        self.virtualmachineid = None
        self.typeInfo['virtualmachineid'] = 'string'
        """display name of the virtual machine"""
        self.vmdisplayname = None
        self.typeInfo['vmdisplayname'] = 'string'
        """name of the virtual machine"""
        self.vmname = None
        self.typeInfo['vmname'] = 'string'
        """state of the virtual machine"""
        self.vmstate = None
        self.typeInfo['vmstate'] = 'string'
        """ID of the availability zone"""
        self.zoneid = None
        self.typeInfo['zoneid'] = 'string'
        """name of the availability zone"""
        self.zonename = None
        self.typeInfo['zonename'] = 'string'
        """the list of resource tags associated with volume"""
        self.tags = []
        """the ID of the latest async job acting on this object"""
        self.jobid = None
        self.typeInfo['jobid'] = ''
        """the current status of the latest async job acting on this object"""
        self.jobstatus = None
        self.typeInfo['jobstatus'] = ''

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

