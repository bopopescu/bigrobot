class Node(object):
    def __init__(self, ip):
        self.ip = ip
        self.http_port = None
        self.base_url = None
        self.rest = None  # REST handle
        
    def platform(self):
        return self.dev.platform()


class ControllerNode(Node):
    def __init__(self, ip):
        super(ControllerNode, self).__init__(ip) 

    def is_bvs(self):
        return self.platform() == 'bvs'

    def is_bigtap(self):
        return self.platform() == 'bigtap'

    def is_bigwire(self):
        return self._platform() == 'bigwire'
    

class MininetNode(Node):
    def __init__(self, ip):
        super(MininetNode, self).__init__(ip) 

    def is_mininet(self):
        return self._platform() == 'mininet'
