#!/usr/bin/env python

from pymongo import MongoClient

db_server = 'qadashboard-mongo'
db_port = 27017

client = MongoClient(db_server, db_port)
db = client.test_catalog
testcases = db.test_cases
tc = testcases.find_one()
print tc

