''' 
###  WARNING !!!!!!!
###  To commit new code, please contact the Library Owner: 
###  Animesh Patcha (animesh.patcha@bigswitch.com)
###  WARNING !!!!!!!
'''
import autobot.helpers as helpers
import autobot.test as test
import subprocess
import string
import telnetlib
import time

class SwitchLight(object):

    def __init__(self):
        pass

#######################################################################
# All Common Switch Show Commands Go Here:
#######################################################################

    def cli_show_interface_macaddress(self,node,intf_name):
        '''Return the MAC/Hardware address of a given interface on a switch
        
            Input:
                    ip_address        IP Address of switch
                    
                    intf_name        Interface Name eg. ethernet1 or portchannel1
                    
            Returns: MAC/Hardware address of interface on success.
        '''
        try:
            t = test.Test()
            s1  = t.switch(node)
            input1 = "show interface " + str(intf_name) + " detail"
            s1.enable(input1)
            content = string.split(s1.cli_content(), '\n')
            (firstvalue,colon,lastvalue) = content[2].strip().partition(':')
            helpers.log("Values after split are %s \n %s \n %s \n" %(firstvalue,colon,lastvalue))
            lastvalue=str(lastvalue).rstrip('\n').replace(" ", "")
            mac_address = lastvalue.rstrip('\n')
            helpers.log("Value in content[1] is %s \n and mac address is %s" %(content[1],mac_address))
            return mac_address
        except:
            helpers.test_failure("Could not execute command. Please check log for errors")
            return False


    def cli_show_interface_state(self,node,intf_name):
        '''Return the Interface State of a given interface on a switch
        
            Input:
                    ip_address        IP Address of switch
                    
                    intf_name        Interface Name eg. ethernet1 or portchannel1
                    
            Returns: Interface State of interface.
        '''
        try:
            t = test.Test()
            s1  = t.switch(node)
            cli_input = "show interface " + str(intf_name) + " detail"
            s1.enable(cli_input)
            content = string.split(s1.cli_content(), '\n')
            helpers.log("Value in content[1] is '%s' " %(content[1]))
            (firstvalue,colon,lastvalue) = content[1].rstrip('\n').strip().split(' ')
            helpers.log("Values after split are %s \n %s \n %s \n" %(firstvalue,colon,lastvalue))
            intf_state = lastvalue.rstrip('\n')
            helpers.log("Value in content[1] is %s \n and intf_state is %s" %(content[1],intf_state))
            return intf_state
        except:
            helpers.test_failure("Could not execute command. Please check log for errors")
            return False

    
    def cli_show_interfaces(self,node,ip_address):
        '''Verify all 52 interfaces are seen in switch
        '''
        try:
            t = test.Test()
            s1  = t.switch(node)
            count=1
            intf_pass_count = 0
            while count < 53 :
                intf_name="ethernet"+str(count)
                cli_input="show interface ethernet"+ str(count) + " detail"
                s1.enable(cli_input)
                cli_output = s1.cli_content()
                if intf_name in cli_output :
                    intf_pass_count=intf_pass_count+1
                helpers.log("Interface %s \n Output is %s \n ======\n" %(intf_name,cli_output))
                count=count+1
            if intf_pass_count == 52:
                    return True
            else:
                    return False
        except:
            helpers.test_failure("Could not execute command. Please check log for errors")
            return False

    def cli_show_ip_address(self,console_ip,console_port):
        '''Detect the IP address of a switch when IP address is not known
        
            Inputs:
                console_ip:    Console IP Address
                console_port:  Console Port Number
        '''
        try:
            user = "admin"
            password = "adminadmin"
            tn = telnetlib.Telnet(str(console_ip),int(console_port))
            tn.read_until("login: ", 3)
            tn.write(user + "\r\n")
            tn.read_until("Password: ", 3)
            tn.write(password + "\r\n")
            tn.read_until('')
            tn.write("show interface ma1 \r\n")
            helpers.sleep(10)
            output = tn.read_very_eager()
            for item in output.split("\n"):
                if "IPv4 Address" in item:
                    output_1 = string.split(item, ': ')
                    output_2 = string.split(output_1[1], '/')
                    ip_address_subnet={'ip-address':str(output_2[0]), 'subnet':str(output_2[1].rstrip('\r'))}           
            tn.write("exit \r\n")
            tn.write("exit \r\n")
            tn.close()
            return (ip_address_subnet)
        except:
            helpers.test_failure("Could not execute command. Please check log for errors")
            return False

    def ping_from_local(self,ip_address):
        '''Execute ping command  from local machine for a particular switch IP
        
            Input:
                ip_address        IP Address of switch
            
            Returns:  Output of Ping
        '''
        try:
            url="/sbin/ping -c 3 %s" % (ip_address)
            returnVal = subprocess.Popen([url], stdout=subprocess.PIPE, shell=True)
            (out, err) = returnVal.communicate()
            helpers.log("URL: %s Output: %s" % (url, out))
            if "Request timeout" in out:
                return False
            else:
                helpers.test_failure("Error was:%s" % (err) )
                return True
        except:
            helpers.test_failure("Could not execute ping. Please check log for errors")
            return False

