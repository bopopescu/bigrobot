from __future__ import print_function
from celery.contrib.methods import task_method
from .celery_app import app
import autobot.helpers as helpers
import autobot.test as test

from keywords.Host import Host


class BsnCommands(object):
    @app.task(filter=task_method)
    def add(self, x, y):
        """
        A very simple task which adds 2 numbers.
        """
        return x + y

    @app.task(filter=task_method)
    def cli_show_user(self, params, node):
        t = test.Test(esb=True, params=params)
        n = t.node(node)
        content = n.cli("show user")['content']
        t.node_disconnect()
        return content

    @app.task(filter=task_method)
    def cli_show_running_config(self, params, node):
        t = test.Test(esb=True, params=params)
        n = t.node(node)
        content = n.enable("show running-config")['content']
        t.node_disconnect()
        return content

    @app.task(filter=task_method)
    def cli_show_version(self, params, node):
        t = test.Test(esb=True, params=params)
        n = t.node(node)
        content = n.cli("show version")['content']
        t.node_disconnect()
        return content

    @app.task(filter=task_method)
    def bash_ping_regression_server(self, params, node):
        t = test.Test(esb=True, params=params)
        n = t.node(node)
        host = Host()
        loss_pct = host.bash_ping(node=node,
                                  dest_ip='regress.qa.bigswitch.com')
        t.node_disconnect()
        return loss_pct
