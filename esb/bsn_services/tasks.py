from __future__ import print_function
import subprocess


from .celery import app
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
