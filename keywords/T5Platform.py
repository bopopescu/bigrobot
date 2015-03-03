import autobot.helpers as helpers
import autobot.test as test
from T5Utilities import T5Utilities as utilities
from T5Utilities import T5PlatformThreads
from BsnCommon import BsnCommon as bsnCommon
import re
import keywords.Mininet as mininet
import keywords.T5 as T5
import keywords.T5L3 as T5L3
import keywords.Host as Host
import keywords.Ixia as Ixia

mininetPingFails = 0
hostPingFails = 0
leafSwitchList = []


class T5Platform(object):

    def __init__(self):
        pass

    def rest_verify_show_cluster(self, **kwargs):

        '''Using the 'show cluster' command verify the cluster formation across both nodes
	       Also check for the formation integrity
	       Additional inputs: IP Addresses of the Controllers can be specified as: 'c1=a.b.c.d  c2=a.b.e.f'
	    '''

        try:
            t = test.Test()
            if 'c1' in kwargs:
                c1 = t.node_spawn(ip=kwargs.get('c1'))
            else:
                c1 = t.controller("c1")
            if 'c2' in kwargs:
                c2 = t.node_spawn(ip=kwargs.get('c2'))
            else:
                c2 = t.controller("c2")

            url = '/api/v1/data/controller/cluster'

            result = c1.rest.get(url)['content']
            reported_active_by_c1 = result[0]['status']['domain-leader']['leader-id']

            result = c2.rest.get(url)['content']
            reported_active_by_c2 = result[0]['status']['domain-leader']['leader-id']

            if(reported_active_by_c1 != reported_active_by_c2):
                helpers.log("Both controllers %s & %s are declaring themselves as active" \
                        % (reported_active_by_c1, reported_active_by_c2))
                helpers.test_failure("Error: Inconsistent active/stand-By cluster formation detected")
                return False
            else:
                helpers.log("Active controller id is: %s " % reported_active_by_c1)
                helpers.log("Pass: Consistent active/standby cluster formation verified")
                return True

        except Exception, err:
            helpers.test_failure("Exception in: rest_verify_ha_cluster %s : %s " % (Exception, err))
            return False


    def _cluster_election(self, initial_sync_check):
        ''' Invoke "failover" commands
            initial_sync_check - by default True
        '''
        t = test.Test()
        slave = t.controller("slave")
        master = t.controller("master")

        masterID, slaveID = self.getNodeID()
        if(masterID == -1 and slaveID == -1):
            return False

        helpers.log("Current slave ID is : %s / Current master ID is: %s" % (slaveID, masterID))

        url = '/api/v1/data/controller/core/high-availability/failover'

        if(initial_sync_check):
            slave.rest.post(url, {"initial-sync-check": True})
        else:
            slave.rest.post(url, {"initial-sync-check": False})

        # helpers.sleep(30)
        helpers.sleep(90)

        newMasterID = self.getNodeID(False)
        if(newMasterID == -1):
            return False

        if(masterID == newMasterID):
            if(initial_sync_check):
                helpers.test_failure("Fail: Master didn't change after executing take-leader")
                return False
            else:
                helpers.log("Pass: Leader election re-run successful - Leader %s  is intact " % (masterID))
                return True
        else:
            helpers.log("Pass: Take-Leader successful - Leader changed from %s to %s" % (masterID, newMasterID))
            return True


    def rest_verify_cluster_election_take_leader(self):
        ''' Invoke "cluster election take-leader" command and verify the controller state
            This function will invoke the take_leader functionality and verify the fabric integrity between
            before and after states
        '''
        obj = utilities()
        utilities.fabric_integrity_checker(obj, "before")
        returnVal = self._cluster_election(True)
        if(not returnVal):
            return False
        # helpers.sleep(30)
        helpers.sleep(90)
        return utilities.fabric_integrity_checker(obj, "after")


    def cli_cluster_take_leader(self, node='slave'):
        ''' Function to trigger failover to slave controller via CLI. This function will verify the
            fabric integrity between states

            Input: None
            Output: True if successful, False otherwise
        '''
        t = test.Test()
        c = t.controller(node)
        obj = utilities()
        utilities.fabric_integrity_checker(obj, "before")

        helpers.log("Failover")
        try:
            c.config("config")
            c.send("reauth")
            c.expect(r"Password:")
            c.config("adminadmin")
            c.send("system failover")
            c.expect(r"Failover to a standby controller node (\"y\" or \"yes\" to continue)?")
            c.config("yes")
            # helpers.sleep(30)
            helpers.sleep(90)
        except:
            helpers.test_log(c.cli_content())
            return False
        else:
            return utilities.fabric_integrity_checker(obj, "after")


    def cli_create_policy_list(self, tenant, policy_list, policy_rule):
        ''' Function to create policy list using cli commands
            Input: tenant-name, policy-list-name, rule
            Output: True if successful, False otherwise
        '''
        t = test.Test()
        c = t.controller('master')

        helpers.log("Provided cli path: tenant-name:%s, policy-list-name:%s, policy-rule:%s" % (tenant, policy_list, policy_rule))
        c.config("config")
        c.config('tenant ' + tenant)
        c.config('logical-router')
        try:
            c.send('policy-list ' + policy_list)
            c.expect([c.get_prompt()])
            if "Error" in c.cli_content():
                helpers.test_failure(c.cli_content())
                return False

            c.send(policy_rule)
            c.expect([c.get_prompt()])
            if "Error" in c.cli_content():
                helpers.test_failure(c.cli_content())
                return False

        except:
            helpers.test_failure(c.cli_content())
            return False
        else:
            return True


    def cli_delete_policy_list(self, tenant, policy_list, policy_rule):
        ''' Function to delete policy rule using cli commands
            Input: tenant-name, policy-list-name, rule
            Output: True if successful, False otherwise
        '''
        t = test.Test()
        c = t.controller('master')

        helpers.log("Provided cli path: tenant-name:%s, policy-list-name:%s, policy-rule:%s" % (tenant, policy_list, policy_rule))
        c.config("config")
        c.config('tenant ' + tenant)
        c.config('logical-router')
        c.config('policy-list ' + policy_list)
        try:
            c.send('no ' + policy_rule)
            c.expect([c.get_prompt()])
            if "Error" in c.cli_content():
                helpers.test_failure(c.cli_content())
                return False
        except:
            helpers.test_failure(c.cli_content())
            return False
        else:
            return True


    def cli_delete_policy(self, tenant, policy_list):
        ''' Function to delete policy  using cli commands
            Input: tenant-name, policy-list-name, rule
            Output: True if successful, False otherwise
        '''
        t = test.Test()
        c = t.controller('master')

        helpers.log("Provided cli path: tenant-name:%s, policy-list-name:%s " % (tenant, policy_list))
        c.config("config")
        c.config('tenant ' + tenant)
        c.config('logical-router')
        try:
            c.send('no policy-list ' + policy_list)
            c.expect([c.get_prompt()])
            if "Error" in c.cli_content():
                helpers.test_failure(c.cli_content())
                return False
        except:
            helpers.test_failure(c.cli_content())
            return False
        else:
            return True





    def cli_apply_policy(self, tenant, policy_list):
        ''' Function to apply policy using cli commands
            Input: tenant-name, policy-list-name
            Output: True if successful, False otherwise
        '''
        t = test.Test()
        c = t.controller('master')

        helpers.log("Provided cli path: tenant-name:%s, policy-list-name:%s" % (tenant, policy_list))
        c.config("config")
        c.config('tenant ' + tenant)
        c.config('logical-router')
        try:
            c.send('apply policy-list ' + policy_list)
            c.expect([c.get_prompt()])
            if "Error" in c.cli_content():
                helpers.test_failure(c.cli_content())
                return False
        except:
            helpers.test_failure(c.cli_content())
            return False
        else:
            return True





    def cli_remove_policy(self, tenant, policy_list):
        ''' Function to remove policy using cli commands
            Input: tenant-name, policy-list-name
            Output: True if successful, False otherwise
        '''
        t = test.Test()
        c = t.controller('master')

        helpers.log("Provided cli path: tenant-name:%s, policy-list-name:%s" % (tenant, policy_list))
        c.config("config")
        c.config('tenant ' + tenant)
        c.config('logical-router')
        try:
            c.send('no apply policy-list ' + policy_list)
            c.expect([c.get_prompt()])
            if "Error" in c.cli_content():
                helpers.test_failure(c.cli_content())
                return False
        except:
            helpers.test_failure(c.cli_content())
            return False
        else:
            return True

    def cli_delete_tenant(self, tenant):
        ''' Function to delete tenant using cli commands
            Input: tenant
            Output: True if successful, False otherwise
        '''
        t = test.Test()
        c = t.controller('master')

        helpers.log("Provided cli path: tenant-name:%s" % (tenant))
        c.config("config")

        try:
            c.send('no tenant ' + tenant)
            c.expect([c.get_prompt()])
            if "Error" in c.cli_content():
                helpers.test_failure(c.cli_content())
                return False
        except:
            helpers.test_failure(c.cli_content())
            return False
        else:
            return True


    def cli_enable_qos(self):
        ''' Function to enable qos using cli commands
            Input:
            Output: True if successful, False otherwise
        '''
        t = test.Test()
        c = t.controller('master')

        c.config("config")


        try:
            c.send('fabric')
            c.expect([c.get_prompt()])
            c.send('qos')
            c.expect([c.get_prompt()])
            if "Error" in c.cli_content():
                helpers.test_failure(c.cli_content())
                return False
        except:
            helpers.test_failure(c.cli_content())
            return False
        else:
            return True


    def cli_disable_qos(self):
        ''' Function to enable qos using cli commands
            Input:
            Output: True if successful, False otherwise
        '''
        t = test.Test()
        c = t.controller('master')

        c.config("config")


        try:
            c.send('fabric')
            c.expect([c.get_prompt()])
            c.send('no qos')
            c.expect([c.get_prompt()])
            if "Error" in c.cli_content():
                helpers.test_failure(c.cli_content())
                return False
        except:
            helpers.test_failure(c.cli_content())
            return False
        else:
            return True



    def rest_verify_cluster_election_rerun(self):
        ''' Invoke "cluster election re-run" command and verify the controller state
        '''
        obj = utilities()
        utilities.fabric_integrity_checker(obj, "before")
        returnVal = self._cluster_election(False)
        if(not returnVal):
            return False
        # helpers.sleep(30)
        helpers.sleep(60)
        return utilities.fabric_integrity_checker(obj, "after")


    def cluster_node_reboot(self, masterNode=True):

        ''' Reboot a node and verify the cluster leadership.
            Reboot Master in dual node setup: masterNode == True
        '''
        t = test.Test()
        master = t.controller("master")
        obj = utilities()

        if (utilities.cli_get_num_nodes(obj) == 1):
            singleNode = True
        else:
            singleNode = False


        if(singleNode):
            masterID = self.getNodeID(False)
        else:
            masterID, slaveID = self.getNodeID()

        if(singleNode):
            if (masterID == -1):
                return False
        else:
            if(masterID == -1 and slaveID == -1):
                return False

        try:
            if(masterNode):
                actual_node_name = master.name()
                ipAddr = master.ip()
                master.enable("system reboot controller", prompt="Confirm \(\"y\" or \"yes\" to continue\)")
                master.enable("yes")
                helpers.log("Master is rebooting")
                # helpers.sleep(90)
                helpers.sleep(190)
            else:
                slave = t.controller("slave")
                actual_node_name = slave.name()
                ipAddr = slave.ip()
                slave.enable("system reboot controller", prompt="Confirm \(\"y\" or \"yes\" to continue\)")
                slave.enable("yes")
                helpers.log("Slave is rebooting")
                # helpers.sleep(90)
                helpers.sleep(190)
        except:
            helpers.log("Node is rebooting")
            helpers.sleep(160)
            count = 0
            while (True):
                loss = helpers.ping(ipAddr)
                helpers.log("loss is: %s" % loss)
                if(loss != 0):
                    if (count > 5):
                        helpers.warn("Cannot connect to the IP Address: %s - Tried for 5 Minutes" % ipAddr)
                        return False
                    helpers.sleep(120)
                    count += 1
                    helpers.log("Trying to connect to the IP Address: %s - Try %s" % (ipAddr, count))
                else:
                    helpers.log("Controller just came alive. Waiting for it to become fully functional")
                    helpers.sleep(180)
                    break

        helpers.log("*** actual_node_name is '%s'. Node reconnect." % actual_node_name)
        t.node_reconnect(actual_node_name)

        if(singleNode):
            newMasterID = self.getNodeID(False)
        else:
            newMasterID, newSlaveID = self.getNodeID()

        if(singleNode):
            if (newMasterID == -1):
                return False
        else:
            if(newMasterID == -1 and newSlaveID == -1):
                return False


        if(singleNode):
            if(masterID == newMasterID):
                # obj.restart_floodlight_monitor("master")
                helpers.log("Pass: After the reboot cluster is stable - Master is still : %s " % (newMasterID))
                return True
            else:
                helpers.log("Fail: Reboot Failed. Cluster is not stable.  Before the reboot Master is: %s  \n \
                    After the reboot Master is: %s " % (masterID, newMasterID))
        else:
            # if(masterNode):
            #    obj.restart_floodlight_monitor("slave")
            # else:
            #    obj.restart_floodlight_monitor("master")

            if(masterNode):
                if(masterID == newSlaveID and slaveID == newMasterID):
                    helpers.log("Pass: After the reboot cluster is stable - Master is : %s / Slave is: %s" % (newMasterID, newSlaveID))
                    return True
                else:
                    helpers.log("Fail: Reboot Failed. Cluster is not stable. Before the master reboot Master is: %s / Slave is : %s \n \
                            After the reboot Master is: %s / Slave is : %s " % (masterID, slaveID, newMasterID, newSlaveID))
                    # obj.stop_floodlight_monitor()
                    return False
            else:
                if(masterID == newMasterID and slaveID == newSlaveID):
                    helpers.log("Pass: After the reboot cluster is stable - Master is : %s / Slave is: %s" % (newMasterID, newSlaveID))
                    return True
                else:
                    helpers.log("Fail: Reboot Failed. Cluster is not stable. Before the slave reboot Master is: %s / Slave is : %s \n \
                            After the reboot Master is: %s / Slave is : %s " % (masterID, slaveID, newMasterID, newSlaveID))
                    # obj.stop_floodlight_monitor()
                    return False


    def cluster_boot_partition(self, node='all', option='alternate'):
        '''
          boot partition  -
          Author: Mingtao
          input:  node  - controller
                          master, slave, c1 c2, all

          usage:
          output:

        '''

        t = test.Test()
        master = t.controller("master")
        obj = utilities()

        string = 'boot partition ' + option
        if node == 'all':
            slave = t.controller("slave")
            slave_name = slave.name()
            slave_contr = t.controller(slave_name)
            helpers.log("***** USR INFO:  Node name is : %s" % slave_name)
            ipAddr2 = slave_contr.ip()

            master_name = master.name()
            master_contr = t.controller(master_name)
            ipAddr1 = master_contr.ip()


            slave_contr.enable('')
            slave_contr.send(string)
            slave_contr.expect(r'[\r\n].+ to continue\):', timeout=180)
            slave_contr.send("yes")
            try:
                slave_contr.expect(r'The system is going down for reboot NOW!', timeout=60)
                content = slave_contr.cli_content()
                helpers.log("*****Output is :\n%s" % content)

            except:
                helpers.log('ERROR: SLave boot partition NOT successfully')
                return False
            else:
                helpers.log('INFO: Slave boot partition successfully')

            master_contr.enable('')
            master_contr.send(string)
            master_contr.expect(r'[\r\n].+ to continue\):', timeout=180)
            master_contr.send("yes")
            try:
                master_contr.expect(r'The system is going down for reboot NOW!', timeout=60)
                content = master_contr.cli_content()
                helpers.log("*****Output is :\n%s" % content)

            except:
                helpers.log('ERROR: Master boot partition NOT successfully')
                return False
            else:
                helpers.log('INFO: Master boot partition successfully')


        else:
            node = t.controller(node)
            ipAddr1 = node.ip()
            name = node.name()
            c = t.controller(name)
            string = 'boot partition ' + option
            c.enable('')
            c.send(string)
            c.expect(r'[\r\n].+ to continue\):', timeout=180)
            c.send("yes")
            try:
                c.expect(r'The system is going down for reboot NOW!', timeout=180)
                content = c.cli_content()
                helpers.log("*****Output is :\n%s" % content)

            except:
                helpers.log('ERROR: boot partition NOT successfully')
                return False
            else:
                helpers.log('INFO: boot partition successfully')

        helpers.log("Node is rebooting")
        helpers.sleep(120)
        count = 0
        while (True):
            loss = helpers.ping(ipAddr1)
            helpers.log("loss is: %s" % loss)
            if(loss != 0):
                if (count > 5):
                    helpers.warn("Cannot connect to the IP Address: %s - Tried for 5 Minutes" % ipAddr1)
                    return False
                helpers.sleep(120)
                count += 1
                helpers.log("Trying to connect to the IP Address: %s - Try %s" % (ipAddr1, count))
            else:
                helpers.log("Controller just came alive. Waiting for it to become fully functional")
                helpers.sleep(180)
                break

        if node == 'all':
            while (True):
                loss = helpers.ping(ipAddr2)
                helpers.log("loss is: %s" % loss)
                if(loss != 0):
                    if (count > 5):
                        helpers.warn("Cannot connect to the IP Address: %s - Tried for 5 Minutes" % ipAddr2)
                        return False
                    helpers.sleep(120)
                    count += 1
                    helpers.log("Trying to connect to the IP Address: %s - Try %s" % (ipAddr2, count))
                else:
                    helpers.log("Controller came alive. ")
                    break
        return True




    def cluster_node_reload(self, masterNode=True):

        ''' Reload a node and verify the cluster leadership.
            Reboot Master in dual node setup: masterNode == True
        '''
        t = test.Test()
        master = t.controller("master")
        obj = utilities()

        if (utilities.cli_get_num_nodes(obj) == 1):
            singleNode = True
        else:
            singleNode = False


        if(singleNode):
            masterID = self.getNodeID(False)
        else:
            masterID, slaveID = self.getNodeID()

        if(singleNode):
            if (masterID == -1):
                return False
        else:
            if(masterID == -1 and slaveID == -1):
                return False

        try:
            if(masterNode):
                actual_node_name = master.name()
                ipAddr = master.ip()
                master.enable("system reload controller", prompt="Confirm \(\"y\" or \"yes\" to continue\)")
                master.enable("yes")
                helpers.log("Master is reloading")
                # helpers.sleep(90)
                helpers.sleep(160)
            else:
                slave = t.controller("slave")
                actual_node_name = slave.name()
                ipAddr = slave.ip()
                slave.enable("system reload controller", prompt="Confirm \(\"y\" or \"yes\" to continue\)")
                slave.enable("yes")
                helpers.log("Slave is reloading")
                # helpers.sleep(90)
                helpers.sleep(160)
        except:
            helpers.log("Node is reloading")
            helpers.sleep(90)
            count = 0
            while (True):
                loss = helpers.ping(ipAddr)
                helpers.log("loss is: %s" % loss)
                if(loss != 0):
                    if (count > 5):
                        helpers.warn("Cannot connect to the IP Address: %s - Tried for 5 Minutes" % ipAddr)
                        return False
                    helpers.sleep(60)
                    count += 1
                    helpers.log("Trying to connect to the IP Address: %s - Try %s" % (ipAddr, count))
                else:
                    helpers.log("Controller just came alive. Waiting for it to become fully functional")
                    helpers.sleep(120)
                    break

        helpers.log("*** actual_node_name is '%s'. Node reconnect." % actual_node_name)
        t.node_reconnect(actual_node_name)

        if(singleNode):
            newMasterID = self.getNodeID(False)
        else:
            newMasterID, newSlaveID = self.getNodeID()

        if(singleNode):
            if (newMasterID == -1):
                return False
        else:
            if(newMasterID == -1 and newSlaveID == -1):
                return False


        if(singleNode):
            if(masterID == newMasterID):
                # obj.restart_floodlight_monitor("master")
                helpers.log("Pass: After the reboot cluster is stable - Master is still : %s " % (newMasterID))
                return True
            else:
                helpers.log("Fail: Reboot Failed. Cluster is not stable.  Before the reboot Master is: %s  \n \
                    After the reboot Master is: %s " % (masterID, newMasterID))
        else:
            # if(masterNode):
            #    obj.restart_floodlight_monitor("slave")
            # else:
            #    obj.restart_floodlight_monitor("master")

            if(masterNode):
                if(masterID == newSlaveID and slaveID == newMasterID):
                    helpers.log("Pass: After the reboot cluster is stable - Master is : %s / Slave is: %s" % (newMasterID, newSlaveID))
                    return True
                else:
                    helpers.log("Fail: Reboot Failed. Cluster is not stable. Before the master reboot Master is: %s / Slave is : %s \n \
                            After the reboot Master is: %s / Slave is : %s " % (masterID, slaveID, newMasterID, newSlaveID))
                    # obj.stop_floodlight_monitor()
                    return False
            else:
                if(masterID == newMasterID and slaveID == newSlaveID):
                    helpers.log("Pass: After the reboot cluster is stable - Master is : %s / Slave is: %s" % (newMasterID, newSlaveID))
                    return True
                else:
                    helpers.log("Fail: Reboot Failed. Cluster is not stable. Before the slave reboot Master is: %s / Slave is : %s \n \
                            After the reboot Master is: %s / Slave is : %s " % (masterID, slaveID, newMasterID, newSlaveID))
                    # obj.stop_floodlight_monitor()
                    return False






    def _cluster_node_shutdown(self, masterNode=True):
        ''' Shutdown the node
        '''
        t = test.Test()
        master = t.controller("master")
        obj = utilities()

        masterID, slaveID = self.getNodeID()
        if(masterID == -1 and slaveID == -1):
            return False

        if(masterNode):
            master.enable("shutdown", prompt="Confirm Shutdown \(yes to continue\)")
            master.enable("yes")
            helpers.log("Master is shutting down")
            helpers.sleep(10)
        else:
            slave = t.controller("slave")
            slave.enable("shutdown", prompt="Confirm Shutdown \(yes to continue\)")
            slave.enable("yes")
            helpers.log("Slave is shutting down")
            helpers.sleep(10)

        newMasterID = self.getNodeID(False)
        if(newMasterID == -1):
            return False

        if(masterNode):
            if(slaveID == newMasterID):
                helpers.log("Pass: After the shutdown cluster is stable - New master is : %s " % (newMasterID))
                return True
            else:
                helpers.log("Fail: Shutdown Failed. Cluster is not stable. Before the master node shutdown Master is: %s / Slave is : %s \n \
                        After the shutdown Master is: %s " % (masterID, slaveID, newMasterID))
                return False
        else:
            if(masterID == newMasterID):
                helpers.log("Pass: After the slave shutdown cluster is stable - Master is still: %s " % (newMasterID))
                return True
            else:
                helpers.log("Fail: Shutdown failed. Cluster is not stable. Before the slave shutdown Master is: %s / Slave is : %s \n \
                        After the shutdown Master is: %s " % (masterID, slaveID, newMasterID))
                return False


    def cli_verify_cluster_master_reboot(self):
        obj = utilities()
        utilities.fabric_integrity_checker(obj, "before")
        returnVal = self.cluster_node_reboot()
        if(not returnVal):
            return False
        return utilities.fabric_integrity_checker(obj, "after")

    def cli_verify_cluster_slave_reboot(self):
        obj = utilities()
        utilities.fabric_integrity_checker(obj, "before")
        returnVal = self.cluster_node_reboot(False)
        if(not returnVal):
            return False
        return utilities.fabric_integrity_checker(obj, "after")


    def cli_verify_cluster_master_reload(self):
        obj = utilities()
        utilities.fabric_integrity_checker(obj, "before")
        returnVal = self.cluster_node_reload()
        if(not returnVal):
            return False
        return utilities.fabric_integrity_checker(obj, "after")

    def cli_verify_cluster_slave_reload(self):
        obj = utilities()
        utilities.fabric_integrity_checker(obj, "before")
        returnVal = self.cluster_node_reload(False)
        if(not returnVal):
            return False
        return utilities.fabric_integrity_checker(obj, "after")


    def cli_verify_cluster_master_shutdown(self):
        obj = utilities()
        utilities.fabric_integrity_checker(obj, "before")
        returnVal = self._cluster_node_shutdown()
        if(not returnVal):
            return False
        return utilities.fabric_integrity_checker(obj, "after")

    def cli_verify_cluster_slave_shutdown(self):
        obj = utilities()
        utilities.fabric_integrity_checker(obj, "before")
        returnVal = self._cluster_node_shutdown(False)
        if(not returnVal):
            return False
        return utilities.fabric_integrity_checker(obj, "after")


    def verify_fabric_with_disruption(self, disruptMode="switchReboot", disruptTime="", failoverMode="", **kwargs):
        '''
            This function will carry out different disruptions during failovers & verify fabric
            integrity. Disruptions will carry out in distributed manner. For eg. if disruptMode is "switchReboot", this
            functions will schedule a dedicated thread to each switch reboot while carrying out failover function as defined by
            'disruptTime' argument.

            Inputs:
                disruptMode  : "switchReboot"    - Reboot leaf or spine switch eg: "switch=spine0"  / "switch=spine0 leaf0-a"

                disruptTime : Disruptions happens 'during' or 'before" the HA event

                failoverMode : "failover"     - Failover by issuing failover command (default)
                               "activeReboot" - Failover by rebooting active controller
                               "standbyReboot" - Reboot standby controller

                kwargs: "switch=spine0 leaf0-a"

        '''

        obj = utilities()
        utilities.fabric_integrity_checker(obj, "before")

        threadCounter = 0
        threadList = []

        if (disruptMode == "switchReboot"):
            switchList = kwargs.get('switch').split(' ')
            threadList.append("thread" + '%s' % threadCounter)
            for i, switchName in enumerate(switchList):
                threadList.append("thread" + '%s' % threadCounter)
                threadList[i] = T5PlatformThreads(threadCounter, "switchReboot", switch=switchName)
                threadCounter += 1
        elif (disruptMode == "switchPowerCycle"):
            threadList.append("thread" + '%s' % threadCounter)
            threadList[0] = T5PlatformThreads(threadCounter, "switchPowerCycle", **kwargs)
            threadCounter += 1

        disruptThreadCounter = threadCounter
        if(len(threadList) == 0):
            helpers.warn("No disruptMode arguments were detected. Exiting")
            return False

        if(failoverMode == "failover"):
            threadList.append("thread" + '%s' % threadCounter)
            threadList[len(threadList) - 1] = T5PlatformThreads(threadCounter, "failover")
            threadCounter += 1
        elif(failoverMode == "activeReboot"):
            threadList.append("thread" + '%s' % threadCounter)
            # threadList[len(threadList)-1] = T5PlatformThreads(threadCounter, "activeReboot", "")
            threadList[len(threadList) - 1] = T5PlatformThreads(threadCounter, "activeReboot")
            threadCounter += 1
        elif(failoverMode == "standbyReboot"):
            threadList.append("thread" + '%s' % threadCounter)
            # threadList[len(threadList)-1] = T5PlatformThreads(threadCounter, "standbyReboot", "")
            threadList[len(threadList) - 1] = T5PlatformThreads(threadCounter, "standbyReboot")
            threadCounter += 1


        if(disruptTime == "during"):
            for thread in threadList:
                helpers.log("Starting thread: %s" % thread)
                thread.start()
        elif(disruptTime == "before"):
            for i, thread in enumerate(threadList):
                helpers.log("Starting thread: %s" % thread)
                thread.start()
                if (i == disruptThreadCounter - 1):
                    helpers.sleep(45)
        else:
            for thread in threadList:
                helpers.log("Starting thread: %s" % thread)
                thread.start()


        for thread in threadList:
            helpers.log("Joining thread: %s" % thread)
            thread.join()

        helpers.sleep(60)
        return utilities.fabric_integrity_checker(obj, "after")

        # Create new threads
        # thread1 = Thread(target= self._verify_HA_duringReboot(kwargs.get("switch")))
        # thread2 = Thread(target= self.cli_cluster_take_leader())





    def rest_add_user(self, numUsers=1):
        numWarn = 0
        t = test.Test()
        master = t.controller("master")
        url = "/api/v1/data/controller/core/aaa/local-user"
        usersString = []
        numErrors = 0
        for i in range (0, int(numUsers)):
            user = "user" + str(i + 1)
            usersString.append(user)
            master.rest.post(url, {"user-name": user})
            helpers.sleep(1)

            if not master.rest.status_code_ok():
                helpers.test_failure(master.rest.error())
                numErrors += 1
            else:
                helpers.log("Successfully added user: %s " % user)

        if(numErrors > 0):
            return False
        else:
            url = "/api/v1/data/controller/core/aaa/local-user"
            result = master.rest.get(url)
            showUsers = []
            for i in range (0, len(result["content"])):
                showUsers.append(result["content"][i]['user-name'])
            helpers.sleep(5)
            for user in usersString:
                if user not in showUsers:
                    numWarn += 1
                    helpers.warn("User: %s not present in the show users" % user)
            if (numWarn > 0):
                return False
            else:
                return True

    def rest_delete_user(self, numUsers=1):
        numWarn = 0
        t = test.Test()
        master = t.controller("master")
        usersString = []
        numErrors = 0
        for i in range (0, int(numUsers)):
            url = "/api/v1/data/controller/core/aaa/local-user[user-name=\""
            user = "user" + str(i + 1)
            usersString.append(user)
            url = url + user + "\"]"
            master.rest.delete(url, {})
            helpers.sleep(1)

            if not master.rest.status_code_ok():
                helpers.test_failure(master.rest.error())
                numErrors += 1
            else:
                helpers.log("Successfully deleted user: %s " % user)

        if(numErrors > 0):
            return False
        else:
            url = "/api/v1/data/controller/core/aaa/local-user"
            result = master.rest.get(url)
            showUsers = []
            for i in range (0, len(result["content"])):
                showUsers.append(result["content"][i]['user-name'])
            helpers.sleep(5)
            for user in usersString:
                if user in showUsers:
                    numWarn += 1
                    helpers.warn("User: %s present in the show users" % user)
            if (numWarn > 0):
                return False
            else:
                return True


    def auto_configure_tenants(self, numTenants, numVnsPerTenant, vnsIntIPList, *args):

        ''' Add tenant & vns  to the running-config.
            Usage:
                * Variables
                @{vnsIntIPDict}  v1  10.10.10.100  v2  20.20.20.100  v3  30.30.30.100
                @{v1MemberPGList}   v1  PG   p1  10  p3  10
                @{v1MemberIntList}  v1  INT  leaf0-a  ethernet33  -1  leaf1-a  ethernet33  -1
                @{v2MemberPGList}   v2  PG   p2  20  p4  20
                @{v2MemberIntList}  v2  INT  leaf0-a  ethernet34  -1  leaf1-a  ethernet34  -1

                Test T5Setup
                    [Tags]  Setup
                    auto configure tenants     1  2  ${vnsIntIPDict}  ${v1MemberPGList}  ${v1MemberIntList}  ${v2MemberPGList}  ${v2MemberIntList}
        '''


        helpers.log("vnsIntIPList is: %s" % vnsIntIPList)
        vnsIPDict = {}

        try:
            vnsIPDict = dict(vnsIntIPList[i:i + 2] for i in range(0, len(vnsIntIPList), 2))
        except:
            helpers.test_failure("Error during converting vnsIntIPList to a Dictionary. Check the input parameters for vnsIntIPList")
            return False

        vnsMemberPGDict = {}
        vnsMemberIntDict = {}

        try:

            for arg in args:
                # helpers.log("arg is: %s" % arg)
                currentVNS = arg[0]
                helpers.log("CurrentVNS is : %s" % currentVNS)

                if (arg[1] == "PG"):
                    vnsMemberPGDict[currentVNS] = arg[2:]
                    helpers.log("Adding %s PG Dict: %s" % (currentVNS, vnsMemberPGDict[currentVNS]))
                elif (arg[1] == "INT"):
                    vnsMemberIntDict[currentVNS] = arg[2:]
                    helpers.log("Adding %s Int Dict: %s" % (currentVNS, vnsMemberIntDict[currentVNS]))

            i = 0
            while(i < int(numTenants) * int(numVnsPerTenant)):
                    i += 1
                    vnsName = 'v' + str(i)
                    # helpers.log("VNS Name is: %s / PG List is: %s" % (vnsName, vnsMemberPGDict[vnsName]))
                    # helpers.log("VNS Name is: %s / Int list is: %s" % (vnsName, vnsMemberIntDict[vnsName]))


        except:
            helpers.test_failure("Error during converting vns member Lists. Check the input parameters for vnsMemberPGList & vnsMemberIntList")
            return False


        autoTenantList = []
        autoVNSList = []
        i = 0
        while (i < int(numTenants)):
            i += 1
            autoTenantList.append('autoT' + str(i))

        helpers.log("Tenant List is: %s" % autoTenantList)

        Fabric = T5.T5()
        FabricL3 = T5L3.T5L3()

        # ==> Add System Router
        Fabric.rest_add_tenant("system")

        i = 0
        for tenant in autoTenantList:
            # ==> Add a Tenant
            Fabric.rest_add_tenant(tenant)

            j = 0
            while (j < int(numVnsPerTenant)):
                i += 1
                j += 1
                vnsName = 'v' + str(i)
                autoVNSList.append(vnsName)
                # ==> Add VNS with vnsName
                Fabric.rest_add_vns(tenant, vnsName)
                try:
                    k = 0
                    helpers.log("VNSName is: %s" % vnsName)
                    while (k < len(vnsMemberPGDict[vnsName])):
                        currentPG = vnsMemberPGDict[vnsName][k]
                        currentVLAN = vnsMemberPGDict[vnsName][k + 1]
                        k += 2
                        # helpers.log("currentPG is: %s" % currentPG)
                        # helpers.log("currentVLAN is: %s" % currentVLAN)

                        # ==> Add member port-group (currentPG, curentVLAN, vnsName)
                        Fabric.rest_add_portgroup_to_vns(tenant, vnsName, currentPG, currentVLAN)

                except(KeyError):
                    pass

                try:
                    k = 0
                    while (k < len(vnsMemberIntDict[vnsName])):
                        currentSwitch = vnsMemberIntDict[vnsName][k]
                        currentInt = vnsMemberIntDict[vnsName][k + 1]
                        currentVLAN = vnsMemberIntDict[vnsName][k + 2]
                        k += 3
                        # helpers.log("currentSwitch is: %s" % currentSwitch)
                        # helpers.log("currentInt is: %s" % currentInt)
                        # helpers.log("currentVLAN is: %s" % currentVLAN)

                        # ==> Add member interface to vns
                        Fabric.rest_add_interface_to_vns(tenant, vnsName, currentSwitch, currentInt, currentVLAN)


                except(KeyError):
                    pass

                # ==> Add the router interface IPs
                FabricL3.rest_add_router_intf(tenant, vnsName)
                FabricL3.rest_add_vns_ip(tenant, vnsName, vnsIPDict[vnsName], '24')

                # ==> Add system interface to tenant
                FabricL3.rest_add_system_intf_to_tenant_routers(tenant)

            # ==> Add tenant router interface to system
            FabricL3.rest_add_tenant_routers_intf_to_system(tenant)

            # ==> Add static routes pointing to system
            FabricL3.rest_add_static_routes(tenant, '0.0.0.0/0', "{\"tenant-name\": \"system\"}")

        return True


    def auto_configure_fabric_switch(self, spineList, leafList, leafPerRack):
        ''' Add leaf & spine switches to the running-config.
            Usage:
                * Variables
                @{spineList}  00:00:00:00:00:01:00:01  00:00:00:00:00:01:00:02
                @{leafList}  00:00:00:00:00:02:00:01  00:00:00:00:00:02:00:02  00:00:00:00:00:02:00:03  00:00:00:00:00:02:00:04

                Test T5Setup
                    [Tags]  Setup
                    auto configure fabric switch  ${spineList}  ${leafList}  2
        '''

        global leafSwitchList

        Fabric = T5.T5()
        for i, dpid in enumerate(spineList):
            spineName = "spine" + str(i)
            Fabric.rest_add_switch(spineName)
            Fabric.rest_add_dpid(spineName, dpid)
            Fabric.rest_add_fabric_role(spineName, 'spine')

        if (int(leafPerRack) == 1):
            for i, dpid in enumerate(leafList):
                leafName = "leaf" + str(i) + '-a'
                leafSwitchList.append(leafName)
                rackName = "rack" + str(i)
                Fabric.rest_add_switch(leafName)
                Fabric.rest_add_dpid(leafName, dpid)
                Fabric.rest_add_fabric_role(leafName, 'leaf')
        else:

            if (int(leafPerRack) == 2):
                if (len(leafList) % 2 == 0):
                    numRacks = len(leafList) / 2
                    for i in range(0, numRacks):
                        leafName = "leaf" + str(i) + '-a'
                        leafSwitchList.append(leafName)
                        rackName = "rack" + str(i)
                        dpid = leafList[i * 2]
                        Fabric.rest_add_switch(leafName)
                        Fabric.rest_add_dpid(leafName, dpid)
                        Fabric.rest_add_fabric_role(leafName, 'leaf')
                        Fabric.rest_add_leaf_group(leafName, rackName)
                        leafName = "leaf" + str(i) + '-b'
                        leafSwitchList.append(leafName)
                        rackName = "rack" + str(i)
                        dpid = leafList[i * 2 + 1]
                        Fabric.rest_add_switch(leafName)
                        Fabric.rest_add_dpid(leafName, dpid)
                        Fabric.rest_add_fabric_role(leafName, 'leaf')
                        Fabric.rest_add_leaf_group(leafName, rackName)
                else:
                    numRacks = (len(leafList) / 2) + 1
                    for i in range(0, numRacks):
                        leafName = "leaf" + str(i) + '-a'
                        leafSwitchList.append(leafName)
                        rackName = "rack" + str(i)
                        dpid = leafList[i * 2]
                        try:
                            testdpid = leafList[i * 2 + 1]
                            Fabric.rest_add_switch(leafName)
                            Fabric.rest_add_dpid(leafName, dpid)
                            Fabric.rest_add_fabric_role(leafName, 'leaf')
                            Fabric.rest_add_leaf_group(leafName, rackName)

                            leafName = "leaf" + str(i) + '-b'
                            leafSwitchList.append(leafName)
                            rackName = "rack" + str(i)
                            dpid = leafList[i * 2 + 1]
                            Fabric.rest_add_switch(leafName)
                            Fabric.rest_add_dpid(leafName, dpid)
                            Fabric.rest_add_fabric_role(leafName, 'leaf')
                            Fabric.rest_add_leaf_group(leafName, rackName)

                        except:
                            Fabric.rest_add_switch(leafName)
                            Fabric.rest_add_dpid(leafName, dpid)
                            Fabric.rest_add_fabric_role(leafName, 'leaf')
                            Fabric.rest_add_leaf_group(leafName, rackName)



    def auto_delete_fabric_switch(self, spineList, leafList, leafPerRack):
        ''' Delete all the switches in the running-config. Use as running config cleanup function. (teardown)
            Usage:
                * Variables
                @{spineList}  00:00:00:00:00:01:00:01  00:00:00:00:00:01:00:02
                @{leafList}  00:00:00:00:00:02:00:01  00:00:00:00:00:02:00:02  00:00:00:00:00:02:00:03  00:00:00:00:00:02:00:04

                Test T5TearDown
                    [Tags]  Teardown
                    auto delete fabric switch  ${spineList}  ${leafList}  2
        '''

        numSpines = len(spineList)
        numLeaves = len(leafList)

        Fabric = T5.T5()
        for i in range(0, numSpines):
            spineName = 'spine' + str(i)
            Fabric.rest_delete_fabric_switch(spineName)

        if (int(leafPerRack) == 1):
            for i in range(0, int(numLeaves)):
                leafName = "leaf" + str(i) + '-a'
                Fabric.rest_delete_fabric_switch(leafName)

        else:
            if (int(leafPerRack) == 2):
                if (numLeaves % 2 == 0):
                    numRacks = numLeaves / 2
                    for i in range(0, numRacks):
                        leafName = "leaf" + str(i) + '-a'
                        Fabric.rest_delete_fabric_switch(leafName)
                        leafName = "leaf" + str(i) + '-b'
                        Fabric.rest_delete_fabric_switch(leafName)
                else:
                    numRacks = (numLeaves / 2) + 1
                    for i in range(0, numRacks):
                        leafName = "leaf" + str(i) + '-a'
                        Fabric.rest_delete_fabric_switch(leafName)
                        try:
                            leafName = "leaf" + str(i) + '-b'
                            Fabric.rest_delete_fabric_switch(leafName)
                        except:
                            pass


    def auto_delete_fabric_portgroups(self):
        ''' Delete all the port groups in the running-config. Use as running config cleanup function. (teardown)
        '''

        url = "/api/v1/data/controller/applications/bcf/port-group?config=true"
        t = test.Test()
        master = t.controller("master")

        result = master.rest.get(url)['content']

        for pg in result:
            url = '/api/v1/data/controller/applications/bcf/port-group[name="%s"]' % pg['name']
            master.rest.delete(url, {})



    def platform_ping(self, src, dst):
        '''
            Extended mininet_ping function to handle ping failures gracefully for platform HA test cases
            Retry ping 5 times and report failures / Issue Bug reports / Sleeps accordingly
        '''
        global mininetPingFails
        mynet = mininet.Mininet()
        loss = mynet.mininet_ping(src, dst)
        if (loss != '0'):
            # helpers.sleep(5)
            loss = mynet.mininet_ping(src, dst)
            if (loss != '0'):
                if(mininetPingFails == 5):
                    helpers.warn("5 Consecutive Ping Failures: Issuing Mininet-BugReport")
                    # mynet.mininet_bugreport()
                    return False
                helpers.warn("Ping failed between: %s & %s" % (src, dst))
                mininetPingFails += 1
                return True
            else:
                mininetPingFails = 0
                return True
        else:
            mininetPingFails = 0
        return True

    def platform_bash_ping(self, src, dst):
        '''
            Extended bash_ping function to handle ping failures gracefully for platform HA test cases
            Retry ping 5 times and report failures / Issue Bug reports / Sleeps accordingly
        '''
        global hostPingFails
        myhost = Host.Host()
        loss = myhost.bash_ping(src, dst)
        if (loss == '100'):
            helpers.sleep(30)
            loss = myhost.bash_ping(src, dst)
            if (loss == '100'):
                if(hostPingFails == 5):
                    helpers.warn("5 Consecutive Ping Failures: Please collect logs from the physical host")
                    # mynet.mininet_bugreport()
                    return False
                helpers.warn("Ping failed between: %s & %s" % (src, dst))
                hostPingFails += 1
                return True
            else:
                hostPingFails = 0
                return True
        else:
            hostPingFails = 0
        return True



    def do_show_run_vns_verify(self, vnsName, numMembers):
        t = test.Test()
        master = t.controller("master")
        url = "/api/v1/data/controller/applications/bcf/tenant?config=true"
        result = master.rest.get(url)
        helpers.log("Show run output is: %s " % result["content"][0]['vns'][0]['port-group-membership-rules'])
        vnsList = result["content"][0]['vns'][0]['port-group-membership-rules']
        if (len(vnsList) != int(numMembers)):
            helpers.warn("Show run output is not correct for VNS members. Collecting support logs from the mininet")
            mynet = mininet.Mininet()
            out = mynet.mininet_bugreport()
            helpers.log("Bug Report Location is: %s " % out)
            for i in range(0, 2):
                helpers.warn("Show run output is not correct for VNS members. Please collect switch support logs")
                helpers.sleep(30)
        else:
            helpers.log("Show run output is correct for VNS members")




    def getNodeID(self, slaveNode=True):

        '''
        Description:
        -    This function will handout the NodeID's for master & slave nodes

        Objective:
        -    This is designed to be resilient to node failures in HA environments. Eg: If the node is not
            reachable or it's powered down this function will handle the logic

        Inputs:
        |    boolean: slaveNode  |  Whether secondary node is available in the system. Default is True

        Outputs:
        |    If slaveNode: return (masterID, slaveID)
        |    else:    return (masterID)


        '''
        numTries = 0
        t = test.Test()
        master = t.controller("master")


        while(True):
            try:
                showUrl = '/api/v1/data/controller/cluster'
                helpers.log("Master is : %s " % master.name)
                result = master.rest.get(showUrl)['content']
                masterID = result[0]['status']['local-node-id']
                break
            except(KeyError):
                if(numTries < 5):
                    helpers.log("Warning: KeyError detected during master ID retrieval. Sleeping for 10 seconds")
                    helpers.sleep(10)
                    numTries += 1
                else:
                    helpers.log("Error: KeyError detected during master ID retrieval")
                    if slaveNode:
                        return (-1, -1)
                    else:
                        return -1

        if(slaveNode):
            slave = t.controller("slave")
            while(True):
                try:
                    showUrl = '/api/v1/data/controller/cluster'
                    result = slave.rest.get(showUrl)['content']
                    slaveID = result[0]['status']['local-node-id']
                    break
                except(KeyError):
                    if(numTries < 5):
                        helpers.log("Warning: KeyError detected during slave ID retrieval. Sleeping for 10 seconds")
                        helpers.sleep(10)
                        numTries += 1
                    else:
                        helpers.log("Error: KeyError detected during slave ID retrieval")
                        return (-1, -1)


        if(slaveNode):
            return (masterID, slaveID)
        else:
            return masterID



    def rest_configure_virtual_ip(self, vip):
        ''' Function to configure Virtual IP of the cluster via REST
        Input: VIP address
        Output: True if successful, False otherwise
        '''
        t = test.Test()
        c = t.controller('master')

        helpers.log("Input arguments: virtual IP = %s" % vip)
        try:
            url = '/api/v1/data/controller/os/config/global/virtual-ip'
            c.rest.post(url, {"ipv4-address": vip})
        except:
            return False
        else:
            return True


    def rest_delete_virtual_ip(self):
        ''' Function to delete Virtual IP from a controller via REST
        Input: None
        Output: True if successful, False otherwise
        '''
        t = test.Test()
        c = t.controller('master')

        helpers.log("Deleting virtual IP address")
        try:
            url = '/api/v1/data/controller/os/config/global/virtual-ip'
            c.rest.delete(url)
        except:
            return False
        else:
            return True



    def cli_configure_virtual_ip(self, vip):
        ''' Function to show Virtual IP of a controller via CLI
        Input: None
        Output: VIP address if configured, None otherwise
        '''
        t = test.Test()
        c = t.controller('master')

        helpers.test_log("Input arguments: virtual IP = %s" % vip)
        try:
            c.config("controller")
            c.config("virtual-ip %s" % vip)
            assert "Error" not in c.cli_content()
        except:
            helpers.test_log(c.cli_content())
            return False
        else:
            return True


    def cli_get_eth0_ip_using_virtual_ip(self, vip):
        ''' Function to verify that Virtual IP address
        points to some controller via CLI
        Input: VIP address
        Output: Eth0 IP address of the controller that Virtual IP points to
        '''
        t = test.Test()
        c = None
        try:
            if 'master' in vip:
                c = t.controller('master')
            else:
                helpers.log("Spawning VIP %s" % vip)
                c = t.node_spawn(ip=vip)
                helpers.log("Successfully spawned VIP %s" % vip)

            content = c.cli('show local node interfaces ethernet0')['content']
            output = helpers.strip_cli_output(content)
            lines = helpers.str_to_list(output)
            assert "IP Address" in lines[0]
            rows = lines[2].split(' ')
        except:
            helpers.test_failure("Exception info: %s" % helpers.exception_info())
            if c:
                helpers.test_log(c.rest.error())
            return ''
        else:
            return rows[3]


    def cli_show_virtual_ip(self):
        ''' Function to show Virtual IP of a controller via CLI
        Input: None
        Output: VIP address if configured, None otherwise
        '''
        t = test.Test()
        c = t.controller('master')
        try:
            content = c.cli('show controller virtual-ip')['content']
            output = helpers.strip_cli_output(content)
            lines = helpers.str_to_list(output)
            assert(len(lines) == 3)
            assert "ipv4 address" in lines[0]
        except:
            helpers.test_log(c.cli_content())
            return None
        else:
            return lines[2].strip()


    def bash_verify_virtual_ip(self, vip, node='master'):
        ''' Function to show Virtual IP of a controller via CLI/Bash
        Input: None
        Output: VIP address if configured, None otherwise
        '''
        t = test.Test()
        c = t.controller(node)
        try:
            content = c.bash('ip addr')['content']
            output = helpers.strip_cli_output(content)
            if vip not in output:
                helpers.test_log("VIP: %s not configured on %s" % (vip, node))
                return False
        except:
            helpers.test_log(c.cli_content())
            return False
        else:
            helpers.log("VIP: %s is configired on %s" % (vip, node))
            return True


    def cli_delete_virtual_ip(self):
        ''' Function to delete Virtual IP from a controller via CLI
        Input: None
        Output: True if successful, False otherwise
        '''
        t = test.Test()
        c = t.controller('master')

        helpers.test_log("Deleting virtual IP address")
        try:
            c.config("controller")
            c.config("no virtual-ip")
        except:
            helpers.test_log(c.cli_content())
            return False
        else:
            return True


    def rest_get_mac_using_virtual_ip(self, vip):
        ''' Function to verify that Virtual IP address
        points to some controller via REST
        Input: VIP address
        Output: Mac address of the controller that Virtual IP points to
        '''
        t = test.Test()
        c = None
        try:
            if 'master' in vip:
                c = t.controller('master')
            else:
                helpers.log("Spawning VIP %s" % vip)
                c = t.node_spawn(ip=vip)
                helpers.log("Successfully spawned VIP %s" % vip)

            helpers.log("Getting MAC address of the controller")
            url = '/api/v1/data/controller/os/action/interface'
            c.rest.get(url)
            content = c.rest.content()
        except:
            helpers.test_failure("Exception info: %s" % helpers.exception_info())
            if c:
                helpers.test_log(c.rest.error())
            return ''
        else:
            return content[0]['hardware-address']


    def rest_show_virtual_ip(self):
        ''' Function to show Virtual IP of a controller via REST
        Input: None
        Output: VIP address if configured, None otherwise
        '''
        t = test.Test()
        c = t.controller('master')

        helpers.log("Getting virtual IP address")
        try:
            url = '/api/v1/data/controller/os/config/global/virtual-ip'
            c.rest.get(url)
            content = c.rest.content()
        except:
            helpers.test_failure(c.rest.error())
            return False
        else:
            if len(content[0]) > 0:
                return content[0]['ipv4-address']
            else:
                return None


    def rest_add_monitor_session(self, sessionID, srcSwitch, srcInt, dstSwitch, dstInt, **kwargs):
        '''
            Add a monitor session (SPAN) to the switch
            Inputs: sessionID - Session ID for the monitor session
                    srcSwitch/Int - Source switch & interface
                    dstSwitch/Int - Destination switch & interface
            Returns:
                True - If the configuration went through without any errors
                False - If the configuration action fails
        '''

        t = test.Test()
        master = t.controller("master")

        url = '/api/v1/data/controller/applications/bcf/monitor-session[id=%s]' % (sessionID)

        master.rest.put(url, {"id": sessionID})

        matchSpec = {}
        if ("src-mac" in kwargs):
            matchSpec["src-mac"] = kwargs.get('src-mac')
        if("src-ip-cidr" in kwargs):
            matchSpec['src-ip-cidr'] = kwargs.get('src-ip-cidr')
        if("src-tp-port" in kwargs):
            matchSpec["src-tp-port"] = kwargs.get('src-tp-port')
        if("dst-mac" in kwargs):
            matchSpec["dst-mac"] = kwargs.get('dst-mac')
        if("dst-ip-cidr" in kwargs):
            matchSpec['dst-ip-cidr'] = kwargs.get('dst-ip-cidr')
        if("dst-tp-port" in kwargs):
            matchSpec["dst-tp-port"] = kwargs.get('dst-tp-port')
        if("ip-dscp" in kwargs):
            matchSpec["ip-dscp"] = kwargs.get('ip-dscp')
        if("ip-ecn" in kwargs):
            matchSpec["ip-ecn"] = kwargs.get('ip-ecn')
        if("ip-proto" in kwargs):
            matchSpec["ip-proto"] = kwargs.get('ip-proto')
        if("ether-type" in kwargs):
            matchSpec["ether-type"] = kwargs.get('ether-type')

        helpers.log("matchSpec is: %s" % matchSpec)

        url = '/api/v1/data/controller/applications/bcf/monitor-session[id=%s]/source[switch-name="%s"][interface-name="%s"]' % (sessionID, srcSwitch, srcInt)

        if (matchSpec):
            result = master.rest.put(url, {"match-specification": matchSpec, "direction": "ingress", "switch-name": srcSwitch, "interface-name": srcInt})
        else:
            result = master.rest.put(url, {"direction": kwargs.get("direction"), "switch-name": srcSwitch , "interface-name": srcInt})


        url = '/api/v1/data/controller/applications/bcf/monitor-session[id=%s]/destination[switch-name="%s"][interface-name="%s"]' % (sessionID, dstSwitch, dstInt)
        result = master.rest.put(url, {"switch-name": srcSwitch , "interface-name": dstInt})


        if master.rest.status_code_ok():
            return True
        else:
            return False


    def rest_activate_monitor_session(self, sessionID):

        t = test.Test()
        master = t.controller("master")
        url = '/api/v1/data/controller/applications/bcf/monitor-session[id=%s]' % (sessionID)

        master.rest.patch(url, {"active": 'true'})

        if master.rest.status_code_ok():
                return True
        else:
                return False


    def rest_deactivate_monitor_session(self, sessionID):
        t = test.Test()
        master = t.controller("master")

        url = '/api/v1/data/controller/applications/bcf/monitor-session[id=%s]/active' % (sessionID)

        master.rest.delete(url)

        if master.rest.status_code_ok():
                return True
        else:
                return False


    def rest_delete_monitor_session(self, sessionID):

        t = test.Test()
        master = t.controller("master")
        url = '/api/v1/data/controller/applications/bcf/monitor-session[id=%s]' % (sessionID)

        master.rest.delete(url, {"id": sessionID})

        if master.rest.status_code_ok():
            return True
        else:
            return False


    def rest_verify_monitor_session(self, sessionID, srcSwitch, srcInt, dstSwitch, dstInt, **kwargs):
        '''
            Verify a monitor session (SPAN) in the switch. This uses "show run monitor-session" command
            for the verification
            Inputs: sessionID - Session ID for the monitor session
                    srcSwitch/Int - Source switch & interface
                    dstSwitch/Int - Destination switch & interface
            Returns:
                True - If the session exits
                False - If the session doesn't exists
        '''

        t = test.Test()
        master = t.controller("master")

        foundSession = False
        url = "/api/v1/data/controller/applications/bcf/monitor-session?config=true"
        result = master.rest.get(url)['content']

        try:
            for session in result:
                if (str(session['id']) == sessionID):
                    foundSession = True
                    if(session['source'][0]['switch-name'] != srcSwitch):
                        helpers.log("Wrong source switch in the monitor session %s : %s" % (sessionID, srcSwitch))
                        return False
                    if(session['source'][0]['interface-name'] != srcInt):
                        helpers.log("Wrong source interface in the monitor session %s : %s" % (sessionID, srcInt))
                        return False
                    if(session['source'][0]['direction'] != kwargs.get('direction')):
                        helpers.log("Wrong source interface direction in the monitor session %s : %s: %s" % (sessionID, srcInt, kwargs.get('direction')))
                        return False
                    if(session['destination'][0]['switch-name'] != dstSwitch):
                        helpers.log("Wrong destination switch in the monitor session %s : %s" % (sessionID, dstSwitch))
                        return False
                    if(session['destination'][0]['interface-name'] != dstInt):
                        helpers.log("Wrong destination interface in the monitor session %s : %s" % (sessionID, dstInt))
                        return False
                    if ('src-mac') in kwargs:
                        if((session['source'][0]['match-specification'])['src-mac'] != kwargs.get('src-mac')):
                            helpers.log("Wrong src-mac in the monitor session %s : %s: %s" % (sessionID, srcInt, kwargs.get('src-mac')))
                            return False
                    if ('src-ip-cidr') in kwargs:
                        if((session['source'][0]['match-specification'])['src-ip-cidr'] != kwargs.get('src-ip-cidr')):
                            helpers.log("Wrong src-ip-cidr in the monitor session %s : %s: %s" % (sessionID, srcInt, kwargs.get('src-ip-cidr')))
                            return False
                    if ('src-tp-port') in kwargs:
                        if(str((session['source'][0]['match-specification'])['src-tp-port']) != kwargs.get('src-tp-port')):
                            helpers.log("Wrong src-tp-port in the monitor session %s : %s: %s" % (sessionID, srcInt, kwargs.get('src-tp-port')))
                            return False
                    if ('dst-mac') in kwargs:
                        if((session['source'][0]['match-specification'])['dst-mac'] != kwargs.get('dst-mac')):
                            helpers.log("Wrong dst-mac in the monitor session %s : %s: %s" % (sessionID, srcInt, kwargs.get('dst-mac')))
                            return False
                    if ('dst-ip-cidr') in kwargs:
                        if((session['source'][0]['match-specification'])['dst-ip-cidr'] != kwargs.get('dst-ip-cidr')):
                            helpers.log("Wrong dst-ip-cidr in the monitor session %s : %s: %s" % (sessionID, srcInt, kwargs.get('dst-ip-cidr')))
                            return False
                    if ('dst-tp-port') in kwargs:
                        if(str((session['source'][0]['match-specification'])['dst-tp-port']) != kwargs.get('dst-tp-port')):
                            helpers.log("Wrong dst-tp-port in the monitor session %s : %s: %s" % (sessionID, srcInt, kwargs.get('dst-tp-port')))
                            return False
                    if ('ip-dscp') in kwargs:
                        if((session['source'][0]['match-specification'])['ip-dscp'] != int(kwargs.get('ip-dscp'))):
                            helpers.log("Wrong ip-dscp in the monitor session %s : %s: %s" % (sessionID, srcInt, kwargs.get('ip-dscp')))
                            return False
                    if ('ip-ecn') in kwargs:
                        if((session['source'][0]['match-specification'])['ip-ecn'] != int(kwargs.get('ip-ecn'))):
                            helpers.log("Wrong ip-ecn in the monitor session %s : %s: %s" % (sessionID, srcInt, kwargs.get('ip-ecn')))
                            return False
                    if ('ip-proto') in kwargs:
                        if((session['source'][0]['match-specification'])['ip-proto'] != (kwargs.get('ip-proto'))):
                            helpers.log("Wrong ip-proto in the monitor session %s : %s: %s" % (sessionID, srcInt, kwargs.get('ip-proto')))
                            return False
                    if ('ether-type') in kwargs:
                        if((session['source'][0]['match-specification'])['ether-type'] != int(kwargs.get('ether-type'))):
                            helpers.log("Wrong ether-type in the monitor session %s : %s: %s" % (sessionID, srcInt, kwargs.get('ether-type')))
                            return False
                    pass

        except(KeyError):
            helpers.warn("KeyError detected: One of the fields are missing from the monitor session")
            helpers.log(session)
            return False

        if(foundSession):
            return True
        else:
            helpers.log("Monitor session is not found in the running config")
            return False



    def verify_ping_with_tcpdump(self, host, ipAddr, verifyHost, verifyInt, *args):

        ''' This function will issue a ping request and verify it through the TCP dump.

        Input:  host -> hostname from the topo file
                ipAddr -> Destination IP address of that ping request should go
                verifyHost -> Host where tcpdump is being executed
                verifyInt -> interfaces of the host that tcpdump would get excuted
                verifyString -> String to search in the tcpdump output
        '''

        t = test.Test()
        n = t.node(verifyHost)

        verifyString = ""
        for arg in args:
            verifyString += '.*' + arg
        verifyString += '.*'
        # Issue a tcpdump & make sure there's no traffic already matching "verifyString" is receiving
        output = n.bash("timeout 5 tcpdump -i %s" % verifyInt)
        match = re.search(r"%s" % verifyString, output['content'], re.S | re.I)

        if match:
            helpers.log("verifyString is: %s" % verifyString)
            helpers.log("Found it on the tcpdump output before issueing a ping: %s" % output['content'])
            return False

        else:
            # Schedule a different thread to execute the ping. Ping will be executed for 10 packets
            pingThread = T5PlatformThreads(1, "hostPing", host=host, IP=ipAddr)
            helpers.log("Starting ping thread to ping from %s to destIP: %s" % (host, ipAddr))
            pingThread.start()


            output = n.bash("timeout 5 tcpdump -i %s" % verifyInt)
            verifyStringFound = re.search(r"%s" % verifyString, output['content'], re.S | re.I)

            pingThread.join()

            if verifyStringFound:
                return True
            else:
                helpers.log("TCPDump match not found for string: %s" % verifyString)
                return False


    def verify_traffic_with_tcpdump(self, verifyHost, verifyInt, verifyOptions, *args):

        ''' This function will verify the traffic through TCP dump.

        Input:
                verifyHost -> Host where tcpdump is being executed
                verifyInt -> interfaces of the host that tcpdump would get excuted
                verifyOptions -> Other TCP Dump options (eg: src port 8000 and tcp)
                verifyString -> String to search in the tcpdump output
        '''

        t = test.Test()
        n = t.node(verifyHost)

        verifyString = ""
        for arg in args:
            verifyString += '.*' + arg
        verifyString += '.*'
        # Issue tcpdump & look for the intended traffic that matches verifyString
        output = n.bash("timeout 5 tcpdump -i %s %s" % (verifyInt, verifyOptions))
        match = re.search(r"%s" % verifyString, output['content'], re.S | re.I)

        if match:
            return True

        else:
            helpers.log("TCPDump match not found for string: %s" % verifyString)
            return False


    def cli_compare(self, node, left=None, right=None,
                    scp_passwd='bsn', soft_error=False):
        """
        Generic function to compare via CLI, also using using SCP
        Input <left> and <right> arguments exactly the same way as you
        would do it in CLI's 'compare' command.

        Inputs:
        | left | Left object for comparison
        | right | Right object for comparison
        | node | Reference to switch/controller as defined in .topo file |
        | scp_passwd | Password for scp connection |
        | soft_error | Soft Error flag |

        Examples:
        | Cli Compare | slave | test-file | scp://bsn@regress:path-to-file/file
        | Cli Compare | master | test-file | snapshot://test-config
        | Cli Compare | master | running-config |  test-file

        Return Value:
        - List of lines, in which <left> and <right> are different
        """
        if not right or not left:
            return helpers.test_error("You need to specify values for 'right'"
                                      " and 'left' arguments.")
        helpers.test_log("Running command:\ncompare %s %s" % (left, right))
        t = test.Test()
        c = t.controller(node)
        c.config("config")
        c.send("compare %s %s" % (left, right))
        options = c.expect([r'[Pp]assword: ', r'\(yes/no\)\?', c.get_prompt()])
        content = c.cli_content()
        helpers.log("*****Output is :\n%s" % content)
        try:
            if (('Could not resolve' in content) or ('Error' in content)
                or ('No such file or directory' in content)):
                return helpers.test_failure(content, soft_error)
            elif options[0] == 0 :
                helpers.log("need to provide passwd")
                output = c.config(scp_passwd)['content']
            elif options[0] == 1:
                helpers.log("need to send yes, then provide passwd")
                c.send('yes')
                c.expect(r'[Pp]assword:')
                output = c.config(scp_passwd)['content']
        except:
            return helpers.test_failure(c.cli_content(), soft_error)

        output = c.cli_content()
        helpers.log("Output *** %s " % output)
        if ("Error" in output) or ('No such file or directory' in output):
            return helpers.test_failure(c.cli_content(), soft_error)

        output = helpers.strip_cli_output(output)
        output = helpers.str_to_list(output)
        if len(output) > 2:
            if "compare" in output[0]:
                helpers.log("Skipping command that is still in first line")
                output = output[1:]
        if options[0] < 2:
            for index, line in enumerate(output):
                if '100%' in line:
                    output = output[(index + 1):]
                    break

        helpers.log("Cropped output *** %s " % output)

        differences = []
        if len(output) == 0:
            helpers.log("Files are identical")
            return differences

        for line in output:
            if re.match(r'[0-9].*|< \!|---|> \!|< \Z|> \Z|\Z', line):
                helpers.log("OK: %s" % line)
            elif (re.match(r'[<>]   hostname|[<>]     ip', line)
                  and node == 'slave'):
                helpers.log("OK: %s" % line)
            else:
                helpers.log("files different at line:\n%s" % line)
                differences.append(line)

        if helpers.any_match(c.cli_content(), r'Error'):
            return helpers.test_failure(c.cli_content(), soft_error)

        return differences


    def cli_copy(self, src, dst, node='master', scp_passwd='bsn'):
        ''' Generic function to copy via CLI, using SCP
        Input:
        Src, Dst - source and destination of copy command
        Scp_Password - password for scp connection
        Node - pointing to Master or Slave controller
        Output: True if successful, False otherwise
        '''
        helpers.test_log("Running command:\ncopy %s %s" % (src, dst))
        t = test.Test()
        c = t.controller(node)
        c.config("")
        c.send("copy %s %s" % (src, dst))
        options = c.expect([r'[Pp]assword: ', r'\(yes/no\)\?', c.get_prompt()],
                           timeout=45)
        content = c.cli_content()
        helpers.log("*****Output is :\n%s" % content)
        if  ('Could not resolve' in content) or ('Error' in content) or ('No such file or directory' in content):
            helpers.test_failure(content)
            return False

        if options[0] < 2:
            if options[0] == 0 :
                helpers.log("INFO:  need to provide passwd ")
                c.send(scp_passwd)
            elif options[0] == 1:
                helpers.log("INFO:  need to send yes, then provide passwd ")
                c.send('yes')
                c.expect(r'[Pp]assword:')
                c.send(scp_passwd)
            try:
                c.expect(c.get_prompt(), timeout=180)
                if not (helpers.any_match(c.cli_content(), r'100%') or helpers.any_match(c.cli_content(), r'applied \d+ updates') or helpers.any_match(c.cli_content(), r'Lines Applied')):
                    helpers.test_failure(c.cli_content())
                    return False
            except:
                helpers.log('scp failed')
                helpers.test_failure(c.cli_content())
                return False
            else:
                helpers.log('scp completed successfully')
        else:
            c.config("config")

        content = c.cli_content()
        if helpers.any_match(content, r'Error') or  helpers.any_match(content, r'input stream empty') or \
        helpers.any_match(content, r'Lines Applied\: None') or helpers.any_match(content, r'Preserving Session'):
            helpers.test_failure(c.cli_content())
            return False
        return True


    def cli_compare_running_config_with_file_line_by_line(self, filename):
        ''' Function to compare current running config with
        config saved in a file, via CLI line by line
        Input: Filename
        Output: True if successful, False otherwise
        '''
        helpers.test_log("Comparing output of 'show running-config' with 'show file %s'" % filename)
        t = test.Test()
        c = t.controller('master')

        if re.match(r'file://.*', filename):
            name = re.split(r'file://', filename)
            filename = name[1]
        try:
            rc = c.config("show running-config")['content']
            if "Error" in c.cli_content():
                helpers.log("Error in CLI content")
                return False
            rc = helpers.strip_cli_output(rc)
            rc = helpers.str_to_list(rc)
            config_file = c.config("show file %s" % filename)['content']
            if "Error" in c.cli_content():
                helpers.log("Error in CLI content")
                return False
            config_file = helpers.strip_cli_output(config_file)
            config_file = helpers.str_to_list(config_file)

            if not len(rc) == len(config_file):
                helpers.log("Length of RC is different than lenght of RC in file")
                return False
            for index, line in enumerate(rc):
                helpers.log("Comparing '%s' and '%s'" % (line, config_file[index]))
                if 'Current Time' in line:
                    assert 'Current Time' in config_file[index]
                    continue
                if not line == config_file[index]:
                    helpers.log("difference")
                    return False
        except:
            helpers.test_log(c.cli_content())
            return False
        else:
            return True


    def cli_compare_running_config_with_snapshot_line_by_line(self, filename):
        ''' Function to compare current running config with
        snapshot saved in snapshot://, via CLI line by line
        Input: Filename
        Output: True if successful, False otherwise
        '''
        helpers.test_log("Comparing output of 'show running-config' with 'show snapshot %s'" % filename)
        t = test.Test()
        c = t.controller('master')
        try:
            rc = c.config("show running-config")['content']
            if "Error" in c.cli_content():
                helpers.log("Error in CLI content")
                return False
            rc = helpers.strip_cli_output(rc)
            rc = helpers.str_to_list(rc)
            snapshot_file = c.config("show snapshot %s" % filename)['content']
            if "Error" in c.cli_content():
                helpers.log("Error in CLI content")
                return False
            snapshot_file = helpers.strip_cli_output(snapshot_file)
            snapshot_file = helpers.str_to_list(snapshot_file)

            helpers.log("length is %s" % len(rc))
            helpers.log("length is %s" % len(snapshot_file))
            # Cropping headers of the outputs
            rc = rc[4:]
            snapshot_file = snapshot_file[8:]

            if not len(rc) == len(snapshot_file):
                helpers.log("Length of RC is different than lenght of RC in snapshot")
                return False
            for index, line in enumerate(rc):
                helpers.log("Comparing '%s' and '%s'" % (line, snapshot_file[index]))
                if not line == snapshot_file[index]:
                    helpers.log("difference")
                    return False
        except:
            helpers.test_log(c.cli_content())
            return False
        else:
            return True

    def cli_delete(self, filename):
        ''' Function to delete file
        via CLI
        Input: Filename
        Output: True if successful, False otherwise
        '''

        if re.match(r'image://.*', filename):
            name = re.split(r'image://', filename)
            cmd = "delete image %s" % name[1]
        elif re.match(r'snapshot://.*', filename):
            name = re.split(r'snapshot://', filename)
            cmd = "delete snapshot %s" % name[1]
        elif re.match(r'file://.*', filename):
            name = re.split(r'file://', filename)
            cmd = "delete file %s" % name[1]
        else:
            cmd = "delete file %s" % filename

        helpers.test_log("Running command:\n%s" % cmd)
        t = test.Test()
        c = t.controller('master')
        if re.match(r'snapshot://.*', filename) or re.match(r'image://.*', filename) :
            helpers.test_log("Deleting snapshot:// or image://, expecting confirmation prompt")
            c.config("config")
            c.send(cmd)
            c.expect(r'[\r\n].+continue+.*|Error.*')
            if 'Error' in c.cli_content():
                helpers.test_failure(c.cli_content())
                return False
            c.config("yes")
        else:
            helpers.test_log("Deleting file")
            c.config(cmd)
        if helpers.any_match(c.cli_content(), r'Error'):
            helpers.test_failure(c.cli_content())
            return False
        return True


    def bash_clear_known_hosts(self):
        ''' Function to delete known SSH RSA keys
        via CLI/BASH
        Output: True if successful, False otherwise
        '''
        helpers.test_log("Running command:\ndebug bash; > .ssh/known_hosts")
        t = test.Test()
        c = t.controller('master')
        try:
            c.config("config")
            c.bash("> .ssh/known_hosts")
            c.config("config")
            if "Error" in c.cli_content():
                helpers.log("Error in CLI content")
                return False
        except:
            helpers.test_log(c.cli_content())
            return False
        else:
            return True

    def copy_pkg_from_jenkins(self, node='master', check=True):
        '''
          copy the latest upgrade package from Jenkin
          Author: Mingtao
          input:  node  - controller to copy the image,
                          master, slave, c1 c2
          usage:
              check: True, if there is a image, will not copy
          output: image build

        '''
        t = test.Test()
        c = t.controller(node)
        if check is True:
            (num, image) = self.cli_check_image(node)
            helpers.log('INFO: *******system image is: %s ' % image)
        else:
            num = -1

        if str(num) == '-1':
            helpers.log("INFO: system NOT have image, or ignore check,   will copy image")
            c.config('')
