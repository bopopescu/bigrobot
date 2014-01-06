import autobot.helpers as helpers
import autobot.test as test
from Exscript.protocols import SSH2
from Exscript import Account, Host


class BsnCommon(object):
    
    def __init__(self):
        t = test.Test()
        c = t.controller()
        url = '%s/auth/login' % c.base_url
        helpers.log("url: %s" % url)
        result = c.rest.post(url, {"user":"admin", "password":"adminadmin"})
        helpers.log("result: %s" % helpers.to_json(result))
        session_cookie = result['content']['session_cookie']
        c.rest.set_session_cookie(session_cookie)

#######################################################
# All Common Controller Show Commands Go Here:
#######################################################
#Generic Sleep Function
    def sleepnow(self,intTime):
        '''Sleep for integer time.
        
           Input: time in seconds
        '''
        helpers.sleep(float(intTime))
        
    def rest_is_c1_master_controller(self):
        '''Returns True if c1 (defined in .topo file) is Master, False otherwise
        '''
        t = test.Test()
        try:
            t.controller('c2')
        except:
            helpers.log('C1 is MASTER')
            return True
        else:
            c1 = t.controller('c1')
            c2 = t.controller('c2')
            url0 = 'http://%s:8000/rest/v1/system/ha/role'  % (c1.ip)
            c1.rest.get(url0)
            content1 = c1.rest.content()
            c1role = content1['role']
            url0 = 'http://%s:8000/rest/v1/system/ha/role'  % (c2.ip)
            c2.rest.get(url0)
            content2 = c2.rest.content()
            c2role = content2['role']
            if c1role =="MASTER":
                helpers.log('C1 is MASTER')
                return True
            else:
                helpers.log('C2 is MASTER')
                return False
        
    def rest_show_version(self):
        '''Return version of controller s/w
        '''
        t = test.Test()
        if(self.rest_is_c1_master_controller()):
            c = t.controller('c1')
            c.http_port=8000
        else:
            c = t.controller('c2')
            c.http_port=8000
        url='http://%s:%s/rest/v1/system/version' % (c.ip,c.http_port)
        c.rest.get(url)
        content = c.rest.content()
        helpers.log("Output: %s" % content[0]['controller'])
        return content[0]['controller']

    def rest_ha_role(self):
        '''Return Current Controller Role viz. Master/Slave
        
            Input: N/A
            
            Returns: Current Controller Role viz. Master/Slave
        '''
        t = test.Test()
        if(self.rest_is_c1_master_controller()):
            c = t.controller('c1')
            c.http_port=8000
        else:
            c = t.controller('c2')
            c.http_port=8000
        url = 'http://%s:%s/system/ha/role'  % (c.ip,c.http_port)
        c.rest.get(url)
        helpers.test_log("Ouput: %s" % c.rest.result_json())
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
        content = c.rest.content()
        return content['role']

    def rest_controller_id(self):
        '''Return Current Controller ID
        
            Input: N/A
            
            Returns: Return Current Controller ID
        '''
        t = test.Test()
        if(self.rest_is_c1_master_controller()):
            c = t.controller('c1')
            c.http_port=8000
        else:
            c = t.controller('c2')
            c.http_port=8000
        url='http://%s:%s/rest/v1/system/controller' % (c.ip,c.http_port)
        c.rest.get(url)
        content = c.rest.content()
        helpers.log("Output: %s" % content['id'])
        return content['id']

    def rest_verify_dict_key(self,content,index,key):
        ''' Given a dictionary, return the value for a particular key
        
            Input:Dictionary, index and required key.
            
            Return Value:  return the value for a particular key
        '''
        return content[int(index)][str(key)]
    
    def rest_show_switch(self):
        '''Return dictionary containing DPID,IP Addresses for every switch connected to current controller
        
            Input: N/A
            
            Returns: Dictionary of Switch DPID and IP Addresses
        '''
        t = test.Test()
        if(self.rest_is_c1_master_controller()):
            c = t.controller('c1')
            c.http_port=8082
        else:
            c = t.controller('c2')
            c.http_port=8082
        url='http://%s:%s/api/v1/data/controller/core/switch' % (c.ip,c.http_port)
        c.rest.get(url)
        content = c.rest.content()
        switchDict ={}
        for x in range (0,len(content)):
            helpers.log("For x = %s dpid is %s" % (str(x),content[x]['dpid']))
            switchDict[str(content[x]['inet-address']['ip'])] = str(content[x]['dpid'])
        return switchDict

    def return_switch_dpid(self,switchDict,ipAddr):
            '''Return DPID of switch, when dictionary from o/p of `rest show switch` and IP Address is provided
            
               Input: 
                   switchDict    dictionary of switch
                   ipAddr        IP Address of Switch
                
               Return: Switch IP Address
            '''
            return switchDict[str(ipAddr)]


    def return_switch_interface_mac(self,switchDpid,interfaceName):
        '''Return the MAC/Hardware Address of a given interface
        
            Input: 
                `switchDpid`       DPID of the Switch
                `interfaceName`    Interface Name e.g. ethernet13
            
            Returns: Hardware/MAC Address of Interface
        '''
        t=test.Test()
        if(self.rest_is_c1_master_controller()):
            c = t.controller('c1')
            c.http_port=8082
        else:
            c = t.controller('c2')
            c.http_port=8082
        url='http://%s:%s/api/v1/data/controller/core/switch[interface/name="%s"][dpid="%s"]?select=interface[name="%s"]' %(c.ip,c.http_port,interfaceName,switchDpid,interfaceName)
        c.rest.get(url)
        helpers.test_log("Ouput: %s" % c.rest.result_json())
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
        content = c.rest.content()
        return content[0]['interface'][0]['hardware-address']
    
    def restart_process_controller(self,process_name,controllerRole):
        '''Restart a process on controller
        
            Input:
               processName        Name of process to be restarted
               controllerRole        Where to execute the command. Accepted values are `Master` and `Slave`
           
           Return Value:  True if the configuration is successful, false otherwise 
        '''
        t=test.Test()
        if(self.btc.rest_is_c1_master_controller() and controllerRole=='Master' ) :
            c = t.controller('c1')
        elif (self.btc.rest_is_c1_master_controller() and controllerRole=='Slave' ):
            c = t.controller('c2')
        elif (not self.btc.rest_is_c1_master_controller() and controllerRole=='Master'):
            c = t.controller('c2')
        else:
            c = t.controller('c1')
        conn = SSH2()
        conn.connect(c.ip)
        conn.login(Account("admin","adminadmin"))
        conn.execute('enable')
        conn.execute('debug bash')
        input='service ' + str(process_name) +  ' restart'
        conn.execute(input)
        conn.send('logout\r')
        conn.send('logout\r')
        conn.close()
        return True         

    def execute_controller_command_return_output(self,input,controllerRole):
        '''Execute a generic command on the controller and return output.
        
            Input:
                controllerRole        Where to execute the command. Accepted values are `Master` and `Slave`
                input            Command to be executed on switch
                
            Return Value: Output from command execution
        '''
        t=test.Test()
        if(self.btc.rest_is_c1_master_controller() and controllerRole=='Master' ) :
            c = t.controller('c1')
        elif (self.btc.rest_is_c1_master_controller() and controllerRole=='Slave' ):
            c = t.controller('c2')            
        elif (not self.btc.rest_is_c1_master_controller() and controllerRole=='Master'):
            c = t.controller('c2')
        else:
            c = t.controller('c1')
        conn = SSH2()
        conn.connect(c.ip)
        conn.login(Account("admin","adminadmin"))
        conn.execute('enable')
        conn.execute('debug bash')
        conn.execute(input)
        output = conn.response
        conn.send('logout\r')
        conn.send('logout\r')
        conn.close()
        return output

    def return_master_slave_ip_address(self):
        '''Returns master and slave IP addresses as a dictionary
        '''
        t=test.Test()
        ip_address_list={}
        try:
            t.controller('c2')
        except:
            return {'Master':str(t.controller('c1').ip)}
        else:
            if(self.btc.rest_is_c1_master_controller()):
                ip_address_list={'Master':str(t.controller('c1').ip), 'Slave':str(t.controller('c2').ip)}
                return (ip_address_list)
            else:
                ip_address_list={'Master':str(t.controller('c2').ip), 'Slave':str(t.controller('c1').ip)}
                return (ip_address_list)

