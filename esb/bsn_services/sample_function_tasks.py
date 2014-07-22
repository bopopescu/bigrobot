"""
Usage:

    def test_esb(self, node):
        from bsn_services import sample_function_tasks as tasks

        t = test.Test()
        helpers.log("***** params: %s" % helpers.prettify(t.params()))

        results = []
        result_dict = {}

        results.append(tasks.cli_show_running_config.delay(node, t.params()))
        task_id = results[-1].task_id
        result_dict[task_id] = { "node": node, "action": "show running-config" }

        results.append(tasks.cli_show_version.delay(node, t.params()))
        task_id = results[-1].task_id
        result_dict[task_id] = { "node": node, "action": "show version" }

        results.append(tasks.cli_show_user.delay(node, t.params()))
        task_id = results[-1].task_id
        result_dict[task_id] = { "node": node, "action": "show user" }

        is_pending = True
        while is_pending:
            is_pending = False
            helpers.sleep(1)
            for res in results:
                if res.ready() == False:
                    helpers.log("****** task_id(%s) is ready" % res.task_id)
                else:
                    helpers.log("****** task_id(%s) is NOT ready" % res.task_id)
                    is_pending = True

        for res in results:
            task_id = res.task_id
            output = res.get()
            result_dict[task_id]["result"] = output

        helpers.log("***** result_dict:\n%s" % helpers.prettify(result_dict))

        return True

"""

from __future__ import print_function
import subprocess


from .celery_app import app
import autobot.helpers as helpers
import autobot.test as test


TOTAL = 0

def run_cmd(cmd):
    print("Executing '%s'" % cmd)
    return subprocess.call(cmd, shell=True)


@app.task
def add(x, y):
    global TOTAL
    result = x + y
    TOTAL += result
    print("*** TOTAL: %s" % TOTAL)

    print("*** helpers.bigrobot_path: %s" % helpers.bigrobot_path())
    print("*** helpers.bigrobot_log_path: %s" % helpers.bigrobot_log_path())
    print("*** helpers.bigrobot_log_path_exec_instance: %s"
          % helpers.bigrobot_log_path_exec_instance())

    return result


@app.task
def dict_to_json(python_dict):
    return helpers.to_json(python_dict)


@app.task
def json_to_dict(json_str):
    return helpers.from_json(json_str)


@app.task
def cli_show_running_config(node, params):
    helpers.bigrobot_esb('True')
    helpers.bigrobot_topology_for_esb(params)
    t = test.Test()
    n = t.node(node)
    content = n.enable("show running-config")['content']
    return content


@app.task
def cli_show_version(node, params):
    helpers.bigrobot_esb('True')
    helpers.bigrobot_topology_for_esb(params)
    t = test.Test()
    n = t.node(node)
    content = n.cli("show version")['content']
    del t
    return content


def run_sub_task(node):
    t = test.Test()
    helpers.summary_log("**** Sub_task")
    n = t.node(node)
    n.bash('uname -a')


@app.task
def cli_show_user(node, params):
    helpers.bigrobot_esb('True')
    helpers.bigrobot_topology_for_esb(params)
    t = test.Test(reset_instance=True)
    n = t.node(node)

    # helpers.summary_log("*** I am here")
    # n = t.node_connect(node)
    content = n.cli("show user")['content']
    run_sub_task(node)
    return content