#######################################################################
# All Common Controller Verification Commands Go Here:
#######################################################################

    def cli_verify_controller(self,node,controller_ip,controller_role):
        '''Configure controller IP address on switch
        
            Input:
                ip_address:        IP Address of switch
        '''
        try:
            t = test.Test()
            s1  = t.switch(node)     
            
            cli_input = "show running-config openflow"
            s1.enable(cli_input)
            cli_output = s1.cli_content()
            run_config = cli_output
            helpers.log("Running Config O/P: \n %s" % (run_config))   
               
            cli_input_2 = "show controller"
            s1.enable(cli_input_2)
            cli_output_2 = s1.cli_content()
            show_output = cli_output_2
            helpers.log("Show Controllers O/P: \n %s" % (cli_input_2)) 
                 
            pass_count=0
            if str(controller_ip) in run_config:
                pass_count=pass_count+1
            input3=str(controller_ip) +":6653"
            if input3 in show_output:
                pass_count=pass_count+1
            if "CONNECTED" in show_output:
                pass_count=pass_count+1
            if controller_role in show_output:
                pass_count=pass_count+1
            if pass_count == 4:
                return True
            else:
                return False
        except:
            helpers.test_failure("Could not execute command. Please check log for errors")
            return False 

    def cli_verify_ip_dns(self,node,subnet,gateway,dns_server,dns_domain):
        '''Verify Switch Correctly reports configured IP Address and DNS
        
            Input: 
                ip_address:    Switch IP address in 1.2.3.4 format
                subnet:        Switch subnet in /18 /24 format
                gateway        IP address of default gateway
                dns_server     dns-server IP address in 1.2.3.4 format
                dns-domain    dns-server IP address in bigswitch.com format
        '''
        try:
            t = test.Test()
            s1  = t.switch(node)     
            
            s1.enable('show running-config interface')
            run_config = s1.cli_content()
            helpers.log("Running Config O/P: \n %s" % (run_config))
            pass_count=0
            input1 = "interface ma1 ip-address " + str(s1.ip) + "/" + str(subnet)
            if input1 in run_config:
                pass_count=pass_count+1
            input2 = "ip default-gateway "+str(gateway)
            if input2 in run_config:
                pass_count=pass_count+1        
            input3 = "dns-domain "+str(dns_domain)
            if input3 in run_config:
                pass_count=pass_count+1             
            input4 = "dns-server "+str(dns_server)
            if input4 in run_config:
                pass_count=pass_count+1
            s1.enable('show interface ma1 detail')
            show_command = s1.cli_content()
            helpers.log("Show Command O/P: \n %s" % (show_command))
            if "ma1 is up" in show_command:
                pass_count=pass_count+1
            input5 = str(s1.ip) + "/"  + str(subnet)
            if input5 in show_command:
                pass_count=pass_count+1
            if "MTU 1500 bytes, Speed 1000 Mbps" in show_command:
                pass_count=pass_count+1
            if pass_count == 7:
                return True
            else:
                return False
        except:
            helpers.test_failure("Could not execute command. Please check log for errors")
            return False

    def cli_verify_dhcp_ip_dns(self,node,subnet,dns_server,dns_domain):
        '''Verify Switch Correctly reports configured IP Address and DNS
        '''
        try:
            t = test.Test()
            s1  = t.switch(node)     
            
            s1.enable('show running-config interface')
            run_config = s1.cli_content()
            helpers.log("Running Config O/P: \n %s" % (run_config))
            pass_count=0
            input1 = "interface ma1 ip-address dhcp"
            if input1 in run_config:
                pass_count=pass_count+1
            input2 = "dns-domain "+str(dns_domain)
            if input2 in run_config:
                pass_count=pass_count+1             
            input3 = "dns-server "+str(dns_server)
            if input3 in run_config:
                pass_count=pass_count+1   
            s1.enable('show interface ma1 detail')
            show_command = s1.cli_content()
            #output_1 = string.split(show_command, '\n')
            #output_2 = string.split(output_1[3], ': ')
            #output_3 = string.split(output_2[1], '/')
            #switch_ip = output_3[0]
            #switch_mask = output_3[1]
            helpers.log("Show Command O/P: \n %s" % (show_command))
            if "ma1 is up" in show_command:
                pass_count=pass_count+1
            input4 = str(s1.ip) + "/"  + str(subnet)
            if input4 in show_command:
                pass_count=pass_count+1
            if "MTU 1500 bytes, Speed 1000 Mbps" in show_command:
                pass_count=pass_count+1
            if pass_count == 6:
                return True
            else:
                return False
        except:
            helpers.test_failure("Could not execute command. Please check log for errors")
            return False       
