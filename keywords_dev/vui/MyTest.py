import autobot.helpers as helpers
import autobot.restclient as restclient
import autobot.test as test

def testing123():
    pass

class MyTest(object):

    def __init__(self):
        t = test.Test()
        c = t.controller()
        
        url = '%s/api/v1/auth/login' % c.base_url
        result = c.rest.post(url, {"user":"admin", "password":"adminadmin"})
        session_cookie = result['content']['session_cookie']
        c.rest.set_session_cookie(session_cookie)
    
    def test_args2(self,
                   arg1,   # Don't try this at home
                   arg2=222,  # Is this too much rope
                   arg3=333,  # definitely too many notes
                   arg4=444,
                   arg5=None,
                   arg6=True,
                   arg7=False,
                   arg8=890,
                   arg9=None,
                   arg10=None,
                   arg11=None,
                   arg12=None):
        args = helpers.get_args(self.test_args2)
        helpers.prettify_log("args:", args)
        
        helpers.log("arg1: %s" % arg1)
        helpers.log("args['arg1']: %s" % args['arg1'])

        helpers.log("arg2: %s" % arg2)
        helpers.log("args['arg2']: %s" % args['arg2'])

        helpers.log("arg3: %s" % arg3)
        helpers.log("args['arg3']: %s" % args['arg3'])

        helpers.log("arg8: %s" % arg8)
        helpers.log("args['arg8']: %s" % args['arg8'])
        
        helpers.log("arg10: %s" % arg10)
        helpers.log("args['arg10']: %s" % args['arg10'])

        helpers.log("arg12: %s" % arg12)
        helpers.log("args['arg12']: %s" % args['arg12'])

    def test_args(self, **kwargs):
        abc, xyz = helpers.get_args(['abc', 'xyz'])
        helpers.log("abc: %s" % abc)
        helpers.log("xyz: %s" % xyz)

    def call_test_args(self):
        #self.test_args(abc=1, xyz=True)
        self.test_args2(arg8=999, arg12=True)
        
    def test_scp(self):
        t = test.Test()
        c = t.controller()
        helpers.scp_put(c.ip, '/etc/hosts', '/tmp')
