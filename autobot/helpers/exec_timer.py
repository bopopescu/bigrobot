import time

class ExecTimer(object):
    """
    Track the execution time.
    """
    def __init__(self):
        """
        Start the clock once the object is instantiated.
        """
        self.start_time = time.time()

    def stop(self):
        """
        Stop the clock. Return the execution time in seconds.
        """
        self.exec_time = time.time() - self.start_time
        return self.exec_time
