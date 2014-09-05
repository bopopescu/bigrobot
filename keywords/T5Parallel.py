import re
import autobot.helpers as helpers
import autobot.test as test

from mingtao_services import tasks as tasks


class T5Parallel(object):

    def __init__(self):
        pass

    def task_finish_check_parallel(self, results, result_dict,timer=10, timeout=600):
        '''
        task_finish_check_parallel
        Input:  
        Output:
        Author: Mingtao
        '''
        helpers.log("***Entering==> task_finish_check_parallel   \n")
        is_pending = True
        iteration = 0
        while is_pending:
            is_pending = False
            iteration += 1
            helpers.sleep(int(timer))
            helpers.log("USR INFO:  result is %s" % results)

            for res in results:
                task_id = res.task_id
                helpers.log_task_output(task_id)
                action = result_dict[task_id]["node"] + ' ' + result_dict[task_id]["action"]
                if res.ready() == True:
                    helpers.log("****** %d.READY     - task_id(%s)['%s']"
                                % (iteration, res.task_id, action))
                else:
                    helpers.log("****** %d.NOT-READY - task_id(%s)['%s']"
                                % (iteration, res.task_id, action))
                    is_pending = True
                    
            if iteration >= int(timeout)/int(timer):
                helpers.test_failure("USR ERROR: the parallel execution did not finish with %s seconds" %timeout)
        helpers.log("*** Parallel tasks completed")

        #
        # Check task output
        #
        for res in results:
            task_id = res.task_id
            helpers.log_task_output(task_id)
            output = res.get()
            result_dict[task_id]["result"] = output
        helpers.log("***** result_dict:\n%s" % helpers.prettify(result_dict))
        return True



    def upgrade_copy_image_HA_parallel(self, nodes, image,finish='yes'):
        '''
        upgrade_copy_image_HA_parallel
        Input:  
        Output:
        Author: Mingtao
        '''

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
            self.task_finish_check_parallel(results, result_dict)
            helpers.log("***Exiting==> upgrade_copy_image_HA_parallel,  all nodes done  \n")
            return True
        else:
            helpers.log("***Exiting==> upgrade_copy_image_HA_parallel NOT checking task finish status\n")
            return { 'results': results, 'result_dict': result_dict }
            

    def upgrade_statge_image_HA_parallel(self, nodes,finish='yes'):
        '''
        upgrade_statge_image_HA_parallel
        Input:  
        Output:
        Author: Mingtao
        '''

        helpers.log("***Entering==> upgrade_statge_image_HA_parallel   \n")
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
            self.task_finish_check_parallel(results, result_dict)
            helpers.log("***Exiting==> upgrade_statge_image_HA_parallel,  all nodes done  \n")
            return  True
        else:
            helpers.log("***Exiting==> upgrade_statge_image_HA_parallel  NOT checking task finish status \n")
            return { 'results': results, 'result_dict': result_dict }
 
  
    def upgrade_launch_image_HA_parallel(self, nodes, option='',finish='yes'):
        '''
        upgrade_launch_image_HA_parallel
        Input:    
        Output:
        Author: Mingtao
        '''

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
            self.task_finish_check_parallel(results, result_dict, timer=30, timeout=900)
            helpers.log("***Exiting==> upgrade_launch_image_HA_parallel,  all node done  \n")
            return True
        else: 
            helpers.log("***Exiting==> upgrade_copy_image_HA_parallel NOT checking task finish status  \n")
            return { 'results': results, 'result_dict': result_dict }
