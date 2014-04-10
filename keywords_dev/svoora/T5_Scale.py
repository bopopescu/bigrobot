import autobot.helpers as helpers
import autobot.test as test
import re

#import autobot.helpers as helpers
#import autobot.restclient as restclient
#import autobot.test as test
#import keywords.Host as Host
#import re
#import os
#import paramiko
#import pexpect
#import optparse

class T5_Scale(object):
    def __init__(self):
        pass



    def copy_config_from_server(self, file_path, server, server_passwd, dest_file='cfg_file_from_server.cfg'):
        t = test.Test()
        c = t.controller('master')
        c.config('')
        #helpers.log("INFO: ****Getting config file from server")
        #string = "copy scp://root@%s:%s %s" % (server, file_path, dest_file)
        #helpers.log("copy string file is:%s" % string)
        #c.send(string)
        try:
            helpers.log("INFO: ****Getting config file from server")
            string = "copy scp://root@%s:%s %s" % (server, file_path, dest_file)
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

        
        
        #opt = c.expect([r'[\r\n].+password:', r'[\r\n].+(yes/no)?'])
        #helpers.log("received option %s" % opt)
        #if opt == 1:
        #    helpers.log("key does not exist in the keychain")
        #    c.send('yes')
        #    c.expect(r'[\r\n].+password:')
        #    c.send(server_passwd)
        #else:
        #    helpers.log("sending server password: %s" % (server_passwd))
        #    c.send(server_passwd)
        #c.expect()
        #cli_content = c.cli_content()
        #assert "100%" in cli_content
        #assert "Error" not in cli_content
        #helpers.log('copy file completed')

    def verify_file(self, file_name):
        t=test.Test()
        c=t.controller('master')
        helpers.log("checking the file exist or not")
        c.config('')
        string = "show file | grep %s" % (file_name)
        c.send(string)
        c.expect()
        #output = c.cli_result()
        output = c.cli_content()
        helpers.log ("received output is: %s" % (output))
        if re.findall(file_name, output):
                helpers.log("INFO:  File exist" )
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
        if re.findall(file_name,result['content']):
            helpers.log("File found under C1, deleting the file")
            c1.sudo('rm -rf c1_%s' % (file_name))
        result = c2.sudo("ls -ltr | grep %s" % (file_name))
        helpers.log(" monitor file under C2: %s" % (result['content']))
        if re.findall(file_name,result['content']):
            helpers.log("File found under C2, deleting the file")
            c2.sudo('rm -rf c2_%s' % (file_name))
        helpers.log("Enabling the tail and redirecting to filename")
        c1.sudo('tail -f /var/log/floodlight/floodlight.log | grep ERROR > c1_%s &' % (file_name))
        c2.sudo('tail -f /var/log/floodlight/floodlight.log | grep ERROR > c2_%s &' % (file_name))
        
    def pid_return_monitor_file(self, role):
        t = test.Test()
        c = t.controller(role)
        helpers.log("Verifing for monitor job")
        c_result = c.sudo('ps ax | grep tail | grep sudo')
        helpers.log("dumping sudo o/p:%s" % (c_result['content']))
        split = re.split('\s+',c_result['content'])
        #FIXME: Need to find another way to regex, to get pid rather splitting
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
        ##FIXME: Need to check if pid got killed or not
        helpers.log(" monitor file pid killed")
    
    def parse_exception(self, role, file_name):
        t = test.Test()
        c = t.controller(role)
        helpers.log("checking file exist in the controller")
        result = c.sudo("ls -ltr | grep %s" % (file_name))
        helpers.log(" monitor file: %s" % (result['content']))
        if re.findall(file_name,result['content']):
            helpers.log("File found, continuing parsing")
            split = re.split('\s+',result['content'])
            helpers.log ("dumping list of file %s" % (split))
            helpers.log("checking file size now")
            #FIXME: Need to check file size correctly
            size = split[10]
            helpers.log("Exception log file size:%s" % (size))
            if size == '0':
                helpers.log("no exceptions found, you are good")
                return size
            else:
                #FIXME: Need to copy log file to external server
                helpers.log("Exceptions found in the file, !!!FILE A BUG!!! and dumping exceptions log to logfile")
                if role == 'c1':
                    c.sudo('cat c1_%s' % (file_name))
                else:
                    c.sudo('cat c2_%s' % (file_name))
                return size
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
        if self.verify_file (file_name):
            c.config("config")
            c.send("copy %s running-config"  % file_name)
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
        url = '%s/api/v1/data/controller/applications/bvs/info/fabric/errors/dual-tor/peer-link-absent' % (c.base_url)
        c.rest.get(url)
        data = c.rest.content()
        return_flag = 0
        if len(data) != 0:
            helpers.test_failure("Fabric error reported for peer-links %s" % data)
            return_flag = 1
        else:
            helpers.log("No Fabric errors Reported for peer-links %s" % data)
            #return_flag = True
        url = '%s/api/v1/data/controller/applications/bvs/info/fabric/errors?select=uni-directional-links' % (c.base_url)
        c.rest.get(url)
        data = c.rest.content()
        if data[0] != {}:
            helpers.test_failure("Fabric error reported for uni-directional-links %s" % data)
            return_flag =  return_flag + 1
        else:
            helpers.log("No Fabric error Reported for uni-directional links %s" % data)
            #return_flag = True
        url = '%s/api/v1/data/controller/applications/bvs/info/fabric/errors/dual-tor/remote-leaf-groups-inconsistent' % (c.base_url)
        c.rest.get(url)
        data = c.rest.content()
        if len(data) != 0:
            helpers.test_failure("Fabric error reported for remote leaf groups %s" % data)
            return_flag =  return_flag + 1
        else:
            helpers.log("No Fabric error Reported for remote leaf groups %s" % data)
            #return_flag = True
        url = '%s/api/v1/data/controller/applications/bvs/info/fabric/errors/dual-tor/no-port-group-configured-interface' % (c.base_url)
        c.rest.get(url)
        data = c.rest.content()
        if len(data) != 0:
            helpers.test_failure("Fabric error reported for port-groups %s" % data)
            return_flag =  return_flag + 1
        else:
            helpers.log("No Fabric error Reported for prot-groups %s" % data)
            #return_flag = True
        return return_flag
    
        
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
        content=""
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
        c_slave = t.controller('slave') # Need to check if 'standby' exists
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
                for i in range (0, len(master_content)):
                    if (master_content[i]['name'] != slave_content[i]['name']):
                        helpers.log("Tenant config is not in sync")
                        return False
            else:
                helpers.log("TENANT:::Configuration is not present in Master or Salve")
            helpers.log("Tenant Configuration is in sync")
                    
        helpers.log("Verifying switch configurations")
        url_get_switches= '/api/v1/data/controller/core/switch-config?config=true'
        try:
            c_master.rest.get(url_get_switches)
            master_content = c_master.rest.content()
            c_slave.rest.get(url_get_switches)
            slave_content = c_slave.rest.content()
        except:
            pass
        else:
            if (master_content and slave_content):
                for i in range (0, len(master_content)):
                    if (master_content[i]['name'] != slave_content[i]['name'] and master_content[i]['dpid'] != slave_content[i]['dpid']):
                        helpers.log("Switches are not in Sync")
                        return False   # Need to Check content length as well
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
                for i in range (0, len(master_content)):
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
                for i in range (0, len(master_content)):
                    if (master_content[i]['ntp-server'] != slave_content[i]['ntp-server']):
                        helpers.log("NTP config is not in sync")
                        return False
            else:
                helpers.log("NTP:::Configuration is not present in Master or Salve")
                
            helpers.log("NTP Configuration is in Sync")
                
        helpers.log("Config is in sync between Active and Standby")
        return True

    
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        