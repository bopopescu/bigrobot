import autobot.helpers as helpers
import autobot.restclient as restclient
import autobot.test as test
import keywords.Host as Host
import re
import os
import paramiko
import pexpect
import optparse

class T5_Scale(object):
    def __init__(self):
        pass



    def copy_config_from_server(self, file_path, server, server_passwd, dest_file='cfg_file_from_server.cfg'):
        t = test.Test()
        c = t.controller('master')
        c.config('')
        helpers.log("INFO: ****Getting config file from server")
        string = "copy scp://root@%s:%s %s" % (server, file_path, dest_file)
        helpers.log("copy string file is:%s" % string)
        c.send (string)
        opt = c.expect([r'[\r\n].+password:', r'[\r\n]Are you sure you want to continue connecting'])
        if opt == 1:
            helpers.log("key does not exist in the keychain")
            c.send('yes')
            c.expect(r'[\r\n].+password:')
            c.send(server_passwd)
        else:
            helpers.log("sending server password: %s" % (server_passwd))
            c.send(server_passwd)
        c.expect()
            
        helpers.log('copy file completed')

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
            helpers.log("INFO: File did not exist")
            return False
        


    def start_monitor_exception(self, file_name):
        t = test.Test()
        c1 = t.controller('c1')
        c2 = t.controller('c2')
        helpers.log("INFO: connecting to bash mode in both controllers")
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
            if size == 0:
                helpers.log("no exceptions found, you are good")
                return size
            if size > 0:
                #FIXME: Need to copy log file to external server
                helpers.log("Exceptions found in the file, !!!FILE A BUG!!! and dumping exceptions log to logfile")
                c.sudo('cat %s' % (file_name))
                return size
        else:
            helpers.log("File not Found")
            return False
            
            
            
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        