#            string = 'copy "scp://bsn@jenkins:/var/lib/jenkins/jobs/bvs master/lastSuccessful/archive/target/appliance/images/bvs/controller-upgrade-bvs-*-SNAPSHOT.pkg"'
            string = 'copy "scp://bsn@jenkins:/var/lib/jenkins/jobs/bcf_master/builds/2060/archive/controller-upgrade-*-SNAPSHOT.pkg"'
            c.send(string + ' image://')
#            c.expect(r'[\r\n].+password: ')

            options = c.expect([r'[\r\n].+password: ', r'[\r\n].+yes/no'])

            if options[0] == 0:
                helpers.log("INFO:  need to provide passwd ")
                c.send('bsn')
            if options[0] == 1:
                helpers.log("INFO:  need to send yes, then provide passwd ")
                c.send('yes')
                c.expect(r'[\r\n].+password: ')
                c.send('bsn')

            content = c.cli_content()
            helpers.log("*****Output is :\n%s" % content)


            try:
                c.expect(timeout=300)
            except:
                helpers.log('scp failed')
                return False
            else:
                helpers.log('scp completed successfully')
                (num, image) = self.cli_check_image(node)
                if num == -1:
                    helpers.log('there is still no image')
                    return False

        else:
            helpers.log("INFO: system has image: %s, will not copy image again" % image)

        return image

    def copy_pkg_from_server(self, src, node='master', passwd='bsn', soft_error=False):
        '''
          copy the a upgrade package from server
          Author: Mingtao
          input:  node  - controller to copy the image,
                          master, slave, c1 c2
          usage:
              copy_pkg_from_server  bsn@qa-kvm-32:/home/mingtao/bigtap-3.0.0-upgrade-2014.02.27.1852.pkg
              soft_error:  True, handle negative case
          output: image build

        '''
        t = test.Test()
        c = t.controller(node)

        c.config('')
        string = 'copy scp://' + src
        c.send(string + ' image://')

        options = c.expect([r'[\r\n].+password: ', r'[\r\n].+yes/no'])

        if options[0] == 0:
            helpers.log("INFO:  need to provide passwd ")
            c.send(passwd)
        if options[0] == 1:
            helpers.log("INFO:  need to send yes, then provide passwd ")
            c.send('yes')
            c.expect(r'[\r\n].+password: ')
            c.send(passwd)

        content = c.cli_content()
        helpers.log("*****Output is :\n%s" % content)

        try:
            c.expect(timeout=180)
        except:
            helpers.log('scp failed')
            return False
        else:
            helpers.log('scp completed successfully')
            content = c.cli_content()
            temp = helpers.strip_cli_output(content)
            temp = helpers.str_to_list(temp)
            helpers.log("USR INFO:   list   is :\n%s" % temp)
            line = temp[-1]
            helpers.log("USR INFO:  line is :\n%s" % line)
            if re.match(r'Error:.*', line) and not re.match(r'.*already exists.*', line):
                helpers.log("Error: %s" % line)
                if soft_error:
                    return ("Error: %s" % line)
                else:
                    helpers.test_failure("Error: %s" % line)
            elif re.match(r'Image added:.* build: (\d+)', line):
                helpers.log("image added")
                match = re.match(r'Image added:.* build: (\d+)', line)
                helpers.log("USR INFO: image is: %s" % match.group(1))
                image = match.group(1)
            elif  re.match(r'.*already exists.*', line):
                helpers.log("image already exists")
                match = re.match(r'.* (\d+):.* already exists.*', line)
                helpers.log("USR INFO: image is : %s" % match.group(1))
                image = match.group(1)

            else:
                (num, images) = self.cli_check_image(node)
                image = max(images)

        return image

    def copy_pkg_from_file(self, src, node='master', soft_error=False):
        '''
          copy the a upgrade package from controller file
          Author: Mingtao
          input:  node  - controller to copy the image,
                          master, slave, c1 c2
          usage:
              copy_pkg_from_file  file/bigtap-3.0.0-upgrade-2014.02.27.1852.pkg
              soft_error:  True, handle negative case
          output: image build

        '''
        t = test.Test()
        c = t.controller(node)

        c.config('')
        string = 'copy ' + src + ' image://'
        c.send(string)

        try:
            c.expect(timeout=180)
        except:
            helpers.log('USER ERROR: copy image failed')
            return False
        else:

            content = c.cli_content()
            temp = helpers.strip_cli_output(content)
            temp = helpers.str_to_list(temp)
            helpers.log("USR INFO:   list   is :\n%s" % temp)
            line = temp[-1]
            helpers.log("USR INFO:  line is :\n%s" % line)
            if re.match(r'Error:.*', line) and not re.match(r'.*already exists.*', line):
                helpers.log("Error: %s" % line)
                if soft_error:
                    return ("Error: %s" % line)
                else:
                    helpers.test_failure("Error: %s" % line)
            elif re.match(r'Image added:.* build: (\d+)', line):
                helpers.log("image added")
                match = re.match(r'Image added:.* build: (\d+)', line)
                helpers.log("USR INFO: image is: %s" % match.group(1))
                image = match.group(1)
            elif  re.match(r'.*already exists.*', line):
                helpers.log("image already exists")
                match = re.match(r'.* (\d+):.* already exists.*', line)
                helpers.log("USR INFO: image is : %s" % match.group(1))
                image = match.group(1)

            else:
                (num, images) = self.cli_check_image(node)
                image = max(images)

        return image

    def cli_check_image(self, node='master', soft_error=False):
        '''
          check image available in the system "show image"
          Author: Mingtao
          input:  node  - controller
                          master, slave, c1 c2
          usage:  ${num}  ${image}=      cli_check_image
          output: ${num - the number of images
                ${image}   - the image build in a list
        '''

        t = test.Test()
        c = t.controller(node)
        helpers.log('INFO: Entering ==> check_image with soft_error: %s' % str(soft_error))

        c.enable("show image")
        content = c.cli_content()
        helpers.log("*****Output is :\n%s" % content)
        temp = helpers.strip_cli_output(content)
        temp = helpers.str_to_list(temp)
        helpers.log("*****Output list   is :\n%s" % temp)
        if re.match(r'Error:.*', temp[0]):
            helpers.log("Error: %s" % temp[0])
            if soft_error:
                return False
            else:
                helpers.test_failure("Error: %s" % temp)

        if len(temp) == 1 and 'None.' in temp:
            helpers.log("INFO:  ***image is not in controller******")
            num = -1
            images = []

        else:
            temp.pop(0);temp.pop(0)
            helpers.log("INFO:  ***image is available: %s" % temp)

            num = len(temp)
            images = []
            for line in temp:
                line = line.split()
                image = line[3]
                helpers.log("INFO: ***image is available: %s" % image)
                images.append(image)
            helpers.log("INFO:  ***image is available: %s" % images)

        return num, images


    def cli_delete_image(self, node='master', image=None):
        '''
          delete image  in system
          Author: Mingtao
          input:  node  - controller
                          master, slave, c1 c2
                  image - build number to be deleted
                          None - delete all the images
          usage:
          output: ${num - the number of images
                  ${image}   - the image build in a list
        '''

        t = test.Test()
        c = t.controller(node)
        helpers.log('INFO: Entering ==> cli_delete_image  ')
        (_, images) = self.cli_check_image(node)
        if image is None:
            for image in images:
                c.config('')
                c.send('delete image %s' % image)
                c.expect(r".*: ")
                c.send('yes')
                c.expect()
            (newnum, newimages) = self.cli_check_image(node)
            if newnum != -1:
                helpers.log('Error:  not all the images are deleted  ')
                return False
        else:
            if image in images:
                c.config('')
                c.send('delete image %s' % image)
                c.expect(r".*: ")
                c.send('yes')
                c.expect()
                (_, newimages) = self.cli_check_image(node)
                if image in newimages:
                    helpers.log('Error: images: %s is NOT deleted' % image)
                    return False
            else:
                helpers.log("INFO: image: %s not in controller" % image)

        return True


    def cli_upgrade_stage(self, node='master', image=None):
        '''
          upgrade stage  -  2 step of upgrade
          Author: Mingtao
          input:  node  - controller
                          master, slave, c1 c2
                  image - build number to be staged
                          None - pick the biggest build number
          usage:
          output: True  - upgrade staged successfully
                  False  -upgrade staged Not successfully
        '''
        t = test.Test()
        c = t.controller(node)
        helpers.log('INFO: Entering ==> cli_upgrade_stage')

        c.enable('')
        if image is None:
            (num, images) = self.cli_check_image(node)
            if num == 1:
                c.send('upgrade stage')
            else:
                image = max(images)
                c.send('upgrade stage ' + image)
        else:
            c.send('upgrade stage ' + image)
        options = c.expect([r'[\r\n].*to continue.*', r'.* currently staged on alternate partition', c.get_prompt()])

        if options[0] == 1:
            helpers.log('USER INFO:  image is staged already,  stage again ... ')
