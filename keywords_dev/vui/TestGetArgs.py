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

        helpers.log("locals(): %s" % helpers.prettify(locals()))

        local_var = 100
        print("local_var (1): %s" % local_var)
        
        locals()['local_var'] = 123
        print("local_var (2): %s" % local_var)

        #arg1 = 8000
        #print("arg1 (1): %s" % arg1)

        #locals()['arg1'] = 123
        #print("arg1 (2): %s" % arg1)
        
        helpers.log("locals(): %s" % helpers.prettify(locals()))
        
        #locals().pop("arg1", None)
        #locals()['arg1'] = 'XXXX'
        #print("arg1: %s" % locals()['arg1'])        

            
    def test_args2(self):
        args = self.test_args(arg1=1000)
        helpers.prettify_log("args:", args)
