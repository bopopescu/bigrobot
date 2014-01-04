import autobot.helpers as helpers
import autobot.test as test
from Exscript.protocols import SSH2
from Exscript import Account, Host
import subprocess
import string
import telnetlib
import time

class BsnSwitchCommon(object):

    def __init__(self):
        t = test.Test()
        c = t.controller()
        url = '%s/auth/login' % c.base_url
        helpers.log("url: %s" % url)
        result = c.rest.post(url, {"user":"admin", "password":"adminadmin"})
        helpers.log("result: %s" % helpers.to_json(result))
        session_cookie = result['content']['session_cookie']
        c.rest.set_session_cookie(session_cookie)

#######################################################################
# All Common Controller Show Commands Go Here:
#######################################################################

    def return_intf_macaddress(self,ip_address,intf_name):
        '''Return the MAC/Hardware address of a given interface on a switch
        
            Input:
                    ip_address        IP Address of switch
                    
                    intf_name        Interface Name eg. ethernet1 or portchannel1
                    
            Returns: MAC/Hardware address of interface.
        '''
        t = test.Test()
        conn = SSH2()
        conn.connect(ip_address)
        conn.login(Account("admin","adminadmin"))
        input = "show interface " + str(intf_name) + " detail"
        conn.execute(input)
        content = string.split(conn.response, '\n')
        (firstvalue,colon,lastvalue) = content[2].strip().partition(':')
        lastvalue=str(lastvalue).rstrip('\n').replace(" ", "")
        mac_address = lastvalue.rstrip('\n')
        helpers.log("Value in content[1] is %s \n and mac address is %s" %(content[1],mac_address))
        return mac_address

    def return_intf_state(self,ip_address,intf_name):
        '''Return the Interface State of a given interface on a switch
        
            Input:
                    ip_address        IP Address of switch
                    
                    intf_name        Interface Name eg. ethernet1 or portchannel1
                    
            Returns: Interface State of interface.
        '''
        t = test.Test()
        conn = SSH2()
        conn.connect(ip_address)
        conn.login(Account("admin","adminadmin"))
        input = "show interface " + str(intf_name) + " detail"
        conn.execute(input)
        content = string.split(conn.response, '\n')
        helpers.log("Value in content[1] is '%s' " %(content[1]))
        (firstvalue,colon,lastvalue) = content[1].rstrip('\n').strip().split(' ')
        intf_state = lastvalue.rstrip('\n')
        helpers.log("Value in content[1] is %s \n and intf_state is %s" %(content[1],intf_state))
        return intf_state

#######################################################################
# All Common Controller Verification Commands Go Here:
#######################################################################


#######################################################################
# All Common Controller Configuration Commands Go Here:
#######################################################################
    def activate_deactivate_controller(self,ip_address,iteration):
        '''Activate and deactivate controller configuration on switch
        
            Inputs:
                ip_address    IP Address of Switch
                iteration     Number of times the operation has to be performed
        '''
        t = test.Test()
        c = t.controller()
        conn = SSH2()
        conn.connect(ip_address)
        conn.login(Account("admin","adminadmin"))
        mycount = 1
        while (mycount<=iteration):
            conn.execute('enable')
            conn.execute('conf t')
            inp = "no controller " + str(c.ip)
            conn.execute(inp)
            conn.execute('end')
            conn.execute('show running-config openflow')
            print conn.response
            helpers.sleep(10)
            conn.execute('conf t')
            inp = "controller " + str(c.ip)
            conn.execute(inp)
            conn.execute('end')
            conn.execute('show running-config openflow')
            print conn.response
            if iteration > mycount :
                mycount=mycount+1
                helpers.sleep(10)
            elif mycount == iteration :
                conn.send('exit\r')
                conn.send('exit\r')
                conn.send('exit\r')
                conn.close()
        return True


    def change_interface_state(self,ip_address,interface_name,state):
        ''' Shut/Unshut interface via CLI
        
            Input:
                ip_address        IP Address of Switch
                interface_name    Interface Name
                state             Yes="shutdown", No="no shutdown"
        '''
        t = test.Test()
        conn = SSH2()
        conn.connect(ip_address)
        conn.login(Account("admin","adminadmin"))
        conn.execute('enable')
        conn.execute('conf t')
        if state =="yes" or state =="Yes":
                input = "interface " + str(interface_name) + " shutdown"
        else:
                input = "no interface " + str(interface_name) + " shutdown"
        conn.execute(input)
        conn.send('logout\r')
        conn.close()
        return True


    def change_interface_state_bshell(self,ip_address,interface_num,state):
        ''' Shut/Unshut interface via broadcom shell command. This can be used only if it is an internal image.
        
            Input:
                ip_address        IP Address of Switch
                interface_name    Interface Name
                state             Yes="shutdown", No="no shutdown"
        '''
        t = test.Test()
        conn = SSH2()
        conn.connect(ip_address)
        conn.login(Account("admin","adminadmin"))
        conn.execute('enable')
        conn.execute('conf t')
        if state =="yes" or state =="Yes":
                input = 'debug ofad "help; ofad-ctl bshell port ' + str(interface_num) + ' enable=0"'
        else:
                input = 'debug ofad "help; ofad-ctl bshell port ' + str(interface_num) + ' enable=1"'
        conn.execute(input)
        conn.send('logout\r')
        conn.close()
        return True

    def flap_interface_ma1(self,conIP,conPort):
        '''Flap interface ma1 on switch
        
            Inputs:
                conIP        IP Address of Console Server
                
                conPort      Console Port Number
        '''
        user = "admin"
        password = "adminadmin"
        tn = telnetlib.Telnet(str(conIP),int(conPort))
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


