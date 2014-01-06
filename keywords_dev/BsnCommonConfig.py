import autobot.helpers as helpers
import autobot.test as test
from Exscript.protocols import SSH2
from Exscript import Account, Host
from BigTapCommonShow import BigTapCommonShow

class BsnCommonConfig(object):

    def __init__(self):
        t = test.Test()
        self.btc=BigTapCommonShow()
        if(self.btc.rest_is_c1_master_controller()):
            c = t.controller('c1')
            c.http_port=8082
        else:
            c = t.controller('c2')
            c.http_port=8082

        url='http://%s:%s/auth/login' % (c.ip,c.http_port)
        
        helpers.log("url: %s" % url)
        result = c.rest.post(url, {"user":"admin", "password":"adminadmin"})

        helpers.log("result: %s" % helpers.to_json(result))

        session_cookie = result['content']['session_cookie']
        c.rest.set_session_cookie(session_cookie)

#   Objective: Set Switch alias via command "switch-alias <switch_alias>"
#   Input: Switch DPID and Switch Alias
#   Return Value:  True/False
    def rest_set_switch_alias(self,switchDpid,switchAlias):
        t = test.Test()
        if(self.btc.rest_is_c1_master_controller()):
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
        
     
    def rest_set_snmp_server_community(self,snmpCommunity):
        t = test.Test()
        if(self.btc.rest_is_c1_master_controller()):
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
        
#   Objective: Set SNMP Contact. Similar to CLI command "snmp-server contact 'Animesh Patcha'"
#   Input: SNMP Contact Info
#   Return Value:  True/False          
    def rest_set_snmp_server_contact(self,snmpContact):
        t = test.Test()
        if(self.btc.rest_is_c1_master_controller()):
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
        
#   Objective: Set SNMP Location. Similar to CLI command "snmp-server location 'Rack 10 Aisle 4'"
#   Input: SNMP Location Info
#   Return Value:  True/False
    def rest_set_snmp_server_location(self,snmpLocation):
        t = test.Test()
        if(self.btc.rest_is_c1_master_controller()):
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

#   Objective: Enable SNMP-Server. Similar to CLI command "snmp-server enable"
#   Input: N/A
#   Return Value:  True/False
    def rest_set_snmp_server_enable(self):
        t = test.Test()
        if(self.btc.rest_is_c1_master_controller()):
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

#   Objective: Set SNMP Trap Server. Similar to CLI command "snmp-server trap server 10.192.3.22 161"
#   Input: SNMP Trap Server IP Address, SNMP Trap Server Port Number
#   Return Value:  True/False   
    def rest_set_snmp_trapserver(self,trapIP,trapPort):
        t = test.Test()
        if(self.btc.rest_is_c1_master_controller()):
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
        t = test.Test()
        if(self.btc.rest_is_c1_master_controller()):
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
        t = test.Test()
        if(self.btc.rest_is_c1_master_controller()):
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
        t = test.Test()
        if(self.btc.rest_is_c1_master_controller()):
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
    def rest_delete_snmp(self):
        t = test.Test()
        if(self.btc.rest_is_c1_master_controller()):
            c = t.controller('c1')
            c.http_port=8000
        else:
            c = t.controller('c2')
            c.http_port=8000
        url1='http://%s:%s/rest/v1/model/snmp-server-config/?id=snmp' % (c.ip,c.http_port)
        helpers.test_log(url1)
        c.rest.delete(url1, {})
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
        if(self.btc.rest_is_c1_master_controller()):
            c = t.controller('c1')
            c.http_port=8000
        else:
            c = t.controller('c2')
            c.http_port=8000
        url1='http://%s:%s/rest/v1/model/snmp-server-config/?id=snmp' % (c.ip,c.http_port)
        helpers.test_log(url1)
        c.rest.put(url1, {"trap-enable": False, "trap-server": "", "trap-port": int(trapPort)})
        return True

    def rest_execute_ha_failover(self):
        t = test.Test()
        if(self.btc.rest_is_c1_master_controller()):
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

    def rest_configure_ntp(self,ntp_server):
        '''Configure NTP server
        
            Inputs:
                ntp_server: Name of NTP server 
            
            Returns: True if configuration is successful, false otherwise
        '''
        t = test.Test()
        if(self.btc.rest_is_c1_master_controller()):
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
        if(self.btc.rest_is_c1_master_controller()):
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


    def rest_configure_syslog(self,syslog_server,log_level):
        '''Configure Syslog server
        
            Inputs:
                syslog_server: Name of Syslog server 
                log_level    :  Logging Level, 0-9
            
            Returns: True if configuration is successful, false otherwise
        '''
        t = test.Test()
        try:
            t.controller('c2')
        except:
            c = t.controller('c1')
            c.http_port=8000
        else:
            if(self.btc.rest_is_c1_master_controller()):
                c = t.controller('c1')
                c.http_port=8000
            else:
                c = t.controller('c2')
                c.http_port=8000
        url='http://%s:%s/rest/v1/model/syslog-server/' % (c.ip,c.http_port)
        c.rest.put(url,  {"logging-enabled": True, "logging-server": str(syslog_server),"logging-level":int(log_level)})
        helpers.test_log("Ouput: %s" % c.rest.result_json())
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
            return False
        else:
            helpers.test_log(c.rest.content_json())
            return True

    def rest_delete_syslog(self,syslog_server,log_level):
        '''Delete Syslog server
        
            Inputs:
                syslog_server: Name of Syslog server 
                log_level    :  Logging Level, 0-9
            
            Returns: True if configuration is successful, false otherwise
        '''
        t = test.Test()
        try:
            t.controller('c2')
        except:
            c = t.controller('c1')
            c.http_port=8000
        else:
            if(self.btc.rest_is_c1_master_controller()):
                c = t.controller('c1')
                c.http_port=8000
            else:
                c = t.controller('c2')
                c.http_port=8000
        url='http://%s:%s/rest/v1/model/syslog-server/?logging-enabled=True&logging-server=%s&logging-level=%d' % (c.ip,c.http_port,str(syslog_server),int(log_level))
        c.rest.delete(url,  {})
        helpers.test_log("Ouput: %s" % c.rest.result_json())
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
            return False
        else:
            helpers.test_log(c.rest.content_json())
            return True

    def flap_eth0_controller(self,controllerRole):
        ''' Flap eth0 on Controller
        
            Input:
               controllerRole        Where to execute the command. Accepted values are `Master` and `Slave`
           
           Return Value:  True if the configuration is successful, false otherwise 
        '''
        t=test.Test()
        try:
            t.controller('c2')
        except:
            c = t.controller('c1')
            c.http_port=8000
        else:
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
        conn.execute('debug bash')
        conn.execute("echo '#!/bin/bash' > test.sh")
        conn.execute("echo 'sleep 15' >> test.sh")
        conn.execute("echo 'sudo ifconfig eth0 down' >> test.sh")
        conn.execute("echo 'sleep 10' >> test.sh")
        conn.execute("echo 'sudo ifconfig eth0 up' >> test.sh")
        conn.execute("echo 'sleep 10' >> test.sh")
        conn.execute("sh test.sh &")
        helpers.sleep(float(30))
        conn.send('exit\r')
        conn.close()
        return True