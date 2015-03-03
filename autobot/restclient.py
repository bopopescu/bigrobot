import httplib2
import base64
import autobot.helpers as helpers
import autobot.utils as br_utils
import re


class RestClient(object):
    """
    REST Client for talking to RESTful web services.
    """

    # Number of seconds to wait before timing out the REST call.
    default_timeout = 45

    http_codes = {
        '200': 'OK',  # 200 through 300 are success (BSN-specific)
        '401': 'Unauthorized',
        '409': 'List element already exists',  # (BSN-specific)
        '500': 'Internal Server Error',
        'unknown': 'Unknown error (unexpected HTTP status code)'
    }

    # FIXME!!! base_url has become sort of useless since the base URL is
    # derived from IP and http_port (if specified). Consider removing base_url
    # at some point... Will also touch the following files: node.py and
    # bsn_restclient.py. Also check user's topo file for base_url (legacy
    # feature).
    def __init__(self, base_url=None, user=None, password=None,
                 content_type='application/json', name=None):
        self.http = httplib2.Http(".cache", disable_ssl_certificate_validation=True, timeout=RestClient.default_timeout)

        self._name = name
        self.base_url = base_url

        # Be sure to keep all header keys as lower case.
        self.default_header = {}
        self.default_header['content-type'] = content_type

        self.session_cookie_url = None
        self.session_cookie = None
        self.session_cookie_loop = 0
        self.last_result = None
        self.user = user
        self.password = password

    def name(self):
        return self._name

    def authen_encoding(self, user=None, password=None):
        if not user:
            user = self.user
        if not password:
            password = self.password

        base64str = base64.encodestring('%s:%s' % (user, password))
        self.default_header['authorization'] = ('Basic %s'
                                                % base64str.replace('\n', ''))
        return self.default_header['authorization']

    def request_session_cookie(self, url=None):
        if url:
            self.session_cookie_url = url
        helpers.log("session_cookie_url: '%s'" % self.session_cookie_url)
        authen = {"user":self.user, "password":self.password}
        helpers.debug("session cookie authen info: '%s'" % authen)
        result = self.post(self.session_cookie_url, authen)
        session_cookie = result['content']['session_cookie']
        self.set_session_cookie(session_cookie)
        return session_cookie

    def delete_session_cookie(self, url=None):
        result = self.delete(url)
        helpers.log("Removing session cookie '%s'" % self.session_cookie)
        self.session_cookie = None
        return result

    def set_session_cookie(self, session, quiet=False):
        if not quiet:
            helpers.log("Saving session cookie '%s'" % session)
        self.session_cookie = session
        return self.session_cookie

    def get_session_cookie(self):
        return self.session_cookie

    def status_code(self, result=None):
        if not result:
            result = self.last_result
        return int(result['status_code'])

    def status_code_ok(self, result=None):
        code = self.status_code(result)
        if code in range(200, 300):
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

    def log_result(self, result=None, level=4, log_level="info"):
        helpers.log("'%s' REST result:\n%s%s"
                    % (self._name, self.result_json(result),
                       br_utils.end_of_output_marker()),
                       level=level, log_level=log_level)

    def content(self, result=None):
        return self.result(result)['content']

    def content_json(self, result=None):
        return helpers.to_json(self.content(result))

    def log_content(self, result=None, level=4):
        helpers.log("'%s' REST content:\n%s%s"
                    % (self._name, self.content_json(result),
                       br_utils.end_of_output_marker()),
                       level=level)

    def _http_request(self, url, verb='GET', data=None, session=None,
                     quiet=0, save_last_result=True, log_level='info'):
        """
        Generic HTTP request for POST, GET, PUT, DELETE, etc.
        data is a Python dictionary.
        """
        
        #helpers.log("url: '%s'" % url)
        #helpers.log("verb: '%s'" % verb)
        #helpers.log("data: '%s'" % data)
        
        if url is None:
            url = self.base_url
            if url is None:
                helpers.environment_failure("Problem locating base URL.")

        headers = self.default_header

        if session:
            headers['Cookie'] = 'session_cookie=%s' % session
        elif self.session_cookie:
            headers['Cookie'] = 'session_cookie=%s' % self.session_cookie

        if helpers.not_quiet(quiet, [2, 5]):
            helpers.log("'%s' RestClient: %s %s" % (self._name, verb, url),
                        level=5, log_level=log_level)
            helpers.log("'%s' Headers = %s"
                        % (self._name, helpers.to_json(headers)),
                        level=5, log_level=log_level)
            if data:
                helpers.log("'%s' Data = %s"
                            % (self._name, helpers.to_json(data)),
                            level=5, log_level=log_level)

        prefix_str = '%s %s' % (self.name(), verb.lower())
        data_str = ''
        if data:
            data_str = ' %s' % helpers.to_json(data, is_raw=True)
            if len(data_str) > 50:
                # If data is more than 50 chars long, then prettify JSON
                data_str = ' %s' % helpers.to_json(data)
        #helpers.bigrobot_devcmd_write("%-9s: %s%s\n"
        #                              % (prefix_str, url, data_str))
        if helpers.is_dict(data) or helpers.is_list(data):
            formatted_data = helpers.to_json(data)
        else:
            formatted_data = data

        resp, content = self.http.request(url,
                                          verb,
                                          body=formatted_data,
                                          headers=headers
                                          )
        code = resp['status']

        if content:
            python_content = helpers.from_json(content)
        else:
            python_content = {}

        result = {'content': python_content}
        result['http_verb'] = verb
        result['http_data'] = formatted_data
        result['status_code'] = int(code)
        result['request_url'] = url

        if save_last_result:
            self.last_result = result

        if helpers.not_quiet(quiet, [1, 5]):
            self.log_result(result=result, level=6, log_level=log_level)

        # ATTENTION: RESTclient will generate an exception when the
        # HTTP status code is anything other than:
        #   - 200-300
        #     - 200 (OK)
        #     - 201 (Created)
        #     - 202 (Accepted)
        #   - 401 (Authen/session cookie issue)
        #   - 409 (List element already exists)
        #
        # Reference:
        # http://www.iana.org/assignments/http-status-codes/http-status-codes.xhtml
        if code in RestClient.http_codes:
            result['status_descr'] = RestClient.http_codes[code]
        elif int(code) in range(200, 300):  # Success (BSN-specific)
            result['status_descr'] = RestClient.http_codes['200']
        else:
            result['status_descr'] = RestClient.http_codes['unknown']

        result['success'] = False

        # As per https://github.com/bigswitch/floodlight/commit/a432f1b501640474b8bf6cb87a07dcbf28df8691
        if int(code) in range(200, 300):
            result['success'] = True
        elif int(code) == 401:
            # Session cookie has expired. This requires exception handling
            # by BigRobot
            pass
        elif int(code) == 409:
            # On POST when "List element already exists"
            result['success'] = True
        else:
            helpers.test_error("REST call failed with status code %s" % code)

        return result

    def http_request(self, *args, **kwargs):
        retries = int(kwargs.pop('retries', 0))
        sleep_time = float(kwargs.pop('sleep_time_between_retries', 10))

        while True:
            try:
                result = self._http_request(*args, **kwargs)
            except:
                helpers.log('HTTP request error:\n%s'
                            % helpers.exception_info())
                if retries > 0:
                    helpers.log(
                        'Retrying HTTP request in %s seconds (retries=%s)'
                        % (sleep_time, retries))
                    retries -= 1
                    helpers.sleep(sleep_time)
                else:
                    raise
            else:
                if int(result['status_code']) == 401:
                    if self.session_cookie_loop > 5:
                        helpers.test_error("Detected session cookie loop.")
                    elif ('description' in result['content'] and
                          re.match(r'.*cookie.*', result['content']['description'], re.I)):
                        # Retry if:
                        #   "Authorization failed: No session found for cookie"
                        #   "Authorization failed: No session cookie provided"
                        self.session_cookie_loop += 1
                        helpers.log("It appears the session cookie has expired."
                                    "  Requesting new session cookie.")
                        self.request_session_cookie()
                        # helpers.sleep(2)
                        # Re-run command
                        result = self._http_request(*args, **kwargs)
                    else:
                        # Error, possibly due to "invalid user/password combination" or others.
                        helpers.test_error("Unable to create session cookie.")
                else:
                    self.session_cookie_loop = 0
                break
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
