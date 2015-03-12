'''
###  WARNING !!!!!!!
###  This is where common code for BigChain will go in.
###
###  To commit new code, please contact the Library Owner:
###  Animesh Patcha (animesh.patcha@bigswitch.com)
###
###  DO NOT COMMIT CODE WITHOUT APPROVAL FROM LIBRARY OWNER
###
###  Last Updated: 1/18/2015
###
###  WARNING !!!!!!!
'''
import autobot.helpers as helpers
import autobot.test as test
import keywords.AppController as AppController
import re
# import json


class BigChain(object):

    def __init__(self):
        pass

###################################################
# All BigChain CLI Commands Go Here:
###################################################

###################################################
# All BigChain REST Commands Go Here:
###################################################
###################################################
##### SHOW COMMANDS
###################################################

    def rest_verify_switch_mode_show(self, node, mode='bigchain', switch_alias=None, sw_dpid=None):
        '''
            Objective:
                -- Verify a switch role via command "show switch <switch_alias>"
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
            helpers.test_log("Could not execute command")
            return False
        else:
            url = '/api/v1/data/controller/core/switch[dpid="%s"]' % str(switch_dpid)
            c.rest.get(url)
            if not c.rest.status_code_ok():
                helpers.test_log(c.rest.error())
                return False
            content = c.rest.content()
            if (content[0]['pipeline-mode']) == str(mode):
                helpers.log("Switch Mode %s is reported correctly" % str(mode))
                return True
            else:
                helpers.log("Switch Mode %s is not reported correctly" % str(mode))
                return False

    def rest_verify_switch_mode_config(self, node, mode='bigchain', switch_alias=None, sw_dpid=None):
        '''
            Objective:
                -- Verify a switch role via command "show running-config"
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
            helpers.test_log("Could not execute command")
            return False
        else:
            url = '/api/v1/data/controller/applications/bigtap/switch-config?config=true'
            c.rest.get(url)
            if not c.rest.status_code_ok():
                helpers.test_log(c.rest.error())
                return False
            content = c.rest.content()
            for switch in content:
                if switch['switch'] == str(switch_dpid) and switch['role'] == str(mode):
                    return True
            return False

    def rest_show_bigchain(self, desired_output="state"):
        '''
            Objective:
                -- Return desired value after executing cli command "show bigchain"
        '''
        try:
            t = test.Test()
            c = t.controller('master')
        except:
            helpers.test_log("Could not execute command")
            return False
        else:
            url = '/api/v1/data/controller/applications/bigchain/info'
            c.rest.get(url)
            if not c.rest.status_code_ok():
                helpers.test_log(c.rest.error())
                return False
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

    def rest_show_bigchain_chain(self, chain_name, desired_output):
        '''
            Objective:
                -- Return desired value after executing cli command "show bigchain chain"       
        '''
        try:
            t = test.Test()
            c = t.controller('master')
        except:
            helpers.test_log("Could not execute command")
            return False
        else:
            # url = '/api/v1/data/controller/applications/bigchain/chain[name="%s"]?select=status' % str(chain_name)
            url = '/api/v1/data/controller/applications/bigchain/chain?select=status'
            c.rest.get(url)
            if not c.rest.status_code_ok():
                helpers.test_log(c.rest.error())
                return False
            content = c.rest.content()
            if len(content) == 0:
                return False
            else:
                for array_entry in content:
                    if (array_entry['name'] == str(chain_name)):
                        if str(desired_output) == "detailedstatus":
                            return array_entry['status']['detailed-status']
                        elif desired_output == "endpoint1":
                            return array_entry['status']['endpoint1']
                        elif desired_output == "endpoint1-drop":
                            return array_entry['status']['endpoint1-drop']
                        elif desired_output == "name-in-status":
                            return array_entry['status']['name']
                        elif desired_output == "runtime-status":
                            return array_entry['status']['runtime-status']
                        elif desired_output == "services":
                            return array_entry['status']['services']
                        elif desired_output == "switch":
                            return array_entry['status']['switch']
                        elif desired_output == "endpoint2":
                            return array_entry['status']['endpoint2']
                        elif desired_output == "endpoint2-drop":
                            return array_entry['status']['endpoint2-drop']
                helpers.test_log("Requested object does not exist")
                return False

    def rest_verify_bigchain_chain(self, node, chain_name=None, interface1=None, interface2=None, switch_alias=None, sw_dpid=None, service1=None, service2=None, service3=None, span_down=False):
        '''
            Objective:
                -- Verify cli command "show bigchain chain <chain_name>"     
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
            helpers.test_log("Could not execute command")
            return False
        else:
            if((chain_name is None)  or (interface1 is None) or (interface2 is None)) :
                helpers.log("FAIL: Cannot add a endpoint pair without specifying a chain name or endpoint interfaces")
                return False
            else:
                url = '/api/v1/data/controller/applications/bigchain/chain[name="%s"]?select=status' % str(chain_name)
                c.rest.get(url)
                if not c.rest.status_code_ok():
                    return False
                content = c.rest.content()
                if len(content) == 0:
                    return False
                else:
                    pass_count = 0
                    if content[0]['name'] == str(chain_name) :
                        helpers.log("Chain Name %s is reported correctly" % str(chain_name))
                    else:
                        helpers.log("Chain Name %s is not reported correctly" % str(chain_name))
                        return False

                    if span_down is False:
                        if (content[0]['status']['runtime-status'] == "installed") :
                            helpers.log("Run Time Status is reported correctly")
                        else:
                            helpers.log("Run Time Status is not reported correctly")
                            return False
                        if (content[0]['status']['detailed-status'] == "All policies active and installed for this chain") or (content[0]['status']['detailed-status'] == "All flows installed for this chain") :
                            helpers.log("Detailed Status is reported correctly")
                        else:
                            helpers.log("Detailed Status is not reported correctly")
                            return False
                    else:
                        if (content[0]['status']['runtime-status'] == "partial") :
                            helpers.log("Run Time Status is reported correctly")
                        else:
                            helpers.log("Run Time Status is not reported correctly")
                            return False
                        if ("failed installing span services" in content[0]['status']['detailed-status']) :
                            helpers.log("Detailed Status is reported correctly")
                        else:
                            helpers.log("Detailed Status is not reported correctly")
                            return False

                    if (content[0]['status']['endpoint1'] == str(interface1)) :
                        helpers.log("Interface %s is reported correctly" % str(interface1))
                    else:
                        helpers.log("Interface %s is not reported correctly" % str(interface1))
                        return False

                    if (content[0]['status']['endpoint2'] == str(interface2)) :
                        pass_count = pass_count + 1
                        helpers.log("Interface %s is reported correctly" % str(interface2))
                    else:
                        helpers.log("Interface %s is not reported correctly" % str(interface2))
                        return False

                    if (content[0]['status']['switch'] == str(switch_dpid)) :
                        pass_count = pass_count + 1
                        helpers.log("Switch DPID %s is reported correctly" % str(switch_dpid))
                    else:
                        helpers.log("Switch DPID %s is not reported correctly" % str(switch_dpid))
                        return False
                    if service1 is None:
                        return True
                    else:
                        if service1 is not None and service2 is None:
                            if (content[0]['status']['services'] == str(service1)):
                                helpers.log("Service %s is reported correctly" % str(service1))
                            else:
                                helpers.log("Service %s is not reported correctly" % str(service1))
                                return False
                        else:
                            temp = content[0]['status']['services']
                            temp_array = temp.split(',')
                            if temp_array[2] == str(service1):
                                helpers.log("Service %s is reported correctly" % str(service1))
                            else:
                                helpers.log("Service %s is not reported correctly" % str(service1))
                                return False
                            if service2 is not None :
                                if temp_array[1] == str(service2):
                                    helpers.log("Service %s is reported correctly" % str(service2))
                                else:
                                    helpers.log("Service %s is not reported correctly" % str(service2))
                                    return False
                            if service3 is not None:
                                if temp_array[0] == str(service3):
                                    helpers.log("Service %s is reported correctly" % str(service3))
                                else:
                                    helpers.log("Service %s is not reported correctly" % str(service3))
                                    return False
                return True

    def rest_verify_bichain_chain_config(self, node, chain_name=None, endpoint1=None, endpoint2=None, switch_alias=None, sw_dpid=None):
        '''
            Objective:
                -- Verify a bigchain chain configuration role via command "show running-config bigchain chain <chain_name>"
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
            helpers.test_log("Could not execute command")
            return False
        else:
            url = '/api/v1/data/controller/applications/bigchain/chain[name="%s"]?config=true' % str(chain_name)
            c.rest.get(url)
            if not c.rest.status_code_ok():
                helpers.test_log(c.rest.error())
                return False
            content = c.rest.content()
            if len(content) == 0:
                return False
            else:
                if content[0]['name'] == str(chain_name) :
                    helpers.log("Chain Name %s is reported correctly" % str(chain_name))
                else:
                    helpers.log("Chain Name %s is not reported correctly" % str(chain_name))
                    return False
                if content[0]['endpoint-pair']['endpoint1'] == str(endpoint1) :
                    helpers.log("End Point 1 %s is reported correctly" % str(endpoint1))
                else:
                    helpers.log("End Point 1 %s is not reported correctly" % str(endpoint1))
                    return False
                if content[0]['endpoint-pair']['endpoint2'] == str(endpoint2) :
                    helpers.log("End Point 2 %s is reported correctly" % str(endpoint2))
                else:
                    helpers.log("End Point 2 %s is not reported correctly" % str(endpoint2))
                    return False
                if content[0]['endpoint-pair']['switch'] == str(switch_dpid) :
                    helpers.log("Switch DPID  %s is reported correctly" % str(switch_dpid))
                else:
                    helpers.log("Switch DPID %s is not reported correctly" % str(switch_dpid))
                    return False
            return True

    def rest_verify_bigchain_policy(self, node, chain_name=None, policy_name=None, endpoint1=None, endpoint2=None, scount=0, fintf=1, dintf=1, presintf=0, postsintf=0, fpktcnt=0, dpktcnt=0):
        '''
            Objective:
                -- Verify cli command "show bigchain policy <chain_policy_name>"
        '''
        try:
            t = test.Test()
            c = t.controller('master')
            AppCommon = AppController.AppController()
            switch_dpid = AppCommon.rest_return_switch_dpid_from_ip(node)
        except:
            helpers.test_log("Could not execute command")
            return False
        else:
            if((policy_name is None) or (chain_name is None)  or (endpoint1 is None) or (endpoint2 is None)) :
                helpers.log("FAIL: Cannot verify bigchain policy without specifying a chain name or endpoint interfaces")
                return False
            else:
                url1 = '/api/v1/data/controller/applications/bigchain/chain/policy[name="%s"]/info' % str(policy_name)
                c.rest.get(url1)
                if not c.rest.status_code_ok():
                    helpers.test_log(c.rest.error())
                    return False
                content = c.rest.content()
                if len(content) == 0:
                    return False
                else:
                    if content[0]['chainName'] == str(chain_name) :
                        helpers.log("Chain Name %s is reported correctly" % str(chain_name))
                    else:
                        helpers.log("Chain Name %s is not reported correctly" % str(chain_name))
                        return False
                    if content[0]['config-status'] == "bypass service-node forwarding" :
                        helpers.log("Config Status is reported correctly as bypass service-node forwarding")
                    elif content[0]['config-status'] == "through service-node forwarding":
                        helpers.log("Config Status is reported correctly as through service-node forwarding")
                    else:
                        helpers.log("Config Status %s is not reported correctly" % str(content[0]['config-status']))
                        return False
                    if content[0]['detailed-status'] == "installed - installed to forward" :
                        helpers.log("detailed Status is reported correctly as installed - installed to forward")
                    else:
                        helpers.log("detailed Status %s is not reported correctly" % str(content[0]['detailed-status']))
                        return False
                    if content[0]['runtime-status'] == "installed" :
                        helpers.log("runtime-status is reported correctly as installed")
                    else:
                        helpers.log("runtime status %s is not reported correctly" % str(content[0]['runtime-status']))
                        return False
                    if content[0]['delivery-interface-count'] == int(dintf) :
                        helpers.log("delivery-interface-count %s is reported correctly" % int(dintf))
                    else:
                        helpers.log("delivery-interface-count %s is not reported correctly" % str(content[0]['delivery-interface-count']))
                        return False
                    if content[0]['filter-interface-count'] == int(fintf) :
                        helpers.log("filter-interface-count %s is reported correctly" % int(fintf))
                    else:
                        helpers.log("filter-interface-count %s is not reported correctly" % str(content[0]['filter-interface-count']))
                        return False
                    if content[0]['pre-service-interface-count'] == int(presintf) :
                        helpers.log("pre-service-interface-count %s is reported correctly" % int(presintf))
                    else:
                        helpers.log("pre-service-interface-count %s is not reported correctly" % str(content[0]['pre-service-interface-count']))
                        return False
                    if content[0]['post-service-interface-count'] == int(postsintf) :
                        helpers.log("post-service-interface-count %s is reported correctly" % int(postsintf))
                    else:
                        helpers.log("post-service-interface-count %s is not reported correctly" % str(content[0]['post-service-interface-count']))
                        return False
                    if content[0]['service-count'] == int(scount) :
                        helpers.log("service-count %s is reported correctly" % int(scount))
                    else:
                        helpers.log("service-count %s is not reported correctly" % str(content[0]['service-count']))
                        return False
                url2 = '/api/v1/data/controller/applications/bigchain/chain/policy[name="%s"]/filter-interface' % str(policy_name)
                c.rest.get(url2)
                if not c.rest.status_code_ok():
                    helpers.test_log(c.rest.error())
                    return False
                content1 = c.rest.content()
                if len(content1) == 0:
                    return False
                else:
                    if content1[0]['interface'] == str(endpoint1) :
                        helpers.log("Endpoint 1 %s is reported correctly" % str(endpoint1))
                    else:
                        helpers.log("Endpoint 1 %s is not reported correctly" % str(content1[0]['interface']))
                        return False
                    if content1[0]['direction'] == "rx" :
                        helpers.log("Endpoint1 direction is reported correctly as rx")
                    else:
                        helpers.log("Endpoint 1 direction is not reported correctly as %s" % str(content1[0]['direction']))
                        return False
                    if content1[0]['state'] == "up" :
                        helpers.log("Endpoint1 state is reported correctly as up")
                    else:
                        helpers.log("Endpoint 1 state is not reported correctly as %s" % str(content1[0]['state']))
                        return False
                    if content1[0]['switch'] == str(switch_dpid) :
                        helpers.log("Endpoint1 Switch is reported correctly as %s" % str(switch_dpid))
                    else:
                        helpers.log("Endpoint 1 Switch is not reported correctly as %s" % str(content1[0]['switch']))
                        return False
                    if content1[0]['packet-count'] == int(fpktcnt) :
                        helpers.log("Endpoint1 Switch is reported correctly as %s" % int(fpktcnt))
                    else:
                        helpers.log("Endpoint 1 Switch is not reported correctly as %s" % str(content1[0]['packet-count']))
                        return False

                url3 = '/api/v1/data/controller/applications/bigchain/chain/policy[name="%s"]/delivery-interface' % str(policy_name)
                c.rest.get(url3)
                if not c.rest.status_code_ok():
                    helpers.test_log(c.rest.error())
                    return False
                content2 = c.rest.content()
                if len(content2) == 0:
                    return False
                else:
                    if content2[0]['interface'] == str(endpoint2) :
                        helpers.log("Endpoint 2 %s is reported correctly" % str(endpoint2))
                    else:
                        helpers.log("Endpoint 2 %s is not reported correctly" % str(content2[0]['interface']))
                        return False
                    if content2[0]['direction'] == "tx" :
                        helpers.log("Endpoint 2 direction is reported correctly as tx")
                    else:
                        helpers.log("Endpoint 2 direction is not reported correctly as %s" % str(content2[0]['direction']))
                        return False
                    if content2[0]['state'] == "up" :
                        helpers.log("Endpoint 2 state is reported correctly as up")
                    else:
                        helpers.log("Endpoint 2 state is not reported correctly as %s" % str(content2[0]['state']))
                        return False
                    if content2[0]['switch'] == str(switch_dpid) :
                        helpers.log("Endpoint 2 Switch is reported correctly as %s" % str(switch_dpid))
                    else:
                        helpers.log("Endpoint 2 Switch is not reported correctly as %s" % str(content2[0]['switch']))
                        return False
                    if content2[0]['packet-count'] == int(fpktcnt) :
                        helpers.log("Endpoint 2 packet count is reported correctly as %s" % int(dpktcnt))
                    else:
                        helpers.log("Endpoint 2 packet count is not reported correctly as %s" % str(content2[0]['packet-count']))
                        return False
                return True

    def rest_verify_bigchain_chain_policy(self, node, chain_name=None, endpoint1=None, endpoint2=None):
        '''
            Objective:
                -- Verify cli command "show bigchain chain <chain_name>"     
        '''
        try:
            t = test.Test()
            c = t.controller('master')
            BigChain1 = BigChain()
        except:
            helpers.test_log("Could not execute command")
            return False
        else:
            if((chain_name is None)  or (endpoint1 is None) or (endpoint2 is None)) :
                helpers.log("FAIL: Cannot verify bigchain policy without specifying a chain name or endpoint interfaces")
                return False
            else:
                url = '/api/v1/data/controller/applications/bigchain/chain[name="{}"]/policy?select=info'.format(str(chain_name))
                c.rest.get(url)
                if not c.rest.status_code_ok():
                    helpers.test_log(c.rest.error())
                    return False
                content = c.rest.content()
                if len(content) == 0:
                    return False
                else:
                    policy_pass = 0
                    for policy_array in content:
                        helpers.log("Policy Array is %s" % policy_array)
                        if policy_array['info']['chainName'] == str(chain_name):
                            policy_interface_array = policy_array['name'].split(":")
                            helpers.log("Policy INTF Array is %s" % policy_interface_array)
                            if (BigChain1.rest_verify_bigchain_policy(node, chain_name, policy_array['name'], policy_interface_array[1], policy_interface_array[3])):
                                policy_pass = policy_pass + 1
                    helpers.log("Policy Pass Count is {}".format(policy_pass))
                    helpers.log("Length of Content is {}".format(len(content)))
                    if policy_pass == len(content):
                        return True
                    else:
                        return False

    def rest_verify_bigchain_service_instance(self, node, chain_service_name=None, chain_service_type=None, instance_id=None, inport=None, outport=None, inskip=False, outskip=False, chain_service_description="", switch_alias=None, sw_dpid=None):
        '''
            Verify service instance is configured correctly
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
            helpers.test_log("Could not execute command")
            return False
        else:
            if (chain_service_name is None) or (chain_service_type is None) or (instance_id is None) or (inport is None) or (outport is None):
                helpers.log("Cannot verify service instance if service name, instance id, in-port or out-port are missing")
                return False
            else:
                url1 = '/api/v1/data/controller/applications/bigchain/service[name="%s"]' % str(chain_service_name)
                c.rest.get(url1)
                if not c.rest.status_code_ok():
                    helpers.test_log(c.rest.error())
                    return False
                content = c.rest.content()
                if content[0]['name'] == str(chain_service_name):
                    helpers.log("Service correctly reports its name")
                else:
                    helpers.log("Service incorrectly reports its name")
                    return False

                if content[0]['type'] == str(chain_service_type):
                    helpers.log("Service correctly reports its type")
                else:
                    helpers.log("Service incorrectly reports its type")
                    return False

                if not chain_service_description and content[0].has_key('description'):
                    if content[0]['description'] == str(chain_service_type):
                        helpers.log("Service correctly reports its description")
                    else:
                        helpers.log("Service incorrectly reports its chain_service_description")
                        return False

                for instance_detail in content[0]['instance']:
                    if instance_detail['id'] == int(instance_id):
                        helpers.log("Specified instance ID exists")
                        if (instance_detail['in-skip'] is False) and (inskip is False):
                            helpers.log("Instance correctly reports in-skip status")
                        elif (instance_detail['in-skip'] is True) and (inskip is True):
                            helpers.log("Instance correctly reports in-skip status")
                        else:
                            helpers.log("Instance incorrectly reports in-skip status")
                            return False

                        if (instance_detail['out-skip'] is False) and (outskip is False):
                            helpers.log("Instance correctly reports out-skip status")
                        elif (instance_detail['out-skip'] is True) and (outskip is True):
                            helpers.log("Instance correctly reports out-skip status")
                        else:
                            helpers.log("Instance incorrectly reports out-skip status")
                            return False

                        if instance_detail['interface-pair']['in'] == str(inport):
                            helpers.log("Instance correctly reports in-port")
                        else:
                            helpers.log("Instance incorrectly reports in-port")
                            return False

                        if instance_detail['interface-pair']['out'] == str(outport):
                            helpers.log("Instance correctly reports out-port")
                        else:
                            helpers.log("Instance incorrectly reports out-port")
                            return False

                        if instance_detail['interface-pair']['switch'] == str(switch_dpid):
                            helpers.log("Instance correctly reports switch dpid")
                        else:
                            helpers.log("Instance incorrectly reports switch dpid")
                            return False
                return True

    def rest_verify_bigchain_service_policy(self, chain_service_name=None, sequence=1, data=None):
        '''
        '''
        try:
            t = test.Test()
            c = t.controller('master')
        except:
            helpers.test_log("Could not execute command")
            return False
        else:
            if (chain_service_name is None) or (data is None):
                helpers.log("Service Name or policy data cannot be empty")
            else:

                try:
                    url1 = '/api/v1/data/controller/applications/bigchain/service[name="%s"]' % str(chain_service_name)
                    c.rest.get(url1)
                except:
                    helpers.test_log(c.rest.error())
                    return False
                else:
                    policy_array = str(data).split()
                    helpers.log("Policy Array is %s" % policy_array)
                    content = c.rest.content()
                    policy_content = content[0]['policy']['rule']
                    helpers.log("Policy Content is %s" % policy_content)
                    number_of_matches = int(len(policy_array) / 2)
                    match_found = 0
                    sequence_found = False
                    for j in range(0, len(policy_content)):
                        if policy_content[j]['sequence'] == int(sequence):
                            sequence_found = True
                            for i in range(1, len(policy_array), 2):
                                if ("port" in policy_array[i - 1])  or ("vlan-" in  policy_array[i - 1]) or  ("tos-" in  policy_array[i - 1]) or  ("proto" in  policy_array[i - 1]):
                                    temp1 = int(policy_content[j][policy_array[i - 1]])
                                    temp2 = int(policy_array[i])
                                else:
                                    temp1 = str(policy_content[j][policy_array[i - 1]])
                                    temp2 = str(policy_array[i])
                                if temp1 == temp2:
                                    match_found = match_found + 1
                                else:
                                    helpers.log("Match not found value1:%s  value2:%s" % (temp1, temp2))
                                    return False
                    if sequence_found is True:
                        if (match_found == number_of_matches) or (match_found == (number_of_matches + 1)):
                            return True
                        else:
                            return False
                    else:
                        helpers.log("Sequence number not found")
                        return False

    def rest_verify_bigchain_address_group(self, chain_addressgrp_name=None, chain_addressgrp_type='ipv4', chain_addressgrp_data=None):
        try:
            t = test.Test()
            c = t.controller('master')
        except:
            helpers.test_log("Could not execute command")
            return False
        else:
            if (chain_addressgrp_name is None) or (chain_addressgrp_data is None):
                helpers.log("FAIL: Cannot verify an address-group without specifying a address-group name or data")
                return False
            else:
                try:
                    url = '/api/v1/data/controller/applications/bigchain/ip-address-set[name="%s"]' % str(chain_addressgrp_name)
                    c.rest.get(url)
                except:
                    helpers.test_log(c.rest.error())
                    return False
                else:
                    content = c.rest.content()
                    if content[0]['name'] == str(chain_addressgrp_name):
                        helpers.log("PASS: Big Chain address group name is reported corretcly as %s" % content[0]['name'])
                    else:
                        helpers.log("FAIL: Big Chain address group name is reported incorretcly as %s" % content[0]['name'])
                        return False
                    if content[0]['ip-address-type'] == str(chain_addressgrp_type):
                        helpers.log("PASS: Big Chain address group type is reported corretcly as %s" % content[0]['ip-address-type'])
                    else:
                        helpers.log("FAIL: Big Chain address group type is reported incorretcly as %s" % content[0]['ip-address-type'])
                        return False
                    addressgrp_data = str(chain_addressgrp_data).split()
                    match_found = 0
                    for j in range(0, len(addressgrp_data), 2):
                        ip_address = addressgrp_data[j]
                        ip_mask = addressgrp_data[j + 1]
                        for i in range(0, len(content[0]['address-mask-set'])):
                            if (content[0]['address-mask-set'][i]['ip'] == str(ip_address)) and (content[0]['address-mask-set'][i]['ip-mask'] == str(ip_mask)):
                                match_found = match_found + 1
                    if match_found == (len(addressgrp_data) / 2):
                        return True
                    else:
                        return False

    def rest_verify_bigchain_span_service(self, node, switch_alias=None, sw_dpid=None, chain_span_service_name=None, chain_span_service_interface=None, chain_span_service_instance=1):
        '''
            Execute CLI command "show bigchain span-service <span_service_name>" and verify
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
            helpers.test_log("Could not execute command")
            return False
        else:
            if (chain_span_service_name is None) or (chain_span_service_interface is None):
                helpers.test_log("Cannot execute command if chain_span_service_name and chain_span_service_interface are not provided ")
                return False
            else:
                try:
                    url = '/api/v1/data/controller/applications/bigchain/span-service[name="%s"]' % str(chain_span_service_name)
                    c.rest.get(url)
                except:
                    helpers.test_log(c.rest.error())
                    return False
                else:
                    content = c.rest.content()
                    found = 0
                    if content[0]['name'] == str(chain_span_service_name):
                        helpers.log("Span Service corretcly reports its name as %s" % str(chain_span_service_name))
                    else:
                        helpers.log("Span Service incorretcly reports its name as %s" % str(content[0]['name']))

                    for i in range(0, len(content[0]['instance'])):
                        if content[0]['instance'][i]['id'] == int(chain_span_service_instance):
                            helpers.log("Span Service corretcly reports its instance ID as %s" % str(chain_span_service_instance))
                            found = 1
                        else:
                            helpers.log("Span Service incorretcly reports its instance ID  as %s" % str(content[0]['instance'][i]['id']))
                        if content[0]['instance'][i].has_key('span-interface'):
                            if content[0]['instance'][i]['span-interface']['interface'] == str(chain_span_service_interface):
                                helpers.log("Span Service corretcly reports its span interface as %s" % str(chain_span_service_interface))
                                found = 1
                            else:
                                helpers.log("Span Service incorretcly reports its span interface as %s" % str(content[0]['instance'][i]['span-interface']['interface']))
                            if content[0]['instance'][i]['span-interface']['switch'] == str(switch_dpid):
                                helpers.log("Span Service corretcly reports its switch_dpid as %s" % str(switch_dpid))
                                found = 1
                            else:
                                helpers.log("Span Service incorretcly reports its switch_dpid as %s" % str(content[0]['instance'][i]['span-interface']['switch']))
                        else:
                            helpers.log("The key span-interface does not exist")
                            return False
                    if found == 0:
                        return False
                    else:
                        return True

    def rest_verify_bigchain_chain_span_service_connection(self, chain_name=None, chain_span_service_name=None, instance=1, endpoint1=False, endpoint2=False):
        '''
            Execute CLI command "show bigchain chain <chain_name> span-service" and verify span service is linked with chain
        '''
        try:
            t = test.Test()
            c = t.controller('master')
        except:
            helpers.test_log("Could not execute command")
            return False
        else:
            if (chain_name is None) or (chain_span_service_name is None):
                helpers.test_log("Cannot execute command if chain_span_service_name and chain_span_service_interface are not provided ")
                return False
            else:
                try:
                    url = '/api/v1/data/controller/applications/bigchain/chain[name="{}"]/endpoint1-span'.format(str(chain_name))
                    c.rest.get(url)
                except:
                    helpers.test_log(c.rest.error())
                    return False
                else:
                    content = c.rest.content()
                    if (bool(content[0]) is False) and (endpoint1 is False):
                        helpers.test_log("CLI correctly returns empty dictionary when endpoint1-span is not configured connected to endpoint1")
                    elif endpoint1 is True:
                        if int(content[0]['instance']) == int(instance):
                            helpers.test_log("CLI corretcly reports instance ID for span-service connected to endpoint1")
                        else:
                            helpers.test_log("CLI does not corretcly report instance ID for span-service connected to endpoint1")
                            return False
                        if str(content[0]['instance']) == str(chain_span_service_name):
                            helpers.test_log("CLI corretcly reports span-service name connected to endpoint1")
                        else:
                            helpers.test_log("CLI does not corretcly report span-service name connected to endpoint1")
                            return False
                try:
                    url = '/api/v1/data/controller/applications/bigchain/chain[name="{}"]/endpoint2-span'.format(str(chain_name))
                    c.rest.get(url)
                except:
                    helpers.test_log(c.rest.error())
                    return False
                else:
                    content = c.rest.content()
                    if (bool(content[0]) is False) and (endpoint2 is False):
                        helpers.test_log("CLI correctly returns empty dictionary when endpoint2-span is not configured")
                    elif endpoint2 is True:
                        if int(content[0]['instance']) == int(instance):
                            helpers.test_log("CLI corretcly reports instance ID for span-service connected to endpoint2")
                        else:
                            helpers.test_log("CLI does not corretcly report instance ID for span-service connected to endpoint2")
                            return False
                        if str(content[0]['instance']) == str(chain_span_service_name):
                            helpers.test_log("CLI corretcly reports span-service name connected to endpoint2")
                        else:
                            helpers.test_log("CLI does not corretcly report span-service name connected to endpoint2")
                            return False
                return True

