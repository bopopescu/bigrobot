#!/bin/sh -x
# This script is designed to run as a cronjob on the Jenkins/Regression server
# to remove old builds which have exceeded the rentention period (default is
# 30 days) unless the build directory contains the file KEEP_FOREVER.txt.

jenkins_job=BCF_Image_Archival
retention_days=30

p=/var/lib/jenkins/jobs/${jenkins_job}/workspace/bcf_builds
p_deleted=$p/.deleted
log="/tmp/`basename $0`.$$"
pwd=`pwd`
cd $p

if [ ! -d $p_deleted ]; then
    mkdir $p_deleted
fi
touch $p_deleted


for dir in `find . -maxdepth 1 -type d -mtime +$retention_days`; do
    if [ -f "$dir/KEEP_FOREVER.txt" ]; then
        echo "Keeping $dir"
    else
        ls_out=`ls -lad $dir`

        echo "Moving $dir to $p_deleted ($ls_out)" | tee -a $log
        mv $dir $p_deleted

        # If we are confident that everything works correctly, we
        # can comment out the mv statement above and enable the rm statement
        # below.

        #echo "Removing $dir ($ls_out)" | tee -a $log
        #rm -rf $dir
    fi
done

cd $pwd

if [ -f $log ]; then
    ./send_mail.py \
        --sender vui.le@bigswitch.com \
        --receiver bigrobot_stats_collection@bigswitch.com \
        --subject "Regression image cleanup ($jenkins_job)" \
        --message "Removing old $jenkins_job images..." \
        --infile $log
fi

rm -f $log

exit 0
