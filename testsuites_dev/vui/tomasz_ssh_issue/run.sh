#!/bin/sh -x
unset BIGROBOT_TESTBED
unset BIGROBOT_PARAMS_INPUT
AAA_TYPE=TACACS BIGROBOT_SUITE=t6_aaa_management gobot test
