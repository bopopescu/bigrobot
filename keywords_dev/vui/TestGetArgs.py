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
        
        locals()['XXX'] = 123
        locals().pop("arg1", None)
        locals()['arg1'] = 8888
        locals()['arg111'] = 8888
        import pprint
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(locals())
        
        args = helpers.get_args(self.test_args)
        helpers.prettify_log("args:", args)
        
        
        helpers.prettify_log("locals():", locals())
        
        vars()['arg1'] = 9999
        helpers.prettify_log("vars():", vars())
        
        helpers.log("arg1: %s" % arg1)
        for key in args:
            helpers.log('key:%s, local()[%s]=%s <= args[%s]=%s'
                        % (key, key, locals()[key], key, args[key]))
            if key in locals():
                helpers.log("Found key('%s') in locals()" % key)
            else:
                helpers.log("Key('%s' not found in locals()" % key)
            #locals()[key] = args[key]
            locals()[key] = 1
            
        return args
    
    def test_args2(self):
        args = self.test_args(arg1=1000)
        helpers.prettify_log("args:", args)
