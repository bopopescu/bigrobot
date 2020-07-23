import autobot.helpers as helpers
import autobot.test as test


class BigTapCommonShow(object):

    def __init__(self):
        pass
    
    def rest_is_c1_main_controller(self):
        t = test.Test()
        try:
            t.controller('c2')
        except:
            helpers.log('C1 is MASTER')
            return True
        else:
            c1 = t.controller('c1')
            c2 = t.controller('c2')
            url0 = '/rest/v1/system/ha/role'
            c1.rest.get(url0)
            content1 = c1.rest.content()
            c1role = content1['role']
            url0 = '/rest/v1/system/ha/role'
            c2.rest.get(url0)
            content2 = c2.rest.content()
            c2role = content2['role']
            if c1role =="MASTER":
                helpers.log('C1 is MASTER')
                return True
            else:
                helpers.log('C2 is MASTER')
                return False

    def rest_show_bigtap_policy(self, policy_name,num_filter_intf,num_delivery_intf):
        '''Parse the output of cli command 'show bigtap policy <policy_name>'
        
        The first input item `policy_name` which is the name of the policy being parsed
        The second input item `num_filter_intf` is the number of configured Filter Interfaces in the policy
        The third input item `num_delivery_intf` is the number of configured Delivery Interfaces in the policy
        
        The policy returns True if and only if all the following conditions are True 
            a) Policy name is seen correctly in the output
            b) Config-Status is either "active and forwarding" or "active and rate measure"
            c) Type is "Configured"
            d) Runtime Status is "installed"
            e) Delivery interface count is num_delivery_intf
            f) Filter Interface count is num_filter_intf
            g) deltailed status is either "installed to forward" or "installed to measure rate"
        
        The function executes a REST GET for 
            http://<CONTROLLER_IP>:8082/api/v1/data/controller/applications/bigtap/view/policy[name="<POLICY_NAME>"]/info
        
        Return value is True/False
        '''
        try:
            t = test.Test()
            c= t.controller('main')
            url ='/api/v1/data/controller/applications/bigtap/view/policy[name="%s"]/info' % (policy_name)
            c.rest.get(url)
            if not c.rest.status_code_ok():
                helpers.test_failure(c.rest.error())
            content = c.rest.content()
        except:
            helpers.test_failure("Could not execute command")
            return False
        else:      
            if content[0]['name'] == str(policy_name):
                    helpers.test_log("Policy correctly reports policy name as : %s" % content[0]['name'])
            else:
                    helpers.test_failure("Policy does not correctly report policy name  : %s" % content[0]['name'])                
                    return False
                  
            if content[0]['config-status'] == "active and forwarding":
                    helpers.test_log("Policy correctly reports config status as : %s" % content[0]['config-status'])
            elif content[0]['config-status'] == "active and rate measure":
                    helpers.test_log("Policy correctly reports config status as : %s" % content[0]['config-status'])          
            else:
                    helpers.test_failure("Policy does not correctly report config status as : %s" % content[0]['config-status'])
                    return False
                  
            if content[0]['type'] == "Configured":
                    helpers.test_log("Policy correctly reports type as : %s" % content[0]['type'])         
            else:
                    helpers.test_failure("Policy does not correctly report type as : %s" % content[0]['type'])
                    return False
                  
            if content[0]['runtime-status'] == "installed":
                    helpers.test_log("Policy correctly reports runtime status as : %s" % content[0]['runtime-status'])         
            else:
                    helpers.test_failure("Policy does not correctly report runtime status as : %s" % content[0]['runtime-status'])
                    return False
                
            if content[0]['delivery-interface-count'] == int(num_delivery_intf) :
                    helpers.test_log("Policy correctly reports number of delivery interfaces as : %s" % content[0]['delivery-interface-count'])
            else:
                    helpers.test_failure("Policy does not correctly report number of delivery interfaces  : %s" % content[0]['delivery-interface-count'])                
                    return False
                          
            if content[0]['filter-interface-count'] == int(num_filter_intf):
                    helpers.test_log("Policy correctly reports number of filter interfaces as : %s" % content[0]['filter-interface-count'])
            else:
                    helpers.test_failure("Policy does not correctly report number of filter interfaces  : %s" % content[0]['filter-interface-count'])                
                    return False
                
            if content[0]['detailed-status'] == "installed to forward":
                    helpers.test_log("Policy correctly reports detailed status as : %s" % content[0]['detailed-status'])
            elif content[0]['detailed-status'] == "installed to measure rate":
                    helpers.test_log("Policy correctly reports detailed status as : %s" % content[0]['detailed-status'])
            else:
                    helpers.test_failure("Policy does not correctly report detailed status as : %s" % content[0]['detailed-status'])
                    return False
            return True

# Do a rest query and check if a particular key exists in the policy.
# index is the index of the dictionary.
# Values for method are info/rule/filter-interface/delivery-interface/service-interface/core-interface/failed-paths    
    def rest_check_policy_key(self,policy_name,method,index,key):
        try:
            t = test.Test()
        except:
            return False
        else:
            c= t.controller('main')
            try:
                url ='/api/v1/data/controller/applications/bigtap/view/policy[name="%s"]/%s' % (str(policy_name),str(method))
                c.rest.get(url)
            except:
                helpers.test_failure(c.rest.error())
                return False
            else:
                if(c.rest.content()):
                    content = c.rest.content()
                    return content[index][key]
                else :
                    helpers.test_log("ERROR Policy %s does not exist. Error seen: %s" % (str(policy_name),c.rest.result_json()))
                    helpers.test_failure(c.rest.error())
                    return False
        
# Return switch dpid given a switch alias
# Input: switch alias
# Output: switch dpid 
    def rest_get_switch_dpid(self,switch_alias):
        try:
            t = test.Test()
        except:
            return False
        else:
            c= t.controller('main')
            try:
                helpers.log("IP address is %s" % (c.ip))
                aliasExists=0
                url ='/api/v1/data/controller/core/switch?select=alias'
                c.rest.get(url)
            except:
                helpers.test_failure(c.rest.error())
                return False
            else:
                content = c.rest.content()
                for i in range(0,len(content)) :
                        if content[i]['alias'] == str(switch_alias) :
                                switch_dpid = content[i]['dpid']
                                aliasExists=1
                if(aliasExists):
                    return switch_dpid
                else:
                    return False
        
# Return number of flows installed in full match table
# Input: switch dpid
# Output: Number of flows      
    def rest_get_switch_flow(self,switch_dpid):
        try:
            t = test.Test()
        except:
            return False
        else:
            c= t.controller('main')
            try:
                url ='/api/v1/data/controller/core/switch[dpid="%s"]?select=stats/table' % (str(switch_dpid))
                c.rest.get(url)
            except:
                helpers.test_failure(c.rest.error())
                return False
            else:            
                content = c.rest.content()
                helpers.log("Return value for number of flows is %s" % content[0]['stats']['table'][1]['active-count'])
                return content[0]['stats']['table'][1]['active-count']    




    