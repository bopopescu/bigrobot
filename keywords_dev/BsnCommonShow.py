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

#Return controller version
    def rest_show_version(self):
        t = test.Test()
        c = t.controller()
        c.http_port = 8000
        url='http://%s:%s/rest/v1/system/version' % (c.ip,c.http_port)
        c.rest.get(url)
        content = c.rest.content()
        helpers.log("Output: %s" % content[0]['controller'])
        return content[0]['controller']

#Return Controller Role
    def rest_ha_role(self):
        t = test.Test()
        c = t.controller()
        url = '%s/system/ha/role'  % (c.base_url)
        c.rest.get(url)
        helpers.test_log("Ouput: %s" % c.rest.result_json())
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
        content = c.rest.content()
        return content['role']

#Return Controller ID
    def rest_controller_id(self):
        t = test.Test()
        c = t.controller()
        c.http_port = 8000
        url='http://%s:%s/rest/v1/system/controller' % (c.ip,c.http_port)
        c.rest.get(url)
        content = c.rest.content()
        helpers.log("Output: %s" % content['id'])
        return content['id']

#Show snmp
    def rest_snmp_show(self):
        t = test.Test()
        c = t.controller()
        c.http_port = 8000
        url='http://%s:%s/rest/v1/model/snmp-server-config/' % (c.ip,c.http_port)
        c.rest.get(url)
        content = c.rest.content()
        return content