#            return True
        elif options[0] == 0:
            c.send("yes")
        elif options[0] == 2:
            return True

        options = c.expect([r'[\r\n].*to continue.*', r'.*copying image into alternate partition', c.get_prompt()])
        if options[0] == 0:
            c.send("yes")
            newoptions = c.expect([r'[\r\n].*to continue.*', r'.*copying image into alternate partition', c.get_prompt()])
            if newoptions[0] == 0:
                c.send("yes")
            elif newoptions[0] == 2:
                return True
        elif options[0] == 2:
            return True

        try:
            c.expect(timeout=900)
        except:
            helpers.log('stage did not finish within 180 second ')
            return False
        else:
            content = c.cli_content()
            helpers.log("INFO:*****Content Output is :\n%s" % content)
            temp = helpers.str_to_list(content)
            helpers.log("INFO:*****temp Output is :\n%s" % temp)
            for line in temp:
                helpers.log("line is : %s" % line)
                if re.match(r'Upgrade stage: Upgrade Staged', line):
                    helpers.log('stage completed successfully')
                    return True
        return False


    def cli_upgrade_stage_negative(self, node='master', breakpoint='yes'):
        '''
          upgrade stage  -  2 step of upgrade
          Author: Mingtao
          input:  node  - controller
                          master, slave, c1 c2
                  breakpoint -  yes or ctrl-c
          usage:
          output: True  - upgrade staged successfully
                  False  -upgrade staged Not successfully
        '''
        t = test.Test()
        c = t.controller(node)
        helpers.log('INFO: Entering ==> cli_upgrade_stage_negative')

        c.config('')
        c.send('upgrade stage')
        options = c.expect(r'[\r\n].*to continue.*')
        if breakpoint == 'yes':
            c.send("no")
            helpers.log('INFO: send NO to break the stage')
            c.expect(timeout=900)
            return True

        c.send("yes")

        c.expect([r'.* copying image into alternate partition', r'.*to continue.*'], timeout=900)
        if options[0] == 1:
            c.send("yes")
            c.expect(r'.* copying image into alternate partition', timeout=900)

        if breakpoint.lower() == 'ctrl-c':
            c.send(helpers.ctrl('c'))
            helpers.summary_log('Ctrl C is hit during stage')
            c.expect(timeout=900)
            return True
        return True


    def cli_upgrade_launch(self, node='master', option='', soft_error=False):
        '''
          upgrade launch  -  3 step of upgrade  - this is for single node upgrade
          Author: Mingtao
          input:  node  - controller
                          master, slave, c1 c2

          usage:
          output: True  - upgrade launched successfully
                  False  -upgrade launched Not successfully
        '''

        t = test.Test()
        c = t.controller(node)
        helpers.log('INFO: Entering ==> cli_upgrade_launch ')
        c.config('')
        string = 'upgrade launch ' + option
