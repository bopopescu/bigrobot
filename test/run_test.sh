#!/bin/sh
test_suite=test_bcf_simple.py
nosetests -vv --nocapture --nologcapture $test_suite