########################################################
# All Common Controller Verification Commands Go Here:
########################################################

    def verify_interface_is_up(self,switchDpid,interfaceName):
        '''Verify if a given interface on a given switch is up
        
            Input: 
                `switchDpid`       DPID of the Switch
                `interfaceName`    Interface Name e.g. ethernet13
            
            Returns: True if the interface is up, false otherwise
        '''
        t=test.Test()
        if(self.rest_is_c1_master_controller()):
            c = t.controller('c1')
            c.http_port=8082
        else:
            c = t.controller('c2')
            c.http_port=8082
        url='http://%s:%s/api/v1/data/controller/core/switch[interface/name="%s"][dpid="%s"]?select=interface[name="%s"]' %(c.ip,c.http_port,interfaceName,switchDpid,interfaceName)
        c.rest.get(url)
        helpers.test_log("Ouput: %s" % c.rest.result_json())
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
        content = c.rest.content()
        if (content[0]['interface'][0]['state-flags'] == 0):
                return True
        else:
                return False

########################################################
# All Common Controller Configuration Commands Go Here:
########################################################
#   Objective: Set Switch alias via command "switch-alias <switch_alias>"
#   Input: Switch DPID and Switch Alias
#   Return Value:  True/False
    def rest_set_switch_alias(self,switchDpid,switchAlias):
        '''Set Switch alias via command "switch-alias <switch_alias>"
        
            Input:
                `switchDpid`        DPID of switch
                `switchAlias`        Desired alias for switch
            
            Return: true if configuration is successful, false otherwise
        '''
        t = test.Test()
        if(self.rest_is_c1_master_controller()):
            c = t.controller('c1')
            c.http_port=8082
        else:
            c = t.controller('c2')
            c.http_port=8082
        url='http://%s:%s/api/v1/data/controller/core/switch[dpid="%s"]' % (c.ip,c.http_port,str(switchDpid))
        c.rest.patch(url, {"alias": str(switchAlias)})
        helpers.test_log("Ouput: %s" % c.rest.result_json())
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
            return False
        else:
            helpers.test_log(c.rest.content_json())
            return True

    def rest_execute_ha_failover(self):
        '''Execute HA failover from master controller
        '''
        t = test.Test()
        if(self.rest_is_c1_master_controller()):
            c = t.controller('c1')
            c.http_port=8000
        else:
            c = t.controller('c2')
            c.http_port=8000
        url1='http://%s:%s/rest/v1/system/ha/failback' % (c.ip,c.http_port)
        helpers.test_log(url1)
        c.rest.put(url1, {})
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
            return False
        else:
            helpers.test_log(c.rest.content_json())
            return True