#        c.send('upgrade launch')
        c.send(string)
        options = c.expect([r'[\r\n].+ \("y" or "yes" to continue\):', c.get_prompt()], timeout=180)

        if options[0] == 1:
            content = c.cli_content()
            helpers.log("*****Output is :\n%s" % content)
            temp = helpers.strip_cli_output(content)
            temp = helpers.str_to_list(temp)
            helpers.log("USR INFO:   list   is :\n%s" % temp)
            line = temp[-1]
            helpers.log("USR INFO:  line is :\n%s" % line)
            if re.match(r'Error:.*', line):
                helpers.log("Error: %s" % line)
                if soft_error:
                    return line
                else:
                    helpers.test_failure("Error: %s" % line)
            elif soft_error:
                return line
            else:
                return False

        c.send("yes")
        options = c.expect([r'fabric is redundant', r'.*\("y" or "yes" to continue\):'])
        content = c.cli_content()
        helpers.log("USER INFO: the content:  %s" % content)
        if options[0] == 1:
            c.send("yes")

        try:
            c.expect(r'[\r\n].+[R|r]ebooting.*', timeout=300)
            content = c.cli_content()
            helpers.log("*****Output is :\n%s" % content)
        except:
            helpers.log('ERROR: upgrade launch NOT successfully')
            return False
        else:
            helpers.log('INFO: upgrade launch  successfully')
            # modify the idle time out TBD Mingtao
            helpers.log("INFO: Node - %s is rebooting" % c.name())
            helpers.sleep(60)
            if self.verify_controller_reachable(node):
                helpers.log("INFO: Node - %s is UP - Wating for it to come to full function" % c.name())
                helpers.sleep(60)
                helpers.log("Node reconnect for '%s'" % c.name())
                c = t.node_reconnect(c.name())
                c.enable('show switch')
                t.cli_add_controller_idle_and_reauth_timeout(c.name(), reconfig_reauth=False)

            return True
        return False



    def cli_take_snapshot(self, node='master', run_config=None, local_node=None, fabric_switch=None, filepath=None):
        '''
          take snapshot of the system, can only take snapshot one by one
          Author: Mingtao
          input:  node  - controller
                          master, slave, c1 c2
                  run_config   - runnning config
                  fabric_switch  -  show fabric switch
                  filepath -  file infos in the filepath
          usage:
          output: "show running-config" or "show fabric_switch" or "ls "

        '''
        t = test.Test()
        c = t.controller(node)
        helpers.log('INFO: Entering ==> cli_take_sanpshot')
        host = Host.Host()

        if run_config:
            c.enable('show running-config')
            content = c.cli_content()
            helpers.log("********content in string:************\n%s" % content)
            temp = helpers.strip_cli_output(content)
            temp = helpers.str_to_list(temp)
            helpers.log("********content is list************\n%s" % helpers.prettify(temp))
            config = temp[6:]
            content = '\n'.join(config)
            helpers.log("********config :************\n%s" % content)
            new_content = re.sub(r'\s+hashed-password.*$', '\n  remove-passwd', content, flags=re.M)
            if local_node is None:
                new_content = re.sub(r'local node.*! user', '\n  remove-local-node', new_content, flags=re.DOTALL)
            helpers.log("********config after remove passwd :************\n%s" % new_content)
            return  new_content
        if fabric_switch:
            c.enable('show fabric switch')
            content = c.cli_content()
            helpers.log("********content in string:************\n%s" % content)
            temp = helpers.strip_cli_output(content)
            helpers.log("********string :************\n%s" % temp)
            return  temp
        if filepath:
            fileinfo = host.bash_ls(node, filepath)
            helpers.log("********file info is************\n%s" % fileinfo)
            return fileinfo
        return False



    def rest_get_node_role(self, node='c1'):
        '''
           return the local node role:
          Author: Mingtao
          input:  node  - controller
                           c1 c2
          usage:
          output: active or standby
          fails if there is no domain-leader for the cluster
        '''
        t = test.Test()
        c = t.controller(node)
        helpers.log('INFO: Entering ==> rest_get_node_role ')


        url = '/api/v1/data/controller/cluster'
        c.rest.get(url)
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())

        if(c.rest.content()):
            local_id = c.rest.content()[0]['status']['local-node-id']
            helpers.log("INFO: local node ID: %s" % local_id)
            if c.rest.content()[0]['status']['domain-leader']:
                leader_id = c.rest.content()[0]['status']['domain-leader']['leader-id']
                helpers.log("INFO: domain-leader: %s" % c.rest.content()[0]['status']['domain-leader']['leader-id'])
                if local_id == leader_id:
                    return 'active'
                else:
                    return 'standby'

            else:
                helpers.log("ERROR: there is no domain-leader")
                helpers.test_failure('ERROR: There is no domain-leader')
        return False


    def cli_get_node_role(self, node='c1'):
        '''
           return the local node role:
          Author: Mingtao
          input:  node  - controller
                           c1 c2
          usage:
          output: active or stand-by
          fails if there is no domain-leader for the cluster
        '''
        t = test.Test()
        c = t.controller(node)
        helpers.log('INFO: Entering ==> cli_get_node_role ')
        c.cli('show controller')
        content = c.cli_content()
        temp = helpers.strip_cli_output(content)
        temp = helpers.str_to_list(temp)
        for line in temp:
            helpers.log("INFO: line is - %s" % line)
            match = re.match(r'.* \* (active|standby).*', line)
            if match:
                helpers.log("INFO: role is: %s" % match.group(1))
                return  match.group(1)
            else:
                helpers.log("INFO: not current node  %s" % line)
        return False



    def rest_get_ver(self, node='c1'):
        '''
          return the local node version
          Author: Mingtao
          input:  node  - controller
                           c1 c2
          usage:
          output:  build

        '''
        t = test.Test()
        c = t.controller(node)
        helpers.log('INFO: Entering ==> rest_get_node_role ')

        url = '/api/v1/data/controller/core/version/appliance'
        c.rest.get(url)
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())

        if(c.rest.content()):
            return c.rest.content()[0]['ci-build-number']
        return False



    def rest_get_num_nodes(self, node='master'):
        '''
          return the number of nodes in the system
          Author: Mingtao
          input:
          usage:
          output:   1  or 2
        '''
        t = test.Test()
        c = t.controller(node)
        helpers.log('INFO: Entering ==> rest_get_num_nodes ')


        url = '/api/v1/data/controller/cluster'
        c.rest.get(url)
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())

        if(c.rest.content()):
            num = len(c.rest.content()[0]['status']['node'])
            helpers.log("INFO: There are %d of controller in cluster" % int(num))
            for index in range(0, num):

                hostname = c.rest.content()[0]['status']['node'][index]['hostname']
                helpers.log("INFO: hostname is: %s" % hostname)

            return num
        else:
            helpers.test_failure(c.rest.error())


    def cli_whoami(self, node='master'):
        '''
          run cli whoami
          Author: Mingtao
          input:
          usage:
          output:   username and group
        '''
        t = test.Test()
        c = t.controller(node)
        helpers.log('INFO: Entering ==> cli_whoami ')

        c.cli('whoami')
        content = c.cli_content()
        temp = helpers.strip_cli_output(content)
        temp = helpers.str_to_list(temp)
        helpers.log("INFO: temp is - %s" % temp)

        for line in temp:
            line = line.lstrip()
            helpers.log("INFO: line is - %s,  " % line)
            match = re.match(r'.*Id\s+:\s*(.*)', line)
            if match:
                name = match.group(1)
                helpers.log("INFO: ID: %s" % match.group(1))
            match = re.match(r'.*Groups\s+:\s*(.*)', line)
            if match:
                group = match.group(1)
                helpers.log("INFO: Group: %s" % match.group(1))

        return [name, group]


    def cli_reauth(self, node='master', user='admin', passwd='adminadmin'):
        '''
          run cli reauth, and run cli_whoami verify
          Author: Mingtao
          input:
          usage:  cli_reauth  user
          output:   True  or False

        '''
        t = test.Test()
        c = t.controller(node)
        helpers.log('INFO: Entering ==> cli_reauth ')

        c.enable('reauth ' + user + ' ' + passwd)

        userinfo = self.cli_whoami()[0]
        if user == userinfo:
            helpers.log('INFO: current session with user:  %s ' % user)
            return True
        else:
            helpers.log('INFO: current session with user:  %s ' % user)
            return False

    def cli_kill_ssh_sessions(self, node):
        '''
        Kill SSH sessions by running 'pkill -TERM sshd' from bash mode.

        Inputs:
        | node | reference to controller as defined in .topo file |

        Return Value:
        - True if killing sessions successful, False otherwise
        '''
        t = test.Test()
        bsn_common = bsnCommon()
        ip_addr = bsn_common.get_node_ip(node)
        c = t.node_spawn(ip=ip_addr)
        helpers.log('INFO: Entering bash mode to kill all sshd processes')
        c.cli("debug bash")
        try:
            c.send("sudo pkill -TERM sshd")
            helpers.log("Kill command sent")
            return True
        except:
            helpers.test_failure('ERROR: failure killing ssh sessions')
            return False


    def bash_top(self, node):
        """
        Execute 'top - n 1' on a device.
        Author:    Mingtao
        Inputs:
        | node | reference to switch/controller/host as defined in .topo file |

        Example:    bash_top   c1

        Return Value:
        - Dictionary
            {'Swap': {'cached': '904268k',
              'free': '1943548k',
              'total': '1943548k',
              'used': '0k'},
                 'cpu': {'hi': '0.0',
                         'id': '97.8',
                         'ni': '0.0',
                         'si': '0.0',
                         'st': '0.1',
                         'sy': '0.4',
                         'us': '0.7',
                         'wa': '0.9'},
                 'init': {'cpu': '0',
                          'mem': '0.1',
                          'pid': '1',
                          'res': '2180',
                          'shr': '1268',
                          'virt': '24340'},
                 'java': {'cpu': '4',
                          'mem': '15.0',
                          'pid': '683',
                          'res': '299m',
                          'shr': '9844',
                          'virt': '3036m'},
                 'load': '0.00, 0.01, 0.05',
                 'mem': {'buffers': '106336k',
                         'free': '499892k',
                         'total': '2051616k',
                         'used': '1551724k'}
         }
        """
        t = test.Test()
        n = t.node(node)
        content = n.bash('top -n 1')['content']
        lines = helpers.strip_cli_output(content, to_list=True)
        helpers.log("lines: %s" % lines)
        topinfo = {}
        linenum = 0
        for line in lines:
            line = line.lstrip()
            helpers.log(" line is - %s" % line)
            linenum = linenum + 1
            if (re.match(r'.*load average: (.*)', line)):

                match = re.match(r'.*load average: (.*)', line)
                topinfo['load'] = match.group(1)
                helpers.log("INFO: *** get the load info *** topinfo is \n  %s" % topinfo)

            elif (re.match(r'Cpu.* (.*)%us,.*', line)):
                topinfo['cpu'] = {}
                match = re.match(r'Cpu.* (.*)%us,\s+(.*)%sy,\s+(.*)%ni,\s+(.*)%id,\s+(.*)%wa,\s+(.*)%hi,\s+(.*)%si,\s+(.*)%st.*', line)
                topinfo['cpu']['us'] = match.group(1)
                topinfo['cpu']['sy'] = match.group(2)
                topinfo['cpu']['ni'] = match.group(3)
                topinfo['cpu']['id'] = match.group(4)
                topinfo['cpu']['wa'] = match.group(5)
                topinfo['cpu']['hi'] = match.group(6)
                topinfo['cpu']['si'] = match.group(7)
                topinfo['cpu']['st'] = match.group(8)
                helpers.log("INFO: *** get the cpu info **** topinfo is \n  %s" % topinfo)
            elif (re.match(r'Mem:.*', line)):
                topinfo['mem'] = {}
                match = re.match(r'Mem:.* (.*) total,\s+(.*) used,\s+(.*) free,\s+(.*) buffers.*', line)
                topinfo['mem']['total'] = match.group(1)
                topinfo['mem']['used'] = match.group(2)
                topinfo['mem']['free'] = match.group(3)
                topinfo['mem']['buffers'] = match.group(4)

                helpers.log("INFO: *** get the Mem info **** topinfo is \n  %s" % topinfo)

            elif (re.match(r'Swap:\s+(.*) total,\s+(.*) used,\s+(.*) free,\s+(.*) cached.*', line)):
                topinfo['Swap'] = {}
                match = re.match(r'Swap:\s+(.*) total,\s+(.*) used,\s+(.*) free,\s+(.*) cached.*', line)
                topinfo['Swap']['total'] = match.group(1)
                topinfo['Swap']['used'] = match.group(2)
                topinfo['Swap']['free'] = match.group(3)
                topinfo['Swap']['cached'] = match.group(4)

                helpers.log("INFO: *** get the Swap info **** topinfo is \n  %s" % topinfo)
            elif (re.match(r'PID USER.*', line)):
                helpers.log("INFO: *** below are stats for process ****   \n ")
                break

        helpers.log("INFO: *** line number is  ****  %d   " % linenum)
        process = lines[linenum:]
        helpers.log("INFO: *** remain lines are  ****   \n  %s" % process)
        for line in process:
            fields = line.split()
            helpers.log("INFO: fields   \n  %s" % fields)
            pname = fields[11]
            if pname == 'init' or  pname == 'java':
                topinfo[pname] = {}
                topinfo[pname]['pid'] = fields[0]
                topinfo[pname]['virt'] = fields[4]
                topinfo[pname]['res'] = fields[5]
                topinfo[pname]['shr'] = fields[6]
                topinfo[pname]['cpu'] = fields[8]
                topinfo[pname]['mem'] = fields[9]
            else:
                continue
        helpers.log("INFO:  topinfo is \n  %s" % helpers.prettify(topinfo))
        return topinfo

    def cli_add_user(self, user='user1', passwd='adminadmin'):
        '''
          cli add user to the system, can only run at master
          Author: Mingtao
          input:   user = username,  passwd  = password
          usage:
          output:   True
        '''

        t = test.Test()
        c = t.controller('master')
        helpers.log('INFO: Entering ==> cli_add_user ')
        t = test.Test()
        c.config('user ' + user)
        c.send('password')
        c.expect('Password: ')
        c.send(passwd)
        c.expect('Re-enter:')
        c.send(passwd)
        c.expect()
        return True



    def cli_group_add_users(self, group=None, user=None):
        '''
          cli add user to group, can only run at master
          Author: Mingtao
          input:   group  - if group not give, will user admin
                  user    - if user not given, will add all uers
          usage:
          output:   True
        '''
        t = test.Test()
        c = t.controller('master')
        helpers.log('INFO: Entering ==> cli_add_user ')
        if group is None:
            group = 'admin'
        c.config('group ' + group)
        if user:
            c.config('associate user ' + user)
        else:
            c.config('show running-config user | grep user')
            content = c.cli_content()
            temp = helpers.strip_cli_output(content)
            temp = helpers.str_to_list(temp)
            helpers.log("********new_content:************\n%s" % helpers.prettify(temp))
            temp.pop(0)
            helpers.log("********new_content:************\n%s" % helpers.prettify(temp))
            for line in temp:
                line = line.lstrip()
                user = line.split(' ')[1]
                helpers.log('INFO: user is: %s ' % user)
                if user == 'admin':
                    continue
                else:
                    c.config('associate user ' + user)

            return True


    def rest_get_user_group(self, user):
        '''
          get the group for a user, can only run at master
          Author: Mingtao
          input:
                  user    - if user not given, will add all uers
          usage:
          output:   group
        '''
        t = test.Test()
        c = t.controller('master')
        helpers.log('INFO: Entering ==> rest_get_user_group ')


        url = '/api/v1/data/controller/core/aaa/group[user="%s"]' % user
        c.rest.get(url)
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())

        if(c.rest.content()):
            helpers.log('INFO: content is: %s ' % c.rest.content())

            if user in c.rest.content()[0]['user']:
                helpers.log('INFO: inside  ')
                return  c.rest.content()[0]['name']
        else:
            helpers.test_failure(c.rest.error())


    def cli_delete_user(self, user):
        '''
          delete users can only run at master
          Author: Mingtao
          input:  user
          usage:
          output:   True

        '''

        t = test.Test()
        c = t.controller('master')
        helpers.log('INFO: Entering ==> cli_delete_user ')
        c.config('no user ' + user)
        return True


    def T5_cli_clean_all_users(self, user=None):
        '''
        delete all users except admin
          Author: Mingtao
          input:  user
          usage:
          output:   True
        '''

        t = test.Test()
        c = t.controller('master')
        helpers.log('INFO: Entering ==> cli_delete_user ')

        if user:
            c.config('no user ' + user)
            return True
        else:
            c.config('show running-config user | grep user')
            content = c.cli_content()
            temp = helpers.strip_cli_output(content)
            temp = helpers.str_to_list(temp)
            helpers.log("********new_content:************\n%s" % helpers.prettify(temp))
            temp.pop(0)
            helpers.log("********new_content:************\n%s" % helpers.prettify(temp))
            for line in temp:
                line = line.lstrip()
                user = line.split(' ')[1]
                helpers.log('INFO: user is: %s ' % user)
                if user == 'admin':
                    continue
                else:
                    c.config('no user ' + user)

            return True



    def first_boot_controller(self, node,
                           join_cluster='no',
                           dhcp='no',
                           ip_address=None,
                           netmask='18',
                           gateway='10.192.64.1',
                           dns_server='10.92.3.1',
                           dns_search='bigswitch.com',
                           hostname='MY-T5-C',
                           cluster_ip='',
                           cluster_passwd='adminadmin',
                           cluster_name='T5cluster',
                           cluster_descr='T5cluster',
                           admin_password='adminadmin',
                           platform='bvs',
                           ntp_server='',
                        ):

        """
        First boot setup: connect to the console  and complete the first boot.
        input: dhcp = no   - static ip assign
               dhcp = yes,  dhcp
               join_cluster = no  - start a new cluster
               join_cluster = yes  - jion existing cluster

        Author: Mingtao

        """
        helpers.log("Entering ====>  first_boot_controller node:'%s' " % node)
        self.first_boot_controller_initial_node_setup(node, dhcp, ip_address, netmask, gateway, dns_server, dns_search, hostname)
        self.first_boot_controller_initial_cluster_setup(node, join_cluster, cluster_ip)
        new_ip_address = self.first_boot_controller_menu_apply(node)
        helpers.sleep(3)  # Sleep for a few seconds just in case...
        helpers.log("new_ip_address = '%s'" % new_ip_address)
        loss = helpers.ping(new_ip_address)
        if loss < 50:
            helpers.log("Node '%s' has survived first-boot!" % node)
            return new_ip_address
        else:
            helpers.test_failure('ERROR: the controller is not reachable')
            return False


    def console_boot_factory_default(self, node, timeout=360):
        """
        Runs boot factory-default from console, the can be used when controller is setup using dhcp
        Author: Mingtao
        """

        t = test.Test()
        n = t.node(node)
        helpers.log("Entering ===> console_boot_factory_default: '%s'" % node)
        helpers.log("Getting the console session for '%s'" % node)
        n_console = n.console()
        helpers.summary_log('BVS boot factory may take a bit of time. Setting timeout to %s seconds.' % timeout)
        n_console.send(helpers.ctrl('c'))
        helpers.sleep(2)
        n_console.send('')
        helpers.sleep(2)
        n_console.send('')
        options = n_console.expect([helpers.regex_bvs(), r'.*> '])
        if options[0] == '0':
            n_console.expect(r'.*login: ')
            n_console.send('admin')
            n_console.expect(r'[Pp]assword: ')
            n_console.send('adminadmin')
            n_console.expect(r'[#>] ')

        n_console.send('enable')
        n_console.expect('#')
        n_console.send('boot factory-default')
        n_console.expect(r'proceed \("yes" or "y" to continue\)')
        n_console.send('y')
        n_console.expect(r'loading image into stage partition', timeout=timeout)
        n_console.expect(r'checking integrity of new partition', timeout=timeout)
        n_console.expect(r'New Partition Ready', timeout=timeout)
        n_console.expect(r'ready for reboot', timeout=timeout)
        n_console.expect(r'"yes" or "y" to continue\): ', timeout=timeout)
        n_console.send('y')

        helpers.summary_log("'%s' has been rebooted." % node)
        helpers.log("Boot factory-default completed on '%s'. System should be rebooting." % node)
        return True


    def first_boot_controller_initial_node_setup(self,
                           node,
                           dhcp='no',
                           ip_address=None,
                           netmask='18',
                           gateway='10.8.0.1',
                           dns_server='10.3.0.4',
                           dns_search='qa.bigswitch.com',
                           hostname='MY-T5-C',
                            ):
        """
        First boot setup I: connect to the console to complete the first-boot node setup part
        input: dhcp = no   - static ip assign
               dhcp = yes,  dhcp
        Author: Mingtao
        """
        t = test.Test()
        n = t.node(node)

        if not ip_address:
            ip_address = n.ip()
        helpers.log("Entering ===> first_boot_controller_initial_node_setup: '%s', %s, %s, %s, %s, %s, %s, %s " \
                    % (node, dhcp, ip_address, netmask, gateway, dns_server, dns_search, hostname))
        helpers.log("Getting the console session for '%s'" % node)
        n_console = n.console()

        options = n_console.expect([r'Escape character.*[\r\n]', r'login:', r'Local Node Configuration'])

        content = n_console.content()
        helpers.log("*****Output is :*******\n%s" % content)
        if options[0] < 2:
            if options[0] == 0 :
                helpers.log("USER INFO:  need to Enter ")
                n_console.send('')
                helpers.log("Need to wait for the system initialize before sending Ctl C")
                helpers.sleep(15)
#                n_console.send(helpers.ctrl('c')))
                n_console.send('')
                try:
                    n_console.expect(helpers.regex_bvs())
                except:
                    helpers.log("Devconf 'expect' error. Possibly corrupted terminal session. Try to reconnect to console.")
                    helpers.log(helpers.exception_info())
                    n.console_close()  # **** Closing the console
                    helpers.sleep(1)
                    n_console = t.dev_console(node, modeless=True)
                    n_console.send('')
                n_console.expect(r'login:')
            elif options[0] == 1:
                helpers.log("INFO:  need to login as  admin")
            n_console.send('admin')

            # Need to enable developer mode to use DHCP option. Magic string
            # to enable it is 'dhcp'.
            if dhcp == 'yes':
                helpers.log("Entering into Developer mode for dhcp options..")
                n_console.expect(r'Do you accept the EULA.* > ')
                n_console.send('dhcp')
                n_console.expect(r'Developer.* mode enabled.*')
            else:
                helpers.log("In Normal First boot mode NOT DEVELOPER MODE NO DHCP OPTION..")

            # The "real" EULA
            n_console.expect(r'Do you accept the EULA.* > ')
            n_console.send('Yes')

            n_console.expect(r'Local Node Configuration')

        n_console.expect(r'Password for emergency recovery user > ')
        n_console.send('bsn')
        n_console.expect(r'Retype Password for emergency recovery user > ')
        n_console.send('bsn')
        if dhcp == 'yes':
            n_console.expect(r'Please choose an IP mode:.*[\r\n]')
            n_console.expect(r'> ')
            # dhcp
            n_console.send('2')  # DHCP
        else:
            # n_console.send('1')  # Manual
            n_console.expect(r'IP address .* > ')
            n_console.send(ip_address)

            if not re.match(r'.*/\d+', ip_address):
                # Send netmask if IP address doesn't contain prefix length
                n_console.expect(r'CIDR prefix length .* > ')
                n_console.send(netmask)

            n_console.expect(r'Default gateway address .* > ')
            n_console.send(gateway)
            n_console.expect(r'DNS server address .* > ')
            n_console.send(dns_server)
            n_console.expect(r'DNS search domain .* > ')
            n_console.send(dns_search)
            n_console.expect(r'Hostname > ')
            n_console.send(hostname)
        helpers.sleep(3)  # Sleep for a few seconds just in case...
        return True

    def first_boot_controller_initial_cluster_setup(self,
                           node,
                           join_cluster='no',
                           cluster_ip='',
                           cluster_passwd='adminadmin',
                           cluster_name='T5cluster',
                           cluster_descr='T5cluster',
                           admin_password='adminadmin',
                           ntp_server='',
                           ):
        """
        First boot setup II: connect to the console to complete the first-boot cluster setup part
        input: join_cluster = no  - start a new cluster
               join_cluster = yes  - jion existing cluster
        Author: Mingtao
        """

        t = test.Test()
        n = t.node(node)
        helpers.log("Entering ===> first_boot_controller_initial_cluster_setup: '%s', %s, %s, %s, %s, %s, %s" \
                    % (node, join_cluster, cluster_ip, cluster_passwd, cluster_descr, admin_password, ntp_server))
        helpers.log("Getting the console session for '%s'" % node)
        n_console = n.console()
#        n_console.expect(r'Controller Clustering')
        n_console.expect(r'Please choose a cluster option:.*')
        n_console.expect(r'> ')

        if join_cluster == 'yes':
            n_console.send('2')  # join existing cluster
            n_console.expect(r'Existing \b(node|Controller)\b IP.*> ')
            n_console.send(cluster_ip)
            n_console.expect(r'Administrator password for cluster.*> ')
            n_console.send(cluster_passwd)
            n_console.expect(r'Retype Administrator password for cluster.*> ')
            n_console.send(cluster_passwd)
        else:
            n_console.send('1')  # Start a new cluster
            n_console.expect(r'Cluster name > ')
            n_console.send(cluster_name)
            n_console.expect(r'Cluster description .* > ')
            n_console.send(cluster_descr)
            n_console.expect(r'Administrator password for cluster > ')
            n_console.send(admin_password)
            n_console.expect(r'Retype .* > ')
            n_console.send(admin_password)
            n_console.expect(r'System Time')
            n_console.expect(r'Enter NTP server .* > ')
            n_console.send(ntp_server)

        helpers.sleep(3)  # Sleep for a few seconds just in case...
        helpers.log("USER INFO:  Please choose an option")

        return True

    def first_boot_controller_menu_apply(self, node):
        """
        First boot setup III: connect to the console to apply the setting.
        First boot setup Menu :  Apply settings
        Author: Mingtao
        """
        t = test.Test()
        n = t.node(node)
        helpers.log("Entering ====>  first_boot_controller_menu_1 for node: '%s'" % node)
        helpers.log("Getting the console session for '%s'" % node)
        n_console = n.console()
        n_console.expect(r'\[1\] > ')
        helpers.log("[1] Apply settings ")
        content = n_console.content()
        helpers.log("USER INFO: the content is '%s'" % content)
        match = re.search(r'\[\s*(\d+)\] Apply settings.*[\r\n$]', content)
        if match:
            option = match.group(1)
            helpers.log("USER INFO: the option is %s" % option)
        else:
            helpers.log("USER ERROR: there is no match")
            return False

        n_console.send(option)  # Apply settings
        n_console.expect(r'Initializing system.*[\r\n]')
        n_console.expect(r'Configuring controller.*[\r\n]')

        n_console.expect(r'IP address on eth0 is (.*)[\r\n]', timeout=600)
        content = n_console.content()

        helpers.log("content is:  %s" % content)
        match = re.search(r'IP address on eth0 is (\d+\.\d+\.\d+\.\d+).*[\r\n]', content)
        new_ip_address = match.group(1)
        helpers.log("new_ip_address: '%s'" % new_ip_address)

        n_console.expect(r'Configuring cluster.*[\r\n]')
        n_console.expect(r'First-time setup is complete.*[\r\n]')
        n_console.expect(r'Press enter to continue > ')
        n_console.send('')
        # helpers.log("Closing console connection for '%s'" % node)
        # n.console_close()

        helpers.sleep(3)  # Sleep for a few seconds just in case...
        return new_ip_address



    def first_boot_controller_menu_recovery(self, node, passwd='bsn'):
        """
        First boot setup Menu :  Update Emergency Recovery Password
        Author: Mingtao
        """
        t = test.Test()
        n = t.node(node)
        helpers.log("Entering ====>  Update Emergency Recovery Password for node: '%s'" % node)
        helpers.log("Getting the console session for '%s'" % node)
        n_console = n.console()
        n_console.expect(r'\[1\] > ')
        content = n_console.content()
        helpers.log("USER INFO: the content is '%s'" % content)
        match = re.search(r'\[\s*(\d+)\] Update Emergency Recovery Password.*[\r\n$]', content)
        if match:
            option = match.group(1)
            helpers.log("USER INFO: the optin is %s" % option)
        else:
            helpers.log("USER ERROR: there is no match")
            return False
        if option != '3':
            helpers.summary_log("choice %s not 2" % option)
        n_console.send(option)  # Apply settings
        n_console.expect(r'Password for emergency recovery user > ')
        n_console.send(passwd)
        n_console.expect(r'Retype Password for emergency recovery user > ')
        n_console.send(passwd)
 #       n_console.expect(r'Please choose an option:.*[\r\n$]')

        helpers.sleep(3)  # Sleep for a few seconds just in case...
        return True

    def first_boot_controller_menu_IP(self, node, ip_addr, netmask='24', invalid_input=False):
        """
       First boot setup Menu :  Update Local IP Address
        Author: Mingtao
        """
        t = test.Test()
        n = t.node(node)
        helpers.log("Entering ====> Update Local IP Address for node: '%s'" % node)
        helpers.log("Getting the console session for '%s'" % node)
        n_console = n.console()
        options = n_console.expect([r'\[1\] > ', r'IP address .* >'])
        content = n_console.content()
        helpers.log("USER INFO: the content is '%s'" % content)
        if options[0] == 0:
            match = re.search(r'\[\s*(\d+)\] Update Local IP Address.*[\r\n$]', content)
            if match:
                option = match.group(1)
                helpers.log("USER INFO: the optin is %s" % option)
            else:
                helpers.log("USER ERROR: there is no match")
                return False
            if option != '5':
                helpers.summary_log("choice %s not 5" % option)
            n_console.send(option)  # Apply settings
            n_console.expect(r'IP address .* > ')
        n_console.send(ip_addr)
        if invalid_input:
            helpers.log("USER INFO: in invalid input,  this is negative case")
            n_console.expect([r'Error:.*', r'.*Must not be.*', r'IP address.*'])
            return True
