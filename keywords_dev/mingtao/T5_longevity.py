import autobot.helpers as helpers
import autobot.test as test
import re
 
class T5_longevity(object):
# This is for all the common function   - Mingtao
    def __init__(self):
        pass

 


#########################  end of commit   ######################
 
  



    def cli_add_user(self,user='user1',passwd='adminadmin'):
        '''
          cli add user to the system, can only run at master
          Author: Mingtao
          input:   user = username,  passwd  = password                                       
          usage:   
          output:   True                            
        '''
  
        t = test.Test()
        c = t.controller('master')
        helpers.log('INFO: Entering ==> cli_add_user ')
        t = test.Test()   
        c.config('user '+user) 
        c.send('password' )
        c.expect('Password: ')        
        c.send(passwd)
        c.expect('Re-enter:')
        c.send(passwd)                
        c.expect()        
        return True     



    def cli_group_add_users(self,group=None,user=None):
        '''  
          cli add user to group, can only run at master
          Author: Mingtao
          input:   group  - if group not give, will user admin
                  user    - if user not given, will add all uers                             
          usage:   
          output:   True                            
        '''  
        t = test.Test()
        c = t.controller('master')
        helpers.log('INFO: Entering ==> cli_add_user ')    
        if group is None:
            group = 'admin'         
        c.config('group '+ group) 
        if user:
            c.config('associate user '+user)
        else: 
            c.config('show running-config user | grep user')   
            content = c.cli_content()
            temp = helpers.strip_cli_output(content)
            temp = helpers.str_to_list(temp)
            helpers.log("********new_content:************\n%s" % helpers.prettify(temp))
            temp.pop(0)
            helpers.log("********new_content:************\n%s" % helpers.prettify(temp))            
            for line in temp:
                line = line.lstrip()
                user = line.split(' ')[1]
                helpers.log('INFO: user is: %s ' % user)  
                if user == 'admin':
                    continue   
                else:                        
                    c.config('associate user '+user)
            
            return True    


    def rest_get_user_group(self,user):
        '''  
          get the group for a user, can only run at master
          Author: Mingtao
          input:   
                  user    - if user not given, will add all uers                             
          usage:   
          output:   group                          
        '''
        t = test.Test()
        c = t.controller('master')
        helpers.log('INFO: Entering ==> rest_get_user_group ')
   
        
        url = '/api/v1/data/controller/core/aaa/group[user="%s"]'  % user
        c.rest.get(url)
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())

        if(c.rest.content()):
            helpers.log('INFO: content is: %s ' %c.rest.content())        

            if user in c.rest.content()[0]['user']:    
                helpers.log('INFO: inside  ')        
                return  c.rest.content()[0]['name']          
        else:
            helpers.test_failure(c.rest.error())      


    def cli_delete_user(self,user):
        '''  
          delete users can only run at master
          Author: Mingtao
          input:  user                        
          usage:   
          output:   True                            
           
        '''
  
        t = test.Test()
        c = t.controller('master')
        helpers.log('INFO: Entering ==> cli_delete_user ')
        c.config('no user '+ user)    
        return True
  

    def T5_cli_clean_all_users(self,user=None ):
        ''' 
        delete all users except admin
          Author: Mingtao
          input:  user                        
          usage:   
          output:   True                                                
        '''
  
        t = test.Test()
        c = t.controller('master')
        helpers.log('INFO: Entering ==> cli_delete_user ')
      
        if user: 
            c.config('no user '+ user)     
            return True
        else:
            c.config('show running-config user | grep user')   
            content = c.cli_content()
            temp = helpers.strip_cli_output(content)
            temp = helpers.str_to_list(temp)
            helpers.log("********new_content:************\n%s" % helpers.prettify(temp))
            temp.pop(0)
            helpers.log("********new_content:************\n%s" % helpers.prettify(temp))            
            for line in temp:
                line = line.lstrip()
                user = line.split(' ')[1]
                helpers.log('INFO: user is: %s ' % user)  
                if user == 'admin':
                    continue   
                else:                        
                    c.config('no user '+ user)
                            
            return True    




