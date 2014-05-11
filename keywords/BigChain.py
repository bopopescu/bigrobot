'''
###  WARNING !!!!!!!
###  This is where common code for BigChain will go in.
###
###  To commit new code, please contact the Library Owner:
###  Animesh Patcha (animesh.patcha@bigswitch.com)
###
###  DO NOT COMMIT CODE WITHOUT APPROVAL FROM LIBRARY OWNER
###
###  Last Updated: 03/11/2014
###
###  WARNING !!!!!!!
'''


import autobot.helpers as helpers
import autobot.test as test
import keywords.AppController as AppController
import json
import re

class BigChain(object):

    def __init__(self):
        pass

###################################################
# All BigChain CLI Commands Go Here:
###################################################

###################################################
# All BigChain REST Commands Go Here:
###################################################
    def rest_show_bigchain(self, desired_output="state", user="admin", password="adminadmin"):
        '''
            Objective:
                -- Return desired value after executing cli command "show bigchain"       
        '''
        try:
            t = test.Test()
            c = t.controller('master')
        except:
            helpers.test_failure("Could not execute command")
            return False
        else:
            url = '/api/v1/data/controller/applications/bigchain/info'
            if "admin" not in user:
                c_user = t.node_reconnect(node='master', user=str(user), password=password)
                c_user.rest.get(url)
                if not c_user.rest.status_code_ok():
                    helpers.test_failure(c_user.rest.error())
                content = c_user.rest.content()
                t.node_reconnect(node='master')
            else:
                c.rest.get(url)
                if not c.rest.status_code_ok():
                    helpers.test_failure(c.rest.error())
                content = c.rest.content()
            if desired_output is "max-delivery-bandwidth":
                return content['max-delivery-bandwidth-bps']
            elif desired_output is "max-filter-bandwidth":
                return content['max-filter-bandwidth-bps']

            elif desired_output is "post-service":
                return content['max-post-service-bandwidth-bps']

            elif desired_output is "pre-service":
                return content['max-pre-service-bandwidth-bps']

            elif desired_output is "active-chain-count":
                return content['num-active-chains']

            elif desired_output is "chain-count":
                return content['num-chains']

            elif desired_output is "service-count":
                return content['num-services']

            elif desired_output is "switch-count":
                return content['num-total-switches']

            elif desired_output is "total-delivery-traffic":
                return content['total-delivery-traffic-bps']

            elif desired_output is "total-filter-traffic":
                return content['total-filter-traffic-bps']

            elif desired_output is "total-post-service-traffic":
                return content['total-post-service-traffic-bps']

            elif desired_output is "total-pre-service-traffic":
                return content['total-pre-service-traffic-bps']

            elif desired_output is "uptime":
                return content['uptime']
            else:
                return content['state']

    def rest_add_a_chain(self, chain_name=None, user="admin", password="adminadmin"):
        '''
            Objective:
                -- Add a chain via command "bigchain chain <chain_name>"       
        '''
        try:
            t = test.Test()
            c = t.controller('master')
        except:
            helpers.test_failure("Could not execute command")
            return False
        else:
            if chain_name is None:
                helpers.log("FAIL: Cannot add a chain without specifying a name")
                return False
            else:
                url = '/api/v1/data/controller/applications/bigchain/chain[name="%s"]' % str(chain_name)
                try:
                    if "admin" not in user:
                        c_user = t.node_reconnect(node='master', user=str(user), password=password)
                        c_user.rest.get(url)
                        if not c_user.rest.status_code_ok():
                            helpers.test_failure(c_user.rest.error())
                        c_user.rest.put(url, {'name':str(chain_name)})
                        t.node_reconnect(node='master')
                    else:
                        c.rest.put(url, {'name':str(chain_name)})
                except:
                    helpers.test_log(c.rest.error())
                    return False
                else:
                    return True

    def rest_add_endpoint(self, node, chain_name=None, interface1=None, interface2=None, switch_alias=None, sw_dpid=None, user="admin", password="adminadmin"):
        '''
            Objective:
                -- Add a chain via command "bigchain chain <chain_name>"       
        '''
        try:
            t = test.Test()
            c = t.controller('master')
            AppCommon = AppController.AppController()
            if (switch_alias is None and sw_dpid is not None):
                switch_dpid = sw_dpid
            elif (switch_alias is None and sw_dpid is None):
                switch_dpid = AppCommon.rest_return_switch_dpid_from_ip(node)
            elif (switch_alias is not None and sw_dpid is None):
                switch_dpid = AppCommon.rest_return_switch_dpid_from_alias(switch_alias)
            else:
                switch_dpid = sw_dpid
        except:
            helpers.test_failure("Could not execute command")
            return False
        else:
            if((chain_name is None)  or (interface1 is None) or (interface2 is None)) :
                helpers.log("FAIL: Cannot add a endpoint pair without specifying a chain name or endpoint interfaces")
                return False
            else:
                url = '/api/v1/data/controller/applications/bigchain/chain[name="%s"]/endpoint-pair' % str(chain_name)
                try:
                    if "admin" not in user:
                        c_user = t.node_reconnect(node='master', user=str(user), password=password)
                        c_user.rest.get(url)
                        if not c_user.rest.status_code_ok():
                            helpers.test_failure(c_user.rest.error())
                        c_user.rest.patch(url, {"interface1": str(interface1), "switch": str(switch_dpid), "interface2": str(interface2)})
                        t.node_reconnect(node='master')
                    else:
                        c.rest.patch(url, {"interface1": str(interface1), "switch": str(switch_dpid), "interface2": str(interface2)})
                except:
                    helpers.test_log(c.rest.error())
                    return False
                else:
                    return True