#        else:
#            n_console.expect(r'Please choose an option:.*[\r\n$]')

        if not re.match(r'.*/\d+', ip_addr):
            # to make sure the next table has CIDR entry
            n_console.expect(r'\[1\] > ')
            content = n_console.content()
            helpers.log("USER INFO: the content is '%s'" % content)
            match = re.search(r'\[\s*(\d+)\] Update CIDR Prefix Length.*[\r\n$]', content)
            if match:
                option = match.group(1)
                helpers.log("USER INFO: the option is %s" % option)
            else:
                helpers.log("USER ERROR: there is no match")
                return False
            n_console.send(option)  # Apply settings
            n_console.expect(r'CIDR prefix length \[24\].* > ')
            n_console.send(netmask)
        helpers.sleep(3)  # Sleep for a few seconds just in case...
        return True


    def first_boot_controller_menu_prefix(self, node, netmask, invalid_input=False):
        """
       First boot setup Menu :  Update CIDR Prefix Length
        Author: Mingtao
        """
        t = test.Test()
        n = t.node(node)
        helpers.log("Entering ====> Update CIDR Prefix Length for node: '%s'" % node)
        helpers.log("Getting the console session for '%s'" % node)
        n_console = n.console()

        options = n_console.expect([r'\[1\] > ', r'CIDR prefix length.* >'])
        content = n_console.content()
        helpers.log("USER INFO: the content:  %s" % content)
        if options[0] == 0:
            match = re.search(r'\[\s*(\d+)\] Update CIDR Prefix Length.*[\r\n$]', content)
            if match:
                option = match.group(1)
                helpers.log("USER INFO: the option is %s" % option)
            else:
                helpers.log("USER ERROR: there is no match")
                return False
            n_console.send(option)  # Apply settings
            n_console.expect(r'CIDR prefix length \[24\].* > ')
        n_console.send(netmask)
        if invalid_input:
            helpers.log("USER INFO: in invalid input,  this is negative case")
            n_console.expect([r'Error:.*', r'.*Must be between'])
#        else:
#            n_console.expect(r'Please choose an option:.*[\r\n$]')

        helpers.sleep(3)  # Sleep for a few seconds just in case...
        return True




    def first_boot_controller_menu_gateway(self, node, gateway):
        """
       First boot setup Menu :  Update Gateway
        Author: Mingtao

        """
        t = test.Test()
        n = t.node(node)
        helpers.log("Entering ====> Update Gateway for node: '%s'" % node)
        helpers.log("Getting the console session for '%s'" % node)
        n_console = n.console()
        n_console.expect(r'\[1\] > ')
        content = n_console.content()
        helpers.log("USER INFO: the content is '%s'" % content)
        match = re.search(r'\[\s*(\d+)\] Update Gateway.*[\r\n$]', content)
        if match:
            option = match.group(1)
            helpers.log("USER INFO: the option is %s" % option)
        else:
            helpers.log("USER ERROR: there is no match")
            return False
        n_console.send(option)  # Apply settings
        n_console.expect(r'Gateway.*')
        n_console.expect(r'Default gateway address.*> ')
        n_console.send(gateway)
#        n_console.expect(r'Please choose an option:.*[\r\n$]')

        helpers.sleep(3)  # Sleep for a few seconds just in case...
        return True

    def first_boot_controller_menu_dnsserver(self, node, dnsserver, invalid_input=False):
        """
       First boot setup Menu :  Update DNS Server
        Author: Mingtao
        """
        t = test.Test()
        n = t.node(node)
        helpers.log("Entering ====> Update DNS Server for node: '%s'" % node)
        helpers.log("Getting the console session for '%s'" % node)
        n_console = n.console()

        options = n_console.expect([r'\[1\] > ', r'DNS server address.* >'])
        content = n_console.content()
        helpers.log("USER INFO: the content:  %s" % content)
        if options[0] == 0:
            match = re.search(r'\[\s*(\d+)\] Update DNS Server.*[\r\n$]', content)
            if match:
                option = match.group(1)
                helpers.log("USER INFO: the option is %s" % option)
            else:
                helpers.log("USER ERROR: there is no match")
                return False
            n_console.send(option)  # Apply settings
            n_console.expect(r'DNS Server.*')
            n_console.expect(r'DNS server address.* > ')

        n_console.send(dnsserver)
        if invalid_input:
            helpers.log("USER INFO: in invalid input,  this is negative case")
            n_console.expect([r'Error:.*', r'.*Must not be.*'])
#        else:
#            n_console.expect(r'Please choose an option:.*[\r\n$]')

        helpers.sleep(3)  # Sleep for a few seconds just in case...
        return True

    def first_boot_controller_menu_domain(self, node, domain):
        """
       First boot setup Menu :  Update DNS Search Domain
        Author: Mingtao
        """
        t = test.Test()
        n = t.node(node)
        helpers.log("Entering ====> Update DNS Search Domain for node: '%s'" % node)
        helpers.log("Getting the console session for '%s'" % node)
        n_console = n.console()
        n_console.expect(r'\[1\] > ')
        content = n_console.content()
        helpers.log("USER INFO: the content is '%s'" % content)
        match = re.search(r'\[\s*(\d+)\] Update DNS Search Domain.*[\r\n$]', content)
        if match:
            option = match.group(1)
            helpers.log("USER INFO: the optin is %s" % option)
        else:
            helpers.log("USER ERROR: there is no match")
            return False
        n_console.send(option)  # Apply settings
        n_console.expect(r'DNS Search Domain.*')
        n_console.expect(r'DNS search domain.* > ')
        n_console.send(domain)
#        n_console.expect(r'Please choose an option:.*[\r\n$]')

        helpers.sleep(3)  # Sleep for a few seconds just in case...
        return True

    def first_boot_controller_menu_name(self, node, name):
        """
       First boot setup Menu :  Update Hostname
        Author: Mingtao
        """
        t = test.Test()
        n = t.node(node)
        helpers.log("Entering ====> Update Hostname for node: '%s'" % node)
        helpers.log("Getting the console session for '%s'" % node)
        n_console = n.console()
        n_console.expect(r'\[1\] > ')
        content = n_console.content()
        helpers.log("USER INFO: the content is '%s'" % content)
        match = re.search(r'\[\s*(\d+)\] Update Hostname.*[\r\n$]', content)
        if match:
            option = match.group(1)
            helpers.log("USER INFO: the optin is %s" % option)
        else:
            helpers.log("USER ERROR: there is no match")
            return False

        n_console.send(option)  # Apply settings
        n_console.expect(r'Hostname.*')
        n_console.expect(r'Hostname.* > ')
        n_console.send(name)
#        n_console.expect(r'Please choose an option:.*[\r\n$]')

        helpers.sleep(3)  # Sleep for a few seconds just in case...
        return True

    def first_boot_controller_menu_cluster_name(self, node, name='MY-T5-C', invalid_input=False):
        """
       First boot setup Menu :   Update Cluster Name
        """
        t = test.Test()
        n = t.node(node)
        helpers.log("Entering ====> Update Cluster Name for node: '%s'" % node)
        helpers.log("Getting the console session for '%s'" % node)
        n_console = n.console()

        options = n_console.expect([r'\[1\] > ', r'Cluster name.* > '])
        content = n_console.content()
        helpers.log("USER INFO: the content is '%s'" % content)
        if options[0] == 0:
            match = re.search(r'\[\s*(\d+)\] Update Cluster Name.*[\r\n$]', content)
            if match:
                option = match.group(1)
                helpers.log("USER INFO: the option is %s" % option)
            else:
                helpers.log("USER ERROR: there is no match")
                return False
            n_console.send(option)  # Apply settings
            n_console.expect(r'Cluster Name.*')
            n_console.expect(r'Cluster name.* > ')

        n_console.send(name)
        if invalid_input:
            helpers.log("USER INFO: in invalid input,  this is negative case")
            n_console.expect(r'Error:.*')
#        else:
#            n_console.expect(r'Please choose an option:.*[\r\n$]')

        helpers.sleep(3)  # Sleep for a few seconds just in case...
        return True

    def first_boot_controller_menu_cluster_desr(self, node, descr='MY-T5-C'):
        """
       First boot setup Menu :   Update Cluster Description
        """
        t = test.Test()
        n = t.node(node)
        helpers.log("Entering ====> Update Cluster Description for node: '%s'" % node)
        helpers.log("Getting the console session for '%s'" % node)
        n_console = n.console()
        n_console.expect(r'\[1\] > ')
        content = n_console.content()
        helpers.log("USER INFO: the content is '%s'" % content)
        match = re.search(r'\[\s*(\d+)\] Update Cluster Description.*[\r\n$]', content)
        if match:
            option = match.group(1)
            helpers.log("USER INFO: the optin is %s" % option)
        else:
            helpers.log("USER ERROR: there is no match")
            return False
        n_console.send(option)  # Apply settings
        n_console.expect(r'Cluster Description.*')
        n_console.expect(r'Cluster description.* > ')
        n_console.send(descr)
#        n_console.expect(r'Please choose an option:.*[\r\n$]')

        helpers.sleep(3)  # Sleep for a few seconds just in case...
        return True

    def first_boot_controller_menu_cluster_passwd(self, node, passwd='adminadmin'):
        """
       First boot setup Menu :   Update Cluster Admin Password
        """
        t = test.Test()
        n = t.node(node)
        helpers.log("Entering ====> Update Cluster Admin Password  for node: '%s'" % node)
        helpers.log("Getting the console session for '%s'" % node)
        n_console = n.console()
        n_console.expect(r'\[1\] > ')
        content = n_console.content()
        helpers.log("USER INFO: the content is '%s'" % content)
        match = re.search(r'\[\s*(\d+)\] Update Cluster Admin Password.*[\r\n$]', content)
        if match:
            option = match.group(1)
            helpers.log("USER INFO: the optin is %s" % option)
        else:
            helpers.log("USER ERROR: there is no match")
            return False
        n_console.send(option)  # Apply settings
        n_console.expect(r'Cluster Admin Password.*')
        n_console.expect(r'Administrator password for cluster.* > ')
        n_console.send(passwd)
        n_console.expect(r'Retype Administrator password for cluster.* > ')
        n_console.send(passwd)
