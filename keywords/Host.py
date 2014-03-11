'''
###  WARNING !!!!!!!
###
###  This is where common code for Host will go in.
###
###  To commit new code, please contact the Library Owner:
###  Vui Le (vui.le@bigswitch.com)
###
###  DO NOT COMMIT CODE WITHOUT APPROVAL FROM LIBRARY OWNER
###
###  Last Updated: 03/11/2014
###
###  WARNING !!!!!!!
'''

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

        See also Controller.cli ping.
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
        status = helpers._ping(dest, node_handle=n, mode='bash',
                               *args, **kwargs)
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

    def bash_delete_tag(self, node, intf, soft_error=False):
        """
        Function to remove the vlan tag from the host eth interfaces.
        """
        t = test.Test()
        n = t.node(node)

        try:
            n.sudo("vconfig rem %s" % intf)
        except:
            output = helpers.exception_info_value()
            helpers.log("Output: %s" % output)

            # Catch error:
            #   ERROR: trying to remove VLAN -:eth1.20:- error: No such device
            if helpers.any_match(str(output), r'error: No such devices'):
                helpers.test_error("vconfig rem error - no such device '%s'" % intf,
                                   soft_error)
                return False
            else:
                helpers.test_error('Uncaught exception:\n%s' %
                                   helpers.exception_info(),
                                   soft_error)
                return False

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

    def bash_get_interface_ipv4(self, node, intf):
        t = test.Test()
        n = t.node(node)
        output = n.sudo("ifconfig %s | grep --color=never -i 'inet addr'" % intf)['content']
        return_stat = n.sudo('echo $?')['content']
        return_stat = helpers.strip_cli_output(return_stat)
        helpers.log("output: %s" % output)
        helpers.log("return_stat: %s" % return_stat)
        if int(return_stat) == 1:
            return ''
        else:
            result = re.search('inet addr:(.*)\sBcast', output)
            return result.group(1)


    def bash_release_dhcpv4_address(self, node, intf):

        t = test.Test()
        n = t.node(node)
        n.sudo("dhclient -r %s" % intf)
        return True
        n.sudo("ifconfig %s | grep --color=never -i 'inet addr'" % intf)['content']
        return_stat = n.sudo('echo $?')['content']
        return_stat = helpers.strip_cli_output(return_stat)
        helpers.log("return_stat: %s" % return_stat)
        if int(return_stat) == 1:
            return True
        else:
            return False

    def bash_renew_dhcpv4_address(self, node, intf):
        '''
             attempt to obtain an IPv4 address via dhcp. timeout is set to 10 seconds in /etc/dhcp/dhclient.conf file for ubuntu host
        '''
        t = test.Test()
        n = t.node(node)
        n.sudo("dhclient -v -4 %s" % intf)
        output = n.sudo("ifconfig %s | grep --color=never -i 'inet addr'" % intf)['content']
        return_stat = n.sudo('echo $?')['content']
        return_stat = helpers.strip_cli_output(return_stat)
        helpers.log("return_stat: %s" % return_stat)
        if int(return_stat) == 1:
            return ''
        else:
            result = re.search('inet addr:(.*)\sBcast', output)
            return result.group(1)

    def bash_add_route(self, node, cidr, gw):
        t = test.Test()
        n = t.node(node)
        n.sudo("route add -net %s gw %s" % (cidr, gw))
        return True

    def bash_delete_route(self, node, cidr, gw):
        t = test.Test()
        n = t.node(node)
        n.sudo("route del -net %s gw %s" % (cidr, gw))
        return True

    def bash_set_mac_address(self, node, intf, mac):
        '''
            change mac address of a host interface
        '''
        t = test.Test()
        n = t.node(node)
        n.sudo("ifconfig %s hw ether %s" % (intf, mac))
        return True

    def bash_get_intf_mac(self, node, intf):
        '''
            return mac address of a host interface
        '''
        t = test.Test()
        n = t.node(node)
        output = n.sudo("ifconfig %s | grep --color=never HWaddr" % (intf))['content']
        return_stat = n.sudo('echo $?')['content']
        return_stat = helpers.strip_cli_output(return_stat)
        helpers.log("return_stat: %s" % return_stat)
        if int(return_stat) == 1:
            helpers.log("I am here")
            return ''
        else:
            helpers.log("I am there")
            helpers.log("output: %s" % output)
            output = helpers.strip_cli_output(output)
            result = re.search('HWaddr (.*)', output)
            mac_addr = result.group(1)
            helpers.log("output: %s" % output)
            helpers.log("result: %s" % result)
            # mac = mac_addr.replace("\r", "")
            mac = mac_addr.strip(' \t\n\r')
            helpers.log("mac_addr: %s" % mac_addr)
            return mac


    def bash_verify_arp(self, node, ip):
        t = test.Test()
        n = t.node(node)
        result = n.sudo("arp -n %s" % ip)
        output = result["content"]
        helpers.log("output: %s" % output)
        match = re.search(r'no entry|incomplete', output, re.S | re.I)
        if match:
            return False
        else:
            return True


    def bash_ifup_intf(self, node, intf):
        t = test.Test()
        n = t.node(node)
        n.sudo("ifconfig %s up" % intf)
        return True

    def bash_ifdown_intf(self, node, intf):
        t = test.Test()
        n = t.node(node)
        n.sudo("ifconfig %s down" % intf)
        return True

    def bash_init_intf(self, node, intf):
        t = test.Test()
        n = t.node(node)
        n.sudo("ifconfig %s 0.0.0.0" % intf)
        return True


    def bash_check_service_status(self, node, processname):
        t = test.Test()
        n = t.node(node)
        output = n.sudo("service %s status" % processname)['content']
        helpers.log("output: %s" % output)
        match = re.search(r'unrecognized service', output, re.S | re.I)
        if match:
            return 'unrecognized service'
        match = re.search(r'is not running', output, re.S | re.I)
        if match:
            return 'is not running'
        match = re.search(r'start\/running', output, re.S | re.I)
        if match:
            return 'is started'