#########################################################
# All Common Controller Platform related Commands Go Here
#########################################################

##NTP

############### NTP SHOW COMMANDS ########################

############### NTP CONFIG COMMANDS ########################

    def rest_configure_ntp(self,ntp_server):
        '''Configure NTP server
        
            Inputs:
                ntp_server: Name of NTP server 
            
            Returns: True if configuration is successful, false otherwise
        '''
        t = test.Test()
        if(self.rest_is_c1_master_controller()):
            c = t.controller('c1')
            c.http_port=8000
        else:
            c = t.controller('c2')
            c.http_port=8000
        url='http://%s:%s/rest/v1/model/ntp-server/' % (c.ip,c.http_port)
        c.rest.put(url,  {"enabled": True, "server": str(ntp_server)})
        helpers.test_log("Ouput: %s" % c.rest.result_json())
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
            return False
        else:
            helpers.test_log(c.rest.content_json())
            return True

    def rest_delete_ntp(self,ntp_server):
        '''Delete NTP server
        
            Inputs:
                ntp_server: Name of NTP server 
            
            Returns: True if configuration is successful, false otherwise
        '''
        t = test.Test()
        if(self.rest_is_c1_master_controller()):
            c = t.controller('c1')
            c.http_port=8000
        else:
            c = t.controller('c2')
            c.http_port=8000
        url='http://%s:%s/rest/v1/model/ntp-server/?enabled=True&server=%s' % (c.ip,c.http_port,str(ntp_server))
        c.rest.delete(url,  {})
        helpers.test_log("Ouput: %s" % c.rest.result_json())
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
            return False
        else:
            helpers.test_log(c.rest.content_json())
            return True      

