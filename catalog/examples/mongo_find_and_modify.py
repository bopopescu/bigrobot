#!/usr/bin/env python

from pymongo import MongoClient

db_server = 'qadashboard-mongo'
db_port = 27017

client = MongoClient(db_server, db_port)
db = client.test_catalog
testcases = db.test_cases

tc = testcases.find_and_modify(
        query={ "name": "add tenant of same name - 1111",
                "product_suite" : "T5_t5_app_cli",
                "starttime_datestamp" : "2014-05-28" },
        update={ "$set": { "status": "PASS" } },
        new=True,
        upsert=True
        )

if tc:
    print "*** SUCCESS! %s" % tc
else:
    print "Did not find an entry"

