import autobot.helpers as helpers
import autobot.restclient as restclient
import autobot.test as test


class MyTest(object):

    def __init__(self):
        t = test.Test()
        c = t.controller()
        
        url = '%s/api/v1/auth/login' % c.base_url
        result = c.rest.post(url, {"user":"admin", "password":"adminadmin"})
        session_cookie = result['content']['session_cookie']
        c.rest.set_session_cookie(session_cookie)
        
    def test_scp(self):
        t = test.Test()
        c = t.controller()

        helpers.scp_put(c.ip, '/etc/hosts', '/tmp')
