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
    (env IS_GOBOT=True). The log file is specified via the 'outputdir'
    parameter in Robot's interface - robot.run().

    Otherwise use Python's logging facility if IS_GOBOT is not True.
    User should set the env AUTOBOT_LOG as followed:
      export AUTOBOT_LOG=/path/to/bigrobot.log
    """
    log_file = None
    autobot_logger = None

    def __init__(self, name=None):
        """
        Get log file name,
          from env AUTOBOT_LOG if exists,
          else from name argument if exists,
          else assign default: /tmp/autobot_<user>.log.
        """
        if gobot.is_gobot() == False:
            self.set_autobot_log(name)

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

    def create_log_dir(self, path):
        # Make sure path to log file exists
        self.mkdir_p(os.path.dirname(path))


    def set_autobot_log(self, name=None):
        has_changed_filename = False
        init_state = True
        if Log.log_file:
            init_state = False
        if os.environ.has_key("AUTOBOT_LOG"):
            if Log.log_file != os.environ["AUTOBOT_LOG"]:
                Log.log_file = os.environ["AUTOBOT_LOG"]
                has_changed_filename = True
        elif name:
            if Log.log_file != name:
                Log.log_file = name
                has_changed_filename = True
        else:
            user = getpass.getuser()
            Log.log_file = '/tmp/autobot_%s.log' % user
            has_changed_filename = True

        if init_state:
            self.create_log_dir(Log.log_file)

            Log.autobot_logger = logging.getLogger()
            Log.autobot_logger.setLevel(logging.DEBUG)

            formatter = logging.Formatter(self.ts_logger() + " - %(levelname)s : %(message)s")
            file_handler = logging.FileHandler(Log.log_file)
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            Log.autobot_logger.addHandler(file_handler)

            print("****** AUTOLOG_LOG: Created log file: %s" % Log.log_file)
        elif has_changed_filename:
            # We want to send logs to a new file. With Python logging module,
            # you have to reassign the log handler. See:
            # http://stackoverflow.com/questions/5296130/restart-logging-to-a-new-file-python
            self.create_log_dir(Log.log_file)

            Log.autobot_logger.handlers[0].stream.close()
            Log.autobot_logger.removeHandler(Log.autobot_logger.handlers[0])

            formatter = logging.Formatter(self.ts_logger() + " - %(levelname)s : %(message)s")
            file_handler = logging.FileHandler(Log.log_file)
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            Log.autobot_logger.addHandler(file_handler)

            print("****** AUTOLOG_LOG: Changed the log file: %s" % Log.log_file)

    def ts_logger(self):
        """
        Return the current timestamp in local time (string format which is
        compatible with the Robot Framework logger format)
        e.g., 20140429 15:01:51.039
        """
        _TZ = timezone("America/Los_Angeles")
        local_datetime = datetime.datetime.now(_TZ)
        return local_datetime.strftime("%Y%m%d %H:%M:%S.%f")[:-3]

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
        if gobot.is_gobot() == False:
            self.set_autobot_log()
            if also_console:
                sys.stderr.write(s + '\n')
            logging.info(msg.strip())
        else:
            robot_logger.info(msg, also_console=also_console)

    def warn(self, s, level=1):
        msg = self._format_log(s, level)
        if gobot.is_gobot() == False:
            self.set_autobot_log()
            logging.warn(msg.strip())
        else:
            robot_logger.warn(msg)

    def debug(self, s, level=1):
        msg = self._format_log(s, level)
        if gobot.is_gobot() == False:
            self.set_autobot_log()
            logging.debug(msg.strip())
        else:
            robot_logger.debug(msg)

    def trace(self, s, level=1):
        msg = self._format_log(s, level)
        if gobot.is_gobot() == False:
            self.set_autobot_log()
            # Python logging module doesn't support trace log level, so
            # improvise with debug.
            logging.debug("TRACE: " + msg.strip())
        else:
            robot_logger.trace(msg)
