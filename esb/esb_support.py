from celery import current_task
import gzip
import autobot.helpers as helpers
import autobot.test as test


def task_execute(params, task_func):
    """
    A wrapper function which executes the task specified in task_func
    (callback). It returns the content of the task and also copies the task
    log to the BigRobot log archiver.

    The task log file is saved at http://qa-tools1.qa.bigswitch.com/bigrobot_esb/<task_id>.log.gz
    where tag_id is the UUID assigned to the task. E.g.,
    http://qa-tools1.qa.bigswitch.com/bigrobot_esb/09190f81-f482-445f-a06f-4422a3da6d5f.log.gz
    """
    task_id = current_task.request.id
    log_file = helpers.bigrobot_log_path_exec_instance() + '/' + task_id + '.log'
    helpers.autobot_log_send_to_file(log_file)
    helpers.log("Starting task %s." % task_id)
    helpers.log("Creating log file '%s'." % log_file)

    t = test.Test(esb=True, params=params)

    content = task_func()

    t.node_disconnect()

    helpers.log("Ending task %s." % task_id)
    helpers.log("Closing log file '%s'." % log_file)
    helpers.autobot_log_send_to_file(log_file, close=True)

    log_file_gzipped = log_file + ".gz"
    f_in = open(log_file, 'rb')
    f_out = gzip.open(log_file_gzipped, 'wb')
    f_out.writelines(f_in)
    f_out.close()
    f_in.close()

    server = helpers.bigrobot_log_archiver()
    dest_path = '/var/www/bigrobot_esb'
    user = 'root'
    password = 'bsn'
    helpers.scp_put(server, log_file_gzipped, dest_path, user, password)
    helpers.file_remove(log_file_gzipped)

    return content

