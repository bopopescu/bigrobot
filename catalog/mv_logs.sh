#!/bin/sh

ts=`date "+%Y-%m-%d_%H%M%S"`
dest=data.$ts

mkdir $dest
mv -f raw_data.* debug.log dev_commands.log syslog.txt report.html output.xml log.html bigrobot_listener.log myrobot.log $dest

