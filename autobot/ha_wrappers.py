import helpers


class HaBsnRestClient(object):
    """
    This class returns a faux BSN Rest Client. It is intended as a wrapper for
    handling HA/mastership logic. So we have to intercept all the common
    interfaces of REST (e.g., post, get, put, patch, delete, content, result,
    etc.) to ensure we are on the correct controller prior to executing the
    command.
    """
    def __init__(self, name, t):
        if name not in ('master', 'slave'):
            helpers.log("HA controller must either be 'master' or 'slave'")
        self.t = t
        self._name = name

    def logical_name(self):
        return self._name

    def status_code(self, *args, **kwargs):
        n = self.t.controller(self.logical_name(), resolve_mastership=True)
        return n.rest.status_code(*args, **kwargs)

    def status_code_ok(self, *args, **kwargs):
        n = self.t.controller(self.logical_name(), resolve_mastership=True)
        return n.rest.status_code_ok(*args, **kwargs)

    def error(self, *args, **kwargs):
        n = self.t.controller(self.logical_name(), resolve_mastership=True)
        return n.rest.error(*args, **kwargs)

    def result(self, *args, **kwargs):
        n = self.t.controller(self.logical_name(), resolve_mastership=True)
        return n.rest.result(*args, **kwargs)

    def result_json(self, *args, **kwargs):
        n = self.t.controller(self.logical_name(), resolve_mastership=True)
        return n.rest.result_json(*args, **kwargs)

    def content(self, *args, **kwargs):
        n = self.t.controller(self.logical_name(), resolve_mastership=True)
        return n.rest.content(*args, **kwargs)

    def content_json(self, *args, **kwargs):
        n = self.t.controller(self.logical_name(), resolve_mastership=True)
        return n.rest.content_json(*args, **kwargs)

    def post(self, *args, **kwargs):
        n = self.t.controller(self.logical_name(), resolve_mastership=True)
        return n.rest.post(*args, **kwargs)

    def get(self, *args, **kwargs):
        n = self.t.controller(self.logical_name(), resolve_mastership=True)
        return n.rest.get(*args, **kwargs)

    def put(self, *args, **kwargs):
        n = self.t.controller(self.logical_name(), resolve_mastership=True)
        return n.rest.put(*args, **kwargs)

    def patch(self, *args, **kwargs):
        n = self.t.controller(self.logical_name(), resolve_mastership=True)
        return n.rest.patch(*args, **kwargs)

    def delete(self, *args, **kwargs):
        n = self.t.controller(self.logical_name(), resolve_mastership=True)
        return n.rest.delete(*args, **kwargs)

    # def request_session_cookie(self, *args, **kwargs):
    #    n = self.t.controller(self.logical_name(), resolve_mastership=True)
    #    return n.rest.request_session_cookie(*args, **kwargs)


class HaControllerNode(object):
    """
    This class returns a faux controller node. It is intended as a wrapper for
    handling HA/mastership logic. So we have to intercept all the common
    interfaces of ControllerNode (e.g., cli, enable, config, bash,
    cli_content, cli_result, REST verbs/results, etc.) to ensure we are on the
    correct controller prior to executing the command.
    """
    def __init__(self, name, t):
        if name not in ('master', 'slave'):
            helpers.log("HA controller must either be 'master' or 'slave'")
        self.t = t
        self._name = name
        self.rest = HaBsnRestClient(name, t)

    # REST Shortcuts
    def post(self, *args, **kwargs):
        return self.rest.post(*args, **kwargs)

    def get(self, *args, **kwargs):
        return self.rest.get(*args, **kwargs)

    def put(self, *args, **kwargs):
        return self.rest.put(*args, **kwargs)

    def patch(self, *args, **kwargs):
        return self.rest.patch(*args, **kwargs)

    def delete(self, *args, **kwargs):
        return self.rest.delete(*args, **kwargs)

    def rest_content(self, *args, **kwargs):
        return self.rest.content(*args, **kwargs)

    def rest_result(self, *args, **kwargs):
        return self.rest.result(*args, **kwargs)

    def rest_content_json(self, *args, **kwargs):
        return self.rest.content_json(*args, **kwargs)

    def rest_result_json(self, *args, **kwargs):
        return self.rest.result_json(*args, **kwargs)

    def logical_name(self):
        return self._name

    def name(self):
        n = self.t.controller(self.logical_name(), resolve_mastership=True)
        return n.name()

    def ip(self):
        n = self.t.controller(self.logical_name(), resolve_mastership=True)
        return n.ip()

    def node_id(self):
        n = self.t.controller(self.logical_name(), resolve_mastership=True)
        return n.node_id()

    def user(self):
        n = self.t.controller(self.logical_name(), resolve_mastership=True)
        return n.user()

    def password(self):
        n = self.t.controller(self.logical_name(), resolve_mastership=True)
        return n.password()

    def platform(self, *args, **kwargs):
        n = self.t.controller(self.logical_name(), resolve_mastership=True)
        return n.platform(*args, **kwargs)

    def cli(self, *args, **kwargs):
        n = self.t.controller(self.logical_name(), resolve_mastership=True)
        return n.cli(*args, **kwargs)

    def enable(self, *args, **kwargs):
        n = self.t.controller(self.logical_name(), resolve_mastership=True)
        return n.enable(*args, **kwargs)

    def config(self, *args, **kwargs):
        n = self.t.controller(self.logical_name(), resolve_mastership=True)
        return n.config(*args, **kwargs)

    def bash(self, *args, **kwargs):
        n = self.t.controller(self.logical_name(), resolve_mastership=True)
        return n.bash(*args, **kwargs)

    def sudo(self, *args, **kwargs):
        n = self.t.controller(self.logical_name(), resolve_mastership=True)
        return n.sudo(*args, **kwargs)

    def cli_content(self, *args, **kwargs):
        n = self.t.controller(self.logical_name(), resolve_mastership=True)
        return n.cli_content(*args, **kwargs)

    def cli_result(self, *args, **kwargs):
        n = self.t.controller(self.logical_name(), resolve_mastership=True)
        return n.cli_result(*args, **kwargs)

    def bash_content(self, *args, **kwargs):
        n = self.t.controller(self.logical_name(), resolve_mastership=True)
        return n.bash_content(*args, **kwargs)

    def bash_result(self, *args, **kwargs):
        n = self.t.controller(self.logical_name(), resolve_mastership=True)
        return n.bash_result(*args, **kwargs)

    def set_prompt(self, *args, **kwargs):
        n = self.t.controller(self.logical_name(), resolve_mastership=True)
        return n.set_prompt(*args, **kwargs)

    def get_prompt(self, *args, **kwargs):
        n = self.t.controller(self.logical_name(), resolve_mastership=True)
        return n.get_prompt(*args, **kwargs)

    def send(self, *args, **kwargs):
        n = self.t.controller(self.logical_name(), resolve_mastership=True)
        return n.send(*args, **kwargs)

    def expect(self, *args, **kwargs):
        n = self.t.controller(self.logical_name(), resolve_mastership=True)
        return n.expect(*args, **kwargs)

    def waitfor(self, *args, **kwargs):
        n = self.t.controller(self.logical_name(), resolve_mastership=True)
        return n.waitfor(*args, **kwargs)

    def connect(self, *args, **kwargs):
        n = self.t.controller(self.logical_name(), resolve_mastership=True)
        return n.connect(*args, **kwargs)

    def console(self, *args, **kwargs):
        n = self.t.controller(self.logical_name(), resolve_mastership=True)
        return n.console(*args, **kwargs)
