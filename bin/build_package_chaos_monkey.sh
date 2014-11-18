#!/bin/sh
# This script is used to create a tarball of all the source/configs required
# by the Autobot framework (for "Chaos Monkey" Opp9 support). By default, the
# package will be saved to /tmp/autobot-x.y.z.tgz.
#
# It is required that you change the version string before rolling a new
# tarball for production.
#

if [ ! -x ../bin/gobot ]; then
    echo "Error: This script must be executed in the bigrobot/catalog/ directory."
    exit 1
fi


dest_p=/tmp/autobot
version=1.0.0
build=0
clean_build=0
cleanup=0

package_basename=`basename $dest_p`
package_dirname=`dirname $dest_p`
dest_tarball=autobot-${version}.tgz


usage() {
    if [ $# -ne 0 ]; then
        echo `basename $0`: ERROR: $* 1>&2
    fi
    echo "Usage: `basename $0` [-build] [-cleanup] [-clean_build]"
    echo ''
    echo '  -build       : build the tarball while leaving previous build artifacts'
    echo '                 intact (overwrite if needed)'
    echo '  -cleanup     : clean up build artifacts' 
    echo '  -clean_build : clean build artifacts first, then build' 
    echo ''
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
    mkdir -p /tmp/autobot/{autobot,configs,keywords,test,vendors,modules}
    
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
    (cd ../modules; cp -rp * ${dest_p}/modules)
    (cd ../vendors; cp -rp Ixia ${dest_p}/vendors)
                
    (cd $dest_p; cd ..; tar zcvf ${dest_tarball} $package_basename)
    echo "Created tarball ${package_dirname}/${dest_tarball}"
}

cleanup() {
    rm -rf $dest_p $dest_tarball
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
