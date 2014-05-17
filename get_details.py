#!/usr/bin/env python
# -*- coding: utf-8 -*- 
"""get_details.py
"""
import pandas as pd
import sys
import os
from crunchbase import Crunchbase
import ujson as json
from pymongo import MongoClient
import datetime

MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/crunchbase')
db = MongoClient(MONGO_URI)['yhat']
crunchbase = db.crunchbase
api = Crunchbase(os.environ['CRUNCHBASE_APIKEY'])

# seen_permalinks = crunchbase.find({"type": "entity"}).distinct("data.permalink")
# new_permalinks = crunchbase.find({"type": "permalink", "data.permalink": {"$nin": seen_permalinks}}).distinct("data.permalink")
# counter = 0
# total = len(new_permalinks)

# for permalink in new_permalinks:
#     counter += 1
#     timestamp = datetime.datetime.utcnow()
#     if counter % 50 == 0:
#         print "{}: Permalink: {} of {}".format(timestamp.isoformat(), counter, total)
#     doc = crunchbase.find_one({"type": "permalink", "data.permalink": permalink})
#     if doc is None:
#         print 'find_one for permalink `{}` was null'.format(permalink)
#         continue
#     if doc['data']['entity_type'] == 'company':
#         details = api.company(doc['data']['permalink'])
#     if doc['data']['entity_type'] == 'financial_organization':
#         details = api.financial_org(doc['data']['permalink'])
#     if details is None:
#         print 'Details was null for ', doc
#     else:
#         # print details
#         details['entity_type'] = doc['data']['entity_type']
#         crunchbase.save({"type": "entity", "data": details})




