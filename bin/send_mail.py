#!/usr/bin/env python

import os
import sys
import httplib2
import json
import argparse

# Determine BigRobot path(s) based on this executable (which resides in
# the bin/ directory.
bigrobot_path = os.path.dirname(__file__) + '/..'
exscript_path = bigrobot_path + '/vendors/exscript/src'

sys.path.insert(0, bigrobot_path)
sys.path.insert(1, exscript_path)

import autobot.helpers as helpers


class SendMail(object):
    def __init__(self, sender, receiver, subject, message=None):
        self._sender = sender
        self._receiver = receiver
        self._subject = subject
        self._message = message

    def service_url(self):
        base_url = helpers.bigrobot_config_rest_services()['send_mail']['url']
        return base_url + "message"

    def headers(self):
        return {
            'Content-Type': 'application/json'
            }

    def send(self, message=None):
        if message:
            self._message = message
        h = httplib2.Http()
        body = json.dumps({
            "from": self._sender,
            "to": self._receiver,
            "subject": self._subject,
            "message_body": self._message,
            })
        resp, content = h.request(
            self.service_url(),
            headers=self.headers(),
            method="POST",
            body=body,
            )

        # resp['status']: 201 (success in sending email)
        return resp, content


def prog_args():
    descr = """
Send an email. Example:

% ./send_mail.py \\
        --sender vui.le@bigswitch.com \\
        --receiver bigrobot_stats_collection@bigswitch.com \\
        --subject "Dashboard stats collected for 'bvs master #2806' - suite 123" \\
        --message "test suites: xyz executed"
"""
    parser = argparse.ArgumentParser(
                        prog='send_mail',
                        formatter_class=argparse.RawDescriptionHelpFormatter,
                        description=descr)
    parser.add_argument('--sender', required=True,
                        help=("The sender, e.g., 'vui.le@bigswitch.com'"))
    parser.add_argument('--receiver', required=True,
                        help=("The receiver, e.g., 'bigrobot_stats_collection@bigswitch.com'"))
    parser.add_argument('--subject', required=True,
                        help=("The email subject line'"))
    parser.add_argument('--message', required=True,
                        help=("The message body"))
    _args = parser.parse_args()
    return _args


def send_mail():
    args = prog_args()
    s = SendMail(sender=args.sender,
                 receiver=args.receiver,
                 subject=args.subject,
                 )
    response, _ = s.send(message=args.message)
    if int(response['status']) == 201:
        print "Message sent successfully."
        sys.exit(0)
    else:
        print "Send mail error.\n%s" % helpers.prettify(response)
        sys.exit(1)


if __name__ == '__main__':
    send_mail()
