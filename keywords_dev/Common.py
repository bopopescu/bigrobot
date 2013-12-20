import autobot.helpers as helpers
import autobot.test as test
import re

class Common(object):

    def __init__(self):
        t = test.Test()
        c = t.controller()

        url = '%s/auth/login' % c.base_url
        result = c.rest.post(url, {"user":"admin", "password":"adminadmin"})
        session_cookie = result['content']['session_cookie']
        c.rest.set_session_cookie(session_cookie)
        
    def rest_show_version(self):
        t = test.Test()
        c = t.controller()
         
        url = '%s/rest/v1/system/version' % (c.base_url)
        c.rest.get(url)
        helpers.log("Output: %s" % c.rest.result_json())

        content_json = c.rest.content_json()
        helpers.log(content_json)
        
        content = c.rest.content()[0]
        helpers.log("content: %s" % content)
        
        output = content['controller']
        helpers.log(output)
        
        matchobj = re.match(r'.*Big Tap*', output)
        if matchobj:
            helpers.log("This is Big Tap controller")
            
        else:
            helpers.test_failure("this is not Big Tap controller")
            
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())

        return c.rest.content()
    
    
    def rest_show_user(self):
        t = test.Test()
        c = t.controller()
         
        url = '%s/api/v1/data/controller/core/aaa/group' % (c.base_url)
        c.rest.get(url)
        helpers.log("Output: %s" % c.rest.result_json())
    

        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())

        return c.rest.content()
    
    def rest_show_controller(self):
        t = test.Test()
        c = t.controller()
        #  TBD need to find the rest api 
        url = '%s/rest/v1/model/controller-node' % (c.base_url)
        c.rest.get(url)
        helpers.log("Output: %s" % c.rest.result_json())
    

        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())

        return c.rest.content()
    
    def rest_show_bigtap(self):
        t = test.Test()
        c = t.controller()
        #  TBD need to find the rest api 
        url = '%s/api/v1/data/controller/applications/bigtap/info' % (c.base_url)
        c.rest.get(url)
        helpers.log("Output: %s" % c.rest.result_json())
    

        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())

        return c.rest.content()
    
    
    
    