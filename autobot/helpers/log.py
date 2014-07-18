import os
import sys
import re
import errno
import datetime
import inspect
import getpass
import logging
import gobot
from pytz import timezone
from robot.api import logger as robot_logger


class Log(object):
    """
    Singleton logger. Autobot applications should write to a common log file.
    Use Robot Framework's logger facility if running in Robot environment
    (env IS_GOBOT=True). Else use Python's logging facility.

    If IS_GOBOT is not True, do:
      export AUTOBOT_LOG=/path/to/bigrobot.log
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
            os.environ["AUTOBOT_LOG"] = Log.log_file

            # Make sure path to log file exists
            path_name = os.path.dirname(Log.log_file)
            self.mkdir_p(path_name)

            if not gobot.is_gobot():
                default_level = logging.DEBUG
                logging.basicConfig(format=self.ts_logger() + " - %(levelname)s : %(message)s",
                                    filename=Log.log_file,
                                    level=default_level)

    def ts_logger(self):
        """
        Return the current timestamp in local time (string format which is
        compatible with the Robot Framework logger format)
        e.g., 20140429 15:01:51.039
        """
        _TZ = timezone("America/Los_Angeles")
        local_datetime = datetime.datetime.now(_TZ)
        return local_datetime.strftime("%Y%m%d %H:%M:%S.%f")[:-3]

    def mkdir_p(self, path):
        """
        Works like 'mkdir -p' (create intermediate directories as required.
        Borrowed from
        http://stackoverflow.com/questions/600268/mkdir-p-functionality-in-python
        """
        try:
            os.makedirs(path)
        except OSError as exc:  # Python >2.5
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else: raise

    def _format_log(self, s, level):
        if level:
            level += 1
            frm = inspect.stack()[level]
            mod = inspect.getmodule(frm[0])
            # filename = os.path.basename(frm[1])
            lineno = frm[2]
            funcname = frm[3]

            if re.match(r'^(<module>)$', funcname):
                funcname = ''
            else:
                funcname = '.' + funcname

            s = s.rstrip()
            # return "[%s:%s%s:%d] %s\n" % (filename, mod.__name__, funcname, lineno, s)
            return "[%s%s:%d] %s\n" % (mod.__name__, funcname, lineno, s)
        else:
            return "%s\n" % s

    def log(self, s, level=1, to_stderr=False, log_level='info'):
        """
        Write to INFO log by default.
        """
        level += 1
        log_level = log_level.lower()
        if log_level == 'info':
            self.info(s, level=level, also_console=to_stderr)
        elif log_level == 'warn':
            self.warn(s, level=level)
        elif log_level == 'debug':
            self.debug(s, level=level)
        else:
            self.trace(s, level=level)  # last resort

    def info(self, s, level=1, also_console=False):
        msg = self._format_log(s, level)
        if not gobot.is_gobot():
            if also_console:
                sys.stderr.write(s + '\n')
            logging.info(msg.strip())
        else:
            robot_logger.info(msg, also_console=also_console)

    def warn(self, s, level=1):
        msg = self._format_log(s, level)
        if not gobot.is_gobot():
            logging.warn(msg.strip())
        else:
            robot_logger.warn(msg)

    def debug(self, s, level=1):
        msg = self._format_log(s, level)
        if not gobot.is_gobot():
            logging.debug(msg.strip())
        else:
            robot_logger.debug(msg)

    def trace(self, s, level=1):
        msg = self._format_log(s, level)
        if not gobot.is_gobot():
            # Python logging module doesn't support trace log level, so
            # improvise with debug.
            logging.debug("TRACE: " + msg.strip())
        else:
            robot_logger.trace(msg)
