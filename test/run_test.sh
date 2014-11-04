#!/bin/sh
test_suite=test_t5_event_alpha.py
nosetests -vv --nocapture --nologcapture $test_suite