#        n_console.expect(r'Please choose an option:.*[\r\n$]')
        helpers.sleep(3)  # Sleep for a few seconds just in case...
        return True

    def first_boot_controller_ctl_c(self, node):
        """
       First boot:   send ctl_c,  then resume
        Author: Mingtao
        """
        t = test.Test()
        n = t.node(node)
        helpers.log("Entering ====> first_boot_controller_ctl_c  for node: '%s'" % node)
        helpers.log("Getting the console session for '%s'" % node)
        n_console = n.console()

        n_console.send(helpers.ctrl('c'))
        helpers.summary_log('CTRL  C is hited')

        n_console.expect(r'Option Menu.*')
        n_console.expect(r'\[1\] > ')
        content = n_console.content()
        helpers.log("USER INFO: the content is '%s'" % content)
        match = re.search(r'\[\s*(\d+)\] Resume setup.*[\r\n$]', content)
        if match:
            option = match.group(1)
            helpers.log("USER INFO: the option is %s" % option)
        else:
            helpers.log("USER ERROR: there is no match for resume setup")
            return False
        n_console.send(option)  # Apply settings
        n_console.expect(r'Resuming setup.*')
        return True

    def rest_controller_add_ip(self, node, ipaddr, netmask, spawn=None):
        """
          config a new local ip address and make sure it is reachable.
          Author: Mingtao
          input:  node  - controller
                           c1 c2
                   spawn: if node= 1.1.1.1,  and the address is not in topology, set it to True
          usage:
          output:
        """
        t = test.Test()
        if spawn:
            #  this is a ip address not in topology,  need to spawn, node is an ip address
            c = t.node_spawn(ip=node)
        else:
            c = t.controller(node)
        url = '/api/v1/data/controller/os/config/local-node/network-config/interface[type="ethernet"][number=0]/ipv4/address[ip-address="%s"]' % ipaddr
        try:
            c.rest.put(url, {"prefix":netmask, "ip-address":ipaddr})
        except:
            helpers.test_failure(c.rest.error())
            return False
        else:
            helpers.sleep(5)  # Sleep for a few seconds just in case...
            loss = helpers.ping(ipaddr)
            if loss < 50:
                helpers.log("Node '%s' ip address:  %s is reachable !" % (node, ipaddr))
                return True
            else:
                return False

    def rest_controller_add_ntp_timezone(self, node, timezone):
        """
          config a ntp time zone.
          Author: Mingtao
          input:  node  - controller
                           c1 c2
                 timezone:    America/Los_Angeles     America/New_York
          usage:
          output:
        """

        t = test.Test()
        c = t.controller(node)
        helpers.log('INFO: Entering ==> rest_controller_add_ntp')
        url = '/api/v1/data/controller/os/config/global/time'

        try:
            c.rest.put(url, {"time-zone":timezone})
        except:
            helpers.test_failure(c.rest.error())
            return False
        else:
            return True

    def cli_controller_show_clock(self, node):
        """
          cli show clock
          Author: Mingtao
          input:  node  - controller
                           c1 c2
          usage:
          output:   {'time':......,'timezone':PDT}
        """
        t = test.Test()
        c = t.controller(node)
        helpers.log('INFO: Entering ==> cli_controller_show_clock')
        c.cli("show clock")
        content = c.cli_content()

        temp = helpers.strip_cli_output(content)
        helpers.log("*****Output is :\n%s" % temp)
        match = re.match(r'System time :\s+(.*) ([A-Z]{3})[\r\n\$]', temp)
        if match:
            time = {}
            helpers.log("INFO: time is: %s" % match.group(1))
            time['time'] = match.group(1)
            helpers.log("INFO: time zone is: %s" % match.group(2))
            time['timezone'] = match.group(2)
            return time
        else:
            helpers.log("ERROR: did not match the time: %s" % temp)
            return False

    def controller_verify_timezone(self, node, timezone):
        """
         verify the timezone configuration
          Author: Mingtao
          input:  node  - controller
                           c1 c2
                timezone:    America/Los_Angeles     America/New_York
          usage:
          output:   True:   if expect and show clock matches
                    False:  if expect and show clock Not matche

        """
        helpers.log('INFO: Entering ==> controller_verify_timezone ')
        temp = self.cli_controller_show_clock(node)
        helpers.log("INFO: timezone is: %s" % temp['timezone'])
        ctimezone = temp['timezone']
        if timezone == 'America/Los_Angeles' and ctimezone == 'PDT':
            return True
        elif timezone == 'America/New_York' and ctimezone == 'EDT':
            return True
        return False


    def first_boot_controller_menu_cluster_option_apply(self, node,
                           join_cluster='no',
                           cluster_ip='',
                           cluster_passwd='adminadmin',
                           cluster_name='T5cluster',
                           cluster_descr='T5cluster',
                           admin_password='adminadmin',
                           ntp_server='',
                            ):
        """
       First boot setup Menu :   Update Cluster Name
        """
        t = test.Test()
        n = t.node(node)
        helpers.log("Entering ====> Update Cluster Option for node: '%s'" % node)

        helpers.log("Getting the console session for '%s'" % node)
        n_console = n.console()
        n_console.expect(r'\[1\] > ')
        content = n_console.content()
        helpers.log("USER INFO: the content is '%s'" % content)
        match = re.search(r'\[\s*(\d+)\] Update Cluster Option.*[\r\n$]', content)
        if match:
            option = match.group(1)
            helpers.log("USER INFO: the option is %s" % option)
        else:
            helpers.log("USER ERROR: there is no match")
            return False
        n_console.send(option)  # Apply settings
        n_console.expect(r'Please choose a cluster option:.*')
        n_console.expect(r'> ')

        if join_cluster == 'yes':
            n_console.send('2')  # join existing cluster
            n_console.expect(r'Existing node IP.*> ')
            n_console.send(cluster_ip)
        else:
            n_console.send('1')  # Start a new cluster
            n_console.expect(r'Cluster name > ')
            n_console.send(cluster_name)
            n_console.expect(r'Cluster description .* > ')
            n_console.send(cluster_descr)
            n_console.expect('')
        try:
            options = n_console.expect([r'\[1\] > ', r'[^\]]> '])
        except:
            content = n_console.content()
            helpers.log("*****Output is :*******\n%s" % content)
            helpers.log("USER ERROR: there is no match")
            helpers.test_failure('There is no match')

        else:
            content = n_console.content()
            helpers.log("*****Output is :*******\n%s" % content)

            if options[0] == 0 :
                helpers.log("*****Matched   [1] > can apply setting now*******  ")
            elif options[0] == 1:
                helpers.log("*****Matched >  can NOT apply setting now*******  ")

                match = re.search(r'\[\s*(\d+)\].*<NOT SET, UPDATE REQUIRED>.*[\r\n$]', content)
                if match:
                    helpers.log("USER INFO:  need to configure ntp")
                    option = match.group(1)
                    helpers.log("USER INFO: the option is %s" % option)
                    n_console.send(option)
                    n_console.expect(r'Enter NTP server.* > ')
                    n_console.send('')
                    n_console.expect(r'\[1\] > ')

            n_console.send('')  # Apply settings
            n_console.expect(r'Initializing system.*[\r\n]')
            n_console.expect(r'Configuring controller.*[\r\n]')

            n_console.expect(r'IP address on eth0 is (.*)[\r\n]')
            content = n_console.content()

            helpers.log("content is:  %s" % content)
            match = re.search(r'IP address on eth0 is (\d+\.\d+\.\d+\.\d+).*[\r\n]', content)
            new_ip_address = match.group(1)
            helpers.log("new_ip_address: '%s'" % new_ip_address)

            n_console.expect(r'Configuring cluster.*[\r\n]')
            n_console.expect(r'First-time setup is complete.*[\r\n]')
            n_console.expect(r'Press enter to continue > ')
            n_console.send('')
            helpers.sleep(3)  # Sleep for a few seconds just in case...
            return new_ip_address


    def first_boot_controller_menu_reset(self, node):
        """
       First boot setup Menu :   reset
        """
        t = test.Test()
        n = t.node(node)
        helpers.log("Entering ====> Reset and start over for node: '%s'" % node)
        helpers.log("Getting the console session for '%s'" % node)
        n_console = n.console()
        n_console.expect(r'\[1\] > ')
        content = n_console.content()
        helpers.log("USER INFO: the content is '%s'" % content)
        match = re.search(r'\[\s*(\d+)\] Reset and start over.*[\r\n$]', content)
        if match:
            option = match.group(1)
            helpers.log("USER INFO: the option is %s" % option)
        else:
            helpers.log("USER ERROR: there is no match")
            return False
        n_console.send(option)

        return True



    def first_boot_controller_menu_apply_negative(self, node, **kwargs):
        """
        First boot setup III: connect to the console to apply the setting.
            this is negative, if wrong gw is given. then NTP and DNS can not be reached
        First boot setup Menu :  Apply settings

        Author: Mingtao
        """
        t = test.Test()
        n = t.node(node)
        helpers.log("Entering ====>  first_boot_controller_menu_apply_negative for node: '%s'" % node)
        helpers.log("Getting the console session for '%s'" % node)
        n_console = n.console()
        n_console.expect(r'\[1\] > ')
        helpers.log("[1] Apply settings ")
        content = n_console.content()
        helpers.log("USER INFO: the content is '%s'" % content)
        match = re.search(r'\[\s*(\d+)\] Apply settings.*[\r\n$]', content)
        if match:
            option = match.group(1)
            helpers.log("USER INFO: the option is %s" % option)
        else:
            helpers.log("USER ERROR: there is no match")
            return False

        n_console.send(option)  # Apply settings
        n_console.expect(r'Initializing system.*[\r\n]')
        n_console.expect(r'Configuring controller.*[\r\n]')
        n_console.expect(r'Waiting for network configuration.*[\r\n]')
        options = n_console.expect([r'Unable to resolve domains with DNS.*[\r\n]', r'No route to host.*[\r\n]'], timeout=300)
        if options[0] == 0:
            n_console.expect(r'Retrieving time from NTP server.*[\r\n]', timeout=120)
            n_console.expect(r'unreachable now.*[\r\n]', timeout=120)
            n_console.expect(r'Configuring cluster.*[\r\n]', timeout=120)
        if options[0] == 1 :
            helpers.log("USER INFO: need to correct cluster ip")
        try:
            options = n_console.expect([r'\[1\] >', r'First-time setup is complete.*[\r\n]'], timeout=120)
        except:
            content = n_console.content()
            helpers.log("*****Output is :*******\n%s" % content)
            helpers.log("USER ERROR: there is no match")
            helpers.test_failure('There is no match')
        else:
            content = n_console.content()
            helpers.log("*****Output is :*******\n%s" % content)

            if options[0] == 0 :
                helpers.summary_log("*****Need to correct parameter *******  ")
                if 'gateway' in kwargs:
                    gateway = kwargs.get('gateway')
                    match = re.search(r'\[\s*(\d+)\] Update Gateway.*[\r\n$]', content)
                    if match:
                        option = match.group(1)
                        helpers.log("USER INFO: the option is %s" % option)
                    else:
                        helpers.log("USER ERROR: there is no match")
                        return False
                    n_console.send(option)  # Apply settings
                    n_console.expect(r'Gateway.*')
                    n_console.expect(r'Default gateway address.*> ')
                    n_console.send(gateway)
                    n_console.expect(r'\[1\] >')
                    content = n_console.content()
                if 'dns' in kwargs:
                    dns = kwargs.get('dns')
                    match = re.search(r'\[\s*(\d+)\] Update DNS Server.*[\r\n$]', content)
                    if match:
                        option = match.group(1)
                        helpers.log("USER INFO: the option is %s" % option)
                    else:
                        helpers.log("USER ERROR: there is no match")
                        return False
                    n_console.send(option)  # Apply settings
                    n_console.expect(r'DNS Server.*')
                    n_console.expect(r'DNS server address.* > ')
                    n_console.send(dns)
                    n_console.expect(r'\[1\] >')
                if 'cluster_ip' in kwargs:
                    clusterip = kwargs.get('cluster_ip')
                    match = re.search(r'\[\s*(\d+)\] Update Existing Controller Node IP Address.*[\r\n$]', content)
                    if match:
                        option = match.group(1)
                        helpers.log("USER INFO: the option is %s" % option)
                    else:
                        helpers.log("USER ERROR: there is no match")
                        return False
                    n_console.send(option)  # Apply settings
                    n_console.expect(r'Existing Controller Node IP Address.*')
                    n_console.expect(r'Existing Controller IP.* > ')
                    n_console.send(clusterip)
                    n_console.expect(r'\[1\] >')

                n_console.send('')  # Apply settings
                n_console.expect(r'Initializing system.*[\r\n]', timeout=120)
                n_console.expect(r'Configuring controller.*[\r\n]', timeout=120)
                n_console.expect(r'Configuring cluster.*[\r\n]', timeout=120)
                n_console.expect(r'First-time setup is complete.*[\r\n]', timeout=120)
                n_console.expect(r'Press enter to continue > ')
                n_console.send('')
                helpers.sleep(3)  # Sleep for a few seconds just in case...
                return True

            if options[0] == 1 :
                helpers.log("*****first boot complete *******  ")
                n_console.expect(r'Press enter to continue > ')
                n_console.send('')
                helpers.summary_log('First boot complete even the NTP/DNS not reachable')
        helpers.sleep(3)  # Sleep for a few seconds just in case...
        return True

    def cli_show_local_config(self, node):
        '''
        show the local node config
        '''

        t = test.Test()
        c = t.controller(node)

        c.enable('')
        c.enable("show running-config local")
        content = c.cli_content()
        helpers.log("*****Output is :\n%s" % content)
        temp = helpers.strip_cli_output(content)
        temp = helpers.str_to_list(temp)
        helpers.log("*****Output list   is :\n%s" % temp)

        localinfo = {}
        for line in temp:
            line = line.lstrip()
            helpers.log(" line is - %s" % line)
            if (re.match(r'.*hostname .*', line)):
                match = re.match(r'.*hostname (.*)', line)
                localinfo['hostname'] = match.group(1)

            elif (re.match(r'.*dns search.*', line)):
                match = re.match(r'.*dns search (.*)', line)
                localinfo['domain'] = match.group(1)

            elif (re.match(r'.*dns server.*', line)):
                match = re.match(r'.*dns server (.*)', line)
                localinfo['dns'] = match.group(1)

            elif (re.match(r'.*ip.* gateway.*', line)):
                match = re.match(r'.*ip (\d+\.\d+\.\d+\.\d+)/(\d+) gateway (\d+\.\d+\.\d+\.\d+)', line)
                localinfo['ip'] = match.group(1)
                localinfo['mask'] = match.group(2)
                localinfo['gateway'] = match.group(3)
            elif (re.match(r'.*Error: running command.*', line)):
                helpers.test_failure("Error:  there is a show command error \n %s " % line)

            helpers.log("INFO: *** local node info *** \n  %s" % localinfo)
        return localinfo


    def bash_df(self, node):
        ''' do df in debug bash
        ouput: index:  directory  with all the field
        '''
        t = test.Test()
        n = t.node(node)
        content = n.bash('df')['content']
        lines = helpers.strip_cli_output(content, to_list=True)
        lines = lines[1:]
        helpers.log("lines: %s" % lines)
        dfinfo = {}

        for line in lines:
            line = line.lstrip()
            fields = line.split()
            helpers.log("fields: %s" % fields)
            dfinfo[fields[5]] = {}
            dfinfo[fields[5]]['filesystem'] = fields[0]
            dfinfo[fields[5]]['1k-blocks'] = fields[1]
            dfinfo[fields[5]]['used'] = fields[2]
            dfinfo[fields[5]]['available'] = fields[3]
            dfinfo[fields[5]]['usedpercent'] = fields[4]
        helpers.log("USER INFO: dfinfo is :\n%s" % dfinfo)
        return dfinfo



    def get_disk_used_percentage(self, node, directory):
        '''
        get the used percentage for given directory
        '''
        dfinfo = self.bash_df(node)
        return dfinfo[directory]['usedpercent']


    def rest_configure_testpath_controller_view(self, **kwargs):
        '''
            This function will query the controller for the test packet path controller view
            Returns True if controller view returns without an error message.

            kwargs Examples:
                src-tenant=T1
                src-segment=v1
                src-ip=10.10.10.51
                dst-tenant=T1
                dst-segment=v1
                dst-ip=10.10.10.52
                ip-protocol=icmp
        '''
        t = test.Test()
        c = t.controller('master')
        url = '/api/v1/data/controller/applications/bcf/test/path/controller-view'

        if(kwargs.get('dst-segment')):
            url = url + '[dst-segment="%s"]' % (kwargs.get('dst-segment'))
        if(kwargs.get('dst-tenant')):
            url = url + '[dst-tenant="%s"]' % (kwargs.get('dst-tenant'))
        if(kwargs.get('ip-protocol')):
            if(kwargs.get('ip-protocol') == "icmp"):
                url = url + '[ip-protocol=1]'
            elif(kwargs.get('ip-protocol') == "tcp"):
                url = url + '[ip-protocol=6]'
            elif(kwargs.get('ip-protocol') == "udp"):
                url = url + '[ip-protocol=17]'
            # url = url + '[ip-protocol="%s"]' % (kwargs.get('ip-protocol'))
        if(kwargs.get('src-ip')):
            url = url + '[src-ip="%s"]' % (kwargs.get('src-ip'))
        if(kwargs.get('src-segment')):
            url = url + '[src-segment="%s"]' % (kwargs.get('src-segment'))
        if(kwargs.get('dst-ip')):
            url = url + '[dst-ip="%s"]' % (kwargs.get('dst-ip'))
        if(kwargs.get('src-tenant')):
            url = url + '[src-tenant="%s"]' % (kwargs.get('src-tenant'))
        if(kwargs.get('src-l4-port')):
            url = url + '[src-l4-port=%s]' % (kwargs.get('src-l4-port'))
        if(kwargs.get('dst-l4-port')):
            url = url + '[dst-l4-port=%s]' % (kwargs.get('dst-l4-port'))

        result = c.rest.get(url)['content']
        try:
            logicalError = result[0]['summary'][0]['logical-error']
            helpers.log("Test Path Error In Controller View: LogicalError: %s" % (logicalError))
            return False
        except (KeyError):
            try:
                physicalError = result[0]['summary'][0]['physical-error']
                helpers.log("Test Path Error In Controller View: PhysicalError: %s" % (physicalError))
                return False
            except (KeyError):
                helpers.log("Test Path Sucees In Controller View. No Errors Were Detected")
                return True

    def  rest_verify_testpath_error_code(self, errorCode, **kwargs):
        '''
            This function will query the controller for the test packet path controller view for the given error code
            Returns True if error code is a match
        '''

        t = test.Test()
        c = t.controller('master')
        url = '/api/v1/data/controller/applications/bcf/test/path/controller-view'

        if(kwargs.get('dst-segment')):
            url = url + '[dst-segment="%s"]' % (kwargs.get('dst-segment'))
        if(kwargs.get('dst-tenant')):
            url = url + '[dst-tenant="%s"]' % (kwargs.get('dst-tenant'))
        # if(kwargs.get('ip-protocol')):
        #    url = url + '[ip-protocol="%s"]' % (kwargs.get('ip-protocol'))
        if(kwargs.get('ip-protocol')):
            if(kwargs.get('ip-protocol') == "icmp"):
                url = url + '[ip-protocol=1]'
            elif(kwargs.get('ip-protocol') == "tcp"):
                url = url + '[ip-protocol=6]'
            elif(kwargs.get('ip-protocol') == "udp"):
                url = url + '[ip-protocol=17]'
        if(kwargs.get('src-ip')):
            url = url + '[src-ip="%s"]' % (kwargs.get('src-ip'))
        if(kwargs.get('src-segment')):
            url = url + '[src-segment="%s"]' % (kwargs.get('src-segment'))
        if(kwargs.get('dst-ip')):
            url = url + '[dst-ip="%s"]' % (kwargs.get('dst-ip'))
        if(kwargs.get('src-tenant')):
            url = url + '[src-tenant="%s"]' % (kwargs.get('src-tenant'))
        if(kwargs.get('src-l4-port')):
            url = url + '[src-l4-port=%s]' % (kwargs.get('src-l4-port'))
        if(kwargs.get('dst-l4-port')):
            url = url + '[dst-l4-port=%s]' % (kwargs.get('dst-l4-port'))


        result = c.rest.get(url)['content']
        try:
            logicalError = result[0]['summary'][0]['logical-error']
            helpers.log("Test Path Error In Controller View: LogicalError: %s" % (logicalError))
            if errorCode in logicalError:
                helpers.log("Error Code is a match : Returning True")
                return True
            else:
                helpers.log("Error Code is not a match : Returning False")
                return False
        except (KeyError):
            try:
                physicalError = result[0]['summary'][0]['physical-error']
                helpers.log("Test Path Error In Controller View: PhysicalError: %s" % (physicalError))
                if errorCode in physicalError:
                    helpers.log("Error Code is a match : Returning True")
                    return True
                else:
                    helpers.log("Error Code is not a match : Returning False")
                    return False
            except (KeyError):
                try:
                    forwardError = result[0]['summary'][0]['forward-result']
                    helpers.log("Test Path Forward Result code: %s" % (forwardError))
                    if errorCode in forwardError:
                        helpers.log("Error Code is a match : Returning True")
                        return True
                    else:
                        helpers.log("Error Code is not a match : Returning False")
                        return False
                except:
                    helpers.log("Test Path Sucees In Controller View. No Errors Were Detected")
                    helpers.log("Error Code is not a match : Returning False")
                    return False


    def rest_configure_testpath_fabric_view(self, **kwargs):
        '''
            This function will set up the fabric view for the controller.
            Returns True if the fabric view returns without an error message after the setup.

            kwargs Examples:
                test-name=Test1
                src-tenant=T1
                src-segment=v1
                src-ip=10.10.10.51
                dst-tenant=T1
                dst-segment=v1
                dst-ip=10.10.10.52
                ip-protocol=tcp
                src-l4-port=8000
                dst-l4-port=8500
        '''
        t = test.Test()
        c = t.controller('master')

        url = '/api/v1/data/controller/applications/bcf/test/path/setup-result'

        if(kwargs.get('test-name')):
            url = url + '[test-name="%s"]' % (kwargs.get('test-name'))
        if(kwargs.get('timeout')):
            url = url + '[timeout="%s"]' % (kwargs.get('timeout'))
        if(kwargs.get('dst-segment')):
            url = url + '[dst-segment="%s"]' % (kwargs.get('dst-segment'))
        if(kwargs.get('dst-tenant')):
            url = url + '[dst-tenant="%s"]' % (kwargs.get('dst-tenant'))
        # if(kwargs.get('ip-protocol')):
        #    url = url + '[ip-protocol="%s"]' % (kwargs.get('ip-protocol'))
        if(kwargs.get('ip-protocol')):
            if(kwargs.get('ip-protocol') == "icmp"):
                url = url + '[ip-protocol=1]'
            elif(kwargs.get('ip-protocol') == "tcp"):
                url = url + '[ip-protocol=6]'
            elif(kwargs.get('ip-protocol') == "udp"):
                url = url + '[ip-protocol=17]'
        if(kwargs.get('src-ip')):
            url = url + '[src-ip="%s"]' % (kwargs.get('src-ip'))
        if(kwargs.get('src-segment')):
            url = url + '[src-segment="%s"]' % (kwargs.get('src-segment'))
        if(kwargs.get('dst-ip')):
            url = url + '[dst-ip="%s"]' % (kwargs.get('dst-ip'))
        if(kwargs.get('src-tenant')):
            url = url + '[src-tenant="%s"]' % (kwargs.get('src-tenant'))
        if(kwargs.get('src-l4-port')):
            url = url + '[src-l4-port=%s]' % (kwargs.get('src-l4-port'))
        if(kwargs.get('dst-l4-port')):
            url = url + '[dst-l4-port=%s]' % (kwargs.get('dst-l4-port'))

        result = c.rest.get(url)['content']
        try:
            logicalError = result[0]['summary'][0]['logical-error']
            helpers.log("Test Path Error In Fabric View:  %s" % logicalError)
            return False
        except:
            helpers.log("Test Path Sucees In Setting Up Fabric View")
            return True


    def rest_verify_testpath_fabric_view(self, testName, trafficMode, *args, **kwargs):

        '''
            This function will verify the fabric view test path with the active traffic stream

            testName => testName from the rest_configure_testpath_fabric_view
            trafficMode => Ixia / HostPing
            args:
                Expected traffic path through the Leaf or Spine switches
                eg: "leaf  spine  leaf"
            kwargs:
                If trafficMode==Ixia:  stream:StreamName (Ixia streamName) [Optional, only if the user wants
                us to start the ixia stream]
                host:hostName (Hostname of the host which the ping should originate from)
                ip:pingIP (The IP address to ping)
        '''
        t = test.Test()
        c = t.controller("master")

        if(trafficMode == 'Ixia'):
            if 'stream' in kwargs:
                helpers.log("Test Path: Starting Ixia Stream: %s" % kwargs.get('stream'))
                ixia = Ixia.Ixia()
                ixia.start_traffic(kwargs.get('stream'))
                helpers.sleep(10)

        elif(trafficMode == 'HostPing'):
            pingThread = T5PlatformThreads(1, "hostPing", host=kwargs.get('host'), IP=kwargs.get('ip'))
            helpers.log("Starting ping thread to ping from %s to destIP: %s" % (kwargs.get('host'), kwargs.get('ip')))
            pingThread.start()
            helpers.sleep(3)

        url = '/api/v1/data/controller/applications/bcf/test/path/fabric-view[test-name="%s"]' % testName
        result = c.rest.get(url)['content']

        count = 0
        while(True):
            if(count == 3):
                helpers.log("Test Path Error During Validating Hops List")
                return  False
            count += 1
            currentHops = []
            currentFlowCount = {}
            currentPktInCount = {}
            try:
                for index, hop in enumerate(result[0]['physical-path']):
                    try:
                        if (index > len(args) - 1):
                            helpers.warn("Test Path Warning:Expected # of Hops:%s /Actual # of Hops:%s-Probably due to dynamic topology changes" % ((len(args), len(result[0]['physical-path']))))
                            # helpers.log("Test Path Error: Expected # of Hops: %s / Actual # of Hops: %s" % ((len(args), len(result[0]['physical-path']))))
                            # return False

                        if(index < len(args) - 1):
                            if args[index] not in hop["hop-name"]:
                                helpers.log("Test Path Error: Expected - %s / Actual - %s" % (args[index], hop["hop-name"]))
                                return False
                            else:
                                currentHops.append(hop['hop-name'])
                                currentFlowCount[hop["hop-name"]] = hop["tcam-counter"].strip('[]')
                                currentPktInCount[hop["hop-name"]] = hop["pktin-counter"].strip('[]')

                        else:
                            currentHops.append(hop['hop-name'])
                            currentFlowCount[hop["hop-name"]] = hop["tcam-counter"].strip('[]')
                            currentPktInCount[hop["hop-name"]] = hop["pktin-counter"].strip('[]')

                    except Exception as e:
                        helpers.log("Test Path Error During Validating Hops List: %s" % str(e))
                        return  False

                if(len(args) != len(currentHops)):
                    # helpers.log("Test Path Error: Expected # Hops : %s / Actual # Hops: %s" % (len(args), len(currentHops)))
                    # return False
                    helpers.warn("Test Path Warning:Expected # of Hops:%s /Actual # of Hops:%s-Probably due to dynamic topology changes" % ((len(args), len(result[0]['physical-path']))))

                break

            except Exception as e:
                helpers.log("Exception occured: %s" % str(e))
                helpers.log("Test Path: No Hops Detected. Retrying ...")


        helpers.sleep(3)
        url = '/api/v1/data/controller/applications/bcf/test/path/fabric-view[test-name="%s"]' % testName
        result = c.rest.get(url)['content']
        for hop in result[0]['physical-path']:
            try:
                newFlowCount = int(hop["tcam-counter"].strip('[]'))
                newPktInCount = int(hop["pktin-counter"].strip('[]'))

                if(newFlowCount > int(currentFlowCount[hop["hop-name"]])):
                    helpers.log("Hop: %s passing @ newTcamCount" % hop["hop-name"])
                    pass
                elif(newPktInCount > int(currentPktInCount[hop["hop-name"]])):
                    helpers.log("Hop: %s passing @ newPktInCount" % hop["hop-name"])
                    pass
                else:
                    helpers.log("Test Path Error During Flow Path Counting For Hop \"%s\": Previous Count- %s / New Count- %s" % (hop["hop-name"], currentFlowCount[hop["hop-name"]], newFlowCount))
                    return False

            except Exception as e:
                helpers.log("Test Path Error During Validating Hops List: %s" % str(e))
                return  False

        if(trafficMode == 'Ixia'):
            if 'stream' in kwargs:
                ixia.stop_traffic(kwargs.get('stream'))
        if(trafficMode == 'HostPing'):
            helpers.log("Waiting for Ping threads to Finish...Default time out : 30")
            pingThread.join(30)

        return True


    def rest_verify_testpath(self, pathName):
        ''' Verify whether the testpath is configured or not
            Returns: True if found
        '''
        t = test.Test()
        c = t.controller("master")

        url = '/api/v1/data/controller/applications/bcf/test/path/all-test'

        try:
            result = c.rest.get(url)['content']
            for testpath in result:
                if testpath['test-name'] == pathName:
                    helpers.log("Found path: %s in the test-path config" % pathName)
                    return True
        except:
            helpers.test_failure(c.rest.error())
            return False
        else:
            helpers.log("Didn't find path: %s in the test-path config" % pathName)
            return False

    def rest_verify_testpath_timeout(self, pathName):
        ''' Verify whether the testpath is timedout or not
            Returns : True if timedout
        '''
        t = test.Test()
        c = t.controller("master")

        url = '/api/v1/data/controller/applications/bcf/test/path/all-test'

        try:
            result = c.rest.get(url)['content']
            for testpath in result:
                if testpath['test-name'] == pathName:
                    if testpath['test-state'] == "TIMEDOUT":
                        helpers.log("Test Path: %s in TIMEDOUT state" % pathName)
                        return True
                    else:
                        helpers.log("Test Path: %s not in TIMEDOUT state" % pathName)
                        return False

        except:
            helpers.test_failure(c.rest.error())
            return False
        else:
            helpers.log("Didn't find path: %s in the test-path config" % pathName)
            return False

    def rest_clear_testpath(self, testname=""):
        ''' Verify whether the testpath is timedout or not
            Returns : True if timedout
        '''
        t = test.Test()
        c = t.controller("master")

        if(testname):
            url = '/api/v1/data/controller/applications/bcf/test/path/all-test[test-name="%s"]' % testname
            result = c.rest.delete(url)
        else:
            url = '/api/v1/data/controller/applications/bcf/test/path/all-test'
            result = c.rest.delete(url)


    def cli_walk_exec(self, string='', file_name=None, padding=''):
        ''' cli_exec_walk
           walk through exec/login mode CLI hierarchy
           output:   file cli_exec_walk
        '''
        t = test.Test()
        c = t.controller('master')
        c.cli('')
        helpers.log("********* Entering cli_exec_walk ----> string: %s, file name: %s" % (string, file_name))
        if string == '':
            cli_string = '?'
        else:
            cli_string = string + ' ?'
        c.send(cli_string, no_cr=True)
        # Match controller prompt for various modes (cli, enable, config, bash, etc).
        # See exscript/src/Exscript/protocols/drivers/bsn_controller.py
        prompt_re = r'[\r\n\x07]+(\w+(-?\w+)?\s?@?)?[\-\w+\.:/]+(?:\([^\)]+\))?(:~)?[>#$] '
        c.expect(prompt_re)
        # c.expect(r'[\r\n\x07][\w-]+[#>] ')
        content = c.cli_content()
        temp = helpers.strip_cli_output(content)
        temp = helpers.str_to_list(temp)
        helpers.log("********new_content:************\n%s" % helpers.prettify(temp))
        c.send(helpers.ctrl('u'))
        c.expect()
        c.cli('')

        string_c = string

        if file_name:
            helpers.log("opening file: %s" % file_name)
            fo = open(file_name, 'a')
            lines = []
            lines.append((padding + string))
            lines.append((padding + '----------'))
            for line in temp:
                lines.append((padding + line))
            lines.append((padding + '=================='))
            content = '\n'.join(lines)
            fo.write(str(content))
            fo.write("\n")

            fo.close()

        num = len(temp)
        padding = "   " + padding

        # Loop through commands and sub-commands
        for line in temp:
            string = string_c
            helpers.log(" line is - %s" % line)
            line = line.lstrip()
            keys = line.split(' ')
            key = keys.pop(0)
            helpers.log("*** key is - %s" % key)
            helpers.log("*** string is - %s" % string)
            helpers.log("*** stringc is - %s" % string_c)

            # Ignoring lines which do not contain actual commands
            if re.match(r'For', line) or re.match(r'Commands', line):
                helpers.log("Ignoring line - %s" % line)
                num = num - 1
                continue

            # Ignoring commands which are either disruptive or are only one level commands
            # These commands would have already been displayed with corresponding help in a previous top-level hierarchy
            if key == "reauth" or key == "echo" or key == "help" or key == "logout" or key == "ping" or key == "watch":
                helpers.log("Ignore line %s" % line)
                num = num - 1
                continue

            # Ignoring sub-commands under 'clear debug' and 'show debug'
            if key == "ApplicationManager" or key == "Controller" or key == "EndpointManager" or key == "FabricManager" or key == "com.bigswitch.floodlight.bvs.application" or key == "ForwardingDebugCounters" or key == "ISyncService" or key == "StatsCollector" or key == "VirtualRoutingManager" or key == "org.projectfloodlight.core" or key == "StatsCollector":
                helpers.log("Ignore line %s" % line)
                num = num - 1
                continue

            # Ignoring sub-commands under 'debug'
            if key == "bash" or key == "cassandra-cli" or key == "cli" or key == "cli-backtrace" or key == "cli-batch" or key == "description" or key == "netconfig" or key == "python" or key == "rest":
                helpers.log("Ignore line %s" % line)
                num = num - 1
                continue

            # Ignoring options that require user input or comments in <>
            if re.match(r'^<.+', line) and not re.match(r'^<cr>', line):
                helpers.log("Ignoring line - %s" % line)
                num = num - 1
                continue

            # Ignoring some sub-commands that may impact test run
            if ((key == '<cr>' and (re.match(r' terminal', string))) or re.match(r' show debug counters', string) or re.match(r' show debug events details', string) or\
                re.match(r' clear session session-id', string) or re.match(r' clear session user', string) or re.match(r' show debug event all events', string)):
                helpers.log("Ignoring line - %s" % string)
                num = num - 1
                continue

            # for interface related commands, only iterate through "all" and one specific interface
            if (re.match(r' show(.*)interface(.*)', string)):
                if key != 'leaf0a-eth1' and key != 'all' and key != '<cr>':
                    helpers.log("Ignoring line - %s" % string)
                    num = num - 1
                    continue

            # for switch related commands, only iterate through "all" and one specific switch
            if (re.match(r' show(.*)switch(.*)', string)):
                if key != 'leaf0a' and key != 'all':
                    helpers.log("Ignoring line - %s" % string)
                    num = num - 1
                    continue

            # for tenant related commands, only iterate through "all" and one specific tenant
            if (re.match(r' show(.*)tenant(.*)', string)):
                if key != 'A' and key != 'all':
                    helpers.log("Ignoring line - %s" % string)
                    num = num - 1
                    continue

            # for vns related commands, only iterate through "all" and one specific vns
            if (re.match(r' show(.*)vns(.*)', string)):
                if key != 'A1' and key != 'all':
                    helpers.log("Ignoring line - %s" % string)
                    num = num - 1
                    continue

            # skip 'show logging', 'show lacp interface', 'show stats interface-history interface', 'show stats interface-history switch' and 'show running-config' - no need to iterate through options
            if (re.match(r' show lacp interface', string)) or (re.match(r' show logging', string)) or (re.match(r' show stats interface-history interface', string)) or (re.match(r' show stats interface-history switch', string)):
                helpers.log("Ignoring line - %s" % string)
                num = num - 1
                continue

            # skip 'topic related commands' (PR BVS-2046)
            if (re.match(r' topic .*', string)):
                helpers.log("Ignoring line - %s" % string)
                num = num - 1
                continue

            # issue the <cr> to test that the command actually works
            if key == '<cr>':

                if re.match(r'boot.*', string) or re.match(r'.*compare.*', string) or re.match(r'.*configure.*', string) or re.match(r'.*copy.*', string) or re.match(r'.*delete.*', string) or re.match(r'.*enable.*', string) or re.match(r'.*end.*', string) or re.match(r'.*exit.*', string) or re.match(r'.*failover.*', string) or re.match(r'.*logout.*', string):
                    helpers.log("Ignoring line - %s" % string)
                    num = num - 1
                    continue

                if re.match(r'.*show controller.*', string) or re.match(r'.*no .*', string) or re.match(r'.*ping.*', string) or re.match(r'.*reauth.*', string) or re.match(r'.*set .*', string) or re.match(r'.*show logging.*', string) or re.match(r'.*system.*', string) or re.match(r'.*test.*', string) or re.match(r'.*upgrade.*', string) or re.match(r'.*watch.*', string):
                    helpers.log("Ignoring line - %s" % string)
                    num = num - 1
                    continue

                # skip due to BSC-6135
                if re.match(r'.*show local node interfaces.*', string):
                    helpers.log("Ignoring line due to PR BSC-6135 - %s" % string)
                    num = num - 1
                    continue

                helpers.log(" complete CLI show command: ******%s******" % string)
                if string == ' support':
                    helpers.log("Issuing %s cmd with timeout." % string)
                    c.cli(string, timeout=200)
                else:
                    helpers.log("Issuing cmd:%s with default timeout" % string)
                    c.cli(string)

                if num == 1:
                    helpers.log("AT END: ******%s******" % string)
                    return string

            # If command has sub-commands, call the function again to walk through sub-command options
            else:
                string = string + ' ' + key
                helpers.log("key - %s" % (key))
                helpers.log("string - %s" % (string))

                helpers.log("***** Call the cli walk again with  --- %s" % string)
                self.cli_walk_exec(string, file_name, padding)

    def cli_walk_enable(self, string='', file_name=None, padding=''):
        t = test.Test()
        c = t.controller('master')
        c.enable('')
        helpers.log("********* Entering CLI show  walk with ----> string: %s, file name: %s" % (string, file_name))
        if string == '':
            cli_string = '?'
        else:
            cli_string = string + ' ?'
        c.send(cli_string, no_cr=True)
        # Match controller prompt for various modes (cli, enable, config, bash, etc).
        # See exscript/src/Exscript/protocols/drivers/bsn_controller.py
        prompt_re = r'[\r\n\x07]+(\w+(-?\w+)?\s?@?)?[\-\w+\.:/]+(?:\([^\)]+\))?(:~)?[>#$] '
        c.expect(prompt_re)
        # c.expect(r'[\r\n\x07][\w-]+[#>] ')
        content = c.cli_content()
        temp = helpers.strip_cli_output(content)
        temp = helpers.str_to_list(temp)
        helpers.log("******new_content:\n%s" % helpers.prettify(temp))
        c.send(helpers.ctrl('u'))
        c.expect()

        string_c = string
        helpers.log("string for this level is: %s" % string_c)
        helpers.log("The length of string: %d" % len(temp))

        if file_name:
            helpers.log("opening file: %s" % file_name)
            fo = open(file_name, 'a')
            lines = []
            lines.append((padding + string))
            lines.append((padding + '----------'))
            for line in temp:
                lines.append((padding + line))
            lines.append((padding + '=================='))
            content = '\n'.join(lines)
            fo.write(str(content))
            fo.write("\n")

            fo.close()

        num = len(temp)
        padding = "   " + padding
        for line in temp:
            string = string_c
            helpers.log(" line is - %s" % line)
            line = line.lstrip()
            keys = line.split(' ')
            key = keys.pop(0)
            helpers.log("*** string is - %s" % string)
            helpers.log("*** key is - %s" % key)
            if re.match(r'All', line):
                helpers.log("Don't need to loop through exec commands- %s" % line)
                continue

            # Ignoring lines which do not contain actual commands
            if re.match(r'For', line) or re.match(r'Commands', line):
                helpers.log("Ignoring line - %s" % line)
                num = num - 1
                continue

            if re.match(r'^<.+', line) and not re.match(r'^<cr>', line):
                helpers.log("Ignoring line - %s" % line)
                num = num - 1
                continue

            # Ignoring sub-commands under 'clear debug' and 'show debug'
            if key == "ApplicationManager" or key == "ControllerCounters" or key == "EndpointManager" or key == "FabricManager" or key == "com.bigswitch.floodlight.bvs.application" or key == "ForwardingDebugCounters" or key == "ISyncService" or key == "OFSwitchManager" or key == "RoleManager" or key == "StatsCollector" or key == "VirtualRoutingManager" or key == "org.projectfloodlight.core" or key == "StatsCollector":
                helpers.log("Ignore line %s" % line)
                num = num - 1
                continue

            # Ignoring sub-commands under 'debug'
            if key == "bash" or key == "cassandra-cli" or key == "cli" or key == "cli-backtrace" or key == "cli-batch" or key == "description" or key == "netconfig" or key == "python" or key == "rest":
                helpers.log("Ignore line %s" % line)
                num = num - 1
                continue

            # Ignoring commands which are either disruptive or are only one level commands
            # These commands would have already been displayed with corresponding help in a previous top-level hierarchy
            if key == "reauth" or key == "echo" or key == "help" or key == "logout" or key == "ping" or key == "watch":
                helpers.log("Ignore line %s" % line)
                num = num - 1
                continue

            # for interface related commands, only iterate through "all" and one specific interface
            if (re.match(r' show(.*)interface(.*)', string)) or (re.match(r' clear(.*)interface-counter(.*)interface', string)):
                if key != 'leaf0a-eth1' and key != 'all' and key != '<cr>':
                    helpers.log("Ignoring line - %s" % string)
                    num = num - 1
                    continue

            # for switch related commands, only iterate through "all" and one specific switch
            if (re.match(r' show(.*)switch(.*)', string)) or (re.match(r' clear(.*)interface-counter(.*)switch', string)):
                if key != 'leaf0a' and key != 'all':
                    helpers.log("Ignoring line - %s" % string)
                    num = num - 1
                    continue

            # for tenant related commands, only iterate through "all" and one specific tenant
            if (re.match(r' show(.*)tenant(.*)', string)) or (re.match(r' clear(.*)vns-counter(.*)tenant(.*)', string)):
                if key != 'A' and key != 'all':
                    helpers.log("Ignoring line - %s" % string)
                    num = num - 1
                    continue

            # for vns related commands, only iterate through "all" and one specific vns
            if (re.match(r' show(.*)vns(.*)', string)) or (re.match(r' clear(.*)vns-counter(.*)vns(.*)', string)):
                if key != 'A1' and key != 'all':
                    helpers.log("Ignoring line - %s" % string)
                    num = num - 1
                    continue

            # Ignorning below cmd as it is effecting the script execution
            if (re.match(r' clear switch all.*', string)):
                helpers.log("Ignoring line - %s" % string)
                num = num - 1
                continue

            # Ignoring some sub-commands that may impact test run or require user input
            if ((key == '<cr>' and (re.match(r' terminal', string))) or re.match(r' test path', string) or \
                re.match(r' show debug counters', string) or re.match(r' show debug events details', string) or re.match(r' clear session session-id', string) or \
                re.match(r' clear session user', string) or re.match(r' show debug event all events', string)):
                helpers.log("Ignoring line - %s" % string)
                num = num - 1
                continue

            # for vns related commands, only iterate through "all" and one specific vns
            if (re.match(r' system reboot', string)) or (re.match(r' system shutdown', string)):
                helpers.log("Ignoring line - %s" % string)
                num = num - 1
                continue

            # for interface related commands, only iterate through "all" and one specific interface
            if (re.match(r' show(.*)interface(.*)', string)):
                if key != 'leaf0a-eth1' and key != 'all' and key != '<cr>':
                    helpers.log("Ignoring line - %s" % string)
                    num = num - 1
                    continue

            # for switch related commands, only iterate through "all" and one specific switch
            if (re.match(r' show(.*)switch(.*)', string)):
                if key != 'leaf0a' and key != 'all':
                    helpers.log("Ignoring line - %s" % string)
                    num = num - 1
                    continue

            # for tenant related commands, only iterate through "all" and one specific tenant
            if (re.match(r' show(.*)tenant(.*)', string)):
                if key != 'A' and key != 'all':
                    helpers.log("Ignoring line - %s" % string)
                    num = num - 1
                    continue

            # for vns related commands, only iterate through "all" and one specific vns
            if (re.match(r' show(.*)vns(.*)', string)):
                if key != 'A1' and key != 'all':
                    helpers.log("Ignoring line - %s" % string)
                    num = num - 1
                    continue

            # skip 'show logging', 'show lacp interface', 'show stats interface-history interface', 'show stats interface-history switch' - no need to iterate through options
            if (re.match(r' show lacp interface', string)) or (re.match(r' show logging', string)) or (re.match(r' show stats interface-history interface', string)) or (re.match(r' show stats interface-history switch', string)):
                helpers.log("Ignoring line - %s" % string)
                num = num - 1
                continue

            if key == '<cr>':

                if re.match(r'.*boot.*', string) or re.match(r'.*compare.*', string) or re.match(r'.*configure.*', string) or re.match(r'.*copy.*', string) or re.match(r'.*delete.*', string) or re.match(r'.*enable.*', string) or re.match(r'.*end.*', string) or re.match(r'.*exit.*', string) or re.match(r'.*failover.*', string) or re.match(r'.*logout.*', string):
                    helpers.log("Ignoring line - %s" % string)
                    num = num - 1
                    continue

                if re.match(r'.*show controller.*', string) or re.match(r'.*no .*', string) or re.match(r'.*ping.*', string) or re.match(r'.*reauth.*', string) or re.match(r'.*set .*', string) or re.match(r'.*show logging.*', string) or re.match(r'.*system.*', string) or re.match(r'.*test.*', string) or re.match(r'.*upgrade.*', string) or re.match(r'.*watch.*', string):
                    helpers.log("Ignoring line - %s" % string)
                    num = num - 1
                    continue

                # skip due to BSC-6135
                if re.match(r'.*show local node interfaces.*', string):
                    helpers.log("Ignoring line due to PR BSC-6135 - %s" % string)
                    num = num - 1
                    continue

                helpers.log(" complete CLI show command: ******%s******" % string)
                if string == ' support':
                    helpers.log("Issuing cmd:%s with timeout option.." % string)
                    c.enable(string, timeout=200)
                else:
                    helpers.log("Issuing cmd:%s with default timeout.." % string)
                    c.enable(string)

                if num == 1:
                    return string
            else:
                string = string + ' ' + key
                helpers.log("key - %s" % (key))
                helpers.log("***** Call the cli walk again with  --- %s" % string)
                self.cli_walk_enable(string, file_name, padding)

    def cli_walk_config(self, string='', file_name=None, padding='', config_submode=False, exec_mode_done=False, base_hierarchy=None):
        t = test.Test()
        c = t.controller('master')
        if base_hierarchy:
            c.config(base_hierarchy)
        else:
            c.config('')
        helpers.log("********* Entering CLI show  walk with ----> string: '%s', file name: '%s'" % (string, file_name))
        if string == '':
            cli_string = '?'
        else:
            cli_string = string + ' ?'
        c.send(cli_string, no_cr=True)
        # Match controller prompt for various modes (cli, enable, config, bash, etc).
        # See exscript/src/Exscript/protocols/drivers/bsn_controller.py
        prompt_re = r'[\r\n\x07]+(\w+(-?\w+)?\s?@?)?[\-\w+\.:/]+(?:\([^\)]+\))?(:~)?[>#$] '
        c.expect(prompt_re)
        # c.expect(r'[\r\n\x07][\w-]+[#>] ')
        # prompt_re = r'[\r\n\x07]?[\w\x07-]+\(([\w\x07-]+)\)(\x07)?[#>]'
        # c.expect(prompt_re)
        content = c.cli_content()
        helpers.log("********** CONTENT ************\n%s" % content)

        # Content is a multiline string. Convert it to a list of strings. Then
        # get the last entry which should be the prompt.
        prompt_str1 = helpers.str_to_list(content)[-1]

        # helpers.log("Prompt1: '%s'" % prompt_str1)

        match = re.match(prompt_re, prompt_str1)
        if match:
            prompt1 = match.group(1)
        else:
            helpers.log("No match")

        temp = helpers.strip_cli_output(content)
        temp = helpers.str_to_list(temp)
        helpers.log("******new_content:\n%s" % helpers.prettify(temp))
        c.send(helpers.ctrl('u'))
        c.expect()
        c.config('')
        string_c = string
        helpers.log("string for this level is: '%s'" % string_c)
        helpers.log("The length of string: '%d'" % len(temp))

        if file_name:
            helpers.log("opening file: '%s'" % file_name)
            fo = open(file_name, 'a')
            lines = []
            lines.append((padding + string))
            lines.append((padding + '----------'))
            for line in temp:
                lines.append((padding + line))
            lines.append((padding + '=================='))
            content = '\n'.join(lines)
            fo.write(str(content))
            fo.write("\n")

            fo.close()

        num = len(temp)
        padding = "   " + padding
        for line in temp:
            string = string_c
            helpers.log(" NUM IS - '%s'" % num)
            helpers.log(" line is - '%s'" % line)
            line = line.lstrip()
            helpers.log(" line: '%s'" % line)
            keys = line.split(' ')
            key = keys.pop(0)
            helpers.log("*** string is - '%s'" % string)
            helpers.log("*** key is - '%s'" % key)

            if re.match(r'Related config commands', line):
                helpers.log("Ignoring line - '%s'" % line)
                num = num - 1
                continue

            # If done iterating over enable commands, set exec_mode_done = True
            if re.match(r'.*Commands:.*', line):
                    helpers.log("Done with enable mode commands")
                    exec_mode_done = True
                    num = num - 1
                    continue

            # Don't iterate over enable commands again if looping through this via a subconfig mode
            if config_submode and not exec_mode_done:
                helpers.log("Ignoring EXEC MODE command - '%s'" % line)
                continue
            else:

                if re.match(r'For', line):
                    helpers.log("Ignoring line - '%s'" % line)
                    num = num - 1
                    continue

                if re.match(r'^<.+', line) and not re.match(r'^<cr>', line):
                    helpers.log("Ignoring line - '%s'" % line)
                    num = num - 1
                    continue
                if key == "debug" or key == "terminal"  or key == "reauth" or key == "echo" or key == "help" or key == "history" or key == "logout" or key == "ping" or key == "watch":
                    helpers.log("Ignore line '%s'" % line)
                    num = num - 1
                    continue
                if re.match(r'.*session.*', string) and key == "session" :
                    helpers.log("Ignore line - '%s'" % string)
                    num = num - 1
                    continue
                if re.match(r'.*session.*', string) and key != "<cr>" :
                    helpers.log("Ignore line - string '%s', key '%s'" % (string, key))
                    num = num - 1
                    continue
                if re.match(r'.*password.*', string) and key == "<cr>" :
                    helpers.log("Ignore line - '%s'" % string)
                    num = num - 1
                    continue

                # Add check for origination and description. BVS-1959 explains why this will not work if under a sub-configuration.
                if key == "origination" or key == "description" :
                    helpers.log("Ignore line - key '%s'" % key)
                    num = num - 1
                    continue


                # for interface related commands, only iterate through "all" and one specific interface
                if (re.match(r' (.*)interface(.*)', string)):
                    if key != 'leaf0a-eth1' and key != 'all' and key != '<cr>':
                        helpers.log("Ignoring line - '%s'" % string)
                        num = num - 1
                        continue

                # for switch related commands, only iterate through "all" and one specific switch
                if (re.match(r' (.*)switch(.*)', string)):
                    if key != 'leaf0a' and key != 'all' and key != '<cr>':
                        helpers.log("Ignoring line - '%s'" % string)
                        num = num - 1
                        continue

                # for tenant related commands, only iterate through "all" and one specific tenant
                if (re.match(r' (.*)tenant(.*)', string)):
                    if key != 'A' and key != 'all' and key != '<cr>':
                        helpers.log("Ignoring line - '%s'" % string)
                        num = num - 1
                        continue

                # for vns related commands, only iterate through "all" and one specific vns
                if (re.match(r' (.*)vns(.*)', string)):
                    if key != 'A1' and key != 'all' and key != '<cr>':
                        helpers.log("Ignoring line - '%s'" % string)
                        num = num - 1
                        continue

                # for lag related commands, only iterate through "any_leaf"
                if (re.match(r' (.*)lag(.*)', string)):
                    if key != 'any_leaf' and key != '<cr>':
                        helpers.log("Ignoring line - '%s'" % string)
                        num = num - 1
                        continue

                if re.match(r'.*shutdown.*', string) and re.match(r'.*controller.*', key):
                    helpers.log("Ignore line  - '%s' '%s'" % (string, key))
                    num = num - 1
                    continue

                if re.match(r' clear session session-id', string):
                    helpers.log("Ignoring line as it may effect the script execution..")
                    num = num - 1
                    continue

                if re.match(r'.*internal.*', key):
                    helpers.log("Ignore line  - '%s'" % string)
                    num = num - 1
                    continue

                if re.match(r'.*hashed-password.*', string):
                    helpers.log("Ignoring line - %s" % string)
                    num = num - 1
                    continue

                # skip command below due to PR BSC-6009
                if re.match(r'.*zerotouch device.*', string) or re.match(r'.*zerotouch unmanaged-device.*', string):
                    helpers.log("Ignoring line - %s" % string)
                    num = num - 1
                    continue

                if re.match(r'All', line):
                    helpers.log("Don't need to loop through exec commands- '%s'" % line)
                    num = num - 1
                    continue

                if key == '<cr>':

                    if re.match(r'.*boot.*', string) or re.match(r'.*compare.*', string) or re.match(r'.*copy.*', string) or re.match(r'.*delete.*', string) or re.match(r'.*enable.*', string) or re.match(r'.*end.*', string) or re.match(r'.*exit.*', string) or re.match(r'.*failover.*', string) or re.match(r'.*logout.*', string):
                        num = num - 1
                        continue

                    if re.match(r'.*support.*', string) or re.match(r'.*show controller.*', string) or re.match(r'.*no .*', string) or re.match(r'.*ping.*', string) or re.match(r'.*reauth.*', string) or re.match(r'.*set .*', string) or re.match(r'.*show logging.*', string) or re.match(r'.*system.*', string) or re.match(r'.*test.*', string) or re.match(r'.*upgrade.*', string) or re.match(r'.*watch.*', string):
                        num = num - 1
                        continue

                    # skip due to BSC-6135
                    if re.match(r'.*show local node interfaces.*', string):
                        helpers.log("Ignoring line due to PR BSC-6135 - %s" % string)
                        num = num - 1
                        continue

                    helpers.log(" complete CLI show command: ******%s******" % string)
                    c.config(string)

                    prompt_re = r'[\r\n\x07]?[\w-]+\(([\w-]+)\)[#>]'
                    content = c.cli_content()

                    helpers.log("********** CONTENT ************\n%s" % content)

                    # Content is a multiline string. Convert it to a list of strings. Then
                    # get the last entry which should be the prompt.
                    prompt_str2 = helpers.str_to_list(content)[-1]

                    match = re.match(prompt_re, prompt_str2)
                    if match:
                        prompt2 = match.group(1)
                    else:
                        helpers.log("No match")

                    helpers.log("Prompt1: '%s'" % prompt_str1)
                    helpers.log("Prompt2: '%s'" % prompt_str2)

                    # string after (stripped control char)
                    helpers.log("stripped Prompt1: %s" % helpers.strip_ctrl_chars(prompt_str1))
                    helpers.log("stripped Prompt1: %s" % helpers.strip_ctrl_chars(prompt_str2))

                    prompt1 = helpers.strip_ctrl_chars(prompt_str1)
                    prompt2 = helpers.strip_ctrl_chars(prompt_str2)

                    # skip due to PR BSC-6137
                    # if re.match(r'.*member port-group.*', string):
                    #    helpers.log("Ignoring line due to PR BSC-6137 - %s" % string)
                    #    num = num - 1
                    #    continue

                    # Compare prompts.
                    if not (re.match(r'.*config-tenant-seg-portgrouprule.*', prompt1) and re.match(r'.*config-tenant-seg.*', prompt2)):
                        if prompt1 != prompt2:
                            newstring = ''
                            helpers.log("***** Call the cli walk again with  --- '%s'" % string)

                            # If different, it means that we entered a new config submode.  Call the function again but set config_submode flag to True
                            c.config('show this')
                            self.cli_walk_config(newstring, file_name, padding, config_submode=True, exec_mode_done=False)

                    if num == 1:
                        return string
                else:
                    string = string + ' ' + key
                    helpers.log("***** Call the cli walk again with  --- '%s'" % string)
                    self.cli_walk_config(string, file_name, padding)

    def cli_walk_command(self, command, cmd_argument_count, cmd_argument=None, config_mode=False, multiline=None, soft_error=False):
        '''
            Execute CLI walk on controller
            Arguments:
            | command | Command to be executed |
            | cmd_argument_count | Number of lines in command help |
            | cmd_argument | Specific arguments that you want the function to look for in the command help|

            Description:
            This function checks for couple of things:
            | 1 | Number of lines in help output is what user has specified |
            | 2 | The CLI command does not have '<cr> <cr>' in its help output|
            | 3 | The CLI command is not missing a help string for some sub command |
            | 4 | if user has specified one or more arguments, those arguments are present in the help string|

            Example:
            |cli walk command |  show switch all | 6 | |
            |cli walk command |  show tenant | 14 | tenant1 tenant2 tenant3|
            |cli walk command |  show switch | 9 | leaf0-a leaf0-b spine0|

            example output of command:
            kk-mcntrlr-c1> show switch <====== Here number of lines are 13, but ideally you should see only 9. (this would be an error). THIS WOULD BE CAUGHT
            Keyword Choices:
                <cr>                            Show fabric information for selected switch
                all                             Show fabric information for selected switch
            Switch Name:Enter a switch name:Name of the switch.
            The field here primarily is a weak reference to that configured
            under core/switch-config/name.
                leaf0-a                         Switch Name selection of
                leaf0-b                         Switch Name selection of
                spine0                          Switch Name selection of
            core/proxy/controller/dpid:MAC Address
            core/proxy/environment/dpid:MAC Address
            core/proxy/inventory/dpid:MAC Address
            switch-name:Switch Name Selection:Switch Name selection
            kk-mcntrlr-c1>

            alpha-cont1> show switch all
            <cr> <cr><================================ THIS WOULD BE CAUGHT
            <cr>            Show fabric information for selected switch
            agent-counters  Show counters for various agents on the Switch
            connections     Show fabric information for selected switch
            details         Show fabric information for selected switch
            interface       <help missing> SHOW_INTERFACE_STATS_COMMAND_DESCRIPTION <====THIS WOULD BE CAUGHT
        '''
        try:
            t = test.Test()
            c = t.controller('master')
        except:
            return False
        else:
            cli_string = command + ' ?'

            if config_mode is True :
                if multiline is not None:
                    c.config(str(multiline))
                    c.send(cli_string, no_cr=True)
                else:
                    c.config('')
                    c.send(cli_string, no_cr=True)
            else:
                c.send(cli_string, no_cr=True)

            # Match controller prompt for various modes (cli, enable, config, bash, etc).
            # See exscript/src/Exscript/protocols/drivers/bsn_controller.py
            prompt_re = r'[\r\n\x07]+(\w+(-?\w+)?\s?@?)?[\-\w+\.:/]+(?:\([^\)]+\))?(:~)?[>#$] '
            c.expect(prompt_re, timeout=100)

            content = c.cli_content()
            temp = helpers.strip_cli_output(content)
            temp = helpers.str_to_list(temp)
            helpers.log("********new_content:************\n%s" % helpers.prettify(temp))
            c.send(helpers.ctrl('u'))
            c.expect()
            c.cli('')
            num = len(temp)
            if num == int(cmd_argument_count):
                helpers.log("Correct number of arguments found in CLI help output")
            else:
                helpers.log("Correct number of arguments not returned", soft_error)
                return False

            if "<cr> <cr>" in content:
                helpers.test_failure("CLI command has an incorrect help string '<cr> <cr>'", soft_error)

            if "<help missing>" in content:
                helpers.test_failure("CLI command has a missing help", soft_error)

            if (cmd_argument is not None) :
                if (' ' in cmd_argument):
                    new_string = cmd_argument.split()
                    helpers.log("New String is %s" % new_string)
                    helpers.log("Temp is %s" % content)
                    for index in range(len(new_string)):
                        if (str(new_string[index]) in content):
                            helpers.log("Argument %s found in CLI help output" % new_string[index])
                        else:
                            helpers.log("Argument %s NOT found in CLI help output. Error was %s " % (new_string[index], soft_error))
                            return False
                else:
                    if (str(cmd_argument) in content):
                        helpers.log("Argument %s found in CLI help output" % cmd_argument)
                    else:
                        helpers.log("Argument %s NOT found in CLI help output. Error was %s " % (cmd_argument, soft_error))
                        return False
            return True
    def cli_reboot_switch_name(self, node='master', switch=None):
        """
        Reboot switch, switches from controller's CLI

        Inputs:
        | node | reference to controller as defined in .topo file |
        | switch | if None,  then reboot all the switches one by one  |

        Return Value:
        - True if successfully executed reboot command, False otherwise
        """
        t = test.Test()
        c = t.controller(node)

        if switch is None:
            url = '/api/v1/data/controller/applications/bcf/info/fabric/switch'
            helpers.log("get switch fabric connection state")

            c.rest.get(url)
            data = c.rest.content()
            switch = []
            if (data):
                for i in range(0, len(data)):
                    switch.append(data[i]['name'])
        else:
            switch = switch.split(',')

        helpers.log("USER INFO - switches are:  %s" % switch)

        for sw in switch:
            c.enable('')
            c.send("system reboot switch %s" % sw)
            options = c.expect([r'.*\("y" or "yes" to continue\):', c.get_prompt()])

            if options[0] == 0:  # login prompt
                c.send("yes")
                c.expect()
            helpers.log("USER INFO: content is: ====== \n  %s" % c.cli_content())

            if "Error" in c.cli_content():
                helpers.test_failure("Error rebooting the switch %s " % sw)

            helpers.log("Reboot switch executed successfully %s" % sw)
        return True

    def cli_reboot_switch_ip(self, node='master', switch=None):
        """
        Reboot switch, switches from controller's CLI

         Inputs:
        | node | reference to controller as defined in .topo file |
        | switch | if None,  then reboot all the switches one by one  |

        Return Value:
        - True if successfully executed reboot command, False otherwise
        """
        t = test.Test()
        c = t.controller(node)

        if switch is None:
            url = '/api/v1/data/controller/applications/bcf/info/fabric/switch'
            helpers.log("get switch fabric connection state")

            c.rest.get(url)
            data = c.rest.content()
            switch = []
            if (data):
                for i in range(0, len(data)):
                    if 'inet-address' in data[i].keys() and 'ip' in data[i]['inet-address'].keys():
                        switch.append(data[i]['inet-address']['ip'])
                    else:
                        helpers.log("ERROR:  there is no ip address for: %s" % data[i]['name'])
        else:
            switch = switch.split(',')
        helpers.log("USER INFO - switches are:  %s" % switch)
        for ip in switch:
            c.enable('')
            c.send("system reboot switch %s" % ip)

            options = c.expect([r'.*\(\"y\" or \"yes\" to continue\): ', c.get_prompt()], timeout=60)
            if options[0] == 0:  # login prompt
                c.send('yes')
                c.expect()

            helpers.log("USER INFO: content is: ====== \n  %s" % c.cli_content())
            if "Error" in c.cli_content():
                helpers.test_failure("Error rebooting the switch")
            helpers.log("Reboot command executed successfully")
            return True

    def cli_reboot_switch_mac(self, node='master', switch=None):
        """
        Reboot switch, switches from controller's CLI

         Inputs:
        | node | reference to controller as defined in .topo file |
        | switch | if None,  then reboot all the switches one by one  |

        Return Value:
        - True if successfully executed reboot command, False otherwise
        """
        t = test.Test()
        c = t.controller(node)
        if switch is None:
            url = '/api/v1/data/controller/applications/bcf/info/fabric/switch'
            helpers.log("get switch fabric connection state")

            c.rest.get(url)
            data = c.rest.content()
            switch = []
            if (data):
                for i in range(0, len(data)):
                    if 'dpid' in data[i].keys():
                        macs = data[i]['dpid'].split(':', 2)
                        mac = macs[2]
                        switch.append(mac)

        else:
            switch = switch.split(',')

        helpers.log("USER INFO - switches are:  %s" % switch)

        for mac in switch:
            c.enable('')
            c.send("system reboot switch %s" % mac)
            options = c.expect([r'.*\("y" or "yes" to continue\):', c.get_prompt()])
            if options[0] == 0:  # login prompt
                c.send("yes")
                c.expect()

            helpers.log("USER INFO: content is: ====== \n  %s" % c.cli_content())
            if "Error" in c.cli_content():
                helpers.test_failure("Error rebooting the switch")
            helpers.log("Reboot command executed successfully")
            return True

    def cli_reboot_switch_all(self, node='master'):
        """
        Reboot switch all , switches from controller's CLI

        Inputs:
        | node | reference to controller as defined in .topo file |
        |

        Return Value:
        - True if successfully executed reboot command, False otherwise
        """
        t = test.Test()
        c = t.controller(node)
        c.enable('')
        c.send("system reboot switch all")
        c.expect(r'.*\("y" or "yes" to continue\):')
        c.send("yes")
        c.expect()

        helpers.log("USER INFO: content is: ====== \n  %s" % c.cli_content())
        if "Error" in c.cli_content():
            helpers.test_failure("Error rebooting the switch")
        helpers.log("Reboot command executed successfully")

        return True


    def ip_to_list(self, ip):
        helpers.test_log("Entering ==> ip to list: %s" % ip)
        return  ip.split('.')

    def bash_get_key(self, node='master', key='ecdsa'):
        '''
        get the public key for controller
        Ouput: index:  directory  with all the field
        '''
        t = test.Test()
        n = t.node(node)
        if key == 'ecdsa':
            content = n.bash('ssh-keygen -lf /etc/ssh/ssh_host_ecdsa_key.pub')['content']
            line = helpers.strip_cli_output(content)
            line = line.lstrip()
            fields = line.split()
            helpers.log("USER INFO: ECDSA key is :\n%s" % fields[1])
        elif key == 'dsa':
            content = n.bash('ssh-keygen -lf /etc/ssh/ssh_host_dsa_key.pub')['content']
            line = helpers.strip_cli_output(content)
            line = line.lstrip()
            fields = line.split()
            helpers.log("USER INFO: DSA key is :\n%s" % fields[1])
        elif key == 'rsa':
            content = n.bash('ssh-keygen -lf /etc/ssh/ssh_host_rsa_key.pub')['content']
            line = helpers.strip_cli_output(content)
            line = line.lstrip()
            fields = line.split()
            helpers.log("USER INFO: RSA key is :\n%s" % fields[1])

        return fields[1]

    def rest_get_suspended_switch(self, node='master'):
        """
        Get fabric connection state of the switch

        Inputs:
        | node | Alias of the controller node |

        Return Value:
        - the list of switches in suspended state
        """
        t = test.Test()
        c = t.controller(node)
        url = '/api/v1/data/controller/applications/bcf/info/fabric/switch'
        helpers.log("get switch fabric connection state")

        c.rest.get(url)
        data = c.rest.content()
        info = []
        if (data):
            for i in range(0, len(data)):
                if data[i]['connected'] == True:
                    if 'fabric-connection-state' in data[i].keys() and (
                        data[i]['fabric-connection-state'] == "not_connected" or data[i]['fabric-connection-state'] == "suspended"):
                        if 'handshake-state' in data[i].keys() and (
                            data[i]['handshake-state'] == "quarantine-state" or data[i]['handshake-state'] == "master-state"):
                            info.append(data[i]['name'])
        helpers.test_log("USER INFO:  the switches in suspended states:  %s" % info)
        return info

    def rest_get_disconnect_switch(self, node='master'):
        """
        Get fabric connection state of the switch

        Inputs:
        | node | Alias of the controller node |

        Return Value:
        - the list of switches in suspended state
        """
        t = test.Test()
        c = t.controller(node)
        url = '/api/v1/data/controller/applications/bcf/info/fabric/switch'
        helpers.log("get switch fabric connection state")

        c.rest.get(url)
        data = c.rest.content()
        info = []
        if (data):
            for i in range(0, len(data)):
                if data[i]['connected'] == False :
                    if 'fabric-connection-state' in data[i].keys() and data[i]['fabric-connection-state'] == "not_connected":
                        info.append(data[i]['name'])
        helpers.test_log("USER INFO:  the switches in NOT connected states:  %s" % info)
        return info

    def cli_boot_partition(self, node='master', option='alternate'):
        '''
          boot partition  -
          Author: Mingtao
          input:  node  - controller
                          master, slave, c1 c2

          usage:
          output: True  - boot successfully
                  False  -boot Not successfully
        '''

        t = test.Test()
        c = t.controller(node)
        helpers.log('INFO: Entering ==> cli_boot_partition ')
        c.config('')
        string = 'boot partition ' + option

        c.send(string)
        c.expect(r'[\r\n].+ to continue\):', timeout=180)
        content = c.cli_content()
        helpers.log("*****USER INFO:\n%s" % content)
        c.send("yes")

        try:
            c.expect(r'[\r\n].+The system is going down for reboot NOW!')
            content = c.cli_content()
            helpers.log("*****Output is :\n%s" % content)
        except:
            helpers.log('ERROR: boot partition NOT successfully')
            return False
        else:
            helpers.log('INFO: boot partition successfully')
            return True
        return False


    def console_switch_config(self, node, config, password='adminadmin'):
        """
        config given node (switch)

        Inputs:
        | node | Alias of the node to use |
        | config|  config string

        Return Value:
        - True
        """
        t = test.Test()
        s = t.dev_console(node, modeless=True)
        s.send("\r")
        options = s.expect([r'[\r\n]*.*login:', s.get_prompt()],
                           timeout=300)
        if options[0] == 0:  # login prompt
            s.send('admin')
            options = s.expect([ r'[Pp]assword:', s.get_prompt()])
            if options[0] == 0:
                helpers.log("Logging in as admin with password %s" % password)
                s.cli(password)
        s.cli('enable; config')
        s.send(config)
        helpers.log(s.cli('')['content'])
        return True

    def cli_upgrade_launch_HA(self, node='master', option=''):
        '''
          upgrade launch  -  2 step of upgrade
          Author: Mingtao
          input:  node  - controller
                          c1 c2

          usage:
          output: True  - upgrade launched successfully
                  False  -upgrade launched Not successfully
        '''


        t = test.Test()
        c = t.controller(node)
        helpers.log('INFO: Entering ==> cli_upgrade_launch_HA ')
        role = self.cli_get_node_role(node=node)
        helpers.log("USER INFO: current controller:  %s  is :  %s" % (node, role))

        c.config('')
        string = 'upgrade launch ' + option
        c.send(string)
        c.expect(r'[\r\n].+ \("y" or "yes" to continue\):', timeout=180)
        content = c.cli_content()
        helpers.log("*****USER INFO:\n%s" % content)
        c.send("yes")
        if role == 'active':
            helpers.log("USER INFO: I AM controller : %s is:   %s" % (node, role))
            helpers.summary_log('Active controller is upgradeing ..... ')
            options = c.expect([r'fabric is redundant', r'.* \(\"y\" or \"yes\" to continue\):'], timeout=300)
            if options[0] == 1:
                c.send("yes")
            try:
                options = c.expect([r'The system is going down for reboot NOW!', r'.*aborted' , c.get_prompt()], timeout=1200)
            except:
                helpers.log('ERROR: upgrade stuck for more than 20 minutes!!!!!!!!!!')
                c.send(helpers.ctrl('c'))
                helpers.summary_log('Ctrl C is hit during upgrade')
                c.expect(timeout=900)
                return False
            else:
                content = c.cli_content()
                helpers.log("*****USER INFO: the upgrade outout is *****\n%s\n\n*****" % content)
                if options[0] == 1:
                    helpers.log("ERROR: upgrade ABORTED")
                    c.expect(timeout=900)
                    return False
                elif options[0] == 2:
                    helpers.log("ERROR: upgrade FAILED")

                    return False
                # TBD Mingtao  change the idle timer
                helpers.log("INFO: Active Node - %s is rebooting" % c.name())
                if self.verify_controller_reachable(node):
                    helpers.log("INFO: Active Node - %s is UP - Wating for it to come to full function" % c.name())
                    helpers.sleep(60)
                    helpers.log("Node reconnect for '%s'" % c.name())
                    c = t.node_reconnect(c.name())
                    c.enable('show switch')
                    t.cli_add_controller_idle_and_reauth_timeout(c.name(), reconfig_reauth=False)
                else:
                    helpers.log("INFO: self.verify_controller_reachable is false")

                return True

        elif role == 'standby':
            helpers.log("USER INFO: I am controller : %s is:   %s" % (node, role))
            helpers.summary_log('Standby controller is upgradeing .... . ')
            try:
                options = c.expect([r'[R|r]ebooting', r'.*upgrade has been aborted' , c.get_prompt()], timeout=300)
            except:
                helpers.log('ERROR: upgrade stuck for more than 5 minutes!!!!!!!!!!')
                c.send(helpers.ctrl('c'))
                helpers.summary_log('Ctrl C is hit during stage')
                c.expect(timeout=900)
                return False
            else:
                content = c.cli_content()
                helpers.log("*****USER INFO: the upgrade outout is *****\n%s\n\n*****" % content)

                if options[0] == 1:
                    helpers.log("ERROR: upgrade ABORTED")
                    c.expect(timeout=900)
                    return False
                elif options[0] == 2 :
                    helpers.log("ERROR: upgrade FAILED")
                    return False

                # TBD  Mingtao
                helpers.log("INFO: Standby Node - %s is rebooting" % c.name())
                if self.verify_controller_reachable(node):
                    helpers.log("INFO: Standby Node - %s is UP - Wating for it to come to full function" % c.name())
                    helpers.sleep(60)
                    helpers.log("Node reconnect for '%s'" % c.name())
                    c = t.node_reconnect(c.name())
                    c.enable('show switch')
                    t.cli_add_controller_idle_and_reauth_timeout(c.name(), reconfig_reauth=False)
                else:
                    helpers.log("INFO: self.verify_controller_reachable is false")

                return True
        else:
            helpers.test_failure("ERROR: can not determine the role of the controller")
            return False


    def rest_add_tenant_vns_scale(self, tenantcount='1', tname='T', tenant_create=None,
                                        vnscount='1', vname='V', vns_create='yes',
                                        vns_ip=None, base="100.0.0.100", step="0.1.0.0", mask="24"
                                        ):
        '''
        Function to add l3 endpoint to all created vns
        Input: tennat , switch , interface
        The ip address is taken from the logical interface, the last byte is modified to 253
        output : will add end into all vns in a tenant
        '''

        t = test.Test()
        c = t.controller('master')

        t5 = T5.T5()
        l3 = T5L3.T5L3()
        helpers.test_log("Entering ==> rest_add_tenant_vns_scale ")

        for count in range(0, int(tenantcount)):
            tenant = tname + str(count)

            if tenant_create == 'yes':
                if not t5.rest_add_tenant(tenant):
                    helpers.test_failure("USER Error: tenant is NOT configured successfully")
            elif  tenant_create is None:
                if (re.match(r'None.*', self.cli_show_tenant(tenant))):
                    helpers.test_log("tenant: %s  does not exist,  creating tenant")
                    if not t5.rest_add_tenant(tenant):
                        helpers.test_failure("USER Error: tenant is NOT configured successfully")

            if vns_create == 'yes' :
                helpers.test_log("creating tenant L2 vns")
                if not t5.rest_add_vns_scale(tenant, vnscount, vname):
                    helpers.test_failure("USER Error: VNS is NOT configured successfully for tenant %s" % tenant)
            if vns_ip is not None:
                i = 1
                while  (i <= int(vnscount)):
                    vns = vname + str(i)
                    l3.rest_add_router_intf(tenant, vns)
                    if not l3.rest_add_vns_ip(tenant, vns, base, mask):
                        helpers.test_failure("USER Error: VNS is NOT configured successfully for tenant %s" % tenant)
                    ip_addr = helpers.get_next_address('ipv4', base, step)
                    base = ip_addr
                    i = i + 1

        c.cli('show running-config tenant')['content']
        return True


    def cli_show_tenant(self, tenant):
        '''
        show tenant
        Input: tenant
        Output:
        Author: Mingtao
        '''
        t = test.Test()
        c = t.controller('master')
        cli = 'show tenant ' + tenant
        content = c.cli(cli)['content']
        temp = helpers.strip_cli_output(content)
        return temp

    def cli_show_vns(self, tenant, vns):
        '''
        show tenant
        Input: tenant
        Output:
        Author: Mingtao
        '''
        t = test.Test()
        c = t.controller('master')

        cli = 'show tenant ' + tenant + ' segment ' + vns
        content = c.cli(cli)['content']
        temp = helpers.strip_cli_output(content)
        return temp


    def fabric_consistency_checker(self, node):
        ''' This function checks the consistency between active and standby nodes.
            Specifically it'll look for:
                1) running-config mismatches between active & standby.
                2) All the runtime fabric integrity verifications which includes:
                        switchlists/endpoints/lags/links/forwarding tables etc

            Arguments: node - linux host name from the topo file which it will use to scp the running configs
        '''

        t = test.Test()
        obj = utilities()
        n = t.node(node)
        nodeIP = n.ip()

        scpLocation = "scp://root@" + nodeIP + ":/root/autoConfig1.txt"
        returnVal = self.cli_copy("running-config", scpLocation)
        if(returnVal):
            helpers.sleep(3)
            scpLocation = "scp://root@" + nodeIP + ":/root/autoConfig2.txt"
            returnVal = self.cli_copy("running-config", scpLocation, "slave")
            if(returnVal):
                returnVal = utilities.cli_diff_running_configs(obj, node, "autoConfig1.txt", "autoConfig2.txt")
                if(returnVal):
                    helpers.log("Configs matches between 2 nodes. Moving on to run time state validations")
                    utilities.fabric_integrity_checker(obj, "before", "single", "Yes")
                    return utilities.fabric_integrity_checker(obj, "after", "single", "Yes")
                else:
                    helpers.log("Error verifying diff between two running config files. Looks like something is off")
                    return False
            else:
                helpers.log("Error during Copying running config to autoConfig2.txt")
                return False
        else:
            helpers.log("Error during Copying running config to autoConfig1.txt")
            return False


    def spawn_log_in(self, sessions=1, node='master'):

        bsn = bsnCommon()
        helpers.log("***Entering==> spawn_log_in   \n")

        t = test.Test()
        ip = bsn.get_node_ip(node)
        session_id = []
        for loop in range (0, int(sessions)):
            helpers.log('USR info:  this is loop:  %d' % loop)
            n = t.node_spawn(ip)
            session_id.append(n)
            n.bash('netstat | grep ssh')
            n.bash('netstat | grep ssh | wc -l')
        helpers.log("***Exiting==> spawn_log_in   \n")

        return session_id

    def spawn_log_out(self, session_id, node='master'):

        bsn = bsnCommon()
        helpers.log("***Entering==> spawn_log_out   \n")

        for session in session_id:
            session.close()

        helpers.log("***Exiting==> spawn_log_out   \n")
        return True

    def generate_support(self, node='master'):
        helpers.log("***Entering==> generate support file  \n")

        t = test.Test()
        c = t.controller(node)

        c.enable('')
        c.send('support')
        options = c.expect([r'\(yes/no\)\?', c.get_prompt()], timeout=1800)
        if options[0] == 0 :
            c.send('yes')
            c.expect(timeout=1200)
        content = c.cli_content()
        temp = helpers.strip_cli_output(content)
        lines = helpers.str_to_list(temp)
        helpers.log("*****Output is :\n%s" % temp)
        for line in lines:
            helpers.log("INFO: line is %s" % line)
            match = re.match(r'Name.*: (floodlight.*)', line)
            if match:
                helpers.log("INFO: file name is: %s" % match.group(1))
                return  match.group(1)

        helpers.test_failure("Error: %s" % temp)

    def delete_support(self, node='master', filename=None):
        helpers.log("***Entering==> delete support file \n")

        t = test.Test()
        c = t.controller(node)

        c.enable('')
        if filename is None:
            c.enable('show support')
            content = c.cli_content()
            output = helpers.strip_cli_output(content)
            lines = helpers.str_to_list(output)
            for line in lines:
                helpers.log("INFO: line is %s" % line)
                match = re.match(r'[0-9]*.* floodlight.*', line, flags=re.M)
                if match:
                    helpers.log("INFO: file name is is: %s" % line.split(' ')[1])
                    c.enable('delete support ' + line.split(' ')[1])

        else:
            c.enable('delete support ' + filename)
        return True

    def cli_get_upgrade_progress(self, node='master'):
        '''
          monitor upgrade launch  in the system "show upgrade progress"
          Author: Mingtao
          input:  node  - controller
                          master, slave, c1 c2
                  breakpoint - phase 1 ,  phase 2 ..
          usage:   cli_monitor_upgrade_launch
          output:  return True when hit the breakpoint

        '''

        t = test.Test()
        c = t.controller(node)
        helpers.log('INFO: Entering ==> cli_get_upgrade_progress')
        c.enable(" show upgrade progress")
        content = c.cli_content()
        helpers.log("*****Output is :\n%s" % content)
        temp = helpers.strip_cli_output(content)
        temp = helpers.str_to_list(temp)
        helpers.log("*****Output list   is :\n%s" % temp)

        if re.match(r'Error:.*', temp[0]):
            helpers.log("Error: %s" % temp[0])
            helpers.test_failure("Error: %s" % temp[0])

        elif re.match(r'upgrade not active', temp[0]):
            helpers.log("USR INFO:  upgrade is not active")
            return {'local': 'not active', 'remote': 'not active'}

        else:
            match = re.match(r'.* Local: (.*)Remote: (.*)', temp[0])
            if match:
                local = match.group(1)
                remote = match.group(2)
                return {'local': local, 'remote': remote}

            else:
                helpers.test_failure("USR Error: did not get the upgrade state: \n %s" % temp[0])


    def cli_monitor_upgrade_launch(self, node, breakpoint=None):
        '''
          monitor upgrade launch  in the system "show upgrade progress"
          Author: Mingtao
          input:  node  - controller
                          master, slave, c1 c2
                  breakpoint - phase 1 ,  phase 2 ..
          usage:   cli_monitor_upgrade_launch
          output:  return True when hit the breakpoint

        '''
        helpers.log('INFO: Entering ==> cli_monitor_upgrade_launch')
        is_continuous = True
        iteration = 0
        while is_continuous:
            is_continuous = False
            iteration += 1
            result = self.cli_get_upgrade_progress(node=node)
            local = result['local']
            remote = result['remote']
            helpers.log("USER INFO: **** %d. upgrade state: Local -  %s ; Remote - %s*****" % (iteration, local, remote))
            if ('phase1' == breakpoint) and ('phase-1-migrate' == remote):
                helpers.log("USER INFO:  upgrade is in:  Phase 1 migrate ")
                return True
            elif ('phase2' == breakpoint) and ('phase-2-migrate' == remote):
                helpers.log("USER INFO: upgrade is in:   Phase 2 migrate ")
                return True

            elif 'not active' in local  and  'not active' in remote:
                return  True
            else:
                is_continuous = True

            if iteration >= 40 :
                helpers.log('USR ERROR: exceed 20 minutes ')
                return False

            helpers.sleep(30)


    def cli_show_endpoint_pattern(self, pattern):
        '''
        '''
        helpers.test_log("Entering ==> cli_show_endpoint_filter: %s" % pattern)
        t = test.Test()
        c = t.controller('master')
        cli = 'show endpoint | grep ' + pattern + ' | wc -l'
        content = c.cli(cli)['content']
        temp = helpers.strip_cli_output(content)
        return temp

    def rest_get_switch_connection(self, switch=None):
        '''
                Objective:
                - Get the switch connections from controller

                Input:
                | switch name |

                Return Value:
                - Content if present
                - Null on failure

        GET http://127.0.0.1:8080/api/v1/data/controller/core/switch[name="spine0"]?select=connection
        GET http://127.0.0.1:8080/api/v1/data/controller/core/switch?select=connection
        '''
        t = test.Test()
        c = t.controller('master')
        if switch is not None:
            url = '/api/v1/data/controller/core/switch[name="%s"]?select=connection' % switch
            c.rest.get(url)
            data = c.rest.content()
            if len(data) == 0:
                return {}
            else:
                return data
        else:
            url = '/api/v1/data/controller/core/switch?select=connection'
            c.rest.get(url)
            data = c.rest.content()
            if len(data) == 0:
                return {}
            else:
                return data


    def cli_remove_node_standby(self):
        '''
        '''
        helpers.test_log("Entering ==> cli_remove_node_standby")
        t = test.Test()
        c = t.controller('master')
        bsn_common = bsnCommon()
        node = bsn_common.get_node_name('master')
        helpers.log("USER INFO: the master controller is:  %s" % node)

        num = self.rest_get_num_nodes(node)
        if num == 1:
            helpers.log("USER INFO:  There is only 1 node in cluster")
            return True

        else:
            url = '/api/v1/data/controller/core/high-availability/node'
            c.rest.get(url)
            content = c.rest.content()
            helpers.log("USER INFO: content is:  %s" % content)
            if content:
                for i in range (0, len(content)):
                    if  content[i]["role"] == 'standby':
                        standby = content[i]["hostname"]
                        helpers.log("USER INFO:  stande by controller is;  %s" % standby)
                        break


                cli = 'system remove-node ' + standby
                c.enable(cli, prompt='Conform remove-node \(\"y\" or \"yes\" to continue\):')
                c.enable('yes', timeout=60)
                helpers.sleep(60)

                num = self.rest_get_num_nodes(node)
                if num == 1:
                    helpers.log("USER INFO: standby node has been removed")
                    return True
                else:
                    return False
            return False


    def cli_detect_bonding_links(self):

        t = test.Test()
        master = t.controller("master")
        slave = t.controller("slave")

        try:
            master.cli("debug bash")
            master.send('ssh bsn@169.254.13.2')
            master.expect('password: ')
            master.send('bsn')
            master.send('sudo ethtool eth0')
            master.expect('Link detected: yes')
            master.send('sudo ethtool eth1')
            master.expect('Link detected: yes')
            master.send('exit')
            master.send('exit')

            slave.cli("debug bash")
            slave.send('ssh bsn@169.254.13.2')
            slave.expect('password: ')
            slave.send('bsn')
            slave.send('sudo ethtool eth0')
            slave.expect('Link detected: yes')
            slave.send('sudo ethtool eth1')
            slave.expect('Link detected: yes')
            slave.send('exit')
            slave.send('exit')

            return True

        except:
            helpers.test_failure("Error Detected during bond link detection.Looks like ")
            return False



    def cli_show_boot_partition(self, node='master'):
        '''
        '''
        helpers.test_log("Entering ==> cli_show_boot_partition")
        t = test.Test()
        c = t.controller(node)
        c.enable('show boot partition')
        content = c.cli_content()
        temp = helpers.strip_cli_output(content)
        temp = helpers.str_to_list(temp)
