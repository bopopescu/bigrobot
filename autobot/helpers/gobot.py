import os


# IS_GOBOT has an initial state of None. It is set to True if environment
# variable IS_GOBOT is set, else False.
IS_GOBOT = None


def is_gobot():
    global IS_GOBOT

    if IS_GOBOT is None:
        if 'IS_GOBOT' in os.environ and os.environ['IS_GOBOT'].lower() == "true":
            IS_GOBOT = True
        else:
            IS_GOBOT = False

    return IS_GOBOT
