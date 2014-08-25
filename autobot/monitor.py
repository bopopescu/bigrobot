import threading
import autobot.helpers as helpers


class Monitor(object):
    """
    A generic monitor for executing timer-based tasks.
    """
    def __init__(self, name, init_timer=10, timer=5, callback_task=None):
        """
        Parameters:
          name - str, name for the task
          init_timer - int (in seconds), the initial timer before executing
               the task
          timer - int (in seconds), the amount of time to wait until the next
               execution
        """
        self._thread = None
        self._name = name
        self._init_timer = int(init_timer)
        self._timer = int(timer)
        self._callback_task = callback_task
        self._counter = 0
        self._has_lock = False
        self.initial_on()

    def _print(self, msg):
        print msg
        helpers.log(msg, level=2)

    def _start_daemon_thread(self, timer, callback):
        thread = threading.Timer(timer, callback)

        # allows thread to be interrupted (thread doesn't block the
        # main program from exiting)
        thread.setDaemon(True)

        thread.start()
        return thread

    def initial_on(self):
        self._counter += 1
        helpers.log("Test Monitor '%s' - enabling (%s sec initial timer)"
                    % (self.name(), self._init_timer))
        self._thread = self._start_daemon_thread(self._init_timer, self.on)

    def on(self, user_invoked=False):
        """
        Execute the callback task and set the timer for future execution.
        """

        if user_invoked:
            # Make sure if it's already on then turn it off first before
            # turning it on again.
            self.off()

        self._has_lock = True
        self._counter += 1
        self._print("%s - Test Monitor '%s' - running task #%s (timer=%s)"
                    % (helpers.ts_logger(),
                       self.name(),
                       self.counter(),
                       self._timer))
        if self._callback_task:
            self._callback_task()
        self._thread = self._start_daemon_thread(self._timer, self.on)
        self._has_lock = False

    def off(self):
        max_count = 5
        sec = 5
        if self._thread:
            count = 0
            while self.has_lock() and count < max_count:
                count += 1
                helpers.log("Test Monitor '%s' - found lock on task."
                            " Sleeping for %s before disabling (count=%s)."
                            % (self.name(), sec, count))
                helpers.sleep(sec)
            helpers.log("Test Monitor '%s' - disabling (%s total events)"
                        % (self.name(), self.counter()))
            self._thread.cancel()
            self._thread = None  # reset

    def name(self):
        return self._name

    def counter(self):
        return self._counter

    def has_lock(self):
        return self._has_lock
