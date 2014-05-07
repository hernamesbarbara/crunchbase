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
db = MongoClient(MONGO_URI)['crunchbase']
api = Crunchbase(os.environ['CRUNCHBASE_APIKEY'])

counter = 0
total = db.permalinks.count()
for doc in db.permalinks.find({}):
    counter += 1
    timestamp = datetime.datetime.utcnow()
    if counter % 50 == 0:
        print "{}: Permalink: {} of {}".format(timestamp.isoformat(), counter, total)
    if db['entities'].find_one({'permalink': doc['permalink']}, timeout=False):
        continue
    if doc['entity_type'] == 'company':
        details = api.company(doc['permalink'])
    if doc['entity_type'] == 'financial_organization':
        details = api.financial_org(doc['permalink'])
    if details is None:
        print 'Details was null for ', doc
    else:
        details['entity_type'] = doc['entity_type']
        db['entities'].save(details)




