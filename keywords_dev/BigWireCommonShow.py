import autobot.helpers as helpers
import autobot.test as test


class BigWireCommonShow(object):

    def __init__(self):
        t = test.Test()
        c = t.controller()
        url = '%s/auth/login' % c.base_url
        helpers.log("url: %s" % url)
        result = c.rest.post(url, {"user":"admin", "password":"adminadmin"})
        helpers.log("result: %s" % helpers.to_json(result))
        session_cookie = result['content']['session_cookie']
        c.rest.set_session_cookie(session_cookie)

# Execute command "show bigwire summary", "show bigwire datacenter", "show bigwire pseudowire" or "show bigwire tenant"
    def rest_show_bigwire_command(self,bwKey):
        t = test.Test()
        c = t.controller()
        c.http_port=8082
        if bwKey == "datacenter":
            bwKeyword = "datacenter-info" # "show bigwire summary"
        elif bwKey == "pseudowire":
            bwKeyword = "pseudowire-info" #"show bigwire pseudowire"
        elif bwKey == "tenant":
            bwKeyword = "tenant-info" #"show bigwire tenant"
        else :                      
            bwKeyword = "info"      # "show bigwire summary"        
        url = 'http://%s:%s/api/v1/data/controller/applications/bigwire/%s' % (c.ip, c.http_port,str(bwKeyword))
        c.rest.get(url)
        helpers.test_log("Ouput: %s" % c.rest.result_json())
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
        content = c.rest.content()
        return content