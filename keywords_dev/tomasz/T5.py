import autobot.helpers as helpers
import autobot.test as test
import json



class T5(object):

    def cli_configure_virtual_ip(self, vip):
        ''' Function to show Virtual IP of a controller via CLI
        Input: None
        Output: VIP address if configured, None otherwise
        '''
        t = test.Test()
        c = t.controller('master')

        helpers.test_log("Input arguments: virtual IP = %s" % vip)
        try:
            c.config("cluster")
            c.config("virtual-ip %s" % vip)
            assert "Error" not in c.cli_content()
        except:
            helpers.test_log(c.cli_content())
            return False
        else:
            return True


    def cli_verify_virtual_ip(self, vip):
        ''' Function to verify that Virtual IP address
        points to some controller via CLI
        Input: VIP address
        Output: Eth0 IP address of the controller that Virtual IP points to
        '''
        t = test.Test()
        try:
            if 'master' in vip:
                c = t.controller('master')
            else:
                c = t.node_spawn(ip=vip)
            content = c.cli('show local node interfaces ethernet0')['content']
            output = helpers.strip_cli_output(content)
            lines = helpers.str_to_list(output)
            assert "Network-interfaceses" in lines[0]
            #  -- should be changed to "interfaces" when BSC-4810 fixed
            rows = lines[3].split(' ')
        except:
            helpers.test_log(c.cli_content())
            return None
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
            content = c.cli('show virtual-ip')['content']
            output = helpers.strip_cli_output(content)
            lines = helpers.str_to_list(output)
            #assert(len(lines) == 3)   -  while writing the output is broken,
            #eventually line should be uncommented
            assert "ipv4 address" in lines[0]
        except:
            helpers.test_log(c.cli_content())
            return None
        else:
            return lines[2].strip()


    def cli_delete_virtual_ip(self):
        ''' Function to delete Virtual IP from a controller via CLI
        Input: None
        Output: True if successful, False otherwise
        '''
        t = test.Test()
        c = t.controller('master')

        helpers.test_log("Deleting virtual IP address")
        try:
            c.config("cluster")
            c.config("no virtual-ip")
        except:
            helpers.test_log(c.cli_content())
            return False
        else:
            return True


    def cli_cluster_take_leader(self):
        ''' Function to trigger failover to slave controller via CLI
        Input: None
        Output: True if successful, False otherwise
        '''
        t = test.Test()
        c = t.controller('slave')

        helpers.log("Failover")
        try:
            c.config("config")
            c.send("reauth")
            c.expect(r"Password:")
            c.config("adminadmin")
            c.send("cluster election take-leader")
            c.expect(r"Election may cause role transition: enter \"yes\" \(or \"y\"\) to continue:")
            c.config("yes")
        except:
            helpers.test_log(c.cli_content())
            return False
        else:
            return True


    def rest_configure_virtual_ip(self, vip):
        ''' Function to configure Virtual IP of the cluster via REST
        Input: VIP address
        Output: True if successful, False otherwise
        '''
        t = test.Test()
        c = t.controller('master')

        helpers.log("Input arguments: virtual IP = %s" % vip)
        try:
            url = '/api/v1/data/controller/os/config/global/virtual-ip-config'
            c.rest.post(url, {"ipv4-address": vip})
        except:
            return False
        else:
            return True


    def rest_verify_virtual_ip(self, vip):
        ''' Function to verify that Virtual IP address
        points to some controller via REST
        Input: VIP address
        Output: Mac address of the controller that Virtual IP points to
        '''
        t = test.Test()
        try:
            if 'master' in vip:
                c = t.controller('master')
            else:
                c = t.node_spawn(ip=vip)

            helpers.log("Getting MAC address of the controller")
            url = '/api/v1/data/controller/os/action/network-interfaces'
            c.rest.get(url)
            content = c.rest.content()
        except:
            helpers.test_log(c.rest.error())
            return False
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
            url = '/api/v1/data/controller/os/config/global/virtual-ip-config'
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


    def rest_delete_virtual_ip(self):
        ''' Function to delete Virtual IP from a controller via REST
        Input: None
        Output: True if successful, False otherwise
        '''
        t = test.Test()
        c = t.controller('master')

        helpers.log("Deleting virtual IP address")
        try:
            url = '/api/v1/data/controller/os/config/global/virtual-ip-config'
            c.rest.delete(url)
        except:
            return False
        else:
            return True


    def rest_cluster_take_leader(self):
        ''' Function to trigger failover to slave controller via REST
        Input: None
        Output: True if successful, False otherwise
        '''
        t = test.Test()
        c = t.controller('slave')

        helpers.log("Failover")
        try:
            url = '/api/v1/data/controller/cluster/config/new-election'
            c.rest.post(url, {"rigged": str('true')})
        except:
            helpers.test_failure(c.rest.error())
            return False
        else:
            return True
