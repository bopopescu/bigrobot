from __future__ import print_function
from celery.contrib.methods import task_method
from .celery_app import app
import autobot.helpers as helpers
import autobot.test as test
from esb_support import task_execute

from keywords.Host import Host
from keywords.AppController import AppController
from keywords.SwitchLight import SwitchLight


class BigtapCommands(object):
    @app.task(filter=task_method)
    def cli_show_user(self, params, node):
        def run():
            helpers.log("Task: cli_show_user")
            t = test.Test()
            n = t.node(node)
            content = n.cli("show user")['content']
            return content
        return task_execute(params, run)

    @app.task(filter=task_method)
    def ha_failover(self, params):
        def run():
            helpers.log("Task: perform ha fail over")
            test.Test()
            app = AppController()
            result = app.rest_execute_ha_failover()
            return result
        return task_execute(params, run)


    @app.task(filter=task_method)
    def restart_switch(self, params, **kwargs):
        def run():
            helpers.log("Task: Restarting a switch")
            test.Test()
            sl = SwitchLight()
            result = sl.cli_restart_switch(**kwargs)
            return result
        return task_execute(params, run)

    @app.task(filter=task_method)
    def cli_copy_upgrade_pkg(self, params, **kwargs):
        def run():
            helpers.log("Task: cli_copy_upgrade_pkg")
            test.Test()
            t5 = T5Platform()
            result = t5.copy_pkg_from_server(**kwargs)
            return result
        return task_execute(params, run)

    @app.task(filter=task_method)
    def execute_ha_failover(self, params, node):
        def run():
            '''
            Execute HA failover from main controller
            '''
            try:
                t = test.Test()
            except:
                return False
            else:
                c = t.controller('main')
                try:
                    url1 = '/rest/v1/system/ha/failback'
                    c.rest.put(url1, {})
                except:
                    helpers.test_log(c.rest.error())
                    return False
                else:
                    helpers.test_log(c.rest.content_json())
                    return True
        return task_execute(params, run)

    @app.task(filter=task_method)
    def cli_show_running_config(self, params, node):
        def run():
            helpers.log("Task: cli_show_running")
            t = test.Test()
            n = t.node(node)
            content = n.enable("show running-config")['content']
            return content
        return task_execute(params, run)

    @app.task(filter=task_method)
    def cli_show_version(self, params, node):
        def run():
            helpers.log("Task: cli_show_version")
            t = test.Test()
            n = t.node(node)
            content = n.cli("show version")['content']
            return content
        return task_execute(params, run)

    @app.task(filter=task_method)
    def bash_ping_regression_server(self, params, node):
        def run():
            helpers.log("Task: bash_ping_regression_server")
            t = test.Test()
            _ = t.node(node)
            host = Host()
            loss_pct = host.bash_ping(node=node,
                                      dest_ip='regress.qa.bigswitch.com')
            return loss_pct
        return task_execute(params, run)
