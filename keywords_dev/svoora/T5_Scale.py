import autobot.helpers as helpers
import autobot.test as test
# from datetime import datetime, time as datetime_time, timedelta
from datetime import datetime
import re

# import autobot.helpers as helpers
# import autobot.restclient as restclient
# import autobot.test as test
# import keywords.Host as Host
# import re
# import os
# import paramiko
# import pexpect
# import optparse

class T5_Scale(object):
    def __init__(self):
        pass



    def copy_config_from_server(self, file_path, server, server_passwd, dest_file='cfg_file_from_server.cfg'):
        t = test.Test()
        c = t.controller('master')
        c.config('')
        # helpers.log("INFO: ****Getting config file from server")
        # string = "copy scp://root@%s:%s %s" % (server, file_path, dest_file)
        # helpers.log("copy string file is:%s" % string)
        # c.send(string)
        try:
            helpers.log("INFO: ****Getting config file from server")
            dest_file_format = "file://" + dest_file
            string = "copy scp://root@%s:%s %s" % (server, file_path, dest_file_format)
            helpers.log("copy string file is:%s" % string)
            c.send (string)
            try:
                c.expect(r"Are you sure you want to continue connecting \(yes/no\)?")
                c.send("yes")
            except:
                helpers.test_log("Apparently already RSA key fingerprint stored")
            c.expect("password")
            c.send(server_passwd)
            c.expect()
            cli_content = c.cli_content()
            assert "100%" in cli_content
            assert "Error" not in cli_content
        except:
            helpers.test_log(c.cli_content())
            return False
        else:
            return False


    def copy_config_from_server_to_snapshot(self, file_path, server, server_passwd, dest_file='cfg_file_from_server.cfg'):
        t = test.Test()
        c = t.controller('master')
        c.config('')
        # helpers.log("INFO: ****Getting config file from server")
        # string = "copy scp://root@%s:%s %s" % (server, file_path, dest_file)
        # helpers.log("copy string file is:%s" % string)
        # c.send(string)
        try:
            helpers.log("INFO: ****Getting config file from server")
            dest_file_format = "snapshot://" + dest_file
            string = "copy scp://root@%s:%s %s" % (server, file_path, dest_file_format)
            helpers.log("copy string file is:%s" % string)
            c.send (string)
            try:
                c.expect(r"Are you sure you want to continue connecting \(yes/no\)?")
                c.send("yes")
            except:
                helpers.test_log("Apparently already RSA key fingerprint stored")
            c.expect("password")
            c.send(server_passwd)
            c.expect()
            cli_content = c.cli_content()
            assert "100%" in cli_content
            assert "Error" not in cli_content
        except:
            helpers.test_log(c.cli_content())
            return False
        else:
            return False

        # opt = c.expect([r'[\r\n].+password:', r'[\r\n].+(yes/no)?'])
        # helpers.log("received option %s" % opt)
        # if opt == 1:
        #    helpers.log("key does not exist in the keychain")
        #    c.send('yes')
        #    c.expect(r'[\r\n].+password:')
        #    c.send(server_passwd)
        # else:
        #    helpers.log("sending server password: %s" % (server_passwd))
        #    c.send(server_passwd)
        # c.expect()
        # cli_content = c.cli_content()
        # assert "100%" in cli_content
        # assert "Error" not in cli_content
        # helpers.log('copy file completed')

    def verify_file(self, file_name):
        t = test.Test()
        c = t.controller('master')
        helpers.log("checking the file exist or not")
        c.config('')
        string = "show file | grep %s" % (file_name)
        c.send(string)
        c.expect()
        # output = c.cli_result()
        output = c.cli_content()
        helpers.log ("received output is: %s" % (output))
        if re.findall(file_name, output):
                helpers.log("INFO:  File exist")
                return True
        else:
            helpers.Log("INFO: File did not exist")
            return False



    def start_monitor_exception(self, file_name):
        t = test.Test()
        c1 = t.controller('c1')
        c2 = t.controller('c2')
        helpers.log("INFO: connecting to bash mode in both controllers")
        helpers.log("INFO: Checking if file already exist in the controller")
        result = c1.sudo("ls -ltr | grep %s" % (file_name))
        helpers.log(" monitor file under C1: %s" % (result['content']))
        if re.findall(file_name, result['content']):
            helpers.log("File found under C1, deleting the file")
            c1.sudo('rm -rf c1_%s' % (file_name))
        result = c2.sudo("ls -ltr | grep %s" % (file_name))
        helpers.log(" monitor file under C2: %s" % (result['content']))
        if re.findall(file_name, result['content']):
            helpers.log("File found under C2, deleting the file")
            c2.sudo('rm -rf c2_%s' % (file_name))
        helpers.log("Enabling the tail and redirecting to filename")
        c1.sudo('tail -f /var/log/floodlight/floodlight.log | grep ERROR > c1_%s &' % (file_name))
        c2.sudo('tail -f /var/log/floodlight/floodlight.log | grep ERROR > c2_%s &' % (file_name))

    def start_monitor_switch_errors(self, file_name):
        t = test.Test()
        c1 = t.controller('c1')

        helpers.log("INFO: connecting to bash mode")
        helpers.log("INFO: Checking if file already exist in the controller")
        result = c1.sudo("ls -ltr | grep %s" % (file_name))
        helpers.log(" monitor file under C1: %s" % (result['content']))
        if re.findall(file_name, result['content']):
            helpers.log("File found under C1, deleting the file")
            c1.sudo('rm -rf c1_%s' % (file_name))
        helpers.log("Enabling the tail and redirecting to filename")
        c1.sudo('tail -f /var/log/switch/* | grep faultd | grep \"/bin/ofad\" > c1_%s &' % (file_name))

    def start_monitor_exception_during_failover(self, file_name):
        t = test.Test()
        c1 = t.controller('c1')
        c2 = t.controller('c2')
        helpers.log("INFO: connecting to bash mode in both controllers")
        helpers.log("INFO: Checking if file already exist in the controller")
        result = c1.sudo("ls -ltr | grep %s" % (file_name))
        helpers.log(" monitor file under C1: %s" % (result['content']))
        if re.findall(file_name, result['content']):
            helpers.log("File found under C1, deleting the file")
            c1.sudo('rm -rf c1_%s' % (file_name))
        result = c2.sudo("ls -ltr | grep %s" % (file_name))
        helpers.log(" monitor file under C2: %s" % (result['content']))
        if re.findall(file_name, result['content']):
            helpers.log("File found under C2, deleting the file")
            c2.sudo('rm -rf c2_%s' % (file_name))
        helpers.log("Enabling the tail and redirecting to filename")
        c1.sudo('tail -f /var/log/floodlight/floodlight.log | grep ERROR | grep -v DebugCounter > c1_%s &' % (file_name))
        c2.sudo('tail -f /var/log/floodlight/floodlight.log | grep ERROR | grep -v DebugCounter > c2_%s &' % (file_name))

    def start_monitor_exception_during_reboot(self, file_name):
        t = test.Test()
        c1 = t.controller('c1')
        c2 = t.controller('c2')
        helpers.log("INFO: connecting to bash mode in both controllers")
        helpers.log("INFO: Checking if file already exist in the controller")
        result = c1.sudo("ls -ltr | grep %s" % (file_name))
        helpers.log(" monitor file under C1: %s" % (result['content']))
        if re.findall(file_name, result['content']):
            helpers.log("File found under C1, deleting the file")
            c1.sudo('rm -rf c1_%s' % (file_name))
        result = c2.sudo("ls -ltr | grep %s" % (file_name))
        helpers.log(" monitor file under C2: %s" % (result['content']))
        if re.findall(file_name, result['content']):
            helpers.log("File found under C2, deleting the file")
            c2.sudo('rm -rf c2_%s' % (file_name))
        helpers.log("Enabling the tail and redirecting to filename")
        c1.sudo('tail -f /var/log/floodlight/floodlight.log | grep ERROR | grep -v ABSRPCCH7002 > c1_%s &' % (file_name))
        c2.sudo('tail -f /var/log/floodlight/floodlight.log | grep ERROR | grep -v ABSRPCCH7002 > c2_%s &' % (file_name))

    def pid_return_monitor_file(self, role):
        t = test.Test()
        c = t.controller(role)
        helpers.log("Verifing for monitor job")
        c_result = c.sudo('ps ax | grep tail | grep sudo')
        helpers.log("dumping sudo o/p:%s" % (c_result['content']))
        split = re.split('\s+', c_result['content'])
        # FIXME: Need to find another way to regex, to get pid rather splitting
        if split[9]:
            pid = split[9]
            return pid
        else:
            return 0

    def pid_return_switch_monitor_file(self):
        t = test.Test()
        c = t.controller('c1')
        helpers.log("Verifing for monitor job")
        c_result = c.sudo('ps ax | grep tail | grep sudo')
        helpers.log("dumping sudo o/p:%s" % (c_result['content']))
        split = re.split('\s+', c_result['content'])
        # FIXME: Need to find another way to regex, to get pid rather splitting
        if split[9]:
            pid = split[9]
            return pid
        else:
            return 0




    def stop_monitor_exception(self, pid, role):
        t = test.Test()
        c = t.controller(role)
        helpers.log("killing monitor job pid:%s" % (pid))
        c.sudo('kill %s' % (pid))
        # #FIXME: Need to check if pid got killed or not
        helpers.log(" monitor file pid killed")


    def stop_monitor_switch_error(self, pid):
        t = test.Test()
        c = t.controller('c1')
        helpers.log("killing monitor job pid:%s" % (pid))
        c.sudo('kill %s' % (pid))
        # #FIXME: Need to check if pid got killed or not
        helpers.log(" monitor file pid killed")

    def time_diff(self, start, end):
        start_date = datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
        end_date = datetime.strptime(end, "%Y-%m-%d %H:%M:%S")
        print start_date
        print end_date
        # if isinstance(start_date, datetime_time):
         #   helpers.log("in if converting times")  # convert to datetime
          #  assert isinstance(end_date, datetime_time)
           # start, end = [datetime.combine(datetime.min, t) for t in [start, end]]
        helpers.log("times are %s and %s" % (start, end))
        return end_date - start_date
        # if start_date <= end_date:
         #   diff = end_date - start_date
          #  helpers.log(diff)  # e.g., 10:33:26-11:15:49
           # return diff
        # else:  # end < start e.g., 23:55:00-00:25:00
         #   end_date += timedelta(1)  # +day
          #  assert end_date > start_date
           # return end_date - start_date

    def parse_exception(self, role, file_name):
        t = test.Test()
        c = t.controller(role)
        helpers.log("checking file exist in the controller")
        result = c.sudo("ls -ltr | grep %s" % (file_name))
        helpers.log(" monitor file: %s" % (result['content']))
        if re.findall(file_name, result['content']):
            helpers.log("File found, continuing parsing")
            split = re.split('\s+', result['content'])
            helpers.log ("dumping list of file %s" % (split))
            helpers.log("checking file size now")
            # FIXME: Need to check file size correctly
            size = split[10]
            helpers.log("Exception log file size:%s" % (size))
            if size == '0':
                helpers.log("no exceptions found, you are good")
                return size
            else:
                # FIXME: Need to copy log file to external server
                helpers.log("Exceptions found in the file, !!!FILE A BUG!!! and dumping exceptions log to logfile")
                if role == 'c1':
                    c.sudo('cat c1_%s' % (file_name))
                else:
                    c.sudo('cat c2_%s' % (file_name))
                return size
        else:
            helpers.log("File not Found")
            return False

    def parse_switch_error(self, file_name):
        t = test.Test()
        c = t.controller('c1')
        helpers.log("checking file exist in the controller")
        result = c.sudo("ls -ltr | grep %s" % (file_name))
        helpers.log(" monitor file: %s" % (result['content']))
        if re.findall(file_name, result['content']):
            helpers.log("File found, continuing parsing")
            split = re.split('\s+', result['content'])
            helpers.log ("dumping list of file %s" % (split))
            helpers.log("checking file size now")
            # FIXME: Need to check file size correctly
            size = split[10]
            helpers.log("Exception log file size:%s" % (size))
            if size == '0':
                helpers.log("no exceptions found, you are good")
                return size
            else:
                # FIXME: Need to copy log file to external server
                helpers.log("Exceptions found in the file, !!!FILE A BUG!!! and dumping exceptions log to logfile")
                c.sudo('cat c1_%s' % (file_name))
        else:
            helpers.log("File not Found")
            return False



    def cli_copy_file_to_running_config(self, file_name):
        ''' Function to copy <file> to running-config
        via CLI
        Input: <file>
        Output: True if successful, False otherwise
        '''
        helpers.test_log("Running command:\ncopy <file> running-config ")
        t = test.Test()
        c = t.controller('master')
        file_name = "snapshot://" + file_name
        if self.verify_file (file_name):
            c.config("config")
            c.send("copy %s running-config" % file_name)
            try:
                c.expect(timeout=180)
            except:
                helpers.test_log(c.cli_content())
                helpers.log('copying to running config took more than 3 mins')
                return False
            else:
                helpers.log('copying to running completed successfully')
                return True
        else:
            helpers.log("INFO: FILE not found")
            return False

    def rest_verify_fabric_errors(self):
        helpers.log("Checking fabric errors")
        t = test.Test()
        c = t.controller()
        url = '%s/api/v1/data/controller/applications/bcf/info/errors/fabric/switch-not-connected-to-standby' % (c.base_url)
        c.rest.get(url)
        data = c.rest.content()
        return_flag = 0
        if len(data) != 0:
            helpers.test_failure("Fabric error reported for switches not connected to standby %s" % data)
            return_flag = 1
        else:
            helpers.log("No Fabric errors Reported for switches not connected to standby %s" % data)
            # return_flag = True
        url = '%s/api/v1/data/controller/applications/bcf/info/errors/fabric/pending-disconnect-switch' % (c.base_url)
        c.rest.get(url)
        data = c.rest.content()
        if len(data) != 0:
            helpers.test_failure("Fabric error reported for disconnect switches %s" % data)
            return_flag = return_flag + 1
        else:
            helpers.log("No Fabric error Reported for disconnect switches %s" % data)
            # return_flag = True
        url = '%s/api/v1/data/controller/applications/bcf/info/errors/fabric/suspended-switch' % (c.base_url)
        c.rest.get(url)
        data = c.rest.content()
        if len(data) != 0:
            helpers.test_failure("Fabric error reported for suspended switches %s" % data)
            return_flag = return_flag + 1
        else:
            helpers.log("No Fabric error Reported for suspended switches %s" % data)
            # return_flag = True
        url = '%s/api/v1/data/controller/applications/bcf/info/errors/fabric/error-threshold-member-count-exceeded-lag' % (c.base_url)
        c.rest.get(url)
        data = c.rest.content()
        if len(data) != 0:
            helpers.test_failure("Fabric error reported for error threashold member count %s" % data)
            return_flag = return_flag + 1
        else:
            helpers.log("No Fabric error Reported for error threashold member count %s" % data)
            # return_flag = True
        url = '%s/api/v1/data/controller/applications/bcf/info/errors/fabric/invalid-link' % (c.base_url)
        c.rest.get(url)
        data = c.rest.content()
        if len(data) != 0:
            helpers.test_failure("Fabric error reported for invalid links %s" % data)
            return_flag = return_flag + 1
        else:
            helpers.log("No Fabric error Reported for invalid links %s" % data)

        url = '%s/api/v1/data/controller/applications/bcf/info/errors/fabric/missing-link' % (c.base_url)
        c.rest.get(url)
        data = c.rest.content()
        if len(data) != 0:
            helpers.test_failure("Fabric error reported for missing links %s" % data)
            return_flag = return_flag + 1
        else:
            helpers.log("No Fabric error Reported for missing links %s" % data)

        url = '%s/api/v1/data/controller/applications/bcf/info/errors/fabric/breakout-failed-interface' % (c.base_url)
        c.rest.get(url)
        data = c.rest.content()
        if len(data) != 0:
            helpers.test_failure("Fabric error reported for break-out links %s" % data)
            return_flag = return_flag + 1
        else:
            helpers.log("No Fabric error Reported for break-out links %s" % data)


        return return_flag


    def rest_verify_debug_coordinator(self):
        ''' Function to verify config sync between controllers by checking config checksum between controllers
        Input:
        Output: True/False
        '''
        t = test.Test()
        c_master = t.controller('master')
        url = '/api/v1/data/controller/core/state-sync-coordinator'
        c_master.rest.get(url)
        data_master = c_master.rest.content()
        master_digest = data_master[0]["current-config-state"]["digest"]

        c_slave = t.controller('slave')
        url = '/api/v1/data/controller/core/state-sync-coordinator'
        c_slave.rest.get(url)
        data_slave = c_slave.rest.content()
        slave_digest = data_slave[0]["current-config-state"]["digest"]


        helpers.log("Printing digest from master and standby controllers %s and %s" % (master_digest, slave_digest))
        if (master_digest == slave_digest):
            helpers.log("Config is in sync between controlelrs and digest match")
            return True
        else:
            helpers.log("config digest do not match between controllers")
            return False
    def rest_shutdown_interface(self, switch, interface):
        ''' Function to shutdown given switch interface
        Input: switch and interface
        Output: True/False
        '''

        t = test.Test()
        c = t.controller('master')
        # /api/v1/data/controller/core/switch-config[name="leaf0a"]/interface[name="ethernet24"] {"shutdown": true}
        url = '/api/v1/data/controller/core/switch-config[name="%s"]/interface[name="%s"]' % (switch, interface)
        try:
            c.rest.post(url, {"shutdown": True})
        except:
            # helpers.test_failure(c.rest.error())
            return False
        else:
            # helpers.test_log("Output: %s" % c.rest.result_json())
            # return c.rest.content()
            return True

    def rest_noshutdown_interface(self, switch, interface):
        ''' Function to no shutdown given switch interface
        Input: switch and interface
        Output: True/False
        '''

        t = test.Test()
        c = t.controller('master')
        # /api/v1/data/controller/core/switch-config[name="leaf0a"]/interface[name="ethernet24"]/shutdown {}
        url = '/api/v1/data/controller/core/switch-config[name="%s"]/interface[name="%s"]/shutdown' % (switch, interface)
        try:
            c.rest.delete(url, {})
        except:
            # helpers.test_failure(c.rest.error())
            return False
        else:
            # helpers.test_log("Output: %s" % c.rest.result_json())
            # return c.rest.content()
            return True

    def rest_verify_disk_usage(self):
        ''' Function to verify disk usage assert if it reaches 100%
        Input:
        Output: True/False
        '''
        t = test.Test()
        c_master = t.controller('master')
        c_slave = t.controller('slave')
        helpers.log("INFO: connecting to bash mode in both controllers")
        helpers.log("INFO: Checking the df -h in both controllers")

        master_df = c_master.sudo('df -h | awk \'{print $5}\'')
        split = re.split('\n', master_df['content'])
        master_df_list = split[1:-1]
        slave_df = c_slave.sudo('df -h | awk \'{print $5}\'')
        split = re.split('\n', slave_df['content'])
        slave_df_list = split[1:-1]

        for df in master_df_list:
            helpers.log(" df value in master: %s" % (df))
            if df == "100%":
                helpers.log("Partition exhausted in Master Controller")
                return False
        for df in slave_df_list:
            helpers.log(" df value in slave: %s" % (df))
            if df == "100%":
                helpers.log("Partition exhausted in Slave Controller")
                return False
        return True

    def rest_verify_sync_state(self):
        ''' Function to verify forwarding sync state for all the switches
        Input:
        Output: True/False
        '''
        t = test.Test()
        c_master = t.controller('master')
        url = '/api/v1/data/controller/applications/bcf/info/forwarding/network/global/sync-state-table'
        c_master.rest.get(url)
        data_master = c_master.rest.content()
        helpers.log("Data returned for total number of switches %d" % (len(data_master)))
        if (len(data_master) == 0):
            helpers.log("Sync state information is not available")
            return False
        else:
            for i in range(0, len(data_master)):
                helpers.log("Printing sync-state info for switch dp-id:%s and status:%s" % (str(data_master[i]["switch-id"]), str(data_master[i]["sync-state"])))
                if (str(data_master[i]["sync-state"]) != "success"):
                    return False
        return True

    def rest_get_active_end_point_count(self):
        ''' Function to get active end point count
        Input:
        Output: return end point count
        '''
        t = test.Test()
        c_master = t.controller('master')
        url = '/api/v1/data/controller/applications/bcf/info/summary/fabric'
        c_master.rest.get(url)
        data_master = c_master.rest.content()
        ep_count = data_master[0]["active-endpoint-count"]
        helpers.log("Total number of end points are %s" % (ep_count))
        return ep_count


    def get_L3_table_count(self, node):
        t = test.Test()
        s = t.switch(node)
        string = 'debug ofad "brcmdriver3 flow-stats"'
        content = s.enable(string)['content']
        temp = helpers.strip_cli_output(content, to_list=True)
        helpers.log("***temp is: %s  \n" % temp)

        for line in temp:
            helpers.log("***line is: %s  \n" % line)
            line = line.lstrip()
            match = re.match(r'L3_HOST_ROUTE\s+(\d+)\s+(\d+).*', line)
            if match:
                helpers.log("INFO: Total L3 table size is %s,  and current allocation is: %s" % (match.group(1), match.group(2)))
                return match.group(2)
        return 0

    def get_L2_table_count(self, node):
        t = test.Test()
        s = t.switch(node)
        string = 'debug ofad "brcmdriver3 flow-stats"'
        content = s.enable(string)['content']
        temp = helpers.strip_cli_output(content, to_list=True)
        helpers.log("***temp is: %s  \n" % temp)

        for line in temp:
            helpers.log("***line is: %s  \n" % line)
            line = line.lstrip()
            match = re.match(r'L2 (\d+)\s+(\d+).*', line)
            if match:
                helpers.log("INFO: Total L2 table size is %s,  and current allocation is: %s" % (match.group(1), match.group(2)))
                return match.group(2)
        return 0

    def get_ACL_table_count(self, node):
        t = test.Test()
        s = t.switch(node)
        string = 'debug ofad "brcmdriver3 flow-stats"'
        content = s.enable(string)['content']
        temp = helpers.strip_cli_output(content, to_list=True)
        helpers.log("***temp is: %s  \n" % temp)

        for line in temp:
            helpers.log("***line is: %s  \n" % line)
            line = line.lstrip()
            match = re.match(r'INGRESS_ACL\s+(\d+)\s+(\d+).*', line)
            if match:
                helpers.log("INFO: Total INGRESS_ACL table size is %s,  and current allocation is: %s" % (match.group(1), match.group(2)))
                return match.group(2)

        return 0





    def Dump_Show_Commands(self):
        t = test.Test()
        c = t.controller('master')
        cmdList = [
           'show running-config',
           'show debug counters',
           'show cluster details',
           'show switch',
           'show fabric switch',
           'show fabric interface',
           'show fabric lacp',
           'show fabric lag',
           'show fabric link',
           'show fabric error',
           'show tenant',
           'show vns',
           'show endpoints',
           'show forwarding',
           ]
        content = ""
        for cmd in cmdList:
            c.cli(cmd)
            content = content + c.cli_content()
        return content


    def compare_configuration(self):
        '''
        Compare Configuration syncs between master and standby
        '''
        t = test.Test()
        c_master = t.controller('master')
        c_slave = t.controller('slave')
        helpers.log("Verifying all tenants")
        url_get_tenant = '/api/v1/data/controller/applications/bvs/tenant?config=true'
        try:
            c_master.rest.get(url_get_tenant)
            master_content = c_master.rest.content()
            c_slave.rest.get(url_get_tenant)
            slave_content = c_slave.rest.content()

        except:
            pass
        else:
            if (master_content and slave_content):
                for i in range (0, len(master_content) - 1):
                    if (master_content[i]['name'] != slave_content[i]['name']):
                        helpers.log("Tenant config is not in sync")
                        return False
                    if (master_content[i]['virtual-router']['active']):
                         helpers.log("Route config present in master")

                         for j in range (0, len(master_content[i]['virtual-router']['routes']) - 1):

                             if (master_content[i]['virtual-router']['routes'][j]['next-hop']['tenant-name'] != slave_content[i]['virtual-router']['routes'][j]['next-hop']['tenant-name']
                                and master_content[i]['virtual-router']['routes'][j]['dest-ip-subnet'] != slave_content[i]['virtual-router']['routes'][j]['dest-ip-subnet']):
                                helpers.log("Routes did not match")
                                return False
                         for j in range (0, len(master_content[i]['virtual-router']['vns-interfaces']) - 1):

                             if (master_content[i]['virtual-router']['vns-interfaces'][j]['ip-cidr'] != slave_content[i]['virtual-router']['vns-interfaces'][j]['ip-cidr']
                                 and master_content[i]['virtual-router']['vns-interfaces'][j]['vns-name'] != slave_content[i]['virtual-router']['vns-interfaces'][j]['vns-name']):
                                 helpers.log("VNS interfaces did not match")
                                 return False
                    for j in range (0, len(master_content[i]['vns']) - 1):

                        if (master_content[i]['vns'][j]['name'] != slave_content[i]['vns'][j]['name']):
                            helpers.log("VNS names do not match")
                            return False
                        for k in range (0, len(master_content[i]['vns'][j]['port-group-membership-rule']) - 1):
                            helpers.log(" Now in nested first k loop: %d" % k)
                            if (master_content[i]['vns'][j]['port-group-membership-rule'][k]['port-group'] != slave_content[i]['vns'][j]['port-group-membership-rule'][k]['port-group']):
                                helpers.log("Port-Group Membership rule do not match")
                                return False

            else:
                helpers.log("TENANT:::Configuration is not present in Master or Salve")
            helpers.log("Tenant Configuration is in sync")

        helpers.log("Verifying switch configurations")
        url_get_switches = '/api/v1/data/controller/core/switch-config?config=true'
        try:
            c_master.rest.get(url_get_switches)
            master_content = c_master.rest.content()
            c_slave.rest.get(url_get_switches)
            slave_content = c_slave.rest.content()
        except:
            pass
        else:
            if (master_content and slave_content):
                for i in range (0, len(master_content) - 1):
                    if (master_content[i]['name'] != slave_content[i]['name'] and master_content[i]['dpid'] != slave_content[i]['dpid']):
                        helpers.log("Switches are not in Sync")
                        return False  # Need to Check content length as well
            else:
                helpers.log("SWITCH:::Configuration is not present in Master or Salve")

            helpers.log("Switch Configuration is in Sync")

        helpers.log("Verifying all port-groups")
        url_get_portgrp = '/api/v1/data/controller/applications/bvs/port-group?config=true'
        try:
            c_master.rest.get(url_get_portgrp)
            master_content = c_master.rest.content()
            c_slave.rest.get(url_get_portgrp)
            slave_content = c_slave.rest.content()
        except:
            pass
        else:
            if (master_content and slave_content):
                for i in range (0, len(master_content) - 1):
                    if (master_content[i]['name'] != slave_content[i]['name']):
                        helpers.log("Port-Group config is not in Sync")
                        return False
            else:
                helpers.log("PORT-GROUP:::Configuration is not present in Master or Salve")

            helpers.log("Port-Group Configuration is in Sync")

        helpers.log("Verifying NTP configurations")
        url_get_ntpservers = '/api/v1/data/controller/os/config/global/time-config?config=true'
        try:
            c._master.rest.get(url_get_ntpservers)
            master_content = c_master.rest.content()
            c._slave.rest.get(url_get_ntpservers)
            slave_content = c_slave.rest.content()

        except:
            pass
        else:
            if (master_content and slave_content):
                for i in range (0, len(master_content) - 1):
                    if (master_content[i]['ntp-server'] != slave_content[i]['ntp-server']):
                        helpers.log("NTP config is not in sync")
                        return False
            else:
                helpers.log("NTP:::Configuration is not present in Master or Salve")

        helpers.log("NTP Configuration is in Sync")

        helpers.log("Verifing snmp configuration")
        url_get_snmp_location = '/api/v1/data/controller/os/config/global/snmp-config?config=true'
        try:
            c._master.rest.get(url_get_snmp_location)
            master_content = c_master.rest.content()
            c._slave.rest.get(url_get_snmp_location)
            slave_content = c_slave.rest.content()

        except:
            pass
        else:
            if (master_content and slave_content):
                for i in range (0, len(master_content) - 1):
                    if (master_content[i]['contact'] != slave_content[i]['contact']
                        and master_content[i]['location'] != slave_content[i]['location']
                        and master_content[i]['community'] != slave_content[i]['community']):
                        helpers.log("SNMP config is not in sync")
                        return False
                    for j in range (0, len(master_content[i]['trap-host']) - 1):
                        if (master_content[i]['trap-host'][j]['ipaddr'] != slave_content[i]['trap-host'][j]['ipaddr']
                            and master_content[i]['trap-host'][j]['udp-port'] != slave_content[i]['trap-host'][j]['udp-port']):
                            helpers.log("SNMP::Trap config is not in sync")
                            return False
            else:
                helpers.log("SNMP:::Configuration is not present in Master or Salve")

        helpers.log("SNMP Configuration is in Sync")

        helpers.log("Config is in sync between Active and Standby")
        return True




















