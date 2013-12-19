#!/usr/bin/env python

import os
import sys

os.environ['IS_GOBOT'] = 'True'

if os.environ.has_key("BIGROBOT_PATH") is False:
    print("Error: Please set the environment variable BIGROBOT_PATH.")
    sys.exit(1)
autobot_path = os.environ["BIGROBOT_PATH"]
sys.path.append(autobot_path)

import autobot.helpers as helpers


def main():
    helpers.log("Testing 1 2 3")

if __name__ == '__main__':
    main()

