import autobot.helpers as helpers
import autobot.test as test


class Host(object):

    def __init__(self):
        pass
        
    def host_ping(self, node, dest_ip=None, dest_node=None, *args, **kwargs):
        """
        :param node: The device name as defined in the topology file, e.g., 'c1', 's1', etc.
        :param dest_ip: Ping this destination IP address
        :param dest_node Ping this destination node ('c1', 's1', etc)
        :param source_if: Source interface
        :param count: Number of ping packets to send  
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
            dest = t.node(dest_node).ip
        status = helpers._ping(dest, node=n, *args, **kwargs)
        return status
