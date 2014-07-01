#!/bin/sh

ts=`date "+%Y-%m-%d_%H%M%S"`
dest=data.$ts

mkdir $dest
mv -f raw_data.* myrobot.log $dest

