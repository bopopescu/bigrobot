#!/usr/bin/env python

from __future__ import absolute_import
import os
import sys
import robot


bigrobot_path = os.path.dirname(__file__) + '/../..'
exscript_path = bigrobot_path + '/vendors/exscript/src'
esb_path = bigrobot_path + '/esb'
sys.path.insert(0, bigrobot_path)
sys.path.insert(1, exscript_path)
sys.path.insert(2, esb_path)


from template_services import tasks
import autobot.helpers as helpers


if __name__ == "__main__":
    task = tasks.BsnCommands()

    res1 = task.add.delay(1, 5)

    # res1 = task.addition(1, 5)
    # print "*** res1: %s" % res1
    # sys.exit(1)

    # helpers.sleep(0.2)
    # while res1.ready() == False:
    #    print("Sleeping for 1 sec")
    #    helpers.sleep(1)

    helpers.sleep(1)

    output = res1.get()
    print("** task_id: %s" % res1.task_id)
    print("** output: %s" % output)

