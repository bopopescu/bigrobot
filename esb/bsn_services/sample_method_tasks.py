from __future__ import print_function
from celery.contrib.methods import task_method
from .celery_app import app
import autobot.helpers as helpers
import autobot.test as test

class BsnCommands(object):
    @app.task(filter=task_method)
    def add(self, x, y):
        return x + y

    @app.task(filter=task_method)
    def cli_show_user(self, node, params):
        helpers.bigrobot_esb('True')
        helpers.bigrobot_topology_for_esb(params)
        t = test.Test(reset_instance=True)

        n = t.node(node)
        content = n.cli("show user")['content']
        return content