#######################################################################
# All Common Controller Configuration Commands Go Here:
#######################################################################
    def cli_enable_disable_controller(self,node,iteration):
        '''Activate and deactivate controller configuration on switch
        
            Inputs:
                ip_address    IP Address of Switch
                iteration     Number of times the operation has to be performed
        '''
        try:
            t = test.Test()
            c = t.controller('master')
            s1  = t.switch(node)  
            mycount = 1
            while (mycount<=iteration):
                cli_input = "no controller " + str(c.ip)
                s1.config(cli_input)
                s1.enable('show running-config openflow')
                helpers.log("Output of show running-config openflow after removing controller configuration %s" %(s1.cli_content()))
                helpers.sleep(10)
                cli_input_1 = "controller " + str(c.ip)
                s1.config(cli_input_1)
                s1.enable('show running-config openflow')
                helpers.log("Output of show running-config openflow after re-enabling controller %s" %(s1.cli_content()))
                if iteration > mycount :
                    mycount=mycount+1
                    helpers.sleep(10)
                elif mycount == iteration :
                    helpers.log('Exiting from loop')
            return True
        except:
            helpers.test_failure("Could not execute command. Please check log for errors")
            return False


    def cli_disable_interface(self,node,interface_name):
        ''' Shut/Unshut interface via CLI
        
            Input:
                ip_address        IP Address of Switch
                interface_name    Interface Name
                state             Yes="shutdown", No="no shutdown"
        '''
        try:
            t = test.Test()
            s1  = t.switch(node)
            cli_input_1 = "interface " + str(interface_name) + " shutdown"
            s1.config(cli_input_1)
            return True
        except:
            helpers.test_failure("Could not execute command. Please check log for errors")
            return False
        
    def cli_enable_interface(self,node,interface_name):
        ''' Shut/Unshut interface via CLI
        
            Input:
                ip_address        IP Address of Switch
                interface_name    Interface Name
                state             Yes="shutdown", No="no shutdown"
        '''
        try:
            t = test.Test()
            s1  = t.switch(node)
            cli_input_1 = "no interface " + str(interface_name) + " shutdown"
            s1.config(cli_input_1)
            return True
        except:
            helpers.test_failure("Could not execute command. Please check log for errors")
            return False

    def bash_disable_interface_bshell(self,node,interface_num):
        ''' Shut/Unshut interface via broadcom shell command. This can be used only if it is an internal image.
        
            Input:
                ip_address        IP Address of Switch
                interface_name    Interface Name
                state             Yes="shutdown", No="no shutdown"
        '''
        try:
            t = test.Test()
            s1  = t.switch(node)  
            bash_input = 'ofad-ctl bshell port ' + str(interface_num) + ' enable=0'
            s1.bash(bash_input)
            return True
        except:
            helpers.test_failure("Could not execute command. Please check log for errors")
            return False

    def bash_enable_interface_bshell(self,node,interface_num):
        ''' Shut/Unshut interface via broadcom shell command. This can be used only if it is an internal image.
        
            Input:
                ip_address        IP Address of Switch
                interface_name    Interface Name
                state             Yes="shutdown", No="no shutdown"
        '''
        try:
            t = test.Test()
            s1  = t.switch(node)  
            bash_input = 'ofad-ctl bshell port ' + str(interface_num) + ' enable=1'
            s1.bash(bash_input)
            return True
        except:
            helpers.test_failure("Could not execute command. Please check log for errors")
            return False

    def cli_add_interface_ma1(self,console_ip,console_port):
        '''Flap interface ma1 on switch
        
            Inputs:
                console_ip        IP Address of Console Server
                
                console_port      Console Port Number
        '''
        try:
            user = "admin"
            password = "adminadmin"
            tn = telnetlib.Telnet(str(console_ip),int(console_port))
            tn.read_until("login: ", 3)
            tn.write(user + "\r\n")
            tn.read_until("Password: ", 3)
            tn.write(password + "\r\n")
            tn.read_until('')
            tn.write("\r\n" + "show running-config" + "\r\n")
            tn.write("\r\n" + "debug bash" + "\r\n")
            tn.write("ifconfig ma1 " + "\r\n")
            tn.write("ifconfig ma1 down" + "\r\n")
            time.sleep(2)
            tn.write("ifconfig ma1 up" + "\r\n")
            tn.write("exit" + "\r\n")
            tn.write("exit" + "\r\n")
            tn.close()
            return True 
        except:
            helpers.test_failure("Could not execute command. Please check log for errors")
            return False

    # Alias
    cli_update_interface_ma1 = cli_add_interface_ma1

    def cli_execute_command(self,node,cli_input):
        '''Execute a generic command on the switch and return ouput.
        
            Input:
                ip_address        IP Address of Switch
                input            Command to be executed on switch
                
            Return Value: Output from command execution
            
            Example:
            
            |${syslog_op}=  |  execute switch command return output | 10.192.75.7  |  debug ofad 'help; cat /var/log/syslog | grep \"Disabling port port-channel1\"' |
                    
        '''
        try:
            t = test.Test()
            s1  = t.switch(node)
            helpers.sleep(float(1))
            s1.enable(cli_input)
            helpers.sleep(float(1))
            cli_output = s1.cli_content()
            helpers.log("Input is '%s' \n Output is %s" %(cli_input,cli_output))
            return cli_output
        except:
            helpers.test_failure("Could not execute command. Please check log for errors")
            return False

    def cli_add_controller(self,node,controller_ip):
        '''Configure controller IP address on switch
        
            Input:
                ip_address:        IP Address of switch
        '''

        try:
            t = test.Test()
            s1  = t.switch(node)
            cli_input="controller "+ s1.ip()
            s1.config(cli_input)            
            helpers.sleep(float(30))
            return True
        except:
            helpers.test_failure("Configuration of controller failed")
            return False  


    def cli_delete_controller(self,node,controller_ip):
        '''Delete controller IP address on switch
        
            Input:
                ip_address:        IP Address of switch
                controller_ip:        IP Address of Controller
        '''

        try:
            t = test.Test()
            s1  = t.switch(node)
            cli_input="no controller "+ s1.ip()
            s1.config(cli_input)            
            helpers.sleep(float(30))
            return True
        except:
            helpers.test_failure("Configuration delete failed")
            return False
    def cli_add_static_ip(self,console_ip,console_port,ip_address,subnet,gateway):
        '''Configure static IP address configuration on switch.
        '''
        try:
            user = "admin"
            password = "adminadmin"
            tn = telnetlib.Telnet(str(console_ip),int(console_port))
            tn.read_until("login: ", 3)
            tn.write(user + "\r\n")
            tn.read_until("Password: ", 3)
            tn.write(password + "\r\n")
            tn.read_until('')
            tn.write("\r\n" + "enable \r\n")
            tn.write("conf t \r\n")
            tn.write("\r\n" + "interface ma1 ip-address " + str(ip_address)+ "/" + str(subnet)+ " \r\n")
            tn.write("\r\n" + "ip default-gateway " + str(gateway)+  " \r\n")
            tn.write("exit" + "\r\n")
            tn.write("exit" + "\r\n")
            tn.close()
            return True
        except:
            helpers.test_failure("Could not execute command. Please check log for errors")
            return False
        
    def cli_delete_static_ip(self,console_ip,console_port,ip_address,subnet,gateway):
        '''Delete static IP address configuration on switch.
        '''
        try:
            user = "admin"
            password = "adminadmin"
            tn = telnetlib.Telnet(str(console_ip),int(console_port))
            tn.read_until("login: ", 3)
            tn.write(user + "\r\n")
            tn.read_until("Password: ", 3)
            tn.write(password + "\r\n")
            tn.read_until('')
            tn.write("\r\n" + "enable \r\n")
            tn.write("\r\n" + "conf t \r\n")
            tn.write("\r\n" + "no interface ma1 ip-address " + str(ip_address)+ "/" + str(subnet)+ " \r\n")
            tn.write("\r\n" + "no ip default-gateway " + str(gateway)+  " \r\n")
            tn.write("exit" + "\r\n")
            tn.write("exit" + "\r\n")
            tn.close()
            return True
        except:
            helpers.test_failure("Could not execute command. Please check log for errors")
            return False

    def cli_add_dhcp_ip(self,console_ip,console_port):
        '''Configure static IP address configuration on switch.
        '''
        try:
            user = "admin"
            password = "adminadmin"
            tn = telnetlib.Telnet(str(console_ip),int(console_port))
            tn.read_until("login: ", 3)
            tn.write(user + "\r\n")
            tn.read_until("Password: ", 3)
            tn.write(password + "\r\n")
            tn.read_until('')
            tn.write("enable \r\n")
            tn.write("conf t \r\n")
            tn.write("interface ma1 ip-address dhcp \r\n")
            helpers.sleep(10)
            tn.read_until(">")
            tn.write("exit \r\n")
            tn.write("exit \r\n")
            tn.close()
            return True
        except:
            helpers.test_failure("Could not execute command. Please check log for errors")
            return False

    def cli_delete_dhcp_ip(self,console_ip,console_port,ip_address, subnet, gateway):
        '''Configure static IP address configuration on switch.
        '''
        try:
            user = "admin"
            password = "adminadmin"
            tn = telnetlib.Telnet(str(console_ip),int(console_port))
            tn.read_until("login: ", 3)
            tn.write(user + "\r\n")
            tn.read_until("Password: ", 3)
            tn.write(password + "\r\n")
            tn.read_until('')
            tn.write("\r\n" + "no interface ma1 dhcp \r\n")
            tn.write("\r\n" + "no interface ma1 ip-address " + str(ip_address) + "/" + str(subnet)+" \r\n")
            tn.write("\r\n" + "no ip default-gateway " + str(gateway) + " \r\n")
            tn.write("exit" + "\r\n")
            tn.write("exit" + "\r\n")
            tn.close()
            return True
        except:
            helpers.test_failure("Could not configure static IP address configuration on switch. Please check log for errors")
            return False

    def cli_add_dns_server_domain(self,console_ip,console_port,dns_server,dns_domain):
        '''Configure static IP address configuration on switch.
        '''
        try:
            user = "admin"
            password = "adminadmin"
            tn = telnetlib.Telnet(str(console_ip),int(console_port))
            tn.read_until("login: ", 3)
            tn.write(user + "\r\n")
            tn.read_until("Password: ", 3)
            tn.write(password + "\r\n")
            tn.read_until('')
            tn.write("\r\n" + "dns-domain " + str(dns_domain)+ " \r\n")
            tn.write("\r\n" + "dns-server " + str(dns_server)+  " \r\n")
            tn.write("exit" + "\r\n")
            tn.write("exit" + "\r\n")
            tn.close()
            return True
        except:
            helpers.test_failure("Could not configure static IP address configuration on switch. Please check log for errors")
            return False
        
    def cli_delete_dns_server_domain(self,console_ip,console_port,dns_server,dns_domain):
        '''Delete static IP address configuration on switch.
        '''
        try:
            user = "admin"
            password = "adminadmin"
            tn = telnetlib.Telnet(str(console_ip),int(console_port))
            tn.read_until("login: ", 3)
            tn.write(user + "\r\n")
            tn.read_until("Password: ", 3)
            tn.write(password + "\r\n")
            tn.read_until('')
            tn.write("\r\n" + "no dns-domain " + str(dns_domain)+ " \r\n")
            tn.write("\r\n" + "no dns-server " + str(dns_server)+  " \r\n")
            tn.write("exit" + "\r\n")
            tn.write("exit" + "\r\n")
            tn.close()
            return True
        except:
            helpers.test_failure("Could not execute command. Please check log for errors")
            return False

