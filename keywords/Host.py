'''
###  WARNING !!!!!!!
###
###  This is where common code for Host will go in.
###
###  To commit new code, please contact the Library Owner:
###  Vui Le (vui.le@bigswitch.com)
###
###  DO NOT COMMIT CODE WITHOUT APPROVAL FROM LIBRARY OWNER
###
###  Last Updated: 03/11/2014
###
###  WARNING !!!!!!!
'''

import autobot.helpers as helpers
import autobot.test as test
import re


class Host(object):

    def bash_scp(self, node, source, dest='.', password='bsn', timeout=180):
        """
        Objective:
        On node, run secure copy a file as defined in source to dest.

        Inputs:
        | node | controller name as defined in .topo file |
        | source | the complete file path, in format user@host:/path/file' |
        | dest | the destination (default is '.') |
        | password | password used to authenticate (default is 'bsn') |
        | timeout | how log to wait before timeout (default is 180 seconds) |

        Example:
        | bash scp | node=c1 | source=bsn@jenkins:/var/lib/jenkins/jobs/bvs\\ master/lastSuccessful/archive/target/appliance/images/bvs/controller-upgrade-bvs-2.0.5-SNAPSHOT.pkg | dest=. |
        | bash_scp | node=h1 | source=/var/log/floodlight/* | dest=jenkins-w9.bigswitch.com:/var/www/regression_logs/vui/test_mininet_20140509_060230 | password='bsn' | timeout=60 |
        Return Value:
        - True if scp succeeds
        - False if scp fails
        """
        t = test.Test()
        n = t.node(node)

        helpers.log("'%s' - Copying '%s' to '%s'"
                    % (node, source, dest))
        n.bash('')
        n.send('sudo scp -rp'
               ' -o UserKnownHostsFile=/dev/null'
               ' -o StrictHostKeyChecking=no %s %s'
               % (source, dest))
        n.expect(r'[\r\n].+password: ')
        n.send(password)
        try:
            n.expect(timeout=timeout)
        except:
            helpers.log('scp failed')
            return False
        else:
            helpers.log('scp completed successfully')
            return True

    def bash_ping_background_start(self, *args, **kwargs):
        """
        Start background ping. It accepts the same options as bash_ping
        although it requires an additional 'label' argument. The label is
        used to name the output log and to store the background PID. So it
        needs to be unique for the duration of the background ping. The reason
        the label is required is because multiple background pings may get
        issued in parallel.

        To stop background ping, call the keyword 'bash ping background stop'
        and provide it with the label.

        Example:
        | bash ping background start | c1 | dest_ip=www.cnn.com | label=test001 |
        | bash ping background stop | c1 | label=test001 |
        | bash ping background stop | c1 | label=test001 | return_stats=${true} |

        Return value:
          - packet loss percentage (default)
          - stats dict if return_stats is ${true}
        """
        _ = self.bash_ping(background=True, *args, **kwargs)

    def bash_ping_background_stop(self, node, label, return_stats=False):
        """
        See details in keyword 'bash ping background start'.
        """
        t = test.Test()
        n = t.node(node)
        ping_output_file = '/tmp/ping_background_output.%s.log' % label
        ping_pid_file = ping_output_file + ".pid"
        pid = helpers.str_to_list(n.bash('cat %s' % ping_pid_file)['content'])[1]
        n.bash('kill -2 %s' % pid)
        ping_output = n.bash('tail -20 %s' % ping_output_file)['content']
        stats = helpers._ping(ping_output=ping_output)
        if return_stats:
            return stats
        else:
            return stats["packets_loss_pct"]

    def bash_ping(self, node=None, dest_ip=None, dest_node=None,
                  return_stats=False, *args, **kwargs):
        """
        Perform a ping from the shell. Returns the loss percentage
        - 0   - 0% loss (default)
        - 100 - 100% loss (default)
        - Stats dict if return_stats is ${true}

        Inputs:
        - node:      The device name as defined in the topology file, e.g., 'c1', 's1', etc.
        - dest_ip:   Ping this destination IP address
        - dest_node  Ping this destination node ('c1', 's1', etc)
        - source_if: Source interface
        - count:     Number of ping packets to send
        - ttl:       IP Time-to-live
        - record_route:  ${true}  - to include RECORD ROUTE option
        - interval:  Time in seconds (floating point value allowed) to wait between sending packets.

        Example:
        | ${lossA} = | Bash Ping | h1          | 10.192.104.1 | source_if=eth1 |
        | ${lossB} = | Bash Ping | node=master | dest_node=s1 |                |
        =>
        - ${lossA} = 0
        - ${lossB} = 100

        Miscellaneous:
        - See also Controller.cli ping
        - See also autobot.helpers.__init__.py to see what Unix ping command option is used for each input parameter.
        """
        t = test.Test()
        n = t.node(node)

        if not dest_ip and not dest_node:
            helpers.test_error("Must specify 'dest_ip' or 'dest_node'")
        if dest_ip and dest_node:
            helpers.test_error("Specify 'dest_ip' or 'dest_node' but not both")
        if dest_ip:
            dest = dest_ip
        if dest_node:
            dest = t.node(dest_node).ip()
        stats = helpers._ping(dest, node_handle=n, mode='bash', *args, **kwargs)
        if kwargs.get('background', False):
            return stats
        elif return_stats:
            return stats
        else:
            return stats["packets_loss_pct"]

    def bash_ping6_background_start(self, *args, **kwargs):
        """
        Start background ping6. It accepts the same options as bash_ping6
        although it requires an additional 'label' argument. The label is
        used to name the output log and to store the background PID. So it
        needs to be unique for the duration of the background ping6. The reason
        the label is required is because multiple background ping6 may get
        issued in parallel.

        To stop background ping6, call the keyword 'bash ping6 background stop'
        and provide it with the label.

        Example:
        | bash ping6 background start | c1 | dest_ip=www.cnn.com | label=test001 |
        | bash ping6 background stop | c1 | label=test001 |
        | bash ping6 background stop | c1 | label=test001 | return_stats=${true} |

        Return value:
          - packet loss percentage (default)
          - stats dict if return_stats is ${true}
        """
        _ = self.bash_ping6(background=True, *args, **kwargs)

    def bash_ping6_background_stop(self, node, label, return_stats=False):
        """
        See details in keyword 'bash ping6 background start'.
        """
        t = test.Test()
        n = t.node(node)
        ping6_output_file = '/tmp/ping6_background_output.%s.log' % label
        ping6_pid_file = ping6_output_file + ".pid"
        pid = helpers.str_to_list(n.bash('cat %s' % ping6_pid_file)['content'])[1]
        n.bash('kill -2 %s' % pid)
        ping6_output = n.bash('tail -20 %s' % ping6_output_file)['content']
        stats = helpers._ping6(ping6_output=ping6_output)
        if return_stats:
            return stats
        else:
            return stats["packets_loss_pct"]

    def bash_ping6(self, node=None, dest_ip=None, dest_node=None,
                  return_stats=False, *args, **kwargs):
        """
        Perform a ping6 from the shell. Returns the loss percentage
        - 0   - 0% loss (default)
        - 100 - 100% loss (default)
        - Stats dict if return_stats is ${true}

        Inputs:
        - node:      The device name as defined in the topology file, e.g., 'c1', 's1', etc.
        - dest_ip:   Ping6 this destination IP address
        - dest_node  Ping6 this destination node ('c1', 's1', etc)
        - source_if: Source interface
        - count:     Number of ping6 packets to send
        - ttl:       IP Time-to-live
        - record_route:  ${true}  - to include RECORD ROUTE option
        - interval:  Time in seconds (floating point value allowed) to wait between sending packets.

        Example:
        | ${lossA} = | Bash Ping6 | h1          | 10.192.104.1 | source_if=eth1 |
        | ${lossB} = | Bash Ping6 | node=master | dest_node=s1 |                |
        =>
        - ${lossA} = 0
        - ${lossB} = 100

        Miscellaneous:
        - See also Controller.cli ping6
        - See also autobot.helpers.__init__.py to see what Unix ping6 command option is used for each input parameter.
        """
        t = test.Test()
        n = t.node(node)

        if not dest_ip and not dest_node:
            helpers.test_error("Must specify 'dest_ip' or 'dest_node'")
        if dest_ip and dest_node:
            helpers.test_error("Specify 'dest_ip' or 'dest_node' but not both")
        if dest_ip:
            dest = dest_ip
        if dest_node:
            dest = t.node(dest_node).ip()
        stats = helpers._ping6(dest, node_handle=n, mode='bash', *args, **kwargs)
        if kwargs.get('background', False):
            return stats
        elif return_stats:
            return stats
        else:
            return stats["packets_loss_pct"]


    def bash_add_tag(self, node, intf, vlan):
        """
        Add vlan tag to a Host eth interfaces.
        """
        t = test.Test()
        n = t.node(node)
        n.sudo("vconfig add %s %s" % (intf, vlan))
        return True

    def bash_add_ip_address(self, node, ipaddr, intf):
        """
        Adding IP address to Host interface,For tagged interface user needs
        to specify interface.tagnumber (e.g eth1.10).
        """
        t = test.Test()
        n = t.node(node)
        n.sudo("ip addr add %s dev %s" % (ipaddr, intf))
        return True

    def bash_delete_ip_address(self, node, ipaddr, intf):
        """
        Removing IP address from the host interface.
        """
        t = test.Test()
        n = t.node(node)
        n.sudo("ip addr del %s dev %s" % (ipaddr, intf))
        return True

    def bash_delete_tag(self, node, intf, soft_error=True):
        """
        Function to remove the vlan tag from the host eth interfaces.
        Note: soft_error=True because in the common use case, we
        just want to log the error but not trigger failure.
        """
        t = test.Test()
        n = t.node(node)

        try:
            n.sudo("vconfig rem %s" % intf)
        except:
            output = helpers.exception_info_value()
            helpers.log("Output: %s" % output)

            # Catch error:
            #   ERROR: trying to remove VLAN -:eth1.20:- error: No such device
            if helpers.any_match(str(output), r'error: No such devices'):
                helpers.test_error("vconfig rem error - no such device '%s'" % intf,
                                   soft_error)
                return False
            else:
                helpers.test_error('Uncaught exception:\n%s' %
                                   helpers.exception_info(),
                                   soft_error)
                return False

        return True

    def bash_network_restart(self, node, timeout=None):
        """
        Function to restart the networking services for Ubuntu 12.04.
        """
        t = test.Test()
        n = t.node(node)
        n.sudo("/etc/init.d/networking restart", timeout=timeout)
        return True

    def bash_get_interface_ipv4(self, node, intf):
        t = test.Test()
        n = t.node(node)
        output = n.sudo("ifconfig %s | grep --color=never -i 'inet addr'" % intf)['content']
        return_stat = n.sudo('echo $?')['content']
        return_stat = helpers.strip_cli_output(return_stat)
        helpers.log("output: %s" % output)
        helpers.log("return_stat: %s" % return_stat)
        if int(return_stat) == 1:
            return ''
        else:
            result = re.search('inet addr:(.*)\sBcast', output)
            return result.group(1)

    def bash_release_dhcpv4_address(self, node, intf):

        t = test.Test()
        n = t.node(node)
        n.sudo("dhclient -r %s" % intf)
        return True
        n.sudo("ifconfig %s | grep --color=never -i 'inet addr'" % intf)['content']
        return_stat = n.sudo('echo $?')['content']
        return_stat = helpers.strip_cli_output(return_stat)
        helpers.log("return_stat: %s" % return_stat)
        if int(return_stat) == 1:
            return True
        else:
            return False

    def bash_renew_dhcpv4_address(self, node, intf):
        '''
             attempt to obtain an IPv4 address via dhcp. timeout is set to 10 seconds in /etc/dhcp/dhclient.conf file for ubuntu host
        '''
        t = test.Test()
        n = t.node(node)
        n.sudo("dhclient -v -4 %s" % intf)
        output = n.sudo("ifconfig %s | grep --color=never -i 'inet addr'" % intf)['content']
        return_stat = n.sudo('echo $?')['content']
        return_stat = helpers.strip_cli_output(return_stat)
        helpers.log("return_stat: %s" % return_stat)
        if int(return_stat) == 1:
            return ''
        else:
            result = re.search('inet addr:(.*)\sBcast', output)
            return result.group(1).strip()

    def bash_add_route(self, node, cidr, gw, dev=None):
        """
        See manpage route(8) for more details.
        """
        t = test.Test()
        n = t.node(node)
        cmd = "route add -net %s gw %s" % (cidr, gw)
        if dev:
            cmd = cmd + " dev %s" % dev
        n.sudo(cmd)
        return True

    def bash_delete_route(self, node, cidr, gw):
        t = test.Test()
        n = t.node(node)
        n.sudo("route del -net %s gw %s" % (cidr, gw))
        return True

    def bash_set_mac_address(self, node, intf, mac):
        '''
            change mac address of a host interface
        '''
        t = test.Test()
        n = t.node(node)
        n.sudo("ifconfig %s hw ether %s" % (intf, mac))
        return True

    def bash_get_intf_mac(self, node, intf):
        '''
            return mac address of a host interface
        '''
        t = test.Test()
        n = t.node(node)
        output = n.sudo("ifconfig %s | grep --color=never HWaddr" % (intf))['content']
        return_stat = n.sudo('echo $?')['content']
        return_stat = helpers.strip_cli_output(return_stat)
        helpers.log("return_stat: %s" % return_stat)
        if int(return_stat) == 1:
