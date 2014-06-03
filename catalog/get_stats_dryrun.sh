#!/bin/sh

ts=`date "+%Y-%m-%d_%H%M%S"`
outfile=doit.sh_output.$ts.log

./_doit.sh > $outfile 2>&1
