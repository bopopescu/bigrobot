import autobot.helpers as helpers
import autobot.test as test
import re


class Host(object):

    def bash_ping(self, node, dest_ip=None, dest_node=None, *args, **kwargs):
        """
        Perform a ping from the shell. Returns the loss percentage
        - 0   - 0% loss
        - 100 - 100% loss
        
        Inputs:
        - node:      The device name as defined in the topology file, e.g., 'c1', 's1', etc.
        - dest_ip:   Ping this destination IP address
        - dest_node  Ping this destination node ('c1', 's1', etc)
        - source_if: Source interface
        - count:     Number of ping packets to send
        
        Example:
        | ${lossA} = | Bash Ping | h1          | 10.192.104.1 | source_if=eth1 |
        | ${lossB} = | Bash Ping | node=master | dest_node=s1 |                |
        =>
        - ${lossA} = 0
        - ${lossB} = 100
        """
        t = test.Test()
        n = t.node(node)

        if not dest_ip and not dest_node:
            helpers.test_error("Must specify 'dest_ip' or 'dest_node'")
        if dest_ip and dest_node:
            helpers.test_error("Specify 'dest_ip' or 'dest_node' but not both")
        if dest_ip:
            dest = dest_ip
        if dest_node:
            dest = t.node(dest_node).ip()
        status = helpers._ping(dest, node=n, *args, **kwargs)
        return status

    def bash_add_tag(self, node, intf, vlan):
        """
        Add vlan tag to a Host eth interfaces.
        """
        t = test.Test()
        n = t.node(node)
        n.sudo("vconfig add %s %s" % (intf, vlan))
        return True

    def bash_add_ip_address(self, node, ipaddr, intf):
        """
        Adding IP address to Host interface,For tagged interface user needs
        to specify interface.tagnumber (e.g eth1.10).
        """
        t = test.Test()
        n = t.node(node)
        n.sudo("ip addr add %s dev %s" % (ipaddr, intf))
        return True

    def bash_delete_ip_address(self, node, ipaddr, intf):
        """
        Removing IP address from the host interface.
        """
        t = test.Test()
        n = t.node(node)
        n.sudo("ip addr del %s dev %s" % (ipaddr, intf))
        return True

    def bash_delete_tag(self, node, intf):
        """
        Function to remove the vlan tag from the host eth interfaces.
        """
        t = test.Test()
        n = t.node(node)
        result = n.sudo("vconfig rem %s" % intf)
        out = result["content"]

        # Catch error:
        #   ERROR: trying to remove VLAN -:eth1.20:- error: No such device
        #
        # Actually, Exscript will detect this error and handle it, so we
        # should never reach here... Exscript/protocols/Protocol.py will raise
        # InvalidCommandException('Device said:\n' + self.response)
        if re.search(r'no such device', out, re.M | re.I):
            helpers.test_error("vconfig error - no such device '%s'" % intf)

        return True

    def bash_network_restart(self, node):
        """
        Function to restart the networking services for Ubuntu 12.04.
        """
        t = test.Test()
        n = t.node(node)
        n.sudo("/etc/init.d/networking restart")
        n.bash("route")
        return True