#        helpers.log("*****Output list   is :\n%s" % temp)
        assert(len(temp) == 4)
        temp.pop(0);temp.pop(0)
        partition = {}
        for line in temp:
            helpers.log("*****line is :\n%s" % line)

            if 'Pending Launch' in line:
                helpers.log(" there is Pending Launch")
                line = line.replace("Pending Launch", "Pending_Launch")
            if  'Active, Boot' in line:
                helpers.log(" there is Active, Boot")
                line = line.replace("Active, Boot", "Active_Boot")
            line = line.split()
            helpers.log("*****line is :\n%s" % line)
            partition[line[0]] = {}
            partition[line[0]]['image'] = line[-1]
            if (line[1] == 'Pending_Launch' or line[1] == 'Failed' or line[1] == 'completed' or
                line[1] == 'Unformatted'):
                partition[line[0]]['state'] = 'None'
                partition[line[0]]['upgrade'] = line[1]
            else:
                partition[line[0]]['state'] = line[1]
                partition[line[0]]['upgrade'] = line[2]

        return partition

    def get_boot_partition(self, node, flag):
        '''
        input:  flag type - Active,  Boot   Pending
        '''
        helpers.test_log("Entering ==> get_boot_partition")

        partition = self.cli_show_boot_partition(node)
        if flag == 'active':
            for key in partition:
                if 'Active' in partition[key]['state']:
                    return key
                    break
            return False
        if flag == 'Boot':
            for key in partition:
                if 'Boot' in partition[key]['state']:
                    return key
                    break
            return False
        if flag == 'Pending_launch':
            for key in partition:
                if 'Pending_Launch' in partition[key]['upgrade']:
                        return key
                        break
            helpers.log("There is no partition Pending Launch ")
            return -1
        if flag == 'Unformatted':
            for key in partition:
                if 'Unformatted' in partition[key]['upgrade']:
                    return key
                    break
            helpers.log("There is no partition unformated ")
            return -1

    def get_boot_partition_image(self, node, flag):
        '''
        input:  flag type - Active,  Boot   Pending
        in progress
        '''
        helpers.test_log("Entering ==> get_boot_partition")

        partition = self.cli_show_boot_partition(node)

        if flag == 'alternate':
            for key in partition:
                if 'Active' not in partition[key]['state']:
                    return partition[key]['image']
                    break
        if flag == 'active' or flag == 'current':
            for key in partition:
                if 'Active' in partition[key]['state']:
                    return partition[key]['image']
                    break


    def cli_verify_node_upgrade_partition(self, singleNode=False):

        ''' Reboot a node and verify the cluster leadership.
            Reboot Master in dual node setup: masterNode == True
        '''

        if(singleNode):
            partition = self.cli_show_boot_partition()
            for key in partition:
                if partition[key]['upgrade'] == ['complete' or 'Pending Launch']:
                    continue
                else:
                    return False
            return True
        else:
            partition1 = self.cli_show_boot_partition()
            partition2 = self.cli_show_boot_partition(node='slave')
            for key in partition1:
                if partition1[key]['state'] == 'Active_Boot':
                        active1 = key
                        break
            for key in partition2:
                if partition2[key]['state'] == 'Active_Boot':
                        active2 = key
                        break

            if active1 == active2:
                helpers.log("system at same partition: %s" % active1)
                return True
            else:
                helpers.log("system at differnet partition: %s  -  %s" % (active1, active2))
                return False


    def cli_verify_switch_configured(self, switch):
        '''
        '''
        helpers.test_log("Entering ==> cli_verify_switch_configured")
        t = test.Test()
        c = t.controller('master')
        c.enable("show switch %s" % switch)
        content = c.cli_content()
        temp = helpers.strip_cli_output(content)
        temp = helpers.str_to_list(temp)
        helpers.log("*****Output list   is :\n%s" % temp)
        for line in temp:
            helpers.log("*****line is :\n%s" % line)
            if 'None' in line:
                helpers.log(" The switch is not found in fabric:  %s" % switch)
                return False
            if switch in line:
                helpers.log(" The switch is found in fabric:  %s" % switch)
                return True
        helpers.test_failure('Error: can not decide the switch in fabric ')
        return False


    def verify_controller_reachable(self, node):
        '''
        '''
        helpers.test_log("Entering ==> verify_controller_reachable")
        t = test.Test()
        c = t.controller(node)
        ipAddr = c.ip()
        count = 0
        while (True):
            loss = helpers.ping(ipAddr)
            helpers.log("loss is: %s" % loss)
            if(loss != 0):
                if (count > 5):
                    helpers.warn("Cannot connect to the IP Address: %s - Tried for 5 Minutes" % ipAddr)
                    return False
                helpers.sleep(60)
                count += 1
                helpers.log("Trying to connect to the IP Address: %s - Try %s" % (ipAddr, count))
            else:
                helpers.log("Controller is alive")
                return True

    def verify_upgrade_not_progress(self):
        '''
        '''
        helpers.test_log("Entering ==> verify_upgrade_not_progress")
        t = test.Test()
        bsn_common = bsnCommon()
        nodes = bsn_common.get_all_controller_nodes()
        for node in nodes:
            c = t.controller(node)
            c.enable("show upgrade progress")
            content = c.cli_content()
            temp = helpers.strip_cli_output(content)
            temp = helpers.str_to_list(temp)
            line = temp[-1]
            helpers.log("USR INFO:  line is :'%s'" % line)
            if re.match(r'Error: Invalid Use: upgrade not active', line):
                helpers.log("USR INFO: no upgrade in node: %s" % node)
            else:
                helpers.log("USR INFO:  upgrade is in progress")
                return False

        for node in nodes:
            if self.cli_check_user_present(user='upgrader', node=node):
                helpers.log("USR INFO:  user upgrader still exist")
                return False
        return True

    def cli_check_user_present(self, user, node='master'):
        '''
        check user present
        '''

        t = test.Test()
        c = t.controller(node)
        url = "/api/v1/data/controller/core/aaa/local-user"

        c.rest.get(url)
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())
        content = c.rest.content()
        helpers.log("INFO: %s " % c.rest.content())

        Users = []
        for i in range (0, len(content)):
            Users.append(content[i]['user-name'])

        helpers.log("USR INFO: all the users are:  %s" % Users)
        if user not in Users:
            helpers.warn("User: %s NOT present" % user)
            return False
        else:
            helpers.log("USER %s is present " % user)
            return True

    def cli_get_debug_counter(self, pattern):
        '''
        get the debug counter
        '''

        t = test.Test()
        c = t.controller('master')
        string = 'show debug counters all | grep ' + pattern
        c.enable(string)
        content = c.cli_content()
        temp = helpers.strip_cli_output(content)
        helpers.log("USR INFO: line is:  %s" % temp)
        match = re.match(r'.* (\d+)', temp)
        counter = 0
        if match:
            counter = match.group(1)
        return counter

    def cli_config_tenant_vns_intf(self, tenant='T', segmant='V',
            ip=None, mask="24", switch=None,
            intf=None, vlan='untagged'
            ):
        '''
        Function to add configure tenant VNS and interface
        Input: tennat , switch , interface

        '''

        t = test.Test()
        c = t.controller('master')

        helpers.test_log("Entering ==> rest_add_tenant_vns_scale ")
        string = 'tenant ' + tenant
        c.config(string)
        string = 'segment ' + segmant
        c.config(string)
        if switch is not None and intf is not None:
            string = 'member switch ' + switch + ' interface ' + intf + ' vlan ' + vlan
            c.config(string)
        if ip is not None:
            c.config('logical-router')
            string = 'interface segment ' + segmant
            c.config(string)
            string = 'ip address ' + ip + '/' + mask
            c.config(string)

        c.cli('show running-config tenant')
        return True



    def cli_clear_icmpa(self, node):
        t = test.Test()
        s = t.switch(node)
        string = 'debug ofad "icmpa clear" '
        s.enable(string)

        return True

    def cli_clear_lacpa(self, node):
        t = test.Test()
        s = t.switch(node)
        string = 'debug ofad "lacpa clear" '
        s.enable(string)

        return True


    def cli_get_agent_counters(self, switch, pattern, node='master'):
        '''
        get the packet
        BCM_port, Q_type, Q_ID, GID, OutPkts, OutBytes, DroppedPkts, DroppedBytes, SharedCNT, MinCNTof_port=0

        '''

        t = test.Test()
        c = t.controller('master')
        string = 'show switch ' + switch + ' agent-counters  | grep ' + pattern
        c.enable(string)
        content = c.cli_content()
        temp = helpers.strip_cli_output(content)
        helpers.log("USR INFO: line is:  %s" % temp)
        match = re.match(r'.* (\d+)', temp)
        counter = 0
        if match:
            counter = match.group(1)
        return counter

    def cli_get_qos_weight(self, node, port='0'):
        t = test.Test()
        s = t.switch(node)
        string = 'debug ofad "qos_weight_info ' + port + '"'
        content = s.enable(string)['content']
        info = []
        temp = helpers.strip_cli_output(content, to_list=True)
        helpers.log("***temp is: %s  \n" % temp)

        for line in temp:
            helpers.log("***line is: %s  \n" % line)
            line = line.lstrip()
            match = re.match(r'queue=(\d+) ->.* weight=(\d+)', line)
            if match:
                helpers.log("INFO: queue is: %s,  weight is: %s" % (match.group(1), match.group(2)))
                info.append(match.group(2))

        helpers.log("***Exiting with info: %s  \n" % info)

        return info

    def cli_get_qos_port_stat(self, node, port='0'):
        '''
        get the packet
        BCM_port, Q_type, Q_ID, GID, OutPkts, OutBytes, DroppedPkts, DroppedBytes, SharedCNT, MinCNTof_port=0

        '''

        t = test.Test()
        s = t.switch(node)
        string = 'debug ofad "qos_port_stat ' + port + '"'
        content = s.enable(string)['content']
        info = {}
        temp = helpers.strip_cli_output(content, to_list=True)
        helpers.log("***temp is: %s  \n" % temp)

        for line in temp:
