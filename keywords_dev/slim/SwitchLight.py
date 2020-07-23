'''
###  WARNING !!!!!!!
###  This is where common code for SwitchLight will go in.
###  
###  To commit new code, please contact the Library Owner: 
###  Animesh Patcha (animesh.patcha@bigswitch.com)
###
###  DO NOT COMMIT CODE WITHOUT APPROVAL FROM LIBRARY OWNER
###  
###  Last Updated: 02/06/2014
###  
###  WARNING !!!!!!!
'''

import autobot.helpers as helpers
import autobot.test as test
from Exscript.protocols import SSH2
from Exscript import Account, Host
import subprocess
import string
import telnetlib
import time
import re

class SwitchLight(object):

    def __init__(self):
        pass

#######################################################################
# All Common Switch Show Commands Go Here:
#######################################################################

    def cli_show_interface_macaddress(self, node, intf_name):
        '''
            Objective:
            - Return the MAC/Hardware address of a given interface on a switch
        
            Input:
            | node | Reference to switch (as defined in .topo file) |                     
            | intf_name | Interface Name eg. ethernet1 or portchannel1 | 
                    
            Return Value: 
            - MAC/Hardware address of interface on success.
        '''
        try:
            t = test.Test()
            s1 = t.switch(node)
            input1 = "show interface " + str(intf_name) + " detail"
            s1.enable(input1)
            content = string.split(s1.cli_content(), '\n')
            (firstvalue, colon, lastvalue) = content[2].strip().partition(':')
            helpers.log("Values are %s \n %s \n %s \n" % (firstvalue, colon, lastvalue))
            lastvalue = str(lastvalue).rstrip('\n').replace(" ", "")
            mac_address = lastvalue.rstrip('\n')
            helpers.log("Value in content[1] is %s \n and mac address is %s" % (content[1], mac_address))
            return mac_address
        except:
            helpers.test_failure("Could not execute command. Please check log for errors")
            return False

    def cli_show_interface_state(self, node, intf_name):
        '''
            Objective:
            - Return the Interface State of a given interface on a switch
        
            Input:
            | node | Reference to switch (as defined in .topo file) |                     
            | intf_name | Interface Name eg. ethernet1 or portchannel1 | 
                    
            Return Value: 
            - Interface State of interface.
        '''
        try:
            t = test.Test()
            s1 = t.switch(node)
            cli_input = "show interface " + str(intf_name) + " detail"
            s1.enable(cli_input)
            content = string.split(s1.cli_content(), '\n')
            helpers.log("Value in content[1] is '%s' " % (content[1]))
            (firstvalue, colon, lastvalue) = content[1].rstrip('\n').strip().split(' ')
            helpers.log("Values after split are %s \n %s \n %s \n" % (firstvalue, colon, lastvalue))
            intf_state = lastvalue.rstrip('\n')
            helpers.log("Value in content[1] is %s \n and intf_state is %s" % (content[1], intf_state))
            return intf_state
        except:
            helpers.test_failure("Could not execute command. Please check log for errors")
            return False

    def cli_show_interface_statistics(self, node, intf_name):
        '''
            Objective:
            - Return the Interface State of a given interface on a switch
        
            Input:
            | node | Reference to switch (as defined in .topo file) |                     
            | intf_name | Interface Name eg. ethernet1 or portchannel1 | 
                    
            Return Value: 
            - Interface State of interface.
        '''
        try:
            t = test.Test()
            s1 = t.switch(node)
            cli_input = "show interface " + str(intf_name) + " detail"
            s1.enable(cli_input)
            lines = string.split(s1.cli_content(), '\n')
            return_array = {}
            for i in lines:
                p = i.lstrip(" ")
                value = re.sub(' +', ' ', p)
                if "Received" in value:
                    return_array["received_bytes"] = int(re.split(' ', value)[1])
                    return_array["received_packets"] = int(re.split(' ', value)[3])
                elif "Sent" in value:
                    return_array["sent_bytes"] = int(re.split(' ', value)[1])
                    return_array["sent_packets"] = int(re.split(' ', value)[3])
            return return_array
        except:
            helpers.test_failure("Could not execute command. Please check log for errors")
            return False

    def cli_show_interfaces(self, node):
        '''
            Objective:
            - Verify all 52 interfaces are seen in switch

            Input:
            | node | Reference to switch (as defined in .topo file) |
            
            Return Value:
            - True if all 52 interfaces are seen
            - False of all 52 interfaces are not seen
        '''
        try:
            t = test.Test()
            s1 = t.switch(node)
            count = 1
            intf_pass_count = 0
            while count < 53:
                intf_name = "ethernet" + str(count)
                cli_input = "show interface ethernet" + str(count) + " detail"
                s1.enable(cli_input)
                cli_output = s1.cli_content()
                if intf_name in cli_output:
                    intf_pass_count = intf_pass_count + 1
                helpers.log("Interface %s \n Output is %s \n ======\n" % (intf_name, cli_output))
                count = count + 1
            if intf_pass_count == 52:
                return True
            else:
                return False
        except:
            helpers.test_failure("Could not execute command. Please check log for errors")
            return False

    def cli_show_ip_address(self, console_ip, console_port):
        '''
        
            Objective:
            - Detect the IP address of a switch when IP address is not known
        
            Inputs:
            | console_ip | Console IP Address | 
            | console_port | Console Port Number |
            
            Return Value:
            - IP address and Subnet on success
            - False in case of failure 
        '''
        try:
            user = "admin"
            password = "adminadmin"
            tn = telnetlib.Telnet(str(console_ip), int(console_port))
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
                    ip_address_subnet = {'ip-address':str(output_2[0]), 'subnet':str(output_2[1].rstrip('\r'))}
            tn.write("exit \r\n")
            tn.write("exit \r\n")
            tn.close()
            return ip_address_subnet
        except:
            helpers.test_failure("Could not execute command. Please check log for errors")
            return False

    def ping_from_local(self, node):
        '''
            Objective:
            - Execute ping command from local machine for a particular switch IP

            Input:
            | ip_address | IP Address of switch |

            Return Value:
            - Output of Ping
        '''
        try:
            t = test.Test()
            switch = t.switch(node)
            url = "/sbin/ping -c 3 %s" % (switch.ip())
            returnVal = subprocess.Popen([url], stdout=subprocess.PIPE, shell=True)
            (out, _) = returnVal.communicate()
            helpers.log("URL: %s Output: %s" % (url, out))
            if "Request timeout" in out:
                return False
            else:
                return True
        except:
            helpers.test_failure("Could not execute ping. Please check log for errors")
            return False

    def cli_ping_from_switch(self, node, remote):
        '''
            Objective:
            - Execute ping command from switch  to a particular remote IP/domain address

            Input:
            | node | Reference to switch (as defined in .topo file) |
            | remote | Remote IP or Domain Address |

            Return Value:
            - True on ping success
            - False on ping failure
        '''
        try:
            t = test.Test()
            switch = t.switch(node)
            cli_action = "ping -c 3 %s" + str(remote)
            switch.enable(cli_action)
            cli_output = switch.cli_content()
            if "Destination Host Unreachable" in cli_output:
                helpers.test_log(cli_output)
                return False
            elif "unknown host" in cli_output:
                helpers.test_log(cli_output)
                return False
            else:
                helpers.test_log(cli_output)
                return True
        except:
            helpers.test_failure("Could not execute ping. Please check log for errors")
            return False
