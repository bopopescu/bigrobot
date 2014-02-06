''' 
###  WARNING !!!!!!!
###  
###  This is where common code for all Controller Platforms will go in.
###  
###  To commit new code, please contact the Library Owner: 
###  Vui Le (vui.le@bigswitch.com)
###
###  DO NOT COMMIT CODE WITHOUT APPROVAL FROM LIBRARY OWNER
###
###  Last Updated: 02/05/2014
###
###  WARNING !!!!!!!
'''

import autobot.helpers as helpers
import autobot.test as test
import ipcalc
import Controller


class BsnCommon(object):

    def __init__(self):
        pass

    def base_suite_setup(self):
        test.Test().topology()
        obj = Controller.Controller()
        obj.cli_save_running_config()

    def base_suite_teardown(self):
        t = test.Test()
        for n in t.topology():
            node = t.node(n)
            if helpers.is_controller(n) or helpers.is_mininet(n):
                helpers.log("Closing device connection for node '%s'" % n)
                node.dev.close()

    def base_test_setup(self):
        test.Test()

    def base_test_teardown(self):
        pass

    def mock_untested(self):
        print("MOCK UNTESTED")

    def mock_passed(self):
        print("MOCK PASSED")

    def mock_failed(self):
        raise AssertionError("MOCK FAILED")

    def manual_untested(self):
        print("MANUAL UNTESTED")

    def manual_passed(self):
        print("MANUAL PASSED")

    def manual_failed(self):
        raise AssertionError("MANUAL FAILED")

    def show_test_topology_params(self):
        t = test.Test()
        helpers.log("Test topology params: %s" % helpers.prettify(t.topology_params()))

    def expr(self, s):
        result = eval(s)
        helpers.log("Express '%s' evaluated to '%s'" % (s, result))
        return result

    def ip_range(self, subnet, first=None, last=None):
        """
        :param subnet: (str) The IP subnet, e.g., '192.168.1.1/24'
        :param first:  (str) [Optional] The first IP address in range
        :param last:   (str) [Optional] The last IP address in range
        """
        subnet_list = [str(ip) for ip in ipcalc.Network(subnet)]

        first_index, last_index = None, None
        if first:
            first_index = subnet_list.index(first)
        if last:
            last_index = subnet_list.index(last) + 1

        if first_index is None and last_index is None:
            return subnet_list
        if last_index is None:
            return subnet_list[first_index:]

        return subnet_list[first_index:last_index]

    def ip_range_byte_mod(self, subnet, first=None, last=None, byte=None):
        """
        :param byte: (str) [Optional] The byte field in the IP address to
                modify in addition to the 4th bite field.
        
        IP address anatomy:
          <byte1>.<byte2>.<byte3>.<byte4>
        
        This is intended for testing TCAM optimization (per MingTao). In
        addition to changing the host byte (4th byte) of the IP address, we
        want to change a network byte as well, such as the 2nd or 3rd byte of
        the IP address.
        """
        subnet_list = self.ip_range(subnet, first, last)

        # Convert byte value to integer
        if byte:
            byte = int(byte)

        if byte in (None, 4):
            return subnet_list

        if byte not in (1, 2, 3):
            helpers.test_error("Error: Can only modify 1st, 2nd, or 3rd byte in IP address.")

        new_subnet_list = []
        for ip in subnet_list:
            byte_list = ip.split('.')
            byte_list[byte - 1] = byte_list[3]
            new_subnet_list.append('.'.join(byte_list))

        return new_subnet_list

    def get_next_mac(self, base, incr):
        """
        Contributor: Mingtao Yang 
        Objective: 
        - Generate the next mac/physical address based on the base and step.
            
        Inputs:
          | base | starting mac address |
          | incr | Value by which we will increment the mac/physical address |
            
        Usage:  
          | macAddr = self.get_next_mac(base,incr) |     
        """

        helpers.log("the base address is: %s,  the step is: %s,  " % (str(base), str(incr)))

        mac = base.split(":")
        step = incr.split(":")
        helpers.log("MAC list is %s" % mac)

        hexmac = []

        for index in range(5, 0, -1):
            mac[index] = int(mac[index], 16) + int(step[index], 16)
            mac[index] = hex(mac[index])
            temp = mac[index]
            if int(temp, 16) >= 256:
                mac[index] = hex(0)
                mac[index - 1] = int(mac[index - 1], 16) + 1
                mac[index - 1] = hex(mac[index - 1])

        mac[0] = int(mac[0], 16) + int(step[0], 16)
        mac[0] = hex(mac[0])

        temp = mac[0]
        if int(temp, 16) >= 256:
            mac[0] = hex(0)

        for i in range(0, 6):
            hexmac.append('{0:02x}'.format(int(mac[i], 16)))
        macAddr = ':'.join(map(str, hexmac))

        return macAddr

    def get_next_address(self, addr_type, base, incr):
        """ 
        Contributor: Mingtao Yang
        Objective:
        Generate the next address bases on the base and step.
        
        Input:
        | addr_type | IPv4/IpV6|
        | base | Starting IP address |
        | incr | Value by which we will increment the IP address|

        Usage:    ipAddr = self.get_next_address(ipv4,'10.0.0.0','0.0.0.1')
                  ipAddr = self.get_next_address(ipv6,'f001:100:0:0:0:0:0:0','0:0:0:0:0:0:0:1:0')
        """

        helpers.log("the base address is: %s,  the step is: %s,  " % (str(base), str(incr)))
        if addr_type == 'ipv4' or addr_type == 'ip':
            ip = list(map(int, base.split(".")))
            step = list(map(int, incr.split(".")))
            ip_address = []
            for i in range(3, 0, -1):
                ip[i] += step[i]
                if ip[i] >= 256:
                    ip[i] = 0
                    ip[i - 1] += 1
            ip[0] += step[0]
            if ip[0] >= 256:
                ip[0] = 0

            ip_address = '.'.join(map(str, ip))

        if addr_type == 'ipv6'  or addr_type == 'ip6':
            ip = base.split(":")
            step = incr.split(":")
            helpers.log("IP list is %s" % ip)

            ip_address = []
            hexip = []

            for i in range(0, 7):
                index = 7 - int(i)
                ip[index] = int(ip[index], 16) + int(step[index], 16)
                ip[index] = hex(ip[index])
                temp = ip[index]
                if int(temp, 16) >= 65536:
                    ip[index] = hex(0)
                    ip[index - 1] = int(ip[index - 1], 16) + 1
                    ip[index - 1] = hex(ip[index - 1])


            ip[0] = int(ip[0], 16) + int(step[0], 16)
            ip[0] = hex(ip[0])
            temp = ip[0]
            if int(temp, 16) >= 65536:
                ip[0] = hex(0)

            for i in range(0, 8):
                hexip.append('{0:x}'.format(int(ip[i], 16)))

            ip_address = ':'.join(map(str, hexip))

        return ip_address