import autobot.helpers as helpers


def warn(msg):
    print "\n"
    print "WARNING: " + msg

def formatted_error_exit(msg):
    print "\n"
    helpers.error_exit(msg, 1)

