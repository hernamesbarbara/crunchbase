#!/usr/bin/env python
# -*- coding: utf-8 -*- 
"""migrate_data.py
"""
import pandas as pd
import sys
import os
import ujson as json
from pymongo import MongoClient
import datetime

MONGO_URI1 = os.environ.get('MONGO_URI1', 'mongodb://localhost:27017/')
db_old = MongoClient(MONGO_URI1)["crunchbase"]

MONGO_URI2 = os.environ.get('MONGO_URI2', 'mongodb://localhost:27017/')
db_new = MongoClient(MONGO_URI2)["yhat"]

total = db_old['entities'].count()
counter = 0
for doc in db_old['entities'].find({}).batch_size(100):
    counter += 1
    if counter % 10:
        print "{} of {} done".format(counter, total)
    exists = db_new['crunchbase'].find_one({"type": "entity", "data.permalink": doc["permalink"]}, {"_id": 1, {"data.entity_type": 1}})
    if not exists:
        doc.pop("_id")
        record = {
            "type": "entity",
            "data": doc
        }
        db_new["crunchbase"].save(record)
    else:
        print "skipping {}".format(exists)