#            helpers.log("I am here")
            return ''
        else:
#            helpers.log("I am there")
#            helpers.log("output: %s" % output)
            output = helpers.strip_cli_output(output)
            result = re.search('HWaddr (.*)', output)
            mac_addr = result.group(1)
            helpers.log("output: %s" % output)
            helpers.log("result: %s" % result)
            # mac = mac_addr.replace("\r", "")
            mac = mac_addr.strip(' \t\n\r')
            helpers.log("mac_addr: %s" % mac_addr)
            return mac

    def bash_verify_arp(self, node, ip):
        t = test.Test()
        n = t.node(node)
        result = n.sudo("arp -n %s" % ip)
        output = result["content"]
        helpers.log("output: %s" % output)
        match = re.search(r'no entry|incomplete', output, re.S | re.I | re.M)
        if match:
            return False
        else:
            return True

    def bash_ifup_intf(self, node, intf):
        t = test.Test()
        n = t.node(node)
        n.sudo("ifconfig %s up" % intf)
        return True

    def bash_ifdown_intf(self, node, intf):
        t = test.Test()
        n = t.node(node)
        n.sudo("ifconfig %s down" % intf)
        return True

    def bash_init_intf(self, node, intf):
        t = test.Test()
        n = t.node(node)
        try:
            n.sudo("ifconfig %s 0.0.0.0" % intf)
        except:
            helpers.test_error("Ignore Host errors",
                               soft_error=True)
        return True

    def bash_check_service_status(self, node, processname):
        t = test.Test()
        n = t.node(node)
        output = n.sudo("service %s status" % processname)['content']
        helpers.log("output: %s" % output)
        match = re.search(r'unrecognized service', output, re.S | re.I | re.M)
        if match:
            return 'unrecognized service'
        match = re.search(r'is not running', output, re.S | re.I | re.M)
        if match:
            return 'is not running'
        match = re.search(r'stop\/waiting', output, re.S | re.I | re.M)
        if match:
            return 'is stopped'
        match = re.search(r'is running', output, re.S | re.I | re.M)
        if match:
            return 'is started'
        match = re.search(r'start\/running', output, re.S | re.I | re.M)
        if match:
            return 'is started'

    def bash_start_service(self, node, processname):
        t = test.Test()
        n = t.node(node)
        n.sudo("service %s start" % processname)
        return True

    def bash_stop_service(self, node, processname):
        t = test.Test()
        n = t.node(node)
        n.sudo("service %s stop" % processname)
        return True

    def bash_restart_service(self, node, processname, timeout=None):
        t = test.Test()
        n = t.node(node)
        n.sudo("service %s restart" % processname, timeout=timeout)
        return True

    def bash_ls(self, node, path):
        """
        Execute 'ls -l --time-style=+%Y-%m-%d <path>' on a device.

        Inputs:
        | node | reference to switch/controller/host as defined in .topo file |
        | path | directory to get listing for |

        Example:
        - bash ls    master    /home/admin
        - bash ls    h1        /etc/passwd

        Return Value:
        - Dictionary with file name as key. Value contains list of fields, where
            - fields[0] = file/dir
            - fields[1] = no of links
            - fields[2] = user
            - fields[3] = group
            - fields[4] = size
            - fields[5] = datetime
        """
        t = test.Test()
        n = t.node(node)
        content = n.bash('ls -l --time-style=+%%Y-%%m-%%d %s' % path)['content']
        lines = helpers.strip_cli_output(content, to_list=True)

        # Output:
        # total 691740
        # -rw-r--r-- 1 root root 708335092 2014-03-03 13:08 controller-upgrade-bvs-2.0.5-SNAPSHOT.pkg
        # -rw-r--r-- 1 bsn  bsn          0 2014-03-12 10:05 blah blah.txt

        # Strip first line ('total <nnnnn>')
        lines = lines[1:]
        # helpers.log("lines: %s" % helpers.prettify(lines))

        files = {}

        for line in lines:
            fields = line.split()
            helpers.log("fields: %s" % fields)
            # fields[6]+ contains filename (may have spaces in name)
            filename = ' '.join(fields[6:])

            # If file is a symlink, remove the symlink (leave just the name)
            # E.g., 'blkid.tab -> /dev/.blkid.tab'
            filename = re.sub('-> .*$', '', filename)
            files[filename] = fields[0:6]

        helpers.log("files:\n%s" % helpers.prettify(files))
        return files


    def bash_delete_arp(self, node, ipaddr):
        t = test.Test()
        n = t.node(node)
        n.sudo("arp -d %s " % ipaddr)
        return True


    def bash_run_command(self, node, cmd):
        t = test.Test()
        n = t.node(node)
        try:
            content = n.bash("%s " % cmd)['content']
            str_list = helpers.strip_cli_output(content, to_list=True)
        except:
            helpers.test_error("Bash run command failed",
                               soft_error=True)
            str_list = "Bash Run Command Failed"
        return  str_list

    def bash_ifconfig_ip_address(self, node, ipaddr, intf, down=False):
        """
        Adding IP address to Host interface,For tagged interface user needs
        to specify interface.tagnumber (e.g eth1.10).
        ifconfig bond0.100 10.10.10.1/24 up
        """
        t = test.Test()
        n = t.node(node)
        if down is True:
            n.sudo("ifconfig %s %s down" % (intf, ipaddr))
        else:
            n.sudo("ifconfig %s %s up" % (intf, ipaddr))
        return True

    def bash_lsb_release(self, node, minor=False, soft_error=False):
        """
        Return the Ubuntu release number. Ubuntu release numbers typically has
        the format "14.04" or "12.04".
        - By default, return the major version number, e.g., 14 or 12.
        - If minor=True, return the minor version number, e.g., 0.3 or 0.4.
        """
        t = test.Test()
        n = t.node(node)
        content = n.bash("lsb_release -r")['content']
        match = re.search(r'Release:\s+(\d+)\.(\d+)', content, re.M)
        if match:
            if minor:
                return int(match.group(2))
            else:
                return int(match.group(1))
        else:
            helpers.test_error("lsb_release command output is invalid",
                               soft_error=soft_error)

    def bash_get_distributor(self, node, soft_error=False):
        """
        Return the distributor id: Ubuntu
        """
        t = test.Test()
        n = t.node(node)
        content = n.bash("lsb_release -i")['content']
        match = re.search(r'Distributor ID:\s+(.*)', content, re.M)
        if match:
            return  match.group(1)

        else:
            helpers.test_error("lsb_release command output is invalid",
                               soft_error=soft_error)



    def bash_restart_networking_service(self, node, timeout=None):
        """
        Restart networking service.
        """
        t = test.Test()
        h = t.controller(node)
        major_version = self.bash_lsb_release(node)
        helpers.log("Host %s is running Ubuntu major version %s"
                    % (node, major_version))
        if major_version == 12:
            h.sudo("/etc/init.d/networking restart", timeout=timeout)
        else:
            h.sudo("service networking restart", timeout=timeout)

    def bash_kill_process(self, node, pname):
        '''
            kill process name
        '''
        t = test.Test()
        n = t.node(node)
        n.bash("ps aux | grep -i %s | grep -v grep" % pname)
        n.bash("for x in `ps aux | grep -i %s | grep -v grep | awk '{print $2}'`; do sudo kill -9 $x; done" % pname)

    def bash_add_static_arp(self, node, ipaddr, hwaddr):
        t = test.Test()
        n = t.node(node)
        n.sudo("arp -s %s %s" % (ipaddr, hwaddr))
        return True

    def Host_reboot(self, host):

        ''' Reboot a host and wait for it to come back.
        '''
        t = test.Test()
        node = t.node(host)
        ipAddr = node.ip()
        content = node.bash('reboot')['content']
        helpers.log("*****Output is :*******\n%s" % content)
        if re.search(r'The system is going down for reboot NOW!', content):
            helpers.log("system is rebooting")
            helpers.sleep(120)
        else:
            helpers.log("USR ERROR: system did NOT reboot")
            return False
        count = 0
        while (True):
            loss = helpers.ping(ipAddr)
            helpers.log("loss is: %s" % loss)
            if(loss != 0):
                if (count > 5):
                    helpers.warn("Cannot connect to the IP Address: %s - Tried for 5 Minutes" % ipAddr)
                    return False
                helpers.sleep(60)
                count += 1
                helpers.log("Trying to connect to the IP Address: %s - Try %s" % (ipAddr, count))
            else:
                helpers.log("USR INFO:  system just came alive. Waiting for it to become fully functional")
                helpers.sleep(30)
                break

        return True

    def Host_powercycle(self, host):

        ''' power cycle a host and wait for it to come back.
        '''
        t = test.Test()
        node = t.node(host)
        ipAddr = node.ip()
        t.power_cycle(host, minutes=0)
        helpers.log("*****system went through power cycle********")

        helpers.sleep(120)
        count = 0
        while (True):
            loss = helpers.ping(ipAddr)
            helpers.log("loss is: %s" % loss)
            if(loss != 0):
                if (count > 10):
                    helpers.warn("Cannot connect to the IP Address: %s - Tried for 5 Minutes" % ipAddr)
                    return False
                helpers.sleep(60)
                count += 1
                helpers.log("Trying to connect to the IP Address: %s - Try %s" % (ipAddr, count))
            else:
                helpers.log("USR INFO:  system just came alive. Waiting for it to become fully functional")
                helpers.sleep(30)
                break

        return True
