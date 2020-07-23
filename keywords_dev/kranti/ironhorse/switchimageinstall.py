import autobot.helpers as helpers
import autobot.test as test
import telnetlib
from multiprocessing import Process
import os 
import paramiko

class switchimageinstall(object):

    def __init__(self):
        pass

    def switchLight_image_install(self, node, newSwitchFlag="true", switchIp=None, netMask=None, gatewayIp=None ):
        t = test.Test()
        switch = t.switch(node)
        user = "root"
        password = "bsn"
        console_ip = t.params(node, "console_ip")
        console_port = t.params(node, "console_port")
        
        if not switchIp:
            helpers.test_error("You must specify switchIp")
        if not netMask:
            helpers.test_error("You must specify netMask")
        if not gatewayIp:
            helpers.test_error("You must specify gatewayIp")

        swLightUrl = "setenv sl_url 'http://10.192.74.102/export/switchlight/autobuilds/master/latest.switchlight-powerpc-release.all.installer'"
        swLightenv =  "setenv sl_ip ${ipaddr}::${gatewayip}:${netmask}::eth0:off"
        swLightonie = "setenv onie_debugargs install_url=${sl_url} ip=${sl_ip}"
        swLightImagePath = "wget http://10.192.74.102/export/switchlight/autobuilds/master/latest.switchlight-powerpc-internal-t5.swi"
        swLightFlash =    "echo \"SWI=flash2:latest.switchlight-powerpc-internal-t5.swi\"  >/mnt/flash/boot-config"
        helpers.log("IN HERE 1")
        #tn= telnetlib.Telnet(console_ip,console_port)
#       is false (${newSwitchflag}, msg="This is not a new Switch"):
        tn= telnetlib.Telnet(console_ip,console_port)
        helpers.log("IN HERE newSwitchFalse")
        tn.read_until("login:", 3)
        tn.write(user + "\r\n")
        helpers.log("IN HERE newSwitchFalse")        
        tn.read_until("password:", 3)
        tn.write(password + "\r\n")
        tn.read_until("#", 3)
            