##SNMP##

############### SNMP SHOW COMMANDS ########################

    def rest_snmp_show(self):
        '''Execute CLI Command "show snmp"
        
            Input: N/A
            
            Returns: dictionary of SNMP related values
        '''
        t = test.Test()
        if(self.rest_is_c1_master_controller()):
            c = t.controller('c1')
            c.http_port=8000
        else:
            c = t.controller('c2')
            c.http_port=8000
        url='http://%s:%s/rest/v1/model/snmp-server-config/' % (c.ip,c.http_port)
        c.rest.get(url)
        content = c.rest.content()
        helpers.log("Output: %s" % content)
        return content

    def rest_snmp_get(self,snmpCommunity,snmpOID):
        '''Execute SNMP Walk from local machine for a particular SNMP OID
        
            Input: SNMP Community and OID
            
            Return Value:  return the SNMP Walk O/P
        '''
        t = test.Test()
        c = t.controller()
        url="/usr/bin/snmpwalk -v2c -c %s %s %s" % (str(snmpCommunity),c.ip,str(snmpOID))
        returnVal = subprocess.Popen([url], stdout=subprocess.PIPE, shell=True)
        (out, err) = returnVal.communicate()
        helpers.log("URL: %s Output: %s" % (url, out))
        return out
    

    def rest_snmp_getnext(self,snmpCommunity,snmpOID):
        '''Execute snmpgetnext from local machine for a particular SNMP OID
        
            Input: SNMP Community and OID
            
            Return Value:  return the SNMP Walk O/P
        '''
        t = test.Test()
        c = t.controller()
        url="/usr/bin/snmpgetnext -v2c -c %s %s %s" % (str(snmpCommunity),c.ip,str(snmpOID))
        returnVal = subprocess.Popen([url], stdout=subprocess.PIPE, shell=True)
        (out, err) = returnVal.communicate()
        helpers.log("URL: %s Output: %s" % (url, out))
        return out
    

    def rest_snmp_cmd(self,snmp_cmd,snmpOptions,snmpCommunity,snmpOID):
        '''Execute a generic snmp command from local machine for a particular SNMP OID
        
            Input: 
                `snmp_cmd`        SNMP Command (snmpbulkget/snmpbulkwalk)
                `snmpOptions`     SNMP Command options
                `snmpCommunity`   SNMP Community
                `snmpOID`         SNMP OID to perform walk on
            
            Return Value:  return the SNMP Walk O/P
        '''
        t = test.Test()
        c = t.controller()
        if snmpOptions == "None" or snmpOptions == "none":
                snmpOptions =" "
        url="/usr/bin/%s -v2c %s -c %s %s %s" % (str(snmp_cmd),str(snmpOptions),str(snmpCommunity),c.ip,str(snmpOID))
        returnVal = subprocess.Popen([url], stdout=subprocess.PIPE, shell=True)
        (out, err) = returnVal.communicate()
        helpers.log("URL: %s Output: %s" % (url, out))
        return out
    
