import autobot.helpers as helpers
import autobot.test as test
import os
import sys
import getopt
import hashlib
import time
import telnetlib
import re
from multiprocessing import Process


class switchimageinstall(object):

    def __init__(self):
        pass

#### First Login using console 
#### reboot
#### Wait for the message "Hit any key to stop autoboot:" 
#### send "enter"
#### Verify Prompt "=>" 
### if not "=>" , then reboot again. errorprompt counter = 1 
### If prompt "=>" 
### Issue the follwoing setenv commands
### => 
### setenv ipaddr 10.192.107.15
### setenv netmask 255.255.192.0
### setenv gatewayip 10.192.64.1
### setenv serverip 10.192.74.102 
### saveenv
### ping 10.192.64.1
### 
### Issue the four installer_cmd* commands
### setenv sl_url 'http://10.192.74.102/export/switchlight/autobuilds/master/latest.switchlight-powerpc-release.all.installer'
### setenv sl_ip ${ipaddr}::${gatewayip}:${netmask}::eth1:off
### setenv onie_debugargs install_url=${sl_url} ip=${sl_ip}
### run onie_bootcmd
### Wait for the message "Press Control-C now to enter loader shell"
### 
### Send Control-C
### Verify propmt "loader#" 
### if prompt not "loader#" , reboot
### Wait for the message "Press Control-C now to enter loader shell"
### Send "Control-C"
### Verify propmt "loader#"
### Send "netconf"
### Wait for message "Which interface (blank for ma1)?"
### send "ma1"
### Wait for message "IP address (/prefix optional for v4)?"
### Send "10.192.107.11/18"
### Wait for message "Default gateway IP address (blank for none)?"
### Send "10.192.64.1"
### Wait for message "DNS IP address (blank for none)?"
### Send  "10.192.3.1"
### Wait for message "DNS default domain (blank for none)?"
### Send  "bigswitch.com"
### Wait for message "Configuring interface ma1"
### Wait for prompt "loader#"
### Send "cd /mnt/flash2"
### Wait for prompt "loader#"
### Send "wget http://10.192.74.102/export/switchlight/autobuilds/master/latest.switchlight-powerpc-internal-t5.swi"
### Wait for prompt "loader#"
### Send "echo "SWI=flash2:latest.switchlight-powerpc-internal-t5.swi"  >/mnt/flash/boot-config"
### Wait for prompt "loader#"
### Send "reboot"
### Wait for prompt "#"
### Send "DONE " 




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
    
        
        
        
        
        
        
