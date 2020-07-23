#!/usr/bin/env python
import os
import sys
import re
import argparse

# Determine BigRobot path(s) based on this executable (which resides in
# the bin/ directory.
bigrobot_path = os.path.dirname(__file__) + '/..'
exscript_path = bigrobot_path + '/vendors/exscript/src'

sys.path.insert(0, bigrobot_path)
sys.path.insert(1, exscript_path)

import autobot.helpers as helpers

helpers.set_env('IS_GOBOT', 'False')
helpers.set_env('AUTOBOT_LOG', './myrobot.log')


def prog_args():
    descr = """\
Generate the BUILD_NAME string based on a BCF/BigTap version string found in
a file (see --version-file) or a string (see --version-str). The version string
needs to have the following format:

    Big Tap Controller 4.1.1  (2014.11.13.1922-b.bsc.corsair-4.1.1beta
    Big Cloud Fabric Appliance 3.0.0-main01-SNAPSHOT (bcf_main #4201)
    Big Cloud Fabric Appliance 2.0.0-main01-SNAPSHOT (ihplus_bcf #515)

Returns the BUILD_NAME as followed:

    corsair411_bigtap_10G-1922
    main_bcf_10G-4201
"""
    parser = argparse.ArgumentParser(
                        prog='build_name_gen',
                        formatter_class=argparse.RawDescriptionHelpFormatter,
                        description=descr)
    parser.add_argument('--version-file',
                        default='/var/tmp/ver.txt',
                        help=("Version file"))
    parser.add_argument('--version-str',
                        help=("Version string"))
    parser.add_argument('--additional-version-descr',
                        help=("An additional version description to add to BUILD_NAME"))
    parser.add_argument('--testbed',
                        required=True,
                        help=("Testbed name, e.g., common, Dell, Accton, Quanta, 10G, 40G, virtual, etc."))
    _args = parser.parse_args()

    if _args.testbed == None:
        helpers.error_exit("Env BIGROBOT_PARAMS_INPUT is not found.")

    return _args


def get_version_string(args):
    version_str = args.version_str
    if version_str == None:
        if helpers.file_not_exists(args.version_file):
            helpers.error_exit("Version file '%s' is not found."
                               % args.version_file)
        version_str = helpers.file_read_once(args.version_file).strip()

    version = None
    release = None
    build_name = None
    testbed = args.testbed


    ##########################################################################
    # Match BigTap build string
    #   - The match logic is as defined in bigrobot/configs/catalog.yaml
    ##########################################################################
    re_bigtap = r'.*Big Tap Controller (\d+\.\d+\.\d+).+\d\d\d\d\.\d\d\.\d\d\.(\d+).+'
    match = re.match(re_bigtap, version_str)
    if match:
        version = match.group(1)
        build_id = match.group(2)

        if version in ['4.0.0', '4.0.1', '4.0.2', '4.1.0']:
            release = 'corsair400'
        elif version in ['4.1.1']:
            release = 'corsair411'
        elif version in ['4.5.0']:
            release = 'corsair450'
        else:
            helpers.error_exit("Invalid BigTap version '%s' in version string '%s'."
                               % (version, version_str))

        build_name = "%s_%s_%s-%s" % (release, "bigtap", testbed, build_id)

        if args.additional_version_descr != None:
            build_name = "%s_%s" % (build_name, args.additional_version_descr)

        return build_name

    ##########################################################################
    # Match BCF build string
    #   - The match logic is as defined in bigrobot/configs/catalog.yaml
    ##########################################################################
    re_bcf = r'.*Big Cloud Fabric Appliance \d+\.\d+\.\d+.+\((\w+)_(\w+) #(\d+)\).*'
    match = re.match(re_bcf, version_str)
    if match:
        if match.group(1) == 'bcf':
            release = match.group(2)
        else:
            release = match.group(1)

        build_id = match.group(3)

        if not release in ['ih', 'ihplus', 'jf', 'main']:
            helpers.error_exit("Invalid BCF version '%s' in version string '%s'."
                               % (version, version_str))

        build_name = "%s_%s_%s-%s" % (release, "bcf", testbed, build_id)

        if args.additional_version_descr != None:
            build_name = "%s_%s" % (build_name, args.additional_version_descr)

        return build_name

    helpers.error_exit("Invalid version string: '%s'." % version_str);


if __name__ == '__main__':
    args = prog_args()
    print get_version_string(args)

