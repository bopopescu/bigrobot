import os
import sys
import re
import inspect
import getpass
import gobot
from robot.api import logger


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

    def _format_log(self, s, level):
        level += 1
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
        return "[%s:%s%s:%d] %s\n" % (filename, mod.__name__, funcname, lineno, s)

    def log(self, s, level=1):
        """
        Write to INFO log.
        """        
        msg = self._format_log(s, level)
        
        if not gobot.is_gobot():
            if Log.log_file is None:
                # Probably impossible to reach here...
                raise RuntimeError("You must specify an Autobot log file")
            
            f = open(Log.log_file, "a")
            f.write(msg)
            f.close()
        else:
            logger.info(msg)

    # Alias
    info = log

    def warn(self, s, level=1):
        msg = self._format_log(s, level)
        logger.warn(msg)

    def debug(self, s, level=1):
        msg = self._format_log(s, level)
        logger.debug(msg)

    def trace(self, s, level=1):
        msg = self._format_log(s, level)
        logger.trace(msg)