#Objective: Grep syslog on switch for string
#Input:     IP Address of Switch, string to grep for.
#Output:    Output string.
    def execute_switch_command_return_output(self,ip_address,input):
        '''Execute a generic command on the switch and return ouput.
        
            Input:
                ip_address        IP Address of Switch
                input            Command to be executed on switch
                
            Return Value: Output from command execution
            
            Example:
            
            |${syslog_op}=  |  execute switch command return output | 10.192.75.7  |  debug ofad 'help; cat /var/log/syslog | grep \"Disabling port port-channel1\"' |
                    
        '''
        t = test.Test()
        conn = SSH2()
        conn.connect(ip_address)
        conn.login(Account("admin","adminadmin"))
        conn.execute('enable')
        conn.execute(input)
        output = conn.response
        conn.send('logout\r')
        conn.close()
        return output  
    
#######################################################################
# All Common Controller Platform/Feature Related Commands Go Here:
#######################################################################

    def restart_process(self,ip_address,processName):
        '''Restart a process on switch
        
            Input:
                ip_address        IP Address of Switch
                
                processName        Name of process to be restarted
        '''
        t = test.Test()
        conn = SSH2()
        conn.connect(ip_address)
        conn.login(Account("admin","adminadmin"))
        conn.execute('enable')
        input='debug ofad "help; service ' + str(processName) +  ' restart"'
        conn.execute(input)
        conn.send('logout\r')
        conn.close()
        return True

############# SNMP SHOW ##############################

    def snmp_show(self,ip_address):
        '''Execute CLI command "show snmp-server".
        
            Input: 
                ip_address        IP Address of switch
        '''
        t = test.Test()
        conn = SSH2()
        conn.connect(ip_address)
        conn.login(Account("admin","adminadmin"))
        conn.execute("show snmp-server")
        return conn.response
    
#   Objective: Execute snmpgetnext from local machine for a particular SNMP OID
#   Input: SNMP Community and OID 
#   Return Value:  return the SNMP Walk O/P
    def snmp_cmd(self,ip_address,snmp_cmd,snmpCommunity,snmpOID):
        '''Execute snmp command which do not require options from local machine for a particular SNMP OID
        
            Input:
                ip_address        IP Address of switch
                
                snmp_cmd          SNMP Command like snmpwalk, snmpget, snmpgetnext etc.
                
                snmpCommunity    SNMP Community
                
                snmpOID           OID for which walk is being performed
            
            Returns:  Output from SNMP Walk.
        '''
        t = test.Test()
        url="/usr/bin/%s -v2c -c %s %s %s" % (str(snmp_cmd),str(snmpCommunity),ip_address,str(snmpOID))
        returnVal = subprocess.Popen([url], stdout=subprocess.PIPE, shell=True)
        (out, err) = returnVal.communicate()
        helpers.log("URL: %s Output: %s" % (url, out))
        return out
        
    def snmp_cmd_opt(self,ip_address,snmp_cmd,snmpOpt, snmpCommunity,snmpOID):
        '''Execute snmp command which  require options from local machine for a particular SNMP OID
        
            Input:
                ip_address        IP Address of switch
                
                snmp_cmd          SNMP Command like snmpbulkwalk, snmpbulkget, etc.
                
                snmpCommunity    SNMP Community
                
                snmpOID           OID for which walk is being performed
            
            Returns:  Output from SNMP Walk.
        '''
        t = test.Test()
        url="/usr/bin/%s  -v2c %s -c %s %s %s" % (str(snmp_cmd),str(snmpOpt),str(snmpCommunity),ip_address,str(snmpOID))
        returnVal = subprocess.Popen([url], stdout=subprocess.PIPE, shell=True)
        (out, err) = returnVal.communicate()
        helpers.log("URL: %s Output: %s" % (url, out))
        return out
    
    
