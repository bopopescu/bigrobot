#!/bin/sh -x

if [ ! -x ../bin/gobot ]; then
    echo "Error: This script must be executed in the bigrobot/catalog/ directory."
    exit 1
fi


build=0
clean_build=0
cleanup=0
dest_p=/tmp/autobot
version=1.0.0

usage() {
    if [ $# -ne 0 ]; then
        echo `basename $0`: ERROR: $* 1>&2
    fi
    echo "Usage: `basename $0` [-build] [-cleanup]"
    exit 1
}

create_version_file() {
    echo $version > $1
}

create_dummy_common_config() {
    file=$1
    cat <<EOF > $file
controller_user:     admin
controller_password: admin123
switch_user:         admin
switch_password:     admin123
host_user:           user123
host_password:       password123
EOF
}

build() {
    mkdir -p /tmp/autobot/{autobot,configs,keywords,test,vendors}
    
    create_version_file ${dest_p}/version.txt
    create_dummy_common_config ${dest_p}/configs/common.yaml
    (cd ../autobot; cp -rp helpers __init__.py bsn_restclient.py devconf.py \
                           ha_wrappers.py node.py nose_support.py restclient.py \
                           setup_env.py test.py utils.py version.py \
                           monitor.py ${dest_p}/autobot \
                  )
    (cd ../keywords; cp __init__.py BsnCommon.py Host.py T5Torture.py ${dest_p}/keywords)
    (cd ../test; rm -f *.pyc; cp * ${dest_p}/test) 
    (cd ../vendors; cp -rp __init__.py exscript* ${dest_p}/vendors)
    
    # IXIA libraries
    #mkdir -p /tmp/autobot/modules
    #(cd ../modules; cp -rp * ${dest_p}/modules)
    #(cd ../vendors; cp -rp Ixia ${dest_p}/vendors)
                
    package_base_name=`basename $dest_p`
    dest_package=autobot-${version}
    (cd $dest_p; cd ..; tar zcvf ${dest_package}.tgz $package_base_name)
    echo "Created package ${dest_package}.tgz"
}

cleanup() {
    rm -rf $dest_p
}


if [ $# -eq 0 ]; then
    usage
fi

while :
do
    case "$1" in
    -build) build=1;;
    -clean_build) clean_build=1;;
    -cleanup) cleanup=1;;
    --) shift; break;;
    -h) usage;;
    -help) usage;;
    -*) usage "bad argument $1";;
    *) break;;
    esac
    shift
done


if [ $clean_build -eq 1 ]; then
    echo "Clean build for $dest_p..."
    cleanup
    build
else
    if [ $cleanup -eq 1 ]; then
        echo "Cleaning up $dest_p..."
        cleanup
    fi

    if [ $build -eq 1 ]; then
        echo "Building..."
        build
    fi
fi