#######################################################################
# All Common Switch Platform/Feature Related Commands Go Here:
#######################################################################

    def bash_restart_process(self,node,processName):
        '''Restart a process on switch
        
            Input:
                node        Switch
                
                processName        Name of process to be restarted
        '''
        try:
            t = test.Test()
            s1  = t.switch(node)
            bash_input='service '+ str(processName) +  ' restart'
            s1.bash(bash_input)
            return True
        except:
            helpers.test_failure("Could not execute command. Please check log for errors")
            return False

############################################################################
#  Platform Testcases
############################################################################
############# SNMP SHOW ##############################

    def cli_show_snmp(self,node):
        '''Execute CLI command "show snmp-server".
        
            Input: 
                ip_address        IP Address of switch
        '''
        try:
            t = test.Test()
            s1  = t.switch(node)
            cli_input='show snmp-server'
            s1.enable(cli_input)
            return s1.cli_content()
        except:
            helpers.test_failure("Could not execute command. Please check log for errors")
            return False
    
#   Objective: Execute snmpgetnext from local machine for a particular SNMP OID
#   Input: SNMP Community and OID 
#   Return Value:  return the SNMP Walk O/P
    def snmp_cmd(self,node,snmp_cmd,snmpCommunity,snmpOID):
        '''Execute snmp command which do not require options from local machine for a particular SNMP OID
        
            Input:
                ip_address        IP Address of switch
                
                snmp_cmd          SNMP Command like snmpwalk, snmpget, snmpgetnext etc.
                
                snmpCommunity    SNMP Community
                
                snmpOID           OID for which walk is being performed
            
            Returns:  Output from SNMP Walk.
        '''
        try:
            t = test.Test()
            s1  = t.switch(node)
            url="/usr/bin/%s -v2c -c %s %s %s" % (str(snmp_cmd),str(snmpCommunity),s1.ip(),str(snmpOID))
            returnVal = subprocess.Popen([url], stdout=subprocess.PIPE, shell=True)
            (out, _) = returnVal.communicate()             
            helpers.log("URL: %s Output: %s" % (url, out))
            return out
        except:
            helpers.test_failure("Could not execute command. Please check log for errors")
            return False
        
    def snmp_cmd_opt(self,ip_address,snmp_cmd,snmpOpt, snmpCommunity,snmpOID):
        '''Execute snmp command which  require options from local machine for a particular SNMP OID
        
            Input:
                ip_address        IP Address of switch
                
                snmp_cmd          SNMP Command like snmpbulkwalk, snmpbulkget, etc.
                
                snmpCommunity    SNMP Community
                
                snmpOID           OID for which walk is being performed
            
            Returns:  Output from SNMP Walk.
        '''
        try:
            url="/usr/bin/%s  -v2c %s -c %s %s %s" % (str(snmp_cmd),str(snmpOpt),str(snmpCommunity),ip_address,str(snmpOID))
            returnVal = subprocess.Popen([url], stdout=subprocess.PIPE, shell=True)
            (out, _ ) = returnVal.communicate()
            helpers.log("URL: %s Output: %s" % (url, out))
            return out
        except:
            helpers.test_failure("Could not execute command. Please check log for errors")
            return False
        
