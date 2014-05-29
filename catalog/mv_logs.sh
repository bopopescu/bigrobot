#!/bin/sh

ts=`date "+%Y-%m-%d_%H%M%S"`
dest=data.$ts

mkdir $dest
mv -f bigrobot_logs doit.sh_output*.log dryrun* test_*.json total*files $dest