############# SNMP CONFIGURATION ##############################

    def configure_snmp_keyword(self,ip_address,snmpKey,snmpValue):
        ''' Configure SNMP Key/Value
        
            Input: 
                ip_address        IP Address of switch
                
                snmpKey           SNMP Key like location, community etc
                
                snmpValue         Value corresponding to SNMP Key    
        '''
        t = test.Test()
        conn = SSH2()
        conn.connect(ip_address)
        conn.login(Account("admin","adminadmin"))
        conn.execute('enable')
        conn.execute('conf t')
        input="snmp-server %s %s" % (str(snmpKey),str(snmpValue))
        conn.execute(input)
        conn.send('exit\r')
        conn.send('exit\r')
        conn.send('exit\r')
        conn.close()
        return True


    def delete_snmp_keyword(self,ip_address,snmpKey,snmpValue):
        ''' Delete SNMP Key/Value
        
            Input: 
                ip_address        IP Address of switch
                
                snmpKey           SNMP Key like location, community etc
                
                snmpValue         Value corresponding to SNMP Key    
        '''
        t = test.Test()
        conn = SSH2()
        conn.connect(ip_address)
        conn.login(Account("admin","adminadmin"))
        conn.execute('enable')
        conn.execute('conf t')
        input="no snmp-server %s %s" % (str(snmpKey),str(snmpValue))
        conn.execute(input)
        conn.send('exit\r')
        conn.send('exit\r')
        conn.send('exit\r')
        conn.close()
        return True
    
    def configure_snmp_host(self,ip_address,remHostIP,snmpKey,snmpCommunity,snmpPort):
        ''' Configure Remote SNMP Host
        
            Input: 
                ip_address        IP Address of switch
                
                remHostIP         IP Address of remote host
                       
                snmpKey           Acceptable values are traps/informs
                
                snmpCommunity     SNMP community
                
                snmpPort          Port on which traps are sent out.
        '''
        t = test.Test()
        conn = SSH2()
        conn.connect(ip_address)
        conn.login(Account("admin","adminadmin"))
        conn.execute('enable')
        conn.execute('conf t')
        if snmpKey == "traps" or snmpKey == "trap":
            snmpKey == "traps"
        else:
            snmpKey == "informs"
        input="snmp-server host %s %s %s udp-port %s" % (str(remHostIP),str(snmpKey),str(snmpCommunity),str(snmpPort))
        conn.execute(input)
        conn.send('exit\r')
        conn.send('exit\r')
        conn.send('exit\r')
        conn.close()
        return True

    def delete_snmp_host(self,ip_address,remHostIP,snmpKey,snmpCommunity,snmpPort):
        ''' Delete Remote SNMP Host
        
            Input: 
                ip_address        IP Address of switch
                
                remHostIP         IP Address of remote host
                       
                snmpKey           Acceptable values are traps/informs
                
                snmpCommunity     SNMP community
                
                snmpPort          Port on which traps are sent out.
        '''
        t = test.Test()
        conn = SSH2()
        conn.connect(ip_address)
        conn.login(Account("admin","adminadmin"))
        conn.execute('enable')
        conn.execute('conf t')
        if snmpKey == "traps" or snmpKey == "trap":
            snmpKey == "traps"
        else:
            snmpKey == "informs"
        input="no snmp-server host %s %s %s udp-port %s" % (str(remHostIP),str(snmpKey),str(snmpCommunity),str(snmpPort))
        conn.execute(input)
        conn.send('exit\r')
        conn.send('exit\r')
        conn.send('exit\r')
        conn.close()
        return True

    def enable_snmp(self,ip_address):
        ''' Enable SNMP Server.
        
            Input: 
                ip_address        IP Address of switch
        '''
        t = test.Test()
        conn = SSH2()
        conn.connect(ip_address)
        conn.login(Account("admin","adminadmin"))
        conn.execute('enable')
        conn.execute('conf t')
        conn.execute("snmp-server enable")
        conn.send('exit\r')
        conn.send('exit\r')
        conn.send('exit\r')
        conn.close()
        return True

    def disable_switch_snmp(self,ip_address):
        ''' Disable SNMP Server.
        
            Input: 
                ip_address        IP Address of switch
        '''
        t = test.Test()
        conn = SSH2()
        conn.connect(ip_address)
        conn.login(Account("admin","adminadmin"))
        conn.execute('enable')
        conn.execute('conf t')
        conn.execute("no snmp-server enable")
        conn.send('exit\r')
        conn.send('exit\r')
        conn.send('exit\r')
        conn.close()
        return True




