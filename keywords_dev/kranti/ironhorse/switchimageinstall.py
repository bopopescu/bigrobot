import autobot.helpers as helpers
import autobot.test as test
import os
import sys
import getopt
import hashlib
import Exscript
import time
import telnetlib
import re
from multiprocessing import Process
from Exscript.util.interact import read_login
from Exscript.protocols import SSH2
from Exscript import Account, Host

class switchimageinstall(object):

    def __init__(self):
        pass

    def switchLight_image_install(self,conIp,conPort):
        user = "root"
        passwd = "bsn"
        tn= telnetlib.Telnet(conIp,conPort)
        tn.read_until("login:", 3)
        tn.write(user + "\r\n")
        tn.read_until("password:", 3)
        tn.write(passwd + "\r\n")
        tn.read_until("#", 3)
        tn.write("#atprompt" + "\r\n")
        tn.close()
    
        
        
        
        
        
        
