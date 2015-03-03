import re
import autobot.helpers as helpers
import autobot.test as test

class T5Parallel(object):

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
                else:
                    helpers.log("****** %d.NOT-READY - task_id(%s)['%s']"
                                % (iteration, res.task_id, action))
                    is_pending = True

            if iteration >= int(timeout) / int(timer):
#                helpers.test_failure("USR ERROR: the parallel execution did not finish with %s seconds" %timeout)
                helpers.log("USR ERROR: the parallel execution did not finish with %s seconds" % timeout)
                return False

        helpers.log("*** Parallel tasks completed ")

        #
        # Check task output
        #
        for res in results:
            task_id = res.task_id
            helpers.log_task_output(task_id)
            output = res.get()
            helpers.log("USER INFO:  for task %s , result is  %s  " % (task_id, output))
            result_dict[task_id]["result"] = output
            if output is False:
                flag = False
                break
        helpers.log("***** result_dict:\n%s" % helpers.prettify(result_dict))
        helpers.log("USER INFO ***** result flag is: %s" % flag)
        return flag



    def upgrade_copy_image_HA_parallel(self, nodes, image, finish='yes'):
        '''
        upgrade_copy_image_HA_parallel
        Input:
        Output:
        Author: Mingtao
        '''
        from bsn_common_services import tasks as tasks
        helpers.log("***Entering==> upgrade_copy_image_HA_parallel   \n")
        t = test.Test()

        results = []
        result_dict = {}
        task = tasks.UpgradeCommands()
        #
        # Parallel execution happens below
        #
        for node in nodes:
            res1 = task.cli_copy_upgrade_pkg.delay(t.params(), src=image, node=node)
            results.append(res1)
            task_id = results[-1].task_id
            result_dict[task_id] = { "node": node, "action": "upgrade_copy" }

        # Check task status - are we done yet?
        #
        if finish == 'yes':
            result = self.task_finish_check_parallel(results, result_dict)
            helpers.log("***Exiting==> upgrade_copy_image_HA_parallel,  all nodes done  \n")
            return result
        else:
            helpers.log("***Exiting==> upgrade_copy_image_HA_parallel NOT checking task finish status\n")
            return { 'results': results, 'result_dict': result_dict }


    def upgrade_statge_image_HA_parallel(self, nodes, finish='yes'):
        '''
        upgrade_statge_image_HA_parallel
        Input:
        Output:
        Author: Mingtao
        '''
        from bsn_common_services import tasks as tasks
        helpers.log("***Entering==> upgrade_statge_image_HA_parallel \n")
        t = test.Test()

        results = []
        result_dict = {}
        task = tasks.UpgradeCommands()
        #
        # Parallel execution happens below
        #
        for node in nodes:
            res1 = task.cli_stage_upgrade_pkg.delay(t.params(), node=node)
            results.append(res1)
            task_id = results[-1].task_id
            result_dict[task_id] = { "node": node, "action": "upgrade_statge" }

        # Check task status - are we done yet?
        if finish == 'yes':
            result = self.task_finish_check_parallel(results, result_dict)
            helpers.log("***Exiting==> upgrade_statge_image_HA_parallel,  all nodes done  \n")
            return  result
        else:
            helpers.log("***Exiting==> upgrade_statge_image_HA_parallel  NOT checking task finish status \n")
            return { 'results': results, 'result_dict': result_dict }


    def upgrade_launch_image_HA_parallel(self, nodes, option='', finish='yes'):
        '''
        upgrade_launch_image_HA_parallel
        Input:
        Output:
        Author: Mingtao
        '''
        from bsn_common_services import tasks as tasks
        helpers.log("***Entering==> upgrade_launch_image_HA_parallel   \n")
        t = test.Test()

        results = []
        result_dict = {}
        task = tasks.UpgradeCommands()
        #
        # Parallel execution happens below
        #
        for node in nodes:
            res1 = task.cli_launch_upgrade_pkg.delay(t.params(), node=node, option=option)

            results.append(res1)
            task_id = results[-1].task_id
            result_dict[task_id] = { "node": node, "action": "upgrade_launch" }

        # Check task status - are we done yet?
        if finish == 'yes':
            result = self.task_finish_check_parallel(results, result_dict, timer=30, timeout=900)
            helpers.log("***Exiting==> upgrade_launch_image_HA_parallel,  all node done  \n")
            return result
        elif finish == 'one':
            result = self.task_one_finish_check_parallel(results, result_dict, timer=30, timeout=900)
            return { 'results': results, 'result_dict': result_dict }
        else:
            helpers.log("***Exiting==> upgrade_launch_image_HA_parallel NOT checking task finish status  \n")
            return { 'results': results, 'result_dict': result_dict }

    def task_one_finish_check_parallel(self, results, result_dict, timer=60, timeout=1200):
        '''
        task_one_finish_check_parallel, check to see at least one job finished
        Input:
        Output:
        Author: Mingtao
        '''
        helpers.log("***Entering==> task_one_finish_check_parallel   \n")
        is_pending = True
        iteration = 0
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
                    helpers.log("USR INFO: on job is ready")

                    helpers.log_task_output(task_id)

                    return True
                else:
                    helpers.log("****** %d.NOT-READY - task_id(%s)['%s']"
                                % (iteration, res.task_id, action))
                    is_pending = True

            if iteration >= int(timeout) / int(timer):
#                helpers.test_failure("USR ERROR: the parallel execution did not finish with %s seconds" %timeout)
                helpers.log("USR ERROR: the parallel execution did not finish with %s seconds" % timeout)
                return False



