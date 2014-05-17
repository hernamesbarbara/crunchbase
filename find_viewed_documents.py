#!/usr/bin/env python
# -*- coding: utf-8 -*- 
"""find_viewed_documents.py
"""
import pandas as pd
import sys
import os
import ujson as json
from pymongo import MongoClient
import datetime

MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/')
print MONGO_URI
db = MongoClient(MONGO_URI)['yhat']

# def find_entity(permalink):
#     try: 
#         doc = db.entities.find_one({"permalink": permalink}, {"_id": 1})
#     except:
#         doc = None
#     return doc

# def already_fetched(record):
#     permalink = record['permalink']
#     return find_entity(permalink) is not None

# # find permalink records which either (A) do not have the `seen` key
# # or (B) have the `seen` key but its value is False
# q = { "$or": [ { "seen": False }, { "seen": {"$exists": False} } ] }

# total = db.permalinks.count()
# unprocessed = db.permalinks.find(q).count()
# counter = 0
# for permalink in db.permalinks.find(q).batch_size(100):
#     counter += 1
#     timestamp = datetime.datetime.utcnow()
#     if counter % 25 == 0:
#         print "{}: Permalink: {} of {} unprocessed of {} total".format(timestamp.isoformat(), counter, unprocessed, total)
#     if already_fetched(permalink):
#         db.permalinks.update({"_id": permalink["_id"]}, {"$set": {"seen": True}}, upsert=False)


# unique_types = db.crunchbase.distinct('type')
