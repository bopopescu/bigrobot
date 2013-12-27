import autobot.helpers as helpers
import autobot.test as test
from Exscript.protocols import SSH2
from Exscript import Account, Host
import subprocess

class BsnSwitchCommon(object):

    def __init__(self):
        t = test.Test()
        c = t.controller()
        url = '%s/auth/login' % c.base_url
        helpers.log("url: %s" % url)
        result = c.rest.post(url, {"user":"admin", "password":"adminadmin"})
        helpers.log("result: %s" % helpers.to_json(result))
        session_cookie = result['content']['session_cookie']
        c.rest.set_session_cookie(session_cookie)

    def activate_deactivate_controller(self,ip_address,iteration):
        t = test.Test()
        c = t.controller()
        conn = SSH2()
        conn.connect(ip_address)
        conn.login(Account("admin","adminadmin"))
        mycount = 1
        while (mycount<=iteration):
            conn.execute('enable')
            conn.execute('conf t')
            inp = "no controller " + str(c.ip)
            conn.execute(inp)
            conn.execute('end')
            conn.execute('show running-config openflow')
            print conn.response
            helpers.sleep(10)
            conn.execute('conf t')
            inp = "controller " + str(c.ip)
            conn.execute(inp)
            conn.execute('end')
            conn.execute('show running-config openflow')
            print conn.response
            if iteration > mycount :
                mycount=mycount+1
                helpers.sleep(10)
            elif mycount == iteration :
                conn.send('exit\r')
                conn.send('exit\r')
                conn.send('exit\r')
                conn.close()
        return True
    
    def configure_snmp_keyword(self,ip_address,snmpKey,snmpValue):
        t = test.Test()
        conn = SSH2()
        conn.connect(ip_address)
        conn.login(Account("admin","adminadmin"))
        conn.execute('enable')
        conn.execute('conf t')
        input="snmp-server %s %s" % (str(snmpKey),str(snmpValue))
        conn.execute(input)
        conn.send('exit\r')
        conn.send('exit\r')
        conn.send('exit\r')
        conn.close()
        return True

    def configure_snmp_host(self,ip_address,remHostIP,snmpKey,snmpCommunity,snmpPort):
        t = test.Test()
        conn = SSH2()
        conn.connect(ip_address)
        conn.login(Account("admin","adminadmin"))
        conn.execute('enable')
        conn.execute('conf t')
        if snmpKey == "traps" or snmpKey == "trap":
            snmpKey == "traps"
        else:
            snmpKey == "informs"
        input="snmp-server host %s %s %s udp-port %s" % (str(remHostIP),str(snmpKey),str(snmpCommunity),str(snmpPort))
        conn.execute(input)
        conn.send('exit\r')
        conn.send('exit\r')
        conn.send('exit\r')
        conn.close()
        return True

    def enable_snmp(self,ip_address):
        t = test.Test()
        conn = SSH2()
        conn.connect(ip_address)
        conn.login(Account("admin","adminadmin"))
        conn.execute('enable')
        conn.execute('conf t')
        conn.execute("snmp-server enable")
        conn.send('exit\r')
        conn.send('exit\r')
        conn.send('exit\r')
        conn.close()
        return True

    def disable_switch_snmp(self,ip_address):
        t = test.Test()
        conn = SSH2()
        conn.connect(ip_address)
        conn.login(Account("admin","adminadmin"))
        conn.execute('enable')
        conn.execute('conf t')
        conn.execute("no snmp-server enable")
        conn.send('exit\r')
        conn.send('exit\r')
        conn.send('exit\r')
        conn.close()
        return True

    def snmp_show(self,ip_address):
        t = test.Test()
        conn = SSH2()
        conn.connect(ip_address)
        conn.login(Account("admin","adminadmin"))
        conn.execute("show snmp-server")
        return conn.response
    
#   Objective: Execute snmpgetnext from local machine for a particular SNMP OID
#   Input: SNMP Community and OID 
#   Return Value:  return the SNMP Walk O/P
    def snmp_cmd(self,ip_address,snmp_cmd,snmpCommunity,snmpOID):
        t = test.Test()
        url="/usr/bin/%s -v2c -c %s %s %s" % (str(snmp_cmd),str(snmpCommunity),ip_address,str(snmpOID))
        returnVal = subprocess.Popen([url], stdout=subprocess.PIPE, shell=True)
        (out, err) = returnVal.communicate()
        helpers.log("URL: %s Output: %s" % (url, out))
        return out
        
    def snmp_cmd_opt(self,ip_address,snmp_cmd,snmpOpt, snmpCommunity,snmpOID):
        t = test.Test()
        url="/usr/bin/%s  -v2c %s -c %s %s %s" % (str(snmp_cmd),str(snmpOpt),str(snmpCommunity),ip_address,str(snmpOID))
        returnVal = subprocess.Popen([url], stdout=subprocess.PIPE, shell=True)
        (out, err) = returnVal.communicate()
        helpers.log("URL: %s Output: %s" % (url, out))
        return out

    def restart_process(self,ip_address,processName):
        t = test.Test()
        conn = SSH2()
        conn.connect(ip_address)
        conn.login(Account("admin","adminadmin"))
        conn.execute('enable')
        input='debug ofad "help; service ' + str(processName) +  ' restart"'
        conn.execute(input)
        conn.send('logout\r')
        conn.close()
        return True