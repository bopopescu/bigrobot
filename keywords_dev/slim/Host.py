import autobot.helpers as helpers
import autobot.test as test
import re


class Host(object):

    def bash_verify_arp(self, node, hostip):
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

        result=n.sudo("arp -n %s" % hostip)
        out = result["content"]
        return out
