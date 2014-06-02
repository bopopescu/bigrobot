#!/usr/bin/env python
"""
Service startup:
  $ ./send_mail.py --host 0.0.0.0

Usage:
  $ curl -i -H "Content-Type: application/json" -X POST \
       -d '{"from":"root@jenkins-w6.bigswitch.com",
            "to":"vui.le@bigswitch.com",
            "subject":"This is a test",
            "message_body":"Testing 1 2 3"}' \
       http://qarest.bigswitch.com:5000/message
"""

import os
import sys
from flask import Flask, jsonify, abort, make_response, request
from flask.ext.runner import Runner
import robot


# Determine BigRobot path(s) based on this executable (which resides in the
# bin/ directory.
bigrobot_path = os.path.dirname(__file__) + '/..'
exscript_path = bigrobot_path + '/vendors/exscript/src'

sys.path.insert(0, bigrobot_path)
sys.path.insert(1, exscript_path)

import autobot.helpers as helpers
# import autobot.devconf as devconf

helpers.set_env('IS_GOBOT', 'False')
helpers.set_env('AUTOBOT_LOG', '/tmp/myrobot.log')

app = Flask(__name__)
runner = Runner(app)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route('/message', methods=['POST'])
def message_send():
    if not request.json or not 'to' in request.json:
        abort(400)
    message = {
        'from': request.json.get('from', ''),
        'to': request.json['to'],
        'subject': request.json.get('subject', "No subject"),
        'message_body': request.json.get('message_body', ""),
        }
    helpers.send_mail(message)
    return jsonify({'message': message}), 201


if __name__ == '__main__':
    runner.run()
    # app.run(host='0.0.0.0')