#############################  below are for  cli walk ####################

    def cli_exec_walk(self, string='', file_name=None, padding=''):
        t = test.Test()
        c = t.controller('master')
        c.cli('')
        helpers.log("********* Entering cli_exec_walk ----> string: %s, file name: %s" % (string, file_name))
        if string =='':
            cli_string = '?' 
        else: 
            cli_string = string + ' ?'
        c.send(cli_string, no_cr=True)
        c.expect(r'[\r\n\x07][\w-]+[#>] ')
        content = c.cli_content()
        temp = helpers.strip_cli_output(content)
        temp = helpers.str_to_list(temp)
        helpers.log("********new_content:************\n%s" % helpers.prettify(temp))
        c.send(helpers.ctrl('u'))
        c.expect()
        c.cli('')
        
        string_c = string
        helpers.log("string for this level is: %s" % string_c)
        helpers.log("The length of string: %d" % len(temp))

        if file_name:
            helpers.log("opening file: %s" % file_name)
            fo = open(file_name, 'a')
            lines = []
            lines.append((padding + string))
            lines.append((padding + '----------'))            
            for line in temp:
                lines.append((padding + line))
            lines.append((padding + '=================='))             
            content = '\n'.join(lines)
            fo.write(str(content))
            fo.write("\n")
            
            fo.close()

        num = len(temp)
        padding = "   " + padding
        for line in temp:
            string = string_c
            helpers.log(" line is - %s" % line)
            line = line.lstrip()
            keys = line.split(' ')
            key = keys.pop(0)
            helpers.log("*** key is - %s" % key)            
            if re.match(r'For', line) or line == "Commands:":
                helpers.log("Ignoring line - %s" % line)
                num = num - 1
                continue
            if key == "debug" or key == "reauth" or key == "echo" or key == "help" or key == "history" or key == "logout" or key == "ping" or key == "show" or key == "watch":
                helpers.log("Ignore line %s" % line)
                num = num - 1
                continue
            if re.match(r'^<.+', line) and not re.match(r'^<cr>', line):
                helpers.log("Ignoring line - %s" % line)
                num = num - 1
                continue
 
            if key == '<cr>':
                helpers.log(" complete CLI show command: ******%s******" % string)
                c.cli(string)
                if num == 1:
                    helpers.log("AT END: ******%s******" % string)                    
                    return string
            else:
                string = string + ' ' + key
                helpers.log("key - %s" % (key))
                helpers.log("***** Call the cli walk again with  --- %s" % string)
                self.cli_exec_walk(string,file_name, padding)
                

    def cli_enable_walk(self, string='', file_name=None, padding=''):
        t = test.Test()
        c = t.controller('master')
        c.enable('')
        helpers.log("********* Entering CLI show  walk with ----> string: %s, file name: %s" % (string, file_name))
        if string =='':
            cli_string = '?' 
        else: 
            cli_string = string + ' ?'
        c.send(cli_string, no_cr=True)
        c.expect(r'[\r\n\x07][\w-]+[#>] ')
        content = c.cli_content()
        temp = helpers.strip_cli_output(content)
        temp = helpers.str_to_list(temp)
        helpers.log("******new_content:\n%s" % helpers.prettify(temp))
        c.send(helpers.ctrl('u'))
        c.expect()

        string_c = string
        helpers.log("string for this level is: %s" % string_c)
        helpers.log("The length of string: %d" % len(temp))

        if file_name:
            helpers.log("opening file: %s" % file_name)
            fo = open(file_name, 'a')
            lines = []
            lines.append((padding + string))
            lines.append((padding + '----------'))            
            for line in temp:
                lines.append((padding + line))
            lines.append((padding + '=================='))             
            content = '\n'.join(lines)
            fo.write(str(content))
            fo.write("\n")
            
            fo.close()

        num = len(temp)
        padding = "   " + padding
        for line in temp:
            string = string_c
            helpers.log(" line is - %s" % line)
            line = line.lstrip()
            keys = line.split(' ')
            key = keys.pop(0)
            helpers.log("*** string is - %s" % string)                     
            helpers.log("*** key is - %s" % key)          
            if re.match(r'For', line) or line == "Commands:"or re.match(r'All', line):
                helpers.log("Ignoring line - %s" % line)
                num = num - 1
                continue
            if re.match(r'^<.+', line) and not re.match(r'^<cr>', line):
                helpers.log("Ignoring line - %s" % line)
                num = num - 1
                continue
            if string == "show running-config fabric port-group":
                helpers.log("GR - BSC-4724 Ignoring line - %s" % line)
                num = num - 1
                continue
            if string == "show running-config switch":
                helpers.log("GR - BSC-4725 Ignoring line - %s" % line)
                num = num - 1
                continue
            if string == "show running-config tenant":
                helpers.log("GR - BSC-4727 Ignoring line - %s" % line)
                num = num - 1
                continue
            if string == "show switch":
                helpers.log("GR - BSC-4729 Ignoring line - %s" % line)
                num = num - 1
                continue
            if string == "show test-packet-path":
                helpers.log("GR -   Ignoring line - %s" % line)
                num = num - 1
                continue
            
            if re.match(r'.*show fabric interface.*',string) and key == "switch" :
                helpers.log("INFO:  within show fabric interface - %s" % line)
                num = num - 1
                continue               
            if re.match(r'.*show fabric lacp.*',string) and key == "switch" :
                helpers.log("INFO:  within show fabric lacp - %s" % line)
                num = num - 1
                continue               
            if re.match(r'.*show stats interface-stats.*',string) and key == "interface" :
                helpers.log("INFO:  within show stats interface-stats - %s" % line)
                num = num - 1
                continue    
            if re.match(r'.*show stats interface-stats.*',string) and key == "switch" :
                helpers.log("INFO:  within show stats interface-stats - %s" % line)
                num = num - 1
                continue    
            if re.match(r'.*show stats vns-stats.*',string) and key == "tenant" :
                helpers.log("INFO:  within show stats interface-stats - %s" % line)
                num = num - 1
                continue            
      
            
            if key == '<cr>':
                helpers.log(" complete CLI show command: ******%s******" % string)
                if re.match(r'boot', string):
                    helpers.log("Ignoring line - %s" % line)                
                continue
                
                c.enable(string)
                if num == 1:
                    return string
            else:
                string = string + ' ' + key
                helpers.log("key - %s" % (key))
                helpers.log("***** Call the cli walk again with  --- %s" % string)
                self.cli_enable_walk(string, file_name, padding)


    def cli_config_walk(self, string='', file_name=None, padding=''):
        t = test.Test()
        c = t.controller('master')
        c.config('')
        helpers.log("********* Entering CLI show  walk with ----> string: %s, file name: %s" % (string, file_name))
        if string =='':
