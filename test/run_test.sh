#!/bin/sh
test_suite=test_bcf_events.py
nosetests -vv --nocapture --nologcapture $test_suite
