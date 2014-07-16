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
    print("*** node: %s" % node)
    print("*** params: %s" % helpers.prettify(params))

    t = test.Test()
    n = t.node(node)
    content = n.enable("show running-configuration")['content']
    return content
