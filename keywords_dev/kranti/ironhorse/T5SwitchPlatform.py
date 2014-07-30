import autobot.helpers as helpers
import autobot.test as test
import string
import telnetlib


class  T5SwitchPlatform(object):

    def __init__(self):
        pass

    def  cli_return_ofaux_connection_from_alias(self, controller, switch_alias):
            '''
                Objective:
                - Get the switch ofaux connections from controller using switch_alias
    
                Input:
                | controller_ip | IP Address of Controller |
                | switch_alias | Reference to switch alias as user input |
                | controller_role | Role of controller (Active/Backup) |
    
                Return Value:
                - True on verification success
                - False on verification failure
            '''
            t = test.Test()
            c = t.controller(controller)
            try:
                url_to_get= '/api/v1/data/controller/core/switch[name="%s"]?select=connection' % str(switch_alias)
                c.rest.get(url_to_get)
            except:
                helpers.log("Could not execute GET on URL")
                return False
            else:
                data1= c.rest.content()
                numofaux= len(data1[0]["connection"])
                helpers.log("Total number of aux channel is %d" % numofaux)
                if numofaux == 4:
                    helpers.log("Total number of aux channel is correct %d" % numofaux)
                    return  True
                else:
                    helpers.log("Total number of aux channel is not correct %d" % numofaux)    
                    return  False
        
        
    def rest_noshut_switch_interface(self, switch, intf):
        '''
         Function to remove shutdown command from the switch interface
         Input: switch and interface
         Output : remove shutdown command 
        '''
        t = test.Test()
        c = t.controller('master')
        try:
            url_to_get= '/api/v1/data/controller/core/switch-config?config=true'
            c.rest.get(url_to_get)
        except:
                helpers.log("Could not execute GET on URL")
                return False
        else:
            data= c.rest.content()
            for i in range(0, len(data)):
                try:
                    value= data[i]["interface"]    
                    helpers.log("the intf is %s" % value)
                    for j in range(0, len(data[i]["interface"])):
                        url= '/api/v1/data/controller/core/switch-config[name="%s"]/interface[name="%s"]' % (data[i]["name"], data[i]["interface"][j]["name"])
                        c.rest.delete(url, {"shutdown": None})
                        helpers.sleep(5)
                    return True
                except:
                        helpers.log("Could not execute GET on URL")
                        return False
                                
                                
    def rest_verify_intf_rxcounter_from_controller(self, switch_name, intf, framecnt, vrange=100 ):
        '''
        Function to verify the rx counter of the type 
        Input: switch, interface, type, range 
        Output : true or false based on the counter value 
        '''
        t = test.Test()
        c = t.controller('master')
        try:
            url_to_get= "/api/v1/data/controller/applications/bvs/info/stats/interface-stats/interface[switch-name='%s'][interface-name='%s']?select=rx-counter" % (str(switch_name), str(intf))
            helpers.log("URL is %s" % url_to_get)
            c.rest.get(url_to_get)           
            data= c.rest.content()
        except:
            helpers.log("Could not execute GET on URL")
            return False
        else:
            if data[0]["switch-name"] in str(switch_name)  and data[0]["interface-name"] in str(intf):
                framecnt= int(framecnt)
                vrange=  int(vrange)
                helpers.log("The framecnt is %d and vrange is %d"  %  framecnt , vrange) 
                if ((data[0]["rx-counter"]["unicast-packet"]) >= (framecnt - vrange)) and ((data[0]["rx-counter"]["unicast-packet"]) <= (framecnt + vrange) ):
                    helpers.log("The framecnt is %d and vrange is %d"  %  framecnt , vrange)
                    helpers.log("PASS: Expected counter %d , Actual Counter  %d") % (framecnt , (data[0]["rx-counter"]["unicast-packet"] ))                                                                      
                    return True
            else:
                helpers.log("FAIL: Expected counter %d , Actual Counter  %d") % (framecnt , (data[0]["rx-counter"]["unicast-packet"] ))
                return False
            
             
    def rest_verify_intf_txcounter_from_controller(self, switch, intf, framecnt, vrange=100):
        ''' Function to get the fabric interface stats from controller
        Input: switch and interface
        Output: Will return the counter stats
        '''
        t = test.Test()
        c = t.controller('master')
              
        try:
            url_to_get= '/api/v1/data/controller/applications/bvs/info/stats/interface-stats/interface[switch-name="%s"][interface-name="%s"]?select=tx-counter' % (switch, intf)
            c.rest.get(url_to_get)
        except:
            helpers.log("Could not execute GET on URL")
            return False
        else:  
            data = c.rest.content()
            helpers.log("output is %s" % data[0])
                        
        return  True
            

    def cli_t5_switch_show_version_model(self, switch, model):
        ''' Function to dump the show version on switch and verify the model
            input : switch and type - leaf or spine 
            output: true , if accton leaf AS5710 , spine AS6700 found in the output
        '''
        try:
            t = test.Test()
            s1= t.switch(switch)
            cli_input1= "show version"
            s1.enable(cli_input1)
            show_output1= s1.cli_content()
            helpers.log("output is %s" % show_output1)
            model= str(model)
        
            if model in show_output1:
                helpers.log("show version has model %s " % model)
                return  True
            else:
                helpers.log("show version did not have model %s" % model)
                return  False
            
        except:
            helpers.log("could not execute command, check for log")
            return  False
           
    def cli_t5_switch_config_interface_1g(self, switch, interface):     
        '''Function to configure interface on switch as 1G
           input - switch , interface 
           Output - True if success
        '''
        try:
            t = test.Test()
            s1= t.switch(switch)
            intf= str(interface)
            cli_input1=  "interface %s 1g-sfp" % intf
            s1.config(cli_input1)
            helpers.sleep(5) 
            return  True
        except:
            helpers.log("could not execute command, check for log")
            return  False
        
    def cli_t5_switch_verify_interface_speed(self, switch, interface, speed):
        '''Function to verify the interface speed
           input - switch, interface , speed
           Output- True if success
        '''
        try:
            t =  test.Test()
            s1=  t.switch(switch)
            intf1=  str(interface)
            speed1=  str(speed)
            cli_input1=  "show interface %s" % intf1
            helpers.log("The intf is %s and speed1 is %s" % (intf1, speed1))
            s1.enable(cli_input1)
            show_output1=  s1.cli_content()
            helpers.log("Output of show interface is %s"  % show_output1)
            if speed1 in show_output1:
                helpers.log("show interface has speed %s" % speed1)    
                return  True
            else:
                helpers.log("show interface does not has speed %s" % speed1)
                return  False
        except:
            helpers.log("could not execute intf command, check for log")
            return  False

    def cli_t5_switch_deconfig_interface_1g(self, switch, interface):     
        '''Function to configure interface on switch as 1G
           input - switch , interface 
           Output - True if success
        '''
        try:
            t = test.Test()
            s1= t.switch(switch)
            intf= str(interface)
            cli_input1=  "no interface %s 1g-sfp" % intf
            s1.config(cli_input1) 
            return  True
        except:
            helpers.log("could not execute command, check for log")
            return  False
   
   
    def cli_switch_show_interface_state(self, switch, interface):
        ''' Function to return interface state when admin down
           input - switch , interface 
           output - Interface state 
        '''
        try:
            t = test.Test()
            s1= t.switch(switch)
            cli_input1=  "show interface " + str(interface) + " detail"
            s1.enable(cli_input1)
            content1 = string.split(s1.cli_content(), '\n')
            helpers.log("value in content1[1] is %s"  % (content1[1]))
            (firstval, a, b, lastval) = content1[1].rstrip('\n').strip().split(' ')
            helpers.log("value of the interface is %s and state is %s"  % (firstval, lastval))
            intf_state=  lastval
            helpers.log("value in content1[1] is %s and state is %s"  % (content1[1], lastval))
            return intf_state
        except:
            helpers.test_failure("Could not execute command. Please check log for errors")
            return False
    
    def cli_t5_switch_show_environment_psu(self, switch, model="none", element="PSU2", element_number=1, component="none"):
        ''' Function to return the show environment output
            input - switch , model 
            output - environment output for PSU 
        '''
        t = test.Test()
        s1 = t.switch(switch)
        
        try:
            cli_input1= "show environment"
            s1.enable(cli_input1)
            content1= string.split(s1.cli_content(), '\n')
            helpers.log("value in content1 is %s"  %  (content1))
                      
            if ("PSU1" in element):
                element_name= "PSU 1"
            elif ("PSU2" in element):
                element_name= "PSU 2"
                
            helpers.log("The element name is %s" % element_name)
            elemt1= " " + str(element_name) + "\r"
            helpers.log("The element name for index is %s" % elemt1)
            element_index = content1.index(elemt1)
            helpers.log("The element index is %d" % element_index)
            
            helpers.log("The remaining content is %s" % content1[element_index:])
            content2 = content1[element_index:]
            for x in range(0, len(content2)):
                psu_dict = {}
                for i in range(0, len(content2)):                    
                    tmp_string= content2[i].lstrip()
                    #helpers.log("The current string is %s" % tmp_string)
                    element_array= tmp_string.split()
                    #helpers.log("The element array is %s" % element_array)
                    if ('State:' in element_array):
                        psu_dict['State'] = element_array[1]
                    elif ('Status:' in element_array):
                        psu_dict['Status'] = element_array[1]
                    elif ('Model:' in element_array):
                        psu_dict['Model'] = element_array[1]
                    elif ('Type:' in element_array):
                        psu_dict['Type'] = element_array[1]
                    elif ('Vin:' in element_array):
                        psu_dict['Vin'] = element_array[1]
                    elif ('Vout:' in element_array):
                        psu_dict['Vout'] = element_array[1]
                    elif ('Iin:' in element_array):
                        psu_dict['Iin'] = element_array[1]
                    elif ('Iout:' in element_array):
                        psu_dict['Iout'] = element_array[1]
                    elif ('Pin:' in element_array):
                        psu_dict['Pin'] = element_array[1]
                    elif ('Pout:' in element_array):
                        psu_dict['Pout'] = element_array[1]
                       
                helpers.log("The dictionary value is %s" % psu_dict)
                
                helpers.log("The component require is %s" % component)
                #helpers.log("The dict has following items %s" % psu_dict.items())
                #helpers.log("The dict has following keys %s" % psu_dict.keys())
                #helpers.log("The dict has following keys %s" % (psu_dict.get('Vin')))
                componentVal =  psu_dict.get(component)
                helpers.log("Got the value %s for the component %s" % (componentVal, component) )
                
                return componentVal 
                                        
            else:
                helpers.log("The element does not exist")    
                return False
        except:
            helpers.test_failure("Could not execute command. Please check log for errors")
            return False       
    
    def cli_t5_switch_show_environment_fan(self, switch, model="none", element="Fan", element_number=1, component="none"):  
        ''' Function to return the show environment output 
            This will parse the fan output from the show environment 
            input - switch , element, element_number, component 
            output - environment output for Fan
        '''                     
        t = test.Test()
        s1 = t.switch(switch)
        
        try:
            cli_input1= "show environment"
            s1.enable(cli_input1)
            content1= string.split(s1.cli_content(), '\n')
            #helpers.log("value of content1 is %s"  %  (content1))   
            
            if ("Fan" in element):
                element_name= str(" Fan ") + element_number + str('\r')
                helpers.log("The element_name is %s" % element_name)
                        
                element_index= content1.index(element_name)
                helpers.log("The element index is %d" % element_index)
                maxlen= element_index + 7 
                helpers.log("The max element index is %d" % maxlen)
               
                fan_dict= {}
                for i in range(element_index, maxlen):
                    tmp_string= content1[i].lstrip()
                    #helpers.log("The current string is %s" % tmp_string)
                    element_array= tmp_string.split()
                    #helpers.log("The element array is %s" % element_array)
                    if ("State:" in element_array):
                        fan_dict['State'] = str(element_array[1])
                    elif ("Status:" in element_array):
                        fan_dict['Status'] = str(element_array[1])
                    elif ("RPM:" in element_array):
                        fan_dict['RPM'] = element_array[1]
                    elif ("Speed:" in element_array):
                        tmpstring= str(element_array[1]).split("%")
                        #helpers.log("The tmpstring for Speed is %s" % tmpstring)
                        fan_dict['Speed'] = str(tmpstring[0])
                    elif ("Airflow:" in element_array):
                        fan_dict['Airflow'] = str(element_array[1])    
              
                helpers.log("The dictionary value is %s" % fan_dict)
                helpers.log("The component require is %s" % component)
                componentVal =  fan_dict.get(component)
                helpers.log("Got the value %s for the component %s" % (componentVal, component) )
                if (component == 'State') and (componentVal == 'Present'):
                    return True
                elif (component == 'Status') and (componentVal == 'Running.'):    
                    return True
                elif (component == 'Airflow') and (componentVal == 'Front-to-Back.'):
                    return True
                else:
                    return componentVal
                
            else:
                helpers.log("The element does not exist")
                return False
            
        except:
            helpers.test_failure("Could not execute command. Please check log for errors")
            return False
        
        
    def cli_t5_switch_show_environment_thermal(self, switch, model="none", element="thermal", element_number=1,component="none"):  
        ''' Function to return the show environment output 
            This will parse the Thermal temperature output from the show environment 
            input - switch , element, element_number 
            output - environment output for Fan
        '''                     
        t = test.Test()
        s1 = t.switch(switch)
        
        try:
            cli_input1= "show environment"
            s1.enable(cli_input1)
            content1= string.split(s1.cli_content(), '\n')
            #helpers.log("value of content1 is %s"  %  (content1)) 
            
            if ("thermal" in element):
                element_name= str(" Thermal ") + element_number + str("\r")
                helpers.log("The element name is %s" % element_name)
                element_index= content1.index(element_name)
                helpers.log("The element index is %s" % element_index) 
                maxlen= element_index + 4 
                thermal_dict= {}
                for i in range(element_index, maxlen):
                    tmp_string= content1[i].lstrip()
                    #helpers.log("The current string is %s" % tmp_string)
                    element_array= tmp_string.split()
                    #helpers.log("The element array is %s" % element_array)
                    if ("Description:" in element_array):
                        thermal_dict['Description'] = str(element_array[1])
                    elif ("Status:" in element_array):
                        thermal_dict['Status'] = str(element_array[1])
                    elif ("Temperature:" in element_array):
                        #helpers.log("The temperature string is %s" % tmp_string)
                        #element_array= tmp_string.split()
                        #helpers.log("The current temp info is %s" % element_array)
                        thermal_dict['Temperature'] = str(element_array[1])
                
                helpers.log("The dictionary value is %s" % thermal_dict)
                helpers.log("The component require is %s" % component)
                componentVal =  thermal_dict.get(component)
                helpers.log("Got the value %s for the component %s" % (componentVal, component) )
                if (component == 'Status') and (componentVal == 'Good'):
                    return True
                elif (component == 'Temperature'):    
                    return componentVal  
                    
            else:
                helpers.log("The element thermal does not exist")
                return False
  
        except:
            helpers.test_failure("Could not execute command in thermal env. Please check log for errors")
            return False   
        
        
    def cli_t5_switch_add_dhcp_ip(self, node):
        '''
        Objective:
        - Configure static IP address configuration on switch.

        Inputs:
        | console_ip | IP Address of Console Server |
        | console_port | Console Port Number |
        | ip_address | IP Address of Switch |
        | subnet | Switch subnet in /18 /24 format |
        | gateway | IP address of default gateway |

        Return Value:
        - True on configuration success
        - False on configuration failure
        '''
        try:
            t = test.Test()
            user = "admin"
            password = "adminadmin"
            tn = t.dev_console(node)
            #console_ip = t.params(node, "console_ip")
            #console_port = t.params(node, "console_port")
            #tn = telnetlib.Telnet(str(console_ip), int(console_port))
            tn.read_until("login: ", 3)
            tn.write(user + "\r\n")
            tn.read_until("Password: ", 3)
            tn.write(password + "\r\n")
            tn.read_until('')
            tn.write("enable \r\n")
            tn.write("conf t \r\n")
            tn.write("interface ma1 ip-address dhcp \r\n")
            helpers.sleep(10)
            tn.read_until(">")
            tn.write("exit \r\n")
            tn.write("exit \r\n")
            tn.close()
            return True
        except:
            helpers.test_failure("Could not execute command. Please check log for errors")
            return False

    def cli_t5_switch_delete_dhcp_ip(self, node):
        '''
        Objective:
         - Delete DHCP IP address configuration on switch.

        Inputs:
        | console_ip | IP Address of Console Server |
        | console_port | Console Port Number |
        | ip_address | IP Address of Switch |
        | subnet | Switch subnet in /18 /24 format |
        | gateway | IP address of default gateway |

        Return Value:
        - True on configuration success
        - False on configuration failure
        '''
        try:
            t = test.Test()
            user = "admin"
            password = "adminadmin"
            tn = t.dev_console(node)
            #console_ip = t.params(node, "console_ip")
            #console_port = t.params(node, "console_port")
            #tn = telnetlib.Telnet(str(console_ip), int(console_port))
            tn.read_until("login: ", 3)
            tn.write(user + "\r\n")
            tn.read_until("Password: ", 3)
            tn.write(password + "\r\n")
            tn.read_until('')
            tn.write("\r\n" + "no interface ma1 ip-address dhcp \r\n")
