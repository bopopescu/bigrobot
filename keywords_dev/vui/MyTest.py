import autobot.helpers as helpers
import autobot.restclient as restclient
import autobot.test as test

def testing123():
    pass

class MyTest(object):

    def __init2__(self):
        t = test.Test()
        c = t.controller()

        url = '%s/api/v1/auth/login' % c.base_url
        result = c.rest.post(url, {"user":"admin", "password":"adminadmin"})
        session_cookie = result['content']['session_cookie']
        c.rest.set_session_cookie(session_cookie)

    def generate_data(self):
        return "MydataXXX"

    def save_data(self, data):
        helpers.log(data)
        return data

    def print_data(self, data):
        helpers.log(data)

    def test_scp(self):
        t = test.Test()
        c = t.controller()
        helpers.scp_put(c.ip, '/etc/hosts', '/tmp/12345/1234')

    def passing_kwargs_additions(self, arg_kw1=None, arg_kw2=None):
        helpers.log("arg_kw1: %s" % arg_kw1)
        helpers.log("arg_kw2: %s" % arg_kw2)

    def passing_kwargs(self, arg1, arg2, **kwargs):
        helpers.log("arg1: %s" % arg1)
        helpers.log("arg2: %s" % arg2)
        self.passing_kwargs_additions(**kwargs)

    def enable_help(self):
        t = test.Test()
        master = t.controller('master')
        helpers.log("master: %s" % master)

        slave = t.controller('slave')
        helpers.log("slave: %s" % slave)

        result = master.cli('show user')
        helpers.log("CLI output: %s" % result['content'])

        # master.rest().get('/api/v1/data/controller/applications/bvs/tenant')
        master.rest.get('/api/v1/data/controller/core/aaa/local-user')
        content = master.rest.content()
        helpers.log("content: %s" % content)

        content_json = master.rest.content_json()
        helpers.log("content_json: %s" % content_json)

        slave.cli("whoami")
        result_json = slave.rest.result_json()
        helpers.log("result_json: %s" % result_json)

        master.sudo('cat /etc/shadow')

    def host_commands(self):
        t = test.Test()
        h1 = t.host('h1')
        helpers.log("h1: %s" % h1)
        h1.bash("cat /etc/passwd")
        # h1.sudo("cat /etc/shadow")

    def switch_show_version(self, node):
        t = test.Test()
        s = t.switch(node)
        helpers.log("node: %s" % s)
        s.cli("show version")

    def switch_show_environment(self, node):
        t = test.Test()
        s = t.switch(node)
        helpers.log("node: %s" % s)
        s.cli("show environment")

    def switch_show_walk(self, node):
        t = test.Test()
        s = t.switch(node)
        helpers.log("Node: %s" % s)
        s.cli("show ?")

    def convert_openstack_table_output_to_dictionary(self):
        openstack_output = """
nova --os-username user1 --os-tenant-name Tenant1  --os-auth-url http://10.193.0.120:5000/v2.0/ --os-password bsn net-list
blah blah
+--------------------------------------+---------------------+------+
| ID                                   | Label               | CIDR |
+--------------------------------------+---------------------+------+
| 02f4a4d1-0930-43bf-94db-2d39b11c343d | External-Network    | None |
| 25b9465a-852c-434c-a06c-dce646145eb6 | Tenant1-Network-2   | None |
| 78f7740d-3774-41df-83e8-77e07a7d4206 | Tenant1-Network-129 | None |
| c2d1d2f4-3706-43cc-ad4a-19e4a97f91b0 | Coke-External       | None |
| d1919755-5872-4f4c-9320-29e91273c54a | 1-OutSide-Net       | None |
| fb68e3c6-dbc1-4334-b2aa-6539361c0bff | Tenant1-Network-1   | None |
+--------------------------------------+---------------------+------+
root@nova-controller:~#
root@nova-controller:~#
root@nova-controller:~#
root@nova-controller:~#
root@nova-controller:~#
"""
        out_dict = helpers.openstack_convert_table_to_dict(openstack_output)
        helpers.prettify_log("out_dict:", out_dict)

        # Now you can walk through the dictionary...
        key = '02f4a4d1-0930-43bf-94db-2d39b11c343d'
        helpers.log("key(%s) contains: %s" % (key, out_dict[key]))
        helpers.log("key(%s) label: %s" % (key, out_dict[key]['label']))

    def restart_mininet(self):
        t = test.Test()
        mn = t.mininet('mn')
        mn.stop_mininet()
        mn.stop_mininet()
        mn.start_mininet()
        mn.restart_mininet()

    def bounce_session_cookie(self):
        t = test.Test()
        c = t.controller('master')
        c.rest.get("/api/v1/data/controller/core/aaa/local-user")

    def get_a_dictionary(self):
        return { "abc": 123, "xyz": True}

    def process_a_dictionary(self, input_dict):
        helpers.warn("input_dict: %s" % input_dict)
        helpers.log("abc: %s" % input_dict['abc'])
        helpers.debug("xyz: %s" % input_dict['xyz'])
        helpers.trace("This is a trace log")

    def json_to_pydict(self, arg):
        helpers.log("arg: %s" % arg)
        arg_dict = helpers.from_json(arg)
        helpers.log("arg_dict: %s" % arg_dict)