############# SNMP CONFIGURATION ##############################

    def cli_add_snmp_keyword(self,node,snmpKey,snmpValue):
        ''' Configure SNMP Key/Value
        
            Input: 
                ip_address        IP Address of switch
                
                snmpKey           SNMP Key like location, community etc
                
                snmpValue         Value corresponding to SNMP Key    
        '''
        try:
            t = test.Test()
            s1  = t.switch(node)
            cli_input="snmp-server %s %s" % (str(snmpKey),str(snmpValue))
            s1.config(cli_input)
            return True
        except:
            helpers.test_failure("Could not execute command. Please check log for errors")
            return False


    def cli_delete_snmp_keyword(self,node,snmpKey,snmpValue):
        ''' Delete SNMP Key/Value
        
            Input: 
                ip_address        IP Address of switch
                
                snmpKey           SNMP Key like location, community etc
                
                snmpValue         Value corresponding to SNMP Key    
        '''
        try:
            t = test.Test()
            s1  = t.switch(node)
            cli_input="no snmp-server %s %s" % (str(snmpKey),str(snmpValue))
            s1.config(cli_input)
            return True
        except:
            helpers.test_failure("Could not execute command. Please check log for errors")
            return False
    
    def cli_add_snmp_host(self,node,remHostIP,snmpKey,snmpCommunity,snmpPort):
        ''' Configure Remote SNMP Host
        
            Input: 
                ip_address        IP Address of switch
                
                remHostIP         IP Address of remote host
                       
                snmpKey           Acceptable values are traps/informs
                
                snmpCommunity     SNMP community
                
                snmpPort          Port on which traps are sent out.
        '''
        try:
            t = test.Test()
            s1  = t.switch(node)
            if snmpKey == "traps" or snmpKey == "trap":
                snmpKey = "traps"
            else:
                snmpKey = "informs"
            cli_input="snmp-server host %s %s %s udp-port %s" % (str(remHostIP),str(snmpKey),str(snmpCommunity),str(snmpPort))
            s1.config(cli_input)
            return True
        except:
            helpers.test_failure("Could not execute command. Please check log for errors")
            return False

    def cli_delete_snmp_host(self,node,remHostIP,snmpKey,snmpCommunity,snmpPort):
        ''' Delete Remote SNMP Host
        
            Input: 
                ip_address        IP Address of switch
                
                remHostIP         IP Address of remote host
                       
                snmpKey           Acceptable values are traps/informs
                
                snmpCommunity     SNMP community
                
                snmpPort          Port on which traps are sent out.
        '''
        try:
            t = test.Test()
            s1  = t.switch(node)
            if snmpKey == "traps" or snmpKey == "trap":
                snmpKey = "traps"
            else:
                snmpKey = "informs"
            cli_input="no snmp-server host %s %s %s udp-port %s" % (str(remHostIP),str(snmpKey),str(snmpCommunity),str(snmpPort))
            s1.config(cli_input)
            return True
        except:
            helpers.test_failure("Could not execute command. Please check log for errors")
            return False

    def cli_enable_snmp(self,node):
        ''' Enable SNMP Server.
        
            Input: 
                ip_address        IP Address of switch
        '''
        try:
            t = test.Test()
            s1  = t.switch(node)
            s1.config("snmp-server enable")
            return True
        except:
            helpers.test_failure("Could not execute command. Please check log for errors")
            return False

    def cli_disable_switch_snmp(self,node):
        ''' Disable SNMP Server.
        
            Input: 
                ip_address        IP Address of switch
        '''
        try:
            t = test.Test()
            s1  = t.switch(node)
            s1.config("no snmp-server enable")
            return True
            return True
        except:
            helpers.test_failure("Could not execute command. Please check log for errors")
            return False




