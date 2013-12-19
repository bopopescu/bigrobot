class Node(object):
    def __init__(self, ip):
        self.ip = ip
        self.http_port = None
        self.base_url = None
        self.rest = None  # REST handle