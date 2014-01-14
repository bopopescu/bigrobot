import autobot.helpers as helpers
import autobot.restclient as restclient
import autobot.test as test

def testing123():
    pass

class MyTest(object):

    def __init2__(self):
        t = test.Test()
        c = t.controller()
        
        url = '%s/api/v1/auth/login' % c.base_url
        result = c.rest.post(url, {"user":"admin", "password":"adminadmin"})
        session_cookie = result['content']['session_cookie']
        c.rest.set_session_cookie(session_cookie)
    
    def generate_data(self):
        return "MydataXXX"
    
    def save_data(self, data):
        helpers.log(data)
        return data
    
    def print_data(self, data):
        helpers.log(data)
        
    def test_scp(self):
        t = test.Test()
        c = t.controller()
        helpers.scp_put(c.ip, '/etc/hosts', '/tmp')

    def passing_kwargs_additions(self, arg_kw1=None, arg_kw2=None):
        helpers.log("arg_kw1: %s" % arg_kw1)
        helpers.log("arg_kw2: %s" % arg_kw2)
        
    def passing_kwargs(self, arg1, arg2, **kwargs):
        helpers.log("arg1: %s" % arg1)
        helpers.log("arg2: %s" % arg2)
        self.passing_kwargs_additions(**kwargs)
        
    def enable_help(self):
        t = test.Test()
        c = t.controller()
        
        #c.enable('help')
        #c.cli('show user')
        #c.config('show running-config')
        #c.cli('history')
        #c.bash('uptime')
        #c.config('whoami')
        #c.bash('sudo cat /etc/hosts')
        #.cli('whoami')
        #c.bash('ls /tmp')
        #c.config('whoami')
        #helpers.log("result: %s" % c.cli_result())
        #return c.cli_result()

        helpers.log("*** platform: %s" % c.platform())
