#!/bin/sh

ts=`date "+%Y-%m-%d_%H%M%S"`
dest=data.$ts

mkdir $dest
mv -f bigrobot_logs doit.sh_output*.log get_stats_dryrun.sh_output* get_stats_regression.sh_output* dryrun* test_*.json total*files $dest