############# PORT-CHANNEL SHOW COMMANDS##############################

    def cli_verify_portchannel(self,node,pcNumber):
        '''Verify portchannel shows as up
        
            Input:
                node        reference to switch
                
                pcNumber           PortChannel number. Range is between 1 and 30
                
            Returns: true if interface is up, false otherwise
        '''
        try:
            t = test.Test()
            s1  = t.switch(node)
            intf_name = "port-channel"+pcNumber
            cli_input = "show interface " + intf_name
            s1.enable(cli_input)
            cli_output = s1.cli_content()
            helpers.log("Multiline is %s" % (string.split(cli_output, '\n')))
            lagNumber = 60 + int(pcNumber)
            input1=str(lagNumber) + "* " + intf_name
            if str(input1) in cli_output:
                    return True
            else:
                    return False
        except:
            helpers.test_failure("Could not execute command. Please check log for errors")
            return False
    
    def cli_verify_portchannel_members(self,node,pc_number,intf_name):
        '''Verify if portchannel contains the member interface that was configured 
        
            Input:
                ip_address        IP Address of switch
                
                pcNumber           PortChannel number. Range is between 1 and 30
                
                intf_name        Interface name of member interface
                
            Returns: true if member interface is present, false otherwise
        '''
        try:
            t = test.Test()
            s1  = t.switch(node)
            cli_input = "show port-channel " + str(pc_number)
            s1.enable(cli_input)
            cli_output = s1.cli_content()
            content = string.split(cli_output, '\n')
            helpers.log("Length of content %d" % (len(content)))
            if len(content) < 8 :
                return False
            else :
                for i in range(8,len(content)):
                    intfName = ' '.join(content[i].split()).split(" ",2)
                    helpers.log('intfName is %s' % intfName)
                    if len(intfName) >1 and intfName[1] == intf_name :
                            helpers.log("IntfName is %s \n" % (intfName[1]))
                            return True
            return False
        except:
            helpers.test_failure("Could not execute command. Please check log for errors")
            return False

    def cli_verify_portchannel_member_state(self,node,pc_number,intf_name):
        '''Verify if portchannel member interface is up
        
            Input:
                node        reference to switch (as defined in topo file)
                
                pcNumber           PortChannel number. Range is between 1 and 30
                
                intf_name        Interface name of member interface
                
            Returns: true if member interface is up, false otherwise
        '''
        try:
            t = test.Test()
            s1  = t.switch(node)
            cli_input = "show port-channel " + str(pc_number)
            s1.enable(cli_input)
            cli_output = s1.cli_content()
            content = string.split(cli_output, '\n')
            helpers.log("Length of content %d" % (len(content)))
            if len(content) < 8 :
                return False
            else :
                for i in range(8,len(content)):
                    intfName = ' '.join(content[i].split()).split(" ",2)
                    if len(intfName) >1 and intfName[1] == intf_name :
                            if intfName[0] == "*" :
                                helpers.log("Intf Name is %s and state is %s \n" % (intfName[1], intfName[0]))
                                return True
                            else:
                                helpers.log("Intf Name is %s and state is %s \n" % (intfName[1], intfName[0]))
                                return False
            return False
        except:
            helpers.test_failure("Could not execute command. Please check log for errors")
            return False

