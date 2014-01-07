import httplib2
import base64
import autobot.helpers as helpers


class RestClient(object):
    '''
    REST Client for talking to RESTful web services
    '''

    # Number of seconds to wait before timing out the REST call.
    default_timeout = 45

    http_codes = {
        '200': 'OK',
        '401': 'Unauthorized',
        '500': 'Internal Server Error',
        'unknown': 'Unknown error (unexpected HTTP status code)'
    }

    def __init__(self, base_url=None, u=None, p=None,
                 content_type='application/json'):
        self.http = httplib2.Http(timeout=RestClient.default_timeout)

        self.base_url = base_url
            
        # Be sure to keep all header keys as lower case.        
        self.default_header = {}
        self.default_header['content-type'] = content_type
        
        self.session_cookie = None
        self.last_result = None
        
        if u and p:
            self.authen_str = self.authen_encoding(u, p)
            self.default_header['authorization'] = 'Basic %s' % self.authen_str

    def authen_encoding(self, u, p):
        base64str = base64.encodestring('%s:%s' % (u, p))
        return base64str.replace('\n', '')

    def set_session_cookie(self, session):
        self.session_cookie = session

    def status_code(self, result=None):
        if not result:
            result = self.last_result
        return int(result['status_code'])

    def status_code_ok(self, result=None):
        code = self.status_code(result)
        if code == 200:
            return True
        else:
            return False

    # Alias
    status_code_200 = status_code_ok

    def status_descr(self, result=None):
        if not result:
            result = self.last_result
        return result['status_descr']

    def error(self, result=None):
        if not result:
            result = self.last_result
        code = self.status_code(result)
        descr = self.status_descr(result)
        return "HTTP status code %d: %s" % (code, descr)

    def result(self, result=None):
        if not result:
            result = self.last_result
        return result

    def result_json(self, result=None):
        return helpers.to_json(self.result(result))

    def content(self, result=None):
        return self.result(result)['content']

    def content_json(self, result=None):
        return helpers.to_json(self.content(result))

    def http_request(self, url, verb='GET', data=None, session=None):
        """
        Generic HTTP request for POST, GET, PUT, DELETE, etc.
        data is a Python dictionary.
        """
        if url is None:
            url = self.base_url
            if url is None:
                helpers.environment_failure("Problem locating base URL.")
        
        headers = self.default_header

        if session:
            headers['Cookie'] = 'session_cookie=%s' % session
        elif self.session_cookie:
            headers['Cookie'] = 'session_cookie=%s' % self.session_cookie

        helpers.analyze("RestClient: %s %s" % (verb, url))
        helpers.analyze("Headers = %s" % helpers.to_json(headers))
        if data:
            helpers.analyze("Data = %s" % helpers.to_json(data))

        resp, content = self.http.request(url,
                                          verb,
                                          body=helpers.to_json(data),
                                          headers=headers
                                          )
        code = resp['status']

        if content:
            python_content = helpers.from_json(content)
        else:
            python_content = {}

        result = {'content': python_content}
        result['http_verb'] = verb
        result['status_code'] = code
        result['request_url'] = url
        if code in RestClient.http_codes:
            result['status_descr'] = RestClient.http_codes[code]
        else:
            result['status_descr'] = RestClient.http_codes['unknown']

        result['success'] = False
        if code == '200':
            result['success'] = True

        self.last_result = result

        return result

    def post(self, url, data=None, session=None):
        return self.http_request(url, 'POST', data, session)

    def get(self, url, session=None):
        return self.http_request(url, 'GET', session=session)

    def put(self, url, data=None, session=None):
        return self.http_request(url, 'PUT', data, session)

    def patch(self, url, data=None, session=None):
        return self.http_request(url, 'PATCH', data, session)

    def delete(self, url, data=None, session=None):
        return self.http_request(url, 'DELETE', data, session)