###################################################
##### CONFIG COMMANDS
###################################################

    def rest_add_switch_role(self, node, switch_alias=None, sw_dpid=None, mode='bigchain'):
        '''
            Objective:
                -- Add a switch role via command "deployment role <mode>"
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
            helpers.test_log("Could not execute command")
            return False
        else:
            url = '/api/v1/data/controller/core/switch[dpid="{}"]'.format(str(switch_dpid))
            try:
                c.rest.patch(url, {"role": str(mode)})
            except:
                helpers.test_log(c.rest.error())
                return False
            else:
                return True


    def rest_delete_switch_role(self, node, switch_alias=None, sw_dpid=None, mode='bigchain'):
        '''
            Objective:
                -- Add a switch role via command "deployment role <mode>"
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
            helpers.test_log("Could not execute command")
            return False
        else:
            url = '/api/v1/data/controller/core/switch[dpid="{}"]'.format(str(switch_dpid))
            try:
                c.rest.delete(url, {"role": str(mode)})
            except:
                helpers.test_log(c.rest.error())
                return False
            else:
                return True

##### Chain Configuration Commands Start
    def rest_add_a_chain(self, chain_name=None):
        '''
            Objective:
                -- Add a chain via command "bigchain chain <chain_name>"       
        '''
        try:
            t = test.Test()
            c = t.controller('master')
        except:
            helpers.test_log("Could not execute command")
            return False
        else:
            if chain_name is None:
                helpers.log("FAIL: Cannot add a chain without specifying a name")
                return False
            else:
                url = '/api/v1/data/controller/applications/bigchain/chain[name="%s"]' % str(chain_name)
                try:
                    c.rest.put(url, {'name':str(chain_name)})
                except:
                    helpers.test_log(c.rest.error())
                    return False
                else:
                    return True

    def rest_add_chain_endpoint(self, node, chain_name=None, interface1=None, interface2=None, switch_alias=None, sw_dpid=None):
        '''
            Objective:
                -- Add an endpoint to a chain via command "endpoint-pair switch app-as5710-1 endpoint1 ethernet21 endpoint2 ethernet22"       
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
            helpers.test_log("Could not execute command")
            return False
        else:
            if((chain_name is None)  or (interface1 is None) or (interface2 is None)) :
                helpers.log("FAIL: Cannot add a endpoint pair without specifying a chain name or endpoint interfaces")
                return False
            else:
                url = '/api/v1/data/controller/applications/bigchain/chain[name="%s"]/endpoint-pair' % str(chain_name)
                try:
                    c.rest.patch(url, {"endpoint2": str(interface2), "switch": str(switch_dpid), "endpoint1": str(interface1)})
                except:
                    helpers.test_log(c.rest.error())
                    return False
                else:
                    return True

    def rest_add_service_to_chain(self, chain_name=None, service_name=None, instance=1, sequence=1, optional=False):
        '''
            Objective:
                -- Add a service to a chain via command "use-service C1S1 instance 1 sequence 1"
       '''
        try:
            t = test.Test()
            c = t.controller('master')
        except:
            helpers.test_log("Could not execute command")
            return False
        else:
            if((chain_name is None)  or (service_name is None)) :
                helpers.log("FAIL: Cannot add a endpoint pair without specifying a chain name or endpoint interfaces")
                return False
            else:
                url = '/api/v1/data/controller/applications/bigchain/chain[name="%s"]/service[sequence=%s]' % (str(chain_name), str(sequence))
                try:
                    if optional is True:
                        c.rest.put(url, {"service-name": str(service_name), "instance": int(instance), "optional": True, "sequence": int(sequence)})
                    else:
                        c.rest.put(url, {"service-name": str(service_name), "instance": int(instance), "sequence": int(sequence)})
                except:
                    helpers.test_log(c.rest.error())
                    return False
                else:
                    return True

    def rest_delete_bigchain_chain(self, chain_name=None):
        '''
            Objective:
                -- Delete a chain via command "no bigchain chain <chain_name>"       
        '''
        try:
            t = test.Test()
            c = t.controller('master')
        except:
            helpers.test_log("Could not execute command")
            return False
        else:
            if chain_name is None:
                helpers.log("FAIL: Cannot delete a chain without specifying a chain name")
                return False
            else:
                url = '/api/v1/data/controller/applications/bigchain/chain[name="%s"]' % str(chain_name)
                try:
                    c.rest.delete(url, {})
                except:
                    helpers.test_log(c.rest.error())
                    return False
                else:
                    return True
##### Chain Configuration Commands End
##### Service Configuration Commands Start
    def rest_add_a_bigchain_service(self, chain_service_name=None, service_type="custom", instance_id=1):
        '''
            Objective:
                -- Add a chain via command "bigchain service <service_name>"       
        '''
        try:
            t = test.Test()
            c = t.controller('master')
        except:
            helpers.test_log("Could not execute command")
            return False
        else:
            if chain_service_name is None:
                helpers.log("FAIL: Cannot add a chain without specifying a name")
                return False
            else:
                url1 = '/api/v1/data/controller/applications/bigchain/service[name="%s"]' % str(chain_service_name)
                try:
                    c.rest.put(url1, {'name':str(chain_service_name)})
                except:
                    helpers.test_log(c.rest.error())
                    return False
                url2 = '/api/v1/data/controller/applications/bigchain/service[name="%s"]' % str(chain_service_name)
                try:
                    c.rest.patch(url2, {'type':str(service_type)})
                except:
                    helpers.test_log(c.rest.error())
                    return False
                url3 = '/api/v1/data/controller/applications/bigchain/service[name="%s"]/instance[id=%d]' % (str(chain_service_name), int(instance_id))
                try:
                    c.rest.put(url3, {'id':int(instance_id)})
                except:
                    helpers.test_log(c.rest.error())
                    return False
                return True

    def rest_add_a_bigchain_service_description(self, chain_service_name=None, descrption=None):
        '''
            Objective:
                -- Add a chain via command "bigchain chain <chain_name>"       
        '''
        try:
            t = test.Test()
            c = t.controller('master')
        except:
            helpers.test_log("Could not execute command")
            return False
        else:
            if (chain_service_name is None) or (descrption is None):
                helpers.log("FAIL: Cannot add a description without specifying a chain name or chain description")
                return False
            else:
                url = '/api/v1/data/controller/applications/bigchain/service[name="%s"]' % str(chain_service_name)
                try:
                    c.rest.patch(url, {'description':str(descrption)})
                except:
                    helpers.test_log(c.rest.error())
                    return False
                else:
                    return True

    def rest_delete_a_bigchain_service_description(self, chain_service_name=None, descrption=None):
        '''
            Objective:
                -- Add a chain via command "bigchain chain <chain_name>"       
        '''
        try:
            t = test.Test()
            c = t.controller('master')
        except:
            helpers.test_log("Could not execute command")
            return False
        else:
            if (chain_service_name is None) or (descrption is None):
                helpers.log("FAIL: Cannot add a description without specifying a chain name or chain description")
                return False
            else:
                url = '/api/v1/data/controller/applications/bigchain/service[name="%s"][name="%s"][description="%s"]/description' % (str(chain_service_name), str(chain_service_name), str(descrption))
                try:
                    c.rest.delete(url, {})
                except:
                    helpers.test_log(c.rest.error())
                    return False
                else:
                    return True

    def rest_add_a_bigchain_service_instance_interface_pair(self, node, switch_alias=None, sw_dpid=None, chain_service_name=None, instance_id=1, inintf=None, outintf=None, update="False"):
        '''
            Objective:
                -- Add a interface-pair under service instance via command "interface-pair switch <switch_dpid> in <inintf> out <outintf>"       
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
            helpers.test_log("Could not execute command")
            return False
        else:
            if (chain_service_name is None) or (inintf is None) or (outintf is None):
                helpers.log("FAIL: Cannot add a description without specifying a chain name or chain description")
                return False
            else:
                url = '/api/v1/data/controller/applications/bigchain/service[name="%s"]/instance[id=%d]/interface-pair' % (str(chain_service_name), int(instance_id))
                try:
                    if update == "False":
                        c.rest.put(url, {"switch": str(switch_dpid), "in": str(inintf), "out": str(outintf)})
                    else:
                        c.rest.patch(url, {"switch": str(switch_dpid), "in": str(inintf), "out": str(outintf)})
                except:
                    helpers.test_log(c.rest.error())
                    return False
                else:
                    return True

    def rest_delete_a_bigchain_service_instance_interface_pair(self, chain_service_name=None, instance_id=1):
        '''
            Objective:
                -- delete an interface-pair under service instance via command "no interface-pair switch <switch_dpid> in <inintf> out <outintf>"       
        '''
        try:
            t = test.Test()
            c = t.controller('master')
        except:
            helpers.test_log("Could not execute command")
            return False
        else:
            if (chain_service_name is None):
                helpers.log("FAIL: Cannot delete an interface-pair without specifying a chain name")
                return False
            else:
                url1 = '/api/v1/data/controller/applications/bigchain/service[name="%s"]/instance[id=%d]/interface-pair/switch' % (str(chain_service_name), int(instance_id))
                try:
                    c.rest.delete(url1, {})
                except:
                    helpers.test_log(c.rest.error())
                    return False
                else:
                    url2 = '/api/v1/data/controller/applications/bigchain/service[name="%s"]/instance[id=%d]/interface-pair/in' % (str(chain_service_name), int(instance_id))
                    try:
                        c.rest.delete(url2, {})
                    except:
                        helpers.test_log(c.rest.error())
                        return False
                    else:
                        url3 = '/api/v1/data/controller/applications/bigchain/service[name="%s"]/instance[id=%d]/interface-pair/out' % (str(chain_service_name), int(instance_id))
                        try:
                            c.rest.delete(url3, {})
                        except:
                            helpers.test_log(c.rest.error())
                            return False
                        else:
                            return True

    def rest_skip_service(self, chain_service_name=None, instance_id=1, inskip="False", outskip="False"):
        '''
            Objective:
                -- Skip service for inbound/outbound traffic       
        '''
        try:
            t = test.Test()
            c = t.controller('master')
        except:
            helpers.test_log("Could not execute command")
            return False
        else:
            if (chain_service_name is None) :
                helpers.log("FAIL: Cannot add in-skip without specifying a chain name")
                return False
            else:
                try:
                    helpers.log("Values are %s and %s and %s and %s" % (chain_service_name, instance_id, inskip, outskip))
                    myinskip = str(inskip).lower()
                    myoutskip = str(outskip).lower()
                    if bool(re.match(myinskip, 'true')) :
                        url1 = '/api/v1/data/controller/applications/bigchain/service[name="%s"]/instance[id=%d]' % (str(chain_service_name), int(instance_id))
                        c.rest.patch(url1, {"in-skip": True})
                    elif bool(re.match(myoutskip, 'true')) :
                        url2 = '/api/v1/data/controller/applications/bigchain/service[name="%s"]/instance[id=%d]' % (str(chain_service_name), int(instance_id))
                        c.rest.patch(url2, {"out-skip": True})
                    elif bool(re.match(myinskip, 'delete')) :
                        url3 = '/api/v1/data/controller/applications/bigchain/service[name="%s"]/instance[id=%d][in-skip="True"][id=%d]/in-skip' % (str(chain_service_name), int(instance_id), int(instance_id))
                        c.rest.delete(url3, {})
                    elif bool(re.match(myoutskip, 'delete')) :
                        url4 = '/api/v1/data/controller/applications/bigchain/service[name="%s"]/instance[id=%d][out-skip="True"][id=%d]/out-skip' % (str(chain_service_name), int(instance_id), int(instance_id))
                        c.rest.delete(url4, {})
                    else:
                        helpers.test_log("FAIL: Invalid values sent for either in-skip or out-skip")
                        return False
                except:
                    helpers.test_log(c.rest.error())
                    return False
                else:
                    return True

    def rest_update_bigchain_policy_action(self, chain_service_name=None, policy_action="do-service"):
        '''
            Objective:
                -- Add a service policy       
        '''
        try:
            t = test.Test()
            c = t.controller('master')
        except:
            helpers.test_log("Could not execute command")
            return False
        else:
            if (chain_service_name is None) :
                helpers.log("FAIL: Cannot add in-skip without specifying a chain name")
                return False
            else:
                try:
                    url = '/api/v1/data/controller/applications/bigchain/service[name="%s"]/policy' % str(chain_service_name)
                    c.rest.patch(url, {"action": str(policy_action)})
                except:
                    helpers.test_log(c.rest.error())
                    return False
                else:
                    return True

    def rest_add_a_bigchain_policy_match(self, chain_service_name=None, match_number=None, data=None, flag=False):
        '''
            Objective:
                -- Add a service policy       
        '''
        try:
            t = test.Test()
            c = t.controller('master')
        except:
            helpers.test_log("Could not execute command")
            return False
        else:
            if (chain_service_name is None) or (match_number is None) or (data is None) :
                helpers.log("FAIL: Cannot add match condition without specifying a chain name, match number or data")
                return False
            else:
                try:
                    url = '/api/v1/data/controller/applications/bigchain/service[name="%s"]/policy/rule[sequence=%d]' % (str(chain_service_name), int(match_number))
                    if not flag:
                        data_dict = helpers.from_json(data)
                    else:
                        data_dict = data
                    helpers.log("Input dictionary is %s" % data_dict)
                    c.rest.put(url, data_dict)
                except:
                    helpers.test_log(c.rest.error())
                    return False
                else:
                    return True

    def rest_delete_a_bigchain_policy_match(self, chain_service_name=None, match_number=None, data=None, flag=False):
        '''
            Objective:
                -- Add a service policy       
        '''
        try:
            t = test.Test()
            c = t.controller('master')
        except:
            helpers.test_log("Could not execute command")
            return False
        else:
            if (chain_service_name is None) or (match_number is None) or (data is None) :
                helpers.log("FAIL: Cannot add match condition without specifying a chain name, match number or data")
                return False
            else:
                try:
                    url = '/api/v1/data/controller/applications/bigchain/service[name="%s"]/policy/rule[sequence=%d]' % (str(chain_service_name), int(match_number))
                    if not flag:
                        data_dict = helpers.from_json(data)
                    else:
                        data_dict = data
                    c.rest.delete(url, data_dict)
                except:
                    helpers.test_log(c.rest.error())
                    return False
                else:
                    return True

    def rest_delete_bigchain_service(self, chain_service_name=None):
        '''
            Objective:
                -- Delete a service 
        '''
        try:
            t = test.Test()
            c = t.controller('master')
        except:
            helpers.test_log("Could not execute command")
            return False
        else:
            if (chain_service_name is None):
                helpers.log("FAIL: Cannot delete a service without specifying a service name")
                return False
            else:
                try:
                    url = '/api/v1/data/controller/applications/bigchain/service[name="%s"]' % str(chain_service_name)
                    c.rest.delete(url, {})
                except:
                    helpers.test_log(c.rest.error())
                    return False
                else:
                    return True
