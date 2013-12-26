import autobot.helpers as helpers
import autobot.test as test


class BigTapCommonShow(object):

    def __init__(self):
        t = test.Test()
        c = t.controller()
        url = '%s/auth/login' % c.base_url
        helpers.log("url: %s" % url)
        result = c.rest.post(url, {"user":"admin", "password":"adminadmin"})
        helpers.log("result: %s" % helpers.to_json(result))
        session_cookie = result['content']['session_cookie']
        c.rest.set_session_cookie(session_cookie)
        
        
    def rest_show_bigtap_policy(self, policyName,numFIntf,numDIntf):
        t = test.Test()
        c = t.controller()
        helpers.test_log("Input arguments: policy = %s" % policyName )
        url = '%s/api/v1/data/controller/applications/bigtap/view/policy[name="%s"]/info' % (c.base_url, policyName)
        c.rest.get(url)
        helpers.test_log("Ouput: %s" % c.rest.result_json())
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
        content = c.rest.content()
                
        if content[0]['name'] == str(policyName):
                helpers.test_log("Policy correctly reports policy name as : %s" % content[0]['name'])
        else:
                helpers.test_failure("Policy does not correctly report policy name  : %s" % content[0]['name'])                
                return False        
        if content[0]['config-status'] == "active and forwarding":
                helpers.test_log("Policy correctly reports config status as : %s" % content[0]['config-status'])
        else:
                helpers.test_failure("Policy does not correctly report detailed status as : %s" % content[0]['delivery-interface-count'])
                return False                
        if content[0]['delivery-interface-count'] == int(numDIntf) :
                helpers.test_log("Policy correctly reports number of delivery interfaces as : %s" % content[0]['delivery-interface-count'])
        else:
                helpers.test_failure("Policy does not correctly report number of delivery interfaces  : %s" % content[0]['delivery-interface-count'])                
                return False                
        if content[0]['filter-interface-count'] == int(numFIntf):
                helpers.test_log("Policy correctly reports number of filter interfaces as : %s" % content[0]['filter-interface-count'])
        else:
                helpers.test_failure("Policy does not correctly report number of filter interfaces  : %s" % content[0]['filter-interface-count'])                
                return False
            
        if content[0]['detailed-status'] == "installed to forward":
                helpers.test_log("Policy correctly reports detailed status as : %s" % content[0]['detailed-status'])
        else:
                helpers.test_failure("Policy does not correctly report detailed status as : %s" % content[0]['detailed-status'])
                return False
        return True

# Do a rest query and check if a particular key exists in the policy.
# index is the index of the dictionary.
# Values for method are info/rule/filter-interface/delivery-interface/service-interface/core-interface/failed-paths    
    def rest_check_policy_key(self,policyName,method,index,key):
        t = test.Test()
        c = t.controller()
        url = '%s/api/v1/data/controller/applications/bigtap/view/policy[name="%s"]/%s' % (c.base_url,str(policyName),str(method))
        c.rest.get(url)
        helpers.test_log("Ouput: %s" % c.rest.result_json())
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
        if(c.rest.content()):
            content = c.rest.content()
            return content[index][key]
        else :
            helpers.test_log("ERROR Policy %s does not exist. Error seen: %s" % (str(policyName),c.rest.result_json()))
            return False
        
# Return switch dpid given a switch alias
# Input: switch alias
# Output: switch dpid 
    def rest_show_switch_dpid(self,switchAlias):
        t = test.Test()
        c = t.controller()
        aliasExists=0
        url='%s/api/v1/data/controller/core/switch?select=alias'   % (c.base_url)
        c.rest.get(url)
        content = c.rest.content()
        for i in range(0,len(content)) :
                if content[i]['alias'] == str(switchAlias) :
                        switchDpid = content[i]['dpid']
                        aliasExists=1
        if(aliasExists):
            return switchDpid
        else:
            return False
        
# Return number of flows installed in full match table
# Input: switch dpid
# Output: Number of flows      
    def rest_show_switch_flow(self,switchDpid):
        t = test.Test()
        c = t.controller()
        url='%s/api/v1/data/controller/core/switch[dpid="%s"]?select=stats/table' % (c.base_url,str(switchDpid))
        c.rest.get(url)
        content = c.rest.content()
        helpers.log("Return value for number of flows is %s" % content[0]['stats']['table'][1]['active-count'])
        return content[0]['stats']['table'][1]['active-count']    




    