#            helpers.log("***line is: %s  \n" % line)
            line = line.lstrip()
            match = re.match(r'\d+, ([A-Z]+), (\d+), \d+, op:(\d+),', line)
            if match:
#                helpers.log("INFO: queue type is: %s, number is: %s, outPkts is: %s" %
#                    (match.group(1), match.group(2), match.group(3)))
                ID = match.group(1) + '_' + match.group(2)
                if match.group(3) == 0:
                    continue
                info[ID] = {}
                info[ID]['outPkts'] = match.group(3)

        helpers.log("***Exiting with info: %s  \n" % info)
        return info


    def cli_qos_clear_stat(self, node, port='0'):
        t = test.Test()
        s = t.switch(node)
        string = 'debug ofad "qos_clear_stat ' + port + '"'
        s.enable(string)

        return True

    def cli_clear_pimu_stat(self, node):
        t = test.Test()
        s = t.switch(node)
        string = 'debug ofad "clear-rx-pimu-stats" '
        s.enable(string)

        return True


    def cli_get_pimu_stat(self, node):
        '''
        get the packet
        # Name    Invoked    Drop  Forward     Fwd priority   Error
        '''

        t = test.Test()
        s = t.switch(node)
        string = 'debug ofad "rx-pimu-stats" '
        content = s.enable(string)['content']
        info = {}
        temp = helpers.strip_cli_output(content, to_list=True)
        temp = temp[1:]
        helpers.log("***temp is: %s  \n" % temp)
        for line in temp:
            helpers.log("***line is: %s  \n" % line)
            if 'nonfab pdu' in line:
                line = line.replace("nonfab pdu", "nonfab_pdu")
            elif 'L2 miss/move' in line:
                line = line.replace("L2 miss/move", "L2_miss_move")

            elif 'debug/acl' in line:
                line = line.replace("debug/acl", "debug_acl")

            elif 'L3 to cpu' in line:
                line = line.replace("L3 to cpu", "L3_to_cpu")

            elif 'L3 Miss/ttl' in line:
                line = line.replace("L3 Miss/ttl", "L3_Miss_ttl")

            elif 'unused 1' in line:
                line = line.replace("unused 1", "unused_1")

            elif 'unused 2' in line:
                line = line.replace("unused 2", "unused_2")

            line = line.lstrip()
            fields = line.split()
            info[fields[1]] = {}
            info[fields[1]]['name'] = fields[1]
            info[fields[1]]['invoked'] = fields[2]
            info[fields[1]]['drop'] = fields[3]
            info[fields[1]]['forward'] = fields[4]
            info[fields[1]]['priority'] = fields[5]
            info[fields[1]]['error'] = fields[6]
        helpers.log("***Exiting with info: %s  \n" % info)
        return info



    def get_queue_with_traffic(self, node, port, threshold):
        '''
        '''
        helpers.test_log("Entering ==> get_queue_with_traffic:  node - %s  port - %s  threshold - %d" % (node, port, int(threshold)))
        info = self.cli_get_qos_port_stat(node, port)
        traffic_queue = []
        for queue in info:
            helpers.test_log("INFO:  queue  - %s  outPkts - %s   " % (queue, info[queue]['outPkts']))
            if int(info[queue]['outPkts']) >= int(threshold):
                traffic_queue.append(queue)
        return traffic_queue


    def rest_clear_endpoints(self, **kwargs):

        '''
        This function will test the "clear endpoints" command.
        It will query for the learned endpoints and then issue the "clear endpoint" command.
        Then it will again query for the endpoints and verify endpoints infact got cleared.
        '''

        t = test.Test()
        master = t.controller("master")

        url = '/api/v1/data/controller/applications/bcf/info/endpoint-manager/clear'
        show_url = '/api/v1/data/controller/applications/bcf/info/endpoint-manager/endpoint'

        if(kwargs.get('mac')):
            url = url + '[mac="' + kwargs.get('mac') + '"]'
            show_url = show_url + '[mac="' + kwargs.get('mac') + '"]'
        if(kwargs.get('segment')):
            url = url + '[segment="' + kwargs.get('segment') + '"]'
            show_url = show_url + '[segment="' + kwargs.get('segment') + '"]'
        if(kwargs.get('tenant')):
            url = url + '[tenant="' + kwargs.get('tenant') + '"]'
            show_url = show_url + '[tenant="' + kwargs.get('tenant') + '"]'

        # Gather all the ip addresses to compare later
        ipAddrList_B4 = []
        show_result = master.rest.get(show_url)['content']
        try:
            for attachmentPoint in show_result:
                if 'ip-address' in attachmentPoint:
                    for ip in attachmentPoint['ip-address']:
                        ipAddrList_B4.append(ip['ip-address'])
                else:
                    pass
        except:
            helpers.log("There are no matching endpoints to clear. Returning False")
            return False

        helpers.log("Before ipAddrList is: %s" % ipAddrList_B4)

        # Clear the endpoints
        master.rest.get(url)
        if master.rest.status_code_ok():
            # Gather all the ip addresses to compare later
            ipAddrList_after = []
            show_result = master.rest.get(show_url)['content']
            try:
                for attachmentPoint in show_result:
                    if 'ip-address' in attachmentPoint:
                        for ip in attachmentPoint['ip-address']:
                            ipAddrList_after.append(ip['ip-address'])
                    else:
                        pass
            except:
                helpers.log("Looks like endpoints got cleared. Returning True")
                return True
        else:
                helpers.log("Something went wrong while clearning the endpoints. Returning False")
                return False

        helpers.log("After ipAddrList is: %s" % ipAddrList_after)

        if(len(ipAddrList_B4) > len(ipAddrList_after)):
            helpers.log("Some IP's got cleared from the list. Returning true")
            return True
        else:
            helpers.log("IP's didn't get cleared properly. Returning false")
            return False

    def rest_show_fabric_status(self):
        '''Return True is overall-status is OK
            Return False if overall-status is NOT OK

        '''
        t = test.Test()
        c = t.controller('master')
        url = '/api/v1/data/controller/applications/bcf/info/summary/fabric'
        c.rest.get(url)
        data = c.rest.content()
        if data[0]['overall-status'] == "NOT OK":
            helpers.log("ERROR:  fabric status is NOT OK  \n  %s" % data)
            c.enable("show fabric error")
            return False
        else:
            helpers.log("USR INFO:  fabric status is OK  \n  %s" % data)
            return True

