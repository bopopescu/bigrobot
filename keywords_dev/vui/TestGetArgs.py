import autobot.helpers as helpers
import autobot.restclient as restclient
import autobot.test as test

class TestGetArgs(object):

    def __init__(self):
        t = test.Test()
        c = t.controller()
        
        url = '%s/api/v1/auth/login' % c.base_url
        result = c.rest.post(url, {"user":"admin", "password":"adminadmin"})
        session_cookie = result['content']['session_cookie']
        c.rest.set_session_cookie(session_cookie)
    
    def test_args(self,
                  arg1,
                  arg2=222,
                  arg3=333,
                  arg4=444,
                  arg5=None,
                  arg6=True,
                  arg7=False,
                  arg8=890,
                  arg9=None,
                  arg10=None,
                  arg11=None,
                  arg12=None):
        args = helpers.get_args(self.test_args)
        helpers.prettify_log("args:", args)
        
        #for key in args:
        #    helpers.log('key:%s, local()[%s]=%s <= args[%s]=%s'
        #                % (key, key, locals()[key], key, args[key]))
        #    locals()[key] = args[key]
        
        helpers.prettify_log("locals():", locals())
        return args
    
    def test_args2(self):
        args = self.test_args(arg1=1000)
        helpers.prettify_log("args:", args)