############# PORT-CHANNEL SHOW COMMANDS##############################

    def verify_portchannel(self,ip_address,pcNumber):
        '''Verify portchannel shows as up
        
            Input:
                ip_address        IP Address of switch
                
                pcNumber           PortChannel number. Range is between 1 and 30
                
            Returns: true if interface is up, false otherwise
        '''
        t = test.Test()
        conn = SSH2()
        conn.connect(ip_address)
        conn.login(Account("admin","adminadmin"))
        conn.execute('enable')
        intf_name = "port-channel"+pcNumber
        input = "show interface " + intf_name
        conn.execute(input)
        helpers.log("Multiline is %s" % (string.split(conn.response, '\n')))
        lagNumber = 60 + int(pcNumber)
        input1=str(lagNumber) + "* " + intf_name
        if str(input1) in conn.response:
                return True
        else:
                return False
    
    def verify_portchannel_members(self,ip_address,pc_number,intf_name):
        '''Verify if portchannel contains the member interface that was configured 
        
            Input:
                ip_address        IP Address of switch
                
                pcNumber           PortChannel number. Range is between 1 and 30
                
                intf_name        Interface name of member interface
                
            Returns: true if member interface is present, false otherwise
        '''
        t = test.Test()
        conn = SSH2()
        conn.connect(ip_address)
        conn.login(Account("admin","adminadmin"))
        input = "show port-channel " + str(pc_number)
        conn.execute(input)
        content = string.split(conn.response, '\n')
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

    def verify_portchannel_member_state(self,ip_address,pc_number,intf_name):
        '''Verify if portchannel member interface is up
        
            Input:
                ip_address        IP Address of switch
                
                pcNumber           PortChannel number. Range is between 1 and 30
                
                intf_name        Interface name of member interface
                
            Returns: true if member interface is up, false otherwise
        '''
        t = test.Test()
        conn = SSH2()
        conn.connect(ip_address)
        conn.login(Account("admin","adminadmin"))
        input = "show port-channel " + str(pc_number)
        conn.execute(input)
        content = string.split(conn.response, '\n')
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

############# PORT-CHANNEL CONFIGURATION COMMANDS##############################

    def configure_portchannel(self,ip_address,pcNumber,portList,hashMode):
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
        t = test.Test()
        conn = SSH2()
        conn.connect(ip_address)
        conn.login(Account("admin","adminadmin"))
        conn.execute('enable')
        conn.execute('conf t')
        input_value = "port-channel " + str(pcNumber) + " interface-list " + str(portList) + "  hash " + str(hashMode)
        helpers.log("Input is %s" % input_value )
        try:
            conn.execute(input_value)
        except:
            return False            
        return True

    def unconfigure_portchannel(self,ip_address,pcNumber):
        '''Unconfigure port-channel
        
            Inputs:
                ip_address        IP Address of switch
                
                pcNumber           PortChannel number. Range is between 1 and 30
                
            Returns: True if configuration is a success or False otherwise
            
            Examples:
            
                | unconfigure portchannel | 10.192.75.7  |  1  |
        '''
        t = test.Test()
        conn = SSH2()
        conn.connect(ip_address)
        conn.login(Account("admin","adminadmin"))
        conn.execute('enable')
        conn.execute('conf t')
        input = "no port-channel " + str(pcNumber) + " "
        conn.execute(input)
        conn.send('logout\r')
        conn.close()
        return True