############### SNMP CONFIGURATION COMMANDS ########################
     
    def rest_set_snmp_server_community(self,snmpCommunity):
        '''Set SNMP Community String. Similar to CLI command "snmp-server community ro public"
        
           Input: `snmpCommunity`    SNMP Community name
           
           Return Value:  True if the configuration is successful, false otherwise 
        '''
        t = test.Test()
        if(self.rest_is_c1_master_controller()):
            c = t.controller('c1')
            c.http_port=8000
        else:
            c = t.controller('c2')
            c.http_port=8000
        url='http://%s:%s/rest/v1/model/snmp-server-config/' % (c.ip,c.http_port)
        c.rest.put(url,  {"id": "snmp", "community": str(snmpCommunity)})
        helpers.test_log("Ouput: %s" % c.rest.result_json())
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
            return False
        else:
            helpers.test_log(c.rest.content_json())
            return True
                 
    def rest_set_snmp_server_contact(self,snmpContact):
        '''Set SNMP Contact. Similar to CLI command "snmp-server contact 'Animesh Patcha'"
        
           Input: `snmpContact`    SNMP Contact Name
           
           Return Value:  True if the configuration is successful, false otherwise 
        '''
        t = test.Test()
        if(self.rest_is_c1_master_controller()):
            c = t.controller('c1')
            c.http_port=8000
        else:
            c = t.controller('c2')
            c.http_port=8000
        url='http://%s:%s/rest/v1/model/snmp-server-config/?id=snmp' % (c.ip,c.http_port)
        c.rest.put(url, {"contact": str(snmpContact)})
        helpers.test_log("Ouput: %s" % c.rest.result_json())
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
            return False
        else:
            helpers.test_log(c.rest.content_json())
            return True

    def rest_set_snmp_server_location(self,snmpLocation):
        '''Set SNMP Location. Similar to CLI command "snmp-server location 'Mountain View'"
        
           Input: `snmpContact`    SNMP Location Name
           
           Return Value:  True if the configuration is successful, false otherwise 
        '''
        t = test.Test()
        if(self.rest_is_c1_master_controller()):
            c = t.controller('c1')
            c.http_port=8000
        else:
            c = t.controller('c2')
            c.http_port=8000
        url='http://%s:%s/rest/v1/model/snmp-server-config/?id=snmp' % (c.ip,c.http_port)
        c.rest.put(url, {"location": str(snmpLocation)})
        helpers.test_log("Ouput: %s" % c.rest.result_json())
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
            return False
        else:
            helpers.test_log(c.rest.content_json())
            return True

    def rest_set_snmp_server_enable(self):
        '''Enable SNMP Server. Similar to cli command "snmp-server enable"
            
           Input: N/A
           
           Return Value:  True if the configuration is successful, false otherwise 
        '''
        t = test.Test()
        if(self.rest_is_c1_master_controller()):
            c = t.controller('c1')
            c.http_port=8000
        else:
            c = t.controller('c2')
            c.http_port=8000
        url='http://%s:%s/rest/v1/model/snmp-server-config/?id=snmp' % (c.ip,c.http_port)
        c.rest.put(url, {"server-enable": True})
        helpers.test_log("Ouput: %s" % c.rest.result_json())
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
            return False
        else:
            helpers.test_log(c.rest.content_json())
            return True
  
    def rest_set_snmp_trapserver(self,trapIP,trapPort):
        '''Configure SNMP Trap Server. Similar to cli command ""snmp-server trap server 10.192.3.22 161"
            
           Input: 
               `trapIP`    SNMP Trap Server IP Address
               
               `trapPort`  SNMP Trap Server Port Number
           
           Return Value:  True if the configuration is successful, false otherwise 
        '''
        t = test.Test()
        if(self.rest_is_c1_master_controller()):
            c = t.controller('c1')
            c.http_port=8000
        else:
            c = t.controller('c2')
            c.http_port=8000
        url='http://%s:%s/rest/v1/model/snmp-server-config/?id=snmp' % (c.ip,c.http_port)
        c.rest.put(url, {"trap-enable": True, "trap-server": str(trapIP), "trap-port": str(trapPort)})
        helpers.test_log("Ouput: %s" % c.rest.result_json())
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
            return False
        else:
            helpers.test_log(c.rest.content_json())
            return True

#   Objective: Enable SNMP-TrapServer. Similar to CLI command "snmp-server trap enable"
#   Input: N/A
#   Return Value:  True/False        
    def rest_enable_snmp_trapserver(self):
        '''Enable SNMP Trap Server. Similar to cli command "snmp-server trap enable"
            
           Input: N/A
           
           Return Value:  True if the configuration is successful, false otherwise 
        '''
        t = test.Test()
        if(self.rest_is_c1_master_controller()):
            c = t.controller('c1')
            c.http_port=8000
        else:
            c = t.controller('c2')
            c.http_port=8000
        url='http://%s:%s/rest/v1/model/snmp-server-config/?id=snmp' % (c.ip,c.http_port)
        c.rest.put(url, {"trap-enable": True, "id": "snmp"})
        helpers.test_log("Ouput: %s" % c.rest.result_json())
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
            return False
        else:
            helpers.test_log(c.rest.content_json())
            return True