#######################################################################
# All Common Controller Verification Commands Go Here:
#######################################################################

    def cli_verify_controller(self, node, controller):
        '''
            Objective:
            - Configure controller IP address on switch

            Input:
            | node | Reference to switch (as defined in .topo file) |
            | controller_ip | IP Address of Controller |
            | controller_role | Role of controller (Active/Backup) |

            Return Value:
            - True on verification success
            - False on verification failure
    '''
        try:
            t = test.Test()
            c = t.controller(controller)
            s1 = t.switch(node)
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

            pass_count = 0
            if (c.is_main()):
                controller_role = "MASTER"
            else:
                controller_role = "SLAVE"

            if str(c.ip()) in run_config:
                pass_count = pass_count + 1
            input3 = str(c.ip()) + ":6653"
            if input3 in show_output:
                pass_count = pass_count + 1
            if "CONNECTED" in show_output:
                pass_count = pass_count + 1
            if controller_role in show_output:
                pass_count = pass_count + 1
            if pass_count == 4:
                return True
            else:
                return False
        except:
            helpers.test_failure("Could not execute command. Please check log for errors")
            return False

    def cli_verify_ip_dns(self, node, subnet, gateway, dns_server, dns_domain):
        '''
            Objective:
            - Verify Switch Correctly reports configured IP Address and DNS

            Input: 
            | node | Reference to switch (as defined in .topo file) |
            | subnet | Switch subnet in /18 /24 format | 
            | gateway | IP address of default gateway | 
            | dns_server | dns-server IP address in 1.2.3.4 format | 
            | dns-domain | dns-server IP address in bigswitch.com format |

            Return Value:
            - True on verification success
            - False on verification failure
    '''
        try:
            t = test.Test()
            switch = t.switch(node)
            switch.enable('show running-config interface')
            run_config = switch.cli_content()
            helpers.log("Running Config O/P: \n %s" % (run_config))
            pass_count = 0
            input1 = "interface ma1 ip-address " + switch.ip() + "/" + str(subnet)
            helpers.log("Input1:%s" % (input1))
            if input1 in run_config:
                helpers.log("PASS:IP Address and Subnet was found in running-config")
                pass_count = pass_count + 1
            else:
                helpers.log("FAIL:IP Address and Subnet was not found in running-config")

            input2 = "ip default-gateway " + str(gateway)
            helpers.log("Input2:%s" % (input2))
            if input2 in run_config:
                helpers.log("PASS:IP default gateway was found in running-config")
                pass_count = pass_count + 1
            else:
                helpers.log("FAIL:IP default gateway was not found in running-config")

            input3 = "dns-domain " + str(dns_domain)
            helpers.log("Input3:%s" % (input3))
            if input3 in run_config:
                helpers.log("PASS:DNS domain was found in running-config")
                pass_count = pass_count + 1
            else:
                helpers.log("FAIL:DNS domain was not found in running-config")

            input4 = "dns-server " + str(dns_server)
            helpers.log("Input4:%s" % (input4))
            if input4 in run_config:
                helpers.log("PASS:DNS server was found in running-config")
                pass_count = pass_count + 1
            else:
                helpers.log("FAIL:DNS server was not found in running-config")

            switch.enable('show interface ma1 detail')
            show_command = switch.cli_content()
            helpers.log("Show Command O/P: \n %s" % (show_command))
            if "ma1 is up" in show_command:
                helpers.log("PASS:MA1 is up in show interface output")
                pass_count = pass_count + 1
            else:
                helpers.log("FAIL:MA1 is not up in show interface output")

            input5 = str(switch.ip()) + "/" + str(subnet)
            helpers.log("Input5:%s" % (input5))
            if input5 in show_command:
                helpers.log("PASS:IP Address and Subnet was found in show interface output")
                pass_count = pass_count + 1
            else:
                helpers.log("FAIL:IP Address and Subnet was not found in show interface output")

            if "MTU 1500 bytes, Speed 1000 Mbps" in show_command:
                helpers.log("PASS:MTU and Speed was found in show interface output")
                pass_count = pass_count + 1
            else:
                helpers.log("FAIL:MTU and Speed was not found in show interface output")
            return True

            if pass_count == 7:
                return True
            else:
                return False
        except:
            helpers.test_log("Could not execute command. Please check log for errors")
            return False

    def cli_verify_dhcp_ip_dns(self, node, subnet, dns_server, dns_domain):
        '''
            Objective:
            - Verify Switch Correctly reports configured IP Address and DNS when IP address is obtained via DHCP

            Input: 
            | node | Reference to switch (as defined in .topo file) |
            | subnet | Switch subnet in /18 /24 format | 
            | gateway | IP address of default gateway | 
            | dns_server | dns-server IP address in 1.2.3.4 format | 
            | dns-domain | dns-server IP address in bigswitch.com format |

            Return Value:
            - True on verification success
            - False on verification failure
    '''
        try:
            t = test.Test()
            s1 = t.switch(node)

            s1.enable('show running-config interface')
            run_config = s1.cli_content()
            helpers.log("Running Config O/P: \n %s" % (run_config))
            pass_count = 0
            input1 = "interface ma1 ip-address dhcp"
            if input1 in run_config:
                pass_count = pass_count + 1
            input2 = "dns-domain " + str(dns_domain)
            if input2 in run_config:
                pass_count = pass_count + 1
            input3 = "dns-server " + str(dns_server)
            if input3 in run_config:
                pass_count = pass_count + 1
            s1.enable('show interface ma1 detail')
            show_command = s1.cli_content()
            # output_1 = string.split(show_command, '\n')
            # output_2 = string.split(output_1[3], ': ')
            # output_3 = string.split(output_2[1], '/')
            # switch_ip = output_3[0]
            # switch_mask = output_3[1]
            helpers.log("Show Command O/P: \n %s" % (show_command))
            if "ma1 is up" in show_command:
                pass_count = pass_count + 1
            input4 = str(s1.ip()) + "/" + str(subnet)
            if input4 in show_command:
                pass_count = pass_count + 1
            if "MTU 1500 bytes, Speed 1000 Mbps" in show_command:
                pass_count = pass_count + 1
            if pass_count == 6:
                return True
            else:
                return False
        except:
            helpers.test_failure("Could not execute command. Please check log for errors")
            return False

    def cli_verify_crc_forwarding_is_disabled(self, node):
        '''
            Objective: Verify CRC Forwarding is disabled.
            
            Inputs:
            | node | Reference to switch (as defined in .topo file) |
            
            Return Value:
            - True on verification success
            - False on verification failure
        '''
        try:
            t = test.Test()
            switch = t.switch(node)
            pass_count = 0

            cli_input = "show running-config forwarding"
            switch.enable(cli_input)
            show_output = switch.cli_content()
            if "forwarding crc disable" in show_output:
                pass_count = pass_count + 1
            else:
                helpers.test_log("FAIL: Did not see 'forwarding crc disable' in running-config")

            cli_input_1 = "show forwarding crc status"
            switch.enable(cli_input_1)
            show_output_1 = switch.cli_content()
            if "Packets with CRC error will be dropped on all ports" in show_output_1:
                pass_count = pass_count + 1
            else:
                helpers.test_log("FAIL: Did not see 'forwarding crc disable' in running-config")

            if pass_count == 2:
                return True
            else:
                return False
        except:
            helpers.test_failure("Could not execute command. Please check log for errors")
            return False

    def cli_verify_crc_forwarding_is_enabled(self, node):
        '''
            Objective: Verify CRC Forwarding is disabled.
            
            Inputs:
            | node | Reference to switch (as defined in .topo file) |
            
            Return Value:
            - True on verification success
            - False on verification failure
        '''
        try:
            t = test.Test()
            switch = t.switch(node)
            cli_input_1 = "show forwarding crc status"
            switch.enable(cli_input_1)
            show_output = switch.cli_content()
            if "Packets with CRC error will be forwarded on all ports" in show_output:
                return True
            else:
                return False
        except:
            helpers.test_failure("Could not execute command. Please check log for errors")
            return False