#       is true (${newSwitchflag}, msg="This is new Switch"):
#       tn= telnetlib.Telnet(console_ip,console_port)
#       helpers.log("IN HERE newSwitchTrue")
#       tn.read_until("#", 3)
            
        helpers.log("Reboot the switch and wait 30 ")    
        tn.write("reboot" + "\r\n")
        #sleep 30
        tn.read_until("Hit any key to stop autoboot:", 30)
        tn.write("\r\n")
        tn.read_until("=>", 3)   
        helpers.log("afterautoboot") 
        tn.read_until("=>", 5)
        tn.write("setenv ipaddr switchIp" + "\r\n")
        tn.read_until("=>", 5)
        tn.write("setenv netmask netMask" + "\r\n")
        tn.read_until("=>", 5)
        tn.write("setenv gatewayip gatewayIp" + "\r\n")
        tn.read_until("=>", 5)
        tn.write("setenv serverip 10.192.74.102" + "\r\n")
        tn.read_until("=>", 5)
        tn.write("saveenv" + "\r\n")
        tn.read_until("=>", 5)
        tn.write(swLightUrl + "\r\n")
        tn.read_until("=>", 5)
        tn.write(swLightenv + "\r\n")
        tn.read_until("=>", 5)
        tn.write(swLightonie + "\r\n")
        tn.read_until("=>", 5)
        tn.write("run onie_bootcmd"  + "\r\n")
        tn.read_until("=>", 5)
        tn.write("boot"  + "\r\n")
        #sleep 10
        tn.read_until("Press Control-C now to enter loader shell", 30)
        tn.write("\x03"  + "\r\n")
        helpers.log("IN HERE loadershell") 
        tn.read_until("loader#", 10)
        tn.write("#inloadershell" + "\r\n")
        tn.read_until("loader#", 3)
        tn.write("netconf" + "\r\n")
        tn.read_until("Which interface (blank for ma1)?", 3)
        tn.write("ma1" + "\r\n")
        tn.read_until("IP address (/prefix optional for v4)?", 3)
        tn.write("switchIp/18" + "\r\n")
        tn.read_until("Default gateway IP address (blank for none)?", 3)
        tn.write("gatewayIp" + "\r\n")
        tn.read_until("DNS IP address (blank for none)?", 3)
        tn.write("10.192.3.1" + "\r\n")
        tn.read_until("DNS default domain (blank for none)?", 3)
        tn.write("bigswitch.com" + "\r\n")
        helpers.log("#DoneLoader#")
        tn.read_until("#", 10)
        tn.write("cd /mnt/flash2" + "\r\n")
        tn.read_until("#", 10)
        tn.write(swLightImagePath + "\r\n")        
        tn.read_until("#", 10)     
        tn.write(swLightFlash + "\r\n")        
        tn.read_until("#", 10)   
        tn.write("boot" + "\r\n")
        helpers.log("AfterUpgradeLogging") 
        tn.read_until("login:", 3)
        tn.write(user + "\r\n")        
        tn.read_until("password:", 3)
        tn.write(password + "\r\n")
        tn.read_until("#", 3)
        helpers.log("AfterUpgradeLogged")       
        tn.write("#DONE#" + "\r\n")
        tn.read_until("#", 5)
        tn.write("uname -a" + "\r\n")
        tn.read_until("#", 5)
        tn.write("exit" + "\r\n")
        #print tn.read_all()
        tn.close()
    
    
    
    def _createSSHClient(server, user, password, port=22):
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(server, port, user, password)
        return client


    
    
    def _switch_upgrade_steps(self, switchIp=None, package=None):    
        ''' 
            To upgrade the switches to the latest switchLight image 
            Input : switchIpList : provide switch Ip List 
            Output : True if upgrade successful
        '''
        
        try:
            t = test.Test()
            switch= t.switch(switchIp)
            if not package:
                helpers.log("no package provided")
                swpackage= "latest.switchlight-powerpc-internal-t5.swi"
        
            imagepath= "http://switch-nfs/export/switchlight/autobuilds/main/"
            full_path= str(imagepath) + str(swpackage)
            bash_cmd1= 'cd /mnt/flash2'
            switch.bash(bash_cmd1)
            bash_cmd2= 'rm ' + str(swpackage)
            switch.bash(bash_cmd2)
            bash_cmd3= 'wget ' + str(full_path)
            switch.bash(bash_cmd3)
            bash_cmd4= 'reboot'
            switch.bash(bash_cmd4)
            return True
        #cmdList= [
        #    'cd /mnt/flash2'
        #    'mv latest.switchlight-powerpc-internal-t5.swi latest.switchlight-powerpc-internal-t5.swi.old'     
        #    'wget http://10.192.74.102/export/switchlight/autobuilds/master/latest.switchlight-powerpc-internal-t5.swi'
        #    'reboot'                  
        #          ]
        except:
            helpers.test_failure("Could not complete the upgrade process, check log")   
            return False
            
              
    def switch_upgrade_test(self, switchIpList, package=None):    
        '''
           To upgrade parallel with switchIpList
           package: None - default 
           Input : switchIpList
           Output : true if upgrade successful
        '''
        try:
            if not switchIpList:
                helpers.test_failure("Please provide switchIpList")
                return False   
            if not package:
                helpers.log("no package provided")
                package= "latest.switchlight-powerpc-internal-t5.swi"            
            if __name__ == '__init__':
                jobs= []
                for switch in switchIpList:
                    p = Process(target= '_switch_upgrade_steps', args=(switch, package ))
                    p.start()
                    jobs.append(p)
                    p.join()
                    return True     

        except: 
            helpers.test_failure("could not complete the upgrade process")
            return False 
        