#   Objective: Modify any SNMP Key. Allows you to change community string, contact info string and/or location string
#   Input: SNMP Key, SNMP Value  for example  SNMP Key can be community, and SNMP Value can be bigswitch
#   Return Value:  True/False     
    def rest_modify_snmp_key(self,snmpKey,snmpValue):
        '''Modify any SNMP Key. Allows you to change community string, contact info string and/or location string
        
            Input:
                `snmpKey`    SNMP Key to be changed.  for example  SNMP Key can be community, and SNMP Value can be bigswitc
                `snmpValue`  New value that will take effect.
           
           Return Value:  True if the configuration is successful, false otherwise 
        '''
        t = test.Test()
        if(self.rest_is_c1_master_controller()):
            c = t.controller('c1')
            c.http_port=8000
        else:
            c = t.controller('c2')
            c.http_port=8000
        url='http://%s:%s/rest/v1/model/snmp-server-config/?id=snmp' % (c.ip,c.http_port)
        if snmpValue == "null":
                snmpValue1=None
        else:
                snmpValue1=str(snmpValue)
    
        helpers.test_log("snmpValue1: %s" % snmpValue1)
        c.rest.put(url, { str(snmpKey) : snmpValue1})
        helpers.test_log("Ouput: %s" % c.rest.result_json())
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
            return False
        else:
            helpers.test_log(c.rest.content_json())
            return True

#   Objective: Modify Firewall to allow port 161 for SNMP Requests from external hosts
#   Input: Controller ID
#   Return Value:  True/False         
    def rest_firewall_allow_snmp(self,controllerID):
        '''Modify Firewall to allow port 161 for SNMP Requests from external hosts
            
           Input: N/A
           
           Return Value:  True if the configuration is successful, false otherwise 
        '''
        t = test.Test()
        if(self.rest_is_c1_master_controller()):
            c = t.controller('c1')
            c.http_port=8000
        else:
            c = t.controller('c2')
            c.http_port=8000
        url='http://%s:%s/rest/v1/model/firewall-rule/' % (c.ip,c.http_port)
        cInterface = "%s|Ethernet|0" %(str(controllerID))
        c.rest.put(url,{"interface": str(cInterface), "vrrp-ip": "", "port": 161, "src-ip": "", "proto": "udp"})
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
            return False
        else:
            helpers.test_log(c.rest.content_json())
            return True

#   Objective: Delete SNMP. Similar to "no snmp-server enable"
#   Input: N/A
#   Return Value:  True/False    
    def rest_delete_snmp_trapserver(self,trapPort):
        '''Delete SNMP trapserver. Similar to "no snmp-server trap server 10.192.3.22 161"
            
           Input: N/A
           
           Return Value:  True if the configuration is successful, false otherwise 
        '''
        t = test.Test()
        if(self.rest_is_c1_master_controller()):
            c = t.controller('c1')
            c.http_port=8000
        else:
            c = t.controller('c2')
            c.http_port=8000
        url1='http://%s:%s/rest/v1/model/snmp-server-config/?id=snmp' % (c.ip,c.http_port)
        helpers.test_log(url1)
        c.rest.put(url1, {"trap-enable": False, "trap-server": "", "trap-port": int(trapPort)})
        return True

#   Objective: Delete SNMP. Similar to "no snmp-server enable"
#   Input: N/A
#   Return Value:  True/False    
    def rest_delete_snmp(self):
        '''Delete SNMP. Similar to "no snmp-server enable"
            
           Input: N/A
           
           Return Value:  True if the configuration is successful, false otherwise 
        '''
        t = test.Test()
        if(self.rest_is_c1_master_controller()):
            c = t.controller('c1')
            c.http_port=8000
        else:
            c = t.controller('c2')
            c.http_port=8000
        url1='http://%s:%s/rest/v1/model/snmp-server-config/?id=snmp' % (c.ip,c.http_port)
        helpers.test_log(url1)
        c.rest.delete(url1, {})
        return True