#######################################################################
# All Common Controller Configuration Commands Go Here:
#######################################################################
    def cli_enable_disable_controller(self, node, iteration):
        '''
            Objective:
            - Activate and deactivate controller configuration on switch
        
            Inputs:
            | node | Reference to switch (as defined in .topo file) |
            | iteration | Number of times the operation has to be performed | 
            
            Return Value:
            - True on verification success
            - False on verification failure
        '''
        try:
            t = test.Test()
            c = t.controller('main')
            s1 = t.switch(node)
            mycount = 1
            while mycount <= int(iteration):
                cli_input = "no controller " + str(c.ip())
                s1.config(cli_input)
                s1.enable('show running-config openflow')
                helpers.log("Output of show running-config openflow after removing controller configuration %s" % (s1.cli_content()))
                helpers.sleep(10)
                cli_input_1 = "controller " + str(c.ip())
                s1.config(cli_input_1)
                s1.enable('show running-config openflow')
                helpers.log("Output of show running-config openflow after re-enabling controller %s" % (s1.cli_content()))
                helpers.log("mycount is %s" % mycount)
                helpers.log("iteration is %s" % iteration)
                if mycount < int(iteration):
                    helpers.log('My Count is %s' % (mycount))
                    mycount = mycount + 1
                    helpers.sleep(10)
                else:
                    helpers.log('Exiting from loop')
                    return True
        except:
            helpers.test_failure("Could not execute command. Please check log for errors")
            return False
        

    def cli_disable_interface(self, node, interface_name):
        ''' 
            Objective:
            - Disable interface via CLI

            Input:
            | node | Reference to switch (as defined in .topo file) |
            | interface_name | Interface Name |
                
            Return Value:
            - True on  success
            - False on  failure
        '''
        try:
            t = test.Test()
            s1 = t.switch(node)
            cli_input_1 = "interface " + str(interface_name) + " shutdown"
            s1.config(cli_input_1)
            return True
        except:
            helpers.test_failure("Could not execute command. Please check log for errors")
            return False

    def cli_enable_interface(self, node, interface_name):
        ''' 
            Objective:
            - Enable interface via CLI
        
            Input:
            | node | Reference to switch (as defined in .topo file) |
            | interface_name | Interface Name |
                
            Return Value:
            - True on  success
            - False on  failure
        '''
        try:
            t = test.Test()
            s1 = t.switch(node)
            cli_input_1 = "no interface " + str(interface_name) + " shutdown"
            s1.config(cli_input_1)
            return True
        except:
            helpers.test_failure("Could not execute command. Please check log for errors")
            return False

    def bash_disable_interface_bshell(self, node, interface_num):
        '''  
            Objective:
            - Disable interface via bshell. This can be used only if it is an internal image.
        
            Input:
            | node | Reference to switch (as defined in .topo file) |
            | interface_name | Interface Name |
                
            Return Value:
            - True on  success
            - False on  failure
        '''
        try:
            t = test.Test()
            s1 = t.switch(node)
            bash_input = 'ofad-ctl bshell port ' + str(interface_num) + ' enable=0'
            s1.bash(bash_input)
            return True
        except:
            helpers.test_failure("Could not execute command. Please check log for errors")
            return False

    def bash_enable_interface_bshell(self, node, interface_num):
        '''  
            Objective:
            - Enable interface via bshell. This can be used only if it is an internal image.

            Input:
            | node | Reference to switch (as defined in .topo file) |
            | interface_name | Interface Name |
                
            Return Value:
            - True on  success
            - False on  failure
        '''
        try:
            t = test.Test()
            s1 = t.switch(node)
            bash_input = 'ofad-ctl bshell port ' + str(interface_num) + ' enable=1'
            s1.bash(bash_input)
            return True
        except:
            helpers.test_failure("Could not execute command. Please check log for errors")
            return False

    def cli_flap_interface_ma1(self, node):
        '''
            Objective: 
            - Flap interface ma1 on switch
        
            Inputs:
            | console_ip | IP Address of Console Server |    
            | console_port | Console Port Number | 
                
            Return Value:
            - True on  success
            - False on  failure
        '''
        try:
            t = test.Test()
            switch = t.switch(node)
            user = "admin"
            password = "adminadmin"
            console_ip = t.params(node, "console_ip")
            console_port = t.params(node, "console_port")
            tn = telnetlib.Telnet(str(console_ip), int(console_port))
            tn.read_until("login: ", 3)
            tn.write(user + "\r\n")
            tn.read_until("Password: ", 3)
            tn.write(password + "\r\n")
            tn.read_until('')
            tn.write("\r\n" + "show running-config" + "\r\n")
            tn.write("\r\n" + "debug bash" + "\r\n")
            tn.write("ifconfig ma1 " + "\r\n")
            tn.write("ifconfig ma1 down" + "\r\n")
            time.sleep(10)
            tn.write("ifconfig ma1 up" + "\r\n")
            tn.write("exit" + "\r\n")
            tn.write("exit" + "\r\n")
            tn.close()
            return True
        except:
            helpers.test_failure("Could not execute command. Please check log for errors")
            return False

    # Alias
    def cli_update_interface_ma1(self, console_ip, console_port):
        return self.cli_add_interface_ma1(console_ip, console_port)


    def cli_execute_command(self, node, cli_input):
        '''
            Objective:
            - Execute a generic command on the switch and return ouput.

            Input:
            | node | Reference to switch (as defined in .topo file) |
            | input  | Command to be executed on switch |
                
            Return Value: 
            - Output from command execution

            Example:
            
            |${syslog_op}=  |  execute switch command return output | 10.192.75.7  |  debug ofad 'help; cat /var/log/syslog | grep \"Disabling port port-channel1\"' |

        '''
        try:
            t = test.Test()
            s1 = t.switch(node)
            helpers.sleep(float(1))
            s1.enable(cli_input)
            helpers.sleep(float(1))
            cli_output = s1.cli_content()
            helpers.log("Input is '%s' \n Output is %s" % (cli_input, cli_output))
            return cli_output
        except:
            helpers.test_failure("Could not execute command. Please check log for errors")
            return False

    def cli_add_controller(self, node, controller):
        '''
            Objective:
            - Configure controller IP address on switch

            Input:
            | node | Reference to switch (as defined in .topo file) |

            Return Value:
            - True on  success
            - False on  failure

        '''

        try:
            t = test.Test()
            c1 = t.controller(controller)
            s1 = t.switch(node)
            cli_input = "controller " + c1.ip()
            s1.config(cli_input)
            helpers.sleep(float(30))
            return True
        except:
            helpers.test_failure("Configuration of controller failed")
            return False

    def cli_delete_controller(self, node, controller):
        '''
            Objective:
            - Delete controller IP address on switch
        
            Input:
            | node | Reference to switch (as defined in .topo file) |
            | controller_ip | IP Address of Controller |

            Return Value:
            - True on  success
            - False on  failure
        '''

        try:
            t = test.Test()
            c1 = t.controller(controller)
            s1 = t.switch(node)
            cli_input = "no controller " + c1.ip()
            s1.config(cli_input)
            helpers.sleep(float(30))
            return True
        except:
            helpers.test_failure("Configuration delete failed")
            return False

    def cli_add_static_ip(self, node, subnet, gateway):
        '''
        Objective:
         - Configure static IP address configuration on switch.

        Inputs:
        | console_ip | IP Address of Console Server |    
        | console_port | Console Port Number | 
        | ip_address | IP Address of Switch |
        | subnet | Switch subnet in /18 /24 format | 
        | gateway | IP address of default gateway | 

        Return Value:
        - True on configuration success
        - False on configuration failure

        '''
        try:
            t = test.Test()
            switch = t.switch(node)
            user = "admin"
            password = "adminadmin"
            console_ip = t.params(node, "console_ip")
            console_port = t.params(node, "console_port")
            tn = telnetlib.Telnet(console_ip, console_port)
            tn.read_until("login: ", 3)
            tn.write(user + "\r\n")
            tn.read_until("Password: ", 3)
            tn.write(password + "\r\n")
            tn.read_until('')
            tn.write("\r\n" + "enable \r\n")
            tn.write("conf t \r\n")
            tn.write("\r\n" + "interface ma1 ip-address " + str(switch.ip()) + "/" + str(subnet) + " \r\n")
            tn.write("\r\n" + "ip default-gateway " + str(gateway) + " \r\n")
            tn.write("exit" + "\r\n")
            tn.write("exit" + "\r\n")
            tn.close()
            return True
        except:
            helpers.test_log("Could not execute command. Please check log for errors")
            return False

    def cli_delete_static_ip(self, node, subnet, gateway):
        '''
        Objective:
        - Delete static IP address configuration on switch.
        
        Inputs:
        | console_ip | IP Address of Console Server |    
        | console_port | Console Port Number | 
        | ip_address | IP Address of Switch |
        | subnet | Switch subnet in /18 /24 format | 
        | gateway | IP address of default gateway | 


        Return Value:
        - True on configuration success
        - False on configuration failure
        '''
        try:
            t = test.Test()
            switch = t.switch(node)
            user = "admin"
            password = "adminadmin"
            console_ip = t.params(node, "console_ip")
            console_port = t.params(node, "console_port")
            tn = telnetlib.Telnet(console_ip, console_port)
            tn.read_until("login: ", 3)
            tn.write(user + "\r\n")
            tn.read_until("Password: ", 3)
            tn.write(password + "\r\n")
            tn.read_until('')
            tn.write("\r\n" + "enable \r\n")
            tn.write("\r\n" + "conf t \r\n")
            tn.write("\r\n" + "no interface ma1 ip-address " + str(switch.ip()) + "/" + str(subnet) + " \r\n")
            tn.write("\r\n" + "no ip default-gateway " + str(gateway) + " \r\n")
            tn.write("exit" + "\r\n")
            tn.write("exit" + "\r\n")
            tn.close()
            return True
        except:
            helpers.test_failure("Could not execute command. Please check log for errors")
            return False

    def cli_add_dhcp_ip(self, console_ip, console_port):
        '''
        Objective:
        - Configure static IP address configuration on switch.
        
        Inputs:
        | console_ip | IP Address of Console Server |    
        | console_port | Console Port Number | 
        | ip_address | IP Address of Switch |
        | subnet | Switch subnet in /18 /24 format | 
        | gateway | IP address of default gateway | 

        Return Value:
        - True on configuration success
        - False on configuration failure
        '''
        try:
            user = "admin"
            password = "adminadmin"
            tn = telnetlib.Telnet(str(console_ip), int(console_port))
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

    def cli_delete_dhcp_ip(self, console_ip, console_port, ip_address, subnet, gateway):
        '''
        Objective:
         - Delete DHCP IP address configuration on switch.
        
        Inputs:
        | console_ip | IP Address of Console Server |    
        | console_port | Console Port Number | 
        | ip_address | IP Address of Switch |
        | subnet | Switch subnet in /18 /24 format | 
        | gateway | IP address of default gateway | 

        Return Value:
        - True on configuration success
        - False on configuration failure
        '''
        try:
            user = "admin"
            password = "adminadmin"
            tn = telnetlib.Telnet(str(console_ip), int(console_port))
            tn.read_until("login: ", 3)
            tn.write(user + "\r\n")
            tn.read_until("Password: ", 3)
            tn.write(password + "\r\n")
            tn.read_until('')
            tn.write("\r\n" + "no interface ma1 dhcp \r\n")
            tn.write("\r\n" + "no interface ma1 ip-address " + str(ip_address) + "/" + str(subnet) + " \r\n")
            tn.write("\r\n" + "no ip default-gateway " + str(gateway) + " \r\n")
            tn.write("exit" + "\r\n")
            tn.write("exit" + "\r\n")
            tn.close()
            return True
        except:
            helpers.test_failure("Could not configure static IP address configuration on switch. Please check log for errors")
            return False

    def cli_add_dns_server_domain(self, node, dns_server, dns_domain):
        '''
        Objective:
        - Add DNS Server and Domain configuration on switch.

        Inputs:
        | console_ip | IP Address of Console Server |    
        | console_port | Console Port Number | 
        | dns_server | dns server Address of Switch |
        | dns_domain | dns domain | 

        Return Value:
        - True on configuration success
        - False on configuration failure
        
        '''
        try:
            t = test.Test()
            # switch = t.switch(node)
            user = "admin"
            password = "adminadmin"
            console_ip = t.params(node, "console_ip")
            console_port = t.params(node, "console_port")
            try:
                helpers.log("Switch Console IP is %s \n Switch Console Port is %s :" % (console_ip, console_port))
                tn = telnetlib.Telnet(console_ip, console_port)
                tn.read_until("login: ", 3)
                tn.write(user + "\r\n")
                tn.read_until("Password: ", 3)
                tn.write(password + "\r\n")
                tn.read_until('')
            except:
                helpers.test_failure("Could not configure static IP address configuration on switch. Please check log for errors")
                return False
            else:
                tn.write("\r\n" + "dns-domain " + str(dns_domain) + " \r\n")
                tn.write("\r\n" + "dns-server " + str(dns_server) + " \r\n")
                tn.write("exit" + "\r\n")
                tn.write("exit" + "\r\n")
                tn.close()
                return True
        except:
            helpers.test_log("Could not configure static IP address configuration on switch. Please check log for errors")
            return False

    def cli_delete_dns_server_domain(self, node, dns_server, dns_domain):
        '''
        Objective:
        - Delete DNS configuration on switch.

        Inputs:
        | console_ip | IP Address of Console Server |    
        | console_port | Console Port Number | 
        | dns_server | dns server Address of Switch |
        | dns_domain | dns domain | 

        Return Value:
        - True on configuration success
        - False on configuration failure
        
        '''
        try:
            t = test.Test()
            # switch = t.switch(node)
            user = "admin"
            password = "adminadmin"
            console_ip = t.params(node, "console_ip")
            console_port = t.params(node, "console_port")
            tn = telnetlib.Telnet(console_ip, console_port)
            tn.read_until("login: ", 3)
            tn.write(user + "\r\n")
            tn.read_until("Password: ", 3)
            tn.write(password + "\r\n")
            tn.read_until('')
            tn.write("\r\n" + "no dns-domain " + str(dns_domain) + " \r\n")
            tn.write("\r\n" + "no dns-server " + str(dns_server) + " \r\n")
            tn.write("exit" + "\r\n")
            tn.write("exit" + "\r\n")
            tn.close()
            return True
        except:
            helpers.test_log("Could not execute command. Please check log for errors")
            return False

    def cli_set_boot(self, node, image):
        '''
            Objective:
            - Configure boot parameters on switch
            
            Inputs:
            | node | Reference to switch (as defined in .topo file) |
            | image | location and name of image |
            | netmask | Network mask |
            | gateway| Default Gateway for network |
            | dns_server | IP Address of DNS Server |
            | dns_domain | DNS Domain Address |
            
            Return Value:
            - True, if configuration is successful
            - False, if configuration is unsuccessful
        '''
        try:

            t = test.Test()
            s1 = t.switch(node)
            cli_input_1 = 'boot image ' + str(image)
            s1.config(cli_input_1)
            helpers.test_log(s1.cli_content)
            return True
        except:
            helpers.test_failure("Could not execute command. Please check log for errors")
            return False


    def cli_enable_crc_forwarding(self, node):
        ''' 
            Objective:
            - Enable crc forwarding via CLI
        
            Input:
            | node | Reference to switch (as defined in .topo file) |
                
            Return Value:
            - True on  success
            - False on  failure
        '''
        try:
            t = test.Test()
            s1 = t.switch(node)
            cli_input_1 = "no forwarding crc disable"
            s1.config(cli_input_1)
            return True
        except:
            helpers.test_failure("Could not execute command. Please check log for errors")
            return False

    def cli_disable_crc_forwarding(self, node):
        ''' 
            Objective:
            - Disable crc forwarding via CLI
        
            Input:
            | node | Reference to switch (as defined in .topo file) |
                
            Return Value:
            - True on  success
            - False on  failure
        '''
        try:
            t = test.Test()
            s1 = t.switch(node)
            cli_input_1 = "forwarding crc disable"
            s1.config(cli_input_1)
            return True
        except:
            helpers.test_failure("Could not execute command. Please check log for errors")
            return False