############# PORT-CHANNEL CONFIGURATION COMMANDS##############################

    def cli_add_portchannel(self,node,pcNumber,portList,hashMode):
        '''Configure port-channel
        
            Inputs:
                ip_address        IP Address of switch
                
                pcNumber           PortChannel number. Range is between 1 and 30
                
                portList          Comma or - separated list of ports (integer values) that are part of PortChannel group.
                
                hashMode            Hash Mode. Supported values are L2 or L3
                
            Returns: True if configuration is a success or False otherwise
            
            Examples:
            
                | configure portchannel | 10.192.75.7  |  1  | 49-50  | L3 |
 
        '''
        try:
            t = test.Test()
            s1  = t.switch(node)
            input_value = "port-channel " + str(pcNumber) + " interface-list " + str(portList) + "  hash " + str(hashMode)
            helpers.log("Input is %s" % input_value )
            try:
                s1.config(input_value)
            except:
                return False            
            return True
        except:
            helpers.test_failure("Could not execute command. Please check log for errors")
            return False

    def cli_delete_portchannel(self,node,pcNumber):
        '''Unconfigure port-channel
        
            Inputs:
                ip_address        IP Address of switch
                
                pcNumber           PortChannel number. Range is between 1 and 30
                
            Returns: True if configuration is a success or False otherwise
            
            Examples:
            
                | unconfigure portchannel | 10.192.75.7  |  1  |
        '''
        try:
            t = test.Test()
            s1  = t.switch(node)
            cli_input = "no port-channel " + str(pcNumber) + " "
            s1.config(cli_input)
            return True
        except:
            helpers.test_failure("Could not execute command. Please check log for errors")
            return False