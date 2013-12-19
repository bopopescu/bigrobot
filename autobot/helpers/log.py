import os
import sys
import re
import inspect
import getpass
import gobot


class Log(object):
    """
    Singleton logger. Autobot applications should write to a common log file. 
    """
    log_file = None
    is_gobot = None

    def __init__(self, name=None):
        """
        Get log file name,
          from env AUTOBOT_LOG if exists,
          else from name argument if exists,
          else assign default: /tmp/autobot_<user>.log.  
        """
        if os.environ.has_key("AUTOBOT_LOG"):
            Log.log_file = os.environ["AUTOBOT_LOG"]

        if Log.log_file is None:
            if name is None:
                user = getpass.getuser()
                Log.log_file = '/tmp/autobot_%s.log' % user
            else:
                Log.log_file = name

    def log(self, s, level=1):
        """
        Write to log file.
        """        
        if not gobot.is_gobot():
            if Log.log_file is None:
                # Probably impossible to reach here...
                raise RuntimeError("You must specify an Autobot log file")
            
            f = open(Log.log_file, "a")
        else:
            # In the Robot Framework environment, we simply write log messages
            # to stdout
            f = sys.stdout
        
        frm = inspect.stack()[level]
        mod = inspect.getmodule(frm[0])
        filename = os.path.basename(frm[1])
        lineno = frm[2]
        funcname = frm[3]

        if re.match(r'^(<module>)$', funcname):
            funcname = ''
        else:
            funcname = '.' + funcname

        s = s.rstrip()
        f.write("[%s:%s%s:%d] %s\n" %
                (filename, mod.__name__, funcname, lineno, s))
        
        if not gobot.is_gobot():
            f.close()
