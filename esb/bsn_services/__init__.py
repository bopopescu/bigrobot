import os
import sys
import robot


bigrobot_path = os.path.dirname(__file__) + '/../..'
exscript_path = bigrobot_path + '/vendors/exscript/src'
sys.path.insert(0, bigrobot_path)
sys.path.insert(1, exscript_path)

import autobot.helpers as helpers
helpers.bigrobot_path(bigrobot_path)
helpers.bigrobot_log_path('/tmp/bigrobot_esb_log')
helpers.bigrobot_log_path_exec_instance(
            helpers.bigrobot_log_path() +
            "/" + os.path.dirname(__file__).split('/')[-1])
