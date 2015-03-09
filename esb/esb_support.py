from celery import current_task
import gzip
import autobot.helpers as helpers
import autobot.test as test


def _archive_logs(task_id):
    helpers.log("Archiving logs for task %s before ending task." % task_id)

    server = helpers.bigrobot_log_archiver()
    dest_path = '/var/www/bigrobot_esb'
    user = 'root'
    password = 'bsn'
    helpers.scp_put(server, helpers.bigrobot_log_path_exec_instance(), dest_path, user, password)

def task_execute(params, task_func):
    """
    A wrapper function which executes the task specified in task_func
    (callback). It returns the content of the task and also copies the task
    log to the BigRobot log archiver.

    The task log file is saved at http://qa-tools1.qa.bigswitch.com/bigrobot_esb/<suite>_<task_id>/
    where tag_id is the UUID assigned to the task. E.g.,
    http://qa-tools1.qa.bigswitch.com/bigrobot_esb/vui_services_cf298f75-533b-4333-96a9-24406ed53fd1/
    """
    task_id = current_task.request.id
    helpers.log("Starting task %s." % task_id)

    # Redirect logs to a separate log directory for this task.
    suite_log_path = helpers.bigrobot_log_path() + '/' + task_id
    helpers.bigrobot_log_path_exec_instance(suite_log_path)
    helpers.set_env('AUTOBOT_LOG',
                    helpers.bigrobot_log_path_exec_instance() +
                    "/bigrobot_autobot.log")
    helpers.log("BIGROBOT_LOG_PATH_EXEC_INSTANCE: %s"
                % helpers.bigrobot_log_path_exec_instance())

    try:
        # esb=True is the equivalent of setting helpers.bigrobot_esb('True').
        t = test.Test(esb=True, params=params)

        content = task_func()

        t.node_disconnect()
    except:
        helpers.log("Error while executing task %s!!! Archiving logs before re-raising exception."
                    % task_id)
        helpers.log("Ending task %s on exception." % task_id)
        helpers.log(helpers.exception_info())
        _archive_logs(task_id)
        raise
    else:
        helpers.log("Ending task %s on success. Archiving logs." % task_id)
        _archive_logs(task_id)
        return content

