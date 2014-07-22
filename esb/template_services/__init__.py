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

