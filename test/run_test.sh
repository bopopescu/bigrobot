#!/bin/sh
test_suite=test_bcf_events.py
#test_suite=test_bcf_simple.py
#test_suite=test_simple.py
nosetests -vv --nocapture --nologcapture $test_suite
