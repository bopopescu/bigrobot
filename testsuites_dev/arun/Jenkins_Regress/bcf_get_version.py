'''
Created on Mar 27, 2015
@author: mallinaarun
'''
'''
    Pring version string of the controller
'''
#!/usr/bin/env python
import paramiko
import re
import os
import sys
import re
import argparse
import yaml

def get_version_string(args):
    controller = paramiko.SSHClient()
    controller.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    controller_ip = args.controller_ip
    controller.connect(controller_ip, port=22, username='admin', password='adminadmin')
    stdin, stdout, stderr = controller.exec_command('show version  | grep "Release string"')
    output = stdout.readlines()
    if len(output) == 0:
        print "Version String Not Found !!!!!"
    else:
        return output[0].split(':')[1]
        controller.close()
    controller.close()


def prog_args():
    descr = """\
Display Version String for Regression BUILD NAME setting

Usage: bcf_get_version --controller_ip 10.9.16.44 or
       bcf_get_version --topo_file /var/temp.topo
"""
    parser = argparse.ArgumentParser(
                        prog='bcf_get_version',
                        formatter_class=argparse.RawDescriptionHelpFormatter,
                        description=descr)
    parser.add_argument('--controller_ip',
                        help=("Controller_ip"))
    parser.add_argument('--topo_file',
                        help=("Bigrobot Topo file"))
    _args = parser.parse_args()

    if _args.controller_ip == None and _args.topo_file == None:
        print "Please provide Controller IP or topo file!!"
        sys.exit(1)
    if _args.topo_file != None:
        if os.path.exists(_args.topo_file):
            stream = open(_args.topo_file, 'r')
            topo_dict = yaml.load(stream)
            _args.controller_ip = topo_dict['c1']['ip']
        else:
            print ("File %s does not exist" % args.topo_file)
            sys.exit(1)

    return _args

if __name__ == '__main__':
    args = prog_args()
    print get_version_string(args)
