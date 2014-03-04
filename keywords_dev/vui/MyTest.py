import autobot.helpers as helpers
import autobot.restclient as restclient
import autobot.test as test
import keywords.Host as Host

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
        helpers.scp_put(c.ip(), '/etc/hosts', '/tmp/12345/1234')

    def passing_kwargs_additions(self, arg_kw1=None, arg_kw2=None):
        helpers.log("arg_kw1: %s" % arg_kw1)
        helpers.log("arg_kw2: %s" % arg_kw2)

    def passing_kwargs(self, arg1, arg2, **kwargs):
        helpers.log("arg1: %s" % arg1)
        helpers.log("arg2: %s" % arg2)
        self.passing_kwargs_additions(**kwargs)
        helpers.log("kwargs: %s" % kwargs)

    def passing_kwargs2(self, **kwargs):
        helpers.log("kwargs: %s" % kwargs)

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
        s.cli("show uptime")
        # s.cli("show ")
        s.enable("show snmp")
        s.enable("bash")
        s.enable("ls -la")
        s.enable("exit")
        s.enable("show arp")

    def switch_show_environment(self, node):
        t = test.Test()
        s = t.switch(node)
        helpers.log("node: %s" % s)
        s.cli("show environment")

    def switch_uptime(self, node):
        t = test.Test()
        s = t.switch(node)
        helpers.log("node: %s" % s)
        s.bash("uptime")

    def switch_ping(self, node):
        t = test.Test()
        s = t.switch(node)
        helpers.log("node: %s" % s)
        host = Host.Host()
        host.bash_ping('s1', 'dev1')

    def switch_info(self, node):
        t = test.Test()
        s = t.switch(node)
        helpers.log("node: %s" % s)
        helpers.log("Switch model is '%s'" % s.info('model'))
        helpers.log("Switch manufacturer is '%s'" % s.info('manufacturer'))
        helpers.log("Switch '%s' console IP:%s, port:%s" %
                    (s.name(),
                     t.params(node, 'console_ip'),
                     t.params(node, 'console_port')))

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

    def kw_read_file(self, f):
        lines = helpers.file_read_once(f)
        helpers.log("lines:\n%s" % lines)
        return lines

    def kw_write_file(self, f, s):
        helpers.file_write_once(f, s)
        helpers.log("Wrote to file: %s" % f)

    def kw_cat_file(self, f):
        helpers.file_cat(f)

    def kw_strip_text(self):
        inf = '/tmp/glance-api-paste.ini'
        outf = '/tmp/new-glance-api-paste.ini'
        line_marker = r'^\[filter:authtoken\]'
        line_marker_end = r'^\[.+'
        append_string = '''
[filter:authtoken]
paste.filter_factory = keystoneclient.middleware.auth_token:filter_factory
delay_auth_decision = true
auth_host = 10.193.0.120
auth_port = 35357
auth_protocol = http
admin_tenant_name = service
admin_user = glance
'''
        helpers.openstack_replace_text_marker(input_file=inf,
                                              output_file=outf,
                                              line_marker=line_marker,
                                              line_marker_end=line_marker_end,
                                              append_string=append_string)

    def kw_mod_config(self):
        openstack_host = '10.193.0.120'
        helpers.scp_get(openstack_host, user='root', password='bsn',
                        remote_file='/etc/glance/glance-api-paste.ini',
                        local_path='/tmp')
        self.kw_strip_text()
        helpers.scp_put(openstack_host, user='root', password='bsn',
                        local_file='/tmp/new-glance-api-paste.ini',
                        remote_path='/tmp/glance-api-paste.ini')

    def ixia_info(self, node):
        t = test.Test()
        tg1 = t.traffic_generator(node)
        platform = tg1.platform()
        helpers.log("'%s' platform is '%s'" % (node, platform))
        params = t.topology_params()
        helpers.log("params: %s" % helpers.prettify(params))

    def sanitize_cli_output(self, node):
        t = test.Test()
        n = t.node(node)
        content = n.cli('show user')['content']
        output = helpers.strip_cli_output(content)
        helpers.log("output:\n%s" % output)

        lines = helpers.str_to_list(output)
        helpers.log("lines:\n%s" % helpers.prettify(lines))

    def check_mastership(self, node):
        t = test.Test()
        n = t.node(node)

        if (n.is_master()):
            controller_role = "MASTER"
        else:
            controller_role = "SLAVE"

        helpers.log("*** I am the %s of the Universe!" % controller_role)

    def restclient_show_user_negative(self):
        t = test.Test()
        n = t.node('c1')

        n.rest.get('/api/v1/data/controller/core/aaa/local-users')
        try:
            n.rest.get('/api/v1/data/controller/core/aaa/local-users')
        except:
            result = n.rest.result()
            helpers.log("***** result: %s" % helpers.prettify(result))
            helpers.log("***** status_code: %s" % result['status_code'])
            if int(result['status_code']) == 400:
                helpers.log("I expected this!!!")
            helpers.log("***** status_descr: %s" % result['status_descr'])

    def print_value(self, *arg):
        # helpers.log("arg: %s" % arg)
        # helpers.log("arg[0]: %s" % arg[0])
        # helpers.log("arg[1]: %s" % arg[1])
        # helpers.log("arg[2]: %s" % arg[2])
        for x in arg:
            helpers.log("x: %s" % x)
        print "I am here"
        helpers.set_env('BIGROBOT_ERROR', 12345)

    def bash_command(self, node, cmd):
        t = test.Test()
        n = t.node(node)
        n.bash(cmd, timeout=20)
        # helpers.log("Bash result: %s" % n.bash_result())
        # helpers.log("Bash content: %s" % n.bash_content())

    def ha_role(self, node):
        t = test.Test()
        c = t.controller(node)
        c.rest.get("/rest/v1/system/ha/role")
        controllers = t.controllers()
        helpers.log("*** Controllers: %s" % controllers)

    def _build_link_list(self, list):
        updated_list = []
        for l in list:
            src_switch = l['src']['interface']['name']
            src_intf = l['src']['switch-info']['switch-name']
            dst_switch = l['dst']['interface']['name']
            dst_intf = l['dst']['switch-info']['switch-name']
            key = "%s %s %s %s" % (src_switch, src_intf, dst_switch, dst_intf)

            # Convert unicode to ascii
            updated_list.append(key.encode('ascii', 'ignore'))
        return updated_list

    def verify_fabric_links(self, node):
        t = test.Test()
        c = t.controller(node)

        # Initial state
        content1 = c.rest.get('/api/v1/data/controller/applications/bvs/info/fabric?select=link')['content']
        link_list1 = self._build_link_list(content1[0]['link'])
        helpers.log("link_list1:\n%s" % helpers.prettify(link_list1))

        # Some stuff happened around here...

        # Next state (after reboot)
        content2 = c.rest.get('/api/v1/data/controller/applications/bvs/info/fabric?select=link')['content']
        link_list2 = self._build_link_list(content2[0]['link'])

        # For negative test... You can inject a bad entry
        # link_list2.append("bad entry")
        link_list2[10] = "bad entry"

        helpers.log("link_list2:\n%s" % helpers.prettify(link_list2))

        return helpers.list_compare(link_list1, link_list2)

    def return_boolean(self, boolean=True):
        helpers.debug("**** DEBUG: I'm inside return_boolean.")
        helpers.trace("**** TRACE: I'm inside return_boolean.")
        return boolean

    def devconf_reconnect(self):
        t = test.Test()
        c = t.controller('master')
        c.bash('uname -a')
        c.rest.get('/api/v1/data/controller/core/aaa/local-user')
        # c_vui = c.connect('vui', 'vuile123', protocol='ssh', name='c1_vui')
        # c_vui = c.connect('userChkPassword', 'bsnbsn', protocol='ssh', name='c1_vui')
        # c_vui.cli('show version')
        # c.bash('uptime')
        # c_vui.enable('show user')
        # c_new = t.node_reconnect(node='master', user='userChkPassword', password='bsnbsn')
        c_new = t.node_reconnect(node='master', user='vui', password='vuile123')
        c_new.enable("show running-config")
        helpers.log("*** user:%s, password:%s" % (c_new.user(), c_new.password()))
        c_new.rest.get('/api/v1/data/controller/core/aaa/local-user')

    def return_dict(self):
        return {'abc': 123, 'xyz': 456}

    def return_list(self):
        return [1, 2, 3, 4, 5]

    def pause(self, msg=None):
        if not msg:
            msg = "Pausing... Press Ctrl-D to continue."
        helpers.warn(msg)
        import fileinput
        for _ in fileinput.input():
            pass

    def pause2(self, msg=None):
        if not msg:
            msg = "Pausing... Press Ctrl-D to continue."
        helpers.warn(msg)
        import sys
        for _ in sys.stdin:
            pass

    def return_false(self):
        return False

    def ssh_send_control_c(self):
        t = test.Test()
        c = t.controller('c1')

        c.cli('')  # Make sure we're in CLI mode

        #**** CLI walk: show ?
        c.send('show ?', no_cr=True)
        c.expect(r'[\r\n\x07][\w_-]+[#>] ')  # Match CLI prompt
        # c.expect(r'[\r\n][\w-_]+[#>] ')  # Match CLI prompt
        content = c.cli_content()
        new_content = helpers.strip_cli_output(content)
        new_content = helpers.str_to_list(new_content)
        helpers.log("new_content:\n%s" % helpers.prettify(new_content))

        c.send(helpers.ctrl('u'))  # Erase input
        c.expect()  # Match default CLI prompt

        #**** CLI walk: show event-history ?
        c.send('show event-history ?', no_cr=True)
        # c.expect(r'[\r\n]\w+[#>] ')  # Match CLI prompt
        c.expect(r'[\r\n\x07][\w_-]+[#>] ')  # Match CLI prompt
        content = c.cli_content()
        new_content = helpers.strip_cli_output(content)
        new_content = helpers.str_to_list(new_content)
        helpers.log("new_content:\n%s" % helpers.prettify(new_content))

        c.send(helpers.ctrl('u'))  # Erase input
        c.expect()  # Match default CLI prompt

        #**** CLI walk: show event-history topology-link ?
        c.send('show event-history topology-link ?', no_cr=True)
        # c.expect(r'[\r\n]\w+[#>] ')  # Match CLI prompt
        c.expect(r'[\r\n\x07][\w_-]+[#>] ')  # Match CLI prompt
        content = c.cli_content()
        new_content = helpers.strip_cli_output(content)
        new_content = helpers.str_to_list(new_content)
        helpers.log("new_content:\n%s" % helpers.prettify(new_content))

        c.send(helpers.ctrl('u'))  # Erase input
        c.expect()  # Match default CLI prompt

        #**** Done! Just making sure some random command continues to work...
        c.cli('show user')

    def ping_from_stage_machine(self, host):
        loss = helpers.ping(host)
        helpers.log("Ping loss = %s" % loss)
        if loss > 10:
            helpers.log("Greater than 10% packet loss")
            return False
        else:
            helpers.log("Less than 10% packet loss")
            return True

    def spawn_a_node(self):
        t = test.Test()
        n = t.node_spawn(ip='10.193.0.43')
        # n = t.node_spawn(ip='10.193.0.43', user='adminX', password='adminadmin')
        n.cli('show user')