#######################################################################
# All Common Switch Platform/Feature Related Commands Go Here:
######################################################################


    def cli_verify_password_change(self, node, user, current_password, version_string):
        '''
            Objective: Return version of switch software
            
            Input:
            | node | Reference to switch (as defined in .topo file) |
    
            Return Value:
            - Output on configuration success
            - False on configuration failure   
        '''
        t = test.Test()
        console_ip = t.params(node, "console_ip")
        console_port = t.params(node, "console_port")
        tn = telnetlib.Telnet(console_ip, console_port)
        tn.set_debuglevel(10)
        tn.read_until("login:", 10)
        tn.write(str(user).encode('ascii') + "\r\n".encode('ascii'))
        tn.read_until("Password: ", 10)
        tn.write(str(current_password).encode('ascii') + "\r\n".encode('ascii'))
        tn.read_until('')
        tn.write("show version \r\n".encode('ascii'))
        helpers.sleep(4)
        output = tn.read_very_eager()
        helpers.log(output)
        tn.write("logout" + "\r\n".encode('ascii'))
        tn.close()
        if version_string in  output:
            return True
        else:
            self.cli_change_user_password(node, user, current_password, "adminadmin")
            return False

    def cli_change_user_password(self, node, user, current_password, new_password):
        '''
            Objective: Change the username and password for a given user
            
            Input:
            | node | Reference to switch (as defined in .topo file) |
            | username | Username for which password has to be changed |
            | current_password | Current Password |
            | new_password | Desired password |
    
            Return Value:
            - True on configuration success
            - False on configuration failure         
        '''
        try:
            t = test.Test()
            console_ip = t.params(node, "console_ip")
            console_port = t.params(node, "console_port")
            helpers.log("Console IP is %s \n Console Port is %s \n" % (console_ip, console_port))
            helpers.log("Username is %s \n Password is %s \n" % (user, new_password))
            tn = telnetlib.Telnet(console_ip, console_port)
            tn.set_debuglevel(10)
            tn.read_until("login:", 10)
            tn.write(str(user) + "\r\n")
            tn.read_until("Password: ", 10)
            tn.write(str(current_password) + "\r\n")
            tn.read_until('')
            tn.write("\r\n" + "enable \r\n")
            tn.write("\r\n" + "configure \r\n")
            tn.write("\r\n" + "username " + str(user) + " password " + str(new_password) + "\r\n")
            tn.write("exit" + "\r\n")
            tn.write("logout" + "\r\n")
            tn.close()
            return True
        except:
            tn.close()
            helpers.test_failure("Could not execute command. Please check log for errors")
            return False

    def bash_execute_command(self, node, command):
        '''
        Objective:
        -Execute a command in bash mode and return output
        
        Input:
        | node | Reference to switch (as defined in .topo file) |
        | command | Command to be executed |

        
        Return Value:
        - Output on success
        - False on configuration failure        
        '''
        try:
            t = test.Test()
            switch = t.switch(node)
        except:
            return False
        else:
            switch.bash(command)
            bash_output = switch.cli_content()
            return bash_output



    def cli_restart_switch(self, node, save_config='no'):
        '''
        Objective:
        -Restart a switch
        
        Input:
        | node | Reference to switch (as defined in .topo file) |
        
        Return Value:
        - True on configuration success
        - False on configuration failure        
        '''
        try:
            t = test.Test()
            switch = t.switch(node)
            if not "no" in save_config:
                switch.config("copy running-config startup-config")
            cli_input = 'reload now'
            switch.enable('')
            switch.send(cli_input)
            helpers.sleep(150)
            return True
        except:
            helpers.test_failure("Could not execute command. Please check log for errors")
            return False

    def bash_restart_process(self, node, processName):
        '''
        Objective:
        -Restart a process on switch
        
        Input:
        | node | Reference to switch (as defined in .topo file) |
        | processName | Name of process to be restarted |
        
        Return Value:
        - True on configuration success
        - False on configuration failure
        
        '''
        try:
            t = test.Test()
            s1 = t.switch(node)
            bash_input = 'service ' + str(processName) + ' restart'
            s1.bash(bash_input, timeout=60)
            return True
        except:
            helpers.test_failure("Could not execute command. Please check log for errors")
            return False

    def bash_upgrade_switch(self, node, image_path):
        '''
        Objective:
        Upgrade switch via bash
        
        Inputs:
        | node | Reference to switch (as defined in .topo file) |
        | image_path | Image path after http://switch-nfs.bigswitch.com/export/switchlight/ |
        
        Return Value:
        - True on upgrade success
        - False on upgrade failure        
        '''

        try:
            t = test.Test()
            switch = t.switch(node)
            image_array = image_path.split('/')
            image_name = image_array[len(image_array) - 1]
            bash_input_1 = 'rm /mnt/flash2/' + str(image_name)
            switch.bash(bash_input_1)
            full_path = "http://switch-nfs.bigswitch.com/export/switchlight/" + str(image_path)
            bash_input_2 = "cd /mnt/flash2/; wget " + str(full_path) + " ./"
            switch.bash(bash_input_2)
            bash_input_3 = "echo SWI=flash2:" + str(image_name) + " > /mnt/flash/boot-config"
            switch.bash(bash_input_3)
            bash_input_4 = "ls -lrt /mnt/flash2/; cat /mnt/flash/boot-config"
            switch.bash(bash_input_4)
            helpers.sleep(1)
            bash_input_5 = "reboot"
            switch.bash(bash_input_5)
            return True
        except:
            helpers.test_failure("Could not execute command. Please check log for errors")
            return False

    def cli_upgrade_switch(self, node, image_path, netdns='10.192.3.1', netdomain='bigswitch.com', netmask='255.255.192.0', netgw='10.192.64.1'):
        '''
        Objective:
        Upgrade switch via CLI
        
        Inputs:
        | node | Reference to switch (as defined in .topo file) |
        | image_path | Image path after http://switch-nfs.bigswitch.com/export/switchlight/ |
        | netdns | IP Address of DNS Server. Default Value is 10.192.3.1|
        | netdomain | DNS Domain. Default Value is bigswitch.com|
        | netmask | NetMask. Default Value is 255.255.192.0|
        | netgw | Default Gateway. Default Value is 10.192.64.1 |
        
        Return Value:
        - True on upgrade success
        - False on upgrade failure    
        '''
        try:
            t = test.Test()
            switch = t.switch(node)
            cli_input_1 = "boot image http://switch-nfs.bigswitch.com/export/switchlight/" + str(image_path)
            switch.config(cli_input_1)
            cli_input_2 = "boot netdev ma1"
            switch.config(cli_input_2)
            cli_input_3 = "boot netdns " + str(netdns)
            switch.config(cli_input_3)
            cli_input_4 = "boot netdomain " + str(netdomain)
            switch.config(cli_input_4)
            cli_input_5 = "boot netip " + str(switch.ip())
            switch.config(cli_input_5)
            cli_input_6 = "boot netmask " + str(netmask)
            switch.config(cli_input_6)
            cli_input_7 = "boot netgw " + str(netgw)
            switch.config(cli_input_7)
            cli_input_8 = "copy running-config startup-config"
            switch.config(cli_input_8)
            cli_input_9 = "reload now"
            switch.config(cli_input_9)
            return True
        except:
            helpers.test_failure("Could not execute command. Please check log for errors")
            return False

