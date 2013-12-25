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
    
    def rest_set_switch_alias(self,switchDpid,switchAlias):
        t = test.Test()
        c = t.controller()
        url='%s/api/v1/data/controller/core/switch[dpid="%s"]' % (c.base_url, str(switchDpid))
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
        c = t.controller()
        c.http_port=8000
        url='http://%s:%s/rest/v1/model/snmp-server-config/?id=snmp' % (c.ip,c.http_port)
        c.rest.put(url, {"community": str(snmpCommunity)})
        helpers.test_log("Ouput: %s" % c.rest.result_json())
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
            return False
        else:
            helpers.test_log(c.rest.content_json())
            return True
        
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