import autobot.helpers as helpers
import autobot.test as test
import ipcalc


class BsnCommon(object):

    def __init__(self):
        pass
        
    def base_suite_setup(self):
        test.Test().topology()

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

    def mock_passed(self):
        #helpers.sleep(2)
        print("MOCK PASSED")
        return True

    def mock_failed(self):
        raise AssertionError("MOCK FAILED")

    def manual_passed(self):
        print("MANUAL PASSED")
        return 8888

    def manual_failed(self):
        raise AssertionError("MANUAL FAILED")

    def show_test_topology_params(self):
        t = test.Test()
        helpers.log("Test topology params: %s" % helpers.prettify(t.topology_params()))

    def host_ping(self, node, dest_ip=None, dest_node=None, *args, **kwargs):
        t = test.Test()
        n = t.node(node)
        
        if not dest_ip and not dest_node:
            helpers.test_error("Must specify 'dest_ip' or 'dest_node'")
        if dest_ip and dest_node:
            helpers.test_error("Specify 'dest_ip' or 'dest_node' but not both")
        if dest_ip:
            dest = dest_ip
        if dest_node:
            dest = t.node(dest_node).ip
        status = helpers._ping(dest, node=n, *args, **kwargs)
        return status
        
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
            byte_list[byte-1] = byte_list[3]
            new_subnet_list.append('.'.join(byte_list))
            
        return new_subnet_list