##### Service Configuration Commands End
##### Span Configuration Commands Begin
    def rest_add_bigchain_span_service(self, node, span_service_name=None, span_instance_id=1, span_interface=None, switch_alias=None, sw_dpid=None, update=False):
        '''
             Objective:
                -- Add a span interface service       
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
            helpers.test_log("Could not execute command")
            return False
        else:
            if (span_service_name is None) or (span_interface is None):
                helpers.log("FAIL: Cannot delete a service without specifying a span service name or interface name")
                return False
            else:
                try:
                    if update is False:
                        url1 = '/api/v1/data/controller/applications/bigchain/span-service[name="%s"]' % str(span_service_name)
                        c.rest.put(url1, {"name": str(span_service_name)})
                except:
                    helpers.test_log(c.rest.error())
                    return False
                else:
                    try:
                        url2 = '/api/v1/data/controller/applications/bigchain/span-service[name="%s"]/instance[id=%s]' % (str(span_service_name), str(span_instance_id))
                        c.rest.put(url2, {"id": int(span_instance_id)})
                    except:
                        helpers.test_log(c.rest.error())
                        return False
                    else:
                        try:
                            url3 = '/api/v1/data/controller/applications/bigchain/span-service[name="%s"]/instance[id=%s]/span-interface' % (str(span_service_name), str(span_instance_id))
                            if update is False:
                                c.rest.put(url3, {"switch": str(switch_dpid), "interface": str(span_interface)})
                            else:
                                c.rest.patch(url3, {"switch": str(switch_dpid), "interface": str(span_interface)})
                        except:
                            helpers.test_log(c.rest.error())
                            return False
                        else:
                            helpers.log("URL3 PUT executed sucessfully")
                            return True
                return True

    def rest_delete_span_service(self, span_service_name=None):
        '''
             Objective:
                -- Delete a span interface service       
        '''
        try:
            t = test.Test()
            c = t.controller('master')
        except:
            helpers.test_log("Could not execute command")
            return False
        else:
            if (span_service_name is None):
                helpers.log("FAIL: Cannot delete a service without specifying a service name")
                return False
            else:
                try:
                    url = '/api/v1/data/controller/applications/bigchain/span-service[name="%s"]' % str(span_service_name)
                    c.rest.delete(url, {})
                except:
                    helpers.test_log(c.rest.error())
                    return False
                else:
                    return True

    def rest_delete_span_service_instance(self, span_service_name=None, span_instance_id=1):
        '''
             Objective:
                -- Delete a span interface service       
        '''
        try:
            t = test.Test()
            c = t.controller('master')
        except:
            helpers.test_log("Could not execute command")
            return False
        else:
            if (span_service_name is None):
                helpers.log("FAIL: Cannot delete a service without specifying a service name")
                return False
            else:
                try:
                    url = '/data/controller/applications/bigchain/span-service[name="%s"]/instance[id=%d]' % (str(span_service_name), int(span_instance_id))
                    c.rest.delete(url, {})
                except:
                    helpers.test_log(c.rest.error())
                    return False
                else:
                    return True

    def rest_delete_span_service_interface(self, span_service_name=None, span_instance_id=1):
        '''
             Objective:
                -- Delete a span interface service       
        '''
        try:
            t = test.Test()
            c = t.controller('master')
        except:
            helpers.test_log("Could not execute command")
            return False
        else:
            if (span_service_name is None):
                helpers.log("FAIL: Cannot delete a service without specifying a service name")
                return False
            else:
                try:
                    url1 = '/data/controller/applications/bigchain/span-service[name="%s"]/instance[id=%d]/span-interface/interface' % (str(span_service_name), int(span_instance_id))
                    c.rest.delete(url1, {})
                except:
                    helpers.test_log(c.rest.error())
                    return False
                else:
                    try:
                        url2 = '/data/controller/applications/bigchain/span-service[name="%s"]/instance[id=%d]/span-interface/switch' % (str(span_service_name), int(span_instance_id))
                        c.rest.delete(url2, {})
                    except:
                        helpers.test_log(c.rest.error())
                        return False
                    else:
                        return True

    def rest_add_span_service_to_chain(self, chain_name=None, endpoint1=False, endpoint2=False, span_service_name=None, span_instance_id=1, update=False):
        try:
            t = test.Test()
            c = t.controller('master')
        except:
            helpers.test_log("Could not execute command")
            return False
        else:
            if (chain_name is None) or (span_service_name is None):
                helpers.log("FAIL: Cannot add a span-service without specifying a service name and chain name")
                return False
            elif (endpoint1 is False) and (endpoint2 is False) :
                helpers.log("FAIL: Cannot span-service without specifying a either a from-span or a to-span  as True")
                return False
            else:
                if endpoint1 is True:
                    try:
                        url = '/api/v1/data/controller/applications/bigchain/chain[name="%s"]/endpoint1-span' % str(chain_name)
                        if update is False:
                            c.rest.put(url, {"instance": int(span_instance_id), "span-name": str(span_service_name)})
                        else:
                            c.rest.patch(url, {"instance": int(span_instance_id), "span-name": str(span_service_name)})
                    except:
                        helpers.test_log(c.rest.error())
                        return False

                if endpoint2 is True:
                    try:
                        url = '/api/v1/data/controller/applications/bigchain/chain[name="%s"]/endpoint2-span' % str(chain_name)
                        if update is False:
                            c.rest.put(url, {"instance": int(span_instance_id), "span-name": str(span_service_name)})
                        else:
                            c.rest.patch(url, {"instance": int(span_instance_id), "span-name": str(span_service_name)})
                    except:
                        helpers.test_log(c.rest.error())
                        return False
                return True

    def rest_delete_span_service_from_chain(self, chain_name=None, endpoint1=False, endpoint2=False):
        try:
            t = test.Test()
            c = t.controller('master')
        except:
            helpers.test_log("Could not execute command")
            return False
        else:
            if (chain_name is None):
                helpers.log("FAIL: Cannot add a span-service without specifying a chain name")
                return False
            elif (endpoint1 is False) and (endpoint2 is False) :
                helpers.log("FAIL: Cannot span-service without specifying a either a from-span or a to-span  as True")
                return False
            else:
                if endpoint1 is True:
                    try:
                        url1 = '/api/v1/data/controller/applications/bigchain/chain[name="%s"]/endpoint1-span/instance' % str(chain_name)
                        c.rest.delete(url1, {})
                    except:
                        helpers.test_log(c.rest.error())
                        return False
                    else:
                        try:
                            url2 = '/api/v1/data/controller/applications/bigchain/chain[name="%s"]/endpoint1-span/span-name' % str(chain_name)
                            c.rest.delete(url2, {})
                        except:
                            helpers.test_log(c.rest.error())
                            return False

                if endpoint2 is True:
                    try:
                        url1 = '/api/v1/data/controller/applications/bigchain/chain[name="%s"]/endpoint2-span/instance' % str(chain_name)
                        c.rest.delete(url1, {})
                    except:
                        helpers.test_log(c.rest.error())
                        return False
                    else:
                        try:
                            url2 = '/api/v1/data/controller/applications/bigchain/chain[name="%s"]/endpoint2-span/span-name' % str(chain_name)
                            c.rest.delete(url2, {})
                        except:
                            helpers.test_log(c.rest.error())
                            return False
                return True

    def rest_add_span_service_policy_match(self, span_service_name=None, match_number=None, data=None, flag=False, update=False):
        '''
            Add a policy match condition to span service
        '''
        try:
            t = test.Test()
            c = t.controller('master')
        except:
            helpers.test_log("Could not execute command")
            return False
        else:
            if (span_service_name is None) or (match_number is None) or (data is None) :
                helpers.log("FAIL: Cannot add match condition without specifying a span service name, match number or data")
                return False
            else:
                if update is False:  # First time policy is being configured
                    try:
                        url1 = '/api/v1/data/controller/applications/bigchain/span-service[name="{}"]/policy'.format(str(span_service_name))
                        c.rest.put(url1, {})
                    except:
                        helpers.test_log(c.rest.error())
                        return False
                try:
                    url2 = '/api/v1/data/controller/applications/bigchain/span-service[name="{}"]/policy/rule[sequence={}]'.format(str(span_service_name), int(match_number))
                    if not flag:
                        data_dict = helpers.from_json(data)
                    else:
                        data_dict = data
                    helpers.log("Input dictionary is %s" % data_dict)
                    c.rest.put(url2, data_dict)
                except:
                    helpers.test_log(c.rest.error())
                    return False
                else:
                    return True

    def rest_delete_span_service_policy_match(self, span_service_name=None, match_number=None, data=None, flag=False):
        '''
            Delete a span service match condition
        '''
        try:
            t = test.Test()
            c = t.controller('master')
        except:
            helpers.test_log("Could not execute command")
            return False
        else:
            if (span_service_name is None) or (match_number is None) or (data is None) :
                helpers.log("FAIL: Cannot add match condition without specifying a span service name, match number or data")
                return False
            else:
                try:
                    url = '/api/v1/data/controller/applications/bigchain/span-service[name="{}"]/policy/rule[sequence={}]'.format(str(span_service_name), int(match_number))
                    if not flag:
                        data_dict = helpers.from_json(data)
                    else:
                        data_dict = data
                    helpers.log("Input dictionary is %s" % data_dict)
                    c.rest.delete(url, data_dict)
                except:
                    helpers.test_log(c.rest.error())
                    return False
                else:
                    return True
##### Span Configuration Commands End
##### Big Chain Address Group  Start
    def rest_add_bigchain_address_group(self, chain_addressgrp_name=None, chain_addressgrp_type='ipv4', chain_addressgrp_data=None):
        try:
            t = test.Test()
            c = t.controller('master')
        except:
            helpers.test_log("Could not execute command")
            return False
        else:
            if (chain_addressgrp_name is None) or (chain_addressgrp_data is None):
                helpers.log("FAIL: Cannot add a span-service without specifying a chain name")
                return False
            else:
                try:
                    url1 = '/api/v1/data/controller/applications/bigchain/ip-address-set[name="%s"]' % str(chain_addressgrp_name)
                    c.rest.put(url1, {"name": str(chain_addressgrp_name)})
                except:
                    helpers.test_log(c.rest.error())
                    return False
                else:
                    try:
                        url2 = '/api/v1/data/controller/applications/bigchain/ip-address-set[name="%s"]' % str(chain_addressgrp_name)
                        c.rest.patch(url2, {"ip-address-type": str(chain_addressgrp_type)})
                    except:
                        helpers.test_log(c.rest.error())
                        return False
                    else:
                        addressgrp_data = str(chain_addressgrp_data).split()
                        helpers.log("Array is %s" % addressgrp_data)
                        for j in range(0, len(addressgrp_data), 2):
                            ip_address = addressgrp_data[j].strip()
                            ip_mask = addressgrp_data[j + 1].strip()
                            try:
                                url3 = '/api/v1/data/controller/applications/bigchain/ip-address-set[name="%s"]/address-mask-set[ip="%s"][ip-mask="%s"]' % (str(chain_addressgrp_name), str(ip_address), str(ip_mask))
                                helpers.log("URL3: %s" % url3)
                                c.rest.put(url3, {"ip": str(ip_address), "ip-mask": str(ip_mask)})
                            except:
                                helpers.test_log(c.rest.error())
                                return False
                        return True

    def rest_delete_bigchain_address_group(self, chain_addressgrp_name=None):
        try:
            t = test.Test()
            c = t.controller('master')
        except:
            helpers.test_log("Could not execute command")
            return False
        else:
            if (chain_addressgrp_name is None):
                helpers.log("FAIL: Cannot add a span-service without specifying a chain name")
                return False
            else:
                try:
                    url = '/api/v1/data/controller/applications/bigchain/ip-address-set[name="%s"]' % str(chain_addressgrp_name)
                    c.rest.delete(url, {})
                except:
                    helpers.test_log(c.rest.error())
                    return False
                else:
                    return True
##### Big Chain Address Group  End
