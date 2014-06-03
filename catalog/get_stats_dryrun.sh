#!/bin/sh

ts=`date "+%Y-%m-%d_%H%M%S"`
outfile=`basename $0`_output.$ts.log

./_doit.sh > $outfile 2>&1
