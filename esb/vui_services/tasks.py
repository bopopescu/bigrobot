from __future__ import print_function
from celery.contrib.methods import task_method
from .celery_app import app
import autobot.helpers as helpers
import autobot.test as test
from esb_support import task_execute

from keywords.Host import Host


class BsnCommands(object):
    @app.task(filter=task_method)
    def cli_show_user(self, params, node):
        def run():
            helpers.log("Task: cli_show_user")
            t = test.Test()
            n = t.node(node)
            content = n.cli("show user")['content']
            10 / 0
            return content
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
