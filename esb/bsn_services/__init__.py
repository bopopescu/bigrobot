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
helpers.get_env('AUTOBOT_LOG')

# helpers.summary_log("BIGROBOT_LOG_PATH: %s"
#                    % helpers.bigrobot_log_path('/tmp/bigrobot_esb_log'))
# helpers.summary_log("BIGROBOT_LOG_PATH_EXEC_INSTANCE: %s"
#                    % helpers.bigrobot_log_path_exec_instance(
#                          helpers.bigrobot_log_path() +
#                          "/" + os.path.dirname(__file__).split('/')[-1]))
