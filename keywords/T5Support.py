'''
Created on Sep 23, 2014

@author: mallinaarun
'''
import autobot.helpers as helpers
import autobot.test as test
from T5Utilities import T5Utilities as utilities
from T5Utilities import T5PlatformThreads
from BsnCommon import BsnCommon as bsnCommon
from time import sleep
import re
import os
import keywords.Mininet as mininet
import keywords.T5 as T5
import keywords.T5L3 as T5L3
import keywords.Host as Host
import keywords.Ixia as Ixia


class support(object):
    def __init__(self):
        pass

    def check_partitions_for_diagnostics(self, node_name='master'):
        t = test.Test()
        node = t.controller(node_name)
        mount_output = node.bash("mount | grep diagnostic")
        helpers.log(mount_output['content'])
        lines = mount_output['content'].split('\n')
        helpers.log(str(len(lines)))
        mount_points = 0
        for line in lines:
            # helpers.log("matching line: \n%s" % line)
            if re.match(r'.*\/var\/lib\/floodlight\/coredumps.*', line):
                helpers.log("Found /var/lib/floodlight/coredumps  Mount point")
                mount_points = mount_points + 1
            if re.match(r'.*\/var\/lib\/floodlight\/heapdumps.*', line):
                helpers.log("Found /var/lib/floodlight/heapdumps  Mount point")
                mount_points = mount_points + 1
            if re.match(r'.*\/var\/lib\/floodlight\/support.*', line):
                helpers.log("Found /var/lib/floodlight/support  Mount point")
                mount_points = mount_points + 1
        helpers.log("mount points: %s" % str(mount_points))
        if mount_points == 3:
            return True
        else:
            helpers.test_failure("Mount cmd from controller did not fine diagnostic mounts points")
            return False
    def check_support_file_location(self, node_name='master'):
        data = self.get_support_bundles(node_name)
        return_value = False
        if len(data) == 0:
            helpers.log("No Support Bundles Found on Controller %s" % node_name)
            return False
        else:
            for i in range(0, len(data)):
                helpers.log("Checking Fs-path for support file: %s " % data[i]['name'])
                helpers.log("fs-path: %s" % data[i]['fs-path'])
                if re.match(r'.*\/var\/lib\/floodlight\/support/.*', data[i]['fs-path']):
                    return_value = True
                else:
                    return_value = False
        return return_value
    def get_support_bundles(self, node_name='master'):
        t = test.Test()
        node = t.controller(node_name)
        url = '/api/v1/data/controller/support/bundle'
        node.get(url)
        data = node.rest.content()
        return data
    def get_support_bundle_fs_path(self, node_name='master'):
        '''
        Get the absolute path of the first available support bundle from controller
        '''
        t = test.Test()
        node = t.controller(node_name)
        data = self.get_support_bundles(node_name)
        if len(data) == 0:
            helpers.log("No Support Bundles Found on Controller %s" % node)
            return False
        else:
            for i in range(0, len(data)):
                helpers.log("fs-path: %s" % data[i]['fs-path'])
                return data[i]['fs-path']

    def get_support_bundle_name(self, node_name='master'):
        '''
        Get The Name of the Support Bundle that is first available on the controller
        '''
        t = test.Test()
        node = t.controller(node_name)
        data = self.get_support_bundles(node_name)
        if len(data) == 0:
            helpers.log("No Support Bundles Found on Controller %s" % node)
            return False
        else:
            for i in range(0, len(data)):
                helpers.log("Support Bundle Name: %s" % data[i]['name'])
                return data[i]['name']

    def delete_support_bundles(self, node_name="master"):
        t = test.Test()
        node = t.controller(node_name)
        data = self.get_support_bundles()
        helpers.prettify(data)
        if len(data) == 0:
            helpers.log("No Support Bundles on controller %s" % node_name)
            return True
        else:
            for i in range(0, len(data)):
                helpers.log("Deleting Support Bundle Name: %s" % data[i]['name'])
                delete_url = '/api/v1/data/controller/support/bundle[name="%s"]' % data[i]['name']
                node.rest.delete(delete_url, {})
                helpers.log("Success Deleting Support Bundle: %s" % data[i]['name'])
        helpers.log("Checking again to check all the support bundles are deleted..")
        data = self.get_support_bundles()
        helpers.prettify(data)
        if len(data) == 0:
            helpers.log("No Support Bundles on controller %s" % node_name)
            return True
        else:
            helpers.test_failure("Unable to Delete all Support bundles..")

    def get_node_mac_address(self, node_name="master"):
        '''
            Get the HW mac address of the give Node from ifconfig output
        '''
        t = test.Test()
        node = t.controller(node_name)
        mac_output = node.bash("ifconfig eth0 | grep HWaddr | awk '{print $5}'")
        helpers.log(mac_output['content'])
        mac_output_lines = mac_output['content'].split('\n')
        for line in mac_output_lines:
            match = re.match(r'.*(([0-9a-f]{2}[:-]){5}([0-9a-f]{2})).*', str(line))
            if match:
                return match.group(1)

    def check_controller_folders(self, support_bundle_folder=None, node='master'):
        ''''
            Check for Controller Folders
        if support_bundle_folder is None:
            helpers.log("Please pass the support bundle Folder")
        '''
        node_mac = self.get_node_mac_address(node)
        node_mac = re.sub(':', '', node_mac)
        support_bundle_folder = re.sub('\.tar\.gz', '', support_bundle_folder)
        for root, dirs, files in os.walk(support_bundle_folder):
            helpers.log("Dir Name: %s  File Name: %s" % (dirs, files))
            for directory in dirs:
                if re.match(r'.*%s.*' % node_mac, directory):
                    return True
        return False

    def check_switch_hardware_counters(self, support_bundle_folder=None, node_name='master'):
        '''
            Check for hardware counters are logded on support logs
        '''
        node_mac = self.get_node_mac_address(node_name)
        node_mac = re.sub(':', '', node_mac)
        result = True
        support_bundle_folder = re.sub('\.tar\.gz', '', support_bundle_folder)
        for root, dirs, files in os.walk(support_bundle_folder):
            helpers.log("Dir Name: %s  File Name: %s" % (dirs, files))
            for directory in dirs:
                if re.match(r'.*%s.*' % node_mac, directory):
                    if len(files) == 0:
                        helpers.test_failure("Please check for connected switches / Support Fail to Generate Switch support logs")
                    else:
                        for file_name in files:
                            if file_name == 'support.log':
                                helpers.log("Skipping checking for support.log")
                            else:
                                output = helpers.run_cmd2('cat %s/%s | grep "ofad-ctl brcm port-hw counters-all" | wc -l' % (support_bundle_folder, file_name), shell=True)
                                outputs = output[1]
                                helpers.log(str(outputs))
                                match = re.match(r'.*(\d+).*', str(outputs))
                                if match:
                                    if int(match.group(0)) == 32 or int(match.group(0)) == 54 or\
                                     int(match.group(0)) == 128 or int(match.group(0)) == 78:
                                        helpers.log("Expected switch hardware counters are logged in switch file : %s" % file_name)
                                    else:
                                        helpers.log("Expected switch hardware counters are not logged..")
                                    helpers.log(str(match.group(0)))
                        return result
        return False

    def check_switch_cmd(self, switch_cmd, support_bundle_folder=None, node_name='master'):
        '''
            Check whether the given switch cmd is logded on support logs
        '''
        node_mac = self.get_node_mac_address(node_name)
        node_mac = re.sub(':', '', node_mac)
        result = False
        support_bundle_folder = re.sub('\.tar\.gz', '', support_bundle_folder)
        for root, dirs, files in os.walk(support_bundle_folder):
            helpers.log("Dir Name: %s  File Name: %s" % (dirs, files))
            for directory in dirs:
                if re.match(r'.*%s.*' % node_mac, directory):
                    if len(files) == 0:
                        helpers.test_failure("Please check for connected switches / Support Fail to Generate Switch support logs")
                    else:
                        for file_name in files:
                            if file_name == 'support.log':
                                helpers.log("Skipping checking for support.log")
                            else:
                                output = helpers.run_cmd2('cat %s/%s | grep -i "%s" | wc -l' % (support_bundle_folder, file_name, switch_cmd), shell=True)
                                outputs = output[1]
                                helpers.log(str(outputs))
                                match = re.match(r'.*(\d+).*', str(outputs))
                                if match:
                                    helpers.log(str(match.group(0)))
                                    if int(match.group(0)) > 0:
                                        helpers.log("Found the given match string in switch log..!")
                                        result = True
        return result

    def check_controller_cli_cmds(self, support_bundle_folder=None, node_name='master'):
        '''
            check for controller cli cmds are logged
        '''
        node_mac = self.get_node_mac_address(node_name)
        node_mac = re.sub(':', '', node_mac)
        result = True
        support_bundle_folder = re.sub('\.tar\.gz', '', support_bundle_folder)
        for root, dirs, files in os.walk(support_bundle_folder):
            helpers.log("Dir Name: %s  File Name: %s" % (dirs, files))
            for directory in dirs:
                if re.match(r'.*%s.*' % node_mac, directory):
                    for root, dirs, files in os.walk(support_bundle_folder + '/' + directory + '/cli'):
                        for file_name in files:
                            helpers.log(str(file_name))
                            output = helpers.run_cmd2('cat %s' % (support_bundle_folder + '/' + directory + '/cli/' + file_name), shell=True)
                            outputs = output[1]
                            helpers.log(str(outputs))
                        return True


