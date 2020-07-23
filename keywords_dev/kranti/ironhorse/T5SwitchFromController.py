import autobot.helpers as helpers
import autobot.test as test
import string
import telnetlib
import re


class  T5SwitchFromController(object):
    
    
    def __init__(self):
        pass
        
    def rest_get_switch_environment_fan_from_controller (self, switch, dpid, model="none", element="Fan", element_number=1, component="none"):
            
            ''' Function to get rest output from controller the show environment output for switch
            This will parse the fan output from the show environment 
            input - switch , dpid, element, element_number, component 
            output - environment output for Fan
            '''                     
            t = test.Test()
            switch_alias = t.switch(switch)
            helpers.log("The switch alias is %s" % switch)
            c = t.controller('main')
            helpers.log("The switch dpid is %s"  % dpid)
            url = ('/api/v1/data/controller/core/proxy/environment[dpid="%s"]' % dpid )
            
            try: 
                helpers.log("Getting the switch %s info from controller" % switch)   
                c.rest.get(url)
                data = c.rest.content()
                helpers.log("The data is %s" % data)
                tmpdata = data[0]["response"]
                helpers.log("The tmpdata is %s" % tmpdata)
                data1 =  string.split(str(tmpdata), '\n')
                helpers.log("The data1 is %s" % data1)
                if ("Fan" in element):
                    element_name =  str(" Fan ") + element_number
                    helpers.log("The element name  is %s" % element_name)
                    element_index = data1.index(element_name)
                    helpers.log("The element index  is %s" % element_index)
                    maxlen = element_index + 7
                    fan_dict = {}
                    for i in range(element_index, maxlen):
                        tmp_string = data1[i].lstrip()
                        #helpers.log("The tmp_string  is %s" % tmp_string)
                        element_array = tmp_string.split()
                        #helpers.log("The elemet_array  is %s" % element_array)
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
                #helpers.log("The component require is %s" % component)
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
        
            except:
                helpers.log("Could not get the rest output.see log for errors\n")
                return  False
            
 
    def rest_get_switch_version_from_controller(self, switch, component="none"):
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
        c = t.controller('main')
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
                helpers.log("The value of model is found as Leaf AS5710")
                return True
            #t4 = data[0]["response"]["Model"]
            #helpers.log("The t4 output is %s" % (t4))
            #t5 = data[0]["response"]["System Information"]
            #helpers.log("The t5 output is %s" % (t5))
            
            if component is None:
                helpers.log("component is None.")
                return True
            elif component is "model":
                helpers.log("getting the switch Model from output")
                model = data[0]["response"][0]["Model"]
                helpers.log("Model is found as %s" % model )
                return model 
        except:
            helpers.log("Could not get the rest output.see log for errors\n")
            return False
 
    def rest_get_switch_environment_psu_from_controller (self, switch, dpid, model="none", element="PSU", element_number=1, component="none"):
            
            ''' Function to get rest output from controller the show environment output for switch
            This will parse the PSU output from the show environment 
            input - switch , dpid, element, element_number, component 
            output - environment output for PSU
            '''                     
            t = test.Test()
            switch_alias = t.switch(switch)
            helpers.log("The switch alias is %s" % switch)
            c = t.controller('main')
            helpers.log("The switch dpid is %s"  % dpid)
            url = ('/api/v1/data/controller/core/proxy/environment[dpid="%s"]' % dpid )
            
            try: 
                helpers.log("Getting the switch %s info from controller" % switch)   
                c.rest.get(url)
                data = c.rest.content()
                helpers.log("The data is %s" % data)
                tmpdata = data[0]["response"]
                helpers.log("The tmpdata is %s" % tmpdata)
                data1 =  string.split(str(tmpdata), '\n')
                helpers.log("The data1 is %s" % data1)
                if ("PSU" in element):
                    element_name =  str(" PSU ") + element_number
                    helpers.log("The element name  is %s" % element_name)
                    element_index = data1.index(element_name)
                    helpers.log("The element index  is %s" % element_index)
                    maxlen = element_index + 23
                    psu_dict = {}
                    for i in range(element_index, maxlen):
                        tmp_string = data1[i].lstrip()
                        helpers.log("The tmp_string  is %s" % tmp_string)
                        element_array = tmp_string.split()
                        helpers.log("The elemet_array  is %s" % element_array)
                        if ("State:" in element_array):
                            psu_dict['State'] = str(element_array[1])
                        elif ("Status:" in element_array):
                            psu_dict['Status'] = str(element_array[1])
                        elif ("Model:" in element_array):
                            psu_dict['Model'] = str(element_array[1])
                        elif ("Type:" in element_array):
                            psu_dict['Type'] = str(element_array[1])
                        elif ("Vin:" in element_array):
                            psu_dict['Vin'] = str(element_array[1])
                        elif ("Vout:" in element_array):
                            psu_dict['Vout'] = str(element_array[1])
                        elif ("Iin:" in element_array):
                            psu_dict['Iin'] = str(element_array[1])
                        elif ("Iout:" in element_array):
                            psu_dict['Iout'] = str(element_array[1])
                        elif ("Pin:" in element_array):
                            psu_dict['Pin'] = str(element_array[1])
                        elif ("Pout:" in element_array):
                            psu_dict['Pout'] = str(element_array[1])
                        
                            
                helpers.log("The dictionary value is %s" % psu_dict)
                #helpers.log("The component require is %s" % component)
                componentVal =  psu_dict.get(component)
                helpers.log("Got the value %s for the component %s" % (componentVal, component) )
                if (component == 'State') and (componentVal == 'Present'):
                    return True
                elif (component == 'Status') and (componentVal == 'Running.'):    
                    return True
                elif (component == 'Type') and (componentVal == 'AC'):    
                    return True
                else:
                    return componentVal
        
            except:
                helpers.log("Could not get the rest output.see log for errors\n")
                return  False
           
            