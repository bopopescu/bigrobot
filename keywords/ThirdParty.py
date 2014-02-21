''' 
###  WARNING !!!!!!!
###  
###  This is where common code for all third party switch will go in.
###  
###  To commit new code, please contact the Library Owner: 
###  Animesh Patcha (animesh.patcha@bigswitch.com)
###
###  DO NOT COMMIT CODE WITHOUT APPROVAL FROM LIBRARY OWNER
###  
###  Last Updated: 02/08/2014
###  
###  WARNING !!!!!!!
'''


import autobot.helpers as helpers
import autobot.test as test
import subprocess
import re

class ThirdParty(object):

    def __init__(self):
        pass

########################################################################
#  Arista : Configuration and Verification                             #
########################################################################

    def cli_arista_add_portchannel(self, node, pc_number, pc_list, pc_mode="active", pc_priority=15000, pc_timeout=5):
        '''Configure Port Channel
        
            Input: 
                `pc_number`        Port Channel to be configured
                `pc_list`          List of port channel interfaces seperated by single space
            
            Return Value:  True on Success
        '''
        try:
            t = test.Test()
            switch = t.switch(node)
        except:
            return False
        else:
            cli_input_1 = "interface Port-Channel" + str(pc_number)
            switch.config(cli_input_1)
            cli_input_2 = "   port-channel lacp fallback"
            switch.config(cli_input_2)
            cli_input_2 = "   port-channel lacp fallback timeout " + str(pc_timeout)
            switch.config(cli_input_2)
            port_list = re.split(' ', pc_list)
            for x in port_list:
                cli_input_2 = "interface ethernet" + str(x)
                switch.config(cli_input_2)
                cli_input_3 = "channel-group " + str(pc_number) + " mode " + str(pc_mode)
                switch.config(cli_input_3)
                cli_input_4 = "lacp port-priority " + str(pc_priority)
                switch.config(cli_input_4)
                switch.config("exit")
            return True

    def cli_arista_delete_portchannel(self, node, pc_number, pc_list, pc_priority=15000):
        '''Configure Port Channel
        
            Input: 
                `pc_number`        Port Channel to be configured
                `pc_list`          List of port channel interfaces seperated by single space
            
            Return Value:  True on Success
        '''
        try:
            t = test.Test()
            switch = t.switch(node)
        except:
            return False
        else:
            port_list = re.split(' ', pc_list)
            for x in port_list:
                cli_input_2 = "interface ethernet" + str(x)
                switch.config(cli_input_2)
                cli_input_3 = "no channel-group " + str(pc_number) + " mode active"
                switch.config(cli_input_3)
                cli_input_4 = "no lacp port-priority " + str(pc_priority)
                switch.config(cli_input_4)

                switch.config("exit")
            cli_input_1 = "no interface Port-Channel" + str(pc_number)
            switch.config(cli_input_1)
            return True

    def cli_arista_add_mtu_interface(self, node, interface_name, mtu_size):
        '''Configure MTU
        
            Input: 
                `interface_name`        Name of Interface
                `mtu_size`          MTU size
            
            Return Value:  True on Success
        '''
        try:
            t = test.Test()
            switch = t.switch(node)
        except:
            return False
        else:
            cli_input_1 = "interface " + str(interface_name)
            switch.config(cli_input_1)
            cli_input_2 = "   mtu" + str(mtu_size)
            switch.config(cli_input_2)
            return True

    def cli_arista_add_vlan(self, node, vlan_number, vlan_name, interface_name, mode="trunk"):
        try:
            t = test.Test()
            switch = t.switch(node)
        except:
            return False
        else:
            cli_input_1 = "vlan " + str(vlan_number)
            switch.config(cli_input_1)
            cli_input_2 = "name " + str(vlan_name)
            switch.config(cli_input_2)
            cli_input_3 = "interface " + str(interface_name)
            switch.config(cli_input_3)
            if "trunk" in mode:
                cli_input_4 = "switchport mode trunk"
                switch.config(cli_input_4)
                cli_input_5 = "switchport trunk allowed vlan " + str(vlan_number)
                switch.config(cli_input_5)
            else:
                cli_input_4 = "switchport mode access"
                switch.config(cli_input_4)
                cli_input_5 = "switchport access vlan " + str(vlan_number)
                switch.config(cli_input_5)
            return True

    def cli_arista_delete_vlan(self, node, vlan_number, vlan_name, interface_name, mode="trunk"):
        try:
            t = test.Test()
            switch = t.switch(node)
        except:
            return False
        else:
            cli_input_1 = "no vlan " + str(vlan_number)
            switch.config(cli_input_1)
            cli_input_3 = "interface " + str(interface_name)
            switch.config(cli_input_3)
            if "trunk" in mode:
                cli_input_4 = "no switchport trunk allowed vlan " + str(vlan_number)
                switch.config(cli_input_4)
                cli_input_5 = "no switchport mode trunk"
                switch.config(cli_input_5)
                cli_input_6 = "switchport"
                switch.config(cli_input_6)
            else:
                cli_input_4 = "no switchport access vlan " + str(vlan_number)
                switch.config(cli_input_4)
                cli_input_5 = "no switchport mode access"
                switch.config(cli_input_5)
            return True

    def cli_arista_execute_command(self, node, command):
        try:
            t = test.Test()
            switch = t.switch(node)
        except:
            return False
        else:
            switch.config(command)
            return switch.cli_content()
