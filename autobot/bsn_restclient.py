from autobot.restclient import RestClient
import re
import helpers


class BsnRestClient(RestClient):
    """
    REST Client for Big Switch devices. 
    """
    def __init__(self, base_url=None, u=None, p=None,
                 content_type='application/json', host=None, platform=None):
        super(BsnRestClient, self).__init__(base_url, u, p, content_type)
        self.host = host
        self.platform = platform

    def format_url(self, url):
        """
        Special handling for Big Switch controllers.
        - For BVS (T5)
          - port 8080
          - http://host:8080/api/v1/auth/login
          - http://host:8080/api/v1/data/controller/applications/bvs/tenant[name="%s"]
        - For BigWire/BigTap
          - port 8082 for API URL
          - port 8000 for REST URL
          - http://host:8082/auth/login (works with both 8000 and 8082 ports)
          - http://host:8082/api/v1/data/controller/core/switch[dpid="%s"]
          - http://host:8000/rest/v1/model/snmp-server-config/

        """
        if re.match(r'^http://', url):
            # Full URL specified. Leave it as is
            return url
        
        if helpers.is_bvs(self.platform):
            if re.match(r'^/api/v1/', url):
                http_port = 8080
                return "http://%s:%s%s" % (self.host, http_port, url) 
            else:
                helpers.environment_failure("Platform=%s, unmatched URL=%s"
                                            % (self.platform, url))
        elif helpers.is_bigtap(self.platform) or helpers.is_bigwire(self.platform):
            if re.match(r'^(/api/v1/|/auth/login)', url):
                http_port = 8082
                return "http://%s:%s%s" % (self.host, http_port, url)
            elif re.match(r'^/rest/v1/', url):
                http_port = 8000
                return "http://%s:%s%s" % (self.host, http_port, url)
            else:
                helpers.environment_failure("Platform=%s, unmatched URL=%s"
                                            % (self.platform, url))
        else:
            helpers.environment_failure("Inconceivable!!! Platform=%s" %
                                        self.platform)
        
    def post(self, url, data=None, session=None, quiet=False):
        url = self.format_url(url)
        return super(BsnRestClient, self).post(url, data, session, quiet)

    def get(self, url, session=None, quiet=False):
        url = self.format_url(url)
        return super(BsnRestClient, self).get(url, session, quiet)

    def put(self, url, data=None, session=None, quiet=False):
        url = self.format_url(url)
        return super(BsnRestClient, self).put(url, data, session, quiet)

    def patch(self, url, data=None, session=None, quiet=False):
        url = self.format_url(url)
        return super(BsnRestClient, self).patch(url, data, session, quiet)

    def delete(self, url, data=None, session=None, quiet=False):
        url = self.format_url(url)
        return super(BsnRestClient, self).delete(url, data, session, quiet)
