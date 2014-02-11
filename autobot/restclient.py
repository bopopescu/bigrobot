import httplib2
import base64
import autobot.helpers as helpers
import autobot.utils as br_utils


class RestClient(object):
    """
    REST Client for talking to RESTful web services.
    """

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

        self.session_cookie_url = None
        self.session_cookie = None
        self.session_cookie_loop = 0
        self.last_result = None

        if u and p:
            self.authen_str = self.authen_encoding(u, p)
            self.default_header['authorization'] = 'Basic %s' % self.authen_str

    def authen_encoding(self, u, p):
        base64str = base64.encodestring('%s:%s' % (u, p))
        return base64str.replace('\n', '')

    def request_session_cookie(self, url=None):
        if url:
            self.session_cookie_url = url
        helpers.log("session_cookie_url: %s" % self.session_cookie_url)
        result = self.post(self.session_cookie_url,
                           {"user":"admin", "password":"adminadmin"})
        session_cookie = result['content']['session_cookie']
        self.set_session_cookie(session_cookie)
        return session_cookie

    def set_session_cookie(self, session):
        helpers.log("Saving session cookie %s" % session)
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

    def log_result(self, result=None, level=4):
        helpers.log("REST result:\n%s%s"
                    % (self.result_json(result),
                       br_utils.end_of_output_marker()),
                       level=level)

    def content(self, result=None):
        return self.result(result)['content']

    def content_json(self, result=None):
        return helpers.to_json(self.content(result))

    def log_content(self, result=None, level=4):
        helpers.log("REST content:\n%s%s"
                    % (self.content_json(result),
                       br_utils.end_of_output_marker()),
                       level=level)

    def _http_request(self, url, verb='GET', data=None, session=None,
                     quiet=False, save_last_result=True):
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

        helpers.log("RestClient: %s %s" % (verb, url), level=5)
        helpers.log("Headers = %s" % helpers.to_json(headers), level=5)
        if data:
            helpers.log("Data = %s" % helpers.to_json(data), level=5)

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

        if save_last_result:
            self.last_result = result

        if not quiet:
            self.log_result(result=result, level=6)

        result['success'] = False
        if code == '200':
            result['success'] = True
        else:
            helpers.test_error("REST call failed with status code %s" % code)

        return result

    def http_request(self, *args, **kwargs):
        result = self._http_request(*args, **kwargs)
        if int(result['status_code']) == 401 and result['status_descr'] == 'Unauthorized':
            if self.session_cookie_loop > 5:
                helpers.test_error("Detected session cookie loop.")
            else:
                self.session_cookie_loop += 1

            helpers.log("It appears the session cookie has expired. Requesting new session cookie.")
            self.request_session_cookie()

            # Re-run command
            result = self._http_request(*args, **kwargs)
        else:
            self.session_cookie_loop = 0
        return result

    def post(self, url, *args, **kwargs):
        return self.http_request(url, 'POST', *args, **kwargs)

    def get(self, url, *args, **kwargs):
        return self.http_request(url, 'GET', *args, **kwargs)

    def put(self, url, *args, **kwargs):
        return self.http_request(url, 'PUT', *args, **kwargs)

    def patch(self, url, *args, **kwargs):
        return self.http_request(url, 'PATCH', *args, **kwargs)

    def delete(self, url, *args, **kwargs):
        return self.http_request(url, 'DELETE', *args, **kwargs)