#            tn.write("\r\n" + "no interface ma1 ip-address " + str(ip_address) + "/" + str(subnet) + " \r\n")
#            tn.write("\r\n" + "no ip default-gateway " + str(gateway) + " \r\n")
            tn.write("exit" + "\r\n")
            tn.write("exit" + "\r\n")
            tn.close()
            return True
        except:
            helpers.test_failure("Could not configure static IP address configuration on switch. Please check log for errors")
            return False
        
        
    def rest_get_switch_output_from_controller(self, switch, field=None):
        '''
            Objective:
            - get the switch output from the controller.

            Inputs:
            | node | switch name  |
    
            Return Value:
            - Return the value of the field [Model, version, image ] 
        
        '''
        t = test.Test()
        #switch = t.switch(switch)
        switch_alias = t.switch(switch)
        helpers.log("The switch alias is %s"  % switch)
        c = t.controller('master')
        url = ('/api/v1/data/controller/core/proxy/version[name="%s"]' % switch )
        helpers.log("Getting the switch %s info from controller %s" % (switch, url) )
        try:
            helpers.log("Getting the switch %s info from controller %s" % (switch, url) )
            c.rest.get(url)
            data = c.rest.content()
            helpers.log("The output is %s" % data)
            t1 = data[0]
            helpers.log("The t1 output is %s" % (t1))
            t2 = data[0]["name"]
            helpers.log("The t2 output is %s" % (t2))
            t3 = data[0]["response"]
            helpers.log("The t3 output is %s" % (t3))
            if ("Model: AS5710" in t3):
                helpers.log("The value of model is found")
                return True
            #t4 = data[0]["response"]["Model"]
            #helpers.log("The t4 output is %s" % (t4))
            #t5 = data[0]["response"]["System Information"]
            #helpers.log("The t5 output is %s" % (t5))
            
            if field is None:
                helpers.log("Got the switch version from controller")
                return True
            elif field is "model":
                helpers.log("getting the switch Model from output")
                model = data[0]["response"][0]["Model"]
                helpers.log("Model is found as %s" % model )
                return model 
        except:
            helpers.log("Could not get the rest output.see log for errors\n")
            return False
                
                
                    