############################################################################
#  Platform Testcases
############################################################################
############# SNMP SHOW ##############################

    def cli_show_snmp(self, node):
        '''
        Objective:
        - Execute CLI command "show snmp-server".
        
        Input:
        | node | Reference to switch (as defined in .topo file) |

        Return Value:
        - True on configuration success
        - False on configuration failure
        '''
        try:
            t = test.Test()
            s1 = t.switch(node)
            cli_input = 'show snmp-server'
            s1.enable(cli_input)
            return s1.cli_content()
        except:
            helpers.test_failure("Could not execute command. Please check log for errors")
            return False



############# SNMP CONFIGURATION ##############################

    def cli_add_snmp_keyword(self, node, snmpKey, snmpValue):
        ''' 
            Objective:
            - Configure SNMP Key/Value
            
            Input:
            | node | Reference to switch (as defined in .topo file) |
            | snmpKey | SNMP Key like location, community etc |
            | snmpValue | Value corresponding to SNMP Key |   
            
            Return Value:
            - True on configuration success
            - False on configuration failure
        '''
        try:
            t = test.Test()
            s1 = t.switch(node)
            cli_input = "snmp-server %s %s" % (str(snmpKey), str(snmpValue))
            s1.config(cli_input)
            return True
        except:
            helpers.test_failure("Could not execute command. Please check log for errors")
            return False


    def cli_delete_snmp_keyword(self, node, snmpKey, snmpValue):
        ''' 
            Objective:
            - Delete a SNMP Key/Value
            
            Input:
            | node | Reference to switch (as defined in .topo file) |
            | snmpKey | SNMP Key like location, community etc |
            | snmpValue | Value corresponding to SNMP Key |   
            
            Return Value:
            - True on configuration success
            - False on configuration failure   
        '''
        try:
            t = test.Test()
            s1 = t.switch(node)
            cli_input = "no snmp-server %s %s" % (str(snmpKey), str(snmpValue))
            s1.config(cli_input)
            return True
        except:
            helpers.test_failure("Could not execute command. Please check log for errors")
            return False

    def cli_add_snmp_host(self, node, remHostIP, snmpKey, snmpCommunity, snmpPort):
        ''' 
            Objective:
            - Configure Remote SNMP Host
        
            Input: 
            | node | Reference to switch (as defined in .topo file) | 
            | remHostIP | IP Address of remote host|      
            | snmpKey | Acceptable values are traps/informs| 
            | snmpCommunity | SNMP community | 
            | snmpPort | Port on which traps are sent out.| 
            
            Return Value:
            - True on configuration success
            - False on configuration failure

        '''
        try:
            t = test.Test()
            s1 = t.switch(node)
            if snmpKey == "traps" or snmpKey == "trap":
                snmpKey = "traps"
            else:
                snmpKey = "informs"
            cli_input = "snmp-server host %s %s %s udp-port %s" % (str(remHostIP), str(snmpKey), str(snmpCommunity), str(snmpPort))
            s1.config(cli_input)
            return True
        except:
            helpers.test_failure("Could not execute command. Please check log for errors")
            return False

    def cli_delete_snmp_host(self, node, remHostIP, snmpKey, snmpCommunity, snmpPort):
        ''' 
            Objective:
            - Delete Remote SNMP Host
        
            Input: 
            | node | Reference to switch (as defined in .topo file) | 
            | remHostIP | IP Address of remote host|      
            | snmpKey | Acceptable values are traps/informs| 
            | snmpCommunity | SNMP community | 
            | snmpPort | Port on which traps are sent out.| 
            
            Return Value:
            - True on configuration success
            - False on configuration failure
        '''
        try:
            t = test.Test()
            s1 = t.switch(node)
            if snmpKey == "traps" or snmpKey == "trap":
                snmpKey = "traps"
            else:
                snmpKey = "informs"
            cli_input = "no snmp-server host %s %s %s udp-port %s" % (str(remHostIP), str(snmpKey), str(snmpCommunity), str(snmpPort))
            s1.config(cli_input)
            return True
        except:
            helpers.test_failure("Could not execute command. Please check log for errors")
            return False

    def cli_enable_snmp(self, node):
        ''' 
            Objective:
            - Enable SNMP Server.
            
            Input: 
            | node | Reference to switch (as defined in .topo file) | 
            
            Return Value:
            - True on configuration success
            - False on configuration failure
        '''
        try:
            t = test.Test()
            s1 = t.switch(node)
            s1.config("snmp-server enable")
            return True
        except:
            helpers.test_failure("Could not execute command. Please check log for errors")
            return False

    def cli_disable_switch_snmp(self, node):
        ''' 
            Objective:
            - Disable SNMP Server.
            
            Input: 
            | node | Reference to switch (as defined in .topo file) | 
            
            Return Value:
            - True on configuration success
            - False on configuration failure
        '''
        try:
            t = test.Test()
            s1 = t.switch(node)
            s1.config("no snmp-server enable")
            return True
        except:
            helpers.test_failure("Could not execute command. Please check log for errors")
            return False




