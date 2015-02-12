from __future__ import print_function
from celery.contrib.methods import task_method
from .celery_app import app
import autobot.helpers as helpers
import autobot.test as test
from esb_support import task_execute


from keywords.Host import Host
from keywords.T5Platform import T5Platform

class UpgradeCommands(object):
    @app.task(filter=task_method)
    def add(self, x, y):
        """
        A very simple task which adds 2 numbers.
        """
        helpers.log("I am here: x=%s y=%s" % (x, y))
        return x + y

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
    def cli_stage_upgrade_pkg(self, params, **kwargs):
        def run():
            test.Test()
            t5 = T5Platform()
            result = t5.cli_upgrade_stage(**kwargs)
            return result
        return task_execute(params, run)

    @app.task(filter=task_method)
    def cli_launch_upgrade_pkg(self, params, **kwargs):
        def run():
            test.Test()
            t5 = T5Platform()
            result = t5.cli_upgrade_launch_HA(**kwargs)
            return result
        return task_execute(params, run)
