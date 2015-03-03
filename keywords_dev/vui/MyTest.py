import sys
import re
import autobot.helpers as helpers
import autobot.test as test
import keywords.Host as Host
from keywords.BsnCommon import BsnCommon

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
        return "MydataX"

    def save_data(self, data):
        helpers.log(data)
        return data

    def print_data(self, data):
        helpers.log(data)

    def test_scp(self):
        t = test.Test()
        c = t.controller()
        helpers.scp_put(c.ip(), '/etc/hosts', '/tmp/12345/1234')

    def test_scp_get_bulk(self):
        t = test.Test()
        c = t.controller()
        helpers.scp_get(c.ip(),
                        remote_file='/var/log',
                        local_path='/tmp',
                        user='recovery',
                        password='bsn')

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
        s.enable("show running-config")
        # # s.cli("show ")
        # s.enable("show snmp")
        # s.enable("bash")
        # s.enable("ls -la")
        # s.enable("exit")
        # s.enable("show arp")

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
        helpers.pretty_log(out_dict)

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

    def rest_version_check(self, node):
        t = test.Test()
        n = t.node(node)
        n.rest.get('/api/v1/data/controller/core/version/appliance')
        content = n.rest.content()
        version_string = content[0]['release-string']
        helpers.log("version string is '%s'" % version_string)
        helpers.log("****** user_abc: %s" % t.params('common', 'user_abc'))
        helpers.log("****** user_switch_image: %s" % t.params('common', 'user_switch_image'))

    def rest_show_user(self, node):
        t = test.Test()
        n = t.node(node)
        n.rest.get('/api/v1/data/controller/core/aaa/local-user')

    def rest_show_user_negative(self):
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

    def _build_link_list(self, alist):
        updated_list = []
        for l in alist:
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

    def controller_reconnect(self):
        t = test.Test()
        t.node_reconnect('c1')

    def return_dict(self):
        return {'abc': 123,
                'xyz': 456,
                'def': [ { 'first': 1, 'second': 2} ]
                }

    def return_list(self):
        return [1, 2, 3, 4, 5]

    def pauseX(self, msg=None):
        if not msg:
            msg = "Pausing... Press Ctrl-D to continue."
        helpers.warn(msg)
        import fileinput
        for _ in fileinput.input():
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

    def return_a_list(self):
        l = [1, 2, 3]
        helpers.summary_log("Return value is %s" % l)
        helpers.summary_log("What is the meaning of life?")
        helpers.summary_log("Life is like a box of chocolate")
        helpers.warn("Here I am")
        helpers.summary_log("This is the end")
        return l

    def set_empty_string(self):
        return 'aa'

    def config_block(self):
        t = test.Test()
        c = t.controller('c1')

        c.config('')
        c.send('?')

        prompt_re = r'[\r\n\x07]?[\w-]+\(([\w-]+)\)[#>] '
        c.expect(prompt_re)
        content = c.cli_content()
        helpers.log("********** CONTENT ************\n%s" % content)

        # Content is a multiline string. Convert it to a list of strings. Then
        # get the last entry which should be the prompt.
        prompt_str = helpers.str_to_list(content)[-1]

        helpers.log("Prompt: '%s'" % prompt_str)

        match = re.match(prompt_re, prompt_str)
        if match:
            print "Match! Found: %s" % match.group(1)
        else:
            print "No match"

    def config_walk(self):
        t = test.Test()
        c = t.controller('c1')
        c.cli('reauth admin', prompt='Password: ')
        c.send('adminadmin')
        c.expect()

    def exit_nested_config(self):
        t = test.Test()
        c = t.controller('c1')
        c.config('user vui')
        c.cli('show user')

    def test_expect_prompts(self):
        t = test.Test()
        c = t.controller('c1')
        c.cli('')
        c.send('show user')
        opts = c.expect(['blah', 'bleh', c.get_prompt()])
        helpers.log("opts[0]: %s" % opts[0])  # 0 matches 'blah' and so on
        helpers.log("opts[1]: %s" % opts[1])  # re.match object (<_sre.SRE_Match object at 0x106ffe1f8>)

    def ping_result(self):
        s = """ping -c 10 dev1
PING dev1.bigswitch.com (10.192.4.11): 56 data bytes
64 bytes from 10.192.4.11: icmp_seq=0 ttl=61 time=4.098 ms
64 bytes from 10.192.4.11: icmp_seq=1 ttl=61 time=0.563 ms
64 bytes from 10.192.4.11: icmp_seq=2 ttl=61 time=0.626 ms
64 bytes from 10.192.4.11: icmp_seq=3 ttl=61 time=0.654 ms
64 bytes from 10.192.4.11: icmp_seq=4 ttl=61 time=0.578 ms
64 bytes from 10.192.4.11: icmp_seq=5 ttl=61 time=0.589 ms
64 bytes from 10.192.4.11: icmp_seq=6 ttl=61 time=0.628 ms
64 bytes from 10.192.4.11: icmp_seq=7 ttl=61 time=8.381 ms
64 bytes from 10.192.4.11: icmp_seq=8 ttl=61 time=0.644 ms
64 bytes from 10.192.4.11: icmp_seq=9 ttl=61 time=0.619 ms

--- dev1.bigswitch.com ping statistics ---
10 packets transmitted, 10 packets received, 0.0% packet loss
round-trip min/avg/max/stddev = 0.563/1.738/8.381/2.446 ms
vui@Vuis-MacBook-Pro$
"""
        return s

    def openstack_server_interact(self):
        t = test.Test()
        os1 = t.openstack_server('os1')
        os1.sudo('cat /etc/shadow')

    def test_console(self, node):
        """
        Telnet to a BSN controller or switch console. Try to put the device in
        CLI mode, or die trying...
        """
        t = test.Test()
        con = t.dev_console(node)
        con.bash("w")
        con.sudo("cat /etc/shadow")
        con.enable("show running-config")

        # IMPORTANT: Be sure to get back to CLI mode so future console
        # connections won't get confused.
        con.cli("")

    def test_controller_console(self, node):
        """
        Telnet to a BSN controller or switch console. Try to put the device in
        CLI mode, or die trying...
        """
        t = test.Test()
        n = t.node(node)
        n_console = t.dev_console(node, expect_console_banner=True)

        n_console.bash("w")
        n_console.sudo("cat /etc/shadow")
        n_console.cli("")
        n.console_close()  # **** Closing the console

        helpers.log("***** Re-establishing connection to console for '%s'" % node)
        n_console = t.dev_console(node, expect_console_banner=True)
        n_console.enable("show running-config")

        # IMPORTANT: Be sure to get back to CLI mode so future console
        # connections won't get confused.
        n_console.cli("")

    def test_switch_console(self, node):
        t = test.Test()
        n = t.node(node)
        n_console = t.dev_console(node)

        n_console.cli("show version")
        n.console_close()  # **** Closing the console

        helpers.log("***** Re-establishing connection to console for '%s'" % node)
        n_console = t.dev_console(node)
        n_console.enable("show running-config")

        # IMPORTANT: Be sure to get back to CLI mode so future console
        # connections won't get confused.
        n_console.cli("")


    def test_console2(self, node):
        t = test.Test()
        n = t.node(node)
        n_console = n.console()
        n_console.expect(r'Escape character.*[\r\n]')

        n_console.send('')
        n_console.expect(r'admin.*\$ ')

        n_console.send('find /etc')
        helpers.log("Sleeping for 3 seconds")
        helpers.sleep(3)
        # n_console.expect(r'.*')
        n_console.expect(r'admin.*\$ ')

        n_console.send('')
        n_console.expect(r'admin.*\$ ')

        n_console.send('pwd')
        n_console.expect(r'admin.*\$ ')

        n_console.send('env')
        n_console.expect(r'admin.*\$ ')

        n_console.send('')
        n_console.expect(r'admin.*\$ ')


    def test_console_reconnect(self, node):
        t = test.Test()
        n = t.node(node)
        n_console = n.console()
        n_console.send('')
        n_console.expect(r'login:')
        n_console.send(helpers.ctrl(']'))
        helpers.sleep(1)
        n_console = n.console_reconnect()
        n_console.send('')
        n_console.expect(r'login:')
        n.console_close()

    def test_run_cmd(self):
        helpers.run_cmd('cd /tmp; echo "This is a test" > outfile', '/tmp', shell=True)

    def test_esb_simple(self, nodes):
        # from bsn_services import sample_method_tasks as tasks
        from template_services import tasks as tasks

        t = test.Test()
        helpers.log("***** params: %s" % helpers.prettify(t.params()))

        results = []
        result_dict = {}

        task = tasks.BsnCommands()

        #
        # Parallel execution happens below
        #

        # Task 1
        res1 = task.cli_show_user.delay(t.params(), nodes[0])
        task_id = res1.task_id
        results.append(res1)
        result_dict[task_id] = { "node": nodes[0], "action": "show user" }

        #
        # Check task status - are we done yet?
        #
        is_pending = True
        iterations = 0
        max_tries = 10
        while is_pending and iterations < max_tries:
            is_pending = False
            iterations += 1
            helpers.sleep(1)
            for res in results:
                task_id = res.task_id
                action = result_dict[task_id]["node"] + ' ' + result_dict[task_id]["action"]
                if res.ready() == True:
                    helpers.log("****** %d.READY     - task_id(%s)['%s']"
                                % (iterations, res.task_id, action))
                else:
                    helpers.log("****** %d.NOT-READY - task_id(%s)['%s']"
                                % (iterations, res.task_id, action))
                    is_pending = True
        if is_pending and iterations > max_tries:
            helpers.log("Not able to retrieve results from ESB")
            return False

        helpers.log("*** Parallel tasks completed")

        #
        # Check task output
        #
        for res in results:
            task_id = res.task_id
            output = res.get()
            result_dict[task_id]["result"] = output

        helpers.log("***** result_dict:\n%s" % helpers.prettify(result_dict))

        return True

    def test_esb(self, nodes):
        # from bsn_services import sample_method_tasks as tasks
        from template_services import tasks as tasks

        t = test.Test()
        helpers.log("***** params: %s" % helpers.prettify(t.params()))

        results = []
        result_dict = {}

        task = tasks.BsnCommands()

        #
        # Parallel execution happens below
        #

        # Task 1
        res1 = task.cli_show_user.delay(t.params(), nodes[0])
        task_id = res1.task_id
        helpers.log("Task_id: %s" % task_id)
        results.append(res1)
        result_dict[task_id] = { "node": nodes[0], "action": "show user" }

        # Task 2
        res1 = task.cli_show_running_config.delay(t.params(), nodes[1])
        task_id = res1.task_id
        helpers.log("Task_id: %s" % task_id)
        results.append(res1)
        result_dict[task_id] = { "node": nodes[1], "action": "show running-config" }

        # Task 3
        res1 = task.bash_ping_regression_server.delay(t.params(), nodes[1])
        task_id = res1.task_id
        helpers.log("Task_id: %s" % task_id)
        results.append(res1)
        result_dict[task_id] = { "node": nodes[1], "action": "ping regression server" }

        # More tasks
        for node in nodes:
            res1 = task.cli_show_version.delay(t.params(), node)
            task_id = res1.task_id
            helpers.log("Task_id: %s" % task_id)
            results.append(res1)
            result_dict[task_id] = { "node": node, "action": "show version" }

        # ...and so on...

        #
        # Check task status - are we done yet?
        #
        is_pending = True
        iterations = 0
        max_tries = 10
        while is_pending and iterations <= max_tries:
            is_pending = False
            iterations += 1
            helpers.sleep(1)
            for res in results:
                task_id = res.task_id
                action = result_dict[task_id]["node"] + ' ' + result_dict[task_id]["action"]
                if res.ready() == True:
                    helpers.log("****** %d.READY     - task_id(%s)['%s']"
                                % (iterations, res.task_id, action))
                else:
                    helpers.log("****** %d.NOT-READY - task_id(%s)['%s']"
                                % (iterations, res.task_id, action))
                    is_pending = True
        if is_pending and iterations > max_tries:
            helpers.log("Not able to retrieve results from ESB")
            return False

        helpers.log("*** Parallel tasks completed")
        for res in results:
            task_id = res.task_id
            helpers.log_task_output(task_id)  # display URL of task output

        #
        # Check task output
        #
        for res in results:
            task_id = res.task_id
            output = res.get()
            result_dict[task_id]["result"] = output

        helpers.log("***** result_dict:\n%s" % helpers.prettify(result_dict))

        return True

    def test_bsn_common_services(self):
        from bsn_common_services import tasks as tasks
        t = test.Test()
        task = tasks.UpgradeCommands()

        res1 = task.add.delay(99, 99)
        res2 = task.add.delay(101, 101)
        results = []
        results.append(res1)
        results.append(res2)

        is_pending = True
        iterations = 0
        max_tries = 10
        while is_pending and iterations <= max_tries:
            is_pending = False
            iterations += 1
            helpers.sleep(3)
            for res in results:
                task_id = res.task_id
                if res.ready() == True:
                    helpers.log("****** %d.READY     - task_id(%s)"
                                % (iterations, res.task_id))
                else:
                    helpers.log("****** %d.NOT-READY - task_id(%s)"
                                % (iterations, res.task_id))
                    is_pending = True
        if is_pending and iterations > max_tries:
            helpers.log("Not able to retrieve results from ESB")
            return False

        helpers.log("*** Parallel tasks completed")
        for res in results:
            task_id = res.task_id
            helpers.log_task_output(task_id)  # display URL of task output

        #
        # Check task output
        #
        for res in results:
            task_id = res.task_id
            output = res.get()
            helpers.log("task_id: %s, result: %s" % (res.task_id, output))

    def test_vui_esb(self, nodes):
        # from bsn_services import sample_method_tasks as tasks
        from vui_services import tasks as tasks

        t = test.Test()
        helpers.log("***** params: %s" % helpers.prettify(t.params()))

        results = []
        result_dict = {}

        task = tasks.BsnCommands()

        #
        # Parallel execution happens below
        #

        # Task 1
        res1 = task.cli_show_user.delay(t.params(), nodes[0])
        task_id = res1.task_id
        helpers.log("Task_id: %s" % task_id)
        results.append(res1)
        result_dict[task_id] = { "node": nodes[0], "action": "show user" }

        # Task 2
        res1 = task.cli_show_running_config.delay(t.params(), nodes[1])
        task_id = res1.task_id
        helpers.log("Task_id: %s" % task_id)
        results.append(res1)
        result_dict[task_id] = { "node": nodes[1], "action": "show running-config" }

        # Task 3
        res1 = task.bash_ping_regression_server.delay(t.params(), nodes[1])
        task_id = res1.task_id
        helpers.log("Task_id: %s" % task_id)
        results.append(res1)
        result_dict[task_id] = { "node": nodes[1], "action": "ping regression server" }

        # More tasks
        for node in nodes:
            res1 = task.cli_show_version.delay(t.params(), node)
            task_id = res1.task_id
            helpers.log("Task_id: %s" % task_id)
            results.append(res1)
            result_dict[task_id] = { "node": node, "action": "show version" }

        # ...and so on...

        #
        # Check task status - are we done yet?
        #
        is_pending = True
        iterations = 0
        max_tries = 10
        while is_pending and iterations <= max_tries:
            is_pending = False
            iterations += 1
            helpers.sleep(3)
            for res in results:
                task_id = res.task_id
                action = result_dict[task_id]["node"] + ' ' + result_dict[task_id]["action"]
                if res.ready() == True:
                    helpers.log("****** %d.READY     - task_id(%s)['%s']"
                                % (iterations, res.task_id, action))
                else:
                    helpers.log("****** %d.NOT-READY - task_id(%s)['%s']"
                                % (iterations, res.task_id, action))
                    is_pending = True
        if is_pending and iterations > max_tries:
            helpers.log("Not able to retrieve results from ESB")
            return False

        helpers.log("*** Parallel tasks completed")
        for res in results:
            task_id = res.task_id
            helpers.log_task_output(task_id)  # display URL of task output

        #
        # Check task output
        #
        for res in results:
            task_id = res.task_id
            helpers.log("Getting result for task_id: %s" % task_id)
            output = res.get()
            result_dict[task_id]["result"] = output

        helpers.log("***** result_dict:\n%s" % helpers.prettify(result_dict))
        return True

    def exit_early(self):
        helpers.log("*** We're bailing early!!!")
        sys.exit(1)

    def my_enable_commands(self, node):
        t = test.Test()
        n = t.node(node)
        n.enable("show switch")
        n.enable("show running-config")
        n.enable("show user")

    def my_config_commands(self, node):
        t = test.Test()
        n = t.node(node)
        n.config("show switch")
        n.config("show running-config")
        n.config("show user")

    def parse_table(self):
        output = """+--------------------------------------+------+-------------------+-----------------------------------------------------------------------------------+
| id                                   | name | mac_address       | fixed_ips                                                                         |
+--------------------------------------+------+-------------------+-----------------------------------------------------------------------------------+
| e5999f23-1974-4cd9-ab45-8f0e61955a96 |      | fa:16:3e:55:c2:2f | {"subnet_id": "ad7148b3-0fee-4b89-a912-1792f75596a7", "ip_address": "100.0.2.12"} |
| fe363bd8-868f-4e29-b848-2e3a6f3b9b35 |      | fa:16:3e:76:57:a0 | {"subnet_id": "d5926f6b-d848-429c-b9b0-3b82600ce195", "ip_address": "20.0.0.1"}   |
+--------------------------------------+------+-------------------+-----------------------------------------------------------------------------------+
"""
        output2 = """
+----------------------+--------------------------------------+
| Property             | Value                                |
+----------------------+--------------------------------------+
| status               | ACTIVE                               |
| updated              | 2014-01-03T06:51:26Z                 |
| name                 | Ubuntu.13.10                         |
| created              | 2014-01-03T06:50:55Z                 |
| minDisk              | 0                                    |
| progress             | 100                                  |
| minRam               | 0                                    |
| OS-EXT-IMG-SIZE:size | 243662848                            |
| id                   | 8caae5ae-66dd-4ee1-87f8-08674da401ff |
+----------------------+--------------------------------------+
prompt>
"""
        table = helpers.openstack_convert_table_to_dict(output)
        helpers.debug("**** table:\n%s" % helpers.prettify(table))

        """
        for key, value in table.items():
            # Parse the fixed_ips column to get IP address
            fixed_ips_str = value['fixed_ips']
            fixed_ips_dict = helpers.from_json(fixed_ips_str)
            helpers.log("ID:%s  ip_address:%s" % (key, fixed_ips_dict['ip_address']))
        """
        return True

    def ping_background_trial(self, node):
        t = test.Test()
        n = t.node(node)
        output = """
PING blade-0-b.eng.bigswitch.com (10.2.3.52) 56(84) bytes of data.
64 bytes from 10.2.3.52: icmp_req=1 ttl=61 time=0.444 ms
64 bytes from 10.2.3.52: icmp_req=2 ttl=61 time=0.458 ms
64 bytes from 10.2.3.52: icmp_req=3 ttl=61 time=0.440 ms
64 bytes from 10.2.3.52: icmp_req=4 ttl=61 time=0.388 ms
64 bytes from 10.2.3.52: icmp_req=5 ttl=61 time=0.417 ms
64 bytes from 10.2.3.52: icmp_req=6 ttl=61 time=0.504 ms
64 bytes from 10.2.3.52: icmp_req=7 ttl=61 time=0.434 ms
64 bytes from 10.2.3.52: icmp_req=8 ttl=61 time=0.499 ms
64 bytes from 10.2.3.52: icmp_req=9 ttl=61 time=0.403 ms
64 bytes from 10.2.3.52: icmp_req=10 ttl=61 time=0.458 ms
64 bytes from 10.2.3.52: icmp_req=11 ttl=61 time=0.464 ms
64 bytes from 10.2.3.52: icmp_req=12 ttl=61 time=0.437 ms
64 bytes from 10.2.3.52: icmp_req=13 ttl=61 time=0.476 ms
64 bytes from 10.2.3.52: icmp_req=14 ttl=61 time=0.428 ms
64 bytes from 10.2.3.52: icmp_req=15 ttl=61 time=0.440 ms
64 bytes from 10.2.3.52: icmp_req=16 ttl=61 time=0.454 ms
64 bytes from 10.2.3.52: icmp_req=17 ttl=61 time=0.491 ms
64 bytes from 10.2.3.52: icmp_req=18 ttl=61 time=0.405 ms
64 bytes from 10.2.3.52: icmp_req=19 ttl=61 time=0.411 ms
64 bytes from 10.2.3.52: icmp_req=20 ttl=61 time=0.451 ms
64 bytes from 10.2.3.52: icmp_req=21 ttl=61 time=0.374 ms
64 bytes from 10.2.3.52: icmp_req=22 ttl=61 time=0.461 ms
64 bytes from 10.2.3.52: icmp_req=23 ttl=61 time=0.405 ms
64 bytes from 10.2.3.52: icmp_req=24 ttl=61 time=0.399 ms
64 bytes from 10.2.3.52: icmp_req=25 ttl=61 time=0.458 ms
64 bytes from 10.2.3.52: icmp_req=26 ttl=61 time=0.507 ms
64 bytes from 10.2.3.52: icmp_req=27 ttl=61 time=0.417 ms
64 bytes from 10.2.3.52: icmp_req=28 ttl=61 time=0.439 ms
64 bytes from 10.2.3.52: icmp_req=29 ttl=61 time=0.363 ms
64 bytes from 10.2.3.52: icmp_req=30 ttl=61 time=0.416 ms
64 bytes from 10.2.3.52: icmp_req=31 ttl=61 time=0.416 ms
64 bytes from 10.2.3.52: icmp_req=32 ttl=61 time=0.456 ms
64 bytes from 10.2.3.52: icmp_req=33 ttl=61 time=0.424 ms
64 bytes from 10.2.3.52: icmp_req=34 ttl=61 time=0.408 ms
64 bytes from 10.2.3.52: icmp_req=35 ttl=61 time=0.404 ms
64 bytes from 10.2.3.52: icmp_req=36 ttl=61 time=0.460 ms
64 bytes from 10.2.3.52: icmp_req=37 ttl=61 time=0.439 ms
64 bytes from 10.2.3.52: icmp_req=38 ttl=61 time=0.420 ms
64 bytes from 10.2.3.52: icmp_req=39 ttl=61 time=0.428 ms
64 bytes from 10.2.3.52: icmp_req=40 ttl=61 time=0.527 ms
64 bytes from 10.2.3.52: icmp_req=41 ttl=61 time=0.457 ms
64 bytes from 10.2.3.52: icmp_req=42 ttl=61 time=0.529 ms
64 bytes from 10.2.3.52: icmp_req=43 ttl=61 time=0.393 ms
64 bytes from 10.2.3.52: icmp_req=44 ttl=61 time=0.368 ms
64 bytes from 10.2.3.52: icmp_req=45 ttl=61 time=0.454 ms
64 bytes from 10.2.3.52: icmp_req=46 ttl=61 time=0.487 ms
64 bytes from 10.2.3.52: icmp_req=47 ttl=61 time=0.443 ms
64 bytes from 10.2.3.52: icmp_req=48 ttl=61 time=0.479 ms
64 bytes from 10.2.3.52: icmp_req=49 ttl=61 time=0.525 ms
64 bytes from 10.2.3.52: icmp_req=50 ttl=61 time=0.470 ms
64 bytes from 10.2.3.52: icmp_req=51 ttl=61 time=0.425 ms
64 bytes from 10.2.3.52: icmp_req=52 ttl=61 time=0.415 ms
64 bytes from 10.2.3.52: icmp_req=53 ttl=61 time=0.455 ms
64 bytes from 10.2.3.52: icmp_req=54 ttl=61 time=0.380 ms
64 bytes from 10.2.3.52: icmp_req=55 ttl=61 time=0.439 ms
64 bytes from 10.2.3.52: icmp_req=56 ttl=61 time=0.516 ms
64 bytes from 10.2.3.52: icmp_req=57 ttl=61 time=0.432 ms
64 bytes from 10.2.3.52: icmp_req=58 ttl=61 time=0.458 ms
64 bytes from 10.2.3.52: icmp_req=59 ttl=61 time=0.507 ms
64 bytes from 10.2.3.52: icmp_req=60 ttl=61 time=0.446 ms
64 bytes from 10.2.3.52: icmp_req=61 ttl=61 time=0.438 ms
64 bytes from 10.2.3.52: icmp_req=62 ttl=61 time=0.457 ms
64 bytes from 10.2.3.52: icmp_req=63 ttl=61 time=0.450 ms
64 bytes from 10.2.3.52: icmp_req=64 ttl=61 time=0.455 ms
64 bytes from 10.2.3.52: icmp_req=65 ttl=61 time=0.419 ms
64 bytes from 10.2.3.52: icmp_req=66 ttl=61 time=0.402 ms
64 bytes from 10.2.3.52: icmp_req=67 ttl=61 time=0.431 ms
64 bytes from 10.2.3.52: icmp_req=68 ttl=61 time=0.480 ms
64 bytes from 10.2.3.52: icmp_req=69 ttl=61 time=0.406 ms

--- blade-0-b.eng.bigswitch.com ping statistics ---
69 packets transmitted, 69 received, 0% packet loss, time 68100ms
rtt min/avg/max/mdev = 0.363/0.442/0.529/0.044 ms
"""
        loss_pct = helpers.ping(ping_output=output)
        helpers.log("Ping loss percentage: %s" % loss_pct)
        return loss_pct

    def run_cmd_test(self):
        arg1, arg2 = helpers.run_cmd('cat /etc/hosts', shell=True)
        helpers.log("arg1: %s" % arg1)
        helpers.log("arg2: %s" % arg2)

    def strip_control_char_test(self):
        string = "abc" + helpers.ctrl('g') + "def"
        helpers.log("string: %s" % string)
        helpers.log("stripped string: %s" % helpers.strip_ctrl_chars(string))

    def match_dict_entries(self, ip, netmask):
        data = '''
[ {
  "copy-to-cpu" : false,
  "drop" : false,
  "dst-vrf" : 1023,
  "ecmp-index" : 0,
  "ip" : "0.0.0.0",
  "ip-mask" : "0.0.0.0",
  "mac" : "5c:16:c7:01:03:ff",
  "port-group-lag-id" : 0,
  "rack-lag-id" : 84,
  "vlan-id" : 4094,
  "vrf" : 18
}, {
  "copy-to-cpu" : true,
  "drop" : true,
  "dst-vrf" : 0,
  "ecmp-index" : 0,
  "ip" : "10.253.1.0",
  "ip-mask" : "255.255.255.0",
  "port-group-lag-id" : 0,
  "rack-lag-id" : 0,
  "vlan-id" : 0,
  "vrf" : 18
}, {
  "copy-to-cpu" : true,
  "drop" : true,
  "dst-vrf" : 0,
  "ecmp-index" : 0,
  "ip" : "10.253.2.0",
  "ip-mask" : "255.255.255.0",
  "port-group-lag-id" : 0,
  "rack-lag-id" : 0,
  "vlan-id" : 0,
  "vrf" : 18
} ]
'''
        new_data = helpers.from_json(data)
        helpers.log("new_data: %s" % helpers.prettify(new_data))
        for entry in new_data:
            if entry['ip'] == ip:
                helpers.log("Match IP address '%s'" % ip)
                if entry['ip-mask'] == netmask:
                    helpers.log("Match IP address '%s', netmask '%s'" % (ip, netmask))
                    return entry
                else:
                    helpers.log("No match")
        return {}

    def test_node_reconnect(self, node):
        t = test.Test()
        n = t.node(node)
        content = n.cli('show user')['content']
        output = helpers.strip_cli_output(content)
        helpers.log("**** output: %s" % output)
        try:
            n = t.node_reconnect(node, delete_session_cookie=False)
        except:
            helpers.log(helpers.exception_info())
        n.bash('uptime')
        n2 = t.node_spawn(ip=n.ip())
        n2.cli('show session')
        n.cli('show version')
        helpers.test_error("I quit!!!", soft_error=True)

    def spawn_login_sessions(self, max_sessions):
        helpers.log("***Entering==> spawn_login_sessions")
        t = test.Test()
        c = t.controller('master')
        ip = c.ip()

        n = []
        for i in range (0, int(max_sessions)):
            helpers.log('USR info:  this is loop: %d' % i)
            node = t.node_spawn(ip)
            n.append(node)
            helpers.log("!!!! Executing command on node(%s, name=%s)" % (i, node.name()))
            node.cli('show user')
            c.bash('netstat | grep ssh; netstat | grep ssh | wc -l; w | grep floodlight-login')
            helpers.sleep(3)

        helpers.log("!!!! Total login sessions: %s" % len(n))

        i = 0
        for node in n:
            helpers.log("!!!! Executing command on node(%s, name=%s)" % (i, node.name()))
            node.cli('show ntp')
            i += 1

        helpers.log("***Exiting==> spawn_login_sessions")
        return True

    def reauth_trial(self, node):
        t = test.Test()
        c = t.controller(node)
        c.cli('')
        c.send('reauth')
        c.expect(r'Password: ')
        c.cli('adminadmin')

    def rest_api_benchmark(self, node, requests=2000, concurrent_requests=40,
                           log_header=False, log_trailer=False):
        """
        Run Apache Bench ('ab') against BCF controller. There are 2 parameters which can be tweaked - requests and concurrent_requests.
        Some caveats:
        - This test doesn't return a PASS/FAIL result.
        - The REST command is limited to a simple GET which minimal data transfered.

        Inputs:
        | rest_api_benchmark | node=c1 | concurrent_request=300 | requests = 5000 |
        """
        t = test.Test()
        c = t.controller(node)
        session_cookie = c.rest.get_session_cookie()
        url = c.rest.format_url('/api/v1/data/controller/core/controller/role')
        output_txt = ("%s/output-concurrent-%s,requests-%s.txt"
                      % (helpers.bigrobot_log_path_exec_instance(),
                         concurrent_requests, requests))
        output_tsv = ("%s/output-concurrent-%s,requests-%s.tsv"
                      % (helpers.bigrobot_log_path_exec_instance(),
                         concurrent_requests, requests))
        output_log = ("%s/output.log"
                      % (helpers.bigrobot_log_path_exec_instance()))

        helpers.log("'%s' session cookie: '%s'" % (node, session_cookie))
        cmd = ("ab -n %s -c %s -H Cookie:session_cookie=%s -g %s %s"
               % (requests, concurrent_requests, session_cookie, output_tsv, url))
        (status, output, err_str, err_code) = helpers.run_cmd2(
                                        cmd=cmd,
                                        shell=True)
        helpers.log("run_cmd2 output:\n%s" % helpers.prettify(
                                                    {"status": status,
                                                     "output": output,
                                                     "err_str": err_str,
                                                     "err_code": err_code}))
        helpers.log(output)
        helpers.log("Dumping benchmark output to %s" % output_txt)
        helpers.file_write_once(output_txt, output)

        for line in helpers.str_to_list(output):
            match = re.match(r'.*concurrency level:\s+(\d+).*', line, re.I)
            if match:
                result_concurrent = match.group(1)
                continue
            match = re.match(r'.*time taken for tests:\s+(\d+(\.\d+)?).*', line, re.I)
            if match:
                result_exec_time = match.group(1)
                continue
            match = re.match(r'.*complete requests:\s+(\d+).*', line, re.I)
            if match:
                result_requests = match.group(1)
                continue
            match = re.match(r'.*total transferred:\s+(\d+).*', line, re.I)
            if match:
                result_transferred_bytes = match.group(1)
                continue
            match = re.match(r'.*requests per second:\s+(\d+(\.\d+)?).*', line, re.I)
            if match:
                result_requests_per_second = match.group(1)
                continue
            match = re.match(r'.*time per request:\s+(\d+(\.\d+)?).*\(mean\).*', line, re.I)
            if match:
                result_time_per_request = match.group(1)
                continue
            match = re.match(r'.*time per request:\s+(\d+(\.\d+)?).*concurrent.*', line, re.I)
            if match:
                result_time_per_request_concurrent = match.group(1)
                continue
            match = re.match(r'.*transfer rate:\s+(\d+(\.\d+)?).*', line, re.I)
            if match:
                result_transfer_rate = match.group(1)
                continue

        if log_header:
            helpers.file_write_append_once(
                    output_log,
                    "#concurrent  #requests  exec_time(sec)  transferred(bytes)  requests/sec  time/request(ms)  concurrent-time/request(ms)  transfer-rate(Kb/sec)\n")
        helpers.file_write_append_once(
                    output_log,
                    "%11s %10s %15s  %18s  %12s  %16s  %16s  %24s\n"
                    % (result_concurrent,
                       result_requests,
                       result_exec_time,
                       result_transferred_bytes,
                       result_requests_per_second,
                       result_time_per_request,
                       result_time_per_request_concurrent,
                       result_transfer_rate,
                       )
                    )
        if log_trailer:
            helpers.log("Benchmark data logged to %s" % output_log)
            helpers.log("Log results:\n%s"
                        % helpers.file_read_once(output_log))

    def test_pdu(self):
        t = test.Test()
        pdu = t.params(node='s1', key='pdu')
        helpers.log("pdu: %s" % pdu)
        p = t.node_spawn(ip=pdu["ip"], device_type='pdu', protocol='telnet')
        p.cli('about')
        p.cli('olStatus 20')
        p.close()

    def test_common_params(self):
        t = test.Test()
        helpers.log("**** params:\n%s" % helpers.prettify(t.params()))

    def test_check_version(self):
        status = BsnCommon().check_version('master', '2.1.0')
        helpers.log("version check against 2.1.0: %s" % status)

    def rest_bigtap_delivery_group(self, node):
        t = test.Test()
        c = t.controller(node)
        res = c.rest.put('/api/v1/data/controller/applications/bigtap/view[name="admin-view"]/policy[name="P1"]/delivery-group[name="demo-eth3"]',
                          data={"name": "demo-eth3"}
                         )
        return res