############# PORT-CHANNEL SHOW COMMANDS##############################

    def cli_verify_portchannel(self, node, pcNumber):
        '''
            Objective:
            - Verify portchannel shows as up
                    
            Input:
            | node | Reference to switch (as defined in .topo file) | 
            | pcNumber | PortChannel number. Range is between 1 and 30 |                 
                           
            Return Value:
            - True on verification success
            - False on verification failure
        '''
        try:
            t = test.Test()
            s1 = t.switch(node)
            intf_name = "port-channel" + pcNumber
            cli_input = "show interface " + intf_name
            s1.enable(cli_input)
            cli_output = s1.cli_content()
            helpers.log("Multiline is %s" % (string.split(cli_output, '\n')))
            lagNumber = 60 + int(pcNumber)
            input1 = str(lagNumber) + "* " + intf_name
            if str(input1) in cli_output:
                return True
            else:
                return False
        except:
            helpers.test_failure("Could not execute command. Please check log for errors")
            return False

    def cli_verify_portchannel_members(self, node, pc_number, *intf_name_list):
        '''
            Objective:
            - Verify if portchannel contains the member interface that was configured 
                    
            Input:
            | node | Reference to switch (as defined in .topo file) | 
            | pcNumber | PortChannel number. Range is between 1 and 30 |                 
                           
            Return Value:
            - True if member interface is present
            - False if member interface is not present
        '''
        try:
            t = test.Test()
            s1 = t.switch(node)
            cli_input = "show port-channel " + str(pc_number)
            s1.enable(cli_input)
            cli_output = s1.cli_content()
            content = string.split(cli_output, '\n')
            helpers.log("Length of content %d" % (len(content)))
            helpers.log("Length of content %d" % (len(intf_name_list)))
            if len(content) < 8 :
                return False
            elif len(intf_name_list) < 1:
                helpers.test_failure("Passed interface list is empty !!")
                return False
            else :
                pass_count = 0
                for i in range(10, len(content) - 1):
                    intfName = ' '.join(content[i].split()).split(" ", 2)
                    helpers.log('intfName is %s \n %s' % (intfName, intfName[1]))
                    for intf_name in intf_name_list:
                        helpers.log('value is %s' % intf_name)
                        if len(intfName) > 1 and intfName[1] == intf_name :
                            helpers.log("IntfName is %s \n" % (intfName[1]))
                            pass_count = pass_count + 1
                if pass_count == len(intf_name_list):
                    return True
            return False
        except:
            helpers.test_failure("Could not execute command. Please check log for errors")
            return False

    def cli_return_member_interface_stats(self, node, pc_number, sub_interface, txrx, packet_byte="packet"):
        '''           
            Objective:
            - Verify if portchannel contains the member interface that was configured 
                    
            Input:
            | node | Reference to switch (as defined in .topo file) | 
            | pcNumber | PortChannel number. Range is between 1 and 30 |                 
                           
            Return Value:
            - True if member interface is present
            - False if member interface is not present
        '''
        try:
            t = test.Test()
            s1 = t.switch(node)
            cli_input = "show port-channel " + str(pc_number)
            s1.enable(cli_input)
            cli_output = s1.cli_content()
            content = string.split(cli_output, '\n')
            for i in range(0, len(content)):
                if sub_interface in content[i]:
                    txrx_value = re.split('\s+', content[i])
                    if  "tx" in txrx.lower():
                        if "packet" in packet_byte:
                            return txrx_value[2]
                        else:
                            return txrx_value[3]
                    elif "rx" in txrx.lower():
                        if "packet" in packet_byte:
                            return txrx_value[4]
                        else:
                            return txrx_value[5]
                    else:
                        return False
        except:
            helpers.test_failure("Could not execute command. Please check log for errors")
            return False

    def cli_verify_portchannel_member_state(self, node, pc_number, *intf_name_list):
        '''
            Objective:
            - Verify if portchannel member interface is up
                    
            Input:
            | node | Reference to switch (as defined in .topo file) | 
            | pcNumber | PortChannel number. Range is between 1 and 30 |     
            | intf_name | Interface name of member interface |              
                           
            Return Value:
            - True if member interface is up
            - False if member interface is not up        

        '''
        try:
            t = test.Test()
            s1 = t.switch(node)
            cli_input = "show port-channel " + str(pc_number)
            s1.enable(cli_input)
            cli_output = s1.cli_content()
            content = string.split(cli_output, '\n')
            helpers.log("Length of content %d" % (len(content)))
            helpers.log("Length of content %d" % (len(intf_name_list)))
            if len(content) < 8 :
                return False
            elif len(intf_name_list) < 1:
                helpers.test_failure("Passed interface list is empty !!")
                return False
            else :
                pass_count = 0
                for i in range(8, len(content)):
                    intfName = ' '.join(content[i].split()).split(" ", 2)
                    for intf_name in intf_name_list:
                        if len(intfName) > 1 and intfName[1] == intf_name:
                            if intfName[0] == "*":
                                helpers.log("Intf Name is %s and state is %s \n" % (intfName[1], intfName[0]))
                                pass_count = pass_count + 1
                if pass_count == len(intf_name_list):
                    return True
            return False
        except:
            helpers.test_failure("Could not execute command. Please check log for errors")
            return False