#            c.config('exit')
            cli_string = '?' 
        else: 
            cli_string = string + ' ?'
        c.send(cli_string, no_cr=True)
        c.expect(r'[\r\n\x07].+[#>] ')
 
        content = c.cli_content()
        temp = helpers.strip_cli_output(content)
        temp = helpers.str_to_list(temp)
        helpers.log("******new_content:\n%s" % helpers.prettify(temp))
        c.send(helpers.ctrl('u'))
        c.expect()
        c.config('')
        string_c = string
        helpers.log("string for this level is: %s" % string_c)
        helpers.log("The length of string: %d" % len(temp))

        if file_name:
            helpers.log("opening file: %s" % file_name)
            fo = open(file_name, 'a')
            lines = []
            lines.append((padding + string))
            lines.append((padding + '----------'))            
            for line in temp:
                lines.append((padding + line))
            lines.append((padding + '=================='))             
            content = '\n'.join(lines)
            fo.write(str(content))
            fo.write("\n")
            
            fo.close()

        num = len(temp)
        padding = "   " + padding
        for line in temp:
            string = string_c
            line = line.lstrip()
            helpers.log(" line is - %s" % line)
            if re.match(r'For', line) or line == "Commands:":
                helpers.log("Ignoring line - %s" % line)
                num = num - 1
                continue
            if re.match(r'All', line)  :
                helpers.log("Ignoring line - %s" % line)
                num = num - 1
                break
            
            if re.match(r'^<.+', line) and not re.match(r'^<cr>', line):
                helpers.log("Ignoring line - %s" % line)
                num = num - 1
                continue
 
            keys = line.split(' ')
            key = keys.pop(0)
            helpers.log("*** key is - %s" % key)
            if key == '<cr>':
                helpers.log(" complete CLI show command: ******%s******" % string)
                c.config(string)
                if num == 1:
                    return string
            else:
#                helpers.log(" string before add key --- ******%s******" % string )
                string = string + ' ' + key
                helpers.log("key - %s" % (key))
                helpers.log("***** Call the cli walk again with  --- %s" % string)
                self.cli_config_walk(string, file_name, padding)


