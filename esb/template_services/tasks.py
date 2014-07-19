from __future__ import print_function
from celery.contrib.methods import task_method
from .celery_app import app
import autobot.helpers as helpers
import autobot.test as test

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
        return content

    @app.task(filter=task_method)
    def cli_show_running_config(self, params, node):
        t = test.Test(esb=True, params=params)
        n = t.node(node)
        content = n.enable("show running-config")['content']
        return content

    @app.task(filter=task_method)
    def cli_show_version(self, params, node):
        t = test.Test(esb=True, params=params)
        n = t.node(node)
        content = n.cli("show version")['content']
        return content