############# PORT-CHANNEL CONFIGURATION COMMANDS##############################

    def cli_add_portchannel(self, node, pcNumber, portList, hashMode):
        '''
            Objective:
            - Configure port-channel
            
            Input:
            | node | Reference to switch (as defined in .topo file) | 
            | pcNumber | PortChannel number. Range is between 1 and 30 |     
            | portList | Comma or - separated list of ports (integer values) that are part of PortChannel group. |
            | hashMode |   Hash Mode. Supported values are L2 or L3 |
                            
            Return Value:
            - True on configuration success
            - False on configuration failure
            
            Examples:
            
                | configure portchannel | 10.192.75.7  |  1  | 49-50  | L3 |
 
        '''
        try:
            t = test.Test()
            s1 = t.switch(node)
            input_value = "port-channel " + str(pcNumber) + " interface-list " + str(portList) + "  hash " + str(hashMode)
            helpers.log("Input is %s" % input_value)
            try:
                s1.config(input_value)
                cli_output = s1.cli_content()
                if "is not a valid interface" in cli_output:
                    return False
                else:
                    return True
            except:
                return False
            return True
        except:
            helpers.test_failure("Could not execute command. Please check log for errors")
            return False

    def cli_delete_portchannel(self, node, pcNumber):
        '''
            Objective:
            - Unconfigure port-channel
            
            Input:
            | node | Reference to switch (as defined in .topo file) | 
            | pcNumber | PortChannel number. Range is between 1 and 30 |     
                            
            Return Value:
            - True on configuration success
            - False on configuration failure
            
            Examples:
            
                | unconfigure portchannel | 10.192.75.7  |  1  |
        '''
        try:
            t = test.Test()
            s1 = t.switch(node)
            cli_input = "no port-channel " + str(pcNumber) + " "
            s1.config(cli_input)
            return True
        except:
            helpers.test_failure("Could not execute command. Please check log for errors")
            return False
        
    def cli_add_dpid(self, node, dpid):
        '''
            Objective:
            - Set switch dpid
            
            Input:
            | node | Reference to switch (as defined in .topo file) | 
            | dpid | dpid number |     
                            
            Return Value:
            - True on configuration success
            - False on configuration failure
            
            Examples:
            
                | cli add dpid | s1 |  00:00:00:00:00:00:00:00:01  |
        '''
        try:
            t = test.Test()
            s1 = t.switch(node)
            cli_input = "datapath id  %s" % str(dpid)
            s1.config(cli_input)
            return True
        except:
            helpers.test_failure("Could not execute command. Please check log for errors")
            return False
                
    def cli_delete_dpid(self, node):
        try:
            t = test.Test()
            s1 = t.switch(node)
            cli_input = "no datapath id "
            s1.config(cli_input)
            return True
        except:
            helpers.test_failure("Could not execute command. Please check log for errors")
            return False        

