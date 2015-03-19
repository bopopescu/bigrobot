import autobot.helpers as helpers
import autobot.test as test
import json
# from keywords.BsnCommon import BsnCommon as bsnCommon
# import re
# import ast
# import urllib2
# import traceback

class Analytics(object):

    def verify_logs_numbers(self, node):
        """
        Check if number of logs stored in elasticsarch matches number of lines
        in floodlight.log, syslog and switch syslogs.

        Inputs:
        | node | reference to controller as defined in .topo file |

        Return Value:
        - True if numbers are matching, False otherwise
        """
        t = test.Test()
        c = t.controller(node)
        total_logs = 0
        tmp_flag = False
        helpers.log("Checking how many logs"
                    " are present on node %s" % node)

        c.bash("sudo iptables -A INPUT -p tcp --dport 9200 -j ACCEPT")
        c.bash("sudo ls -alt /var/log/floodlight/floodlight.log*")
        output = c.cli_content()
        output = helpers.strip_cli_output(output)
        output = helpers.str_to_list(output)
        if len(output) > 1:
            c.bash("sudo cp /var/log/floodlight/floodlight.log.* /tmp/")
            c.bash("sudo gunzip /tmp/floodlight.log*")
            c.bash("grep $(date +'20%y-%m-%d'') /tmp/"
                   "floodlight.log* > /tmp/floodlight_date")
            tmp_flag = True
        else:
            c.bash("grep $(date +'20%y-%m-%d') /var/log/floodlight/"
                   "floodlight.log > /tmp/floodlight_date")
        c.bash("sudo wc -l /tmp/floodlight_date")
        output = c.cli_content()
        output = helpers.strip_cli_output(output)
        output = helpers.str_to_list(output)
        number = output[len(output) - 1].split()[0]
        helpers.log("There are %s lines in floodlight.log" % number)
        total_logs = total_logs + int(number)

        if (tmp_flag == True):
            c.bash("sudo rm /tmp/floodlight.log*")
        c.bash("sudo rm /tmp/floodlight_date")


        c.bash("sudo wc -l /var/log/syslog*")
        output = c.cli_content()
        output = helpers.strip_cli_output(output)
        output = helpers.str_to_list(output)
        number = output[len(output) - 1].split()[0]
        helpers.log("There are %s lines in syslog" % number)
        total_logs = total_logs + int(number)


        c.bash("sudo wc -l /var/log/switch/*")
        output = c.cli_content()
        output = helpers.strip_cli_output(output)
        output = helpers.str_to_list(output)
        if "No such file or directory" in output[0]:
            number = 0
        else:
            number = output[len(output) - 1].split()[0]
        helpers.log("There are %s lines in switch syslogs" % number)
        total_logs = total_logs + int(number)

        c.bash("grep $(date +'20%y-%m-%d') /var/log/vsphere-extension/"
               "vsphere-extension.log*  > /tmp/vsphere_date")
        c.bash("sudo wc -l /tmp/vsphere_date*")
        output = c.cli_content()
        output = helpers.strip_cli_output(output)
        output = helpers.str_to_list(output)
        number = output[len(output) - 1].split()[0]
        helpers.log("There are %s lines in vsphere-extension.log" % number)
        total_logs = total_logs + int(number)
        c.bash("sudo rm /tmp/vsphere_date")


        helpers.log("There are %s lines in controller logs" % total_logs)

        helpers.log("Checking how many entries are reported by Elasticsearch")
        c.bash("curl -XGET 'http://localhost:9200/_search'; echo")
        output = c.cli_content()
        output = helpers.strip_cli_output(output)
        data = json.loads(output)
        total_elastic = int(data['hits']['total'])
        helpers.log("There are %s entries in Elasticsearch" % total_elastic)

        helpers.log("Controller: %s, Elastic: %s" % (total_logs, total_elastic))
        tolerance = total_logs / 50
        helpers.log("Allowed discrepancy in logs is 2%%, i.e. %s" % tolerance)
        discrepancy = abs(total_logs - total_elastic)
        helpers.log("Actual discrepancy is %s" % discrepancy)

        if (discrepancy < tolerance):
            return True
        else:
            helpers.log("The discrepancy in log numbers is too big")
            return False

