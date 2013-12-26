import autobot.helpers as helpers
import autobot.test as test


class BsnCommonConfig(object):

    def __init__(self):
        t = test.Test()
        c = t.controller()

        url = '%s/auth/login' % c.base_url
        
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
        c = t.controller()
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
        
#   Objective: Set SNMP Community String. Similar to CLI command "snmp-server community ro public"
#   Input: SNMP Community name
#   Return Value:  True/False       
    def rest_set_snmp_server_community(self,snmpCommunity):
        t = test.Test()
        c = t.controller()
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
        c = t.controller()
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
        c = t.controller()
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
        c = t.controller()
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
        c = t.controller()
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
        c = t.controller()
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
        c = t.controller()
        c.http_port=8000
        url='http://%s:%s/rest/v1/model/snmp-server-config/?id=snmp' % (c.ip,c.http_port)
        c.rest.put(url, { str(snmpKey) : str(snmpValue)})
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
        c = t.controller()
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
        c = t.controller()
        c.http_port=8000
        url1='http://%s:%s/rest/v1/model/snmp-server-config/?id=snmp' % (c.ip,c.http_port)
        helpers.test_log(url1)
        retVal = c.rest.delete(url1, {})
        helpers.test_log(retVal)
        return True
        