import re
import autobot.helpers as helpers
import autobot.test as test

from sahaja_services import tasks as tasks


class BigTapParallel(object):

    def __init__(self):
        pass

    def task_finish_check_parallel(self, results, result_dict, timer=60, timeout=1500):
        '''
        task_finish_check_parallel
        Input:
        Output:
        Author: Mingtao
        '''
        helpers.log("***Entering==> task_finish_check_parallel   \n")
        is_pending = True
        iteration = 0
        flag = True
        while is_pending:
            is_pending = False
            iteration += 1
            helpers.sleep(int(timer))
            helpers.log("USR INFO:  result is %s" % results)

            for res in results:
                task_id = res.task_id
                action = result_dict[task_id]["node"] + ' ' + result_dict[task_id]["action"]
                if res.ready() == True:

                    helpers.log("****** %d.READY     - task_id(%s)['%s']"
                                % (iteration, res.task_id, action))
                    output = res.get()
                    helpers.log("Output after it is ready is %s" % output)
                else:
                    helpers.log("****** %d.NOT-READY - task_id(%s)['%s']"
                                % (iteration, res.task_id, action))
                    is_pending = True
                    output = res.get()
                    helpers.log("Output before it is ready is %s" % output)

            if iteration >= int(timeout) / int(timer):
#                helpers.test_failure("USR ERROR: the parallel execution did not finish with %s seconds" %timeout)
                helpers.log("USR ERROR: the parallel execution did not finish with %s seconds" % timeout)
                return False

        helpers.log("*** Parallel tasks completed ")

        #
        # Check task output
        #
        for res in results:
            helpers.log("Inside for res value is %s" % res)
            task_id = res.task_id
            helpers.log_task_output(task_id)
            helpers.log("Inside for res task id is %s" % task_id)
            output = res.get()
            helpers.log("USER INFO:  for task %s , result is  %s  " % (task_id, output))
            result_dict[task_id]["result"] = output
            if output is False:
                flag = False
        helpers.log("***** result_dict:\n%s" % helpers.prettify(result_dict))
        helpers.log("USER INFO ***** result flag is: %s" % flag)
        return flag



    def failover_switch_reboot_parallel(self, node, c1, save_config='yes', finish='yes'):
        '''
        upgrade_copy_image_HA_parallel
        Input:
        Output:
        Author: Mingtao
        '''

        helpers.log("***Entering==> ha Failover and rebooting a switch \n")
        t = test.Test()

        results = []
        result_dict = {}
        task = tasks.BigtapCommands()
        #
        # Parallel execution happens below
        #
        # Task 1
        res1 = task.ha_failover.delay(t.params())
        results.append(res1)
        task_id = results[-1].task_id
        result_dict[task_id] = {"node":c1, "action": "ha failover" }

        # Task 2
        res1 = task.restart_switch.delay(t.params(), node, save_config)
        results.append(res1)
        task_id = results[-1].task_id
        result_dict[task_id] = {"node": node, "action": "reboot switch" }

        # Check task status - are we done yet?
        #
        if finish == 'yes':
            result = self.task_finish_check_parallel(results, result_dict)
            helpers.log("***Exiting==> upgrade_copy_image_HA_parallel,  all nodes done  \n")
            return result
        else:
            helpers.log("***Exiting==> upgrade_copy_image_HA_parallel NOT checking task finish status\n")
            return { 'results': results, 'result_dict': result_dict }
