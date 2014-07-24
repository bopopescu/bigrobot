import os
import sys
import robot


bigrobot_path = os.path.dirname(__file__) + '/../..'
sys.path.insert(0, bigrobot_path + '/vendors/exscript/src')
sys.path.insert(0, bigrobot_path + '/esb')
sys.path.insert(0, bigrobot_path)

import autobot.helpers as helpers
helpers.set_env('IS_GOBOT', 'False')
helpers.bigrobot_path(bigrobot_path)

helpers.bigrobot_log_path('/tmp/bigrobot_esb_log')
helpers.bigrobot_log_path_exec_instance(
                          helpers.bigrobot_log_path() +
                          "/" + os.path.dirname(__file__).split('/')[-1])

helpers.set_env('AUTOBOT_LOG', helpers.bigrobot_log_path_exec_instance() + "/bigrobot_autobot.log")
helpers.log("testing 1 2 3 (to autobot log #1)")

helpers.set_env('AUTOBOT_LOG', helpers.bigrobot_log_path_exec_instance() + "/bigrobot_autobot2.log")
helpers.log("testing 1 2 3 (to autobot log #2)")