### this is Tomaz's API
    def cli_copy_running_config_to_file(self,node='master',filename='config_save' ):
        ''' Function to copy running config to regular file
        via CLI
        Input: Filename
        Output: True if successful, False otherwise
        '''
        helpers.test_log("Running command:\ncopy running-config %s" % filename)
        t = test.Test()
        c = t.controller(node)
        try:
            c.config("copy running-config %s" % filename)
            assert "Error" not in c.cli_content()
        except:
            helpers.test_log(c.cli_content())
            return False
        else:
            return True

    def bash_ls(self, node, path):
        """
        Execute 'ls -l <path>' on a device.

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
            - fields[5] = date
            - fields[6] = time
        """
        t = test.Test()
        n = t.node(node)
        content = n.bash('ls -l %s' % path)['content']
        lines = helpers.strip_cli_output(content, to_list=True)

        # Output:
        # total 691740
        # -rw-r--r-- 1 root root 708335092 2014-03-03 13:08 controller-upgrade-bvs-2.0.5-SNAPSHOT.pkg
        # -rw-r--r-- 1 bsn  bsn          0 2014-03-12 10:05 blah blah.txt

        # Strip first line ('total <nnnnn>')
        lines = lines[1:]
        helpers.log("lines: %s" % helpers.prettify(lines))

        files = {}

        for line in lines:
            fields = line.split()
            # fields[7]+ contains filename (may have spaces in name)
            filename = ' '.join(fields[7:])
            files[filename] = fields[0:6]

        helpers.log("files: %s" % helpers.prettify(files))
        return files



    def bash_ntpq(self, node):
        """
        Execute 'ntpq -pn' on a device.
        Author:    Mingtao
        Inputs:
        | node | reference to switch/controller/host as defined in .topo file |
  
        Example:
        Return Value:
        - Dictionary with remote as key. Value contains offset
          {'*204.2.134.164': {'offset': '-0.225'}, '+74.120.8.2': {'offset': '3.819'}}
        """
        t = test.Test()
        n = t.node(node)
        content = n.bash('ntpq -pn' )['content']
        lines = helpers.strip_cli_output(content, to_list=True)
        lines = lines[2:]
        helpers.log("lines: %s" % helpers.prettify(lines))

        ntpinfo = {}

        for line in lines:
            fields = line.split()
            remote = fields[0]
            helpers.log("lines: %s  - field:  %s" % (line, fields))  
            ntpinfo[remote]={}
            ntpinfo[remote]['offset']=fields[8] 
        helpers.log("INFO:  ntpinfo is \n  %s" % helpers.prettify(ntpinfo))                                     
        return ntpinfo
    
    
    def check_ntp_whitin(self, node,tolerance='250' ):
        """
        verify ntp offset whin range
        Author:    Mingtao
        Example:   check_ntp_whitin   c1   250
        """
        ntpinfo = self.bash_ntpq(node)           
        helpers.log("ntp info : %s" % helpers.prettify(ntpinfo))
        for ntp in ntpinfo:
            offset =  ntpinfo[ntp]['offset']
            helpers.log("INFO:  offset for remote %s  is  %s - %.3f" % (ntp, offset,float(offset)  ))  
            if float(ntpinfo[ntp]['offset']) > 250  or float(ntpinfo[ntp]['offset']) < -250:
                helpers.log("ERROR: %s  is more than 250 ms" % ntpinfo[ntp]['offset'] )
                return False
                                     
        return True


    def rest_delete_cluster_nodes(self,node='slave'):
        '''  
           delete 
           output:       
            TBD
    
        '''
        t = test.Test()
        c = t.controller('master')
        helpers.log('INFO: Entering ==> rest_get_node_role ')
   
        
        url = '/api/v1/data/controller/cluster'  
        c.rest.get(url)
        if not c.rest.status_code_ok():
            helpers.test_failure(c.rest.error())

        if(c.rest.content()):
            num = len(c.rest.content()[0]['status']['nodes'])
            helpers.log("INFO: There are %d of controller in cluster" %  num)
            for index in range(0,num):
                
                hostname = c.rest.content()[0]['status']['nodes'][index]['hostname']
                helpers.log("INFO: hostname is: %s" % hostname )
                  
            return num
        else:
            helpers.test_failure(c.rest.error())      



    def cli_scp_file (self,remote,node='master',local='running-config',passwd='bsn',flag='from'):
        '''cli scp file
            copy to/from 
            usage:    cli_scp_file  bsn@qa-kvm-32:/home/mingtao/config_new  config_new    
                      cli_scp_file  bsn@qa-kvm-32:/home/mingtao/config_new  config_new   adminadmin    to
            output:
              - mingtao
                 
        '''
        t = test.Test()
        c = t.controller(node)                 
        c.enable('')
        if flag == 'to':
            string = 'copy ' +local + ' scp://'+remote 
        if flag == 'from':
            string = 'copy scp://'+ remote + ' ' + local
        
        helpers.log("INFO:  string is: %s " % string )        
        c.send(string)
        c.expect(r'[\r\n].+password: |[\r\n].+(yes/no)?')
        content = c.cli_content()
        helpers.log("*****Output is :\n%s" % content)
        if re.match(r'.*password:.* ', content):
            helpers.log("INFO:  need to provide passwd " )
            c.send(passwd)
        elif re.match(r'.+(yes/no)?', content):
            helpers.log("INFO:  need to send yes, then provide passwd " )
            c.send('yes')
            c.expect(r'[\r\n].+password: ')
            c.send(passwd)
        
        try:
            c.expect(timeout=180)
        except:
            helpers.log('scp failed')
            return False
        else:
            helpers.log('scp completed successfully')
        return True


